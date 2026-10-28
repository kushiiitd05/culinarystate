"""Synthetic controls for the draft review overlay; no human labels or real recipes."""
import copy

import pytest

from culinarystate.annotation.schema_review import review_record


def codes(record, **kw):
    return {i.code for i in review_record(record, **kw)}


@pytest.mark.parametrize("lo,hi", [("low", "high"), ("mass_low_g", "mass_high_g"),
                                       ("normalized_mass_low_g", "normalized_mass_high_g")])
def test_inverted_interval_is_reported_without_changing_input(lo, hi):
    r = {"nested": {lo: 2, hi: 1}}
    before = copy.deepcopy(r)
    assert "INVERTED_INTERVAL" in codes(r)
    assert r == before


def test_unknown_bound_is_not_filled_or_treated_as_zero():
    assert "INVERTED_INTERVAL" not in codes({"low": None, "high": -1})


@pytest.mark.parametrize("number", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_number_has_a_precise_path(number):
    issues = review_record({"items": [{"low": number}]})
    assert any(i.code == "NONFINITE_NUMBER" and i.path == "$.items[0].low" for i in issues)


def test_metadata_requirement_is_explicit_and_does_not_reject_legacy_by_default():
    r = {"variables": {"temperature": {"status": "MEASURED", "value": 20, "unit": "C"}}}
    assert "MISSING_METADATA" not in codes(r)
    assert "MISSING_METADATA" in codes(r, require_metadata=True)


def test_metadata_triple_cannot_be_satisfied_by_empty_object():
    r = {"status": "MEASURED", "value": 1, "meta": {}}
    assert "INCOMPLETE_METADATA" in codes(r, require_metadata=True)


def test_family_namespace_and_membership_are_distinct_checks():
    assert "UNKNOWN_PROCESS_FAMILY" in codes({"process_family_id": "FAM:BOGUS"}, family_ids={"FAM:DRY_HEAT"})
    assert "PROCESS_FAMILY_NAMESPACE" in codes({"process_family_id": "PROC-000001"})
    assert not review_record({"process_family_id": "FAM:DRY_HEAT"}, family_ids={"FAM:DRY_HEAT"})


def test_ast_range_missing_bounds_is_reported():
    assert "AST_RANGE_BOUNDS" in codes({"ast": {"node_type": "RANGE"}})
    assert "AST_RANGE_BOUNDS" not in codes({"ast": {"node_type": "RANGE", "low": 1, "high": 2}})


def test_unspecified_ast_contract_is_visible_instead_of_invented():
    assert "AST_CONTRACT_PENDING" in codes({"ast": {"node_type": "RATIONAL"}})


def test_unknown_metadata_cannot_carry_qualitative_or_censored_claim():
    r = {"status": "QUALITATIVE", "qualitative": "hot", "meta": {"status": "UNKNOWN"}}
    assert "UNKNOWN_WITH_CLAIM" in codes(r)
