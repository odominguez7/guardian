# GUARDIAN v9 W0 — Wildlife cam research report (REVISED)

**Conducted:** 2026-05-17 night.
**Budget consumed:** ~1.5 hour (initial 4-cam YouTube probe + producer pushback + non-YouTube probe + honest pivot).
**Outcome:** Honest hybrid model. **2 NPS landscape feeds (image_url, no bot wall) + 2 Veo AI-generated wildlife simulation tiles (synthetic, with explicit AI-generated provenance disclosure — no claim of capture date or third-party verification).** The agentic narrative is the hero; cams are the evidence layer.

## Why the original 4-YouTube plan was wrong

Producer pushback 2026-05-17 night: *"for reference youtube blocks the bots you should know that."*

I had to admit the v6/v7 lesson I'd just re-violated:
- Cloud-hosted ops-center origin → YouTube embed → "Sign in to confirm you're not a bot" wall.
- The oembed + `playableInEmbed:true` check passes in synthetic probes but FAILS in real browser sessions originating from `*.run.app`.
- This was the recurring v6 NamibiaCam failure mode that producer had already caught twice.

## Why non-YouTube wildlife sources don't solve it either

Three direct probes 2026-05-17 night:

| Source | Result |
|---|---|
| Raptor Resource Project — Decorah Eagles `/birdcams/decorah-eagles/` | Page iframe is `youtube.com/embed/IVmL3diwJuw`. Same bot-wall risk. Macaulay Library iframe is bird-audio archive, not live video. |
| Smithsonian National Zoo — Elephant + Panda cams | Player serves `blob:nationalzoo.si.edu/<uuid>` (MSE-decoded HLS). The actual HLS endpoint is server-tokenized and not embeddable on third-party origins. |
| Monterey Bay Aquarium — Live Cams | Cams lazy-load via authenticated JS players. Headless probe finds only tracking iframes (`doubleclick`, `zoom`, `onetrust`). Real cam players require their domain. |

Pattern: every "real-wildlife" stream is either (a) YouTube under the hood with bot-wall risk, or (b) MSE-served from a tokenized HLS that's not embeddable. The honest budget consumed says: **no viable non-YouTube wildlife embed exists for this submission window.**

## The honest pivot — agentic narrative is the hero

Producer issue #14: *"Demo feels recorded made-up not real-time."*
Producer issue #15: *"Communicate business model, impact, revolutionary tool."*

These two flags are bigger than the cam imagery question. The fix is not "find better cam tiles." The fix is **make the agents the demo and the cams the evidence layer with honest provenance disclosure.**

### v9 cam tile model (locked)

| Tile slot | Source kind | Backing URL / asset | Honest label shown in UI |
|---|---|---|---|
| CAM-01 | NPS image | `https://www.nps.gov/.../webcam-current.jpg` (Old Faithful) | "Yellowstone NPS — Old Faithful — refreshes 60s" |
| CAM-02 | NPS image | `https://www.nps.gov/.../webcam-current.jpg` (Glacier) | "Glacier NPS — refreshes 60s" |
| CAM-03 | Veo simulation | `ops-center/public/cams/tembe-sim.mp4` (Veo 3.1 Fast render of elephant matriarch group archetype) | "AI-generated archival-style simulation — Tembe Elephant Park archetype" |
| CAM-04 | Veo simulation | `ops-center/public/cams/manatee-sim.mp4` (Veo 3.1 Fast render of manatees-at-springs archetype) | "AI-generated archival-style simulation — Homosassa Springs archetype" |

Critical UX rule: **the label is part of the tile, not a footnote.** Every tile carries its source-kind chip ("Live image · refresh 60s" or "AI-generated simulation · Veo 3.1 Fast"). No tile pretends to be something it isn't, and no tile claims a real-world capture date or third-party verification for AI-generated content.

### Why this is more defensible to F500 buyers than the YouTube plan

Sponsor/sustainability CSOs evaluating GUARDIAN will ask: *"What happens when the underlying stream goes offline?"* The honest answer becomes a feature, not a bug:

> "GUARDIAN's evidence layer cycles between live federally-operated feeds and AI-generated simulation tiles. Each tile discloses its source kind. When a live source degrades, the agents do not silently substitute — they label the tile, disclose the source, and proceed with synthetic-provenance pattern recognition. Production deployment swaps the simulation tiles for licensed reserve footage with attribution."

This is exactly the F500 audit-trail posture the Falsifier already encodes. The cams are now consistent with the rest of the architecture (everything is labeled, sourced, and falsifiable).

### Why this partially satisfies "we MUST spot animals" (with residual gap)

The auto-spot agentic cycle runs on the **Veo simulation tiles** for the animal-spotting beat. The simulation depicts elephants and manatees at archetype habitats; the pattern-recognition agent processes the synthetic frames the same way it would real footage. The spotting transcript explicitly discloses synthetic provenance:

> "Spotting CAM-03 — AI-generated archival-style simulation, Tembe Elephant Park archetype. 7 individuals detected, matriarch-group composition. Cross-referencing CITES Appendix I + IUCN Vulnerable database for the species depicted. Note: this tile is a simulation; production deployment would swap for licensed reserve footage."

