"""Deploy GUARDIAN's root_agent to Vertex AI Agent Engine.

Track 3 mandate (Refactor for Marketplace + Gemini Enterprise) explicitly
names Agent Engine Runtime as one of the valid infra targets, alongside
Cloud Run and GKE. GUARDIAN runs on Cloud Run today; this script also
ships the orchestrator to Agent Engine so we hit BOTH mandated runtimes,
which is the maximum-credit position for the Technical Implementation 30%
judging dimension.

Cloud Run stays the public-traffic surface (the FastAPI + WebSocket
ops-center firehose lives there). Agent Engine becomes the ADK-blessed
runtime that judges + Gemini Enterprise consumers discover via the ADK
client SDK.

Usage (interactive):
    uv run python deployment/agent_engine.py deploy

Idempotent: if AGENT_ENGINE_RESOURCE_NAME is set in env (e.g. from prior
deployment), `deploy` updates that resource; otherwise creates new.

Inspect existing deployment:
    uv run python deployment/agent_engine.py describe
    uv run python deployment/agent_engine.py list
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

import vertexai
from vertexai import agent_engines

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def _project_id() -> str:
    return os.environ.get("GOOGLE_CLOUD_PROJECT") or "guardian-gfs-2026"


def _location() -> str:
    # Agent Engine deploys regional; us-central1 mirrors our Cloud Run.
    return os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")


def _staging_bucket() -> str:
    return os.environ.get("AGENT_ENGINE_STAGING_BUCKET",
                          f"gs://{_project_id()}-agent-engine-staging")


# Runtime requirements pinned to match the orchestrator's pyproject. Agent
# Engine builds a containerized environment from these, so they must be
# self-contained (no implicit reach back into the source tree).
RUNTIME_REQUIREMENTS = [
    "google-adk[bigquery-analytics]>=1.21.0",
    "a2a-sdk~=0.3.22",
    "google-cloud-aiplatform[evaluation]>=1.130.0",
    "google-cloud-logging>=3.12.0,<4.0.0",
    "fastapi>=0.115.8,<1.0.0",
    "yt-dlp>=2025.0.0",
]

DISPLAY_NAME = "guardian-orchestrator"
DESCRIPTION = (
    "GUARDIAN: multi-agent biodiversity defense + auto-filed TNFD/CSRD "
    "disclosure for Fortune 500 sponsors. ADK 2.0 ParallelAgent fan-out "
    "to 4 A2A peers (park service, sponsor sustainability, funder "
    "reporter, neighbor park) with Gemini 2.5 Pro/Flash, Vertex AI "
    "Search RAG, and adversarial Falsifier review."
)


def _load_root_agent():
    """Lazy import so `list` / `describe` work without ADC."""
    # Add repo root to sys.path so `from app.agent import root_agent` works
    # when invoked from anywhere.
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from app.agent import root_agent  # noqa: WPS433 (lazy import intentional)
    return root_agent


def cmd_deploy(args: argparse.Namespace) -> int:
    vertexai.init(
        project=_project_id(),
        location=_location(),
        staging_bucket=_staging_bucket(),
    )
    root_agent = _load_root_agent()
    existing = os.environ.get("AGENT_ENGINE_RESOURCE_NAME", "").strip()

    if existing:
        log.info("Updating existing Agent Engine: %s", existing)
        remote = agent_engines.update(
            resource_name=existing,
            agent_engine=root_agent,
            requirements=RUNTIME_REQUIREMENTS,
            display_name=DISPLAY_NAME,
            description=DESCRIPTION,
        )
    else:
        log.info("Creating new Agent Engine deployment in %s/%s",
                 _project_id(), _location())
        remote = agent_engines.create(
            agent_engine=root_agent,
            requirements=RUNTIME_REQUIREMENTS,
            display_name=DISPLAY_NAME,
            description=DESCRIPTION,
        )

    log.info("DEPLOYED")
    log.info("  resource_name: %s", remote.resource_name)
    log.info("  Export: export AGENT_ENGINE_RESOURCE_NAME=%s", remote.resource_name)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    vertexai.init(project=_project_id(), location=_location())
    engines = list(agent_engines.list())
    if not engines:
        log.info("No Agent Engine deployments found in %s/%s",
                 _project_id(), _location())
        return 0
    for e in engines:
        log.info("- %s | %s | %s", e.display_name, e.resource_name,
                 e.create_time.isoformat() if e.create_time else "?")
    return 0


def cmd_describe(args: argparse.Namespace) -> int:
    vertexai.init(project=_project_id(), location=_location())
    name = args.resource_name or os.environ.get("AGENT_ENGINE_RESOURCE_NAME", "")
    if not name:
        log.error("Pass --resource-name or set AGENT_ENGINE_RESOURCE_NAME")
        return 2
    e = agent_engines.get(name)
    log.info("display_name: %s", e.display_name)
    log.info("description : %s", (e.description or "")[:200])
    log.info("create_time : %s", e.create_time)
    log.info("update_time : %s", e.update_time)
    log.info("resource    : %s", e.resource_name)
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    vertexai.init(project=_project_id(), location=_location())
    name = args.resource_name or os.environ.get("AGENT_ENGINE_RESOURCE_NAME", "")
    if not name:
        log.error("Pass --resource-name or set AGENT_ENGINE_RESOURCE_NAME")
        return 2
    e = agent_engines.get(name)
    e.delete()
    log.info("Deleted %s", name)
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("deploy")
    sub.add_parser("list")
    describe = sub.add_parser("describe")
    describe.add_argument("--resource-name", default=None)
    delete = sub.add_parser("delete")
    delete.add_argument("--resource-name", default=None)
    args = p.parse_args()

    if args.cmd == "deploy":
        return cmd_deploy(args)
    if args.cmd == "list":
        return cmd_list(args)
    if args.cmd == "describe":
        return cmd_describe(args)
    if args.cmd == "delete":
        return cmd_delete(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
