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

from app import events
from app.agents.audio_agent import audio_agent
from app.agents.species_id import species_id_agent
from app.agents.stream_watcher import stream_watcher_agent
from app.tools.a2a_peers import (
    get_funder_card,
    get_neighbor_park_card,
    get_park_service_card,
    get_sponsor_sustainability_card,
    mint_incident_id,
    notify_funder,
    notify_neighbor_park,
    notify_park_service,
    notify_sponsor_sustainability,
)


def new_incident_id(seed: str = "") -> dict:
    """Mint a fresh GUARDIAN incident_id to share across A2A peer calls.

    Call this ONCE at the start of any incident-response sequence. Pass the
    returned id into BOTH `notify_park_service` and
    `notify_sponsor_sustainability` so the park record and the sponsor
    filing reconcile.

    Args:
        seed: Optional deterministic seed (e.g. the source camera + timestamp).
            Same seed → same incident_id, useful for de-duplication when the
            same camera event is re-processed.

    Returns:
        {"incident_id": "GU-<hex>"}
    """
    iid = mint_incident_id(seed or None)
    events.emit(
        kind="incident_event",
        agent="root_agent",
        tool="new_incident_id",
        incident_id=iid,
        severity="info",
        payload={"seed_provided": bool(seed)},
    )
    return {"incident_id": iid}

# --- Environment setup (Vertex AI auth) ---------------------------------------
# Resolve project_id from ADC if available; fall back to env so the module
# imports cleanly in CI / no-credential environments. Actual Vertex calls
# fail later with a meaningful error rather than crashing at import.
try:
    _, _resolved_project_id = google.auth.default()
    if _resolved_project_id:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", _resolved_project_id)
except Exception as _adc_err:  # google.auth.exceptions.DefaultCredentialsError + transient
    logging.warning(
        "ADC unavailable at import — GUARDIAN will load but live GCP calls "
        "will fail until credentials are present: %s",
        _adc_err,
    )
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# Orchestrator model. PLAN.md targets gemini-3-pro; not yet available in this
# project's Vertex AI (404 across all regions as of 2026-05-15). Fall back to
# 2.5 Pro until allowlist lands. Flip via env when 3 Pro is callable.
ORCHESTRATOR_MODEL = os.environ.get("GUARDIAN_ORCHESTRATOR_MODEL", "gemini-2.5-pro")


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
- audio_agent: classifies camera-trap microphone audio (gunshot, vehicle_engine,
  distressed_herd, human_voices, wildlife_natural, silence). Returns severity +
  threat_signal flags routing keys use.
- species_id: identifies wildlife from a still image, then grounds the finding
  in the wildlife corpus (IUCN, CITES, TNFD) via Vertex AI Search. Returns a
  compliance_flag ("material" | "informational" | "unlisted") the orchestrator
  uses to decide whether to fan out to sponsor + funder peers.
  (Additional specialists in subsequent days: pattern, visualizer, dispatch,
   court_evidence.)

Your A2A peers (independent agents run by OTHER organizations):
- park_service (national park authority): call `notify_park_service` to report
  a wildlife-threat incident and receive a ranger-dispatch acknowledgement.
- sponsor_sustainability (Fortune 500 sponsor's sustainability office): call
  `notify_sponsor_sustainability` to file a TNFD / CSRD-ESRS-E4 biodiversity-
  impact entry. Receives back a filing_id + dashboard_url.
- funder_reporter (conservation funder, WWF/IUCN/IFAW style): call
  `notify_funder` to file a program-tagged impact receipt for the foundation's
  quarterly impact report. Use funder_program="general_impact" if uncertain.
- neighbor_park (adjacent national park, e.g. Maasai Mara): call
  `notify_neighbor_park` to send a cross-border mutual-aid request when an
  incident might cross the border. Pass origin_park name + crossover_corridor.

Routing rules:
- Video URI, GCS path → delegate to `stream_watcher`.
- Audio URI (gs://*.mp3/.wav, https://*.mp3, etc.) → delegate to `audio_agent`.
  If sound_class is "gunshot" or "vehicle_engine" or "distressed_herd", treat
  as requires_escalation=True with severity from the agent's response.
- Still image URI (.jpg/.png/.webp) → delegate to `species_id`. If the
  agent returns compliance_flag="material", treat as requires_escalation=True
  with severity at least "high". If compliance_flag is "informational",
  severity defaults to "medium".
- If a specialist returns `requires_escalation=True`, run this sequence:
    0. FIRST call `new_incident_id` to mint a single shared incident_id.
       Pass it into BOTH peer calls below so park + sponsor records
       reconcile. Never invent your own GU-... id by hand.
    1. `notify_park_service(incident_id, location, severity, summary)` —
       get ranger dispatch. Use best location available, severity inferred
       from threat_signals (gunshot/vehicle at night → critical; vehicle
       in restricted zone → high; suspicious silhouette → medium; low
       confidence → low).
    2. If severity is "high" or "critical" OR a sponsored species is
       involved, also call `notify_sponsor_sustainability(incident_id,
       location, species_affected, threat_type, severity,
       observation_timestamp)`. Use the SAME incident_id from step 0.
       Map threat_signals to threat_type: "vehicle" → "vehicle_intrusion",
       "human silhouette" → "habitat_intrusion", "gunshot" → "poaching",
       "fence damage" → "fence_breach", anything else → "other".
  Surface both peers' acks to the user verbatim.
- For diagnostic / discovery: `get_park_service_card`,
  `get_sponsor_sustainability_card`.
- For status questions: answer directly using the agent card.

Tone: terse, operational. You are running real-time biodiversity defense, not chit-chat.
"""


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=ORCHESTRATOR_MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "GUARDIAN orchestrator. Coordinates wildlife stream analysis, threat detection, "
        "ranger dispatch, and corporate biodiversity reporting (TNFD/CSRD)."
    ),
    instruction=ROOT_INSTRUCTION,
    sub_agents=[stream_watcher_agent, audio_agent, species_id_agent],
    tools=[
        LongRunningFunctionTool(func=request_user_input),
        new_incident_id,
        notify_park_service,
        get_park_service_card,
        notify_sponsor_sustainability,
        get_sponsor_sustainability_card,
        notify_funder,
        get_funder_card,
        notify_neighbor_park,
        get_neighbor_park_card,
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
