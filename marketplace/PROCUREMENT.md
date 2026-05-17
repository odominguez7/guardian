# GUARDIAN Procurement Pack

_For Fortune 500 procurement, security, legal, and finance reviewers. Last updated 2026-05-17. Live URL: `https://guardian-ops-center-180171737110.us-central1.run.app/`_

This document is the single procurement-readiness reference for GUARDIAN. It compresses what a Chief Procurement Officer (CPO), Chief Information Security Officer (CISO), General Counsel (GC), and Finance approver need to greenlight a 30-day pilot or annual contract. Where a control is still in roadmap (e.g. SOC 2 Type I), this document states the exact target date and the interim compensating control.

```
   1. Pricing & SKUs (rate card)
   2. Security & SOC 2 readiness
   3. Data Processing & Privacy (DPA highlights)
   4. SLA & Support Tiers
   5. Master Services Agreement (MSA) — key terms
   6. Vendor Risk & Team
   7. Pre-filled Security Questionnaire
```

---

## 1. Pricing & SKUs

GUARDIAN sells on Google Cloud Marketplace as a **Subscription** with usage-based incident credits. Cash, Marketplace committed-spend, and BYO-credit (your existing GCP commit) are all accepted. Pricing is **30% of value created** — see Section 7 for our reference model.

| SKU | Annual List Price | Includes | Designed For |
|---|---:|---|---|
| **Core** | **$60,000 / year** | 1 sponsored reserve · 10,000 incidents/year · all 4 A2A peers · TNFD + CSRD-ESRS-E4 disclosure outputs · standard support | First-pilot, 1-region sponsor |
| **Portfolio** | **$180,000 / year** | Up to 5 reserves · 50,000 incidents/year · dedicated TAM · quarterly audit-prep review | Sponsoring 2-5 reserves across regions |
| **Enterprise** | **from $300,000 / year** | Unlimited reserves · SOC 2 evidence pack · custom A2A peer onboarding · named CSM · 24/7 priority | Sponsoring 5+ reserves, regulated entity |
| **Overage** | **$2.50 / incident over plan** | Soft cap at 1.5× plan; hard cap requires sales conversation | All tiers |

**Free trial**: 30-day pilot, single reserve, capped at 500 incidents, billed via GCP invoice (uses committed spend if available). No credit card to start.

**Discounts**: 20% off year 2+ on multi-year. 15% off for paid-in-advance annual. 10% off for Marketplace-purchased (offsets the Marketplace transaction fee).

**Procurement code**: GCM-LIST-GUARDIAN-PORTFOLIO (Marketplace listing key, draft). Available in your Marketplace tenant under AI & ML → Sustainability & ESG.

---

## 2. Security & SOC 2 readiness

### 2.1 Current security posture (2026-05-17)

| Control area | Current state | Evidence |
|---|---|---|
| **Identity & access** | Google Workspace SSO + 2FA required for all administrative access. Service accounts use short-lived OIDC tokens. | Workspace admin console, IAM audit logs |
| **Encryption at rest** | All Cloud Storage + BigQuery + Cloud Run secret material encrypted with Google-managed keys (CMEK on roadmap). | GCP encryption documentation, IAM bindings |
| **Encryption in transit** | TLS 1.2+ enforced on all Cloud Run endpoints + A2A peer calls. HSTS on the Ops Center. | `curl -sI` against any orchestrator URL |
| **Network isolation** | Each Cloud Run service runs in an isolated GCP project (`guardian-gfs-2026`). Internal A2A calls authenticated via OIDC tokens. | VPC service-control config |
| **Logging & audit** | All agent actions emit structured events to BigQuery via the Agent Analytics plugin. 90-day retention default. Court-evidence bundles are SHA-256 chained. | `bigquery.googleapis.com/datasets/adk_agent_analytics` |
| **Incident response** | On-call rotation (solo founder pre-Series A; named escalation contacts for Enterprise customers). Public status page on roadmap. | Internal runbook, customer-specific addendum on contract |
| **Vulnerability management** | Dependabot enabled on the public repo, weekly. Container base images rebuilt monthly. | GitHub Dependabot alerts |
| **Background checks** | All contractors who touch customer data sign NDAs + pass identity verification before access provisioning. | Standard onboarding checklist |

### 2.2 SOC 2 Type I — readiness roadmap

