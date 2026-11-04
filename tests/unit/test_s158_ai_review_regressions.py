"""RED regression tests for the S158 AI cross-review of ksh's parts A + B (AI verdict, pending Kush/Parv review).

Reviewer: worker "prv", an AI agent (not Parv). SYNTHETIC fixtures only. Each test encodes one finding of
reports/step21/S158_ai_review.md; the tests fail on the reviewed code and pass after the fix commits.
"""
from __future__ import annotations

import copy
from typing import Any

from culinarystate.lineage import kinetic_contract as KC
from culinarystate.mechanism import mech_contract as MC
from tests.fixtures import kinetic_v1_1_fixtures as F
from tests.fixtures.mech_v1_1_fixtures import (
    accepted,
    cat_gate,
    entry,
    evidence_ref,
    gate,
    open_,
    precondition,
    stated,
)


def _verified(k: dict[str, Any]) -> dict[str, Any]:
    k["verification"] = {"status": "HUMAN_VERIFIED", "verifier": "Kush", "verified_at": F.NOW}
    return k


# ----------------------------------------------------------------------------- R1 split eligibility
def test_r1_unverified_series_is_never_eligible_for_test_or_sim_val() -> None:
    """04.6-min KIN row (D-029): may enter test / calibration "Y only if human verified"."""
    k, pts, obs = F.series(digitised=True)
    assert k["verification"]["status"] == "UNVERIFIED"
    v = KC.split_eligibility(k, pts, obs)
    assert v.verdict != KC.ELIGIBLE and "NOT_HUMAN_VERIFIED" in v.reasons, v
    for status in ("AI_PRECHECKED", "NEEDS_SOURCE", "CONFLICT"):
        k["verification"] = {"status": status}
        assert KC.split_eligibility(k, pts, obs).verdict == KC.UNKNOWN, status
    k["verification"] = {"status": "HUMAN_REJECTED", "verifier": "Parv", "verified_at": F.NOW}
    assert KC.split_eligibility(k, pts, obs).verdict == KC.NOT_ELIGIBLE
    assert KC.split_eligibility(_verified(k), pts, obs).verdict == KC.ELIGIBLE


def test_r1_a_retracted_or_superseded_series_is_not_eligible() -> None:
    k, pts, obs = F.series(digitised=True)
    _verified(k)
    for status in ("RETRACTED", "SUPERSEDED", "DEPRECATED"):
        k["status"] = status
        v = KC.split_eligibility(k, pts, obs)
        assert v.verdict == KC.NOT_ELIGIBLE and "RECORD_NOT_ACTIVE" in v.reasons, (status, v)


# ----------------------------------------------------------------------------- R2 Arrhenius eligibility
def test_r2_no_reported_temperature_is_never_arrhenius_eligible() -> None:
    """R04-15 and the v1.1 doc section 2: a series without a reported temperature cannot be ELIGIBLE."""
    for iso, come_up in (("PRODUCT_ISOTHERMAL_STATED", "NOT_REPORTED"), ("SETPOINT_ONLY", "EXCLUDED_FROM_TIME")):
        k = F.kin()
        assert k["condition_profile"]["temperature_status"] == "NOT_REPORTED"
        k["condition_profile"]["isothermality"] = iso
        k["time_base"]["come_up_time"]["status"] = come_up
        v = KC.arrhenius_eligibility(k)
        assert v.verdict == KC.NOT_ELIGIBLE and "TEMPERATURE_NOT_REPORTED" in v.reasons, (iso, come_up, v)
        k["condition_profile"]["temperature_status"] = "UNKNOWN"
        v = KC.arrhenius_eligibility(k)
        assert v.verdict == KC.UNKNOWN and "TEMPERATURE_STATUS_UNKNOWN" in v.reasons, (iso, come_up, v)


# ----------------------------------------------------------------------------- R3 consumable entries are ACTIVE
def test_r3_only_active_records_are_consumable_for_applicability() -> None:
    for status, sup in (("RETRACTED", None), ("DEPRECATED", None), ("SUPERSEDED", "MECH-000002")):
        e = accepted(status=status, superseded_by=sup)
        assert MC.schema_errors(e) == [], status
        ok, why = MC.consumable_for_applicability(e)
        assert not ok and "NOT_ACTIVE" in why, (status, why)
    assert MC.consumable_for_applicability(accepted()) == (True, ())


