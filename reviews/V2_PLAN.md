# GUARDIAN demo video v2 — Approach D (codex-tightened cinema)

**Status:** CEO-reviewed + codex-reviewed 2026-05-16. Producer-locked. Mode: SCOPE EXPANSION → codex correction → SELECTIVE EXPANSION. All 6 codex HARD FIX findings absorbed. Cross-model tension resolved by producer: take codex's pacing correction, keep light story-arc framing, eliminate credibility landmines.

**Premise:** Make AI Agents Challenge judges remember GUARDIAN. They came for agents working. Lead with agents. Light narrative around the agents, not narrative as the centerpiece. Ship at 8/10 with track-winner credibility; not at "10/10 ceiling, 5/10 floor" with IP and overclaim risk.

---

## §0 — Hard blockers (must clear before execution)

| # | Item | Status | Action |
|---|---|---|---|
| 1 | Mapbox public token | MISSING | Omar pastes `pk.eyJ...` from mapbox.com (free signup) |
| 2 | ElevenLabs API key + Voice ID | AVAILABLE in `/Users/odominguez7/Desktop/o22-studio/.env` | Copy to `GFS - guardIAn/.env.local` |
| 3 | Wildlife b-roll, 6 sec, CC0 license | TO FETCH | Pexels free wildlife (search "elephant savanna dusk"). Pexels is CC0, no attribution required. Snapshot Serengeti deferred unless we confirm clip-level CC0. |
| 4 | Royalty-free music bed, ~3:00 | TO FETCH | Pixabay Music search "ambient cinematic tension 80 bpm" |
| 5 | KPMG quote citation method | DECIDED (codex correction) | Text-only quote with attribution + footnote URL. NO screenshot of report cover (IP gray area). |
| 6 | Fact-check pass on CSRD claims | TO DO | Verify "EU CSRD requires biodiversity disclosure from Fortune 500" with current source; include citation URL on-screen |

**Producer hard rule:** No re-recording until Mapbox token is in `.env.local`, Ops Center rebuilt locally, and Omar visually confirms map + pin pulse + arrows in browser. If Mapbox fails, fall back to OpenStreetMap via Leaflet (no token needed, slightly less polish, no cinema dependency on a missing token).

---

## §1 — Storyboard (Approach D: agents-first, light arc)

**Total: 3:00.** Product visible by **0:15** (codex correction from 0:50). Cold open compressed to 10s. Demo section is the centerpiece (60 seconds). All factual claims softened to defensible language.

```
0:00–0:10  COLD OPEN          Wildlife ambient → black → product
0:10–0:30  PROBLEM + REVEAL   The stat + the bridge + cut to Ops Center live
0:30–1:30  DEMO               60 seconds, all 4 A2A peers, real receipts
1:30–1:50  PROOF              Evidence packet + "this is reproducible" line
1:50–2:25  ARCHITECTURE       The stack, callouts as named
2:25–2:50  BUSINESS CASE      Market size + Marketplace + ask
2:50–3:00  PRODUCER CLOSE     Punchline + credit
```

