# Producer Portal submission walkthrough

_Step-by-step for Omar. Every field below is copy-paste ready. Estimated time: 10 minutes if no account-verification blocking; 30-60 minutes if first time + needs producer-account setup._

---

## Step 0: Producer-account preconditions

Google Cloud Marketplace Producer Portal requires an enrolled producer account BEFORE listing submission. Verify or enroll at:

> https://console.cloud.google.com/producer-portal?project=guardian-gfs-2026

If first time, complete:

| Required | Status | Action |
|---|---|---|
| Producer agreement signed | TBD | One-click acceptance in Producer Portal |
| Legal entity of record | TBD | Use personal name + MIT Sloan address as transitional. Real LLC formation is post-hackathon. |
| Tax form (W-9 US or W-8BEN non-US) | TBD | Fill personal W-9 if no LLC yet. |
| Stripe Connect billing onboarding | TBD | Skip for "Free trial only" listing first; add billing pre-D17. |
| GCP project owner role | DONE | `guardian-gfs-2026` is Omar's |

If the Portal blocks listing creation pending producer enrollment, that itself counts as the submission-attempt evidence per hackathon judging. Screenshot the block screen + add to `screenshots/submission-block.png`.

---

## Step 1: Create new SaaS listing

Producer Portal -> "Add product" -> select **SaaS** product type.

Form fields:

| Field | Value (copy-paste) |
|---|---|
| Product name | `GUARDIAN - Biodiversity Operations Platform for Enterprise` |
| Product ID (slug) | `guardian-biodiversity-ops` |
| Producer name | `Omar Dominguez Mondragon - CEO & Founder, GuardIAn Wildlife (MIT Sloan)` |
| Producer support email | `omar.dominguez7@gmail.com` |
| Primary category | `AI & ML > Multi-Agent Systems` (or closest available; fall back to `AI & ML > Generative AI`) |
| Secondary category | `Industry Solutions > Sustainability & ESG` (or closest available) |

---

## Step 2: Listing copy

Open `marketplace/LISTING.md` side-by-side with the Producer Portal form. Copy these fields exactly:

| Portal field | Source in LISTING.md |
|---|---|
| Tagline (short description) | section `## Listing summary` |
| Long description / overview | section `## Solution overview` |
| Key benefits | section `## Key benefits` (5 bullets) |
| Integrations | section `## Integrations` |
| Security + compliance | section `## Security & compliance` |
| Tags | section `## Tags` |

---

## Step 3: Pricing

In Producer Portal, choose **Subscription** pricing model. Configure three SKU lines per `PRICING.md`:

| Plan name | Annual price | Configure |
|---|---|---|
| `GUARDIAN Core` | $60,000 / year | 1 reserve, 10,000 incidents included, $2.50 overage |
| `GUARDIAN Portfolio` | $180,000 / year | 5 reserves, 50,000 incidents included, $2.50 overage |
| `GUARDIAN Enterprise` | from $300,000 / year | Custom; flag as "Contact sales" |

Set free trial: **30 days, single reserve, capped 500 incidents**.

Billing path: bill via the customer's existing Google Cloud invoice (Subscription default). Mark Stripe Connect as TBD if not yet onboarded; this can block GA listing but NOT block draft submission.

---

## Step 4: Media uploads

Upload these to the Producer Portal media section. Required minimum: 1 logo + 3 screenshots. Recommended: 5-8 screenshots + 1 video.

| File | Source | Required? |
|---|---|---|
| Logo (256x256 PNG) | TODO: generate from marketplace-preview.html `.listing-logo` block | Required |
| Screenshot 1: Ops Center idle state | TODO: capture from https://guardian-ops-center-180171737110.us-central1.run.app | Required |
| Screenshot 2: Ops Center 4-peer fanout cinema | TODO: capture mid-scenario | Required |
| Screenshot 3: Incident panel with all 4 peer cards | TODO: capture post-fanout | Required |
| Screenshot 4: marketplace-preview.html rendered | DONE: open `marketplace/marketplace-preview.html`, full-page screenshot | Optional |
| Screenshot 5: Agent card JSON | TODO: curl agent-card.json, render as syntax-highlighted screenshot | Optional |
| Demo video (3 min) | D19-D21 production | Optional now, required pre-GA |

---

## Step 5: Required URLs

The Portal asks for these URLs. Use the table below (some are TODO placeholders that get final URLs pre-submission).

| Portal field | URL |
|---|---|
| Public website | https://github.com/odominguez7/guardian (use repo until guardian.example.com is live) |
| Privacy policy | `https://guardian.example/privacy` (TODO finalize) |
| Terms of service | `https://guardian.example/terms` (TODO finalize) |
| Support contact | `omar.dominguez7@gmail.com` |
| Support terms | `https://guardian.example/support` (TODO finalize) |
| Demo URL | https://guardian-ops-center-180171737110.us-central1.run.app |

---

## Step 6: Deployment configuration

Producer Portal asks how the customer deploys. Choose **SaaS service URL** (since GUARDIAN is a multi-service Cloud Run deployment, not a single VM/container).

| Field | Value |
|---|---|
| Deployment type | SaaS (customer connects to your hosted service) |
| Service endpoint | https://guardian-180171737110.us-central1.run.app |
| Customer onboarding flow | Email-based onboarding link sent post-subscription; CSM walkthrough included |
| Customer-facing API documentation | _add when public_ |

For Marketplace listings requiring "deploy into customer's GCP project" (the GUARDIAN intended motion long-term), shift to a `Terraform-based` listing later. For hackathon submission, the SaaS-service-URL path works.

---

## Step 7: Submit for review

Click **Submit for review** at the bottom of the Portal page.

Expected response:

1. Portal returns a confirmation with a draft listing URL like `console.cloud.google.com/producer-portal/products/<id>/preview`.
2. Google sends an automated email confirming receipt of submission.
3. First-pass automated check completes within 24 hours; surface flags require fixes.
4. Full Google review takes 4-6 weeks for first-time ISVs. Approval is post-hackathon.

---

## Step 8: Capture receipt

Whatever the Portal returns (submission-confirmation page, OR a producer-account-enrollment-required page), screenshot it.

```bash
# Save as:
marketplace/screenshots/submission-receipt-<YYYYMMDD>.png
```

Then update `SUBMISSION_NOTES.md`:

```markdown
## D17 submission attempt log

- 2026-05-31 HH:MM PT: Opened Producer Portal at console.cloud.google.com/producer-portal?project=guardian-gfs-2026
- 2026-05-31 HH:MM PT: <what happened: created draft listing / blocked at producer enrollment / etc>
- Receipt saved to: marketplace/screenshots/submission-receipt-20260531.png
- Listing URL (draft state): <paste URL or "blocked - see screenshot">
```

That receipt is the D18 deliverable. Hackathon judging treats a submission-attempt screenshot as evidence the SKU motion is real, regardless of whether Google has approved the listing yet.

---

## What if Producer Portal blocks at producer enrollment?

The Track 3 mandate is satisfied by **structural evidence the product is built as a Marketplace SKU**, not by an approved listing. If the Portal blocks at producer enrollment (very likely for a first-time founder with no LLC):

1. Screenshot the block screen.
2. In `SUBMISSION_NOTES.md`, log: "Submission attempt blocked at producer-enrollment step pending legal entity formation. Listing package complete; enrollment is a post-hackathon side-quest. See screenshot."
3. Submit the hackathon entry with the listing package + the screenshot + the live Ops Center demo. That's a real, complete D18 deliverable.

Do NOT try to fake an entity formation to push past the block. Real founders + real reviewers will both reward "honest about the gate" over "claimed approval we don't have."
