#!/usr/bin/env bash
# Generate per-segment voiceover MP3s from segments.json via Google Cloud TTS Chirp 3 HD.
# Supports: SSML text, skip_tts flag, per-segment speaking_rate override.
# Output: video-assets/voice-v2/<segment-id>.mp3
set -euo pipefail

cd "$(dirname "$0")/../.."
SEGMENTS_FILE="scripts/video/segments.json"
OUT_DIR="video-assets/voice-v2"
PROJECT="guardian-gfs-2026"

mkdir -p "$OUT_DIR"

ONLY="${ONLY:-}"
VOICE_OVERRIDE="${VOICE:-}"

TOKEN=$(gcloud auth print-access-token)

python3 <<PY
import json, os, base64, subprocess, sys, urllib.request, urllib.error

cfg = json.load(open("$SEGMENTS_FILE"))
token = "$TOKEN"
project = "$PROJECT"
out_dir = "$OUT_DIR"
only = "$ONLY".strip()
voice_override = "$VOICE_OVERRIDE".strip()

base_voice = voice_override or cfg.get("voice", "en-US-Chirp3-HD-Charon")
lang = cfg.get("languageCode", "en-US")
base_rate = float(cfg.get("speakingRate", 0.92))
pitch = float(cfg.get("pitch", 0.0))

ok = skip = fail = 0
for seg in cfg["segments"]:
    sid = seg["id"]
    if only and sid != only:
        continue
    text = (seg.get("text") or "").strip()
    out_path = os.path.join(out_dir, f"{sid}.mp3")
    if seg.get("skip_tts") or not text:
        print(f"[skip] {sid}  visual-only beat")
        skip += 1
        continue

    # per-segment speaking rate override (e.g. 0.88 on punchline)
    rate = float(seg.get("voice_settings_override", {}).get("speaking_rate", base_rate))

    # SSML vs plain — strip <speak> wrapper since Chirp 3 takes ssml field
    is_ssml = text.startswith("<speak")
    input_block = {"ssml": text} if is_ssml else {"text": text}

    body = {
        "input": input_block,
        "voice": {"languageCode": lang, "name": base_voice},
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": rate,
            "pitch": pitch,
            "sampleRateHertz": 24000,
        },
    }
    req = urllib.request.Request(
        "https://texttospeech.googleapis.com/v1/text:synthesize",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": project,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        audio = base64.b64decode(data["audioContent"])
        with open(out_path, "wb") as f:
            f.write(audio)
        dur = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", out_path],
            capture_output=True, text=True
        ).stdout.strip()
        target = seg.get("duration_target_s", "?")
        print(f"[ok]   {sid}  {len(audio):>7} bytes  {dur}s  (target {target}s, rate {rate})")
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