| Sec | Beat | Visual | Audio |
|---|---|---|---|
| 0:00–0:06 | **Wildlife ambient** | Pexels clip: dusk savanna, elephant silhouette. No text overlay. | Music: low ambient drone. No SFX, no gunshot. Natural ambient wildlife sound only. |
| 0:06–0:10 | **Pre-cut text** | Single line on the ambient footage: *"Conservation is a data problem."* Hold 2s, then cut to black for 0.5s. | Music: drone holds. |
| 0:10–0:18 | **Hook stat** | Black background. White type: *"730+ companies. $22 trillion in assets. All committed to TNFD biodiversity disclosure."* Small URL footnote: *tnfd.global/who-we-are*. | Music: subtle lift. VO: *"Seven hundred thirty companies have committed to TNFD biodiversity disclosure."* |
| 0:18–0:25 | **Bridge** | Black, white type: KPMG attributed pull-quote, text only (no cover image). Footnote: *KPMG Survey of Sustainability Reporting · biodiversity chapter*. | VO: *"And as KPMG put it: most can't even prove they have the data."* |
| 0:25–0:30 | **Reveal** | GUARDIAN wordmark holds 1s, fades into Ops Center live, map of Africa visible behind. | VO: *"GUARDIAN. Multi-agent biodiversity defense on Google Cloud."* |
| 0:30–0:42 | **Demo opens** | Cursor clicks `Full Multimodal Chain`. Mapbox flyTo from continent to Selous over 1.5s. Pulsing amber pin at Tag-22. Stream Watcher card appears. | VO: *"Camera-trap Tag-22 fires. Stream Watcher confirms a vehicle frame. Audio Agent classifies a gunshot."* |
| 0:42–0:55 | **Species ID + corpus RAG** | Species ID card appears. Pop-out highlights the corpus lookup row: *Endangered · CITES Appendix I · TNFD material*. | VO: *"Species ID grounds the herd in the IUCN corpus. Endangered. CITES Appendix One. Material under TNFD."* |
| 0:55–1:20 | **A2A fan-out (centerpiece)** | Four animated amber arrows draw from Selous to peer markers on the map. Each peer ack card appears under the incident with real IDs (PSR-9737, TNFD-2026-A0192B2A32, FUND-A0192B2A32, MUTAID-A019282A32). **Lower-third overlay during this beat:** *"Each peer is a separate Cloud Run service. github.com/odominguez7/guardian"* | Music: subtle arrival hits. VO: *"The orchestrator fans out to four independent A2A peers, each a separate service: Park Service, Sponsor Sustainability, Funder Reporter, Neighbor Park."* |
| 1:20–1:30 | **Demo close** | Cursor clicks evidence link. Court-evidence packet opens, scroll once. SHA-256 chain hash visible. | VO: *"Twenty events. SHA-256 anchored. Audit-grade chain of custody."* |
| 1:30–1:50 | **Proof / reproducibility** | Punchline static frame: TNFD filing ID `TNFD-2026-A0192B2A32` centered, large. **Below it, smaller, monospace:** *"reproducible · POST /demo/run/multimodal_pipeline · github.com/odominguez7/guardian"*. | VO: *"Every ID on screen comes from a live call to a public endpoint. This is reproducible. Source on GitHub."* |
| 1:50–2:25 | **Architecture** | Architecture diagram slow Ken-Burns. Callouts highlight as named. | VO: *"Five Cloud Run services. ADK orchestrator on Gemini two point five Pro. Three specialists. Four A2A peers. Vertex AI Search grounding. BigQuery audit trail. One Marketplace install."* |
| 2:25–2:50 | **Business case** | Three stats appear as VO names them: *$300B reporting market · Fortune 500 mandate · 4 enterprise A2A peers shipped*. Then Marketplace listing thumbnail. | VO: *"Three hundred billion dollar biodiversity reporting market. Disclosure is mandatory for every Fortune 500. GUARDIAN ships on Google Cloud Marketplace through the channels procurement already trusts."* |
| 2:50–3:00 | **Producer close** | Filing-ID frame returns dimmed. Producer credit overlays. | VO: *"Built by Omar Dominguez Mondragon. CEO and Founder, GuardIAn Wildlife. MIT Sloan."* |

### Claim softening (codex correction)

| v1/V2A claim | V2D corrected |
|---|---|
| "Court-admissible chain of custody" | "Audit-grade chain of custody" |
| "Auto-files TNFD entry you owe the regulator" | "Files the TNFD entry" (no auto, no regulator-debt framing) |
| "Ninety seconds" (the end-to-end claim) | Removed entirely |
| "One Marketplace install" | Kept (factually true) |
| "Real-time" | Kept (the firehose is real-time) |
| "SOC 2 readiness" | Removed (not landed, weakens nearby claims) |

### IP / citation rules

- **No external screenshots** of KPMG, TNFD, or third-party report covers in the video itself. Quote with text attribution only, footnote with URL.
- All stats (730+ TNFD adopters, $22T AUM, $300B market) get a small on-screen footnote URL when displayed.
- Marketplace listing thumbnail is OUR listing (already shipped per D18), no third-party logos beyond Google Cloud's.

---

## §2 — Mapbox (codex-corrected deploy path)

**Codex's simpler path wins.** Local `.env.local` build instead of Cloud Build deploy pipeline change.

