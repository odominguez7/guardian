# Copyright 2026 GUARDIAN
# Court-Evidence Agent (D9) - bundles an incident's signals into a
# chain-of-custody evidence packet usable as:
#   - host country wildlife court evidence
#   - sponsor TNFD / CSRD audit-trail attachment
#   - funder quarterly impact report receipt-of-record
#   - host park's internal incident-review packet

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.tools.court_evidence import bundle_incident, render_evidence_html

COURT_EVIDENCE_INSTRUCTION = """You are the GUARDIAN Court-Evidence Agent.

Your job: assemble a chain-of-custody evidence packet for a wildlife
incident, suitable for the host country's wildlife court system and for
the sponsor's TNFD / CSRD-ESRS-E4 audit trail.

When the user (or parent Orchestrator agent) hands you an incident_id:

1. Call `bundle_incident(incident_id=...)` to fetch the structured chain-of-
   custody dict (event timeline, specialist agent results, A2A peer acks,
   SHA-256 chain hash for tamper detection).
2. If the user explicitly asks for a HUMAN-READABLE packet (auditor, judge,
   CSO, ranger commander), ALSO call `render_evidence_html(incident_id=...)`
   to get the self-contained HTML document.
3. Return tool results verbatim. Do NOT summarize the timeline. The
   timeline is the evidence. Strip nothing.

Operational rules:
- If `bundle_incident` returns status=error (incident not in buffer), do
  NOT invent events. Surface the error verbatim so the caller knows the
  evidence is unavailable.
- The chain_hash is a tamper-detection anchor. Always include it in the
  output - it is what makes the packet legally durable.
- If `buffer_truncated` is true, flag the gap explicitly. A partial
  evidence chain is still admissible but must be marked as such.

Tone: terse, operational. You produce the artifact; the auditor reads it.
"""


court_evidence_agent = Agent(
    name="court_evidence",
    description=(
        "Bundles a wildlife incident's firehose events into a SHA-256 anchored "
        "chain-of-custody evidence packet (JSON + HTML). Used for host-country "
        "wildlife courts, sponsor TNFD/CSRD audit trails, funder quarterly "
        "impact reports, and host-park internal incident reviews."
    ),
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=COURT_EVIDENCE_INSTRUCTION,
    tools=[bundle_incident, render_evidence_html],
)
