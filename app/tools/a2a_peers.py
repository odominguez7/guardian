# Copyright 2026 GUARDIAN
# A2A client tools — let GUARDIAN's orchestrator call its peer agents.
#
# Each peer is a separate Cloud Run service operated (in production) by a
# different organization. GUARDIAN talks to them over the A2A protocol via
# JSON-RPC over HTTPS, with the peer's agent card auto-discovered at
# `<peer_url>/a2a/<peer_name>/.well-known/agent-card.json`.

import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from urllib.parse import urlparse

import google.auth.transport.requests
import httpx
from a2a.client import A2ACardResolver, A2AClient, A2AClientError
from a2a.types import (
    Message,
    MessageSendParams,
    Role,
    SendMessageRequest,
    TextPart,
)
from google.oauth2 import id_token

from app import events

logger = logging.getLogger(__name__)

# Cap how long we wait for a peer to respond. The peer can do real work
# (call its model + tool). 60s read for 4-peer parallel cold-start: each
# peer spawns a Gemini Pro call that itself spins up; bumped from 30s
# after codex flagged simultaneous-cold-start timeouts as a demo risk.
_A2A_TIMEOUT = httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=10.0)

# Cache short-lived ID tokens per audience so we don't refetch on every call.
# Cloud Run ID tokens are valid for 1 hour; we expire after 45 min to be safe.
_ID_TOKEN_TTL_S = 45 * 60
_id_token_cache: dict[str, tuple[str, float]] = {}


def _is_local(url: str) -> bool:
    """True if the URL points at a local dev peer (no auth needed)."""
    host = urlparse(url).hostname or ""
    return host in {"localhost", "127.0.0.1", "0.0.0.0"} or host.endswith(".local")


def _fetch_id_token(audience: str) -> str | None:
    """Fetch a Cloud Run-compatible ID token for the audience (peer base URL).

    Returns None for local-dev URLs so we don't waste a metadata-server call.
    Uses a process-local cache to amortize the metadata round-trip.
    """
    if _is_local(audience):
        return None
    cached = _id_token_cache.get(audience)
    if cached is not None:
        token, expires_at = cached
        if time.time() < expires_at:
            return token
    try:
        auth_req = google.auth.transport.requests.Request()
        token = id_token.fetch_id_token(auth_req, audience)
        _id_token_cache[audience] = (token, time.time() + _ID_TOKEN_TTL_S)
        return token
    except Exception as e:
        # No ADC, or service account lacks roles/run.invoker on the peer.
        # Surface the failure as a clear error envelope upstream instead of
        # silently sending an unauthenticated request that 401s.
        logger.warning("ID token fetch failed for audience %s: %s", audience, e)
        return None


def mint_incident_id(seed: str | None = None) -> str:
    """Mint a stable GUARDIAN incident_id.

    Use this once per incident in the orchestrator's pre-tool wiring (NOT in
    the LLM's free-form generation). The same id flows into both peer calls
    so park_service and sponsor_sustainability records reconcile.

    Form: `GU-<12hex>`. When `seed` is provided (e.g. camera id + observation
    timestamp), the hex is derived deterministically from seed alone — NO
    wall-clock dependency, so reprocessing the same event across midnight UTC
    or after a multi-day delay yields the same id. When `seed` is None, falls
    back to a monotonic timestamp + uuid suffix (still non-replayable, but
    that's the intended behavior of the unseeded path).

    Why not bake the date? Codex challenge 2026-05-15 flagged that
    GU-YYYYMMDD-... reprocessing crosses date boundaries → distinct ids →
    audit/dedup breakage. The date prefix gave human-readable bucketing but
    cost more than it's worth.
    """
    if seed:
        digest = hashlib.sha256(seed.encode()).hexdigest()
        return f"GU-{digest[:12].upper()}"
    # Non-seeded fallback: time-monotonic to avoid uuid collision risk.
    fallback = f"{time.time_ns()}-{uuid.uuid4().hex}"
    digest = hashlib.sha256(fallback.encode()).hexdigest()
    return f"GU-{digest[:12].upper()}"

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
    "funder_reporter": {
        "env_var": "FUNDER_REPORTER_URL",
        "default_url": "http://localhost:8003",
        "a2a_path": "/a2a/funder_reporter",
    },
    "neighbor_park": {
        "env_var": "NEIGHBOR_PARK_URL",
        "default_url": "http://localhost:8004",
        "a2a_path": "/a2a/neighbor_park",
    },
}


