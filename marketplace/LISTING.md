# GUARDIAN - Google Cloud Marketplace Listing (draft)

_Track 3 deliverable. Submission target 2026-06-01 (D18). Listing copy
mirrors the Google Cloud Marketplace producer portal field structure._

---

## Product name

**GUARDIAN - Biodiversity Operations Platform for Enterprise**

Marketing tagline: *Real-time anti-poaching defense + auto-filed Taskforce on Nature-related Financial Disclosures (TNFD) and Corporate Sustainability Reporting Directive (CSRD) biodiversity disclosures, on one Gemini-native multi-agent platform.*

---

## Listing summary (max 130 chars)

Multi-agent biodiversity defense + auto-filed disclosure under the Taskforce on Nature-related Financial Disclosures (TNFD) and the Corporate Sustainability Reporting Directive (CSRD), for Fortune 500 sponsors of protected conservation areas.

---

## Solution overview (200–400 words)

Fortune 500 firms with sponsored conservation portfolios now face Corporate Sustainability Reporting Directive (CSRD) disclosure requirements under European Sustainability Reporting Standard E4: Biodiversity and Ecosystems (ESRS E4) when in scope, alongside rising Taskforce on Nature-related Financial Disclosures (TNFD) expectations. The data required - incident-level evidence that material biodiversity impacts in your sponsored reserves have been detected, dispatched, and chain-of-custody preserved - has historically been impossible to produce at audit grade.

GUARDIAN is a Gemini-native multi-agent platform that runs in production on the conservation areas your firm sponsors. Stream Watcher, Audio Agent, and Species ID specialists analyze camera-trap and microphone feeds in real time, escalate poaching threats to the Orchestrator, and trigger A2A protocol fan-out to four independent enterprise agents:

1. **Park Authority Agent** - dispatches the on-call ranger unit at the host park.
2. **Sponsor Sustainability Agent** - files a TNFD-aligned, CSRD-ESRS-E4 compliant biodiversity-impact entry directly into the sponsor's disclosure dashboard.
3. **Funder Reporter Agent** - issues a program-tagged impact receipt for the conservation funder's quarterly impact report.
4. **Neighbor Park Mutual-Aid Agent** - accepts a cross-border Convention on International Trade in Endangered Species — Monitoring the Illegal Killing of Elephants (CITES-MIKE) handoff when the incident may cross a trans-frontier conservation area.

Every incident produces a deterministic, chain-of-custody-grade evidence bundle. The same artifact serves the ranger response, the sponsor's regulator, the funder's quarterly impact report, and (when needed) the host country's wildlife court system.

Built on Vertex AI (Gemini 2.5 Pro orchestrator, Gemini multimodal specialists), Vertex AI Search (IUCN Red List + CITES + reserve playbook RAG), Cloud Run (orchestrator + 4 independent peer services), A2A protocol v0.3.0 for enterprise-agent interop, and BigQuery agent analytics for AgentOps observability.

---

## Key benefits (6 bullets)

- **TNFD-aligned + CSRD-ESRS-E4-compatible disclosure outputs.** Every biodiversity-relevant incident on a sponsored reserve auto-emits a structured disclosure entry tagged with `compliance_frameworks: ["TNFD","CSRD-ESRS-E4"]` and the same `incident_id` used by ranger response - a chain-of-custody trail your external auditor's testing procedures can validate.
- **Multi-agent coordination across organizations.** Four independent enterprise agents (park authority, sponsor sustainability office, conservation funder, neighbor park) coordinate live over the A2A protocol. No shared databases, no proprietary APIs, no human glue.
- **Adversarial agent audit mode (Falsifier).** Every proposed dispatch is reviewed by an internal-audit adversarial agent before action — verdict (concur / dissent / abstain) plus per-gate diagnostics ship in the Court-Evidence bundle AND the Sponsor TNFD filing as `adversarial_review_passed: bool`. Big Four (Deloitte, PwC, EY, KPMG) audit teams get the dissent record on every disclosure, which is the chain-of-custody requirement no spreadsheet workflow can match.
- **Board-ready slide auto-export.** Every Sponsor TNFD filing emits a 16:9 board-deck-ready HTML page with KPI tiles, audit hash, and a one-click "Download as PNG" — drag-and-drop into the CSO's quarterly board pack. The artifact every F500 Chief Sustainability Officer is three weeks late on, generated automatically per incident.
- **End-to-end fan-out in seconds.** Measured median end-to-end latency for a 4-peer fan-out on `guardian-00022-rs8`: 3-8 seconds when peers are warm; 18-26 seconds on cold start (Vertex AI Gemini Pro spin-up). Parallel fan-out, retry-on-flake hardening, cold-start safe.
- **Native to your existing Google Cloud commit.** Deploys to Cloud Run + Vertex AI + BigQuery in your existing GCP project. Draws against your committed-spend agreement. No new procurement.

