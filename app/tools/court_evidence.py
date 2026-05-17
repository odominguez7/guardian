# Copyright 2026 GUARDIAN
# Court-Evidence tools - bundle an incident's firehose events into a
# chain-of-custody evidence packet suitable for the host country's wildlife
# court system + the sponsor's TNFD audit trail.
#
# Two tools:
#   bundle_incident(incident_id)            - structured JSON evidence bundle
#                                              (chain-of-custody + agent acks)
#   render_evidence_html(incident_id)       - judge-clickable HTML packet
#                                              with the same content rendered

import hashlib
import html
import json
import logging
from datetime import datetime, timezone

from app import events as _events

logger = logging.getLogger(__name__)


def bundle_incident(incident_id: str) -> dict:
    """Bundle every firehose event for an incident into a chain-of-custody dict.

    Use this tool AFTER an incident's peer fan-out has completed, when the
    Orchestrator needs to assemble a legal-evidence packet. Walks the event
    ring buffer for everything tagged with the incident_id, partitions by
    event kind (specialist tool calls, A2A requests, A2A responses), computes
    a SHA-256 internal-consistency hash, and returns a structured bundle a
    downstream Document AI / PDF renderer can format.

    Integrity scope (be precise about what the hash guarantees):
    The chain_hash proves the events RETURNED in this bundle are internally
    consistent at the moment of generation. It does NOT prove the events
    were never dropped before reaching the buffer (the buffer is in-memory
    and bounded by GUARDIAN_EVENT_BUFFER). For a fully durable evidence
    chain, pair this bundle with a persistent log sink (BigQuery / Cloud
    Logging - both are wired). The `buffer_depth` and `buffer_size` fields
    in the response let an auditor sanity-check completeness.

    Args:
        incident_id: GUARDIAN's incident reference (e.g., GU-466F7A6FA1F3).

    Returns:
        Dict with:
            status, incident_id, bundle_id (CHN-<year>-<10hex>), generated_at,
            event_count, time_window {start, end, duration_s},
            chain_hash (SHA-256 of ordered event ids),
            specialists (list of specialist tool_end summaries),
            peer_acks (list of A2A response summaries from each peer),
            timeline (full event list, chronological),
            buffer_truncated (bool - true if ring buffer may have evicted earlier events).
    """
    if not incident_id:
        return {"status": "error", "error": "incident_id is required"}

    evts = _events.snapshot_for_incident(incident_id)
    if not evts:
        return {
            "status": "error",
            "error": (
                f"No events buffered for incident_id={incident_id}. The ring "
                "buffer is bounded; very old incidents may have been evicted."
            ),
            "incident_id": incident_id,
        }

    timestamps = [e.get("ts") for e in evts if e.get("ts")]
    start = min(timestamps) if timestamps else None
    end = max(timestamps) if timestamps else None

    duration_s = None
    if start and end:
        try:
            s = datetime.fromisoformat(start.replace("Z", "+00:00"))
            e = datetime.fromisoformat(end.replace("Z", "+00:00"))
            duration_s = (e - s).total_seconds()
        except ValueError as parse_err:
            # Codex flagged this as silent data loss. Log so an operator
            # can find which incident's timestamps were corrupted.
            logger.warning(
                "court_evidence: ISO timestamp parse failed for "
                "incident=%s start=%r end=%r err=%s",
                incident_id, start, end, parse_err,
            )
            duration_s = None

    chain_hash = _chain_hash(evts)
    digest = hashlib.sha256(incident_id.encode()).hexdigest()
    year = datetime.now(timezone.utc).year
    bundle_id = f"CHN-{year}-{digest[:10].upper()}"

    specialists = []
    peer_acks = []
    # All falsifier reviews for this incident, chronological. The "current"
    # top-level adversarial_review is the LAST one (latest decision wins),
    # but every review is preserved in `adversarial_reviews` so an auditor
    # can see the full dissent history — Big-4 chain-of-custody requirement
    # if the orchestrator re-reviewed mid-incident. Codex Move 1 P2 fix.
    adversarial_reviews: list[dict] = []
    for e in evts:
        kind = e.get("kind")
        if kind == "tool_end" and e.get("agent") == "falsifier":
            payload = e.get("payload") or {}
            adversarial_reviews.append({
                "verdict": payload.get("verdict"),
                "dissent_reason": payload.get("dissent_reason", ""),
                "severity_0_5": payload.get("severity_0_5"),
                "audit_threshold_met": payload.get("audit_threshold_met", {}),
                "reviewed_at": payload.get("reviewed_at"),
                "reviewer": "falsifier (GUARDIAN internal audit principal)",
            })
    adversarial_review = adversarial_reviews[-1] if adversarial_reviews else None
    for e in evts:
        kind = e.get("kind")
        if kind == "tool_end" and e.get("agent") in {
            "stream_watcher", "audio_agent", "species_id"
        }:
            specialists.append({
                "agent": e["agent"],
                "tool": e.get("tool"),
                "severity": e.get("severity"),
                "ts": e.get("ts"),
                "latency_ms": e.get("latency_ms"),
                "result_summary": _summarize_payload(e.get("payload")),
            })
        elif kind == "a2a_response":
            payload = e.get("payload") or {}
            peer_acks.append({
                "peer": e.get("agent"),
                "status": payload.get("status"),
                "ts": e.get("ts"),
                "latency_ms": e.get("latency_ms"),
                "identifier": _peer_identifier(e.get("agent"), payload),
            })

    # v4 sub-move A5 (post-audit revisions per CODEX_MOVE_7_V4.md):
    # Management Review Required exception workflow.
    #
    # Triggers when EITHER:
    #   (a) any Falsifier review in the incident's history dissented, OR
    #   (b) any Falsifier review abstained,
    # AND the incident's MAX severity (across its lifecycle, not just the
    # latest event) reached "high" or "critical".
    #
    # Rationale:
    # - Abstain on critical was silently missed by the v4 ship — Big-4 audit
    #   charters treat "auditor declined to opine" as MORE serious than
    #   "auditor disagreed."
    # - Walking events and keeping the latest severity dropped management
    #   review when an incident downgraded mid-flight (e.g. critical → medium
    #   on better evidence). We now use the timeline's peak.
    # - A retracted dissent (dissent → concur on re-review) is still
    #   audit-material; any-in-history is the right surface, not latest-only.
    SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    severities_seen = [
        e.get("severity") for e in evts
        if e.get("severity") in SEVERITY_RANK
    ]
    max_severity = (
        max(severities_seen, key=lambda s: SEVERITY_RANK[s])
        if severities_seen else None
    )
    any_dissent = any(r.get("verdict") == "dissent" for r in adversarial_reviews)
    any_abstain = any(r.get("verdict") == "abstain" for r in adversarial_reviews)
    triggering_verdict = "dissent" if any_dissent else ("abstain" if any_abstain else None)

    management_review_required = False
    management_review = None
    if triggering_verdict and max_severity in {"high", "critical"}:
        management_review_required = True
        management_review = {
            "status": "pending_assignment",
            "required_role": "Sustainability Controller (or above)",
            "trigger": (
                f"Falsifier {triggering_verdict} in incident review history "
                f"with peak severity {max_severity}. Internal-audit charter "
                "requires named-reviewer sign-off before TNFD filing reaches "
                "external auditor evidence pack."
            ),
            "triggering_verdict": triggering_verdict,
            "peak_severity": max_severity,
            "sla_hours": 4 if max_severity == "critical" else 24,
            "queue": "sponsor.sustainability_controller.exceptions",
            "audit_artifacts_attached": [
                "adversarial_reviews (full history, not just latest)",
                "chain_hash",
                "specialists timeline",
                "peer_acks (park / sponsor / funder / neighbor)",
            ],
        }
    elif triggering_verdict and not max_severity:
        # Surface the policy gap rather than hide it: an incident with a
        # Falsifier dissent/abstain but no severity-tagged events is anomalous
        # and worth a warning so an operator can audit the upstream emit path.
        logger.warning(
            "court_evidence: Falsifier %s with no severity events for "
            "incident=%s — management-review gate skipped, may indicate "
            "upstream specialist emit gap.",
            triggering_verdict, incident_id,
        )

    # Buffer-state context lets an auditor reason about completeness rather
    # than rely on a single heuristic flag. Codex flagged the prior heuristic
    # (len<=2) as missing partial-truncation cases.
    buffer_depth = _events.buffer_depth()
    buffer_size = _events.buffer_size()
    # "Suspicious gap" signal: real 4-peer fan-out produces ~15+ events
    # (1 incident_event + 4 a2a_request + 4 a2a_response + N tool spans).
    # Sub-10 event count OR buffer-full-during-capture (which suggests the
    # ring may have evicted earlier events) flags as suspicious.
    suspicious_gap = len(evts) < 10 or buffer_depth >= buffer_size - 1

    return {
        "status": "ok",
        "bundle_id": bundle_id,
        "incident_id": incident_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "event_count": len(evts),
        "buffer_depth": buffer_depth,
        "buffer_size": buffer_size,
        "time_window": {
            "start": start,
            "end": end,
            "duration_s": duration_s,
        },
        "chain_hash": chain_hash,
        "chain_hash_scope": (
            "Internal consistency of the buffered events returned in this "
            "bundle. Does NOT prove completeness vs. emitted events; pair "
            "with a persistent log sink for full chain of custody."
        ),
        "specialists": specialists,
        "peer_acks": peer_acks,
        "adversarial_review": adversarial_review,
        "adversarial_reviews": adversarial_reviews,
        "management_review_required": management_review_required,
        "management_review": management_review,
        "timeline": evts,
        "suspicious_gap": suspicious_gap,
        "compliance_frameworks": ["TNFD", "CSRD-ESRS-E4", "CITES-MIKE"],
    }


