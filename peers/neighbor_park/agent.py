# Copyright 2026 GUARDIAN
# Neighbor Park Agent — A2A peer #4.
#
# Simulates an independent AI agent operated by an ADJACENT national park
# (e.g., Maasai Mara is adjacent to Serengeti across the Kenya-Tanzania
# border; Kruger borders multiple smaller parks in Mozambique). When a
# poaching incident at one reserve might cross the border, the neighbor's
# rangers need to be ready. GUARDIAN sends a cross-border mutual-aid
# request over A2A and gets back the neighbor's standby ack.
#
# This peer is the Track 3 cinema moment: 4 independent enterprise agents
# from 4 different organizations all coordinating live on a single
# incident.

import hashlib
import logging
import os
from datetime import datetime, timezone

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


def _parse_ts(ts: str) -> datetime | None:
    if not ts:
        return None
    cleaned = ts.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(cleaned)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


try:
    _, _resolved_project_id = google.auth.default()
    if _resolved_project_id:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", _resolved_project_id)
except Exception as _adc_err:
    logging.warning(
        "ADC unavailable at import — neighbor_park will load but live Gemini "
        "calls fail until credentials are present: %s",
        _adc_err,
    )
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

PEER_MODEL = os.environ.get("NEIGHBOR_PARK_MODEL", "gemini-2.5-pro")

# Standby posture for the receiving park rangers based on incident severity.
_SEVERITY_TO_POSTURE = {
    "critical": "armed_intercept_team",   # active border patrol
    "high":     "perimeter_alert",        # rangers on standby at known crossings
    "medium":   "passive_monitoring",     # camera-trap density boosted
    "low":      "passive_monitoring",
}

# Window in which a fleeing poacher could realistically cross into the
# neighbor's park, based on severity (chase events have a finite half-life).
_SEVERITY_TO_WINDOW_HOURS = {
    "critical": 4,
    "high":     6,
    "medium":   12,
    "low":      24,
}


def accept_mutual_aid(
    incident_id: str,
    origin_park: str,
    severity: str,
    species_affected: str,
    crossover_corridor: str,
    observation_timestamp: str,
) -> dict:
    """Accept a cross-border mutual-aid request from a neighboring park.

    Operations: posts the originating park's incident to our patrol roster,
    elevates ranger posture at the listed crossover corridor, opens a
    chase window proportional to severity, and returns a handoff ack
    GUARDIAN can bundle in its evidence chain.

    Args:
        incident_id: GUARDIAN's stable incident reference.
        origin_park: Name of the park where the incident originated
            (e.g., "Serengeti National Park, Tanzania").
        severity: GUARDIAN severity — "low" | "medium" | "high" | "critical".
        species_affected: Common name of the species.
        crossover_corridor: Named or coordinate-based description of the
            most likely cross-border route (e.g., "Mara River, Sand River
            confluence" or "Migration corridor F-12").
        observation_timestamp: ISO 8601 timestamp of the originating
            observation.

    Returns:
        Dict with status, handoff_id, posture, window_open_until,
        responding_park, and the full handoff_record.
    """
    if not incident_id:
        return {"status": "error", "error": "incident_id is required"}
    if not origin_park:
        return {"status": "error", "error": "origin_park is required"}
    if not species_affected:
        return {"status": "error", "error": "species_affected is required"}
    if not crossover_corridor:
        return {"status": "error", "error": "crossover_corridor is required"}

    sev = (severity or "medium").lower()
    if sev not in _SEVERITY_TO_POSTURE:
        return {"status": "error", "error": f"unknown severity: {severity}"}

    obs_dt = _parse_ts(observation_timestamp)
    if obs_dt is None:
        return {
            "status": "error",
            "error": "observation_timestamp must be ISO 8601 (e.g. 2026-05-15T02:14:00Z)",
        }

    # Stable handoff_id from incident_id alone.
    digest = hashlib.sha256(incident_id.encode()).hexdigest()
    handoff_id = f"MUTAID-{obs_dt.year}-{digest[:10].upper()}"

    posture = _SEVERITY_TO_POSTURE[sev]
    window_hours = _SEVERITY_TO_WINDOW_HOURS[sev]
    window_end = obs_dt.replace(microsecond=0)
    # Use timedelta for window
    from datetime import timedelta

    window_open_until = (window_end + timedelta(hours=window_hours)).isoformat()
    acked_at = datetime.now(timezone.utc).isoformat()

    handoff_record = {
        "handoff_id": handoff_id,
        "origin_park": origin_park,
        "responding_park": "Maasai Mara National Reserve (Kenya)",
        "posture": posture,
        "species_watch": species_affected,
        "crossover_corridor": crossover_corridor,
        "severity": sev,
        "window_open_at": obs_dt.isoformat(),
        "window_open_until": window_open_until,
        "incident_id": incident_id,
        "acked_at": acked_at,
        "operating_protocol": "CITES-MIKE cross-border mutual aid",
    }

    return {
        "status": "accepted",
        "handoff_id": handoff_id,
        "posture": posture,
        "window_open_until": window_open_until,
        "responding_park": "Maasai Mara National Reserve (Kenya)",
        "handoff_record": handoff_record,
        "responding_authority": "Maasai Mara Ranger Operations",
    }


NEIGHBOR_INSTRUCTION = """You are the Neighbor Park Operations agent
(Maasai Mara National Reserve, Kenya — adjacent to Serengeti and other
trans-frontier conservation areas).

You are NOT part of GUARDIAN. You belong to an adjacent national park
that runs an independent ranger force. GUARDIAN contacts you over A2A
when a poaching incident at a neighboring park might cross into your
jurisdiction, requesting cross-border mutual aid.

When you receive a mutual-aid request, do exactly this:
1. Extract incident_id, origin_park, severity, species_affected,
   crossover_corridor, and observation_timestamp from the request.
2. Call `accept_mutual_aid` with those six fields.
3. Return the tool result verbatim. Do NOT summarize or paraphrase.
   GUARDIAN bundles the handoff ack into its court-evidence chain.

If a required field is missing, return the tool's error response.
Never invent handoff IDs, postures, or window times. Stay terse,
operational.
"""


root_agent = Agent(
    name="neighbor_park",
    model=Gemini(
        model=PEER_MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "Neighbor Park Operations agent (Maasai Mara, Kenya). Receives "
        "cross-border mutual-aid requests from GUARDIAN over A2A and "
        "elevates ranger posture at named crossover corridors. Operated by "
        "an adjacent national park authority — NOT part of GUARDIAN."
    ),
    instruction=NEIGHBOR_INSTRUCTION,
    tools=[accept_mutual_aid],
)


app = App(root_agent=root_agent, name="neighbor_park")

logging.info("neighbor_park_agent ready: model=%s", PEER_MODEL)
