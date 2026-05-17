# GUARDIAN — Execution Plan v3 (locked 2026-05-17)

_Supersedes PLAN.md §8 schedule + reviews/V2_PLAN.md §12.4 execution order. Both retained for historical context. v3 is the live source of truth from 2026-05-17 forward._

---

## §1 — Decision context

**Trigger:** Specialist-panel reset 2026-05-17. After auditing the actual filesystem (not the narrative in prior reviews), Omar locked the following targets:

| Target | Value | Source |
|---|---|---|
| Objective rubric score | **95-97/100** | Producer call after specialist convergence + codex challenge |
| Universal-clarity audience set | **F500 buyer + Google judges + any non-technical human** | Producer call |
| Submission deadline | 2026-06-05 5pm PT | Devpost rules §4 |
| Effort budget for remaining moves | **~14 CC hours over ~19 calendar days** | Producer call (8x buffer vs estimate) |

**What we are NOT optimizing for:** "Probability of winning" as a quotable number. See [[feedback_no_unsourced_probabilities]] — hackathon outcomes have a luck floor we can't engineer out. We optimize controllable rubric performance.

---

## §2 — Stakeholder map (canonical names)

Source of truth: `docs/stakeholders.md` (the agent ↔ stakeholder map) **plus** `docs/stakeholder_lingo_2026.md` (the demo-voice lingo rules — first-mention acronym spell-outs, "no WWF/IUCN as canonical," Google tooling terms kept verbatim). Every demo card / VO line / Marketplace copy / README must use these names verbatim. Acronyms (TNFD, CSRD, ESRS E4, IUCN, CITES, SHA-256, Big Four) get a first-mention spell-out in prose docs and audio VO; on-screen card text stays tight (cards are space-constrained).

- **F500 sustainability buyer** (Ring 1 — customer / who pays)
- **Park Authority** + **Park Service** agent (Ring 2 — operator)
- **Funder Reporter** (Ring 2 — operator)
- **Neighbor Park** (Ring 2 — operator)
- **Sponsor Sustainability** (the A2A peer that files TNFD for the F500 buyer)
- **Falsifier** (the adversarial / dissenting agent — new in v3)
- **GUARDIAN** the system; **"GuardIAn Wildlife"** only in producer credit close card

---

## §3 — Six-move execution plan

Sequence chosen so each move is independently shippable, and Move 0 unblocks visibility of all subsequent moves on the live URL.

### Move 0 — Live site truth: Mapbox + Firebase + Auto-Cycle Demo Mode

**Why first:** A judge clicking the public Ops Center URL right now sees an empty map placeholder and a static page. Everything we ship after this is invisible to that judge until Move 0 lands.

| Sub | What | Files |
|---|---|---|
| 0.1 | Source env vars from `ops-center/.env.local` and run `make deploy-ops-center` with proper `--substitutions` (Mapbox token + Firebase config) | Makefile (already supports env vars; just need them in shell) |
| 0.2 | "Auto-Cycle Demo" toggle in Toolbar: when idle 10s, automatically cycle through the 4 scenarios with 30s spacing. Stops on any user click. | `ops-center/src/components/Toolbar.tsx`, `ops-center/src/app/page.tsx` |
| 0.3 | Add a discreet "AUTO DEMO" badge near scenario buttons when cycle mode is on, so judges know it's intentional | `Toolbar.tsx` |

**Effort:** 45 min (30 code + 3 deploy + 12 verify)
**Success criteria:**
- Visiting the public URL shows Mapbox-rendered Africa map within 2 seconds
- Sign-in button visible (Firebase configured) instead of any banner
- After 10s idle, scenarios begin cycling automatically
- Auto-Cycle badge visible during cycle mode
**Audience lift:** Universal (page becomes a living demo); Google judges (Mapbox + Firebase prove production-ready); F500 (sees the live evidence flow without needing to interact)
**Risk:** Low. Backward compatible. Existing scenarios untouched.

### Move 1 — Falsifier adversarial agent

**Why:** Innovation 16→19 lift. Two independent specialists (architect + codex) converged on this. F500 audit trail requirement + Google ADK team novelty + universal-human "AI argues with itself" legibility.

