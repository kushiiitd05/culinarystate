"""Step 23a applicability engine on CONSTRUCTED SYNTHETIC cases (S158, DRAFT_PENDING_21b_22a_H4).

Engine verification only: every case states its states and conditions explicitly (spine: no COND consumed);
every mechanism, process, bound and value is a placeholder from tests/fixtures/step22a_23a_fixtures.py. No case
here is a sealed or labelled 22c case, and passing is not the G23 gate. Plan Step 23 card and 23-M: K3
three-valued gates (APPLICABLE / NOT_APPLICABLE / UNKNOWN), UNKNOWN never routes to SIMULATE (R-15); 23b is
BLOCKED (07.A, 15b) and the engine refuses that mode.
"""
from __future__ import annotations

import csv
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from culinarystate.mechanism import applicability as AP
from culinarystate.mechanism import process_signatures as PS
from tests.fixtures.mech_v1_1_fixtures import (
    cat_gate,
    entry,
    history,
    inhibitor,
    open_question,
    scope,
    state,
    stated,
    via_gate,
)
from tests.fixtures.step22a_23a_fixtures import (
    HIERARCHY_ROWS,
    MATRIX,
    accepted_competitor,
    accepted_target,
    inhibiting_gate,
    mech,
    necessary_gate,
    rule,
)

ROOT = Path(__file__).resolve().parents[2]
A, NA, U = "APPLICABLE", "NOT_APPLICABLE", "UNKNOWN"
H = PS.hierarchy_from_rows(HIERARCHY_ROWS)
AXIS = "axis:CV-013@TISSUE"
EV = ["SRC-000001"]


