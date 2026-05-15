# ruff: noqa
# Copyright 2026 GUARDIAN
# Root orchestrator for the GUARDIAN multi-agent system.

import logging
import os

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.plugins.bigquery_agent_analytics_plugin import (
    BigQueryAgentAnalyticsPlugin,
    BigQueryLoggerConfig,
)
from google.adk.tools import LongRunningFunctionTool
from google.cloud import bigquery
from google.genai import types

from app.agents.stream_watcher import stream_watcher_agent

# --- Environment setup (Vertex AI auth) ---------------------------------------
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def request_user_input(message: str) -> dict:
    """Request additional input from the user.

    Use when GUARDIAN needs clarification before continuing — e.g. ambiguous
    geolocation, unclear severity, missing ranger contact.

    Args:
        message: The question or clarification request to show the user.
    """
    return {"status": "pending", "message": message}


# --- Root orchestrator --------------------------------------------------------
ROOT_INSTRUCTION = """You are GUARDIAN, a multi-agent system that protects conservation
areas from poaching and produces TNFD/CSRD biodiversity reports for corporate sponsors.

Your team of specialist agents:
- stream_watcher: analyzes video/image streams for wildlife and threats.
  (Additional agents wired in subsequent days: audio, species_id, pattern, visualizer,
   dispatch, court_evidence; plus four A2A peer agents.)

Routing rules:
- For any video URI, GCS path, or image URI: delegate to `stream_watcher`.
- For status questions: answer directly using the agent card.
- If a specialist returns `requires_escalation=True`, surface the alert prominently
  and tell the user what downstream agents *will* be invoked (placeholder until D4+).

Tone: terse, operational. You are running real-time biodiversity defense, not chit-chat.
"""


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-pro",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "GUARDIAN orchestrator. Coordinates wildlife stream analysis, threat detection, "
        "ranger dispatch, and corporate biodiversity reporting (TNFD/CSRD)."
    ),
    instruction=ROOT_INSTRUCTION,
    sub_agents=[stream_watcher_agent],
    tools=[
        LongRunningFunctionTool(func=request_user_input),
    ],
)


# --- BigQuery Agent Analytics plugin (observability spine) -------------------
_plugins = []
_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
_dataset_id = os.environ.get("BQ_ANALYTICS_DATASET_ID", "adk_agent_analytics")
_location = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")

if _project_id:
    try:
        bq = bigquery.Client(project=_project_id)
        bq.create_dataset(f"{_project_id}.{_dataset_id}", exists_ok=True)

        _plugins.append(
            BigQueryAgentAnalyticsPlugin(
                project_id=_project_id,
                dataset_id=_dataset_id,
                location=_location,
                config=BigQueryLoggerConfig(
                    gcs_bucket_name=os.environ.get("BQ_ANALYTICS_GCS_BUCKET"),
                    connection_id=os.environ.get("BQ_ANALYTICS_CONNECTION_ID"),
                ),
            )
        )
    except Exception as e:
        logging.warning(f"Failed to initialize BigQuery Analytics: {e}")


app = App(
    root_agent=root_agent,
    name="app",
    plugins=_plugins,
)