| Sub | What | Files |
|---|---|---|
| 1.1 | New ADK LlmAgent on Gemini 2.5 Flash. Hostile-auditor instruction. Returns `{verdict: concur|dissent|abstain, dissent_reason, severity_0_5}`. 2s hard timeout, fallback = concur. | `app/agents/falsifier.py` (new), `app/agents/__init__.py` |
| 1.2 | Wire orchestrator: call falsifier before dispatch fan-out. Attach verdict to incident state in Firestore. | `app/agent.py`, `app/tools/peer_orchestrator.py` |
| 1.3 | Court-Evidence bundle gets `adversarial_review` block (verdict + reason + severity) | `app/tools/court_evidence.py` |
| 1.4 | Sponsor Sustainability TNFD filing gets `adversarial_review_passed: bool` field — judges and Big-4 auditors both see it | `peers/sponsor_sustainability/agent.py` |
| 1.5 | DISSENT chip on Ops Center IncidentPanel (red when severity ≥3, yellow when <3 with abstain) | `ops-center/src/components/IncidentPanel.tsx` |
| 1.6 | Firehose emits `falsifier.verdict` events on the WebSocket | `app/fast_api_app.py` (firehose emit) |
| 1.7 | 4 ADK eval trajectories: concur-strong, dissent-weak-audio, dissent-species-mismatch, timeout-fallback. Plus 3 unit tests for the falsifier function. | `tests/eval/falsifier_*.json` (4 new), `tests/unit/test_falsifier.py` (new) |

**Effort:** 4 hr
**Success criteria:**
- Calling `/demo/run/multimodal_pipeline` produces an `adversarial_review` block in the response
- All 4 eval trajectories pass on a single `adk eval` invocation
- Unit tests pass (3/3)
- Live Ops Center shows DISSENT chip on at least one pre-seeded scenario
- Court-Evidence bundle includes the dissent record
**Audience lift:** Google judges (novelty: adversarial multi-agent is barely shipped elsewhere in 2026); F500 (auditable dissent record satisfies Big-4 chain-of-custody requirements); any human ("we don't trust our AI; we have another AI argue with it")
**Risk:** Medium. Adds 1-2s to dispatch latency. Mitigated by timeout + parallel execution path.

### Move 2 — GCP suite taste pass (Lyria + Imagen + Veo)

**Why:** Demo 16→17.7 lift via universal-human "this person has taste" reaction. Uses Google's own generative suite (Track 3 stack-max bonus). Replaces third-party stock assets (Pexels) with licensable, GCP-rendered originals.

| Sub | What | Files |
|---|---|---|
| 2.1 | Lyria 2 (Vertex AI Music) — generate one 60s ambient drone bed. Loop in Ops Center on page load at -28 dBFS. Also use as the demo video's music bed (solves codex P1 #3). | `scripts/assets/generate-lyria-bed.py` (new), `video-assets/music/guardian-ambient-60s.mp3` (output), `ops-center/src/app/page.tsx` (audio loop) |
| 2.2 | Imagen 4 — generate 9 cinematic agent-portrait avatars (5 orchestrator-side agents + 4 peers). Style brief: "NASA mission control meets Studio Ghibli — silhouette, single accent color per agent, dark background, 256x256." Replace emoji glyphs in cards. | `scripts/assets/generate-imagen-portraits.py` (new), `ops-center/public/portraits/*.png` (9 outputs), `ops-center/src/components/IncidentPanel.tsx` + `EventStream.tsx` (use portraits) |
| 2.3 | Veo 3.1 Fast — generate one 6-second cinematic hero loop: "African elephant herd at dusk near a camera trap, drone descent shot, no people, no logos, photoreal, 1920x1080." Place in idle Ops Center hero panel. Also slot in as cold-open replacement in the demo video. | `scripts/assets/generate-veo-hero.py` (new), `video-assets/broll/guardian-hero-6s.mp4` (output), `ops-center/src/app/page.tsx` (loop in hero) |

**Cost:** Lyria $0.06 + Imagen 9×$0.04 ≈ $0.36 + Veo $0.40 ≈ $0.82 total. Well inside §7 budget.
**Effort:** 3 hr (mostly compute wait time, can run in background)
**Success criteria:**
- Lyria MP3 plays at page load with fade-in, fade-out on tab blur
- All 9 Imagen portraits render in IncidentPanel + EventStream within 100ms (preloaded)
- Veo MP4 loops in Ops Center hero panel without judder
- Demo video v2.1 incorporates Lyria + Veo cold-open
**Audience lift:** Any human (production cinema feel); Google judges (Track 3 stack-max bonus: Lyria + Imagen + Veo are all named in the GCP generative-AI catalog); F500 (page feels enterprise-budget, not student-hackathon)
**Risk:** Medium. Veo generation can take 8-15 min and occasionally fails. Mitigation: pre-render today, have Pexels backup as fallback. Imagen API rate limits handled via 200ms throttle.

### Move 3 — Board-ready slide auto-export from Sponsor Sustainability

**Why:** Business Case 28→30 lift. This was Maya CSO's #1 ask in the specialist panel: every F500 CSO is 3 weeks late on their next board pack. If GUARDIAN's Sponsor Sustainability agent generates the artifact that goes on slide 14, you've moved from "interesting tool" to "you saved my Q2."

