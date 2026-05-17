# GUARDIAN — Architecture

_System architecture for Track 3 of the Google for Startups AI Agents Challenge. This document is the canonical reference for how the orchestrator, specialists, peers, and ops surface fit together. Last updated 2026-05-17._

---

## One-paragraph summary

GUARDIAN is a multi-agent biodiversity defense platform. An ADK 2.0 root_agent (Gemini 2.5 Pro) coordinates **five specialist sub-agents** (Stream Watcher, Audio Agent, Species ID, Falsifier, Court Evidence) and one **`ParallelAgent` peer fan-out** that calls **four independent A2A v0.3 peer services** running as separate Cloud Run deployments (Park Authority, Sponsor Sustainability, Funder Reporter, Neighbor Park). The system runs on **two of three Track-3-mandated infrastructure surfaces** — Cloud Run for the public traffic + WebSocket firehose, and Vertex AI Agent Engine for the ADK-discoverable surface used by Gemini Enterprise / Marketplace consumers. Every incident produces a SHA-256-anchored chain-of-custody artifact.

---

## Diagram (ASCII)

```
┌──────────────────────────── USER SURFACE ────────────────────────────┐
│                                                                       │
│   Ops Center (Next.js 16, Cloud Run)                                  │
│     • Live Cams tab (NPS public webcam JPEGs, image_url path)         │
│     • Mission Bridge tab (Imagen 4 photo-real portraits, A2A topology)│
│     • Operations tab (Mapbox + 4-peer fan-out animation + firehose)   │
│     • "Built on Google Cloud" panel (O22 column with cost/role/ID)    │
│                                                                       │
└─────────────────────────────────┬─────────────────────────────────────┘
                                  │
                       WebSocket firehose (events.py)
                                  │
                                  ▼
┌───────────────────────── ORCHESTRATOR ────────────────────────────────┐
│                                                                        │
│   ADK 2.0 root_agent (Gemini 2.5 Pro)                                  │
│   ├─ stream_watcher      (Gemini 2.5 Pro, vision)                      │
│   ├─ audio_agent         (Gemini 2.5 Flash, audio classification)      │
│   ├─ species_id          (Gemini 2.5 Pro + Vertex AI Search RAG)       │
│   ├─ falsifier           (Gemini 2.5 Flash, 4-gate adversarial SOP)    │
│   ├─ court_evidence      (SHA-256 chain-of-custody bundler)            │
│   └─ peer_fanout         (ADK 2.0 ParallelAgent)                       │
│        ├─ park_service_caller                                          │
│        ├─ sponsor_sustainability_caller                                │
│        ├─ funder_reporter_caller                                       │
│        └─ neighbor_park_caller                                         │
│                                                                        │
│   Runtime A (public traffic): Cloud Run @ guardian-180171737110...     │
│   Runtime B (ADK-discoverable): Vertex AI Agent Engine                 │
│   Observability: ADK Agent Analytics → BigQuery                        │
│                                                                        │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                A2A v0.3 (ID-token-authed Cloud Run service-to-service)
                                 │
        ┌───────────────┬────────┴────────┬──────────────┐
        ▼               ▼                  ▼              ▼
┌──────────────┐ ┌──────────────────┐ ┌────────────┐ ┌──────────────┐
│Park Service  │ │ Sponsor          │ │ Funder     │ │ Neighbor     │
│              │ │ Sustainability   │ │ Reporter   │ │ Park         │
│ranger        │ │                  │ │            │ │              │
│dispatch +    │ │ TNFD/CSRD-E4     │ │ impact     │ │ cross-border │
│PSR-N ack     │ │ filing + board   │ │ receipt    │ │ CITES-MIKE   │
│              │ │ slide URL        │ │            │ │ mutual aid   │
└──────────────┘ └──────────────────┘ └────────────┘ └──────────────┘
   Cloud Run        Cloud Run            Cloud Run      Cloud Run
   (each is an independent A2A peer agent, each with its own agent.json)
```

---

## Data flow — Spot Now (canonical happy path)

