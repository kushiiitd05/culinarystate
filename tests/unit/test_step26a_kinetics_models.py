"""Tests of the Step 26a kinetic model forms (S159, DRAFT_PENDING_26_0_H4).

All parameter values below are SYNTHETIC TEST VALUES chosen inside the test to check algebra; none is a
literature or fitted value for any food system. Forms are only those the Plan v2 Step 26 / 24 cards name.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from culinarystate.simulation.kinetics import models as M
from culinarystate.simulation.kinetics import units as U

R = U.GAS_CONSTANT_J_PER_MOL_K
TAU = np.array([0.0, 60.0, 300.0, 900.0, 1800.0])


def test_status_and_registered_forms() -> None:
    assert M.STATUS == "DRAFT_PENDING_26_0_H4"
    assert set(M.FORMS) == {"ZERO_ORDER", "FIRST_ORDER", "WEIBULL", "ARRHENIUS_REF_T", "FIRST_ORDER_ARRHENIUS"}
    assert set(M.CARD_NAMED_FORMS) == set(M.FORMS) and M.AI_PROPOSED_FORMS == ()
    for f in M.FORMS.values():
        assert f.card_ref and f.kin_family in {"ZERO_ORDER", "FIRST_ORDER", "WEIBULL", "ARRHENIUS_SECONDARY"}


def test_forms_hold_no_parameter_values() -> None:
    for f in M.FORMS.values():
        for p in f.parameters:
            assert set(vars(p)) == {"symbol", "dimension", "transform", "role", "description"}


@pytest.mark.parametrize("name", sorted(M.FORMS))
def test_every_form_is_dimensionally_consistent(name: str) -> None:
    assert M.check_form_dimensions(M.FORMS[name]).verdict == U.CONSISTENT


def test_first_order_matches_closed_form() -> None:
    k = 1.3e-3
    got = M.FORMS["FIRST_ORDER"].predict({"k": k}, {"tau_s": TAU})
    np.testing.assert_allclose(got, -k * TAU, rtol=0, atol=1e-15)


def test_zero_order_matches_closed_form() -> None:
    got = M.FORMS["ZERO_ORDER"].predict({"C0": 5.0, "k0": 1e-3}, {"tau_s": TAU})
    np.testing.assert_allclose(got, 5.0 - 1e-3 * TAU, rtol=1e-15)


def test_weibull_reduces_to_first_order_at_shape_one() -> None:
    alpha = 700.0
    w = M.FORMS["WEIBULL"].predict({"alpha": alpha, "beta": 1.0}, {"tau_s": TAU})
    f = M.FORMS["FIRST_ORDER"].predict({"k": 1.0 / alpha}, {"tau_s": TAU})
    np.testing.assert_allclose(w, f, rtol=1e-14, atol=1e-15)


def test_arrhenius_equals_k_ref_at_t_ref_and_is_kelvin_only() -> None:
    k = M.arrhenius_rate(2e-3, 7.0e4, np.array([350.0]), 350.0)
    assert k[0] == pytest.approx(2e-3, rel=1e-15)
    ln_k = M.FORMS["ARRHENIUS_REF_T"].predict({"k_ref": 2e-3, "Ea": 7.0e4}, {"T_K": np.array([340.0, 360.0])},
                                              {"T_ref_K": 350.0})
    expect = math.log(2e-3) - (7.0e4 / R) * (1 / np.array([340.0, 360.0]) - 1 / 350.0)
    np.testing.assert_allclose(ln_k, expect, rtol=1e-14)
    with pytest.raises(M.ModelError):
        M.arrhenius_rate(2e-3, 7.0e4, np.array([-5.0]), 350.0)


def test_t_ref_is_required_and_never_defaulted() -> None:
    with pytest.raises(M.ModelError, match="T_ref_K"):
        M.FORMS["FIRST_ORDER_ARRHENIUS"].predict({"k_ref": 1e-3, "Ea": 5e4},
                                                 {"tau_s": TAU, "T_K": np.full(TAU.shape, 350.0)})


def test_missing_parameter_or_covariate_raises() -> None:
    with pytest.raises(M.ModelError):
        M.FORMS["FIRST_ORDER"].predict({}, {"tau_s": TAU})
    with pytest.raises(M.ModelError):
        M.FORMS["FIRST_ORDER"].predict({"k": 1e-3}, {})
    with pytest.raises(M.ModelError):
        M.FORMS["FIRST_ORDER"].predict({"k": 1e-3}, {"tau_s": np.array([-1.0])})


def test_first_order_arrhenius_isothermal_equals_first_order_at_k_of_t() -> None:
    T = np.full(TAU.shape, 360.0)
    got = M.FORMS["FIRST_ORDER_ARRHENIUS"].predict({"k_ref": 1e-3, "Ea": 6e4}, {"tau_s": TAU, "T_K": T},
                                                   {"T_ref_K": 350.0})
    k = M.arrhenius_rate(1e-3, 6e4, T, 350.0)
    np.testing.assert_allclose(got, -k * TAU, rtol=1e-14)


def test_piecewise_constant_temperature_is_the_sum_of_segments() -> None:
    segs = ((0.0, 120.0, 330.0), (120.0, 600.0, 360.0), (600.0, 2000.0, 345.0))
    tau = np.array([0.0, 60.0, 120.0, 300.0, 600.0, 1500.0])
    got = M.ln_retention_first_order_piecewise(1e-3, 6e4, 350.0, segs, tau)
    k = [M.arrhenius_rate(1e-3, 6e4, np.array([T]), 350.0)[0] for _, _, T in segs]
    expect = [0.0, -k[0] * 60, -k[0] * 120, -k[0] * 120 - k[1] * 180, -k[0] * 120 - k[1] * 480,
              -k[0] * 120 - k[1] * 480 - k[2] * 900]
    np.testing.assert_allclose(got, expect, rtol=1e-13, atol=1e-16)


def test_piecewise_semigroup_property_at_constant_temperature() -> None:
    one = M.ln_retention_first_order_piecewise(1e-3, 6e4, 350.0, ((0.0, 1000.0, 355.0),), np.array([1000.0]))
    two = M.ln_retention_first_order_piecewise(1e-3, 6e4, 350.0, ((0.0, 400.0, 355.0), (400.0, 1000.0, 355.0)),
                                               np.array([1000.0]))
    assert one[0] == pytest.approx(two[0], rel=1e-14)


@pytest.mark.parametrize("segs", [
    ((0.0, 100.0, 350.0), (150.0, 200.0, 350.0)),     # gap
    ((10.0, 100.0, 350.0),),                           # does not start at 0
    ((0.0, 100.0, -1.0),),                             # not Kelvin
    ((0.0, 100.0, 350.0), (50.0, 200.0, 350.0)),       # overlap
])
def test_piecewise_schedule_is_validated(segs: tuple[tuple[float, float, float], ...]) -> None:
    with pytest.raises(M.ModelError):
        M.ln_retention_first_order_piecewise(1e-3, 6e4, 350.0, segs, np.array([50.0]))


def test_piecewise_refuses_times_beyond_the_schedule() -> None:
    with pytest.raises(M.ModelError):
        M.ln_retention_first_order_piecewise(1e-3, 6e4, 350.0, ((0.0, 100.0, 350.0),), np.array([150.0]))
