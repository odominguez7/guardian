# CEO Review — 2026-05-17 (post browser-disconnect realignment)

_Trigger: Producer asked for a full CEO review + codex handshake after a browser disconnect interrupted execution rhythm. Goal: re-anchor on the locked plan, the current artifact state, and the next action in the right order._

**Mode selected:** **HOLD SCOPE.** V2_PLAN §12 is already locked. The V2 cut exists. The codex P0/P1 punch list is known. This review's job is to verify the §12.4 execution order is still right and to call out any new facts from the live system that change the next move — not to re-open scope.

---

## §1 — What's been shipped since the prior CEO review (2026-05-16)

Git log since `9f048df` (the README polish HEAD that memory thought was current):

| Commit | What it did | Maps to V2_PLAN step |
|---|---|---|
| `afc5b91` | V2 cut rendered — voice + cards + plan + codex review | (V0 baseline before §12.4) |
| `dabd2d9` | Voice GUARDIAN-Design-1 locked (ElevenLabs generative) | (preparatory) |
| `719578f` | Post-V2-cut CEO §12 review committed | (this current plan locked) |
| `eb868e0` | VO v2.2 transcript codex-handshaken (FACTS + DEMO PARITY PASS) + acronyms expanded | partial V3 |
| `103a0af` | Re-rendered 6 segments with full-name acronyms | partial V3 |

**Net effect:** the **audio side of V2.1 is essentially locked.** Voice + transcript both codex-cleared. The remaining work is all on the visual side + the Mapbox unblock + final assembly.

---

## §2 — Live system verification (run during this review, 2026-05-17 00:43 UTC)

POSTed `multimodal_pipeline` to the live endpoint twice. Result:

| ID family | Deterministic? | Live value |
|---|---|---|
| `incident_id` | ✅ YES | `GU-466F7A6FA1F3` |
| `filing_id` (Sponsor / TNFD) | ✅ YES | `TNFD-2026-A0192B2A32` |
| `receipt_id` (Funder) | ✅ YES | `FUND-2026-A0192B2A32` |
| `handoff_id` (Neighbor) | ✅ YES | `MUTAID-2026-A0192B2A32` |
| `ranger_unit` (Park Service) | ❌ NO | `PSR-9168` this call. Past calls: `PSR-9737`, `PSR-5280`, `PSR-4078`, `PSR-0501`. |

**4 of 5 IDs are reproducible right now.** Only `ranger_unit` randomizes per call. This is a 15-min seed-by-incident_id fix in `app/tools/peer_handlers.py` (already on the TODOS.md P3 list).

### §2.1 — Net implication for codex P0s

| Codex P0 | Status after live verification |
|---|---|
| #6 reproducibility unverified | **PARTIALLY RESOLVED.** 4/5 IDs are deterministic. Once ranger_unit is seeded, claim "every ID on screen comes from a live call to a public endpoint" is fully defensible. |
| #7 ID mismatch in demo vs script | **DEEPER THAN PRIOR REVIEW CAUGHT.** Script segment `07-demo-fanout` still names `PSR-9737`, `FUND-A0192B2A32`, `MUTAID-A019282A32`. Typo IDs are corrected by 2 char swaps; PSR randomness fixed by seeding. |

This is **good news** for the V2_PLAN §12.4 sequence. The reproducibility story can become an *asset* rather than a credibility risk — provided we fix ranger_unit before re-recording.

---

## §3 — Strategic alignment check against the locked plan

Re-rating each scoring axis given current state:

| Scoring axis | Target | Where we are now | Risk |
|---|---|---|---|
| Technical (30%) | 28/30 | 4-peer A2A live + multi-modal pipeline live + AgentOps wired + codex-cleared. **At target.** | Low. Only ParallelAgent refactor + Pattern+Memory Bank would lift; neither moves the rubric meaningfully now. |
| Business Case (30%) | 28/30 | Marketplace listing submitted + F500-first storyboard + 4-peer story + 3-tier customer model. **At target.** | Low. |
| Innovation (20%) | 18/20 | 4 distinct enterprise A2A peers shipped, structurally required (not bolted-on). **At target.** | Low. ParallelAgent would push to 19 if time allows. |
| Demo (20%) | 17/20 | V2 cut exists but has 7 P0s flagged by codex. Voice is codex-handshaken. Mapbox + Firebase blockers still open. **At 13-14/20 today.** | **HIGH.** All score risk is concentrated here. |

**Verdict:** Single risk concentration. The CEO review's only job is to surface the cleanest path to closing the Demo gap.

---

## §4 — The decision tree

Three real-world paths, ranked by expected score outcome:

### Option B (locked in V2_PLAN §12) — re-record with map + pre-rendered Mapbox sequence

