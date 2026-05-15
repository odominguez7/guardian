# Copyright 2026 GUARDIAN
# Integration test for Stream Watcher — proves D3 deliverable.

"""Run with:
    .venv/bin/pytest tests/integration/test_stream_watcher.py -v -s

Tests hit real Vertex AI Gemini Vision. Each test costs ~$0.01-0.03.
Skip via env var GUARDIAN_SKIP_LIVE=1.
"""

import json
import os

import pytest

from app.tools.vision import analyze_image_frame, analyze_video_clip


# Sample clips owned by GUARDIAN (copied from gs://cloud-samples-data/video/).
# Owning them means stable IAM, no surprise URL outages, no robots.txt edge cases.
SAMPLE_ANIMALS_VIDEO = "gs://guardian-gfs-2026-samples/wildlife/animals.mp4"
SAMPLE_CAT_VIDEO = "gs://guardian-gfs-2026-samples/wildlife/cat_shortened.mp4"


@pytest.mark.skipif(
    os.environ.get("GUARDIAN_SKIP_LIVE") == "1",
    reason="Live Gemini calls disabled (GUARDIAN_SKIP_LIVE=1)",
)
def test_analyze_animals_video_schema():
    """The flagship D3 deliverable: real wildlife clip → structured event."""
    result = analyze_video_clip(SAMPLE_ANIMALS_VIDEO)
    print("\n=== Stream Watcher output (animals.mp4) ===")
    print(json.dumps(result, indent=2)[:2000])

    assert result["status"] == "ok", f"tool errored: {result.get('error')}"
    for field in (
        "species",
        "total_animal_count",
        "behaviors",
        "threat_signals",
        "time_of_day_inference",
        "environmental_context",
        "overall_confidence",
        "requires_escalation",
        "raw_observations",
    ):
        assert field in result, f"missing field in tool output: {field}"

    assert isinstance(result["species"], list)
    assert isinstance(result["threat_signals"], list)
    assert isinstance(result["behaviors"], list)
    assert 0.0 <= result["overall_confidence"] <= 1.0


@pytest.mark.skipif(
    os.environ.get("GUARDIAN_SKIP_LIVE") == "1",
    reason="Live Gemini calls disabled (GUARDIAN_SKIP_LIVE=1)",
)
def test_analyze_cat_video_no_threat():
    """Short cat clip should detect a cat and NOT trigger threat escalation."""
    result = analyze_video_clip(SAMPLE_CAT_VIDEO)
    print("\n=== Stream Watcher output (cat_shortened.mp4) ===")
    print(json.dumps(result, indent=2)[:1500])

    assert result["status"] == "ok", f"tool errored: {result.get('error')}"
    # Cat clip shouldn't include human threats / weapons / vehicles.
    assert "weapons" not in [t.lower() for t in result["threat_signals"]]
    assert "gunshot" not in " ".join(result["threat_signals"]).lower()


def test_empty_uri_returns_error():
    """Defensive: empty input must not crash the agent."""
    result = analyze_video_clip("")
    assert result["status"] == "error"
    assert "video_uri is required" in result["error"]


def test_empty_image_uri_returns_error():
    """Same defensive check for image tool."""
    result = analyze_image_frame("")
    assert result["status"] == "error"
    assert "image_uri is required" in result["error"]
