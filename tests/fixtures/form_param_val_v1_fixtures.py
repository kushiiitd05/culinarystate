"""SYNTHETIC SCHEMA FIXTURES for the Step 24a FORM / PARAM / VAL v1 DRAFT schemas (S159, DRAFT_PENDING_H4).

Structure only: placeholder strings, fixture ids and dummy numbers (1.0, 2.0 ...). None of these numbers
is a fitted value, a rate constant, an activation energy or a literature value. Nothing here reads a ledger.
Envelope keys follow tests/fixtures/kinetic_v1_1_fixtures.py (KIN v1.1) so the two contracts share names.
"""
from __future__ import annotations

import copy
from typing import Any

Z = "SYNTHETIC-PLACEHOLDER"
NOW = "2026-11-03T00:00:00+00:00"
SCHEMA_VERSION = "1.0.0-draft"
ENERGY_PER_AMOUNT = "ENERGY*AMOUNT^-1"

DISP_NONE: dict[str, Any] = {
    "type": "NONE_REPORTED", "value": None, "low": None, "high": None, "ci_level": None, "unit": None,
    "n_basis": "NOT_APPLICABLE", "scope": "NOT_APPLICABLE", "significance_raw": None, "derivation": "NOT_APPLICABLE"}
LOC: dict[str, Any] = {"doc_id": "DOC-000001", "locator_type": "TABLE_CELL", "page": None, "table_id": None,
                       "row_label": None, "column_label": None, "figure_id": None, "char_span": None, "raw_text": Z}
UNKNOWN_VALUE: dict[str, Any] = {"status": "UNKNOWN", "value": None, "low": None, "high": None}
SI_NC: dict[str, Any] = {"status": "NOT_CONVERTED", "value": None, "unit_si": None}


def env(prefix: str, n: int = 1, record_type: str | None = None) -> dict[str, Any]:
    return {"id": f"{prefix}-{n:06d}", "record_type": record_type or prefix, "schema_version": SCHEMA_VERSION,
            "version": 1, "status": "ACTIVE", "superseded_by": None, "created_at": NOW, "created_by": "fixture",
            "provenance": {"method": "MANUAL", "source_ids": ["SRC-000001"]},
            "verification": {"status": "UNVERIFIED"}, "notes": "SYNTHETIC SCHEMA FIXTURE"}


def slot(symbol: str = "k", *, role: str = "RATE_CONSTANT", dimension: str = "TIME^-1",
         order: float | None = 1, positive: bool = True, needs_t_ref: bool = False) -> dict[str, Any]:
    ro = ({"status": "STATED", "value": order} if order is not None
          else {"status": "NOT_APPLICABLE", "value": None})
    return {"symbol": symbol, "role": role, "dimension": dimension, "reaction_order": ro, "positive": positive,
            "needs_T_ref": needs_t_ref, "description": None}


def form(n: int = 1, *, prefix: str = "FORM", family: str = "FIRST_ORDER",
         slots: list[dict[str, Any]] | None = None, lifecycle: str = "CANDIDATE") -> dict[str, Any]:
    f = env(prefix, n, record_type="FORM")
    f.update({
        "model_discriminator": "FORMULA_MODEL" if prefix == "MODEL" else None,
        "mechanism_ids": ["MECH-000001"], "model_tier": "PRIMARY", "model_family": family, "model_kind": "KINETIC",
        "equation": {"latex": Z, "ast": None, "ast_status": "NOT_YET_WRITTEN", "text_raw": None},
        "state_variables": [{"symbol": "C", "svar_id": None, "dimension": "CONCENTRATION", "description": None}],
        "inputs": [{"name": "tau", "cv_id": None, "required_location": "NOT_APPLICABLE", "dimension": "TIME",
                    "clock": "PROCESS_TAU", "observability_required": True}],
        "parameter_slots": slots if slots is not None else [slot()],
        "assumptions": [{"constraint_expr": Z, "kind": "CONSTRAINT",
                         "consequence": "INVALIDATES_FROM_VIOLATION", "source_note": None}],
        "initial_conditions_required": ["C0"], "boundary_conditions": None,
        "effective_or_mechanistic": "EFFECTIVE",
        "ms_limits": {"status": "NOT_YET_STATED", "medium": [], "temperature_range": None, "pressure_note": None,
                      "phase_note": None, "geometry_class_note": None},
        "calibration_domain_ref": None, "validated_domain_refs": [], "identifiability_status": "NOT_ASSESSED",
        "implementation": None, "solver": {"kind": "ANALYTIC", "curie": None},
        "uncertainty_representation": "NONE_YET", "context_of_use": None, "model_risk_grade": "NOT_ASSESSED",
        "domain_of_verification": None, "credibility_levels": [], "lifecycle_status": lifecycle,
        "reproduction_refs": [], "source_refs": [], "licence_status": "UNKNOWN"})
    return f


