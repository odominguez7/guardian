# Copyright 2026 GUARDIAN
# Incident pipeline — v5 SCAFFOLD for declarative ADK 2.0 SequentialAgent.
#
# Why this is a scaffold (NotImplementedError) rather than a working factory:
# ADK 2.0 enforces one-parent-per-agent — the specialist instances
# (stream_watcher_agent, audio_agent, species_id_agent, falsifier_agent,
# peer_fanout_agent) are already parented to root_agent in app/agent.py.
# A SequentialAgent that reused them would crash at import.
#
# The clean v5 path is to expose `build_*()` factories on each specialist
# module that return FRESH instances, so this pipeline can construct an
# unparented chain for ADK Eval / Memory Bank runs. Those factories don't
# exist yet, so build_incident_pipeline() raises NotImplementedError with
# a clear roadmap message instead of failing on ImportError.
#
# Audited 2026-05-17 (CODEX_MOVE_7_V4.md BLOCK 1): the prior version
# silently imported non-existent build_* helpers — dead code.
# This version makes the v5 dependency explicit.

from __future__ import annotations

PIPELINE_TOPOLOGY = (
    "stream_watcher -> audio_agent -> species_id -> falsifier -> "
    "peer_fanout (ParallelAgent of 4 A2A peer callers)"
)


def build_incident_pipeline():
    """Construct a fresh SequentialAgent for ADK Eval / Memory Bank.

    Not yet implemented — depends on per-specialist build_* factories that
    ship in v5. The topology this pipeline will encode is fixed and lives
    in PIPELINE_TOPOLOGY for reviewers + the marketplace listing.

    Why not implemented in v4:
        Each specialist agent module currently exports a single module-level
        global (e.g. `audio_agent`) parented to root_agent. ADK 2.0 enforces
        one-parent-per-agent, so a SequentialAgent wrapping the same instances
        would crash at import. The v5 fix is to add `build_audio_agent()`
        etc. factories that return unparented copies on demand.

    See: reviews/CODEX_MOVE_7_V4.md (BLOCK 1) for context.
    """
    raise NotImplementedError(
        "build_incident_pipeline is a v5 scaffold. Required dependencies "
        "(build_audio_agent, build_falsifier_agent, build_peer_fanout_agent, "
        "build_species_id_agent, build_stream_watcher_agent) ship in v5. "
        f"Topology: {PIPELINE_TOPOLOGY}."
    )
