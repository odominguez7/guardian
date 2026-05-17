# GUARDIAN v3.2 — Full Visual Overhaul

_Producer feedback 2026-05-17 night: "3/10 visuals, you have Google suite at disposal and refuse to use it." This plan reverses the v3.1 scope-reduction call and SWINGS for the 98+. Replaces conservatism with the Visual designer's full vision._

## Specific complaints from producer

1. Map not centered in independent browser
2. Music doesn't make sense — replace or remove (use ElevenLabs not Lyria for audio)
3. Active Incidents bar lacks visible scrollbar
4. **"NO single trace of Google visual tools applied"** — Imagen / Veo / Nano Banana / Gemini Live not visible
5. Tabs still look old (current = scenario pill buttons; want real top-level nav tabs)
6. Want a SPECIAL space for visual agent interaction
7. Plain ticker is 4/9 — needs visual punch for the 15-year-old
8. Trace mode is good; keep
9. **Want fake-staged "live cams" with Veo animal videos**

## v3.2 plan — 9 sub-moves, ~12 CC hours

| # | What | Effort | Addresses |
|---|---|---|---|
| **7.0** | **Map centering + visible scrollbar fixes**. Reserve Map recenters on Africa with proper zoom; IncidentPanel gets `scrollbar-thin` styling so navigation is obvious. | 30 min | #1, #3 |
| **7.1** | **3-tab architecture with Vision Pro segmented control** at top-left. Tabs: `Operations` (current canvas refined) · `Live Cams` (Veo + Imagen showcase) · `Agent Theater` (the visual interaction space producer asked for). Tab strip uses frosted-glass + sliding amber indicator. | 1.5 hr | #5, #6 |
| **7.2** | **Live Cams tab.** 4 Veo 3.1 generated 6s loops in a 2×2 grid: African elephant herd at dusk · cheetah crossing · vehicle in distance (poacher) · camera-trap IR night. Each cam tile has a Imagen still frame that crossfades over the Veo loop when its incident triggers. Live waveform overlay during audio detection. | 4 hr | #4 (Veo + Imagen), #9 |
| **7.3** | **Agent Theater tab.** Center stage: the 10 Imagen agent portraits at 192×192 (not buried 24px avatars). When a scenario fires, agents "speak" in sequence with speech-bubble overlays + ElevenLabs voice playback. Visual choreography: agent portraits glow → speak bubble appears → next agent picks up. The Falsifier gets the dramatic counter-position stage right. | 4 hr | #4 (Imagen + ElevenLabs), #6, #7 |
| **7.4** | **ElevenLabs narration baked per-scenario.** Pre-generate one ElevenLabs MP3 per (agent, scenario) combo. Played in Agent Theater + replaces browser SpeechSynthesis in Falsifier Tribunal. ~16 short clips total ($0.10-0.30 cost). | 1 hr | #4, #6 |
| **7.5** | **Kill the ambient music.** Remove Lyria bed from Ops Center page-load. Music in the demo VIDEO is fine — but the live Ops Center plays SILENT until a scenario fires; THEN ElevenLabs narration is the audio. | 15 min | #2 |
| **7.6** | **Plain ticker visual punch.** Each event row gets agent-tinted left border + tiny agent portrait (16px). Different agents = different color signatures. The 15-year-old's eye lands on the colors not the text. | 30 min | #7 |
| **7.7** | **Codex pre-implementation challenge** on this plan. Absorb amendments. | 30 min | discipline |
| **7.8** | **Codex final sweep + redeploy.** Per §4.5 handshake gate. | 1 hr | discipline |

**Total: ~12 hours.** Bigger than v3.1's 6-hour cap, but matches the producer's explicit ambition.

## Cost projection

- Veo 3.1 Fast: 4 clips × $0.60 = $2.40
- ElevenLabs: 16 clips × ~$0.02 = $0.32
- Imagen: existing portraits reused, no new spend
- Total new: ~$2.70

Adds to existing $1.10 from Move 2 → cumulative GCP spend ~$3.80 (well below the $1,991 hackathon ceiling).

## Architectural decisions

- **Tab navigation NOT scenario buttons.** Scenario buttons move INSIDE the Operations tab; tabs are top-level surfaces.
- **Live Cams + Agent Theater are NEW SURFACES not modals or drawers.** Full-page real estate.
- **Agent Theater is the producer's "agentic interaction space"** — the one most-requested visual move.
- **Ambient music dies on the Ops Center**; it stays on the demo video where it has narrative purpose.

## What's still deferred (post-submission v4)

- Vertex AI Memory Bank integration (DeepMind's "learned coordination" move)
- Counterfactual sliders on Falsifier (DeepMind move A)
- Tool-selection probability ribbon (DeepMind move B)
- Adversarial 2nd-model rollout (replace SOP linter with real adversarial Gemini call)
- Nano Banana species-continuity across cards

## Verdict

CLEAR for execution after codex challenge. The "tabs old / no Google visuals" critique gets fully answered. The 15-year-old finally sees animals on screen. The Falsifier gets its dramatic stage. The Google suite is on stage by name.
