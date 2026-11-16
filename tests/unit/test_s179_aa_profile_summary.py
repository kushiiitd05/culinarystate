"""Profile summaries must agree with constrained OLS, not a Wald relabelling."""
import copy
import math

import numpy as np
import pytest
from scipy.stats import chi2, t

from tools.s179_aa_profile_summary import profile_summary


def fixture():
    x = np.array([[1, 0, -2], [1, 0, -1], [1, 0, 0],
                  [0, 1, -1], [0, 1, 0], [0, 1, 1], [0, 1, 2]], dtype=float)
    y = x @ np.array([-4, -3, 0.3]) + np.array([.1, -.2, .05, .2, -.1, .15, -.05])
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    ssr = np.sum((y - x @ beta) ** 2)
    cov = ssr / 4 * np.linalg.inv(x.T @ x)
    fit = {"model": "A_SHARED_EA_PAPER_INTERCEPTS", "n_rows": 7, "n_papers": 2,
           "papers": ["SYNTH-A", "SYNTH-B"], "dof": 4, "T_ref_K": 363.15,
           "intercepts": dict(zip(["SYNTH-A", "SYNTH-B"], beta[:2])),
           "Ea_J_per_mol": beta[2], "residual_sd": math.sqrt(ssr / 4), "cov": cov.tolist()}
    return fit, x, y, ssr


def test_profiles_match_direct_constrained_refits():
    fit, x, y, ssr = fixture()
    out = profile_summary(fit)
    for j, row in enumerate(out["parameters"]):
        for value in row["profile_lr95"]:
            free = [k for k in range(3) if k != j]
            z = y - x[:, j] * value
            nuisance = np.linalg.lstsq(x[:, free], z, rcond=None)[0]
            constrained_ssr = np.sum((z - x[:, free] @ nuisance) ** 2)
            assert 7 * math.log(constrained_ssr / ssr) == pytest.approx(chi2.ppf(.95, 1))


def test_small_sample_t_intervals_are_reported_separately_and_wider():
    fit, *_ = fixture()
    out = profile_summary(fit)
    assert out["dof"] == 4
    for row in out["parameters"]:
        assert row["t95"][1] - row["estimate"] == pytest.approx(t.ppf(.975, 4) * row["se"])
        assert row["t95"][1] > row["profile_lr95"][1]
        assert row["profile_status"] == "BOUNDED_CONDITIONAL_ON_OLS_MODEL"
        assert row["practical_gate_status"] == "NOT_ASSESSED_NO_LOCKED_PRECISION_CRITERION"


def test_no_input_mutation_and_no_validation_claim():
    fit, *_ = fixture()
    before = copy.deepcopy(fit)
    out = profile_summary(fit)
    assert fit == before
    assert out["validation_label"] == "NOT_VALIDATED / RESEARCH_ONLY"
    assert "NO_HUMAN_SIGNOFF_D085" in out["labels"]


@pytest.mark.parametrize("field,value", [("dof", 0), ("dof", 5), ("residual_sd", 0),
                                         ("residual_sd", float("nan")), ("n_rows", 7.5)])
def test_invalid_summary_refused(field, value):
    fit, *_ = fixture()
    fit[field] = value
    with pytest.raises(ValueError):
        profile_summary(fit)


def test_invalid_covariance_refused():
    fit, *_ = fixture()
    fit["cov"][0][0] = -1
    with pytest.raises(ValueError):
        profile_summary(fit)


def test_duplicate_papers_refused():
    fit, *_ = fixture()
    fit["papers"] = ["SYNTH-A", "SYNTH-A"]
    with pytest.raises(ValueError):
        profile_summary(fit)
