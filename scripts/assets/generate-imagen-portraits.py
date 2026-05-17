"""Generate Imagen 4 agent portraits for the Ops Center IncidentPanel + EventStream.

PLAN_V3.md Move 2.2. Replaces emoji glyphs with 10 cinematic portraits — one
per GUARDIAN agent and per A2A peer. Style: NASA mission control × Studio
Ghibli; silhouette + single accent color per agent; dark background.

Usage:
    uv run python scripts/assets/generate-imagen-portraits.py
    uv run python scripts/assets/generate-imagen-portraits.py --force

Idempotent: skips agents whose PNG already exists. Override with --force.

Cost: ~$0.04 / image × 10 = $0.40.

Reproducibility caveat: Imagen 4 does not accept a seed parameter at the
publisher-model surface — every regeneration is stochastic. The portraits
in `ops-center/public/portraits/` are the COMMITTED canonical set. Do not
re-run with --force unless you intend to replace them all; the committed
PNGs are the source of truth for the deployed Ops Center, not this script.
The Falsifier portrait took two attempts on 2026-05-17 (first try was
flat white-bg; the noir prompt below produces dark-mode results
reliably in our experience but is not guaranteed deterministic).
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from google import genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OUT_DIR = Path("ops-center/public/portraits")

# Each agent gets a portrait. Accent colors picked to match the existing
# IncidentPanel + EventStream chip colors (Tailwind palette names + hex).
# Prompt style: a single sentence describing the silhouette + accent + mood;
# Imagen 4 reliably produces clean profile illustrations from this shape.
_BASE_STYLE = (
    "Cinematic vector portrait illustration in profile silhouette, deep "
    "black background, single accent color, minimalist, NASA-mission-control "
    "meets Studio Ghibli aesthetic, no text, no logos, no people identifiable "
    "by features, 1:1 framing, centered, museum-quality."
)

PORTRAITS = {
    "root_agent": (
        "An orchestrator-conductor silhouette holding a coordination baton, "
        "amber accent, viewed in 3/4 profile, suggesting calm authority and "
        "system-wide oversight."
    ),
    "stream_watcher": (
        "A figure intently watching a wall of monitors, sky-blue accent, "
        "warm-cool contrast, suggesting 24/7 vigilance on video feeds."
    ),
    "audio_agent": (
        "A figure listening with headphones, waveform tracery emerging from "
        "their head, violet accent, suggesting acute focused hearing."
    ),
    "species_id": (
        "A figure examining a small leaf or feather under a magnifier, "
        "emerald-green accent, suggesting scientific identification."
    ),
    "falsifier": (
        "Profile silhouette of an auditor at a darkened bench, slim "
        "rose-red beam of light catching the edge of a raised gavel "
        "against pure black void background. Almost-monochrome rim "
        "lighting from the side. Minimal interior detail. Dignified, "
        "procedural, courtroom-noir."
    ),
    "court_evidence": (
        "An archivist silhouette holding a sealed document chain, slate-blue "
        "accent, suggesting tamper-evident chain-of-custody record-keeping."
    ),
    "park_service": (
        "A ranger silhouette in field gear with a radio at the shoulder, "
        "warm-orange accent, suggesting frontline dispatch and protection."
    ),
    "sponsor_sustainability": (
        "An executive silhouette reviewing a portfolio document, "
        "navy-and-gold accent, suggesting corporate sustainability "
        "compliance and board-level reporting."
    ),
    "funder_reporter": (
        "A philanthropist silhouette extending a hand of support, lavender "
        "accent, suggesting impact funding and quarterly reporting."
    ),
    "neighbor_park": (
        "A second ranger silhouette across a border line, teal accent, "
        "suggesting cross-jurisdiction mutual aid and adjacent-park "
        "coordination."
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
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    to_generate = []
    for agent, body in PORTRAITS.items():
        out_path = OUT_DIR / f"{agent}.png"
        if out_path.exists() and not args.force:
            log.info("Skip %s (already exists, %d bytes)", out_path, out_path.stat().st_size)
            continue
        to_generate.append((agent, body, out_path))

    if not to_generate:
        log.info("All portraits already generated. Use --force to re-bill.")
        return 0

    log.info("Generating %d Imagen 4 portraits (cost ~$%.2f)...",
             len(to_generate), 0.04 * len(to_generate))
    log.info("  project=%s location=%s", _project_id(), _location())

    client = genai.Client(vertexai=True, project=_project_id(), location=_location())
    for agent, body, out_path in to_generate:
        prompt = f"{_BASE_STYLE} {body}"
        log.info("  %s ...", agent)
        response = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config={
                "number_of_images": 1,
                "aspect_ratio": "1:1",
                "person_generation": "allow_adult",
            },
        )
        img = response.generated_images[0]
        img.image.save(str(out_path))
        log.info("    wrote %s (%.1f KB)", out_path, out_path.stat().st_size / 1024)

    log.info("Done — %d portraits in %s", len(to_generate), OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
