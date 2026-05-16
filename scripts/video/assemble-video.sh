#!/usr/bin/env bash
# Stitch the GUARDIAN demo video v1.
#
# Inputs:
#   video-assets/cards/*.png          1920x1080 still slides
#   video-assets/architecture/*.png   architecture diagram
#   video-assets/footage/ops-center-*.webm   Playwright recording
#   video-assets/voice/*.mp3          Chirp 3 HD voiceover segments
#
# Output:
#   video-assets/output/guardian-demo-v1.mp4
#
# Strategy: build a video track and an audio track separately, then mux.
#  - VIDEO: each segment is encoded to a uniform 1920x1080 30fps H.264 clip,
#    then concatenated via the concat demuxer (no re-encode of the join).
#  - AUDIO: voiceover MP3s are concatenated with silence padding for visual-only
#    beats (hook cards), then muxed onto the video.
#
# Re-runnable: deletes prior intermediates first.

set -euo pipefail
cd "$(dirname "$0")/../.."

OUT="video-assets/output"
TMP="video-assets/output/_tmp"
rm -rf "$TMP" && mkdir -p "$TMP" "$OUT"

CARDS="video-assets/cards"
ARCH="video-assets/architecture"
VOICE="video-assets/voice"
FOOTAGE_WEBM=$(ls -t video-assets/footage/ops-center-*.webm | head -1)
echo "Using footage: $FOOTAGE_WEBM"

# Common encode settings — keep uniform so concat demuxer works.
VENC=(-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black")

# Helper: render a still image into an N-second silent clip.
still_to_clip () {
  local img="$1" dur="$2" out="$3"
  ffmpeg -y -loglevel error -loop 1 -i "$img" -t "$dur" "${VENC[@]}" -an "$out"
}

# Helper: clip a section of a video and re-encode to uniform format.
trim_clip () {
  local src="$1" start="$2" dur="$3" out="$4"
  ffmpeg -y -loglevel error -ss "$start" -i "$src" -t "$dur" "${VENC[@]}" -an "$out"
}

echo "→ rendering still-image clips"
# Section timings (locked to the VO durations measured earlier):
still_to_clip "$CARDS/00-hook-beat-1.png"        3     "$TMP/v00.mp4"
still_to_clip "$CARDS/01-hook-beat-2-quote.png"  5     "$TMP/v01.mp4"
# 8s: card 01 lingers under "EU CSRD requires..." VO
still_to_clip "$CARDS/01-hook-beat-2-quote.png"  8.064 "$TMP/v02.mp4"
# Use first few seconds of footage as the "Ops Center idle" wide for the product beat
echo "→ trimming footage for product beat (idle wide)"
trim_clip "$FOOTAGE_WEBM" 0 22.656                "$TMP/v03.mp4"
# The live walkthrough — from t=6s (scenario about to fire) to end of footage.
# Demo VO 04..12 sums to 70.488s. Available footage from t=6s is ~58.5s. Stretch to fit.
# Approach: take all footage from t=6s, freeze the last frame to fill to 70.488s using tpad.
DEMO_VO_DUR=70.488
echo "→ extracting demo walkthrough section + freeze-frame pad to ${DEMO_VO_DUR}s"
ffmpeg -y -loglevel error -ss 6 -i "$FOOTAGE_WEBM" -filter:v "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,tpad=stop_mode=clone:stop_duration=20" -r 30 -t "$DEMO_VO_DUR" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -an "$TMP/v04-12.mp4"
# Architecture diagram still — held for 35.5s (length of arch VO)
still_to_clip "$ARCH/guardian-architecture.png"   35.544 "$TMP/v13.mp4"
# Business case card — held for 28.5s
still_to_clip "$CARDS/50-business-case.png"        28.488 "$TMP/v14.mp4"
# Close card — held for 17.2s
still_to_clip "$CARDS/99-close.png"                17.136 "$TMP/v15.mp4"

echo "→ concatenating video track"
{
  for v in v00 v01 v02 v03 v04-12 v13 v14 v15; do
    echo "file '$PWD/$TMP/$v.mp4'"
  done
} > "$TMP/concat-video.txt"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$TMP/concat-video.txt" -c copy "$TMP/video-track.mp4"
TOTAL_V=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$TMP/video-track.mp4")
echo "  video track duration: ${TOTAL_V}s"

# ---- AUDIO ----
# Audio timeline (matches the video segment list):
#   v00 (3s)      silence
#   v01 (5s)      silence  (let the quote breathe)
#   v02 (8.064s)  02-hook-vo
#   v03 (22.656s) 03-product
#   v04-12        04-demo-open .. 12-demo-evidence concatenated (~70.5s)
#   v13 (35.544s) 13-architecture
#   v14 (28.488s) 14-business
#   v15 (17.136s) 15-close

echo "→ building audio track"

# Generate silence padding clips at MP3 settings matching the VO (24kHz mono).
gen_silence () { local dur="$1" out="$2"
  ffmpeg -y -loglevel error -f lavfi -i anullsrc=channel_layout=mono:sample_rate=24000 -t "$dur" -c:a libmp3lame -b:a 128k "$out"
}
gen_silence 3      "$TMP/a-silence-3s.mp3"
gen_silence 5      "$TMP/a-silence-5s.mp3"

# Standardize all VO mp3s to the same codec parameters (already at 24kHz mono from TTS).
{
  echo "file '$PWD/$TMP/a-silence-3s.mp3'"      # v00
  echo "file '$PWD/$TMP/a-silence-5s.mp3'"      # v01 (quote breathing)
  echo "file '$PWD/$VOICE/02-hook-vo.mp3'"      # v02
  echo "file '$PWD/$VOICE/03-product.mp3'"      # v03
  for s in 04-demo-open 05-demo-audio 06-demo-species 07-demo-escalate 08-demo-park 09-demo-sponsor 10-demo-funder 11-demo-neighbor 12-demo-evidence; do
    echo "file '$PWD/$VOICE/$s.mp3'"
  done
  echo "file '$PWD/$VOICE/13-architecture.mp3'"
  echo "file '$PWD/$VOICE/14-business.mp3'"
  echo "file '$PWD/$VOICE/15-close.mp3'"
} > "$TMP/concat-audio.txt"

ffmpeg -y -loglevel error -f concat -safe 0 -i "$TMP/concat-audio.txt" -c:a libmp3lame -b:a 192k "$TMP/audio-track.mp3"
TOTAL_A=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$TMP/audio-track.mp3")
echo "  audio track duration: ${TOTAL_A}s"

# Mux
echo "→ muxing final video"
ffmpeg -y -loglevel error -i "$TMP/video-track.mp4" -i "$TMP/audio-track.mp3" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  "$OUT/guardian-demo-v1.mp4"

FINAL=$(ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT/guardian-demo-v1.mp4")
echo
echo "✓ $OUT/guardian-demo-v1.mp4"
echo "$FINAL"
ls -la "$OUT/guardian-demo-v1.mp4"
