# GUARDIAN v9 — CEO Plan: Hero Screen + Storytelling Reset

**Generated:** 2026-05-17 evening after v8 Day 14 ship.
**Mode:** SELECTIVE EXPANSION (hold v8 scope, redesign the demo surface).
**Codex protocol:** §4.5 handshake gate per work-stream — same as v4-v8.

---

## Premise challenge (Step 0A)

Producer reviewed the Ops Center after v8 Day 14 and said: *"the demo feels more like a recorded 'made-up' command center rather than showing Google's judges a real command center and agentic work using their protocols, architecture, and a real business model behind it."*

That critique is correct. The current Ops Center has 3 tabs (Operations / Live Cams / Mission Bridge) that judges visit sequentially; the agentic story plays inside Mission Bridge as portraits with text bubbles. The narrative is **scattered**: cams are real but separate from the agents reacting, the map is the visual center but doesn't show animals, and the Mission Bridge feels like a teaching diagram, not a live operations floor.

The v9 thesis: **one hero screen** where the real live cameras are the visual center, agents auto-watch them in real time with their Google protocol stack visible while they speak, the map is contextual (orbital), and every A2A peer has a distinct voice + role explanation + protocol callout. The screen has to feel like the agents are doing real work right now, not running a script.

## Existing-code leverage (Step 0B)

What we keep from v8:
- `/livecam/spot` endpoint, three-source pattern (image_url / mp4_url / youtube_id) — works
- `image_url` path via NPS public webcams + ffmpeg/yt-dlp fallback — works
- Honest escalation logic (IUCN hot-list + threat signals) — works
- 4-peer A2A fan-out with real Gemini responses — works
- Mission Bridge component as a TAB stays available for deep-dive
- All v8 docs (PROCUREMENT, LISTING, DEVPOST, ARCHITECTURE) — keep

What we replace:
- Operations tab + Live Cams tab → merge into single **Hero** view
- Mission Bridge tab → becomes a side-drawer triggered from Hero, not a full tab
- Static cam grid → expandable click-to-focus tiles
- Geographic map as center → context strip / minimap with slow rotation
- Generic NPS landscape cams → wildlife-rich sources (research below)

## Dream-state map (Step 0C)

```
NOW (v8 Day 14)                              v9 IDEAL (after this plan)
─────────────────                            ─────────────────────────
3 tabs · cams in tab 2 · agents in tab 3 ── one Hero · cams center · agents auto-react
Spot Now manual button                  ── auto-cycle every 30-60s
Generic photo-real portraits            ── role-specific: judge, robot, ranger uniforms
A2A peers same voice template           ── 4 distinct voices, each with protocol callout
Map = visual anchor                     ── Map = small orbital reference
NPS landscape cams (no animals)         ── wildlife-rich sources (research below)
Demo feels "recorded made-up"           ── "agents doing real work right now"
```

## Implementation approaches (Step 0C-bis, MANDATORY)

### Approach A — Minimal: improve in place (~3 hr)
Keep 3 tabs. Fix the 15 producer issues inside their current locations:
- Better portraits per agent role
- A2A peer voices + intros
- Protocol callouts as text badges
- Map 3D fix
- New wildlife cam sources
- Smaller Mission Bridge

**Pros:** low risk, no UX disruption.
**Cons:** doesn't address the producer's central "boring dashboard" critique — judges still tab-hop.
**Completeness: 5/10** (covers 12 of 15 issues, leaves narrative gap intact)

### Approach B (recommended) — Hero rebuild: single live-ops screen (~6-8 hr)
Rebuild the main view as one cinematic operations floor:
- **Top 65%:** 2×2 grid of expandable real wildlife cams (click to fullscreen)
- **Bottom 20%:** narration strip — protocol-aware running ticker ("[A2A v0.3] Park Service ack · ranger PSR-2205 dispatched")
- **Right 15% side rail:** mini-map rotating slowly + active agent portrait + 4-peer ack chips
- **Drawer:** Mission Bridge moves to a slide-out panel for the deep-dive view
- Auto-cycle: agents auto-fire Spot Now on the most active cam every 30-60s
- 4 distinct A2A peer voices with role intros + protocol stack badges
- Better wildlife cam sources (research candidates below)