| Step | Action | Effort |
|---|---|---|
| 1 | Omar pastes Mapbox token into `ops-center/.env.local` | 30s |
| 2 | `cd ops-center && npm run dev` locally | 15s |
| 3 | Verify map + tile render in `localhost:3000` | 1 min |
| 4 | Add map animation code (§2.1) | 45 min |
| 5 | `npm run build && npm start` to verify production build works | 5 min |
| 6 | Record against `localhost:3000` via Playwright (not against Cloud Run!) | 5 min |

Recording locally means: no Cloud Build, no Dockerfile change, no Cloud Run redeploy, no production dependency, no risk of breaking the live judge-clickable URL. The live URL stays exactly as it is (the existing 2026-05-15 Ops Center revision). The video is recorded against our local dev server with the token in `.env.local`. After submission, we can do a separate clean deploy of the map-enabled version at our leisure.

### §2.1 — Map animation enhancements

~80 LOC in `ReserveMap.tsx`:
- CSS keyframe pulse on the camera-trap marker
- Animated dashed line layer drawing from Selous to peer coords on `peer.dispatched` firehose events
- `map.flyTo({center: SELOUS, zoom: 6, duration: 1500})` on scenario start
- Peer markers fade in at their geographic positions when their ack lands

Each peer needs a fixed geographic anchor for the visual:
- Park Service → Dar es Salaam (placeholder for Tanzania park authority HQ)
- Sponsor Sustainability → abstracted off-map (London, since target is EU-domiciled F500)
- Funder Reporter → abstracted off-map (Geneva, common conservation funder geography)
- Neighbor Park → Maasai Mara, Kenya (real adjacent park)

These coords are hardcoded in `lib/reserves.ts`.

---

## §3 — Voice (codex-corrected acceptance test)

**Codex correction:** acceptance test isn't "can't tell AI in 3s" (wrong metric — could pass while still sounding like a sales pitch). New metric: **"sounds trustworthy for an enterprise compliance buyer."**

### Voice selection

Generate one 12-second sample of the proof line (1:30–1:50 beat: *"Every ID on screen comes from a live call to a public endpoint. This is reproducible. Source on GitHub."*) on three voices:
1. `Brian` — deep American masculine, slow cadence (first choice)
2. `Daniel` — British masculine, documentary register
3. `Antoni` — warm, slightly accented

Settings: `eleven_multilingual_v2`, stability 0.5, similarity 0.75, style 0.15, speaking_rate 0.92.

### Acceptance gate (revised per codex)

Omar listens to all three samples, picks based on: **"if this person was reading me a security incident report, would I trust them?"** Not "is it AI." Trust > undetectability.

### Pacing parameters

- Speaking rate 0.92 throughout (gravitas without sleepiness)
- 200ms SSML pauses between sentences in cold open, hook, and proof beats
- Punchline ("Every ID on screen comes from a live call...") drops to 0.88

---

## §4 — Music bed (right-sized)

**Codex flagged "music + SFX = slop trap."** Mitigation: simpler music, no SFX layer beyond natural ambient in the wildlife clip.

- **Single track, one mood.** No stitching, no mood swings. Ambient cinematic drone at ~80 BPM.
- **Volume curve simplified:**
  - 0:00–0:10 cold open: -16 dBFS (music carries)
  - 0:10–2:50 main: -28 dBFS (under VO consistently)
  - 2:50–3:00 close: fade out
- **No SFX layer.** Wildlife clip carries any natural ambient noise. No added gunshot, no whoosh transitions, no impact hits on the A2A arrows.

Picking: Pixabay Music, sort by "trending ambient" + filter ≥3 minutes, pick the first track with low BPM + no melodic earworm. Decision in ~5 minutes, no over-curation.

---

## §5 — B-roll (license-clean only)

Codex flagged Snapshot Serengeti clip licensing as "verify before use."

**Path of least friction:** Pexels free stock video. Search `"elephant"` filter by HD + free license. Pexels license = CC0-equivalent, no attribution required, commercial use OK.

Process: pick one 8-10 second clip. Crop to 1920x1080 if needed. Optionally desaturate -10%. NO slow-mo (codex flagged "trying too hard"). Use as-is.

