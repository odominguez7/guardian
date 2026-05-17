# §4.5 Handshake Gate — v4 Diff Audit

**Status:** OpenAI codex quota exhausted at 2026-05-17 03:13–03:45 UTC. Independent adversarial review performed instead by a fresh-context Plan subagent. When codex quota returns, re-run the same prompt (`scripts/codex/move7_v4_prompt.txt`) for confirmation.

**Commit audited:** `2a31835` — feat(v4): ParallelAgent fan-out + ADK Eval + complement-not-compete + YouTube live

## BLOCK — must fix before submission

**BLOCK 1 [incident_pipeline.py:47-51]** — `build_incident_pipeline()` imports `build_audio_agent`, `build_falsifier_agent`, `build_species_id_agent`, `build_stream_watcher_agent`, `build_peer_fanout_agent`. None of those exist; only the module-level globals do. Calling the factory raises `ImportError`. Dead code. **Fix:** scope the file as v5 scaffold (raise NotImplementedError with a clear v5 message) OR delete it. Producer choice: keep as scaffold (judges see the SequentialAgent intent in code) with explicit NotImplementedError.

**BLOCK 2 [agent.py:103-181]** — `peer_fanout_agent` is in `sub_agents` but ROOT_INSTRUCTION still tells the LLM to call `notify_*` tools directly. There's no `transfer_to_agent("peer_fanout")` rule. In production the ParallelAgent never fires. The `peer_fanout.evalset.json` trajectory will not match live behavior. **Fix:** rewrite the escalation step in ROOT_INSTRUCTION to `transfer_to_agent("peer_fanout")` for severity in {high, critical}; keep the direct `notify_*` tools for {low, medium} fallback.

**BLOCK 3 [court_evidence.py:148-154]** — `management_review_required` only triggers on `verdict == "dissent"`. **Abstain on critical** (auditor declined to opine on a critical dispatch) is the case Big-4 audit charters care about most, and is silently missed. **Fix:** include `"abstain"` in the verdict trigger.

## WARN — judges will notice

- **WARN [peer_fanout.py:36-49]** — Each of 4 thin Gemini 2.5 Flash agents adds ~600-1200ms for a tool-call-only role. Accepted as documented tradeoff: declarative ADK 2.0 topology costs latency. Parallelism keeps total fan-out at max(t_i) not sum, so worst-case +1.2s vs the pre-v4 `asyncio.gather` path. Will document inline.

- **WARN [court_evidence.py:148, last_severity logic]** — Walking events and keeping the latest severity drops the management review when an incident's severity is downgraded mid-flight (e.g., critical → medium on better evidence). **Fix:** compute max-severity across the timeline, not last.

- **WARN [court_evidence.py:148, multi-falsifier mixed verdicts]** — `adversarial_review = adversarial_reviews[-1]` is correct for "current verdict" but dropping management review on a retracted dissent hides Big-4-relevant audit signal. **Fix:** trigger if *any* review dissented or abstained on a high/critical timeline.

- **WARN [peer_fanout.evalset.json:23-30]** — ParallelAgent sub-agent tool calls may not appear under a single flat `tool_uses` array in ADK Eval; trajectory may need `notify_*` only, no `transfer_to_agent`. Verify with `adk eval --dry-run` before claiming pass.

- **WARN [falsifier.evalset.json `falsifier_abstain_stale_observation`]** — Missing `new_incident_id` step; ROOT_INSTRUCTION mandates it first. **Fix:** add the mint step or relax instruction wording.

- **WARN [user_simulation.evalset.json sustainability_analyst turn 1]** — Expects `transfer_to_agent("court_evidence")` for a quarterly multi-incident query; the agent only has per-incident tools (`bundle_incident` / `render_evidence_html`). Will hallucinate or error. **Fix:** narrow the user prompt to a single `GU-...` id.

- **WARN [LiveCams.tsx:67-76]** — Missing `sandbox` attribute, unnecessary `encrypted-media` in `allow=`, full youtube.com cookies. **Fix:** sandbox tight; swap to `youtube-nocookie.com/embed/`; drop encrypted-media; degrade gracefully if the video privatizes.

- **WARN [LISTING.md SMART/EarthRanger/SERCA cell]** — Per the Oct 2025 SMART–EarthRanger Conservation Alliance (SERCA) announcement: SMART is being folded into EarthRanger and rebranded as SERCA. Listing all three as parallel reads as hallucinated copy. **Fix:** "**SMART / EarthRanger** (merging into **SERCA**, the SMART–EarthRanger Conservation Alliance, Oct 2025)". Also IBAT row missing Conservation International as a fourth co-publisher.

## NIT — small polish

- **NIT [agent.py:84-87]** — gemini-3-pro fallback comment is aspirational; trim or commit to env-flip.
- **NIT [LiveCams.tsx:143]** — "Veo 3.1 Fast generated · 6s loops" implies 4 Veo; now 3 Veo + 1 YouTube.
- **NIT [LISTING.md:45]** — Revision suffix `guardian-00022-rs8` shouldn't appear in marketing copy.
- **NIT [LISTING.md:150]** — `github.com/odominguez7/guardian _(replace with real path)_` is a placeholder.
- **NIT [court_evidence.py:178-179]** — Reading `events._BUFFER_SIZE` via leading-underscore name; add a `events.buffer_size()` public accessor.

## OK

- Falsifier verdict surfacing structurally correct; `adversarial_reviews` plural preserves full history.
- Hash-scope language is honest ("does NOT prove completeness vs emitted events").
- LISTING.md complement-not-compete framing is the right F500 procurement posture; only SERCA row needs the merger fix.

## Bottom line

HOLD — do not ship until BLOCK 1 (dead-code factory), BLOCK 2 (no routing to peer_fanout), and BLOCK 3 (abstain miss) are resolved. The audit weaknesses called out in §4.5 (agentic depth, F500 procurement) get surface paint without these fixes; a competent ADK reviewer running `adk eval` against the evalsets will catch the import error and routing gap in 10 minutes.
