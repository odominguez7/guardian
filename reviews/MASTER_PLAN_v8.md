# GUARDIAN v8 — Master Plan to Win Track 3

**Generated:** 2026-05-17
**Submission deadline:** 2026-06-05 5pm PT (19 days)
**Judging:** 2026-06-11 → 06-18
**Winners:** 2026-06-22

## Track confirmation: Track 3 — Refactor for Google Cloud Marketplace + Gemini Enterprise

Verified against PDF rules: GUARDIAN already meets all 4 architectural mandates.
- ✅ B2B focus (F500 sponsor → park ↔ funder ↔ neighbor)
- ✅ Cloud-Native Runtime (Cloud Run for orchestrator + 4 peers + ops-center)
- ✅ Vertex-Powered Intelligence (Gemini 2.5 Pro + 2.5 Flash + Vertex AI Search)
- ✅ A2A Interoperability (v0.3.0, 4 independent peers, real fan-out)

Mandatory technologies: Gemini API ✅ · ADK 2.0 ✅ · Cloud Run ✅.

## Prize math
- **Grand Prize**: $15K + $10K Cloud Credits + VIP Bay Area + Addy Osmani coffee
- **Best of Theme (Refactor)**: $10K + $7.5K credits — **this is our realistic target**
- **Regional (APAC/EMEA)**: $5K + $2.5K (we're not in either — N/A)
- Each project = max 1 prize

## Judging criteria (weighted)

| Criterion | Weight | What it asks |
|---|---:|---|
| Technical Implementation | 30% | Clean code, ADK core-concept use |
| Business Case | 30% | Compelling B2B problem + impact |
| Innovation & Creativity | 20% | Novel, original, unique solution |
| Demo & Presentation | 20% | Clear problem, effective demo + docs, ADK explanation, architectural diagram |

## Honest gap analysis (today's score vs Best-of-Theme cutoff)

| Lens | Now | After v8 | Why the gap |
|---|---:|---:|---|
| Technical 30% | 24/30 (8.0) | 28/30 (9.3) | Need: Agent Engine deployment, ADK Eval real trajectories in CI, cleaner ARCHITECTURE.md, MCP tool list |
| Business 30% | 21/30 (7.0) | 27/30 (9.0) | Need: procurement pack stub (SOC2/MSA/DPA), Marketplace LISTING polish, market sizing slide |
| Innovation 20% | 18/20 (9.0) | 18.5/20 (9.3) | Already strong — Falsifier adversarial agent + 4-peer A2A + live-cam Spot Now is genuinely novel |
| Demo 20% | 12/20 (6.0) | 19/20 (9.5) | Critical gap — no 2-min producer-quality video yet. Architecture diagram exists but isn't IN a video |
| **Total** | **75/100** | **92.5/100** | Best-of-Theme realistic at 88+ |

## 19-day execution chart with codex handshake gates

| Day | Date | Block | Deliverable | Codex gate |
|--:|------|-------|-------------|----------|
| 1 | 2026-05-17 | TODAY: master plan + handshake | this doc + codex CLEAR | ✓ |
| 2 | 2026-05-18 | Mission Bridge v2: photo-real Imagen 4 faces + Veo 3.1 lip-sync intros + dynamic agent stage | 10 new portraits, 10×4s clips, new layout | ✓ |
| 3 | 2026-05-19 | Vertex AI Agent Engine deployment (Track 3 explicit) | live Agent Engine endpoint + docs | ✓ |
| 4 | 2026-05-20 | ADK Eval real trajectories in CI | 6 evalsets passing nightly | ✓ |
| 5 | 2026-05-21 | Procurement pack stub | marketplace/PROCUREMENT.md (SOC2/MSA/DPA checklists) | ✓ |
| 6 | 2026-05-22 | Marketplace LISTING polish + pricing 3-tier rev | LISTING.md final | ✓ |
| 7 | 2026-05-23 | o22 brief authorship (2-min video script) | briefs/guardian-hero.yaml + cinematography prompts | ✓ on script |
| 8 | 2026-05-24 | o22 render run (~$6 budget) | 4 MP4 variants + SRTs in tools/o22-render/output/ | — |
| 9 | 2026-05-25 | Live-platform footage capture (Mission Bridge, Live Cams Spot Now, Operations fan-out) | screen recordings + voice-over takes | — |
| 10 | 2026-05-26 | Stitch 2-min cut (o22 variants + platform footage + agent narrations) | guardian-demo-v1.mp4 | — |
| 11 | 2026-05-27 | Producer review v1 → iterate | guardian-demo-v2.mp4 | producer ✓ |
| 12 | 2026-05-28 | Devpost text writeup + arch diagram polish | submission-draft.md + arch.svg | ✓ |
| 13 | 2026-05-29 | Public repo cleanup (README + ARCHITECTURE + RUNBOOK) | repo polished | ✓ |
| 14 | 2026-05-30 | End-to-end audit + codex final handshake | submission-ready | ✓ |
| 15 | 2026-05-31 | Buffer / fixups | — | — |
| 16 | 2026-06-01 | Producer stranger test (3 non-team viewers) | feedback log | — |
| 17 | 2026-06-02 | Stranger-test fixes | clean | ✓ |
| 18 | 2026-06-03 | Producer final approval of video + writeup | ✓ producer sign-off | — |
| 19 | 2026-06-04 | Submit on Devpost; verify all renders | submitted | — |
| 20 | 2026-06-05 | Buffer day (deadline 5pm PT) | — | — |

**14 codex handshake gates** across the 19-day arc. Each gate must clear before the next day's work starts.

## Six work streams

### A. Mission Bridge v2 (Day 2)
**Problem:** producer 6/10 → wants 9/10. Current portraits are okay but the cards + icons feel static.

**Approach:**
1. Re-render 10 agent portraits with photo-realistic Imagen 4 prompts:
   - 5 specialists with distinct human-recognizable faces (cinematic documentary photography)
   - Falsifier with adversarial stance (counter-stage)
   - 4 A2A peer "operators" with distinct uniforms/badges (Park Service ranger, F500 sustainability officer, conservation funder, neighbor park ranger)
2. Generate 10 Veo 3.1 Fast 4-second lip-sync clips: each agent speaks their intro line. Replace static portrait with clip on hover/active.
3. Rebuild MissionBridge.tsx topology: less grid, more "control room" depth. Orchestrator center, specialists ringing on a curve, peers on the outer arc, Falsifier on a slightly elevated counter-stage.
4. Add ambient pulse animation that traces data flow between active agents.

**Cost:** Imagen 10 × $0.04 = $0.40 · Veo 10 × $0.10/s × 4s = $4.00 · total ~$4.40 + retries

### B. Vertex AI Agent Engine deployment (Day 3)
**Track 3 mandate** explicitly mentions "Agent Engine Runtime" as a valid infra target. Deploying the orchestrator on Agent Engine (alongside Cloud Run) shows we hit ALL mandated infra options. Bonus signal for tech-rigor judges.

**Approach:** add `app/agent_engine_deployment.yaml` + GitHub Actions workflow that deploys on push to main. Keep Cloud Run as the public-traffic surface; Agent Engine as the ADK-blessed runtime for the agentic flows.

### C. ADK Eval framework real trajectories (Day 4)
We have 6 evalsets defined but they're synthetic. Wire them into a nightly GitHub Action that runs `adk eval` and posts pass/fail to repo. This is exactly what "Technical Implementation (30%) - ADK core concepts" rewards.

### D. Procurement pack stub (Day 5)
F500 buyers need: SOC 2 Type I roadmap, MSA template, DPA template, security questionnaire pre-filled, pricing rate card. Stub these in `marketplace/PROCUREMENT.md`. Doesn't need to be SOC 2 certified — just needs to show we've thought about the procurement journey.

### E. o22 video pipeline (Days 7-11)
Vendor o22-studio at `tools/o22-render` (DONE today, pinned to commit `d1dbc4e` rev13). Author a 2-min hero brief that:
- Opens with the F500 CSO pain (TNFD disclosure, audit-grade evidence)
- Shows the live cam → Spot Now → Gemini Vision → Falsifier → 4-peer fan-out chain
- Highlights the Marketplace listing surface
- Closes with the team + tech stack

o22 outputs 4 hook variants + body shots. We stitch with platform screen recordings into a 2-min final cut.

### F. Stranger test (Days 16-17)
Producer shows the demo + repo to 3 non-team people. Capture which moments confuse, which delight, what they remember 24 hours later. Iterate.

## Bonus: more public wildlife/zoo webcams (nice-to-have)

NPS already gives us 4 working cams. Adding more is low-priority but easy. Best additional candidates (need to probe each):
- **Brooks Falls bears (Katmai NP)**: uses explore.org / YouTube — likely blocked
- **Smithsonian Zoo cams**: iframe-only, JPEG endpoint not exposed
- **HDOnTap wildlife streams**: paid embed, need partnership
- **Monterey Bay Aquarium jellies/otters/sharks**: HLS via their player, URL not exposed in HTML
- **MORE NPS cams**: confirmed working: Glacier (5+ cams), Yellowstone (8 cams), Isle Royale (5 cams), Joshua Tree (Painted Hills, SheepRock)

**Recommendation:** stay with the 4 NPS cams we have. They reliably catch wildlife (Yellowstone bison/elk/wolves; Isle Royale moose/wolves). Adding more is purely cosmetic.

## Codex handshake amendments (Day 1 absorptions)

Codex returned CLEAR on the plan with 4 WARNs + 4 NITs absorbed below.

**Demo timing front-loading (WARN)**: Days 7-10 had zero slack for script + render + capture + cut. Updated:
- Day 7 — author brief + **start platform screen capture in parallel**
- Day 8 — o22 render run + finish capture
- Day 9 — assemble first rough cut + render second variant pack
- Day 10 — finalize cut

**Agent Engine + CI access (WARN)**: starting today (Day 1) — file Agent Engine allowlist request + create the GitHub Actions workflow skeleton so Day 3-4 has no infra surprises.

**o22 budget reconciliation (WARN)**: producer's vendored o22-studio retail variant pack = $79 = ~$25 of compute per pack (~10× $0.04 Imagen + ~$24 Veo + ~$0.06 Lyria). A 2-min final cut needs ~1-2 full variant packs + 4-6 extra Veo body shots. Realistic budget: **$30-50 total** (matches the Risks section, not the $6 line in Day 8). Day 8 line corrected. Tier-1 Veo quota fits this volume.

**Submission logistics (WARN)**: added Day 13.5 sub-task:
- Devpost form field draft (description, tagline, technologies-used, video URL, public-repo URL, demo URL, team list, accept rules)
- Judge access setup: ops-center URL is already public; document orchestrator A2A discovery URL + how to trigger Spot Now
- Recording quality: verify the 2-min video file uploads under Devpost's 100MB limit + plays in their embedded player

**Mission Bridge A/B fallback (NIT)**: keep current `/portraits/*.png` set in place as `*-v1.png` and ship new `*-v2.png` alongside. UI gets a `?bridge=v1` query param to swap back. If producer dislikes realistic faces, no Day 2 lost.

**92.5 target framing (NIT)**: communicating internally as **stretch**. Realistic floor: **88-90**, which still lands Best-of-Theme zone.

## What's NOT in scope for v8

- Residential-IP proxy to bypass YouTube anti-bot (~$20/mo, v9 if we want true literal-current-second YouTube)
- Vertex AI Memory Bank (pattern-of-life across incidents) — would be a Track 3 differentiator but adds 2-3 days
- Live Audio Agent via Gemini Live API — would let Audio Agent listen to live cam mic — out of scope
- Custom MCP server — could be a tech-rigor win but adds 1 day
- Smithsonian/aquarium scraping work — see Bonus section

## Risks

1. **o22 render quota** — Tier-2 Veo quota was filed 2026-05-16, approves ~2026-06-15 (AFTER submission). v7.7 used Veo at $0.10/s/render. 2-min video at variant-pack pricing = ~$30-50. Within budget.
2. **Stranger test reveals architectural gap** — if 3/3 strangers don't grok the F500/sponsor framing, we need a Days 18-19 rewrite.
3. **Mission Bridge v2 visual gamble** — if Imagen + Veo realistic faces look creepier than the current Imagen rev1 portraits, we revert to current and lose Day 2.

## Codex handshake protocol

Per §4.5 already proven across v4-v7: every Move ships → codex sweep → BLOCK/WARN/NIT → fixes → re-sweep until CLEAR. Same gate for each of the 14 listed below. Plan total budget: ~3 codex hours across 19 days.

## Next action

This document → codex handshake immediately. After CLEAR, start Day 2 (Mission Bridge v2 — Imagen + Veo realistic agent faces).
