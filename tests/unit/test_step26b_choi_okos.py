"""Step 26b Choi-Okos composition property structure (S159, DRAFT_PENDING_26_0_H4).

The correlation coefficients are literature values that are NOT entered: every coefficient here is a synthetic
placeholder generated in the test, supplied as a caller PARAM input. Tested: the mixing structure (mass-fraction
cp, inverse-sum density, volume-fraction parallel conductivity), lumped time constant and Biot check, refusals.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from culinarystate.simulation import choi_okos as CO

COMP = {"WATER": 0.8, "SOLIDS": 0.2}


def corr(component: str, prop: str, coeffs: tuple[float, ...], lo: float = 270.0, hi: float = 400.0):
    pid = f"SYNTH-PARAM-{component}-{prop}".upper()
    return CO.PropertyCorrelation(pid, component, prop, coeffs, CO.PROPERTY_UNITS.get(prop, "1"), (lo, hi), "SYNTHETIC")


def corrs() -> list[CO.PropertyCorrelation]:
    # Synthetic polynomials in T_degC (placeholders, not Choi-Okos coefficients).
    return [corr("WATER", "cp", (4000.0, 1.0)), corr("WATER", "rho", (1000.0, -0.5)), corr("WATER", "k", (0.5, 1e-3)),
            corr("SOLIDS", "cp", (1500.0, 2.0, 1e-3)), corr("SOLIDS", "rho", (1400.0,)), corr("SOLIDS", "k", (0.2,))]


def test_header_and_no_float_literal() -> None:
    src = Path(CO.__file__).read_text(encoding="utf-8")
    assert CO.STATUS == "DRAFT_PENDING_26_0_H4" and "DRAFT_PENDING_26_0_H4" in src.splitlines()[0]
    tree = ast.parse(src)
    assert [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, float)] == []
    assert any("Choi" in s and "OPEN" in s for s in CO.OPEN_FOR_HUMANS)


def test_component_polynomial_is_in_degc_from_kelvin() -> None:
    c = corr("WATER", "cp", (4000.0, 1.0, 0.25))
    t_c = 350.0 - 273.15
    assert CO.component_property(c, 350.0) == pytest.approx(4000.0 + t_c + 0.25 * t_c ** 2, rel=1e-15)
    with pytest.raises(CO.ChoiOkosRefusal, match="OUTSIDE_T_VALIDITY"):
        CO.component_property(c, 401.0)


def test_mixture_rules() -> None:
    T = 350.0
    t_c = T - 273.15
    est = CO.mixture_properties(COMP, corrs(), T, fraction_sum_tol=1e-12)
    cp_w, cp_s = 4000.0 + t_c, 1500.0 + 2.0 * t_c + 1e-3 * t_c ** 2
    rho_w, rho_s = 1000.0 - 0.5 * t_c, 1400.0
    k_w, k_s = 0.5 + 1e-3 * t_c, 0.2
    rho = 1.0 / (0.8 / rho_w + 0.2 / rho_s)
    v_w, v_s = 0.8 / rho_w * rho, 0.2 / rho_s * rho
    assert est.cp == pytest.approx(0.8 * cp_w + 0.2 * cp_s, rel=1e-14)
    assert est.rho == pytest.approx(rho, rel=1e-14)
    assert est.k == pytest.approx(v_w * k_w + v_s * k_s, rel=1e-14)
    assert est.origin == "MODEL_DERIVED" and est.is_evidence is False
    assert est.derived_from == tuple(sorted(c.param_id for c in corrs()))


def test_refusals() -> None:
    with pytest.raises(CO.ChoiOkosRefusal, match="FRACTIONS_DO_NOT_SUM"):
        CO.mixture_properties({"WATER": 0.8, "SOLIDS": 0.3}, corrs(), 350.0, fraction_sum_tol=1e-12)
    with pytest.raises(CO.ChoiOkosRefusal, match="CORRELATION_MISSING"):
        CO.mixture_properties(COMP, corrs()[:-1], 350.0, fraction_sum_tol=1e-12)
    with pytest.raises(CO.ChoiOkosRefusal, match="CORRELATION_DUPLICATE"):
        CO.mixture_properties(COMP, corrs() + corrs()[:1], 350.0, fraction_sum_tol=1e-12)
    with pytest.raises(CO.ChoiOkosRefusal, match="FRACTION_NEGATIVE"):
        CO.mixture_properties({"WATER": 1.2, "SOLIDS": -0.2}, corrs(), 350.0, fraction_sum_tol=1e-12)
    with pytest.raises(CO.ChoiOkosError):
        corr("WATER", "viscosity", (1.0,))
    with pytest.raises(CO.ChoiOkosError):
        CO.PropertyCorrelation("SYNTH-PARAM-X", "WATER", "cp", (), "J/(kg*K)", (270.0, 400.0), "SYNTHETIC")
    with pytest.raises(CO.ChoiOkosError):
        CO.PropertyCorrelation("SYNTH-PARAM-X", "WATER", "cp", (1.0,), "kJ/(kg*K)", (270.0, 400.0), "SYNTHETIC")
    with pytest.raises(CO.ChoiOkosRefusal, match="PROPERTY_NOT_POSITIVE"):
        CO.mixture_properties(COMP, [c if c.property != "rho" or c.component != "SOLIDS"
                                     else corr("SOLIDS", "rho", (-1.0,)) for c in corrs()], 350.0,
                              fraction_sum_tol=1e-12)


def test_lumped_time_constant_and_biot_guard() -> None:
    est = CO.mixture_properties(COMP, corrs(), 350.0, fraction_sum_tol=1e-12)
    h = CO.SurfaceCoefficient("SYNTH-PARAM-H", 50.0, "J/(s*m^2*K)", "SYNTHETIC")
    tau = CO.tau_h_param(est, h, characteristic_length_m=0.002, geometry_ref="SYNTH-GEOM-1", max_biot=0.5,
                         matrix_class="MATRIX_X", piece_size_class="SIZE_CLASS_A")
    assert tau.symbol == "tau_h" and tau.unit_si == "s" and tau.origin == "MODEL_DERIVED"
    assert tau.value_si == pytest.approx(est.rho * est.cp * 0.002 / 50.0, rel=1e-15)
    assert tau.param_id.startswith("DERIVED-") and tau.piece_size_class == "SIZE_CLASS_A"
    assert CO.biot_number(50.0, 0.002, est.k) == pytest.approx(50.0 * 0.002 / est.k, rel=1e-15)
    with pytest.raises(CO.ChoiOkosRefusal, match="LUMPED_CAPACITANCE_INVALID"):
        CO.tau_h_param(est, h, characteristic_length_m=0.05, geometry_ref="SYNTH-GEOM-1", max_biot=0.5,
                       matrix_class="MATRIX_X", piece_size_class="SIZE_CLASS_A")
    same = CO.tau_h_param(est, h, characteristic_length_m=0.002, geometry_ref="SYNTH-GEOM-1", max_biot=0.5,
                          matrix_class="MATRIX_X", piece_size_class="SIZE_CLASS_A")
    assert same.param_id == tau.param_id
