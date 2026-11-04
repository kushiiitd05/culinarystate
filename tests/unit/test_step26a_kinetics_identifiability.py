"""Tests of the Step 26a identifiability tools (S159, DRAFT_PENDING_26_0_H4).

Synthetic data from KNOWN SYNTHETIC parameter values generated inside the test. Includes the required
non-identifiable cases: they must be reported as NOT_IDENTIFIABLE, never fitted confidently.
The criteria values passed here are TEST SETTINGS. They are not the G26-CAL values (condition number < 1e6,
>= 5 observations per parameter are PROPOSED_PILOT, unsigned) and the library holds no default for them.
"""
from __future__ import annotations

import dataclasses
import importlib.util
from statistics import NormalDist

import numpy as np
import pytest

from culinarystate.simulation.kinetics import fitting as FT
from culinarystate.simulation.kinetics import identifiability as ID
from culinarystate.simulation.kinetics import models as M

HAS_SCIPY = importlib.util.find_spec("scipy") is not None
BACKENDS = ["numpy", pytest.param("scipy", marks=pytest.mark.skipif(not HAS_SCIPY, reason="scipy not installed"))]
SEED = 20261103
KREF, EA, T_REF = 1.2e-3, 6.0e4, 350.0       # SYNTHETIC_TEST_VALUE
K_TRUE = 1.5e-3                               # SYNTHETIC_TEST_VALUE
TAU = np.array([0.0, 120.0, 300.0, 600.0, 900.0, 1200.0, 1800.0])
FOA = M.FORMS["FIRST_ORDER_ARRHENIUS"]
FO = M.FORMS["FIRST_ORDER"]
BOUNDS = {"k_ref": (1e-6, 1e-1), "Ea": (1e3, 3e5)}


def criteria(**kw: object) -> ID.IdentifiabilityCriteria:
    base: dict[str, object] = {"profile_level": 0.95, "profile_half_width": {"k_ref": 3.0, "Ea": 1.5e5, "k": 3.0},
                               "n_profile_points": 30, "rank_rtol": 1e-8, "max_condition_number": None,
                               "min_observations_per_parameter": None}
    base.update(kw)
    return ID.IdentifiabilityCriteria(**base)  # type: ignore[arg-type]


def arr_obs(temps: tuple[float, ...], *, sigma: float, seed: int = SEED) -> FT.Observations:
    cov = {"tau_s": np.tile(TAU, len(temps)), "T_K": np.repeat(np.array(temps), len(TAU))}
    y = FOA.predict({"k_ref": KREF, "Ea": EA}, cov, {"T_ref_K": T_REF})
    y = y + np.random.default_rng(seed).normal(0.0, sigma, size=y.shape)
    return FT.Observations(response=y, covariates=cov, sigma=np.full(y.shape, sigma), response_kind="LN_RETENTION",
                           origin="SYNTHETIC")


def arr_fit(obs: FT.Observations, backend: str = "numpy") -> FT.FitResult:
    starts = FT.starts_from_bounds(FOA, BOUNDS, n=8, seed=SEED)
    return FT.fit_least_squares(FOA, obs, starts=starts, fixed={"T_ref_K": T_REF}, backend=backend)


def test_status_and_vocabulary() -> None:
    assert ID.STATUS == "DRAFT_PENDING_26_0_H4"
    assert ID.VERDICTS == ("IDENTIFIABLE", "NOT_IDENTIFIABLE", "UNKNOWN")
    assert set(ID.CLASSES) == {"PRACTICALLY_IDENTIFIABLE", "STRUCTURALLY_NON_IDENTIFIABLE",
                               "PRACTICALLY_NON_IDENTIFIABLE", "UNKNOWN"}


def test_criteria_have_no_defaults() -> None:
    assert all(f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING
               for f in dataclasses.fields(ID.IdentifiabilityCriteria))
    with pytest.raises(ID.IdentifiabilityError):
        criteria(profile_level=1.5)
    with pytest.raises(ID.IdentifiabilityError):
        criteria(n_profile_points=1)


