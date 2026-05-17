# GUARDIAN

Real-time multi-agent system for biodiversity protection and corporate ESG reporting under the Taskforce on Nature-related Financial Disclosures (TNFD) and Corporate Sustainability Reporting Directive (CSRD). Built for the **Google for Startups AI Agents Challenge** — Track 3 (Refactor for Marketplace + Gemini Enterprise).

**Submission deadline:** 2026-06-05 · **Status as of 2026-05-16:** core platform LIVE, demo video remains.

---

## What it does

A team of specialized AI agents watches conservation areas in real time, detects poaching threats before they happen, coordinates ranger response across agencies, and auto-files the TNFD/CSRD biodiversity reports Fortune 500 sustainability buyers are now legally required to deliver.

**6 in-system agents** (Orchestrator, Stream Watcher, Audio, Species ID, Court-Evidence, + Pattern WIP) · **4 distinct A2A peers** (Park Authority, Sponsor Sustainability, Funder Reporter, Neighbor Park) · **Cinema-grade Ops Center** judges can click + screen-record.

## Live endpoints

| Service | URL | Revision |
|---|---|---|
| GUARDIAN orchestrator | https://guardian-180171737110.us-central1.run.app | `guardian-00022-rs8` |
| Ops Center (frontend) | https://guardian-ops-center-180171737110.us-central1.run.app | `guardian-ops-center-00012-rd9` |
| A2A peer — Park Authority | https://guardian-park-service-180171737110.us-central1.run.app | `guardian-park-service-00004-2sk` |
| A2A peer — Sponsor Sustainability (TNFD) | https://guardian-sponsor-sustainability-180171737110.us-central1.run.app | `guardian-sponsor-sustainability-00004-729` |
| A2A peer — Funder Reporter | live on Cloud Run | live |
| A2A peer — Neighbor Park (Maasai Mara) | live on Cloud Run | live |

**A2A agent card:** `/a2a/app/.well-known/agent-card.json` · **API docs:** `/docs` · **Court-evidence packet:** `/demo/evidence/{id}` · **Evidence HTML:** `/demo/evidence/{id}/html` · **Board-ready slide (F500 CSO Q2 deck artifact):** `/board-slide/{filing_id}` · **Vendored html2canvas:** `/static/html2canvas.min.js`

**Reproducibility check:** `python3 scripts/dev/verify_ids.py --runs 5` → all 5 ID families (incident_id, ranger_unit, filing_id, funder_receipt_id, neighbor_handoff_id) deterministic across N back-to-back calls. Every on-screen ID in the demo video can be re-derived live by anyone with `gcloud auth print-identity-token`.

## Build status — 22-day plan

12 of 22 plan-days shipped in 1.3 calendar days (2026-05-15 → 2026-05-16). 4 codex adversarial sweeps cleared inline that session; an additional 5 per-Move codex handshakes cleared on 2026-05-17 during the v3 execution pass (see `reviews/CODEX_MOVE_*.md`).

### v3 execution pass (2026-05-17) — see `PLAN_V3.md` for full plan