def _peer_base_url(peer_name: str) -> str:
    """Return the peer's base URL (origin only, no path). Defensive against
    misconfigured env vars that accidentally include the A2A path."""
    cfg = _PEERS[peer_name]
    raw = os.environ.get(cfg["env_var"], cfg["default_url"]).rstrip("/")
    # Strip any accidentally-included path component; we want origin only.
    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        # Bare hostname or weird value — fall through and let the call fail loudly
        return raw
    return f"{parsed.scheme}://{parsed.netloc}"


def _peer_rpc_url(peer_name: str) -> str:
    cfg = _PEERS[peer_name]
    return f"{_peer_base_url(peer_name)}{cfg['a2a_path']}"


def _looks_echoed(result: dict, instruction: str) -> bool:
    """Detect when the peer LLM echoed the instruction payload instead of
    calling its tool. Failure mode under concurrent Gemini Pro load: the
    response is the input JSON, not the tool result.

    Heuristic: if the result has no `status` field AND it contains the
    `_peer` we injected but no operational fields (filing_id, ranger_unit,
    handoff_id, receipt_id, dashboard_url, posture, materiality), it's
    almost certainly an echo. The `source: "GUARDIAN orchestrator"` marker
    we put in every instruction payload is a strong tell.
    """
    if not isinstance(result, dict):
        return False
    if result.get("status") in ("dispatched", "filed", "accepted", "ok"):
        return False
    op_signals = {
        "filing_id", "ranger_unit", "handoff_id", "receipt_id",
        "dashboard_url", "posture", "materiality", "estimated_arrival_minutes",
        "impact_tier", "tnfd_entry", "handoff_record", "impact_entry",
    }
    if any(k in result for k in op_signals):
        return False
    # If the response carries our orchestrator-source marker, the LLM
    # literally regurgitated our instruction JSON.
    if result.get("source") == "GUARDIAN orchestrator":
        return True
    return False


async def _send_once(rpc_url: str, instruction: str, headers: dict, peer_name: str) -> dict:
    """Single A2A round trip. Used by _call_peer + its retry path."""
    try:
        async with httpx.AsyncClient(timeout=_A2A_TIMEOUT, headers=headers) as http:
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


async def _call_peer(peer_name: str, instruction: str, *, incident_id: str | None = None) -> dict:
    """Send a SendMessageRequest to a registered peer and unwrap the response.

    Returns the peer's tool result dict, with `_peer` injected for chain-of-
    custody. Transport / JSON-RPC errors become structured error envelopes.

    For Cloud Run peers deployed with --no-allow-unauthenticated, fetches a
    service-account ID token for the peer's audience and includes it as a
    Bearer credential. Localhost dev peers skip auth.

    Auto-retry-once on echo detection: under concurrent 4-peer fan-out
    Gemini Pro intermittently echoes the input JSON instead of calling
    its tool. We detect that pattern via `_looks_echoed` and retry the
    same RPC once. The second attempt nearly always succeeds because
    the cold-start has already happened.

    Emits A2A request/response events to the firehose so the Ops Center UI
    can visualize the fan-out in real time.
    """
    base_url = _peer_base_url(peer_name)
    rpc_url = _peer_rpc_url(peer_name)

    t0 = time.monotonic_ns()
    events.emit(
        kind="a2a_request",
        agent="root_agent",
        tool=f"notify_{peer_name}",
        incident_id=incident_id,
        severity="high",
        payload={"peer": peer_name, "rpc_url": rpc_url},
    )

    headers: dict[str, str] = {}
    if not _is_local(base_url):
        token = _fetch_id_token(base_url)
        if token is None:
            result = {
                "status": "error",
                "error": (
                    "auth_unavailable: could not fetch ID token for peer audience "
                    f"{base_url}. In Cloud Run, ensure the orchestrator's service "
                    "account has roles/run.invoker on the peer service."
                ),
                "_peer": peer_name,
            }
            events.emit(
                kind="a2a_response",
                agent=peer_name,
                tool=f"notify_{peer_name}",
                incident_id=incident_id,
                severity="error",
                payload={"error": result["error"]},
                latency_ms=(time.monotonic_ns() - t0) // 1_000_000,
            )
            return result
        headers["Authorization"] = f"Bearer {token}"

    result = await _send_once(rpc_url, instruction, headers, peer_name)

    # If the peer echoed the instruction instead of calling its tool, retry
    # up to 2 more times (3 total attempts). Gemini Pro under concurrent
    # 4-peer fan-out has been observed to echo the same payload twice in a
    # row when the prompt is identical — almost certainly a deterministic
    # decode given identical input. We mutate the instruction on each retry
    # (added retry directive + nonce) to break that determinism and force
    # a fresh tool-call decision. 400ms backoff lets Pro spin down before
    # the next attempt so the retry isn't another concurrent cold-start.
    _MAX_ECHO_RETRIES = 2
    for attempt in range(1, _MAX_ECHO_RETRIES + 1):
        if not _looks_echoed(result, instruction):
            break
        logger.warning(
            "Peer %s echoed instruction instead of calling tool; retry %d/%d",
            peer_name,
            attempt,
            _MAX_ECHO_RETRIES,
        )
        await asyncio.sleep(0.4)
        events.emit(
            kind="a2a_request",
            agent="root_agent",
            tool=f"notify_{peer_name}",
            incident_id=incident_id,
            severity="high",
            payload={
                "peer": peer_name,
                "rpc_url": rpc_url,
                "retry": attempt,
            },
        )
        retry_instruction = (
            f"[RETRY {attempt}] Previous attempt echoed the input JSON "
            f"instead of calling the tool. You MUST call the tool now "
            f"with the fields below. Do not echo.\n\n{instruction}"
        )
        result = await _send_once(rpc_url, retry_instruction, headers, peer_name)

    severity = "error" if result.get("status") == "error" else "high"
    events.emit(
        kind="a2a_response",
        agent=peer_name,
        tool=f"notify_{peer_name}",
        incident_id=incident_id,
        severity=severity,
        payload=result,
        latency_ms=(time.monotonic_ns() - t0) // 1_000_000,
    )
    return result