def test_chi2_threshold_from_the_normal_quantile() -> None:
    assert ID.chi2_1_quantile(0.95) == pytest.approx(NormalDist().inv_cdf(0.975) ** 2, rel=1e-15)
    assert ID.chi2_1_quantile(0.95) == pytest.approx(3.841458820694124, rel=1e-12)


# ----------------------------------------------------------------------------- local sensitivity
def test_first_order_sensitivity_matches_the_analytic_derivative() -> None:
    s = ID.local_sensitivity(FO, {"k": K_TRUE}, {"tau_s": TAU})
    np.testing.assert_allclose(s.scaled[:, 0], -K_TRUE * TAU, rtol=1e-6, atol=1e-12)
    assert s.numerical_rank == 1 and s.parameters == ("k",)


def test_single_temperature_arrhenius_is_rank_deficient() -> None:
    cov = {"tau_s": TAU, "T_K": np.full(TAU.shape, 360.0)}
    s = ID.local_sensitivity(FOA, {"k_ref": KREF, "Ea": EA}, cov, {"T_ref_K": T_REF})
    assert s.numerical_rank == 1
    assert s.condition_number > 1e8 or not np.isfinite(s.condition_number)


def test_reference_temperature_at_the_design_centre_lowers_the_condition_number() -> None:
    temps = np.repeat(np.array([335.0, 345.0, 355.0, 365.0]), len(TAU))
    cov = {"tau_s": np.tile(TAU, 4), "T_K": temps}
    centred = ID.local_sensitivity(FOA, {"k_ref": KREF, "Ea": EA}, cov, {"T_ref_K": 350.0})
    k_far = float(M.arrhenius_rate(KREF, EA, np.array([300.0]), 350.0)[0])
    far = ID.local_sensitivity(FOA, {"k_ref": k_far, "Ea": EA}, cov, {"T_ref_K": 300.0})
    assert centred.condition_number < far.condition_number
    assert abs(centred.correlation[0, 1]) < abs(far.correlation[0, 1])


# ----------------------------------------------------------------------------- profile likelihood
def test_profile_ci_contains_truth_for_an_identifiable_fit() -> None:
    obs = arr_obs((335.0, 345.0, 355.0, 365.0), sigma=0.01)
    res = arr_fit(obs)
    for p, truth in (("k_ref", KREF), ("Ea", EA)):
        pr = ID.profile_likelihood(FOA, obs, res, p, half_width=criteria().profile_half_width[p], n_points=30,
                                   level=0.95)
        assert pr.lower_closed and pr.upper_closed
        assert pr.ci_low < truth < pr.ci_high
        assert pr.ci_low < res.estimates[p] < pr.ci_high
        assert pr.threshold == pytest.approx(ID.chi2_1_quantile(0.95))


def test_first_order_profile_ci_coverage_over_repeated_datasets() -> None:
    """90 % profile CIs over 100 synthetic datasets: empirical coverage in [0.80, 0.97]."""
    hits = 0
    for i in range(100):
        y = FO.predict({"k": K_TRUE}, {"tau_s": TAU}) + np.random.default_rng(SEED + i).normal(0, 0.02, TAU.shape)
        obs = FT.Observations(response=y, covariates={"tau_s": TAU}, sigma=np.full(TAU.shape, 0.02),
                              response_kind="LN_RETENTION", origin="SYNTHETIC")
        res = FT.fit_least_squares(FO, obs, starts=[{"k": 1e-3}], backend="numpy")
        pr = ID.profile_likelihood(FO, obs, res, "k", half_width=1.0, n_points=40, level=0.90)
        hits += int(pr.ci_low is not None and pr.ci_high is not None and pr.ci_low <= K_TRUE <= pr.ci_high)
    assert 0.80 <= hits / 100 <= 0.97


