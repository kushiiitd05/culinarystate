"""Contract test for the Step 21a MECH v1.1 DRAFT schema (S158, DRAFT_PENDING_H4).

Ported from the proposed (never committed) test in reports/step21/README.md section 5 and run against the
NEW file registry/schemas/MECH.draft_v1_1.schema.json; the v1 schema and the README stay unchanged.
Adds the v1.1 controls (round-3 items 21-12, 21-17, 21-19 and the D21-23 open-question guard).
Fixtures are SYNTHETIC SCHEMA FIXTURES (tests/fixtures/mech_v1_1_fixtures.py). Passing is evidence about the
draft's logic, not H4 approval, not a dual blind review and not a chemistry verdict.
"""
from __future__ import annotations

import csv
import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from tests.fixtures import mech_v1_1_fixtures as M
from tests.fixtures.mech_v1_1_fixtures import (
    accepted,
    bound,
    cat_gate,
    competes,
    consecutive,
    entry,
    enzyme_obj,
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
    sink,
    state,
    stated,
    target,
    via_gate,
)

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "registry"
SCHEMA = json.loads((REG / "schemas" / "MECH.draft_v1_1.schema.json").read_text(encoding="utf-8"))
SCHEMA_V1 = json.loads((REG / "schemas" / "MECH.draft_v1.schema.json").read_text(encoding="utf-8"))
VAL = Draft202012Validator({k: v for k, v in SCHEMA.items() if k != "$id"})
STATUS = "DRAFT_PENDING_H4"

# Every subtree in which v1.1 may differ from v1 (reports/step21/mechanism_ontology_v1_1_DRAFT_changes.md).
DECLARED_CHANGES = ("/$id", "/title", "/description", "/$comment", "/required", "/allOf", "/properties/open_questions",
                    "/$defs/open_question", "/$defs/affected_target/required",
                    "/$defs/affected_target/properties/target_class", "/$defs/affected_target/properties/analyte_form",
                    "/$defs/affected_target/allOf", "/$defs/marker/required",
                    "/$defs/marker/properties/sharing_status", "/$defs/marker/properties/shared_with_mechanism_keys",
                    "/$defs/marker/allOf", "/$defs/marker/description")


