# Codex Handshake — Move 5 Final Sweep (Pre-Submission)

_Per PLAN_V3.md §4.5 + Move 5.2 (final codex slop-detection sweep). Run 2026-05-17._

## Scope

Final pre-submission sweep across the entire repo state before Omar uploads to Devpost. Codex was asked to find ANY P0/P1 credibility landmine that would embarrass the submission in front of Google judges, F500 sustainability buyers, Big Four audit teams, or any non-technical demo viewer.

## Codex Pass 1 — VERDICT: BLOCK

**P0 (1):**
- `README.md:13` agent roster listed "Pattern WIP" (cut from scope) and omitted Falsifier (shipped in Move 1) — first-summary-line misstatement.

**P1 (3):**
1. README live endpoints table left Funder + Neighbor as "live on Cloud Run" with no URL/revision; called the Park peer "Park Authority" instead of the canonical agent name "Park Service".
2. `docs/stakeholders.md:104` said "A2A protocol v0.2"; rest of repo + agent.json says v0.3.0.
3. `marketplace/LISTING.md:31` introduced "CITES-MIKE" without first-mention spell-out (violates the lingo canon).

**P2 (3):**
1. README status date "2026-05-16" stale (v3 pass closed 2026-05-17).
2. TODOS.md: planned `tests/eval/evalsets/falsifier.evalset.json` not present; needs explicit reminder note for future reviewers.
3. `marketplace/marketplace-preview.html:183` advertised "all 8 specialist agents"; actual is 5 specialist sub-agents + orchestrator + 4 A2A peers.

## Fixes applied (commit f03c18b)

- **P0:** Agent roster updated to "Orchestrator, Stream Watcher, Audio, Species ID, **Falsifier** (adversarial review), Court-Evidence". Pattern dropped.
- **P1 #1:** Live URL + revision filled in for Funder Reporter (`guardian-funder-reporter-180171737110...` / `00002-vfp`) and Neighbor Park (`guardian-neighbor-park-180171737110...` / `00002-nlg`). Park peer row renamed "Park Service".
- **P1 #2:** A2A version aligned to v0.3.0 in `docs/stakeholders.md` audience script.
- **P1 #3:** CITES-MIKE spelled out on first mention: "Convention on International Trade in Endangered Species — Monitoring the Illegal Killing of Elephants (CITES-MIKE)".
- **P2 #1:** README status stamp refreshed to 2026-05-17.
- **P2 #2:** TODOS.md reminder line added pointing to deferred ADK evalset.
- **P2 #3:** Marketplace preview HTML updated to "5 specialist sub-agents + adversarial audit mode".

## Codex Pass 2 — VERDICT: SHIP-READY

> "README status stamp and roster reflect 2026-05-17 plus the Falsifier addition; live endpoints table now carries the production Funder/Neighbor URLs with revisions and Park Service naming. Stakeholder protocol reference is synced to v0.3.0. P0: none outstanding. **Devpost submission is greenlit.**"

## Handoff

The remaining Move 5 work is producer-side:
- **5.1** — Stranger lean-in test (3 non-technical people, first 25s of `video-assets/output/guardian-demo-v2.mp4`). Pass: 3/3 say "I'd watch the rest" AND can articulate what GUARDIAN does in plain words.
- **5.4** — Devpost upload (video, code link, architecture, live URLs, test login).

Code-side work for the v3 pass is COMPLETE.
