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

- ~~**AgentPhone MCP existence (D1).** Verify whether AgentPhone is a real MCP server.~~ ✅ **VERIFIED 2026-05-15.** Real ADK-native MCP via `McpToolset` + npx `agentphone-mcp`. `send_message` tool for SMS. No Twilio fallback needed.

## P2 — Codex challenge findings (2026-05-15 sweep)

Items below are from the codex adversarial challenge after D1 work. P0 + 6 P1s were fixed inline; these P2s defer to D17 polish.

- **A2A task store is in-memory.** `peers/*/fast_api_app.py:28-37` use `InMemoryTaskStore`. On Cloud Run scale-to-zero or multi-instance, streaming/task follow-ups can lose history/artifacts or land on a different instance. Fix: migrate to Firestore-backed task store for production. ~2 hr.

- **No A2A-layer idempotency.** Each `_call_peer` mints a fresh `message_id` via `uuid.uuid4()`. If we add retries (below), the peer sees a new id per retry and double-dispatches rangers / double-files TNFD. Fix: derive idempotency key from `incident_id + peer_name + operation`. ~1 hr.

- **No retry / backoff on transient peer failures.** Cold-start of a peer Cloud Run service can take 5-10s; the first A2A call after idle may timeout. Add exponential backoff (3 attempts) + circuit breaker. ~1 hr. _Tied to idempotency above._

- **SSRF surface via env var.** Orchestrator blindly calls whatever URL is in `PARK_SERVICE_URL` / `SPONSOR_SUSTAINABILITY_URL`. A compromised env var becomes SSRF into metadata/internal services. Fix: host allowlist (e.g. `*.run.app`, project number prefix). ~30 min.

- **Severity can diverge between peer calls.** Park dispatch logic and sponsor materiality both hinge on severity, but nothing enforces same-value reuse across the fan-out. Fix: pass severity in `new_incident_id`'s seed, or expose a separate `start_incident` tool that returns the bundle of {incident_id, severity}. ~45 min.

- **No canonical sponsored-species list.** Routing rule says "sponsor call if a sponsored species is involved" — LLM-driven, subjective. Fix: ship a static species → sponsor mapping in code, deterministic check. ~30 min.

- **Tool surface is unguarded.** Any user prompt can trigger `notify_*` calls with arbitrary payloads; no policy gate or rate limiting. Fix: add a thin pre-tool guard that requires the incident to come from Stream Watcher's escalation flag, not free-form user input. ~1 hr.

- **`requires_escalation=True` triggers on low confidence.** A noisy model spams real-world ops. Fix: add `overall_confidence >= 0.6` AND threat-signals-non-empty as a compound gate in the orchestrator instruction. ~15 min.

- **`--no-cpu-throttling` cost.** Both peers deployed with `--no-cpu-throttling` + 2Gi RAM. Idle instances still bill CPU. Fix for prod: drop to default throttled mode + 1Gi RAM (cold start +1-2s acceptable). ~10 min, but trades latency for cost.

- **Sponsor uses Pro for every filing.** `gemini-2.5-pro` on every notify_sponsor_sustainability call; no throttling/dedup. Cost spikes on noisy streams. Fix: switch to Flash with structured-output mode for the deterministic TNFD entry. Verified Flash can't do 6-arg tool calls reliably so this is non-trivial. ~2 hr.

- **Search engine LLM add-on charges per query.** `SEARCH_ADD_ON_LLM` + query expansion + spell correction = LLM billing per query. Fix: drop the LLM add-on for normal queries, enable only for natural-language search. ~15 min.

- **BigQuery analytics auto-init.** `app/agent.py` initializes BigQuery dataset whenever `GOOGLE_CLOUD_PROJECT` is set. Production opt-in should be explicit. Fix: gate behind `GUARDIAN_ENABLE_BQ_ANALYTICS=true`. ~10 min.

- **No dedup across frames.** Identical incidents from successive camera frames fan out repeatedly with new ids when seed is omitted. Fix: enforce seed via tool description + dedup window in `mint_incident_id`. ~30 min.

- **Bucket creation race in `ingest_corpus.py`.** Only handles `AlreadyExists`; a globally existing bucket in another project/region raises `Conflict/Forbidden` and hard-fails. Fix: catch `Conflict` + fall back to existing bucket if owned by this project. ~15 min.

- **Manifest path collision on concurrent ingests.** `corpus/_manifest.jsonl` is overwritten on each ingest run. Concurrent imports can read partial/mismatched manifests. Fix: timestamp-suffixed manifest paths. ~10 min.

- **`ReconciliationMode.INCREMENTAL` never removes stale docs.** Deletions/renames persist forever. Fix: switch to `FULL` mode on a scheduled reindex cadence, or add an explicit delete step. ~30 min.

- **`SEARCH_ADD_ON_LLM` no fallback on quota miss.** If the project lacks the allowlist, `create_engine` fails with no fallback. Fix: try with add-on, fall back without on quota error. ~30 min.

## P2 — Codex final-sweep findings (2026-05-15 evening, post-Ops-Center)

- **Mobile / small-window layout unusable.** Fixed 3-column grid + `overflow-hidden` on body means panels are clipped on narrow viewports with no scroll. Desktop-first hackathon demo so deferred. Fix: switch to CSS grid with min-content rows + flex-wrap below ~1024px breakpoint. ~1 hr.
  Refs: `ops-center/src/app/page.tsx:199`, `ops-center/src/app/layout.tsx:31`

- **Firebase ID token-in-URL leakage path (dead code).** `firehose.ts` ships code to put a Firebase ID token in the WebSocket URL query string, which gets logged by proxies/Cloud Run. The server never validates it. Dead-code-but-latent. Fix when wiring real Firebase auth: use a server-side WebSocket proxy with header-based auth instead. ~2 hr.
  Refs: `ops-center/src/lib/firehose.ts:154`, `app/fast_api_app.py:152`

- **Mapbox token in build logs + shell history.** Token is passed via Cloud Build `--substitutions _MAPBOX_TOKEN=$MAPBOX_TOKEN` which logs to Cloud Build logs (visible to anyone with `roles/cloudbuild.builds.viewer`) and the make invocation lives in shell history. Mitigation already documented in `MAPBOX_USAGE_MONITORING.md` — when Omar's back, he creates a URL-restricted custom token; the leaked default token then becomes unusable from the wrong origin. ~15 min for the dashboard work.

## Process

- After D17 polish pass, this file should be empty or only contain items that genuinely don't matter for the submission. Anything left here on D22 morning is officially "won't fix for the hackathon."