def read_csv(name: str) -> list[dict[str, str]]:
    with open(REG / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def flat_errors(instance: dict[str, Any]) -> list[str]:
    out: list[str] = []

    def walk(e: Any) -> None:
        out.append("/".join(map(str, e.absolute_path)) + " :: " + "/".join(map(str, e.absolute_schema_path))
                   + " :: " + e.message)
        for c in e.context or []:
            walk(c)

    for e in VAL.iter_errors(instance):
        walk(e)
    return out


def valid(instance: dict[str, Any]) -> bool:
    return not list(VAL.iter_errors(instance))


def walk_schema(node: Any, path: str = "") -> Iterator[tuple[str, dict[str, Any]]]:
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from walk_schema(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_schema(v, f"{path}/{i}")


def diff_paths(a: Any, b: Any, path: str = "") -> set[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out: set[str] = set()
        for k in set(a) | set(b):
            out |= {f"{path}/{k}"} if (k not in a or k not in b) else diff_paths(a[k], b[k], f"{path}/{k}")
        return out
    return set() if a == b else {path}


# ----------------------------------------------------------------------------- accepted variants (V-1..V-23 of v1, V-24.. new)
def accepted_variants() -> Iterator[tuple[str, dict[str, Any]]]:
    yield "V-1 minimal CANDIDATE, gates_unknown true", entry()
    yield "V-2 NECESSARY pH gate, every bound NOT_REPORTED", entry(gates_unknown=False, condition_gates=[gate()])
    yield "V-3 STATED min + OPEN_STATED max with evidence ids", entry(
        gates_unknown=False, evidence_refs=[evidence_ref()],
        condition_gates=[gate(mn=stated(1.0), mx=open_(10.0), evidence_ids=["SRC-000001"])])
    yield "V-4 core-temperature gate", entry(gates_unknown=False, condition_gates=[gate(cv="CV-008", unit="K", location="NOT_APPLICABLE")])
    yield "V-5 categorical INHIBITING gate alone, gates_unknown stays true", entry(
        evidence_refs=[evidence_ref()], condition_gates=[cat_gate(excluded=["synthetic agent"], evidence_ids=["SRC-000001"])])
    yield "V-6 time gate on the process clock", entry(
        gates_unknown=False, condition_gates=[gate(cv="CV-003", unit="s", location="NOT_APPLICABLE", clock="PROCESS_TAU")])
    yield "V-7 moisture gate with wet basis", entry(gates_unknown=False, condition_gates=[gate(cv="CV-016", unit="fraction", basis="WET_BASIS")])
    yield "V-8 precondition IS on a proposed history key", entry(gates_unknown=False, preconditions=[precondition()])
    yield "V-9 UNRESOLVED_SINK", sink()
    yield "V-10 fully specified ACCEPTED entry", accepted()
    yield "V-11 ENZYMATIC entry with an enzyme object", entry(kind="ENZYMATIC", enzyme=enzyme_obj())
    yield "V-12 label collision kept as REJECTED", entry(xrefs=[
        {"curie": "RXNO:0000207", "relation": "NOT_EQUIVALENT_COLLISION", "match_basis": "LABEL_MATCH_ONLY",
         "xref_status": "REJECTED", "verification_status": "HUMAN_REJECTED", "verified_by": "Parv",
         "collision_note": "synthetic: same label, different reaction"}])
    yield "V-13 inhibitor through an INHIBITING gate", entry(
        gates_unknown=False, preconditions=[precondition()], condition_gates=[cat_gate()],
        inhibitors_mitigators=[inhibitor(via=via_gate())])
    yield "V-14 competition and consecutive declarations", entry(competes_with=[competes()], consecutive_with=[consecutive()])
    yield "V-15 LEACHED tissue DECREASE and medium INCREASE", entry(affected_targets=[
        target("LEACHED", ("DECREASE",), "TISSUE", key="TGT01", cls="TRANSFERRED_AMOUNT"),
        target("LEACHED", ("INCREASE",), "COOKING_MEDIUM", key="TGT02", cls="TRANSFERRED_AMOUNT")])
    yield "V-16 FORMED peak then decline", entry(affected_targets=[target("FORMED", ("INCREASE", "DECREASE"), "TISSUE", "PEAK_THEN_DECLINE")])
    yield "V-17 direction exactly [UNKNOWN]", entry(affected_targets=[target("UNKNOWN_TRANSFORMATION", ("UNKNOWN",))])
    yield "V-18 matrix scope MODEL_SYSTEM", entry(matrix_scope=scope("MODEL_SYSTEM", inc=("synthetic model system",)))
    yield "V-19 VOLATILIZED from the whole system, DECREASE", entry(affected_targets=[target("VOLATILIZED", ("DECREASE",), "WHOLE_SYSTEM")])
    yield "V-20 VOLATILIZED in the medium, no direction rule", entry(affected_targets=[target("VOLATILIZED", ("DECREASE",), "COOKING_MEDIUM")])
    yield "V-21 catalyst through a MODULATING gate, chelator acting on it", entry(
        condition_gates=[cat_gate("MODULATING")],
        inhibitors_mitigators=[inhibitor("INH01", "CATALYST", "SBO:0000013", "NOT_APPLICABLE", via_gate()),
                               inhibitor("INH02", acts_on_modifier_key="INH01")])
    yield "V-22 OXIDIZED substrate falls, product rises", entry(affected_targets=[
        target("OXIDIZED", ("DECREASE",), role="SUBSTRATE", key="TGT01"), target("OXIDIZED", ("INCREASE",), role="PRODUCT", key="TGT02")])
    yield "V-23 coupled-redox competition and a start-mode history item", entry(
        competes_with=[competes("COUPLED_REDOX")], history_dependence=[history("INPUT_REQUIRED_START_MODE", "synthetic_start_mode")])
    # ---- v1.1
    yield "V-24 stated analyte form, no approved token registry", entry(affected_targets=[target(analyte_form={
        "status": "STATED", "text": "synthetic form", "token": None, "token_status": "NO_APPROVED_REGISTRY"})])
    yield "V-25 analyte form with a registry token (list itself open, EQ21-06)", entry(affected_targets=[target(analyte_form={
        "status": "STATED", "text": "synthetic form", "token": "SYNTH_FORM_A", "token_status": "REGISTRY_TOKEN"})])
    yield "V-26 observable target with shape UNKNOWN and no evidence", entry(affected_targets=[target(
        "UNKNOWN_TRANSFORMATION", ("UNKNOWN",), shape="UNKNOWN", cls="OBSERVABLE")])
    yield "V-27 observable target, MONOTONIC with an evidence id", entry(evidence_refs=[evidence_ref(supports=("TARGET_EFFECT",))],
        affected_targets=[target("STRUCTURE_ALTERED", ("DECREASE",), cls="OBSERVABLE", evidence_ids=["SRC-000001"])])
    yield "V-28 observable target PEAK_THEN_DECLINE without evidence", entry(affected_targets=[target(
        "STRUCTURE_ALTERED", ("INCREASE", "DECREASE"), shape="PEAK_THEN_DECLINE", cls="OBSERVABLE")])
    yield "V-29 marker declared as shared with another entry", entry(markers=[marker(shared=("SYNTH_FIXTURE_TWO",))])
    yield "V-30 marker whose sharing was not assessed", entry(markers=[marker()])
    yield "V-31 CANDIDATE with an OPEN expert question", entry(open_questions=[open_question()])
    yield "V-32 expert answer recorded, pending human review", entry(open_questions=[
        open_question(status="EXPERT_ANSWER_RECORDED_PENDING_HUMAN_REVIEW", answer="synthetic answer locator")])
    yield "V-33 ACCEPTED entry whose question was closed by a human decision", accepted(open_questions=[
        open_question(status="CLOSED_BY_HUMAN_DECISION", decision="D-999")])


def test_accepted_variants_validate() -> None:
    for name, inst in accepted_variants():
        assert valid(inst), f"{name} should validate: {flat_errors(inst)[:3]}"


# ----------------------------------------------------------------------------- negative controls
def negatives() -> list[tuple[str, dict[str, Any], str]]:
    b = entry(gates_unknown=False, condition_gates=[gate(mn=stated(1.0), mx=open_(10.0), evidence_ids=["SRC-000001"])],
              evidence_refs=[evidence_ref()])
    acc = accepted()
    ine = inhibitor()
    g0 = lambda **kw: mutate(b, lambda x: x["condition_gates"][0].update(**kw))
    return [
        ("N-1 no precondition, no gate, gates_unknown false", entry(gates_unknown=False), r"anyOf|minItems"),
        ("N-2 missing_input_verdict APPLICABLE on a gate", g0(missing_input_verdict="APPLICABLE"), r"missing_input_verdict"),
        ("N-3 missing_input_verdict APPLICABLE on a precondition", entry(gates_unknown=False, preconditions=[dict(precondition(), missing_input_verdict="APPLICABLE")]), r"missing_input_verdict"),
        ("N-4 bare null as an interval bound", mutate(b, lambda x: x["condition_gates"][0]["interval"].update(min=None)), r"interval/min"),
        ("N-5 STATED bound without a value", mutate(b, lambda x: x["condition_gates"][0]["interval"].update(min=bound("STATED", None, True))), r"interval/min"),
        ("N-6 OPEN_STATED bound without the studied extreme", mutate(b, lambda x: x["condition_gates"][0]["interval"].update(max=bound("OPEN_STATED"))), r"interval/max"),
        ("N-7 STATED bound without evidence ids", g0(evidence_ids=[]), r"evidence_ids"),
        ("N-8 numeric kinetic key on the entry", entry(k_ref=1.0), r"k_ref|Additional properties"),
        ("N-9 numeric kinetic key on a gate", g0(activation_energy=1.0), r"activation_energy|Additional properties"),
        ("N-10 default value key on a gate", g0(default=1.0), r"default|Additional properties"),
        ("N-11 marker_unique true", entry(markers=[dict(marker(), marker_unique=True)]), r"marker_unique"),
        ("N-12 gate on CV-009", g0(cv_id="CV-009", location="NOT_APPLICABLE"), r"cv_id|not"),
        ("N-12b gate on CV-010", g0(cv_id="CV-010", location="NOT_APPLICABLE"), r"cv_id|not"),
        ("N-12c gate on CV-004", g0(cv_id="CV-004", location="NOT_APPLICABLE"), r"cv_id|not"),
        ("N-13 temperature gate that repeats a location", g0(cv_id="CV-008", location="TISSUE"), r"location"),
        ("N-14 pH gate with location NOT_APPLICABLE", g0(location="NOT_APPLICABLE"), r"location"),
        ("N-15 moisture gate without a basis", g0(cv_id="CV-016"), r"basis"),
        ("N-16 basis on a non-moisture gate", g0(basis="WET_BASIS"), r"basis"),
        ("N-17 time gate without the process clock", g0(cv_id="CV-003", location="NOT_APPLICABLE"), r"clock"),
        ("N-18 clock on a non-time gate", g0(clock="PROCESS_TAU"), r"clock"),
        ("N-19 categorical gate that carries an interval", g0(domain_kind="CATEGORICAL_SET"), r"categories|interval"),
        ("N-20 MODULATING gate with modulates NOT_APPLICABLE", g0(gate_type="MODULATING", modulates="NOT_APPLICABLE"), r"modulates"),
        ("N-21 NECESSARY gate with modulates RATE", g0(modulates="RATE"), r"modulates"),
        ("N-22 ACCEPTED gate with location UNKNOWN", mutate(acc, lambda x: x["condition_gates"][0].update(location="UNKNOWN")), r"location"),
        ("N-23 ACCEPTED entry without HUMAN_VERIFIED", mutate(acc, lambda x: x["verification"].update(status="AI_PRECHECKED", verifier=None, verified_at=None)), r"verification"),
        ("N-24 ACCEPTED entry with only REVIEW_CONTEXT evidence", mutate(acc, lambda x: x["evidence_refs"][0].update(doc_type="REVIEW_CONTEXT")), r"evidence_refs|contains"),
        ("N-25 ACCEPTED entry reviewed by one person", mutate(acc, lambda x: x["review"].update(reviewer_ids=["Kush"])), r"reviewer_ids|minItems"),
        ("N-26 ACCEPTED entry with invalid review provenance", mutate(acc, lambda x: x["review"].update(review_provenance_valid="INVALID")), r"review_provenance_valid"),
        ("N-27 HUMAN_VERIFIED by someone else", mutate(acc, lambda x: x["verification"].update(verifier="Someone")), r"verifier"),
        ("N-28 ENZYMATIC entry without an enzyme", entry(kind="ENZYMATIC"), r"enzyme"),
        ("N-29 non-ENZYMATIC entry with an enzyme", entry(enzyme=enzyme_obj()), r"enzyme"),
        ("N-30 sink with a participant", sink(participants=[{"role_label": "x", "entity": {"ref_type": "CLASS_LABEL", "ref": "x", "label_raw": "x"}, "sbo_role": "UNKNOWN"}]), r"participants"),
        ("N-31 sink with gates_unknown false", sink(gates_unknown=False), r"gates_unknown"),
        ("N-32 sink with an affected target", sink(affected_targets=[target()]), r"affected_targets"),
        ("N-33 non-sink without an affected target", entry(affected_targets=[]), r"affected_targets|minItems"),
        ("N-34 is_evidence true", entry(is_evidence=True), r"is_evidence"),
        ("N-35 ACCEPTED xref without human verification", entry(xrefs=[{"curie": "GO:0000001", "relation": "EXACT", "match_basis": "LABEL_MATCH_ONLY", "xref_status": "ACCEPTED", "verification_status": "UNVERIFIED", "verified_by": None, "collision_note": None}]), r"verification_status|verified_by"),
        ("N-36 collision xref that is not REJECTED", entry(xrefs=[{"curie": "RXNO:0000207", "relation": "NOT_EQUIVALENT_COLLISION", "match_basis": "LABEL_MATCH_ONLY", "xref_status": "PROPOSED", "verification_status": "UNVERIFIED", "verified_by": None, "collision_note": "x"}]), r"xref_status"),
        ("N-37 undocumented inhibitor with gates_unknown false", entry(gates_unknown=False, preconditions=[precondition()], inhibitors_mitigators=[ine]), r"gates_unknown"),
        ("N-38 FORMED target that can only DECREASE", entry(affected_targets=[target("FORMED", ("DECREASE",))]), r"allowed_directions"),
        ("N-39 DEGRADED target that can INCREASE", entry(affected_targets=[target("DEGRADED", ("INCREASE",))]), r"allowed_directions"),
        ("N-40 UNKNOWN direction mixed with INCREASE", entry(affected_targets=[target("UNKNOWN_TRANSFORMATION", ("UNKNOWN", "INCREASE"))]), r"allowed_directions|maxItems"),
        ("N-41 LEACHED from the whole system", entry(affected_targets=[target("LEACHED", ("DECREASE",), "WHOLE_SYSTEM")]), r"compartment"),
        ("N-42 LEACHED into the medium as DECREASE", entry(affected_targets=[target("LEACHED", ("DECREASE",), "COOKING_MEDIUM")]), r"allowed_directions"),
        ("N-43 ABSORBED into the tissue as DECREASE", entry(affected_targets=[target("ABSORBED", ("DECREASE",), "TISSUE")]), r"allowed_directions"),
        ("N-44 effect type outside the registry (RETAINED)", entry(affected_targets=[target("RETAINED", ("INCREASE",))]), r"effect_type"),
        ("N-45 evidence id that is a sealed case id", entry(evidence_refs=[dict(evidence_ref(), evidence_id="CASE-000001")]), r"evidence_id"),
        ("N-46 PRIMARY evidence without a locator", entry(evidence_refs=[dict(evidence_ref(), locator=None)]), r"locator"),
        ("N-47 lineage root without PRESENT status", entry(evidence_refs=[dict(evidence_ref(), lineage_root_id="LROOT-000001")]), r"lineage_root_id"),
        ("N-48 predicate with UNKNOWN as a satisfying value", entry(gates_unknown=False, preconditions=[precondition(values=("UNKNOWN",))]), r"values"),
        ("N-49 PRESENT predicate carrying values", entry(gates_unknown=False, preconditions=[precondition(op="PRESENT", values=("X",))]), r"values|maxItems"),
        ("N-50 IN predicate with one value", entry(gates_unknown=False, preconditions=[precondition(op="IN", values=("X",))]), r"values|minItems"),
        ("N-51 state ref with both svar id and key", entry(gates_unknown=False, preconditions=[dict(precondition(), state_ref={"ref_status": "PROPOSED_KEY", "svar_id": "SVAR-000001", "state_key": "x_y_z", "label_raw": "x"})]), r"svar_id|state_ref"),
        ("N-52 FOOD_CLASS scope without an included matrix", entry(matrix_scope=scope("FOOD_CLASS")), r"included|minItems"),
        ("N-53 unlisted matrix verdict APPLICABLE", entry(matrix_scope=dict(scope(), unlisted_verdict="APPLICABLE")), r"unlisted_verdict"),
        ("N-54 mechanism key in lower case", entry(mechanism_key="lower_case"), r"mechanism_key"),
        ("N-55 id outside the MECH pattern", entry(id="MECH-UNRESOLVED_LOSS"), r"/id|id "),
        ("N-56 EXTERNAL_VERIFIED on an unverified entry", entry(provenance_class="EXTERNAL_VERIFIED"), r"verification|provenance_class"),
        ("N-57 derivation anchors missing", entry(derivation_anchors=[]), r"derivation_anchors|minItems"),
        ("N-58 competes_with without a shared target", entry(competes_with=[{k: v for k, v in competes().items() if k != "shared_target"}]), r"shared_target|required"),
        ("N-59 UNKNOWN as an allowed category", entry(condition_gates=[cat_gate(allowed=["UNKNOWN"])]), r"allowed"),
        ("N-60 Unknown (mixed case) as an allowed category", entry(condition_gates=[cat_gate(allowed=["Unknown"])]), r"allowed"),
        ("N-61 unknown as an excluded category", entry(condition_gates=[cat_gate(excluded=["unknown"])]), r"excluded"),
        ("N-62 unknown as a predicate value", entry(gates_unknown=False, preconditions=[precondition(values=("unknown",))]), r"values"),
        ("N-63 ACCEPTED precondition without evidence", entry(preconditions=[precondition(status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-64 ACCEPTED competes_with without evidence", entry(competes_with=[dict(competes(), status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-65 ACCEPTED consecutive_with without evidence", entry(consecutive_with=[dict(consecutive(), status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-66 ACCEPTED affected_target without evidence", entry(affected_targets=[dict(target(), status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-67 ACCEPTED marker without evidence", entry(markers=[dict(marker(), status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-68 ACCEPTED history item without evidence", entry(history_dependence=[dict(history(), status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-69 lone MODULATING gate with gates_unknown false", entry(gates_unknown=False, condition_gates=[gate(gtype="MODULATING")]), r"anyOf|contains|minItems"),
        ("N-70 lone INHIBITING gate with gates_unknown false", entry(gates_unknown=False, condition_gates=[cat_gate()]), r"anyOf|contains|minItems"),
        ("N-71 VOLATILIZED from the whole system as INCREASE", entry(affected_targets=[target("VOLATILIZED", ("INCREASE",), "WHOLE_SYSTEM")]), r"allowed_directions"),
        ("N-72 ABSORBED into the whole system", entry(affected_targets=[target("ABSORBED", ("INCREASE",), "WHOLE_SYSTEM")]), r"compartment"),
        ("N-73 OXIDIZED substrate that increases", entry(affected_targets=[target("OXIDIZED", ("INCREASE",), role="SUBSTRATE")]), r"allowed_directions"),
        ("N-74 OXIDIZED product that can only decrease", entry(affected_targets=[target("OXIDIZED", ("DECREASE",), role="PRODUCT")]), r"allowed_directions"),
        ("N-75 old-style gate key G1", entry(gates_unknown=False, condition_gates=[gate(key="G1")]), r"gate_key"),
        ("N-76 old-style target key T1", entry(affected_targets=[target(key="T1")]), r"target_key"),
        ("N-77 old-style inhibitor key I1", entry(inhibitors_mitigators=[inhibitor("I1")]), r"inhibitor_key"),
        ("N-78 CV-021 headspace oxygen with location MEDIUM", entry(gates_unknown=False, condition_gates=[gate(cv="CV-021", unit="fraction", location="MEDIUM")]), r"location"),
        ("N-79 interval that still carries an optimum", mutate(b, lambda x: x["condition_gates"][0]["interval"].update(opt=bound())), r"opt|Additional properties"),
        ("N-80 xref in a namespace that is not admitted (MESH)", entry(xrefs=[{"curie": "MESH:D000001", "relation": "RELATED", "match_basis": "AI_PROPOSED", "xref_status": "PROPOSED", "verification_status": "UNVERIFIED", "verified_by": None, "collision_note": None}]), r"curie"),
        ("N-81 catalyst with a COMPLETE extent", entry(inhibitors_mitigators=[inhibitor(role="CATALYST", sbo="SBO:0000013", extent="COMPLETE")]), r"extent"),
        ("N-82 catalyst carrying the inhibitor SBO role", entry(inhibitors_mitigators=[inhibitor(role="CATALYST", extent="NOT_APPLICABLE")]), r"sbo_role"),
        ("N-83 catalyst that points at another modifier", entry(inhibitors_mitigators=[inhibitor(role="CATALYST", sbo="SBO:0000013", extent="NOT_APPLICABLE", acts_on_modifier_key="INH02")]), r"role"),
        ("N-84 inhibitor with extent NOT_APPLICABLE", entry(inhibitors_mitigators=[inhibitor(extent="NOT_APPLICABLE")]), r"extent"),
        ("N-85 affected target without target_role", entry(affected_targets=[{k: v for k, v in target().items() if k != "target_role"}]), r"target_role|required"),
        # ---- v1.1 controls
        ("N-86 affected target without target_class", entry(affected_targets=[{k: v for k, v in target().items() if k != "target_class"}]), r"target_class|required"),
        ("N-87 target_class outside the vocabulary", entry(affected_targets=[target(cls="COLOUR")]), r"target_class"),
        ("N-88 observable MONOTONIC without evidence (21-17)", entry(affected_targets=[target("STRUCTURE_ALTERED", ("DECREASE",), cls="OBSERVABLE")]), r"evidence_ids|minItems"),
        ("N-89 UNKNOWN-class MONOTONIC without evidence", entry(affected_targets=[target(cls="UNKNOWN")]), r"evidence_ids|minItems"),
        ("N-90 analyte form without token_status", entry(affected_targets=[target(analyte_form={"status": "NOT_REPORTED", "text": None, "token": None})]), r"token_status|required"),
        ("N-91 token without an approved registry", entry(affected_targets=[target(analyte_form={"status": "STATED", "text": "x", "token": "SYNTH_A", "token_status": "NO_APPROVED_REGISTRY"})]), r"token"),
        ("N-92 UNKNOWN as a token", entry(affected_targets=[target(analyte_form={"status": "STATED", "text": "x", "token": "UNKNOWN", "token_status": "REGISTRY_TOKEN"})]), r"token"),
        ("N-93 REGISTRY_TOKEN without a token", entry(affected_targets=[target(analyte_form={"status": "STATED", "text": "x", "token": None, "token_status": "REGISTRY_TOKEN"})]), r"token"),
        ("N-94 token on a form that was not reported", entry(affected_targets=[target(analyte_form={"status": "NOT_REPORTED", "text": None, "token": "SYNTH_A", "token_status": "REGISTRY_TOKEN"})]), r"token"),
        ("N-95 marker SHARED_DECLARED without partner keys", entry(markers=[dict(marker(), sharing_status="SHARED_DECLARED")]), r"shared_with_mechanism_keys|minItems"),
        ("N-96 marker NOT_ASSESSED with partner keys", entry(markers=[dict(marker(), shared_with_mechanism_keys=["SYNTH_FIXTURE_TWO"])]), r"shared_with_mechanism_keys|maxItems"),
        ("N-97 marker sharing 'none' (absence of sharing would read as uniqueness)", entry(markers=[dict(marker(), sharing_status="NOT_SHARED")]), r"sharing_status"),
        ("N-98 marker partner key in lower case", entry(markers=[marker(shared=("lower_key",))]), r"shared_with_mechanism_keys"),
        ("N-99 ACCEPTED entry with an OPEN expert question (D21-23)", accepted(open_questions=[open_question()]), r"open_questions|status"),
        ("N-100 ACCEPTED entry whose answer awaits human review", accepted(open_questions=[open_question(status="EXPERT_ANSWER_RECORDED_PENDING_HUMAN_REVIEW", answer="x")]), r"open_questions|status"),
        ("N-101 question closed without a decision id", entry(open_questions=[open_question(status="CLOSED_BY_HUMAN_DECISION")]), r"decision_ref"),
        ("N-102 expert answer without its locator", entry(open_questions=[open_question(status="EXPERT_ANSWER_RECORDED_PENDING_HUMAN_REVIEW")]), r"answer_locator"),
        ("N-103 question ref outside the EQ21 pattern", entry(open_questions=[open_question(ref="Q1")]), r"question_ref"),
        ("N-104 open_questions key missing", {k: v for k, v in entry().items() if k != "open_questions"}, r"open_questions|required"),
    ]


def test_negative_controls_rejected_for_the_intended_reason() -> None:
    cases = negatives()
    assert len({n for n, _, _ in cases}) == len(cases)
    for name, inst, why in cases:
        errs = flat_errors(inst)
        assert errs, f"{name} was ACCEPTED but must be rejected"
        assert any(re.search(why, e) for e in errs), f"{name}: rejected, but not for /{why}/: {errs[:4]}"


# ----------------------------------------------------------------------------- structure
FORBIDDEN_NAMES = {"k", "k_ref", "ln_k_ref", "ea", "e_a", "activation_energy", "a_factor", "pre_exponential", "arrhenius",
                   "q10", "half_life", "d_value", "z_value", "rate_constant", "reaction_order", "order_of_reaction",
                   "t_ref", "tref", "kinetic_parameter", "k_value"}


def test_schema_is_a_valid_2020_12_draft_marked_v1_1() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA["$schema"].endswith("2020-12/schema")
    assert SCHEMA["$id"] == "culinarystate/draft/MECH.draft_v1_1.schema.json"
    assert "DRAFT_PENDING_H4" in SCHEMA["title"]
    assert SCHEMA["description"].startswith("schema_version 1.1.0-draft. STATUS DRAFT_PENDING_H4")
    for r in (n["$ref"] for _, n in walk_schema(SCHEMA) if isinstance(n.get("$ref"), str)):
        assert r.startswith("#/$defs/") and r.split("/")[-1] in SCHEMA["$defs"], r


def test_v1_1_differs_from_v1_only_inside_the_declared_subtrees() -> None:
    assert SCHEMA_V1["description"].startswith("schema_version 1.0.0-draft"), "v1 must stay as it was"
    diffs = diff_paths(SCHEMA_V1, SCHEMA)
    stray = {d for d in diffs if not any(d == c or d.startswith(c + "/") for c in DECLARED_CHANGES)}
    assert not stray, stray
    unused = {c for c in DECLARED_CHANGES if not any(d == c or d.startswith(c + "/") for d in diffs)}
    assert not unused, unused
    assert set(SCHEMA_V1["required"]) | {"open_questions"} == set(SCHEMA["required"])


def test_no_additional_properties_anywhere_and_no_default_keyword() -> None:
    for p, n in walk_schema(SCHEMA):
        if "properties" in n and n.get("type") == "object" and not re.search(r"/(if|contains|not)(/|$)", p):
            assert n.get("additionalProperties") is False, f"open object at {p}"
        assert "default" not in n, f"'default' keyword at {p}"


def test_no_kinetic_parameter_names_in_the_schema() -> None:
    names: set[str] = set()
    for _, n in walk_schema(SCHEMA):
        if isinstance(n.get("properties"), dict):
            names |= {k.lower() for k in n["properties"]}
    assert not (names & FORBIDDEN_NAMES), names & FORBIDDEN_NAMES


def test_r15_constants_are_in_the_schema() -> None:
    d = SCHEMA["$defs"]
    assert d["missing_input_verdict"]["const"] == "UNKNOWN"
    assert SCHEMA["properties"]["is_evidence"]["const"] is False
    assert d["marker"]["properties"]["marker_unique"]["const"] is False
    for k in ("precondition", "condition_gate", "inhibitor"):
        assert d[k]["properties"]["missing_input_verdict"] == {"$ref": "#/$defs/missing_input_verdict"}
    assert "opt" not in d["interval"]["properties"] and "opt_bound" not in d
    for k in ("precondition", "competes_with", "consecutive_with", "affected_target", "marker", "history_item",
              "condition_gate", "inhibitor"):
        rules = [json.dumps(x) for x in d[k].get("allOf", [])]
        assert any('"ACCEPTED"' in r and '"evidence_ids": {"minItems": 1}' in r for r in rules), f"{k}: ACCEPTED needs evidence"
    assert "NOT_SHARED" not in json.dumps(d["marker"]), "absence of sharing is never recorded as a fact"


def test_prefix_is_free_in_the_python_registry() -> None:
    p = ROOT / "src" / "culinarystate" / "ledgers" / "registry.py"
    assert not re.search(r'_add\("MECH"', p.read_text(encoding="utf-8")), "MECH already registered"


def test_r14_schema_names_neither_candidate_system_and_holds_no_token_list() -> None:
    text = json.dumps(SCHEMA)
    assert "SIM-AA" not in text and "SIM-CHL" not in text
    assert not re.search(r"ascorb|chlorophyll|pheoph|vitamin c", text, re.IGNORECASE)
    af = SCHEMA["$defs"]["affected_target"]["properties"]["analyte_form"]
    assert "enum" not in json.dumps(af["properties"]["token"]), "the token list is an expert question, not schema content"


# ----------------------------------------------------------------------------- vocabularies (CSVs unchanged, read-only)
def test_vocabulary_rows_are_draft_sourced_and_unique() -> None:
    spec = {"mechanism_seed_roster_draft_v1.csv": ("mechanism_key", "source_anchors"),
            "effect_type_registry_draft_v1.csv": ("effect_type", "source"),
            "condition_gate_type_registry_draft_v1.csv": ("gate_type", "source")}
    for name, (key, src) in spec.items():
        rows = read_csv(name)
        assert rows and len({r[key] for r in rows}) == len(rows), name
        for r in rows:
            assert r["registry_status"] == STATUS and r[src].strip() and r["ai_drafted"] in ("TRUE", "FALSE"), (name, r[key])


def test_effect_types_match_schema_and_rxn_enum() -> None:
    rows = read_csv("effect_type_registry_draft_v1.csv")
    assert {r["effect_type"] for r in rows} == set(SCHEMA["$defs"]["affected_target"]["properties"]["effect_type"]["enum"])
    rxn = json.loads((ROOT / "ledgers" / "schemas" / "RXN.schema.json").read_text(encoding="utf-8"))
    aligned = {r["rxn_relation"] for r in rows if r["origin"] == "ALIGNED_RXN"}
    assert set(rxn["properties"]["relation"]["enum"]) - aligned == {"RETAINED"}


def test_target_class_vocabulary_covers_the_effect_csv_classes() -> None:
    classes = set(SCHEMA["$defs"]["affected_target"]["properties"]["target_class"]["enum"])
    assert classes == {"SPECIES", "TRANSFERRED_AMOUNT", "OBSERVABLE", "STATE", "UNKNOWN"}
    csv_classes = {r["target_class"] for r in read_csv("effect_type_registry_draft_v1.csv")}
    expand = {"OBSERVABLE_OR_STATE": {"OBSERVABLE", "STATE"}, "ANY": classes - {"UNKNOWN"}}
    assert set().union(*(expand.get(c, {c}) for c in csv_classes)) <= classes


def test_direction_rules_in_the_effect_csv_match_the_schema() -> None:
    rows = {r["effect_type"]: r["direction_rule"] for r in read_csv("effect_type_registry_draft_v1.csv")}
    table = [("LEACHED", "TISSUE", ("DECREASE",), True, "compartment TISSUE: DECREASE only"),
             ("LEACHED", "COOKING_MEDIUM", ("DECREASE",), False, None),
             ("LEACHED", "WHOLE_SYSTEM", ("DECREASE",), False, "WHOLE_SYSTEM is not admitted"),
             ("VOLATILIZED", "COOKING_MEDIUM", ("INCREASE",), True, "compartment COOKING_MEDIUM: no direction rule"),
             ("VOLATILIZED", "WHOLE_SYSTEM", ("DECREASE",), True, "compartment WHOLE_SYSTEM: DECREASE only"),
             ("VOLATILIZED", "WHOLE_SYSTEM", ("INCREASE",), False, None),
             ("ABSORBED", "TISSUE", ("INCREASE",), True, "compartment TISSUE: INCREASE only"),
             ("ABSORBED", "WHOLE_SYSTEM", ("INCREASE",), False, "WHOLE_SYSTEM is not admitted")]
    for eff, comp, dirs, ok, phrase in table:
        assert valid(entry(affected_targets=[target(eff, dirs, comp, cls="TRANSFERRED_AMOUNT")])) == ok, (eff, comp, dirs)
        if phrase:
            assert phrase in rows[eff], (eff, phrase)


def test_roster_uses_only_schema_vocabulary() -> None:
    top, effects = SCHEMA["properties"], set(SCHEMA["$defs"]["affected_target"]["properties"]["effect_type"]["enum"])
    key_re = re.compile(top["mechanism_key"]["pattern"])
    for r in read_csv("mechanism_seed_roster_draft_v1.csv"):
        assert key_re.match(r["mechanism_key"]) and r["kind"] in top["kind"]["enum"], r["mechanism_key"]
        assert r["family"] in top["family"]["enum"] and r["edge_semantics_proposed"] in top["edge_semantics"]["enum"]
        assert set(filter(None, r["typical_effect_types"].split(";"))) <= effects, r["mechanism_key"]
        assert r["entry_status"] == "SEED_NOT_YET_AUTHORED"


def test_every_roster_open_question_has_an_expert_question() -> None:
    """Each roster row whose open_issue says OPEN_QUESTION is listed in S158_expert_questions.md."""
    text = (ROOT / "reports" / "step21" / "S158_expert_questions.md").read_text(encoding="utf-8")
    for r in read_csv("mechanism_seed_roster_draft_v1.csv"):
        if "OPEN_QUESTION" in r["open_issue"]:
            assert f"`{r['mechanism_key']}`" in text, r["mechanism_key"]
    assert len(set(re.findall(r"^### (EQ21-\d{2})\b", text, re.MULTILINE))) >= 10
    pattern = SCHEMA["$defs"]["open_question"]["properties"]["question_ref"]["pattern"]
    assert all(re.match(pattern, q) for q in re.findall(r"^### (EQ21-\d{2})\b", text, re.MULTILINE))


def test_fixture_module_is_synthetic() -> None:
    assert M.SCHEMA_VERSION == "1.1.0-draft"
    assert state()["ref_status"] == "PROPOSED_KEY"
