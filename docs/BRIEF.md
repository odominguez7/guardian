# Google for Startups AI Agents Challenge — Brief

_Generated 2026-05-14 from Devpost pages + Google's official "Startup technical guide: AI agents" (60-page playbook) + adk.dev + adk.dev/integrations._

## Hackathon at a glance
- **Organizer:** Google Cloud + Google DeepMind
- **Registrations:** 536 people / 401 idea pages already created — crowded field
- **Submission deadline:** 2026-06-05, 5:00 PM PT (22 days from today)
- **Judging window:** Jun 11 → Jun 18 · Winners announced Jun 22, 5:00 PM EDT
- **Eligibility:** Startups · $500 GCP credits for every eligible team

## Prize pool — $97,500 total ($60K cash + $37.5K credits)
| Award | Cash | Credits | Extras |
|---|---|---|---|
| Grand Prize (×1) | $15,000 | $10,000 | Addy Osmani coffee + Bay Area VIP + Google social |
| Track winner (×3) | $10,000 | $7,500 | Coffee + Bay Area VIP + social |
| Regional winner APAC/EMEA (×2) | $5,000 | $2,500 | Coffee + social |

## The three tracks
1. **Build (net-new agents)** — Blank canvas → autonomous agent on ADK (or LangChain/CrewAI). MCP for external tool access. "From static code to declarative intent."
2. **Optimize (existing agents)** — Bring a working agent, stress-test it. Use **Agent Simulation** (synthetic edge-case events), **Agent Observability** (trace stalled reasoning), **Agent Optimizer** (programmatic refinement of system instructions). Production-grade reliability.
3. **Refactor for Marketplace + Gemini Enterprise** — Hardest, most lucrative for B2B startups. Mandates:
   - B2B core function
   - Cloud-native runtime: Cloud Run or GKE
   - Gemini (or any LLM exclusively via Agent Platform)
   - **A2A protocol** for inter-agent communication
   - Prepped for Google Cloud Marketplace listing

## Mandatory tech (any track)
- **Intelligence:** Gemini API (or other LLM only via Agent Platform)
- **Orchestration:** ADK (or LangChain/CrewAI managed on Agent Platform)
- **Infrastructure:** Cloud Run or GKE on GCP

## Judging rubric
- Technical Implementation — **30%**
- Business Case — **30%**
- Innovation & Creativity — **20%**
- Demo & Presentation — **20%**

## Required submission artifacts
1. Code repo
2. Video walkthrough
3. Architecture diagram
4. Working demo with login (if private)

## What Google explicitly wants to see (from "Key Considerations")
- **Multi-agent system** with ADK-based orchestration (sequential / parallel / loop / custom)
- Deployment on **Vertex AI Agent Engine**
- Strong grounding via **Vertex AI Search**, Google Search, Google Maps, private RAG
- A2A so agents from different teams can discover + collaborate
- "Collaboration between agents > single agent could achieve"

## Canonical example Google ships (Smart Facility Energy Agent)
A multi-agent system: Energy Agent (ADK) ← MCP → HVAC IoT + weather API + grid prices; A2A peering with the company's HR Agent to anticipate occupancy spikes during all-hands. Pre-cools building during off-peak hours. Track 1 builds it, Track 2 hardens it against rare conflicts (extreme weather + peak pricing), Track 3 refactors to GKE + A2A + Marketplace-ready.

Other examples Google calls out:
- Automated Talent Sourcing (resume screen + tailored interview Qs)
- IT Incident Resolution (alert triage + RAG on ticket history + diagnostics)
- Dynamic Supply Chain Predictor (weather × inventory × proactive client alerts)

## The Google Cloud agent stack (full toolkit available)
- **Models:** Gemini 3 Pro (reasoning), 2.5 Flash (balanced), 2.5 Flash-Lite (cheap+fast); Gemma; 200+ models in Vertex AI Model Garden
- **Orchestration:** ADK (Python primary; also TS/Go/Java). Agent types: LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, CustomAgent
- **Protocols:** MCP (tool discovery), A2A (agent-to-agent collaboration)
- **Runtime:** Vertex AI Agent Engine (managed), Cloud Run (serverless), GKE (granular control)
- **Knowledge layer:**
  - Vertex AI Search / RAG Engine (managed RAG, GraphRAG support)
  - Vertex AI Vector Search (vector DB)
  - Vertex AI Memory Bank (auto-distilled long-term memory, GenerateMemories)
  - Firestore (state, sessions), Cloud Storage (raw), BigQuery (analytics), Memorystore (cache), Cloud SQL (audit), Cloud Spanner (global)
- **AgentOps stack:** Agent Starter Pack (`uvx agent-starter-pack create ... -a adk@gemini-fullstack`) — Terraform, Cloud Build CI/CD, Cloud Trace, Cloud Logging, Vertex AI eval, Looker Studio dashboards, OpenTelemetry
- **Built-in ADK tools:** Google Search, Code Exec, BigQuery, Spanner, Bigtable, Pub/Sub, Cloud Trace, Knowledge Engine, GKE Code Executor, Agent Identity, Agent Registry
- **Frontend:** Firebase Studio for full-stack app prototyping; A2UI / AG-UI for streaming chat UIs
- **Pre-built agents:** Agent Garden (deploy pre-built ADK agents) — composable

## Where competition will cluster (avoid these)
The 401 visible idea titles already include: SmartDev Agent, RecruitAgent, ProcuForge, AutoIntern, FinanceAgent, BookingAgent, EduAgents, CalorieTracker, CustomerService, RealtyOpsOS, CompanyLens, ZovackWhatsApp. The shallow lanes (recruiter agents, customer support agents, generic finance agents, calendar bots) will be saturated. **Differentiation will come from depth-of-domain, complexity of orchestration, and the realness of the workflow being automated.**

## My competitive read (taste, not yet a plan)
- **Track 3 is the right target.** Hardest mandates, smaller field, most cash, opens Marketplace distribution after the event.
- **B2B + vertical depth wins.** "Yet another HR agent" loses to a multi-agent system that automates a workflow only an insider would even think to model.
- **A2A demo is the trump card.** Most teams will hand-wave A2A; build it for real with ≥2 agents peering across a clear trust boundary.
- **Production-grade is a differentiator.** Most demos won't run AgentOps. Ship with: golden trajectory tests, Cloud Trace dashboards, eval set in BigQuery, IaC, CI/CD via Agent Starter Pack. That alone moves Technical Implementation from 22/30 to 28/30.
- **A real B2B paying customer story moves Business Case from 22 to 28.** Need a workflow with verifiable economics (hours saved × loaded labor rate, or revenue unlocked).