async def _resolve_peer_card(peer_name: str) -> dict:
    """Fetch a peer's public agent card. Used for diagnostics + A2A discovery.

    Same auth model as `_call_peer`: localhost is unauthenticated, Cloud Run
    URLs get a service-account ID token for the peer audience.
    """
    base = _peer_base_url(peer_name)
    cfg = _PEERS[peer_name]
    headers: dict[str, str] = {}
    if not _is_local(base):
        token = _fetch_id_token(base)
        if token is None:
            return {
                "status": "error",
                "error": (
                    "auth_unavailable: could not fetch ID token for peer audience "
                    f"{base}. Card endpoint requires invoker role on Cloud Run."
                ),
                "_peer": peer_name,
            }
        headers["Authorization"] = f"Bearer {token}"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=10.0), headers=headers) as http:
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
    return await _call_peer("park_service", instruction, incident_id=incident_id)


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
    return await _call_peer("sponsor_sustainability", instruction, incident_id=incident_id)


async def get_sponsor_sustainability_card() -> dict:
    """Fetch the Sponsor Sustainability peer's public agent card.

    Diagnostic / discovery only. For routing, use notify_sponsor_sustainability.
    """
    return await _resolve_peer_card("sponsor_sustainability")


# Mirror of peers/funder_reporter/agent.py _VALID_PROGRAMS. Keep in sync.
_VALID_FUNDER_PROGRAMS = {
    "elephants_at_risk",
    "rhino_horn_crisis",
    "biodiversity_corridor_2030",
    "predator_coexistence",
    "general_impact",
}


# ----- Peer #3: Funder Reporter ----------------------------------------------


