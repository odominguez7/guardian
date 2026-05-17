#!/usr/bin/env bash
# Stitch the GUARDIAN demo video — V2 / Approach D (3:00).
#
# Inputs:
#   video-assets/cards/{00,01,02,50,99}.png   - V2 still slides (fact-checked)
#   video-assets/architecture/*.png           - architecture diagram
#   video-assets/broll/wildlife-coldopen-1080p.mp4
#   video-assets/footage/ops-center-*.webm    - Playwright recording of localhost (re-record after Mapbox token)
#   video-assets/voice-v2/*.mp3               - Chirp 3 voiceover (Approach D text)
#   video-assets/music/*.mp3                  - OPTIONAL ambient drone (if present)
#
# Output:
#   video-assets/output/guardian-demo-v2.mp4

set -euo pipefail
cd "$(dirname "$0")/../.."

OUT="video-assets/output"
TMP="$OUT/_tmp_v2"
rm -rf "$TMP" && mkdir -p "$TMP" "$OUT"

CARDS="video-assets/cards"
ARCH="video-assets/architecture"
VOICE="video-assets/voice-v2"
BROLL="video-assets/broll/wildlife-coldopen-1080p.mp4"
# Pin to the GOOD localhost recording that has full cinema (flyTo + 4 peer
# markers + arrows + incident card). Newer recordings broke after CSS
# changes — debugging deferred. The two known issues in this footage
# (auth banner top-right, "1 Issue" bubble bottom-left) are masked in
# assembly with black drawbox overlays (see VF_FOOTAGE_MASK below).
FOOTAGE_WEBM="${FOOTAGE_WEBM:-video-assets/footage/ops-center-2026-05-16T20-41-04.webm}"
[[ -f "$FOOTAGE_WEBM" ]] || FOOTAGE_WEBM=$(ls -t video-assets/footage/ops-center-*.webm 2>/dev/null | head -1 || echo "")
MUSIC=$(ls -t video-assets/music/*.mp3 2>/dev/null | head -1 || echo "")

echo "→ inputs"
echo "  cards   : $CARDS"
echo "  voice   : $VOICE"
echo "  b-roll  : $BROLL"
echo "  footage : ${FOOTAGE_WEBM:-MISSING}"
echo "  music   : ${MUSIC:-NONE (will use silence under VO)}"

if [[ ! -f "$BROLL" ]]; then
  echo "ERROR: $BROLL missing — run scripts/video/assemble helpers or download Pexels b-roll" >&2
  exit 1
fi
if [[ -z "$FOOTAGE_WEBM" || ! -f "$FOOTAGE_WEBM" ]]; then
  echo "WARNING: no ops-center footage found. Demo section will use a placeholder still (architecture diagram)." >&2
  FOOTAGE_WEBM=""
fi

# Common encode: uniform 1920x1080 30fps, yuv420p, for concat-without-reencode.
VF_PAD="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black"
VENC=(-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -vf "$VF_PAD")

# Helper: render a still image into an N-second silent clip.
still_to_clip () { local img="$1" dur="$2" out="$3"
  ffmpeg -y -loglevel error -loop 1 -i "$img" -t "$dur" "${VENC[@]}" -an "$out"
}

# Helper: still with Ken-Burns slow zoom (1.0 → 1.08 over duration)
still_kenburns () { local img="$1" dur="$2" out="$3"
  local frames=$(printf "%.0f" "$(echo "$dur*30" | bc -l)")
  ffmpeg -y -loglevel error -loop 1 -i "$img" -t "$dur" \
    -vf "scale=4000:-1,zoompan=z='min(zoom+0.0008,1.08)':d=$frames:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30,format=yuv420p" \
    -c:v libx264 -preset medium -crf 18 -an "$out"
}

# Helper: video clip → uniform format
re_encode_clip () { local src="$1" start="$2" dur="$3" out="$4"
  ffmpeg -y -loglevel error -ss "$start" -i "$src" -t "$dur" "${VENC[@]}" -an "$out"
}

# Helper: take wildlife clip and overlay a transparent PNG (text artwork) for the full duration
broll_with_overlay () { local src="$1" dur="$2" overlay_png="$3" out="$4"
  ffmpeg -y -loglevel error -i "$src" -loop 1 -t "$dur" -i "$overlay_png" -t "$dur" \
    -filter_complex "[0:v]$VF_PAD,eq=saturation=0.9[bg];[bg][1:v]overlay=0:0:format=auto:enable='between(t,1,$dur)'" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -an "$out"
}

# ── Beat timings per V2 / Approach D storyboard ──
# 0:00–0:06  wildlife ambient (b-roll)              6s
# 0:06–0:10  pretext text overlay on b-roll         4s
# 0:10–0:18  hook stat (00-hook-beat-1)             8s
# 0:18–0:25  KPMG quote (01-hook-beat-2-quote)      7s
# 0:25–0:30  reveal — wordmark + ops idle           5s
# 0:30–1:30  demo walkthrough                       60s
# 1:30–1:50  punchline (02-proof-tnfd-id)           20s
# 1:50–2:25  architecture                           35s
# 2:25–2:50  business case                          25s
# 2:50–3:00  close                                  10s

echo "→ rendering video clips"

# v00 — wildlife ambient (no text)
re_encode_clip "$BROLL" 0 6 "$TMP/v00.mp4"

# v01 — wildlife + "Conservation is a data problem." overlay (PNG art over b-roll)
broll_with_overlay "$BROLL" 4 "$CARDS/pretext-overlay.png" "$TMP/v01.mp4"

# v02 — hook stat
still_to_clip "$CARDS/00-hook-beat-1.png" 8 "$TMP/v02.mp4"

# v03 — KPMG quote
still_to_clip "$CARDS/01-hook-beat-2-quote.png" 7 "$TMP/v03.mp4"

# v04 — reveal: hold KPMG card 1s of fade-equivalent + ops idle 4s
# Without a clean "wordmark+idle" we approximate with the punchline-style title held — use existing close card briefly
still_to_clip "$CARDS/00-hook-beat-1.png" 1 "$TMP/v04a.mp4"
if [[ -n "$FOOTAGE_WEBM" ]]; then
  ffmpeg -y -loglevel error -ss 0 -i "$FOOTAGE_WEBM" -t 4 \
    -vf "$VF_PAD,drawbox=x=1430:y=0:w=490:h=44:color=black@1.0:t=fill,drawbox=x=0:y=985:w=200:h=95:color=black@1.0:t=fill" \
    -r 30 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -an "$TMP/v04b.mp4"
else
  still_to_clip "$ARCH/guardian-architecture.png" 4 "$TMP/v04b.mp4"
fi

# v05 — demo walkthrough (60s). Pull from t=6 in footage to skip dashboard load.
# Mask two known UI artifacts in the live recording:
#   - top-right auth banner: black box from x=1430,y=0 to x=1920,y=44
#   - bottom-left issues bubble: black box from x=0,y=h-95 to x=200,y=h
# Plus PLAN_V3.md Move 4.2 — telemetric HUD overlay in the bottom-right
# corner during the demo beat. Real numbers from the live multimodal_pipeline
# call (audio confidence 0.93, species_id 0.91, falsifier dissent severity
# 4 per Move 1's deterministic gate engine).
DEMO_DUR=60
FOOTAGE_MASK="drawbox=x=1430:y=0:w=490:h=44:color=black@1.0:t=fill,drawbox=x=0:y=985:w=200:h=95:color=black@1.0:t=fill"
# PLAN_V3.md Move 4.2 — telemetric HUD overlay. drawtext is unavailable in
# this ffmpeg build (libfreetype not linked); we pre-render the HUD as a
# transparent PNG via scripts/video/render-hud-overlay.py and overlay it
# with the (always-available) overlay filter. Regenerate the PNG before
# running this script if you change the HUD text.
HUD_PNG="$CARDS/hud-overlay.png"
if [[ -n "$FOOTAGE_WEBM" ]]; then
  if [[ -f "$HUD_PNG" ]]; then
    ffmpeg -y -loglevel error -ss 6 -i "$FOOTAGE_WEBM" -loop 1 -t "$DEMO_DUR" -i "$HUD_PNG" -t "$DEMO_DUR" \
      -filter_complex "[0:v]$VF_PAD,$FOOTAGE_MASK[bg];[bg][1:v]overlay=0:0:format=auto[v]" \
      -map "[v]" -r 30 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -an "$TMP/v05.mp4"
  else
    echo "  WARNING: HUD overlay missing; rendering demo without HUD. Run scripts/video/render-hud-overlay.py first."
    ffmpeg -y -loglevel error -ss 6 -i "$FOOTAGE_WEBM" -t "$DEMO_DUR" \
      -vf "$VF_PAD,$FOOTAGE_MASK,tpad=stop_mode=clone:stop_duration=30" -r 30 \
      -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -an "$TMP/v05.mp4"
  fi
else
  still_to_clip "$ARCH/guardian-architecture.png" "$DEMO_DUR" "$TMP/v05.mp4"
fi

# v06 — punchline frame (TNFD-2026-A0192B2A32)
still_to_clip "$CARDS/02-proof-tnfd-id.png" 20 "$TMP/v06.mp4"

# v07 — architecture (Ken-Burns slow zoom 35s)
still_kenburns "$ARCH/guardian-architecture.png" 35 "$TMP/v07.mp4"

# v08 — business case
still_to_clip "$CARDS/50-business-case.png" 25 "$TMP/v08.mp4"

# v09 — close
still_to_clip "$CARDS/99-close.png" 10 "$TMP/v09.mp4"

echo "→ concatenating video track"
{
  for v in v00 v01 v02 v03 v04a v04b v05 v06 v07 v08 v09; do
    echo "file '$PWD/$TMP/$v.mp4'"
  done
} > "$TMP/concat-video.txt"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$TMP/concat-video.txt" -c copy "$TMP/video-track.mp4"
TOTAL_V=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$TMP/video-track.mp4")
printf "  video track duration: %.2fs\n" "$TOTAL_V"

# ── AUDIO ──
echo "→ building audio track"

# Generate silence padding for visual-only beats and offsets.
gen_silence () { local dur="$1" out="$2"
  ffmpeg -y -loglevel error -f lavfi -i anullsrc=channel_layout=mono:sample_rate=24000 -t "$dur" -c:a libmp3lame -b:a 128k "$out"
}

# Approach D audio timeline:
#   v00 (6s)      silence (b-roll ambient retained later if music added)
#   v01 (4s)      silence (text + b-roll continues)
#   v02 (8s)      02-hook-stat.mp3        actual ~9.12s → trim or let bleed; we trim VO via -t
#   v03 (7s)      03-kpmg-quote.mp3       actual 7.08s ≈ on
#   v04a+v04b (5s) 04-reveal.mp3          actual 4.92s
#   v05 (60s)     concat: 05-demo-open + 06-demo-species + 07-demo-fanout + 08-demo-evidence (≈52s) + 8s silence pad
#   v06 (20s)     09-proof.mp3 (≈11s) + 9s silence
#   v07 (35s)     10-architecture.mp3 (≈18.6s) + 16.4s silence (music carries)
#   v08 (25s)     11-business.mp3 (≈23.2s) + 1.8s silence
#   v09 (10s)     12-close.mp3 (≈10.4s) — trim to 10s

gen_silence 6      "$TMP/a-silence-6s.mp3"
gen_silence 4      "$TMP/a-silence-4s.mp3"
gen_silence 0.2    "$TMP/a-pad-hook.mp3"          # 8s window − 7.8s hook VO
gen_silence 22.3   "$TMP/a-pad-demo.mp3"          # 60s window − (7.2+16.0+9.8+4.7) demo VOs
gen_silence 12.6   "$TMP/a-pad-proof.mp3"         # 20s window − 7.4s proof VO
gen_silence 6.6    "$TMP/a-pad-arch.mp3"          # 35s window − 28.4s arch VO
gen_silence 7.2    "$TMP/a-pad-business.mp3"     # 25s window − 17.8s business VO
gen_silence 4.1    "$TMP/a-pad-close.mp3"        # 10s window − 5.9s close VO

# 02-hook-stat is ~5s after tightening; we'll add a 3s silence pad after.
cp "$VOICE/02-hook-stat.mp3" "$TMP/a02.mp3"
# Architecture VO needs to fit but archives at 18.5s — pad after
# Close — clip to 10s exactly
ffmpeg -y -loglevel error -t 10 -i "$VOICE/12-close.mp3" -c:a libmp3lame -b:a 128k "$TMP/a09.mp3"

{
  echo "file '$PWD/$TMP/a-silence-6s.mp3'"           # v00
  echo "file '$PWD/$TMP/a-silence-4s.mp3'"           # v01
  echo "file '$PWD/$TMP/a02.mp3'"                    # v02 hook (5s VO)
  echo "file '$PWD/$TMP/a-pad-hook.mp3'"             #   + 3s silence = 8s
  echo "file '$PWD/$VOICE/03-kpmg-quote.mp3'"        # v03 KPMG (~7s)
  echo "file '$PWD/$VOICE/04-reveal.mp3'"            # v04 reveal (~5s)
  echo "file '$PWD/$VOICE/05-demo-open.mp3'"         # v05 demo (60s total)
  echo "file '$PWD/$VOICE/06-demo-species.mp3'"
  echo "file '$PWD/$VOICE/07-demo-fanout.mp3'"
  echo "file '$PWD/$VOICE/08-demo-evidence.mp3'"
  echo "file '$PWD/$TMP/a-pad-demo.mp3'"
  echo "file '$PWD/$VOICE/09-proof.mp3'"             # v06 (20s with pad)
  echo "file '$PWD/$TMP/a-pad-proof.mp3'"
  echo "file '$PWD/$VOICE/10-architecture.mp3'"      # v07 (35s with pad)
  echo "file '$PWD/$TMP/a-pad-arch.mp3'"
  echo "file '$PWD/$VOICE/11-business.mp3'"          # v08 (25s with pad)
  echo "file '$PWD/$TMP/a-pad-business.mp3'"
  echo "file '$PWD/$TMP/a09.mp3'"                    # v09 close VO (5.9s)
  echo "file '$PWD/$TMP/a-pad-close.mp3'"             # + 4.1s silence → 10s window
} > "$TMP/concat-audio.txt"

ffmpeg -y -loglevel error -f concat -safe 0 -i "$TMP/concat-audio.txt" -c:a libmp3lame -b:a 192k "$TMP/audio-vo.mp3"
TOTAL_A=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$TMP/audio-vo.mp3")
printf "  VO track duration: %.2fs\n" "$TOTAL_A"

# ── MUSIC MIX (Lyria 2 ambient bed at -28 dBFS — PLAN_V3.md Move 4.1) ──
# The Lyria bed is 30s; loop it across the full 178s output with a 3s fade-in
# at the start and 2s fade-out before the close beat. -28 dBFS sits below the
# VO so words stay legible while the bed adds atmospheric weight.
if [[ -n "$MUSIC" && -f "$MUSIC" ]]; then
  echo "→ mixing Lyria 2 ambient bed under VO (loops 30s bed across full runtime)"
  # normalize=0 disables amix's auto-division-by-input-count so the music
  # stays at its target -22 dBFS instead of being halved to -28 dBFS by
  # the mix (PLAN_V3.md Move 4.1 — initial mix had bed at -65 dB mean,
  # below audibility on most speakers).
  ffmpeg -y -loglevel error -stream_loop -1 -i "$MUSIC" -i "$TMP/audio-vo.mp3" -filter_complex \
    "[0:a]volume=-22dB,afade=t=in:st=0:d=3,afade=t=out:st=176:d=2,atrim=0:180[mus]; \
     [1:a]volume=0dB[vo]; \
     [mus][vo]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mix]" \
    -map "[mix]" -c:a libmp3lame -b:a 192k "$TMP/audio-track.mp3"
else
  cp "$TMP/audio-vo.mp3" "$TMP/audio-track.mp3"
fi

# ── CAPTIONS (burned-in) ──
# Build SRT from segments.json text + segment timings.
echo "→ generating captions SRT"
python3 <<'PY' > "$TMP/captions.srt"
import json, datetime
cfg = json.load(open("scripts/video/segments.json"))
# Beat timing: cumulative.
beats = [
  ("00-coldopen-ambient", 6, ""),
  ("01-pretext",          4, ""),
  ("02-hook-stat",        8, None),
  ("03-kpmg-quote",       7, None),
  ("04-reveal",           5, None),
  ("05-demo-open",       12, None),
  ("06-demo-species",    13, None),
  ("07-demo-fanout",     25, None),
  ("08-demo-evidence",   10, None),
  ("09-proof",           20, None),
  ("10-architecture",    35, None),
  ("11-business",        25, None),
  ("12-close",           10, None),
]
by_id = {s["id"]: s for s in cfg["segments"]}
def ts(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    ms = int(round((s - int(s)) * 1000))
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{ms:03d}"
t0 = 0
idx = 1
import re
strip = re.compile(r"<[^>]+>")
for sid, dur, _ in beats:
    seg = by_id[sid]
    text = (seg.get("text") or "").strip()
    text = strip.sub("", text).strip()
    if not text:
        t0 += dur; continue
    # Use VO actual length (cap at beat duration)
    start = t0
    end = t0 + dur
    print(idx); idx += 1
    print(f"{ts(start)} --> {ts(end)}")
    # word-wrap to ~50 chars
    words = text.split()
    line = ""; lines = []
    for w in words:
        if len(line) + len(w) + 1 > 50:
            lines.append(line.rstrip()); line = w + " "
        else:
            line += w + " "
    if line.strip(): lines.append(line.rstrip())
    print("\n".join(lines))
    print()
    t0 += dur
PY

# ── MUX with optional burned-in subtitles ──
SUBFILE="$TMP/captions.srt"
BURN_SUBS="${BURN_SUBS:-1}"   # set BURN_SUBS=0 to skip
echo "→ muxing"
if [[ "$BURN_SUBS" = "1" && -s "$SUBFILE" ]]; then
  # Use subtitles filter with styling
  STYLE="FontName=Helvetica,FontSize=11,PrimaryColour=&HFFFFFF&,BorderStyle=4,BackColour=&H80000000,Outline=0,Shadow=0,MarginV=60,Alignment=2"
  ffmpeg -y -loglevel error -i "$TMP/video-track.mp4" -i "$TMP/audio-track.mp3" \
    -vf "subtitles='$SUBFILE':force_style='$STYLE'" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -shortest "$OUT/guardian-demo-v2.mp4"
else
  ffmpeg -y -loglevel error -i "$TMP/video-track.mp4" -i "$TMP/audio-track.mp3" \
    -c:v copy -c:a aac -b:a 192k -shortest "$OUT/guardian-demo-v2.mp4"
fi

echo
FINAL=$(ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT/guardian-demo-v2.mp4")
echo "✓ $OUT/guardian-demo-v2.mp4"
echo "$FINAL"
ls -la "$OUT/guardian-demo-v2.mp4"