| Sub | What | Files |
|---|---|---|
| 3.1 | New tool on Sponsor Sustainability peer: `generate_board_slide(filing_id) -> png_url`. Renders a 16:9 PNG via HTML→Image pipeline. KPI tiles: elephants protected, hectares monitored, A2A-confirmed filings, audit hash. Footer: next board meeting date + filing reference. Top: F500-brand-neutral header "Q2 Biodiversity Material Risk — Selous Sponsorship". | `peers/sponsor_sustainability/board_slide.py` (new), `peers/sponsor_sustainability/templates/board-slide.html` (new) |
| 3.2 | Sponsor peer returns `board_slide_url` in TNFD filing response | `peers/sponsor_sustainability/agent.py` |
| 3.3 | Ops Center surfaces a "📋 Download board slide" button in the Sponsor ack card | `ops-center/src/components/IncidentPanel.tsx` |
| 3.4 | Demo video gets a 10s beat at 1:00-1:10: cursor clicks "Download board slide" → opens PNG → drags into Google Slides | `scripts/video/segments.json` (new beat in `07b-board-slide`) |

**Effort:** 3 hr
**Success criteria:**
- POSTing to `/demo/run/multimodal_pipeline` returns a `board_slide_url` in the sponsor section
- Clicking the URL serves a 16:9 PNG with the actual incident's KPIs interpolated
- Demo video shows the drag-into-Slides moment
**Audience lift:** F500 buyer (instant "I want to pilot this" trigger); any human ("the AI made my board slide for me"); Google judges (concrete enterprise artifact)
**Risk:** Low. HTML-to-PNG rendering well-trodden (Puppeteer / Playwright).

### Move 4 — Music final mix + Telemetric HUD overlay in demo video

**Why:** Demo 17.7→19 lift. Closes the designer's top-2 visual moves (telemetric burn-in + music polish) without re-recording. Both apply to existing footage.

| Sub | What | Files |
|---|---|---|
| 4.1 | Compose Lyria bed (from Move 2.1) into demo video at -28 dBFS under VO. Fade-in 3s at 0:00, fade-out 2s at 2:55. | `scripts/video/assemble-video-v2.sh` (music layer) |
| 4.2 | Telemetric HUD overlay on demo beat 0:30-1:20: top-right corner, monospace 16pt, format `gemini-2.5-pro · 0.93 conf · 720ms · 1,247 tok · vertex-rag/iucn`. Real numbers pulled from a captured Cloud Trace export. | `scripts/video/segments.json` (overlay spec in 05/06/07/08), `scripts/video/render-overlay.mjs` (extend) |
| 4.3 | Re-render v2.1 final MP4 with both layers | `scripts/video/assemble-video-v2.sh` |

**Effort:** 1.5 hr
**Success criteria:**
- Final MP4 has music bed continuously under VO at -28 dBFS measured
- HUD overlay visible at all 4 demo sub-beats with real telemetry values
- Runtime stays ≤3:00
**Audience lift:** Any human (cinematic production feel); Google judges (telemetry on-screen signals "this team has observability"); F500 (legibility — the system has real numbers)
**Risk:** Low. Layer addition to existing ffmpeg pipeline.

### Move 5 — Lean-in test + codex sweep + Devpost submit

| Sub | What | Files |
|---|---|---|
| 5.1 | Stranger lean-in test (3 non-technical humans, first 25s of v2.1 final). Pass condition: 3/3 say "I'd watch the rest" AND 3/3 can articulate what GUARDIAN does in plain words. | (manual, Omar runs) |
| 5.2 | One final codex slop-detection sweep on v2.1 final cut + script. Fix only catastrophic issues (per §12.5 hard freeze). | `reviews/CODEX_V2_1_FINAL.md` (output) |
| 5.3 | README walkthrough updated. Architecture diagram updated to include Falsifier. Marketplace listing updated with audit-mode bullet. | `README.md`, `docs/architecture.md`, `marketplace/listing.md` |
| 5.4 | Omar uploads to Devpost: video, code link, architecture diagram, live URL, test login | (manual, Omar) |

**Effort:** 2 hr CC + Omar's submission time
**Success criteria:** Submission accepted on Devpost before 2026-06-05 5pm PT

---

## §4 — Hard scope freeze (these are NOT in scope, even if tempting)

