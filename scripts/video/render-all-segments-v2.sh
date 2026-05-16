#!/usr/bin/env bash
# Re-render all 12 demo voice segments with the chosen GUARDIAN-Design-1 voice
# and Omar-approved dynamic settings (preview-matched).
#
# Voice: VWMVKLErKOK9RBSdUWIw (Voice Design generative — "30yo SV founder, F500 narrator, MIT register")
# Model: eleven_multilingual_v2
# Settings: stability 0.40, similarity_boost 0.85, style 0.35, use_speaker_boost true
#
# Overwrites video-assets/voice-v2/*.mp3 — the prior Janet renders.
# Existing voice-v2 files are backed up to video-assets/voice-v2/_janet-archive/ first.
set -euo pipefail

cd "$(dirname "$0")/../.."
ENV_FILE="ops-center/.env.local"
[[ -f "$ENV_FILE" ]] || { echo "ERROR: $ENV_FILE missing"; exit 1; }
set -a; source "$ENV_FILE"; set +a

OUT="video-assets/voice-v2"
SEGMENTS="scripts/video/segments.json"
VOICE_ID="VWMVKLErKOK9RBSdUWIw"

# Archive Janet renders before overwriting
if ls "$OUT"/*.mp3 >/dev/null 2>&1; then
  mkdir -p "$OUT/_janet-archive"
  mv "$OUT"/*.mp3 "$OUT/_janet-archive/"
  echo "Archived $(ls $OUT/_janet-archive/*.mp3 | wc -l | tr -d ' ') Janet files to $OUT/_janet-archive/"
fi

# Render each segment
python3 <<'PY' > /tmp/segments-to-render.txt
import json
with open('scripts/video/segments.json') as f: data = json.load(f)
items = data.get('segments', data) if isinstance(data, dict) else data
for s in items:
    sid = s.get('id', '')
    text = s.get('text', '').strip()
    if sid and text:
        # write id|text on one line, tab-separated
        print(f"{sid}\t{text}")
PY

count=0
fail=0
while IFS=$'\t' read -r sid text; do
  [[ -z "$sid" ]] && continue
  payload=$(python3 -c "
import json, sys
print(json.dumps({
  'text': sys.argv[1],
  'model_id': 'eleven_multilingual_v2',
  'voice_settings': {
    'stability': 0.40,
    'similarity_boost': 0.85,
    'style': 0.35,
    'use_speaker_boost': True
  }
}))
" "$text")
  outfile="$OUT/$sid.mp3"
  http=$(curl -sS -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID?output_format=mp3_44100_128" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" \
    -H "Content-Type: application/json" \
    --max-time 120 \
    -d "$payload" \
    -o "$outfile" \
    -w "%{http_code}")
  if [[ "$http" == "200" ]] && file "$outfile" 2>/dev/null | grep -q "Audio"; then
    sz=$(wc -c < "$outfile" | tr -d ' ')
    dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$outfile" 2>/dev/null)
    printf "  ✓ %-22s %8s bytes  %4.1fs\n" "$sid" "$sz" "${dur:-0}"
    count=$((count+1))
  else
    printf "  ✗ %-22s HTTP %s — " "$sid" "$http"
    head -c 200 "$outfile" 2>/dev/null; echo
    fail=$((fail+1))
  fi
done < /tmp/segments-to-render.txt

echo ""
echo "=== Rendered $count segments, $fail failures ==="
ls -lah "$OUT"/*.mp3 | grep -v _janet-archive | awk '{printf "  %s  %s\n", $NF, $5}'
