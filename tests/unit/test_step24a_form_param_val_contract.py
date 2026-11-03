"""Cross-record tests of the Step 24a FORM / PARAM / VAL validator (S159, DRAFT_PENDING_H4).

SYNTHETIC SCHEMA FIXTURES only (tests/fixtures/form_param_val_v1_fixtures.py and kinetic_v1_1_fixtures.py):
placeholder strings and dummy numbers. No value here is a rate constant, an activation energy or a literature
value. The FORM- versus MODEL- prefix (24f) is not decided: every call names the prefix it checks against.
"""
from __future__ import annotations

import copy
import inspect
from typing import Any

import pytest

from culinarystate.mechanism import form_param_val as FPV
from tests.fixtures import form_param_val_v1_fixtures as F
from tests.fixtures import kinetic_v1_1_fixtures as KF

OPAQUE = {"u": "CONCENTRATION"}


def codes(issues: list[Any], severity: str | None = "ERROR") -> set[str]:
    return {i.code for i in issues if severity is None or i.severity == severity}


def kin_with_author_fit(n: int = 1, *, k_level: str = "K1", root: str = "LROOT-000001") -> dict[str, Any]:
    k = KF.kin(n)
    k["k_level"] = {"value": k_level, "scope": "SERIES_ONLY", "classifier_version": "fixture"}
    k["lineage"]["lineage_root_id"] = root
    k["fit"] = [{"fit_origin": "AUTHOR_REPORTED", "candidate_model_family": "FIRST_ORDER", "parameters": []}]
    return k


def forms() -> dict[str, dict[str, Any]]:
    return {f["id"]: f for f in (F.form(), F.arrhenius_form())}


def kins(**kw: Any) -> dict[str, dict[str, Any]]:
    k = kin_with_author_fit(**kw)
    return {k["id"]: k}


def vp(p: dict[str, Any], **kw: Any) -> list[Any]:
    kw.setdefault("forms_by_id", forms())
    kw.setdefault("opaque_units", OPAQUE)
    return FPV.validate_param(p, form_id_prefix=kw.pop("form_id_prefix", "FORM"), **kw)


# ----------------------------------------------------------------------------- module contract
def test_module_status_and_open_prefix_decision() -> None:
    assert FPV.STATUS == "DRAFT_PENDING_H4"
    assert FPV.FORM_ID_PREFIX_OPTIONS == ("FORM", "MODEL")
    assert FPV.FORM_ID_PREFIX_DECISION == "OPEN_24f_H4"
    assert any("24f" in item for item in FPV.OPEN_FOR_HUMANS)
    assert FPV.ELIGIBLE == "ELIGIBLE_UNDER_DRAFT_RULES"


@pytest.mark.parametrize("fn", ["validate_form", "validate_param", "validate_val", "calibration_eligibility"])
def test_prefix_is_a_required_keyword_without_default(fn: str) -> None:
    p = inspect.signature(getattr(FPV, fn)).parameters["form_id_prefix"]
    assert p.kind is inspect.Parameter.KEYWORD_ONLY and p.default is inspect.Parameter.empty


def test_unknown_prefix_is_refused() -> None:
    with pytest.raises(FPV.FormParamValError):
        FPV.validate_form(F.form(), form_id_prefix="FORMULA")


def test_schema_errors_dispatch() -> None:
    assert FPV.schema_errors(F.form(), "FORM") == []
    assert FPV.schema_errors(F.param(), "PARAM") == []
    assert FPV.schema_errors(F.val(), "VAL") == []
    with pytest.raises(ValueError):
        FPV.schema_errors(F.form(), "KIN")


def test_validators_do_not_mutate_inputs() -> None:
    f, p, v = F.form(), F.param(), F.val()
    fs, ps, ks = forms(), {p["id"]: p}, kins()
    snap = copy.deepcopy((f, p, v, fs, ps, ks))
    FPV.validate_form(f, form_id_prefix="FORM")
    vp(p, kins_by_id=ks)
    FPV.validate_val(v, form_id_prefix="FORM", forms_by_id=fs, params_by_id=ps, kins_by_id=ks)
    assert (f, p, v, fs, ps, ks) == snap


