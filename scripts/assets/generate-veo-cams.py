"""Generate 4 Veo 3.1 Fast wildlife clips for the v3.2 Live Cams tab.

PLAN_V3_2 sub-move 7.2. Pre-renders short loops representing the 4
camera-trap perspectives the user sees in the Live Cams tab.

Usage:
    uv run python scripts/assets/generate-veo-cams.py

Idempotent: skips clips that already exist. Cost: 4 × $0.60 = $2.40.
Wall time: ~30-60 min total (Veo Fast is 3-15 min per clip).
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from google import genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_DIR = Path("ops-center/public/cams")
VEO_MODEL = "veo-3.1-fast-generate-001"

CLIPS = {
    "elephant-dusk": (
        "Cinematic photoreal aerial drone shot at dusk over African savanna, "
        "a herd of African elephants moving slowly across golden grassland, "
        "low atmospheric haze, long shadows, distant baobab silhouettes. "
        "Wide framing, no people, no vehicles, no logos, no text. "
        "Steady deliberate motion. 16:9 1080p documentary aesthetic, no audio."
    ),
    "cheetah-crossing": (
        "Photoreal ground-level shot of a cheetah crossing dry savanna grass "
        "in late afternoon sun, the cat alert, ears forward, scanning the "
        "horizon. Soft golden light, shallow depth of field on cheetah. "
        "No humans, no vehicles, no logos. 16:9 1080p, no audio."
    ),
    "vehicle-night": (
        "Infrared night-vision camera-trap perspective looking down a dirt "
        "track in African bush. A pickup truck silhouette in the distance "
        "emerges with headlights cutting through scrub. Green-monochrome IR "
        "look, slight digital scan lines, distant vehicle small and "
        "unidentified. No people visible, no logos. 16:9 1080p, no audio."
    ),
    "trap-perspective": (
        "Static low-angle fixed camera-trap point-of-view in dense African "
        "bushland at dawn. Foreground a thin pole, small red status LED "
        "blinking. Background gentle morning mist over grass and acacia. "
        "Bird flits across frame mid-clip. Naturalistic documentary feel. "
        "No humans, no vehicles, no logos, no text. 16:9 1080p, no audio."
    ),
}


def _project_id() -> str:
    return os.environ.get("GOOGLE_CLOUD_PROJECT") or "guardian-gfs-2026"


def _location() -> str:
    return os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")


def render_one(client, name: str, prompt: str, force: bool) -> str:
    out_path = OUT_DIR / f"{name}.mp4"
    if out_path.exists() and not force:
        return f"skip {name} (exists, {out_path.stat().st_size / 1024 / 1024:.1f} MB)"
    started = time.time()
    log.info("  submit Veo: %s", name)
    op = client.models.generate_videos(
        model=VEO_MODEL,
        prompt=prompt,
        config={
            "aspect_ratio": "16:9",
            "duration_seconds": 6,
            "generate_audio": False,
            "number_of_videos": 1,
            "person_generation": "allow_adult",
        },
    )
    while not op.done:
        if time.time() - started > 1200:  # 20 min timeout
            return f"timeout {name}"
        time.sleep(15)
        op = client.operations.get(op)
    if op.error:
        return f"error {name}: {op.error}"
    video = op.response.generated_videos[0].video
    vb = getattr(video, "video_bytes", None)
    uri = getattr(video, "uri", None)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if vb:
        out_path.write_bytes(vb)
    elif uri:
        subprocess.run(["gsutil", "cp", uri, str(out_path)], check=True)
    else:
        return f"error {name}: no bytes/uri"
    return f"ok {name} ({out_path.stat().st_size / 1024 / 1024:.1f} MB, {time.time() - started:.0f}s)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--parallel", type=int, default=2)
    args = parser.parse_args()

    log.info("Generating %d Veo cams (~$%.2f, ~30-60 min wall)…",
             len(CLIPS), 0.60 * len(CLIPS))
    log.info("  project=%s location=%s parallel=%d", _project_id(), _location(), args.parallel)
    client = genai.Client(vertexai=True, project=_project_id(), location=_location())

    with ThreadPoolExecutor(max_workers=args.parallel) as ex:
        futures = {ex.submit(render_one, client, n, p, args.force): n for n, p in CLIPS.items()}
        for fut in as_completed(futures):
            log.info("  ← %s", fut.result())

    log.info("Done. Outputs in %s", OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