def _chain_hash(evts: list[dict]) -> str:
    """SHA-256 of the chronologically ordered event_ids + their timestamps.

    Any reordering, insertion, or deletion of events in the timeline changes
    the hash. Stored in the bundle so a downstream auditor can re-derive it
    against the source events and verify the chain hasn't been tampered with.
    """
    h = hashlib.sha256()
    for e in evts:
        h.update(str(e.get("id", "")).encode())
        h.update(str(e.get("ts", "")).encode())
    return h.hexdigest()


def _summarize_payload(payload) -> str:
    """1-line summary of a tool_end payload for the specialists list."""
    if not isinstance(payload, dict):
        return ""
    if "primary_species" in payload:
        ps = payload.get("primary_species")
        if isinstance(ps, dict):
            return f"{ps.get('common_name','?')} ({ps.get('count','?')} animals, conf {ps.get('confidence','?')})"
        if isinstance(ps, str):
            return ps
    if "sound_class" in payload:
        return f"{payload.get('sound_class','?')} (conf {payload.get('confidence','?')})"
    if "threat_signals" in payload:
        signals = payload.get("threat_signals") or []
        return f"threat_signals={','.join(signals[:3]) or 'none'}"
    if "top_match" in payload:
        tm = payload.get("top_match") or {}
        return f"factsheet: {tm.get('common_name','?')} {tm.get('iucn_status','?')}"
    return ""


