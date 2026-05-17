# Test for the 2026-05-17 codex P0 #6/#7 fix: ranger_unit must be deterministic
# per incident_id so the "every on-screen ID comes from a live, reproducible
# call" claim is fully defensible.

from peers.park_service.agent import dispatch_rangers


def test_same_incident_id_yields_same_ranger_unit():
    a = dispatch_rangers(
        incident_id="GU-466F7A6FA1F3",
        location="Selous Game Reserve, Tag-22 camera (Tanzania)",
        severity="critical",
    )
    b = dispatch_rangers(
        incident_id="GU-466F7A6FA1F3",
        location="Selous Game Reserve, Tag-22 camera (Tanzania)",
        severity="critical",
    )
    assert a["ranger_unit"] == b["ranger_unit"]
    assert a["ranger_unit"].startswith("PSR-")
    assert len(a["ranger_unit"]) == 8  # "PSR-" + 4 digits


def test_different_incident_ids_yield_different_ranger_units():
    a = dispatch_rangers(
        incident_id="GU-AAAA1111", location="X", severity="critical"
    )
    b = dispatch_rangers(
        incident_id="GU-BBBB2222", location="X", severity="critical"
    )
    assert a["ranger_unit"] != b["ranger_unit"]


def test_severity_does_not_affect_unit_choice():
    a = dispatch_rangers(
        incident_id="GU-466F7A6FA1F3", location="X", severity="critical"
    )
    b = dispatch_rangers(
        incident_id="GU-466F7A6FA1F3", location="X", severity="medium"
    )
    assert a["ranger_unit"] == b["ranger_unit"]
    assert a["estimated_arrival_minutes"] != b["estimated_arrival_minutes"]