# ----------------------------------------------------------------------------- FORM
def test_form_fixtures_pass_under_their_own_prefix() -> None:
    assert codes(FPV.validate_form(F.form(), form_id_prefix="FORM")) == set()
    assert codes(FPV.validate_form(F.arrhenius_form(), form_id_prefix="FORM")) == set()
    assert codes(FPV.validate_form(F.form(prefix="MODEL"), form_id_prefix="MODEL")) == set()


def test_form_prefix_mismatch_under_the_other_option() -> None:
    assert "FORM_ID_PREFIX_MISMATCH" in codes(FPV.validate_form(F.form(), form_id_prefix="MODEL"))
    assert "FORM_ID_PREFIX_MISMATCH" in codes(FPV.validate_form(F.form(prefix="MODEL"), form_id_prefix="FORM"))


def test_form_schema_violation_is_an_issue() -> None:
    f = F.form()
    f["parameter_slots"][0]["value"] = 1.0
    assert "SCHEMA_INVALID" in codes(FPV.validate_form(f, form_id_prefix="FORM"))


@pytest.mark.parametrize("slots, code", [
    ([F.slot("k"), F.slot("k")], "SLOT_SYMBOL_DUPLICATE"),
    ([F.slot("k", dimension="FURLONG^-1")], "SLOT_DIMENSION_UNPARSEABLE"),
    ([F.slot("k", dimension="CONCENTRATION*TIME^-1", order=1)], "RATE_CONSTANT_DIMENSION_ORDER_MISMATCH"),
    ([F.slot("k", dimension="TIME^-1", order=0)], "RATE_CONSTANT_DIMENSION_ORDER_MISMATCH"),
    ([F.slot("Ea", role="ACTIVATION_ENERGY", dimension="ENERGY", order=None)], "ACTIVATION_ENERGY_DIMENSION_MISMATCH"),
    ([F.slot("T_ref", role="REFERENCE_TEMPERATURE", dimension="TIME", order=None)],
     "REFERENCE_TEMPERATURE_DIMENSION_MISMATCH"),
])
def test_form_slot_rules(slots: list[dict[str, Any]], code: str) -> None:
    assert code in codes(FPV.validate_form(F.form(slots=slots), form_id_prefix="FORM"))


@pytest.mark.parametrize("order, dim", [(0, "CONCENTRATION*TIME^-1"), (1, "TIME^-1"),
                                        (2, "CONCENTRATION^-1*TIME^-1"), (1.5, "CONCENTRATION^-1/2*TIME^-1")])
def test_rate_constant_dimension_follows_the_order(order: float, dim: str) -> None:
    assert codes(FPV.validate_form(F.form(slots=[F.slot("k", dimension=dim, order=order)]),
                                   form_id_prefix="FORM")) == set()


def test_rate_constant_with_unknown_order_is_a_warning_not_an_error() -> None:
    s = F.slot("k")
    s["reaction_order"] = {"status": "UNKNOWN", "value": None}
    issues = FPV.validate_form(F.form(slots=[s]), form_id_prefix="FORM")
    assert codes(issues) == set() and "RATE_CONSTANT_ORDER_UNKNOWN" in codes(issues, "WARN")


def test_validated_domain_refs_need_defining_val_records() -> None:
    f = F.form()
    f["validated_domain_refs"] = ["VAL-000001", "VAL-000002"]
    defining = F.val(1)
    defining.update(may_define_validated_domain=True)
    non_defining = F.val(2, tier="V3_HELDOUT_MATRIX")
    got = codes(FPV.validated_domain_issues(f, {"VAL-000001": defining, "VAL-000002": non_defining}))
    assert got == {"VALIDATED_DOMAIN_FROM_NON_DEFINING_VAL"}
    assert codes(FPV.validated_domain_issues(f, {})) == {"VALIDATED_DOMAIN_REF_MISSING"}


# ----------------------------------------------------------------------------- PARAM
def test_param_fixture_passes_with_its_kin() -> None:
    assert codes(vp(F.param(), kins_by_id=kins())) == set()


def test_unknown_param_is_valid() -> None:
    assert codes(vp(F.unknown_param(), kins_by_id=kins())) == set()


