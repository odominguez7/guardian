#!/usr/bin/env bash
# Render 3-beat audition gauntlet × 3 voices for GUARDIAN voice pick.
# Beats: 02-hook-stat / 03-kpmg-quote / 10-architecture (codex methodology).
# Voices: Brian / Bill L. Oxley / Declan Sage.
# Settings: codex-tuned narration — stability 0.55, similarity 0.80, style 0.0, speaker_boost true.
set -euo pipefail

cd "$(dirname "$0")/../.."
ENV_FILE="ops-center/.env.local"
[[ -f "$ENV_FILE" ]] || { echo "ERROR: $ENV_FILE missing" >&2; exit 1; }
set -a; source "$ENV_FILE"; set +a

OUT="video-assets/auditions"
mkdir -p "$OUT"

render_segment() {
  local voice_id="$1" seg_id="$2" outfile="$3"
  local payload
  payload=$(python3 <<PY
import json
segs = {
  '02-hook-stat': '<speak>Seven hundred T-N-F-D adopters. <break time="150ms"/> Trillions in assets under management.</speak>',
  '03-kpmg-quote': '<speak>K-P-M-G\\'s twenty twenty-four survey: <break time="250ms"/> disclosure has doubled, <break time="150ms"/> but half still don\\'t report biodiversity risk.</speak>',
  '10-architecture': '<speak>Five Cloud Run services. <break time="200ms"/> One A-D-K orchestrator on Gemini two point five Pro. <break time="200ms"/> Three specialists. <break time="200ms"/> Four independent A-two-A peers run by four different organizations. <break time="250ms"/> Vertex A-I Search grounding. <break time="150ms"/> Big Query audit trail. <break time="150ms"/> Cloud Trace on every agent call.</speak>',
}
print(json.dumps({
  'text': segs['$seg_id'],
  'model_id': 'eleven_multilingual_v2',
  'voice_settings': {
    'stability': 0.55,
    'similarity_boost': 0.80,
    'style': 0.0,
    'use_speaker_boost': True
  }
}))
PY
)
  local http
  http=$(curl -sS -X POST "https://api.elevenlabs.io/v1/text-to-speech/$voice_id?output_format=mp3_44100_128" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" \
    -H "Content-Type: application/json" \
    --max-time 90 \
    -d "$payload" \
    -o "$outfile" \
    -w "%{http_code}")
  if [[ "$http" == "200" ]] && file "$outfile" 2>/dev/null | grep -q "Audio"; then
    local sz; sz=$(wc -c < "$outfile" | tr -d ' ')
    printf "  ✓ %-32s %s bytes\n" "$(basename "$outfile")" "$sz"
    return 0
  else
    printf "  ✗ %-32s HTTP %s\n" "$(basename "$outfile")" "$http"
    head -c 300 "$outfile" >&2; echo >&2
    return 1
  fi
}

concat_voice() {
  local voice="$1"
  ffmpeg -y \
    -i "$OUT/${voice}-02-hook-stat.mp3" \
    -i "$OUT/${voice}-03-kpmg-quote.mp3" \
    -i "$OUT/${voice}-10-architecture.mp3" \
    -f lavfi -t 0.6 -i "anullsrc=channel_layout=mono:sample_rate=44100" \
    -filter_complex "[0:a][3:a][1:a][3:a][2:a]concat=n=5:v=0:a=1[out]" \
    -map "[out]" -ar 44100 -b:a 128k \
    "$OUT/${voice}-audition.mp3" 2>/dev/null
  local dur
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/${voice}-audition.mp3" 2>/dev/null)
  printf "  → %s-audition.mp3 (%.1fs)\n" "$voice" "${dur:-0}"
}

# Voice catalog
render_voice() {
  local name="$1" voice_id="$2"
  echo "=== Rendering $name ($voice_id) ==="
  render_segment "$voice_id" "02-hook-stat"    "$OUT/${name}-02-hook-stat.mp3"
  render_segment "$voice_id" "03-kpmg-quote"   "$OUT/${name}-03-kpmg-quote.mp3"
  render_segment "$voice_id" "10-architecture" "$OUT/${name}-10-architecture.mp3"
  concat_voice "$name"
}

render_voice "brian"  "nPczCjzI2devNBz1zQrb"
render_voice "bill"   "iiidtqDt9FBdT1vfBluA"
render_voice "declan" "kqVT88a5QfII1HNAEPTJ"

echo ""
echo "=== AUDITIONS READY ==="
ls -lah "$OUT"/*-audition.mp3 | awk '{print "  " $9 "  " $5}'
echo ""
echo "Play each:"
echo "  afplay $OUT/brian-audition.mp3"
echo "  afplay $OUT/bill-audition.mp3"
echo "  afplay $OUT/declan-audition.mp3"
