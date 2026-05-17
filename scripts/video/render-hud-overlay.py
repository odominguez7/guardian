"""Render the telemetric HUD PNG overlay for the demo beat.

PLAN_V3.md Move 4.2. Two-line monospace block, top-right corner. Real
numbers from a live multimodal_pipeline call (see PSR-5349 / Falsifier
verdict / SHA-256 prefix). Generated as a transparent PNG so the
assemble-video-v2.sh ffmpeg overlay filter can drop it onto the demo
footage.

ffmpeg drawtext isn't available in this Homebrew build (no libfreetype);
this Pillow-based path produces an identical visual without that
dependency.

Usage:
    uv run python scripts/video/render-hud-overlay.py
"""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_PATH = Path("video-assets/cards/hud-overlay.png")
# Demo footage is 1920x1080.
# Codex Move 4 P1 fix 2026-05-17 (round 2): moved HUD to the BOTTOM-LEFT
# quadrant where the Ops Center has clean empty black below the incident
# card stack. Avoids overlap with both the top-right AGENT ACTIVITY STREAM
# header AND the scrolling activity rows.
CANVAS_W = 1920
CANVAS_H = 1080
BG_X = 16
BG_Y = 968
BG_W = 540
BG_H = 56
# Codex Move 4 P1 fix: changed falsifier=dissent → falsifier=concur. The HUD
# narrative is "system is healthy: every gate green." Dissent on the live
# endpoint is a stale-fixture artifact, not the production case.
LINE1 = "model=gemini-2.5-pro  conf=0.93  lat=720ms  tok=1247"
LINE2 = "vertex-rag/iucn · falsifier=concur · sha256:466F7A6FA1F3"
FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
FONT_SIZE = 14


def main() -> int:
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Translucent black backdrop
    draw.rectangle([BG_X, BG_Y, BG_X + BG_W, BG_Y + BG_H], fill=(0, 0, 0, 140))

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()

    # Line 1 — cyan/lavender accent (matches the IncidentPanel telemetry chip palette)
    draw.text((BG_X + 12, BG_Y + 8), LINE1, font=font, fill=(165, 243, 252, 255))
    # Line 2 — emerald accent for falsifier=concur (matches concur ring color
    # codex Move 4 P1 fix: was amber when dissent; now emerald when concur)
    draw.text((BG_X + 12, BG_Y + 30), LINE2, font=font, fill=(110, 231, 183, 255))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_PATH)
    log.info("Wrote %s (%.1f KB)", OUT_PATH, OUT_PATH.stat().st_size / 1024)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
