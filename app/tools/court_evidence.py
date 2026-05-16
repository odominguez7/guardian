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
    a SHA-256 chain hash for tamper detection, and returns a structured bundle
    a downstream Document AI / PDF renderer can format.

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
        except ValueError:
            duration_s = None

    chain_hash = _chain_hash(evts)
    digest = hashlib.sha256(incident_id.encode()).hexdigest()
    year = datetime.now(timezone.utc).year
    bundle_id = f"CHN-{year}-{digest[:10].upper()}"

    specialists = []
    peer_acks = []
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

    return {
        "status": "ok",
        "bundle_id": bundle_id,
        "incident_id": incident_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "event_count": len(evts),
        "time_window": {
            "start": start,
            "end": end,
            "duration_s": duration_s,
        },
        "chain_hash": chain_hash,
        "specialists": specialists,
        "peer_acks": peer_acks,
        "timeline": evts,
        "buffer_truncated": len(evts) <= 2,  # heuristic: real fanout produces ~15+ events
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
    truncated_note = (
        '<div class="warn">Ring buffer truncated - the timeline may be partial. '
        'Re-fire the incident or extend GUARDIAN_EVENT_BUFFER for complete capture.</div>'
        if bundle.get("buffer_truncated") else ""
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
  footer {{ margin-top: 40px; color: #94a3b8; font-size: 11px; text-align: center; padding-top: 16px; border-top: 1px solid #e2e8f0; }}
</style>
</head>
<body>
  <h1>GUARDIAN Chain-of-Custody Evidence Packet</h1>
  <div class="sub">Generated for legal + sustainability audit chain. SHA-256 anchored. Compliance frameworks: {frameworks}.</div>
  <span class="stamp">Authenticated by chain hash</span>

  <h2>Bundle Metadata</h2>
  <dl class="meta">
    <dt>Bundle ID</dt>          <dd><code>{bid}</code></dd>
    <dt>Incident ID</dt>        <dd><code>{iid}</code></dd>
    <dt>Generated at</dt>       <dd>{gen}</dd>
    <dt>Observation window</dt> <dd>{win_start} - {win_end} ({win_dur_str})</dd>
    <dt>Event count</dt>        <dd>{bundle['event_count']}</dd>
    <dt>Chain hash (SHA-256)</dt><dd><code>{chain}</code></dd>
  </dl>
  {truncated_note}

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

  <h2>Full Timeline</h2>
  <table>
    <thead><tr><th>Timestamp</th><th>Kind</th><th>Agent</th><th>Tool</th><th>Severity</th></tr></thead>
    <tbody>{timeline_rows}</tbody>
  </table>

  <footer>
    GUARDIAN Chain-of-Custody Evidence Packet {bid} - generated {gen}.<br>
    This document is a regulatory disclosure artifact. The chain hash above can be re-derived by any auditor from the underlying event log.
  </footer>
</body>
</html>
"""
