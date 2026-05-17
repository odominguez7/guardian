# Copyright 2026 GUARDIAN
# Slim Agent Engine variant of the root orchestrator.
#
# Track 3 mandate ships the orchestrator on Vertex AI Agent Engine
# alongside Cloud Run. Agent Engine's managed container can't run the
# things Cloud Run's image runs:
#   - BigQueryAgentAnalyticsPlugin needs IAM that Agent Engine doesn't
#     get by default (the FastAPI traffic observability stack is for
#     Cloud Run only)
#   - yt-dlp / ffmpeg subprocesses for the /livecam/spot path don't
#     exist as binaries in Agent Engine's sandbox
#   - FastAPI app construction isn't needed (Agent Engine has its own
#     HTTP layer)
#
# This module exposes the SAME root_agent identity as app.agent — same
# specialists, same A2A peer tools, same Falsifier — but skips the
# Cloud-Run-only side effects so cloudpickle + Agent Engine container
# boot cleanly.

import logging
import os

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import LongRunningFunctionTool
from google.genai import types

from app.agents.audio_agent import audio_agent
from app.agents.court_evidence import court_evidence_agent
from app.agents.falsifier import falsifier_agent
from app.agents.peer_fanout import peer_fanout_agent
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

# new_incident_id intentionally lives in app.agent (Cloud Run) because it
# emits to the firehose. Agent Engine variant uses the underlying
# mint_incident_id helper directly without the firehose emit.
def new_incident_id(seed: str = "") -> dict:
    """Mint a fresh GUARDIAN incident_id (Agent Engine variant — no firehose)."""
    iid = mint_incident_id(seed or None)
    return {"incident_id": iid}


os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

ORCHESTRATOR_MODEL = os.environ.get("GUARDIAN_ORCHESTRATOR_MODEL", "gemini-2.5-pro")

# Same routing prose as the Cloud Run orchestrator. Copied (not imported)
# so changes here don't drift from app.agent — keep the two ROOT_INSTRUCTION
# strings in lockstep on every orchestrator-prompt edit.
ROOT_INSTRUCTION = """You are GUARDIAN, a multi-agent system that protects conservation
areas from poaching and produces TNFD/CSRD biodiversity reports for corporate sponsors.

Your team of specialist agents:
- stream_watcher: analyzes video/image streams for wildlife and threats.
- audio_agent: classifies camera-trap microphone audio (gunshot, vehicle_engine,
  distressed_herd, human_voices, wildlife_natural, silence). Returns severity +
  threat_signal flags routing keys use.
- species_id: identifies wildlife from a still image, then grounds the finding
  in the wildlife corpus (IUCN, CITES, TNFD) via Vertex AI Search. Returns a
  compliance_flag ("material" | "informational" | "unlisted").
- court_evidence: bundles every firehose event for an incident into a SHA-256
  anchored chain-of-custody packet.
- falsifier: adversarial second opinion on every proposed dispatch. BEFORE
  you call any notify_* tool, you MUST delegate to `falsifier`.

Your A2A peers (independent agents run by OTHER organizations):
- park_service / sponsor_sustainability / funder_reporter / neighbor_park.
  For severity in {"high", "critical"}: transfer_to_agent("peer_fanout").
  For {"low", "medium"}: call notify_* directly.

Always call `new_incident_id` FIRST to mint a single shared id.
Tone: terse, operational.
"""


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=ORCHESTRATOR_MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "GUARDIAN orchestrator (Agent Engine variant). Coordinates wildlife "
        "stream analysis, threat detection, ranger dispatch, and corporate "
        "biodiversity reporting (TNFD/CSRD)."
    ),
    instruction=ROOT_INSTRUCTION,
    sub_agents=[
        stream_watcher_agent,
        audio_agent,
        species_id_agent,
        falsifier_agent,
        court_evidence_agent,
        peer_fanout_agent,
    ],
    tools=[
        LongRunningFunctionTool(func=lambda message: {"status": "pending", "message": message}),
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


# Agent Engine queries this `app` attribute. Same shape as
# app.agent.app but no BigQuery plugin (no IAM, no analytics dataset
# creation at import).
app = App(
    root_agent=root_agent,
    name="app",
)