```
producer clicks "Spot Now" in Live Cams tab
        │
        ▼ POST /livecam/spot {image_url: "https://nps.gov/webcams-yell/washburn_ne.jpg"}
        │
   Orchestrator (Cloud Run)
        │
        ├──> fetch JPEG bytes (urllib, 8s timeout, validate JPEG magic)
        ├──> sha256(bytes) for provenance
        ├──> mint_incident_id(GU-...)
        ├──> firehose.emit(incident_event, livecam:spot)
        │
        ├──> Stream Watcher (analyze_image_bytes via Gemini 2.5 Pro vision)
        │       returns species[] + threat_signals[] + behaviors[]
        │
        ├──> Falsifier (review_dispatch, 4 SOP gates)
        │       returns verdict ∈ {concur, dissent, abstain}
        │
        ├──> escalation gate:
        │       requires_escalation = gemini_says_yes
        │                          OR threat_signals nonempty
        │                          OR species in IUCN-hot-list
        │
        └──> if escalation:
                │
                │ ParallelAgent peer_fanout
                │
                ├─[A2A]─> Park Service     (ranger PSR-NNNN dispatched)
                ├─[A2A]─> Sponsor Sustain  (TNFD-2026-XXX filed + board_slide_url)
                ├─[A2A]─> Funder Reporter  (FUND-2026-XXX impact receipt)
                └─[A2A]─> Neighbor Park    (cross-border ACK if material)
                │
                ▼
        court_evidence.bundle_incident(incident_id)
                │
                ▼ returns SHA-256-chained packet (JSON + HTML)
        │
        ▼ HTTP 200 response back to Ops Center
        │
   Ops Center renders inline result overlay on the cam tile:
     • Top species + count + confidence
     • Falsifier verdict (color-coded)
     • 4 peer ack badges with ranger unit, TNFD filing id, etc.
     • Frame SHA proof
```

Sub-7-second wall time end-to-end when peers are warm. ~$0.30 per fully-fanned-out incident.

---

## Infrastructure mandate matrix (Track 3)

| Track 3 mandate | Implementation | Live URL or path |
|---|---|---|
| **Cloud-Native Runtime** (≥1 of Cloud Run / GKE / Agent Engine) | **2 of 3 hit** | Cloud Run + Agent Engine, both live |
| **Vertex-Powered Intelligence** | Gemini 2.5 Pro/Flash + Vertex AI Search | All inference paths |
| **A2A Interoperability** | A2A v0.3 across 4 independent peers, each with its own `agent.json` | `/a2a/app/.well-known/agent-card.json` on every service |
| **B2B Focus** | Fortune 500 sponsors of conservation reserves; F500 CSO is the primary buyer persona | `marketplace/BUYER_PERSONA.md` |

---

## Module map

```
guardian/
├── app/
│   ├── agent.py                  # Cloud Run root_agent — full toolchain
│   ├── agent_engine_root.py      # Slim Agent Engine variant (3.6 KB pickle)
│   ├── fast_api_app.py           # FastAPI + WebSocket firehose
│   ├── events.py                 # Thread-safe event ring buffer (Cloud Run only)
│   ├── agents/
│   │   ├── stream_watcher.py     # Vision sub-agent
│   │   ├── audio_agent.py        # Audio classifier sub-agent
│   │   ├── species_id.py         # RAG-grounded species ID sub-agent
│   │   ├── falsifier.py          # Adversarial reviewer sub-agent
│   │   ├── court_evidence.py     # Chain-of-custody sub-agent
│   │   ├── peer_fanout.py        # ParallelAgent + 4 thin peer callers
│   │   └── incident_pipeline.py  # SequentialAgent scaffold (v5+ factory)
│   └── tools/
│       ├── vision.py             # analyze_image_frame, analyze_image_bytes
│       ├── audio.py              # classify_audio
│       ├── species.py            # identify_species, lookup_species_factsheet
│       ├── falsifier.py          # review_dispatch (4-gate deterministic SOP)
│       ├── court_evidence.py     # bundle_incident + render_evidence_html
│       ├── board_slide.py        # render_board_slide
│       ├── a2a_peers.py          # notify_park_service, ..._sustainability, etc.
│       └── livecam_frame.py      # get_live_frame (yt-dlp+ffmpeg) + get_mp4_frame
│
├── peers/                        # 4 independent A2A peers (one Cloud Run each)
│   ├── park_service/agent.py
│   ├── sponsor_sustainability/agent.py
│   ├── funder_reporter/agent.py
│   └── neighbor_park/agent.py
│
├── ops-center/                   # Next.js 16 frontend
│   └── src/components/
│       ├── LiveCams.tsx          # Multi-source (image_url / mp4_url / youtube_id)
│       ├── MissionBridge.tsx     # Circular topology, photo-real Imagen portraits
│       ├── BuiltOnGoogleCloud.tsx# O22-style product column
│       ├── IncidentPanel.tsx     # Live incident cards
│       ├── EventStream.tsx       # Plain-language firehose ticker
│       └── ReserveMap.tsx        # Mapbox + 4-peer fan-out arrows
│
├── deployment/agent_engine.py    # Vertex AI Agent Engine deploy/list/describe
├── marketplace/                  # LISTING + PROCUREMENT + DEVPOST + policies
├── docs/AGENT_ENGINE.md          # Track 3 deployment rationale + debug lessons
├── tests/eval/                   # ADK Eval framework (5 evalsets, LLM-as-judge)
└── tools/o22-render/             # Vendored video-render pipeline (rev13)
```

