"""Generate the Veo 3.1 Fast hero loop for the Ops Center idle panel + video cold-open.

PLAN_V3.md Move 2.3. 6-second photoreal clip: African elephant herd at dusk
near a camera trap. Replaces the Pexels stock footage in the demo video's
cold open and plays in the Ops Center hero region when idle.

Usage:
    uv run python scripts/assets/generate-veo-hero.py
    uv run python scripts/assets/generate-veo-hero.py --force

Idempotent: skips if output exists. Override with --force.

Cost: $0.10/sec × 6s = $0.60. One-shot, slow (8-15 min wall).
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import time
from pathlib import Path

from google import genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_PATH = Path("video-assets/broll/guardian-hero-6s.mp4")

VEO_MODEL = "veo-3.1-fast-generate-001"
DURATION_SECONDS = 6  # Valid: {4, 6, 8}
ASPECT_RATIO = "16:9"

# Veo prompt — defended in PLAN_V3.md Move 2.3. Goal is documentary realism,
# not slow-mo / overcooked stock-video aesthetic. Reference: Planet Earth II
# evening shots near watering holes.
PROMPT = (
    "Cinematic photoreal aerial drone shot at dusk, slowly descending toward "
    "a herd of African elephants moving across savanna grassland. Soft "
    "golden-hour light, long shadows, low atmospheric haze. A single fixed "
    "camera-trap pole stands in the foreground at a respectful distance, "
    "small red status LED blinking. Wide framing. No people, no vehicles, "
    "no logos. Steady, deliberate, documentary tone — Planet Earth II "
    "aesthetic. 16:9, 1080p, no audio."
)


def _project_id() -> str:
    return os.environ.get("GOOGLE_CLOUD_PROJECT") or "guardian-gfs-2026"


def _location() -> str:
    return os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="Re-generate even if output exists (re-bills $0.60).")
    args = parser.parse_args()

    if OUT_PATH.exists() and not args.force:
        log.info("Veo hero already exists at %s (size %.1f MB) — skipping. "
                 "Use --force to regenerate.",
                 OUT_PATH, OUT_PATH.stat().st_size / 1024 / 1024)
        return 0

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    log.info("Submitting Veo 3.1 Fast render (%ds, %s, %s, ~$%.2f, 8-15 min wall)...",
             DURATION_SECONDS, ASPECT_RATIO, VEO_MODEL, 0.10 * DURATION_SECONDS)

    client = genai.Client(vertexai=True, project=_project_id(), location=_location())
    operation = client.models.generate_videos(
        model=VEO_MODEL,
        prompt=PROMPT,
        config={
            "aspect_ratio": ASPECT_RATIO,
            "duration_seconds": DURATION_SECONDS,
            "generate_audio": False,
            "number_of_videos": 1,
            "person_generation": "allow_adult",
        },
    )
    log.info("  operation submitted: %s", getattr(operation, "name", "<no name>"))

    started = time.time()
    while not operation.done:
        if time.time() - started > 900:  # 15 min timeout
            raise TimeoutError(f"Veo render exceeded 15 min")
        time.sleep(10)
        operation = client.operations.get(operation)
        log.info("  ... polling (%.0fs elapsed)", time.time() - started)

    if operation.error:
        raise RuntimeError(f"Veo render failed: {operation.error}")

    # Veo 3.1 Fast returns inline bytes via `video_bytes`; older v3.0 returned
    # a GCS URI. Support both.
    video = operation.response.generated_videos[0].video
    video_bytes = getattr(video, "video_bytes", None)
    video_uri = getattr(video, "uri", None)
    if video_bytes:
        OUT_PATH.write_bytes(video_bytes)
    elif video_uri:
        subprocess.run(["gsutil", "cp", video_uri, str(OUT_PATH)], check=True)
    else:
        raise RuntimeError(
            f"Veo response has neither video_bytes nor uri. Available attrs: "
            f"{[a for a in dir(video) if not a.startswith('_')]}"
        )

    log.info("Wrote %s (%.1f MB) in %.0fs wall",
             OUT_PATH, OUT_PATH.stat().st_size / 1024 / 1024, time.time() - started)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
