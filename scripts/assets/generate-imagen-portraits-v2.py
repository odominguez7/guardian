"""Generate Imagen 4 PHOTO-REAL agent portraits for Mission Bridge v2.

Producer feedback 2026-05-17: "the cards and the icons" (v1 silhouette set)
felt static. Wanted photo-realistic faces that explain the agents'
character more vividly. v2 outputs to ops-center/public/portraits-v2/.

The v1 portraits stay committed at ops-center/public/portraits/ as a
fallback — MissionBridge.tsx reads ?bridge=v1 or ?bridge=v2 query param
to pick which set to render. Per codex master-plan WARN: A/B fallback so
Day 2 isn't lost if realistic faces feel uncanny.

Usage:
    uv run python scripts/assets/generate-imagen-portraits-v2.py
    uv run python scripts/assets/generate-imagen-portraits-v2.py --force

Cost: ~$0.04 × 10 = $0.40. Imagen 4 is non-deterministic (no seed param),
so committed PNGs are the source of truth — don't --force casually.
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from google import genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_DIR = Path("ops-center/public/portraits-v2")

# Shared style frame — documentary headshot photography. Headshot framing
# (chest-up, eyes engaging the camera) is the most reliable Imagen output
# for "trustworthy professional" without uncanny-valley. Cinematic lighting
# pulls the silhouette out of background.
_BASE_STYLE = (
    "Cinematic documentary photograph, professional headshot framing "
    "chest-up, sharp eye contact with camera, hyperdetailed face, "
    "subtle dramatic key-light from one side, soft cool-tone shadow on "
    "the other, slight bokeh background, no logos, no text, photo-real "
    "skin texture, museum-quality editorial portrait, 1:1 framing."
)

# 10 agents, each with a role + visual cue + accent color sentence.
# Diverse cast deliberately reflected in prompts so judges + viewers see
# a global multi-org coordination team, not one demographic.
PORTRAITS = {
    "root_agent": (
        "A composed senior operations director in their 40s of South Asian "
        "descent, dark blazer over an open collar, looking calmly at the "
        "camera from a dim control center, amber wallscreens glowing "
        "softly out of focus behind them. Trustworthy authority, "
        "system-wide oversight."
    ),
    "stream_watcher": (
        "A focused Black female computer vision engineer in her 30s "
        "wearing technical layers, looking attentively at the camera, "
        "subtle sky-blue rim light from a wall of monitors behind her, "
        "alert and patient."
    ),
    "audio_agent": (
        "A bioacoustics analyst in their 30s of Latin descent, wearing "
        "studio-quality over-ear headphones around their neck, looking "
        "at the camera with quiet intensity, violet panel light catching "
        "the edge of the frame, intelligent focus."
    ),
    "species_id": (
        "A field biologist in their late 20s, East Asian descent, in "
        "earth-toned outdoor research clothing, holding a field notebook, "
        "warm emerald background bokeh suggesting forest canopy, "
        "looking at the camera with curious expertise."
    ),
    "court_evidence": (
        "A meticulous archival forensic analyst in their 40s, Middle "
        "Eastern descent, wearing wire-frame glasses and a slate-blue "
        "button-down, holding a sealed chain-of-custody envelope just "
        "visible at the bottom of the frame, looking at the camera with "
        "careful attention, courtroom-noir lighting."
    ),
    "falsifier": (
        "An incisive internal auditor in their 50s, white-haired, sharp "
        "features, wearing a dark high-collared garment, single rose-red "
        "accent light catching the edge of the frame from one side against "
        "deep black background, posture suggesting skeptical questioning. "
        "Adversarial counter-stage character — sharp but fair."
    ),
    "park_service": (
        "A weathered African park ranger in their 40s wearing a tan "
        "uniform shirt with shoulder radio, looking at the camera with "
        "calm command authority, warm orange dust-haze of an East African "
        "savanna at golden hour behind them."
    ),
    "sponsor_sustainability": (
        "A poised corporate sustainability officer in their 30s, mixed-"
        "race, wearing a tailored navy suit, looking at the camera with "
        "executive composure, warm board-room teak paneling soft in the "
        "background, subtle gold accent light."
    ),
    "funder_reporter": (
        "A compassionate conservation foundation program officer in "
        "their 50s of European descent, silver hair, wearing a soft "
        "lavender knit, looking at the camera with empathetic resolve, "
        "warm Geneva office light filtering through window blinds behind."
    ),
    "neighbor_park": (
        "A Kenyan cross-border park liaison in their 30s, wearing field "
        "gear and a satellite-phone clip, looking at the camera with "
        "collaborative warmth, teal Maasai Mara escarpment background "
        "softly out of focus."
    ),
}


def _project_id() -> str:
    return os.environ.get("GOOGLE_CLOUD_PROJECT") or "guardian-gfs-2026"


def _location() -> str:
    return os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="Re-generate all portraits (re-bills ~$0.40 total).")
    parser.add_argument(
        "--only", action="append", default=None,
        help="Limit to specific agent ids (repeatable).",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    to_generate = []
    for agent, body in PORTRAITS.items():
        if args.only and agent not in args.only:
            continue
        out_path = OUT_DIR / f"{agent}.png"
        if out_path.exists() and not args.force:
            log.info("Skip %s (exists, %d bytes)", out_path, out_path.stat().st_size)
            continue
        to_generate.append((agent, body, out_path))

    if not to_generate:
        log.info("All v2 portraits already generated. Use --force to re-bill.")
        return 0

    log.info("Generating %d Imagen 4 photo-real portraits (~$%.2f)...",
             len(to_generate), 0.04 * len(to_generate))
    log.info("  project=%s location=%s", _project_id(), _location())

    client = genai.Client(vertexai=True, project=_project_id(), location=_location())
    for agent, body, out_path in to_generate:
        prompt = f"{_BASE_STYLE} {body}"
        log.info("  %s ...", agent)
        try:
            response = client.models.generate_images(
                model="imagen-4.0-generate-001",
                prompt=prompt,
                config={
                    "number_of_images": 1,
                    "aspect_ratio": "1:1",
                    "person_generation": "allow_adult",
                },
            )
        except Exception as e:
            log.warning("  %s FAILED: %s", agent, e)
            continue
        if not response.generated_images:
            log.warning("  %s — empty response (safety filter likely)", agent)
            continue
        img = response.generated_images[0]
        img.image.save(str(out_path))
        log.info("    wrote %s (%.1f KB)", out_path, out_path.stat().st_size / 1024)

    log.info("Done — %d portraits in %s", len(to_generate), OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
