# GUARDIAN — Real-time Anti-Poaching & Biodiversity Defense Network

_Locked 2026-05-15. Track 3 (Refactor for Marketplace + Gemini Enterprise). Submission deadline 2026-06-05 5pm PT._

---

## §1 — Product

**One-line:** A multi-agent system that watches conservation areas in real time, detects poaching threats before they happen, coordinates ranger response across agencies, and auto-generates the TNFD/CSRD biodiversity reports Fortune 500 companies are now legally required to file.

**Who pays:**
- Tier 1: Fortune 500 corporate sustainability buyers (TNFD/CSRD compliance). $50-300K ACV. The market that pays.
- Tier 2: National parks + conservation orgs. $24-100K ACV.
- Tier 3: Insurance carriers underwriting biodiversity risk. Emerging market.

**Forcing function:** EU CSRD biodiversity reporting mandatory from 2025. TNFD Recommendations adopted by 500+ corporations. SEC climate rule. These buyers are looking for tooling NOW.

**Marketplace SKU:** "Gemini Enterprise for Biodiversity Operations" — clean fit into Google Cloud Marketplace.

---

## §2 — The agent system

### Orchestrator + 6 specialized agents + 4 A2A peers

```
                    ┌────────────────────────────────────────┐
                    │  Web UI (Cloud Run · Firebase Auth)    │
                    │  AG-UI streaming map + live feed       │
                    └────────────────┬───────────────────────┘
                                     │ HTTPS
                                     ▼
            ┌─────────────────────────────────────────────────┐
            │  Orchestrator Agent (Cloud Run #1)             │
            │  ADK LlmAgent · Gemini 3 Pro                   │
            │  agent.json (A2A card · v0.2 spec)             │
            └─┬─────┬─────┬─────┬─────┬─────┬───────────────┘
              │     │     │     │     │     │
       ┌──────▼─┐ ┌─▼──┐ ┌▼───┐ ┌▼──┐ ┌▼───┐ ┌▼─────────┐
       │ Stream │ │Audi│ │Spe-│ │Pat│ │Vis-│ │ Dispatch │
       │Watcher │ │o   │ │cies│ │ter│ │ual │ │  Agent   │
       │(Live)  │ │Agt │ │ID  │ │n  │ │izer│ │(AgentPh) │
       │Gemini  │ │STT+│ │G3P │ │BQ+│ │Imag│ │          │
       │Live    │ │Live│ │Vis │ │Spa│ │en  │ │          │
       └──┬─────┘ └─┬──┘ └──┬─┘ └─┬─┘ └─┬──┘ └─┬────────┘
          │         │       │     │     │      │
          ▼         ▼       ▼     ▼     ▼      ▼
        Camera   Mic    IUCN+ Spanner Cloud   SMS+
        feed     feed   CITES Graph   Stor.   Voice
        (mock)   (mock) corp.        (sketch)

        ┌───────────────────────────────────────────────┐
        │  Court-Evidence Agent (LlmAgent · Doc AI)    │
        │  Bundles all signals into legal evidence     │
        └───────────────────────────────────────────────┘

   ═══════════════════════════════════════════════════════
                  A2A PEERS  (HTTPS · agent.json · mTLS)
   ═══════════════════════════════════════════════════════
       ▲             ▲             ▲             ▲
       │             │             │             │
  ┌────┴────┐  ┌─────┴────┐  ┌─────┴─────┐  ┌────┴─────┐
  │ Park    │  │ Corporate│  │ Funder    │  │Neighbor  │
  │ Auth.   │  │ Sustain. │  │ Reporter  │  │ Park     │
  │ Agent   │  │ Agent    │  │ (NGO /    │  │ Mutual   │
  │(Run #2) │  │(Run #3 — │  │ philan-   │  │  Aid     │
  │         │  │ TNFD/CSRD│  │ thropic)  │  │(Run #5)  │
  │         │  │  report) │  │ (Run #4)  │  │          │
  └─────────┘  └──────────┘  └───────────┘  └──────────┘

  Each peer = independent Cloud Run service · own agent.json · own SA
  Each accepts/responds to A2A task requests · mutual mTLS
```

