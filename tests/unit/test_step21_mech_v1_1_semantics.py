"""Semantic validator and Step 22 / 23 read API for MECH v1.1 DRAFT entries (S158, DRAFT_PENDING_H4).

Exercises culinarystate.mechanism.mech_contract on SYNTHETIC SCHEMA FIXTURES. The three-valued evaluator
at the end is the TEST-LOCAL reference of README section 5 (v1), kept test-local: it defines no behaviour
for the Step 23 engine, it only shows that the v1.1 record cannot be read so that UNKNOWN becomes APPLICABLE.
"""
from __future__ import annotations

import copy
import csv
import random
from pathlib import Path
from typing import Any

from culinarystate.mechanism import mech_contract as MC

from tests.fixtures.mech_v1_1_fixtures import (
    accepted,
    bound,
    cat_gate,
    competes,
    consecutive,
    entry,
    evidence_ref,
    gate,
    history,
    inhibitor,
    marker,
    mutate,
    open_,
    open_question,
    precondition,
    scope,
    state,
    stated,
    target,
    via_gate,
)

ROOT = Path(__file__).resolve().parents[2]
A, NA, U = MC.APPLICABLE, MC.NOT_APPLICABLE, MC.UNKNOWN


def cv_rows() -> list[dict[str, str]]:
    with open(ROOT / "registry" / "condition_variable_registry_v1.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def effect_rows() -> list[dict[str, str]]:
    with open(ROOT / "registry" / "effect_type_registry_draft_v1.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ----------------------------------------------------------------------------- module basics
def test_module_points_at_the_v1_1_schema_and_validates_fixtures() -> None:
    assert MC.MECH_SCHEMA_PATH.name == "MECH.draft_v1_1.schema.json"
    assert MC.SCHEMA_VERSION == "1.1.0-draft"
    assert (A, NA, U) == ("APPLICABLE", "NOT_APPLICABLE", "UNKNOWN")
    assert MC.schema_errors(accepted()) == []
    assert MC.schema_errors(entry(is_evidence=True))


def test_registry_readers_return_rows() -> None:
    assert {r["condition_variable_id"] for r in MC.read_cv_rows()} == {r["condition_variable_id"] for r in cv_rows()}
    assert len(MC.read_effect_rows()) == len(effect_rows())


# ----------------------------------------------------------------------------- semantic checks (v1 design, ported)
def test_semantic_checks_on_clean_fixtures() -> None:
    assert MC.semantic_problems(accepted(), cv_rows(), effect_rows=effect_rows()) == []
    ok = entry(gates_unknown=False, condition_gates=[gate(mn=stated(1.0), mx=stated(2.0), evidence_ids=["SRC-000001"],
                                                          rationale_raw="synthetic absence statement")],
               evidence_refs=[evidence_ref()])
    assert MC.semantic_problems(ok, cv_rows()) == []


def test_semantic_defects_are_found_on_schema_valid_fixtures() -> None:
    bad = {
        "duplicate gate_key": entry(gates_unknown=False, condition_gates=[gate(), gate(cv="CV-015", unit="aw")]),
        "E-7": entry(gates_unknown=False, condition_gates=[gate(mn=stated(1.0), mx=stated(2.0), evidence_ids=["SRC-000001"])],
                     evidence_refs=[evidence_ref("SRC-000001", "REVIEW_CONTEXT")]),
        "acts_on non-catalyst": entry(inhibitors_mitigators=[inhibitor("INH01"), inhibitor("INH02", acts_on_modifier_key="INH01")]),
        "catalyst through INHIBITING gate": entry(condition_gates=[cat_gate("INHIBITING")], inhibitors_mitigators=[
            inhibitor("INH01", "CATALYST", "SBO:0000013", "NOT_APPLICABLE", via_gate())]),
        "order": entry(gates_unknown=False, condition_gates=[gate(mn=stated(3.0), mx=stated(2.0), evidence_ids=["SRC-000001"])],
                       evidence_refs=[evidence_ref()]),
        "unit": entry(gates_unknown=False, condition_gates=[gate(unit="K")]),
        "unknown CV": entry(gates_unknown=False, condition_gates=[gate(cv="CV-999")]),
        "evidence not in refs": entry(gates_unknown=False, condition_gates=[gate(mn=stated(1.0), evidence_ids=["SRC-000009"])]),
        "inhibitor names a NECESSARY gate": entry(gates_unknown=False, condition_gates=[gate()],
                                                  inhibitors_mitigators=[inhibitor(via=via_gate())]),
        "categorical overlap": entry(condition_gates=[cat_gate(allowed=["x"], excluded=["x"], evidence_ids=["SRC-000001"])],
                                     evidence_refs=[evidence_ref()]),
        # v1.1
        "target class contradicts the effect type": entry(affected_targets=[target("LEACHED", ("DECREASE",), cls="SPECIES")]),
        "marker shared with itself": entry(markers=[marker(shared=("SYNTH_FIXTURE_ONE",))]),
        "duplicate question ref": entry(open_questions=[open_question(), dict(open_question(), topic_raw="second topic")]),
        "registry token without an approved registry": entry(affected_targets=[target(analyte_form={
            "status": "STATED", "text": "x", "token": "SYNTH_FORM_A", "token_status": "REGISTRY_TOKEN"})]),
    }
    for name, inst in bad.items():
        assert MC.schema_errors(inst) == [], f"{name}: fixture must be schema-valid (the defect is semantic)"
        assert MC.semantic_problems(inst, cv_rows(), effect_rows=effect_rows()), f"{name}: semantic defect not found"


def test_target_class_unknown_is_always_admitted_and_any_effect_admits_every_class() -> None:
    for e in (entry(affected_targets=[target("LEACHED", ("DECREASE",), shape="UNKNOWN", cls="UNKNOWN")]),
              entry(affected_targets=[target("UNKNOWN_TRANSFORMATION", ("UNKNOWN",), cls="OBSERVABLE", shape="UNKNOWN")]),
              entry(affected_targets=[target("DENATURED", ("UNKNOWN",), cls="STATE", shape="UNKNOWN")])):
        assert MC.schema_errors(e) == []
        assert MC.semantic_problems(e, cv_rows(), effect_rows=effect_rows()) == []


def test_registry_token_is_checked_against_an_approved_list_only_when_one_is_given() -> None:
    e = entry(affected_targets=[target(analyte_form={"status": "STATED", "text": "x", "token": "SYNTH_FORM_A",
                                                     "token_status": "REGISTRY_TOKEN"})])
    assert MC.semantic_problems(e, cv_rows(), analyte_form_tokens=frozenset({"SYNTH_FORM_A"})) == []
    assert MC.semantic_problems(e, cv_rows(), analyte_form_tokens=frozenset({"SYNTH_FORM_B"}))


def test_competition_and_consecutive_links_must_be_declared_on_both_sides() -> None:
    a = entry(mechanism_key="SYNTH_FIXTURE_ONE", competes_with=[competes()],
              consecutive_with=[consecutive("THIS_PRECEDES_OTHER")])
    b = entry(mechanism_key="SYNTH_FIXTURE_TWO")
    assert len(MC.asymmetric_links([a, b])) == 2
    b["competes_with"] = [competes(key="SYNTH_FIXTURE_ONE")]
    b["consecutive_with"] = [consecutive("OTHER_PRECEDES_THIS", key="SYNTH_FIXTURE_ONE")]
    assert MC.asymmetric_links([a, b]) == []


def test_links_to_keys_outside_the_registry_are_reported() -> None:
    a = entry(mechanism_key="SYNTH_FIXTURE_ONE", markers=[marker(shared=("SYNTH_FIXTURE_NINE",))],
              competes_with=[competes(key="SYNTH_FIXTURE_TWO")])
    b = entry(mechanism_key="SYNTH_FIXTURE_TWO", competes_with=[competes(key="SYNTH_FIXTURE_ONE")])
    assert MC.unresolved_links([a, b]) == [("markers", "SYNTH_FIXTURE_ONE", "SYNTH_FIXTURE_NINE")]
    assert MC.unresolved_links([a]) == [("competes_with", "SYNTH_FIXTURE_ONE", "SYNTH_FIXTURE_TWO"),
                                        ("markers", "SYNTH_FIXTURE_ONE", "SYNTH_FIXTURE_NINE")]


# ----------------------------------------------------------------------------- Step 22 / 23 read API
def test_required_condition_axes_include_every_gate_and_mark_modifier_gates() -> None:
    e = entry(condition_gates=[gate(key="CG01"), cat_gate("MODULATING", key="CG02")],
              inhibitors_mitigators=[inhibitor("INH01", "CATALYST", "SBO:0000013", "NOT_APPLICABLE", via_gate("CG02"))])
    axes = MC.required_condition_axes(e)
    assert [(x.cv_id, x.location, x.gate_key, x.gate_type, x.via) for x in axes] == [
        ("CV-013", "TISSUE", "CG01", "NECESSARY", "GATE"), ("CV-023", "MEDIUM", "CG02", "MODULATING", "MODIFIER_GATE")]
    assert all(isinstance(x, MC.AxisRequirement) for x in axes)


def test_required_state_inputs_collect_preconditions_history_and_inline_modifiers() -> None:
    inline = {"mode": "STATE_PREDICATE", "gate_key": None, "state_ref": state("synthetic_modifier_state"),
              "predicate": {"operator": "IS", "values": ["SYNTH_A"]}}
    e = entry(preconditions=[precondition()], history_dependence=[history("ACTIVE_UNTIL_STATE_CHANGE", "synthetic_enzyme_state")],
              inhibitors_mitigators=[inhibitor(via=inline)])
    got = [(s.state_key, s.source, s.item_key) for s in MC.required_state_inputs(e)]
    assert got == [("synthetic_state", "PRECONDITION", "PRE01"), ("synthetic_enzyme_state", "HISTORY", "ACTIVE_UNTIL_STATE_CHANGE"),
                   ("synthetic_modifier_state", "MODIFIER", "INH01")]


def test_candidate_effects_carry_signs_and_never_a_magnitude() -> None:
    e = entry(affected_targets=[target("LEACHED", ("DECREASE",), "TISSUE", key="TGT01", cls="TRANSFERRED_AMOUNT"),
                                target("LEACHED", ("INCREASE",), "COOKING_MEDIUM", key="TGT02", cls="TRANSFERRED_AMOUNT")])
    effs = MC.candidate_effects(e)
    assert [(c.target_key, c.compartment, c.allowed_directions) for c in effs] == [
        ("TGT01", "TISSUE", ("DECREASE",)), ("TGT02", "COOKING_MEDIUM", ("INCREASE",))]
    assert all(c.mechanism_key == "SYNTH_FIXTURE_ONE" and c.status == "CANDIDATE" for c in effs)
    assert not {"value", "magnitude", "rate", "extent"} & set(MC.CandidateEffect.__dataclass_fields__)


def test_only_accepted_entries_without_open_questions_are_consumable() -> None:
    ok, why = MC.consumable_for_applicability(accepted())
    assert ok and why == ()
    cases = {"NOT_ACCEPTED": entry(), "GATES_UNKNOWN": accepted(gates_unknown=True),
             "OPEN_QUESTIONS": accepted(open_questions=[open_question()]),
             "UNRESOLVED_SINK": accepted(kind="UNRESOLVED_SINK")}
    for reason, e in cases.items():
        ok, why = MC.consumable_for_applicability(e)
        assert not ok and reason in why, (reason, why)
    closed = accepted(open_questions=[open_question(status="CLOSED_BY_HUMAN_DECISION", decision="D-999")])
    assert MC.consumable_for_applicability(closed) == (True, ())


def test_module_is_pure_and_holds_no_chemistry() -> None:
    import re
    src = Path(MC.__file__).read_text(encoding="utf-8")
    assert not re.search(r"ascorb|chlorophyll|pheoph|vitamin", src, re.IGNORECASE)
    for banned in ("write_text", "write_bytes", "ledgers/data", "subprocess", "requests"):
        assert banned not in src, banned


# ----------------------------------------------------------------------------- three-valued reading (test-local reference)
def k3(vs: list[str | None]) -> str:
    vals = [v for v in vs if v is not None]
    return NA if NA in vals else (U if U in vals else A)


def side(b: dict[str, Any], x: float, lower: bool) -> str:
    if b["status"] == "NOT_REPORTED":
        return U
    if b["status"] == "OPEN_STATED":
        inside = (x >= b["value"] if lower else x <= b["value"]) if b["inclusive"] else (x > b["value"] if lower else x < b["value"])
        return A if inside else U
    ok = (x >= b["value"] if b["inclusive"] else x > b["value"]) if lower else (x <= b["value"] if b["inclusive"] else x < b["value"])
    return A if ok else NA


def window(g: dict[str, Any], x: float | None) -> str:
    return U if x is None else k3([side(g["interval"]["min"], x, True), side(g["interval"]["max"], x, False)])


def gate_verdict(g: dict[str, Any], x: float | None) -> str | None:
    if g["status"] != "ACCEPTED":
        return U
    if g["gate_type"] == "MODULATING":
        return None
    w = window(g, x)
    return w if g["gate_type"] == "NECESSARY" else {A: NA, NA: A, U: U}[w]


def pre_verdict(p: dict[str, Any], v: str | None) -> str:
    if p["status"] != "ACCEPTED" or v in (None, "UNKNOWN"):
        return U
    op, vals = p["predicate"]["operator"], p["predicate"]["values"]
    return A if {"IS": v in vals, "IN": v in vals, "IS_NOT": v not in vals, "NOT_IN": v not in vals,
                 "PRESENT": v == "PRESENT", "ABSENT": v == "ABSENT"}[op] else NA


def matrix_verdict(ms: dict[str, Any], m: str | None) -> str:
    if m is None:
        return U
    if m in {i["ref"] for i in ms["excluded"]}:
        return NA
    return A if m in {i["ref"] for i in ms["included"]} else U


def entry_verdict(e: dict[str, Any], q: dict[str, Any]) -> str:
    if not MC.consumable_for_applicability(e)[0]:
        return U
    parts: list[str | None] = [matrix_verdict(e["matrix_scope"], q.get("matrix"))]
    parts += [pre_verdict(p, q["states"].get(p["state_ref"]["state_key"])) for p in e["preconditions"]]
    parts += [gate_verdict(g, q["axes"].get(g["cv_id"])) for g in e["condition_gates"]]
    return k3(parts)


def test_k3_table_and_interval_bounds() -> None:
    assert k3([A, A]) == A and k3([A, U]) == U and k3([U, NA]) == NA and k3([]) == A
    g = gate(mn=stated(1.0), mx=bound(), status="ACCEPTED")
    assert window(g, 5.0) == U and window(g, 0.5) == NA and window(g, None) == U
    g2 = gate(mn=stated(1.0), mx=open_(10.0), status="ACCEPTED")
    assert window(g2, 10.0) == A and window(g2, 10.5) == U


def test_open_question_keeps_an_otherwise_applicable_entry_unknown() -> None:
    q = {"matrix": "synthetic class", "states": {"synthetic_state": "SYNTH_A"}, "axes": {"CV-013": 5.0}}
    e = accepted()
    assert entry_verdict(e, q) == A
    assert entry_verdict(mutate(e, lambda x: x.update(open_questions=[open_question()])), q) == U


def test_property_unknown_never_becomes_applicable() -> None:
    rng = random.Random(158)
    for _ in range(2000):
        mn = rng.choice([stated(rng.uniform(0, 5)), open_(rng.uniform(0, 5)), bound()])
        mx = rng.choice([stated(rng.uniform(5, 10)), open_(rng.uniform(5, 10)), bound()])
        g = gate(gtype=rng.choice(["NECESSARY", "INHIBITING", "MODULATING"]), mn=mn, mx=mx,
                 status=rng.choice(["ACCEPTED", "ACCEPTED", "CANDIDATE"]))
        p = precondition(status=rng.choice(["ACCEPTED", "CANDIDATE"]))
        e = accepted(gates_unknown=rng.choice([False, False, True]), preconditions=[p],
                     condition_gates=[g], matrix_scope=scope("FOOD_CLASS", inc=("m",), exc=("x",)),
                     open_questions=rng.choice([[], [], [open_question()]]))
        q = {"matrix": rng.choice(["m", "x", "z", None]), "axes": {"CV-013": rng.choice([None, rng.uniform(-1, 12)])},
             "states": {"synthetic_state": rng.choice(["SYNTH_A", "SYNTH_B", "UNKNOWN", None])}}
        v = entry_verdict(copy.deepcopy(e), q)
        if v == A:
            assert not e["open_questions"] and e["gates_unknown"] is False and q["matrix"] == "m"
            assert p["status"] == "ACCEPTED" and q["states"]["synthetic_state"] == "SYNTH_A" and g["status"] == "ACCEPTED"
        if v == NA:
            assert q["matrix"] == "x" or q["states"]["synthetic_state"] == "SYNTH_B" or q["axes"]["CV-013"] is not None
