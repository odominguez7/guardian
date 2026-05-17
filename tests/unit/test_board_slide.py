# Unit + integration tests for app.tools.board_slide.render_board_slide.
# PLAN_V3.md Move 3 — Board-ready slide auto-export.

import hashlib

from app import events as _events
from app.tools.board_slide import render_board_slide


def _seed_filing(incident_id: str, filing_id: str) -> None:
    """Seed enough events that render_board_slide can derive KPIs."""
    _events.emit(
        kind="tool_end",
        agent="stream_watcher",
        tool="analyze_video_clip",
        incident_id=incident_id,
        severity="high",
        payload={
            "primary_species": "African elephant",
            "total_animal_count": 11,
        },
    )
    _events.emit(
        kind="tool_end",
        agent="species_id",
        tool="lookup_species_factsheet",
        incident_id=incident_id,
        severity="high",
        payload={
            "primary_species": {"common_name": "African elephant", "count": 11},
            "top_match": {"common_name": "African elephant"},
            "compliance_flag": "material",
        },
    )
    _events.emit(
        kind="a2a_response",
        agent="park_service",
        tool="dispatch_rangers",
        incident_id=incident_id,
        severity="critical",
        payload={"status": "dispatched", "ranger_unit": "PSR-5349"},
    )
    _events.emit(
        kind="a2a_response",
        agent="sponsor_sustainability",
        tool="file_tnfd_entry",
        incident_id=incident_id,
        severity="critical",
        payload={"status": "filed", "filing_id": filing_id},
    )
    _events.emit(
        kind="a2a_response",
        agent="funder_reporter",
        tool="file_impact_receipt",
        incident_id=incident_id,
        severity="info",
        payload={"status": "filed", "receipt_id": "FUND-2026-A0192B2A32"},
    )
    _events.emit(
        kind="a2a_response",
        agent="neighbor_park",
        tool="accept_handoff",
        incident_id=incident_id,
        severity="info",
        payload={"status": "accepted", "handoff_id": "MUTAID-2026-A0192B2A32"},
    )


def test_render_board_slide_status_ok():
    iid = "GU-BS-OK"
    fid = "TNFD-2026-OK"
    _seed_filing(iid, fid)

    out = render_board_slide(fid)
    assert out["status"] == "ok"
    assert out["filing_id"] == fid
    assert out["incident_id"] == iid
    assert out["board_slide_url"] == f"/board-slide/{fid}"
    assert "html" in out and out["html"].startswith("<!doctype html>")


def test_render_board_slide_kpis_correct():
    iid = "GU-BS-KPI"
    fid = "TNFD-2026-KPI"
    _seed_filing(iid, fid)
    out = render_board_slide(fid)
    kpis = out["kpis"]
    assert kpis["species_protected"] == 11
    assert kpis["species_name"] == "African elephant"
    assert kpis["hectares_monitored"] == 50_000
    assert kpis["a2a_confirmed_filings"] == 4  # park, sponsor, funder, neighbor
    expected_hash = hashlib.sha256(iid.encode()).hexdigest()[:16].upper()
    assert kpis["audit_hash"] == expected_hash


def test_render_board_slide_html_includes_all_fields():
    iid = "GU-BS-HTML"
    fid = "TNFD-2026-HTML"
    _seed_filing(iid, fid)
    html = render_board_slide(fid)["html"]
    assert "African elephant" in html
    assert "Q2" in html  # reporting period
    assert "11" in html  # species count
    assert "50,000" in html  # hectares
    assert "TNFD-2026-HTML" in html  # filing_id
    assert "GU-BS-HTML" in html  # incident_id
    assert "PSR-5349" in html  # peer id
    assert "Download as PNG" in html  # client-side download button
    assert "html2canvas" in html  # client-side renderer


def test_render_board_slide_missing_filing():
    out = render_board_slide("TNFD-2026-MISSING")
    assert out["status"] == "error"
    assert "No incident found" in out["error"]


def test_render_board_slide_empty_filing_id_returns_error():
    out = render_board_slide("")
    assert out["status"] == "error"
    assert "filing_id is required" in out["error"]
