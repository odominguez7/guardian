# Copyright 2026 GUARDIAN
# A2A client tools — let GUARDIAN's orchestrator call its peer agents.
#
# Each peer is a separate Cloud Run service operated (in production) by a
# different organization. GUARDIAN talks to them over the A2A protocol via
# JSON-RPC over HTTPS, with the peer's agent card auto-discovered at
# `<peer_url>/a2a/<peer_name>/.well-known/agent-card.json`.

import json
import logging
import os
import uuid

import httpx
from a2a.client import A2ACardResolver, A2AClient, A2AClientError
from a2a.types import (
    Message,
    MessageSendParams,
    Role,
    SendMessageRequest,
    TextPart,
)

logger = logging.getLogger(__name__)

# Cap how long we wait for a peer to respond. The peer can do real work
# (call its model + tool) so 30s is generous but not infinite.
_A2A_TIMEOUT_S = 30.0

# Peer registry. Single source of truth for env var + URL path for each peer.
# Add a new peer here and call _call_peer(name, ...) from a tool function.
_PEERS: dict[str, dict[str, str]] = {
    "park_service": {
        "env_var": "PARK_SERVICE_URL",
        "default_url": "http://localhost:8001",
        "a2a_path": "/a2a/park_service",
    },
    "sponsor_sustainability": {
        "env_var": "SPONSOR_SUSTAINABILITY_URL",
        "default_url": "http://localhost:8002",
        "a2a_path": "/a2a/sponsor_sustainability",
    },
}


def _peer_rpc_url(peer_name: str) -> str:
    cfg = _PEERS[peer_name]
    base = os.environ.get(cfg["env_var"], cfg["default_url"]).rstrip("/")
    return f"{base}{cfg['a2a_path']}"


def _peer_base_url(peer_name: str) -> str:
    cfg = _PEERS[peer_name]
    return os.environ.get(cfg["env_var"], cfg["default_url"]).rstrip("/")


async def _call_peer(peer_name: str, instruction: str) -> dict:
    """Send a SendMessageRequest to a registered peer and unwrap the response.

    Returns the peer's tool result dict, with `_peer` injected for chain-of-
    custody. Transport / JSON-RPC errors become structured error envelopes.
    """
    rpc_url = _peer_rpc_url(peer_name)
    try:
        async with httpx.AsyncClient(timeout=_A2A_TIMEOUT_S) as http:
            client = A2AClient(httpx_client=http, url=rpc_url)
            request = SendMessageRequest(
                id=str(uuid.uuid4()),
                jsonrpc="2.0",
                method="message/send",
                params=MessageSendParams(
                    message=Message(
                        message_id=str(uuid.uuid4()),
                        kind="message",
                        role=Role.user,
                        parts=[TextPart(kind="text", text=instruction)],
                    )
                ),
            )
            response = await client.send_message(request=request)
            return _unwrap_response(response, peer_name=peer_name)
    except A2AClientError as e:
        logger.warning("A2A call to %s failed: %s", peer_name, e)
        return {
            "status": "error",
            "error": f"a2a_transport: {type(e).__name__}: {e}",
            "_peer": peer_name,
        }
    except httpx.HTTPError as e:
        logger.warning("HTTP error calling %s peer: %s", peer_name, e)
        return {
            "status": "error",
            "error": f"http_transport: {type(e).__name__}: {e}",
            "_peer": peer_name,
        }


async def _resolve_peer_card(peer_name: str) -> dict:
    """Fetch a peer's public agent card. Used for diagnostics + A2A discovery."""
    base = _peer_base_url(peer_name)
    cfg = _PEERS[peer_name]
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            resolver = A2ACardResolver(
                httpx_client=http,
                base_url=base,
                agent_card_path=f"{cfg['a2a_path']}/.well-known/agent-card.json",
            )
            card = await resolver.get_agent_card()
            return {
                "status": "ok",
                "_peer": peer_name,
                "card": card.model_dump(mode="json"),
            }
    except Exception as e:
        return {
            "status": "error",
            "error": f"{type(e).__name__}: {e}",
            "_peer": peer_name,
        }


