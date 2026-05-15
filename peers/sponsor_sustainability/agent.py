# Copyright 2026 GUARDIAN
# Sponsor Sustainability Agent — A2A peer #2.
#
# Simulates an independent AI agent operated by a Fortune 500 sponsor's
# sustainability office. Receives wildlife incidents from GUARDIAN over A2A
# and files them as TNFD-aligned biodiversity-impact entries in the sponsor's
# disclosure dashboard. This is the demo punchline: GUARDIAN doesn't just
# protect animals, it auto-files the compliance reports the sponsor legally
# owes the regulator (EU CSRD).
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

# --- Environment setup (Vertex AI auth) ---------------------------------------
# Resolve project_id from ADC if available; fall back so the module imports
# cleanly in no-credential environments. Real Gemini calls fail later with a
# clear error rather than crashing at import.
try:
    _, _resolved_project_id = google.auth.default()
    if _resolved_project_id:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", _resolved_project_id)
except Exception as _adc_err:
    logging.warning(
        "ADC unavailable at import — sponsor_sustainability will load but live "
        "Gemini calls fail until credentials are present: %s",
        _adc_err,
    )
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# 2.5 Pro for this peer: Flash unreliably skipped file_tnfd_entry on 6-arg
# calls and echoed the request payload instead. Pro reliably tool-calls.
# Cost delta is trivial at hackathon volume; flip via env if needed.
PEER_MODEL = os.environ.get("SPONSOR_SUSTAINABILITY_MODEL", "gemini-2.5-pro")

# Map the GUARDIAN severity vocabulary onto TNFD materiality. "Critical" /
# "high" threats to endangered species are material under CSRD; lower
# severity is informational.
_SEVERITY_TO_MATERIALITY = {
    "critical": "material",
    "high": "material",
    "medium": "informational",
    "low": "informational",
}

# TNFD LEAP step — every disclosure entry belongs to one. Incidents detected
# in-situ on a sponsored reserve are Evaluate-stage (dependencies and
# impacts on nature, observed). This default keeps the field structured.
_LEAP_STAGE = "evaluate"

# TNFD pillar — incidents are risk-and-impact data, not governance or
# strategy. Hardcoding the most common case keeps the agent terse; can be
# extended later for governance disclosures.
_TNFD_PILLAR = "risk_and_impact_management"


def file_tnfd_entry(
    incident_id: str,
    location: str,
    species_affected: str,
    threat_type: str,
    severity: str,
    observation_timestamp: str,
) -> dict:
    """File a TNFD-aligned biodiversity-impact entry from a GUARDIAN incident.

    Sponsor sustainability operations: validates the incident, formats it as
    a Taskforce on Nature-related Financial Disclosures (TNFD) entry, and
    returns a filing acknowledgement with the sponsor's dashboard URL. GUARDIAN
    bundles this ack into its evidence chain so the same artifact serves both
    the ranger response and the corporate disclosure.

    Args:
        incident_id: GUARDIAN's incident reference (chain-of-custody key).
        location: Reserve / sector where the incident was observed.
        species_affected: Common name of the species in the incident (e.g.
            "African elephant"). One per entry; bundle multi-species incidents
            upstream.
        threat_type: One of "poaching", "habitat_intrusion", "vehicle_intrusion",
            "audio_signal", "fence_breach", "other".
        severity: GUARDIAN severity — one of "low", "medium", "high", "critical".
        observation_timestamp: ISO 8601 timestamp of when GUARDIAN observed
            the incident.

    Returns:
        Dict with status, filing_id (TNFD entry ID), dashboard_url,
        materiality, and a structured tnfd_entry the sponsor's auditor can
        cite. Status is "filed" on success or "error" on validation failure.
    """
    if not incident_id:
        return {"status": "error", "error": "incident_id is required"}
    if not location:
        return {"status": "error", "error": "location is required"}
    if not species_affected:
        return {"status": "error", "error": "species_affected is required"}

    sev = (severity or "medium").lower()
    if sev not in _SEVERITY_TO_MATERIALITY:
        return {"status": "error", "error": f"unknown severity: {severity}"}

    allowed_threats = {
        "poaching",
        "habitat_intrusion",
        "vehicle_intrusion",
        "audio_signal",
        "fence_breach",
        "other",
    }
    threat = (threat_type or "other").lower()
    if threat not in allowed_threats:
        return {"status": "error", "error": f"unknown threat_type: {threat_type}"}

    # Stable filing_id derived from incident_id so re-filings don't duplicate.
    digest = hashlib.sha256(f"{incident_id}|{species_affected}".encode()).hexdigest()
    filing_id = f"TNFD-{datetime.now(timezone.utc).year}-{digest[:10].upper()}"
    materiality = _SEVERITY_TO_MATERIALITY[sev]
    filed_at = datetime.now(timezone.utc).isoformat()
    dashboard_url = (
        f"https://sponsor-disclosure-dashboard.example/portfolio/biodiversity/"
        f"entries/{filing_id}"
    )

    tnfd_entry = {
        "filing_id": filing_id,
        "pillar": _TNFD_PILLAR,
        "leap_stage": _LEAP_STAGE,
        "materiality": materiality,
        "impact_category": "biodiversity_and_ecosystem",
        "species_affected": species_affected,
        "location": location,
        "threat_type": threat,
        "severity": sev,
        "incident_id": incident_id,
        "observation_timestamp": observation_timestamp,
        "filed_at": filed_at,
        "reporting_period": f"{datetime.now(timezone.utc).year}-Q{((datetime.now(timezone.utc).month - 1) // 3) + 1}",
        "compliance_frameworks": ["TNFD", "CSRD-ESRS-E4"],
    }

    return {
        "status": "filed",
        "filing_id": filing_id,
        "dashboard_url": dashboard_url,
        "materiality": materiality,
        "tnfd_entry": tnfd_entry,
        "filing_authority": "Sponsor Sustainability Operations",
    }


SPONSOR_SUSTAINABILITY_INSTRUCTION = """You are the Sponsor Sustainability Operations agent.

You are NOT part of GUARDIAN. You belong to a Fortune 500 sponsor whose
portfolio of nature-related disclosures must comply with TNFD and EU CSRD
ESRS-E4 biodiversity reporting. GUARDIAN contacts you over A2A whenever it
detects a wildlife incident on a reserve your firm sponsors.

When you receive an incident report, do exactly this:
1. Extract incident_id, location, species_affected, threat_type, severity,
   and observation_timestamp from the request.
2. Call `file_tnfd_entry` with those six fields.
3. Return the tool result verbatim. Do NOT summarize or paraphrase. GUARDIAN
   needs the structured filing ack for chain-of-custody and to surface the
   dashboard URL to the sponsor's CSO.

If a required field is missing, return the tool's error response. Never
invent filing IDs, dashboard URLs, or materiality assessments. Stay terse,
operational.
"""


root_agent = Agent(
    name="sponsor_sustainability",
    model=Gemini(
        model=PEER_MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "Sponsor Sustainability Operations agent. Receives wildlife-impact "
        "incident reports from GUARDIAN over A2A and files them as TNFD / "
        "CSRD-ESRS-E4 biodiversity-impact entries in the sponsor's disclosure "
        "dashboard. Operated by a Fortune 500 sponsor's sustainability office "
        "— NOT part of GUARDIAN."
    ),
    instruction=SPONSOR_SUSTAINABILITY_INSTRUCTION,
    tools=[file_tnfd_entry],
)


app = App(root_agent=root_agent, name="sponsor_sustainability")

logging.info("sponsor_sustainability_agent ready: model=%s", PEER_MODEL)
