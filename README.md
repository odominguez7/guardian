# GUARDIAN

Real-time multi-agent system for biodiversity protection and corporate ESG (TNFD/CSRD) reporting. Built for the **Google for Startups AI Agents Challenge** (Track 3 — Refactor for Marketplace + Gemini Enterprise).

**Submission deadline:** 2026-06-05.

---

## What it does

A team of specialized AI agents watches conservation areas in real time, detects poaching threats before they happen, coordinates ranger response across agencies, and auto-files the TNFD/CSRD biodiversity reports Fortune 500 sustainability buyers are now legally required to deliver.

Six in-system agents (Stream Watcher, Audio, Species ID, Pattern, Visualizer, Dispatch, Court-Evidence) + an Orchestrator + **4 distinct A2A peer agents** representing the park authority, a corporate sustainability buyer, a funder reporting agent, and a neighboring park's mutual-aid agent.

## Stack

- **Intelligence:** Gemini 3 Pro (orchestrator) · Gemini 2.5 Flash (sub-agents) · Gemini Live (real-time video + audio)
- **Orchestration:** Agent Development Kit (ADK) · Model Context Protocol (MCP) · Agent-to-Agent (A2A) protocol
- **Knowledge:** Vertex AI Search · Vertex AI Vector Search · Vertex AI Memory Bank · Spanner GraphRAG · BigQuery
- **Vision/Media:** Imagen 4 · Nano Banana Pro · Document AI · Speech-to-Text
- **Runtime:** Cloud Run · Firebase Auth · Pub/Sub · Memorystore · Cloud Storage
- **AgentOps:** Agent Starter Pack · Terraform · Cloud Build CI/CD · Cloud Trace · Vertex AI eval · Looker Studio dashboards · Cloud Logging → BigQuery

## Track 3 mandate checklist

| Mandate | Implementation |
|---|---|
| B2B core function | Fortune 500 TNFD/CSRD compliance buyers · conservation orgs · insurance underwriters |
| Cloud-native runtime | 5+ Cloud Run services, Terraform IaC |
| Google Cloud powered intelligence | Gemini 3 Pro orchestrator + 2.5 Flash sub-agents |
| **A2A interoperability** | 4 distinct enterprise agents in separate Cloud Run services, each with `agent.json` + mTLS |
| Marketplace-ready | Marketplace listing draft + pricing page + SOC 2 readiness checklist included |

## Repo layout (in progress)

```
guardian/
  agents/             # ADK agent code, one folder per service
    orchestrator/
    stream_watcher/
    audio/
    species_id/
    pattern/
    visualizer/
    dispatch/
    court_evidence/
  peers/              # A2A peer agents (independent services)
    park_authority/
    corporate_sustainability/
    funder_reporter/
    neighbor_mutual_aid/
  infra/              # Terraform modules
  eval/               # Golden trajectories, eval set
  marketplace/        # Listing draft, pricing, SOC 2 readiness
  docs/               # Architecture, BRIEF, PLAN
  web/                # Frontend (Firebase Auth + AG-UI)
```

## Build status

See [`PLAN.md`](./PLAN.md) for the locked 22-day execution schedule.

## License

MIT. See [LICENSE](./LICENSE).
