"""Step 26b model structures sim_aa_1 and sim_chl_1 against the Plan v2 Step 26 card (S159, DRAFT_PENDING_26_0_H4).

Synthetic parameters only (tests/fixtures/step26b_fixtures.py). The card equations checked here:
AA  dA_t/dt = -k_d(T_p) A_t - k_L (A_t - (K_p/r) A_w); dA_w/dt = k_L (A_t - (K_p/r) A_w) - k_dw A_w;
    dD/dt = k_d(T_p) A_t + k_dw A_w; k_L = 0 without water contact; optional dT_p/dt = (T_b - T_p) / tau_h.
CHL Chl_x -> Pheo_x first order, k_x(T) * g(pH), no leaching term; pH a required input.
"""
from __future__ import annotations

import numpy as np
import pytest

from culinarystate.simulation import sim_aa_1, sim_chl_1, systems as S
from culinarystate.simulation.kinetics import models as M
from tests.fixtures import step26b_fixtures as F

TIMES = (0.0, 600.0, 1200.0, 1800.0)


def sim(system: str, cond, params, **kw):
    kw.setdefault("appdec", F.appdec(event_id=cond.event_id))
    kw.setdefault("solver", F.solver())
    kw.setdefault("ms_limits", F.limits())
    return S.simulate(system, cond, params, form_id=F.FORM_ID, **kw)


def theta(params) -> dict[str, float]:
    return {x.symbol: x.value_si for x in params}


# ----------------------------------------------------------------------------- sim_aa_1 structure
def test_aa_rate_matrix_is_the_card_compartment_model() -> None:
    cond = F.aa_conditions(kdw="ON")
    th = theta(F.aa_params(k_dw=5e-5))
    Mx = sim_aa_1.SPEC.rate_matrix(th, cond, F.T_BATH)
    kd = float(M.arrhenius_rate(th["k_ref"], th["Ea"], np.array([F.T_BATH]), th["T_ref"])[0])
    kl, b, kdw = th["k_L"], th["k_L"] * th["K_p"] / cond.system_inputs["water_ratio_m3_per_kg"], th["k_dw"]
    want = np.array([[-(kd + kl), b, 0.0], [kl, -(b + kdw), 0.0], [kd, kdw, 0.0]])
    assert np.allclose(Mx, want, rtol=1e-14, atol=0.0)
    assert np.allclose(Mx.sum(axis=0), 0.0, atol=1e-18)           # columns conserve A_t + A_w + D
    assert sim_aa_1.SPEC.state_names == ("A_t", "A_w", "D") and sim_aa_1.SPEC.initial_state == (1, 0, 0)


def test_aa_without_water_contact_reduces_to_first_order_arrhenius_closed_form() -> None:
    sched = F.schedule((0.0, 900.0, 355.0), (900.0, 1800.0, 368.0))
    cond = F.aa_conditions(contact="NO_WATER_CONTACT", sched=sched)
    params = F.aa_params(k_l=None, k_p=None)
    out = sim(F.AA, cond, params)
    assert out.status == "COMPLETED", out.reasons
    th = theta(params)
    ref = M.ln_retention_first_order_piecewise(th["k_ref"], th["Ea"], th["T_ref"],
                                               [(0.0, 900.0, 355.0), (900.0, 1800.0, 368.0)], np.array(TIMES))
    assert np.allclose(np.log(out.outputs["retention_tissue"]), ref, rtol=1e-12, atol=1e-15)
    assert max(abs(x) for x in out.outputs["fraction_water"]) == 0.0


def test_aa_leaching_term_needs_water_contact() -> None:
    out = sim(F.AA, F.aa_conditions(contact="NO_WATER_CONTACT"), F.aa_params())
    assert {"PARAM_UNEXPECTED_K_L", "PARAM_UNEXPECTED_K_P"} <= set(out.reasons)


