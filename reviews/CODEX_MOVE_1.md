# Codex Handshake — Move 1 (Falsifier adversarial agent)

_Per PLAN_V3.md §4.5. Run 2026-05-17._

## What Move 1 shipped

- `app/tools/falsifier.py` — `review_dispatch()` SOP gate engine (audio confidence × severity; species-flag materiality ceiling; observation freshness; hot threat-signal requirement). Emits `tool_end` event on every call with severity=critical when dissent_severity ≥ 3.
- `app/agents/falsifier.py` — ADK LlmAgent on Gemini 2.5 Flash wrapping the tool. Hostile-auditor instruction.
- `app/agent.py` — Falsifier registered as the 4th sub-agent; orchestrator instruction now mandates delegation at step 0.5 of escalation, before any notify_*.
- `app/tools/court_evidence.py` — bundle_incident extracts falsifier events into top-level `adversarial_review` + chronological `adversarial_reviews` list. HTML packet renders "Adversarial Review (Falsifier)" section with verdict pill + per-gate PASS/FAIL diagnostics. Warns when no review found.
- `peers/sponsor_sustainability/agent.py` — `file_tnfd_entry` accepts adversarial_review_verdict + severity_0_5; tnfd_entry payload carries `adversarial_review_passed` bool.
- `app/tools/a2a_peers.py` — `notify_sponsor_sustainability` extended to pass-through verdict + severity to the Sponsor peer.
- `app/fast_api_app.py` — `/demo/run` extracts telemetry from pre_steps, calls review_dispatch inline, includes adversarial_review in response, threads verdict into the Sponsor peer call.
- `ops-center/src/components/IncidentPanel.tsx` — DISSENT chip (Gavel icon, color-coded by verdict, AUDIT FLAG badge when severity ≥ 3).
- `ops-center/src/app/page.tsx` — event handler populates inc.falsifier; pendingFalsifierRef buffers verdicts that arrive before their incident_event (race fix).
- 15 unit + integration tests, all green.

## Codex Pass 1 — VERDICT: BLOCK

**P0:**
- `/demo/run` never invoked Falsifier (fixture path bypassed orchestrator)
- `notify_sponsor_sustainability` didn't forward new adversarial-review fields

**P1:**
- page.tsx race: falsifier event before incident_event → dropped chip
- 4 ADK eval trajectories not committed

**P2:**
- bundle_incident overwrote adversarial_review on multiple falsifier events

## Fixes applied (commit 2fa5f12)

- `/demo/run` extracts audio_confidence, species_compliance_flag, threat_signals (normalized vocabulary) from pre_steps, calls review_dispatch, threads verdict into Sponsor peer + response record
- `notify_sponsor_sustainability` signature extended (backward compat: new args default to empty/0); instruction payload carries the new fields
- page.tsx introduces `pendingFalsifierRef` Map; verdicts that arrive before incident_event are adopted on incident upsert + cleared
- bundle_incident produces both top-level `adversarial_review` (latest) and `adversarial_reviews` list (chronological)
- ADK eval trajectories logged to TODOS.md as deferred (~1hr post-submission); 5 pytest integration tests are the substitute

## Codex Pass 2 — VERDICT: CLEAR

> "/demo/run now mirrors the orchestrator path: it harvests audio/species/stream telemetry, normalizes threat signals, calls review_dispatch, injects the verdict into the sponsor call, and returns the audit block to clients, matching PLAN_V3 targets... Move 2 (GCP suite taste pass) is greenlit."

P0: none. P1: none. P2: none.

## Move 1 wraps. Move 2 starts.
