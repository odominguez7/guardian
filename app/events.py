"""GUARDIAN — structured event firehose.

Emits one structured event per significant orchestrator/peer action: tool
calls, transfer_to_agent transitions, A2A peer requests/responses,
incident lifecycle. Events are JSON-serializable and pushed to a thread-
safe ring buffer + asyncio broadcast queues for any WebSocket subscriber.

The Ops Center frontend consumes this stream to animate the live map.

Schema:
    {
      "id":         "evt_<12hex>",
      "ts":         "2026-05-15T19:42:01.123456Z",   # ISO 8601 UTC
      "kind":       "tool_start" | "tool_end" | "agent_transfer" |
                    "a2a_request" | "a2a_response" | "incident_event",
      "agent":      "root_agent" | "stream_watcher" | "park_service" | ...
      "tool":       "analyze_video_clip" | "notify_park_service" | ...
      "incident_id": "GU-..." or None,
      "severity":   "critical" | "high" | "medium" | "low" | "info",
      "payload":    {...},                            # tool args / result
      "latency_ms": int or None,                       # for *_end events
    }
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import threading
import time
from collections import deque
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Ring buffer of the last N events so a new WebSocket subscriber can backfill.
_BUFFER_SIZE = int(os.environ.get("GUARDIAN_EVENT_BUFFER", "200"))
_buffer: deque[dict] = deque(maxlen=_BUFFER_SIZE)
_buffer_lock = asyncio.Lock()

# Active subscriber queues. Each WebSocket gets its own. Slow subscribers get
# their oldest event dropped to keep the broadcast moving.
_subscribers: set[asyncio.Queue[dict]] = set()
_subscribers_lock = asyncio.Lock()

# Thread-level lock for the registry + ring buffer. asyncio.Lock only protects
# coroutines on the same event loop; if any code path emits from a worker
# thread (e.g., google.cloud SDKs that run in thread executors) the buffer +
# subscriber-set need real OS-thread mutual exclusion.
# Codex challenge 2026-05-15 (final sweep) flagged this gap.
_thread_lock = threading.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_event_id() -> str:
    seed = f"{time.time_ns()}-{id(_buffer)}"
    return f"evt_{hashlib.sha256(seed.encode()).hexdigest()[:12]}"


def emit(
    *,
    kind: str,
    agent: str,
    tool: str | None = None,
    incident_id: str | None = None,
    severity: str = "info",
    payload: dict[str, Any] | None = None,
    latency_ms: int | None = None,
) -> dict:
    """Build + broadcast a structured event. Returns the event for inline use."""
    event = {
        "id": _new_event_id(),
        "ts": _now_iso(),
        "kind": kind,
        "agent": agent,
        "tool": tool,
        "incident_id": incident_id,
        "severity": severity,
        "payload": payload or {},
        "latency_ms": latency_ms,
    }
    _broadcast(event)
    return event


def _broadcast(event: dict) -> None:
    """Push to ring buffer + every subscriber queue.

    Safe across three call patterns (codex challenge 2026-05-15 surfaced
    all three as latent issues):
      1. From an async coroutine (event loop running, current thread is
         the loop's thread). Use queue.put_nowait directly.
      2. From sync code on the loop's thread (e.g., a tool_span __exit__
         in a sync orchestrator path). Use put_nowait directly.
      3. From a worker thread or process WITHOUT a running loop. Use
         loop.call_soon_threadsafe so the put happens on the loop's
         thread, avoiding "RuntimeError: no running event loop".

    Ring buffer append + subscriber snapshot are protected by an OS-thread
    lock (codex final sweep 2026-05-15 flagged the asyncio-only locks as
    insufficient for cross-thread emit calls; if any tool runs in a thread
    executor, the deque append + set iteration would race).
    """
    with _thread_lock:
        _buffer.append(event)
        # Snapshot under the thread lock so the iteration below isn't
        # racing with concurrent add/remove from subscribe()/unsubscribe.
        subs = list(_subscribers)

    try:
        loop = asyncio.get_running_loop()
        on_loop = True
    except RuntimeError:
        loop = None
        on_loop = False

    for q in subs:
        if on_loop:
            _put_with_backpressure(q, event)
        else:
            # Not on the loop. Schedule the put on the loop's thread.
            # Use the queue's event loop if accessible; otherwise fall
            # back to the buffered ring (already populated above).
            queue_loop = getattr(q, "_loop", None)
            if queue_loop is not None:
                try:
                    queue_loop.call_soon_threadsafe(
                        _put_with_backpressure, q, event
                    )
                except RuntimeError:
                    # loop is closed; ignore this subscriber, ring buffer wins
                    pass


def _put_with_backpressure(q: "asyncio.Queue[dict]", event: dict) -> None:
    """Put with old-event eviction on full. Must run on the queue's loop."""
    try:
        q.put_nowait(event)
    except asyncio.QueueFull:
        try:
            q.get_nowait()
            q.put_nowait(event)
        except (asyncio.QueueEmpty, asyncio.QueueFull):
            pass


