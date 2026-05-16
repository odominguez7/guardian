# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import os
import traceback
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import google.auth
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard
from a2a.utils.constants import (
    AGENT_CARD_WELL_KNOWN_PATH,
    EXTENDED_AGENT_CARD_PATH,
)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder
from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud import logging as google_cloud_logging

from app import events as _events
from app.agent import app as adk_app
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

setup_telemetry()
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# Artifact bucket for ADK (created by Terraform, passed via env var)
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")
artifact_service = (
    GcsArtifactService(bucket_name=logs_bucket_name)
    if logs_bucket_name
    else InMemoryArtifactService()
)

runner = Runner(
    app=adk_app,
    artifact_service=artifact_service,
    session_service=InMemorySessionService(),
)

request_handler = DefaultRequestHandler(
    agent_executor=A2aAgentExecutor(runner=runner), task_store=InMemoryTaskStore()
)

A2A_RPC_PATH = f"/a2a/{adk_app.name}"


async def build_dynamic_agent_card() -> AgentCard:
    """Builds the Agent Card dynamically from the root_agent."""
    agent_card_builder = AgentCardBuilder(
        agent=adk_app.root_agent,
        capabilities=AgentCapabilities(streaming=True),
        rpc_url=f"{os.getenv('APP_URL', 'http://0.0.0.0:8000')}{A2A_RPC_PATH}",
        agent_version=os.getenv("AGENT_VERSION", "0.1.0"),
    )
    agent_card = await agent_card_builder.build()
    return agent_card


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
    agent_card = await build_dynamic_agent_card()
    a2a_app = A2AFastAPIApplication(agent_card=agent_card, http_handler=request_handler)
    a2a_app.add_routes_to_app(
        app_instance,
        agent_card_url=f"{A2A_RPC_PATH}{AGENT_CARD_WELL_KNOWN_PATH}",
        rpc_url=A2A_RPC_PATH,
        extended_agent_card_url=f"{A2A_RPC_PATH}{EXTENDED_AGENT_CARD_PATH}",
    )
    yield