Backup: Pixabay video (same license terms).

Snapshot Serengeti deferred — researching the per-clip license takes time we don't have, and the public dataset is image-only on closer reading anyway.

---

## §6 — Captions (P0, burned in)

No change from V2A plan. SRT generated from `segments.json`, burned in with ffmpeg `subtitles` filter.

Style: Inter 26pt white, 60% opacity black backdrop, bottom-center, 80px from edge. Standard, not branded — captions should disappear into the experience, not call attention.

---

## §7 — Acceptance tests (codex-revised)

| Test | Pass condition | Tester | When |
|---|---|---|---|
| Stranger lean-in | Show first 25s to 3 non-technical people. 3/3 say "yes, I'd watch the rest." | Omar asks | After v2 cut |
| Voice trust | Omar listens to chosen voice on proof beat. Trusts the speaker for a security/compliance report. | Omar | Before final voice gen |
| Fact-check | Every on-screen stat has a verifiable source. Every claim ("audit-grade", "files TNFD", "reproducible") survives a hostile read. | Omar + spot-check | Before submission |
| Runtime cap | Final MP4 ≤ 3:00 | ffprobe | At each assembly |
| Reproducibility | Re-run `POST /demo/run/multimodal_pipeline` after the video is locked. IDs in the new response match what's on-screen. | curl | Day-of submission |
| Mapbox renders | Local Ops Center shows map tiles + pin pulse + arrows + flyTo working before recording | Omar visual | Before T8 |
| IP audit | No third-party logos, screenshots, or copyrighted artwork in the final cut (other than our own Marketplace listing thumbnail) | Spot review | Before submission |

All 7 must pass.

---

## §8 — Order of execution (codex-corrected sequence + buffers)

```
PHASE 0 — Tokens + assets (asset-fetch pulled forward per codex)
0a. Omar pastes Mapbox token to .env.local            ← human, 2 min
0b. Pull wildlife b-roll from Pexels                  ← 10 min
0c. Pull music bed from Pixabay                       ← 10 min
0d. Fact-check 730+/$22T/$300B/CSRD claims, save URLs ← 15 min
0e. Copy ElevenLabs creds to repo .env.local           ← 2 min

PHASE 1 — Map (the dependency that unblocks recording)
1a. Add pulse + flyTo + arrow code to ReserveMap      ← 45 min
1b. npm run dev + visual smoke test                   ← 5 min
1c. Omar signs off on map behavior                    ← 5 min

PHASE 2 — Script lock (script first, recording later, per codex)
2a. Rewrite segments.json to Approach D storyboard    ← 30 min
2b. Update DEMO_SCRIPT.md to match                    ← 15 min

PHASE 3 — Voice
3a. Switch generate-voiceover.sh to ElevenLabs        ← 25 min
3b. 3-voice A/B on proof beat, Omar picks             ← 10 min
3c. Generate all segments at chosen voice             ← 5 min

PHASE 4 — Cinema assets
4a. Build punchline frame (filing-ID + reproducibility tagline) ← 20 min
4b. Crop/prep b-roll                                  ← 10 min
4c. Prep music bed (trim, fade)                       ← 10 min
4d. Update cards: hook stat with URL footnote, KPMG quote (text-only) ← 15 min

PHASE 5 — Recording
5a. Re-run Playwright recorder against localhost:3000 ← 10 min + 45-min RE-TAKE BUFFER per codex
5b. Verify footage has map + pin + arrows + acks       ← 5 min

PHASE 6 — Assembly + captions
6a. Upgrade assemble-video.sh: b-roll prep + music curve + caption burn ← 45 min
6b. First v2 assembly                                  ← 15 min

PHASE 7 — Review + ship
7a. Codex slop-detection pass on the cut + script     ← 20 min
7b. Apply codex findings + reassemble                 ← 30 min
7c. Stranger lean-in test                             ← variable
7d. Final IP / fact-check audit                       ← 15 min
7e. Submit                                            ← when ready

Total CC effort estimate (no re-take blowouts): ~5h 45m
With one major re-take blowout: ~6h 30m
With two: ~7h 15m (still well within 20-day calendar runway)
```

---