async def subscribe() -> AsyncGenerator[dict, None]:
    """Async generator yielding every event for the lifetime of the subscriber.

    On connect, replays the ring buffer (up to _BUFFER_SIZE recent events) so
    clients always see context. Drops oldest on slow consumers.

    Usage:
        async for event in subscribe():
            await websocket.send_json(event)
    """
    queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=_BUFFER_SIZE)

    with _thread_lock:
        _subscribers.add(queue)
        # Replay buffer snapshot under the same lock so a concurrent
        # _broadcast doesn't slip an event past us between snapshot + listen.
        replay = list(_buffer)

    try:
        for evt in replay:
            try:
                queue.put_nowait(evt)
            except asyncio.QueueFull:
                break

        while True:
            evt = await queue.get()
            yield evt
    finally:
        with _thread_lock:
            _subscribers.discard(queue)


async def snapshot() -> list[dict]:
    """Return a copy of the current ring buffer. Used by HTTP replay endpoint."""
    with _thread_lock:
        return list(_buffer)


def subscriber_count() -> int:
    """Lightweight gauge for /health diagnostics."""
    with _thread_lock:
        return len(_subscribers)


def buffer_depth() -> int:
    with _thread_lock:
        return len(_buffer)


# ---- Instrumentation helpers used by the orchestrator + peer agents ---------


class tool_span:
    """Context manager: emit tool_start / tool_end around a tool execution.

    Usage:
        with tool_span("notify_park_service", agent="root_agent",
                       incident_id=iid, payload={...}) as span:
            result = call_tool(...)
            span.set_result(result)  # optional, recorded in tool_end payload

    Times the call in ms, captures exceptions as tool_end with severity=error.
    Safe to use in async code too (no blocking I/O inside __enter__/__exit__).
    """

    __slots__ = ("agent", "tool", "incident_id", "severity", "payload",
                 "_t_start", "_result", "_error")

    def __init__(
        self,
        tool: str,
        *,
        agent: str,
        incident_id: str | None = None,
        severity: str = "info",
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.agent = agent
        self.tool = tool
        self.incident_id = incident_id
        self.severity = severity
        self.payload = payload or {}
        self._t_start: int = 0
        self._result: Any = None
        self._error: BaseException | None = None

    def __enter__(self) -> "tool_span":
        self._t_start = time.monotonic_ns()
        emit(
            kind="tool_start",
            agent=self.agent,
            tool=self.tool,
            incident_id=self.incident_id,
            severity=self.severity,
            payload=self.payload,
        )
        return self

    def set_result(self, result: Any) -> None:
        self._result = result

    def __exit__(self, exc_type, exc, tb) -> bool:
        latency_ms = (time.monotonic_ns() - self._t_start) // 1_000_000
        if exc is not None:
            self._error = exc
            emit(
                kind="tool_end",
                agent=self.agent,
                tool=self.tool,
                incident_id=self.incident_id,
                severity="error",
                payload={"error": f"{type(exc).__name__}: {exc}"},
                latency_ms=latency_ms,
            )
            return False  # re-raise
        # Serialize result safely. Some tool results are large; truncate strings.
        try:
            payload = {"result": _safe_jsonable(self._result)}
        except Exception:
            payload = {"result_repr": repr(self._result)[:512]}
        emit(
            kind="tool_end",
            agent=self.agent,
            tool=self.tool,
            incident_id=self.incident_id,
            severity=self.severity,
            payload=payload,
            latency_ms=latency_ms,
        )
        return False


def _safe_jsonable(obj: Any, _depth: int = 0) -> Any:
    """Coerce to JSON-safe shape. Truncates strings + nested depth."""
    if _depth > 6:
        return "<depth-truncated>"
    if obj is None or isinstance(obj, (bool, int, float)):
        return obj
    if isinstance(obj, str):
        return obj if len(obj) <= 2000 else obj[:2000] + "...<truncated>"
    if isinstance(obj, dict):
        return {str(k): _safe_jsonable(v, _depth + 1) for k, v in list(obj.items())[:50]}
    if isinstance(obj, (list, tuple)):
        return [_safe_jsonable(x, _depth + 1) for x in list(obj)[:50]]
    try:
        return json.loads(json.dumps(obj, default=str))
    except Exception:
        return repr(obj)[:512]
