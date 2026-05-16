# GUARDIAN SKU - what the customer actually buys

_The line items inside each tier. Read this before pricing conversations._

---

## What ships when the customer clicks Subscribe

A Marketplace-launched GUARDIAN tenant is a guided deployment into the customer's existing GCP project (Terraform module in progress for submission) that provisions, in this order:

| # | Service | Cloud Run instances | Why |
|---|---|---|---|
| 1 | Orchestrator | 1 service, autoscale 1–10, 1 vCPU / 2 GB | Root agent, A2A client, demo + ops API, event firehose |
| 2 | Park Authority Peer | 1 service, autoscale 0–5 | A2A peer #1 (ranger dispatch ack) |
| 3 | Sponsor Sustainability Peer | 1 service, autoscale 0–5 | A2A peer #2 (TNFD entry filer) |
| 4 | Funder Reporter Peer | 1 service, autoscale 0–5 | A2A peer #3 (program impact receipt) |
| 5 | Neighbor Park Peer | 1 service, autoscale 0–5 | A2A peer #4 (cross-border mutual aid) |
| 6 | Ops Center frontend | 1 service, autoscale 1–3, 1 vCPU / 1 GB | Live operations dashboard (Next.js + Mapbox) |
| 7 | Vertex AI Search data store | `guardian-collection` | IUCN / CITES / playbook corpus RAG |
| 8 | BigQuery dataset | `adk_agent_analytics` | AgentOps observability, eval evidence |
| 9 | Cloud Storage bucket | `<project>-guardian-docs` | Corpus + evidence-bundle artifacts |
| 10 | IAM bindings | service-to-service `roles/run.invoker` between orchestrator and 4 peers | Zero-trust agent communication |

Total provisioned services: 6 Cloud Run + 1 Vertex AI Search + 1 BigQuery dataset + 1 GCS bucket + IAM. All in the customer's GCP project; all billed to the customer's existing GCP invoice.

Time from "Subscribe" click to first incident-processable: **≈ 12 minutes** in a clean GCP project (Cloud Run service provisioning is the long pole).

---

## What's NOT in the SKU (intentional)

These would balloon the SKU and confuse the buyer:

- **Camera hardware.** Customer's reserves already have camera traps. GUARDIAN ingests existing GCS-uploaded clips.
- **Ranger radios / SMS gateway.** Optional AgentPhone MCP integration; customer brings their own number pool.
- **Reserve management software replacement.** We integrate via A2A, we do not replace SMART.
- **Insurance product underwriting.** That's Tier 3 of the customer model and a different SKU (post-MVP).

---

## Per-tier line items

### Core ($60,000 / year)

- 1 sponsored reserve
- 10,000 incidents/year allotment
- All 4 A2A peers
- Specialist agents shipped today: Stream Watcher, Audio, Species ID (plus Orchestrator)
- TNFD + CSRD-ESRS-E4 + CITES-MIKE report generation
- Vertex AI Search corpus (IUCN Red List, CITES Appendix I-III, anti-poaching playbook)
- Standard support (business-hours email + community Slack, 1 BD response)
- Annual audit-prep workbook (PDF + JSON)

### Portfolio ($180,000 / year)

Everything in Core, plus:

- Up to 5 reserves
- 50,000 incidents/year allotment
- Priority support (24/7 email + Slack Connect, 4-hour response)
- Dedicated TAM (8 hours/month implementation + tuning)
- Quarterly audit-prep review (TAM walks Big 4 auditor through evidence chain)
- Looker Studio dashboard pre-built for CSO read-only access

### Enterprise (from $300,000 / year)

Everything in Portfolio, plus:

- Unlimited reserves
- 100,000+ incidents/year (custom)
- Premier support (named CSM, 1-hour response, root-cause in 24h)
- SOC 2 Type II evidence pack
- Custom A2A peer onboarding (e.g. add a 5th peer for insurance carrier or government agency)
- Optional dedicated Cloud Run / GKE cluster
- Cloud Trace + Cloud Logging delivered to customer's existing observability stack
- Annual on-site implementation review (1 GUARDIAN engineer, 1 week)
- Multi-region deployment (US + EU + APAC) for data-residency-constrained customers

---

## Unit economics (per Core deployment, per year)

### Per-incident cost model (5 LLM calls per incident, ~1,400 token avg)

Each incident triggers a chain of LLM calls: orchestrator routing (≈400 tok in / 200 tok out), one specialist (≈1,000 tok in image+prompt / 400 tok out), and four peer A2A handoffs (≈800 tok in / 200 tok out each).