### Why each agent exists

| Agent | Job | Model | Distinguishing tool |
|---|---|---|---|
| **Orchestrator** | Routes signals to specialists, manages task state, exposes A2A interface to all 4 peers | Gemini 2.5 Pro (env-driven, see §5) | A2A SDK · ADK LlmAgent |
| **Stream Watcher** | 24/7 watches camera feeds (in prod) / processes recorded clips (in demo) | Gemini Live (video) | Gemini Live API |
| **Audio Agent** | Listens for gunshots, vehicles, distress, human voices | Gemini Live (audio) + Speech-to-Text | Audio classification |
| **Species ID** | Identifies species + individual animals (matriarch Echo) from frames | Gemini 2.5 Pro Vision | Vertex AI Vector Search over species embeddings |
| **Pattern Agent** | Cross-references with historical poaching, identifies entry routes, predicts next strike | Gemini 2.5 Flash | Spanner GraphRAG · BigQuery |
| **Visualizer** | Generates suspect sketch from low-res frames; renders heatmaps | Imagen 4 + Nano Banana Pro | Imagen API |
| **Dispatch** | Notifies rangers via SMS/voice/radio | Gemini 2.5 Flash | AgentPhone MCP |
| **Court-Evidence** | Packages signals into chain-of-custody evidence bundle | Gemini 2.5 Flash | Document AI |

### The 4 A2A peers — and why this is Track 3's strongest A2A story

| Peer | What it is | Why A2A (not API) |
|---|---|---|
| **Park Authority Agent** | Independent agent run by the park (mocked from us, but separate Cloud Run service with its own agent.json) | Different org, different trust boundary, different schedule of operations |
| **Sponsor Sustainability Agent** | Agent run by a Fortune 500 sponsor needing TNFD/CSRD report data | Sponsor + park need bidirectional reporting without sharing DBs |
| **Funder Reporter Agent** | An impact-reporting agent operated by a conservation funder (e.g., wildlife NGO or philanthropic program — WWF / IUCN style; not canonical, examples only) | Funder wants periodic impact reports without raw access to park data |
| **Neighboring Park Mutual-Aid Agent** | Adjacent reserve's incident response agent | Cross-border coordination during chase events; agents from rival jurisdictions |

Track 3 says: _"Your agent's communication layer must utilize the Agent-to-Agent (A2A) protocol, ensuring it can be seamlessly discovered by and coordinate with other enterprise agents."_ GUARDIAN ships 4 distinct enterprise agents that aren't owned by us. That's the literal mandate fulfilled, with receipts.

---

## §3 — Data + state layer

| Service | Role | Used by |
|---|---|---|
| **Vertex AI Search** | RAG over IUCN Red List, CITES, public Snapshot Serengeti, ranger SOPs | Species ID + Pattern + Court-Evidence |
| **Vertex AI Vector Search** | Per-individual-animal embeddings (Echo, etc.) | Species ID |
| **Vertex AI Memory Bank** | Long-term memory: this park's known animals, prior incidents, agent state | Orchestrator |
| **Spanner (smallest instance)** | GraphRAG: species ↔ park ↔ pattern ↔ ranger ↔ funder relationships | Pattern Agent |
| **BigQuery** | Historical poaching incidents, eval set, Looker dashboard backend | Pattern + Court-Evidence + AgentOps |
| **Firestore** | Real-time session/task state, A2A handshake state | Orchestrator + all peers |
| **Cloud Storage** | Raw video clips, audio captures, generated sketches | Stream + Audio + Visualizer |
| **Memorystore (Redis)** | Tool-call cache, reduces inference cost | Orchestrator |
| **Pub/Sub** | Async event bus between agents | All |

---

## §4 — AgentOps spine

Bootstrap via Agent Starter Pack: `uvx agent-starter-pack create guardian -a adk@gemini-fullstack`. Out of the box:

- **Terraform IaC** — every cloud resource reproducible
- **Cloud Build CI/CD** — per agent service, runs eval suite on every PR
- **Cloud Trace + OpenTelemetry** — full Reason/Act/Observe trajectory traces
- **Vertex AI eval** — 30+ golden trajectories run on every PR
- **Looker Studio public dashboard** — trace count, eval scores, tool-call success rate, p99 latency per agent
- **Cloud Logging → BigQuery audit sink** — durable trail for compliance

---

## §5 — Track 3 mandate checklist

| Mandate | Implementation | Receipt |
|---|---|---|
| B2B core function | Fortune 500 TNFD/CSRD compliance reporting; conservation orgs; insurance underwriters | Pricing page, customer persona doc |
| Cloud-Native Runtime | All 5+ Cloud Run services with Terraform | `infra/main.tf` |
| Google Cloud Powered Intelligence | Gemini 2.5 Pro orchestrator + 2.5 Flash sub-agents + Gemini 3 Flash Preview for evals + Gemini Live (later) | `GUARDIAN_ORCHESTRATOR_MODEL` env var, ships on 2.5 Pro; auto-upgrades to 3 Pro by env flip when Vertex allowlist lands |
| **A2A Interoperability** | 4 distinct peer agents in separate Cloud Run services, each with `agent.json` + mTLS. Tiered: Park + Corp Sustainability = full bidirectional A2A flows; Funder + Neighbor = lighter request/response. | Public agent.json URLs |
| Marketplace-ready | **Real Marketplace listing submission attempt** to Google by D22 + pricing page + SOC 2 readiness checklist | `marketplace/` folder + actual submission receipt |

---

## §6 — Submission artifacts (required by Devpost)

1. **Code** — public GitHub repo `guardian` under odominguez7
2. **Video** — 3-min walkthrough hosted on YouTube/Loom; embed in submission
3. **Architecture diagram** — Mermaid rendered to SVG; lives in `docs/architecture.md`
4. **Testing access** — live demo URL on Cloud Run with a test login (Firebase Auth seeded account)
5. **Bonus differentiators not strictly required:**
   - Live Looker Studio dashboard link
   - Marketplace listing intent letter
   - SOC 2 readiness checklist
   - Public `agent.json` URLs for each peer

---

## §7 — Budget plan (target: stay under $1,500 of $1,991 ceiling)

| Item | Estimated cost | Strategy |
|---|---|---|
| Gemini 3 Pro dev inference | $40-80 | Hard cap via Vertex AI quota |
| Gemini 2.5 Flash sub-agents | $5-15 | Cheap, no constraint |
| Gemini Live (audio + video) | $80-200 | Pre-recorded clips for demo, not continuous streaming |
| Vertex AI Search queries | $20-50 | Cache via Memorystore |
| Vertex AI Vector Search | $30-60 | Smallest tier |
| Spanner (smallest, 22 days × 24h × $0.30) | $158 | Run 12 days only (start D9) → ~$86 |
| Imagen 4 | $5-15 | Few sketches |
| Nano Banana Pro | $5-10 | Character consistency for Echo + ranger sketches |
| Document AI | $40-100 | 50-100 evidence pages |
| Cloud Run + Firestore + BigQuery | $30-60 | Scale-to-zero |
| AgentPhone (SMS/voice) | $20-40 | Limited demo use |
| Pub/Sub + Memorystore + Cloud Storage | $10-25 | Free tier covers most |
| Buffer | $200 | Re-renders, eval suite runs |
| **TOTAL** | **~$700-1,150** | Comfortably under ceiling |

Apply to GFS Cloud Program ($350K) Day 1 anyway — removes any constraint and is free to apply.

---

## §8 — 22-day execution schedule (locked)

### Actual progress log (live)

**End of calendar D1 (2026-05-15) — effective deliverable day: D15+ (Operations Center shipped 14 days early).**