## §9 — Risks + mitigations (codex-revised)

| Risk | Likelihood | Mitigation |
|---|---|---|
| Mapbox token blocked or account issue | Low | Free tier, 2-min signup. Fallback: Leaflet/OpenStreetMap (no token, -1 polish point). |
| Map animation work breaks existing demo | Low | Recording is against `localhost:3000`, not Cloud Run. Live URL untouched. Zero production-deploy risk per codex correction. |
| ElevenLabs free-tier quota exhausted | Medium | ~3.5k chars × 3 voice samples = 10.5k chars, slightly over free 10k limit. Mitigation: use o22-studio's existing paid tier ($5 Creator) if needed. |
| Voice direction drifts to "AI sales-pitch" | Medium | Trust-based acceptance gate per codex correction. Stranger test catches sales-pitch tone. |
| Cumulative cinema over-cooks into "AI slop" | Medium | Codex review #2 (T10) explicitly hunts for this. Plus stranger lean-in test. |
| Fact-checking surfaces an inaccurate claim | Medium | T0d fact-check runs BEFORE script lock. Adjust language to match what we can actually source. Codex flagged this — taking it seriously. |
| Playwright re-record glitches | High | 45-min re-take buffer baked in per codex. 4 backup scenarios. |
| Final cut runs over 3:00 | Medium-Low | Total VO at speaking_rate 0.92 should land at ~2:55. Buffer in §8 phase 6 for tightening. |
| Submission deadline crunch | Low | 20 days of calendar runway from today (2026-05-16). Plan is ~6-8 CC hours. ~50x buffer. |

---

## §10 — Out of scope (unchanged)

- Live drone footage of real reserves
- Voice cloning of Omar
- Multiple language tracks
- Custom-composed score
- 4K resolution
- Real-time edits during voiceover recording
- KPMG report cover screenshot (codex-flagged IP risk; replaced with text-only quote)
- Cold-open gunshot SFX (codex-flagged sensationalism + slop risk)

---

## §11 — Implementation Tasks (Approach D)

