"""D-029 D-6 / D-032 addendum: DOC, LIN, SEXP, SMP, OBS ported into the ledger registry.

Examples are built from the *draft* schemas' required fields (registry/schemas/*.draft_v1_1.schema.json) and
validated against the schemas regenerated from the registry. IdMinter is only ever pointed at tmp_path.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from culinarystate.ledgers.common import envelope
from culinarystate.ledgers.registry import PREFIXES, R
from culinarystate.ledgers.store import IdMinter
from tests.fixtures.ledger_examples import base

ROOT = Path(__file__).resolve().parents[2]
NEW = ["DOC", "LIN", "SEXP", "SMP", "OBS"]
STAMP = "2026-10-26T05:00:00+00:00"


def _draft(prefix: str) -> dict:
    return json.loads((ROOT / "registry" / "schemas" / f"{prefix}.draft_v1_1.schema.json").read_text())


def _string(schema: dict) -> str:
    pat = schema.get("pattern")
    if pat:
        if pat == "^[0-9a-f]{64}$":
            return "a" * 64
        m = re.fullmatch(r"\^\(?([A-Z]+(?:-[A-Z]+)?)(?:\|[A-Z|]+)?\)?-\\d\{(\d)\}\$", pat)
        if m:
            return f"{m.group(1)}-{1:0{int(m.group(2))}d}"
        raise AssertionError(f"unhandled pattern {pat}")
    if schema.get("format") == "date-time":
        return STAMP
    return "x"


def _build(schema: dict, defs: dict):
    """Smallest instance from required fields only; enum -> first value; anyOf -> first alternative."""
    if "$ref" in schema:
        return _build(defs[schema["$ref"].rsplit("/", 1)[1]], defs)
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][0]
    if "anyOf" in schema:
        return _build(schema["anyOf"][0], defs)
    t = schema.get("type")
    if t == "string":
        return _string(schema)
    if t == "integer":
        return max(schema.get("minimum", 0), 1)
    if t == "number":
        return schema.get("minimum", 0)
    if t == "boolean":
        return False
    if t == "null":
        return None
    if t == "array":
        return [_build(schema["items"], defs)] if schema.get("minItems", 0) else []
    if t == "object":
        props = schema.get("properties", {})
        return {k: _build(props[k], defs) for k in schema.get("required", [])}
    raise AssertionError(f"unhandled schema {schema}")


# Where the first enum value would trip a conditional (allOf) rule of the draft, pick the consistent value.
OVERRIDES = {
    "DOC": {"report_kind": "PRIMARY_REPORT", "is_compilation_hub": "NO", "authorship": {
        "status": "UNKNOWN", "authors_raw": [], "affiliations_raw": [], "corresponding_author_raw": None,
        "year_published": None}},
    "LIN": {"edge_type": "SAME_STUDY_AS", "from_id": "DOC-000001", "to_id": "DOC-000002", "score": None,
            "reviewer": None, "detection_method": "DOI_MATCH", "detector_level": "B1",
            "edge_status": "PROVISIONAL", "rule_version": "lin-rules-r1"},
    "SEXP": {"reference_design": "OWN_REFERENCE", "condition_status": "NOT_REPORTED", "protocol_locator": None},
    "SMP": {"derived_from": {"status": "ROOT", "sample_id": None, "process_id": None, "process_raw_name": None,
                             "condition_id": None, "condition_status": "NOT_APPLICABLE"},
            "material_origin": {"status": "NOT_REPORTED", "batch_label_raw": None, "cultivar_raw": None,
                                "purchase_or_harvest_raw": None},
            "n_biological_units": {"status": "NOT_REPORTED", "value": None}},
    "OBS": {
        "value": {"status": "MEASURED", "value": 1.5, "unit": "mg/100 g"},
        "measurement_dedup": {"status": "UNIQUE_MEASUREMENT", "canonical_obs_id": None, "report_priority": 1},
        "dispersion": {"type": "NONE_REPORTED", "value": None, "low": None, "high": None, "ci_level": None,
                       "unit": None, "n_basis": "NOT_APPLICABLE", "scope": "NOT_APPLICABLE",
                       "significance_raw": None, "derivation": "NOT_APPLICABLE"},
        "censoring": {"kind": "DETECTED", "registry_id": None, "limit_low": None, "limit_high": None,
                      "limit_unit": None, "limit_origin": "NOT_APPLICABLE", "resolution": None, "basis_note": None},
        "lod": {"status": "NOT_REPORTED", "value": None, "unit": None},
        "loq": {"status": "NOT_REPORTED", "value": None, "unit": None},
        "digitization": None,
    },
}


def example(prefix: str, **changes) -> dict:
    d = _draft(prefix)
    rec = {k: _build(d["properties"][k], d.get("$defs", {})) for k in d["required"]}
    rec.update(base(prefix, 1))
    rec.update(copy.deepcopy(OVERRIDES[prefix]))
    rec.update(changes)
    return rec


def validator(prefix: str) -> Draft202012Validator:
    return Draft202012Validator(R[prefix], format_checker=Draft202012Validator.FORMAT_CHECKER)


def messages(prefix: str, rec: dict) -> list[str]:
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in validator(prefix).iter_errors(rec)]


# ---- registration / minter ----
@pytest.mark.parametrize("prefix", NEW)
def test_prefix_registered(prefix):
    assert prefix in R and prefix in PREFIXES


@pytest.mark.parametrize("prefix,key", [
    ("DOC", "SRC-000001|sha256:" + "a" * 64),
    ("LIN", "SAME_STUDY_AS|DOC-000001|DOC-000002"),
    ("SEXP", "STUDY-000001|1"),
    ("SMP", "SEXP-000001|1"),
    ("OBS", "SMP-000001|SVAR-000001|WHOLE|T1:r2"),
])
def test_mint_new_prefix_is_idempotent_on_tmp_ledger(tmp_path, prefix, key):
    ids = IdMinter(tmp_path)
    first = ids.mint(prefix, key)
    assert first == f"{prefix}-000001"
    assert ids.mint(prefix, key) == first                      # same key, same id
    assert ids.mint(prefix, key + "x") == f"{prefix}-000002"   # new key, next number
    assert IdMinter(tmp_path).lookup(prefix, key) == first     # survives reload
    assert len((tmp_path / "_ids.jsonl").read_text().splitlines()) == 2


@pytest.mark.parametrize("prefix", ["LROOT", "KINETIC", "AGG", "DRV", "NOPE"])
def test_unregistered_prefix_still_raises(tmp_path, prefix):
    assert prefix not in R
    with pytest.raises(KeyError):
        IdMinter(tmp_path).mint(prefix, "k")


# ---- schema envelope ----
@pytest.mark.parametrize("prefix", NEW)
def test_schema_envelope_matches_existing_ones(prefix):
    s, ref = R[prefix], R["STUDY"]
    assert s["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert s["$id"] == f"culinarystate/{prefix}.schema.json"
    assert s["title"].startswith(f"{prefix}- ") and "DRAFT" not in s["title"]
    assert s["type"] == "object" and s["additionalProperties"] is False
    assert s["description"] == ref["description"]
    assert {k: s["properties"][k] for k in envelope(prefix)} == envelope(prefix)
    assert s["properties"]["record_type"] == {"const": prefix}
    assert s["required"][:8] == ref["required"][:8]
    Draft202012Validator.check_schema(s)


@pytest.mark.parametrize("prefix", NEW)
def test_fields_and_required_match_the_draft(prefix):
    d, s = _draft(prefix), R[prefix]
    assert s["required"] == d["required"]
    assert s["properties"] == d["properties"]
    assert s.get("$defs", {}) == d.get("$defs", {})
    assert s["allOf"] == d["allOf"]


# ---- example records ----
@pytest.mark.parametrize("prefix", NEW)
def test_example_from_required_fields_validates(prefix):
    assert messages(prefix, example(prefix)) == []


@pytest.mark.parametrize("prefix", NEW)
def test_missing_required_field_rejected(prefix):
    for field in _draft(prefix)["required"][8:]:
        rec = example(prefix)
        del rec[field]
        assert messages(prefix, rec), field


@pytest.mark.parametrize("prefix", NEW)
def test_unknown_field_and_bad_id_rejected(prefix):
    assert messages(prefix, example(prefix, favourite_colour="red"))
    assert messages(prefix, example(prefix, id=f"{prefix}-12"))


def test_human_verified_needs_human_verifier_everywhere():
    for prefix in NEW:
        bad = example(prefix, verification={"status": "HUMAN_VERIFIED", "verifier": "claude", "verified_at": STAMP})
        assert messages(prefix, bad), prefix
        ok = example(prefix, verification={"status": "HUMAN_VERIFIED", "verifier": "Kush", "verified_at": STAMP})
        assert messages(prefix, ok) == [], prefix


# ---- D-029 decisions visible in the schemas ----
def test_lin_edge_rules():
    assert messages("LIN", example("LIN", edge_type="ALTERNATE_OF", from_id="DOC-000001", to_id="STUDY-000001"))
    assert messages("LIN", example("LIN", edge_type="PRIMARY_SOURCE", from_id="AGG-000001", to_id="SRC-000001"))
    assert messages("LIN", example("LIN", edge_type="PRIMARY_SOURCE", from_id="SRC-000002", to_id="SRC-000001",
                                   membership_status="UNKNOWN", detection_method="BIBLIOGRAPHY_LISTING",
                                   detector_level="STRONG")) == []
    assert messages("LIN", example("LIN", edge_status="HUMAN_CONFIRMED", reviewer="claude", reviewed_at=STAMP))
    assert messages("LIN", example("LIN", edge_status="REJECTED"))


def test_doc_hub_rule_and_authorship_never_guessed():
    assert messages("DOC", example("DOC", report_kind="REVIEW", is_compilation_hub="NO"))
    assert messages("DOC", example("DOC", authorship={"status": "UNKNOWN", "authors_raw": ["A B"],
                                                      "affiliations_raw": [], "corresponding_author_raw": None,
                                                      "year_published": None}))


def test_sexp_borrowed_reference_needs_ids():
    assert messages("SEXP", example("SEXP", reference_design="BORROWED_REFERENCE"))
    assert messages("SEXP", example("SEXP", reference_design="BORROWED_REFERENCE",
                                    borrowed_reference_sample_ids=["SMP-000009"])) == []


def test_smp_count_never_zero_or_default():
    assert messages("SMP", example("SMP", n_biological_units={"status": "REPORTED", "value": 0}))
    assert messages("SMP", example("SMP", n_biological_units={"status": "UNKNOWN", "value": 3}))


# ---- regenerated files (tools/export_schemas.py output) ----
@pytest.mark.parametrize("prefix", NEW)
def test_exported_schema_file_equals_registry(prefix):
    path = ROOT / "ledgers" / "schemas" / f"{prefix}.schema.json"
    assert path.is_file(), "run tools/export_schemas.py"
    assert json.loads(path.read_text()) == R[prefix]
