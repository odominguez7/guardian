# GUARDIAN - Pricing Model

_How we price, why we price this way, and the per-line math._

---

## The three SKUs

| SKU | Annual price | Reserves | Incident allotment | Headcount profile | Support |
|---|---|---|---|---|---|
| **Core** | $60,000 | 1 | 10,000 incidents/yr | 1 sustainability analyst + park ops contact | Standard |
| **Portfolio** | $180,000 | up to 5 | 50,000 incidents/yr | Sustainability team + dedicated TAM | Priority |
| **Enterprise** | from $300,000 | unlimited | from 100,000/yr | Sustainability office + named CSM | Premier |

Overage: $2.50 per incident above plan. Soft cap at 1.5× plan; hard cap forces a sales conversation.

Free trial: 30 days on a single reserve, capped at 500 incidents. Bills land on the customer's Google Cloud invoice; auto-applies committed-spend if present.

---

## Pricing rationale - three frames

### Frame 1: Cost-of-non-compliance avoided

EU Corporate Sustainability Reporting Directive (CSRD) enforcement runs through member-state administrative sanctions and public enforcement - Germany's *Bilanzkontrollverfahren* and France's AMF financial-reporting reviews are early bellwethers. Penalty levels vary by jurisdiction but the reputational cost of a public enforcement action far exceeds the fine. For a $50B revenue F500, a single missed CSRD disclosure cycle that triggers a national-level public enforcement notice is a hundreds-of-millions reputation event. GUARDIAN Portfolio at $180K/yr is a rounding error on the compliance line item. CSRD-audit defense reads to a Big Four (Deloitte, PwC, EY, KPMG) auditor as a structured chain-of-custody packet, not as ad-hoc spreadsheets.

### Frame 2: Cost of the human-only alternative

A single full-time ESG-data analyst at a F500 sustainability office costs **$140K-$220K loaded**. Producing audit-grade incident-level biodiversity disclosures by hand requires at least one such analyst per portfolio of reserves, plus park-ops contact-hours, plus consultant audit prep. GUARDIAN Portfolio replaces ~1.5 FTEs of that workflow at less than the cost of the cheapest analyst.

### Frame 3: Cost of a missed poaching incident

Illegal-wildlife-trade markets value a poached elephant tusk pair or rhino horn at multiples of GUARDIAN's annual subscription price (public TRAFFIC + Convention on International Trade in Endangered Species (CITES) standing-committee reports across 2018-2024 routinely cite five-to-six-figure per-incident street values; specific number ranges shift year over year). Beyond the trafficked value: the reserve loses the animal, the funder loses a portfolio-grade asset, and the sponsor loses the CSRD compliance evidence the dead animal would have produced. Stopping one critically endangered poaching event a year pays for the Enterprise tier outright.

---

## Why three tiers, not five

Three SKUs match Marketplace's natural buyer-segment map:

- **Core** - single-reserve sustainability program at a mid-cap or a regional F500. The "we sponsor one reserve" buyer.
- **Portfolio** - F500 with a published biodiversity portfolio (e.g. AB InBev sponsors several African reserves; Tiffany funds elephant corridors). The CSRD-priority buyer.
- **Enterprise** - global F500 with a sponsored-reserves count in the double digits AND a binding SOC 2 / supplier-security review. The "needs the SOC 2 evidence pack" buyer.

Two tiers is too few (Enterprise customers always ask for a middle). Five tiers is too many (forces every prospect into a competitive sales matrix). Three matches the actual buyer segments.

---

## What's NOT priced as a separate SKU

Deliberately bundled to remove friction:

- **All 4 A2A peers** - Park Authority, Sponsor Sustainability, Funder Reporter, Neighbor Park - are part of every tier. The Track 3 narrative requires the 4-peer story; gating peers behind tiers fragments it.
- **Taskforce on Nature-related Financial Disclosures (TNFD) report generation** - included. Not a pay-per-report line item. CSRD officers do not want metered output.
- **Vertex AI Search corpus seeding** - included. The IUCN Red List + CITES + reserve playbook corpus is part of the SKU.
- **Audit-prep review** - Portfolio and Enterprise customers get it included quarterly. Core does not (those buyers don't have an external audit yet).

What IS metered:

- **Incidents over plan** - $2.50 per incident. Reflects real Vertex AI + Cloud Run cost per fanout (estimated $0.18/incident at scale, with margin).
- **Custom A2A peer onboarding** - quoted per peer. Bringing a fifth peer (e.g. an insurance carrier's underwriting agent) onto the protocol requires schema + IAM work.

---

## How the customer pays

Three paths, in order of GTM preference:

1. **Google Cloud Marketplace Subscription billing** - clicks "Subscribe", bill lands on existing GCP invoice, draws against committed spend. Fastest path. Default.
2. **Annual invoice via partner** - for customers whose procurement won't approve Marketplace billing yet. We invoice directly, NET 60.
3. **Enterprise master agreement** - multi-year commit, paper.

Pricing is FX-stable: quoted in USD; non-USD invoices priced via Google Cloud's daily FX rate.

---

## Discounts

- **Multi-year prepay:** 15% off for 24-month, 25% off for 36-month
- **Multi-reserve volume:** Portfolio tier already gets 33% per-reserve discount vs 5× Core
- **Conservation funder co-purchase:** if both the F500 sponsor AND a conservation funder (wildlife NGO or philanthropic program — e.g., WWF / IUCN / IFAW; examples only, not canonical) buy GUARDIAN for the same reserve, each pays 80% of list (= 160% of list combined revenue; 60% premium vs single-buyer list, signals trust-asymmetric ecosystem buy)
- **Pre-paid in committed GCP spend:** no incremental discount but billing lands clean

---

## What we will NOT discount

- **Below $40K/yr on Core** - below that, the unit economics turn negative once a single TAM call gets booked.
- **Per-incident below $2.00** - that's the Vertex AI + Cloud Run cost floor with no margin.
- **A2A peer count "à la carte"** - the 4-peer story is the product. Stripping peers strips the story.

---

## Hidden floor

The smallest plausible deal we will close is **Core $60K**. Anything below requires the buyer to be a strategic logo win (e.g. a foundation we want quoted in the customer-success list). Discounting Core below $40K destroys reference value.
