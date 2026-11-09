"""AA kinetics pilot: verdict rule and Model A fit (reports/step10/aa_pilot_preregistration_DRAFT.md §4, §6). DRAFT.

Model A: ln k_ij = a_i - (Ea/R)(1/T_ij - 1/T_ref), one intercept per paper (matrix), one shared Ea, T_ref = 90 C,
unweighted OLS on ln k. Linear in (a_1..a_m, Ea), so the covariance is exact OLS. Prediction for an unseen matrix
uses mean(a_i) with the between-paper SD, the residual SD and the parameter covariance. Pure functions; no file I/O.
Rows reach the fit only if both humans VERIFIED them (or CORRECTED them to the same value).
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Mapping, Sequence

import numpy as np

R = 8.314462618  # J/(mol K)
T_REF_K = 363.15
T_MIN_C, T_MAX_C = 60.0, 100.0
Z95 = 1.959963984540054
VERDICTS = ("VERIFIED", "CORRECTED", "REJECTED")
FIT_VERSION = "aa-pilot-fit-0.1.0-draft"


class FitRefused(ValueError):
    """Inputs violate the pre-registered rule or the design cannot identify the model."""


def _num(s) -> float | None:
    try:
        return float(str(s).strip())
    except (TypeError, ValueError):
        return None


def agreed_rows(a: Sequence[Mapping], b: Sequence[Mapping]) -> tuple[list[dict], dict]:
    """Rows both reviewers VERIFIED, or CORRECTED to the same value; reasons for the rest."""
    A, B = {r["row_id"]: r for r in a}, {r["row_id"]: r for r in b}
    if set(A) != set(B):
        raise FitRefused("the two verification files list different row ids")
    kept, why = [], Counter()
    for rid in sorted(A):
        ra, rb = A[rid], B[rid]
        va, vb = str(ra.get("verdict", "")).strip(), str(rb.get("verdict", "")).strip()
        if va not in VERDICTS or vb not in VERDICTS:
            raise FitRefused(f"{rid}: blank or invalid verdict")
        if "REJECTED" in (va, vb):
            why["NOT_BOTH_VERIFIED"] += 1
            continue
        if va == vb == "VERIFIED":
            raw = ra["value"]
        elif va == vb == "CORRECTED" and _num(ra.get("corrected_value")) == _num(rb.get("corrected_value")) \
                and _num(ra.get("corrected_value")) is not None:
            raw = ra["corrected_value"]
        else:
            why["CORRECTIONS_DIFFER"] += 1
            continue
        k_at_t = ra["row_type"] == "K_AT_T"
        kept.append({"row_id": rid, "candidate_id": ra["candidate_id"], "row_type": ra["row_type"],
                     "T": _num(ra["T_C"]) if k_at_t else None, "k": _num(raw) if k_at_t else None,
                     "order": str(ra.get("order", ""))})
    return kept, dict(sorted(why.items()))


def include(rows: Sequence[Mapping]) -> tuple[list[dict], dict]:
    """Pre-registered inclusion: K_AT_T, first order, 60 C <= T <= 100 C, k > 0."""
    inc, why = [], Counter()
    for r in rows:
        if r["row_type"] != "K_AT_T":
            why["NOT_K_AT_T"] += 1
        elif not r["order"].lower().startswith("first"):
            why["NOT_FIRST_ORDER"] += 1
        elif r["T"] is None or r["T"] < T_MIN_C:
            why["BELOW_60C"] += 1
        elif r["T"] > T_MAX_C:
            why["ABOVE_100C"] += 1
        elif not r["k"] or r["k"] <= 0:
            why["NONPOSITIVE_K"] += 1
        else:
            inc.append(dict(r))
    return inc, dict(sorted(why.items()))


def _x(T_C: float) -> float:
    return 1.0 / (T_C + 273.15) - 1.0 / T_REF_K


def fit_model_a(rows: Sequence[Mapping]) -> dict:
    papers = sorted({r["candidate_id"] for r in rows})
    m, n = len(papers), len(rows)
    if m < 2:
        raise FitRefused("Model A needs at least 2 papers (between-paper SD)")
    X = np.zeros((n, m + 1))
    y = np.empty(n)
    for i, r in enumerate(sorted(rows, key=lambda r: r["row_id"])):
        X[i, papers.index(r["candidate_id"])] = 1.0
        X[i, m] = -_x(r["T"]) / R
        y[i] = math.log(r["k"])
    if np.linalg.matrix_rank(X) < m + 1 or n <= m + 1:
        raise FitRefused("design does not identify Ea (too few temperatures or rows)")
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    s2 = float(resid @ resid) / (n - m - 1)
    cov = s2 * np.linalg.inv(X.T @ X)
    a = beta[:m]
    return {"model": "A_SHARED_EA_PAPER_INTERCEPTS", "fit_version": FIT_VERSION, "label": "PILOT_MODEL_ASSISTED",
            "T_ref_K": T_REF_K, "Ea_J_per_mol": float(beta[m]), "Ea_se": float(math.sqrt(cov[m, m])),
            "intercepts": {p: float(a[j]) for j, p in enumerate(papers)},
            "intercept_se": {p: float(math.sqrt(cov[j, j])) for j, p in enumerate(papers)},
            "residual_sd": math.sqrt(s2), "sigma_between": float(np.std(a, ddof=1)),
            "cov": [[float(v) for v in row] for row in cov], "papers": papers, "n_rows": n, "n_papers": m,
            "dof": n - m - 1, "row_ids": sorted(r["row_id"] for r in rows),
            "rows_by_paper": {p: sum(r["candidate_id"] == p for r in rows) for p in papers}}


def predict_ln_k(fit: Mapping, T_C: float) -> tuple[float, float, float]:
    """Unseen matrix: (mid, lo95, hi95) for ln k [1/min] at T_C."""
    m = fit["n_papers"]
    c = np.array([1.0 / m] * m + [-_x(T_C) / R])
    beta = np.array([fit["intercepts"][p] for p in fit["papers"]] + [fit["Ea_J_per_mol"]])
    var = float(c @ np.array(fit["cov"]) @ c) + fit["sigma_between"] ** 2 + fit["residual_sd"] ** 2
    mid = float(c @ beta)
    half = Z95 * math.sqrt(var)
    return mid, mid - half, mid + half
