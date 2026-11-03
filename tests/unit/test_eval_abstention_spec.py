"""DRAFT_PENDING_34c_KUSH -- tests for the Step 34c rollout abstention specification schema.

The tracked draft spec is unsigned and has every threshold UNKNOWN; it must be refused.
A signed spec appears only in synthetic tests, with made-up values that are not proposals.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from culinarystate.evaluation import abstention_spec as ab

REPO = Path(__file__).resolve().parents[2]
DRAFT = REPO / ab.DRAFT_SPEC_PATH


def _codes(exc) -> set[str]:
    return {b.split(":", 1)[0] for b in exc.value.blockers}


def _signed() -> dict:
    spec = ab.draft_spec_template()
    for i, name in enumerate(ab.THRESHOLDS):
        spec["thresholds"][name] = {"value": 1.0 + i, "threshold_id": f"THR-SYN-{i:02d}",
                                    "value_status": "SYNTHETIC_TEST_VALUE"}
    for t in spec["triggers"]:
        t["action"] = "DOWNGRADE_QUALITATIVE"
    spec.update(status="SIGNED", signed_by="Kush Tokas (synthetic)", signed_at="2026-11-03")
    return spec


def test_tracked_draft_equals_the_template_and_is_unsigned():
    on_disk = json.loads(DRAFT.read_text(encoding="utf-8"))
    assert on_disk == ab.draft_spec_template()
    assert on_disk["status"] == "DRAFT_PENDING_34c_KUSH_SIGNATURE"
    assert all(v["value"] is None and v["value_status"] == "UNKNOWN" for v in on_disk["thresholds"].values())
    assert ab.validate_spec(on_disk) == []
    with pytest.raises(ab.SpecRefused) as exc:
        ab.require_signed_spec(on_disk)
    assert {"SPEC_NOT_SIGNED", "THRESHOLD_UNKNOWN", "ACTION_UNKNOWN"} <= _codes(exc)


def test_template_lists_the_five_plan_triggers_once():
    names = [t["trigger"] for t in ab.draft_spec_template()["triggers"]]
    assert names == list(ab.TRIGGERS) and len(set(names)) == 5


def test_synthetic_signed_spec_is_accepted():
    assert ab.require_signed_spec(_signed()) is not None


@pytest.mark.parametrize("edit,code", [
    (lambda s: s.update(signed_by="ksh"), "SIGNER_NOT_KUSH"),
    (lambda s: s.update(signed_by="Parv Goyal"), "SIGNER_NOT_KUSH"),
    (lambda s: s.update(signed_by="Claude for Kush"), "SIGNER_NOT_KUSH"),
    (lambda s: s.update(signed_at="yesterday"), "SIGNED_AT_INVALID"),
    (lambda s: s["thresholds"]["tau"].update(value=None), "THRESHOLD_UNKNOWN"),
    (lambda s: s["thresholds"]["eps_max"].update(threshold_id=None), "THRESHOLD_ID_MISSING"),
    (lambda s: s["triggers"].pop(), "TRIGGER_MISSING"),
    (lambda s: s["triggers"][0].update(action="ANSWER_ANYWAY"), "ACTION_INVALID"),
])
def test_signed_spec_refusals(edit, code):
    spec = _signed()
    edit(spec)
    with pytest.raises(ab.SpecRefused) as exc:
        ab.require_signed_spec(spec)
    assert code in _codes(exc)


def test_structural_validation():
    assert "SPEC_NOT_OBJECT" in {i.split(":")[0] for i in ab.validate_spec([])}
    bad = ab.draft_spec_template()
    bad["thresholds"]["new_knob"] = {"value": None, "threshold_id": None, "value_status": "UNKNOWN"}
    assert any(i.startswith("THRESHOLD_UNEXPECTED") for i in ab.validate_spec(bad))


def test_decide_refuses_unsigned_spec():
    with pytest.raises(ab.SpecRefused):
        ab.decide(ab.draft_spec_template(), {})


def _query(**over):
    q = {"evidence_distance": 0.0, "interval_width": 0.0, "constraint_violation": False, "horizon": 1,
         "input_state_observed": True}
    q.update(over)
    return q


def test_decide_answers_only_when_no_trigger_fires():
    spec = _signed()
    assert ab.decide(spec, _query()) == ("ANSWER", [])
    action, fired = ab.decide(spec, _query(evidence_distance=99.0, input_state_observed=False))
    assert action == "DOWNGRADE_QUALITATIVE"
    assert fired == ["EVIDENCE_DISTANCE_GT_TAU", "INPUT_STATE_INFERRED"]


def test_stop_wins_over_downgrade():
    spec = _signed()
    spec["triggers"][1]["action"] = "STOP"  # interval width
    action, fired = ab.decide(spec, _query(evidence_distance=99.0, interval_width=99.0))
    assert action == "STOP" and len(fired) == 2


@pytest.mark.parametrize("field", ["evidence_distance", "interval_width", "constraint_violation", "horizon",
                                   "input_state_observed"])
def test_unknown_query_field_never_answers(field):
    action, fired = ab.decide(_signed(), _query(**{field: None}))
    assert action != "ANSWER" and fired
