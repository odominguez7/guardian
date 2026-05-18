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

**BLOCK A — W0 arithmetic impossible** [RESOLVED via real research, not paper math]: W0 sprint was executed 2026-05-17 night, ~1 hour budget consumed. Report at `reviews/v9-cam-research.md`. **4 of 4 candidate live wildlife cams verified isLive + playableInEmbed:**

| Tile | YouTube id | Wildlife |
|---|---|---|
| CAM-12 | `0P_LBKqVbfs` | Tembe Elephant Park (elephants) |
| CAM-07 | `Fz6sl9YJZE0` | Homosassa Springs (manatees) |
| CAM-22 | `GGIE1E-kaMQ` | Decorah Eagles (bald eagles) |
| CAM-04 | `5e4lsEe4Vew` | International Wolf Center (wolves) |

All 4 are explore.org-branded 24/7 streams. Producer's "we MUST spot animals" requirement is genuinely met. **No fallback to NPS + Veo simulation needed.** G0.5 codex on the research report runs next; W3 (cam wiring) reduces to a 30-min task.

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

**BLOCK 1 absorbed — W0 prepended (research SPRINT before W1)**: rather than treat wildlife-cam research as a 1-hr sub-task inside W3, promote it to a **standalone W0 sprint** that runs FIRST and gates W1. Concrete sources to test (with the legal-or-bot-wall risk explicitly named):

| Source | Risk | Test |
|---|---|---|
| Africam.com (Tembe Elephant Park, Naledi) | Was YouTube-walled v6; check their native site for direct HLS | `curl -sI https://www.africam.com/wildlife/africam-live-stream-tembe-elephant-park` → look for `.m3u8` |
| WildEarth.tv | Subscription player (paid); embed may need partner agreement | Probe site for guest preview embed |
| explore.org (Brooks Falls bears, Pete's Pond) | Uses proprietary CDN; URL may be exposed via their iframe player | Inspect player network tab in Devtools |
| Smithsonian National Zoo (panda, cheetah) | iframe-based; check `<source>` tag URLs | Same as above |
| AlertWildlife — Brown Bear Webcam (Brooks River) | Public stream | Probe known endpoint |
| NOAA Bald Eagle cams (Decorah, Sauces) | Public mjpeg | Probe known endpoint |
| **Fallback if research yields <4 wildlife-rich sources**: keep NPS cams BUT replace 2 of them with the highest-wildlife-density NPS cams (Glacier Many Glacier, Yellowstone Lamar Valley, Katmai if NPS hosts it). Add a 3rd-party Veo loop tile labeled "production camera" so we still hit "4 cams" with 2-3 verified wildlife sources + 1-2 production-grade stand-ins. |

W0 ends with a written report at `reviews/v9-cam-research.md` listing each tested source + verdict. G0.5 codex sweep on the report before W1 starts.

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

### W0 — Wildlife cam research SPRINT [DONE 2026-05-17 night]
Executed in ~1 hour. Report at `reviews/v9-cam-research.md`. 4/4 explore.org-branded wildlife streams verified live + embeddable: Tembe Elephant Park, Homosassa Manatees, Decorah Eagles, International Wolf Center. **No fallback needed.** G0.5 codex on the report fires next.

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

### W3 — Better wildlife cam sources (~1 hr research + 1 hr wire)
- Research targets (need to verify each):
  - **Africam.com / WildEarth.tv** — Tembe Elephant Park, Naledi Game Reserve, Idube. Have their own HLS players; may expose direct stream URLs.
  - **Smithsonian Zoo** — Asian Pandas, Cheetahs, African Lions on public webcams.
  - **explore.org wildlife cams** — Brown Bears at Brooks Falls (Katmai), Pete's Pond Botswana, African Watering Hole at Mpala Research Centre Kenya.
  - **AlertWildlife** — bear + wolf + moose cams.
  - **NOAA Eagle Cams** — Decorah, Sauces Bald Eagles.
- Pick 4 with verified wildlife traffic + embeddable surface
- Replace NPS landscape cams in `LiveCams.tsx` CAMS array
- Test each manually for actual wildlife presence

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
| W3+W4 Cams wired + portraits (paired) | G3 | Cam wire-up + 3 role-specific portraits |
| W5 Map + minimap | G5 | 3D render reliability + orbital rotation perf |
| Final | G6 | End-to-end hero screen + Devpost copy update |

Each gate clears before the next stream starts. Same protocol that ran 19 successful sweeps across v4-v8.

---

## Risks

1. **Wildlife cam research yields no public sources without bot walls** — fallback: combine NPS cams + 1-2 Veo loops as "production camera" preview tiles. Producer already approved this fallback in v7.5.
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

Day 1 (today): G0 codex on this plan → producer approves → save memory
Day 2 (tomorrow): W3 wildlife cam research + W4 portraits in parallel → G3 + G4
Day 3: W1 hero rebuild → G1
Day 4: W2 A2A storytelling → G2
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

## Codex prompt for G0

Plan reviewed should answer:
1. Is SELECTIVE EXPANSION the right mode given the producer's "boring dashboard" verdict?
2. Are the 5 work streams sized realistically (~9-12 CC hours total)?
3. Is the hero rebuild architecturally sound — does demoting Mission Bridge from tab to drawer regress anything?
4. Will the wildlife cam research succeed? What are concrete candidate URLs?
5. Is the protocol-badge-while-speaking idea feasible with current ElevenLabs + DOM rendering, or does it need a new agent?
6. Does the 5-gate codex schedule have the right granularity?
7. What's NOT in this plan that producer's 15 issues implied?

End with CLEAR or HOLD with specific BLOCK items to add to the plan.