**Pros:** addresses every producer critique, single cohesive narrative, judges see "real" not "rehearsed."
**Cons:** higher refactor risk, biggest UX change in the v8 arc.
**Completeness: 9/10** (covers all 15 issues with one architectural pass)

### Approach C — Boil-the-lake (~12-16 hr)
B + new role-specific Imagen 4 portraits (court_evidence = federal judge in chambers, orchestrator = robotic conductor) + Veo 3.1 lip-sync clips for each agent's intro + WebSocket-driven LIVE protocol callouts pulled from the actual firehose (not canned).

**Pros:** maximum "wow"; protocol callouts become provably real because they're sourced from the WebSocket.
**Cons:** Veo cost ~$8-10, Imagen ~$0.40 + re-render time, and may regress if uncanny.
**Completeness: 10/10** but risks running out the v8 clock for the Day 8-11 video work.

**Recommendation: B.** Hits all 15 issues with one architectural pass, leaves Veo lip-sync as v10 stretch. C is the right answer ONLY if producer wants to delay the submission video; B is the right answer if the submission video lands on schedule.

## Mode selection (Step 0F)

**SELECTIVE EXPANSION.** Hold v8 ship-line; cherry-pick the hero rebuild + 3 supporting work streams. NOT a full v9 rewrite — every existing v8 deliverable stays canonical.

---

## Codex G0.2 absorption (2026-05-17 night)

Second-round verdict: HOLD with 3 BLOCKs + 3 WARNs. All real engineering, not formatting. Absorbed below.

**BLOCK A — W0 arithmetic impossible** [RESOLVED via real research + honest pivot]: W0 sprint executed 2026-05-17 night, ~1.5 hr budget consumed (initial 4-cam YouTube probe + producer pushback + non-YouTube probe + pivot). Report at `reviews/v9-cam-research.md`.

**Initial 4-YouTube plan was INVALIDATED by producer 2026-05-17 night**: *"for reference youtube blocks the bots you should know that"* — same v6/v7 bot-wall failure mode. Three direct probes of non-YouTube alternatives (Raptor Resource, Smithsonian Zoo, Monterey Bay Aquarium) showed every "real-wildlife" stream is either YouTube-under-the-hood or MSE-tokenized HLS that can't be embedded on a third-party origin.

**Honest hybrid model locked instead:**

| Tile | Source kind | Asset / URL | UI chip label |
|---|---|---|---|
| CAM-01 | NPS image | `https://www.nps.gov/.../webcam-current.jpg` (Old Faithful) | Live image · refresh 60s |
| CAM-02 | NPS image | `https://www.nps.gov/.../webcam-current.jpg` (Glacier) | Live image · refresh 60s |
| CAM-03 | Veo simulation | `ops-center/public/cams/tembe-sim.mp4` | AI-generated simulation · Veo 3.1 Fast |
| CAM-04 | Veo simulation | `ops-center/public/cams/manatee-sim.mp4` | AI-generated simulation · Veo 3.1 Fast |

Producer's "we MUST spot animals" requirement is **partially** met via the Veo simulation tiles — animals ARE spotted in the pattern-recognition sense, but the imagery is synthetic and the spotting transcript MUST disclose synthetic provenance ("AI-generated archival-style simulation, Tembe archetype"). No tile carries a fabricated capture date or third-party verification claim. The cam tiles become evidence layer with honest provenance audit; the agentic narrative is the hero. This is the F500-defensible posture: every tile labeled, sourced, falsifiable — including the synthetic ones.