| Plan day | Status | Date shipped | Evidence |
|---|---|---|---|
| D1 | ✅ SHIPPED | 2026-05-15 | github.com/odominguez7/guardian, Cloud Run service `guardian-180171737110.us-central1.run.app` |
| D2 | ✅ SHIPPED (pulled forward) | 2026-05-15 | Vertex AI Search data store `guardian-collection` + search engine `guardian-search-dev` + 7-doc wildlife corpus, test query returns expected ranking |
| D3 | ✅ SHIPPED | 2026-05-15 | Stream Watcher live, 2 ADK eval trajectories, live in playground at localhost:8501 |
| D11 | ✅ SHIPPED (pulled forward) | 2026-05-15 | Park Service A2A peer at `guardian-park-service-180171737110.us-central1.run.app`, 3/3 integration tests, live ranger dispatch verified |
| D12 | ✅ SHIPPED (pulled forward) | 2026-05-15 | Sponsor Sustainability A2A peer at `guardian-sponsor-sustainability-180171737110.us-central1.run.app`, 3/3 integration tests, live TNFD filing verified, fan-out reconciliation via deterministic `incident_id` |
| **D15** | ✅ **SHIPPED (pulled forward 14 days)** | 2026-05-15 | **GUARDIAN Operations Center at `guardian-ops-center-180171737110.us-central1.run.app`. Next.js 16 + Mapbox GL JS + Firebase Auth + Framer Motion. Live event firehose (WebSocket), 3 demo scenarios, animated incident cards, ranger + TNFD ack cards, dashed A2A fan-out arrows on the map. Cinema-grade demo surface judges can click + screen-record.** |

**Bonus work D1 (not in original plan):**
- 5 cross-model / structured reviews CLEAR: Claude `/review`, `/plan-ceo-review` (x2), `/plan-eng-review`, OpenAI `/codex review`, AND `/codex challenge` adversarial sweep (x3 — peers, Ops Center, final)
- Codex challenge sweeps caught 1 P0 + 13 P1 issues — all 14 fixed inline + redeployed + verified end-to-end
- Boot-time GCP auth hardened in 7 files; service-to-service Cloud Run ID token auth wired into A2A client; APP_URL injected so agent cards advertise correct URLs in prod
- Deterministic `incident_id` (no UTC date baked in); sponsor `filing_id` + `reporting_period` anchored on `observation_timestamp`
- /demo/run protected by 15s per-scenario cooldown + asyncio.Lock (no spam-abuse, no incident_id collisions on concurrent triggers)
- CORS credentials properly gated; event firehose loop-safe across sync/async/threadpool callers
- **GUARDIAN Operations Center**: full Live Operations dashboard at `guardian-ops-center-...run.app` — Next.js 16, Mapbox GL JS, Firebase Auth scaffold, real-time WebSocket event stream, animated incident cards, dashed A2A fan-out arrows on the map. Verified live: scenario click → map pin pulse + amber arrows → incident card with ranger PSR-XXXX (8min ETA) + TNFD-2026-XXXXX filing ack. Cinema for the 3-min video.
- `TODOS.md` cataloging 30+ deferred P2/P3 items; `MAPBOX_USAGE_MONITORING.md` documenting free-tier limits + token-restriction polish path
- AgentPhone MCP availability verified for D8 (no Twilio fallback needed)
- ~20 commits pushed to `origin/main`

**CEO review 2026-05-15 (evening) cherry-picks for D2-D22:**

| # | Decision | Direction | Rationale |
|---|---|---|---|
| 1 | Peers #3 + #4 next | PRIORITIZE before more sub-agents | Locks 4-peer Track 3 mandate; template copies, ½ day each |
| 2 | Pattern Agent (D6) | YES build | Produces visible "historical poaching corridor" narrative in demo |
| 3 | Spanner GraphRAG | DOWNSCOPE to BigQuery-only | Saves $86 + 1 day; demo doesn't notice the difference |
| 4 | Court-Evidence Agent (D9) | YES build | Real PDF artifact judges can click; high demo value |
| 5 | Audio Agent (D4) | SHIP THIN | One-tool classifier; ~2 hr; needed for multi-modal story |
| 6 | Species ID (D5) | SHIP THIN | Vertex Vector Search over existing corpus; ~3 hr |
| 7 | Visualizer (D7) | CUT or pre-render | Imagen sketch is cinema-only; pre-rendered placeholder in demo video saves 1 day |
| 8 | Dispatch (D8) | STUB with AgentPhone hook | Mock dispatch_rangers ack; keep AgentPhone MCP code path documented |
| 9 | ParallelAgent (D16) | PULL FORWARD to D5 | Each new sub-agent benefits; foundational |
| 10 | Frontend polish | +map-load counter widget, scenario history | ~30 min each |
| 11 | F500 voiceover | Research already done (KPMG quote) | Use `docs/demo-opener-quotes.md` |
| 12 | Marketplace listing draft | YES D18 | Track 3 mandate |
| 13 | Demo video | D19-D21 from live Ops Center | Press scenario button + screen-record |

