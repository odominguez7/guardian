# Copyright 2026 GUARDIAN
# Audio analysis tools — Gemini multimodal classifier for camera-trap microphone feeds.
#
# Sound classes the demo cares about (each maps to an action by the orchestrator):
#   - "gunshot"            -> critical, fan-out to all 4 peers
#   - "vehicle_engine"     -> high, fan-out
#   - "distressed_herd"    -> high, fan-out
#   - "human_voices"       -> medium, dispatch only
#   - "wildlife_natural"   -> info, no fan-out
#   - "silence"            -> info, no fan-out

import json
import logging
import os

import google.auth
from google import genai
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

_DEFAULT_AUDIO_MODEL = os.environ.get("AUDIO_AGENT_MODEL", "gemini-2.5-flash")
_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

_client: "genai.Client | None" = None


def _get_client() -> "genai.Client":
    global _client
    if _client is None:
        _, project_id = google.auth.default()
        _client = genai.Client(vertexai=True, project=project_id, location=_LOCATION)
    return _client


_AUDIO_CLASSIFIER_PROMPT = """You are GUARDIAN's Audio Agent, a camera-trap microphone analyst.

Listen to the provided audio clip. Return a SINGLE JSON object — no prose, no markdown — with this schema:

{
  "sound_class": str,                  // one of: gunshot | vehicle_engine | distressed_herd | human_voices | wildlife_natural | silence | unknown
  "confidence": float,                 // 0.0 - 1.0
  "threat_signal": bool,               // true if sound_class is gunshot/vehicle_engine/distressed_herd/human_voices
  "secondary_sounds": [str],            // other audible sounds in priority order
  "estimated_distance_m": int,         // best-guess meters; 0 if unknown
  "duration_inference_s": float,       // approximate clip duration in seconds
  "explanation": str,                  // 1-sentence rationale a ranger would understand
  "severity": str                      // critical | high | medium | low | info
}

Severity mapping:
  - gunshot                  -> critical
  - vehicle_engine           -> high
  - distressed_herd          -> high
  - human_voices in restricted area -> medium
  - wildlife_natural         -> info
  - silence / unknown        -> info

Be conservative. If you cannot identify the sound with >0.5 confidence, return sound_class="unknown" and severity="info".
Never invent sounds you don't actually hear in the clip.
"""


def classify_audio(audio_uri: str) -> dict:
    """Classify a camera-trap microphone clip into one of GUARDIAN's sound classes.

    Use this tool when given an audio URL (gs://, https://, or data URI) from a
    camera-trap microphone, ranger body-cam audio, or any short wildlife audio
    recording. Returns a structured event the Orchestrator can route to
    specialist agents (Stream Watcher for visual confirmation, Park Authority
    for dispatch).

    Args:
        audio_uri: An audio source. Supports:
            - gs://bucket/path.mp3
            - https://example.com/clip.wav (public HTTP URL)
            - data:audio/mp3;base64,...

    Returns:
        Dict matching the Audio Agent schema with keys:
            status, sound_class, confidence, threat_signal, secondary_sounds,
            estimated_distance_m, duration_inference_s, explanation, severity,
            _source_uri, _model. status="error" with error field on failure.
    """
    if not audio_uri:
        return {"status": "error", "error": "audio_uri is required"}

    try:
        part = _build_audio_part(audio_uri)
        response = _get_client().models.generate_content(
            model=_DEFAULT_AUDIO_MODEL,
            contents=[part, _AUDIO_CLASSIFIER_PROMPT],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        parsed = json.loads(response.text)
        parsed["status"] = "ok"
        parsed["_source_uri"] = audio_uri
        parsed["_model"] = _DEFAULT_AUDIO_MODEL
        return parsed
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error": f"Model returned non-JSON output: {e}",
            "_raw_text": getattr(response, "text", "")[:500] if "response" in locals() else "",
        }
    except Exception as e:
        logger.warning("classify_audio failed for %s: %s", audio_uri, e)
        return {"status": "error", "error": f"{type(e).__name__}: {e}"}


def _build_audio_part(uri: str) -> genai_types.Part:
    mime = _infer_audio_mime(uri)
    return genai_types.Part.from_uri(file_uri=uri, mime_type=mime)


def _infer_audio_mime(uri: str) -> str:
    lower = uri.lower()
    if lower.endswith(".wav"):
        return "audio/wav"
    if lower.endswith(".ogg"):
        return "audio/ogg"
    if lower.endswith(".flac"):
        return "audio/flac"
    if lower.endswith(".m4a") or lower.endswith(".aac"):
        return "audio/aac"
    return "audio/mpeg"