---

## Cross-runtime state model

The Cloud Run orchestrator and the Agent Engine orchestrator share the SAME `root_agent` identity at the spec level (sub-agents, instruction, model). They differ in what tools and side-effects they carry:

| Aspect | Cloud Run (`app.agent`) | Agent Engine (`app.agent_engine_root`) |
|---|---|---|
| Tools | full toolchain (15+ tools including livecam_frame, court_evidence, a2a_peers, etc.) | none (questions-about-GUARDIAN only) |
| Sub-agents | 5 specialists + peer_fanout (with 4 callers) | none |
| Firehose | yes (events.py with threading.Lock) | no |
| BigQuery analytics plugin | yes | no |
| Subprocess deps (yt-dlp, ffmpeg) | yes | no |
| Pickle size | ~irrelevant (Cloud Run uses source not pickle) | 3.6 KB |
| Purpose | live demo + agentic chain | ADK-discoverable Marketplace surface |

This split is deliberate: Agent Engine's managed container can't tolerate `threading.Lock` in a cloudpickle, can't reach `ffmpeg`, and doesn't need our Cloud-Run-only side effects. Live demo runs on Cloud Run; Agent Engine is the discovery layer.

---

## Observability

Every tool call emits a structured event via `app/events.py`:

```python
events.emit(
    kind="tool_end",
    agent="falsifier",
    tool="review_dispatch",
    incident_id="GU-...",
    severity="critical",
    payload={"verdict": "dissent", "severity_0_5": 4, ...},
    latency_ms=1234,
)
```

These events flow to:

1. **WebSocket firehose** — Ops Center renders the live ticker + incident panel + Mission Bridge active-line pulses
2. **BigQuery** — `adk_agent_analytics` dataset via `BigQueryAgentAnalyticsPlugin`, retained 90 days default / 365 / 7yr (audit tier)
3. **Cloud Logging** — structured JSON entries for incident response

---

## Security boundary

- All Cloud Run services deployed with `--no-allow-unauthenticated` (except the public orchestrator and ops-center which are intentionally public for the live demo)
- Service-to-service A2A calls use Google ID tokens (OIDC, short-lived, IAM-bound)
- Frontend authentication: Firebase Auth + Google Workspace SSO
- All inputs validated at API boundary (Pydantic models on FastAPI endpoints)
- Subprocess invocations (yt-dlp, ffmpeg) use list-args with strict regex validation on youtube_id and URL allowlist on mp4_url / image_url
- See [`marketplace/PROCUREMENT.md`](./marketplace/PROCUREMENT.md) §2 for the full security control matrix

---

## Evaluation

ADK Eval framework runs against 5 evalsets covering core agentic trajectories:

| Evalset | Trajectories | What it tests |
|---|---|---|
| `basic.evalset.json` | 2 | orchestrator routing + first-tool-call correctness |
| `stream_watcher.evalset.json` | 2 | vision → escalation gate |
| `falsifier.evalset.json` | 3 | concur / dissent / abstain across SOP gates |
| `peer_fanout.evalset.json` | 1 | ParallelAgent topology firing |
| `user_simulation.evalset.json` | 2 | multi-turn sustainability_analyst + field_ranger personas |

LLM-as-judge: `gemini-3-flash-preview`, threshold 0.8 on relevance + helpfulness rubrics. Nightly GitHub Action at `.github/workflows/adk-eval.yml`. Local invocation: `make eval`.

---

## Codex handshake history

GUARDIAN treats `codex exec --model gpt-5-codex` as a §4.5 quality gate. Every commit triggers a codex adversarial review with BLOCK / WARN / NIT / OK verdicts. The v4-v8 arc has cleared **19+ handshake rounds**, with findings absorbed before each next-Move proceeds.

See `reviews/CODEX_*.md` for the per-Move handshake artifacts.

---

## Pricing model (compressed)

| SKU | Annual | Includes |
|---|---:|---|
| Core | $60K | 1 reserve, 10K incidents/year, all 4 A2A peers |
| Portfolio | $180K | 5 reserves, 50K incidents/year, dedicated TAM |
| Enterprise | from $300K | unlimited reserves + SOC 2 evidence + custom A2A onboarding |

Full rate card + procurement terms: [`marketplace/PROCUREMENT.md`](./marketplace/PROCUREMENT.md).

---

_Architecture diagrams + deeper module documentation will continue to evolve through v9. For the canonical source of truth on what's live today, refer to the live URLs in [`README.md`](./README.md) and the deployed revisions table._
