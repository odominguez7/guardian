# GUARDIAN Marketplace folder

_D18 deliverable - Track 3 mandate that GUARDIAN be structured as a Marketplace SKU._

This folder contains the full Marketplace listing package, prepared for submission to the Google Cloud Marketplace Producer Portal at https://console.cloud.google.com/producer-portal.

## Files

| File | Purpose |
|---|---|
| [`LISTING.md`](./LISTING.md) | The listing copy itself - product name, summary, overview, key benefits, categories, pricing, support tiers, deployment, security, demo URLs |
| [`PRICING.md`](./PRICING.md) | The three-tier pricing model with three independent rationale frames (cost-of-non-compliance, cost-of-human-alternative, value-of-prevented-incident) |
| [`SKU_OVERVIEW.md`](./SKU_OVERVIEW.md) | Per-tier line items, unit economics, gross-margin math, churn-prevention triggers, next-tier upsell pitch |
| [`BUYER_PERSONA.md`](./BUYER_PERSONA.md) | Sarah Chen - Director of ESG Reporting at an F500. What she owns, what keeps her up at night, what makes her click Subscribe |
| [`SUBMISSION_NOTES.md`](./SUBMISSION_NOTES.md) | The submission path, readiness checklist, planned producer-portal steps, risk + mitigation table |
| [`marketplace-preview.html`](./marketplace-preview.html) | A pixel-honest mockup of what the listing page will look like once submitted. Open in a browser to inspect |
| `screenshots/` | Listing media (filled D17 before final submission) |

## Why this matters for the hackathon

Track 3 of the GFS AI Agents Challenge is literally titled "Refactor for Marketplace + Gemini Enterprise." The Marketplace artifact is the single largest scoring delta available on the Business Case axis (30% of total score). Without it the rubric scores us ~20/30 instead of the target ~28/30.

The Marketplace SKU is also the actual GTM moat for GUARDIAN post-hackathon: F500 sustainability officers procure through their existing GCP committed-spend agreement, not through new POs. Marketplace removes the procurement bottleneck.

## What it does NOT do

This folder does not contain a fully approved + live Marketplace listing. Google's listing review is ≥6 weeks for first-time ISVs. What it contains is the **submission package** - everything a Google reviewer would need to approve the listing, plus the producer-portal submission attempt evidence we'll capture on D17-D18.

For hackathon judging, this is sufficient: the rubric scores understanding of the SKU motion, not Google's rubber stamp.

## Status timeline

| Date | Milestone |
|---|---|
| 2026-05-15 | Listing artifacts drafted (this commit). Codex adversarial pass scheduled. |
| 2026-05-31 (D17) | Open Producer Portal, paste listing copy, configure pricing, submit for Google review. Capture receipt screenshot. |
| 2026-06-01 (D18) | Producer Portal SUBMITTED state. Add submission-receipt.png to `screenshots/`. Update `SUBMISSION_NOTES.md` with timestamp. |
| 2026-06-05 (D22) | Hackathon submission. Marketplace folder + receipt screenshot are part of the deliverable. |
| Post-hackathon | Address whatever Google reviewer flags. Approval typically lands ~6 weeks after submission. |
