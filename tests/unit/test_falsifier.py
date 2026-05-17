# Unit tests for app.tools.falsifier.review_dispatch — the deterministic
# SOP gate engine behind the Falsifier agent.

from app.tools.falsifier import review_dispatch


def test_concur_when_evidence_strong():
    r = review_dispatch(
        incident_id="GU-466F7A6FA1F3",
        severity="critical",
        audio_confidence=0.93,
        species_compliance_flag="material",
        threat_signals=["gunshot", "vehicle_engine"],
    )
    assert r["verdict"] == "concur"
    assert r["dissent_reason"] == ""
    assert r["severity_0_5"] == 0
    assert all(r["audit_threshold_met"].values())


def test_dissent_when_audio_confidence_below_critical_gate():
    r = review_dispatch(
        incident_id="GU-1",
        severity="critical",
        audio_confidence=0.65,  # below 0.80 critical gate
        species_compliance_flag="material",
        threat_signals=["gunshot"],
    )
    assert r["verdict"] == "dissent"
    assert "audio confidence" in r["dissent_reason"]
    assert r["severity_0_5"] >= 2


def test_dissent_when_unlisted_species_high_severity():
    r = review_dispatch(
        incident_id="GU-2",
        severity="high",
        audio_confidence=0.9,
        species_compliance_flag="unlisted",
        threat_signals=["vehicle_engine"],
    )
    assert r["verdict"] == "dissent"
    assert "unlisted" in r["dissent_reason"] or "ceiling" in r["dissent_reason"]


def test_dissent_when_severity_lacks_hot_signal():
    r = review_dispatch(
        incident_id="GU-3",
        severity="critical",
        audio_confidence=0.9,
        species_compliance_flag="material",
        threat_signals=["unknown_signal"],  # no hot signal
    )
    assert r["verdict"] == "dissent"
    assert "hot threat_signal" in r["dissent_reason"]


def test_abstain_when_no_telemetry():
    r = review_dispatch(
        incident_id="GU-4",
        severity="medium",
    )
    assert r["verdict"] == "abstain"
    assert "no audit-eligible telemetry" in r["dissent_reason"]


def test_abstain_when_missing_incident_id():
    r = review_dispatch(
        incident_id="",
        severity="critical",
        audio_confidence=0.9,
    )
    assert r["verdict"] == "abstain"
    assert "incident_id" in r["dissent_reason"]


def test_abstain_when_invalid_severity():
    r = review_dispatch(
        incident_id="GU-5",
        severity="cataclysmic",
        audio_confidence=0.9,
    )
    assert r["verdict"] == "abstain"


def test_audit_threshold_records_per_gate_pass_fail():
    r = review_dispatch(
        incident_id="GU-6",
        severity="critical",
        audio_confidence=0.65,  # fails critical gate
        species_compliance_flag="material",
        threat_signals=["gunshot"],
    )
    # Audio gate explicitly fails.
    audio_gate_key = next(k for k in r["audit_threshold_met"] if k.startswith("audio_conf"))
    assert r["audit_threshold_met"][audio_gate_key] is False
    # Hot-signal gate passes.
    assert r["audit_threshold_met"]["high+_severity_has_hot_signal"] is True


def test_includes_reviewed_at_timestamp():
    r = review_dispatch(
        incident_id="GU-7",
        severity="medium",
        audio_confidence=0.6,
    )
    assert "reviewed_at" in r
    # Should be ISO-8601-ish with timezone.
    assert "T" in r["reviewed_at"]
    assert r["reviewed_at"].endswith("+00:00")
