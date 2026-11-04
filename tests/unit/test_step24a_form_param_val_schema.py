"""Record-level tests for the Step 24a FORM / PARAM / VAL v1 DRAFT schemas (S159, DRAFT_PENDING_H4).

Fixtures are SYNTHETIC SCHEMA FIXTURES (tests/fixtures/form_param_val_v1_fixtures.py): placeholder strings and
dummy numbers, never data. A passing test is evidence about the drafts' logic only; it is not H4 approval,
it does not decide the FORM- versus MODEL- prefix (24f) and it signs nothing.
"""
from __future__ import annotations

import copy
import json
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from tests.fixtures import form_param_val_v1_fixtures as F

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "registry" / "schemas"
FILES = {"FORM": "FORM.draft_v1.schema.json", "PARAM": "PARAM.draft_v1.schema.json",
         "VAL": "VAL.draft_v1.schema.json"}
SHARED_DEFS = ("value_obj", "dispersion", "count", "locator", "matrix", "process", "time_conversion")


def load(name: str) -> dict[str, Any]:
    return json.loads((SCHEMAS / FILES[name]).read_text(encoding="utf-8"))


def kin_schema() -> dict[str, Any]:
    return json.loads((SCHEMAS / "KIN.draft_v1_1.schema.json").read_text(encoding="utf-8"))


def errors(name: str, record: dict[str, Any]) -> list[str]:
    schema = {k: v for k, v in load(name).items() if k != "$id"}
    return sorted(e.message for e in Draft202012Validator(schema).iter_errors(record))


def walk(node: Any) -> Iterator[tuple[str, Any]]:
    if isinstance(node, dict):
        for k, v in node.items():
            yield k, v
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