def test_param_without_provenance_is_rejected() -> None:
    p = F.param()
    del p["value_provenance"]
    assert "SCHEMA_INVALID" in codes(vp(p))
    p = F.param()
    p["value_provenance"]["source_class"] = "UNKNOWN"
    assert "SCHEMA_INVALID" in codes(vp(p))


def test_param_form_resolution_and_prefix() -> None:
    assert "PARAM_FORM_MISSING" in codes(vp(F.param(form_id="FORM-000099")))
    assert "FORM_ID_PREFIX_MISMATCH" in codes(vp(F.param(form_id="MODEL-000001")))
    assert "PARAM_SLOT_NOT_IN_FORM" in codes(vp(F.param(slot_symbol="k_ref2")))


@pytest.mark.parametrize("unit, code", [
    ("1/min", None), ("min^-1", None), ("1/h", None), ("s^-1", None),
    ("u/min", "PARAM_UNIT_DIMENSION_MISMATCH"), ("min", "PARAM_UNIT_DIMENSION_MISMATCH"),
    ("1/degC", "PARAM_UNIT_DIMENSION_MISMATCH"),
])
def test_param_unit_dimension_against_slot(unit: str, code: str | None) -> None:
    got = codes(vp(F.param(unit=unit)))
    assert (code in got) if code else not ({"PARAM_UNIT_DIMENSION_MISMATCH"} & got)


def test_param_unit_with_unknown_token_is_a_warning() -> None:
    issues = vp(F.param(unit="1/fortnight"))
    assert "PARAM_UNIT_UNKNOWN" in codes(issues, "WARN") and "PARAM_UNIT_DIMENSION_MISMATCH" not in codes(issues)


def test_zero_order_param_needs_the_declared_opaque_concentration_unit() -> None:
    f = F.form(3, family="ZERO_ORDER", slots=[F.slot("k0", dimension="CONCENTRATION*TIME^-1", order=0)])
    p = F.param(form_id="FORM-000003", slot_symbol="k0", unit="u/min", order=0)
    assert codes(vp(p, forms_by_id={f["id"]: f})) == set()
    assert "PARAM_UNIT_UNKNOWN" in codes(vp(p, forms_by_id={f["id"]: f}, opaque_units={}), "WARN")


def test_param_order_must_match_slot() -> None:
    assert "PARAM_ORDER_MISMATCH_WITH_SLOT" in codes(vp(F.param(order=2)))


@pytest.mark.parametrize("value", [-1.0, 0.0])
def test_positive_slot_rejects_non_positive_value(value: float) -> None:
    assert "PARAM_NOT_POSITIVE" in codes(vp(F.param(value=value)))


def test_positive_slot_rejects_non_positive_range() -> None:
    p = F.param()
    p["value"] = {"status": "RANGE", "low": -1.0, "high": 2.0, "unit": "1/min", "value": None}
    assert "PARAM_NOT_POSITIVE" in codes(vp(p))


def _arr_param(**kw: Any) -> dict[str, Any]:
    p = F.param(form_id="FORM-000002", slot_symbol="k_ref", **kw)
    p["T_ref"] = {"status": "MEASURED", "value": 1.0, "unit": "K"}
    return p


def test_t_ref_rules() -> None:
    assert codes(vp(_arr_param())) == set()
    p = _arr_param()
    p["T_ref"] = None
    assert "PARAM_T_REF_REQUIRED" in codes(vp(p))
    p = _arr_param()
    p["T_ref"] = {"status": "MEASURED", "value": 1.0, "unit": "degC"}
    assert "T_REF_NOT_KELVIN" in codes(vp(p))
    p = _arr_param()
    p["T_ref"] = {"status": "UNKNOWN"}
    assert codes(vp(p)) == set()


@pytest.mark.parametrize("unit, ok", [("kJ/mol", True), ("J/mol", True), ("J*mol^-1", True), ("kJ", False),
                                      ("kJ/(mol*K)", False)])
def test_activation_energy_unit(unit: str, ok: bool) -> None:
    p = F.param(form_id="FORM-000002", slot_symbol="Ea", unit=unit, order=None)
    got = codes(vp(p))
    assert ("PARAM_UNIT_DIMENSION_MISMATCH" not in got) is ok