async def notify_funder(
    incident_id: str,
    location: str,
    species_affected: str,
    severity: str,
    funder_program: str,
    observation_timestamp: str,
) -> dict:
    """File a wildlife-incident impact receipt with the Funder Reporter peer.

    A2A call to a SEPARATE agent operated by a conservation funder
    (WWF / IUCN / IFAW style). The funder's quarterly impact report
    auto-files every incident GUARDIAN detects on reserves the foundation
    sponsors. GUARDIAN bundles the returned receipt into its evidence chain.

    Call this for ANY incident on a funder-sponsored reserve. Most reserves
    have at least one funder program; default to `general_impact` if unsure.

    Args:
        incident_id: Same incident_id used across all peer calls.
        location: Reserve / sector observed.
        species_affected: Common name.
        severity: GUARDIAN severity — "low", "medium", "high", "critical".
        funder_program: One of "elephants_at_risk", "rhino_horn_crisis",
            "biodiversity_corridor_2030", "predator_coexistence",
            "general_impact".
        observation_timestamp: ISO 8601 timestamp.

    Returns:
        Dict from the Funder Reporter peer with status, receipt_id,
        dashboard_url, impact_tier, funder_program, and impact_entry.
    """
    if (
        not incident_id
        or not location
        or not species_affected
        or not severity
        or not funder_program
        or not observation_timestamp
    ):
        return {
            "status": "error",
            "error": (
                "incident_id, location, species_affected, severity, "
                "funder_program, observation_timestamp are required"
            ),
            "_peer": "funder_reporter",
        }

    # Coerce off-list funder_program to general_impact. The peer rejects
    # unknowns with a structured error, which produces no funder card in
    # the Ops Center — looks like the peer didn't respond. Codex flagged
    # this as a demo failure mode if the orchestrating LLM hallucinates
    # a program name (e.g. "tigers_program" instead of "elephants_at_risk").
    if funder_program.lower() not in _VALID_FUNDER_PROGRAMS:
        funder_program = "general_impact"

    payload = {
        "incident_id": incident_id,
        "location": location,
        "species_affected": species_affected,
        "severity": severity,
        "funder_program": funder_program,
        "observation_timestamp": observation_timestamp,
        "source": "GUARDIAN orchestrator",
    }
    instruction = (
        "Incoming wildlife-impact incident from GUARDIAN, eligible for "
        f"funder impact reporting. Call file_impact_report with these fields "
        f"and return the result verbatim:\n{json.dumps(payload, indent=2)}"
    )
    return await _call_peer("funder_reporter", instruction, incident_id=incident_id)


async def get_funder_card() -> dict:
    """Fetch the Funder Reporter peer's public agent card."""
    return await _resolve_peer_card("funder_reporter")


# ----- Peer #4: Neighbor Park ------------------------------------------------


async def notify_neighbor_park(
    incident_id: str,
    origin_park: str,
    severity: str,
    species_affected: str,
    crossover_corridor: str,
    observation_timestamp: str,
) -> dict:
    """Send a cross-border mutual-aid request to the Neighbor Park peer.

    A2A call to a SEPARATE agent operated by an ADJACENT park (Maasai Mara,
    adjacent to Serengeti and other trans-frontier conservation areas).
    When a poaching incident at one reserve might cross the border, the
    neighbor's rangers need to be alerted so they can elevate posture at
    the crossover corridor.

    Call this for critical/high severity incidents near trans-frontier
    boundaries.

    Args:
        incident_id: Same incident_id used across all peer calls.
        origin_park: Where the incident originated (e.g. "Serengeti
            National Park, Tanzania").
        severity: GUARDIAN severity.
        species_affected: Common name.
        crossover_corridor: Named / coord-described likely crossing
            (e.g. "Mara River, Sand River confluence").
        observation_timestamp: ISO 8601 timestamp.

    Returns:
        Dict with status (accepted), handoff_id, posture, window_open_until,
        responding_park, handoff_record.
    """
    if (
        not incident_id
        or not origin_park
        or not severity
        or not species_affected
        or not crossover_corridor
        or not observation_timestamp
    ):
        return {
            "status": "error",
            "error": (
                "incident_id, origin_park, severity, species_affected, "
                "crossover_corridor, observation_timestamp are required"
            ),
            "_peer": "neighbor_park",
        }

    payload = {
        "incident_id": incident_id,
        "origin_park": origin_park,
        "severity": severity,
        "species_affected": species_affected,
        "crossover_corridor": crossover_corridor,
        "observation_timestamp": observation_timestamp,
        "source": "GUARDIAN orchestrator",
    }
    instruction = (
        "Incoming cross-border mutual-aid request from GUARDIAN. Call "
        f"accept_mutual_aid with these fields and return the result "
        f"verbatim:\n{json.dumps(payload, indent=2)}"
    )
    return await _call_peer("neighbor_park", instruction, incident_id=incident_id)


async def get_neighbor_park_card() -> dict:
    """Fetch the Neighbor Park peer's public agent card."""
    return await _resolve_peer_card("neighbor_park")


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
    so we scan tail-first.

    Three unwrap cases handled:
      1. `{"<tool>_response": {...}}` — ADK auto-wrapper (single key, ends in
         _response). Drill in once.
      2. `{"<tool>_response": [...]}` — same wrapper but tool returned a list
         (e.g. multi-result query). Wrap as {"results": [...]} so the caller
         still gets a dict.
      3. Naked dict. Pass through.
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
        if only_key.endswith("_response"):
            if isinstance(only_val, dict):
                return only_val
            if isinstance(only_val, list):
                return {"results": only_val, "_wrapped_from": only_key}

    return last_obj
