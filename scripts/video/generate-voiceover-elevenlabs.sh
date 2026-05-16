#!/usr/bin/env bash
# Generate per-segment voiceover MP3s from segments.json via ElevenLabs TTS.
# Reads ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID from ops-center/.env.local.
# Output: video-assets/voice/<segment-id>.mp3
#
# Usage:
#   scripts/video/generate-voiceover-elevenlabs.sh                    # all segments
#   VOICE_ID=brian   scripts/video/generate-voiceover-elevenlabs.sh   # override voice
#   ONLY=09-proof    scripts/video/generate-voiceover-elevenlabs.sh   # single segment (for A/B)
set -euo pipefail

cd "$(dirname "$0")/../.."
SEGMENTS_FILE="scripts/video/segments.json"
OUT_DIR="video-assets/voice-v2"
ENV_FILE="ops-center/.env.local"

mkdir -p "$OUT_DIR"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: $ENV_FILE not found. Copy ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID there." >&2
  exit 1
fi

# Load .env.local
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

# Allow VOICE_ID override (for A/B testing — Brian, Daniel, Antoni etc.)
VOICE_ID="${VOICE_ID:-${ELEVENLABS_VOICE_ID:-}}"
API_KEY="${ELEVENLABS_API_KEY:-}"

if [[ -z "$API_KEY" || -z "$VOICE_ID" ]]; then
  echo "ERROR: ELEVENLABS_API_KEY or ELEVENLABS_VOICE_ID missing from $ENV_FILE" >&2
  exit 1
fi

ONLY="${ONLY:-}"

python3 <<PY
import json, os, sys, subprocess, urllib.request, urllib.error

cfg = json.load(open("$SEGMENTS_FILE"))
api_key = "$API_KEY"
voice_id = "$VOICE_ID"
out_dir  = "$OUT_DIR"
only     = "$ONLY".strip()

defaults = cfg.get("default_voice_settings", {})
model_id = cfg.get("model_id", "eleven_multilingual_v2")

ok = skip = fail = 0
for seg in cfg["segments"]:
    sid = seg["id"]
    if only and sid != only:
        continue
    text = (seg.get("text") or "").strip()
    if seg.get("skip_tts") or not text:
        print(f"[skip] {sid}  visual-only beat")
        skip += 1
        continue
    # Merge default voice settings with per-segment override
    settings = dict(defaults)
    settings.update(seg.get("voice_settings_override", {}))

    # ElevenLabs voice_settings keys: stability, similarity_boost, style, use_speaker_boost, speed
    # NB: ElevenLabs uses "speed" (0.7-1.2), not "speaking_rate" — map it.
    el_settings = {
        "stability": settings.get("stability", 0.5),
        "similarity_boost": settings.get("similarity_boost", 0.75),
        "style": settings.get("style", 0.15),
        "use_speaker_boost": settings.get("use_speaker_boost", True),
        "speed": settings.get("speaking_rate", 0.92),
    }
    body = {
        "text": text,
        "model_id": model_id,
        "voice_settings": el_settings,
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    out_path = os.path.join(out_dir, f"{sid}.mp3")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            audio = resp.read()
        with open(out_path, "wb") as f:
            f.write(audio)
        dur = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", out_path],
            capture_output=True, text=True
        ).stdout.strip()
        target = seg.get("duration_target_s", "?")
        print(f"[ok]   {sid}  {len(audio):>7} bytes  {dur}s  (target {target}s, rate {el_settings['speed']})")
        ok += 1
    except urllib.error.HTTPError as e:
        print(f"[FAIL] {sid}  HTTP {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        fail += 1
    except Exception as e:
        print(f"[FAIL] {sid}  {e}", file=sys.stderr)
        fail += 1

print(f"\\n{ok} synthesized, {skip} silent/visual, {fail} failed")
sys.exit(1 if fail else 0)
PY
