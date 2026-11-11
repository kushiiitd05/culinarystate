#!/usr/bin/env python3
"""Separate AA diagnostic from frozen OLS summaries; never refits or changes Model A.

For a single coefficient b, profiling the other coefficients gives
SSR(b)=SSRmin+s²(b-bhat)²/Cjj, C=s²(X'X)^-1. Profiling unknown Gaussian
variance yields LR(b)=n*log(SSR(b)/SSRmin). Its chi-square calibration is
asymptotic; the small-sample Student-t interval is reported separately.
No precision cutoff or scientific gate is introduced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import chi2, t

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["DIAGNOSTIC", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085", "AI_PRECHECKED"]


def profile_summary(fit: dict) -> dict:
    """Derive unconstrained coefficient profiles from positive-definite OLS covariance."""
    if fit.get("model") != "A_SHARED_EA_PAPER_INTERCEPTS":
        raise ValueError("only frozen Model A OLS summaries are supported")
    n, m, df = (fit[k] for k in ("n_rows", "n_papers", "dof"))
    if any(type(v) is not int for v in (n, m, df)) or m < 2 or df <= 0 or df != n - m - 1:
        raise ValueError("invalid n, paper count or residual degrees of freedom")
    papers = fit["papers"]
    if len(papers) != m or len(set(papers)) != m or set(papers) != set(fit["intercepts"]):
        raise ValueError("paper/intercept alignment is inconsistent")
    beta = np.array([fit["intercepts"][p] for p in papers] + [fit["Ea_J_per_mol"]], dtype=float)
    cov = np.asarray(fit["cov"], dtype=float)
    sd = float(fit["residual_sd"])
    if not math.isfinite(sd) or sd <= 0 or not np.isfinite(beta).all():
        raise ValueError("invalid estimates or residual SD")
    if cov.shape != (m + 1, m + 1) or not np.isfinite(cov).all() or not np.allclose(cov, cov.T):
        raise ValueError("invalid OLS covariance")
    try:
        np.linalg.cholesky(cov)
    except np.linalg.LinAlgError as exc:
        raise ValueError("OLS covariance must be positive definite") from exc
    lr_cutoff = float(chi2.ppf(.95, 1))
    lr_factor = math.sqrt(df * math.expm1(lr_cutoff / n))
    t_factor = float(t.ppf(.975, df))
    names = [f"ln_k_ref[{p}]" for p in papers] + ["Ea_J_per_mol"]
    parameters = []
    for j, name in enumerate(names):
        estimate, se = float(beta[j]), math.sqrt(float(cov[j, j]))
        parameters.append({"parameter": name, "estimate": estimate, "se": se,
                           "profile_lr95": [estimate - lr_factor * se, estimate + lr_factor * se],
                           "t95": [estimate - t_factor * se, estimate + t_factor * se],
                           "profile_status": "BOUNDED_CONDITIONAL_ON_OLS_MODEL",
                           "practical_gate_status": "NOT_ASSESSED_NO_LOCKED_PRECISION_CRITERION"})
    scales = np.sqrt(np.diag(cov))
    corr = cov / np.outer(scales, scales)
    return {"record": "AA_FROZEN_MODEL_A_PROFILE_SUMMARY", "labels": LABELS.copy(),
            "validation_label": "NOT_VALIDATED / RESEARCH_ONLY", "n_rows": n, "n_parameters": m + 1,
            "n_papers": m, "dof": df, "T_ref_K": fit["T_ref_K"], "residual_ssr": df * sd ** 2,
            "lr_cutoff": lr_cutoff, "lr_calibration": "CHI2_1_ASYMPTOTIC_DIAGNOSTIC",
            "profile_method": "UNCONSTRAINED_LINEAR_GAUSSIAN_UNKNOWN_VARIANCE_ANALYTIC",
            "t_calibration": "STUDENT_T_CONDITIONAL_ON_IID_GAUSSIAN_ERRORS",
            "parameters": parameters, "coefficient_correlation": corr.tolist(),
            "design_condition_number": None,
            "design_condition_number_reason": "NO_PREDECLARED_PARAMETER_SCALING_OR_RAW_DESIGN",
            "limitations": ["Only two papers; four residual degrees of freedom.",
                            "No residual diagnostics or raw-row checks from summaries.",
                            "Within-paper independence and equal residual variance are assumptions.",
                            "Bounded model-conditional profiles do not establish transportability or practical precision.",
                            "Between-paper variance is not profiled; no validation or SIMULATE gate opens."]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    doc = json.loads(args.fit.read_text())
    for path, expected in doc["code_sha256"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"frozen fit code hash changed: {path}")
    out = profile_summary(doc["fit"])
    out["input_fit_sha256"] = hashlib.sha256(args.fit.read_bytes()).hexdigest()
    out["tool_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with args.out.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("AA profile diagnostic written; no fit, freeze or scientific gate changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
