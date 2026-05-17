# Codex Handshake — Move 0 (Live site truth)

_Per PLAN_V3.md §4.5 codex handshake gate. Run 2026-05-17._

---

## What Move 0 shipped

- `ops-center/src/app/page.tsx` — Auto-Cycle Demo Mode (10s idle → scenarios rotate; pointer/keyboard activity pauses; AUTO DEMO badge state)
- `ops-center/src/components/Toolbar.tsx` — `autoCycleActive` prop renders pulsing green AUTO DEMO chip
- `Makefile` `deploy-ops-center` — auto-sources `ops-center/.env.local`, maps `NEXT_PUBLIC_*` → bare names, fails fast on empty Mapbox token
- Cloud Run revision `guardian-ops-center-00009-k4z` live with Mapbox token baked in (build substitution confirmed via `gcloud builds describe ... --format=json` → `pk.eyJ1...` 96 chars)

## Codex Pass 1 — VERDICT: BLOCK

**P0 (1):**
- `Makefile:256` — `${VAR:=$NEXT_PUBLIC_VAR}` fallback assignments were inside the `if [ -f ops-center/.env.local ]` guard. CI environments that export only `NEXT_PUBLIC_*` (no .env.local) would silently ship empty `_MAPBOX_TOKEN`. Fix: move fallbacks outside the if, fail fast if MAPBOX_TOKEN still empty.

**Notes (everything else cleared):**
- Auto-cycle interval tears down cleanly on dependency change/unmount (page.tsx:321-343)
- Pointer/keyboard activity correctly halts badge and resets idle (page.tsx:345-357)
- Toolbar disables buttons while scenario runs → no double-fire race (Toolbar.tsx:55-65)
- ReserveMap placeholder only renders when token truly missing (ReserveMap.tsx:213-233)

## Fix applied

- Moved all `${VAR:=$NEXT_PUBLIC_VAR}` fallbacks outside the `.env.local` guard
- Added explicit `export` of the mapped vars
- Fail-fast `exit 1` with a clear error when MAPBOX_TOKEN is empty
- Smoke-tested 3 modes locally:
  - No env at all → exits 1 with clear error ✅
  - Only `NEXT_PUBLIC_MAPBOX_TOKEN` exported, no .env.local → mapping fills MAPBOX_TOKEN ✅
  - .env.local present (normal case) → token length 96 ✅

Commit: `88720e4`

## Codex Pass 2 — VERDICT: CLEAR

> "All Move 0 checks satisfied. Remaining blockers: P0 none, P1 none, P2 none. Greenlight to proceed with Move 1 (Falsifier)."

## Acceptance gate from PLAN_V3.md §5

- ✅ Mapbox token in Cloud Build substitution (96 chars confirmed via build JSON)
- ✅ Cloud Run revision live (`guardian-ops-center-00009-k4z`)
- ✅ Auto-Cycle code present and TypeScript-clean
- ✅ AUTO DEMO badge wired
- ✅ Deploy mechanism hardened for CI / dev-only environments

## Move 1 starts now.
