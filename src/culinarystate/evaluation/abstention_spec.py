"""DRAFT_PENDING_34c_KUSH -- Step 34c rollout abstention specification schema (unsigned draft).

Plan Step 34, "Abstention rule (34c)": stop or downgrade to QUALITATIVE when any holds:
evidence distance > tau; interval width > eps_max; a constraint violation; horizon
k > H_trust; or the input state is inferred rather than observed. Spine row 34c: "HUMAN:
Kush signs abstention spec"; G34c: the spec is frozen and consumed by the Step-36 tests.

This module defines the schema, a draft template with every threshold ``UNKNOWN`` and every
action unset, a validator, and ``decide`` which refuses any spec that Kush has not signed.
No tau, eps_max or H_trust value is proposed (they are PROPOSED_PILOT, calibrated on held-out
calibration sequences, never on test). Which trigger STOPs and which DOWNGRADEs is not
specified by the plan and is left for Kush. AI proposal (not adopted): a query field that is
missing or not a number fires its trigger, so UNKNOWN never yields an answer.
"""
from __future__ import annotations

import math
import re
from datetime import date
from typing import Any, Iterable, Mapping

STATUS_DRAFT = "DRAFT_PENDING_34c_KUSH_SIGNATURE"
STATUS_SIGNED = "SIGNED"
SCHEMA_VERSION = "34c-abstention-schema-v1"
DRAFT_SPEC_PATH = "reports/step34/rollout_abstention_spec_v1_DRAFT.json"
THRESHOLDS = ("tau", "eps_max", "h_trust")
ACTIONS = ("STOP", "DOWNGRADE_QUALITATIVE")
# trigger -> (query field, threshold or None, comparison)
TRIGGER_RULES: dict[str, tuple[str, str | None, str]] = {
    "EVIDENCE_DISTANCE_GT_TAU": ("evidence_distance", "tau", "gt"),
    "INTERVAL_WIDTH_GT_EPS_MAX": ("interval_width", "eps_max", "gt"),
    "CONSTRAINT_VIOLATION": ("constraint_violation", None, "is_true"),
    "HORIZON_GT_H_TRUST": ("horizon", "h_trust", "gt"),
    "INPUT_STATE_INFERRED": ("input_state_observed", None, "is_false"),
}
TRIGGERS = tuple(TRIGGER_RULES)
_TOP_KEYS = ("spec_id", "schema_version", "status", "source", "thresholds", "triggers", "signed_by", "signed_at")
_AI_LABEL = re.compile(r"\b(ksh|prv|claude|anthropic|agent|ai|assistant|bot|gpt)\b", re.I)


class SpecRefused(RuntimeError):
    """The spec is not consumable; ``blockers`` lists every reason as ``CODE: detail``."""

    def __init__(self, blockers: Iterable[str]):
        self.blockers = list(blockers)
        super().__init__("34c spec refused: " + "; ".join(self.blockers))


def draft_spec_template() -> dict[str, Any]:
    """The unsigned draft: thresholds UNKNOWN, actions unset, no signer."""
    return {
        "spec_id": "ROLLOUT-ABSTAIN-34c-v1",
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_DRAFT,
        "source": ("docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md STEP 34, 'Abstention rule (34c)' "
                   "(cites SSOT L20149-20158); registry/execution_spine_v2.csv row 34c"),
        "note": ("AI draft by worker prv (an agent, not Kush or Parv). Every value is UNKNOWN; "
                 "Kush supplies thresholds (with threshold ids), actions and the signature."),
        "thresholds": {name: {"value": None, "threshold_id": None, "value_status": "UNKNOWN"} for name in THRESHOLDS},
        "triggers": [{"trigger": t, "reads": TRIGGER_RULES[t][0], "threshold": TRIGGER_RULES[t][1], "action": None}
                     for t in TRIGGERS],
        "signed_by": None,
        "signed_at": None,
    }