def test_aa_k_dw_mode_is_required_and_switches_the_slot() -> None:
    assert "PARAM_UNEXPECTED_K_DW" in sim(F.AA, F.aa_conditions(kdw="OFF"), F.aa_params(k_dw=1e-5)).reasons
    assert "PARAM_MISSING_K_DW" in sim(F.AA, F.aa_conditions(kdw="ON"), F.aa_params()).reasons
    out = sim(F.AA, F.aa_conditions(contact="NO_WATER_CONTACT", kdw="ON"), F.aa_params(k_l=None, k_p=None,
                                                                                       k_dw=1e-5))
    assert "K_DW_WITHOUT_WATER_CONTACT" in out.reasons


def test_aa_leaching_moves_mass_to_water_and_conserves_the_total() -> None:
    out = sim(F.AA, F.aa_conditions(kdw="ON"), F.aa_params(k_dw=5e-5))
    assert out.status == "COMPLETED"
    tot = (np.array(out.outputs["retention_tissue"]) + np.array(out.outputs["fraction_water"])
           + np.array(out.outputs["fraction_degraded"]))
    assert np.max(np.abs(tot - 1.0)) <= 1e-12
    assert out.outputs["fraction_water"][-1] > 0 and out.diagnostics["mass_balance_residual"] <= 1e-12
    assert np.all(np.diff(out.outputs["retention_tissue"]) < 0)


def test_aa_partition_term_sets_the_quasi_equilibrium_ratio() -> None:
    # Degradation made negligible; the exchange term vanishes at A_t = (K_p / r) A_w, so A_w / A_t -> r / K_p.
    cond = F.aa_conditions(duration=1800.0)
    params = F.aa_params(k_ref=1e-12, k_l=5e-2)
    out = sim(F.AA, cond, params, solver=F.solver(times=(0.0, 1800.0)))
    ratio = out.outputs["fraction_water"][-1] / out.outputs["retention_tissue"][-1]
    want = cond.system_inputs["water_ratio_m3_per_kg"] / theta(params)["K_p"]
    assert ratio == pytest.approx(want, rel=1e-6)


def test_aa_product_temperature_lag_is_flagged_extrapolated_and_slows_loss() -> None:
    lag_cond = F.aa_conditions(mode="LUMPED_LAG", tp0=300.0)
    out_lag = sim(F.AA, lag_cond, F.aa_params(tau_h=300.0), solver=F.solver("TRAPEZOID_FIXED", steps=400))
    out_bath = sim(F.AA, F.aa_conditions(), F.aa_params())
    assert out_lag.status == "COMPLETED", out_lag.reasons
    assert "T_P_LAG_EXTRAPOLATED" in out_lag.flags and "T_P_LAG_EXTRAPOLATED" not in out_bath.flags
    tp = np.array(out_lag.outputs["T_p_K"])
    want = F.T_BATH + (300.0 - F.T_BATH) * np.exp(-np.array(TIMES) / 300.0)
    assert np.allclose(tp, want, rtol=1e-12)
    assert out_lag.outputs["retention_tissue"][-1] > out_bath.outputs["retention_tissue"][-1]


def test_aa_lag_time_constant_must_match_the_piece_size_class() -> None:
    params = [x for x in F.aa_params()] + [F.p("tau_h", 300.0, "s", size="SIZE_CLASS_B")]
    out = sim(F.AA, F.aa_conditions(mode="LUMPED_LAG", tp0=300.0), params,
              solver=F.solver("TRAPEZOID_FIXED"))
    assert "NO_COMPATIBLE_SIZE_CLASS_TAU_H" in out.reasons
    params = [x for x in F.aa_params()] + [F.p("tau_h", 300.0, "s", size=None)]
    out = sim(F.AA, F.aa_conditions(mode="LUMPED_LAG", tp0=300.0), params, solver=F.solver("TRAPEZOID_FIXED"))
    assert "NO_COMPATIBLE_SIZE_CLASS_TAU_H" in out.reasons


