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

# Park Service Cloud Run URL. Set in env per environment.
# Local dev: http://localhost:8001
# Cloud Run: https://guardian-park-service-<hash>.us-central1.run.app
PARK_SERVICE_URL = os.environ.get("PARK_SERVICE_URL", "http://localhost:8001")
PARK_SERVICE_A2A_PATH = "/a2a/park_service"

# Cap how long we wait for a peer to respond. The peer can do real work
# (call its model, run dispatch_rangers) so 30s is generous but not infinite.
_A2A_TIMEOUT_S = 30.0


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

    peer_url = PARK_SERVICE_URL.rstrip("/")
    rpc_url = f"{peer_url}{PARK_SERVICE_A2A_PATH}"

    # The peer's agent expects a natural-language instruction in the message
    # body. We send a structured JSON payload so the peer's LLM extracts
    # incident_id, location, severity unambiguously and calls dispatch_rangers.
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
            return _unwrap_response(response)
    except A2AClientError as e:
        logger.warning("A2A call to park_service failed: %s", e)
        return {
            "status": "error",
            "error": f"a2a_transport: {type(e).__name__}: {e}",
            "_peer": "park_service",
        }
    except httpx.HTTPError as e:
        logger.warning("HTTP error calling park_service peer: %s", e)
        return {
            "status": "error",
            "error": f"http_transport: {type(e).__name__}: {e}",
            "_peer": "park_service",
        }


async def get_park_service_card() -> dict:
    """Fetch the Park Service peer's public agent card.

    Use this for diagnostic / discovery questions ("what can the Park Service
    agent do?"). Returns the agent.json the peer publishes at its well-known
    A2A path. Not for routing decisions — for routing, use notify_park_service.
    """
    peer_url = PARK_SERVICE_URL.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            resolver = A2ACardResolver(
                httpx_client=http,
                base_url=peer_url,
                agent_card_path=f"{PARK_SERVICE_A2A_PATH}/.well-known/agent-card.json",
            )
            card = await resolver.get_agent_card()
            return {
                "status": "ok",
                "_peer": "park_service",
                "card": card.model_dump(mode="json"),
            }
    except Exception as e:
        return {
            "status": "error",
            "error": f"{type(e).__name__}: {e}",
            "_peer": "park_service",
        }


def _unwrap_response(response) -> dict:
    """Pull the structured tool output out of an A2A SendMessageResponse.

    A2A peers wrap their tool result inside Message.parts[].text, OR (for
    Task-shaped responses) inside Task.history[].parts[].text or
    Task.artifacts[].parts[].text. The Park Service peer returns the
    dispatch_rangers dict as JSON inside one of those text parts. We harvest
    text from every plausible location and parse the JSON.
    """
    try:
        root = response.root  # SendMessageSuccessResponse | JSONRPCErrorResponse

        # JSON-RPC error envelope
        if hasattr(root, "error") and root.error is not None:
            return {
                "status": "error",
                "error": f"jsonrpc_error: {root.error.code} {root.error.message}",
                "_peer": "park_service",
            }

        result = root.result  # Task or Message
        text_blob = _collect_text(result)

        # Best-effort: peer returned the dispatch_rangers JSON inside the text.
        parsed = _try_parse_json_blob(text_blob)
        if parsed is not None:
            parsed.setdefault("_peer", "park_service")
            return parsed

        return {
            "status": "ok",
            "_peer": "park_service",
            "raw_response": text_blob[:2000],
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"unwrap_failed: {type(e).__name__}: {e}",
            "_peer": "park_service",
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

    # Message.parts
    _from_parts(getattr(obj, "parts", None))

    # Task.status.message.parts
    status = getattr(obj, "status", None)
    if status is not None:
        msg = getattr(status, "message", None)
        if msg is not None:
            _from_parts(getattr(msg, "parts", None))

    # Task.history[].parts (full conversation echo)
    for msg in getattr(obj, "history", None) or []:
        _from_parts(getattr(msg, "parts", None))

    # Task.artifacts[].parts (tool outputs / agent products)
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

    # Unwrap ADK's "<tool>_response": {...} envelope, but only when the wrapper
    # is the sole key — preserves any peer that returns its own multi-key dict.
    if len(last_obj) == 1:
        only_key = next(iter(last_obj))
        only_val = last_obj[only_key]
        if only_key.endswith("_response") and isinstance(only_val, dict):
            return only_val

    return last_obj