Residual gap: producer issues #12 ("real wildlife") and #14 ("not recorded made-up") are only partially satisfied — disclosure makes the demo truthful but the imagery itself is still synthetic. **Mitigation candidates if budget allows (~2 hr stretch):**
1. License a 12-second wildlife clip from Pond5 / Shutterstock / Storyblocks ($25-50/clip) and use that for CAM-03 or CAM-04 with proper attribution chip ("Licensed footage · Pond5 #<id> · 2024").
2. Reach out 2026-05-18 to Tembe Elephant Park / Save-The-Manatee Club for a research-use grant of a short archival clip with permission.
3. If neither lands in time, stay on the honest 2-NPS-image + 2-Veo-simulation hybrid and lean harder on the agentic narrative as the wow.

## Veo loop assets needed

| Asset | Veo prompt | Duration | Cost |
|---|---|---|---|
| `tembe-sim.mp4` | "African elephant matriarch group at watering hole, golden hour, savanna landscape, documentary realism, no text, no overlays, 12s loop" | 12s | ~$0.50 |
| `manatee-sim.mp4` | "Florida manatees underwater at clear spring, slow drift, sun rays through water, no text, documentary realism, 12s loop" | 12s | ~$0.50 |

Total Veo cost: ~$1.00 (within the $30-50 demo render budget already approved for Day 8). **Filenames intentionally do not contain the word "archival"** so that no consumer of the file path is misled into treating these as real captures.

Budget caveat: 30-min producer-supervised assumes Veo billing + prompt templates are pre-warmed (existing `make render-demo-video` infra). If billing requires fresh GCP project setup or queue depth, budget 60-120 min. Producer-supervised because Veo billing remains on the human, and because the producer is the only one with eyes-on judgment for "does this clip read as compelling wildlife archetype or as a glitchy AI artifact."

## What this means for the v9 plan

1. **W0 → DONE** (this report).
2. **W3 (wildlife cam wiring)** stays ~30 min: replace the 4 NPS landscape entries in `ops-center/src/components/LiveCams.tsx` with the hybrid set above + add the source-kind chip rendering.
3. **W3.5 (NEW, 30-120 min producer-supervised)**: render the 2 Veo AI-generated simulation tiles via `make render-cam-loops` (or inline curl to Veo API). Drop in `ops-center/public/cams/{tembe,manatee}-sim.mp4`.
4. **W1 (Hero unification) + W2a/b (protocol badges) + W4 (auto-spot agentic chain)** are now MORE important, not less — the cams' honest source disclosure forces the agentic narrative to carry the wow.
5. **Producer disclosure required**: the v9 demo cuts MUST verbally name the cam source kinds in the VO. "Two federally-operated NPS feeds and two AI-generated archetype simulations of protected reserves; production deployment swaps in licensed footage" — one sentence in the orchestrator intro.

## Anti-pattern flags for codex G0.5

The codex reviewer should specifically falsify:
- Any UI tile that LACKS the source-kind chip — that violates the F500 audit posture.
- Any VO line that calls the Veo loops "live" — that violates the honest-provenance posture.
- Any cam URL still pointing at `youtube.com/embed/*` — full reversion to the failing plan.
- Any "fallback to YouTube if Veo render fails" logic — that re-introduces the bot-wall risk under the guise of resilience.

## Citations + recovery path

- Producer message 2026-05-17 night: *"for reference youtube blocks the bots you should know that"* — single sentence, no link, treated as authoritative.
- Probes:
  - `https://www.raptorresource.org/birdcams/decorah-eagles/` — youtube.com/embed/IVmL3diwJuw + macaulaylibrary.org/asset/.../embed/
  - `https://nationalzoo.si.edu/webcams/panda-cam` — `<video src="blob:...">` MSE source, no public HLS
  - `https://nationalzoo.si.edu/webcams/elephants` — same blob: pattern
  - `https://www.montereybayaquarium.org/animals/live-cams` — lazy-loaded JS player, no static embed
- If YouTube bot-wall issue is resolved post-submission (residential-proxy Cloud Function), the v10 stretch can re-introduce 1-2 explore.org cams as `live_archival` hybrid tiles. v9 stays on the honest hybrid.

## G0.5 audit summary

| Claim | Evidence in this report |
|---|---|
| YouTube embeds bot-wall on cloud-hosted origin | Producer's direct observation + v6/v7 history (`feedback_*.md` memories) |
| Non-YouTube wildlife sources also unavailable | 3 direct probes documented above |
| Honest hybrid model partially satisfies producer issue #12 + #14, fully satisfies #15 | UI chip + VO synthetic-provenance disclosure + agentic spotting on Veo simulation tiles. Residual gap on #12/#14 is acknowledged + has licensed-footage stretch path |
| Veo cost within budget | $1.00 of pre-approved $30-50 demo render budget |
| W0 truly done, not deferred | This report; W3 + W3.5 are wiring tasks, not research tasks |
