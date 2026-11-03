"""S159 AI cross-review of ksh's 24a / 26a: regression tests for the defects found (AI verdict, pending review).

Each test failed on the pre-fix code (reports/step26/S159_ai_review.md, findings R1-R3). Synthetic inputs only.
"""
from __future__ import annotations

import numpy as np

from culinarystate.mechanism import form_param_val as FPV
from culinarystate.simulation.kinetics import fitting as FT, identifiability as ID, models as M, units as U
from tests.fixtures import form_param_val_v1_fixtures as FX


# ----------------------------------------------------------------------------- R1 rate-constant order by unit
def test_r1_undeclared_mass_ratio_rate_unit_is_not_accepted_as_first_order() -> None:
    # "mg/g/min" is a zero-order unit on a mass-ratio basis; reduced to TIME^-1 it looked first order.
    for unit in ("mg/g/min", "mg/kg/s", "g/g/h"):
        chk = U.check_rate_constant_unit(unit, 1)
        assert chk.verdict == U.UNKNOWN and "CONCENTRATION_TOKENS_UNDECLARED" in chk.detail
    chk = U.check_rate_constant_unit("mol/L/s", 0)           # molar zero order: undeclared, not "inconsistent"
    assert chk.verdict == U.UNKNOWN and "CONCENTRATION_TOKENS_UNDECLARED" in chk.detail
    assert U.check_rate_constant_unit("[mg/g]/min", 0, opaque={"[mg/g]": "CONCENTRATION"}).verdict == U.CONSISTENT
    assert U.check_rate_constant_unit("[mg/g]/min", 1, opaque={"[mg/g]": "CONCENTRATION"}).verdict == U.INCONSISTENT
    assert U.check_rate_constant_unit("1/min", 1).verdict == U.CONSISTENT
    assert U.check_rate_constant_unit("min^-1", 1).verdict == U.CONSISTENT


def test_r1_param_on_a_rate_constant_slot_with_a_mass_ratio_unit_is_flagged() -> None:
    form = FX.form()
    p = FX.param(unit="mg/g/min")
    issues = FPV.validate_param(p, form_id_prefix="FORM", forms_by_id={form["id"]: form})
    assert any(i.code == "PARAM_UNIT_UNKNOWN" and "CONCENTRATION_TOKENS_UNDECLARED" in i.detail for i in issues)
    ok = FPV.validate_param(FX.param(unit="1/min"), form_id_prefix="FORM", forms_by_id={form["id"]: form})
    assert not any(i.code.startswith("PARAM_UNIT") for i in ok)


# ----------------------------------------------------------------------------- R2 / R3 zero residual dof
def _exact_fit():
    form = M.FORMS["FIRST_ORDER_ARRHENIUS"]
    tau, T = np.array([600.0, 1200.0]), np.array([340.0, 360.0])
    y = form.predict({"k_ref": 2e-4, "Ea": 8e4}, {"tau_s": tau, "T_K": T}, {"T_ref_K": 350.0}) + np.array([0.01, -0.02])
    obs = FT.Observations(y, {"tau_s": tau, "T_K": T}, None, "LN_RETENTION", "SYNTHETIC")
    fit = FT.fit_least_squares(form, obs, starts=[{"k_ref": 1e-4, "Ea": 5e4}], fixed={"T_ref_K": 350.0},
                               backend="numpy")
    return form, obs, fit


def test_r2_unknown_sigma_with_no_residual_dof_is_never_identifiable() -> None:
    form, obs, fit = _exact_fit()
    assert fit.dof == 0 and not fit.sigma_known
    crit = ID.IdentifiabilityCriteria(0.95, {"k_ref": 2.0, "Ea": 1e5}, 6, 1e-8, None, None)
    rep = ID.assess_identifiability(form, obs, fit, crit, backend="numpy")
    assert rep.overall_verdict == "UNKNOWN"
    for p in rep.parameters:
        assert p.verdict == "UNKNOWN" and "NO_RESIDUAL_DOF_SIGMA_UNKNOWN" in p.reasons
        assert p.ci_low is None and p.ci_high is None
    assert rep.reportable_estimates() == {}
    assert "NO_RESIDUAL_DOF_SIGMA_UNKNOWN" in ID.REASONS


def test_r2_one_observation_one_parameter_is_unknown_too() -> None:
    form = M.FORMS["FIRST_ORDER"]
    obs = FT.Observations(np.array([-0.3]), {"tau_s": np.array([600.0])}, None, "LN_RETENTION", "SYNTHETIC")
    fit = FT.fit_least_squares(form, obs, starts=[{"k": 1e-3}], backend="numpy")
    rep = ID.assess_identifiability(form, obs, fit, ID.IdentifiabilityCriteria(0.95, {"k": 2.0}, 6, 1e-8, None, None),
                                    backend="numpy")
    assert rep.parameters[0].verdict == "UNKNOWN"


def test_r2_known_sigma_with_zero_dof_still_uses_the_known_scale() -> None:
    form = M.FORMS["FIRST_ORDER"]
    obs = FT.Observations(np.array([-0.3]), {"tau_s": np.array([600.0])}, np.array([0.01]), "LN_RETENTION",
                          "SYNTHETIC")
    fit = FT.fit_least_squares(form, obs, starts=[{"k": 1e-3}], backend="numpy")
    rep = ID.assess_identifiability(form, obs, fit, ID.IdentifiabilityCriteria(0.95, {"k": 2.0}, 6, 1e-8, None, None),
                                    backend="numpy")
    assert rep.parameters[0].verdict == "IDENTIFIABLE"


def test_r3_covariance_is_none_without_a_variance_estimate() -> None:
    _, _, fit = _exact_fit()
    assert fit.covariance_transformed() is None
