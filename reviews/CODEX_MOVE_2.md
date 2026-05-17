# Codex Handshake — Move 2 (GCP suite taste pass)

_Per PLAN_V3.md §4.5. Run 2026-05-17._

## What Move 2 shipped

- **Lyria 2 ambient bed** — `scripts/assets/generate-lyria-bed.py` (REST predict to `lyria-002`), `video-assets/music/guardian-ambient-30s.{wav,mp3}`, `ops-center/public/ambient-30s.mp3`. 30s seamless drone, 70 BPM, -28 dBFS-suitable, no melody. ~$0.06.
- **Imagen 4 portraits** — `scripts/assets/generate-imagen-portraits.py`, 10 PNGs at `ops-center/public/portraits/*.png`. Cinematic silhouettes (NASA × Studio Ghibli), one accent color each. ~$0.44 (one re-render of Falsifier).
- **Veo 3.1 Fast hero** — `scripts/assets/generate-veo-hero.py`, `video-assets/broll/guardian-hero-6s.mp4`, `ops-center/public/hero-6s.mp4`. 6s photoreal elephant herd at dusk near camera trap. ~$0.60.
- Wired into Ops Center: ambient autoplay on first gesture (pointer/keyboard/wheel/touch), AUTO+AMBIENT toolbar chips, portrait avatars on all peer ack cards + Falsifier chip, Veo hero in idle IncidentPanel region.

Total Move 2 spend: ~$1.10.

## Codex Pass 1 — VERDICT: RECONSIDER

**P1 (blocker):** `IncidentPanel.tsx` imports 5 lucide icons (ShieldAlert, FileCheck2, HandCoins, MapIcon, Gavel) replaced by `<img>` tags. ESLint config errors on unused imports.

**P2 (accepted):**
1. Ambient bed only starts on click/keydown — judges who scroll-only never hear audio
2. `.gitignore` un-ignores ALL public/*.mp4 — would let future big drops sneak into git
3. Imagen 4 has no seed — Falsifier could drift on regen; committed PNGs are canonical
4. Veo 9.5MB ships in every Docker layer (acceptable for hackathon)

## Fixes applied (commit 043935f)

- Trimmed IncidentPanel imports to `Siren, Clock3` (the 2 still in use)
- Broadened gesture surface to include passive wheel + touchstart events
- Tightened gitignore exception to `!ops-center/public/hero-6s.mp4` (specific filename)
- Imagen script docstring documents the non-determinism + canonical-PNG policy
- Veo size accepted, deferred

`npm run build` clean. Live revision: `guardian-ops-center-00011-ccg`.

## Codex Pass 2 — VERDICT: CLEAR

> "No P0/P1/P2 remain. Greenlight Move 3 (Board-ready slide auto-export)."

## Move 2 wraps. Move 3 starts.
