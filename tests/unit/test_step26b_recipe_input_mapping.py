"""Step 26b <- 26g input mapping (S159, DRAFT_PENDING_26_0_H4).

Every 26g required input (recipe_adapter.SYSTEM_REQUIREMENTS, PROPOSED_PENDING_26b) is mapped explicitly to a
26b input with a disposition; mismatches are documented in systems.MISMATCHES_26G instead of editing 26g.
Synthetic replayed graphs and bindings only (same shape as tests/unit/test_step26g_recipe_adapter.py).
"""
from __future__ import annotations

from fractions import Fraction

import pytest

from culinarystate.simulation import recipe_adapter as ra, sim_core as SC, systems as S
from culinarystate.simulation.recipe_adapter import (
    ApplicabilityBinding, ConditionBinding, ProfileSegment, build_simulation_inputs)
from culinarystate.state_graph.event_log import EngineEvent
from culinarystate.state_graph.replay import replay_events
from culinarystate.state_graph.source_class import SourceClass
from tests.fixtures import step26b_fixtures as F

Fr = Fraction
REC = "SYN-26B"
CONTACT = {"WATER": "WATER_IMMERSION", "STEAM": "NO_WATER_CONTACT"}


def replay():
    intro = EngineEvent("INTRO/N1", (-1, 0), kind="INTRODUCE_LOT", produces=("N1",),
                        produced_types=(("N1", "INGREDIENT_LOT"),))
    e1 = EngineEvent("E1", (0, 0), consumes=("N1",), produces=("N2",), produced_types=(("N2", "INTERMEDIATE"),))
    return replay_events([intro, e1])


def bnd(name: str, value, unit=None, ref="COND-000001", kind="COND") -> ConditionBinding:
    return ConditionBinding("E1", name, value, kind, ref, SourceClass.SYNTHETIC, unit)


def seg(a, b, lo, hi=None) -> ProfileSegment:
    return ProfileSegment(Fr(a), Fr(b), Fr(lo), Fr(hi if hi is not None else lo))


def aa_bindings(*, profile=None, duration=Fr(30), medium="WATER") -> list[ConditionBinding]:
    return [bnd("temperature_profile", profile or (seg(0, 15, 85), seg(15, 30, 95)), "min|degC"),
            bnd("duration", duration, "min"), bnd("medium", medium), bnd("water_ratio", Fr(4), "mL/g"),
            bnd("start_mode", "COLD_START"), bnd("lid_state", "OPEN"), bnd("piece_size_class", F.SIZE),
            bnd("matrix_class", F.MATRIX_CLASS)]


def chl_bindings(*, ph=Fr(6)) -> list[ConditionBinding]:
    return [bnd("temperature_profile", (seg(0, 30, 92),), "min|degC"), bnd("duration", Fr(30), "min"),
            bnd("medium", "WATER"), bnd("medium_ph", ph, "pH"), bnd("piece_size_class", F.SIZE),
            bnd("matrix_class", F.MATRIX_CLASS)]


def record(system: str, bindings, appdec_id: str):
    s = build_simulation_inputs(replay(), recipe_id=REC, system_id=system, bindings=bindings,
                                applicability=[ApplicabilityBinding("E1", system, "APPLICABLE", appdec_id)])
    return next(r for r in s.records if r.event_id == "E1")


def aa_kw(**over):
    kw = {"medium_contact_by_code": CONTACT, "product_temperature_mode": "BATH_EQUALS_PRODUCT",
          "initial_product_temperature_K": None, "k_dw_mode": "OFF"}
    kw.update(over)
    return kw


def test_every_26g_required_input_is_mapped_with_a_disposition() -> None:
    assert set(S.RECIPE_INPUT_MAP) == set(ra.SYSTEM_REQUIREMENTS)
    for system, names in ra.SYSTEM_REQUIREMENTS.items():
        assert set(S.RECIPE_INPUT_MAP[system]) == set(names)
        for m in S.RECIPE_INPUT_MAP[system].values():
            assert m.disposition in S.DISPOSITIONS and m.target and m.note
    assert S.RECIPE_INPUT_MAP["sim_aa_1"]["start_mode"].disposition == "RECORDED_ONLY"
    assert S.RECIPE_INPUT_MAP["sim_chl_1"]["medium"].disposition == "RECORDED_ONLY"
    assert len(S.MISMATCHES_26G) >= 5 and all(m.strip() for m in S.MISMATCHES_26G)


