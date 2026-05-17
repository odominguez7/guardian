# Integration test for PLAN_V3.md Move 1 — Falsifier verdict propagates
# through the event firehose into the Court-Evidence chain-of-custody bundle.
#
# This covers the contract between:
#   app.tools.falsifier.review_dispatch() → events.emit(tool_end, falsifier)
#   ↓
#   app.events buffer
#   ↓
#   app.tools.court_evidence.bundle_incident() → adversarial_review block
#   ↓
#   render_evidence_html() → "Adversarial Review (Falsifier)" section

import re

from app import events as _events
from app.tools.court_evidence import bundle_incident, render_evidence_html
from app.tools.falsifier import review_dispatch


def _seed_minimal_incident(incident_id: str) -> None:
    """Seed enough events so suspicious_gap heuristic does not flag."""
    for i in range(12):
        _events.emit(
            kind="tool_end",
            agent="stream_watcher",
            tool="analyze_video_clip",
            incident_id=incident_id,
            severity="info",
            payload={"frame": i},
        )


def test_falsifier_concur_lands_in_court_evidence_bundle():
    iid = "GU-INTEG-CONCUR"
    _seed_minimal_incident(iid)
    review_dispatch(
        incident_id=iid,
        severity="critical",
        audio_confidence=0.93,
        species_compliance_flag="material",
        threat_signals=["gunshot", "vehicle_engine"],
    )

    bundle = bundle_incident(iid)
    assert bundle["status"] == "ok"
    review = bundle.get("adversarial_review")
    assert review is not None, "adversarial_review block missing"
    assert review["verdict"] == "concur"
    assert review["severity_0_5"] == 0
    assert review["audit_threshold_met"], "per-gate diagnostics missing"
    assert all(review["audit_threshold_met"].values())


def test_falsifier_dissent_lands_in_court_evidence_bundle():
    iid = "GU-INTEG-DISSENT"
    _seed_minimal_incident(iid)
    review_dispatch(
        incident_id=iid,
        severity="critical",
        audio_confidence=0.50,  # below 0.80 critical gate
        species_compliance_flag="material",
        threat_signals=["gunshot"],
    )

    bundle = bundle_incident(iid)
    review = bundle["adversarial_review"]
    assert review["verdict"] == "dissent"
    assert "audio confidence" in review["dissent_reason"]
    assert review["severity_0_5"] >= 2


def test_no_falsifier_review_shows_warning_in_html():
    iid = "GU-INTEG-NOREVIEW"
    _seed_minimal_incident(iid)
    # Intentionally do NOT call review_dispatch — should produce the
    # "no adversarial review found" warning in the HTML.
    out = render_evidence_html(iid)
    assert out["status"] == "ok"
    assert "No adversarial review found" in out["html"], (
        "HTML packet must warn when Falsifier was not invoked — Big-4 audit "
        "requirement per PLAN_V3.md Move 1."
    )


def test_adversarial_review_section_renders_in_html():
    iid = "GU-INTEG-HTML"
    _seed_minimal_incident(iid)
    review_dispatch(
        incident_id=iid,
        severity="critical",
        audio_confidence=0.65,  # dissent territory
        threat_signals=["gunshot"],
    )

    out = render_evidence_html(iid)
    html = out["html"]
    # Header is present.
    assert "Adversarial Review (Falsifier)" in html
    # Verdict pill renders with the right CSS class.
    assert re.search(r'class="verdict dissent">DISSENT', html), "DISSENT verdict pill missing or wrong CSS class"
    # Per-gate diagnostics render.
    assert "PASS" in html or "FAIL" in html
    # Dissent reason rendered.
    assert "audio confidence" in html


def test_event_emit_carries_severity_critical_on_severe_dissent():
    """The firehose severity for a dissent ≥ 3 must be 'critical' — that's
    the signal the Ops Center IncidentPanel uses to surface the AUDIT FLAG.
    """
    iid = "GU-INTEG-SEVERITY"
    # Big severity gap → dissent severity 4.
    result = review_dispatch(
        incident_id=iid,
        severity="critical",
        audio_confidence=0.30,  # 0.50 below the 0.80 critical gate → severity ~5
        threat_signals=["gunshot"],
    )
    assert result["verdict"] == "dissent"
    assert result["severity_0_5"] >= 3

    # Find the most recent falsifier event in the buffer.
    snapshot = _events.snapshot_for_incident(iid)
    falsifier_events = [e for e in snapshot if e.get("agent") == "falsifier"]
    assert len(falsifier_events) >= 1
    assert falsifier_events[-1]["severity"] == "critical"