app = FastAPI(
    title="guardian",
    description="API for interacting with the Agent guardian",
    lifespan=lifespan,
)


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# --- Ops Center event firehose -----------------------------------------------
# WebSocket + HTTP endpoints that surface the orchestrator's structured event
# stream to the Operations Center frontend. New subscribers get the recent
# ring-buffer replayed before live events resume.
#
# CORS — Ops Center frontend on a different Cloud Run URL needs cross-origin
# access. Codex challenge 2026-05-15 flagged: allow_origins=["*"] +
# allow_credentials=True is browser-rejected. Drop credentials when no
# specific origins are configured; only enable credentials when caller passed
# an explicit allowlist.
_cors_raw = os.environ.get("GUARDIAN_CORS_ORIGINS", "*")
_cors_origins = [o.strip() for o in _cors_raw.split(",") if o.strip()]
_cors_credentials = bool(_cors_origins and _cors_origins != ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/events/replay")
async def events_replay() -> dict:
    """Snapshot the ring buffer for HTTP polling clients.

    Returns the most recent ~200 events. Use the WebSocket endpoint for live
    streaming; this is a fallback for environments that don't support WS.
    """
    snap = await _events.snapshot()
    return {
        "subscribers": _events.subscriber_count(),
        "buffer_depth": _events.buffer_depth(),
        "events": snap,
    }


@app.websocket("/events/stream")
async def events_stream(websocket: WebSocket) -> None:
    """Live event stream WebSocket.

    Behavior:
      - Accept connection.
      - Replay ring buffer (up to ~200 events) so the client has context.
      - Stream every subsequent event as it's emitted.
      - Heartbeat every 25s so Cloud Run / proxy idle timeouts don't kill us.
      - On disconnect, deregister cleanly.
    """
    await websocket.accept()
    heartbeat_task: asyncio.Task | None = None

    async def heartbeat() -> None:
        try:
            while True:
                await asyncio.sleep(25)
                await websocket.send_json({"kind": "heartbeat", "ts": _events._now_iso()})
        except (WebSocketDisconnect, RuntimeError):
            return

    try:
        heartbeat_task = asyncio.create_task(heartbeat())
        async for evt in _events.subscribe():
            try:
                await websocket.send_json(evt)
            except (WebSocketDisconnect, RuntimeError):
                break
    finally:
        if heartbeat_task and not heartbeat_task.done():
            heartbeat_task.cancel()


# --- Demo scenario endpoints -------------------------------------------------
# Server-side scripted incidents the Ops Center can fire via a single button.
# Each scenario runs the orchestrator + peer fan-out end-to-end with a stable
# seed so the same scenario can be replayed for a video.

from fastapi import HTTPException  # noqa: E402

from app.tools.a2a_peers import (  # noqa: E402
    mint_incident_id,
    notify_funder,
    notify_neighbor_park,
    notify_park_service,
    notify_sponsor_sustainability,
)

_SCENARIOS = {
    "poacher_truck": {
        "title": "Poacher Truck — Serengeti Sector C",
        "narrative": (
            "Pickup truck detected approaching an African elephant herd at "
            "02:14 local time on a known poaching corridor in Serengeti "
            "Sector C. Audio confirms engine noise. Pattern agent flags "
            "historical poaching corridor. Cross-border risk — Maasai Mara "
            "rangers placed on alert."
        ),
        "seed": "scenario:poacher_truck|serengeti-sector-c|2026-05-15T02:14:00Z",
        # All 4 peers fire on this scenario — the Track 3 demo punchline.
        "fanout": ["park_service", "sponsor_sustainability", "funder_reporter", "neighbor_park"],
        "park_args": {
            "location": "Serengeti Sector C, north fence (Tanzania)",
            "severity": "critical",
            "summary": (
                "Pickup truck approaching elephant herd at 02:14; audio "
                "confirms engine; pattern matches known poaching corridor."
            ),
        },
        "sponsor_args": {
            "location": "Serengeti Sector C, north fence (Tanzania)",
            "species_affected": "African elephant",
            "threat_type": "vehicle_intrusion",
            "severity": "critical",
            "observation_timestamp": "2026-05-15T02:14:00Z",
        },
        "funder_args": {
            "location": "Serengeti Sector C, north fence (Tanzania)",
            "species_affected": "African elephant",
            "severity": "critical",
            "funder_program": "elephants_at_risk",
            "observation_timestamp": "2026-05-15T02:14:00Z",
        },
        "neighbor_args": {
            "origin_park": "Serengeti National Park, Tanzania",
            "severity": "critical",
            "species_affected": "African elephant",
            "crossover_corridor": "Mara River corridor (Serengeti-Maasai Mara border)",
            "observation_timestamp": "2026-05-15T02:14:00Z",
        },
    },
    "audio_gunshot": {
        "title": "Audio Gunshot — Kruger Northern Sector",
        "narrative": (
            "Audio agent classified a high-confidence gunshot signal at 03:42 "
            "near a Kruger black rhino crash. Stream Watcher confirms vehicle "
            "tail-lights in the same frame. Critical poaching event in progress."
        ),
        "seed": "scenario:audio_gunshot|kruger-north|2026-05-15T03:42:00Z",
        # All 4 peers — gunshot + black rhino triggers full coordination.
        "fanout": ["park_service", "sponsor_sustainability", "funder_reporter", "neighbor_park"],
        "park_args": {
            "location": "Kruger Northern Sector, ranger road 7 (South Africa)",
            "severity": "critical",
            "summary": (
                "Gunshot audio classification + vehicle tail-lights at 03:42 "
                "near black rhino crash. Active poaching event."
            ),
        },
        "sponsor_args": {
            "location": "Kruger Northern Sector, ranger road 7 (South Africa)",
            "species_affected": "Black rhinoceros",
            "threat_type": "poaching",
            "severity": "critical",
            "observation_timestamp": "2026-05-15T03:42:00Z",
        },
        "funder_args": {
            "location": "Kruger Northern Sector, ranger road 7 (South Africa)",
            "species_affected": "Black rhinoceros",
            "severity": "critical",
            "funder_program": "rhino_horn_crisis",
            "observation_timestamp": "2026-05-15T03:42:00Z",
        },
        "neighbor_args": {
            "origin_park": "Kruger National Park, South Africa",
            "severity": "critical",
            "species_affected": "Black rhinoceros",
            "crossover_corridor": "Limpopo River corridor (Kruger-Gonarezhou border)",
            "observation_timestamp": "2026-05-15T03:42:00Z",
        },
    },
    "sponsored_species": {
        "title": "Sponsored Species Encounter — Etosha cheetah crossing",
        "narrative": (
            "Stream Watcher identified two cheetahs (sponsored species, IUCN "
            "Vulnerable) crossing fence break-point F-14 in Etosha at 17:22. "
            "Medium severity but mandatory sponsor + funder disclosure required."
        ),
        "seed": "scenario:sponsored_species|etosha-f14|2026-05-15T17:22:00Z",
        # 3 peers — no cross-border in Etosha (interior reserve). Skips
        # neighbor_park to demonstrate fan-out is per-scenario, not all-or-nothing.
        "fanout": ["park_service", "sponsor_sustainability", "funder_reporter"],
        "park_args": {
            "location": "Etosha National Park, fence break F-14 (Namibia)",
            "severity": "high",
            "summary": (
                "Two cheetahs crossing fence break F-14 at 17:22; investigate "
                "fence integrity + log for sponsor disclosure."
            ),
        },
        "sponsor_args": {
            "location": "Etosha National Park, fence break F-14 (Namibia)",
            "species_affected": "Cheetah",
            "threat_type": "fence_breach",
            "severity": "high",
            "observation_timestamp": "2026-05-15T17:22:00Z",
        },
        "funder_args": {
            "location": "Etosha National Park, fence break F-14 (Namibia)",
            "species_affected": "Cheetah",
            "severity": "high",
            "funder_program": "predator_coexistence",
            "observation_timestamp": "2026-05-15T17:22:00Z",
        },
    },
}


@app.get("/demo/scenarios")
def list_scenarios() -> dict:
    """Public list of available demo scenarios for the Ops Center UI."""
    return {
        "scenarios": [
            {"id": k, "title": v["title"], "narrative": v["narrative"]}
            for k, v in _SCENARIOS.items()
        ]
    }


# --- Demo abuse guard --------------------------------------------------------
# Codex challenge 2026-05-15 flagged: /demo/run was non-idempotent +
# unrate-limited. A single user could spam it and fan out unlimited LLM calls
# to peers. Add a per-scenario cooldown (15s between runs) + in-flight lock
# (only one concurrent run per scenario). Process-local; for multi-instance
# protection a shared store would be needed (Redis/Firestore) — out of scope
# for hackathon, captured in TODOS.md.
_SCENARIO_COOLDOWN_S = 15.0
_scenario_last_run: dict[str, float] = {}
_scenario_in_flight: dict[str, asyncio.Lock] = {}


def _scenario_lock(scenario_id: str) -> asyncio.Lock:
    lock = _scenario_in_flight.get(scenario_id)
    if lock is None:
        lock = asyncio.Lock()
        _scenario_in_flight[scenario_id] = lock
    return lock


@app.post("/demo/run/{scenario_id}")
async def run_scenario(scenario_id: str) -> dict:
    """Fire a scripted scenario end-to-end and return the incident record.

    The scenario is deterministic: seed → mint_incident_id → notify both
    peers in parallel → return the consolidated record. Every step emits to
    the firehose so subscribed clients see the dance in real time.

    Guards:
    - 15-second cooldown per scenario (returns 429 if hit too fast)
    - Per-scenario in-flight lock so concurrent triggers serialize rather
      than interleave with the same incident_id
    """
    scenario = _SCENARIOS.get(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"Unknown scenario: {scenario_id}")

    import time as _time

    now = _time.monotonic()
    last = _scenario_last_run.get(scenario_id, 0.0)
    if now - last < _SCENARIO_COOLDOWN_S:
        wait = _SCENARIO_COOLDOWN_S - (now - last)
        raise HTTPException(
            status_code=429,
            detail=f"Scenario '{scenario_id}' on cooldown. Retry in {wait:.1f}s.",
        )

    lock = _scenario_lock(scenario_id)
    async with lock:
        # Re-check cooldown under the lock so concurrent triggers serialize.
        now = _time.monotonic()
        last = _scenario_last_run.get(scenario_id, 0.0)
        if now - last < _SCENARIO_COOLDOWN_S:
            wait = _SCENARIO_COOLDOWN_S - (now - last)
            raise HTTPException(
                status_code=429,
                detail=f"Scenario '{scenario_id}' on cooldown. Retry in {wait:.1f}s.",
            )
        _scenario_last_run[scenario_id] = now

        incident_id = mint_incident_id(scenario["seed"])
        _events.emit(
            kind="incident_event",
            agent="ops_center",
            tool=f"scenario:{scenario_id}",
            incident_id=incident_id,
            severity=scenario["park_args"]["severity"],
            payload={
                "scenario_id": scenario_id,
                "title": scenario["title"],
                "narrative": scenario["narrative"],
                "fanout": scenario.get("fanout", []),
            },
        )

        # Dispatch only the peers listed in fanout for this scenario.
        # Default behavior for legacy scenarios (no fanout key) is the
        # original 2-peer fan-out for backwards compat.
        fanout = scenario.get("fanout") or ["park_service", "sponsor_sustainability"]
        tasks: dict[str, asyncio.Task] = {}
        if "park_service" in fanout:
            tasks["park_service"] = asyncio.create_task(
                notify_park_service(incident_id=incident_id, **scenario["park_args"])
            )
        if "sponsor_sustainability" in fanout:
            tasks["sponsor_sustainability"] = asyncio.create_task(
                notify_sponsor_sustainability(incident_id=incident_id, **scenario["sponsor_args"])
            )
        if "funder_reporter" in fanout:
            tasks["funder_reporter"] = asyncio.create_task(
                notify_funder(incident_id=incident_id, **scenario["funder_args"])
            )
        if "neighbor_park" in fanout:
            tasks["neighbor_park"] = asyncio.create_task(
                notify_neighbor_park(incident_id=incident_id, **scenario["neighbor_args"])
            )

        # Await all in parallel. return_exceptions=True so ONE peer raising
        # doesn't 500 the request and silently kill the other 3 peers' UI
        # cards. Codex flagged this as the single highest-blast-radius
        # demo risk: any unexpected exception in one fanout task would
        # prevent :complete from firing, leaving the Ops Center wedged.
        peer_names = list(tasks.keys())
        completed = await asyncio.gather(*tasks.values(), return_exceptions=True)
        results: dict[str, dict] = {}
        for peer_name, outcome in zip(peer_names, completed):
            if isinstance(outcome, Exception):
                logger.log_struct(
                    {
                        "event": "fanout_peer_exception",
                        "peer": peer_name,
                        "incident_id": incident_id,
                        "error": f"{type(outcome).__name__}: {outcome}",
                        "traceback": traceback.format_exception(
                            type(outcome), outcome, outcome.__traceback__
                        ),
                    },
                    severity="ERROR",
                )
                results[peer_name] = {
                    "status": "error",
                    "error": f"{type(outcome).__name__}: {outcome}",
                    "peer": peer_name,
                    "source": "GUARDIAN orchestrator (fanout exception guard)",
                }
            else:
                results[peer_name] = outcome

        record = {
            "incident_id": incident_id,
            "scenario_id": scenario_id,
            "title": scenario["title"],
            **results,
        }
        _events.emit(
            kind="incident_event",
            agent="ops_center",
            tool=f"scenario:{scenario_id}:complete",
            incident_id=incident_id,
            severity="info",
            payload={
                f"{peer}_status": result.get("status")
                for peer, result in results.items()
            },
        )
        return record


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
