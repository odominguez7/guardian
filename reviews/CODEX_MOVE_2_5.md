# Codex Handshake — Move 2.5 (Stakeholder lingo alignment)

_Per PLAN_V3.md §4.5. Run 2026-05-17._

## What Move 2.5 shipped

Stakeholder lingo alignment sweep applied across the repo, sourced from `guardian_stakeholder_reframing_2026.md` (saved as `docs/stakeholder_lingo_2026.md`). Producer accepted 3 of Claude's pushbacks at the outset:
- Big Four stays abbreviated (initially)
- Cards / on-screen UI stay tight
- `[cite:NN]` markers treated as decorative

## Codex Pass 1 — VERDICT: BLOCK

**P0 (4):**
1. `PLAN.md:93` named "Corporate Sustainability Agent" — regression vs canonical "Sponsor Sustainability agent"
2. `README.md:42,45,47` SHA-256 / ESRS E4 / CITES not spelled out on first mention
3. `marketplace/LISTING.md:12,18,117` acronyms appeared before any spell-out
4. `marketplace/PRICING.md` never spelled out CSRD / TNFD / CITES anywhere

**Codex pushback on Claude's pushbacks:**
- "Big Four abbreviated" → push-back-now (spelling out 4 firms once in customer-facing copy adds audit credibility)
- "Cards stay tight" → agree
- "Cite tags decorative" → push-back-now (looks like unresolved research refs; remove or supply mapping)

## Fixes applied (commits 30f92c7 + a020fa2)

- Renamed `Corporate Sustainability Agent` → `Sponsor Sustainability Agent` in PLAN.md
- Spelled out SHA-256 / ESRS E4 / CITES / MIKE on first mention in README build-status rows
- Spelled out TNFD + CSRD in LISTING tagline; SHA-256 in security section
- Spelled out CSRD in PRICING Frame 1, CITES in Frame 3, TNFD in bundling section
- **Accepted codex pushback:** Big Four expanded to "Deloitte, PwC, EY, KPMG" ONCE in PRICING Frame 1 (the audit-credibility moment)
- **Accepted codex pushback:** stripped all `[cite:NN]` markers from `docs/stakeholder_lingo_2026.md`; added header note explaining cleanup + conflict-resolution rule (stakeholders.md wins on naming; lingo doc wins on audience-voice)
- **Held:** cards stay tight per producer call (codex agreed)

## Codex Pass 2 — VERDICT: CLEAR

> "Move 3 (Board-ready slide auto-export from the Sponsor Sustainability agent) is greenlit."

No P0 / P1 / P2 remaining.

## Move 2.5 wraps. Move 3 starts.
