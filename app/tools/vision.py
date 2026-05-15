# Copyright 2026 GUARDIAN
# Vision analysis tools — wraps Gemini Vision for wildlife scene understanding.

import json
import os
from typing import Optional

import google.auth
from google import genai
from google.genai import types as genai_types

# Configure Vertex AI client once at import time.
_, _PROJECT_ID = google.auth.default()
_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
_client = genai.Client(vertexai=True, project=_PROJECT_ID, location=_LOCATION)

# Use Flash for high-volume frame analysis. Pro for tough scenes (e.g., low-light).
_DEFAULT_VISION_MODEL = "gemini-2.5-flash"

_STREAM_WATCHER_PROMPT = """You are GUARDIAN's Stream Watcher, a wildlife camera-trap analyst.

Analyze the provided video clip or image. Return a SINGLE JSON object — no prose, no markdown — with this schema:

{
  "species": [{"name": str, "common_name": str, "count": int, "confidence": float}],
  "total_animal_count": int,
  "behaviors": [str],                  // e.g. ["grazing", "alert posture", "fleeing"]
  "threat_signals": [str],              // e.g. ["human silhouette", "vehicle headlights", "gunshot residue"], empty if none
  "time_of_day_inference": str,         // "dawn" | "day" | "dusk" | "night" | "unknown"
  "environmental_context": str,         // brief: terrain, weather, vegetation
  "overall_confidence": float,          // 0.0 - 1.0
  "requires_escalation": bool,          // true if threat_signals non-empty OR low confidence
  "raw_observations": str               // 1-2 sentence free-text summary
}

Be conservative: if uncertain, lower confidence and flag for escalation. Never invent species you cannot identify.
"""


def analyze_video_clip(video_uri: str) -> dict:
    """Analyze a wildlife video clip for species, behavior, and threat signals.

    Use this tool when given a camera-trap clip, ranger body-cam footage, or any
    short wildlife video. Returns a structured event the Orchestrator can route
    to specialist agents (Species ID, Pattern, Dispatch).

    Args:
        video_uri: A video source. Supports:
            - gs://bucket/path.mp4  (Cloud Storage URI)
            - https://example.com/clip.mp4 (public HTTP URL)
            - https://youtu.be/...  (YouTube URL — Gemini-native support)

    Returns:
        Dict matching the Stream Watcher schema:
          - species: list of {name, common_name, count, confidence}
          - total_animal_count: int
          - behaviors: list of behavioral tags
          - threat_signals: list of detected threats (humans, vehicles, weapons)
          - time_of_day_inference: dawn|day|dusk|night|unknown
          - environmental_context: short str
          - overall_confidence: 0.0-1.0
          - requires_escalation: bool
          - raw_observations: 1-2 sentence summary
          - status: "ok" | "error"
          - error: str (if status=error)
    """
    if not video_uri:
        return {"status": "error", "error": "video_uri is required"}

    try:
        part = _build_video_part(video_uri)
        response = _client.models.generate_content(
            model=_DEFAULT_VISION_MODEL,
            contents=[part, _STREAM_WATCHER_PROMPT],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        parsed = json.loads(response.text)
        parsed["status"] = "ok"
        parsed["_source_uri"] = video_uri
        parsed["_model"] = _DEFAULT_VISION_MODEL
        return parsed
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error": f"Model returned non-JSON output: {e}",
            "_raw_text": getattr(response, "text", "")[:500] if "response" in locals() else "",
        }
    except Exception as e:
        return {"status": "error", "error": f"{type(e).__name__}: {e}"}


def analyze_image_frame(image_uri: str, focus: Optional[str] = None) -> dict:
    """Analyze a single image frame from a camera trap or ranger photo.

    Useful when the source is a still image rather than video, or when the
    Orchestrator wants to drill into a specific frame surfaced by the video tool.

    Args:
        image_uri: gs://, https://, or data URI to an image (JPEG/PNG/WEBP).
        focus: Optional focus instruction (e.g., "identify the individual elephant
            by ear notches" or "look for human presence").

    Returns:
        Same schema as analyze_video_clip but for a single frame.
    """
    if not image_uri:
        return {"status": "error", "error": "image_uri is required"}

    instruction = _STREAM_WATCHER_PROMPT
    if focus:
        instruction += f"\n\nADDITIONAL FOCUS: {focus}"

    try:
        part = _build_image_part(image_uri)
        response = _client.models.generate_content(
            model=_DEFAULT_VISION_MODEL,
            contents=[part, instruction],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        parsed = json.loads(response.text)
        parsed["status"] = "ok"
        parsed["_source_uri"] = image_uri
        parsed["_model"] = _DEFAULT_VISION_MODEL
        return parsed
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error": f"Model returned non-JSON output: {e}",
            "_raw_text": getattr(response, "text", "")[:500] if "response" in locals() else "",
        }
    except Exception as e:
        return {"status": "error", "error": f"{type(e).__name__}: {e}"}


def _build_video_part(uri: str) -> genai_types.Part:
    mime = _infer_video_mime(uri)
    return genai_types.Part.from_uri(file_uri=uri, mime_type=mime)


def _build_image_part(uri: str) -> genai_types.Part:
    mime = _infer_image_mime(uri)
    return genai_types.Part.from_uri(file_uri=uri, mime_type=mime)


def _infer_video_mime(uri: str) -> str:
    lower = uri.lower()
    if "youtube.com" in lower or "youtu.be" in lower:
        return "video/mp4"  # Gemini treats YouTube URIs specially regardless
    if lower.endswith(".webm"):
        return "video/webm"
    if lower.endswith(".mov"):
        return "video/quicktime"
    if lower.endswith(".mkv"):
        return "video/x-matroska"
    return "video/mp4"


def _infer_image_mime(uri: str) -> str:
    lower = uri.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"
