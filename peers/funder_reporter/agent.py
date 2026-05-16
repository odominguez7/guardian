# Copyright 2026 GUARDIAN
# Funder Reporter Agent — A2A peer #3.
#
# Simulates an independent AI agent operated by a conservation funder
# (WWF / IUCN / IFAW style). Receives wildlife-incident summaries from
# GUARDIAN over A2A and files them as funder impact-receipts so the
# foundation's quarterly impact report assembles itself in real time.
# Demos the "your foundation dollars are working" narrative.
#
# Separate deployable: own Cloud Run service, own service account, own card.

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
    """Parse ISO 8601 tolerantly. Returns None on failure."""
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


# --- Environment setup (Vertex AI auth) ---------------------------------------
try:
    _, _resolved_project_id = google.auth.default()
    if _resolved_project_id:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", _resolved_project_id)
except Exception as _adc_err:
    logging.warning(
        "ADC unavailable at import — funder_reporter will load but live Gemini "
        "calls fail until credentials are present: %s",
        _adc_err,
    )
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

PEER_MODEL = os.environ.get("FUNDER_REPORTER_MODEL", "gemini-2.5-pro")

# Map GUARDIAN severity onto funder impact-receipt categories.
_SEVERITY_TO_IMPACT_TIER = {
    "critical": "headline_impact",   # goes in the quarterly report cover
    "high":     "material_impact",   # featured in the report body
    "medium":   "monitored",         # tracked, not featured
    "low":      "monitored",         # tracked, not featured
}

# Funder programs we currently report against. Realistic-sounding,
# fabricated for the demo so the receipts look like a real foundation
# would issue them.
_VALID_PROGRAMS = {
    "elephants_at_risk",
    "rhino_horn_crisis",
    "biodiversity_corridor_2030",
    "predator_coexistence",
    "general_impact",
}


def file_impact_report(
    incident_id: str,
    location: str,
    species_affected: str,
    severity: str,
    funder_program: str,
    observation_timestamp: str,
) -> dict:
    """File a funder impact-report entry from a GUARDIAN incident.

    Funder reporting operations: validates the incident, formats it as a
    program-tagged impact receipt the foundation's quarterly report builder
    will pick up, and returns the receipt with a stable receipt_id +
    dashboard URL.

    Args:
        incident_id: GUARDIAN's incident reference (chain-of-custody key).
        location: Reserve / sector where the incident was observed.
        species_affected: Common name of the species involved.
        severity: GUARDIAN severity — "low", "medium", "high", "critical".
        funder_program: One of:
          - "elephants_at_risk"
          - "rhino_horn_crisis"
          - "biodiversity_corridor_2030"
          - "predator_coexistence"
          - "general_impact"
        observation_timestamp: ISO 8601 timestamp of GUARDIAN's observation.

    Returns:
        Dict with status, receipt_id (FUND-YYYY-<10hex>), dashboard_url,
        impact_tier (headline/material/monitored), and the structured
        impact_entry.
    """
    if not incident_id:
        return {"status": "error", "error": "incident_id is required"}
    if not location:
        return {"status": "error", "error": "location is required"}
    if not species_affected:
        return {"status": "error", "error": "species_affected is required"}

    sev = (severity or "medium").lower()
    if sev not in _SEVERITY_TO_IMPACT_TIER:
        return {"status": "error", "error": f"unknown severity: {severity}"}

    program = (funder_program or "general_impact").lower()
    if program not in _VALID_PROGRAMS:
        return {
            "status": "error",
            "error": f"unknown funder_program: {funder_program}. Valid: {sorted(_VALID_PROGRAMS)}",
        }

    obs_dt = _parse_ts(observation_timestamp)
    if obs_dt is None:
        return {
            "status": "error",
            "error": (
                "observation_timestamp must be ISO 8601 "
                "(e.g. 2026-05-15T02:14:00Z)"
            ),
        }

    # Stable receipt_id from incident_id alone (codex challenge lesson:
    # don't bake species or wall-clock into it — defeats dedup).
    digest = hashlib.sha256(incident_id.encode()).hexdigest()
    receipt_id = f"FUND-{obs_dt.year}-{digest[:10].upper()}"
    impact_tier = _SEVERITY_TO_IMPACT_TIER[sev]
    filed_at = datetime.now(timezone.utc).isoformat()
    dashboard_url = (
        f"https://funder-impact-dashboard.example/programs/{program}/"
        f"receipts/{receipt_id}"
    )

    impact_entry = {
        "receipt_id": receipt_id,
        "funder_program": program,
        "impact_tier": impact_tier,
        "species_affected": species_affected,
        "location": location,
        "severity": sev,
        "incident_id": incident_id,
        "observation_timestamp": observation_timestamp,
        "filed_at": filed_at,
        "reporting_quarter": f"{obs_dt.year}-Q{((obs_dt.month - 1) // 3) + 1}",
        "narrative_hook": (
            f"Your {program.replace('_', ' ')} support enabled real-time "
            f"detection + dispatch protecting {species_affected} at {location}."
        ),
    }

    return {
        "status": "filed",
        "receipt_id": receipt_id,
        "dashboard_url": dashboard_url,
        "impact_tier": impact_tier,
        "funder_program": program,
        "impact_entry": impact_entry,
        "filing_authority": "Funder Impact Reporting Service",
    }


FUNDER_INSTRUCTION = """You are the Funder Impact Reporter agent.

You are NOT part of GUARDIAN. You belong to a conservation funder (WWF /
IUCN / IFAW style) whose foundation quarterly impact report auto-files
every incident GUARDIAN detects on the reserves your dollars support.
GUARDIAN contacts you over A2A whenever it detects a wildlife incident
relevant to a funder program.

When you receive an incident report, do exactly this:
1. Extract incident_id, location, species_affected, severity,
   funder_program, and observation_timestamp from the request.
2. Call `file_impact_report` with those six fields.
3. Return the tool result verbatim. Do NOT summarize or paraphrase.
   GUARDIAN bundles the receipt into its evidence chain.

If a required field is missing, return the tool's error response. Never
invent receipt_ids, dashboard URLs, or impact tiers. Stay terse,
operational.
"""


root_agent = Agent(
    name="funder_reporter",
    model=Gemini(
        model=PEER_MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "Funder Impact Reporter agent. Receives wildlife-incident summaries "
        "from GUARDIAN over A2A and files them as program-tagged impact "
        "receipts for the foundation's quarterly report. Operated by a "
        "conservation funder (WWF/IUCN/IFAW style) — NOT part of GUARDIAN."
    ),
    instruction=FUNDER_INSTRUCTION,
    tools=[file_impact_report],
)


app = App(root_agent=root_agent, name="funder_reporter")

logging.info("funder_reporter_agent ready: model=%s", PEER_MODEL)
