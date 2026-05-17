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
from app.tools.falsifier import review_dispatch  # noqa: E402

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
    "multimodal_pipeline": {
        "title": "Full Multimodal Chain — Selous gunshot + elephant herd",
        "narrative": (
            "Camera-trap Tag-22 in Selous fires the full multi-agent chain: "
            "Stream Watcher confirms a vehicle frame at 04:08, Audio Agent "
            "classifies a gunshot signal at 0.93 confidence, Species ID + "
            "corpus RAG flag the herd as Endangered + CITES Appendix I, "
            "orchestrator escalates and fans out to all 4 enterprise peers."
        ),
        "seed": "scenario:multimodal_pipeline|selous-tag22|2026-05-15T04:08:00Z",
        "fanout": ["park_service", "sponsor_sustainability", "funder_reporter", "neighbor_park"],
        # Pre-emit cinema steps before the peer fan-out. Each step appears in
        # the Ops Center event firehose as a tool_start + tool_end pair,
        # making the multi-agent chain visible. Outputs are canned for demo
        # reliability — the live agents (audio_agent, species_id) are
        # exercisable via the LLM chat path for judge inspection.
        "pre_steps": [
            {
                "agent": "stream_watcher",
                "tool": "analyze_video_clip",
                "duration_ms": 850,
                "severity": "high",
                "result": {
                    "primary_species": "African elephant",
                    "total_animal_count": 11,
                    "threat_signals": ["vehicle silhouette", "engine glow at 220m"],
                    "time_of_day_inference": "night",
                    "overall_confidence": 0.82,
                    "requires_escalation": True,
                },
            },
            {
                "agent": "audio_agent",
                "tool": "classify_audio",
                "duration_ms": 720,
                "severity": "critical",
                "result": {
                    "sound_class": "gunshot",
                    "confidence": 0.93,
                    "threat_signal": True,
                    "secondary_sounds": ["distressed_herd", "vehicle_engine"],
                    "severity": "critical",
                    "explanation": "Single high-amplitude impulse, gunshot-consistent waveform.",
                },
            },
            {
                "agent": "species_id",
                "tool": "identify_species",
                "duration_ms": 920,
                "severity": "high",
                "result": {
                    "primary_species": {
                        "common_name": "African elephant",
                        "scientific_name": "Loxodonta africana",
                        "count": 11,
                        "confidence": 0.91,
                    },
                    "individual_animal_hints": [
                        "matriarchal posture, lead cow",
                        "calf at heel (estimated 18 months)",
                    ],
                    "behavior_observed": ["alert posture", "huddle formation"],
                    "endangered_listed": True,
                    "overall_confidence": 0.91,
                },
            },
            {
                "agent": "species_id",
                "tool": "lookup_species_factsheet",
                "duration_ms": 380,
                "severity": "high",
                "result": {
                    "common_name": "African elephant",
                    "top_match": {
                        "doc_id": "species-loxodonta-africana",
                        "scientific_name": "Loxodonta africana",
                        "iucn_status": "Endangered",
                        "cites_appendix": "I",
                        "habitat": ["savanna", "forest", "wetland"],
                    },
                    "compliance_flag": "material",
                    "rationale": "IUCN Endangered + CITES Appendix I → material under TNFD + CSRD-ESRS-E4.",
                },
            },
        ],
        "park_args": {
            "location": "Selous Game Reserve, Tag-22 camera (Tanzania)",
            "severity": "critical",
            "summary": (
                "Stream Watcher + Audio chain: gunshot (0.93 conf) and "
                "vehicle silhouette near 11-elephant herd at 04:08. Active "
                "poaching event."
            ),
        },
        "sponsor_args": {
            "location": "Selous Game Reserve, Tag-22 camera (Tanzania)",
            "species_affected": "African elephant",
            "threat_type": "poaching",
            "severity": "critical",
            "observation_timestamp": "2026-05-15T04:08:00Z",
        },
        "funder_args": {
            "location": "Selous Game Reserve, Tag-22 camera (Tanzania)",
            "species_affected": "African elephant",
            "severity": "critical",
            "funder_program": "elephants_at_risk",
            "observation_timestamp": "2026-05-15T04:08:00Z",
        },
        "neighbor_args": {
            "origin_park": "Selous Game Reserve, Tanzania",
            "severity": "critical",
            "species_affected": "African elephant",
            "crossover_corridor": "Ruvuma River corridor (Selous-Niassa trans-frontier)",
            "observation_timestamp": "2026-05-15T04:08:00Z",
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
                "pre_steps": [s["agent"] + ":" + s["tool"] for s in scenario.get("pre_steps", [])],
            },
        )

        # Emit the canned multimodal pre-step events (Stream Watcher → Audio
        # → Species → factsheet) so the Ops Center cinema shows the agentic
        # chain before the 4-peer fan-out kicks in. Each step is a real
        # tool_start + tool_end pair on the firehose, with a tiny delay so
        # the cards stagger naturally instead of all appearing at once.
        for step in scenario.get("pre_steps", []) or []:
            _events.emit(
                kind="tool_start",
                agent=step["agent"],
                tool=step["tool"],
                incident_id=incident_id,
                severity=step.get("severity", "info"),
                payload={"args_summary": step["tool"]},
            )
            await asyncio.sleep(step.get("duration_ms", 600) / 1000.0)
            _events.emit(
                kind="tool_end",
                agent=step["agent"],
                tool=step["tool"],
                incident_id=incident_id,
                severity=step.get("severity", "info"),
                payload=step["result"],
                latency_ms=step.get("duration_ms", 600),
            )

        # Adversarial review (Falsifier) — PLAN_V3.md Move 1. The orchestrator's
        # LLM path delegates to falsifier_agent before fan-out; the /demo/run
        # fixture path must mirror that so the response carries the verdict
        # and Sponsor Sustainability receives the adversarial_review_*
        # fields. Telemetry is extracted from the pre_steps results:
        #   - audio_confidence from any audio_agent step's result.confidence
        #   - species_compliance_flag from species_id factsheet's compliance_flag
        #   - threat_signals from stream_watcher step's threat_signals list
        #     plus audio's secondary_sounds (deduped)
        audio_conf: float | None = None
        species_flag: str | None = None
        threat_signals: list[str] = []
        for step in scenario.get("pre_steps", []) or []:
            r = step.get("result") or {}
            if step["agent"] == "audio_agent":
                if "confidence" in r:
                    audio_conf = float(r["confidence"])
                # Combine top-level sound_class + secondary_sounds into the
                # threat_signal vocabulary the Falsifier checks against.
                if r.get("sound_class"):
                    threat_signals.append(r["sound_class"])
                threat_signals.extend(r.get("secondary_sounds") or [])
            if step["agent"] == "species_id" and step["tool"] == "lookup_species_factsheet":
                species_flag = r.get("compliance_flag")
            if step["agent"] == "stream_watcher":
                # Normalize "vehicle silhouette" / "engine glow" to the hot-signal
                # vocabulary so Gate 4 (hot threat signal for high+ severity)
                # can resolve correctly.
                for raw in r.get("threat_signals") or []:
                    if "vehicle" in raw.lower() or "engine" in raw.lower():
                        threat_signals.append("vehicle_engine")
                    elif "gun" in raw.lower():
                        threat_signals.append("gunshot")
        # Dedupe while preserving order.
        seen = set()
        threat_signals = [t for t in threat_signals if not (t in seen or seen.add(t))]

        review = review_dispatch(
            incident_id=incident_id,
            severity=scenario["park_args"]["severity"],
            audio_confidence=audio_conf,
            species_compliance_flag=species_flag,
            threat_signals=threat_signals,
            observation_timestamp=scenario.get("sponsor_args", {}).get("observation_timestamp"),
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
            # Sponsor peer gets the Falsifier verdict + severity so the
            # TNFD entry's adversarial_review_passed field is populated.
            tasks["sponsor_sustainability"] = asyncio.create_task(
                notify_sponsor_sustainability(
                    incident_id=incident_id,
                    adversarial_review_verdict=review["verdict"],
                    adversarial_review_severity_0_5=review["severity_0_5"],
                    **scenario["sponsor_args"],
                )
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
            "adversarial_review": {
                "verdict": review["verdict"],
                "dissent_reason": review["dissent_reason"],
                "severity_0_5": review["severity_0_5"],
                "audit_threshold_met": review["audit_threshold_met"],
                "reviewer": "falsifier",
            },
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


# ----- Live Cam → real agent activation (v6) --------------------------------
# Producer ask 2026-05-17: "when we spot something in the live cam, can we
# launch some agent in real life?" YES. This endpoint pulls a fresh frame
# from the YouTube live thumbnail surface (which ticks for live streams),
# runs Gemini 2.5 Pro vision on it via the real stream_watcher tool, and if
# anything material is detected, fans out to the four A2A peers exactly like
# /demo/run would — except the trigger is a REAL frame from a REAL live cam,
# not a canned fixture.
#
# Why thumbnail not HLS frame sampling: a full yt-dlp + ffmpeg pull from
# the HLS manifest gets a sharper frame, but adds 2 binary dependencies and
# ~3s of latency to the demo. The live thumbnail
# (https://i.ytimg.com/vi/<id>/maxres_live_1.jpg) ticks every ~30-60s for
# live streams and is sufficient for a Gemini Vision multi-class detection.
# v7 will add the yt-dlp path once the demo loop is proven.

import urllib.request as _urllib_request  # noqa: E402
import urllib.error as _urllib_error  # noqa: E402

from pydantic import BaseModel as _BaseModel  # noqa: E402
from app.tools.vision import analyze_image_frame as _analyze_image_frame  # noqa: E402


class _LivecamSpotRequest(_BaseModel):
    youtube_id: str
    cam_label: str | None = None


_LIVECAM_COOLDOWN_S = 12.0
_livecam_last_run: dict[str, float] = {}


def _pick_live_thumbnail(youtube_id: str) -> str | None:
    """Return the freshest publicly fetchable thumbnail URL for a YouTube
    live stream, or None if every candidate 404s. For live streams YouTube
    rotates maxres_live_1.jpg / maxres_live_2.jpg / maxres_live_3.jpg every
    ~30s, with maxresdefault as the static poster fallback.

    v6 codex BLOCK fix: callers wrap this in asyncio.to_thread because the
    sequential HEAD probes can take up to ~21s worst-case and would freeze
    the event loop otherwise.
    """
    candidates = [
        f"https://i.ytimg.com/vi/{youtube_id}/maxres_live_1.jpg",
        f"https://i.ytimg.com/vi/{youtube_id}/maxres_live_2.jpg",
        f"https://i.ytimg.com/vi/{youtube_id}/maxres_live_3.jpg",
        f"https://i.ytimg.com/vi/{youtube_id}/maxresdefault_live.jpg",
        f"https://i.ytimg.com/vi/{youtube_id}/maxresdefault.jpg",
        f"https://i.ytimg.com/vi/{youtube_id}/hqdefault_live.jpg",
        f"https://i.ytimg.com/vi/{youtube_id}/hqdefault.jpg",
    ]
    for url in candidates:
        try:
            req = _urllib_request.Request(url, method="HEAD", headers={"User-Agent": "GUARDIAN/1.0"})
            with _urllib_request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    return url
        except (_urllib_error.URLError, _urllib_error.HTTPError, TimeoutError, Exception):
            continue
    return None


@app.post("/livecam/spot")
async def livecam_spot(req: _LivecamSpotRequest) -> dict:
    """Producer-triggered "Spot Now" on a YouTube live cam.

    Pulls the freshest live thumbnail for the supplied YouTube video id,
    runs Gemini 2.5 Pro vision via the real `analyze_image_frame` tool,
    decides escalation, and if material fans out to all four A2A peers in
    parallel — exactly like /demo/run but with a REAL frame from a REAL
    live stream, not a canned fixture.

    Returns the incident record with the analysis + peer acks. Emits the
    same firehose event shape /demo/run does, so the Ops Center UI lights
    up the existing topology + fan-out animation.
    """
    import time as _time
    import secrets as _secrets
    from datetime import datetime, timezone

    youtube_id = req.youtube_id.strip()
    if not youtube_id or len(youtube_id) > 32:
        raise HTTPException(status_code=400, detail="youtube_id required (≤32 chars)")
    cam_label = (req.cam_label or "Live Cam").strip()[:64]

    now = _time.monotonic()
    last = _livecam_last_run.get(youtube_id, 0.0)
    if now - last < _LIVECAM_COOLDOWN_S:
        wait = _LIVECAM_COOLDOWN_S - (now - last)
        raise HTTPException(
            status_code=429,
            detail=f"Live cam '{youtube_id}' on cooldown. Retry in {wait:.1f}s.",
        )
    _livecam_last_run[youtube_id] = now

    # v6.1 codex BLOCK fix: wrap the 7-URL HEAD probe in to_thread so the
    # event loop isn't frozen for up to ~21s while we search for a frame.
    thumbnail_url = await asyncio.to_thread(_pick_live_thumbnail, youtube_id)
    if thumbnail_url is None:
        raise HTTPException(
            status_code=502,
            detail=f"No fetchable thumbnail for youtube_id={youtube_id}",
        )
    # v6.1 codex WARN fix: add a cache-buster query param. YouTube's CDN
    # otherwise serves the same edge-cached crop, which would make every
    # successive "Spot Now" click analyze the same image.
    sep = "&" if "?" in thumbnail_url else "?"
    thumbnail_url = f"{thumbnail_url}{sep}_ts={int(_time.time())}"

    # v6.1 codex WARN fix: incident_id seed now includes random entropy so
    # cross-pod / rapid-fire clicks can't collide on the same id. Same
    # second + same youtube_id + different click → unique incident.
    incident_id = mint_incident_id(
        seed=f"livecam:{youtube_id}|{int(_time.time())}|{_secrets.token_hex(4)}"
    )
    # Real ISO timestamp — passed to every peer arg below. v6 codex BLOCK
    # fix: sponsor / funder / neighbor all reject None timestamps with a
    # structured error envelope and the incident would silently not fan out.
    observation_iso = datetime.now(timezone.utc).isoformat()

    # 1) Announce the spot on the firehose so the UI lights up immediately.
    _events.emit(
        kind="incident_event",
        agent="ops_center",
        tool="livecam:spot",
        incident_id=incident_id,
        severity="info",
        payload={
            "scenario_id": "livecam-spot",
            "title": f"Live Spot — {cam_label}",
            "narrative": (
                f"Producer triggered Stream Watcher on a real frame from "
                f"YouTube live cam {youtube_id}. Frame URL: {thumbnail_url}"
            ),
            "fanout": ["park_service", "sponsor_sustainability", "funder_reporter", "neighbor_park"],
            "source": "livecam",
            "youtube_id": youtube_id,
            "thumbnail_url": thumbnail_url,
            "pre_steps": ["stream_watcher:analyze_image_frame"],
        },
    )

    # 2) Run REAL Gemini Vision on the frame. Emit tool_start + tool_end so
    # the Mission Bridge active line lights up while it's analyzing.
    _events.emit(
        kind="tool_start",
        agent="stream_watcher",
        tool="analyze_image_frame",
        incident_id=incident_id,
        severity="info",
        payload={"image_uri": thumbnail_url, "focus": "wildlife + threat detection"},
    )
    vision_started = _time.monotonic()
    result = await asyncio.to_thread(
        _analyze_image_frame,
        thumbnail_url,
        "identify wildlife species, count, behavior, and any threat signals "
        "(humans, vehicles, gunshot residue, fences cut). Be specific.",
    )
    latency_ms = int((_time.monotonic() - vision_started) * 1000)
    _events.emit(
        kind="tool_end",
        agent="stream_watcher",
        tool="analyze_image_frame",
        incident_id=incident_id,
        severity="medium",
        payload=result,
        latency_ms=latency_ms,
    )

    # 3) Decide escalation from the vision result.
    # v6.2 fix: the analyze_image_frame response schema uses `species` (list)
    # + `total_animal_count`, NOT `primary_species`. v6.0 read the wrong
    # fields and the fallback-escalation never fired on real sightings —
    # the smoke test caught 5 ostriches + 1 oryx but didn't fan out.
    requires_escalation = bool(result.get("requires_escalation"))
    species_list = result.get("species") or []
    threat_signals = result.get("threat_signals") or []
    # Pick the highest-confidence common name as the headline species.
    species_headline: str = ""
    if isinstance(species_list, list) and species_list:
        try:
            top = sorted(
                (s for s in species_list if isinstance(s, dict)),
                key=lambda s: float(s.get("confidence") or 0),
                reverse=True,
            )[0]
            cn = (top.get("common_name") or top.get("name") or "").strip()
            if cn:
                species_headline = cn
        except (TypeError, ValueError):
            pass
    total_animal_count = int(result.get("total_animal_count") or 0)
    if not requires_escalation and (total_animal_count > 0 or threat_signals):
        # Producer ergonomic: any live wildlife sighting is worth a fan-out
        # so the demo shows the agentic chain reacting. If the vision tool
        # is conservative, escalate to medium here so the peers always run.
        requires_escalation = True
    # v6.3 codex WARN fix: threat-only escalations (e.g. fence breach with
    # no animals visible in the frame) used to ship "wildlife sighting" as
    # species_affected on every peer payload — misleading on the TNFD
    # filing. Now we derive a threat-specific label when species is empty.
    if not species_headline:
        if threat_signals:
            species_headline = f"scene event ({threat_signals[0]})"
        else:
            species_headline = "wildlife sighting"
    # Bind back to species_name for the peer-args dicts below.
    species_name = species_headline
    severity = (
        "critical" if any("gun" in s.lower() for s in threat_signals)
        else "high" if any("vehicle" in s.lower() or "human" in s.lower() for s in threat_signals)
        else "medium"
    )

    # 4) Falsifier adversarial review — same path /demo/run uses.
    review = await asyncio.to_thread(
        review_dispatch,
        incident_id=incident_id,
        severity=severity,
        audio_confidence=None,
        species_compliance_flag=None,
        threat_signals=threat_signals,
        observation_timestamp=None,
    )

    if not requires_escalation:
        _events.emit(
            kind="incident_event",
            agent="ops_center",
            tool="livecam:spot:complete",
            incident_id=incident_id,
            severity="info",
            payload={"requires_escalation": False, "vision_status": result.get("status")},
        )
        return {
            "status": "ok",
            "incident_id": incident_id,
            "requires_escalation": False,
            "vision": result,
            "adversarial_review": review,
            "thumbnail_url": thumbnail_url,
        }

    # 5) Fan out to ALL four A2A peers in parallel — real LLM calls, real
    # acks, real chain of custody. Same path /demo/run uses.
    park_args = {
        "location": cam_label,
        "severity": severity,
        "summary": (
            f"Live cam spot · {species_name} detected · "
            f"threat_signals={threat_signals or 'none'}"
        ),
    }
    sponsor_args = {
        "location": cam_label,
        "species_affected": species_name,
        "threat_type": (
            "poaching" if any("gun" in s.lower() for s in threat_signals)
            else "vehicle_intrusion" if any("vehicle" in s.lower() for s in threat_signals)
            else "habitat_intrusion" if any("human" in s.lower() for s in threat_signals)
            else "other"
        ),
        "severity": severity,
        "observation_timestamp": observation_iso,
    }
    funder_args = {
        "location": cam_label,
        "species_affected": species_name,
        "funder_program": "general_impact",
        "severity": severity,
        "observation_timestamp": observation_iso,
    }
    # v6.1 codex BLOCK fix: neighbor_park's arg is species_affected (not
    # species), and observation_timestamp must be ISO not None.
    neighbor_args = {
        "origin_park": cam_label,
        "crossover_corridor": "live-cam-detected",
        "severity": severity,
        "species_affected": species_name,
        "observation_timestamp": observation_iso,
    }

    tasks = {
        "park_service": asyncio.create_task(
            notify_park_service(incident_id=incident_id, **park_args)
        ),
        "sponsor_sustainability": asyncio.create_task(
            notify_sponsor_sustainability(
                incident_id=incident_id,
                adversarial_review_verdict=review["verdict"],
                adversarial_review_severity_0_5=review["severity_0_5"],
                **sponsor_args,
            )
        ),
        "funder_reporter": asyncio.create_task(
            notify_funder(incident_id=incident_id, **funder_args)
        ),
        "neighbor_park": asyncio.create_task(
            notify_neighbor_park(incident_id=incident_id, **neighbor_args)
        ),
    }
    peer_names = list(tasks.keys())
    completed = await asyncio.gather(*tasks.values(), return_exceptions=True)
    results: dict[str, dict] = {}
    for peer_name, outcome in zip(peer_names, completed):
        if isinstance(outcome, Exception):
            logger.log_struct(
                {
                    "event": "livecam_fanout_peer_exception",
                    "peer": peer_name,
                    "incident_id": incident_id,
                    "error": f"{type(outcome).__name__}: {outcome}",
                },
                severity="ERROR",
            )
            results[peer_name] = {
                "status": "error",
                "error": f"{type(outcome).__name__}: {outcome}",
                "peer": peer_name,
            }
        else:
            results[peer_name] = outcome

    _events.emit(
        kind="incident_event",
        agent="ops_center",
        tool="livecam:spot:complete",
        incident_id=incident_id,
        severity="info",
        payload={
            f"{peer}_status": r.get("status") for peer, r in results.items()
        },
    )

    return {
        "status": "ok",
        "incident_id": incident_id,
        "requires_escalation": True,
        "vision": result,
        "adversarial_review": review,
        "thumbnail_url": thumbnail_url,
        **results,
    }


# ----- Court-Evidence endpoints ---------------------------------------------
# Surface the chain-of-custody bundle (JSON + HTML) for any incident that
# still has events in the firehose ring buffer. Used by:
#   - The Ops Center "Generate evidence packet" button (post-scenario)
#   - Direct judge / auditor clicks during demo evaluation
#   - The orchestrator's LLM when it calls court_evidence_agent.
#
# Auth gate: codex flagged the endpoints as public-by-default which would
# leak incident details to anyone who can guess an incident_id. The
# orchestrator service is currently --allow-unauthenticated for hackathon
# demo, so we layer an explicit shared-secret gate controlled by
# GUARDIAN_EVIDENCE_AUTH_TOKEN env var. When the env var is set, the
# evidence endpoints require Authorization: Bearer <token>. When unset
# (the hackathon default), endpoints are open for judges to click. Flip
# the env var in production via `make wire-evidence-auth`.

from fastapi import Header, Request  # noqa: E402
from fastapi.responses import HTMLResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pathlib import Path as _Path  # noqa: E402

# Serve vendored static assets (e.g., html2canvas.min.js for board slides).
# Codex Move 3 P1 fix 2026-05-17 — removes third-party CDN dependency from
# the board-slide artifact (regulated-disclosure surface).
_static_dir = _Path(__file__).parent / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

from app.tools.court_evidence import (  # noqa: E402
    bundle_incident as _bundle_incident,
    render_evidence_html as _render_evidence_html,
)
from app.tools.board_slide import render_board_slide as _render_board_slide  # noqa: E402


def _check_evidence_auth(authorization: str | None) -> None:
    """Raise 401 if GUARDIAN_EVIDENCE_AUTH_TOKEN is set and the request
    Authorization header doesn't carry that bearer token. No-op when the
    env var is unset (hackathon demo default)."""
    required = os.environ.get("GUARDIAN_EVIDENCE_AUTH_TOKEN", "").strip()
    if not required:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="evidence endpoint requires Bearer token")
    presented = authorization[len("Bearer "):].strip()
    if presented != required:
        raise HTTPException(status_code=401, detail="invalid evidence bearer token")


@app.get("/demo/evidence/{incident_id}")
async def evidence_bundle(
    incident_id: str,
    authorization: str | None = Header(default=None),
) -> dict:
    """Return the structured chain-of-custody bundle for an incident.

    JSON shape matches `bundle_incident()`. 404 if no events buffered.
    Requires Bearer auth when `GUARDIAN_EVIDENCE_AUTH_TOKEN` env is set.
    """
    _check_evidence_auth(authorization)
    bundle = _bundle_incident(incident_id)
    if bundle.get("status") != "ok":
        raise HTTPException(status_code=404, detail=bundle.get("error", "no evidence"))
    return bundle


@app.get("/demo/evidence/{incident_id}/html", response_class=HTMLResponse)
async def evidence_html(
    incident_id: str,
    authorization: str | None = Header(default=None),
) -> HTMLResponse:
    """Return the human-readable HTML evidence packet for an incident.

    Self-contained document (inline CSS) with embedded timeline JSON so an
    auditor can re-derive the chain hash from the HTML alone. Saves as
    PDF via browser print. 404 if no events buffered. Bearer-gated when
    `GUARDIAN_EVIDENCE_AUTH_TOKEN` is set.

    Response includes `Content-Disposition: attachment` so click-to-save
    works as a one-step download for filing.
    """
    _check_evidence_auth(authorization)
    rendered = _render_evidence_html(incident_id)
    if rendered.get("status") != "ok":
        raise HTTPException(status_code=404, detail=rendered.get("error", "no evidence"))
    return HTMLResponse(
        content=rendered["html"],
        status_code=200,
        headers={
            "Content-Disposition": (
                f'inline; filename="evidence-{incident_id}.html"'
            ),
        },
    )


@app.get("/board-slide/{filing_id}", response_class=HTMLResponse)
async def board_slide(filing_id: str) -> HTMLResponse:
    """Return the board-ready 16:9 slide for a Sponsor Sustainability TNFD filing.

    PLAN_V3.md Move 3 — Maya CSO's #1 ask. The CSO clicks the link from
    the Ops Center Sponsor ack card, the slide opens in a new tab, she
    clicks "Download as PNG" (html2canvas), drags the PNG into Slide 14
    of her Q2 board pack. No public auth gate — the slide content is
    aggregate-only (no PII) and serves as audit-trail evidence.
    """
    rendered = _render_board_slide(filing_id)
    if rendered.get("status") != "ok":
        raise HTTPException(status_code=404, detail=rendered.get("error", "no slide"))
    return HTMLResponse(
        content=rendered["html"],
        status_code=200,
        headers={
            "Content-Disposition": (
                f'inline; filename="board-slide-{filing_id}.html"'
            ),
        },
    )


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