def arrhenius_form(n: int = 2, *, prefix: str = "FORM") -> dict[str, Any]:
    return form(n, prefix=prefix, family="ARRHENIUS_SECONDARY", slots=[
        slot("k_ref", needs_t_ref=True),
        slot("Ea", role="ACTIVATION_ENERGY", dimension=ENERGY_PER_AMOUNT, order=None, positive=False)])


def fitted_on(*, kin_lineage_root: str = "LROOT-000001", k_level: str = "K1") -> dict[str, Any]:
    return {"study_ids": ["STUDY-000001"], "lineage_root_ids": [kin_lineage_root],
            "split_group_ids": ["SPLITGRP-EVD-000001"], "lab_group_ids": ["LABGRP-000001"],
            "lineage_status": "ASSIGNED", "matrix": {"ingredient_id": None, "raw_name": Z}, "matrix_class": None,
            "composition_note": None, "process": {"process_id": None, "raw_name": Z}, "design_points": [],
            "k_level": k_level, "measurement": {"meas_id": None, "basis_id": None, "analyte_raw": None},
            "pooling": "SINGLE_SERIES"}


def param(n: int = 1, *, form_id: str = "FORM-000001", slot_symbol: str = "k", value: float | None = 1.0,
          unit: str = "1/min", source_class: str = "AUTHOR_REPORTED", kin_ids: tuple[str, ...] = ("KIN-000001",),
          order: float | None = 1) -> dict[str, Any]:
    p = env("PARAM", n)
    if value is None:
        val: dict[str, Any] = copy.deepcopy(UNKNOWN_VALUE)
    else:
        val = {"status": "MEASURED", "value": value, "unit": unit, "raw": Z}
    prov: dict[str, Any] = {"source_class": source_class, "kin_ids": list(kin_ids), "author_fit_ref": None,
                            "fit_run_id": None, "fitting_library_version": None}
    if source_class == "AUTHOR_REPORTED":
        prov["author_fit_ref"] = {"kin_id": kin_ids[0], "fit_index": 0}
    elif source_class == "PROJECT_REFIT":
        prov.update(fit_run_id="FITRUN-0123456789abcdef", fitting_library_version="fixture")
    p.update({
        "form_id": form_id, "slot_symbol": slot_symbol, "symbol_source": None, "symbol_canonical": slot_symbol,
        "conversion_note": None, "value": val, "value_si": dict(SI_NC), "distribution": None,
        "reaction_order": ({"status": "STATED", "value": order} if order is not None
                           else {"status": "NOT_APPLICABLE", "value": None}),
        "T_ref": None, "estimation_method": "NOT_REPORTED", "ci": copy.deepcopy(DISP_NONE),
        "ci_method": "NOT_REPORTED", "correlation_with": [], "value_provenance": prov, "fitted_on": fitted_on(),
        "fit_T_range": None, "fit_tau_range": None, "effective_or_mechanistic": "EFFECTIVE",
        "source_locator": ({"locator": copy.deepcopy(LOC), "data_origin": "TABLE",
                            "digitisation_uncertainty": copy.deepcopy(DISP_NONE)}
                           if source_class == "AUTHOR_REPORTED" else None),
        "extraction_version": None, "partition": "PENDING_15B"})
    return p


def unknown_param(n: int = 9) -> dict[str, Any]:
    """A slot whose value is UNKNOWN (a valid answer): no number, no fit, provenance says UNKNOWN."""
    return param(n, value=None, source_class="UNKNOWN", kin_ids=())


METRIC_KEYS = ("ln_ret_err", "rmse_natural", "bias_factor", "accuracy_factor", "cov80", "cov95", "width", "crps",
               "vv20_E_vs_uval")


def val(n: int = 1, *, form_id: str = "FORM-000001", param_ids: tuple[str, ...] = ("PARAM-000001",),
        eval_ids: tuple[str, ...] = ("KIN-000002",), tier: str = "V1_IN_DOMAIN") -> dict[str, Any]:
    v = env("VAL", n)
    v.update({
        "form_id": form_id, "param_set_ids": list(param_ids), "eval_series_ids": list(eval_ids),
        "study_disjoint": {"status": "UNKNOWN", "lineage_proof": None}, "matrix_relation": "UNKNOWN",
        "tier": tier, "condition_points": [],
        "metrics": {k: copy.deepcopy(UNKNOWN_VALUE) for k in METRIC_KEYS},
        "verdict": "NOT_EVALUATED", "preregistration_ref": None, "val_plan_sha256": None,
        "may_define_validated_domain": False})
    return v