def test_r3_the_23a_engine_refuses_a_retracted_entry() -> None:
    from culinarystate.mechanism import applicability as AP
    from culinarystate.mechanism import process_signatures as PS
    from tests.fixtures.step22a_23a_fixtures import HIERARCHY_ROWS, MATRIX, mech, rule

    h = PS.hierarchy_from_rows(HIERARCHY_ROWS)
    e = mech(status="RETRACTED")
    sigs = PS.build_signatures([PS.SignatureRule(**rule())], [e], h, heat_transfer_mode_ids=frozenset()).signatures
    q = AP.ApplicabilityQuery(
        case_id="SYNTH-R3", entity_version_id="SYN-ENT@1", event_id="E1", target_svar_id=None,
        target_state_key="synthetic_target", process_id="PROC-SYN001", matrix=MATRIX,
        states={"synthetic_state": "SYNTH_A"}, axes=(AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"),),
        formula=AP.CaseGate("APPLICABLE", (), "F"), observability=AP.CaseGate("APPLICABLE", (), "O"),
        parameters=AP.CaseGate("APPLICABLE", (), "P"), domain_flag="IN_VALIDATION_DOMAIN", safety_critical="NO")
    rec = AP.evaluate(q, sigs, [e], h)
    m = rec["mechanisms"][0]
    assert m["verdict"] == "UNKNOWN" and "MECH_NOT_ACTIVE" in m["reasons"] and rec["route"] != "SIMULATE"


# ----------------------------------------------------------------------------- R4 / R5 semantic validator gaps
def _cv() -> list[dict[str, str]]:
    return MC.read_cv_rows()


def test_r4_categorical_set_on_a_numeric_cv_is_a_semantic_problem() -> None:
    """Schema $comment: 'dimension agrees with domain_kind' is semantic-validator work (both directions)."""
    g = cat_gate("INHIBITING", allowed=["SYNTH_A"], evidence_ids=["SRC-000001"])
    g.update(cv_id="CV-013", location="TISSUE")
    e = entry(condition_gates=[g], evidence_refs=[evidence_ref()])
    assert MC.schema_errors(e) == []
    assert any("categorical set on a non-categorical CV" in p for p in MC.semantic_problems(e, _cv()))
    ok = entry(condition_gates=[cat_gate("INHIBITING", allowed=["SYNTH_A"], evidence_ids=["SRC-000001"])],
               evidence_refs=[evidence_ref()])
    assert MC.semantic_problems(ok, _cv()) == []


def test_r5_open_stated_bounds_take_part_in_the_min_max_order() -> None:
    ev = {"evidence_ids": ["SRC-000001"], "rationale_raw": "synthetic"}
    bad = entry(condition_gates=[gate(cv="CV-015", unit="aw", mn=open_(0.9), mx=stated(0.2), **ev)],
                evidence_refs=[evidence_ref()])
    assert MC.schema_errors(bad) == []
    assert any("min <= max" in p for p in MC.semantic_problems(bad, _cv()))
    good = entry(condition_gates=[gate(cv="CV-015", unit="aw", mn=open_(0.2), mx=stated(0.9), **ev)],
                 evidence_refs=[evidence_ref()])
    assert MC.semantic_problems(good, _cv()) == []


# ----------------------------------------------------------------------------- R6 evidence for the EQ21-07 wording fix
def test_r6_a_chemical_entry_with_a_precondition_and_only_modulating_gates_may_set_gates_unknown_false() -> None:
    """Evidence for the doc fix (no code change): EQ21-07 said such an entry 'can never' have gates_unknown false."""
    e = entry(gates_unknown=False, kind="CHEMICAL_REACTION", preconditions=[precondition()],
              condition_gates=[gate(gtype="MODULATING")])
    assert MC.schema_errors(copy.deepcopy(e)) == []