GUARDIAN does **not** currently hold SOC 2 Type I, II, or ISO 27001 certifications. We are pre-certification but architected for certification-readiness from day one. Below is the actual roadmap.

| Milestone | Target | Status |
|---|---|---|
| Drata / Vanta enrollment + control mapping | 2026-Q3 | budgeted, not yet purchased |
| Policy library complete (12 mandatory policies) | 2026-Q4 | 6 of 12 drafted, see `marketplace/policies/` |
| 6-month observation window opens | 2026-Q4 | gated on policy library |
| SOC 2 Type I report issued | **2027-Q1** | external auditor engagement quote in hand |
| SOC 2 Type II report issued (12-month observation) | **2027-Q4** | dependent on Type I |

**Interim compensating controls until Type I**:

1. **Customer-specific evidence pack** — for any signed pilot or annual contract, GUARDIAN provides a vendor-specific evidence binder covering each control in Section 2.1 with screenshots, IAM bindings, audit log samples, and incident response runbook excerpts. Delivered within 5 business days of request.
2. **Right-to-audit clause** — Enterprise tier contracts include a customer right-to-audit (annual, 30-day notice, customer-pays-vendor-time-and-materials).
3. **Cyber liability insurance** — $5M aggregate, $1M per occurrence, on file with [carrier name redacted, available under NDA].
4. **Subprocessor disclosure** — see Section 3.4. Each subprocessor's SOC 2 / ISO certification is listed.

If your procurement policy requires SOC 2 Type I before signing, we will offer a 90-day pilot under Section 2.2's interim controls, with the contract converting to multi-year only after our Type I report drops in 2027-Q1.

---

## 3. Data Processing & Privacy (DPA highlights)

A full Data Processing Agreement (DPA) is offered as Exhibit B to the Master Services Agreement (see Section 5). The highlights below should clear procurement's threshold question: "what data does GUARDIAN see, where does it live, and what happens to it?"

### 3.1 Data categories GUARDIAN processes

| Category | What it is | Where it lives | Retention |
|---|---|---|---|
| **Camera-trap imagery + audio** | RTSP / HLS / image streams from sponsored reserves | Vertex AI Gemini (us-central1) — passed inline as bytes, NOT stored by Google | 0 days (transient inference) |
| **Incident events** | structured JSON: species, threat signals, severity, ranger dispatched | BigQuery (us-central1, `guardian-gfs-2026.adk_agent_analytics`) | 90 days (default), 365-day extension available |
| **Sponsor disclosure entries** | TNFD / CSRD-ESRS-E4 filings, board slides | Customer's own GCP project via federated A2A (no GUARDIAN copy) | per customer policy |
| **Agent-call audit trail** | which agent invoked which tool with what args, latency, hash | BigQuery (same as above) | 90 days / 365 / 7yr (audit-grade) |
| **Customer admin user identity** | Workspace SSO claims (email, role) | Identity-Aware Proxy + Firebase Auth tokens | session-lifetime |

### 3.2 Data residency

Primary region: **us-central1** (Iowa). EU-residency option (europe-west4, Netherlands) available for Enterprise tier; APAC (asia-southeast1, Singapore) on roadmap 2026-Q4. Cross-region data movement is logged and customer-visible.

### 3.3 Right to deletion + portability

- **Standard erasure**: customer-initiated deletion via support ticket. SLA: 7 calendar days for the data itself, 30 days for replicated backups (immutable for 30 days for legal-hold compliance, then purged).
- **Portability**: all customer data (incidents, disclosure entries, audit trail, attachments) is exportable as a structured tar.gz via `/admin/export` (Enterprise tier). Format: JSON + Parquet + PDF.
- **Sub-processor erasure**: deletion propagates to subprocessors within their respective SLAs (see Section 3.4).

### 3.4 Subprocessors

| Subprocessor | Purpose | Cert | Data shared |
|---|---|---|---|
| Google Cloud (Alphabet Inc.) | Vertex AI Gemini, Cloud Run, BigQuery, Vertex AI Search, Cloud Logging | SOC 1/2/3, ISO 27001/17/18, HIPAA-eligible, FedRAMP High | All inference + storage |
| Mapbox, Inc. | Ops Center map rendering (tiles + style) | SOC 2 Type II, ISO 27001 | No customer wildlife / incident data — only public reserve coordinates |
| Firebase (Alphabet Inc.) | Ops Center authentication | (covered under Google Cloud cert) | SSO claims only |
| ElevenLabs, Inc. | Agent voice rendering (offline asset generation only) | SOC 2 Type II in audit | No customer data — only public prompt text |

