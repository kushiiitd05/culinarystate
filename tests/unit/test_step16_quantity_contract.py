"""Synthetic controls for proposed rc2 metadata and quantity AST contracts."""
import copy
import csv
import json
from fractions import Fraction
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from culinarystate.quantity.draft_contract import (
    ContractError, claim_targets, evaluate_ast, make_record_schema, metadata_schema, validate_ast, validate_record,
)
from tests.unit.test_step16a_schema_drafts import qnt, st

ROOT = Path(__file__).resolve().parents[2]


def meta(status="KNOWN", origin="EXPLICIT_SOURCE", route="EXPLICIT"):
    return {"origin": origin, "status": status, "claim_route": route,
            "evidence_refs": ["synthetic:source"]}


def rat(n, d=1, unit="g", **kw):
    return {"node_type": "RATIONAL", "numerator": n, "denominator": d,
            "unit": unit, "meta": meta(), **kw}


def interval(lo, hi, unit="g"):
    return {"node_type": "RANGE", "low": lo, "high": hi, "unit": unit, "meta": meta()}


def op(kind, *children):
    return {"node_type": kind, "children": list(children),
            "meta": meta(origin="DERIVED_DETERMINISTIC", route="INFERRED_RULE")}


def unknown():
    return {"node_type": "UNKNOWN", "raw": "unstated", "unit": "g", "meta": meta("UNKNOWN", "UNKNOWN")}


def schema(kind):
    return json.loads((ROOT / f"reports/step16/schema_drafts/{kind}.draft_v2.schema.json").read_text())


def record(kind):
    # Fixture-only annotations. The implementation never backfills metadata.
    r = qnt(ast=rat(1)) if kind == "QNT" else st(variables={"temperature": {"status": "UNKNOWN"}})
    r["schema_version"] = "1.0.0-rc2"
    r["field_metadata"] = {}
    for path, value in claim_targets(r).items():
        if isinstance(value, dict) and "meta" in value:
            continue
        missing = value is None or isinstance(value, dict) and value.get("status") == "UNKNOWN"
        r["field_metadata"][path] = meta("UNKNOWN", "UNKNOWN") if missing else meta()
    return r


@pytest.mark.parametrize("node", [
    rat(1, 3), interval(1, 2), op("ADD", rat(1), rat(2)),
    op("MULTIPLY", rat(2, unit="1"), rat(3)),
    op("FRACTION_OF", rat(1, 2, "1"), rat(3)),
    op("REMAINDER_OF", rat(10), rat(2)),
    op("PACKAGE_CONTENT", rat(2, unit="1"), rat(400)),
    op("ALTERNATIVE", rat(500), rat(1, unit="cup")),
    {"node_type": "QUALITATIVE", "raw": "a synthetic pinch", "meta": meta()},
    {"node_type": "OPEN_AMOUNT", "raw": "as needed", "meta": meta()}, unknown(),
])
def test_all_eleven_node_types_have_typed_payloads(node):
    assert validate_ast(node) == []


@pytest.mark.parametrize("node", [
    {"node_type": "RATIONAL"}, rat(1, 0), rat(True), rat(1, unit=""),
    interval(2, 1), interval(float("nan"), 1), interval(1, float("inf")),
    op("ADD", rat(1)), op("MULTIPLY", rat(1)), op("FRACTION_OF", rat(1)),
    {"node_type": "QUALITATIVE", "raw": "pinch", "value": 0, "meta": meta()},
    {"node_type": "UNKNOWN", "meta": meta()},
    rat(1, meta=meta("UNKNOWN")),
])
def test_invalid_ast_cannot_be_executed(node):
    assert validate_ast(node)
    with pytest.raises(ContractError):
        evaluate_ast(node)


def test_exact_rational_arithmetic_preserves_range_without_midpoint():
    assert evaluate_ast(rat(1, 3)).low == Fraction(1, 3)
    result = evaluate_ast(op("ADD", rat(100), interval(25, 50)))
    assert (result.low, result.high, result.unit) == (125, 150, "g")
    assert result.status == "RANGE"
    assert "DERIVED_DETERMINISTIC" in result.origins


