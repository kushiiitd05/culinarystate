"""SYNTHETIC fixtures for the Step 26b simulator and the 26c verification suite (S159, DRAFT_PENDING_26_0_H4).

Every number here is a synthetic placeholder chosen inside the tests for verification only (SYNTHETIC_NOT_GOLD):
rate constants, activation energies, partition coefficients, time constants, pH modifiers, M&S ceilings and
tolerances are test settings, never literature or scientific values, and never enter a PARAM row or a ledger.
APPDEC records come from the real S158 23a engine run on its own constructed synthetic case fixtures.
"""
from __future__ import annotations

from typing import Any

from culinarystate.mechanism import applicability as AP
from culinarystate.mechanism import process_signatures as PS
from culinarystate.simulation import sim_core as SC
from tests.fixtures.step22a_23a_fixtures import HIERARCHY_ROWS, MATRIX, mech, rule

H = PS.hierarchy_from_rows(HIERARCHY_ROWS)
AA, CHL = "sim_aa_1", "sim_chl_1"
MATRIX_CLASS = "MATRIX_X"
SIZE = "SIZE_CLASS_A"
FORM_ID = "SYNTH-FORM-000001"
T_REF = 360.0                     # synthetic reference temperature, K
T_BATH = 365.0                    # synthetic bath temperature, K


def appdec(event_id: str = "E1", **over: Any) -> dict[str, Any]:
    """An APPDEC record from the 23a engine; the default constructed case routes SIMULATE."""
    entries = [mech()]
    keys = tuple(e["mechanism_key"] for e in entries)
    sigs = PS.build_signatures([PS.SignatureRule(**rule(mechanism_keys=keys))], entries, H,
                               heat_transfer_mode_ids=frozenset()).signatures
    base: dict[str, Any] = {
        "case_id": "SYNTH-CASE-26B", "entity_version_id": "SYN-ENT@1", "event_id": event_id,
        "target_svar_id": None, "target_state_key": "synthetic_target", "process_id": "PROC-SYN001",
        "matrix": MATRIX, "states": {"synthetic_state": "SYNTH_A"},
        "axes": (AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"),),
        "formula": AP.CaseGate("APPLICABLE", (), "SYNTH-FORM-1"),
        "observability": AP.CaseGate("APPLICABLE", (), "SYNTH-OBS-1"),
        "parameters": AP.CaseGate("APPLICABLE", (), "SYNTH-PARAM-1"),
        "domain_flag": "IN_VALIDATION_DOMAIN", "safety_critical": "NO"}
    base.update(over)
    return AP.evaluate(AP.ApplicabilityQuery(**base), sigs, entries, H)


def p(symbol: str, value: float, unit: str, *, matrix: str = MATRIX_CLASS, size: str | None = None,
      ph: tuple[float, float] | None = None, origin: str = "SYNTHETIC", pid: str | None = None) -> SC.ParamValue:
    if pid is None:
        pid = "SYNTH-PARAM-" + symbol.upper().replace("_", "-")
    return SC.ParamValue(pid, symbol, value, unit, matrix, size, ph, origin)


def aa_params(*, k_ref: float = 2.0e-4, ea: float = 7.0e4, k_l: float | None = 3.0e-4,
              k_p: float | None = 2.0e-3, k_dw: float | None = None, tau_h: float | None = None,
              t_ref: float = T_REF) -> list[SC.ParamValue]:
    out = [p("k_ref", k_ref, "1/s"), p("Ea", ea, "J/mol"), p("T_ref", t_ref, "K")]
    if k_l is not None:
        out.append(p("k_L", k_l, "1/s"))
    if k_p is not None:
        out.append(p("K_p", k_p, "m^3/kg"))
    if k_dw is not None:
        out.append(p("k_dw", k_dw, "1/s"))
    if tau_h is not None:
        out.append(p("tau_h", tau_h, "s", size=SIZE))
    return out


def chl_params(*, ka: float = 3.0e-4, ea_a: float = 6.0e4, kb: float = 1.5e-4, ea_b: float = 5.0e4,
               g: float = 1.5, ph: tuple[float, float] | None = (5.0, 7.0), tau_h: float | None = None,
               t_ref: float = T_REF) -> list[SC.ParamValue]:
    out = [p("k_ref_a", ka, "1/s"), p("Ea_a", ea_a, "J/mol"), p("k_ref_b", kb, "1/s"), p("Ea_b", ea_b, "J/mol"),
           p("T_ref", t_ref, "K"), p("g_pH", g, "1", ph=ph)]
    if tau_h is not None:
        out.append(p("tau_h", tau_h, "s", size=SIZE))
    return out


def schedule(*segs: tuple[float, float, float]) -> tuple[SC.BathSegment, ...]:
    return tuple(SC.BathSegment(a, b, t) for a, b, t in segs)


def aa_conditions(*, contact: str = "WATER_IMMERSION", ratio: float | None = 4.0e-3, kdw: str = "OFF",
                  sched: tuple[SC.BathSegment, ...] | None = None, duration: float = 1800.0,
                  mode: str = "BATH_EQUALS_PRODUCT", tp0: float | None = None, event_id: str = "E1",
                  matrix: str = MATRIX_CLASS) -> SC.EventConditions:
    return SC.EventConditions(
        event_id=event_id, matrix_class=matrix, bath_schedule=sched or schedule((0.0, 1800.0, T_BATH)),
        duration_s=duration, product_temperature_mode=mode, initial_product_temperature_K=tp0,
        piece_size_class=SIZE,
        system_inputs={"medium_contact": contact, "water_ratio_m3_per_kg": ratio, "k_dw_mode": kdw},
        carried_codes={"medium": "WATER", "start_mode": "COLD_START", "lid_state": "OPEN"},
        input_refs=("EVT-000001", "QNT-000001"))


def chl_conditions(*, ph: float | None = 6.0, sched: tuple[SC.BathSegment, ...] | None = None,
                   duration: float = 1800.0, mode: str = "BATH_EQUALS_PRODUCT", tp0: float | None = None,
                   event_id: str = "E1") -> SC.EventConditions:
    return SC.EventConditions(
        event_id=event_id, matrix_class=MATRIX_CLASS, bath_schedule=sched or schedule((0.0, 1800.0, T_BATH)),
        duration_s=duration, product_temperature_mode=mode, initial_product_temperature_K=tp0,
        piece_size_class=SIZE, system_inputs={"medium_ph": ph}, carried_codes={"medium": "WATER"},
        input_refs=("EVT-000001",))


def solver(method: str = "EXPM_PIECEWISE", *, times: tuple[float, ...] = (0.0, 600.0, 1200.0, 1800.0),
           rtol: float | None = None, atol: float | None = None, steps: int | None = None,
           stab: float | None = None, mb_tol: float = 1e-12, nn_tol: float = 1e-12) -> SC.SolverConfig:
    if method.startswith("SCIPY_"):
        rtol = 1e-10 if rtol is None else rtol
        atol = 1e-12 if atol is None else atol
    if method in ("TRAPEZOID_FIXED", "RK4_FIXED") and steps is None:
        steps = 64
    if method in ("TRAPEZOID_FIXED", "RK4_FIXED") and stab is None:
        stab = 2.0
    return SC.SolverConfig(method, times, rtol, atol, steps, stab, mb_tol, nn_tol)


def limits(t_max: float = 380.0) -> SC.MSLimits:
    return SC.MSLimits(t_max, "SYNTH-MS-LIMITS")
