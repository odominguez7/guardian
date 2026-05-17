"""Downscale + WebP-encode the Mission Bridge v2 portraits.

Codex Day 2 WARN: raw Imagen 4 outputs are 1.2-1.4 MB / 1024px PNG each,
totaling ~12.5 MB on Mission Bridge cold-load. Mission Bridge displays
them at 70-116 px badges max — 1024px source is 9x oversized. This script
crops them square, resizes to 512px (2x retina for the largest badge),
encodes to WebP quality=85, and writes alongside the PNG sources so the
component can prefer .webp via <picture>. Total payload after: ~1.5 MB.

Usage:
    uv run python scripts/assets/optimize-portraits-v2.py
    uv run python scripts/assets/optimize-portraits-v2.py --force
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SRC_DIR = Path("ops-center/public/portraits-v2")
TARGET_PX = 512  # 2x retina for the largest 116px badge
WEBP_QUALITY = 85


def optimize(png_path: Path, force: bool) -> None:
    webp_path = png_path.with_suffix(".webp")
    if webp_path.exists() and not force:
        log.info("skip %s (exists, %d KB)", webp_path.name, webp_path.stat().st_size // 1024)
        return
    img = Image.open(png_path).convert("RGB")
    # Square crop is already 1:1 from Imagen, just resize.
    w, h = img.size
    if w != h:
        log.warning("non-square source %s (%dx%d), centering crop", png_path.name, w, h)
        m = min(w, h)
        img = img.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2))
    img = img.resize((TARGET_PX, TARGET_PX), Image.LANCZOS)
    img.save(webp_path, format="WEBP", quality=WEBP_QUALITY, method=6)
    log.info(
        "wrote %s  png=%dKB → webp=%dKB",
        webp_path.name,
        png_path.stat().st_size // 1024,
        webp_path.stat().st_size // 1024,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    pngs = sorted(SRC_DIR.glob("*.png"))
    if not pngs:
        log.error("no PNGs in %s", SRC_DIR)
        return 1
    for p in pngs:
        optimize(p, args.force)
    log.info("done — %d portraits optimized in %s", len(pngs), SRC_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