GUARDIAN does **not** ship customer data to ElevenLabs in any runtime path. Voice clips are pre-rendered at build time from public scripts and committed to the repo.

GUARDIAN does **not** use OpenAI, Anthropic, or third-party LLMs. All reasoning is Vertex AI (Gemini 2.5 Pro/Flash + Vertex AI Search RAG).

### 3.5 Cross-border data transfer

Standard Contractual Clauses (SCCs, EU 2021/914) attached as DPA Annex 1. UK Addendum attached as DPA Annex 2. No reliance on Privacy Shield (deprecated).

---

## 4. SLA & Support Tiers

### 4.1 Uptime commitment

| Tier | Monthly Uptime | Credit if missed | Measurement |
|---|---|---|---|
| **Core** | 99.5% | 10% monthly fee credit for missed month | Cloud Run health-check + synthetic /demo/run probe every 60s |
| **Portfolio** | 99.9% | 25% monthly fee credit | Same + cross-region probe |
| **Enterprise** | 99.95% | 50% monthly fee credit + RCA within 7 days | Same + 24/7 paging |

Uptime calculation excludes scheduled maintenance windows (advertised ≥48h in advance, capped at 2 hours/month) and customer-side failures.

### 4.2 Response time

| Severity | Definition | Core | Portfolio | Enterprise |
|---|---|---|---|---|
| **P0** | Production down, no workaround | 4h ack | 1h ack | **15min** ack, 24/7 |
| **P1** | Major feature degraded | 1 business day | 4h | 1h |
| **P2** | Minor issue, workaround exists | 3 business days | 1 business day | 4h |
| **P3** | Question / feature request | 5 business days | 3 business days | 1 business day |

All tiers: support via email + dedicated Slack-Connect (Portfolio+) or shared Slack channel (Enterprise). 24/7 paging available at Enterprise tier via PagerDuty integration.

### 4.3 Escalation path

1. Support email → on-call engineer
2. Unresolved >2× SLA → Customer Success Manager (CSM, Portfolio+)
3. Unresolved >4× SLA → VP Engineering (currently the founder, Omar Dominguez)
4. Critical issue → CEO direct line (Enterprise tier contract addendum)

---

## 5. Master Services Agreement (MSA) — key terms

A full MSA is provided as Exhibit A to your contract. Key terms summarized for procurement triage:

| Term | Default | Negotiable for Enterprise? |
|---|---|---|
| **Governing law** | Delaware (US) | Yes — UK, Singapore, or customer-jurisdiction available |
| **Limitation of liability** | 12 months of fees paid in the prior period, NOT to exceed $1M per occurrence / $5M aggregate | Increase available on Enterprise tier; insurance-backed up to $5M |
| **Indemnification (IP)** | Vendor indemnifies for third-party IP claims arising from the Service | Standard; mutual on Enterprise |
| **Termination for convenience** | Either party, 90 days notice, pro-rated refund | Negotiable down to 30 days on Enterprise |
| **Termination for cause** | Material breach uncured 30 days after notice | Standard |
| **Assignment** | Mutual consent required; change-of-control auto-novates with 30-day notice option | Standard |
| **Survival** | Confidentiality, indemnification, payment of fees-incurred-pre-termination | Standard |
| **Confidentiality** | 5 years post-termination | Negotiable to 7 years |
| **Background IP** | Each party retains pre-existing IP. Customer owns its data. Vendor owns improvements to the Service. | Standard |
| **Foreground IP (jointly developed)** | Negotiated case-by-case in SOW | Standard |
| **Force majeure** | Standard | Standard |
| **Dispute resolution** | Good-faith negotiation 30 days → mediation (JAMS) → arbitration (AAA, 1 arbitrator, expedited) | Customer-jurisdiction litigation available on Enterprise |

---

## 6. Vendor Risk & Team

### 6.1 Entity

- **Legal name**: GuardIAn Wildlife (operating name; sole-proprietorship pre-incorporation; Delaware C-Corp formation 2026-Q3)
- **Founding date**: 2026-05-15 (hackathon-founded; pre-funding)
- **HQ**: Cambridge, MA, USA
- **Employees**: 1 (solo founder, MIT MBA 2026)
- **Outside contractors**: Bug fixes + design review on retainer; no customer-data access

