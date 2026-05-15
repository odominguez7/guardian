# Copyright 2026 GUARDIAN
# A2A round-trip test: orchestrator -> sponsor_sustainability peer.
#
# Spins up the peer in a background uvicorn process on port 8002, then drives
# notify_sponsor_sustainability against it. Asserts the TNFD filing ack comes
# back end to end.
#
# Run with:
#   .venv/bin/pytest tests/integration/test_a2a_sponsor_sustainability.py -v -s

import json
import os
import socket
import subprocess
import sys
import time

import httpx
import pytest

PEER_PORT = 8002
PEER_URL = f"http://localhost:{PEER_PORT}"


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


@pytest.fixture(scope="module")
def sponsor_peer():
    """Spin up the sponsor_sustainability peer on port 8002 for the module."""
    if _port_open("localhost", PEER_PORT):
        pytest.skip(f"port {PEER_PORT} already in use; not auto-starting peer")

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "peers.sponsor_sustainability.fast_api_app:app",
            "--host",
            "localhost",
            "--port",
            str(PEER_PORT),
            "--log-level",
            "warning",
        ],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    deadline = time.time() + 30
    while time.time() < deadline:
        if _port_open("localhost", PEER_PORT):
            break
        if proc.poll() is not None:
            stderr = proc.stderr.read().decode() if proc.stderr else ""
            raise RuntimeError(f"peer died on startup:\n{stderr[-2000:]}")
        time.sleep(0.5)
    else:
        proc.terminate()
        raise TimeoutError(
            f"sponsor_sustainability peer did not bind to {PEER_PORT} within 30s"
        )

    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            r = httpx.get(f"{PEER_URL}/health", timeout=2.0)
            if r.status_code == 200:
                break
        except httpx.HTTPError:
            pass
        time.sleep(0.5)

    yield PEER_URL

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.mark.skipif(
    os.environ.get("GUARDIAN_SKIP_LIVE") == "1",
    reason="Live Gemini calls disabled (GUARDIAN_SKIP_LIVE=1)",
)
@pytest.mark.asyncio
async def test_sponsor_card_resolves(sponsor_peer):
    """The peer must publish a discoverable A2A agent card."""
    os.environ["SPONSOR_SUSTAINABILITY_URL"] = sponsor_peer
    from app.tools.a2a_peers import get_sponsor_sustainability_card

    result = await get_sponsor_sustainability_card()
    assert result["status"] == "ok", f"card resolution failed: {result}"
    card = result["card"]
    assert card["name"] == "sponsor_sustainability"
    assert "sponsor_sustainability" in card["url"]


@pytest.mark.skipif(
    os.environ.get("GUARDIAN_SKIP_LIVE") == "1",
    reason="Live Gemini calls disabled (GUARDIAN_SKIP_LIVE=1)",
)
@pytest.mark.asyncio
async def test_sponsor_files_tnfd_entry(sponsor_peer):
    """The flagship A2A round-trip: GUARDIAN incident → TNFD filing."""
    os.environ["SPONSOR_SUSTAINABILITY_URL"] = sponsor_peer
    from app.tools.a2a_peers import notify_sponsor_sustainability

    result = await notify_sponsor_sustainability(
        incident_id="GU-2026-0515-TEST-001",
        location="Serengeti Sector C",
        species_affected="African elephant",
        threat_type="vehicle_intrusion",
        severity="critical",
        observation_timestamp="2026-05-15T02:14:00Z",
    )

    print("\n=== Sponsor Sustainability A2A response ===")
    print(json.dumps(result, indent=2)[:2000])

    assert result["status"] == "filed", f"peer did not file: {result}"
    assert result["_peer"] == "sponsor_sustainability"
    assert result["filing_id"].startswith("TNFD-2026-")
    assert result["materiality"] == "material"
    assert result["tnfd_entry"]["species_affected"] == "African elephant"
    assert result["tnfd_entry"]["threat_type"] == "vehicle_intrusion"
    assert "CSRD-ESRS-E4" in result["tnfd_entry"]["compliance_frameworks"]
    assert result["dashboard_url"].endswith(result["filing_id"])


def test_sponsor_rejects_missing_fields():
    """Orchestrator-side validation runs before A2A transport."""
    import asyncio

    from app.tools.a2a_peers import notify_sponsor_sustainability

    result = asyncio.run(
        notify_sponsor_sustainability("", "loc", "sp", "poaching", "high", "ts")
    )
    assert result["status"] == "error"
    assert "required" in result["error"]
    assert result["_peer"] == "sponsor_sustainability"
