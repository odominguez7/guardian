# GUARDIAN End-to-End Audit — 2026-05-17 night

_Producer asked for a brutal 1-10 evaluation across product, agentic depth, F500 enterprise readiness, competitive position, and self-learning loop maturity. Two specialist audits + 3 web searches synthesized below. Autonomous implementation authority granted for the highest-leverage recommendations._

## Honest scores

| Lens | Score | Headline |
|---|---|---|
| **F500 CPO (real procurement)** | **3.7 / 10** | Pilot candidate at $25-40K; would NOT sign at $180K Portfolio price. SOC 2 + DPA + Big Four reference customer = hard blockers. |
| **Agentic depth vs ADK 2.0** | **4.5 / 10** | Using bottom third of ADK 2.0 surface area. Missing every formal workflow agent, all of Live API, Memory Bank, the Eval framework, Agent Runtime, session features. |
| **Hackathon Track 3 rubric** | ~91 / 100 (codex's prior estimate) | Demo-strong, enterprise-light. Won't lose for visuals; could lose for "you didn't use the new ADK features." |

## Incumbent landscape (live web research today)

| Player | Position | Threat to GUARDIAN |
|---|---|---|
| **IBAT** (IUCN / UNEP-WCMC / BirdLife) | 700+ corporate users; dominant biodiversity assessment tool. Olam mapped 100% of cocoa/coffee/hazelnut across 58 countries. | High — IBAT owns the species/data authority moat |
| **Sweep** | Verdantix 2026 Green Quadrant Leader for enterprise carbon/TNFD reporting | High — has the CFO-comfortable carbon module + multi-cloud distribution |
| **SMART** (Spatial Monitoring and Reporting Tool) | 1,200 sites, 100+ countries. Used by WWF, Panthera, everyone serious in wildlife law enforcement | High in wildlife ops; orthogonal to F500 disclosure |
| **EarthRanger** (Allen Institute for AI) | Tech partner with WWF/WCS | Merging with SMART |
| **SERCA (2026)** | SMART + EarthRanger merger; rolls out late 2026 | **Massive future threat** — absorbs the feature moat GUARDIAN currently has |
| **Asuene** | Enterprise climate cloud with TNFD modules | Medium — Asia-focused, growing |

TNFD adoption: 733 orgs, $22T AUM as of Nov 2025. ISSB nature exposure draft expected Oct 2026 COP17.

## Where GUARDIAN actually wins vs incumbents (per CPO)

- **A2A multi-org coordination model** — IBAT is a query tool, SMART is a ranger tool, Sweep is a reporting tool. None natively model the **sponsor ↔ park ↔ funder ↔ neighbor** relationship that F500 conservation sponsorships actually have. This is the one architectural insight worth pricing.
- **Per-incident chain of custody with deterministic IDs + adversarial review** — SMART/SERCA log incidents for operational use; GUARDIAN structures them for DISCLOSURE use. Different artifact.
- **GCP-native committed-spend draw** — Procurement-friction killer that Sweep (multi-cloud) cannot match.

## Where GUARDIAN loses today

- Authority, install base, audit precedent
- Breadth of biodiversity datasets (IBAT's IUCN/UNEP-WCMC/BirdLife data lineage is the real moat — GUARDIAN's "7-doc wildlife corpus" is hackathon-grade)
- Field operations (SMART/SERCA win this for the decade)
- Procurement readiness (no SOC 2, MSA, DPA, customers, financials)

## Tools inventory + improvement opportunity

| Tool | Currently used | ADK 2.0 ceiling | Effort to add |
|---|---|---|---|
| Gemini 2.5 Pro (ADK orchestrator) | ✅ as `root_agent` with `sub_agents` | Could use `SequentialAgent` + `ParallelAgent` workflow patterns | 1.5 hr |
| Gemini 2.5 Flash | ✅ Falsifier + Audio + Species ID | Eval-tuned via ADK Eval framework | 90 min |
| Vertex AI Search | ✅ Species corpus RAG | Could ground Falsifier reasoning too | 15 min |
| Vertex AI Memory Bank | ❌ NOT USED | Pattern-of-life: "Tag-22 fired same signal 3 nights ago" | 75 min |
| Gemini Live API (audio/video) | ❌ NOT USED | Real-time stream sampling on YouTube live cam | 90 min |
| ADK Eval framework | ❌ NOT USED (have 23 pytest tests) | Trajectory eval + user simulation + visual debug UI | 90 min |
| ADK Sequential/Loop/Parallel workflow agents | ❌ NOT USED | Declarative agent topology vs LLM-prose routing | 1.5 hr |
| ADK Agent Runtime (deployment target) | ❌ Using Cloud Run | Native Google deployment surface (new in 2.0) | 30 min |
| A2A protocol v0.3.0 | ✅ 4 peers | Could expose Falsifier as A2A peer for external auditors | 60 min |
| Lyria 2 | ✅ ambient bed (now removed from Ops Center, retained in demo video) | — | — |
| Imagen 4 | ✅ 10 portraits + board slide art | — | — |
| Veo 3.1 Fast | ✅ 4 wildlife clips + 1 hero | Replace Veo[0] with REAL YouTube live cam embed | 45 min |
| ElevenLabs (3rd party) | ✅ 9 voice clips | — | — |
| Nano Banana (gemini-2.5-flash-image) | ❌ NOT USED | Species-identity continuity across surfaces | deferred v5 |
| BigQuery Analytics | ✅ plugin wired | — | — |

## Live cam integration plan (producer's specific ask)

**Step 1 — visible quick win (45 min):** Replace one Live Cams tile (the elephant-dusk Veo) with an embedded YouTube live stream of Tembe Elephant Park (Africam). The chrome stays (CAM-XX label, LIVE dot, accent subtitle); the source changes from Veo MP4 to YouTube iframe. Demo line: "three rendered, one live from Tembe Elephant Park right now."

**Step 2 (deferred to v5):** Server-side frame sampling — `yt-dlp` grabs a 1280×720 frame every 12s, passes to `stream_watcher_agent.analyze_image_frame`, emits real classification events. Converts GUARDIAN from "fixture replay" to "live agentic system watching a real waterhole."

## Self-learning loop definition (concrete to ADK 2.0)

1. **Vertex AI Memory Bank** stores incident outcomes: `incident_id → {verdict, actual_outcome, time_to_resolution}`
2. **ADK Eval framework** runs nightly with Memory Bank as the environment. Custom metric `falsifier_calibration = correct_dissent_rate / total_dissents`. If <0.7, eval fails CI.
3. **Trajectory replay + session migrate**: when calibration drifts, replay the last 50 failing trajectories with the Falsifier instruction tuned (e.g., `audio_confidence` gate 0.5 → 0.6). Best-scoring variant gets promoted.

That's the GUARDIAN learns-from-its-misses loop in ADK 2.0 primitives, not vibes.

## Autonomous implementation queue (~5 CC hours)

Per producer's grant of autonomous authority:

| # | Move | Effort | Why |
|---|---|---|---|
| **A1** | YouTube live embed in Live Cams tile #1 (Tembe Elephant Park) | 45 min | Visible "this is real" lift, no incumbent has it |
| **A2** | `ParallelAgent` for peer fan-out | 45 min | Declarative ADK 2.0 pattern; researcher signal |
| **A3** | `SequentialAgent` wrapping Stream Watcher → Audio → Species ID → Falsifier → fan-out | 60 min | Replaces canned `pre_steps` prose with declared pipeline |
| **A4** | ADK Eval framework with 4 trajectories + 2 user-simulation scenarios | 90 min | The single highest-leverage feature against incumbents who can't ship eval suites |
| **A5** | Reposition marketplace LISTING as IBAT/SERCA **complement**, not replacement; add v3.2 features visibly; add Falsifier "Management Review Required" exception workflow stub to Court Evidence | 60 min | CPO's #3 conversion move — make incumbents A2A peers, not competitors |
| **A6** | Codex final handshake (when quota allows) + redeploy | 30 min | §4.5 gate |

**Deferred to v5 (out of autonomous budget):**
- Vertex AI Memory Bank wiring
- Gemini Live API on Audio Agent (real-time YouTube audio sampling)
- Server-side YouTube frame sampling
- Big Four design partner + signed auditor walkthrough memo
- Procurement-pack v1 (SOC 2 Type I, MSA, DPA, XBRL)
- Nano Banana species-identity continuity

## Verdict

GUARDIAN is a **strong hackathon demo + weak enterprise vendor**. The v3.2 work made it visually competitive. Today's autonomous queue adds the ADK 2.0 depth + live-cam realism + complement-not-compete positioning that converts it from a "competent demo" to a "this person read the docs and understood the market." The 1-10 score after this round, by my honest read, lands at: hackathon Track 3 ~94-96, F500 procurement ~5.0, agentic depth ~7.5.

Going to 98+ rubric on Track 3 + 8+ procurement requires v5 work (Memory Bank, Live API, Big Four partnership) that does not fit this submission's clock. Producer should choose between "ship v4.0 at 94-96 now" or "delay 7-10 days for v5.0 at 97-98."