# ----------------------------------------------------------------------------- structure
@pytest.mark.parametrize("name", sorted(FILES))
def test_schema_is_a_valid_draft_2020_12_document_marked_draft_pending_h4(name: str) -> None:
    s = load(name)
    assert s["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(s)
    assert "DRAFT_PENDING_H4" in s["title"] and "STATUS DRAFT_PENDING_H4" in s["description"]
    assert s["additionalProperties"] is False
    assert s["properties"]["record_type"] == {"const": name}


@pytest.mark.parametrize("name", sorted(FILES))
def test_schema_holds_no_default_value_anywhere(name: str) -> None:
    assert [k for k, _ in walk(load(name)) if k == "default"] == []


@pytest.mark.parametrize("name", sorted(FILES))
@pytest.mark.parametrize("d", SHARED_DEFS)
def test_shared_defs_are_identical_to_kin_v1_1(name: str, d: str) -> None:
    assert load(name)["$defs"][d] == kin_schema()["$defs"][d]


@pytest.mark.parametrize("name", sorted(FILES))
@pytest.mark.parametrize("key", ["provenance", "verification", "status", "version", "created_at", "created_by"])
def test_envelope_fields_are_identical_to_kin_v1_1(name: str, key: str) -> None:
    assert load(name)["properties"][key] == kin_schema()["properties"][key]


def test_vocabularies_are_shared_with_kin_v1_1() -> None:
    kin = kin_schema()
    fit = kin["properties"]["fit"]["items"]["properties"]
    form, param = load("FORM")["properties"], load("PARAM")["properties"]
    assert form["model_family"]["enum"] == fit["candidate_model_family"]["enum"]
    assert form["effective_or_mechanistic"] == fit["effective_or_mechanistic"]
    assert form["licence_status"] == kin["properties"]["licence_status"]
    assert param["estimation_method"]["enum"] == fit["fit_method"]["enum"]
    assert param["effective_or_mechanistic"] == fit["effective_or_mechanistic"]
    fo = load("PARAM")["$defs"]["fitted_on"]["properties"]
    assert fo["k_level"]["enum"] == kin["properties"]["k_level"]["properties"]["value"]["enum"]
    time_units = kin["properties"]["time_base"]["properties"]["unit"]["enum"]
    assert load("PARAM")["$defs"]["tau_range"]["properties"]["unit"]["enum"] == time_units
    assert load("PARAM")["$defs"]["tau_range"]["properties"]["clock"] == {"const": "PROCESS_TAU"}


def test_id_patterns_and_configurable_form_prefix() -> None:
    form = load("FORM")["properties"]
    assert form["id"]["pattern"] == "^(FORM|MODEL)-\\d{6}$"
    assert load("PARAM")["properties"]["form_id"]["pattern"] == "^(FORM|MODEL)-\\d{6}$"
    assert load("VAL")["properties"]["form_id"]["pattern"] == "^(FORM|MODEL)-\\d{6}$"
    assert load("PARAM")["properties"]["id"]["pattern"] == "^PARAM-\\d{6}$"
    assert load("VAL")["properties"]["id"]["pattern"] == "^VAL-\\d{6}$"


def test_parameter_slots_cannot_carry_a_value() -> None:
    slot = load("FORM")["$defs"]["parameter_slot"]
    assert slot["additionalProperties"] is False
    assert not {"value", "estimate", "default"} & set(slot["properties"])


def test_val_metrics_exclude_fit_statistics() -> None:
    metrics = load("VAL")["properties"]["metrics"]
    assert metrics["additionalProperties"] is False
    assert set(metrics["properties"]) == set(F.METRIC_KEYS)


# ----------------------------------------------------------------------------- valid fixtures
VALID: dict[str, Callable[[], tuple[str, dict[str, Any]]]] = {
    "form_first_order": lambda: ("FORM", F.form()),
    "form_arrhenius": lambda: ("FORM", F.arrhenius_form()),
    "form_model_prefix_with_discriminator": lambda: ("FORM", F.form(prefix="MODEL")),
    "param_author_reported": lambda: ("PARAM", F.param()),
    "param_project_refit": lambda: ("PARAM", F.param(source_class="PROJECT_REFIT")),
    "param_unknown_value": lambda: ("PARAM", F.unknown_param()),
    "val_not_evaluated": lambda: ("VAL", F.val()),
}


def _range_param() -> dict[str, Any]:
    p = F.param()
    p["value"] = {"status": "RANGE", "low": 1.0, "high": 2.0, "unit": "1/min", "value": None}
    return p


def _reproduced_form() -> dict[str, Any]:
    f = F.form(lifecycle="REPRODUCED")
    f["implementation"] = {"path": "src/x.py", "code_sha256": "0" * 64, "library_version": "fixture"}
    f["reproduction_refs"] = ["reports/step24/reproduction_report.md#fixture"]
    return f


def _validated_val() -> dict[str, Any]:
    v = F.val()
    v.update(verdict="MEETS_PREREGISTERED_CRITERIA", preregistration_ref="THR-FIXTURE",
             may_define_validated_domain=True, study_disjoint={"status": "YES", "lineage_proof": Z_PROOF})
    return v


Z_PROOF = "fixture lineage proof"
VALID.update({
    "param_range_value": lambda: ("PARAM", _range_param()),
    "form_reproduced": lambda: ("FORM", _reproduced_form()),
    "val_meets_criteria_may_define": lambda: ("VAL", _validated_val()),
    "val_v3_may_not_define": lambda: ("VAL", F.val(tier="V3_HELDOUT_MATRIX")),
})


@pytest.mark.parametrize("case", sorted(VALID))
def test_valid_fixture(case: str) -> None:
    name, rec = VALID[case]()
    assert errors(name, rec) == []


# ----------------------------------------------------------------------------- negative controls
def _m(builder: Callable[[], dict[str, Any]], fn: Callable[[dict[str, Any]], None]) -> Callable[[], dict[str, Any]]:
    def make() -> dict[str, Any]:
        r = copy.deepcopy(builder())
        fn(r)
        return r
    return make


def _set(path: str, value: Any) -> Callable[[dict[str, Any]], None]:
    def fn(r: dict[str, Any]) -> None:
        node = r
        *head, last = path.split(".")
        for k in head:
            node = node[int(k)] if isinstance(node, list) else node[k]
        node[last] = value
    return fn


def _del(key: str) -> Callable[[dict[str, Any]], None]:
    return lambda r: r.pop(key)


NEGATIVE: dict[str, tuple[str, Callable[[], dict[str, Any]]]] = {
    # FORM
    "form_bad_prefix": ("FORM", _m(F.form, _set("id", "FOO-000001"))),
    "form_model_prefix_without_discriminator": ("FORM", _m(lambda: F.form(prefix="MODEL"),
                                                           _set("model_discriminator", None))),
    "form_form_prefix_with_discriminator": ("FORM", _m(F.form, _set("model_discriminator", "FORMULA_MODEL"))),
    "form_slot_with_value": ("FORM", _m(F.form, _set("parameter_slots.0.value", 1.0))),
    "form_slot_with_default": ("FORM", _m(F.form, _set("parameter_slots.0.default", 1.0))),
    "form_reproduced_without_reproduction_refs": ("FORM", _m(_reproduced_form, _set("reproduction_refs", []))),
    "form_reproduced_without_implementation": ("FORM", _m(_reproduced_form, _set("implementation", None))),
    "form_calibrated_without_calibration_domain": ("FORM", _m(_reproduced_form,
                                                              _set("lifecycle_status", "CALIBRATED"))),
    "form_validated_domain_before_validation": ("FORM", _m(F.form, _set("validated_domain_refs", ["VAL-000001"]))),
    "form_validated_without_val": ("FORM", _m(_reproduced_form, lambda r: r.update(
        lifecycle_status="VALIDATED_HELD_OUT", calibration_domain_ref="fixture"))),
    "form_kisao_without_curie": ("FORM", _m(F.form, _set("solver", {"kind": "KISAO", "curie": None}))),
    "form_unknown_family": ("FORM", _m(F.form, _set("model_family", "EXPONENTIAL_GUESS"))),
    "form_extra_property": ("FORM", _m(F.form, _set("rate_constant", 1.0))),
    "form_input_unspecified_location": ("FORM", _m(F.form, _set("inputs.0.required_location", "UNSPECIFIED"))),
    # PARAM: provenance
    "param_number_without_source_class": ("PARAM", _m(F.param, _set("value_provenance.source_class", "UNKNOWN"))),
    "param_missing_provenance": ("PARAM", _m(F.param, _del("value_provenance"))),
    "param_author_without_fit_ref": ("PARAM", _m(F.param, _set("value_provenance.author_fit_ref", None))),
    "param_author_without_kin_ids": ("PARAM", _m(F.param, _set("value_provenance.kin_ids", []))),
    "param_author_without_locator": ("PARAM", _m(F.param, _set("source_locator", None))),
    "param_refit_without_fit_run": ("PARAM", _m(lambda: F.param(source_class="PROJECT_REFIT"),
                                                _set("value_provenance.fit_run_id", None))),
    "param_refit_bad_fit_run_id": ("PARAM", _m(lambda: F.param(source_class="PROJECT_REFIT"),
                                               _set("value_provenance.fit_run_id", "FIT-1"))),
    "param_refit_without_library_version": ("PARAM", _m(lambda: F.param(source_class="PROJECT_REFIT"),
                                                        _set("value_provenance.fitting_library_version", None))),
    "param_refit_with_author_ref": ("PARAM", _m(lambda: F.param(source_class="PROJECT_REFIT"),
                                                _set("value_provenance.author_fit_ref",
                                                     {"kin_id": "KIN-000001", "fit_index": 0}))),
    "param_unknown_with_fit_run": ("PARAM", _m(F.unknown_param,
                                               _set("value_provenance.fit_run_id", "FITRUN-0123456789abcdef"))),
    # PARAM: values and rules
    "param_qualitative_value": ("PARAM", _m(F.param, _set("value", {"status": "QUALITATIVE", "qualitative": "x"}))),
    "param_censored_value": ("PARAM", _m(F.param, _set("value", {"status": "CENSORED", "unit": "1/min"}))),
    "param_from_k0": ("PARAM", _m(F.param, _set("fitted_on.k_level", "K0"))),
    "param_single_study_pooling_two_studies": ("PARAM", _m(F.param, lambda r: r["fitted_on"].update(
        pooling="SINGLE_STUDY", study_ids=["STUDY-000001", "STUDY-000002"]))),
    "param_si_exact_without_value": ("PARAM", _m(F.param, _set("value_si", {"status": "CONVERTED_EXACT",
                                                                            "value": None, "unit_si": None}))),
    "param_si_not_converted_with_value": ("PARAM", _m(F.param, _set("value_si", {"status": "NOT_CONVERTED",
                                                                                 "value": 1.0, "unit_si": "1/s"}))),
    "param_bad_partition": ("PARAM", _m(F.param, _set("partition", "TEST"))),
    "param_tau_range_wrong_clock": ("PARAM", _m(F.param, _set("fit_tau_range", {
        "clock": "WALL_CLOCK", "unit": "min", "unit_raw": "min", "low": 0, "high": 1,
        "low_seconds": {"status": "NOT_CONVERTED", "value": None, "convention": None},
        "high_seconds": {"status": "NOT_CONVERTED", "value": None, "convention": None}}))),
    "param_recipe_plane_split_group": ("PARAM", _m(F.param, _set("fitted_on.split_group_ids",
                                                                 ["SPLITGRP-REC-000001"]))),
    "param_bad_form_id": ("PARAM", _m(F.param, _set("form_id", "MECH-000001"))),
    "param_correlation_out_of_range": ("PARAM", _m(F.param, _set("correlation_with", [
        {"param_id": "PARAM-000002", "value": 1.5, "status": "REPORTED"}]))),
    # VAL
    "val_v3_may_define": ("VAL", _m(_validated_val, _set("tier", "V3_HELDOUT_MATRIX"))),
    "val_not_disjoint_may_define": ("VAL", _m(_validated_val, _set("study_disjoint",
                                                                   {"status": "NO", "lineage_proof": None}))),
    "val_not_evaluated_may_define": ("VAL", _m(F.val, _set("may_define_validated_domain", True))),
    "val_fit_statistic_r2": ("VAL", _m(F.val, _set("metrics.r2", dict(F.UNKNOWN_VALUE)))),
    "val_fit_statistic_aic": ("VAL", _m(F.val, _set("metrics.aic", dict(F.UNKNOWN_VALUE)))),
    "val_verdict_without_prereg": ("VAL", _m(_validated_val, _set("preregistration_ref", None))),
    "val_no_params": ("VAL", _m(F.val, _set("param_set_ids", []))),
    "val_no_eval_series": ("VAL", _m(F.val, _set("eval_series_ids", []))),
    "val_disjoint_without_proof": ("VAL", _m(_validated_val, _set("study_disjoint",
                                                                  {"status": "YES", "lineage_proof": None}))),
    "val_metric_missing": ("VAL", _m(F.val, lambda r: r["metrics"].pop("crps"))),
}


@pytest.mark.parametrize("case", sorted(NEGATIVE))
def test_negative_control_is_rejected(case: str) -> None:
    name, make = NEGATIVE[case]
    assert errors(name, make()) != [], case
