"""Independent engineering auditor: planted provenance failures cannot become passes."""
from copy import deepcopy

import pytest

from culinarystate.evaluation.emission_audit import audit_text, audit_payload


EVD = {"EVD-990001": {"status": "ACTIVE", "derived": {"retention_factor": {
    "status": "MEASURED", "value": .55, "unit": "1"}}}}


@pytest.mark.parametrize("number", ["2.5", "55%", "5.5e-1", "-0.55", "55 percent"])
def test_all_retention_number_formats_need_a_reference(number):
    result = audit_text(f"Retention factor is {number}.", EVD, packet_ids=set())
    assert result["issues"]["UNCITED_CHEMISTRY_NUMBER"] == 1


def test_known_id_does_not_authorize_a_different_numeric_value():
    result = audit_text("Retention factor 0.85 [EVD-990001].", EVD, packet_ids=set(EVD))
    assert result["issues"]["VALUE_NOT_IN_CITED_POINT_EVIDENCE"] == 1


def test_reference_must_belong_to_recorded_packet():
    result = audit_text("Retention factor 0.55 [EVD-990001].", EVD, packet_ids=set())
    assert result["issues"]["CITATION_OUTSIDE_RECORDED_PACKET"] == 1


def test_lexical_alignment_never_becomes_semantic_validation():
    result = audit_text("Retention factor 0.55 [EVD-990001].", EVD, packet_ids=set(EVD))
    assert not result["issues"]
    assert result["aligned_retention_numbers"] == 1
    assert result["semantic_entailment_verified"] is False


def test_citation_only_fragment_and_ordinary_counts_are_distinguished():
    result = audit_text("Retention factor 55%. [EVD-990001]\nAcross 10 rows from 2 independent sources.",
                        EVD, packet_ids=set(EVD))
    assert result["aligned_retention_numbers"] == 1
    assert result["counts"]["METADATA_COUNT"] == 2
    assert not result["issues"]


def test_qualitative_cap_cannot_emit_a_retention_value():
    result = audit_text("Retention factor 0.55 [EVD-990001].", EVD, packet_ids=set(EVD), no_numbers=True)
    assert result["issues"]["NUMERIC_CLAIM_EXCEEDS_PRECISION_CAP"] == 1


def test_censored_limit_is_not_an_observed_point():
    evd = deepcopy(EVD)
    evd["EVD-990001"]["derived"]["retention_factor"] = {"status": "CENSORED", "censor": {"limit": .55}}
    result = audit_text("Retention factor 0.55 [EVD-990001].", evd, packet_ids=set(evd))
    assert result["issues"]["VALUE_NOT_IN_CITED_POINT_EVIDENCE"] == 1


def test_unknown_cannot_reach_simulate():
    result = audit_payload({"route": "SIMULATE", "temperature": {"status": "UNKNOWN"}})
    assert result["UNKNOWN_INPUT_TO_SIMULATE"] == 1


@pytest.mark.parametrize("basis", ["SCENARIO", "ASSUMED_DEFAULT", "MODEL_DERIVED"])
def test_model_or_assumed_basis_never_gets_evidence_label(basis):
    result = audit_payload({"label": "evidence_supported", "basis": basis})
    assert result["MODEL_BASIS_LABELLED_EVIDENCE"] == 1


def test_layer2_cannot_establish_not_possible():
    result = audit_payload({"verdict": "NOT_POSSIBLE", "basis": "LAYER2"})
    assert result["NOT_POSSIBLE_FROM_LAYER2"] == 1


def test_unknown_units_are_review_gaps_and_text_is_not_exposed():
    text = "Secret meal includes 10 mg vitamin C."
    result = audit_text(text, EVD, packet_ids=None)
    assert result["gaps"]
    assert "Secret" not in str(result)


def test_demo_sampling_is_deterministic_with_explicit_synthetic_recipe_arm():
    from tools.s179_emission_audit import sample_cases
    rows = [{"id": "EVD-990001", "status": "ACTIVE", "matrix": {"raw_name": "carrot"},
             "process": {"raw_name": "boil"}, "target": {"raw_name": "vitamin C"}}]
    before = deepcopy(rows)
    a = sample_cases(rows, n=10, seed=7, recipe_every=5)
    assert a == sample_cases(rows, n=10, seed=7, recipe_every=5)
    assert sum(bool(c["recipe_text"]) for c in a) == 2
    assert all(c["recipe_origin"] in ("NONE", "SYNTHETIC_CALLER_INPUT") for c in a)
    assert rows == before