**Remaining critical-path agents:** D4 Audio, D5 Species ID, D6 Pattern + Memory Bank, D7 Visualizer, D8 Dispatch, D9 Court-Evidence, D10 Spanner GraphRAG, D13 Funder peer, D14 Neighbor peer, D15 Frontend, D16 ParallelAgent refactor.

---

### Locked schedule (original)

| Day | Date | Milestone | Concrete deliverable |
|---|---|---|---|
| **D1** | 2026-05-15 | Repo + GCP project + auth verified + Agent Starter Pack scaffold cleanly applied | github.com/odominguez7/guardian + GCP project `guardian-gfs-2026` + Cloud Run live |
| D2 | 05-16 | Hello-Agent on Cloud Run with `agent.json` + Vertex AI Search index seeded (IUCN, CITES, Snapshot Serengeti) — _search seeding pulled forward to D1_ | Live HTTPS URL + queryable corpus |
| D3 | 05-17 | Stream Watcher agent processes 1 sample clip → emits structured event | Sample clip detected |
| D4 | 05-18 | Audio agent detects gunshot/vehicle in sample audio | Audio classified |
| D5 | 05-19 | Species ID agent identifies 5 individual animals from frames | Echo recognized |
| D6 | 05-20 | Pattern agent online with BigQuery historical data + initial Spanner schema + **Memory Bank wired** (eng review 2026-05-15 pulled Memory Bank forward from D16 to avoid Pattern Agent refactor) | Cross-reference works |
| D7 | 05-21 | Visualizer agent generates suspect sketch from blurry frame + heatmap | Imagen output visible |
| D8 | 05-22 | Dispatch agent sends SMS to a test phone (eng review 2026-05-15: verify AgentPhone MCP availability D1; fallback Twilio direct if unavailable) | Real SMS arrives |
| D9 | 05-23 | Court-Evidence agent packages a sample incident → PDF | PDF generated |
| D10 | 05-24 | Spanner GraphRAG live; Pattern agent uses it | Graph queries work |
| D11 | 05-25 | **A2A Peer #1**: Park Authority agent (Cloud Run #2) + handshake works — _front-loaded to D1_ | A2A handshake on video |
| D12 | 05-26 | **A2A Peer #2**: Corporate Sustainability agent (auto-files TNFD entry) — _front-loaded to D1_ | TNFD JSON output |
| D13 | 05-27 | **A2A Peer #3**: Funder Reporter agent (sends impact report) | Sample report |
| D14 | 05-28 | **A2A Peer #4**: Neighboring Park Mutual-Aid agent | Cross-border handoff |
| D15 | 05-29 | Frontend Cloud Run app w/ Firebase Auth + AG-UI streaming map + live feed (eng review 2026-05-15 locked **Firebase Studio** as the scaffolding tool — Track 3 stack-maximization bonus + fastest path to a working demo URL) | Demo UI live |
| D16 | 05-30 | Vertex AI eval green. **Trajectory tests already at ~30 from continuous 2/agent ramp.** (Memory Bank moved to D6 per eng review.) **Refactor specialist chain to ADK `ParallelAgent`** so Stream/Audio/Species/Pattern run concurrently — cuts real-time chain latency ~90s → ~30-40s, strengthens Innovation 20% story | Eval green on PR + parallel chain in playground |
| D17 | 05-31 | Looker Studio dashboard public + Cloud Trace permalinks; security pass (mTLS, RLS) | Dashboard URL |
| D18 | 06-01 | **Real Marketplace listing submission attempt to Google** + pricing page + SOC 2 readiness checklist | Marketplace submission receipt + `marketplace/` folder |
| D19 | 06-02 | Pre-record demo clips + run agent end-to-end live | Demo footage |
| D20 | 06-03 | 3-min video v1 + architecture diagram polished + README polished | Submission v1 |
| D21 | 06-04 | `/codex review` + `/review` + outside-voice pass; fix top issues; re-record video | Submission v2 |
| D22 | **06-05** | Final dry run; submit on Devpost before 5pm PT | **SHIPPED** |