def _peer_identifier(peer: str | None, payload: dict) -> str:
    """Pull the relevant operational identifier from each peer's ack."""
    if not isinstance(payload, dict):
        return ""
    if peer == "park_service":
        return payload.get("ranger_unit", "")
    if peer == "sponsor_sustainability":
        return payload.get("filing_id", "")
    if peer == "funder_reporter":
        return payload.get("receipt_id", "")
    if peer == "neighbor_park":
        return payload.get("handoff_id", "")
    return ""


def render_evidence_html(incident_id: str) -> dict:
    """Render an incident's chain-of-custody bundle as a clickable HTML packet.

    Use this tool when a human (auditor, court officer, sponsor CSO) needs to
    READ the evidence rather than parse JSON. The HTML packet is self-contained
    (inline CSS), prints cleanly, and renders the timeline + chain hash + peer
    acks + compliance framework references.

    Args:
        incident_id: GUARDIAN's incident reference.

    Returns:
        Dict with status, incident_id, bundle_id, html (full self-contained
        document), and meta fields mirroring bundle_incident.
    """
    bundle = bundle_incident(incident_id)
    if bundle.get("status") != "ok":
        return bundle

    html_doc = _format_html(bundle)
    return {
        "status": "ok",
        "incident_id": incident_id,
        "bundle_id": bundle["bundle_id"],
        "chain_hash": bundle["chain_hash"],
        "html": html_doc,
        "event_count": bundle["event_count"],
        "compliance_frameworks": bundle["compliance_frameworks"],
    }


