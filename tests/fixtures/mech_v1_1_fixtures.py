"""SYNTHETIC SCHEMA FIXTURES for the Step 21a MECH v1.1 DRAFT contract (S158, DRAFT_PENDING_H4).

Ported from the proposed contract test in reports/step21/README.md section 5 (v1) and extended with the
v1.1 keys (affected_target.target_class, analyte_form token slot, marker sharing, entry open_questions).
Structure only: placeholder strings and dummy bounds (1.0, 10.0 ...), never scientific data; no entry here
describes a real mechanism.
"""
from __future__ import annotations

import copy
from collections.abc import Callable, Iterable
from typing import Any

NOW = "2026-11-03T00:00:00+00:00"
SCHEMA_VERSION = "1.1.0-draft"
AF_NR: dict[str, Any] = {"status": "NOT_REPORTED", "text": None, "token": None, "token_status": "NOT_APPLICABLE"}


def mutate(base: dict[str, Any], fn: Callable[[dict[str, Any]], Any]) -> dict[str, Any]:
    x = copy.deepcopy(base)
    fn(x)
    return x


def state(key: str = "synthetic_state") -> dict[str, Any]:
    return {"ref_status": "PROPOSED_KEY", "svar_id": None, "state_key": key, "label_raw": "synthetic " + key}


def scope(kind: str = "UNKNOWN", inc: Iterable[str] = (), exc: Iterable[str] = ()) -> dict[str, Any]:
    def item(r: str) -> dict[str, Any]:
        return {"ref_type": "CLASS_LABEL", "ref": r, "label_raw": r}
    return {"scope_kind": kind, "included": [item(r) for r in inc], "excluded": [item(r) for r in exc],
            "unlisted_verdict": "UNKNOWN", "note_raw": None}


def target(effect: str = "DEGRADED", dirs: Iterable[str] = ("DECREASE",), comp: str = "TISSUE", shape: str = "MONOTONIC",
           key: str = "TGT01", role: str = "UNKNOWN", cls: str = "SPECIES", **over: Any) -> dict[str, Any]:
    t = {"target_key": key, "target": state("synthetic_target"), "target_role": role, "target_class": cls,
         "analyte_form": dict(AF_NR), "compartment": comp, "effect_type": effect, "allowed_directions": list(dirs),
         "trajectory_shape": shape, "evidence_ids": [], "status": "CANDIDATE"}
    t.update(over)
    return t


def bound(status: str = "NOT_REPORTED", value: float | None = None, inclusive: bool | None = None) -> dict[str, Any]:
    return {"status": status, "value": value, "inclusive": inclusive}


def stated(v: float, inclusive: bool = True) -> dict[str, Any]:
    return bound("STATED", v, inclusive)


def open_(v: float, inclusive: bool = True) -> dict[str, Any]:
    """OPEN_STATED: not limited on this side within the studied range; v is the studied extreme (required)."""
    return bound("OPEN_STATED", v, inclusive)


def gate(cv: str = "CV-013", gtype: str = "NECESSARY", mn: dict[str, Any] | None = None, mx: dict[str, Any] | None = None,
         unit: str = "pH", key: str = "CG01", status: str = "CANDIDATE", **over: Any) -> dict[str, Any]:
    g = {"gate_key": key, "gate_type": gtype, "cv_id": cv, "location": "TISSUE", "basis": "NOT_APPLICABLE",
         "clock": "NOT_APPLICABLE", "domain_kind": "NUMERIC_INTERVAL",
         "interval": {"unit": unit, "min": mn or bound(), "max": mx or bound()},
         "categories": None, "modulates": "NOT_APPLICABLE" if gtype != "MODULATING" else "RATE",
         "independence_assumed": "UNKNOWN", "matrix_scope": scope(), "missing_input_verdict": "UNKNOWN",
         "evidence_ids": [], "status": status, "rationale_raw": None}
    g.update(over)
    return g


def cat_gate(gtype: str = "INHIBITING", allowed: Iterable[str] = (), excluded: Iterable[str] = (),
             key: str = "CG01", **over: Any) -> dict[str, Any]:
    return gate(cv="CV-023", gtype=gtype, location="MEDIUM", domain_kind="CATEGORICAL_SET", interval=None, key=key,
                categories={"allowed": list(allowed), "excluded": list(excluded), "unlisted_verdict": "UNKNOWN"}, **over)


def precondition(key: str = "PRE01", state_key: str = "synthetic_state", op: str = "IS", values: Iterable[str] = ("SYNTH_A",),
                 status: str = "CANDIDATE", evidence_ids: Iterable[str] = ()) -> dict[str, Any]:
    return {"precondition_key": key, "state_ref": state(state_key), "subject_entity": None,
            "predicate": {"operator": op, "values": list(values)}, "missing_input_verdict": "UNKNOWN",
            "evidence_ids": list(evidence_ids), "status": status}


def evidence_ref(eid: str = "SRC-000001", doc_type: str = "PRIMARY", supports: Iterable[str] = ("GATE",)) -> dict[str, Any]:
    return {"evidence_id": eid, "doc_type": doc_type, "supports": list(supports), "locator": "synthetic locator",
            "lineage_root_id": None, "lineage_status": "UNKNOWN"}


def open_question(ref: str = "EQ21-01", status: str = "OPEN", decision: str | None = None,
                  answer: str | None = None) -> dict[str, Any]:
    return {"question_ref": ref, "topic_raw": "synthetic open question", "status": status,
            "answer_locator": answer, "decision_ref": decision}


