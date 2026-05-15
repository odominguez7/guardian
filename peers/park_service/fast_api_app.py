# Copyright 2026 GUARDIAN
# FastAPI host for the Park Service Agent (A2A peer #1).
#
# Mirrors app/fast_api_app.py but mounts the peer's ADK app at /a2a/park_service.
# Deployed as a SEPARATE Cloud Run service: `guardian-park-service`.

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import google.auth
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH, EXTENDED_AGENT_CARD_PATH
from fastapi import FastAPI
from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from peers.park_service.agent import app as adk_app

# Guard import-time auth so the service still binds a port in CI / no-ADC
# environments. Real Gemini calls fail later with a clear error rather than
# crashing at import. Symmetric to the fix in app/agent.py and the peer
# agent.py modules (codex /review 2026-05-15).
try:
    _, project_id = google.auth.default()
except Exception as _adc_err:
    import logging as _logging

    _logging.warning(
        "ADC unavailable when starting park_service FastAPI app — service "
        "will start but live Gemini calls fail until ADC is present: %s",
        _adc_err,
    )
    project_id = None

runner = Runner(
    app=adk_app,
    artifact_service=InMemoryArtifactService(),
    session_service=InMemorySessionService(),
)

request_handler = DefaultRequestHandler(
    agent_executor=A2aAgentExecutor(runner=runner),
    task_store=InMemoryTaskStore(),
)

A2A_RPC_PATH = f"/a2a/{adk_app.name}"


async def build_dynamic_agent_card() -> AgentCard:
    """Builds the Park Service agent card dynamically from the root_agent."""
    builder = AgentCardBuilder(
        agent=adk_app.root_agent,
        capabilities=AgentCapabilities(streaming=True),
        rpc_url=f"{os.getenv('APP_URL', 'http://0.0.0.0:8001')}{A2A_RPC_PATH}",
        agent_version=os.getenv("AGENT_VERSION", "0.1.0"),
    )
    return await builder.build()


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
    title="guardian-park-service",
    description=(
        "Park Service Operations agent. A2A peer of GUARDIAN. Receives "
        "wildlife-threat incident reports and dispatches rangers."
    ),
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "agent": "park_service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