---

## How GUARDIAN fits with existing tools

GUARDIAN does NOT replace the biodiversity-data, ranger-operations, or carbon-disclosure platforms your organization already runs. It is the **multi-organization coordination + per-incident audit-grade evidence layer** that those tools were not built to produce.

| You already run... | GUARDIAN's role |
|---|---|
| **IBAT** (IUCN / UNEP-WCMC / BirdLife International / Conservation International — Integrated Biodiversity Assessment Tool) | GUARDIAN treats IBAT as the authoritative species-and-site data source. The Species ID specialist's IUCN Red List grounding aligns with IBAT's data lineage. We coordinate; we do not re-derive. |
| **SMART** / **EarthRanger** (merging into **SERCA**, the SMART–EarthRanger Conservation Alliance, announced Oct 2025) | GUARDIAN's Park Authority Agent A2A peer can register against your existing SMART, EarthRanger, or post-merger SERCA instance. Your rangers keep their tool. GUARDIAN handles the cross-organization fan-out (sponsor + funder + neighbor park) that those field-ops tools intentionally do not. |
| **Sweep** / **Asuene** / your CSRD reporting suite | GUARDIAN's Sponsor Sustainability Agent files structured TNFD/CSRD-ESRS-E4 entries with a `compliance_frameworks` tag. Drops into your reporting suite's ingest endpoint. Your suite remains the disclosure system of record; GUARDIAN supplies incident-grade upstream evidence. |
| **Your CFO's carbon disclosure module** | GUARDIAN is purpose-built for E4 (biodiversity/ecosystems) — the disclosure dimension the carbon module is structurally not designed to produce. |

**The architectural insight worth pricing:** none of the above natively models the **sponsor ↔ park ↔ funder ↔ neighbor-park** four-way relationship that Fortune 500 conservation sponsorships actually have. GUARDIAN is the A2A-protocol coordination layer that connects them, with the per-incident chain-of-custody artifact that maps to your Big Four (Deloitte, PwC, EY, KPMG) auditor's testing evidence.

---

## Exception workflow (Management Review Required)

When the Falsifier adversarial agent dissents on a high or critical incident, GUARDIAN auto-routes the disclosure to a Management Review Required queue inside the Sponsor Sustainability dashboard. Default routing: Sustainability Controller (or above), SLA 4 hours for critical / 24 hours for high. The court-evidence bundle attaches the adversarial review, chain hash, specialists timeline, and four peer acknowledgements. This is the named-reviewer sign-off Big Four Information Technology General Controls testing looks for. Live in v4 on every incident bundle (`management_review_required: bool`, `management_review: {...}` fields).

---

## Categories

- AI & ML → Generative AI
- AI & ML → Multi-Agent Systems
- Industry Solutions → Sustainability & ESG
- Security & Compliance → Regulatory Reporting

---

## Tags

`gemini`, `agent-development-kit`, `a2a-protocol`, `adversarial-agent`, `audit-mode`, `falsifier`, `tnfd`, `csrd`, `esrs-e4`, `biodiversity`, `sustainability`, `vertex-ai-search`, `lyria`, `imagen`, `veo`, `cloud-run`, `multi-agent`, `compliance-automation`, `enterprise-agent-interop`, `board-deck-export`

---

## Pricing model

See `PRICING.md` for the full three-tier model. Listed on Marketplace as **Subscription** with usage-based incident credits. SKU lines:

| SKU | Price | Includes |
|---|---|---|
| **GUARDIAN Core (annual)** | $60,000 / year | 1 sponsored reserve, up to 10,000 incidents/year, all 4 A2A peers, TNFD + CSRD-ESRS-E4 report generation, standard support |
| **GUARDIAN Portfolio (annual)** | $180,000 / year | Up to 5 reserves, 50,000 incidents/year, dedicated TAM, quarterly audit-prep review |
| **GUARDIAN Enterprise (custom)** | from $300,000 / year | Unlimited reserves, SOC 2 evidence pack, custom A2A peer onboarding, named CSM, 24/7 priority |
| **Overage** | $2.50 / incident over plan | Soft cap at 1.5× plan; hard cap requires sales conversation |

Free trial: 30-day pilot on a single reserve, capped at 500 incidents. Billed via Google Cloud invoice; uses committed-spend if available.

---

## Support tiers

