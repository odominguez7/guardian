# GUARDIAN Demo Video Script — V2 / Approach D (3:00)

**Target:** GFS AI Agents Challenge submission, Track 3 (Marketplace + Gemini Enterprise).
**Deadline:** 2026-06-05 5pm PT.
**Producer credit:** Omar Dominguez Mondragon, CEO & Founder, GuardIAn Wildlife, MIT Sloan.
**Stack on-screen at end:** Gemini, ADK, A2A, Cloud Run, Vertex AI Search, BigQuery.
**Voice:** ElevenLabs (`eleven_multilingual_v2`), pick from 3-voice A/B at proof beat. Speaking rate 0.92 default.

**Live surfaces used:**
- Ops Center: https://guardian-ops-center-180171737110.us-central1.run.app (live submission target; recording done against `localhost:3000` with Mapbox token in `.env.local`)
- Orchestrator: https://guardian-180171737110.us-central1.run.app
- Agent card: `/a2a/app/.well-known/agent-card.json`
- Court-evidence HTML: `/demo/evidence/{incident_id}/html`
- Reproducibility endpoint (called on-screen): `POST /demo/run/multimodal_pipeline`

---

## Storyboard — Approach D (agents-first, light arc)

| Sec | Beat | Visual | VO | On-screen text / footnote |
|---|---|---|---|---|
| 0:00–0:06 | **Wildlife ambient** | Pexels 4K aerial elephant (`wildlife-coldopen.mp4`), cropped 1920×1080, -10% sat | — (silence; ambient from clip) | none |
| 0:06–0:10 | **Pretext** | Same clip continues. Single line of type: *"Conservation is a data problem."* Hold 2s, cut to black 0.5s | — | *"Conservation is a data problem."* |
| 0:10–0:18 | **Hook stat** | Black. White center type. | *"Seven hundred thirty-three companies. Twenty-two trillion dollars in assets. All committed to T-N-F-D biodiversity disclosure."* | *"733 companies. $22 trillion in assets. Committed to TNFD biodiversity disclosure."* · footnote `tnfd.global/engage/tnfd-adopters` |
| 0:18–0:25 | **KPMG quote** | Black. Italic center type, text-only (no cover image). | *"And as K-P-M-G found: three quarters of the world's largest at-risk companies still don't report it."* | *"Three quarters of the world's largest at-risk companies still don't report biodiversity loss." — KPMG* · footnote `KPMG Survey of Sustainability Reporting · biodiversity chapter` |
| 0:25–0:30 | **Reveal** | GUARDIAN wordmark 1s → fade into Ops Center idle wide, Africa map visible | *"GUARDIAN. Multi-agent biodiversity defense on Google Cloud."* | — |
| 0:30–0:42 | **Demo opens** | Cursor clicks `Full Multimodal Chain`. Mapbox `flyTo` from continent to Selous, 1500ms. Pulsing amber pin on Tag-22. Stream Watcher card appears. Audio Agent card slides up. | *"Camera-trap Tag twenty-two fires. Stream Watcher confirms a vehicle frame. Audio Agent classifies a gunshot at zero point nine three confidence."* | none |
| 0:42–0:55 | **Species ID + corpus RAG** | Species ID card. Pop-out highlights corpus lookup row: *Endangered · CITES Appendix I · TNFD material*. | *"Species I-D grounds the herd in the I-U-C-N corpus. Endangered. CITES Appendix One. Material under T-N-F-D."* | none |
| 0:55–1:20 | **A2A fan-out (centerpiece)** | 4 amber arrows draw from Selous to peer markers: Park Service (Dar es Salaam), Sponsor (London), Funder (Geneva), Neighbor Park (Maasai Mara). Each peer ack card lands under incident with real IDs: PSR-9737, TNFD-2026-A0192B2A32, FUND-A0192B2A32, MUTAID-A019282A32. | *"The orchestrator fans out to four independent A2A peers, each a separate service: Park Service. Sponsor Sustainability. Funder Reporter. Neighbor Park."* | Lower-third overlay: *"Each peer = separate Cloud Run service · github.com/odominguez7/guardian"* |
| 1:20–1:30 | **Demo close — evidence** | Cursor clicks evidence link. Court-evidence packet opens, scroll once. SHA-256 chain hash visible. | *"Twenty events. S-H-A two five six anchored. Audit-grade chain of custody."* | none |
| 1:30–1:50 | **Proof / reproducibility** | Punchline frame: large mono `TNFD-2026-A0192B2A32` centered; mono subline below | *(rate 0.88)* *"Every I-D on screen comes from a live call to a public endpoint. This is reproducible. Source on GitHub."* | Mono subline: *"reproducible · POST /demo/run/multimodal_pipeline · github.com/odominguez7/guardian"* |
| 1:50–2:25 | **Architecture** | Architecture diagram (`guardian-architecture.png`), slow Ken-Burns, callouts highlight as named | *(rate 0.95)* *"Five Cloud Run services. An A-D-K orchestrator on Gemini two point five Pro. Three in-house specialists. Four independent A2A peers run by four different organizations. Vertex AI Search grounding over I-U-C-N, CITES, and T-N-F-D. BigQuery audit trail. Cloud Trace on every agent call. One Marketplace install."* | none |
| 2:25–2:50 | **Business case** | 3 stats appear as VO names them; then Marketplace listing thumbnail | *"Fifty-eight trillion dollars of global G-D-P depends on nature. The E-U's C-S-R-D makes biodiversity disclosure mandatory under E-S-R-S E-four. GUARDIAN ships on Google Cloud Marketplace, through the channels procurement already trusts."* | Stats: *"$58T of global GDP depends on nature"* (PwC 2023) · *"EU CSRD · ESRS E4 mandatory"* · *"4 enterprise A2A peers shipped"* |
| 2:50–3:00 | **Producer close** | Filing-ID frame dimmed under credit overlay | *"Built by Omar Dominguez Mondragon. C-E-O and Founder, GuardIAn Wildlife. M-I-T Sloan."* | Credit overlay |