**Cut-the-line discipline:** If we slip past D14, cut the Funder peer (#3) first, then Neighbor peer (#4). NEVER cut Park Authority + Corporate Sustainability (#1, #2) — those carry the Track 3 A2A mandate.

**Continuous test ramp (revised 2026-05-15):** Each specialist agent ships with 2 ADK eval trajectory tests on its merge day. ~14 tests by D9, ~30 by D16 naturally — replaces the D16 mega-push.

---

## §9 — Demo video storyboard (3 min, F500-first cut — revised 2026-05-15)

**Positioning rule:** GUARDIAN is an enterprise compliance platform that happens to protect endangered species. Lead with the buyer. Animals are the data, not the hero. Kills the "feels non-profit" risk (§12).

| Sec | Beat | What viewer sees |
|---|---|---|
| 0:00-0:15 | Hook | F500 sustainability officer at her desk. On-screen quote (real, attributed): "[F500 CSRD officer quote about biodiversity reporting pain]." Voiceover: "EU CSRD requires every Fortune 500 to file biodiversity impact data. Most can't even prove they have it." |
| 0:15-0:45 | The product | "GUARDIAN is a multi-agent system that watches conservation areas your sponsor portfolio funds, detects threats in real time, and auto-files the TNFD entries you owe the regulator. One platform. Two outcomes." |
| 0:45-1:45 | **THE LIVE DEMO** | Split-screen mode optional. Real-time agents collaborating: Stream Watcher detects vehicle → Audio agent confirms engine noise → Species ID identifies endangered elephant herd in path → Pattern agent flags route as historical poaching corridor → Visualizer generates suspect sketch → A2A handshake with Park Authority agent → Dispatch sends ranger SMS → Court-Evidence agent bundles legal packet → **Corporate Sustainability agent A2A handshake auto-files TNFD entry into the F500 dashboard** (close on this — it's the punchline). **All 4 A2A peers visible on screen.** |
| 1:45-2:15 | The architecture | 10-second architecture diagram walkthrough. Highlight 5 Cloud Run services + Vertex AI Search + Spanner GraphRAG + Memory Bank + AgentOps eval suite. |
| 2:15-2:45 | The business case | "$300B biodiversity reporting market. EU CSRD mandates compliance for every Fortune 500. GUARDIAN ships on Google Cloud Marketplace with 4-peer A2A interop, 30 golden trajectory evals, and SOC 2 readiness." |
| 2:45-3:00 | The ask | "Built on Gemini, ADK, A2A, and Cloud Run. Live at guardian.{domain}.com. Source: github.com/odominguez7/guardian." |

---

## §10 — Scoring math (target: 91/100, grand-prize contention)

| Criterion | Weight | Target | Source of points |
|---|---|---|---|
| Technical | 30% | **28/30** | 4-peer A2A · multi-agent ADK · Spanner GraphRAG · Memory Bank · AgentOps spine (eval suite + golden trajectories + Looker dashboard + Cloud Trace + BigQuery audit) |
| Business Case | 30% | **28/30** | Forced-buyer narrative (EU CSRD) · $300B market · Marketplace listing draft · 3-tier customer model · SOC 2 readiness |
| Innovation | 20% | **18/20** | Real-time multimodal in production · 4 distinct enterprise A2A peers · structurally-required (not bolted-on) A2A |
| Demo | 20% | **17/20** | Cinematic 3-min video · live cloud demo · public dashboard · Mermaid architecture diagram |
| **TOTAL** | 100% | **91/100** | Grand-prize contention; Theme winner near-certain if rubric is real |

---

## §11 — What's explicitly out of scope

- Real production camera-trap hardware integration (we use Snapshot Serengeti public dataset + sample clips)
- Mobile native app (web works for demo)
- Real customer signed contract (TNFD reporting narrative + named target accounts is sufficient)
- Multi-language support beyond English (later)
- True GKE deployment (Cloud Run is our target; GKE migration documented in roadmap)
- Foreman/AgentsArmy/YU integration

---

## §12 — Risks + mitigations

| Risk | Probability | Mitigation |
|---|---|---|
| Gemini 3 Pro unavailable in this project's Vertex AI | **Realized 2026-05-15** | Verified 404 across global/us-central1/us-east5/us-east4/europe-west4/asia-southeast1. Orchestrator runs on `gemini-2.5-pro` via `GUARDIAN_ORCHESTRATOR_MODEL` env var. Flip to `gemini-3-pro` the moment Vertex allowlist lands. Submit allowlist request via Cloud Console. |
| Veo unavailable / over quota | Low (not using Veo) | N/A — Imagen is enough |
| Gemini Live latency in demo | Medium | Pre-record agent runs; play them back during live demo session |
| Spanner cost overrun | Low | Start instance D10 only; tear down on D22 |
| A2A spec drift | Low | Pin to `a2a-protocol.org` v0.2 spec; document version in `agent.json` |
| 22 days too aggressive | Medium | Cut-the-line discipline documented above |
| "Feels non-profit" framing | Low (was Medium) | Storyboard §9 rewritten 2026-05-15 to lead with F500 sustainability officer + real attributed CSRD officer quote on-screen. Animals are data, not hero. |
| GFS Cloud Program approval too slow to unlock $350K | Low | Apply D1; not dependent on it for our budget |

---

## §13 — GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 2 | CLEAR (SELECTIVE EXPANSION 2026-05-15) | 7 cherry-picks accepted, 2 code-vs-plan mismatches caught (Gemini 3 Pro env-driven, F500-first storyboard) |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | CLEAR (2026-05-15) | 6 P2 issues, 0 critical gaps. 6 decisions locked: Vertex Search pulled to D1 (DONE), AgentPhone verify-then-fallback (VERIFIED, no fallback needed), Memory Bank pulled to D6, Firebase Studio frontend, ADK ParallelAgent refactor on D16, TODOS.md consolidation (DONE). |
| Codex Review | `/codex review` | Independent 2nd opinion | 1 | CLEAR (3 P1 findings, 3 fixed) | Caught 3 import-time GCP auth crashes Claude missed. All fixed via lazy init in 5 files. |
| Codex Challenge | `/codex challenge` | Adversarial sweep of D1 work | 1 | CLEAR (1 P0 fixed, 6 P1 fixed, 20+ P2 to TODOS.md) | Caught Cloud Run service-to-service ID token auth gap (would have broken the demo for any judge clicking the live URL). All P0/P1 fixed inline + verified: orchestrator-in-Cloud-Run → peer-in-Cloud-Run round-trip returns "Acks received". Agent cards now advertise correct Cloud Run URLs. |
| Adversarial | `/review` adversarial pass | Always-on per-diff | 1 | CLEAR | 10 findings (1 fixed, 9 deferred to D17 polish + TODOS.md) |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | optional, run D15 with frontend |

**CODEX:** 3 import-time auth crashes (app/agent.py, app/tools/vision.py, app/app_utils/telemetry.py) — all fixed via lazy init + try/except guards, symmetrically applied to both peer agents.

**CROSS-MODEL:** Zero overlap between Claude and Codex findings — Claude caught semantics/protocol, Codex caught startup invariants. Both reviewers' fixes shipped.

**UNRESOLVED:** 0 (pending codex-challenge sweep results)

**VERDICT:** CEO + ENG + CODEX REVIEW all CLEARED. Vertex AI Search live. AgentPhone path locked. Ready for D4 (Audio Agent) and forward.