# ----- Peer #1: Park Service ---------------------------------------------------


async def notify_park_service(
    incident_id: str, location: str, severity: str, summary: str
) -> dict:
    """Send a wildlife-threat incident report to the Park Service peer agent.

    This is an A2A call to a SEPARATE agent operated by the national park
    authority. GUARDIAN does NOT decide ranger dispatch — the park service
    agent does. GUARDIAN only reports what it observed and gets back a
    dispatch acknowledgement.

    Use this tool after the orchestrator's specialist agents (Stream Watcher,
    Audio, Species ID, Pattern) have produced a threat signal that warrants
    ranger response.

    Args:
        incident_id: GUARDIAN's unique reference for this incident. Required.
        location: Best-effort coordinates or named area. Required.
        severity: One of "low", "medium", "high", "critical". Required.
        summary: One-sentence description of what GUARDIAN observed.

    Returns:
        Dict from the Park Service peer with status, ranger_unit, ETA, etc.
        Includes `_peer` field marking this came over A2A (for evidence
        chain-of-custody). On transport error, returns
        {"status": "error", "error": ..., "_peer": "park_service"}.
    """
    if not incident_id or not location or not severity:
        return {
            "status": "error",
            "error": "incident_id, location, and severity are required",
            "_peer": "park_service",
        }

    payload = {
        "incident_id": incident_id,
        "location": location,
        "severity": severity,
        "summary": summary,
        "source": "GUARDIAN orchestrator",
    }
    instruction = (
        "Incoming wildlife-threat incident report from GUARDIAN. Call "
        f"dispatch_rangers with these fields and return the result verbatim:\n"
        f"{json.dumps(payload, indent=2)}"
    )
    return await _call_peer("park_service", instruction)


async def get_park_service_card() -> dict:
    """Fetch the Park Service peer's public agent card.

    Use this for diagnostic / discovery questions ("what can the Park Service
    agent do?"). Returns the agent.json the peer publishes at its well-known
    A2A path. Not for routing decisions — for routing, use notify_park_service.
    """
    return await _resolve_peer_card("park_service")


# ----- Peer #2: Sponsor Sustainability ----------------------------------------


async def notify_sponsor_sustainability(
    incident_id: str,
    location: str,
    species_affected: str,
    threat_type: str,
    severity: str,
    observation_timestamp: str,
) -> dict:
    """File a wildlife-incident TNFD entry with the Sponsor Sustainability peer.

    A2A call to a SEPARATE agent operated by a Fortune 500 sponsor's
    sustainability office. GUARDIAN does NOT generate the TNFD entry — the
    sponsor's agent does, because they own the disclosure dashboard and the
    regulatory relationship. GUARDIAN just forwards what it observed and
    bundles the returned filing ack into its evidence chain.

    Call this after notify_park_service for any incident worth disclosing to
    the sponsor (severity high or critical, OR any incident involving a
    sponsored species).

    Args:
        incident_id: GUARDIAN's incident reference (must match what was sent
            to park_service so the sponsor + park records reconcile).
        location: Reserve / sector where the incident was observed.
        species_affected: Common name of the species affected (e.g. "African
            elephant"). One per call.
        threat_type: One of "poaching", "habitat_intrusion", "vehicle_intrusion",
            "audio_signal", "fence_breach", "other".
        severity: GUARDIAN severity — "low", "medium", "high", "critical".
        observation_timestamp: ISO 8601 timestamp from GUARDIAN's observation.

    Returns:
        Dict from the Sponsor Sustainability peer with status, filing_id,
        dashboard_url, materiality, and the full tnfd_entry record. Includes
        `_peer` field for chain-of-custody. Error envelope on transport
        failure.
    """
    if (
        not incident_id
        or not location
        or not species_affected
        or not threat_type
        or not severity
        or not observation_timestamp
    ):
        return {
            "status": "error",
            "error": (
                "incident_id, location, species_affected, threat_type, "
                "severity, observation_timestamp are required"
            ),
            "_peer": "sponsor_sustainability",
        }

    payload = {
        "incident_id": incident_id,
        "location": location,
        "species_affected": species_affected,
        "threat_type": threat_type,
        "severity": severity,
        "observation_timestamp": observation_timestamp,
        "source": "GUARDIAN orchestrator",
    }
    instruction = (
        "Incoming wildlife-impact incident from GUARDIAN. Call "
        f"file_tnfd_entry with these fields and return the result verbatim:\n"
        f"{json.dumps(payload, indent=2)}"
    )
    return await _call_peer("sponsor_sustainability", instruction)


