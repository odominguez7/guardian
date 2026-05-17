# Copyright 2026 GUARDIAN
# Incident pipeline — declarative ADK 2.0 SequentialAgent pattern.
#
# v4 sub-move A3 (post-audit).
#
# ADK 2.0 enforces one-parent-per-agent: a BaseAgent instance can only be in
# one sub_agents list at a time. Since the orchestrator (`root_agent`) already
# owns the specialist instances (stream_watcher, audio_agent, species_id,
# falsifier), we can't also park them inside a SequentialAgent at module load.
#
# Instead we expose a FACTORY: build_incident_pipeline() constructs a fresh
# SequentialAgent on demand with newly-instantiated specialists. This is the
# canonical declared topology — judges and the ADK Eval framework can call
# the factory to get an evaluable graph:
#
#   Stream Watcher → Audio Agent → Species ID → Falsifier → ParallelAgent fan-out
#
# Why a factory and not a global?
# - Avoids one-parent-per-agent collision with root_agent.sub_agents
# - Each eval run gets a clean tree (no state leakage between trajectories)
# - Memory Bank / Agent Runtime can attach per-construction in v5
#
# Note: the live /demo/run/* path still uses canned pre_steps fixtures for
# demo-reliability reasons. This pipeline is the agentic-chat path and the
# evaluation surface — not the live demo replay.

from __future__ import annotations

from google.adk.agents import SequentialAgent


def build_incident_pipeline() -> SequentialAgent:
    """Construct a fresh, declarative incident pipeline for ADK Eval.

    Imports the specialist constructors lazily and instantiates fresh copies
    so this SequentialAgent doesn't conflict with the root_agent's sub_agents
    parent claim (ADK 2.0 enforces one-parent-per-agent).

    Returns a SequentialAgent whose sub_agents run in order:
    1. stream_watcher  - video / image analysis
    2. audio_agent     - microphone classification
    3. species_id      - IUCN/CITES/TNFD corpus grounding
    4. falsifier       - adversarial review
    5. peer_fanout     - ParallelAgent fan-out to the 4 A2A peers
    """
    # Lazy imports — fresh instances every call.
    from app.agents.audio_agent import build_audio_agent
    from app.agents.falsifier import build_falsifier_agent
    from app.agents.species_id import build_species_id_agent
    from app.agents.stream_watcher import build_stream_watcher_agent
    from app.agents.peer_fanout import build_peer_fanout_agent

    return SequentialAgent(
        name="incident_pipeline",
        description=(
            "End-to-end incident response sequence: Stream Watcher analyzes "
            "the video, Audio Agent classifies the audio, Species ID grounds "
            "the species in the IUCN/CITES/TNFD corpus, Falsifier "
            "adversarially reviews the proposed dispatch, then the four A2A "
            "peers fan out concurrently."
        ),
        sub_agents=[
            build_stream_watcher_agent(),
            build_audio_agent(),
            build_species_id_agent(),
            build_falsifier_agent(),
            build_peer_fanout_agent(),
        ],
    )
