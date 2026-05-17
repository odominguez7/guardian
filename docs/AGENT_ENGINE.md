# Vertex AI Agent Engine deployment (Track 3 alignment)

The Google for Startups AI Agents Challenge Track 3 — "Refactor for Marketplace + Gemini Enterprise" — lists three valid infrastructure targets in the official rules:

> **Infrastructure**: Google Cloud deployment (e.g., Agent Engine Runtime, Cloud Run, or GKE).

GUARDIAN ships on **two** of the three:

| Runtime | Surface | What it hosts |
|---|---|---|
| **Cloud Run** | `https://guardian-180171737110.us-central1.run.app` | FastAPI + WebSocket firehose for the Ops Center, A2A peer endpoints, `/livecam/spot` endpoint, board-slide renderer |
| **Vertex AI Agent Engine** | `projects/.../reasoningEngines/<id>` | ADK-blessed runtime for the `root_agent`, discoverable by the ADK client SDK and Gemini Enterprise consumers |

The two runtimes share the SAME `root_agent` object (imported from `app.agent`). Cloud Run is the public traffic + WebSocket surface for the demo's live UI; Agent Engine is the ADK runtime that judges + enterprise buyers see when they go through the agent-discovery layer.

## Why both?

| Lens | Cloud Run alone | Agent Engine alone | Both (current) |
|---|---|---|---|
| Public demo URL | ✅ | ❌ (no public HTTP) | ✅ |
| WebSocket firehose | ✅ | ❌ | ✅ |
| ADK client SDK discovery | partial | ✅ canonical | ✅ |
| Gemini Enterprise marketplace listing | requires shim | ✅ native | ✅ |
| Track 3 explicit infra mandate signal | 1 of 3 | 1 of 3 | **2 of 3** |

## Deploy

```bash
# One-shot (creates a new deployment):
make deploy-agent-engine

# Or directly:
uv run python deployment/agent_engine.py deploy

# Inspect / list / delete:
uv run python deployment/agent_engine.py list
uv run python deployment/agent_engine.py describe --resource-name projects/.../reasoningEngines/123
uv run python deployment/agent_engine.py delete --resource-name projects/.../reasoningEngines/123
```

The staging bucket is `gs://guardian-gfs-2026-agent-engine-staging` (override via `AGENT_ENGINE_STAGING_BUCKET`). The deploy script reads `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` from the active gcloud config — make sure the `guardian` config is active before invoking (`gcloud config configurations activate guardian`).

## Idempotency

If `AGENT_ENGINE_RESOURCE_NAME` is exported, `deploy` updates that resource in place. Otherwise it creates a new one and prints the resource name to export.

## What gets uploaded

- The `root_agent` Python object (built lazily via `app.agent.root_agent`)
- Runtime requirements pinned in `RUNTIME_REQUIREMENTS` (matches `pyproject.toml` orchestration deps)
- Agent Engine builds a container internally; staging bucket holds the artifact

## Verification after deploy

```bash
# From any machine with ADC:
uv run python -c "
import vertexai
from vertexai import agent_engines
vertexai.init(project='guardian-gfs-2026', location='us-central1')
remote = agent_engines.get('projects/.../reasoningEngines/<id>')
print(remote.query(input='What does GUARDIAN do?'))
"
```

## Hackathon judging surface

Devpost submission lists both URLs:
1. **Cloud Run demo**: `https://guardian-ops-center-180171737110.us-central1.run.app/` (Ops Center) + `https://guardian-180171737110.us-central1.run.app/` (orchestrator A2A)
2. **Agent Engine resource**: `projects/guardian-gfs-2026/locations/us-central1/reasoningEngines/<id>` (judges discover via ADK SDK)

Both are required reading for the Technical Implementation 30% dimension.
