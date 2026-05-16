# CODEX V2 CUT REVIEW — GUARDIAN (Adversarial Pass)

Overall judgment: **DO NOT SHIP YET**. You are close, but there are several credibility landmines that must be fixed to avoid judge skepticism. Once P0s are cleared, I expect a **ship-it**.

---

## HARD FIX (P0 — must change before submission)

1) **Top-right “ANONYMOUS DEMO – FIREBASE AUTH NOT CONFIGURED” banner**
- **Beat/file:** Demo frames (see `video-assets/output/v2b-frame-50s.jpg`, `v2b-frame-75s.jpg`)
- **Why:** Reads as broken/incomplete product; kills enterprise trust.
- **Exact fix:** Hide the banner in the UI for recording (set `FIREBASE_AUTH` to configured or gate the label behind a dev flag) or crop the top 24–32px off the recording. Re-record demo section.

2) **Bottom-left red “2 issues” bubble**
- **Beat/file:** Demo frames (see `video-assets/output/v2b-frame-50s.jpg`, `v2b-frame-75s.jpg`)
- **Why:** Looks like an error state; invites doubt.
- **Exact fix:** Disable the issues indicator for demo mode or crop left/bottom so it’s not visible. Re-record demo section.

3) **Hook stat misframes TNFD AUM**
- **Beat/file:** Hook card + VO (`docs/DEMO_SCRIPT.md`, `scripts/video/segments.json` id `02-hook-stat`; keyframe `v2-keyframes-02.jpg`)
- **Why:** TNFD’s $22.4T AUM applies to financial institution adopters, not all 733 organizations. Current wording implies all adopters hold $22T.
- **Exact fix (on-screen):**
  - Replace with: **“733 TNFD adopters. 179 financial institutions with $22.4T AUM.”**
  - Footnote remains `tnfd.global/engage/tnfd-adopters`.
- **Exact fix (VO):** “Seven hundred thirty-three TNFD adopters, including financial institutions representing twenty-two trillion dollars in assets under management.”

4) **KPMG “three quarters still don’t report” is stale without year**
- **Beat/file:** KPMG card + VO (`docs/DEMO_SCRIPT.md`, `scripts/video/segments.json` id `03-kpmg-quote`)
- **Why:** KPMG 2024 shows ~49% disclosure (about half still don’t). “Three quarters” reads outdated unless year-stamped.
- **Exact fix (preferred, current):**
  - On-screen: **“KPMG 2024: 49% now disclose biodiversity risk — about half still don’t.”**
  - VO: “KPMG’s 2024 survey shows disclosure has doubled — but about half still don’t report biodiversity risk.”
- **If you keep 75%:** add **“(KPMG 2020/2022)”** explicitly on-screen and in VO to avoid stale-claim risk.

5) **Proof card overclaim: “FILED UNDER EU CSRD · ESRS E4”**
- **Beat/file:** Punchline frame (`video-assets/output/v2-keyframes-09.jpg`)
- **Why:** Implies an actual regulatory filing, which you are not doing. Also conflicts with materiality + phase-in relief.
- **Exact fix:** Remove the top line entirely, or change to **“Mapped to ESRS E4 (materiality assessed)”**.

6) **Reproducibility claim unverified**
- **Beat/file:** Proof beat + VO (`scripts/video/segments.json` id `09-proof`)
- **Why:** The review request explicitly asks to verify the endpoint returns the on-screen ID. I attempted:
  - `curl -X POST https://guardian-180171737110.us-central1.run.app/demo/run/multimodal_pipeline`
  - Result: failed locally (DNS/network). I could not verify determinism.
- **Exact fix:** **Before shipping**, run the POST and confirm the ID is deterministic. If not deterministic, change wording to:
  - On-screen: **“IDs generated from live calls to a public endpoint (see /demo/run/multimodal_pipeline)”**
  - VO: “Every ID on screen comes from a live call to a public endpoint. Verifiable on GitHub.”