- **Standard** (included with Core): business-hours email + community Slack, 1 business day response SLO
- **Priority** (included with Portfolio): 24/7 email + Slack Connect, 4-hour response SLO
- **Premier** (Enterprise): named CSM, 1-hour response SLO, root-cause within 24h, optional dedicated cluster

Support contact: `support@guardian.example` _(replace with real domain pre-submission)_.

---

## Deployment

GUARDIAN ships as a Cloud Run-native, multi-service deployment:

- 1 × Orchestrator service (1 vCPU, 2 GB, autoscaled 1–10 instances)
- 4 × A2A peer services (each 1 vCPU, 2 GB, autoscaled 0–5; scales to zero between incidents)
- 1 × Ops Center frontend (1 vCPU, 1 GB, autoscaled 1–3)

Deploy via the provided setup guide (Terraform module in progress for submission): provisions the 6 Cloud Run services, configures Vertex AI Search data store seeding, sets up Cloud Run service-to-service IAM with `roles/run.invoker`, and outputs the Ops Center URL.

Time-to-first-incident in a clean GCP project: ~12 minutes.

---

## Integrations

- **Google Cloud:** Vertex AI (Gemini 2.5 Pro, multimodal Live + Vision), Vertex AI Search, Cloud Run, BigQuery, Firestore, Cloud Storage, Cloud Logging
- **A2A protocol v0.3.0:** any enterprise agent that publishes a compliant agent card can be added as a 5th+ peer (Cloud Endpoints / API Gateway optional)
- **Disclosure outputs:** TNFD-aligned JSON for the EFRAG sustainability reporting taxonomy; CSRD-ESRS-E4 datapoint mapping (XBRL via partner integration on Enterprise tier)
- **Cross-border coordination:** Neighbor Park peer issues structured handoff IDs compatible with the CITES-MIKE programme's bilateral reporting templates (TRAFFIC-style standing-committee format); does not replace formal MIKE submissions
- **Ranger dispatch:** AgentPhone MCP for SMS / voice / radio (optional)

---

## Security & compliance

- Service-to-service Cloud Run authentication via Google ID tokens
- All A2A peers deployed `--no-allow-unauthenticated`; only the orchestrator's runtime service account has `roles/run.invoker`
- Incident IDs are Secure Hash Algorithm 256-bit (SHA-256) derived and idempotent - same observation produces the same incident_id, preventing duplicate ranger dispatches or duplicate TNFD filings
- Echo-detection retry guard with prompt-mutation hardens against LLM tool-call flakes
- Cross-thread-safe event firehose for live operations dashboard
- SOC 2 Type II evidence-pack roadmap available on Enterprise tier (full SOC 2 attestation in progress; Enterprise customers receive interim controls-mapping workbook + customer-managed-key option)
- Designed for GDPR, Kenya DPA, and Tanzania DPA alignment via per-customer GCP region pinning (ranger PII never leaves the host country's region); customer-specific legal review required pre-deployment

---

## Demo + documentation

- **Live demo:** https://guardian-ops-center-180171737110.us-central1.run.app
- **Source repository:** https://github.com/odominguez7/guardian _(replace with real path)_
- **Agent cards:** https://guardian-180171737110.us-central1.run.app/a2a/app/.well-known/agent-card.json
- **3-minute video walkthrough:** _(D19-D21 production)_

---

## Buyer persona fit

See `BUYER_PERSONA.md`. Lead buyer: F500 Chief Sustainability Officer or Director of ESG Reporting at a firm with a sponsored conservation portfolio (e.g. Tiffany, LVMH, KPMG, AB InBev) facing CSRD-ESRS-E4 disclosure where in scope and TNFD-aligned expectations.

---

## Producer info

- **Producer:** GuardIAn Wildlife
- **Founder + CEO:** Omar Dominguez Mondragon (MIT Sloan)
- **Listing contact:** `omar.dominguez7@gmail.com`
- **Producer portal entry:** see `SUBMISSION_NOTES.md`

---

## Required listing-page URLs

The following URLs are required by the Google Cloud Marketplace Producer Portal at SaaS-listing submission. Drafted as placeholders; finalized pre-submission D17-D18.

| Field | URL | Status |
|---|---|---|
| Privacy policy | `https://guardian.example/privacy` | TODO before submission |
| Terms of service / EULA | `https://guardian.example/terms` | TODO before submission |
| Support terms + SLO | `https://guardian.example/support` | TODO before submission |
| Pricing terms | `https://guardian.example/pricing-terms` | TODO before submission |
| Trademark attestation | self-attested on Producer Portal form | DONE on submission |
| Third-party security review | self-attested + SOC 2 roadmap | DONE on submission |
| Demo video URL | YouTube unlisted, D19-D21 production | TODO D19 |