- [ ] **T0a (P0, human: 2min)** — Omar pastes Mapbox `pk.eyJ...` token. Blocker.
- [ ] **T0b (P0, CC: 10min)** — content — Pull wildlife b-roll from Pexels. Save to `video-assets/broll/wildlife-coldopen.mp4`. Document URL + license.
- [ ] **T0c (P0, CC: 10min)** — content — Pull music bed from Pixabay. Save to `video-assets/music/`. Document.
- [ ] **T0d (P0, CC: 15min)** — research — Fact-check 730+/$22T/$300B/CSRD claims via WebSearch. Save citation URLs to `video-assets/citations.md`.
- [ ] **T0e (P0, CC: 2min)** — infra — Copy ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID from `/Users/odominguez7/Desktop/o22-studio/.env` to `GFS - guardIAn/.env.local`.
- [ ] **T1a (P0, CC: 45min)** — ops-center — Add pulse CSS keyframe + flyTo + animated arrow layer to `ReserveMap.tsx`. Files: `ops-center/src/components/ReserveMap.tsx`, `ops-center/src/app/globals.css`. Hardcode peer coords in `lib/reserves.ts`.
- [ ] **T1b (P0, CC: 5min)** — verify — `npm run dev`, click scenario, confirm map + pulse + arrows render. Screenshot the working state to `video-assets/verification/map-working.png`.
- [ ] **T1c (P0, human: 5min)** — Omar visual sign-off on local Ops Center. Hard gate.
- [ ] **T2a (P0, CC: 30min)** — scripts — Rewrite `segments.json` to Approach D storyboard (§1). Total VO target ≤ 2:55. Include SSML pause tags.
- [ ] **T2b (P0, CC: 15min)** — docs — Update `docs/DEMO_SCRIPT.md` to mirror Approach D.
- [ ] **T3a (P0, CC: 25min)** — scripts — Build `scripts/video/generate-voiceover-elevenlabs.sh`. Reads ELEVENLABS_API_KEY + VOICE_ID, hits `api.elevenlabs.io/v1/text-to-speech/{voice_id}`. Supports stability/similarity/style/speaking_rate from segments.json.
- [ ] **T3b (P1, human: 10min)** — Omar A/B test 3 voices on proof beat. Trust criterion, not detection criterion. Pick one.
- [ ] **T3c (P0, CC: 5min)** — scripts — Run ElevenLabs generator on all segments at chosen voice.
- [ ] **T4a (P0, CC: 20min)** — content — Build punchline frame HTML: large `TNFD-2026-A0192B2A32`, small `reproducible · POST /demo/run/multimodal_pipeline · github.com/odominguez7/guardian`. Render to PNG.
- [ ] **T4b (P0, CC: 10min)** — content — Crop b-roll to 1920x1080 + slight desaturation.
- [ ] **T4c (P0, CC: 10min)** — content — Trim music to 3:05, add 3-sec fade-in + 2-sec fade-out.
- [ ] **T4d (P0, CC: 15min)** — content — Update hook stat card (with URL footnote) + KPMG quote card (text-only, no cover screenshot). Regenerate PNGs.
- [ ] **T5a (P0, CC: 10min + 45min buffer)** — capture — Re-run Playwright recorder against `localhost:3000`. Reserve 45 minutes for re-takes per codex.
- [ ] **T5b (P0, CC: 5min)** — verify — Spot-check footage shows map tiles + pulse + arrows + ack cards.
- [ ] **T6a (P0, CC: 45min)** — scripts — Upgrade `assemble-video.sh`: layer b-roll, music with volume curve, punchline frame at 1:30, caption burn via ffmpeg `subtitles` filter.
- [ ] **T6b (P0, CC: 15min)** — build — First v2 assembly. Verify duration ≤ 3:00, audio matches video track.
- [ ] **T7a (P0, CC: 20min)** — review — Codex slop-detection pass on the v2 cut (visual review via key frames) + the script. Output: `reviews/CODEX_V2_CUT_REVIEW.md`.
- [ ] **T7b (P0, CC: 30min)** — fix — Apply codex findings, regenerate any segments that need it, reassemble.
- [ ] **T7c (P0, human: variable)** — Omar runs stranger lean-in test (3 people, first 25s). 3/3 pass required.
- [ ] **T7d (P0, CC: 15min)** — audit — Final IP + fact-check sweep on the locked cut. No third-party logos/screenshots beyond our Marketplace listing.
- [ ] **T7e (P0, human)** — Submit to Devpost.

---

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | CLEAR (SCOPE EXPANSION 2026-05-16, then SELECTIVE EXPANSION after codex correction) | Story-arc rebuild proposed; codex pushed back on pacing + claims; producer adopted Approach D synthesis. |
| Codex Review | `/codex review` (planreview prompt) | Independent 2nd opinion | 1 | CLEAR (4/10 on v2A, all 6 HARD FIX findings absorbed into Approach D) | 6 hard fixes: CSRD citation, KPMG IP, court-admissible claim, auto-files claim, fake-ID provability, A2A peer credibility. 4 medium: re-take budget, Cloud Build risk, last-60s overload, review buffer. All resolved. |
| Eng Review | `/plan-eng-review` | Architecture & tests | n/a | n/a | Video assembly is build-script work; ops-center map animation is ~80 LOC in an already-reviewed component. |
| Design Review | `/plan-design-review` | UI/UX gaps | n/a | n/a | Ops Center design previously reviewed; video storyboard reviewed in CEO + codex passes. |

**CODEX:** Codex outside-voice flagged 6 hard credibility landmines + 4 medium findings. All absorbed. Plan rewritten as Approach D: tighter pacing (product visible by 0:15 not 0:50), softened claims (audit-grade not court-admissible, "files TNFD" not "auto-files"), text-only KPMG citation (no cover screenshot), local-build Mapbox (no Cloud Build risk), 45-min re-take buffer, SOC 2 dropped.

**CROSS-MODEL:** CEO and codex disagreed on narrative weight (CEO: cinema-forward / codex: agents-forward). Producer-resolved toward codex's pacing with a light arc retained. Both reviewers now aligned on Approach D.

**UNRESOLVED:** Mapbox token from producer is the only outstanding dependency.

**VERDICT:** CEO + CODEX CLEARED — ready to execute Phase 0 (tokens + assets) on producer signal.
