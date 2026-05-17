# CEO Review v3.1 FINAL — rewritten after codex RECONSIDER

_Codex flagged 6 sharp objections to the v3.1 draft. All absorbed. This is the rewrite._

## What codex challenged (and how this rewrite responds)

| Codex objection | Response in this rewrite |
|---|---|
| 6.4 Heavy-Lifting panel narrates synthetic metrics on scripted fixtures — doesn't break pre-fab feel | **REFRAMED:** panel now reads from REAL `tool_end` events already emitted by the live firehose (Cloud Trace data, real model names, real latency_ms, real token counts). Not synthetic. Pre-fab break is real. |
| 15-year-old's "moving map" comprehension ask was deferred | **PROMOTED in.** Lightweight sprite-based path strip showing the poacher truck approaching the elephant herd is now Sub-move 6.4. Watch Dogs-style top-down. |
| Modal Tribunal interrupts demo flow | **MOVED inline.** Falsifier dissent expansion now lives inside the IncidentPanel card itself — click-to-expand, no overlay. |
| Google logo compliance risk even with "permission granted" | **DEFERRED.** Heavy-Lifting panel ships with text-only product names (`Gemini 2.5 Pro · 720ms · 1247 tok`). No Gemini/Imagen/Veo/Lyria/Vertex logo art in v3.1. Logo work moved to v3.2 pending formal Google brand-partner channel. |
| Gemini 2.5 Flash translator at event-emit time = real-time backlog | **CHANGED:** plain-language ticker copy is now **pre-generated per scenario** (canned narrative variants stored in `scripts/video/ticker-copy.json`). Zero LLM in the hot firehose path. |
| 6 hours is optimistic — actually ~13 | **REBUDGETED at ~10 hours.** Codex's sub-move estimates accepted. Heavy-Lifting panel kept (now smaller scope: real-data-only). Tribunal modal replaced with inline (smaller scope). Map sprite added. |

---

## Final v3.1 plan

| # | Sub-move | Effort | Specific outcome |
|---|---|---|---|
| **6.0** | Banner regression fix: add `_DEMO_MODE` to `ops-center/cloudbuild.yaml` substitutions; verify post-redeploy that "ANONYMOUS DEMO · FIREBASE AUTH NOT CONFIGURED" is gone from the live URL. | 0.5 hr | P0 audit finding resolved |
| **6.1** | **Pre-generated plain-language ticker.** Each event kind gets a narrative template in a new `scripts/video/ticker-copy.json` fixture: `audio_agent.classify_audio → "Audio Agent heard a {sound_class} near {camera}. {confidence}% confidence."` Ticker renderer interpolates from the event payload — no LLM call. Toggle `[PLAIN · TRACE]` in the panel header. | 1.5 hr | Omar #1, 15yo Discord critique, designer #3 |
| **6.2** | **Audio playback chip on the Audio Agent ack.** `<audio controls>` with a CC0 gunshot clip (~30 KB) preloaded; "🔊 Replay" button. When `audio_agent` returns `sound_class != "silence"`, the chip appears in the IncidentPanel inline. | 1.5 hr | Omar new ask #1 |
| **6.3** | **Falsifier dissent inlined.** Replace today's small chip with an expandable card section. Always-visible header ("Falsifier · CONCUR" or "DISSENT"); click expands to show: orchestrator's claim summary (LEFT), Falsifier's challenge + gate fired + delta (RIGHT), and a `<audio>` element with a pre-recorded Gemini Live narration of the dissent reason (different voice from main). No modal. Stays on incident card. | 1.5 hr | Omar #4, DeepMind move A, designer #5, codex revised flagship |
| **6.4** | **NEW: Watch Dogs sprite path strip.** Above the map (or replacing the dead-map center if WebGL is the only blocker), a 1920×120 horizontal sprite strip with two animated dots: red "Poacher Truck" pin advancing left→right, green "Elephant Herd" pin holding center, dashed line between them. Distance closes over the demo beat. Ranger Service sprite intercepts. SVG + Framer Motion; no Mapbox dependency. | 2 hr | 15yo's #1 ask + universal-comprehension bar |
| **6.5** | **Google Heavy-Lifting panel (REAL data only).** Collapsible bottom strip displaying live `tool_end` events from the firehose: each row shows model name (text, no logo), real `latency_ms` from the event, real `payload.tok_count` if available, and a click-to-expand prompt/response. Reads existing events; no synthetic data; surfaces the real work the agents do. | 2 hr | Omar new asks #2/4/5 + DeepMind move B (lite) |
| **6.6** | Codex final sweep on v3.1 + single redeploy of ops-center. | 1 hr | §4.5 handshake gate |

**Total: ~10 CC hours** (codex re-estimate accepted).

---

## What's still deferred to v3.2 (post-submission roadmap)

- Veo aerial map background loop
- Live Trace tab with agent graph + node-click reasoning expansion
- Field Feed tab with 4-cam grid + waveforms
- Vision Pro tab strip styling
- Nano Banana species-identity continuity across surfaces
- Tool-selection top-3 probability ribbon
- Adversarial second-model rollout (turn the SOP linter into a real adversarial sampler)
- Counterfactual sliders on the Falsifier debate
- Google-branded logo art on heavy-lifting panel (pending formal Google brand-partner channel)

---

## Honest probability estimate (per codex)

- Moves 0-5 alone: ~92/100 against the Track 3 rubric
- Moves 0-5 + v3.1 (this plan): ~95-96/100
- Reaching 98/100 needs at least 1-2 of the v3.2 deferrals (most likely: the moving map upgrade to real Mapbox + Field Feed Tab C)

**Codex's stance:** even this rewrite is unlikely to deliver 98 by submission. Honest range is **95-96.** Going for the 98 target risks destabilizing the ship-ready state.

---

## Recommendation

**Proceed at the 10-hour v3.1 scope.** Targets 95-96/100. Drops the 98-ambition floor honestly. Defers the high-effort moves to a v3.2 roadmap that can ship if GUARDIAN advances to a Track 3 finalist round.

**Single highest-leverage move if forced to one:** Sub-move 6.4 (Watch Dogs sprite path strip). Closes the "no elephant on screen" comprehension gap that the 15-year-old flagged as a deal-breaker. Solves the most measurable comprehension problem at the lowest effort.

**Pending:** Omar greenlight before any code lands.