# ----------------------------------------------------------------------------- verdicts
@pytest.mark.parametrize("backend", BACKENDS)
def test_wide_temperature_design_is_identifiable(backend: str) -> None:
    obs = arr_obs((335.0, 345.0, 355.0, 365.0), sigma=0.01)
    rep = ID.assess_identifiability(FOA, obs, arr_fit(obs, backend), criteria(), backend=backend)
    assert rep.overall_verdict == "IDENTIFIABLE"
    assert {p.parameter: p.identifiability_class for p in rep.parameters} == {
        "k_ref": "PRACTICALLY_IDENTIFIABLE", "Ea": "PRACTICALLY_IDENTIFIABLE"}
    est = rep.reportable_estimates()
    assert set(est) == {"k_ref", "Ea"}
    assert abs(est["k_ref"] / KREF - 1) <= 0.03 and abs(est["Ea"] / EA - 1) <= 0.05


@pytest.mark.parametrize("backend", BACKENDS)
def test_single_temperature_design_is_not_identifiable(backend: str) -> None:
    """Correlated parameters: at one temperature ln k_ref and Ea trade off exactly (structural)."""
    obs = arr_obs((360.0,), sigma=0.01)
    rep = ID.assess_identifiability(FOA, obs, arr_fit(obs, backend), criteria(), backend=backend)
    assert rep.overall_verdict == "NOT_IDENTIFIABLE"
    by = {p.parameter: p for p in rep.parameters}
    for name in ("k_ref", "Ea"):
        assert by[name].verdict == "NOT_IDENTIFIABLE"
        assert by[name].identifiability_class == "STRUCTURALLY_NON_IDENTIFIABLE"
        assert "STRUCTURAL_RANK_DEFICIENT" in by[name].reasons
        assert by[name].ci_low is None or by[name].ci_high is None
    assert rep.reportable_estimates() == {}


def test_nearly_equal_temperatures_are_practically_not_identifiable() -> None:
    """Two temperatures 0.02 K apart: full rank, but the Ea profile stays below threshold (flat)."""
    obs = arr_obs((359.99, 360.01), sigma=0.01)
    rep = ID.assess_identifiability(FOA, obs, arr_fit(obs), criteria())
    by = {p.parameter: p for p in rep.parameters}
    assert rep.overall_verdict == "NOT_IDENTIFIABLE"
    assert by["Ea"].identifiability_class == "PRACTICALLY_NON_IDENTIFIABLE"
    assert {"PROFILE_FLAT_LOWER", "PROFILE_FLAT_UPPER"} & set(by["Ea"].reasons)
    assert "Ea" not in rep.reportable_estimates()


def test_condition_number_and_observation_criteria_when_supplied() -> None:
    obs = arr_obs((335.0, 345.0, 355.0, 365.0), sigma=0.01)
    res = arr_fit(obs)
    rep = ID.assess_identifiability(FOA, obs, res, criteria(max_condition_number=1.0))
    assert rep.overall_verdict == "NOT_IDENTIFIABLE"
    assert all("ILL_CONDITIONED" in p.reasons for p in rep.parameters)
    rep = ID.assess_identifiability(FOA, obs, res, criteria(min_observations_per_parameter=100))
    assert all("TOO_FEW_OBSERVATIONS" in p.reasons for p in rep.parameters)


def test_unconverged_fit_is_unknown() -> None:
    obs = arr_obs((335.0, 345.0, 355.0, 365.0), sigma=0.01)
    res = dataclasses.replace(arr_fit(obs), converged=False)
    rep = ID.assess_identifiability(FOA, obs, res, criteria())
    assert rep.overall_verdict == "UNKNOWN"
    assert all(p.verdict == "UNKNOWN" and "FIT_NOT_CONVERGED" in p.reasons for p in rep.parameters)
    assert rep.reportable_estimates() == {}


def test_report_carries_the_fit_id_and_criteria() -> None:
    obs = arr_obs((335.0, 345.0, 355.0, 365.0), sigma=0.01)
    res = arr_fit(obs)
    rep = ID.assess_identifiability(FOA, obs, res, criteria())
    assert rep.fit_id == res.fit_id and rep.criteria == criteria() and rep.status == ID.STATUS
    assert rep.to_dict()["overall_verdict"] == "IDENTIFIABLE"