def test_aa_conditions_are_converted_exactly_from_a_simulate_record() -> None:
    rec = record("sim_aa_1", aa_bindings(), "APPDEC-SYN-1")
    assert rec.route == "SIMULATE"
    cond, reasons = S.conditions_from_26g(rec, **aa_kw())
    assert reasons == ()
    assert cond.event_id == "E1" and cond.matrix_class == F.MATRIX_CLASS and cond.piece_size_class == F.SIZE
    assert cond.duration_s == 1800.0
    assert [(b.t_start_s, b.t_end_s, b.T_K) for b in cond.bath_schedule] == [
        (0.0, 900.0, float(Fr(85) + Fr(27315, 100))), (900.0, 1800.0, float(Fr(95) + Fr(27315, 100)))]
    assert cond.system_inputs == {"medium_contact": "WATER_IMMERSION", "water_ratio_m3_per_kg": float(Fr(4, 1000)),
                                  "k_dw_mode": "OFF"}
    assert cond.carried_codes == {"medium": "WATER", "start_mode": "COLD_START", "lid_state": "OPEN"}
    assert "COND-000001" in cond.input_refs


def test_prohibited_or_ranged_records_never_become_conditions() -> None:
    rec = record("sim_aa_1", aa_bindings()[:-1], "APPDEC-SYN-1")          # matrix_class missing in 26g
    cond, reasons = S.conditions_from_26g(rec, **aa_kw())
    assert cond is None and "RECIPE_ADAPTER_SIM_PROHIBITED" in reasons and "MISSING_MATRIX_CLASS" in reasons
    rec = record("sim_aa_1", aa_bindings(profile=(seg(0, 30, 85, 95),)), "APPDEC-SYN-1")
    cond, reasons = S.conditions_from_26g(rec, **aa_kw())
    assert cond is None and "INPUT_RANGE_NOT_SIMULATED_TEMPERATURE_PROFILE" in reasons
    rec = record("sim_aa_1", aa_bindings(duration=(Fr(25), Fr(30))), "APPDEC-SYN-1")
    cond, reasons = S.conditions_from_26g(rec, **aa_kw())
    assert cond is None and "INPUT_RANGE_NOT_SIMULATED_DURATION" in reasons


def test_medium_code_needs_an_explicit_caller_map() -> None:
    rec = record("sim_aa_1", aa_bindings(medium="BROTH"), "APPDEC-SYN-1")
    cond, reasons = S.conditions_from_26g(rec, **aa_kw())
    assert cond is None and "MEDIUM_CONTACT_UNMAPPED" in reasons
    cond, _ = S.conditions_from_26g(record("sim_aa_1", aa_bindings(medium="STEAM"), "APPDEC-SYN-1"), **aa_kw())
    assert cond.system_inputs["medium_contact"] == "NO_WATER_CONTACT"
    with pytest.raises(SC.SimulationError):
        S.conditions_from_26g(rec, **aa_kw(medium_contact_by_code={"WATER": "SPLASH"}))


def test_chl_conditions_carry_the_ph() -> None:
    rec = record("sim_chl_1", chl_bindings(), "APPDEC-SYN-2")
    cond, reasons = S.conditions_from_26g(rec, medium_contact_by_code=None,
                                          product_temperature_mode="BATH_EQUALS_PRODUCT",
                                          initial_product_temperature_K=None, k_dw_mode=None)
    assert reasons == () and cond.system_inputs == {"medium_ph": 6.0}
    rec = record("sim_chl_1", chl_bindings(ph=(Fr(5), Fr(6))), "APPDEC-SYN-2")
    cond, reasons = S.conditions_from_26g(rec, medium_contact_by_code=None,
                                          product_temperature_mode="BATH_EQUALS_PRODUCT",
                                          initial_product_temperature_K=None, k_dw_mode=None)
    assert cond is None and "INPUT_RANGE_NOT_SIMULATED_MEDIUM_PH" in reasons


def test_simulate_from_26g_needs_the_appdec_the_record_names() -> None:
    dec = F.appdec()
    rec = record("sim_aa_1", aa_bindings(), dec["appdec_id"])
    kw = {"appdec": dec, "solver": F.solver(times=(0.0, 900.0, 1800.0)), "ms_limits": F.limits(),
          "form_id": F.FORM_ID, **aa_kw()}
    out = S.simulate_from_26g(rec, F.aa_params(), **kw)
    assert out.status == "COMPLETED", out.reasons
    assert out.provenance["recipe_event_id"] == f"{REC}#E1" and out.provenance["simulation_input_sha256"] == rec.sha256
    other = record("sim_aa_1", aa_bindings(), "APPDEC-DRAFT-0000000000000000")
    out = S.simulate_from_26g(other, F.aa_params(), **kw)
    assert out.status == "SIM_PROHIBITED" and "APPDEC_NOT_REFERENCED_BY_26G_RECORD" in out.reasons
    bad = record("sim_aa_1", aa_bindings()[:-1], dec["appdec_id"])
    out = S.simulate_from_26g(bad, F.aa_params(), **kw)
    assert out.status == "SIM_PROHIBITED" and "RECIPE_ADAPTER_SIM_PROHIBITED" in out.reasons