def test_aa_initial_product_temperature_only_with_the_lag() -> None:
    out = sim(F.AA, F.aa_conditions(mode="BATH_EQUALS_PRODUCT", tp0=300.0), F.aa_params())
    assert "INPUT_UNEXPECTED_INITIAL_PRODUCT_TEMPERATURE" in out.reasons
    out = sim(F.AA, F.aa_conditions(mode="SOMETIMES"), F.aa_params())
    assert "INPUT_INVALID_PRODUCT_TEMPERATURE_MODE" in out.reasons


def test_aa_outputs_are_fractions_of_the_initial_tissue_amount() -> None:
    out = sim(F.AA, F.aa_conditions(), F.aa_params())
    assert set(out.outputs) >= {"retention_tissue", "fraction_water", "fraction_degraded", "ln_retention_tissue"}
    assert out.outputs["retention_tissue"][0] == 1.0 and out.outputs["fraction_water"][0] == 0.0
    assert np.allclose(np.exp(out.outputs["ln_retention_tissue"]), out.outputs["retention_tissue"], rtol=1e-15)
    assert set(out.states) == {"A_t", "A_w", "D"}


# ----------------------------------------------------------------------------- sim_chl_1 structure
def test_chl_is_two_first_order_pigment_pathways_times_a_ph_modifier() -> None:
    params = F.chl_params()
    out = sim(F.CHL, F.chl_conditions(), params)
    assert out.status == "COMPLETED", out.reasons
    th = theta(params)
    tau = np.array(TIMES)
    for pig in ("a", "b"):
        k = float(M.arrhenius_rate(th[f"k_ref_{pig}"], th[f"Ea_{pig}"], np.array([F.T_BATH]), th["T_ref"])[0])
        want = np.exp(-k * th["g_pH"] * tau)
        assert np.allclose(out.outputs[f"retention_chl_{pig}"], want, rtol=1e-12)
        assert np.allclose(np.array(out.outputs[f"retention_chl_{pig}"]) + np.array(out.outputs[f"fraction_pheo_{pig}"]),
                           1.0, atol=1e-12)
    assert out.provenance["kinetic_forms"] == ["ARRHENIUS_REF_T"]
    assert sim_chl_1.SPEC.conservation == ((1, 0, 1, 0), (0, 1, 0, 1))


def test_chl_ph_is_required_and_must_lie_in_the_modifier_validity() -> None:
    assert "INPUT_MISSING_MEDIUM_PH" in sim(F.CHL, F.chl_conditions(ph=None), F.chl_params()).reasons
    assert "PH_OUTSIDE_MODIFIER_VALIDITY" in sim(F.CHL, F.chl_conditions(ph=7.5), F.chl_params()).reasons
    assert "PH_MODIFIER_VALIDITY_MISSING" in sim(F.CHL, F.chl_conditions(), F.chl_params(ph=None)).reasons


def test_chl_has_no_leaching_term() -> None:
    params = F.chl_params() + [F.p("k_L", 1e-4, "1/s")]
    assert "PARAM_UNEXPECTED_K_L" in sim(F.CHL, F.chl_conditions(), params).reasons
    names = {s.symbol for s in sim_chl_1.SPEC.slots(F.chl_conditions()).values()}
    assert names == {"k_ref_a", "Ea_a", "k_ref_b", "Ea_b", "T_ref", "g_pH"}


def test_chl_lag_mode_shares_the_product_temperature_structure() -> None:
    out = sim(F.CHL, F.chl_conditions(mode="LUMPED_LAG", tp0=300.0), F.chl_params(tau_h=200.0),
              solver=F.solver("TRAPEZOID_FIXED", steps=200))
    assert out.status == "COMPLETED" and "T_P_LAG_EXTRAPOLATED" in out.flags


def test_both_systems_share_one_result_shape() -> None:
    a = sim(F.AA, F.aa_conditions(), F.aa_params())
    c = sim(F.CHL, F.chl_conditions(), F.chl_params())
    assert type(a) is type(c)
    assert set(a.provenance) == set(c.provenance) and set(a.diagnostics) == set(c.diagnostics)