def _format_html(bundle: dict) -> str:
    """Render the chain-of-custody bundle as a self-contained HTML document."""
    iid = html.escape(bundle["incident_id"])
    bid = html.escape(bundle["bundle_id"])
    chain = html.escape(bundle["chain_hash"])
    gen = html.escape(bundle["generated_at"])
    win = bundle.get("time_window", {})
    win_start = html.escape(win.get("start") or "?")
    win_end = html.escape(win.get("end") or "?")
    win_dur = win.get("duration_s")
    win_dur_str = f"{win_dur:.2f}s" if isinstance(win_dur, (int, float)) else "?"

    spec_rows = "".join(
        f"<tr><td>{html.escape(s['agent'])}</td>"
        f"<td>{html.escape(s.get('tool') or '')}</td>"
        f"<td>{html.escape(s.get('severity') or '')}</td>"
        f"<td>{html.escape(str(s.get('latency_ms') or ''))}</td>"
        f"<td>{html.escape(s.get('result_summary') or '')}</td></tr>"
        for s in bundle.get("specialists", [])
    ) or '<tr><td colspan="5" class="empty">No specialist events buffered.</td></tr>'

    peer_rows = "".join(
        f"<tr><td>{html.escape(p['peer'] or '')}</td>"
        f"<td>{html.escape(p.get('status') or '')}</td>"
        f"<td><code>{html.escape(p.get('identifier') or '')}</code></td>"
        f"<td>{html.escape(str(p.get('latency_ms') or ''))}</td>"
        f"<td>{html.escape(p.get('ts') or '')}</td></tr>"
        for p in bundle.get("peer_acks", [])
    ) or '<tr><td colspan="5" class="empty">No peer acks buffered.</td></tr>'

    timeline_rows = "".join(
        f"<tr><td>{html.escape(e.get('ts') or '')}</td>"
        f"<td>{html.escape(e.get('kind') or '')}</td>"
        f"<td>{html.escape(e.get('agent') or '')}</td>"
        f"<td>{html.escape(e.get('tool') or '')}</td>"
        f"<td>{html.escape(e.get('severity') or '')}</td></tr>"
        for e in bundle.get("timeline", [])
    )

    frameworks = ", ".join(html.escape(f) for f in bundle.get("compliance_frameworks", []))

    # Adversarial review block — the Falsifier's verdict on this dispatch.
    # Required by Big-4 audit standards and TNFD chain-of-custody review.
    rev = bundle.get("adversarial_review")
    if rev:
        verdict = html.escape(rev.get("verdict") or "?")
        verdict_class = {
            "concur": "concur",
            "dissent": "dissent",
            "abstain": "abstain",
        }.get(rev.get("verdict") or "", "abstain")
        reason = html.escape(rev.get("dissent_reason") or "")
        sev = rev.get("severity_0_5") or 0
        reviewed_at = html.escape(rev.get("reviewed_at") or "")
        gates = rev.get("audit_threshold_met") or {}
        gate_rows = "".join(
            f"<tr><td>{html.escape(k)}</td>"
            f'<td><span class="gate-{("pass" if v else "fail")}">'
            f'{"PASS" if v else "FAIL"}</span></td></tr>'
            for k, v in gates.items()
        ) or '<tr><td colspan="2" class="empty">No SOP gates evaluated.</td></tr>'
        adversarial_block = f"""
  <h2>Adversarial Review (Falsifier)</h2>
  <div class="sub">An independent internal-audit principal evaluated the proposed dispatch against the GUARDIAN SOP gates. Verdict and per-gate diagnostics are part of the chain-of-custody record per Big-4 audit standards and TNFD chain-of-custody review.</div>
  <dl class="meta">
    <dt>Verdict</dt>          <dd><span class="verdict {verdict_class}">{verdict.upper()}</span></dd>
    <dt>Severity (0-5)</dt>   <dd>{sev}</dd>
    <dt>Reviewed at</dt>      <dd>{reviewed_at}</dd>
    <dt>Reviewer</dt>         <dd>{html.escape(rev.get("reviewer") or "")}</dd>
    {("<dt>Dissent reason</dt><dd>" + reason + "</dd>") if reason else ""}
  </dl>
  <table>
    <thead><tr><th>SOP gate</th><th>Result</th></tr></thead>
    <tbody>{gate_rows}</tbody>
  </table>
"""
    else:
        adversarial_block = """
  <h2>Adversarial Review (Falsifier)</h2>
  <div class="warn">No adversarial review found in the event buffer. The Falsifier agent may not have been invoked for this dispatch. Chain-of-custody packets without an internal-audit verdict do not meet Big-4 review standards.</div>
"""

    suspicious_note = (
        f'<div class="warn">Buffer state suggests this bundle may be incomplete '
        f'(event_count={bundle["event_count"]}, buffer_depth={bundle.get("buffer_depth")} / '
        f'buffer_size={bundle.get("buffer_size")}). Re-fire the incident or '
        f'extend GUARDIAN_EVENT_BUFFER for full capture.</div>'
        if bundle.get("suspicious_gap") else ""
    )
    # Embed the timeline JSON in the HTML so an auditor can re-derive the
    # chain hash from the document alone. Codex flagged the prior version
    # for claiming re-derivation without shipping the source events.
    timeline_json = html.escape(
        json.dumps(bundle.get("timeline", []), default=str, indent=2),
        quote=False,
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>GUARDIAN Evidence Packet {bid}</title>
<style>
  body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; color: #0f172a; max-width: 980px; margin: 24px auto; padding: 0 24px 64px; line-height: 1.45; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  h2 {{ font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px; color: #475569; margin-top: 28px; padding-top: 16px; border-top: 1px solid #e2e8f0; }}
  .sub {{ color: #64748b; font-size: 13px; }}
  .meta {{ display: grid; grid-template-columns: 180px 1fr; gap: 6px 16px; font-size: 13px; margin-top: 12px; }}
  .meta dt {{ color: #64748b; }}
  .meta dd {{ margin: 0; }}
  code {{ font-family: 'SF Mono', Menlo, monospace; font-size: 12px; background: #f1f5f9; padding: 1px 5px; border-radius: 3px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }}
  th {{ text-align: left; font-weight: 500; color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; padding: 6px 8px; border-bottom: 1px solid #e2e8f0; }}
  td {{ padding: 6px 8px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
  td.empty {{ color: #94a3b8; font-style: italic; text-align: center; }}
  .stamp {{ display: inline-block; padding: 4px 10px; border-radius: 4px; background: #ecfdf5; color: #047857; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; margin-top: 4px; }}
  .warn {{ background: #fef3c7; color: #92400e; padding: 8px 12px; border-radius: 4px; font-size: 12px; margin-top: 10px; }}
  .verdict {{ display: inline-block; padding: 3px 8px; border-radius: 3px; font-weight: 600; font-size: 11px; letter-spacing: 0.5px; }}
  .verdict.concur {{ background: #ecfdf5; color: #047857; }}
  .verdict.dissent {{ background: #fee2e2; color: #b91c1c; }}
  .verdict.abstain {{ background: #f1f5f9; color: #475569; }}
  .gate-pass {{ color: #047857; font-weight: 600; font-size: 11px; }}
  .gate-fail {{ color: #b91c1c; font-weight: 600; font-size: 11px; }}
  footer {{ margin-top: 40px; color: #94a3b8; font-size: 11px; text-align: center; padding-top: 16px; border-top: 1px solid #e2e8f0; }}
</style>
</head>
<body>
  <h1>GUARDIAN Chain-of-Custody Evidence Packet</h1>
  <div class="sub">Generated for legal + sustainability audit chain. SHA-256 internal-consistency anchored. Compliance frameworks: {frameworks}.</div>
  <span class="stamp">Internal consistency hash present</span>

  <h2>Bundle Metadata</h2>
  <dl class="meta">
    <dt>Bundle ID</dt>          <dd><code>{bid}</code></dd>
    <dt>Incident ID</dt>        <dd><code>{iid}</code></dd>
    <dt>Generated at</dt>       <dd>{gen}</dd>
    <dt>Observation window</dt> <dd>{win_start} - {win_end} ({win_dur_str})</dd>
    <dt>Event count</dt>        <dd>{bundle['event_count']} (buffer depth {bundle.get('buffer_depth')} / size {bundle.get('buffer_size')})</dd>
    <dt>Chain hash (SHA-256)</dt><dd><code>{chain}</code></dd>
    <dt>Hash scope</dt>          <dd>Internal consistency of buffered events returned in this packet. Pair with persistent log sink for full chain of custody.</dd>
  </dl>
  {suspicious_note}

  <h2>Specialist Agents (multi-modal analysis)</h2>
  <table>
    <thead><tr><th>Agent</th><th>Tool</th><th>Severity</th><th>Latency (ms)</th><th>Result</th></tr></thead>
    <tbody>{spec_rows}</tbody>
  </table>

  <h2>A2A Peer Acknowledgements (cross-organization coordination)</h2>
  <table>
    <thead><tr><th>Peer</th><th>Status</th><th>Identifier</th><th>Latency (ms)</th><th>Timestamp</th></tr></thead>
    <tbody>{peer_rows}</tbody>
  </table>
{adversarial_block}

  <h2>Full Timeline</h2>
  <table>
    <thead><tr><th>Timestamp</th><th>Kind</th><th>Agent</th><th>Tool</th><th>Severity</th></tr></thead>
    <tbody>{timeline_rows}</tbody>
  </table>

  <h2>Source event log (chain-hash inputs)</h2>
  <div class="sub">Embedded so an auditor can re-derive the chain hash from this document alone. Hash is SHA-256 of each event's <code>id</code> + <code>ts</code>, concatenated in chronological order.</div>
  <script id="guardian-event-log" type="application/json">{timeline_json}</script>
  <pre style="background:#0f172a;color:#e2e8f0;padding:12px;border-radius:6px;font-size:11px;max-height:400px;overflow:auto;font-family:'SF Mono',Menlo,monospace;">{timeline_json}</pre>

  <footer>
    GUARDIAN Chain-of-Custody Evidence Packet {bid} - generated {gen}.<br>
    This document is a regulatory disclosure artifact. The chain hash above can be re-derived from the embedded event log via the SHA-256 algorithm described in the "Hash scope" field.
  </footer>
</body>
</html>
"""