def test_package_fraction_and_remainder_use_only_explicit_operands():
    assert evaluate_ast(op("PACKAGE_CONTENT", rat(2, unit="1"), rat(400))).low == 800
    result = evaluate_ast(op("FRACTION_OF", rat(1, 2, "1"), interval(100, 200)))
    assert (result.low, result.high) == (50, 100)
    result = evaluate_ast(op("REMAINDER_OF", rat(100), rat(25), interval(10, 20)))
    assert (result.low, result.high) == (55, 65)


@pytest.mark.parametrize("node", [op("ADD", rat(1, unit="cup"), rat(100)),
                                  op("ADD", rat(1, unit="kg"), rat(100)),
                                  op("MULTIPLY", rat(1), rat(2)),
                                  op("FRACTION_OF", rat(2, unit="1"), rat(100)),
                                  op("REMAINDER_OF", rat(10), rat(20))])
def test_incompatible_or_impossible_arithmetic_is_not_repaired(node):
    with pytest.raises(ContractError):
        evaluate_ast(node)


def test_uncertain_overallocation_is_unknown_and_never_clipped():
    result = evaluate_ast(op("REMAINDER_OF", interval(10, 20), rat(15)))
    assert result.status == "UNKNOWN" and result.low is None
    assert result.reason == "POSSIBLE_OVERALLOCATION"


def test_alternatives_stay_separate_and_cannot_be_multiplied():
    alt = op("ALTERNATIVE", rat(500), rat(1, unit="cup"))
    result = evaluate_ast(alt)
    assert result.status == "ALTERNATIVE" and result.low is None
    assert [r.unit for r in result.alternatives] == ["g", "cup"]
    with pytest.raises(ContractError):
        evaluate_ast(op("MULTIPLY", rat(2, unit="1"), alt))


def test_unknown_and_qualitative_amounts_are_not_zero():
    assert evaluate_ast(op("ADD", rat(10), unknown())).status == "UNKNOWN"
    assert evaluate_ast(rat(0)).low == 0
    q = {"node_type": "QUALITATIVE", "raw": "a pinch", "meta": meta()}
    result = evaluate_ast(q)
    assert result.low is None and result.raw == "a pinch"


@pytest.mark.parametrize("status", ["CONFLICTING", "CENSORED"])
def test_flagged_evidence_is_not_used_as_an_exact_point(status):
    result = evaluate_ast(rat(1, meta=meta(status)))
    assert result.status == "UNKNOWN" and result.low is None


@pytest.mark.parametrize("kind", ["QNT", "STATE"])
def test_rc2_schema_and_complete_metadata_validate(kind):
    s = schema(kind)
    Draft202012Validator.check_schema(s)
    r = record(kind)
    before = copy.deepcopy(r)
    assert validate_record(r, s) == []
    assert r == before


def test_missing_metadata_never_gets_backfilled():
    r = record("QNT")
    del r["field_metadata"]["/parsed"]
    assert any(i.code == "MISSING_METADATA" for i in validate_record(r, schema("QNT")))
    assert "/parsed" not in r["field_metadata"]


def test_numeric_bounds_need_their_own_provenance_and_cannot_be_unknown():
    r = record("QNT")
    r.update(normalized_mass_low_g=100, normalized_mass_high_g=120)
    assert any(i.code == "MISSING_METADATA" for i in validate_record(r, schema("QNT")))
    r["field_metadata"].update({"/normalized_mass_low_g": meta("UNKNOWN"),
                                "/normalized_mass_high_g": meta()})
    assert any(i.code == "UNKNOWN_WITH_CLAIM" for i in validate_record(r, schema("QNT")))


def test_stale_metadata_and_disagreement_with_inline_metadata_are_reported():
    r = record("QNT")
    r["field_metadata"]["/does_not_exist"] = meta()
    r["field_metadata"]["/ast"] = meta(origin="INFERRED_LLM", route="INFERRED_LLM")
    codes = {i.code for i in validate_record(r, schema("QNT"))}
    assert {"METADATA_PATH", "METADATA_CONFLICT"} <= codes


def test_state_variable_names_use_json_pointer_escaping():
    r = record("STATE")
    r["variables"] = {"a/b~c": {"status": "UNKNOWN"}}
    r["field_metadata"] = {"/belief": meta(), "/variables/a~1b~0c": meta("UNKNOWN", "UNKNOWN")}
    assert validate_record(r, schema("STATE")) == []


def test_v1_record_is_not_silently_migrated_to_rc2():
    r = qnt()
    assert validate_record(r, schema("QNT"))
    assert r["schema_version"] == "1.0.0" and "field_metadata" not in r


