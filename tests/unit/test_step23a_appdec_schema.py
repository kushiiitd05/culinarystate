"""APPDEC draft v1 record schema for the Step 23a applicability engine (S158, DRAFT_PENDING_21b_22a_H4).

Hand-built SYNTHETIC records only. The schema encodes the R-15 route invariant at record level: a SIMULATE
route (or a SIMULATE cross-check) needs G1 and G4..G8 APPLICABLE, a validated domain and a non-safety-critical
query; UNKNOWN or NOT_APPLICABLE applicability never carries SIMULATE. 23a consumes no COND value.
"""
from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "registry" / "schemas" / "APPDEC.draft_v1.schema.json"
REASONS_PATH = ROOT / "registry" / "mechanisms" / "applicability_reason_code_registry_v1_DRAFT.csv"
GATES = ("G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9")


def validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator({k: v for k, v in schema.items() if k != "$id"})


def errors(rec: dict[str, Any]) -> list[str]:
    return [e.message for e in validator().iter_errors(rec)]


def gate(verdict: str = "APPLICABLE", reasons: tuple[str, ...] = ()) -> dict[str, Any]:
    return {"verdict": verdict, "reasons": list(reasons)}


def record(**over: Any) -> dict[str, Any]:
    gates = {g: gate() for g in GATES}
    gates["G0"] = gate("NOT_REQUIRED", ("G0_NOT_EVALUATED",))
    gates["G2"] = gate("NOT_REQUIRED")
    gates["G9"] = gate("NOT_REQUIRED")
    r = {
        "record_type": "APPDEC", "schema_version": "0.1.0-draft", "appdec_id": "APPDEC-DRAFT-0123456789abcdef",
        "status": "DRAFT_PENDING_21b_22a_H4", "mode": "23a", "is_evidence": False,
        "provenance_class": "MODEL_ESTIMATED", "condition_source": "CONSTRUCTED_CASE",
        "query": {"case_id": "SYNTH-CASE-001", "entity_version_id": "SYN-ENT@1", "event_id": "E1",
                  "target": {"svar_id": None, "state_key": "synthetic_target"}, "process_id": "PROC-SYN001",
                  "event_resolved": True, "matrix": "synthetic class", "modifiers": {}},
        "evidence_precheck": "NOT_EVALUATED", "deterministic_change_refs": [],
        "mechanisms": [{"mechanism_key": "SYNTH_FIXTURE_ONE", "mechanism_id": "MECH-000001",
                        "signature_keys": ["SYNTH_RULE_ONE:SYNTH_FIXTURE_ONE"], "consumable": True,
                        "refusal_reasons": [], "verdict": "APPLICABLE", "reasons": [], "directions": ["DECREASE"],
                        "qualitative_only": False, "missing_inputs": []}],
        "gates": gates, "applicability": "APPLICABLE", "route": "SIMULATE", "cross_check": "NONE",
        "model_estimate_label": "NONE", "domain_flag": "IN_VALIDATION_DOMAIN", "safety_critical": "NO",
        "direction_set": ["DECREASE"], "conflict_flag": False, "missing_inputs": [], "ask_candidates": [],
        "registry_versions": {"engine": "step23a-engine-0.1.0-draft", "mech_schema": "1.1.0-draft",
                              "signature_contract": "step22a-procsig-0.1.0-draft",
                              "reason_code_registry_sha256": "0" * 64, "route_enum_sha256": "0" * 64},
        "code_sha256": "0" * 64, "input_sha256": "0" * 64, "sim_run_id": None,
    }
    r.update(over)
    return r


def unknown_record(**over: Any) -> dict[str, Any]:
    r = record(applicability="UNKNOWN", route="UNKNOWN", domain_flag="UNKNOWN", safety_critical="UNKNOWN")
    r["gates"]["G6"] = gate("UNKNOWN", ("NO_FORM",))
    r.update(over)
    return r


def test_schema_is_valid_draft_2020_12_and_accepts_synthetic_records() -> None:
    assert errors(record()) == []
    assert errors(unknown_record()) == []


def test_fixed_fields() -> None:
    for field, bad in (("is_evidence", True), ("mode", "23b"), ("condition_source", "COND"),
                       ("status", "APPROVED"), ("sim_run_id", "SIMRUN-1"), ("record_type", "EVD")):
        assert errors(record(**{field: bad})), field
    assert errors(record(appdec_id="APPDEC-000001")), "an APPDEC id is a content id, never a minted ledger id"
    assert errors(record(extra_field=1))


def test_reason_codes_are_closed_to_the_registry() -> None:
    codes = {r["reason_code"] for r in csv.DictReader(REASONS_PATH.open(encoding="utf-8"))}
    rec = unknown_record()
    rec["gates"]["G6"] = gate("UNKNOWN", ("NOT_A_REGISTERED_CODE",))
    assert errors(rec)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert set(schema["$defs"]["reason_code"]["enum"]) == codes


def test_simulate_needs_every_g4_to_g8_gate_applicable() -> None:
    for g in ("G1", "G4", "G5", "G6", "G7", "G8"):
        for v in ("UNKNOWN", "NOT_APPLICABLE"):
            rec = record()
            rec["gates"][g] = gate(v, ("INPUT_UNOBSERVED",) if g == "G7" else ("NO_FORM",) if g == "G6" else
                                   ("EVENT_UNRESOLVED",) if g == "G1" else ("COMPETING_UNRESOLVED",) if g == "G5" else
                                   ("PARAM_UNCONFIRMABLE",) if g == "G8" else ("NECESSARY_AXIS_UNKNOWN",))
            assert errors(rec), (g, v)


def test_simulate_needs_validated_domain_safety_and_no_evidence_preemption() -> None:
    for over in ({"domain_flag": "IN_CALIBRATION_ONLY"}, {"domain_flag": "UNKNOWN"}, {"safety_critical": "UNKNOWN"},
                 {"safety_critical": "YES"}, {"applicability": "UNKNOWN"}, {"evidence_precheck": "DIRECT"}):
        assert errors(record(**over)), over


def test_unknown_applicability_never_carries_simulate_or_a_simulate_cross_check() -> None:
    assert errors(unknown_record(route="SIMULATE"))
    assert errors(unknown_record(route="DIRECT", evidence_precheck="DIRECT", cross_check="SIMULATE"))
    assert errors(record(route="DIRECT", evidence_precheck="DIRECT", cross_check="SIMULATE")) == []
    assert errors(record(cross_check="SIMULATE")), "a cross-check belongs to DIRECT / INTERPOLATE only"


def test_model_estimate_label_only_on_qualitative() -> None:
    assert errors(record(route="QUALITATIVE", domain_flag="IN_CALIBRATION_ONLY",
                         model_estimate_label="RESEARCH_ONLY")) == []
    assert errors(record(model_estimate_label="RESEARCH_ONLY"))


def test_mechanism_items_carry_signs_only() -> None:
    rec = record()
    rec["mechanisms"][0]["magnitude"] = 0.5
    assert errors(rec)
    rec = record()
    rec["mechanisms"][0]["directions"] = ["UP"]
    assert errors(rec)
    rec = copy.deepcopy(record())
    rec["mechanisms"][0]["refusal_reasons"] = ["NOT_A_REASON"]
    assert errors(rec)
