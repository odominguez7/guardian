# §4.5 Handshake Gate — v6 / v6.1 / v6.2 / v6.3 (CLEAR)

**Status:** CLEAR. Codex final verdict 2026-05-17 on commit `0770567`:
> "CLEAR — v6.3 ships, agentic loop closed end-to-end on real live frames."

## What v6 ships

Producer ask: "when we spot something in the live cam, can we launch some agent in real life?"

Closed loop: **YouTube live cam frame → real Gemini 2.5 vision → real Falsifier adversarial review → real 4-peer A2A fan-out → real TNFD board slide.**

- `POST /livecam/spot {youtube_id, cam_label}` on the orchestrator
- "Spot Now" button on the live cam tile in the Ops Center
- 12s per-stream cooldown, asyncio.to_thread on the thumbnail probe, cache-buster on the picked URL, real ISO `observation_timestamp` threaded through every peer call, 32 bits of random entropy on the incident_id seed

## Smoke test (v6.2 against live NamibiaCam)
- Vision: 5 Ostriches + 1 Gemsbok detected at the waterhole (confidence 0.95)
- requires_escalation: true (fallback fired on total_animal_count=6)
- park_service: ranger PSR-2703 dispatched, ETA 30min
- sponsor_sustainability: TNFD-2026-4C7483FB9F filed with board_slide_url
- funder_reporter: receipt issued under "general_impact"
- neighbor_park: ACK in flight
- adversarial_review: abstain (correct — vision-only event with no audit telemetry)

## Codex rounds

### Round 1 — v6 (commit `fc2776f`): BLOCK verdict
- BLOCK 1: sponsor/funder/neighbor reject None `observation_timestamp` → no fan-out
- BLOCK 2: 7-URL HEAD probe blocks event loop ~21s worst case
- WARN: thumbnail cache buster missing
- WARN: incident_id seed entropy = 1s granularity
- WARN: frontend 429 assumed `detail` field
- WARN: hair-trigger escalation heuristic (acceptable for demo, deferred to v7)

### Round 2 — v6.1 (commit `58c7862`): smoke-test caught regression
- BLOCK 1 fixed: real `datetime.now(timezone.utc).isoformat()` threaded through all peer args
- BLOCK 1.5 fixed: neighbor_park's species arg is `species_affected`, not `species`
- BLOCK 2 fixed: `asyncio.to_thread(_pick_live_thumbnail, ...)`
- WARN fixes: `?_ts=<epoch>` cache buster, `secrets.token_hex(4)` entropy, frontend fallback message
- Smoke test caught: `result.species[]` schema vs my assumed `result.primary_species` — fallback escalation never fired

### Round 3 — v6.2 (commit `9c9f0b9`): WARN verdict
- Schema fix: `species_list = result.get("species") or []`, top-confidence headline, `total_animal_count` drives fallback gate
- New WARN: threat-only escalations (empty species + threat_signals) labeled "wildlife sighting" on TNFD — wrong
- New WARN: board_slide.py read `primary_species` (legacy schema) — live filings showed "Endangered species" fallback

### Round 4 — v6.3 (commit `0770567`): CLEAR
- Threat-only species headline: `f"scene event ({threat_signals[0]})"` when species empty + threat present
- board_slide.py `_species_summary` reads top-confidence entry from `species: [...]` with primary_species fallback for legacy /demo/run fixtures
- Codex CLEAR: "v6.3 ships, agentic loop closed end-to-end on real live frames"

## Deploy state
- Orchestrator: `guardian-00029-z7s` (v6.3)
- Ops Center: `guardian-ops-center-00022-rtk` (v5.4 — Spot Now frontend shipped in v6.1, no further frontend changes)
- Live URL: https://guardian-ops-center-180171737110.us-central1.run.app

## NIT deferred to v7
- `adversarial_review_passed` is a bool that maps `abstain → False`. Codex suggested tri-state (bool + status note) so sponsors can distinguish "not reviewed" from "failed audit." Deferred to v7.
- yt-dlp HLS frame extraction for guaranteed-fresh frames (current path uses YouTube live thumbnails which rotate every ~30-60s).