def entry(**over: Any) -> dict[str, Any]:
    e = {"id": "MECH-000001", "record_type": "MECH", "schema_version": SCHEMA_VERSION, "version": 1, "status": "ACTIVE",
         "superseded_by": None, "created_at": NOW, "created_by": "synthetic-fixture",
         "provenance": {"method": "LLM", "source_ids": [], "agent": "synthetic", "locator": None, "notes": None},
         "verification": {"status": "UNVERIFIED", "verifier": None, "verified_at": None, "ai_reviewer": None, "notes": None},
         "external_refs": [], "notes": None,
         "mechanism_key": "SYNTH_FIXTURE_ONE", "label": "synthetic fixture one", "synonyms": [],
         "family": "MICRONUTRIENT_DEGRADATION", "kind": "CHEMICAL_REACTION", "edge_semantics": "REACTION",
         "is_evidence": False, "ai_drafted": True, "provenance_class": "INFERRED_LLM", "review_status": "CANDIDATE",
         "review": {"dual_blind_status": "NOT_STARTED", "reviewer_ids": [], "adjudication_ref": None,
                    "review_provenance_valid": "NOT_CHECKED", "review_packet_row_ids": []},
         "derivation_anchors": [{"anchor_kind": "STEP_CARD", "ref": "synthetic anchor"}],
         "participants": [], "enzyme": None, "gates_unknown": True, "preconditions": [], "condition_gates": [],
         "inhibitors_mitigators": [], "competes_with": [], "consecutive_with": [], "affected_targets": [target()],
         "markers": [], "history_dependence": [], "matrix_scope": scope(), "xrefs": [], "evidence_refs": [],
         "open_questions": []}
    e.update(over)
    return e


def accepted(**over: Any) -> dict[str, Any]:
    """A fully specified ACCEPTED synthetic entry (one STATED gate, one precondition, PRIMARY evidence)."""
    g = gate(mn=stated(1.0), mx=open_(10.0), evidence_ids=["SRC-000001"], status="ACCEPTED",
             matrix_scope=scope("FOOD_CLASS", inc=("synthetic class",)),
             rationale_raw="synthetic: a PRIMARY source states that the reaction is absent outside this window")
    p = precondition(status="ACCEPTED", evidence_ids=["SRC-000001"])
    e = entry(review_status="ACCEPTED", gates_unknown=False, provenance_class="EXTERNAL_VERIFIED",
              verification={"status": "HUMAN_VERIFIED", "verifier": "Kush", "verified_at": NOW, "ai_reviewer": None, "notes": None},
              review={"dual_blind_status": "ADJUDICATED", "reviewer_ids": ["Kush", "Parv"], "adjudication_ref": "synthetic",
                      "review_provenance_valid": "VALID", "review_packet_row_ids": ["synthetic-row"]},
              preconditions=[p], condition_gates=[g], evidence_refs=[evidence_ref()],
              matrix_scope=scope("FOOD_CLASS", inc=("synthetic class",)))
    e.update(over)
    return e


def sink(**over: Any) -> dict[str, Any]:
    e = entry(mechanism_key="SYNTH_SINK", kind="UNRESOLVED_SINK", family="UNRESOLVED", edge_semantics="NOT_APPLICABLE",
              affected_targets=[], gates_unknown=True)
    e.update(over)
    return e


def enzyme_obj() -> dict[str, Any]:
    def x(c: str) -> dict[str, Any]:
        return {"curie": c, "relation": "EXACT", "match_basis": "AI_PROPOSED", "xref_status": "PROPOSED",
                "verification_status": "UNVERIFIED", "verified_by": None, "collision_note": None}
    return {"label_raw": "synthetic enzyme", "ec": x("EC:1.1.1.1"), "go_mf": x("GO:0000001"), "rhea": None}


def competes(relation: str = "PARALLEL_PATHWAY", key: str = "SYNTH_FIXTURE_TWO") -> dict[str, Any]:
    return {"mechanism_key": key, "shared_target": state("synthetic_target"), "relation": relation,
            "evidence_ids": [], "status": "CANDIDATE"}


def consecutive(order: str = "UNKNOWN", key: str = "SYNTH_FIXTURE_TWO") -> dict[str, Any]:
    return {"mechanism_key": key, "order": order, "shared_species": None, "evidence_ids": [], "status": "CANDIDATE"}


def marker(key: str = "MRK01", shared: Iterable[str] = ()) -> dict[str, Any]:
    shared = list(shared)
    return {"marker_key": key, "marker": {"ref_type": "CLASS_LABEL", "ref": "x", "label_raw": "x"}, "marker_unique": False,
            "sharing_status": "SHARED_DECLARED" if shared else "NOT_ASSESSED", "shared_with_mechanism_keys": shared,
            "evidence_ids": [], "status": "CANDIDATE"}


def history(role: str = "INPUT_REQUIRED", key: str = "synthetic_history") -> dict[str, Any]:
    return {"state_ref": state(key), "role": role, "evidence_ids": [], "status": "CANDIDATE"}


def inhibitor(key: str = "INH01", role: str = "INHIBITOR", sbo: str = "SBO:0000020", extent: str = "UNKNOWN",
              via: dict[str, Any] | None = None, **over: Any) -> dict[str, Any]:
    i = {"inhibitor_key": key, "role": role, "agent_or_condition_raw": "synthetic agent", "sbo_role": sbo, "extent": extent,
         "evaluated_via": via or {"mode": "NOT_EVALUABLE_YET", "gate_key": None, "state_ref": None, "predicate": None},
         "missing_input_verdict": "UNKNOWN", "evidence_ids": [], "status": "CANDIDATE"}
    i.update(over)
    return i


def via_gate(key: str = "CG01") -> dict[str, Any]:
    return {"mode": "GATE", "gate_key": key, "state_ref": None, "predicate": None}