| Move | What shipped | Status |
|---|---|---|
| **0** | Live-site truth: Mapbox token + Firebase config baked into Ops Center; **Auto-Cycle Demo Mode** (judges land, 10s idle → scenarios auto-rotate). Makefile env-source hardening. | ✅ CLEAR |
| **1** | **Falsifier adversarial agent**: 4-gate deterministic SOP engine (audio-conf × severity, species-flag materiality ceiling, observation freshness, hot threat_signal) returns `concur` / `dissent` / `abstain`. Verdict logged in Court-Evidence bundle + Sponsor TNFD filing (`adversarial_review_passed: bool`). DISSENT chip on Ops Center IncidentPanel. 15 unit + integration tests. | ✅ CLEAR |
| **2** | **GCP suite taste pass**: Lyria 2 ambient bed (30s) + Imagen 4 cinematic portraits (10 agents) + Veo 3.1 Fast hero loop (6s African elephant dusk). All wired into Ops Center. ~$1.10 spend. | ✅ CLEAR |
| **3** | **Board-ready slide auto-export** (Maya CSO's #1 ask): Sponsor TNFD filing returns `board_slide_url` → live HTML page at `/board-slide/{filing_id}` with KPI tiles + SHA-256 audit hash + client-side "Download as PNG" via vendored html2canvas. LRU render cache survives buffer eviction. | ✅ CLEAR |
| **4** | **Final video v2.1 cut**: Lyria 2 music bed mixed under VO at -22 dBFS + bottom-left telemetric HUD overlay (real Cloud Trace numbers). SRT sidecar captions for accessibility. 179.9s / 45 MB. | ✅ CLEAR |
| **5** | Stranger lean-in test + final codex sweep + Devpost submit | ⏳ in progress |

### Original 22-day schedule

| Day | Milestone | Status | Evidence |
|---|---|---|---|
| **D1** | Repo + GCP + Cloud Run scaffold | ✅ SHIPPED | `guardian-gfs-2026`, github.com/odominguez7/guardian |
| **D2** | Vertex AI Search corpus seeded | ✅ SHIPPED | `guardian-collection`, 7-doc wildlife corpus |
| **D3** | Stream Watcher agent | ✅ SHIPPED | 2 ADK eval trajectories, live in playground |
| **D4** | Audio Agent (gunshot/vehicle classifier) | ✅ SHIPPED | `classify_audio`, Gemini multimodal, 6 sound classes |
| **D5** | Species ID Agent (two-tool agentic RAG) | ✅ SHIPPED | `identify_species` + `lookup_species_factsheet` over corpus |
| D6 | Pattern Agent + Memory Bank | ⏳ TODO | downscoped to BigQuery-only (no Spanner) |
| D7 | Visualizer (suspect sketch + heatmap) | ✂️ CUT | pre-render placeholder in demo video |
| D8 | Dispatch Agent (SMS) | 🟨 STUB | AgentPhone MCP hook documented, mock ack returned |
| **D9** | Court-Evidence Agent | ✅ SHIPPED | Secure Hash Algorithm 256-bit (SHA-256) anchored chain-of-custody bundle + `/html` endpoint |
| D10 | Spanner GraphRAG | ✂️ CUT | CEO-review downscope, saved $86 + 1 day |
| **D11** | A2A Peer #1 — Park Authority | ✅ SHIPPED | independent Cloud Run, live ranger dispatch ack |
| **D12** | A2A Peer #2 — Sponsor Sustainability | ✅ SHIPPED | TNFD / Corporate Sustainability Reporting Directive — European Sustainability Reporting Standard E4: Biodiversity and Ecosystems (CSRD-ESRS-E4) filer (Pro for tool-call reliability) |
| **D13** | A2A Peer #3 — Funder Reporter | ✅ SHIPPED | impact receipt issuer |
| **D14** | A2A Peer #4 — Neighbor Park | ✅ SHIPPED | cross-border Convention on International Trade in Endangered Species (CITES) / Monitoring the Illegal Killing of Elephants (MIKE) handoff (Maasai Mara) |
| **D15** | Frontend Ops Center | ✅ SHIPPED (-14d) | Next.js 16 + Mapbox + WS firehose + animated 4-peer fan-out |
| D16 | ParallelAgent refactor | ⏳ TODO | cut chain latency ~90s → ~30-40s |
| D17 | Looker dashboard + security pass | ⏳ TODO | mTLS, RLS |
| **D18** | Marketplace listing package | ✅ SHIPPED | 8 files, codex-cleared, Producer Portal evidence |
| D19-D21 | Demo video + arch diagram + reviews | ⏳ TODO | **highest-leverage remaining work** |
| D22 | Devpost submit | ⏳ TODO | 2026-06-05 5pm PT |

**Codex adversarial sweeps cleared in session:** 4 — Tier 1 hardening, service-to-service auth, Marketplace listing fact-check, D9 court-evidence. Each found 1+ P0 and several P1; all auto-applied or manually fixed.

## Stack

- **Intelligence:** Gemini 3 Pro (orchestrator, legal output) · Gemini 2.5 Flash (sub-agents) · Gemini Live (real-time video + audio)
- **Orchestration:** Agent Development Kit (ADK) · Model Context Protocol (MCP) · Agent-to-Agent (A2A) protocol v0.3.0
- **Knowledge:** Vertex AI Search · BigQuery (Spanner downscoped) · planned Memory Bank (D6)
- **Vision/Media:** Imagen 4 (cut from runtime) · Document AI · Speech-to-Text
- **Runtime:** 6 Cloud Run services · Firebase Auth · Pub/Sub · Cloud Storage
- **AgentOps:** Agent Starter Pack v0.41.3 (`adk_a2a` template) · Cloud Build CI/CD · Cloud Trace · Looker Studio (D17) · Cloud Logging → BigQuery

## Track 3 mandate checklist

| Mandate | Implementation | Status |
|---|---|---|
| B2B core function | F500 TNFD/CSRD compliance buyers · conservation orgs · insurance underwriters | ✅ |
| Cloud-native runtime | 6 Cloud Run services | ✅ |
| Google Cloud powered intelligence | Gemini 3 Pro orchestrator + 2.5 Flash sub-agents + Vertex AI Search | ✅ |
| **A2A interoperability** | 4 distinct enterprise peers in separate Cloud Run services, each with `agent.json` + service-to-service ID token auth | ✅ |
| Marketplace-ready | Listing package + pricing + producer-portal submission evidence | ✅ |

## Repo layout

```
guardian/
  app/                # Orchestrator + in-system agents (ADK)
  peers/              # 4 A2A peer agents (independent Cloud Run services)
  ops-center/         # Next.js 16 + Mapbox + WS firehose frontend
  marketplace/        # Listing package, pricing, SOC 2 readiness, submission evidence
  deployment/         # Terraform + Cloud Build
  reviews/            # CEO + eng + design + codex review artifacts
  tests/              # ADK eval trajectories + integration
  PLAN.md             # 22-day locked execution schedule
  TODOS.md            # 30+ deferred P2/P3 items
```

## Local dev

```bash
# install deps
uv sync

# run orchestrator locally
make dev

# re-deploy services
make deploy                          # orchestrator
make deploy-park-service             # Park Authority peer
make deploy-sponsor-sustainability   # Sponsor Sustainability peer
```

See `Makefile` for full target list.

## License

MIT. See [LICENSE](./LICENSE).
