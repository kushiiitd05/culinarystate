"""Separate, non-citable CAL sensitivities; frozen Model A and its code stay untouched.

Inputs are already licence-admissible, AI-prechecked K_AT_T rows in min^-1.
This module never opens source text, SIM-VAL, a ledger or a frozen output.
"""
from __future__ import annotations

import math
from collections import Counter

import numpy as np

from . import aa_pilot_fit as frozen

LABELS = ["DIAGNOSTIC", "NON_CITABLE", "AI_PRECHECKED", "NO_HUMAN_SIGNOFF_D085"]


def _checked(rows):
    out = []
    for r in rows:
        a = dict(r)
        if not isinstance(a.get("row_id"), str) or not isinstance(a.get("candidate_id"), str):
            raise ValueError("row and paper IDs are required")
        for key in ("T", "k"):
            v = a.get(key)
            if isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v):
                raise ValueError("finite numeric temperature/rate required")
        if a["T"] <= -273.15 or a["k"] <= 0:
            raise ValueError("positive Kelvin temperature and rate required")
        out.append(a)
    if len({r["row_id"] for r in out}) != len(out):
        raise ValueError("duplicate row IDs")
    return sorted(out, key=lambda r: r["row_id"])


def fit_paper(rows):
    """Unweighted per-paper Arrhenius OLS, only with >=3 distinct temperatures.

    A numerical-roundoff-perfect fit retains coefficient estimates, but does not
    turn a residual variance indistinguishable from zero into a precision claim.
    No scientific goodness-of-fit or practical precision threshold is applied.
    """
    rows = _checked(rows)
    papers = {r["candidate_id"] for r in rows}
    if len(papers) > 1:
        raise ValueError("fit_paper accepts one paper")
    base = {"n_rows": len(rows), "n_temperatures": len({r["T"] for r in rows}),
            "row_ids": [r["row_id"] for r in rows], "labels": LABELS.copy()}
    if base["n_temperatures"] < 3:
        return {**base, "status": "NEED_DATA", "reason": "FEWER_THAN_THREE_INCLUDED_TEMPERATURES"}
    # Scale the slope to kJ/mol for a well-conditioned numerical design.
    X = np.array([[1., -(1. / (r["T"] + 273.15) - 1. / frozen.T_REF_K) * 1000. / frozen.R]
                  for r in rows])
    y = np.log([r["k"] for r in rows])
    if np.linalg.matrix_rank(X) != 2:
        return {**base, "status": "NEED_DATA", "reason": "RANK_DEFICIENT"}
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    residual = y - X @ beta
    ssr, dof = float(residual @ residual), len(rows) - 2
    # Roundoff threshold, not a scientific acceptance criterion.
    numerical_zero = np.finfo(float).eps ** 2 * 100 * max(1., float(y @ y))
    common = {**base, "dof": dof, "Ea_J_per_mol": float(beta[1] * 1000.),
              "ln_k_ref": float(beta[0]), "T_ref_K": frozen.T_REF_K, "k_unit": "min^-1",
              "residual_ssr": ssr}
    if ssr <= numerical_zero:
        return {**common, "status": "NEED_DATA_FOR_UNCERTAINTY", "reason": "ROUND_OFF_PERFECT_FIT",
                "Ea_se": None, "ln_k_ref_se": None, "residual_sd": None}
    cov = ssr / dof * np.linalg.inv(X.T @ X)
    return {**common, "status": "FIT_DIAGNOSTIC_ONLY", "residual_sd": math.sqrt(ssr / dof),
            "Ea_se": math.sqrt(float(cov[1, 1])) * 1000.,
            "ln_k_ref_se": math.sqrt(float(cov[0, 0])),
            "uncertainty_basis": "UNWEIGHTED_OLS_IID_HOMOSCEDASTIC_LOG_RATE_ERRORS"}


def model_b(rows):
    rows = _checked(rows)
    return {p: fit_paper([r for r in rows if r["candidate_id"] == p])
            for p in sorted({r["candidate_id"] for r in rows})}


def _model_a_arm(rows, primary_ids):
    """New diagnostic output using the unchanged primary fitter, never replacing it."""
    base = {"n_rows": len(rows), "n_papers": len({r["candidate_id"] for r in rows}),
            "row_ids": sorted(r["row_id"] for r in rows), "labels": LABELS.copy()}
    if base["row_ids"] == primary_ids:
        return {**base, "status": "SAME_ROWS_AS_PRIMARY_NO_REFIT"}
    if base["n_papers"] < 2:
        return {**base, "status": "NEED_DATA", "reason": "Model A needs at least 2 papers (between-paper SD)"}
    try:
        fit = frozen.fit_model_a(rows)
    except frozen.FitRefused as exc:
        return {**base, "status": "NEED_DATA", "reason": str(exc)}
    return {**base, "status": "FIT_DIAGNOSTIC_ONLY", "fit": fit}


def sensitivity_report(admissible_rows, metadata, *, rejected_papers):
    """Only admissible rows enter any arm; rejected papers never return via sensitivity."""
    rows = _checked(admissible_rows)
    papers = {r["candidate_id"] for r in rows}
    if papers & set(rejected_papers):
        raise ValueError("rejected paper present in admissible rows")
    if not papers <= set(metadata):
        raise ValueError("paper metadata missing")
    for p in papers:
        if metadata[p].get("water_contact") not in ("YES", "NO", "UNKNOWN"):
            raise ValueError("water contact must be explicit three-valued metadata")
        if type(metadata[p].get("aa_specific")) is not bool:
            raise ValueError("AA-specific assay flag required")
    primary = [r for r in rows if frozen.T_MIN_C <= r["T"] <= frozen.T_MAX_C]
    primary_ids = sorted(r["row_id"] for r in primary)
    without_water = [r for r in primary if metadata[r["candidate_id"]]["water_contact"] != "YES"]
    without_assay = [r for r in primary if metadata[r["candidate_id"]]["aa_specific"]]
    water_arm = _model_a_arm(without_water, primary_ids)
    water_arm.update(same_rows_as_primary=[r["row_id"] for r in without_water] == [r["row_id"] for r in primary],
                     unknown_water_contact_papers=sorted(p for p in papers if metadata[p]["water_contact"] == "UNKNOWN"),
                     rule="REMOVE_EXPLICIT_WATER_CONTACT_ONLY;UNKNOWN_IS_NOT_NO_WATER_CONTACT")
    all_arm = _model_a_arm(rows, primary_ids)
    all_arm["added_below_60C"] = sum(r["T"] < frozen.T_MIN_C for r in rows)
    return {"record": "AA_CAL_POST_FREEZE_SENSITIVITIES", "labels": LABELS.copy(),
            "validation_label": "NOT_VALIDATED / RESEARCH_ONLY", "primary_fit_replaced": False,
            "primary_included_rows": len(primary), "primary_rows_by_paper": dict(sorted(Counter(
                r["candidate_id"] for r in primary).items())),
            "model_b": model_b(primary), "all_admissible_temperatures": all_arm,
            "all_rows_including_rejected": {"status": "NOT_RUN_LICENCE_REJECTED",
                                             "rejected_papers": sorted(rejected_papers),
                                             "reason": "Predeclared all-rows arm cannot override licence/verdict rejection."},
            "without_water_contact": water_arm,
            "without_non_aa_specific": _model_a_arm(without_assay, primary_ids)}
