"""Synthetic-truth recovery tests of the Step 26a least-squares fitter (S159, DRAFT_PENDING_26_0_H4).

Every dataset is generated inside the test from KNOWN, SYNTHETIC parameter values (not literature values,
not fitted to any data) and the fitter must recover them within the tolerances stated next to each test.
The numpy backend always runs; the scipy backend (optional extra `step26`, D-050) runs when scipy imports.
"""
from __future__ import annotations

import importlib.util

import numpy as np
import pytest

from culinarystate.simulation.kinetics import fitting as FT
from culinarystate.simulation.kinetics import models as M

HAS_SCIPY = importlib.util.find_spec("scipy") is not None
BACKENDS = ["numpy", pytest.param("scipy", marks=pytest.mark.skipif(not HAS_SCIPY, reason="scipy not installed"))]
SEED = 20261103

# Synthetic truths (SYNTHETIC_TEST_VALUE: chosen for algebra, not taken from any source).
K_TRUE = 1.5e-3            # s^-1
C0_TRUE, K0_TRUE = 4.0, 1.0e-3
ALPHA_TRUE, BETA_TRUE = 800.0, 0.7
KREF_TRUE, EA_TRUE, T_REF = 1.2e-3, 6.0e4, 350.0
TAU = np.array([0.0, 120.0, 300.0, 600.0, 900.0, 1200.0, 1800.0])
TEMPS = (335.0, 345.0, 355.0, 365.0)


def design_arrhenius() -> dict[str, np.ndarray]:
    tau = np.tile(TAU, len(TEMPS))
    temp = np.repeat(np.array(TEMPS), len(TAU))
    return {"tau_s": tau, "T_K": temp}


def synth(form: M.KineticForm, theta: dict[str, float], cov: dict[str, np.ndarray], *, sigma: float | None,
          seed: int = SEED, fixed: dict[str, float] | None = None) -> FT.Observations:
    y = form.predict(theta, cov, fixed)
    if sigma:
        y = y + np.random.default_rng(seed).normal(0.0, sigma, size=y.shape)
    return FT.Observations(response=y, covariates=cov, sigma=None if sigma is None else np.full(y.shape, sigma),
                           response_kind=form.response, origin="SYNTHETIC")


BOUNDS = {
    "FIRST_ORDER": {"k": (1e-6, 1e-1)},
    "ZERO_ORDER": {"C0": (0.5, 20.0), "k0": (1e-6, 1e-1)},
    "WEIBULL": {"alpha": (10.0, 1e5), "beta": (0.2, 3.0)},
    "ARRHENIUS_REF_T": {"k_ref": (1e-6, 1e-1), "Ea": (1e3, 3e5)},
    "FIRST_ORDER_ARRHENIUS": {"k_ref": (1e-6, 1e-1), "Ea": (1e3, 3e5)},
}


def fit(form: M.KineticForm, obs: FT.Observations, backend: str, fixed: dict[str, float] | None = None,
        n_starts: int = 8) -> FT.FitResult:
    starts = FT.starts_from_bounds(form, BOUNDS[form.name], n=n_starts, seed=SEED)
    return FT.fit_least_squares(form, obs, starts=starts, fixed=fixed, backend=backend)


# ----------------------------------------------------------------------------- inputs
def test_status_header() -> None:
    assert FT.STATUS == "DRAFT_PENDING_26_0_H4"


@pytest.mark.parametrize("kw", [
    {"response": np.zeros(3), "covariates": {"tau_s": np.zeros(2)}},
    {"response": np.array([0.0, np.nan]), "covariates": {"tau_s": np.zeros(2)}},
    {"response": np.zeros(2), "covariates": {"tau_s": np.zeros(2)}, "sigma": np.array([1.0, 0.0])},
    {"response": np.zeros(2), "covariates": {"tau_s": np.zeros(2)}, "origin": "KIN_SERIES"},
    {"response": np.zeros(2), "covariates": {"tau_s": np.zeros(2)}, "origin": "LITERATURE_GUESS"},
])
def test_observations_are_validated(kw: dict) -> None:
    base = {"sigma": None, "response_kind": "LN_RETENTION", "origin": "SYNTHETIC"}
    with pytest.raises(FT.FitError):
        FT.Observations(**{**base, **kw})


def test_kin_series_observations_carry_kin_ids() -> None:
    o = FT.Observations(response=np.zeros(2), covariates={"tau_s": np.zeros(2)}, sigma=None,
                        response_kind="LN_RETENTION", origin="KIN_SERIES", kin_ids=("KIN-000001",))
    assert o.kin_ids == ("KIN-000001",)


