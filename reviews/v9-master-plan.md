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

## Five work streams (v9 scope)

### W1 — Hero screen rebuild (~3 hr)
- New top-level layout in `ops-center/src/app/page.tsx`:
  - Replace 3-tab strip with: Hero (default) · Mission Bridge (drawer) · Library (current 3 tabs accessible from a menu)
  - 2×2 cam grid as visual center
  - Right side rail: minimap (slow rotation) + active-agent portrait + 4 peer ack chips
  - Bottom narration strip with protocol-aware ticker
- Auto-cycle agent-driven Spot Now (every 30s by default, with a pause toggle)
- Click any cam → fullscreen expand with overlay agent narration

### W2 — A2A peer storytelling (~1.5 hr)
- Each peer gets:
  - Distinct ElevenLabs voice (separate voice ID per peer)
  - Longer intro line (~12-18 words) explaining what the org does + which protocol it uses ("I'm the Funder Reporter. When a hot-species incident fires, I issue a program-tagged impact receipt to the conservation foundation's quarterly report via A2A v0.3.")
  - Protocol stack badge visible while speaking: `[A2A v0.3]` `[Gemini 2.5 Pro]` `[Vertex AI Search]` `[Cloud Run]`
- Generate 4 new voice clips via the existing ElevenLabs script
- Update `MissionBridge.tsx` AGENTS array intros + add voice files

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
| Plan itself | **G0** | This document |
| W1 Hero rebuild | G1 | New page.tsx layout + tab refactor |
| W2 A2A storytelling | G2 | 4 voice clips + protocol badges + intro length |
| W3 Wildlife cams | G3 | Source legitimacy + embed-license posture + reliability |
| W4 Portraits | G4 | Photo realism + role legibility (no uncanny) |
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

~6 calendar days, ~9-12 CC hours, plus producer time for the Day 8-11 Veo render.

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