async def get_sponsor_sustainability_card() -> dict:
    """Fetch the Sponsor Sustainability peer's public agent card.

    Diagnostic / discovery only. For routing, use notify_sponsor_sustainability.
    """
    return await _resolve_peer_card("sponsor_sustainability")


# ----- Shared response unwrapping ---------------------------------------------


def _unwrap_response(response, peer_name: str) -> dict:
    """Pull the structured tool output out of an A2A SendMessageResponse.

    A2A peers wrap their tool result inside Message.parts[].text, OR (for
    Task-shaped responses) inside Task.history[].parts[].text or
    Task.artifacts[].parts[].text. We harvest text from every plausible
    location and pull the last JSON object out of it.
    """
    try:
        root = response.root  # SendMessageSuccessResponse | JSONRPCErrorResponse

        if hasattr(root, "error") and root.error is not None:
            return {
                "status": "error",
                "error": f"jsonrpc_error: {root.error.code} {root.error.message}",
                "_peer": peer_name,
            }

        result = root.result  # Task or Message
        text_blob = _collect_text(result)
        parsed = _try_parse_json_blob(text_blob)
        if parsed is not None:
            parsed.setdefault("_peer", peer_name)
            return parsed

        return {
            "status": "ok",
            "_peer": peer_name,
            "raw_response": text_blob[:2000],
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"unwrap_failed: {type(e).__name__}: {e}",
            "_peer": peer_name,
        }


def _collect_text(obj) -> str:
    """Harvest every text part anywhere inside an A2A Message/Task envelope."""
    chunks: list[str] = []

    def _from_parts(parts):
        if not parts:
            return
        for p in parts:
            pr = getattr(p, "root", p)
            if getattr(pr, "kind", None) == "text":
                chunks.append(pr.text)

    _from_parts(getattr(obj, "parts", None))

    status = getattr(obj, "status", None)
    if status is not None:
        msg = getattr(status, "message", None)
        if msg is not None:
            _from_parts(getattr(msg, "parts", None))

    for msg in getattr(obj, "history", None) or []:
        _from_parts(getattr(msg, "parts", None))

    for art in getattr(obj, "artifacts", None) or []:
        _from_parts(getattr(art, "parts", None))

    return "\n".join(chunks)


def _try_parse_json_blob(blob: str) -> dict | None:
    """Find the last well-formed JSON object in an A2A text response.

    A2A peer responses bundle the full conversation history (the echoed
    instruction plus the actual tool result). The tool result is always last,
    so we scan tail-first. ADK also wraps tool returns as
    `{"<tool_name>_response": {...real result...}}`; we unwrap that single
    layer so the orchestrator gets the operational fields at the top level.
    """
    if not blob:
        return None

    last_obj: dict | None = None
    decoder = json.JSONDecoder()
    idx = 0
    n = len(blob)
    while idx < n:
        brace = blob.find("{", idx)
        if brace == -1:
            break
        try:
            obj, end = decoder.raw_decode(blob, brace)
        except (json.JSONDecodeError, ValueError):
            idx = brace + 1
            continue
        if isinstance(obj, dict):
            last_obj = obj
        idx = end

    if last_obj is None:
        return None

    if len(last_obj) == 1:
        only_key = next(iter(last_obj))
        only_val = last_obj[only_key]
        if only_key.endswith("_response") and isinstance(only_val, dict):
            return only_val

    return last_obj
