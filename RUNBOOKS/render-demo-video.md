# Runbook — Render the 2-minute GUARDIAN demo video

**When to use:** v8 Day 8 of the master plan, then again whenever the brief changes.

**What you get:** 4 hook variants + 3 body shots + cover frame + Lyria music bed, all generated end-to-end by the vendored `tools/o22-render` pipeline (rev13 cinematic baseline) from one canonical brief at `briefs/guardian-hero.yaml`. Output lands in `tools/o22-render/validation/output/<run-id>/finished/`.

**Wall time:** ~10-15 minutes. **Spend:** $30-50 (Tier-1 Veo pricing, 4 variants).

---

## Pre-flight (one-time)

The o22 pipeline runs against the **o22-dev** GCP project, NOT against `guardian-gfs-2026`. It uses its own venv + secrets that are NOT vendored into the GUARDIAN repo. These steps run ONCE per dev machine.

```bash
# 1. Make sure the o22 submodule is checked out at rev13
cd "/Users/odominguez7/Desktop/GFS - guardIAn"
git submodule update --init --recursive tools/o22-render

# 2. Activate the o22 gcloud configuration (creates if missing)
bash tools/o22-render/RUNBOOKS/gcloud-config-setup.sh
# Should end with: ✅ O22 environment is live. Safe to deploy.

# 3. Set up the o22 Python venv
cd tools/o22-render
python -m venv .venv
source .venv/bin/activate
pip install -e .

# 4. Configure o22's secrets (ONE TIME — do not commit)
cp .env.example .env
$EDITOR .env   # set GCP_PROJECT=o22-dev, GCP_LOCATION=us-central1,
               # ELEVENLABS_API_KEY=<your key>

cd ../..
```

---

## Run the GUARDIAN render

```bash
cd "/Users/odominguez7/Desktop/GFS - guardIAn"
cd tools/o22-render
source .venv/bin/activate

# Dry-run first (no spend) to verify the brief parses + see cost projection
python validation/render_pack.py \
  --brief ../../briefs/guardian-hero.yaml \
  --dry-run

# Real render (paste --max-cost-usd that matches what you saw in dry-run + 20% buffer)
python validation/render_pack.py \
  --brief ../../briefs/guardian-hero.yaml \
  --max-cost-usd 50
```

Or via the Makefile shortcut:

```bash
make render-demo-video
```

---

## What "complete" looks like

```
tools/o22-render/validation/output/guardian-<timestamp>-<hex>/
├── brief.yaml                  (snapshot of briefs/guardian-hero.yaml at run time)
├── script.json                 (Gemini 2.5 Pro output: 4 hooks + 3 body shots + closing)
├── storyboard/                 (Imagen 4 reference PNGs)
├── character/                  (Nano Banana character-consistent PNGs)
├── veo/                        (raw silent Veo MP4s: 3 body + 4 hooks)
├── voice/                      (ElevenLabs WAVs: 1 body + 4 hook VOs)
├── audio/music.wav             (Lyria 2 music bed)
└── finished/
    ├── variant-A.mp4           THE 4 HOOK VARIANTS
    ├── variant-B.mp4
    ├── variant-C.mp4
    └── variant-D.mp4
```

---

## Day 9 — stitch the 2-min cut

Producer picks the strongest hook from finished/variant-*.mp4 and stitches with:
1. Screen recording of the GUARDIAN Ops Center (Live Cams → Spot Now → Mission Bridge fan-out)
2. Screen recording of the live demo URL while the agentic chain fires
3. The Veo body shots from validation/output/<run>/finished/variant-*.mp4

ffmpeg concat or producer's preferred NLE. The cut goes to `video-assets/guardian-demo-v8.mp4` and is the canonical Devpost video submission.

---

## Day 10 — producer review checkpoint

Producer + at least one stranger watch the cut end-to-end. The stranger should answer:
- "What does GUARDIAN do?"
- "Who is it for?"
- "What about it is unusual?"

If they hesitate on any of the three, recut the opening 20 seconds before Day 11 final approval.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `gcloud config configurations activate o22` fails | First-time setup not run | Run `tools/o22-render/RUNBOOKS/gcloud-config-setup.sh` |
| `quota exceeded` on Veo | Tier-1 limit hit | Wait 1 hour for window reset, OR file Tier-2 quota (already filed under Case 0d2ac776; approves ~2026-06-15) |
| Render hangs at Veo step | Async Veo polling stuck | `python validation/render_pack.py --kill` then re-run |
| `ELEVENLABS_API_KEY missing` | .env not populated | Re-check `tools/o22-render/.env` |
| Output frames look stylized/illustrated | wrong visual_style in brief | Confirm `visual_style: documentary` in `briefs/guardian-hero.yaml` |

---

## Producer responsibility

This is the ONE step in the v8 plan that intentionally requires human-supervised execution:
- Real Vertex AI spend ($30-50)
- Brand/quality judgment on the output
- Possibility the brief needs a re-render with revised prompts

Bot agents do not autonomously spend on Veo without supervised approval. Producer runs the command, watches the output, commits the final video to `video-assets/guardian-demo-v8.mp4`.
