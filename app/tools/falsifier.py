# Copyright 2026 GUARDIAN
# Falsifier — adversarial review of every proposed dispatch.
#
# The Falsifier's job is to push back. When the orchestrator is about to fire
# notify_park_service / notify_sponsor_sustainability, the Falsifier asks: is
# the evidence strong enough to warrant this action, given the SOPs? If not,
# it issues a DISSENT — which does NOT block the action (humans decide), but
# the dissent record ships in the Court-Evidence bundle and the Sponsor
# Sustainability TNFD filing.
#
# Why: a system where every agent agrees with every other agent is
# unauditable. Big-4 auditors and TNFD reviewers require the dissent record
# to be present in any chain-of-custody packet. Falsifier produces it.
#
# Design: deterministic rule engine first (no LLM hallucination on the
# verdict), wrapped by an ADK agent layer for the agentic story. The verdict
# is decidable from the inputs alone — no flexibility, no judgment-on-the-fly.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

# --- Threshold constants (the SOPs the Falsifier defends) ------------------

# Audio confidence required for dispatch at each severity.
AUDIO_CONF_GATE = {
    "critical": 0.80,
    "high": 0.70,
    "medium": 0.50,
    "low": 0.30,
}

# Severity may not exceed this when species is "unlisted" in IUCN/CITES.
MAX_SEVERITY_FOR_UNLISTED = "medium"

_SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def review_dispatch(
    incident_id: str,
    severity: str,
    audio_confidence: Optional[float] = None,
    species_compliance_flag: Optional[str] = None,
    threat_signals: Optional[list[str]] = None,
    observation_timestamp: Optional[str] = None,
) -> dict:
    """Adversarial review of a proposed dispatch action.

    Pushes back against the orchestrator's escalation when the evidence
    does not meet the SOP gates. Verdict is decidable from inputs — no
    LLM judgment in the loop. The dissent record (if any) ships in the
    Court-Evidence bundle and the Sponsor Sustainability TNFD filing.

    Args:
        incident_id: GUARDIAN incident_id under review.
        severity: Proposed severity (low | medium | high | critical).
        audio_confidence: Audio Agent's confidence in classification (0-1).
        species_compliance_flag: Species ID's flag (material | informational
            | unlisted). Drives the materiality cap for sponsor filings.
        threat_signals: Threat_signal list from upstream agents
            (e.g., ["gunshot", "vehicle_engine"]).
        observation_timestamp: ISO-8601 timestamp of the observation.

    Returns:
        Dict with:
        - verdict: "concur" | "dissent" | "abstain"
        - dissent_reason: human-readable explanation when verdict=dissent
        - severity_0_5: int — Falsifier's confidence in its position
        - audit_threshold_met: per-gate pass/fail diagnostics
        - reviewed_at: ISO-8601 timestamp
    """
    if not incident_id:
        return {
            "verdict": "abstain",
            "dissent_reason": "incident_id is required; Falsifier cannot audit anonymous dispatches",
            "severity_0_5": 5,
            "audit_threshold_met": {},
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }

    sev = (severity or "medium").lower()
    if sev not in _SEVERITY_RANK:
        return {
            "verdict": "abstain",
            "dissent_reason": f"unknown severity: {severity!r}; cannot evaluate against SOPs",
            "severity_0_5": 5,
            "audit_threshold_met": {},
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }

    gates: dict[str, bool] = {}
    dissent_reasons: list[str] = []
    dissent_severity = 0

    # Gate 1: audio confidence vs severity threshold.
    if audio_confidence is not None:
        gate_value = AUDIO_CONF_GATE.get(sev, 0.5)
        passed = audio_confidence >= gate_value
        gates[f"audio_conf>={gate_value:.2f}_for_{sev}"] = passed
        if not passed:
            dissent_reasons.append(
                f"audio confidence {audio_confidence:.2f} below {sev} dispatch threshold "
                f"({gate_value:.2f}); recommend human-verification step before dispatch"
            )
            # Severity of dissent scales with the gap.
            gap = gate_value - audio_confidence
            dissent_severity = max(dissent_severity, min(5, int(gap * 10) + 2))

    # Gate 2: severity ceiling when species is unlisted.
    if species_compliance_flag == "unlisted":
        max_rank = _SEVERITY_RANK[MAX_SEVERITY_FOR_UNLISTED]
        cur_rank = _SEVERITY_RANK[sev]
        passed = cur_rank <= max_rank
        gates[f"severity<={MAX_SEVERITY_FOR_UNLISTED}_for_unlisted_species"] = passed
        if not passed:
            dissent_reasons.append(
                f"severity {sev!r} exceeds the {MAX_SEVERITY_FOR_UNLISTED!r} ceiling for "
                "species not listed in IUCN/CITES; this escalation may overstate "
                "regulatory materiality"
            )
            dissent_severity = max(dissent_severity, 3)

    # Gate 3: observation_timestamp must be within 1h of now (replay attack guard).
    if observation_timestamp:
        try:
            ts = datetime.fromisoformat(observation_timestamp.replace("Z", "+00:00"))
            delta_s = abs((datetime.now(timezone.utc) - ts).total_seconds())
            within_window = delta_s <= 3600
            gates["observation_within_1h"] = within_window
            if not within_window:
                dissent_reasons.append(
                    f"observation_timestamp drift {delta_s:.0f}s exceeds the 1h freshness "
                    "gate; this incident may be a replay or stale event"
                )
                dissent_severity = max(dissent_severity, 4)
        except (ValueError, TypeError):
            gates["observation_within_1h"] = False
            dissent_reasons.append(
                f"observation_timestamp {observation_timestamp!r} is malformed; "
                "cannot verify event freshness"
            )
            dissent_severity = max(dissent_severity, 3)

    # Gate 4: threat_signals must align with severity.
    if threat_signals and sev in {"high", "critical"}:
        hot_signals = {"gunshot", "vehicle_engine", "distressed_herd", "fence_breach"}
        has_hot = any(s.lower() in hot_signals for s in threat_signals)
        gates["high+_severity_has_hot_signal"] = has_hot
        if not has_hot:
            dissent_reasons.append(
                f"severity {sev!r} not supported by any hot threat_signal "
                f"({hot_signals!r}); current signals: {threat_signals!r}"
            )
            dissent_severity = max(dissent_severity, 3)

    # Decide verdict.
    if not gates:
        # Nothing to audit (no telemetry provided). Abstain rather than fake concur.
        verdict = "abstain"
        reason = "no audit-eligible telemetry provided (audio_confidence, species_compliance_flag, threat_signals all None)"
        sev_out = 1
    elif dissent_reasons:
        verdict = "dissent"
        reason = "; ".join(dissent_reasons)
        sev_out = dissent_severity
    else:
        verdict = "concur"
        reason = ""
        sev_out = 0

    return {
        "verdict": verdict,
        "dissent_reason": reason,
        "severity_0_5": sev_out,
        "audit_threshold_met": gates,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "incident_id": incident_id,
    }
