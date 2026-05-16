# GUARDIAN - Buyer persona

_The single human who clicks "Subscribe" on the Marketplace listing. Everything in the product is built for her._

---

## Primary persona - Sarah Chen, Director of ESG Reporting

**Title:** Director of ESG Reporting & Biodiversity Disclosure
**Company:** Fortune 500 with publicly-stated Nature & Biodiversity commitments. Profile examples (illustrative, not endorsed): AB InBev (water-stewardship + biodiversity targets), Tiffany & Co (sourcing-region biodiversity programs), LVMH Beauty (LIFE 360 nature commitments), Unilever (Climate & Nature Fund), Heineken (Brewing a Better World), KPMG (advisory practice serving these buyers). Specific buyer firms validated through public commitment disclosures and proxy statements.
**Reports to:** Chief Sustainability Officer (member of the Executive Committee)
**Team size:** 4-8 (mix of analysts, framework specialists, external-auditor liaisons)
**Annual sustainability programs budget:** $4M-$25M (program spend, not ARR - this is annual budget, not recurring revenue)
**Located:** New York, London, Amsterdam, Munich, or Singapore HQ

---

## What Sarah owns

- The firm's annual TNFD-aligned disclosure (filed voluntarily as part of the firm's annual sustainability report; TNFD is a voluntary framework, but a growing universe of asset managers and audit committees treats it as table-stakes)
- The firm's CSRD ESRS-E4 biodiversity section if the firm is in scope. CSRD applies in phased waves: Wave 1 (large EU public-interest entities) reports starting FY 2024; Wave 2 (other large EU companies) FY 2025; Wave 3 (listed SMEs) FY 2026; Wave 4 (non-EU parents with significant EU revenue) FY 2028. Sarah's firm has at least one EU operating subsidiary in scope.
- The audit-prep workpapers her external auditor (Big 4) requires
- The sponsored-reserves portfolio review presented quarterly to the CSO + once-annually to the Audit Committee
- Vendor selection for the data, monitoring, and reporting tools that feed the above

---

## What keeps Sarah up at night (in priority order)

1. **"We have to file E4 but we cannot produce incident-level evidence."** Her firm sponsors three African reserves through a 5-year, $14M commitment. Under CSRD E4 she has to disclose material biodiversity impacts. Today she gets a PDF report from each reserve at year-end, written in narrative form. Her auditor wants line-item incidents with timestamps. She has no way to produce them. This is the open audit finding from her FY24 review.

2. **"My boss told the board we've reduced poaching incidents 38%."** She has no way to verify or falsify the 38% number. The reserves report it. The auditor is starting to ask.

3. **"The activists are watching."** A failed biodiversity disclosure or a single missed elephant-poaching incident on a sponsored reserve trends on social media within 48 hours. The reputational cost of one bad incident outweighs the entire compliance budget.

4. **"Procurement won't approve another niche SaaS."** Sarah has tried two startup biodiversity-data vendors. Both stalled in security review. She needs a tool that lives inside her existing GCP commit so security review takes weeks not quarters.

5. **"I cannot hire two more analysts."** Her CSO has frozen sustainability headcount. Anything new has to be tooling, not FTE.

---

## What Sarah is NOT

- Not the buyer of "anti-poaching technology." That's a Park Authority or a conservation NGO buyer. They have no money.
- Not a biodiversity scientist. She speaks audit language, not species-conservation language.
- Not a Cloud architect. But she has a Cloud architect on her IT side who reviews the deployment.
- Not a procurement officer. But she works with one named procurement contact who can fast-track Marketplace SKUs.

---

## What Sarah has already tried

- **A boutique biodiversity-data consultancy** ($180K/year) - produced PDF narrative reports. Failed the FY24 audit's "where's the incident-level evidence?" question.
- **Two startup biodiversity SaaS tools** - both stalled in vendor security review. One was acquihired before completing the review.
- **An NGO partnership** (~free) - produced narrative content for the annual report but no audit-grade structured data.
- **An internal initiative** to build a custom tool - killed at quarter 2 after the engineering team estimated 18 months and $4M.

She is fatigued. She will close the next vendor demo that **shows incident-level data flowing live, in production, with the right framework tags applied automatically**.

---

## What makes Sarah click "Subscribe"

1. **The TNFD-aligned filing receipt visible on screen.** Not "we generate TNFD reports" - actual `filing_id: TNFD-2026-XXXXX` rendered in the live ops dashboard, with the schema mapping the TNFD-published taxonomy. This is what her external auditor would call "in scope."

2. **The CSRD ESRS-E4 framework reference baked into the response.** Her firm has to map every disclosure to an ESRS data point. Seeing GUARDIAN's response include `compliance_frameworks: ["TNFD", "CSRD-ESRS-E4"]` removes the most expensive step of her workflow.

3. **Cloud Run + Vertex AI deployment.** She can answer the procurement question "where does this run" with one sentence: "Our existing GCP project." Vendor security review collapses from 6 months to 6 weeks.

4. **The 4-peer A2A coordination shown live.** This proves the system is built for the real multi-org reality of conservation work - the host park, the funder, the sponsor, the neighbor. Single-DB vendors look naïve next to it.

5. **The price is in her existing budget.** $180K/year Portfolio comes out of her sustainability programs budget without requiring a board ask.

---

## How Sarah finds GUARDIAN

In rough order of GTM expected channel mix:

1. **The Google Cloud Marketplace listing search** - when she types "biodiversity reporting" or "TNFD" into the Marketplace catalog. (Why this listing matters so much.)
2. **Her firm's Google Account Executive surfaces it** because their account is in GCP committed-spend conversations and the AE has been briefed.
3. **The annual Climate Week / VERGE / GreenBiz circuit** - where GUARDIAN sponsors a session on biodiversity disclosure tooling.
4. **Her existing CSO peer network** sharing a case study from the second reference customer.

---

## What Sarah would NEVER pay for

- A "biodiversity data lake" - she has one, it's broken, she does not want another.
- A consulting engagement labeled "biodiversity strategy" - done that, useless.
- Anything sold as "AI for nature" with no compliance-framework hook - sounds like a NGO grant proposal.

---

## How long Sarah takes to close

For the **first reference customer** (solo founder, pre-logo): typical 9-15 months from free trial to closed-won. Pilot-first motion: 3-6 month paid pilot ($25K-$40K) → reference + co-developed audit walkthrough → full Core or Portfolio contract.

For **customers 2 and 3** (citing the first as reference): typical 4-8 months.

For **customers 4+** (multiple logos, public case study): typical 3-6 months.

The right framing for GTM: do not promise a 3-month close on the first deal. Promise a 3-month paid pilot.

---

## Secondary persona (lurking, not primary)

**Marcus Okonkwo, Park Operations Director** at a conservation reserve. Cares about ranger SOPs, not regulatory disclosure. Comes into the GUARDIAN deployment after Sarah signs. Influences renewal and recommends GUARDIAN to peer parks. Not the buyer; the user.

We sell to Sarah. We deploy with Marcus. Never invert that order.
