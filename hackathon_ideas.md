# Hackathon Ideas

## 1. STORYFORGE — Multi-agent Generative Production Studio

**Strategic positioning:** New strategic bullseye.

**What it does:** A multi-agent studio that takes a brief and ships a finished 30-second ad, explainer, or pitch reel. Built for ad agencies, brand teams, and creator studios.

### Agent team
- Script agent (Gemini 3 Pro) — generates script, manages revisions, character development.
- Storyboard agent (Imagen 4 + Nano Banana Pro) — frame-by-frame storyboards, maintains character consistency across all shots (Nano Banana Pro's killer feature).
- Shot agent (Veo 3) — generates each video shot from storyboard + script + style guide.
- Voice agent (Gemini Live + ElevenLabs MCP) — clones voices, ADR, lip-sync.
- Sound design agent — generates ambient sound, foley, music.
- Editor agent — assembles final cut following director-style memory.
- Brand-compliance agent — RAG over brand guidelines, blocks off-brand shots.
- A2A peer: Client revision agent — receives notes ("make the protagonist younger"), propagates to script → storyboard → voice → video.
- A2A peer: Distribution agent — auto-cuts platform-optimized versions for YouTube, TikTok, and Meta.

### Wow demo (90 seconds)
Brief in: "Make a 30-second ad for an electric SUV, target busy moms."

Watch 8 agents collaborate live:
- Script generated.
- Storyboard frames render.
- Veo renders 8 shots.
- Voice cloned.
- Music scored.
- Final assembled.
- Client agent fires note ("make it 5% more emotional").
- Change propagates.
- Re-renders in 30 seconds.

**Time-compression demo:** "What a team of 12 does in 3 weeks, done in 4 minutes."

### Google stack used
Gemini 3 Pro · Gemini 2.5 Flash · Gemini Live · Veo 3 · Imagen 4 · Nano Banana Pro · Vertex AI Search · Vertex AI Memory Bank · BigQuery · Firestore · Cloud Run · A2A · MCP · ElevenLabs MCP · Document AI (brand guidelines) · Speech-to-Text · Cloud Storage · Looker Studio

### Business case
- 500K+ ad agencies.
- 50K+ creator studios.
- Every Fortune 500 spending $50K+/yr on content.
- ACV: $36K-200K.
- TAM: $400B+ ad/content market.
- Forcing function: AI is gutting agency retainers; early adopters win.

### Why it could win
Google's own perspective doc says "video will replace text" and bet heavily on Veo/Imagen. A submission that ships Google's own thesis using their entire generative stack is the platonic ideal of what Google wants to fund.

### Risk
Veo 3 quota or generation latency in a live demo. Mitigation: pre-render some shots and live-generate others.

---

## 2. GUARDIAN — Real-time Anti-Poaching Defense Network

**Positioning:** ConservationOps leveled up.

**What it does:** Live multimodal multi-agent defense system for national parks, conservation organizations, and corporate biodiversity reporting.

### Agent team
- Live video agent (Gemini Live) — analyzes camera-trap streams 24/7.
- Audio agent (Gemini Live + Speech-to-Text) — detects gunshots, vehicles, distress calls.
- Species-ID agent (Gemini 3 Pro Vision) — identifies individual animals (matriarch Echo, lone elephant).
- Pattern agent (BigQuery + Spanner GraphRAG) — cross-references historical poaching, knows entry routes.
- Visualization agent (Imagen) — generates heatmap of risk + suspect sketch from blurry footage.
- Ranger-dispatch agent (AgentPhone for SMS/voice to rangers).
- Court-evidence agent (Document AI) — packages legal evidence for prosecution.
- A2A peer: National park authority agent.
- A2A peer: Corporate sustainability agent (TNFD/CSRD compliance reporting).
- A2A peer: WWF/IUCN funder agent (auto-generates impact reports → unlocks next funding round).

### Wow demo (90 seconds)
Live wildlife camera stream.

Agent narration:
- "Elephant herd of 12, matriarch Echo present, behavior normal."
- Audio agent: "Vehicle engine detected, no permit logged."
- Pattern agent: "Vehicle matches profile from June 2023 poaching incident."
- Visualization agent generates suspect sketch from grainy frame.
- A2A: ranger agent dispatched, ETA 8 min.
- Court-evidence agent packages everything.
- Corporate reporting agent writes an "incident prevented" entry for the corporate sponsor's TNFD report.

### Google stack
Gemini Live · Gemini 3 Pro Vision · Veo (incident reconstruction) · Imagen · Vertex AI Search · GraphRAG on Spanner · BigQuery · Memory Bank (per-animal individual recognition) · Firestore · Pub/Sub · Cloud Run · A2A · MCP · Document AI · Speech-to-Text · AgentPhone

### Business case
- 1,200 conservation organizations.
- 600 national parks.
- Every Fortune 500 needing TNFD/CSRD biodiversity reporting (mandatory in EU from 2025).
- ACV: $50K-300K.
- Additional corporate sponsor revenue.

### Why it could win
Most cinematic demo possible. Real-time multimodal in production. Judges have likely never seen this. Aligns with Google DeepMind's Wildlife.ai ethos.

### Risk
Could feel non-profit or cause-related versus hard B2B. Mitigation: lead with the corporate-sponsor TNFD revenue line, not the conservation story.

---

## 3. PAWPROOF — The Trust Layer for the AI-Generated Pet Industry

**Positioning:** PawConscious-X, leveled up.

**What it does:** A multi-agent network catching AI-generated misinformation about pet products in real time, validating claims with veterinary science, and arbitrating disputes across brands, vets, retailers, and regulators.

### Agent team
- Claim-monitoring agent (Gemini Live + MCP to Amazon/Instagram/TikTok) — live-monitors pet product claims being made.
- Evidence agent (Vertex AI Search over PubMed Vet, FDA CVM, AAFCO standards).
- Veterinary-validation agent (AgentMail) — drafts validation asks to opted-in vet network.
- Visualization agent (Imagen) — generates beautiful trust badges + warning labels.
- Brand-defense agent — for brand customers, generates compliant marketing copy with citations.
- A2A peer: Vet practice agent — vets validate or reject in their dashboard.
- A2A peer: Retailer agent (Amazon/Chewy) — auto-flags unvalidated claims at point of sale.
- A2A peer: FTC complaint agent — drafts and files complaints for clear violations.
- Computer Use agent — literally drives the FTC complaint portal on screen.

### Wow demo (90 seconds)
Live Instagram monitoring.

Claim-monitoring sequence:
- "New brand 'TailWag' just claimed 'cures arthritis in 7 days.'"
- Evidence agent: "Zero supporting studies in PubMed Vet."
- Vet-validation agent drafts 12 vet outreach emails.
- A2A: Amazon retailer agent flags product, hides it from search.
- Computer Use agent opens FTC complaint portal and fills draft.
- Visualization agent generates an "UNVERIFIED CLAIM" trust badge.
- Entire event completes in 2 minutes from claim posted to remediation in flight.

### Google stack
Gemini Live · Gemini 3 Pro · Imagen · Vertex AI Search · GraphRAG on Spanner (brand ↔ claim ↔ evidence ↔ vet) · BigQuery · Memory Bank · Firestore · Cloud Run · A2A · MCP · AgentMail · Computer Use · Document AI

### Business case
- Pet industry: $124B.
- AI-generated content explosion creates a trust crisis.
- Four revenue lines: brands ($24K-60K ACV defense), vets (revenue share), retailers (compliance license), and data sales to regulators.

### Why it could win
Genuinely novel: trust infrastructure for AI-era marketing. Computer Use demo + live monitoring is compelling. Pet content is universal, so judges relate quickly.

### Risk
Less visual wow than STORYFORGE's full generative stack. However, the A2A story is stronger, with 4 distinct peers versus STORYFORGE's 2.
