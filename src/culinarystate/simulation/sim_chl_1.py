"""sim_chl_1: chlorophyll a / b -> pheophytin a / b, first order with a pH modifier (S159, DRAFT_PENDING_26_0_H4).

Structure only, from the Plan v2 Step 26 card "Fallback system (pre-registered)": "Chl a, Chl b -> pheophytin a/b;
first-order Arrhenius degradation x a pH modifier g(pH) taken from the Step-24 FORM entry (form PROPOSED; pH is a
required input, UNKNOWN => prohibited); T <= 100 degC (pyropheophytin above is out of limits); no leaching term".

States (each pigment as a fraction of its own initial amount): Chl_a, Chl_b, Pheo_a, Pheo_b; initial (1, 1, 0, 0).

    k_x(T, pH) = k_ref_x * exp(-(Ea_x/R)(1/T - 1/T_ref)) * g(pH),   x in {a, b}
    dChl_x/dt = -k_x Chl_x ;  dPheo_x/dt = +k_x Chl_x              (Chl_x + Pheo_x = 1 for each pigment)

The functional form of g(pH) is not given by the card and is NOT invented here: the caller supplies ``g_pH``, the
value of g for the event's pH, as a dimensionless PARAM input carrying the pH validity interval it was evaluated
for; the medium pH must lie inside it (else PH_OUTSIDE_MODIFIER_VALIDITY). One g is shared by both pigments as the
card states one modifier (OPEN). The T ceiling is the caller's ``MSLimits`` (26e). Colour (a*) is not produced.
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from pathlib import Path

import numpy as np

from culinarystate.simulation import sim_core as SC
from culinarystate.simulation.kinetics import models as M

STATUS = "DRAFT_PENDING_26_0_H4"
SYSTEM_ID = "sim_chl_1"
MODEL_STRUCTURE_ID = "SIM-CHL-1-STRUCTURE-0.1.0-draft"
CARD_REF = "Plan v2 Step 26 card, Architecture detail: fallback system (pre-registered) SIM-CHL-1"
R = M.R

SLOTS: Mapping[str, SC.Slot] = {s.symbol: s for s in (
    SC.Slot("k_ref_a", "TIME^-1", "1/s", "POSITIVE", "Chl a -> Pheo a first-order rate constant at T_ref"),
    SC.Slot("Ea_a", "ENERGY*AMOUNT^-1", "J/mol", "FINITE", "activation energy, Chl a"),
    SC.Slot("k_ref_b", "TIME^-1", "1/s", "POSITIVE", "Chl b -> Pheo b first-order rate constant at T_ref"),
    SC.Slot("Ea_b", "ENERGY*AMOUNT^-1", "J/mol", "FINITE", "activation energy, Chl b"),
    SC.Slot("T_ref", "TEMPERATURE", "K", "POSITIVE", "pre-declared reference temperature"),
    SC.Slot("g_pH", "1", "1", "POSITIVE", "pH modifier g evaluated for the event pH (form OPEN, Step 24b FORM)"),
    SC.TAU_H_SLOT,
)}


def slots(c: SC.EventConditions) -> dict[str, SC.Slot]:
    out = {k: SLOTS[k] for k in ("k_ref_a", "Ea_a", "k_ref_b", "Ea_b", "T_ref", "g_pH")}
    out.update(SC.lag_slots(c))
    return out


def _ph(c: SC.EventConditions) -> float | None:
    v = c.system_inputs.get("medium_ph")
    if v is None or isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        return None
    return float(v)


def check_conditions(c: SC.EventConditions) -> list[str]:
    out = [f"INPUT_UNEXPECTED_{k.upper()}" for k in sorted(set(c.system_inputs) - {"medium_ph"})]
    if c.system_inputs.get("medium_ph") is None:
        out.append("INPUT_MISSING_MEDIUM_PH")
    elif _ph(c) is None:
        out.append("INPUT_INVALID_MEDIUM_PH")
    return out


def param_checks(c: SC.EventConditions, by: Mapping[str, SC.ParamValue]) -> list[str]:
    g = by.get("g_pH")
    ph = _ph(c)
    if g is None or ph is None:
        return []
    if g.ph_validity is None:
        return ["PH_MODIFIER_VALIDITY_MISSING"]
    lo, hi = g.ph_validity
    return [] if lo <= ph <= hi else ["PH_OUTSIDE_MODIFIER_VALIDITY"]


def _k(th: Mapping[str, float], pig: str, T: float) -> float:
    base = M.arrhenius_rate(th[f"k_ref_{pig}"], th[f"Ea_{pig}"], np.array([T]), th["T_ref"])[0]
    return float(base) * th["g_pH"]


def rate_matrix(th: Mapping[str, float], c: SC.EventConditions, T: float) -> np.ndarray:
    ka, kb = _k(th, "a", T), _k(th, "b", T)
    return np.array([[-ka, 0, 0, 0], [0, -kb, 0, 0], [ka, 0, 0, 0], [0, kb, 0, 0]], dtype=float)


def d_rate_matrix_dT(th: Mapping[str, float], c: SC.EventConditions, T: float) -> np.ndarray:
    da = _k(th, "a", T) * th["Ea_a"] / (R * T * T)
    db = _k(th, "b", T) * th["Ea_b"] / (R * T * T)
    return np.array([[-da, 0, 0, 0], [0, -db, 0, 0], [da, 0, 0, 0], [0, db, 0, 0]], dtype=float)


def outputs(states: Mapping[str, np.ndarray]) -> dict[str, tuple[float | None, ...]]:
    return {"retention_chl_a": tuple(float(v) for v in states["Chl_a"]),
            "retention_chl_b": tuple(float(v) for v in states["Chl_b"]),
            "fraction_pheo_a": tuple(float(v) for v in states["Pheo_a"]),
            "fraction_pheo_b": tuple(float(v) for v in states["Pheo_b"]),
            "ln_retention_chl_a": SC.ln_or_none(states["Chl_a"]),
            "ln_retention_chl_b": SC.ln_or_none(states["Chl_b"])}


SPEC = SC.SystemSpec(
    system_id=SYSTEM_ID, model_structure_id=MODEL_STRUCTURE_ID, card_ref=CARD_REF,
    state_names=("Chl_a", "Chl_b", "Pheo_a", "Pheo_b"), initial_state=(1, 1, 0, 0),
    conservation=((1, 0, 1, 0), (0, 1, 0, 1)), kinetic_forms=("ARRHENIUS_REF_T",), all_slots=SLOTS,
    rate_terms={"k_a": (("k_ref_a", 1), ("g_pH", 1)), "k_b": (("k_ref_b", 1), ("g_pH", 1)), "lag": (("tau_h", -1),)},
    term_inputs={"T_p": "TEMPERATURE", "R": "ENERGY*AMOUNT^-1*TEMPERATURE^-1"},
    dimensionless_groups=((("Ea_a", 1), ("R", -1), ("T_p", -1)), (("Ea_b", 1), ("R", -1), ("T_p", -1)),
                          (("Ea_a", 1), ("R", -1), ("T_ref", -1)), (("g_pH", 1),)),
    slots=slots, check_conditions=check_conditions, param_checks=param_checks, rate_matrix=rate_matrix,
    d_rate_matrix_dT=d_rate_matrix_dT, outputs=outputs, module_path=Path(__file__))
