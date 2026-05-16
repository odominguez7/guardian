# GUARDIAN Marketplace - submission notes

_Trail of evidence for the D18 Marketplace listing milestone._

---

## Submission path chosen

Google Cloud Marketplace **Producer Portal** at https://console.cloud.google.com/producer-portal - the canonical entry point for ISV listing submissions.

This is the path Google itself documents for ISVs publishing SaaS / Subscription products onto the Marketplace catalog. Alternative paths considered:

| Path | Why not |
|---|---|
| **Google Cloud Marketplace Partner Portal** | Requires Google Cloud Partner Advantage membership at the Partner-Plus tier or above. ~12-month onboarding cycle. Not feasible inside hackathon timeline. |
| **Cloud Marketplace Self-Service for SaaS** | Same as Producer Portal under the hood; rebranded. Use Producer Portal directly. |
| **Marketplace via reseller** | Margin loss + slow. Not a hackathon-stage move. |

---

## Submission readiness checklist

Status as of 2026-05-15:

| Requirement | Status | Artifact |
|---|---|---|
| Product name + tagline | DONE | `LISTING.md §Product name` |
| Listing summary (130 char max) | DONE | `LISTING.md §Listing summary` |
| Solution overview (200-400 words) | DONE | `LISTING.md §Solution overview` |
| Key benefits (5 bullets) | DONE | `LISTING.md §Key benefits` |
| Categories + tags | DONE | `LISTING.md §Categories / §Tags` |
| Pricing model (SKU + per-line) | DONE | `PRICING.md` |
| Support tiers | DONE | `LISTING.md §Support tiers` |
| Deployment instructions | DONE | `LISTING.md §Deployment` |
| Security + compliance overview | DONE | `LISTING.md §Security & compliance` |
| Producer / contact info | DONE | `LISTING.md §Producer info` |
| Working demo URL | DONE | https://guardian-ops-center-180171737110.us-central1.run.app |
| Source repo URL | TODO (need real path) | placeholder in LISTING.md |
| 3-min video walkthrough | TODO D19-D21 | n/a |
| Screenshots (min 3, recommended 5-8) | IN PROGRESS | `marketplace/screenshots/` |
| Terraform one-click deploy module | TODO | needs `marketplace/terraform/` |
| Producer portal account verification | TODO | requires Google producer onboarding form |
| Legal entity Stripe Connect / billing account | TODO | requires founding entity legal docs |
| Tax + W-9 | TODO | requires legal entity |

---

## What's required vs nice-to-have for hackathon judging

The Track 3 mandate says: "Refactor for Marketplace + Gemini Enterprise." It does not require a fully *approved* Marketplace listing (that takes weeks of Google's review process). It requires demonstrable evidence that GUARDIAN is **structured as a Marketplace SKU**.

What we have for the judging cycle:

1. **The listing artifacts** (`LISTING.md`, `PRICING.md`, `SKU_OVERVIEW.md`, `BUYER_PERSONA.md`) - proves the SKU is real on paper.
2. **The live multi-service deployment** - proves the SKU is structurally deployable, not vaporware.
3. **The 4 A2A peers as independent Cloud Run services with their own SAs** - proves the multi-tenant architecture every Marketplace SKU requires.
4. **The Producer Portal submission attempt** (this document) - proves intent + path.

What we will NOT have:

- A Marketplace-listed, search-indexable SKU. Google's listing review takes ≥ 6 weeks for first-time ISVs. Hackathon timeline is 22 days from D1.
- Stripe Connect billing live. Requires the founding legal entity which is a multi-week side-quest.

---

## Producer Portal submission steps performed

_To be appended with timestamped action evidence on D17-D18 (2026-05-31 to 2026-06-01)._

1. _[D17 planned]_ Open `console.cloud.google.com/producer-portal` in `guardian-gfs-2026` GCP project.
2. _[D17 planned]_ Create a new SaaS / Subscription listing entry.
3. _[D17 planned]_ Paste listing copy from `LISTING.md` into producer portal form fields.
4. _[D17 planned]_ Upload `marketplace/screenshots/*.png` as listing media.
5. _[D17 planned]_ Set pricing per `PRICING.md` (Subscription, USD, 3 tiers).
6. _[D17 planned]_ Configure deployment via Terraform module reference.
7. _[D17 planned]_ Submit for Google review.
8. _[D17 planned]_ Screenshot the submission confirmation page → save to `marketplace/screenshots/submission-receipt.png`.
9. _[D17 planned]_ Save the listing URL (will be a draft URL until approval) → append to this file.

---

## Why this still scores well for Track 3 without approval

The hackathon rubric's Business Case criterion is about evidence that the team **understands the buyer + SKU motion**, not that Google has rubber-stamped the listing. A submission attempt with full artifacts demonstrates that understanding more durably than a half-baked approved listing would.

The judging panel sees:

1. Buyer persona with named target accounts (Sarah Chen → AB InBev, LVMH, KPMG, Tiffany).
2. Pricing model justified from three independent frames (cost of non-compliance, cost of human alternative, value of a single prevented incident).
3. Unit economics with 57-78% gross margin math.
4. SKU structurally aligned to Marketplace's mandatory listing fields.
5. Live multi-service deployment matching the SKU's described architecture.
6. Submission attempt evidence (this document + receipt screenshot when D17-D18 execute).

That covers the Business Case scoring axis in full.

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Google reviewer rejects listing for "no legal entity yet" | Listing artifacts still satisfy hackathon judging; legal entity is a post-hackathon side-quest. |
| Producer Portal flow demands SOC 2 readiness questionnaire upfront | Enterprise SKU lists SOC 2 evidence pack; Core + Portfolio do not require it. Decline question or mark "in progress." |
| Marketplace categorization restricts to "AI & ML" only (no "Sustainability") | Add `Industry Solutions → Sustainability & ESG` as secondary; primary tagging can be `Generative AI / Multi-Agent`. |
| Listing requires legal name, address for Stripe Connect | Use founder name + MIT MBA address as legal-entity-of-record proxy for hackathon submission; flag as transitional. |
