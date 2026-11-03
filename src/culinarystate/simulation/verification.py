"""Step 26c verification harness for sim_aa_1 / sim_chl_1 (S159, DRAFT_PENDING_26_0_H4).

Small, pure helpers used by tests/unit/test_step26c_*.py. The card's 26c list: analytic vs numeric, convergence,
mass balance, units, non-negativity, semigroup, synthetic truth recovery, negative-design test. The harness holds
no parameter value and no tolerance: callers (the tests) generate synthetic truths and choose test settings. The
G26-VER numbers in the card are PROPOSED_PILOT; nothing here evaluates or passes that gate.

- ``first_order_reference``: exp of the 26a closed form (models.ln_retention_first_order_piecewise).
- ``observed_orders``: log(e_i / e_{i+1}) / log(refinement) for successive refinements.
- ``mass_balance_residual``, ``transition``, ``semigroup_residual``: invariants on runs and propagators.
- ``rate_term_dimensions``: every rate term TIME^-1 and every declared group dimensionless (26a units checker).
- ``simulator_kinetic_form``: wraps a system as a 26a ``KineticForm`` (isothermal observations; response = ln of
  the selected state as a fraction of its initial amount) so the 26a fitting / identifiability library can be run
  on simulator-generated synthetic data. Fits of it are SYNTHETIC and never become PARAM provenance.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from culinarystate.simulation import sim_core as SC
from culinarystate.simulation.kinetics import models as M
from culinarystate.simulation.kinetics import units as U

STATUS = "DRAFT_PENDING_26_0_H4"
RESPONSE_STATES: Mapping[str, tuple[str, ...]] = {"sim_aa_1": ("A_t", "A_w"), "sim_chl_1": ("Chl_a", "Chl_b")}
_ROLE = {"TIME^-1": "RATE_CONSTANT", "ENERGY*AMOUNT^-1": "ACTIVATION_ENERGY", "LENGTH^3*MASS^-1": "PARTITION_COEFFICIENT"}


def first_order_reference(theta: Mapping[str, float], segments: Sequence[tuple[float, float, float]],
                          times: Sequence[float]) -> np.ndarray:
    ln = M.ln_retention_first_order_piecewise(theta["k_ref"], theta["Ea"], theta["T_ref"], segments,
                                              np.asarray(times, dtype=float))
    return np.exp(ln)


def max_relative_error(numeric: Sequence[float], reference: Sequence[float]) -> float:
    a, b = np.asarray(numeric, dtype=float), np.asarray(reference, dtype=float)
    if a.shape != b.shape or a.size == 0 or np.any(b == 0) or not np.all(np.isfinite(a)):
        raise ValueError("relative error needs equal, non-empty, finite arrays and a reference without zeros")
    return float(np.max(np.abs(a - b) / np.abs(b)))


def observed_orders(errors: Sequence[float], *, refinement: int) -> tuple[float, ...]:
    e = np.asarray(errors, dtype=float)
    if e.size < 2 or np.any(e <= 0) or refinement < 2:
        raise ValueError("need >= 2 positive errors and an integer refinement >= 2")
    return tuple(float(x) for x in np.log(e[:-1] / e[1:]) / np.log(refinement))


def mass_balance_residual(run: SC.SimulationRun, spec: SC.SystemSpec) -> float:
    if run.states is None:
        raise ValueError("no states: the run was refused or failed")
    X = np.column_stack([np.asarray(run.states[n], dtype=float) for n in spec.state_names])
    C = np.asarray(spec.conservation, dtype=float)
    x0 = np.asarray(spec.initial_state, dtype=float)
    return float(np.max(np.abs(X @ C.T - C @ x0)))


def transition(spec: SC.SystemSpec, theta: Mapping[str, float], conditions: SC.EventConditions, T_K: float,
               dt: float) -> np.ndarray:
    """Propagator exp(M(T) dt) at constant conditions."""
    return SC.expm(spec.rate_matrix(theta, conditions, T_K) * dt)


def semigroup_residual(spec: SC.SystemSpec, theta: Mapping[str, float], conditions: SC.EventConditions, T_K: float,
                       t: float, s: float) -> float:
    whole = transition(spec, theta, conditions, T_K, t + s)
    parts = transition(spec, theta, conditions, T_K, t) @ transition(spec, theta, conditions, T_K, s)
    return float(np.max(np.abs(whole - parts)))


def rate_term_dimensions(spec: SC.SystemSpec) -> dict[str, str]:
    dims = {s: U.dimension(slot.dimension) for s, slot in spec.all_slots.items()}
    dims.update({k: U.dimension(v) for k, v in spec.term_inputs.items()})
    want = U.dimension("TIME^-1")
    out: dict[str, str] = {}

    def product(group: Sequence[tuple[str, int]]) -> U.Dimension | None:
        d = U.ONE
        for sym, power in group:
            if sym not in dims:
                return None
            d = d * dims[sym] ** power
        return d

    for name, group in spec.rate_terms.items():
        d = product(group)
        out[f"term:{name}"] = U.UNKNOWN if d is None else (U.CONSISTENT if d == want else U.INCONSISTENT)
    for i, group in enumerate(spec.dimensionless_groups):
        d = product(group)
        out[f"group:{i}"] = U.UNKNOWN if d is None else (U.CONSISTENT if d.is_dimensionless() else U.INCONSISTENT)
    return out


def simulator_kinetic_form(system_id: str, *, free: Sequence[str], fixed_theta: Mapping[str, float],
                           system_inputs: Mapping[str, Any], name: str) -> M.KineticForm:
    """A 26a KineticForm over one system in bath mode. Covariates tau_s, T_K and response_index (index into
    ``RESPONSE_STATES[system_id]``); fixed ``T_ref_K``. ``free`` are fitted, ``fixed_theta`` are held."""
    from culinarystate.simulation.systems import SYSTEMS

    spec = SYSTEMS[system_id]
    cond = SC.EventConditions("SYNTH-FIT", "SYNTH_FIT", (SC.BathSegment(0, 1, 1),), 1, "BATH_EQUALS_PRODUCT", None,
                              "SYNTH_FIT", dict(system_inputs), {}, ())
    need = set(spec.slots(cond))
    free = tuple(free)
    if "T_ref" in free or "T_ref" in fixed_theta:
        raise ValueError("T_ref is the fixed input T_ref_K of the form, not a parameter")
    if set(free) & set(fixed_theta) or set(free) | set(fixed_theta) | {"T_ref"} != need:
        raise ValueError(f"free and fixed_theta must partition {sorted(need - {'T_ref'})}")
    params = []
    for sym in free:
        slot = spec.all_slots[sym]
        params.append(M.ParameterSpec(sym, slot.dimension, "IDENTITY" if slot.constraint == "FINITE" else "LOG",
                                      _ROLE.get(slot.dimension, "OTHER"), slot.description))
    states = RESPONSE_STATES[system_id]
    x0 = np.asarray(spec.initial_state, dtype=float)
    held = {k: float(v) for k, v in fixed_theta.items()}

    def fn(th: Mapping[str, float], cov: Mapping[str, np.ndarray], fx: Mapping[str, float]) -> np.ndarray:
        theta = {**held, **th, "T_ref": float(fx["T_ref_K"])}
        idx = cov["response_index"].astype(int)
        if np.any(idx < 0) or np.any(idx >= len(states)) or np.any(cov["response_index"] != idx):
            raise M.ModelError("response_index must index RESPONSE_STATES")
        cache: dict[tuple[float, float], np.ndarray] = {}
        out = np.empty(idx.size)
        for i, (tau, T) in enumerate(zip(cov["tau_s"], cov["T_K"])):
            key = (float(tau), float(T))
            if key not in cache:
                cache[key] = SC.expm(spec.rate_matrix(theta, cond, key[1]) * key[0]) @ x0
            v = cache[key][spec.state_names.index(states[idx[i]])]
            out[i] = np.log(v) if v > 0 else -np.inf
        return out

    return M.KineticForm(name, "OTHER", "ONE_STEP_GLOBAL", "LN_RETENTION", tuple(params),
                         ("tau_s", "T_K", "response_index"), ("T_ref_K",),
                         f"ln x_state(tau) of {system_id}, x' = M(T) x, isothermal", spec.card_ref, (), fn)
