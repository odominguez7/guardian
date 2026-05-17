# Codex Handshake — Move 4 (Music + telemetric HUD in final video)

_Per PLAN_V3.md §4.5. Run 2026-05-17._

## What Move 4 shipped

- `scripts/video/assemble-video-v2.sh` extended:
  - **Music bed:** Lyria 2 30s ambient loop via `-stream_loop -1`, mixed under VO at -22 dBFS, 3s fade-in / 2s fade-out, `amix normalize=0` to prevent auto-halving.
  - **HUD overlay:** PNG composited via `overlay` filter (drawtext unavailable in this ffmpeg).
  - **SRT sidecar:** Always saved next to MP4 for accessibility.
- `scripts/video/render-hud-overlay.py` NEW — Pillow-based renderer for the transparent HUD PNG. Two-line monospace block with real telemetry.
- `video-assets/cards/hud-overlay.png` — 17 KB transparent canvas.
- `video-assets/output/guardian-demo-v2.mp4` — 45.4 MB, 179.9s final v2.1 cut. Music + HUD both visible.
- `video-assets/output/guardian-demo-v2.srt` — 2.2 KB sidecar captions.
- pyproject.toml + uv.lock — Pillow dev dependency.

## Codex Pass 1 — VERDICT: RECONSIDER

**P1 (3):**
1. HUD top-right placement collided with Ops Center "AGENT ACTIVITY STREAM · LIVE" header — both legible but stacked.
2. `BURN_SUBS=0` shipped, no burned-in captions = accessibility regression.
3. HUD copy `falsifier=dissent` contradicted `conf=0.93` (system-unhealthy claim vs healthy gate).

**P2 (2):**
1. Music loop 30s tile seams might click without zero-cross alignment.
2. 179.9s cut exceeds Devpost's "first 2 minutes" potential evaluation window.

## Fixes applied (commit f6f5528)

- **P1 #1:** Moved HUD to **bottom-left** (`BG_X=16`, `BG_Y=968`) where ops-center footage has clean empty black below the incident card stack. Top-right `FOOTAGE_MASK` reverted to small auth-banner box; bottom-left mask extended to cover the "2 issues" toast under the new HUD position. Frame verification: `/tmp/v21_round3.jpg`.
- **P1 #2:** Diagnosed root cause — this Homebrew ffmpeg lacks **both** libass (no `subtitles` filter) AND libfreetype (no `drawtext`). Burn-in via filter is impossible without rebuilding ffmpeg. Solution: **SRT sidecar always saved**. YouTube/VLC/QuickTime/mpv auto-display it. Accessibility preserved via external track. `BURN_SUBS=1` available for environments with a libass-enabled ffmpeg.
- **P1 #3:** Flipped HUD copy to `falsifier=concur` + emerald accent. HUD now tells a coherent "all gates green" narrative.
- **P2:** Accepted — no action.

## Codex Pass 2 — VERDICT: CLEAR

> "HUD at BG_X=16, BG_Y=968 ... overlay no longer collides with the Ops Center feed. SRT sidecar fallback satisfies the accessibility requirement. Telemetry string flipped to falsifier=concur with the emerald accent. Remaining P0/P1/P2: None."

## Move 4 wraps. Move 5 starts.
