# Copyright 2026 GUARDIAN
# Park Service Agent — A2A peer #1.
#
# Simulates an independent AI agent operated by a national park authority.
# Receives incident reports from GUARDIAN (via A2A) and acknowledges ranger
# dispatch. This is a SEPARATE deployable from app/agent.py; it runs in its
# own Cloud Run service with its own service account and its own agent.json.

import logging
import os
import random
import string
from datetime import datetime, timezone

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# --- Environment setup (Vertex AI auth) ---------------------------------------
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

PEER_MODEL = os.environ.get("PARK_SERVICE_MODEL", "gemini-2.5-flash")


def dispatch_rangers(incident_id: str, location: str, severity: str) -> dict:
    """Acknowledge an incident from GUARDIAN and dispatch the nearest ranger unit.

    Park Service operations: validates the incident, picks a ranger unit by
    severity, and returns a dispatch acknowledgement that GUARDIAN can log in
    its evidence bundle.

    Args:
        incident_id: GUARDIAN's incident reference (used for chain-of-custody).
        location: Best-effort coordinates or named area ("Sector C, north fence").
        severity: One of "low", "medium", "high", "critical".

    Returns:
        Dict with status, ranger_unit, estimated_arrival_minutes, and
        ack_timestamp. Status is "dispatched" on success or "error" on failure.
    """
    if not incident_id:
        return {"status": "error", "error": "incident_id is required"}
    if not location:
        return {"status": "error", "error": "location is required"}

    sev = (severity or "medium").lower()
    if sev not in {"low", "medium", "high", "critical"}:
        return {"status": "error", "error": f"unknown severity: {severity}"}

    eta_minutes = {"critical": 8, "high": 15, "medium": 30, "low": 60}[sev]
    unit_id = "PSR-" + "".join(random.choices(string.digits, k=4))

    return {
        "status": "dispatched",
        "incident_id": incident_id,
        "ranger_unit": unit_id,
        "estimated_arrival_minutes": eta_minutes,
        "location": location,
        "severity": sev,
        "ack_timestamp": datetime.now(timezone.utc).isoformat(),
        "responding_authority": "Park Service Operations Center",
    }


PARK_SERVICE_INSTRUCTION = """You are the Park Service Operations agent.

You are NOT part of GUARDIAN. You belong to the national park authority and you
coordinate ranger dispatch. GUARDIAN contacts you over A2A when it has detected
a wildlife threat (poacher, vehicle, gunshot, distressed herd).

When you receive an incident report, do exactly this:
1. Extract the incident_id, location, and severity from the request.
2. Call `dispatch_rangers` with those three fields.
3. Return the tool result verbatim. Do NOT summarize or paraphrase. GUARDIAN
   needs the structured ack for its court-evidence bundle.

If the request is missing required fields, return the tool's error response.
Never invent ranger units or arrival times. Stay terse, operational.
"""


root_agent = Agent(
    name="park_service",
    model=Gemini(
        model=PEER_MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "Park Service Operations agent. Receives wildlife-threat incident "
        "reports from GUARDIAN (A2A) and acknowledges ranger dispatch with "
        "unit ID and ETA. Operated by the national park authority — NOT part "
        "of GUARDIAN."
    ),
    instruction=PARK_SERVICE_INSTRUCTION,
    tools=[dispatch_rangers],
)


app = App(root_agent=root_agent, name="park_service")

logging.info("park_service_agent ready: model=%s", PEER_MODEL)
