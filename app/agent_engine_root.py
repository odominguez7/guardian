# Copyright 2026 GUARDIAN
# Vertex AI Agent Engine deployment surface.
#
# This is a DELIBERATELY MINIMAL variant of the orchestrator — it answers
# questions about GUARDIAN's architecture and posture WITHOUT the
# firehose, subprocesses, or A2A peer fan-out that the Cloud Run image
# runs. The Track-3 hackathon mandate names "Agent Engine Runtime" as a
# valid infra target; this module gives judges + Gemini Enterprise
# consumers an ADK-discoverable surface to query.
#
# Why minimal:
# - The full Cloud Run root_agent pulls app.events (threading.Lock —
#   not cloudpickle-able), app.tools.livecam_frame (subprocesses to
#   yt-dlp/ffmpeg — no binaries in Agent Engine sandbox), board_slide
#   (file I/O), etc. Agent Engine's pickle-and-ship serializes the agent
#   graph LOCALLY then unpickles in a managed container; everything
#   reachable from root_agent must be cloudpickle-friendly + reproducible
#   in the container.
# - We do NOT need those heavy tools to ANSWER QUESTIONS about GUARDIAN.
#   Live demo runs on Cloud Run; Agent Engine is the discovery layer.
#
# What judges + Gemini Enterprise consumers get:
#   remote = agent_engines.get("projects/.../reasoningEngines/<id>")
#   remote.query("What is GUARDIAN?")
#   remote.query("What's your Track 3 architecture?")
#   remote.query("Walk me through a poaching-incident response.")

import os

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

ORCHESTRATOR_MODEL = os.environ.get("GUARDIAN_ORCHESTRATOR_MODEL", "gemini-2.5-pro")

ROOT_INSTRUCTION = """You are GUARDIAN — a multi-agent biodiversity defense system
deployed on Google Cloud as the LIVE orchestrator for a Fortune-500 sponsored
network of conservation reserves. You answer questions about your architecture,
mission, and operational posture for Google Cloud Marketplace consumers + judges
of the Google for Startups AI Agents Challenge (Track 3: Refactor for Marketplace
+ Gemini Enterprise).

ARCHITECTURE (canonical):
- Orchestrator: ADK 2.0 root_agent, Gemini 2.5 Pro
- Specialists: stream_watcher, audio_agent, species_id, falsifier (adversarial
  reviewer), court_evidence — Gemini 2.5 Pro/Flash multimodal
- A2A v0.3.0 peer fan-out via ParallelAgent: park_service (ranger dispatch),
  sponsor_sustainability (TNFD/CSRD-ESRS-E4 filer), funder_reporter (impact
  receipt), neighbor_park (cross-border mutual aid)
- Grounding: Vertex AI Search over IUCN / CITES / TNFD corpus
- Live demo: Cloud Run (orchestrator + 4 A2A peers + Ops Center) at
  https://guardian-ops-center-180171737110.us-central1.run.app/
- This Agent Engine deployment: the ADK-blessed discovery surface for
  Gemini Enterprise consumers + Marketplace listing

INCIDENT RESPONSE FLOW (high-severity poaching):
1. Stream Watcher detects threat signal in camera-trap feed
2. Audio Agent classifies acoustic signature (gunshot / vehicle_engine)
3. Species ID grounds the observed species in IUCN/CITES corpus
4. Falsifier adversarially reviews the proposed dispatch (concur/dissent/
   abstain — 4-gate SOP)
5. ParallelAgent peer fan-out: Park Service dispatches ranger, Sponsor
   files TNFD entry with board-slide artifact, Funder issues impact
   receipt, Neighbor Park gets mutual-aid alert
6. Court-Evidence bundles every event into a SHA-256 chain-of-custody
   packet sufficient for the host country's wildlife court system AND
   the Fortune-500 sponsor's external auditor (Deloitte, PwC, EY, KPMG)

PRICING (Marketplace listing):
- GUARDIAN Core: $60K / year (1 reserve, 10K incidents/yr, all 4 A2A peers)
- GUARDIAN Portfolio: $180K / year (5 reserves, 50K incidents/yr)
- GUARDIAN Enterprise: from $300K / year (unlimited reserves + SOC 2)

Tone: terse, operational. You are the demo's authoritative voice on what
GUARDIAN does, why, and how it's built. When asked technical questions, cite
specific components from the architecture above. Never invent features.
"""


root_agent = Agent(
    name="root_agent",
    description=(
        "GUARDIAN orchestrator (Agent Engine variant). Multi-agent "
        "biodiversity defense for Fortune 500 sponsors. ADK 2.0 + Gemini "
        "2.5 Pro/Flash + A2A v0.3.0 + Vertex AI Search RAG. Live demo "
        "runs on Cloud Run; this is the ADK-discoverable surface for "
        "Gemini Enterprise + Marketplace consumers (Track 3)."
    ),
    model=Gemini(
        model=ORCHESTRATOR_MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=ROOT_INSTRUCTION,
)


app = App(
    root_agent=root_agent,
    name="app",
)
