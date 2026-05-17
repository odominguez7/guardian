"""Generate a Lyria 2 ambient bed for the Ops Center page-load loop.

PLAN_V3.md Move 2.1. Ships a 30s seamless ambient drone that loops in the
Ops Center hero panel + serves as the music bed under the demo video VO.

Usage:
    uv run python scripts/assets/generate-lyria-bed.py

Idempotent: skips generation if output already exists. Override with --force.

Cost: ~$0.06 / generation. One-shot.
"""

from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import subprocess
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_WAV = Path("video-assets/music/guardian-ambient-30s.wav")
OUT_MP3 = Path("video-assets/music/guardian-ambient-30s.mp3")

# Lyria 2 prompt — defended in PLAN_V3.md Move 2.1.
# Style: NASA-mission-control + Studio Ghibli ambient. Low drone bed at ~70-80
# BPM, no melodic earworm, no percussion that competes with VO. The reference
# is the soundtrack to Patagonia documentaries — wide, deliberate, calm.
PROMPT = (
    "Ambient cinematic drone, low and slow, 70 BPM, deep sustained strings "
    "and pad textures, no percussion, no melody, no vocals. Hushed, "
    "contemplative, dignified. Operating-room-quiet with a faint pulse — "
    "the sound of a watchful system. Mix at -28 dBFS leaving room for "
    "spoken voiceover. Suitable for seamless looping."
)

DURATION_SECONDS = 30  # Lyria 2 max single-shot per Vertex AI docs ~30s.


def _project_id() -> str:
    return os.environ.get("GOOGLE_CLOUD_PROJECT") or "guardian-gfs-2026"


def _location() -> str:
    return os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")


def _gcloud_token() -> str:
    out = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        check=True, capture_output=True, text=True,
    )
    return out.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="Re-generate even if output exists (re-bills ~$0.06).")
    args = parser.parse_args()

    if OUT_WAV.exists() and OUT_MP3.exists() and not args.force:
        log.info("Lyria bed already exists at %s + %s — skipping. "
                 "Use --force to regenerate.", OUT_WAV, OUT_MP3)
        return 0

    OUT_WAV.parent.mkdir(parents=True, exist_ok=True)
    log.info("Generating Lyria 2 ambient bed (%ds, ~$0.06)...", DURATION_SECONDS)
    log.info("  project=%s location=%s", _project_id(), _location())
    log.info("  prompt: %s...", PROMPT[:80])

    # The genai SDK 1.73 has no client.models.generate_audio; Lyria 2 is
    # exposed via the Vertex AI publisher-models predict REST endpoint.
    url = (
        f"https://{_location()}-aiplatform.googleapis.com/v1/projects/"
        f"{_project_id()}/locations/{_location()}/publishers/google/"
        f"models/lyria-002:predict"
    )
    body = json.dumps({
        "instances": [{"prompt": PROMPT}],
        "parameters": {
            "sample_count": 1,
            "duration_seconds": DURATION_SECONDS,
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {_gcloud_token()}",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # Predict response shape (Vertex publisher models): predictions[0].bytesBase64Encoded
    if "predictions" not in data or not data["predictions"]:
        raise RuntimeError(f"Lyria response missing predictions: {data!r}")
    pred = data["predictions"][0]
    audio_b64 = pred.get("bytesBase64Encoded") or pred.get("audioContent")
    if not audio_b64:
        raise RuntimeError(
            f"Lyria response has no bytesBase64Encoded / audioContent. Keys: {list(pred.keys())}"
        )

    # Lyria 2 returns 48 kHz / 16-bit / stereo WAV bytes. Keep the WAV as the
    # source-of-truth artifact, then re-encode to MP3 for browser delivery
    # (smaller payload, every browser supports it).
    OUT_WAV.write_bytes(base64.b64decode(audio_b64))
    log.info("Wrote %s (%.1f KB, WAV source)", OUT_WAV, OUT_WAV.stat().st_size / 1024)

    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(OUT_WAV),
            "-codec:a", "libmp3lame", "-b:a", "128k", "-ac", "2",
            str(OUT_MP3),
        ],
        check=True,
    )
    log.info("Wrote %s (%.1f KB, MP3 for browser)", OUT_MP3, OUT_MP3.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