7) **ID mismatch in demo vs script**
- **Beat/file:** Demo UI card IDs in frame vs script (`docs/DEMO_SCRIPT.md`, `scripts/video/segments.json` id `07-demo-fanout`)
- **Why:** Demo frame shows **PSR-5280** and **MUTAID-2026-A0192B2A32**; script claims **PSR-9737** and **MUTAID-A019282A32** (typo/mismatch).
- **Exact fix:** Update script + cards to match actual on-screen IDs, or re-run demo so IDs match the script. Keep all IDs consistent across VO, UI, and proof frame.

---

## STRONG SUGGEST (P1 — change unless impossible)

1) **Product visible by 0:15**
- **Beat/file:** Timeline (0:00–0:25) in `docs/DEMO_SCRIPT.md`
- **Why:** Current cut reveals product at 0:25; earlier codex guidance was product visible by 0:15 to avoid “long preamble.”
- **Fix:** Move the KPMG card after the reveal (or shorten hook+quote) so Ops Center appears by ~0:15.

2) **CSRD/ESRS E4 phrasing too absolute**
- **Beat/file:** Business case card + VO (`scripts/video/segments.json` id `11-business`; keyframe `v2-keyframes-13.jpg`)
- **Why:** “ESRS E4 mandatory” ignores materiality and 2025–2026 phase-in relief.
- **Fix (on-screen):** “CSRD + ESRS E4 (materiality-based; E4 can be deferred FY25–26)”
- **Fix (VO):** “CSRD requires biodiversity disclosure where material; ESRS E4 can be phased in through FY 2026.”

3) **No-music-bed risk**
- **Beat/file:** Entire cut
- **Why:** Pure VO over silence can feel synthetic. A subtle ambient bed reduces “AI voice in a void.”
- **Fix:** Add a single low drone track at -28 dBFS (no SFX). If licensing is blocked, keep silence but avoid abrupt gaps with gentle room tone.

4) **Architecture Ken Burns feels static**
- **Beat/file:** Architecture beat (`v2-keyframes-10/11/12.jpg`)
- **Why:** A slow zoom on a static diagram can read like a slide deck.
- **Fix:** Add gentle node highlight pulses or staggered callout emphasis to show motion, or cut 5–7 seconds and speed the zoom.

5) **VO phrasing that reads “LLM-ish”**
- **Beat/file:** Demo VO (`scripts/video/segments.json` ids `05`, `06`, `08`)
- **Why:** Phrases like “classifies a gunshot at zero point nine three confidence” feel machine-like.
- **Fix:** Tighten to: “Audio Agent flags a gunshot (0.93).” and “SHA‑256 anchored chain of custody.”

---

## NICE TO HAVE (P2 — log only)

1) **Wildlife cold open is clearly stock**
- **Beat/file:** `video-assets/output/v2-keyframes-01.jpg`
- **Fix:** Add a subtle location label (“Selous, Tanzania”) or a 3–5% film grain to reduce stock feel.

2) **Founder credit risk of self‑promo**
- **Beat/file:** Close card (`v2-keyframes-15.jpg`)
- **Fix:** Optional trim to “Omar Dominguez Mondragon — GuardIAn Wildlife” if you want a more neutral close.

---

## CLEAR (validated / looks good)

- Demo map visuals and A2A fan‑out are legible and cinematic; the “money shot” at ~50s reads clean and impressive.
- Card typography and hierarchy are clean; no obvious AI‑generated typeface slop.
- Hook stat card (layout only) is strong and minimal once the wording is corrected.
- Proof frame composition is strong; the mono ID is readable and feels “forensic.”
- Overall pacing of the 60s demo block is solid (not too long once the P0 fixes are in).

---

### Bottom line
Fix the P0 items, especially the on-screen UI errors, the TNFD AUM framing, and the KPMG wording. After those, this is **ship‑ready**.