def validate_spec(spec: Any) -> list[str]:
    """Structural issues (empty list = well-formed; says nothing about signature)."""
    if not isinstance(spec, dict):
        return ["SPEC_NOT_OBJECT: the spec must be a JSON object"]
    out = [f"KEY_MISSING: {k}" for k in _TOP_KEYS if k not in spec]
    if spec.get("schema_version") != SCHEMA_VERSION:
        out.append(f"SCHEMA_VERSION_INVALID: expected {SCHEMA_VERSION}")
    if spec.get("status") not in (STATUS_DRAFT, STATUS_SIGNED):
        out.append(f"STATUS_INVALID: {spec.get('status')!r}")
    th = spec.get("thresholds")
    if not isinstance(th, dict):
        out.append("THRESHOLDS_NOT_OBJECT")
    else:
        out += [f"THRESHOLD_MISSING: {n}" for n in THRESHOLDS if n not in th]
        out += [f"THRESHOLD_UNEXPECTED: {n}" for n in th if n not in THRESHOLDS]
        out += [f"THRESHOLD_MALFORMED: {n}" for n, v in th.items()
                if n in THRESHOLDS and not (isinstance(v, dict) and {"value", "threshold_id", "value_status"} <= set(v))]
    trig = spec.get("triggers")
    if not isinstance(trig, list):
        out.append("TRIGGERS_NOT_LIST")
    else:
        names = [t.get("trigger") if isinstance(t, dict) else None for t in trig]
        out += [f"TRIGGER_MISSING: {t}" for t in TRIGGERS if t not in names]
        out += [f"TRIGGER_DUPLICATE: {t}" for t in TRIGGERS if names.count(t) > 1]
        out += [f"TRIGGER_UNEXPECTED: {t}" for t in names if t not in TRIGGERS]
        out += [f"ACTION_INVALID: {t.get('trigger')}" for t in trig
                if isinstance(t, dict) and t.get("action") is not None and t.get("action") not in ACTIONS]
    return out


def _signer_is_kush(value: Any) -> bool:
    return (isinstance(value, str) and re.search(r"\bkush\b", value, re.I) is not None
            and _AI_LABEL.search(value) is None)


def _real(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def require_signed_spec(spec: Any) -> dict[str, Any]:
    """Return the spec if Kush signed a complete one; otherwise refuse with every blocker."""
    blockers = validate_spec(spec)
    if not isinstance(spec, dict):
        raise SpecRefused(blockers)
    if spec.get("status") != STATUS_SIGNED:
        blockers.append(f"SPEC_NOT_SIGNED: status is {spec.get('status')!r}")
    if not _signer_is_kush(spec.get("signed_by")):
        blockers.append("SIGNER_NOT_KUSH: signed_by must name Kush (not an AI worker label)")
    try:
        date.fromisoformat(str(spec.get("signed_at")))
    except ValueError:
        blockers.append("SIGNED_AT_INVALID: an ISO date is required")
    for name, v in (spec.get("thresholds") or {}).items():
        if not isinstance(v, dict) or name not in THRESHOLDS:
            continue
        if not _real(v.get("value")):
            blockers.append(f"THRESHOLD_UNKNOWN: {name}")
        if not v.get("threshold_id"):
            blockers.append(f"THRESHOLD_ID_MISSING: {name}")
    for t in spec.get("triggers") or []:
        if isinstance(t, dict) and t.get("action") is None:
            blockers.append(f"ACTION_UNKNOWN: {t.get('trigger')}")
    if blockers:
        raise SpecRefused(blockers)
    return spec


def _fires(rule: tuple[str, str | None, str], query: Mapping[str, Any], spec: Mapping[str, Any]) -> bool:
    field, threshold, op = rule
    value = query.get(field)
    if op == "is_true":
        return value is not False
    if op == "is_false":
        return value is not True
    if not _real(value):
        return True
    return float(value) > float(spec["thresholds"][threshold]["value"])


def decide(spec: Mapping[str, Any], query: Mapping[str, Any]) -> tuple[str, list[str]]:
    """("ANSWER", []) or (STOP | DOWNGRADE_QUALITATIVE, fired triggers); refuses unsigned specs."""
    require_signed_spec(spec)
    actions = {t["trigger"]: t["action"] for t in spec["triggers"]}
    fired = [t for t in TRIGGERS if _fires(TRIGGER_RULES[t], query, spec)]
    if not fired:
        return "ANSWER", []
    return ("STOP" if any(actions[t] == "STOP" for t in fired) else "DOWNGRADE_QUALITATIVE"), fired
