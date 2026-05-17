"""Generate ElevenLabs agent intro + Falsifier dissent narration for v3.2.

PLAN_V3_2 sub-move 7.4. Pre-generates short narrations played in the
Agent Theater tab + Falsifier Tribunal expansion. Avoids browser
SpeechSynthesis fallback (worse voice quality, inconsistent across browsers).

Usage:
    uv run python scripts/assets/generate-elevenlabs-agent-voices.py
    uv run python scripts/assets/generate-elevenlabs-agent-voices.py --force

Reads ELEVENLABS_API_KEY from ops-center/.env.local.
Cost: ~9 clips × ~50 chars × $0.18/1K chars ≈ $0.10 total.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_DIR = Path("ops-center/public/voices")

# Default ElevenLabs voice IDs (well-known public). Override via env if needed.
# Orchestrator + sub-agents share an authoritative calm voice (Adam).
# Falsifier gets a darker timbre (Daniel) to feel adversarial. Codex amendment.
VOICE_ORCH = os.environ.get("ELEVENLABS_VOICE_ORCH", "pNInz6obpgDQGcFmaJgB")  # Adam
VOICE_FALS = os.environ.get("ELEVENLABS_VOICE_FALSIFIER", "onwK4e9ZLuTAKqWW03F9")  # Daniel

LINES: list[tuple[str, str, str]] = [
    # (filename, voice_id, text)
    ("intro-root_agent.mp3", VOICE_ORCH,
     "I am the orchestrator. I route signals to specialists and coordinate the dispatch."),
    ("intro-stream_watcher.mp3", VOICE_ORCH,
     "Stream Watcher. I analyze camera feeds in real time and flag threats."),
    ("intro-audio_agent.mp3", VOICE_ORCH,
     "Audio Agent. I classify acoustic signatures — gunshots, vehicle engines, distress calls."),
    ("intro-species_id.mp3", VOICE_ORCH,
     "Species I-D. I identify species and ground findings in the conservation corpus."),
    ("intro-court_evidence.mp3", VOICE_ORCH,
     "Court Evidence. I package every action into a chain-of-custody packet for the auditor."),
    ("intro-falsifier.mp3", VOICE_FALS,
     "Falsifier. I challenge every dispatch before action. My dissent ships in the audit trail."),
    # Per-scenario Falsifier dissent
    ("dissent-stale-timestamp.mp3", VOICE_FALS,
     "Dissent. The observation timestamp drift exceeds the one-hour freshness gate. This may be a replay event. Recommend human verification before dispatch."),
    ("dissent-low-audio-conf.mp3", VOICE_FALS,
     "Dissent. Audio confidence sits below the critical-severity threshold. The signal does not yet justify a critical-class response."),
    ("concur-clean-dispatch.mp3", VOICE_ORCH,
     "Falsifier concurs. All standard-operating-procedure gates pass. Dispatch authorized."),
]


def _load_env() -> None:
    """Load ELEVENLABS_API_KEY from ops-center/.env.local if not already set."""
    if os.environ.get("ELEVENLABS_API_KEY"):
        return
    env = Path("ops-center/.env.local")
    if not env.is_file():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def synth(voice_id: str, text: str, out_path: Path) -> None:
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY missing. Add it to ops-center/.env.local.")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    body = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.85, "style": 0.30, "use_speaker_boost": True},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(resp.read())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    _load_env()

    log.info("Generating %d ElevenLabs agent voices...", len(LINES))
    for filename, voice_id, text in LINES:
        out_path = OUT_DIR / filename
        if out_path.exists() and not args.force:
            log.info("  skip %s (exists)", filename)
            continue
        log.info("  synth %s ...", filename)
        try:
            synth(voice_id, text, out_path)
            log.info("    wrote %s (%.1f KB)", out_path, out_path.stat().st_size / 1024)
        except Exception as e:
            log.error("    error %s: %s", filename, e)
    log.info("Done. Outputs in %s", OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
