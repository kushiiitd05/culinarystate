"""Tests of the Step 26a unit / dimension checker (S159, DRAFT_PENDING_26_0_H4).

Unit strings and dimension expressions only; no parameter value of any food system appears here.
SSOT 210.30: rate-constant units depend on the order and are never harmonised across orders.
G24.3: Kelvin in Arrhenius. KIN v1.1: s / min / h / d / week convert exactly; month / year never do.
"""
from __future__ import annotations

from fractions import Fraction

import pytest

from culinarystate.lineage.kinetic_contract import SECONDS_PER_UNIT
from culinarystate.simulation.kinetics import units as U

OPAQUE = {"u": "CONCENTRATION"}


def test_status_header() -> None:
    assert U.STATUS == "DRAFT_PENDING_26_0_H4"


def test_dimension_algebra_and_canonical_text() -> None:
    d = U.dimension("CONCENTRATION^-1*TIME^-1")
    assert d == U.dimension("TIME^-1*CONCENTRATION^-1")
    assert str(d) == "CONCENTRATION^-1*TIME^-1"
    assert U.dimension("1").is_dimensionless()
    assert (U.dimension("TIME") * U.dimension("TIME^-1")).is_dimensionless()
    assert U.dimension("ENERGY") == U.dimension("MASS*LENGTH^2*TIME^-2")
    assert U.dimension("CONCENTRATION^-1/2").exponents == (("CONCENTRATION", Fraction(-1, 2)),)
    assert U.dimension("TIME") ** 2 == U.dimension("TIME^2")
    assert U.dimension("TIME") / U.dimension("TIME") == U.dimension("1")


@pytest.mark.parametrize("bad", ["FURLONG", "TIME^x", "", "TIME**2", "time"])
def test_bad_dimension_expression_raises(bad: str) -> None:
    with pytest.raises(U.UnitError):
        U.dimension(bad)


@pytest.mark.parametrize("unit, dim", [
    ("s", "TIME"), ("min", "TIME"), ("h", "TIME"), ("d", "TIME"), ("week", "TIME"), ("month", "TIME"),
    ("1/s", "TIME^-1"), ("min^-1", "TIME^-1"), ("s^-1", "TIME^-1"), ("K", "TEMPERATURE"),
    ("J/mol", "ENERGY*AMOUNT^-1"), ("kJ/mol", "ENERGY*AMOUNT^-1"), ("kJ*mol^-1", "ENERGY*AMOUNT^-1"),
    ("J/(mol*K)", "ENERGY*AMOUNT^-1*TEMPERATURE^-1"), ("u/min", "CONCENTRATION*TIME^-1"),
    ("1/(u*min)", "CONCENTRATION^-1*TIME^-1"), ("1", "1"), ("mg", "MASS"), ("mL", "LENGTH^3"),
])
def test_parse_unit_dimension(unit: str, dim: str) -> None:
    assert U.parse_unit(unit, opaque=OPAQUE).dimension == U.dimension(dim)


def test_bracketed_opaque_concentration_token() -> None:
    p = U.parse_unit("[mg/100g]/min", opaque={"[mg/100g]": "CONCENTRATION"})
    assert p.dimension == U.dimension("CONCENTRATION*TIME^-1") and p.factor_to_si is None


def test_unknown_token_raises_in_parse_and_is_unknown_in_check() -> None:
    with pytest.raises(U.UnitError):
        U.parse_unit("1/fortnight")
    c = U.check_unit("1/fortnight", "TIME^-1")
    assert c.verdict == U.UNKNOWN and "UNIT_TOKEN_UNKNOWN" in c.detail


@pytest.mark.parametrize("unit", [None, "", "UNKNOWN"])
def test_missing_unit_is_unknown_not_a_default(unit: str | None) -> None:
    assert U.check_unit(unit, "TIME^-1").verdict == U.UNKNOWN


def test_time_factors_are_the_kin_v1_1_exact_factors() -> None:
    for token, factor in SECONDS_PER_UNIT.items():
        assert U.parse_unit(token).factor_to_si == Fraction(factor)
    assert U.parse_unit("month").factor_to_si is None and U.parse_unit("year").factor_to_si is None
    assert U.parse_unit("1/min").factor_to_si == Fraction(1, 60)
    assert U.parse_unit("kJ/mol").factor_to_si == Fraction(1000)


def test_to_si() -> None:
    assert U.to_si(2.0, "min") == 120.0
    assert U.to_si(3.0, "1/min") == pytest.approx(0.05, rel=1e-15)
    assert U.to_si(1.0, "1/month") is None
    assert U.to_si(1.0, "degC") is None
    assert U.to_si(1.0, "u/min", opaque=OPAQUE) is None


@pytest.mark.parametrize("order, unit, verdict", [
    (0, "u/min", U.CONSISTENT), (1, "1/min", U.CONSISTENT), (2, "1/(u*min)", U.CONSISTENT),
    (Fraction(3, 2), "u^-1/2*min^-1", U.CONSISTENT),
    (0, "1/min", U.INCONSISTENT), (1, "u/min", U.INCONSISTENT), (2, "1/min", U.INCONSISTENT),
    (1, "min", U.INCONSISTENT),
])
def test_rate_constant_units_by_order(order: Fraction | int, unit: str, verdict: str) -> None:
    assert U.rate_constant_dimension(order) == U.dimension("CONCENTRATION") ** (1 - Fraction(order)) \
        * U.dimension("TIME^-1")
    assert U.check_rate_constant_unit(unit, order, opaque=OPAQUE).verdict == verdict


@pytest.mark.parametrize("ea, t, verdict", [
    ("kJ/mol", "K", U.CONSISTENT), ("J/mol", "K", U.CONSISTENT),
    ("kJ/mol", "degC", U.INCONSISTENT), ("kJ", "K", U.INCONSISTENT), ("J/mol", "min", U.INCONSISTENT),
    (None, "K", U.UNKNOWN),
])
def test_arrhenius_units_need_energy_per_amount_and_kelvin(ea: str | None, t: str, verdict: str) -> None:
    assert U.check_arrhenius_units(ea, t).verdict == verdict


def test_dimensionless_group_check() -> None:
    assert U.check_dimensionless([("1/min", 1), ("min", 1)]).verdict == U.CONSISTENT
    assert U.check_dimensionless([("1/min", 1), ("h", 1)]).verdict == U.CONSISTENT  # dimension, not factor
    assert U.check_dimensionless([("1/min", 1), ("K", 1)]).verdict == U.INCONSISTENT
    assert U.check_dimensionless([("degC", 1)]).verdict == U.INCONSISTENT


def test_gas_constant_is_the_exact_si_product_of_defining_constants() -> None:
    assert U.AVOGADRO_PER_MOL == 6.02214076e23 and U.BOLTZMANN_J_PER_K == 1.380649e-23
    assert U.GAS_CONSTANT_J_PER_MOL_K == U.AVOGADRO_PER_MOL * U.BOLTZMANN_J_PER_K
    assert U.parse_unit(U.GAS_CONSTANT_UNIT).dimension == U.dimension("ENERGY*AMOUNT^-1*TEMPERATURE^-1")
