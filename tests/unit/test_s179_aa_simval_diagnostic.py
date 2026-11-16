"""Held-out rate diagnostics never pass validation or manufacture retention observations."""
from copy import deepcopy

import pytest

from tools import s179_aa_simval_diagnostic as tool
from tools.s179_aa_simval_diagnostic import compare_rows as _compare_rows


def compare_rows(rows, model, *, source_precheck=None):
    if source_precheck is None:
        source_precheck = {r["row_id"]: {"status": "PASS", "computational_eligibility":
                          "ELIGIBLE_FOR_RATE_DIAGNOSTIC"} for r in rows}
    return _compare_rows(rows, model, source_precheck=source_precheck)


def fit():
    return {"n_papers": 2, "papers": ["CAL-A", "CAL-B"],
            "intercepts": {"CAL-A": -4., "CAL-B": -3.}, "Ea_J_per_mol": 60000.,
            "cov": [[.01, 0., 0.], [0., .01, 0.], [0., 0., 1000000.]],
            "sigma_between": .5, "residual_sd": .1}


def row(**changes):
    return {"row_id": "SYN-VAL-1", "candidate_id": "VAL-C", "partition": "SIM-VAL",
            "row_kind": "K_AT_T", "reaction_order": "1", "temperature_C": "80",
            "k_raw": "72.30", "k_raw_unit": "10^-4 min^-1", "k_normalized_min_1": "0.007230",
            "licence_status": "CONFIRMED_ON_PUBLISHER_PAGE_D085", "comparison_eligibility": "PENDING_HUMAN_AND_BASIS_REVIEW",
            **changes}


def test_pending_basis_only_enters_flagged_rate_diagnostic():
    private, report = compare_rows([row()], fit())
    assert len(private) == 1
    assert report["primary_comparable_rows"] == 0
    assert report["rate_diagnostic"]["n_rows"] == 1
    assert report["retention_observations"] == 0
    assert report["validation_status"] == "NOT_VALIDATED / RESEARCH_ONLY"
    assert private[0]["basis_status"] == "UNRESOLVED_SOURCE_BASIS"
    assert report["production_route_allowed"] is False


def test_aggregates_are_never_used_as_rate_constants():
    private, report = compare_rows([row(row_kind="AUTHOR_FIT_K0")], fit())
    assert private == [] and report["rate_diagnostic"]["mean_abs_ln_k_error"] is None


@pytest.mark.parametrize("changes", [
    {"candidate_id": "CAL-A"}, {"temperature_C": "NaN"}, {"temperature_C": "110"},
    {"k_raw": "NaN"}, {"k_normalized_min_1": "72.30"}, {"k_raw_unit": "1/hour"},
    {"licence_status": "UNCONFIRMED"}, {"reaction_order": "0"}, {"partition": "SIM-CAL"},
])
def test_inadmissible_rows_are_not_predicted(changes):
    private, report = compare_rows([row(**changes)], fit())
    assert private == [] and sum(report["excluded"].values()) == 1


def test_duplicate_ids_refused_and_inputs_not_mutated():
    rows, model = [row()], fit()
    before = deepcopy((rows, model))
    compare_rows(rows, model)
    assert (rows, model) == before
    with pytest.raises(ValueError, match="duplicate"):
        compare_rows(rows + rows, model)


def test_summary_has_no_individual_observed_or_predicted_rates():
    _, report = compare_rows([row()], fit())
    assert "observed_k" not in str(report) and "predicted_ln_k" not in str(report)


def test_source_precheck_flag_excludes_even_numerically_usable_rate():
    private, report = compare_rows([row()], fit(), source_precheck={"SYN-VAL-1": {
        "status": "FLAG", "computational_eligibility": "EXCLUDE_PENDING_ASSAY_BASIS_REVIEW"}})
    assert private == []
    assert report["excluded"] == {"SOURCE_PRECHECK_NOT_ELIGIBLE": 1}


def test_missing_source_precheck_excludes_rate():
    private, report = compare_rows([row()], fit(), source_precheck={})
    assert private == [] and report["excluded"] == {"SOURCE_PRECHECK_NOT_ELIGIBLE": 1}


@pytest.mark.parametrize("field", ["candidate_id", "row_kind", "pdf_sha256", "source_locator"])
def test_precheck_for_other_source_provenance_cannot_authorize_row(field):
    extracted = {"row_id": "A", "candidate_id": "C", "row_kind": "K_AT_T",
                 "pdf_sha256": "a" * 64, "source_locator": "Table1"}
    checked = {**extracted, field: "different"}
    with pytest.raises(ValueError, match="provenance"):
        tool.validate_source_binding([extracted], [checked])


def test_cli_refuses_public_per_row_destination_without_reading_inputs(tmp_path):
    with pytest.raises(SystemExit):
        tool.main(["--fit", "absent", "--extraction", "absent", "--manifest", "absent",
                   "--source-precheck", "absent", "--private-out", str(tmp_path / "public.csv"),
                   "--out", str(tmp_path / "summary.json")])
    assert not (tmp_path / "public.csv").exists()


def test_cli_manifest_mismatch_refuses_before_fit_use(tmp_path, monkeypatch):
    import json
    monkeypatch.setattr(tool, "ROOT", tmp_path)
    private_dir = tmp_path / "annotation/aa_pilot"
    private_dir.mkdir(parents=True)
    # Stub only the local git-ignore check; manifest validation must still fail closed.
    monkeypatch.setattr(tool.subprocess, "run", lambda *a, **k: type("Ignored", (), {"returncode": 0})())
    extraction, model, manifest = (tmp_path / p for p in ["rows.csv", "fit.json", "manifest.json"])
    extraction.write_text("row_id\nA\n")
    model.write_text("not a model")
    manifest.write_text(json.dumps({"status": "FINAL_EXTRACTION", "extraction_completed_utc": "2026-11-11",
                                    "extraction_sha256": "0" * 64}))
    with pytest.raises(SystemExit):
        tool.main(["--fit", str(model), "--extraction", str(extraction), "--manifest", str(manifest),
                   "--source-precheck", "absent", "--private-out", str(private_dir / "private.csv"),
                   "--out", str(tmp_path / "summary.json")])
    assert not (private_dir / "private.csv").exists()
