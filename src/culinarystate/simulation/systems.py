"""Step 26b one interface over sim_aa_1 and sim_chl_1, and the 26g -> 26b input mapping (S159, DRAFT_PENDING_26_0_H4).

``simulate(system_id, conditions, params, appdec=, solver=, ms_limits=, form_id=)`` is the single entry point (card:
"sim_aa_1, sim_chl_1 behind one interface so a switch costs only calibration"). Which system is used is NOT chosen
here: that is the 26.0 selection record, a Kush + Parv decision transcribing the single 11.D entry (R-14).

26g mapping: ``RECIPE_INPUT_MAP`` maps every input in ``recipe_adapter.SYSTEM_REQUIREMENTS`` (PROPOSED_PENDING_26b)
to a 26b input with a disposition; ``conditions_from_26g`` converts a SIMULATE ``SimulationInputRecord`` exactly
(min -> s by the KIN factor, degC -> K by the exact 273.15 offset, mL/g -> m^3/kg by the unit factor) and refuses
everything else. Mismatches between the 26g contract and what 26b needs are listed in ``MISMATCHES_26G``; 26g is
not edited (its SIMULATOR_STATUS / docstrings still say 26b is not built: OPEN for the humans).
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from culinarystate.simulation import recipe_adapter as RA, sim_aa_1, sim_chl_1, sim_core as SC
from culinarystate.simulation.kinetics import units as U

STATUS = "DRAFT_PENDING_26_0_H4"
SYSTEMS: Mapping[str, SC.SystemSpec] = {sim_aa_1.SYSTEM_ID: sim_aa_1.SPEC, sim_chl_1.SYSTEM_ID: sim_chl_1.SPEC}
SOLVER_METHODS = SC.SOLVER_METHODS
DISPOSITIONS = ("USED", "USED_VIA_CALLER_MAP", "USED_IF_LAG", "RECORDED_ONLY")

OPEN_FOR_HUMANS: tuple[str, ...] = (
    "26.0 system selection (AA leading vs CHL fallback, D-027) is a Kush + Parv record; nothing here chooses",
    "sim_aa_1 K_p dimension: r kept in the 26g unit (mL/g, SI m^3/kg) so K_p is LENGTH^3*MASS^-1; the card's "
    "'K_p default 1' assumes a dimensionless r and is not used (no default)",
    "sim_aa_1 k_L not temperature dependent and k_dw first order, as in the card equations (H4 / expert)",
    "sim_chl_1 g(pH) functional form is not given by the card: g is a caller PARAM value for the event pH with its "
    "pH validity interval; one g shared by Chl a and b (Step 24b FORM, expert)",
    "tau_h per piece-size class is a caller PARAM (or a Choi-Okos MODEL_DERIVED value); the lag stays flagged "
    "T_P_LAG_EXTRAPOLATED until validated (E26-6); initial product temperature is not a 26g input",
    "Choi-Okos 1986 coefficients, mixing rules and validity ranges are caller-supplied PARAM inputs (none entered; "
    "mixing rules as recalled by the AI need checking against the paper)",
    "M&S limits (T ceiling, water/steam only, size classes) are caller inputs until the 26e model card states them",
    "KiSAO ids of the solver methods are AI-recalled and UNVERIFIED (hosts not checked)",
    "solver tolerances, the fixed-step stiffness limit and invariant tolerances are caller settings; the G26-VER "
    "numbers are PROPOSED_PILOT and only the signed 26.0 pre-registration can fix them",
    "medium code -> contact (WATER_IMMERSION / NO_WATER_CONTACT) has no vocabulary in 26g; the caller supplies the map",
    "RANGE inputs (interval temperature profile, duration, pH) are refused by the deterministic simulator; interval "
    "propagation belongs to the 26d / 26e UQ layer",
)

MISMATCHES_26G: tuple[str, ...] = (
    "temperature_profile: 26g allows RANGE segments; 26b simulates MEASURED (point) segments only",
    "duration: 26g does not cross-check duration against the profile end (NOT_CHECKED); 26b refuses "
    "DURATION_BEYOND_SCHEDULE",
    "medium: 26g holds an open upper-case code; 26b needs medium_contact, supplied through a caller map",
    "water_ratio: 26g unit mL/g is kept (exact SI m^3/kg), which fixes the K_p dimension (not the card's "
    "dimensionless K_p)",
    "start_mode and lid_state: required by 26g, recorded only by 26b (the bath schedule carries the start; "
    "no equation term uses them)",
    "26b needs inputs 26g does not hold: product_temperature_mode, initial product temperature (lag), k_dw_mode, "
    "the parameter set, M&S limits, FORM id and the APPDEC record itself (26g keeps only its id)",
    "sim_chl_1 medium: required by 26g, recorded only (the card has no leaching term)",
)


@dataclass(frozen=True)
class InputMapping:
    disposition: str
    target: str
    note: str


_PROFILE = InputMapping("USED", "bath_schedule", "min|degC exact -> s|K exact; MEASURED segments only")
_DURATION = InputMapping("USED", "duration_s", "min -> s exact; must not exceed the profile end")
_SIZE = InputMapping("USED_IF_LAG", "piece_size_class", "selects the tau_h scope in LUMPED_LAG; recorded otherwise")
_MATRIX = InputMapping("USED", "matrix_class", "must equal every PARAM matrix class, else NO_COMPATIBLE_SET")
RECIPE_INPUT_MAP: Mapping[str, Mapping[str, InputMapping]] = {
    "sim_aa_1": {
        "temperature_profile": _PROFILE, "duration": _DURATION,
        "medium": InputMapping("USED_VIA_CALLER_MAP", "system_inputs.medium_contact",
                               "caller map code -> WATER_IMMERSION / NO_WATER_CONTACT; unmapped is refused"),
        "water_ratio": InputMapping("USED", "system_inputs.water_ratio_m3_per_kg", "mL/g -> m^3/kg exact (r)"),
        "start_mode": InputMapping("RECORDED_ONLY", "carried_codes.start_mode", "encoded by the bath schedule"),
        "lid_state": InputMapping("RECORDED_ONLY", "carried_codes.lid_state", "no equation term"),
        "piece_size_class": _SIZE, "matrix_class": _MATRIX},
    "sim_chl_1": {
        "temperature_profile": _PROFILE, "duration": _DURATION,
        "medium": InputMapping("RECORDED_ONLY", "carried_codes.medium", "no leaching term in SIM-CHL-1"),
        "medium_ph": InputMapping("USED", "system_inputs.medium_ph", "point pH; must lie in the g_pH validity"),
        "piece_size_class": _SIZE, "matrix_class": _MATRIX},
}


def _spec(system_id: str) -> SC.SystemSpec:
    spec = SYSTEMS.get(system_id)
    if spec is None:
        raise SC.SimulationError(f"system_id must be one of {tuple(SYSTEMS)}")
    return spec


def simulate(system_id: str, conditions: SC.EventConditions, params: Sequence[SC.ParamValue], *,
             appdec: Mapping[str, Any] | None, solver: SC.SolverConfig, ms_limits: SC.MSLimits,
             form_id: str) -> SC.SimulationRun:
    """The one interface: run ``system_id`` on one event, or refuse with reason codes."""
    return SC.run(_spec(system_id), conditions, params, appdec=appdec, solver=solver, ms_limits=ms_limits,
                  form_id=form_id)


# ----------------------------------------------------------------------------- 26g -> 26b
def _f(x: Fraction) -> float:
    return float(x)


def conditions_from_26g(record: RA.SimulationInputRecord, *, medium_contact_by_code: Mapping[str, str] | None,
                        product_temperature_mode: str, initial_product_temperature_K: float | None,
                        k_dw_mode: str | None) -> tuple[SC.EventConditions | None, tuple[str, ...]]:
    """EventConditions from a 26g record, or (None, reasons). Nothing is defaulted or inferred."""
    if not isinstance(record, RA.SimulationInputRecord):
        raise SC.SimulationError("conditions_from_26g takes a 26g SimulationInputRecord")
    spec = _spec(record.system_id)
    if medium_contact_by_code is not None and not set(medium_contact_by_code.values()) <= set(sim_aa_1.MEDIUM_CONTACT):
        raise SC.SimulationError(f"medium_contact_by_code values must be in {sim_aa_1.MEDIUM_CONTACT}")
    if spec is sim_chl_1.SPEC and (medium_contact_by_code is not None or k_dw_mode is not None):
        raise SC.SimulationError("sim_chl_1 has no water-contact or k_dw switch")
    if record.route != "SIMULATE":
        return None, tuple(sorted({"RECIPE_ADAPTER_SIM_PROHIBITED", *record.reasons}))
    inputs = {i.name: i for i in record.inputs}
    reasons = [f"INPUT_RANGE_NOT_SIMULATED_{i.name.upper()}" for i in record.inputs if i.status == "RANGE"]
    reasons += [f"INPUT_UNKNOWN_{i.name.upper()}" for i in record.inputs if i.status == "UNKNOWN"]
    system_inputs: dict[str, Any] = {}
    carried: dict[str, str] = {}
    if spec is sim_aa_1.SPEC:
        code = inputs["medium"].value
        contact = (medium_contact_by_code or {}).get(code)
        if contact is None:
            reasons.append("MEDIUM_CONTACT_UNMAPPED")
        ratio = inputs["water_ratio"].value
        factor = U.parse_unit(RA.INPUT_SPECS["water_ratio"].unit).factor_to_si
        system_inputs = {"medium_contact": contact, "k_dw_mode": k_dw_mode,
                         "water_ratio_m3_per_kg": _f(ratio * factor) if isinstance(ratio, Fraction) else None}
        carried = {"medium": code, "start_mode": inputs["start_mode"].value, "lid_state": inputs["lid_state"].value}
    else:
        ph = inputs["medium_ph"].value
        system_inputs = {"medium_ph": _f(ph) if isinstance(ph, Fraction) else None}
        carried = {"medium": inputs["medium"].value}
    if reasons:
        return None, tuple(sorted(set(reasons)))
    sched = tuple(SC.BathSegment(_f(s.start * SC.SECONDS_PER_MINUTE), _f(s.end * SC.SECONDS_PER_MINUTE),
                                 _f(s.low + SC.CELSIUS_OFFSET_K)) for s in inputs["temperature_profile"].value)
    refs = tuple(sorted({ref for i in record.inputs for _, ref in i.provenance}))
    cond = SC.EventConditions(
        event_id=record.event_id, matrix_class=inputs["matrix_class"].value, bath_schedule=sched,
        duration_s=_f(inputs["duration"].value * SC.SECONDS_PER_MINUTE),
        product_temperature_mode=product_temperature_mode,
        initial_product_temperature_K=initial_product_temperature_K,
        piece_size_class=inputs["piece_size_class"].value, system_inputs=system_inputs, carried_codes=carried,
        input_refs=refs)
    return cond, ()


def simulate_from_26g(record: RA.SimulationInputRecord, params: Sequence[SC.ParamValue], *,
                      appdec: Mapping[str, Any] | None, solver: SC.SolverConfig, ms_limits: SC.MSLimits,
                      form_id: str, medium_contact_by_code: Mapping[str, str] | None, product_temperature_mode: str,
                      initial_product_temperature_K: float | None, k_dw_mode: str | None) -> SC.SimulationRun:
    """Run from a 26g record; the APPDEC passed must be one the record references (applicability_refs)."""
    spec = _spec(record.system_id)
    cond, reasons = conditions_from_26g(record, medium_contact_by_code=medium_contact_by_code,
                                        product_temperature_mode=product_temperature_mode,
                                        initial_product_temperature_K=initial_product_temperature_K,
                                        k_dw_mode=k_dw_mode)
    extra = list(reasons)
    if isinstance(appdec, Mapping) and appdec.get("appdec_id") not in record.applicability_refs:
        extra.append("APPDEC_NOT_REFERENCED_BY_26G_RECORD")
    context = {"recipe_event_id": record.recipe_event_id, "simulation_input_sha256": record.sha256}
    if cond is None or extra:
        return SC.prohibited(spec, extra, solver, form_id=form_id, appdec=appdec, context=context)
    return SC.run(spec, cond, params, appdec=appdec, solver=solver, ms_limits=ms_limits, form_id=form_id,
                  context=context)
