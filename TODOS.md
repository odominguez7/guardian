# GUARDIAN — TODOS

Deferred items from `/review`, `/codex review`, and `/plan-eng-review` (2026-05-15).
All P2/P3 informational; none blocks the demo. Scheduled for the D17 security/polish pass.

## P2 — Robustness

- **Retry / circuit breaker on transient peer failures.** `app/tools/a2a_peers.py`. Cold-starting peer Cloud Run services can take 5-10s; the first A2A call after idle may timeout. Add exponential backoff (3 attempts) and a circuit-breaker that opens on 5 consecutive failures. _Why deferred: demo path warms up before recording, so cold-start lag is invisible there._

- **A2A request idempotency.** `app/tools/a2a_peers.py`. Every `_call_peer` mints a fresh `message_id` via `uuid.uuid4()`. If we add retries (above), the peer sees a new id per retry and processes duplicates (park dispatches twice). Add an idempotency key derived from `incident_id + peer_name`. _Why deferred: tied to retry policy._

- **Tighten `_try_parse_json_blob` unwrap.** `app/tools/a2a_peers.py`. Currently unwraps any single-key dict ending in `_response`. If a future peer's tool legitimately returns `{"webhook_response": {...}}` as its real shape, we'd unwrap the wrong layer. Make the unwrap match a known tool-name allowlist. _Why deferred: current peers return multi-key dicts, so no risk today._

- **Agent card description leakage.** ADK's `AgentCardBuilder` auto-derives skill descriptions from the agent's instruction string. The peers' first-person instructions ("I am NOT part of GUARDIAN") leak into public agent card metadata. Looks unprofessional in a Track 3 audit. Override the builder to pass a sanitized skill description. _Why deferred: cosmetic, ~20 min fix._

- **Public agent card vs IAM-gated tradeoff.** Cloud Run is `--no-allow-unauthenticated`, so the agent card needs a bearer token. Track 3 spec implies peers should be discoverable by other agents. Either open the agent card path via Cloud Endpoints / API Gateway, or accept that judges must use IAM auth to discover. _Why deferred: security-vs-discoverability call needs explicit decision._

- **No saga / compensating action on partial peer failure.** If park_service succeeds and sponsor_sustainability fails, we have an inconsistent audit trail. Production multi-tenant compliance would need a compensating action. _Why deferred: out of scope for hackathon demo._

- **Multi-agent demo latency (60-90s full chain).** Locked **Option 2 (parallelize via ADK `ParallelAgent`)** in eng review. Scheduled for D16. Cuts real-time chain ~90s → 30-40s. _Status: scheduled, not deferred._

## P3 — Polish

- **`httpx.AsyncClient(timeout=30)` is a single number.** Better: `httpx.Timeout(connect=5, read=30)` so connect failures fail fast (5s) but operations get the full 30s. ~10 min change. _Why deferred: works today._

- **A2AClient deprecation warning.** The `a2a.client.A2AClient` class is deprecated; the new path is `ClientFactory` with a JSON-RPC transport. Tests emit DeprecationWarning. ~30 min migration. _Why deferred: warning only, behavior unchanged._

- **Refactor peers into a registry-driven factory.** `app/tools/a2a_peers.py`. After Funder + Neighbor peers ship, we'll have 8 per-peer wrapper functions. Codegen via `make_peer_tools(name, request_fields)`. ~1 hr. _Why deferred: not blocking; can ship Funder + Neighbor with the current pattern._

- **`dispatch_rangers` returns random ranger units.** Same incident replayed → different unit. Fine for demo, fails any "same input → same output" reproducibility test. ~15 min fix (seed by `incident_id`). _Why deferred: replay determinism isn't a hackathon scoring axis._

- **Structured logging with `incident_id` context.** `logger.warning(...)` calls don't attach `incident_id`. In Cloud Run logs we can't grep "show me all events for incident GU-...-001". ~30 min to add `logging.LoggerAdapter` per request. _Why deferred: dev convenience, not blocking._

- **Declarative A2A tool schemas.** Instruction-as-natural-language is brittle — the peer LLM extracts fields from prose. Future Gemini behavior changes could break extraction. Declare tool schemas in the agent card + invoke via direct A2A method calls. _Why deferred: working today, large refactor._

## P1 — Pending verification (eng review)

- **AgentPhone MCP existence (D1).** Verify whether AgentPhone is a real MCP server. If yes, use it for Dispatch agent (D8) — Track 3 MCP signaling bonus. If no, fall back to Twilio direct API. ~30 min verification. _Status: assigned for D1 today._

## Process

- After D17 polish pass, this file should be empty or only contain items that genuinely don't matter for the submission. Anything left here on D22 morning is officially "won't fix for the hackathon."
