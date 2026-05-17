# Copyright 2026 GUARDIAN
# Live-cam frame extraction — pulls a REAL current frame from a YouTube
# live HLS stream.
#
# Why this exists (producer caught the bug 2026-05-17):
# The v6 path used `https://i.ytimg.com/vi/<id>/maxresdefault_live.jpg`
# expecting it to be a live-updating thumbnail. It is NOT — that URL serves
# a static poster YouTube cached when the broadcast started, and YouTube
# CDN ignores cache-buster query params. Verified by hashing the URL three
# times across 24s and getting identical bytes. Gemini Vision was
# analyzing the same poster image every "Spot Now" click. Producer
# correctly flagged a fox on screen vs Gemini reporting ostriches.
#
# The v7 fix: resolve the HLS m3u8 manifest with yt-dlp, ask ffmpeg to
# decode exactly one frame to JPEG, return the raw bytes. The caller hands
# those bytes to Gemini Vision as inline data. Every call gets a frame
# that is at most a few seconds stale.
#
# Latency budget on Cloud Run (4Gi, us-central1, NamibiaCam tested):
#   yt-dlp manifest resolve : ~600ms cold, ~50ms warm (cached 60s)
#   ffmpeg single-frame     : ~800-1500ms
#   Total                   : ~1.5-2.5s before the Gemini call.
#
# Fallback: on any subprocess failure (network blip, manifest expired,
# ffmpeg OOM), returns None. Caller logs the failure and degrades to the
# legacy poster path so the demo never fully breaks.

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import time
from threading import Lock

logger = logging.getLogger(__name__)

# Restrict youtube_id to the documented YouTube id alphabet so we never
# pass user-controlled bytes into subprocess argv. The 11-char id is
# canonical; allow a small tolerance for legacy/short ids.
_YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,16}$")

# Cache resolved HLS manifest URLs for ~60s per youtube_id. HLS manifests
# are valid for ~6h but the segment list rolls fast enough that ffmpeg
# wants a fresh manifest each call; 60s is the right balance between
# yt-dlp latency saved and segment staleness.
_MANIFEST_TTL_S = 60.0
_manifest_cache: dict[str, tuple[float, str]] = {}
_manifest_lock = Lock()


def _resolve_hls_manifest(youtube_id: str, timeout_s: float = 6.0) -> str | None:
    """Use yt-dlp to resolve the HLS m3u8 manifest URL for a live video.

    Returns the URL on success, None on failure (logged at WARNING).
    Cached for _MANIFEST_TTL_S to absorb back-to-back Spot Now clicks.
    """
    now = time.monotonic()
    with _manifest_lock:
        cached = _manifest_cache.get(youtube_id)
        if cached and now - cached[0] < _MANIFEST_TTL_S:
            return cached[1]

    yt_url = f"https://www.youtube.com/watch?v={youtube_id}"
    try:
        # -g    : print the direct URL and exit (no download)
        # -f    : prefer 480p HLS so the segment is small + decodes fast
        # --no-warnings keeps stderr clean for our logger
        result = subprocess.run(
            [
                "yt-dlp",
                "-g",
                "-f",
                "best[protocol^=m3u8][height<=480]/best[protocol^=m3u8]/best",
                "--no-warnings",
                "--no-playlist",
                yt_url,
            ],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        logger.warning("livecam_frame: yt-dlp timed out for %s", youtube_id)
        return None
    except FileNotFoundError:
        logger.warning("livecam_frame: yt-dlp binary not on PATH")
        return None
    except OSError as e:
        logger.warning("livecam_frame: yt-dlp launch failed: %s", e)
        return None

    if result.returncode != 0:
        logger.warning(
            "livecam_frame: yt-dlp non-zero for %s: %s",
            youtube_id,
            (result.stderr or "")[:300],
        )
        return None

    # yt-dlp prints one URL per output stream; for HLS we take the first.
    candidate = (result.stdout or "").splitlines()[0].strip() if result.stdout else ""
    if not candidate.startswith(("http://", "https://")):
        logger.warning(
            "livecam_frame: yt-dlp produced no usable URL for %s", youtube_id
        )
        return None

    with _manifest_lock:
        _manifest_cache[youtube_id] = (now, candidate)
    return candidate


def get_live_frame(
    youtube_id: str,
    *,
    yt_dlp_timeout_s: float = 6.0,
    ffmpeg_timeout_s: float = 8.0,
) -> bytes | None:
    """Extract one current JPEG frame from a YouTube live stream.

    Resolves the HLS manifest via yt-dlp, then asks ffmpeg to decode a
    single keyframe-aligned frame and emit it as JPEG to stdout. Returns
    the JPEG bytes, or None if either subprocess fails.

    Args:
        youtube_id: 11-char YouTube video id. Validated against
            [A-Za-z0-9_-]{6,16} before reaching subprocess argv.
        yt_dlp_timeout_s: max seconds for the manifest resolve.
        ffmpeg_timeout_s: max seconds for the frame decode.

    Returns:
        JPEG bytes, or None on any failure (logged at WARNING).
    """
    if not isinstance(youtube_id, str) or not _YOUTUBE_ID_RE.match(youtube_id):
        logger.warning("livecam_frame: invalid youtube_id rejected: %r", youtube_id)
        return None

    # ffmpeg is required. yt-dlp is required. Both checked up front so the
    # caller can log "binary missing" rather than chasing subprocess
    # surprises.
    if shutil.which("ffmpeg") is None:
        logger.warning("livecam_frame: ffmpeg binary not on PATH")
        return None
    if shutil.which("yt-dlp") is None:
        # yt-dlp Python module is installed via uv but the CLI binary
        # comes from the same package. shutil.which finds the entrypoint
        # script after `uv sync`. Belt-and-suspenders check.
        logger.warning("livecam_frame: yt-dlp CLI not on PATH")
        return None

    manifest = _resolve_hls_manifest(youtube_id, timeout_s=yt_dlp_timeout_s)
    if manifest is None:
        return None

    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                # Live HLS — fetch from the playlist live edge, not the
                # archive head.
                "-fflags",
                "+genpts+discardcorrupt",
                "-i",
                manifest,
                # Single frame, mid-quality MJPEG to stdout.
                "-vframes",
                "1",
                "-q:v",
                "3",
                "-f",
                "image2pipe",
                "-c:v",
                "mjpeg",
                "pipe:1",
            ],
            capture_output=True,
            timeout=ffmpeg_timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        logger.warning("livecam_frame: ffmpeg timed out for %s", youtube_id)
        return None
    except OSError as e:
        logger.warning("livecam_frame: ffmpeg launch failed: %s", e)
        return None

    if result.returncode != 0 or not result.stdout:
        stderr_preview = (
            result.stderr.decode("utf-8", errors="replace")[:300]
            if result.stderr
            else ""
        )
        logger.warning(
            "livecam_frame: ffmpeg non-zero for %s rc=%s err=%s",
            youtube_id,
            result.returncode,
            stderr_preview,
        )
        return None

    # Sanity: a JPEG should be at least a few KB and start with FF D8.
    data = result.stdout
    if len(data) < 1024 or data[:2] != b"\xff\xd8":
        logger.warning(
            "livecam_frame: ffmpeg returned %d bytes, not a JPEG, for %s",
            len(data),
            youtube_id,
        )
        return None

    return data
