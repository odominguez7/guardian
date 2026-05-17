# Copyright 2026 GUARDIAN
# Live-cam frame extraction — best-effort path to a current frame from a
# YouTube live HLS stream via yt-dlp + ffmpeg.
#
# Status (2026-05-17):
# YouTube actively blocks server-side yt-dlp access from Cloud Run egress
# IPs ("Sign in to confirm you're not a bot"). Local development with a
# residential IP usually works; Cloud Run usually doesn't. The honest fix
# is a residential-proxy service or baked-in browser cookies, both of
# which are out of scope for v7. We keep this path because:
#   - When yt-dlp DOES succeed (some Cloud Run pods get lucky IPs), we
#     get a genuinely current frame.
#   - The fallback to YouTube's published thumbnail (handled in
#     fast_api_app._pick_live_thumbnail) is still real Gemini Vision on
#     a real frame from the same camera — just not literally the current
#     second. YouTube refreshes the thumbnail every few minutes for
#     active live streams.
#   - The frontend transparently labels which path served the frame
#     ("LIVE · <sha>" vs "RECENT · <sha>") so the producer knows what
#     they're looking at.
#
# Producer caught the bug 2026-05-17: v6 ALWAYS used the thumbnail and
# labeled it as live. v7 attempts the real HLS path first, with honest
# labeling on the fallback.
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
_MANIFEST_CACHE_MAX = 32  # v7.1 codex NIT: prune so hammering many ids doesn't grow unbounded
_manifest_cache: dict[str, tuple[float, str]] = {}
_manifest_lock = Lock()


def _prune_manifest_cache_locked(now: float) -> None:
    """Drop expired manifest entries. Called inside _manifest_lock. v7.1."""
    expired = [k for k, (ts, _) in _manifest_cache.items() if now - ts >= _MANIFEST_TTL_S]
    for k in expired:
        _manifest_cache.pop(k, None)
    # Hard cap: if still over the max, drop oldest first.
    if len(_manifest_cache) > _MANIFEST_CACHE_MAX:
        ordered = sorted(_manifest_cache.items(), key=lambda kv: kv[1][0])
        for k, _ in ordered[: len(_manifest_cache) - _MANIFEST_CACHE_MAX]:
            _manifest_cache.pop(k, None)


def _resolve_hls_manifest(youtube_id: str, timeout_s: float = 10.0) -> str | None:
    """Use yt-dlp to resolve the HLS m3u8 manifest URL for a live video.

    Returns the URL on success, None on failure (logged at WARNING).
    Cached for _MANIFEST_TTL_S to absorb back-to-back Spot Now clicks.
    """
    now = time.monotonic()
    with _manifest_lock:
        _prune_manifest_cache_locked(now)
        cached = _manifest_cache.get(youtube_id)
        if cached and now - cached[0] < _MANIFEST_TTL_S:
            return cached[1]

    yt_url = f"https://www.youtube.com/watch?v={youtube_id}"
    try:
        # -g    : print the direct URL and exit (no download)
        # -f    : prefer 480p HLS so the segment is small + decodes fast
        # --no-warnings keeps stderr clean for our logger
        # --extractor-args: v7.2 fix — YouTube blocks the default web
        #   player_client when requests originate from Cloud Run IPs ("Sign
        #   in to confirm you're not a bot"). The android + ios + tv_safari
        #   clients don't require web-style auth tokens for live HLS, so
        #   we pin to those. mweb is a useful fallback.
        result = subprocess.run(
            [
                "yt-dlp",
                "-g",
                "-f",
                "best[protocol^=m3u8][height<=480]/best[protocol^=m3u8]/best",
                "--no-warnings",
                "--no-playlist",
                "--extractor-args",
                "youtube:player_client=android,ios,tv_safari,mweb",
                "--user-agent",
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
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


# v7.5 — same idea as get_live_frame() but for an MP4 URL (Veo loops or
# any bundled wildlife footage). No yt-dlp involved; we just point ffmpeg
# at the URL with a random seek so producers get different frames on
# successive Spot Now clicks. URL is validated to https:// + ops-center
# style domains so users can't smuggle arbitrary file:// paths through.
import random as _random  # noqa: E402

# Bounded random seek into the clip so successive spots see different
# moments — most Veo loops are 6-8s.
_MP4_SEEK_MIN_S = 0.5
_MP4_SEEK_MAX_S = 6.0


def get_mp4_frame(
    mp4_url: str,
    *,
    ffmpeg_timeout_s: float = 12.0,
) -> bytes | None:
    """Extract one JPEG frame from a publicly-fetchable MP4 URL.

    Validates the URL is https://, then asks ffmpeg to seek to a random
    timestamp and decode a single frame to mjpeg/stdout. Returns the
    JPEG bytes or None on failure.

    Args:
        mp4_url: Absolute https URL of the MP4.
        ffmpeg_timeout_s: max seconds for the ffmpeg call.
    """
    if not isinstance(mp4_url, str) or not mp4_url.startswith("https://"):
        logger.warning("get_mp4_frame: invalid mp4_url: %r", mp4_url[:80] if mp4_url else mp4_url)
        return None
    if len(mp4_url) > 512:
        logger.warning("get_mp4_frame: mp4_url too long")
        return None

    if shutil.which("ffmpeg") is None:
        logger.warning("get_mp4_frame: ffmpeg not on PATH")
        return None

    seek = round(_random.uniform(_MP4_SEEK_MIN_S, _MP4_SEEK_MAX_S), 2)
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-loglevel", "error",
                "-y",
                # -ss BEFORE -i is fast keyframe seek; the seek is approximate
                # but for short Veo loops that's fine and ~10x faster.
                "-ss", str(seek),
                "-i", mp4_url,
                "-vframes", "1",
                "-q:v", "3",
                "-f", "image2pipe",
                "-c:v", "mjpeg",
                "pipe:1",
            ],
            capture_output=True,
            timeout=ffmpeg_timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        logger.warning("get_mp4_frame: ffmpeg timed out for %s", mp4_url[:80])
        return None
    except OSError as e:
        logger.warning("get_mp4_frame: ffmpeg launch failed: %s", e)
        return None

    if result.returncode != 0 or not result.stdout:
        stderr_preview = (
            result.stderr.decode("utf-8", errors="replace")[:200]
            if result.stderr else ""
        )
        logger.warning(
            "get_mp4_frame: ffmpeg non-zero rc=%s err=%s",
            result.returncode, stderr_preview,
        )
        return None

    data = result.stdout
    if len(data) < 1024 or data[:2] != b"\xff\xd8":
        logger.warning("get_mp4_frame: ffmpeg returned non-JPEG payload")
        return None
    return data


def get_live_frame(
    youtube_id: str,
    *,
    yt_dlp_timeout_s: float = 10.0,
    ffmpeg_timeout_s: float = 12.0,
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