def test_starts_are_required_and_complete() -> None:
    form = M.FORMS["FIRST_ORDER"]
    obs = synth(form, {"k": K_TRUE}, {"tau_s": TAU}, sigma=None)
    with pytest.raises(FT.FitError):
        FT.fit_least_squares(form, obs, starts=[], backend="numpy")
    with pytest.raises(FT.FitError):
        FT.fit_least_squares(form, obs, starts=[{"kk": 1e-3}], backend="numpy")
    with pytest.raises(FT.FitError):
        FT.fit_least_squares(form, obs, starts=[{"k": -1e-3}], backend="numpy")


def test_response_kind_must_match_form() -> None:
    form = M.FORMS["FIRST_ORDER"]
    obs = FT.Observations(response=np.zeros(3), covariates={"tau_s": TAU[:3]}, sigma=None,
                          response_kind="CONCENTRATION", origin="SYNTHETIC")
    with pytest.raises(FT.FitError):
        FT.fit_least_squares(form, obs, starts=[{"k": 1e-3}], backend="numpy")


def test_fixed_t_ref_is_required() -> None:
    form = M.FORMS["FIRST_ORDER_ARRHENIUS"]
    obs = synth(form, {"k_ref": KREF_TRUE, "Ea": EA_TRUE}, design_arrhenius(), sigma=None, fixed={"T_ref_K": T_REF})
    with pytest.raises((FT.FitError, M.ModelError)):
        FT.fit_least_squares(form, obs, starts=[{"k_ref": 1e-3, "Ea": 5e4}], backend="numpy")


def test_starts_from_bounds_is_deterministic_and_in_bounds() -> None:
    form = M.FORMS["WEIBULL"]
    a = FT.starts_from_bounds(form, BOUNDS["WEIBULL"], n=10, seed=3)
    assert a == FT.starts_from_bounds(form, BOUNDS["WEIBULL"], n=10, seed=3)
    assert all(10.0 <= s["alpha"] <= 1e5 and 0.2 <= s["beta"] <= 3.0 for s in a)
    with pytest.raises(FT.FitError):
        FT.starts_from_bounds(form, {"alpha": (-1.0, 5.0), "beta": (0.2, 3.0)}, n=2, seed=0)
    with pytest.raises(FT.FitError):
        FT.starts_from_bounds(form, {"alpha": (10.0, 1e5)}, n=2, seed=0)


# ----------------------------------------------------------------------------- noise-free recovery (rel 1e-6)
CASES = {
    "FIRST_ORDER": ({"k": K_TRUE}, {"tau_s": TAU}, None),
    "ZERO_ORDER": ({"C0": C0_TRUE, "k0": K0_TRUE}, {"tau_s": TAU}, None),
    "WEIBULL": ({"alpha": ALPHA_TRUE, "beta": BETA_TRUE}, {"tau_s": TAU[1:]}, None),
    "ARRHENIUS_REF_T": ({"k_ref": KREF_TRUE, "Ea": EA_TRUE}, {"T_K": np.array(TEMPS)}, {"T_ref_K": T_REF}),
    "FIRST_ORDER_ARRHENIUS": ({"k_ref": KREF_TRUE, "Ea": EA_TRUE}, design_arrhenius(), {"T_ref_K": T_REF}),
}


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("name", sorted(CASES))
def test_noise_free_recovery_within_1e_6(name: str, backend: str) -> None:
    theta, cov, fixed = CASES[name]
    form = M.FORMS[name]
    res = fit(form, synth(form, theta, cov, sigma=None, fixed=fixed), backend, fixed)
    assert res.converged and res.backend == backend
    for p, truth in theta.items():
        assert res.estimates[p] == pytest.approx(truth, rel=1e-6), p


# ----------------------------------------------------------------------------- noisy recovery
@pytest.mark.parametrize("backend", BACKENDS)
def test_noisy_first_order_arrhenius_recovery(backend: str) -> None:
    """sigma 0.01 on ln-retention, 4 T x 7 tau: |rel error| <= 3 % (k_ref) and <= 5 % (Ea)."""
    form = M.FORMS["FIRST_ORDER_ARRHENIUS"]
    fixed = {"T_ref_K": T_REF}
    res = fit(form, synth(form, {"k_ref": KREF_TRUE, "Ea": EA_TRUE}, design_arrhenius(), sigma=0.01,
                          fixed=fixed), backend, fixed)
    assert res.converged
    assert abs(res.estimates["k_ref"] / KREF_TRUE - 1) <= 0.03
    assert abs(res.estimates["Ea"] / EA_TRUE - 1) <= 0.05


