# GUARDIAN Demo Video — Asset Pack

Everything staged for the 3-minute submission video. Pressing record on the Ops Center is the only step that needs a human.

## What's here

```
video-assets/
├── README.md                          ← this file
├── cards/                             ← text-card slides (rendered at 1920x1080)
│   ├── 00-hook-beat-1.{html,png}      0:00–0:03  "730+ companies. $22T."
│   ├── 01-hook-beat-2-quote.{html,png}0:03–0:08  KPMG quote
│   ├── 50-business-case.{html,png}    2:15–2:45  $300B · F500 · 4 peers
│   └── 99-close.{html,png}            2:45–3:00  ask + producer credit
├── architecture/
│   ├── guardian-architecture.mmd      source (Mermaid)
│   ├── guardian-architecture.html     CDN-rendered wrapper
│   └── guardian-architecture.png      1920x1080 still for §4 (1:45–2:15)
└── receipts/                          ← real outputs from the live orchestrator
    ├── scenario_multimodal_response.json
    ├── court_evidence_bundle.json
    └── court_evidence_packet.html     33 KB, opens in any browser
```

## The dry-run incident (use these IDs in voiceover and lower-thirds)

```
Incident ID:        GU-466F7A6FA1F3
Bundle ID:          CHN-2026-A0192B2A32
Chain hash (SHA-256): 6d014032ea2acdbaab7cf44ea03a659ce17bd710f0ae292a8aa87752daee2e18
Park dispatch:      PSR-9737, ETA 8 min, severity critical
TNFD filing:        TNFD-2026-A0192B2A32  (filed into CSRD-ESRS-E4)
Funder receipt:     FUND-2026-A0192B2A32  (elephants_at_risk program)
Cross-border:       MUTAID-2026-A0192B2A32  (Selous → Maasai Mara)
Events captured:    20
Peer acks:          4
Species:            African elephant (Endangered, CITES Appendix I)
Location:           Selous Game Reserve, Tag-22 camera (Tanzania)
```

Every ID above came from a real `POST /demo/run/multimodal_pipeline` and a real
`GET /demo/evidence/.../html` against the production Cloud Run service. Same
seed reproduces the same IDs — re-fire safely.

## Recording checklist (when ready to press record)

1. Quit any extension that overlays the browser. Use Chrome incognito.
2. Browser zoom 100%. Hide bookmarks bar. Window 1920x1080.
3. Open https://guardian-ops-center-180171737110.us-central1.run.app once to
   warm Cloud Run (first hit was 5.4s cold today). Wait for the dashboard to
   show "Connected". Leave the tab idle ~30 seconds, then refresh once.
4. Roll screen capture. Wait 2 seconds idle, then click the
   `Full Multimodal Chain — Selous gunshot + elephant herd` button.
5. Let the chain play out fully (about 45 seconds end to end). Don't cut early
   — judges watch for the *Neighbor Park* cross-border card, it's the
   differentiator over single-peer demos.
6. Cursor click into the evidence link, scroll once, top to bottom.
7. Three takes minimum. Voiceover goes on after the cleanest take, not live.
8. If `/demo/run` returns a cooldown error, wait 15 seconds or pick a
   different scenario (`audio_gunshot`, `sponsored_species`, `poacher_truck`).

## How to use the cards in the edit

The PNG cards are 1920x1080 transparent-on-black. Drop them on V2 over the
black-frame transitions in your NLE. Hold for the duration in the script
(`docs/DEMO_SCRIPT.md` §1, §5, §6). No Ken-Burns needed; the type was already
sized for hold-still.

## How to use the receipts

`court_evidence_packet.html` opens standalone. Use it for:
- §3 closing beat: cursor-click from Ops Center → packet opens → scroll once
- §5 cutaway: lower-third overlay showing `TNFD-2026-A0192B2A32` filing ID
  pulled from `scenario_multimodal_response.json`

## Re-render any card

```bash
# from repo root
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu --window-size=1920,1080 --hide-scrollbars \
  --screenshot=video-assets/cards/01-hook-beat-2-quote.png \
  "file://$PWD/video-assets/cards/01-hook-beat-2-quote.html"
```

Architecture diagram needs `--virtual-time-budget=4000` because Mermaid hits a CDN.