def test_wrong_schema_is_rejected_without_a_runtime_exception():
    legacy = json.loads((ROOT / "reports/step16/schema_drafts/QNT.draft_v1.schema.json").read_text())
    assert any(i.code == "DRAFT_SCHEMA" for i in validate_record(qnt(), legacy))
    with pytest.raises(ValueError, match="record type"):
        make_record_schema(legacy, "STATE")


def test_schema_generation_is_deterministic_and_does_not_mutate_rc1():
    legacy = json.loads((ROOT / "reports/step16/schema_drafts/QNT.draft_v1.schema.json").read_text())
    before = copy.deepcopy(legacy)
    assert make_record_schema(legacy, "QNT") == schema("QNT")
    assert legacy == before


@pytest.mark.parametrize("node", [
    {"node_type": "QUALITATIVE", "raw": " ", "meta": meta()},
    rat(1, meta={**meta(), "evidence_refs": [" "]}),
])
def test_blank_assertions_are_not_evidence(node):
    assert validate_ast(node)


def test_not_applicable_and_model_provenance_are_not_promoted():
    n = {"node_type": "UNKNOWN", "meta": meta("NOT_APPLICABLE", "UNKNOWN")}
    assert evaluate_ast(n).status == "NOT_APPLICABLE"
    result = evaluate_ast(rat(1, meta=meta(origin="MODEL_ESTIMATED", route="MODEL")))
    assert result.origins == ("MODEL_ESTIMATED",)


def test_interval_bands_keep_separate_metadata():
    r = record("QNT")
    r["intervals"] = [{"kind": "SOURCE_RANGE", "low": 1, "high": 2, "unit": "g"},
                      {"kind": "CONVERSION_UNCERTAINTY", "low": 1, "high": 3, "unit": "g"}]
    r["field_metadata"].update({"/intervals/0": meta(), "/intervals/1": meta(origin="MODEL_ESTIMATED", route="MODEL")})
    assert validate_record(r, schema("QNT")) == []
    del r["field_metadata"]["/intervals/1"]
    assert any(i.path == "/intervals/1" and i.code == "MISSING_METADATA" for i in validate_record(r, schema("QNT")))


def test_metadata_enums_match_the_existing_registries():
    m = metadata_schema()["properties"]
    with (ROOT / "registry/provenance_class_registry_v1.csv").open(newline="") as f:
        assert set(m["origin"]["enum"]) == {r["provenance_class"] for r in csv.DictReader(f)}
    for axis, filename in [("status", "field_status"), ("claim_route", "claim_route")]:
        with (ROOT / f"registry/recipe_semantics/{filename}_registry_v1_DRAFT.csv").open(newline="") as f:
            assert set(m[axis]["enum"]) == {r["code"] for r in csv.DictReader(f)}


def test_rc2_semantic_errors_use_unambiguous_json_pointer_paths():
    r = record("STATE")
    r["variables"] = {"a/b~c": {"status": "RANGE", "low": 2, "high": 1, "unit": "g"}}
    r["field_metadata"] = {"/belief": meta(), "/variables/a~1b~0c": meta()}
    assert any(i.code == "INVERTED_INTERVAL" and i.path == "/variables/a~1b~0c"
               for i in validate_record(r, schema("STATE")))


def test_results_serialize_exact_fractions_and_unknowns_without_mutating_input():
    node = op("ALTERNATIVE", rat(1, 3), unknown())
    before = copy.deepcopy(node)
    result = evaluate_ast(node)
    wire = json.loads(json.dumps(result.to_mapping()))
    assert wire["alternatives"][0]["low"] == {"numerator": 1, "denominator": 3}
    assert wire["alternatives"][1]["low"] is None
    assert wire["status"] == "ALTERNATIVE" and wire["low"] is None
    assert node == before


def test_record_validator_checks_ast_arithmetic_as_well_as_payload_shape():
    r = record("QNT")
    r["ast"] = op("ADD", rat(100), rat(1, unit="cup"))
    assert any(i.code == "AST_ARITHMETIC" and i.path == "/ast" for i in validate_record(r, schema("QNT")))


def test_invalid_document_root_uses_the_empty_json_pointer():
    issues = validate_record(None, schema("QNT"))
    assert issues and issues[0].code == "SCHEMA" and issues[0].path == ""
