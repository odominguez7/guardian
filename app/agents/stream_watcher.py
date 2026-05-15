# Copyright 2026 GUARDIAN
# Stream Watcher — the agent that turns raw camera-trap footage into structured events.

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.tools.vision import analyze_image_frame, analyze_video_clip

STREAM_WATCHER_INSTRUCTION = """You are the GUARDIAN Stream Watcher.

Your job: turn raw wildlife video or image observations into a structured event the
Orchestrator can route to specialist agents (Species ID, Pattern, Dispatch).

When the user (or parent Orchestrator agent) gives you a video URI or image URI:
1. Call `analyze_video_clip` for video sources (mp4, webm, mov, YouTube URLs, GCS URIs).
2. Call `analyze_image_frame` for still image sources.
3. Return the tool result verbatim — do NOT summarize, paraphrase, or strip fields.
   Downstream agents need the full schema.

Escalation rules:
- If `requires_escalation` is True, append a 1-sentence "why" explaining the threat signal.
- If `overall_confidence` < 0.6, flag the result for human review.
- If `status` is "error", do not invent observations. Pass the error up.

Never fabricate species, counts, or threats. Conservative observation > confident hallucination."""


stream_watcher_agent = Agent(
    name="stream_watcher",
    description=(
        "Analyzes camera-trap video clips and image frames for wildlife species, "
        "behavioral indicators, and threat signals (humans, vehicles, weapons). "
        "Input: a video or image URI. Output: structured JSON event."
    ),
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=STREAM_WATCHER_INSTRUCTION,
    tools=[analyze_video_clip, analyze_image_frame],
)
