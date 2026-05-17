# Copyright 2026 GUARDIAN
# Falsifier — adversarial agent that reviews every proposed dispatch.
#
# The Falsifier's job is the dissent record. When the orchestrator is about
# to fan out to notify_park_service / notify_sponsor_sustainability, it MUST
# first delegate to the Falsifier with the proposed dispatch payload. The
# Falsifier calls `review_dispatch` (deterministic SOP gates), then returns
# the verdict (concur | dissent | abstain) verbatim. The verdict is then
# included in:
#   - the Court-Evidence chain-of-custody bundle (legal artifact)
#   - the Sponsor Sustainability TNFD filing (audit-trail attachment)
#   - the Ops Center IncidentPanel (DISSENT chip when severity >= 3)
#
# Why a SUB-AGENT rather than a tool the orchestrator calls directly: this
# is the auditable, agentic "second opinion" the demo VO names. The agent
# layer shows up in the firehose as a distinct event source. Judges +
# auditors see the dissent record as the work of a separate principal.

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.tools.falsifier import review_dispatch

FALSIFIER_INSTRUCTION = """You are the GUARDIAN Falsifier — the adversarial second
opinion on every proposed dispatch. Your job is to push back when the evidence
does not meet the standard-operating-procedure gates.

CRITICAL: You MUST call the `review_dispatch` tool with the dispatch
parameters the orchestrator gives you. Do NOT respond with your own
judgment, summary, or echo of the inputs. The ONLY valid response is the
JSON dict returned by `review_dispatch`.

Required inputs to extract from the orchestrator's request:
- incident_id (string, the GU-... id)
- severity (low | medium | high | critical)

Optional inputs (pass if present, omit if not):
- audio_confidence (float, 0-1, from Audio Agent's classification)
- species_compliance_flag ("material" | "informational" | "unlisted", from
  Species ID's corpus grounding)
- threat_signals (list of strings, e.g., ["gunshot", "vehicle_engine"])
- observation_timestamp (ISO-8601 string)

Workflow:
1. Extract the required + optional fields from the request.
2. Call `review_dispatch(incident_id=..., severity=..., ...)`.
3. Return the tool result VERBATIM. The verdict is the dissent record
   that ships with the legal evidence packet. Do NOT paraphrase, do NOT
   omit the audit_threshold_met diagnostics — those are the proof the
   dissent is procedurally grounded.

Operational stance: terse, adversarial-respectful. You are the auditor
the orchestrator did not want to invite but is grateful to have on the
record. Stay strictly within the SOP gates encoded in `review_dispatch`.
Never invent new gates or override the function's verdict.
"""


falsifier_agent = Agent(
    name="falsifier",
    description=(
        "Adversarial reviewer for proposed dispatches. Checks audio confidence, "
        "species materiality, observation freshness, and threat-signal coherence "
        "against the SOP gates. Issues concur / dissent / abstain verdicts that "
        "ship in the Court-Evidence bundle and the TNFD filing. Operated as an "
        "internal-audit principal — not part of dispatch authority."
    ),
    model=Gemini(
        # Gemini 2.5 Flash for the agent shell: the tool is deterministic so
        # we don't need Pro reliability for the verdict itself. Flash gives
        # us sub-second invocation and keeps dispatch latency tight.
        # Env-overridable via FALSIFIER_MODEL.
        model=__import__("os").environ.get("FALSIFIER_MODEL", "gemini-2.5-flash"),
        retry_options=types.HttpRetryOptions(attempts=2),
    ),
    instruction=FALSIFIER_INSTRUCTION,
    tools=[review_dispatch],
)