**Residual gap** (producer issues #12 + #14 partially open): if a licensed real-wildlife clip can be sourced before submission (Pond5/Shutterstock at ~$25-50, or a research-use grant from Tembe / Save-The-Manatee Club), swap into CAM-03 or CAM-04 with proper attribution chip. Otherwise stay on the honest hybrid and lean on the agentic narrative.

**W0 = DONE.** W3 (cam wiring) ~30 min. NEW W3.5 (Veo render, 30-120 min producer-supervised, ~$1.00 Veo cost) prepended. G0.5 codex on the revised research report fires next.

**BLOCK B — Auto-cycle math wrong**: amended plan said "1 cam every 5 min = 48 calls/hr." Math: 60/5 = 12 spots/hr if rotating one-at-a-time across 4 cams. If "every 5 min" applies per-cam, it's 4 × 12 = 48/hr. Plan was ambiguous.

Resolution: **Exact intent locked in**: 1 spot total every 5 minutes (rotating round-robin through cams) = **12 spots/hr total**. Per-session/tab throttle: max 20 spots/hr globally (covers manual + auto). Pause on tab blur. SHA-skip if cam image unchanged. Multiple judge tabs do NOT multiply — server-side cooldown at `_LIVECAM_COOLDOWN_S=12s` already enforces. Sustainable on Gemini 2.5 Pro daily quota; confirms Day 14's 429 won't repeat.

**BLOCK C — Protocol-badge schema gap**: events.py emits `agent` + `tool` + opaque payload. No authoritative `model` or `protocol_stack` field. Frontend can't render `[Gemini 2.5 Pro · Vertex AI Vision]` from current schema.

Resolution: **W2 split into W2a (backend schema) + W2b (UI/voice polish)** with new **G2.5 gate** between them.
- **W2a — firehose contract extension** (~60 min): `events.emit()` signature gains optional `model: str | None = None` and `protocol_stack: list[str] | None = None`. Tool emission sites updated:
  - `stream_watcher.analyze_image_bytes`/`analyze_image_frame` → `model="gemini-2.5-flash"`, `protocol_stack=["Vertex AI Gemini Vision","Cloud Run"]`
  - `audio_agent.classify_audio` → `model="gemini-2.5-flash"`, `protocol_stack=["Vertex AI Gemini Audio","Cloud Run"]`
  - `species_id.lookup_species_factsheet` → `protocol_stack=["Vertex AI Search","Cloud Run"]`
  - `falsifier.review_dispatch` → `model="gemini-2.5-flash"`, `protocol_stack=["ADK 2.0 SequentialAgent","SOP Gates"]`
  - `court_evidence.bundle_incident` → `protocol_stack=["SHA-256","BigQuery"]`
  - `a2a_peers.notify_*` (all 4) → `protocol_stack=["A2A v0.3.0","Cloud Run","ID-token auth"]`
  - TypeScript types in `ops-center/src/types/events.ts` extended to match. Pydantic event types extended to match. G2.5 codex sweep on the schema diff.
- **W2b — UI consumes the new fields** (~75 min): Mission Bridge speech bubble + new NarrationStrip.tsx render the protocol chips from `event.protocol_stack` when an event matching the speaking agent fires. Static intro = idle fallback.

**WARN A — Drawer width 35-40%**: locked at `width: clamp(420px, 38vw, 560px)`.

**WARN B — Business-model on screen**: NarrationStrip gets a fixed first slot for the compliance pitch — rotates between three lines:
1. "Every incident here lands in a SHA-256 chain-of-custody bundle."
2. "Fortune 500 sustainability officers file CSRD-E4 + TNFD disclosures from this stream."
3. "Four enterprise organizations coordinate live over A2A v0.3."

These rotate every 8s. Live protocol badges from the firehose appear adjacent.

**WARN C — G2.5 gate added** (between W2a backend and W2b UI). Total gates now: G0/G0.5/G1/G2a-G2.5-G2b/G3/G5/G6 = 8.

## Codex G0 absorption (2026-05-17 evening)

Codex G0 returned HOLD with 2 BLOCKs + 4 WARNs + 3 NITs. Plan amended below.

**BLOCK 1 absorbed — W0 prepended (research SPRINT before W1) [DONE 2026-05-17 night]**: research SPRINT executed and CONCLUDED. Result: 4 YouTube wildlife cams initially "verified" via oembed, then rejected by producer ("youtube blocks the bots"), then 3 non-YouTube alternatives (Raptor Resource, Smithsonian, Monterey Bay) directly probed and found unusable (YouTube-under-hood / blob:MSE / lazy-JS-only). Honest hybrid locked: 2 NPS image + 2 Veo simulation (NOT "archival" — synthetic, with explicit AI-generated provenance chip). See `reviews/v9-cam-research.md` and BLOCK A above for the canonical record. G0.5 codex on the revised research report fires next.

**BLOCK 2 absorbed — auto-cycle cadence revised**: 30s × 4 cams was 480 calls/hr (Gemini 429 territory). New cadence: **1 cam every 5 minutes** = 12 calls/hr per cam = 48/hr total. Sustainable on quota. Producer-facing language: "agent-active rotation" so it doesn't sound constrained. Additional safeguards:
- Pause auto-cycle when the browser tab loses focus
- Hash-based gate: skip the cycle if the cam image SHA matches the prior cycle's SHA (no change means no new wildlife)
- Manual Spot Now button always works (no rate-limit for human-triggered)

**WARN 1 absorbed — W1 budget revised to 5-6 hr** (was 3). Total v9 budget moves from 9-12 hr to 12-16 hr. Still fits inside v8's Days 15-20 buffer.

**WARN 2 absorbed — protocol callouts are firehose-driven, not decoration**: W2 now requires Mission Bridge + the narration strip to subscribe to the WebSocket firehose and render protocol badges (`[A2A v0.3]`, `[Vertex AI Search]`, etc.) when actual events come through with that protocol's tag. Static-by-agent intros stay as the idle fallback. This makes the "live" beat REAL.

**WARN 3 absorbed — Mission Bridge drawer discoverability**: persistent right-edge tab on the hero view labeled "Agent Roster · 10 agents" with `Cmd+M` hotkey. Drawer auto-opens once on first-visit to onboard judges to the topology, then collapses.

**WARN 4 absorbed — dynamic protocol signaling promoted into scope**: this is exactly what producer's "feels recorded" critique was asking for. Now W2 ships REAL protocol signaling not decorative badges.

**NITs absorbed**: W2 budget bumped to 2 hr to cover review loops · G3/G4 paired (now G3 covers W3+W4 together since both are content work).

## Five work streams (v9 scope)

### W0 — Wildlife cam research SPRINT [DONE 2026-05-17 night, REVISED after producer pushback]
Executed in ~1.5 hr. Report at `reviews/v9-cam-research.md`. **Initial 4-YouTube plan rejected by producer ("youtube blocks the bots") + confirmed by direct probes of non-YouTube alternatives (Smithsonian = blob:MSE, Monterey = lazy-JS, Decorah = YouTube-under-hood).** Honest hybrid locked: 2 NPS image feeds + 2 Veo AI-generated simulation tiles, each with source-kind UI chip + VO synthetic-provenance disclosure. Agentic narrative becomes the hero; cams are evidence layer with honest provenance (consistent with Falsifier posture). G0.5 codex on the revised report fires next.

### W1 — Hero screen rebuild (~5-6 hr after W0 clears)
- New top-level layout in `ops-center/src/app/page.tsx`:
  - Replace 3-tab strip with: Hero (default) · Mission Bridge (drawer) · Library (current 3 tabs accessible from a menu)
  - 2×2 cam grid as visual center
  - Right side rail: minimap (slow rotation) + active-agent portrait + 4 peer ack chips
  - Bottom narration strip with protocol-aware ticker
- Auto-cycle agent-driven Spot Now: **1 cam every 5 minutes** (rotating through 4 cams = 1 spot per cam per 20 min). Pause on tab blur. SHA-skip if image hasn't changed since prior cycle. Manual Spot Now always honored. Sustainable on Gemini 2.5 Pro daily quota.
- Click any cam → fullscreen expand with overlay agent narration

### W2a — Firehose contract extension (~60 min, G2.5 before W2b)
See BLOCK C resolution in the absorption section. Add `model` + `protocol_stack` fields to events.emit + Pydantic event types + TypeScript types. Update 6 emission sites (vision, audio, species_id, falsifier, court_evidence, a2a_peers). G2.5 codex sweep verifies schema before W2b consumes it.

### W2b — A2A peer storytelling + LIVE protocol UI (~75 min, after G2.5)
- Each peer gets:
  - Distinct ElevenLabs voice (separate voice ID per peer)
  - Longer intro line (~12-18 words) explaining what the org does + which protocol it uses
- Mission Bridge speech bubble + new `NarrationStrip.tsx` subscribe to firehose, render protocol chips LIVE from `event.protocol_stack` when an event matching the speaking agent fires
- Static-by-agent intros = idle fallback only
- Generate 4 new voice clips via the existing ElevenLabs script

### W3 — Cam tile wiring + source-kind chips (~30 min wire only — W0 already picked the sources)
- Replace `CAMS` array in `ops-center/src/components/LiveCams.tsx` with the hybrid model (2 NPS image URLs + 2 Veo mp4 paths). Each entry carries an explicit `source_kind: "live_image" | "veo_simulation"` field — the second value accurately names the source as AI-generated, not archival, and not "verified."
- Add `<SourceKindChip>` component rendering `Live image · refresh 60s` (green dot) or `AI-generated simulation · Veo 3.1 Fast` (amber dot, with hover tooltip explaining synthetic provenance + the production-deployment swap-in plan).
- Update `/livecam/spot` endpoint to disclose source kind in the spotting transcript:
  - `live_image` tiles announce: "Spotting CAM-01, live federal NPS feed."
  - `veo_simulation` tiles announce: "Spotting CAM-03, AI-generated archival-style simulation, Tembe Elephant Park archetype. Note: this tile is a simulation; production deployment would swap for licensed reserve footage."
- The Falsifier audit chain extends to cam provenance: any spotting result includes `source_kind` + `provenance_note` fields in the BigQuery event log (NOT `verified_by` — we do not claim third-party verification for synthetic content).

### W3.5 — Veo wildlife simulation render (30-120 min producer-supervised, ~$1.00 Veo cost)
- Render `ops-center/public/cams/tembe-sim.mp4` (12s loop, elephant matriarch group at watering hole archetype, Veo 3.1 Fast)
- Render `ops-center/public/cams/manatee-sim.mp4` (12s loop, Florida manatees at clear spring archetype, Veo 3.1 Fast)
- Filenames intentionally do NOT contain "archival" — no file-path consumer should be misled.
- Producer-supervised because Veo billing remains on human + producer eyes-on judgment for "compelling archetype vs glitchy artifact." Reuse existing `make render-demo-video` infra or add `make render-cam-loops` target.
- 30-min estimate assumes pre-warmed billing + prompt templates. Fresh GCP project setup or queue depth → 60-120 min. Budget the higher number.
- Both clips MUST be silent (no audio track) — UI overlays the agent narration audio separately.
- Verify both clips do NOT contain any text overlays or watermarks (Veo prompt explicitly excludes text + overlays).

### W4 — Role-specific portraits (~1 hr)
- New Imagen 4 prompts for the 3 portraits producer flagged:
  - `court_evidence` → federal judge in chambers, black robe, formal authority
  - `root_agent` → cinematic robotic conductor (or human commander in mission control — producer choice)
  - `funder_reporter` → conservation foundation grant officer (clear "program officer" signal)
- Keep current 7 portraits as-is unless producer flags more
- Cost: $0.04 × 3 = $0.12

### W5 — Map 3D + minimap (~1.5 hr)
- Investigate why Mapbox 3D terrain doesn't always render (likely `terrain` config racing the style load)
- New `OrbitalMinimap.tsx` for the side rail (small, slow rotation, focused on the active cam's region)
- Keep `ReserveMap.tsx` for the Operations deep-dive (now in the Library menu)

---

## Codex handshake schedule (per work stream)

| Stream | Codex gate | What gets audited |
|---|---|---|
| Plan itself | **G0/G0.2/G0.3/G0.4** | This document (G0+G0.2+G0.3 HOLDs absorbed; G0.4 fires after this commit) |
| W0 Cam research [DONE] | G0.5 | reviews/v9-cam-research.md report |
| W1 Hero rebuild | G1 | New page.tsx layout + tab refactor |
| **W2a Firehose schema** | **G2.5** | model + protocol_stack fields across 6 emission sites + Pydantic + TS types |
| **W2b UI + voice** | G2 | NarrationStrip.tsx + Mission Bridge consume new fields + 4 voice clips |
| W3 Cam wiring + source-kind chips | G3a | Hybrid CAMS array + SourceKindChip + spotting transcript provenance |
| W3.5 Veo simulation render | G3b | tembe-sim.mp4 + manatee-sim.mp4 silent + watermark-free + no fabricated date/verified claims in filenames or chips |
| W4 Role-specific portraits | G4 | 3 Imagen 4 re-renders (judge/robot/grant-officer) |
| W5 Map + minimap | G5 | 3D render reliability + orbital rotation perf |
| Final | G6 | End-to-end hero screen + Devpost copy update |

Each gate clears before the next stream starts. Same protocol that ran 19 successful sweeps across v4-v8.

---

## Risks

1. **Wildlife cam research yielded no bot-wall-free public sources** [LOCKED 2026-05-17 night]: producer's "youtube blocks the bots" + 3 direct probes of non-YouTube alternatives all failed. Honest hybrid (2 NPS image + 2 Veo AI-generated simulation, with UI source-kind chips + VO synthetic-provenance disclosure) is the v9 model. Anti-pattern flags for codex: (a) any tile still pointing at `youtube.com/embed/*` = full revert to the failing plan; (b) any "fallback to YouTube if Veo render fails" logic = re-introduces bot-wall under guise of resilience; (c) any chip/transcript/filename claiming "verified" / "archival 2024" / third-party verification for Veo-generated content = the F500-trust-torpedo provenance lie.
2. **Hero rebuild regresses Mission Bridge UX** — keep MissionBridge.tsx component intact; just demote from tab to drawer. Zero risk to the existing photo-real portrait work.
3. **Auto-cycle Spot Now burns Gemini quota** — set client-side gate: pause auto-cycle when any tab loses focus + cap at 1 cycle/30s/cam.
4. **Robotic orchestrator portrait reads as 1980s sci-fi** — Approach A keeps current portraits; Approach C does Veo lip-sync. We're at Approach B (re-prompt 3 portraits with role-specificity). Acceptable taste risk.

---

## NOT in scope for v9

- Veo lip-sync clips per agent (v10 stretch, ~$4-8 Veo cost)
- Live frame-by-frame Gemini Live API for true real-time analysis
- Custom MCP tool server
- Spanner GraphRAG re-introduction
- Bug bounty program / SOC 2 certification work (v9+ roadmap, see PROCUREMENT.md)

---

## Order of operations

Day 1 (today): G0/G0.2/G0.3/G0.4 codex sweeps on this plan + W0 cam research DONE → save memory → producer approves
Day 2 (tomorrow): W3 cam wiring + W3.5 Veo render + W4 portraits in parallel → G3a + G3b + G4
Day 3: W1 hero rebuild → G1
Day 4: W2a firehose schema → G2.5 → W2b UI + voice → G2
Day 5: W5 map fixes → G5
Day 6: Integration + G6 end-to-end + Devpost copy update

~6-7 calendar days, ~12-16 CC hours (revised up per codex WARN 1), plus producer time for the Day 8-11 Veo render.

This compresses cleanly into v8's Days 15-20 buffer — no submission-deadline impact.

## What this plan does NOT change

- `/livecam/spot` endpoint contract
- Mission Bridge component file structure (just demoted from tab to drawer)
- 4 A2A peer Cloud Run services on the backend
- Agent Engine deployment
- ADK Eval framework
- Procurement pack
- Devpost submission draft

All Track 3 mandate signals stay intact.

## Codex prompt history

G0 / G0.2 / G0.3 / G0.4 swept. Verdicts + absorptions captured in the absorption sections above (BLOCK A, BLOCK B, BLOCK C + WARN/NIT resolutions). The original G0 prompt is preserved in git history at commit c804042 if needed.

G0.4 (commit dd345b1) HOLD absorbed in commit `<this commit>` — provenance-truthfulness BLOCKs (no "archival 2024 verified" claims for AI-generated content), stale-research-language WARN, optimistic-Veo-budget WARN, residual #12/#14 partial-satisfaction WARN. After this absorption, G0.5 sweeps the revised research report.
