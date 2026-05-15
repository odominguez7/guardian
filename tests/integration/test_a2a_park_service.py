# Copyright 2026 GUARDIAN
# A2A round-trip test: orchestrator -> park_service peer.
#
# Spins up the peer in a background uvicorn process on port 8001, then drives
# notify_park_service against it. Asserts the dispatch ack comes back end to end.
#
# Run with:
#   .venv/bin/pytest tests/integration/test_a2a_park_service.py -v -s
#
# Skipped under GUARDIAN_SKIP_LIVE=1 (cost = a single Gemini Flash call for the
# peer's LLM to call dispatch_rangers).

import os
import socket
import subprocess
import sys
import time

import httpx
import pytest

PEER_PORT = 8001
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
def park_service_peer():
    """Spin up the peer's FastAPI app on port 8001 for the duration of the module."""
    if _port_open("localhost", PEER_PORT):
        pytest.skip(f"port {PEER_PORT} already in use; not auto-starting peer")

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "peers.park_service.fast_api_app:app",
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

    # Wait up to 30s for the peer to come up (cold ADK import is slow).
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
        raise TimeoutError("park_service peer did not bind to 8001 within 30s")

    # One more health probe to confirm the lifespan handler finished and the
    # A2A routes are mounted.
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
async def test_park_service_card_resolves(park_service_peer):
    """The peer must publish a discoverable A2A agent card."""
    os.environ["PARK_SERVICE_URL"] = park_service_peer
    # Re-import after env var is set so the module reads it fresh.
    from app.tools.a2a_peers import get_park_service_card

    result = await get_park_service_card()
    assert result["status"] == "ok", f"card resolution failed: {result}"
    card = result["card"]
    assert card["name"] == "park_service"
    assert "description" in card
    # The peer's RPC URL should point at the peer, not at GUARDIAN.
    assert "park_service" in card["url"]


@pytest.mark.skipif(
    os.environ.get("GUARDIAN_SKIP_LIVE") == "1",
    reason="Live Gemini calls disabled (GUARDIAN_SKIP_LIVE=1)",
)
@pytest.mark.asyncio
async def test_park_service_dispatches_critical_incident(park_service_peer):
    """The flagship A2A round-trip: GUARDIAN reports a poacher → peer dispatches."""
    os.environ["PARK_SERVICE_URL"] = park_service_peer
    from app.tools.a2a_peers import notify_park_service

    result = await notify_park_service(
        incident_id="GU-2026-0515-TEST-001",
        location="Sector C, north fence (Serengeti)",
        severity="critical",
        summary=(
            "Stream Watcher detected a pickup truck approaching an elephant herd at 02:14 "
            "local time on a known poaching corridor. Audio agent confirmed engine noise."
        ),
    )

    print("\n=== Park Service A2A response ===")
    import json as _json

    print(_json.dumps(result, indent=2)[:1500])

    assert result["status"] == "dispatched", f"peer did not dispatch: {result}"
    assert result["_peer"] == "park_service"
    assert result["incident_id"] == "GU-2026-0515-TEST-001"
    assert result["severity"] == "critical"
    assert result["estimated_arrival_minutes"] == 8  # critical → 8 min ETA
    assert result["ranger_unit"].startswith("PSR-")
    assert "ack_timestamp" in result


def test_notify_rejects_missing_fields():
    """Defensive: orchestrator-side validation runs before A2A transport."""
    import asyncio

    from app.tools.a2a_peers import notify_park_service

    result = asyncio.run(notify_park_service("", "anywhere", "high", "x"))
    assert result["status"] == "error"
    assert "incident_id" in result["error"]
    assert result["_peer"] == "park_service"
