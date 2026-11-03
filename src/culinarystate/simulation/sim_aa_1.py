"""sim_aa_1: ascorbic-acid tissue / water / degraded compartment model (S159, DRAFT_PENDING_26_0_H4).

Structure only, from the Plan v2 Step 26 card "Architecture detail" (SIM-AA-1, leading candidate, not frozen:
R-14; the 26.0 record decides the system). No parameter value, default, prior or literature number is held here.

States (fractions of the initial tissue amount A_t(0); A_0 cancels): A_t tissue, A_w cooking water, D degraded.
Initial state (1, 0, 0) is the card's A_w(0) = 0, D(0) = 0. Basis stays "reduced AA"; no DHA compartment.

    k_d(T)  = k_ref * exp(-(Ea/R)(1/T - 1/T_ref))                  (26a ARRHENIUS_REF_T, models.arrhenius_rate)
    dA_t/dt = -k_d(T_p) A_t - k_L (A_t - (K_p/r) A_w)
    dA_w/dt = +k_L (A_t - (K_p/r) A_w) - k_dw A_w
    dD/dt   = +k_d(T_p) A_t + k_dw A_w                             (columns sum to zero: A_t + A_w + D = 1)

Switches are required inputs, never defaulted:
- ``medium_contact`` WATER_IMMERSION (k_L, K_p required, r = water_ratio_m3_per_kg required) or NO_WATER_CONTACT
  (card: "k_L = 0 for steam / sealed / no-water media"; k_L and K_p must then not be supplied);
- ``k_dw_mode`` ON (k_dw required) or OFF (card: "k_dw default OFF" is recorded as an explicit caller choice);
  ON without water contact is refused (A_w stays 0);
- product temperature: core ``product_temperature_mode`` (tau_h for the piece-size class in LUMPED_LAG).

Dimensions: r = V_w / m_t keeps the 26g unit mL/g (SI m^3/kg), so K_p carries LENGTH^3*MASS^-1 and K_p/r is
dimensionless. The card's "K_p default 1" assumes a dimensionless r; no default is used and the dimension choice
is OPEN for H4 (systems.OPEN_FOR_HUMANS). k_L is not temperature dependent in the card equations.
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from pathlib import Path

import numpy as np

from culinarystate.simulation import sim_core as SC
from culinarystate.simulation.kinetics import models as M

STATUS = "DRAFT_PENDING_26_0_H4"
SYSTEM_ID = "sim_aa_1"
MODEL_STRUCTURE_ID = "SIM-AA-1-STRUCTURE-0.1.0-draft"
CARD_REF = "Plan v2 Step 26 card, Architecture detail: state variables, equations, product temperature, solver"
MEDIUM_CONTACT = ("WATER_IMMERSION", "NO_WATER_CONTACT")
K_DW_MODES = ("ON", "OFF")
R = M.R

SLOTS: Mapping[str, SC.Slot] = {s.symbol: s for s in (
    SC.Slot("k_ref", "TIME^-1", "1/s", "POSITIVE", "first-order degradation rate constant at T_ref (order 1)"),
    SC.Slot("Ea", "ENERGY*AMOUNT^-1", "J/mol", "FINITE", "activation energy of degradation"),
    SC.Slot("T_ref", "TEMPERATURE", "K", "POSITIVE", "pre-declared reference temperature (card: centre of the "
                                                    "calibration T range)"),
    SC.Slot("k_L", "TIME^-1", "1/s", "NONNEGATIVE", "lumped leaching rate constant (0 = leaching off, E26-4)"),
    SC.Slot("K_p", "LENGTH^3*MASS^-1", "m^3/kg", "POSITIVE", "partition coefficient in the r = V_w/m_t dimension"),
    SC.Slot("k_dw", "TIME^-1", "1/s", "NONNEGATIVE", "first-order degradation rate constant in the water"),
    SC.TAU_H_SLOT,
)}


def _immersion(c: SC.EventConditions) -> bool:
    return c.system_inputs.get("medium_contact") == "WATER_IMMERSION"


def slots(c: SC.EventConditions) -> dict[str, SC.Slot]:
    out = {k: SLOTS[k] for k in ("k_ref", "Ea", "T_ref")}
    if _immersion(c):
        out.update({k: SLOTS[k] for k in ("k_L", "K_p")})
    if c.system_inputs.get("k_dw_mode") == "ON":
        out["k_dw"] = SLOTS["k_dw"]
    out.update(SC.lag_slots(c))
    return out


def check_conditions(c: SC.EventConditions) -> list[str]:
    out: list[str] = []
    si = c.system_inputs
    unknown = set(si) - {"medium_contact", "water_ratio_m3_per_kg", "k_dw_mode"}
    out += [f"INPUT_UNEXPECTED_{k.upper()}" for k in sorted(unknown)]
    contact = si.get("medium_contact")
    if contact is None:
        out.append("INPUT_MISSING_MEDIUM_CONTACT")
    elif contact not in MEDIUM_CONTACT:
        out.append("INPUT_INVALID_MEDIUM_CONTACT")
    mode = si.get("k_dw_mode")
    if mode is None:
        out.append("INPUT_MISSING_K_DW_MODE")
    elif mode not in K_DW_MODES:
        out.append("INPUT_INVALID_K_DW_MODE")
    elif mode == "ON" and contact == "NO_WATER_CONTACT":
        out.append("K_DW_WITHOUT_WATER_CONTACT")
    r = si.get("water_ratio_m3_per_kg")
    if contact == "WATER_IMMERSION":
        if r is None:
            out.append("INPUT_MISSING_WATER_RATIO_M3_PER_KG")
        elif isinstance(r, bool) or not isinstance(r, (int, float)) or not math.isfinite(r) or not r > 0:
            out.append("INPUT_INVALID_WATER_RATIO_M3_PER_KG")
    return out


def param_checks(c: SC.EventConditions, by: Mapping[str, SC.ParamValue]) -> list[str]:
    return []


def _kd(th: Mapping[str, float], T: float) -> float:
    return float(M.arrhenius_rate(th["k_ref"], th["Ea"], np.array([T]), th["T_ref"])[0])


def _exchange(th: Mapping[str, float], c: SC.EventConditions) -> tuple[float, float, float]:
    if not _immersion(c):
        return 0, 0, 0
    kl = th["k_L"]
    back = kl * th["K_p"] / float(c.system_inputs["water_ratio_m3_per_kg"])
    kdw = th["k_dw"] if c.system_inputs.get("k_dw_mode") == "ON" else 0
    return kl, back, kdw


def rate_matrix(th: Mapping[str, float], c: SC.EventConditions, T: float) -> np.ndarray:
    kd = _kd(th, T)
    kl, back, kdw = _exchange(th, c)
    return np.array([[-(kd + kl), back, 0], [kl, -(back + kdw), 0], [kd, kdw, 0]], dtype=float)


def d_rate_matrix_dT(th: Mapping[str, float], c: SC.EventConditions, T: float) -> np.ndarray:
    dkd = _kd(th, T) * th["Ea"] / (R * T * T)
    return np.array([[-dkd, 0, 0], [0, 0, 0], [dkd, 0, 0]], dtype=float)


def outputs(states: Mapping[str, np.ndarray]) -> dict[str, tuple[float | None, ...]]:
    return {"retention_tissue": tuple(float(v) for v in states["A_t"]),
            "fraction_water": tuple(float(v) for v in states["A_w"]),
            "fraction_degraded": tuple(float(v) for v in states["D"]),
            "ln_retention_tissue": SC.ln_or_none(states["A_t"])}


SPEC = SC.SystemSpec(
    system_id=SYSTEM_ID, model_structure_id=MODEL_STRUCTURE_ID, card_ref=CARD_REF,
    state_names=("A_t", "A_w", "D"), initial_state=(1, 0, 0), conservation=((1, 1, 1),),
    kinetic_forms=("ARRHENIUS_REF_T",), all_slots=SLOTS,
    rate_terms={"k_d": (("k_ref", 1),), "k_L": (("k_L", 1),), "back_exchange": (("k_L", 1), ("K_p", 1), ("r", -1)),
                "k_dw": (("k_dw", 1),), "lag": (("tau_h", -1),)},
    term_inputs={"r": "LENGTH^3*MASS^-1", "T_p": "TEMPERATURE", "R": "ENERGY*AMOUNT^-1*TEMPERATURE^-1"},
    dimensionless_groups=((("Ea", 1), ("R", -1), ("T_p", -1)), (("Ea", 1), ("R", -1), ("T_ref", -1)),
                          (("K_p", 1), ("r", -1))),
    slots=slots, check_conditions=check_conditions, param_checks=param_checks, rate_matrix=rate_matrix,
    d_rate_matrix_dT=d_rate_matrix_dT, outputs=outputs, module_path=Path(__file__))
