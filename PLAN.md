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
  │ Agent   │  │ Agent    │  │ (WWF/IUCN │  │ Mutual   │
  │(Run #2) │  │(Run #3 — │  │  style)   │  │  Aid     │
  │         │  │ TNFD/CSRD│  │ (Run #4)  │  │(Run #5)  │
  │         │  │  report) │  │           │  │          │
  └─────────┘  └──────────┘  └───────────┘  └──────────┘

  Each peer = independent Cloud Run service · own agent.json · own SA
  Each accepts/responds to A2A task requests · mutual mTLS
```

### Why each agent exists

| Agent | Job | Model | Distinguishing tool |
|---|---|---|---|
| **Orchestrator** | Routes signals to specialists, manages task state, exposes A2A interface to all 4 peers | Gemini 3 Pro | A2A SDK · ADK LlmAgent |
| **Stream Watcher** | 24/7 watches camera feeds (in prod) / processes recorded clips (in demo) | Gemini Live (video) | Gemini Live API |
| **Audio Agent** | Listens for gunshots, vehicles, distress, human voices | Gemini Live (audio) + Speech-to-Text | Audio classification |
| **Species ID** | Identifies species + individual animals (matriarch Echo) from frames | Gemini 3 Pro Vision | Vertex AI Vector Search over species embeddings |
| **Pattern Agent** | Cross-references with historical poaching, identifies entry routes, predicts next strike | Gemini 2.5 Flash | Spanner GraphRAG · BigQuery |
| **Visualizer** | Generates suspect sketch from low-res frames; renders heatmaps | Imagen 4 + Nano Banana Pro | Imagen API |
| **Dispatch** | Notifies rangers via SMS/voice/radio | Gemini 2.5 Flash | AgentPhone MCP |
| **Court-Evidence** | Packages signals into chain-of-custody evidence bundle | Gemini 2.5 Flash | Document AI |

### The 4 A2A peers — and why this is Track 3's strongest A2A story

| Peer | What it is | Why A2A (not API) |
|---|---|---|
| **Park Authority Agent** | Independent agent run by the park (mocked from us, but separate Cloud Run service with its own agent.json) | Different org, different trust boundary, different schedule of operations |
| **Corporate Sustainability Agent** | Agent run by a Fortune 500 sponsor needing TNFD/CSRD report data | Sponsor + park need bidirectional reporting without sharing DBs |
| **Funder Reporter Agent** | Style of WWF/IUCN, but operated by the funder | Funder wants periodic impact reports without raw access to park data |
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
| Google Cloud Powered Intelligence | Gemini 3 Pro orchestrator (env-driven, see below) + 2.5 Flash sub-agents + Gemini Live | `ORCHESTRATOR_MODEL` env var, default `gemini-2.5-pro` until 3 Pro lands on Vertex for this project |
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

| Day | Date | Milestone | Concrete deliverable |
|---|---|---|---|
| **D1** | 2026-05-15 | Repo + GCP project + auth verified + GFS Cloud Program applied + Agent Starter Pack scaffold cleanly applied | github.com/odominguez7/guardian + GCP project `guardian-xxx` + Terraform applies |
| D2 | 05-16 | Hello-Agent on Cloud Run with `agent.json` + Vertex AI Search index seeded (IUCN, CITES, Snapshot Serengeti) | Live HTTPS URL |
| D3 | 05-17 | Stream Watcher agent processes 1 sample clip → emits structured event | Sample clip detected |
| D4 | 05-18 | Audio agent detects gunshot/vehicle in sample audio | Audio classified |
| D5 | 05-19 | Species ID agent identifies 5 individual animals from frames | Echo recognized |
| D6 | 05-20 | Pattern agent online with BigQuery historical data + initial Spanner schema | Cross-reference works |
| D7 | 05-21 | Visualizer agent generates suspect sketch from blurry frame + heatmap | Imagen output visible |
| D8 | 05-22 | Dispatch agent sends SMS to a test phone | Real SMS arrives |
| D9 | 05-23 | Court-Evidence agent packages a sample incident → PDF | PDF generated |
| D10 | 05-24 | Spanner GraphRAG live; Pattern agent uses it | Graph queries work |
| D11 | 05-25 | **A2A Peer #1**: Park Authority agent (Cloud Run #2) + handshake works | A2A handshake on video |
| D12 | 05-26 | **A2A Peer #2**: Corporate Sustainability agent (auto-files TNFD entry) | TNFD JSON output |
| D13 | 05-27 | **A2A Peer #3**: Funder Reporter agent (sends impact report) | Sample report |
| D14 | 05-28 | **A2A Peer #4**: Neighboring Park Mutual-Aid agent | Cross-border handoff |
| D15 | 05-29 | Frontend Cloud Run app w/ Firebase Auth + AG-UI streaming map + live feed | Demo UI live |
| D16 | 05-30 | Memory Bank wired (per-park, per-animal); Vertex AI eval green. **Trajectory tests already at ~30 from continuous 2/agent ramp.** | Eval green on PR |
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
| 2:45-3:00 | The ask | "Built on Gemini 3 Pro, ADK, A2A, and Cloud Run. Live at guardian.{domain}.com. Source: github.com/odominguez7/guardian." |

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
| CEO Review | `/plan-ceo-review` | Scope & strategy | 2 | CLEAR (SELECTIVE EXPANSION — D1 execution review 2026-05-15) | 7 cherry-picks accepted, 2 code-vs-plan mismatches caught (Gemini 3 Pro upgrade, F500-first storyboard) |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 0 | — | run after D6 (Pattern Agent scaffold) |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | optional, run D15 with frontend |
| Codex Review | `/codex review` | Independent 2nd opinion | 0 | — | run D21 pre-submission |
| Outside Voice | — | Cross-model challenge | 0 | — | run D21 pre-submission |

**UNRESOLVED:** 0
**VERDICT:** GUARDIAN locked. D1 execution proceeds with 7 accepted upgrades. Next: upgrade orchestrator to Gemini 3 Pro, backfill 2 Stream Watcher trajectory tests, redeploy.