def test_si_conversion_is_checked_and_raw_value_is_kept() -> None:
    p = F.param()
    p["value_si"] = {"status": "CONVERTED_EXACT", "value": 1.0 / 60.0, "unit_si": "1/s"}
    assert codes(vp(p)) == set()
    p["value_si"]["value"] = 1.0
    assert "PARAM_SI_CONVERSION_MISMATCH" in codes(vp(p))
    p = F.param(unit="1/month")
    p["value_si"] = {"status": "CONVERTED_EXACT", "value": 1.0, "unit_si": "1/s"}
    assert "PARAM_SI_NOT_EXACT" in codes(vp(p))
    p = F.param()
    p["value_si"] = {"status": "CONVERTED_EXACT", "value": 1.0 / 60.0, "unit_si": "s"}
    assert "PARAM_SI_UNIT_DIMENSION_MISMATCH" in codes(vp(p))


def test_provenance_cross_checks_against_kin() -> None:
    assert "PROVENANCE_KIN_MISSING" in codes(vp(F.param(), kins_by_id={}))
    p = F.param(kin_ids=("KIN-000001", "KIN-000002"))
    p["value_provenance"]["author_fit_ref"] = {"kin_id": "KIN-000003", "fit_index": 0}
    assert "AUTHOR_FIT_REF_NOT_IN_KIN_IDS" in codes(vp(p))
    p = F.param()
    p["value_provenance"]["author_fit_ref"]["fit_index"] = 3
    assert "AUTHOR_FIT_REF_MISSING" in codes(vp(p, kins_by_id=kins()))
    k = kins()
    k["KIN-000001"]["fit"][0]["fit_origin"] = "PROJECT_REFIT"
    assert "AUTHOR_FIT_ORIGIN_MISMATCH" in codes(vp(F.param(), kins_by_id=k))


def test_param_from_k0_series_is_rejected() -> None:
    assert "PARAM_FROM_K0_AGGREGATE" in codes(vp(F.param(), kins_by_id=kins(k_level="K0")))


def test_fitted_on_lineage_must_match_the_kin_series() -> None:
    assert "FITTED_ON_LINEAGE_MISMATCH" in codes(vp(F.param(), kins_by_id=kins(root="LROOT-000777")))


def test_pooling_without_hierarchy_is_rejected() -> None:
    p = F.param()
    p["fitted_on"].update(pooling="POOLED_NON_HIERARCHICAL", study_ids=["STUDY-000001", "STUDY-000002"])
    assert "POOLING_WITHOUT_HIERARCHY" in codes(vp(p))


def test_project_refit_param_passes() -> None:
    assert codes(vp(F.param(source_class="PROJECT_REFIT"), kins_by_id=kins())) == set()


# ----------------------------------------------------------------------------- VAL
def _val_ctx(**kw: Any) -> dict[str, Any]:
    p = F.param()
    ctx: dict[str, Any] = {"forms_by_id": forms(), "params_by_id": {p["id"]: p}}
    ctx.update(kw)
    return ctx


def test_val_fixture_passes() -> None:
    assert codes(FPV.validate_val(F.val(), form_id_prefix="FORM", **_val_ctx())) == set()


def test_val_resolution_errors() -> None:
    assert "VAL_FORM_MISSING" in codes(FPV.validate_val(F.val(form_id="FORM-000099"), form_id_prefix="FORM",
                                                        **_val_ctx()))
    assert "VAL_PARAM_MISSING" in codes(FPV.validate_val(F.val(param_ids=("PARAM-000042",)), form_id_prefix="FORM",
                                                         **_val_ctx()))
    assert "VAL_PARAM_FORM_MISMATCH" in codes(FPV.validate_val(F.val(form_id="FORM-000002"), form_id_prefix="FORM",
                                                               **_val_ctx()))
    assert "FORM_ID_PREFIX_MISMATCH" in codes(FPV.validate_val(F.val(), form_id_prefix="MODEL", **_val_ctx()))


def test_val_eval_series_used_in_fit() -> None:
    v = F.val(eval_ids=("KIN-000001",))
    assert "VAL_EVAL_SERIES_USED_IN_FIT" in codes(FPV.validate_val(v, form_id_prefix="FORM", **_val_ctx()))


