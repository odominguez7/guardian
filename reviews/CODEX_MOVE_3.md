# Codex Handshake — Move 3 (Board-ready slide auto-export)

_Per PLAN_V3.md §4.5. Run 2026-05-17._

## What Move 3 shipped

- `app/tools/board_slide.py` NEW — `render_board_slide(filing_id)` walks the event ring buffer for the matching sponsor a2a_response, derives KPIs (species protected, hectares monitored, A2A-confirmed filings count, SHA-256 audit hash), renders a self-contained 16:9 HTML page with inline CSS.
- `GET /board-slide/{filing_id}` endpoint on the orchestrator (mirrors `/demo/evidence/{id}/html` pattern).
- Sponsor peer `file_tnfd_entry` returns `board_slide_url` constructed from `GUARDIAN_ORCHESTRATOR_URL` + `/board-slide/{filing_id}`.
- `app/tools/a2a_peers.py` allowlist extended for `board_slide_url`.
- Ops Center IncidentPanel: "📋 Slide" download button on Sponsor ack card.
- Ops Center page.tsx: sponsor a2a_response extracts `board_slide_url` onto `inc.tnfd`.
- Tests: 5 new (20 total).

Live: orchestrator `guardian-00021-6dn` → upgraded to `guardian-00022-rs8` post-fixes; ops-center `guardian-ops-center-00012-rd9`; sponsor `guardian-sponsor-sustainability-00004-729`.

## Codex Pass 1 — VERDICT: RECONSIDER

**P1:**
1. `html2canvas` loaded from Cloudflare CDN on a regulated-disclosure artifact — supply-chain + offline-save risk
2. Buffer eviction → 404 weeks later; CSO bookmarks the link, comes back, gets a 404

**P2:**
1. Reporting quarter derived from earliest event — Q1 detection / Q2 filing labels wrong quarter
2. Direct access to `_events._buffer` + `_events._thread_lock` — fragile private contract

## Fixes applied (commit 76e2569)

- **P1 #1:** Vendored `app/static/html2canvas.min.js` (199KB, SHA-256 `e87e5507...`); FastAPI mounts `/static` via StaticFiles; slide template references `/static/html2canvas.min.js`. Live-verified: `/static/html2canvas.min.js` returns 200 + slide HTML carries `/static/html2canvas` with zero `cdnjs.cloudflare` references.
- **P1 #2:** `app/events.py` adds `cache_render(key, html)` + `get_cached_render(key)` — LRU-capped at `GUARDIAN_RENDER_CACHE_MAX` (default 200). `render_board_slide` caches on first derivation; subsequent calls hit cache fast-path with `from_cache: true`. Survives ring-buffer eviction (does not survive Cloud Run cold starts; production path documented as GCS/Firestore).
- **P2 #1:** `_reporting_period_from_events(anchor_agent=...)`. `board_slide` passes `"sponsor_sustainability"` so quarter anchors on filing event.
- **P2 #2:** `app/events.py` adds public `lookup_incident_by_a2a_field(agent, field, value)`. `board_slide.py` migrated.

3 new tests (23 total green): cache survives 250-event flush; quarter anchoring honors `anchor_agent`; public lookup helper happy + edge cases.

## Codex Pass 2 — VERDICT: CLEAR

> "fixes hold; greenlight Move 4. Remaining P0/P1/P2: None outstanding."

## Move 3 wraps. Move 4 starts.
