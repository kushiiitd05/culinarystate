"""Step 26c verification suite for sim_aa_1 / sim_chl_1 (S159, DRAFT_PENDING_26_0_H4).

Card (Plan v2 Step 26, 26c and "Solver"): analytic vs numeric, convergence under step refinement, mass balance,
units / dimensions, non-negativity, semigroup property, stiffness handling. Tolerances below are TEST SETTINGS
that mirror the PROPOSED_PILOT G26-VER numbers (rel. error <= 1e-6, observed order within +-0.2 of nominal,
mass-balance residual <= 1e-9); they are not the signed 26.0 pre-registration and pass nothing.
All parameters are synthetic (tests/fixtures/step26b_fixtures.py).
"""
from __future__ import annotations

import numpy as np
import pytest

from culinarystate.simulation import sim_aa_1, sim_chl_1, systems as S, verification as V
from culinarystate.simulation.kinetics import units as U
from tests.fixtures import step26b_fixtures as F

SCIPY = ("SCIPY_BDF", "SCIPY_RADAU", "SCIPY_LSODA")
TIMES = (0.0, 600.0, 1200.0, 1800.0)
STEP_T = ((0.0, 700.0, 352.0), (700.0, 1300.0, 369.0), (1300.0, 1800.0, 360.0))
REL_TOL = 1e-6          # test setting (G26-VER PROPOSED_PILOT value)
MB_TOL = 1e-9           # test setting (G26-VER PROPOSED_PILOT value)


def sim(system, cond, params, solver):
    return S.simulate(system, cond, params, appdec=F.appdec(event_id=cond.event_id), solver=solver,
                      ms_limits=F.limits(), form_id=F.FORM_ID)


def theta(params) -> dict[str, float]:
    return {x.symbol: x.value_si for x in params}


def has_scipy() -> bool:
    try:
        import scipy  # noqa: F401
    except ImportError:
        return False
    return True


# ----------------------------------------------------------------------------- analytic vs numeric
@pytest.mark.parametrize("segments", [((0.0, 1800.0, F.T_BATH),), STEP_T], ids=["isothermal", "step_T"])
@pytest.mark.parametrize("method", ["EXPM_PIECEWISE", "TRAPEZOID_FIXED", "RK4_FIXED", *SCIPY])
def test_first_order_closed_form_vs_integrator(method: str, segments) -> None:
    if method.startswith("SCIPY_") and not has_scipy():
        pytest.skip("scipy (optional extra step26) not installed")
    params = F.aa_params(k_l=None, k_p=None)
    cond = F.aa_conditions(contact="NO_WATER_CONTACT", sched=F.schedule(*segments))
    out = sim(F.AA, cond, params, F.solver(method, steps=256 if method == "TRAPEZOID_FIXED" else None))
    assert out.status == "COMPLETED", out.reasons
    ref = V.first_order_reference(theta(params), segments, TIMES)
    assert V.max_relative_error(out.outputs["retention_tissue"], ref) <= REL_TOL


@pytest.mark.parametrize("method", ["TRAPEZOID_FIXED", "RK4_FIXED", *SCIPY])
def test_full_aa_model_numeric_vs_matrix_exponential_reference(method: str) -> None:
    if method.startswith("SCIPY_") and not has_scipy():
        pytest.skip("scipy (optional extra step26) not installed")
    params = F.aa_params(k_dw=4e-5)
    cond = F.aa_conditions(kdw="ON", sched=F.schedule(*STEP_T))
    ref = sim(F.AA, cond, params, F.solver())
    out = sim(F.AA, cond, params, F.solver(method, steps=256 if method == "TRAPEZOID_FIXED" else None))
    for name in ("A_t", "A_w", "D"):
        assert V.max_relative_error(out.states[name][1:], ref.states[name][1:]) <= REL_TOL


def test_chl_closed_form_vs_integrator() -> None:
    params = F.chl_params()
    th = theta(params)
    cond = F.chl_conditions(sched=F.schedule(*STEP_T))
    out = sim(F.CHL, cond, params, F.solver("RK4_FIXED"))
    for pig in ("a", "b"):
        ref = V.first_order_reference({"k_ref": th[f"k_ref_{pig}"] * th["g_pH"], "Ea": th[f"Ea_{pig}"],
                                       "T_ref": th["T_ref"]}, STEP_T, TIMES)
        assert V.max_relative_error(out.outputs[f"retention_chl_{pig}"], ref) <= REL_TOL


# ----------------------------------------------------------------------------- convergence under refinement
@pytest.mark.parametrize("method, nominal, steps", [("TRAPEZOID_FIXED", 2, (4, 8, 16, 32)),
                                                    ("RK4_FIXED", 4, (16, 32, 64, 128))])
