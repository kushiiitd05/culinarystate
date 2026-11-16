"""Source-bound staging never invents production lineage or erases source exclusions."""
from copy import deepcopy

import pytest

from culinarystate.simulation.aa_lineage_readiness import build_readiness, normalise_doi


def fixture():
    cal = [{"row_id": "C1", "candidate_id": "P1", "doi": "10.1234/test", "partition": "SIM-CAL",
            "row_type": "K_AT_T", "pdf_sha256": "a" * 64, "verdict": "VERIFIED"}]
    val = [{"row_id": "V1", "candidate_id": "P2", "doi": "10.1234/other", "partition": "SIM-VAL",
            "row_kind": "K_AT_T", "pdf_sha256": "b" * 64, "matrix_pH": "2.5"}]
    pre = [{"row_id": "V1", "candidate_id": "P2", "row_kind": "K_AT_T", "pdf_sha256": "b" * 64,
            "status": "FLAG", "computational_eligibility": "EXCLUDE_PENDING_ASSAY_BASIS_REVIEW", "reason": "ASSAY_BASIS_UNRESOLVED"}]
    licences = {"P1": "CONFIRMED_ON_PUBLISHER_PAGE", "P2": "CONFIRMED_ON_PUBLISHER_PAGE"}
    pdfs = {"P1": "a" * 64, "P2": "b" * 64}
    return cal, val, pre, {}, licences, pdfs


def test_doi_matching_is_exact_and_normalised_not_a_free_text_substring():
    assert normalise_doi("https://doi.org/10.1234/TEST") == "10.1234/test"
    assert normalise_doi("doi:10.1234/test") == "10.1234/test"
    assert normalise_doi("paper discusses 10.1234/test and more") is None
    values = list(fixture())
    values[3] = {"DOC": [{"id": "DOC-000001", "status": "ACTIVE", "external_refs": ["doi:10.1234/test"]},
                         {"id": "DOC-000002", "status": "ACTIVE", "notes": "paper discusses 10.1234/other and more"}]}
    report, _ = build_readiness(*values)
    assert report["rows"][0]["existing_source_refs"]["DOC"] == ["DOC-000001"]
    assert report["rows"][1]["existing_source_refs"]["DOC"] == []


def test_all_missing_dependencies_are_explicit_and_no_ids_minted():
    report, staging = build_readiness(*fixture())
    assert report["minted_ids"] == [] and report["production_eligible_rows"] == 0
    assert "MISSING_SRC_ID" in report["rows"][0]["blockers"]
    assert "NO_SOURCE_RAW_TRAJECTORY" in report["rows"][0]["blockers"]
    assert all(r["record_type"] == "AA_SOURCE_STAGING_CANDIDATE" for r in staging)
    assert all(r["verification"] == "AI_PRECHECKED" for r in staging)


def test_simval_flag_remains_excluded_even_with_complete_source_id_links():
    args = list(fixture())
    args[3] = {fam: [{"id": fam + "-000001", "status": "ACTIVE", "doi": "10.1234/other"}] for fam in ["SRC", "DOC", "STUDY"]}
    report, staging = build_readiness(*args)
    assert "SOURCE_PRECHECK_EXCLUDES" in report["rows"][1]["blockers"]
    assert staging[1]["original_row"]["matrix_pH"] == "2.5"
    assert report["production_eligible_rows"] == 0


@pytest.mark.parametrize("defect", ["pdf", "precheck", "duplicate", "partition"])
def test_corrupt_binding_or_duplicate_or_partition_refused(defect):
    args = list(deepcopy(fixture()))
    if defect == "pdf": args[5]["P1"] = "c" * 64
    if defect == "precheck": args[2][0]["pdf_sha256"] = "c" * 64
    if defect == "duplicate": args[0].append(dict(args[0][0]))
    if defect == "partition": args[1][0]["partition"] = "SIM-CAL"
    with pytest.raises(ValueError): build_readiness(*args)


def test_isothermal_ph_context_is_corrected_only_in_new_staging_not_original():
    args = list(deepcopy(fixture()))
    args[1][0].update(row_kind="AUTHOR_FIT_K0", matrix_pH="3.1")
    args[2][0].update(row_kind="AUTHOR_FIT_K0", reason="ISOTHERMAL_CONTEXT_AND_EXPONENT_SERIALIZATION")
    before = deepcopy(args)
    report, staging = build_readiness(*args)
    assert args == before
    assert staging[1]["normalised_metadata"]["matrix_pH"] == "NOT_REPORTED_BY_SOURCE"
    assert staging[1]["normalised_metadata"]["original_nonisothermal_pH"] == "3.1"
    assert staging[1]["original_row"]["matrix_pH"] == "3.1"
    assert "AUTHOR_AGGREGATE_NOT_RAW_OBSERVATIONS" in report["rows"][1]["blockers"]
    assert report["ph_context_staging_corrections"] == 1