def _validator() -> Draft202012Validator:
    schema = json.loads(AP.APPDEC_SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator({k: v for k, v in schema.items() if k != "$id"})


VALIDATOR = _validator()


def sigs(entries: list[dict[str, Any]], rules: list[dict[str, Any]] | None = None) -> tuple[PS.ProcessSignature, ...]:
    keys = tuple(e["mechanism_key"] for e in entries)
    out = PS.build_signatures([PS.SignatureRule(**r) for r in (rules or [rule(mechanism_keys=keys)])], entries, H,
                              heat_transfer_mode_ids=frozenset())
    assert out.problems == ()
    return out.signatures


def q(**over: Any) -> AP.ApplicabilityQuery:
    base: dict[str, Any] = dict(
        case_id="SYNTH-CASE-001", entity_version_id="SYN-ENT@1", event_id="E1", target_svar_id=None,
        target_state_key="synthetic_target", process_id="PROC-SYN001", matrix=MATRIX,
        states={"synthetic_state": "SYNTH_A"}, axes=(AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"),),
        formula=AP.CaseGate(A, (), "SYNTH-FORM-1"), observability=AP.CaseGate(A, (), "SYNTH-OBS-1"),
        parameters=AP.CaseGate(A, (), "SYNTH-PARAM-1"), domain_flag="IN_VALIDATION_DOMAIN", safety_critical="NO")
    base.update(over)
    return AP.ApplicabilityQuery(**base)


def run(query: AP.ApplicabilityQuery | None = None, entries: list[dict[str, Any]] | None = None,
        rules: list[dict[str, Any]] | None = None, **kw: Any) -> dict[str, Any]:
    entries = entries if entries is not None else [mech()]
    rec = AP.evaluate(query or q(), sigs(entries, rules), entries, H, **kw)
    errs = sorted(e.message for e in VALIDATOR.iter_errors(rec))
    assert errs == [], errs
    return rec


def g(rec: dict[str, Any], gate: str) -> tuple[str, list[str]]:
    return rec["gates"][gate]["verdict"], rec["gates"][gate]["reasons"]


# ----------------------------------------------------------------------------- header, registries, modes
def test_header_constants_and_registries_agree() -> None:
    assert AP.STATUS == "DRAFT_PENDING_21b_22a_H4" and "DRAFT_PENDING_21b_22a_H4" in (AP.__doc__ or "")
    assert AP.ROUTES == ("DIRECT", "INTERPOLATE", "SIMULATE", "QUALITATIVE", "ASK", "UNKNOWN")
    rows = list(csv.DictReader(AP.REASON_REGISTRY_PATH.open(encoding="utf-8")))
    assert {r["reason_code"]: r["gate"] for r in rows} == AP.REASON_CODES
    assert all(r["status"] == AP.STATUS for r in rows)
    plan = {"NECESSARY_AXIS_UNKNOWN", "PRECONDITION_FAIL", "INHIBITOR_PRESENT", "COMPETING_UNRESOLVED",
            "INPUT_UNOBSERVED", "NO_FORM", "ASSUMPTION_VIOLATED", "NO_COMPATIBLE_PARAM", "OUT_OF_MS_LIMITS",
            "SAFETY_CRITICAL", "CONDITION_UNAUDITED"}
    assert plan <= set(AP.REASON_CODES)
    assert {r["reason_code"] for r in rows if r["origin"] == "PLAN_23M"} == plan
    routes = [r["route"] for r in csv.DictReader(AP.ROUTE_ENUM_PATH.open(encoding="utf-8"))]
    assert tuple(routes) == AP.ROUTES


def test_23b_mode_is_refused_explicitly_and_other_modes_too() -> None:
    entries = [mech()]
    with pytest.raises(AP.ApplicabilityError, match="23b.*BLOCKED"):
        AP.evaluate(q(), sigs(entries), entries, H, mode="23b")
    for m in ("23c", "", "SCIENTIFIC"):
        with pytest.raises(AP.ApplicabilityError):
            AP.evaluate(q(), sigs(entries), entries, H, mode=m)


def test_no_cond_value_is_consumed_in_23a() -> None:
    for ax in (AP.AxisValue("CV-013", "TISSUE", 5.0, "pH", source_kind="COND"),
               AP.AxisValue("CV-013", "TISSUE", 5.0, "pH", source_ref="COND-000001")):
        with pytest.raises(AP.ApplicabilityError, match="COND"):
            run(q(axes=(ax,)))


def test_axis_values_cannot_be_imputed_or_malformed() -> None:
    for bad in (float("nan"), True, (5.0, 1.0), (1.0,), Fraction(1, 2), "lower case"):
        with pytest.raises(AP.ApplicabilityError):
            AP.AxisValue("CV-013", "TISSUE", bad, "pH")


# ----------------------------------------------------------------------------- complete positive and defaults
def test_complete_constructed_positive_routes_simulate_with_a_content_id() -> None:
    rec = run()
    assert rec["route"] == "SIMULATE" and rec["applicability"] == A
    assert all(g(rec, x)[0] == A for x in ("G1", "G3", "G4", "G5", "G6", "G7", "G8"))
    assert re.fullmatch(r"APPDEC-DRAFT-[0-9a-f]{16}", rec["appdec_id"])
    assert rec["is_evidence"] is False and rec["sim_run_id"] is None and rec["condition_source"] == "CONSTRUCTED_CASE"
    assert rec["direction_set"] == ["DECREASE"] and rec["conflict_flag"] is False
    assert rec["mechanisms"][0]["signature_keys"] == ["SYNTH_RULE_ONE:SYNTH_FIXTURE_ONE"]


def test_absent_form_and_parameter_registries_leave_g6_g8_unknown_and_route_qualitative() -> None:
    rec = run(q(formula=None, observability=None, parameters=None))
    assert g(rec, "G6") == (U, ["NO_FORM"]) and g(rec, "G7") == (U, ["INPUT_UNOBSERVED"])
    assert g(rec, "G8") == (U, ["PARAM_UNCONFIRMABLE"])
    assert rec["applicability"] == U and rec["route"] == "QUALITATIVE" and g(rec, "G4")[0] == A


# ----------------------------------------------------------------------------- G4: condition gates
@pytest.mark.parametrize("value,verdict,reason", [
    (None, U, "NECESSARY_AXIS_UNKNOWN"), (0.5, NA, "NECESSARY_AXIS_OUTSIDE"), (12.0, U, "AXIS_NOT_DECIDABLE"),
    ((0.5, 5.0), U, "AXIS_NOT_DECIDABLE"), ((2.0, 3.0), A, None), (1.0, A, None), (10.0, A, None),
    ((0.1, 0.5), NA, "NECESSARY_AXIS_OUTSIDE")])
def test_necessary_numeric_gate(value: Any, verdict: str, reason: str | None) -> None:
    rec = run(q(axes=(AP.AxisValue("CV-013", "TISSUE", value, "pH"),)))
    m = rec["mechanisms"][0]
    assert m["verdict"] == verdict
    assert (reason in m["reasons"]) if reason else m["reasons"] == []
    if verdict != A:
        assert rec["route"] != "SIMULATE" and rec["applicability"] == verdict


def test_missing_axis_is_listed_and_can_become_an_ask() -> None:
    rec = run(q(axes=()))
    assert AXIS in rec["missing_inputs"] and rec["route"] == "UNKNOWN" and rec["ask_candidates"] == []
    rec = run(q(axes=(), user_observable=(AXIS,)))
    assert rec["route"] == "ASK" and rec["ask_candidates"] == [AXIS]


def test_location_unit_basis_and_conflicts_are_never_reconciled() -> None:
    cases = {"NECESSARY_AXIS_UNKNOWN": (AP.AxisValue("CV-013", "MEDIUM", 5.0, "pH"),),
             "AXIS_UNIT_MISMATCH": (AP.AxisValue("CV-013", "TISSUE", 5.0, "K"),),
             "AXIS_CONFLICT": (AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"), AP.AxisValue("CV-013", "TISSUE", 6.0, "pH")),
             "AXIS_TYPE_MISMATCH": (AP.AxisValue("CV-013", "TISSUE", "SYNTH_A", None),)}
    for reason, axes in cases.items():
        m = run(q(axes=axes))["mechanisms"][0]
        assert m["verdict"] == U and reason in m["reasons"], reason
    same = (AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"), AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"))
    assert run(q(axes=same))["mechanisms"][0]["verdict"] == A
    moist = necessary_gate(key="CG02", cv="CV-016", unit="fraction", basis="WET_BASIS", mn=stated(0.1), mx=stated(0.9))
    e = mech(condition_gates=[necessary_gate(), moist])
    ph = AP.AxisValue("CV-013", "TISSUE", 5.0, "pH")
    for basis, verdict in (("DRY_BASIS", U), ("NOT_APPLICABLE", U), ("WET_BASIS", A)):
        m = run(q(axes=(ph, AP.AxisValue("CV-016", "TISSUE", 0.5, "fraction", basis=basis))), [e])["mechanisms"][0]
        assert m["verdict"] == verdict and (verdict == A or "AXIS_BASIS_MISMATCH" in m["reasons"]), basis


def test_semantically_defective_entries_are_refused() -> None:
    e = mech(condition_gates=[necessary_gate(unit="K")])
    with pytest.raises(AP.ApplicabilityError, match="semantic"):
        AP.evaluate(q(), sigs([e]), [e], H)


def test_candidate_gate_and_gate_matrix_scope_give_unknown() -> None:
    e = mech(condition_gates=[necessary_gate(status="CANDIDATE")])
    m = run(entries=[e])["mechanisms"][0]
    assert m["verdict"] == U and "ITEM_NOT_ACCEPTED" in m["reasons"]
    e = mech(condition_gates=[necessary_gate(matrix_scope=scope("FOOD_CLASS", inc=("synthetic other class",)))])
    m = run(entries=[e])["mechanisms"][0]
    assert m["verdict"] == U and "GATE_MATRIX_UNLISTED" in m["reasons"]


def test_categorical_necessary_gate() -> None:
    cg = cat_gate("NECESSARY", allowed=["SYNTH_OK"], excluded=["SYNTH_BAD"], key="CG02", status="ACCEPTED",
                  evidence_ids=EV, matrix_scope=scope("FOOD_CLASS", inc=(MATRIX,)), rationale_raw="synthetic")
    e = mech(condition_gates=[necessary_gate(), cg])
    base = (AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"),)
    for val, verdict, reason in (("SYNTH_OK", A, None), ("SYNTH_BAD", NA, "CATEGORY_EXCLUDED"),
                                 ("SYNTH_OTHER", U, "CATEGORY_UNLISTED"), (None, U, "NECESSARY_AXIS_UNKNOWN")):
        m = run(q(axes=base + (AP.AxisValue("CV-023", "MEDIUM", val, None),)), [e])["mechanisms"][0]
        assert m["verdict"] == verdict and (reason is None or reason in m["reasons"]), val


# ----------------------------------------------------------------------------- G4: preconditions and matrix
@pytest.mark.parametrize("value,verdict,reason", [
    ("SYNTH_B", NA, "PRECONDITION_FAIL"), (None, U, "PRECONDITION_UNKNOWN"), ("UNKNOWN", U, "PRECONDITION_UNKNOWN")])
def test_precondition(value: str | None, verdict: str, reason: str) -> None:
    states = {} if value is None else {"synthetic_state": value}
    m = run(q(states=states))["mechanisms"][0]
    assert m["verdict"] == verdict and reason in m["reasons"]


def test_matrix_scope() -> None:
    e = mech(matrix_scope=scope("FOOD_CLASS", inc=(MATRIX,), exc=("synthetic excluded",)))
    for matrix, verdict, reason in (("synthetic excluded", NA, "MATRIX_EXCLUDED"), ("synthetic unlisted", U,
                                                                                     "MATRIX_UNLISTED"),
                                    (None, U, "MATRIX_UNKNOWN")):
        m = run(q(matrix=matrix), [e])["mechanisms"][0]
        assert m["verdict"] == verdict and reason in m["reasons"], matrix


# ----------------------------------------------------------------------------- G4: inhibitors and modifiers
def test_inhibiting_gate_present_absent_and_partial() -> None:
    e = mech(condition_gates=[necessary_gate(), inhibiting_gate()])
    two = (AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"),)
    assert run(q(axes=two), [e])["mechanisms"][0]["verdict"] == A, "the same axis outside the inhibiting window"
    e = mech(condition_gates=[necessary_gate(mx=stated(40.0)), inhibiting_gate()])
    m = run(q(axes=(AP.AxisValue("CV-013", "TISSUE", 25.0, "pH"),)), [e])["mechanisms"][0]
    assert m["verdict"] == NA and "INHIBITOR_PRESENT" in m["reasons"]
    partial = inhibitor("INH01", extent="PARTIAL", via=via_gate("CG02"), status="ACCEPTED", evidence_ids=EV)
    e = mech(condition_gates=[necessary_gate(mx=stated(40.0)), inhibiting_gate()], inhibitors_mitigators=[partial])
    rec = run(q(axes=(AP.AxisValue("CV-013", "TISSUE", 25.0, "pH"),)), [e])
    assert rec["mechanisms"][0]["verdict"] == A and rec["mechanisms"][0]["qualitative_only"] is True
    assert rec["route"] == "QUALITATIVE" and "QUALITATIVE_ONLY_PARTIAL_INHIBITION" in g(rec, "G9")[1]
    unknown_extent = dict(partial, extent="UNKNOWN")
    e = mech(condition_gates=[necessary_gate(mx=stated(40.0)), inhibiting_gate()], inhibitors_mitigators=[unknown_extent])
    m = run(q(axes=(AP.AxisValue("CV-013", "TISSUE", 25.0, "pH"),)), [e])["mechanisms"][0]
    assert m["verdict"] == U and "INHIBITOR_EXTENT_UNKNOWN" in m["reasons"]


def test_state_predicate_inhibitor() -> None:
    via = {"mode": "STATE_PREDICATE", "gate_key": None, "state_ref": state("synthetic_agent"),
           "predicate": {"operator": "IS", "values": ["SYNTH_PRESENT"]}}
    e = mech(inhibitors_mitigators=[inhibitor("INH01", extent="COMPLETE", via=via, status="ACCEPTED",
                                              evidence_ids=EV)])
    for agent, verdict, reason in (("SYNTH_PRESENT", NA, "INHIBITOR_PRESENT"), ("SYNTH_ABSENT", A, None),
                                   (None, U, "INHIBITOR_UNKNOWN")):
        states = {"synthetic_state": "SYNTH_A"} | ({} if agent is None else {"synthetic_agent": agent})
        m = run(q(states=states), [e])["mechanisms"][0]
        assert m["verdict"] == verdict and (reason is None or reason in m["reasons"]), agent


def test_catalyst_never_changes_g4_but_its_missing_axis_makes_g7_unknown() -> None:
    mg = cat_gate("MODULATING", allowed=["SYNTH_CAT"], key="CG02", status="ACCEPTED", evidence_ids=EV,
                  matrix_scope=scope("FOOD_CLASS", inc=(MATRIX,)))
    cat = inhibitor("INH01", "CATALYST", "SBO:0000013", "NOT_APPLICABLE", via_gate("CG02"), status="ACCEPTED",
                    evidence_ids=EV)
    e = mech(condition_gates=[necessary_gate(), mg], inhibitors_mitigators=[cat])
    rec = run(entries=[e])
    assert g(rec, "G4")[0] == A and g(rec, "G7") == (U, ["MODIFIER_INPUT_UNOBSERVED"])
    assert rec["route"] != "SIMULATE" and "axis:CV-023@MEDIUM" in rec["missing_inputs"]
    rec = run(q(axes=(AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"), AP.AxisValue("CV-023", "MEDIUM", "SYNTH_X", None))),
              [e])
    assert g(rec, "G7")[0] == A and rec["route"] == "SIMULATE"


def test_history_input_is_an_observability_requirement() -> None:
    h = history("INPUT_REQUIRED", "synthetic_history")
    h.update(status="ACCEPTED", evidence_ids=EV)
    rec = run(entries=[mech(history_dependence=[h])])
    assert g(rec, "G7") == (U, ["HISTORY_INPUT_UNOBSERVED"]) and rec["route"] != "SIMULATE"
    rec = run(q(states={"synthetic_state": "SYNTH_A", "synthetic_history": "SYNTH_H"}), [mech(history_dependence=[h])])
    assert g(rec, "G7")[0] == A


# ----------------------------------------------------------------------------- refusal of non-consumable MECH entries
def test_non_consumable_entries_are_refused_with_reasons_propagated() -> None:
    rec = run(entries=[entry()])
    m = rec["mechanisms"][0]
    assert m["consumable"] is False and m["verdict"] == U
    assert {"NOT_ACCEPTED", "NOT_HUMAN_VERIFIED", "GATES_UNKNOWN"} <= set(m["refusal_reasons"])
    assert {"MECH_NOT_CONSUMABLE", "MECH_NOT_ACCEPTED", "MECH_GATES_UNKNOWN"} <= set(m["reasons"])
    assert rec["applicability"] == U and rec["route"] != "SIMULATE"
    m = run(entries=[mech(open_questions=[open_question()])])["mechanisms"][0]
    assert m["verdict"] == U and "MECH_OPEN_QUESTIONS" in m["reasons"]


def test_candidate_target_contributes_unknown() -> None:
    m = run(entries=[mech(affected_targets=[accepted_target(status="CANDIDATE")])])["mechanisms"][0]
    assert m["verdict"] == U and "TARGET_NOT_ACCEPTED" in m["reasons"]


# ----------------------------------------------------------------------------- G1, G3 and G5
def test_unresolved_event_no_candidate_and_unknown_trigger_modifier() -> None:
    rec = run(q(process_id=None, event_resolved=False))
    assert g(rec, "G1") == (U, ["EVENT_UNRESOLVED"]) and rec["route"] == "UNKNOWN"
    rec = run(q(process_id="PROC-SYN777"))
    assert g(rec, "G1") == (U, ["PROCESS_NOT_IN_HIERARCHY"])
    rec = run(q(process_id="PROC-SYN003"))
    assert g(rec, "G3") == (U, ["NO_CANDIDATE_MECHANISM"]) and g(rec, "G4")[0] == U and rec["route"] == "UNKNOWN"
    pred = PS.ModifierPredicate("INTENSITY", "IS", ("SYNTH_LOW",))
    rec = run(rules=[rule(modifier_predicates=(pred,))])
    assert g(rec, "G3") == (U, ["TRIGGER_MODIFIER_UNKNOWN"]) and rec["mechanisms"][0]["verdict"] == U
    rec = run(q(modifiers={"INTENSITY": "SYNTH_LOW"}), rules=[rule(modifier_predicates=(pred,))])
    assert rec["route"] == "SIMULATE"
    rec = run(q(target_state_key="synthetic_unrelated"))
    assert g(rec, "G3") == (U, ["NO_CANDIDATE_MECHANISM"]) and rec["mechanisms"] == []


def two(dirs2: tuple[str, ...] = ("DECREASE",), **over2: Any) -> list[dict[str, Any]]:
    one = mech(competes_with=[accepted_competitor("SYNTH_FIXTURE_TWO")])
    effect = {"effect": "FORMED"} if dirs2 == ("INCREASE",) else {}
    other = mech("SYNTH_FIXTURE_TWO", "MECH-000002", competes_with=[accepted_competitor("SYNTH_FIXTURE_ONE")],
                 affected_targets=[accepted_target(dirs=dirs2, **effect)], **over2)
    return [one, other]


def test_competition_rules() -> None:
    rec = run(entries=two())
    assert g(rec, "G5") == (NA, ["COMPETING_BOTH_APPLICABLE"]) and rec["applicability"] == NA
    assert rec["route"] == "QUALITATIVE" and rec["direction_set"] == ["DECREASE"]
    rec = run(q(joint_form_ref="SYNTH-JOINT-FORM"), two())
    assert g(rec, "G5")[0] == A and rec["route"] == "SIMULATE"
    rec = run(entries=two(condition_gates=[necessary_gate(cv="CV-015", unit="aw", mn=None, mx=None)]))
    assert g(rec, "G5") == (U, ["COMPETING_UNRESOLVED"]) and rec["route"] == "QUALITATIVE"
    rec = run(entries=two(("INCREASE",)))
    assert rec["conflict_flag"] is True and rec["route"] == "UNKNOWN"
    one = mech(competes_with=[dict(accepted_competitor("SYNTH_FIXTURE_TWO"), status="CANDIDATE")])
    rec = run(entries=[one, two()[1]], rules=[rule(mechanism_keys=("SYNTH_FIXTURE_ONE",))])
    assert g(rec, "G5") == (U, ["COMPETITION_NOT_ACCEPTED"]) and rec["route"] != "SIMULATE"


def test_competitor_outside_the_candidate_set_does_not_block() -> None:
    one = mech(competes_with=[accepted_competitor("SYNTH_FIXTURE_TWO")])
    other = two()[1]
    rec = run(entries=[one, other], rules=[rule(mechanism_keys=("SYNTH_FIXTURE_ONE",))])
    assert g(rec, "G5")[0] == A and rec["route"] == "SIMULATE"


# ----------------------------------------------------------------------------- G0, G6-G8 case gates and the route
def test_case_stated_gates_are_validated() -> None:
    rec = run(q(formula=AP.CaseGate(NA, ("ASSUMPTION_VIOLATED",))))
    assert g(rec, "G6") == (NA, ["ASSUMPTION_VIOLATED"]) and rec["applicability"] == NA
    rec = run(q(parameters=AP.CaseGate(NA, ("NO_COMPATIBLE_PARAM",))))
    assert rec["applicability"] == NA and rec["route"] == "QUALITATIVE"
    for bad in (AP.CaseGate(A, ()), AP.CaseGate(U, ()), AP.CaseGate(U, ("NO_COMPATIBLE_PARAM",)),
                AP.CaseGate("MAYBE", ("NO_FORM",))):
        with pytest.raises(AP.ApplicabilityError):
            run(q(formula=bad))


@pytest.mark.parametrize("domain,safety,route,label,reason", [
    ("IN_CALIBRATION_ONLY", "NO", "QUALITATIVE", "RESEARCH_ONLY", "DOMAIN_NOT_VALIDATED"),
    ("EXTRAPOLATED_WITHIN_LIMITS", "NO", "QUALITATIVE", "EXTRAPOLATED", "DOMAIN_NOT_VALIDATED"),
    ("SIM_PROHIBITED", "NO", "QUALITATIVE", "NONE", "OUT_OF_MS_LIMITS"),
    ("UNKNOWN", "NO", "QUALITATIVE", "NONE", "DOMAIN_UNKNOWN"),
    ("IN_VALIDATION_DOMAIN", "YES", "QUALITATIVE", "NONE", "SAFETY_CRITICAL"),
    ("IN_VALIDATION_DOMAIN", "UNKNOWN", "QUALITATIVE", "NONE", "SAFETY_UNKNOWN")])
def test_domain_and_safety_keep_simulate_narrow(domain: str, safety: str, route: str, label: str, reason: str) -> None:
    rec = run(q(domain_flag=domain, safety_critical=safety))
    assert rec["route"] == route and rec["model_estimate_label"] == label and reason in g(rec, "G9")[1]


def test_evidence_precheck_dominates_and_cross_check_needs_every_gate() -> None:
    rec = run(q(evidence_precheck="DIRECT"))
    assert rec["route"] == "DIRECT" and rec["cross_check"] == "SIMULATE"
    rec = run(q(evidence_precheck="BRACKETING", formula=None))
    assert rec["route"] == "INTERPOLATE" and rec["cross_check"] == "NONE"
    assert "G0_NOT_EVALUATED" in g(run(), "G0")[1]


# ----------------------------------------------------------------------------- refusal of malformed inputs
def test_schema_invalid_entries_and_tampered_signatures_are_refused() -> None:
    bad = mech()
    bad["is_evidence"] = True
    with pytest.raises(AP.ApplicabilityError, match="schema"):
        AP.evaluate(q(), sigs([mech()]), [bad], H)
    s = sigs([mech()])[0]
    from dataclasses import replace
    widened = replace(s, candidate_effects=(replace(s.candidate_effects[0], allowed_directions=("INCREASE",)),))
    with pytest.raises(AP.ApplicabilityError, match="signature"):
        AP.evaluate(q(), (widened,), [mech()], H)


# ----------------------------------------------------------------------------- determinism and registry closure
def test_replay_is_byte_identical_and_ids_change_with_input() -> None:
    a = json.dumps(run(), sort_keys=True)
    assert a == json.dumps(run(), sort_keys=True)
    assert run()["appdec_id"] != run(q(case_id="SYNTH-CASE-002"))["appdec_id"]


def test_every_emitted_reason_is_registered() -> None:
    recs = [run(), run(q(axes=())), run(q(formula=None, observability=None, parameters=None)), run(entries=[entry()]),
            run(q(process_id=None, event_resolved=False)), run(entries=two())]
    for rec in recs:
        emitted = {r for x in rec["gates"].values() for r in x["reasons"]}
        emitted |= {r for m in rec["mechanisms"] for r in m["reasons"]}
        assert emitted <= set(AP.REASON_CODES)
        assert "CONDITION_UNAUDITED" not in emitted


# ----------------------------------------------------------------------------- 26g compatibility
def test_projection_to_the_26g_applicability_binding() -> None:
    from culinarystate.simulation import recipe_adapter as ra
    system = sorted(ra.SYSTEM_REQUIREMENTS)[0]
    rec = run()
    b = AP.to_applicability_binding(rec, system)
    assert isinstance(b, ra.ApplicabilityBinding)
    assert (b.event_id, b.system_id, b.status, b.ref) == ("E1", system, A, rec["appdec_id"])
    qual = run(q(formula=None))
    assert AP.to_applicability_binding(qual, system).status == U, "only a SIMULATE route projects to APPLICABLE"
    na = run(q(axes=(AP.AxisValue("CV-013", "TISSUE", 0.5, "pH"),)))
    assert AP.to_applicability_binding(na, system).status == NA
    direct = run(q(evidence_precheck="DIRECT"))
    assert AP.to_applicability_binding(direct, system).status == U


def test_26g_routes_simulate_only_from_an_appdec_simulate_record() -> None:
    from culinarystate.simulation import recipe_adapter as ra
    from culinarystate.state_graph.event_log import EngineEvent
    from culinarystate.state_graph.replay import replay_events
    from culinarystate.state_graph.source_class import SourceClass

    system = sorted(ra.SYSTEM_REQUIREMENTS)[0]
    replay = replay_events([EngineEvent("INTRO/N1", (-1, 0), kind="INTRODUCE_LOT", produces=("N1",),
                                        produced_types=(("N1", "INGREDIENT_LOT"),)),
                            EngineEvent("E1", (0, 0), consumes=("N1",), produces=("N2",),
                                        produced_types=(("N2", "INTERMEDIATE"),))])

    def binding(name: str) -> ra.ConditionBinding:
        spec = ra.INPUT_SPECS[name]
        value: Any = {"PROFILE": (ra.ProfileSegment(Fraction(0), Fraction(1), Fraction(1), Fraction(1)),),
                      "NUMBER": Fraction(1), "CODE": "SYNTH_CODE"}[spec.kind]
        return ra.ConditionBinding("E1", name, value, "EVT", "EVT-000001", SourceClass.SYNTHETIC, spec.unit)

    inputs = [binding(n) for n in ra.SYSTEM_REQUIREMENTS[system]]
    for rec, route in ((run(), "SIMULATE"), (run(q(formula=None)), "SIM_PROHIBITED"), (run(q(axes=())), "SIM_PROHIBITED")):
        out = ra.build_simulation_inputs(replay, recipe_id="SYN-23A", system_id=system, bindings=inputs,
                                         applicability=[AP.to_applicability_binding(rec, system)])
        r = {x.event_id: x for x in out.records}["E1"]
        assert r.route == route
        assert r.applicability_refs == (rec["appdec_id"],)


# ----------------------------------------------------------------------------- purity
def test_engine_module_is_pure_and_names_no_chemistry_or_system() -> None:
    src = Path(AP.__file__).read_text(encoding="utf-8")
    assert not re.search(r"ascorb|chlorophyll|pheoph|vitamin|alliin|maillard|sim_aa|sim_chl", src, re.I)
    for banned in ("write_text", "write_bytes", "ledgers/data", "COND.jsonl", "subprocess", "requests"):
        assert banned not in src, banned
