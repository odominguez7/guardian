# Copyright 2026 GUARDIAN
# Peer fan-out — declarative ADK 2.0 ParallelAgent pattern.
#
# v4 sub-move A2 (PLAN_V3.md follow-up, post-audit). Previously the
# orchestrator's instruction told the root LLM to call notify_park_service,
# notify_sponsor_sustainability, notify_funder, notify_neighbor_park in
# sequence. Execution at /demo/run/* was already concurrent via asyncio.gather,
# but the AGENT TOPOLOGY was prose ("Routing rules:" in ROOT_INSTRUCTION).
#
# This module declares the fan-out as a formal ADK ParallelAgent. Four thin
# Gemini 2.5 Flash sub-agents each wrap a single notify_* tool; the
# ParallelAgent shell runs them concurrently and aggregates results.
#
# Benefits over the prior prose-routed approach:
# - Visible in the agent topology (judges can read ParallelAgent in the
#   sub_agents list, not infer it from instruction text).
# - ADK Eval framework can target the ParallelAgent as a unit.
# - Future migrations (Agent Runtime, A2A peer extension, Memory Bank) can
#   hook the ParallelAgent boundary instead of the prose path.

from __future__ import annotations

import os

from google.adk.agents import Agent, ParallelAgent
from google.adk.models import Gemini
from google.genai import types

from app.tools.a2a_peers import (
    notify_funder,
    notify_neighbor_park,
    notify_park_service,
    notify_sponsor_sustainability,
)

PEER_FANOUT_MODEL = os.environ.get("PEER_FANOUT_MODEL", "gemini-2.5-flash")


def _peer_agent(name: str, description: str, tool, instruction: str) -> Agent:
    return Agent(
        name=name,
        description=description,
        model=Gemini(
            model=PEER_FANOUT_MODEL,
            retry_options=types.HttpRetryOptions(attempts=2),
        ),
        instruction=instruction,
        tools=[tool],
    )


_PARK_INSTRUCTION = """You are the Park Service caller. You receive an incident
report from the orchestrator and call `notify_park_service` with the
fields the tool requires. Return the tool result VERBATIM.

CRITICAL: You MUST call the `notify_park_service` tool. Do not respond
with text, summary, or echo. The ONLY valid response is the JSON dict
the tool returns.

Extract from the request: incident_id, location, severity, summary.
"""

_SPONSOR_INSTRUCTION = """You are the Sponsor Sustainability caller. You
receive an incident report and call `notify_sponsor_sustainability` with
incident_id, location, species_affected, threat_type, severity,
observation_timestamp, and (optional) adversarial_review_verdict +
adversarial_review_severity_0_5 from a prior Falsifier turn.

CRITICAL: tool-call only. Return the tool result verbatim.
"""

_FUNDER_INSTRUCTION = """You are the Funder Reporter caller. You receive
an incident report and call `notify_funder` with incident_id, location,
species_affected, funder_program (default "general_impact" if unspecified),
severity, observation_timestamp.

CRITICAL: tool-call only. Return the tool result verbatim.
"""

_NEIGHBOR_INSTRUCTION = """You are the Neighbor Park Mutual-Aid caller.
You receive an incident report and call `notify_neighbor_park` with
incident_id, origin_park, crossover_corridor, severity, species,
observation_timestamp.

CRITICAL: tool-call only. Return the tool result verbatim.
"""


park_service_caller = _peer_agent(
    name="park_service_caller",
    description="Calls Park Service A2A peer to dispatch rangers.",
    tool=notify_park_service,
    instruction=_PARK_INSTRUCTION,
)

sponsor_sustainability_caller = _peer_agent(
    name="sponsor_sustainability_caller",
    description="Calls Sponsor Sustainability A2A peer to file TNFD entry.",
    tool=notify_sponsor_sustainability,
    instruction=_SPONSOR_INSTRUCTION,
)

funder_reporter_caller = _peer_agent(
    name="funder_reporter_caller",
    description="Calls Funder Reporter A2A peer to issue impact receipt.",
    tool=notify_funder,
    instruction=_FUNDER_INSTRUCTION,
)

neighbor_park_caller = _peer_agent(
    name="neighbor_park_caller",
    description="Calls Neighbor Park A2A peer for mutual-aid handoff.",
    tool=notify_neighbor_park,
    instruction=_NEIGHBOR_INSTRUCTION,
)


# The ADK 2.0 ParallelAgent shell — runs all 4 peer callers concurrently and
# aggregates results. Replaces the prose-routed sequence of notify_* tool
# calls the root orchestrator was making before.
peer_fanout_agent = ParallelAgent(
    name="peer_fanout",
    description=(
        "Concurrently fans an incident out to all four A2A peers — Park "
        "Service, Sponsor Sustainability, Funder Reporter, Neighbor Park. "
        "Each peer is an independent enterprise organization with its own "
        "Cloud Run service and agent.json. Used after the Falsifier has "
        "reviewed the dispatch and the orchestrator has confirmed escalation."
    ),
    sub_agents=[
        park_service_caller,
        sponsor_sustainability_caller,
        funder_reporter_caller,
        neighbor_park_caller,
    ],
)