def test_observed_order_against_the_analytic_reference(method: str, nominal: int, steps) -> None:
    params = F.aa_params(k_ref=2e-3, k_l=2e-3, k_dw=1e-3)
    cond = F.aa_conditions(kdw="ON", sched=F.schedule(*STEP_T))
    ref = sim(F.AA, cond, params, F.solver())
    errs = []
    for n in steps:
        out = sim(F.AA, cond, params, F.solver(method, steps=n, stab=4.0))
        errs.append(V.max_relative_error(out.states["A_t"][1:], ref.states["A_t"][1:]))
    orders = V.observed_orders(errs, refinement=2)
    assert all(abs(o - nominal) <= 0.2 for o in orders), orders


def test_observed_order_with_the_product_temperature_lag_reference_free() -> None:
    params = F.aa_params(k_ref=2e-3, k_l=2e-3, tau_h=250.0)
    cond = F.aa_conditions(mode="LUMPED_LAG", tp0=300.0, sched=F.schedule(*STEP_T))
    sols = [np.array(sim(F.AA, cond, params, F.solver("TRAPEZOID_FIXED", steps=n, stab=4.0)).states["A_t"][1:])
            for n in (4, 8, 16, 32, 64)]
    diffs = [float(np.max(np.abs(a - b) / np.abs(b))) for a, b in zip(sols, sols[1:])]
    orders = V.observed_orders(diffs, refinement=2)
    assert all(abs(o - 2) <= 0.2 for o in orders), orders


def test_scipy_integrates_the_product_temperature_as_a_state() -> None:
    if not has_scipy():
        pytest.skip("scipy (optional extra step26) not installed")
    params = F.aa_params(tau_h=250.0)
    cond = F.aa_conditions(mode="LUMPED_LAG", tp0=300.0, sched=F.schedule(*STEP_T))
    out = sim(F.AA, cond, params, F.solver("SCIPY_RADAU"))
    ref = sim(F.AA, cond, params, F.solver("TRAPEZOID_FIXED", steps=2048))
    assert V.max_relative_error(out.outputs["T_p_K"], ref.outputs["T_p_K"]) <= 1e-10
    assert V.max_relative_error(out.states["A_t"][1:], ref.states["A_t"][1:]) <= REL_TOL


# ----------------------------------------------------------------------------- mass balance, non-negativity
@pytest.mark.parametrize("method", ["EXPM_PIECEWISE", "TRAPEZOID_FIXED", "RK4_FIXED", *SCIPY])
def test_mass_balance_and_non_negativity_every_run(method: str) -> None:
    if method.startswith("SCIPY_") and not has_scipy():
        pytest.skip("scipy (optional extra step26) not installed")
    rng = np.random.default_rng(26)
    for _ in range(4):
        params = F.aa_params(k_ref=float(np.exp(rng.uniform(-10, -6))), ea=float(rng.uniform(3e4, 1e5)),
                             k_l=float(np.exp(rng.uniform(-10, -6))), k_p=float(np.exp(rng.uniform(-8, -4))),
                             k_dw=float(np.exp(rng.uniform(-11, -7))))
        out = sim(F.AA, F.aa_conditions(kdw="ON", sched=F.schedule(*STEP_T)), params,
                  F.solver(method, mb_tol=MB_TOL, nn_tol=MB_TOL))
        assert out.status == "COMPLETED", out.reasons
        assert V.mass_balance_residual(out, sim_aa_1.SPEC) <= MB_TOL
        assert out.diagnostics["min_state"] >= -MB_TOL
    out = sim(F.CHL, F.chl_conditions(sched=F.schedule(*STEP_T)), F.chl_params(), F.solver(method))
    assert V.mass_balance_residual(out, sim_chl_1.SPEC) <= MB_TOL


def test_invariant_failure_is_reported_not_returned_as_an_estimate() -> None:
    # A stiff exchange integrated with a coarse fixed step and a permissive (wrong) stiffness limit:
    # the trapezoid rule is A-stable but not L-stable, so the fast mode rings and a state goes negative.
    params = F.aa_params(k_ref=2e-3, k_l=5.0, k_p=4e-3)
    out = sim(F.AA, F.aa_conditions(), params, F.solver("TRAPEZOID_FIXED", steps=3, stab=1e9,
                                                         times=(0.0, 200.0, 400.0, 600.0)))
    assert out.status == "FAILED_INVARIANT" and "NEGATIVE_STATE" in out.reasons
    assert out.outputs is None and out.states is None and out.diagnostics["min_state"] < 0