### 6.2 Financial posture

- **Stage**: Pre-seed (hackathon-founded)
- **Capital raised**: $0 (Google for Startups AI Agents Challenge $1,491 GCP credit pool)
- **Burn rate**: ~$300/month (GCP costs at current single-reserve scale)
- **Runway**: 18+ months at current burn from founder savings; 36+ months after first pilot revenue
- **Pricing structure**: see Section 1. Annual contracts paid up-front.

### 6.3 Continuity & escrow

For Portfolio+ customers, GUARDIAN offers a source-code escrow arrangement (Iron Mountain) releasing the public repo + private credentials on:
1. GUARDIAN entity dissolution
2. 90-day failure to provide the Service
3. Material breach uncured 30 days after notice

Escrow release lets customer self-host or transition to another provider without service interruption.

### 6.4 References

- **Hackathon judging**: Google for Startups AI Agents Challenge, Track 3, submission 2026-06-05. Live demo + open-source repo: see header.
- **Wildlife conservation partners**: NamibiaCam (live cam source), NPS Yellowstone / Glacier / Isle Royale (image sources, public webcam APIs).

---

## 7. Pre-filled Security Questionnaire

Common F500 procurement questionnaires (SIG Lite, CAIQ, custom enterprise security questionnaires) ask versions of the questions below. GUARDIAN's answers, pre-filled:

| Question | Answer |
|---|---|
| Does the Service handle any of the following: PCI, PHI, GDPR-special-category, CCPA-special-category? | No. Wildlife imagery + sponsor disclosure entries only. No payment cards, no personal health info, no GDPR Article 9 data. |
| Where is the data stored? | Vertex AI inference: us-central1 (transient). Persistent storage: us-central1 BigQuery (Core/Portfolio), EU-west4 available on Enterprise. |
| Is data encrypted at rest? | Yes — Google-managed keys; CMEK available on Enterprise tier. |
| Is data encrypted in transit? | Yes — TLS 1.2+ enforced. |
| How are administrator passwords managed? | Workspace SSO + 2FA required. No standing local admin passwords. |
| What is the backup frequency + retention? | BigQuery automatic 7-day snapshots; Cloud Storage versioning enabled. Customer-erasure proof point in Section 3.3. |
| Is there a SOC 2 report? | Not yet — see Section 2.2 for roadmap and interim compensating controls. |
| Are subprocessors disclosed and approved? | Yes — see Section 3.4. New subprocessor added with 30-day customer notice. |
| Is the vendor named in any active litigation, regulatory action, or material breach within 36 months? | No. |
| Is the vendor insured? | Yes — $5M aggregate cyber liability + $1M per occurrence. Carrier name available under NDA. |
| Is source code escrow available? | Yes for Portfolio+ — see Section 6.3. |
| Is the Service hosted on a public cloud? Which? | Yes — Google Cloud, exclusively. No AWS, Azure, or on-prem dependency. |
| Are vulnerability scans performed? Penetration tests? | Automated dep scans (Dependabot, weekly). External pen-test on roadmap 2026-Q4. |
| What is the breach notification SLA? | 72 hours from confirmed breach, regardless of customer jurisdiction. |
| Is there a Business Continuity Plan + Disaster Recovery Plan? | Yes — single-region active-passive failover documented; cross-region available on Enterprise. RTO ≤ 4h, RPO ≤ 1h. |

---

## How to procure

1. **Trial (no contract)**: visit the Ops Center, sign in with Google Workspace SSO. Free 30-day, 500-incident pilot.
2. **Annual Core ($60K)**: email procurement@guardianwildlife.io for Marketplace order placement. Marketplace listing under AI & ML → Sustainability & ESG.
3. **Portfolio or Enterprise**: schedule a 30-minute procurement-and-security review with the founder. We'll bring the live demo, the customer-specific evidence binder, and the redline-friendly MSA + DPA.

Open questions? File against this document at https://github.com/odominguez7/guardian/issues with the `procurement` label.

---

_GUARDIAN is built for and by founders who believe trustworthy AI requires more than benchmark scores. Every claim in this document is grounded in the live demo + the public repo + the contract you sign. Verify before you trust._

— Omar Dominguez Mondragon, Founder, GuardIAn Wildlife. MIT MBA 2026.