| LLM call | Input tokens | Output tokens | Per-call cost at Gemini 2.5 Pro list ($1.25/M input · $5.00/M output) |
|---|---|---|---|
| Orchestrator routing | 400 | 200 | $0.0015 |
| Specialist (Vision or Audio) | 1,000 | 400 | $0.0033 |
| Peer × 4 | 3,200 | 800 | $0.0080 |
| **Per-incident LLM total** | **4,600** | **1,400** | **~$0.013** |

At 10,000 incidents/yr this is **~$130 LLM cost**. We budgeted $1,800 to absorb spikes (eval suite, retry-on-flake, judge-clicked-the-button), giving 14× headroom over base case.

### Annual cost breakdown

| Line | Annual cost | Basis |
|---|---|---|
| Vertex AI inference (10K incidents × $0.013 + eval + retry headroom) | ~$1,800 | Per-incident model above |
| Cloud Run compute (6 services, mostly idle, ~2 vCPU-hrs/day avg) | ~$1,200 | $0.0000240/vCPU-s × 730 vCPU-hr × 12 mo |
| Vertex AI Search storage + query (7-doc corpus, 50K queries/yr) | ~$600 | Storage flat; query at $4/1K LRO calls |
| BigQuery analytics storage + query (5 GB stored, 100 GB query/yr) | ~$200 | $0.02/GB stored + $5/TB query |
| Cloud Storage (evidence bundles + corpus, ~50 GB) | ~$120 | $0.02/GB · standard class |
| Cloud Logging + Trace | ~$240 | $0.50/GB ingest, ~40 GB/yr |
| Other (Pub/Sub, Memorystore optional, egress) | ~$300 | Headroom |
| **Subtotal infrastructure** | **~$4,460** | |
| TAM allocation (8 hr / month × $200/hr loaded) | $19,200 | Loaded = base + benefits + overhead; conservative |
| Support allocation (Standard tier - email + community Slack) | $2,400 | 20 hr/yr × $120/hr loaded support engineer |
| **Subtotal services** | **$21,600** | |
| **Total cost** | **~$26,060** | |
| **Core list price** | **$60,000** | |
| **Gross margin** | **~57%** | |

### Margin scaling

- **Portfolio** ($180K list): TAM hours stay flat at 8 hr/month while incident volume rises 5×, so per-reserve TAM cost drops. Infrastructure scales with incidents (~$22K/yr at 50K incidents). Total cost ~$52K; **GM ~71%**.
- **Enterprise** ($300K list): adds CSM time, dedicated cluster optional, SOC 2 evidence pack maintenance. Infrastructure scales but flat for the first 100K incidents. Total cost ~$66K; **GM ~78%**.

### Overage margin check

Overage is $2.50/incident. Marginal cost per incident-above-plan = LLM ($0.013) + prorated infrastructure (~$0.05) + retry/eval headroom ($0.07) = **~$0.13/incident marginal cost**. Margin on overage is therefore ~95%, but capped because we don't let customers exceed 1.5× plan without a sales conversation.

---

## What's NOT charged for in the unit economics

- **Customer's GCP infrastructure spend.** Customer pays Google directly via their existing invoice. ~$4,460/yr above. We do not mark this up - it's transparent on their invoice.
- **Customer's existing GCP committed-spend.** If the customer has a `commit-burndown` agreement, the Marketplace subscription consumes against it. Sales-friction reducer, not a margin lever.

---

## Renewal mechanics

Annual subscription auto-renews 30 days before term end unless the customer opts out via Marketplace console. Standard 60-day notification window for price changes per Marketplace policy.

Churn-prevention triggers:

- **Incident volume dropping below 30% of plan for 2+ quarters** - automatic outreach from CSM; signals reserve activity gap or sensor degradation, not GUARDIAN failure.
- **Compliance season approaching (Q3-Q4 of customer's fiscal year)** - pro-active audit-prep walkthrough.
- **CSRD reporting cycle change** - CSM proactively maps any framework updates into the GUARDIAN report templates.

---

## What gets bundled into the next-tier upsell pitch

Core → Portfolio:
- Customer hits 8K+ incidents (80% of plan)
- Customer's auditor flags need for cross-reserve pattern data
- Customer adds a second reserve to portfolio

Portfolio → Enterprise:
- Customer hits 40K+ incidents
- Customer's procurement triggers a SOC 2 / supplier-security review
- Customer asks for a custom peer (insurance carrier, government, second-tier funder)
- Customer requires multi-region deployment (EU data-residency for ESRS filings)