- **Effort:** 6-9 CC hours
- **Blocker:** Omar pastes Mapbox token. Already documented in `INTERVENTION_NEEDED.md`.
- **Expected score lift:** ~3 points (14 → 17 Demo).
- **Risk:** scope creep cascade (codex's flagged worry); mitigated by §12.5 hard freeze rule.

### Option A — ship V2 without map, apply all non-Mapbox P0s

- **Effort:** 3-4 CC hours
- **Blocker:** none
- **Expected score lift:** ~1.5 points (14 → 15.5 Demo)
- **Risk:** Loses the moneyshot beat (50-75s). Demo reads as "agentic dashboard screenshot," not "live multi-agent system."

### Option C — ship V2 as-is

- **Effort:** 0
- **Risk:** Codex's "DO NOT SHIP YET" verdict still standing. Firebase banner + 2-issues toast + TNFD framing + KPMG year + ESRS overclaim all visible. Track 3 odds estimated 3-5%.

**CEO CALL:** **Option B holds.** With the new information from §2 (4/5 IDs deterministic), Option B's payoff is *higher* than the V2_PLAN estimated — the reproducibility punchline is real, not aspirational. The cost stays the same.

---

## §5 — Re-sequenced execution order (refinement of §12.4)

The V2_PLAN §12.4 is correct in *what* to do; this review adjusts *order* to do unblocked work first while Omar is still pasting tokens.

### New tier ordering: do everything that doesn't need Omar's tokens FIRST.

| # | Task | Blocked on Omar? | Effort | Owner |
|---|---|---|---|---|
| **A1** | Seed `ranger_unit` by `incident_id` so `dispatch_rangers` returns same `PSR-XXXX` per call | No | 15 min | CC |
| **A2** | Verify A1 by hitting `/demo/run/multimodal_pipeline` twice and confirming PSR matches | No | 5 min | CC |
| **A3** | Update `segments.json` `07-demo-fanout` visual descriptor: corrected IDs (`FUND-2026-A0192B2A32`, `MUTAID-2026-A0192B2A32`) + the now-deterministic `PSR-XXXX` from A2 | No | 10 min | CC |
| **A4** | Update `09-proof` punchline frame: `Mapped to ESRS E4 (materiality assessed)` (P0 #5 fix) + keep `TNFD-2026-A0192B2A32` (deterministic) | No | 5 min | CC |
| **A5** | Re-render the 2 affected cards (07 fanout overlay, 09 punchline) | No | 20 min | CC |
| **A6** | Re-render any VO segments whose text changed in A3-A4 (likely none if visuals-only changes) | No | ~0-15 min | CC |
| **A7** | Optional: Cloud Trace span-tree 10s screen-record for architecture beat (designer recommendation) | No | 30-45 min | CC |
| **B1** | Omar pastes Mapbox token → `ops-center/.env.local` | YES | 5 min | Omar |
| **B2** | Omar decides on Firebase: paste config OR confirm we'll suppress banner with CSS-only hack | YES | 5-15 min | Omar |
| **B3** | Suppress Firebase banner + 2-issues toast for demo build (CSS gate or env flag) | depends on B2 | 30 min | CC |
| **B4** | Pre-render Mapbox sequence (flyTo + pulse + 4 animated arrows) offline → MP4 | YES (needs token) | 90-120 min | CC |
| **B5** | Re-record demo phase (35s-1:35) against localhost:3000 with banner hidden + comp the Mapbox MP4 | YES | 60 min | CC |
| **C1** | Reassemble v2.1 final | After all above | 30 min | CC |
| **C2** | Single codex slop-detection sweep on v2.1 keyframes | After C1 | 20 min | CC |
| **C3** | Stranger lean-in test (3 people, first 25s) | After C1 | variable | Omar |
| **C4** | Submit to Devpost | After C3 | 15 min | Omar |

**Key change from §12.4:** A1-A7 are all unblocked work. We should be making forward progress on A1-A7 *while* Omar is pasting tokens, instead of waiting on a serialized blocker.

**Hard cutover gate (unchanged from §12.4):** if Mapbox token isn't pasted within 24h (CC hour 6 of total work), pivot to Option A. The non-Mapbox P0s from A1-A7 will already be done, so the cost of pivoting is small.

---

## §6 — Scope-creep red flags (preemptive enforcement of §12.5 freeze rule)

After this review, the following are **not in scope** under any circumstance:

- Pattern Agent / Memory Bank (D6) — won't move Innovation rubric meaningfully now.
- ParallelAgent refactor (D16) — Innovation gain too small for risk.
- Looker dashboard polish (D17) — judges may not click it.
- Real Firebase Auth implementation (vs hiding banner) — wastes 2-3 hours for zero scoring lift.
- Additional A2A peer (#5, #6) — 4-peer story is already strong.
- Demo video V3 — only the v2.1 reassembly is sanctioned; no v3 budget.

If any of these come up during execution, **log to TODOS.md and move on**.

---

## §7 — What the prior review missed (that this review catches)

1. **Live ID determinism is mostly real.** Prior review treated reproducibility as a 50/50 risk; live verification shows 4/5 IDs are deterministic. The proof beat's narrative power is higher than expected.

2. **Audio side is already locked.** Memory + prior CEO review both implicitly treated voice production as forward work. Git log shows it's done. Saves ~2-3 hours of mental load when sequencing.

3. **ranger_unit randomness is the cheapest P0 in the punch list.** 15-min fix. Should be A1 — leads the new sequence — because it converts a credibility risk into an "every ID is deterministic" demo asset.

4. **The unblocked work pool is larger than V2_PLAN §12.4 implied.** A1-A7 = ~95 minutes of CC work that can happen *before* Omar pastes a single token. The current rhythm-loss issue is partly because we treated the Mapbox blocker as serializing all remaining work.

---

## §8 — Verdict

**CLEAR.** Mode held (HOLD SCOPE). Plan held (Option B). Sequence refined (A1-A7 unblocked work first, then B1-B5 Omar-token-gated work, then C1-C4 finalize/submit).

**Single most important action now:** Start A1 (seed `ranger_unit` by `incident_id`). 15 minutes. Converts P0 #7 from "credibility landmine" into "the reproducibility claim is real."

**Track 3 odds re-estimated:** with Option B + A1-A7 cleanly executed + Omar unblocking Mapbox + Firebase within 24h = **15-20%** (up from V2_PLAN's 12-18% because the reproducibility story turned out stronger than estimated).

**Awaiting handshake:** codex consult on this review before execution.

---

## §9 — Codex handshake (2026-05-17 00:50 UTC, gpt-5-codex)

**Codex verdict: RECONSIDER.** Accepted in full. Codex's amendments are absorbed below.

### §9.1 — What codex challenged

1. **Mode drift.** "HOLD SCOPE" assumes Option B is viable *once Omar pastes tokens*. We are now ~24h past the prior commit with zero token movement. That is *scope reduction in reality, not scope hold.* Every idle hour waiting on tokens burns the 6-9h CC budget.

2. **Option B risk dominates.** All the Demo-score uplift in Option B is gated on Mapbox + Firebase config from Omar. Option A unlocks the *same* codex P0s (banner, ID consistency, proof frame) without producer gating.

3. **Sequence still serializes on Omar.** The CEO review parked Firebase-banner suppression (P0 #1) and 2-issues-toast suppression (P0 #2) inside the Omar-gated tier (B3). Both are pure CSS / feature-flag work. They can ship today.

4. **P0 coverage is overstated.** `scripts/video/segments.json:74` still ships stale IDs (`PSR-9737`, `MUTAID-A019282A32`, `FUND-A0192B2A32`). Until that file moves, codex P0 #7 stays open. The 2-call determinism check is too sparse to celebrate — need a 10-call automated harness.

### §9.2 — Better path codex proposes (Option A-first, Mapbox additive)

Invert trunk and stretch:

| New order | Task | Blocked on Omar? | Effort |
|---|---|---|---|
| 1 | Deterministic ID script fix in `segments.json` `07-demo-fanout` (drop PSR-9737; fix FUND/MUTAID typos) + re-render affected cards | No | 25 min |
| 2 | Seed `ranger_unit` by `incident_id` in `app/tools/peer_handlers.py` so PSR is reproducible per incident | No | 15 min |
| 3 | Determinism harness `scripts/dev/verify_ids.py` — 10 back-to-back POSTs, fails on any variance | No | 25 min |
| 4 | CSS / feature-flag suppression of Firebase banner + 2-issues toast for demo build | No | 30 min |
| 5 | Proof frame (`09-proof`) update: "Mapped to ESRS E4 (materiality assessed)" wording, deterministic IDs only | No | 15 min |
| 6 | Re-record Option A demo phase against `localhost:3000` (Ops Center with banner hidden, no Mapbox) | No | 45 min |
| 7 | Reassemble v2.1 Option A cut + codex slop sweep | No | 50 min |
| 8 | Producer escalation: 2h window for Omar to deliver Mapbox + Firebase configs. If miss → freeze on Option A v2.1 cut. | Omar | escalation, not blocker |
| 9 | *(stretch)* If tokens land: pre-render Mapbox sequence + composite into demo beat → v2.2 stretch cut | YES | 90-120 min |
| 10 | Stranger lean-in test + Devpost submit | Omar | variable |

**Net effect:** there is a shippable v2.1 (Option A) within ~3.5 CC hours regardless of Omar's token timing. The Mapbox path becomes a stretch upgrade, not a blocker.

### §9.3 — Codex amendments not directly absorbed (and why)

- **"Re-open the Firebase-auth ban from §6"** — codex argued real Firebase auth removes 2 P0s at once. **Held to scope freeze.** CSS suppression solves the same problem in 30min vs 2-3h of real auth wiring. If CSS proves fragile in step 4, revisit.
- **"Automate determinism check"** — fully absorbed as step 3.

### §9.4 — Updated track 3 odds

With Option A-first + steps 1-7 cleanly executed = **10-13%** as a guaranteed floor.
If steps 8-9 also land cleanly (Omar tokens within 24h + Mapbox pre-render works first try) = **17-22%**.

Better expected value than the prior plan because the floor is no longer zero.

### §9.5 — Revised verdict

**CLEAR-WITH-AMENDMENTS.** Trunk = Option A. Stretch = Mapbox via pre-render. Start with step 1 (deterministic ID script fix).