def test_val_study_disjoint_claim_checked_against_lineage() -> None:
    v = F.val()
    v["study_disjoint"] = {"status": "YES", "lineage_proof": "fixture"}
    same_root = kin_with_author_fit(2, root="LROOT-000001")
    other_root = kin_with_author_fit(2, root="LROOT-000002")
    got = codes(FPV.validate_val(v, form_id_prefix="FORM", **_val_ctx(kins_by_id={"KIN-000002": same_root})))
    assert "VAL_NOT_STUDY_DISJOINT" in got
    got = codes(FPV.validate_val(v, form_id_prefix="FORM", **_val_ctx(kins_by_id={"KIN-000002": other_root})))
    assert "VAL_NOT_STUDY_DISJOINT" not in got


# ----------------------------------------------------------------------------- calibration eligibility
def _verified(p: dict[str, Any]) -> dict[str, Any]:
    # Schema-shaped placeholder only (KIN v1.1 admits verifier Kush / Parv; same pattern as the S158 KIN tests).
    # No human verified anything: this is a SYNTHETIC SCHEMA FIXTURE.
    p["verification"] = {"status": "HUMAN_VERIFIED", "verifier": "Kush", "verified_at": F.NOW}
    p["partition"] = "SIM_CALIBRATION"
    return p


def elig(p: dict[str, Any], *, ks: dict[str, Any] | None = None, locked: frozenset[str] = frozenset()) -> Any:
    return FPV.calibration_eligibility(p, form_id_prefix="FORM", forms_by_id=forms(),
                                       kins_by_id=kins() if ks is None else ks, locked_lineage_root_ids=locked,
                                       opaque_units=OPAQUE)


def test_eligible_only_under_draft_rules() -> None:
    e = elig(_verified(F.param()))
    assert e.verdict == FPV.ELIGIBLE and e.reasons == ()


def test_unverified_or_unpartitioned_is_unknown() -> None:
    e = elig(F.param())
    assert e.verdict == FPV.UNKNOWN
    assert {"NOT_HUMAN_VERIFIED", "PARTITION_PENDING"} <= set(e.reasons)


@pytest.mark.parametrize("mutate, reason", [
    (lambda p: p.update(partition="SIM_VALIDATION_LOCKED"), "PARTITION_NOT_SIM_CALIBRATION"),
    (lambda p: p.update(partition="DOWNSTREAM_TRAIN"), "PARTITION_NOT_SIM_CALIBRATION"),
    (lambda p: p["verification"].update(status="HUMAN_REJECTED"), "HUMAN_REJECTED"),
    (lambda p: p.update(status="RETRACTED"), "RECORD_NOT_ACTIVE"),
])
def test_not_eligible_cases(mutate: Any, reason: str) -> None:
    p = _verified(F.param())
    mutate(p)
    e = elig(p)
    assert e.verdict == FPV.NOT_ELIGIBLE and reason in e.reasons


def test_unknown_value_is_never_eligible() -> None:
    e = elig(_verified(F.unknown_param()))
    assert e.verdict == FPV.NOT_ELIGIBLE and "VALUE_UNKNOWN" in e.reasons


def test_locked_lineage_root_is_not_eligible() -> None:
    e = elig(_verified(F.param()), locked=frozenset({"LROOT-000001"}))
    assert e.verdict == FPV.NOT_ELIGIBLE and "FITTED_ON_SIM_VAL_LINEAGE" in e.reasons


def test_k0_kin_is_not_eligible_and_missing_or_unknown_kin_is_unknown() -> None:
    assert elig(_verified(F.param()), ks=kins(k_level="K0")).verdict == FPV.NOT_ELIGIBLE
    e = elig(_verified(F.param()), ks={})
    assert e.verdict == FPV.NOT_ELIGIBLE  # a validator ERROR (PROVENANCE_KIN_MISSING) is never eligible
    e = elig(_verified(F.param()), ks=kins(k_level="UNKNOWN"))
    assert e.verdict == FPV.UNKNOWN and "KIN_K_LEVEL_UNKNOWN" in e.reasons


def test_unknown_t_ref_makes_calibration_use_unknown() -> None:
    p = _verified(_arr_param())
    p["T_ref"] = {"status": "UNKNOWN"}
    e = elig(p)
    assert e.verdict == FPV.UNKNOWN and "T_REF_UNKNOWN" in e.reasons