@pytest.mark.parametrize("backend", BACKENDS)
def test_noisy_weibull_recovery(backend: str) -> None:
    """sigma 0.01 on ln-retention, 12 tau: |rel error| <= 10 % for alpha and beta."""
    form = M.FORMS["WEIBULL"]
    tau = np.linspace(60.0, 3600.0, 12)
    res = fit(form, synth(form, {"alpha": ALPHA_TRUE, "beta": BETA_TRUE}, {"tau_s": tau}, sigma=0.01), backend)
    assert abs(res.estimates["alpha"] / ALPHA_TRUE - 1) <= 0.10
    assert abs(res.estimates["beta"] / BETA_TRUE - 1) <= 0.10


@pytest.mark.skipif(not HAS_SCIPY, reason="scipy not installed")
def test_backends_agree_on_noisy_data() -> None:
    form = M.FORMS["FIRST_ORDER_ARRHENIUS"]
    fixed = {"T_ref_K": T_REF}
    obs = synth(form, {"k_ref": KREF_TRUE, "Ea": EA_TRUE}, design_arrhenius(), sigma=0.01, fixed=fixed)
    a, b = fit(form, obs, "numpy", fixed), fit(form, obs, "scipy", fixed)
    for p in a.estimates:
        assert a.estimates[p] == pytest.approx(b.estimates[p], rel=1e-6)
    assert a.fit_id != b.fit_id  # the backend is part of the fit identity


def test_first_order_covariance_matches_the_analytic_value() -> None:
    """Var(ln k) = 1 / sum((k tau / sigma)^2) for ln R = -k tau with known sigma (Gauss-Newton exact)."""
    form, sigma = M.FORMS["FIRST_ORDER"], 0.01
    res = fit(form, synth(form, {"k": K_TRUE}, {"tau_s": TAU}, sigma=sigma), "numpy")
    k = res.estimates["k"]
    expect = 1.0 / np.sum((k * TAU / sigma) ** 2)
    cov = res.covariance_transformed()
    assert cov is not None and cov[0, 0] == pytest.approx(expect, rel=1e-4)
    assert res.sigma_known and res.dof == len(TAU) - 1


def test_unknown_sigma_is_estimated_from_residuals() -> None:
    form = M.FORMS["FIRST_ORDER"]
    obs = synth(form, {"k": K_TRUE}, {"tau_s": np.linspace(0, 3600, 40)}, sigma=0.02)
    obs = FT.Observations(response=obs.response, covariates=obs.covariates, sigma=None,
                          response_kind=obs.response_kind, origin="SYNTHETIC")
    res = fit(form, obs, "numpy")
    assert not res.sigma_known and 0.01 < res.sigma_hat < 0.03


def test_fit_id_is_a_deterministic_content_id() -> None:
    form = M.FORMS["FIRST_ORDER"]
    obs = synth(form, {"k": K_TRUE}, {"tau_s": TAU}, sigma=0.01)
    a, b = fit(form, obs, "numpy"), fit(form, obs, "numpy")
    assert a.fit_id == b.fit_id and a.fit_id.startswith("FITRUN-") and len(a.fit_id) == len("FITRUN-") + 16
    other = synth(form, {"k": K_TRUE}, {"tau_s": TAU}, sigma=0.01, seed=SEED + 1)
    assert fit(form, other, "numpy").fit_id != a.fit_id


def test_fit_does_not_modify_inputs() -> None:
    form = M.FORMS["FIRST_ORDER"]
    obs = synth(form, {"k": K_TRUE}, {"tau_s": TAU}, sigma=0.01)
    y, t = obs.response.copy(), obs.covariates["tau_s"].copy()
    fit(form, obs, "numpy")
    np.testing.assert_array_equal(obs.response, y)
    np.testing.assert_array_equal(obs.covariates["tau_s"], t)


def test_unknown_backend_is_refused() -> None:
    form = M.FORMS["FIRST_ORDER"]
    obs = synth(form, {"k": K_TRUE}, {"tau_s": TAU}, sigma=None)
    with pytest.raises(FT.FitError):
        FT.fit_least_squares(form, obs, starts=[{"k": 1e-3}], backend="magic")