**Total runtime:** 3:00 exact.

---

## Claim register (NO overclaim — see `video-assets/citations.md`)

| Old (V1) wording | V2 / Approach D wording |
|---|---|
| "Court-admissible chain of custody" | "Audit-grade chain of custody" |
| "Auto-files TNFD entry you owe the regulator" | "Files the T-N-F-D entry" (no auto, no regulator-debt) |
| "Most can't even prove they have the data" | "Three quarters of the world's largest at-risk companies still don't report it." (KPMG actual finding) |
| "EU CSRD requires biodiversity disclosure from every Fortune 500" | "EU CSRD makes biodiversity disclosure mandatory under ESRS E4" |
| "$300B biodiversity reporting market" | "$58 trillion of global GDP depends on nature" (PwC 2023 / WEF 2020) |
| "SOC 2 readiness" | DROPPED |
| "Ninety seconds" end-to-end claim | DROPPED |

---

## Recording order (shoot what's stable first, edit into beats after)

| # | Source | Capture | Approx duration |
|---|---|---|---|
| 1 | `wildlife-coldopen.mp4` | Already in repo — no recording needed | 0:10 |
| 2 | Black cards | Hook stat + KPMG quote (HTML → PNG via existing card pipeline) | 0:15 |
| 3 | `localhost:3000` Ops Center | flyTo + scenario click → 4-peer fan-out → evidence packet scroll (via `record-demo.mjs` against localhost) | 0:60 |
| 4 | Punchline frame | New: `cards/02-proof-tnfd-id.html` → PNG | 0:20 |
| 5 | `guardian-architecture.png` | Already in repo — Ken-Burns in ffmpeg | 0:35 |
| 6 | Business cards | Stats + Marketplace thumbnail (HTML → PNG) | 0:25 |
| 7 | `99-close.html` | Already in repo | 0:10 |

---

## Cinema rules (codex-locked)

- **Music:** single ambient drone, no SFX layer, no whoosh, no stinger. Volume: -16 dBFS cold open → -28 dBFS under VO → fade-out 2:50–3:00.
- **Captions:** burned-in via ffmpeg `subtitles` filter. Inter 26pt white, 60% opacity black backdrop, bottom-center, 80px from bottom.
- **IP:** no third-party logos, screenshots, or cover images. Marketplace thumbnail = ours only.
- **No slow-mo on b-roll.** No "trying too hard."
- **Cap:** 3:00 hard. ffprobe each assembly to confirm.
