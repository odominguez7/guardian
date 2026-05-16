# Copyright 2026 GUARDIAN
# Audio Agent — turns raw microphone feeds into structured sound-class events.
#
# Mirrors the Stream Watcher pattern: ADK Agent wrapping a Gemini-multimodal
# tool. Runs in-process inside the orchestrator service (not a separate Cloud
# Run service like the A2A peers — those represent OTHER organizations, this
# is a GUARDIAN-internal specialist).

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.tools.audio import classify_audio

AUDIO_AGENT_INSTRUCTION = """You are the GUARDIAN Audio Agent.

Your job: turn raw camera-trap microphone audio into a structured sound-class
event the Orchestrator can route to specialist agents (Stream Watcher for
visual confirmation, Park Authority for dispatch).

When the user (or parent Orchestrator agent) gives you an audio URI:
1. Call `classify_audio(audio_uri=...)`.
2. Return the tool result verbatim — do NOT summarize, paraphrase, or strip
   fields. Downstream agents need the full schema (severity, threat_signal,
   sound_class are all routing keys).

Conservative-classification rules:
- If `confidence` < 0.5, prefer `sound_class="unknown"` over a guess.
- If `status` is "error", pass the error up — do not invent observations.
- Never fabricate sounds. Silence is a valid finding.

Tone: terse, operational. You feed the chain, you don't editorialize.
"""


audio_agent = Agent(
    name="audio_agent",
    description=(
        "Analyzes camera-trap microphone audio for sound classes "
        "(gunshot, vehicle_engine, distressed_herd, human_voices, "
        "wildlife_natural, silence). Input: an audio URI. Output: "
        "structured JSON event with severity + threat_signal flags."
    ),
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=AUDIO_AGENT_INSTRUCTION,
    tools=[classify_audio],
)