- Pattern Agent + Memory Bank (D6 in original PLAN)
- ParallelAgent refactor (D16)
- Looker Studio dashboard (D17)
- `redteam_poacher` autonomous adversary service (codex Path-C overflow)
- O22-rendered video integrations beyond the GCP-suite Lyria/Imagen/Veo calls already in Move 2
- Additional A2A peers (#5, #6)
- Real Firebase Auth wiring beyond what Move 0 enables
- v3 demo video (only v2.1 reassembly is sanctioned)
- New on-screen claims not already in the v2 script

If any of these come up during execution: log to `TODOS.md` and move on.

---

## §4.5 — Codex handshake gate (locked 2026-05-17 by Omar)

**Every Move ends with a codex handshake review.** Next Move does not start until the current Move's codex handshake is CLEAR (or CLEAR-WITH-AMENDMENTS with amendments absorbed). This is non-negotiable.

Per-Move handshake protocol:

1. Execute the Move; commit each sub-step.
2. Run codex via:
   ```bash
   codex exec --sandbox read-only -m gpt-5-codex \
     --prompt "You are codex in adversarial review mode. The producer just completed Move N of PLAN_V3.md. Read the changed files. Verify the §3 Move N success criteria. List P0 (block next Move), P1 (strong-suggest), P2 (log only)."
   ```
3. Pipe codex's verdict to `reviews/CODEX_MOVE_N.md` for the audit trail.
4. If P0: fix inline, re-run codex, loop until clear.
5. Acceptance gate from §5 must also pass.
6. Only then: start next Move.

**The producer-visible phrase in chat:** "Move N is committed. Running codex handshake. Holding on Move N+1 until P0-clear."

**Why:** [[feedback_codex_handshake_per_move]] in memory. Codex's adversarial mode is the highest-coverage net for catching P0/P1 regressions, scope creep, and premature ship claims. Per [[feedback_codex_velocity]], codex sweeps add velocity, not just safety — ~10-20 min CC time per Move vs. hours of debug at submission.

---

## §5 — Acceptance tests (the gates)

Before each Move's commit, the corresponding gate must pass:

| Gate | Test |
|---|---|
| Live site truth | Mapbox + Firebase visible on public URL within 2s of load |
| Falsifier deployed | `curl /demo/run/multimodal_pipeline` returns `adversarial_review` block; 4 eval trajectories green |
| Lyria | Audio plays in Ops Center; same MP3 in video bed |
| Imagen | All 9 portraits load in IncidentPanel cards |
| Veo | 6s hero loop plays without judder in Ops Center + video |
| Board slide | Sponsor peer returns `board_slide_url`; PNG renders with real KPIs |
| Music + HUD | Final MP4 has music + HUD overlay; runtime ≤3:00 |
| Stranger test | 3/3 pass lean-in + articulate-what-it-does |
| Codex sweep | No new P0 in final review |
| Reproducibility | `python3 scripts/dev/verify_ids.py --runs 5` shows 5/5 stable |

---

## §6 — Live URLs (public, durable; will follow along with each move)

- **Ops Center (cinema surface):** https://guardian-ops-center-180171737110.us-central1.run.app
- **Orchestrator API + Swagger:** https://guardian-180171737110.us-central1.run.app/docs
- **A2A Agent Card:** https://guardian-180171737110.us-central1.run.app/a2a/app/.well-known/agent-card.json
- **GitHub:** https://github.com/odominguez7/guardian
- **Reproducibility check:** `python3 scripts/dev/verify_ids.py --runs 5`

Each commit during execution gets pushed to `origin/main`. Producer can follow `git log --oneline` for fast-paced progress visibility.

---

## §7 — Effort + schedule

Total: **~14 CC hours**, distributable across **19 calendar days**.

| Move | Effort | Cumulative | Calendar day target (if executed daily) |
|---|---|---|---|
| 0 — Live site | 0.75 hr | 0.75 | day 1 (today) |
| 1 — Falsifier | 4 hr | 4.75 | day 2-3 |
| 2 — Lyria + Imagen + Veo | 3 hr | 7.75 | day 4 |
| 3 — Board slide | 3 hr | 10.75 | day 5 |
| 4 — Music + HUD | 1.5 hr | 12.25 | day 6 |
| 5 — Lean-in + codex + submit | 2 hr | 14.25 | day 7 |

**Buffer:** ~12 days. Per [[feedback_codex_velocity]], reserved for codex challenge sweeps and any P0 fixes that surface.

---

## §8 — Source documents this plan supersedes / extends

- `PLAN.md` §8 — historical, the original 22-day schedule
- `reviews/V2_PLAN.md` — V2 cut planning; §12 retained as historical post-cut review
- `reviews/CEO_REVIEW_2026-05-16.md` — historical
- `reviews/CEO_REVIEW_2026-05-17.md` — context for this plan
- `docs/stakeholders.md` — name source of truth (this plan defers to it)

This plan v3 is the current execution truth. If it conflicts with any of the above, v3 wins.