# ----------------------------------------------------------------------------- units / dimensions
@pytest.mark.parametrize("system", [F.AA, F.CHL])
def test_every_rate_term_has_dimension_time_inverse_and_arrhenius_is_dimensionless(system: str) -> None:
    report = V.rate_term_dimensions(S.SYSTEMS[system])
    assert report and all(v == U.CONSISTENT for v in report.values()), report


def test_slot_units_match_slot_dimensions() -> None:
    for spec, cond in ((sim_aa_1.SPEC, F.aa_conditions(kdw="ON", mode="LUMPED_LAG", tp0=300.0)),
                       (sim_chl_1.SPEC, F.chl_conditions(mode="LUMPED_LAG", tp0=300.0))):
        for slot in spec.slots(cond).values():
            assert U.check_unit(slot.si_unit, slot.dimension).verdict == U.CONSISTENT
            assert U.parse_unit(slot.si_unit).factor_to_si == 1


def test_water_ratio_conversion_is_exact() -> None:
    assert U.parse_unit("mL/g").factor_to_si * 4 == pytest.approx(4e-3, rel=0)
    assert U.check_dimensionless([("m^3/kg", 1), ("m^3/kg", -1)]).verdict == U.CONSISTENT


# ----------------------------------------------------------------------------- semigroup
def test_semigroup_property_at_constant_conditions() -> None:
    params = F.aa_params(k_dw=4e-5)
    cond = F.aa_conditions(kdw="ON")
    assert V.semigroup_residual(sim_aa_1.SPEC, theta(params), cond, F.T_BATH, 400.0, 700.0) <= 1e-13
    out = sim(F.AA, cond, params, F.solver(times=(0.0, 500.0, 1300.0)))
    x1 = np.array([out.states[n][1] for n in ("A_t", "A_w", "D")])
    x2 = np.array([out.states[n][2] for n in ("A_t", "A_w", "D")])
    phi = V.transition(sim_aa_1.SPEC, theta(params), cond, F.T_BATH, 800.0)
    assert np.max(np.abs(phi @ x1 - x2)) <= 1e-14


def test_expm_matches_scipy_reference() -> None:
    if not has_scipy():
        pytest.skip("scipy (optional extra step26) not installed")
    from scipy.linalg import expm as sexpm
    from culinarystate.simulation import sim_core as SC
    rng = np.random.default_rng(5)
    for scale in (1e-3, 1.0, 50.0, 5e3):
        G = rng.uniform(0.0, 1.0, size=(4, 4)) * scale       # compartment (generator) matrix: columns sum to 0
        np.fill_diagonal(G, 0.0)
        G -= np.diag(G.sum(axis=0))
        assert np.allclose(SC.expm(G), sexpm(G), rtol=1e-9, atol=1e-12)
        assert np.max(np.abs(SC.expm(G).sum(axis=0) - 1.0)) <= 1e-11


# ----------------------------------------------------------------------------- stiffness
def stiff():
    return F.aa_params(k_l=20.0, k_p=4e-3), F.aa_conditions()


def test_stiff_case_is_refused_for_a_fixed_step_beyond_its_limit() -> None:
    params, cond = stiff()
    out = sim(F.AA, cond, params, F.solver("RK4_FIXED", steps=64, stab=2.0))
    assert out.status == "SIM_PROHIBITED" and "STIFF_FOR_FIXED_STEP" in out.reasons
    assert out.diagnostics["max_rate_per_s"] > 20.0


@pytest.mark.parametrize("method", ["SCIPY_BDF", "SCIPY_RADAU", "SCIPY_LSODA"])
def test_stiff_case_is_solved_by_a_stiff_method(method: str) -> None:
    if not has_scipy():
        pytest.skip("scipy (optional extra step26) not installed")
    params, cond = stiff()
    ref = sim(F.AA, cond, params, F.solver(mb_tol=MB_TOL))
    out = sim(F.AA, cond, params, F.solver(method, mb_tol=MB_TOL))
    assert out.status == "COMPLETED", out.reasons
    assert out.diagnostics["stiffness_ratio"] > 1e4
    for name in ("A_t", "A_w", "D"):
        assert V.max_relative_error(out.states[name][1:], ref.states[name][1:]) <= REL_TOL
    assert out.provenance["solver"]["stiff_capable"] is True


def test_solver_metadata_records_the_method_family() -> None:
    for method, meta in S.SOLVER_METHODS.items():
        assert {"kind", "stiff_capable", "kisao", "kisao_status"} <= set(meta)
        assert meta["kisao_status"] in ("NOT_APPLICABLE", "AI_RECALLED_UNVERIFIED")
    assert S.SOLVER_METHODS["RK4_FIXED"]["stiff_capable"] is False
    assert S.SOLVER_METHODS["EXPM_PIECEWISE"]["kind"] == "ANALYTIC"
