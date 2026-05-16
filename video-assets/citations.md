# GUARDIAN v2 video — claim citations

Source-of-truth for every on-screen number and quote. Fact-checked 2026-05-16.

---

## ✅ CONFIRMED — use as-is in V2 cut

### 1. TNFD adopter base (the hook)

**Claim on screen:** *"733 companies. $22 trillion in assets under management. Committed to TNFD biodiversity disclosure."*

**Source:** TNFD official adopter dashboard.
- URL: https://tnfd.global/engage/tnfd-adopters/
- As of: November 2025 — 733 organizations across 56 countries; 179 financial institutions representing ~$22.4T AUM and ~$9T market cap.
- 46% growth since COP16 (Nov 2024).

**On-screen footnote:** `tnfd.global/engage/tnfd-adopters`

### 2. EU CSRD / ESRS E4 biodiversity disclosure

**Claim on screen:** *"The EU's CSRD makes biodiversity disclosure mandatory under ESRS E4. Wave-1 large companies report from FY 2025."*

**Source:** European Commission + EFRAG.
- URL: https://finance.ec.europa.eu/financial-markets/company-reporting-and-auditing/company-reporting/corporate-sustainability-reporting_en
- Scope: ~49,000 large EU companies + non-EU with significant EU presence under Omnibus I (Dec 2025 amendment: 1,000+ employees, €450M+ turnover).
- ESRS E4 = topical standard for biodiversity & ecosystems; reporting required where material; Wave-1 quick-fix defers full E4 to FY 2025/FY 2026.

**On-screen footnote:** `EU CSRD · ESRS E4`

**REPHRASE NOTE:** Drop "Fortune 500" specifically — the directive applies to companies meeting size thresholds. Many F500 are caught but the framing is "large companies operating in the EU," not "Fortune 500."

### 3. Nature-economy materiality (the business-case number)

**Claim on screen:** *"$58 trillion — 55% of global GDP — is moderately or highly dependent on nature."*

**Source:** PwC 2023 update of WEF 2020 study.
- URL: https://www.pwc.com/gx/en/news-room/press-releases/2023/pwcboosts-global-nature-and-biodiversity-capabilities.html
- Original WEF: https://www.weforum.org/press/2020/01/half-of-world-s-gdp-moderately-or-highly-dependent-on-nature-says-new-report/

**On-screen footnote:** `PwC · WEF`

### 4. KPMG biodiversity-reporting gap

**Claim on screen (text-only quote, no cover image):** *"Three-quarters of the world's largest companies at risk from biodiversity loss don't report it."* — KPMG

**Source:** KPMG Survey of Sustainability Reporting (2020 + 2022 update).
- URL: https://www.sustainability-reports.com/over-three-quarters-of-worlds-largest-companies-do-not-report-risks-from-biodiversity-loss-kpmg-survey/
- Underlying KPMG report (2022): https://kpmg.com/xx/en/our-insights/esg/survey-of-sustainability-reporting-2022/biodiversity.html
- 2020 finding: 23% of at-risk companies disclose biodiversity risk → 77% do not.
- 2024 update: ~49% of large enterprises now disclose (doubled vs 2020 — but still half don't).

**On-screen footnote:** `KPMG Survey of Sustainability Reporting · biodiversity chapter`

---

## ❌ REJECTED — DO NOT USE

### "$300 billion biodiversity reporting market"
**Why rejected:** Not sourceable. Biodiversity *credit* market is much smaller (~$8.8B in 2026 high-end per Grand View Research, $3.46B low-end per other analyses). Biodiversity *finance gap* is ~$700B/yr per UN/TNC but that's the spending shortfall, not the "reporting market."

**Replacement:** Use the $58T nature-dependent-GDP number (PwC 2023, see §3) — bigger, more defensible, and reframes the buyer's stakes.

### "EU CSRD requires biodiversity disclosure from every Fortune 500 starting 2025"
**Why rejected:** Overclaim. CSRD applies to size-threshold companies, not specifically the Fortune 500. Wave-1 reports cover FY 2024; ESRS E4 itself can be deferred to FY 2025/FY 2026.

**Replacement:** Use precise CSRD/ESRS E4 framing (see §2).

### "Most can't even prove they have the data"
**Why rejected:** Not a sourceable verbatim KPMG quote. The actual KPMG finding is a percentage, not a memorable epigram.

**Replacement:** Use the 77% / "three quarters don't report it" wording with KPMG attribution (see §4). This is the actual KPMG finding, more defensible than a paraphrased epigram.

---

## On-screen tagline / claim register

| Beat | Final wording | Citation footnote |
|---|---|---|
| 0:10–0:18 Hook stat | *"733 companies. $22 trillion in assets. Committed to TNFD biodiversity disclosure."* | `tnfd.global/engage/tnfd-adopters` |
| 0:18–0:25 KPMG quote | *"Three quarters of the world's largest at-risk companies still don't report biodiversity loss."* — KPMG | `KPMG Survey of Sustainability Reporting · 2022` |
| 2:25–2:50 Business case | *"$58 trillion of global GDP depends on nature."* + *"EU's CSRD mandates biodiversity disclosure under ESRS E4."* + *"GUARDIAN ships on Google Cloud Marketplace."* | `PwC 2023 · EU CSRD · ESRS E4` |

All other on-screen IDs (TNFD-2026-A0192B2A32, PSR-9737, etc.) are reproducible from `POST /demo/run/multimodal_pipeline` against the live Cloud Run service.
