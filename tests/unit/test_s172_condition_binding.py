"""S172 / D-077 Layer 1 (TEXT_STATED): recipe text -> per-event simulator inputs, traced; nothing defaulted."""
from __future__ import annotations

from fractions import Fraction

import pytest

from culinarystate.simulation import condition_binding as CB
from culinarystate.simulation import recipe_adapter as RA
from culinarystate.state_graph.source_class import SourceClass


@pytest.fixture(scope="module")
def binder():
    return CB.Binder.load()


def _ev(res, action):
    return next(e for e in res["events"] if e["action"].lower() == action.lower())


def test_fahrenheit_is_converted_exactly_and_duration_bound(binder):
    ev = _ev(binder.bind_text("Bake at 400F for 25 mins."), "bake")
    assert ev["inputs"]["duration"]["value"] == Fraction(25) and ev["inputs"]["duration"]["status"] == "MEASURED"
    tp = ev["inputs"]["temperature_profile"]
    assert tp["value"] == Fraction(1840, 9) and tp["basis"] == "TEXT_STATED" and tp["span"]
    assert ev["inputs"]["medium"]["value"] == "OVEN_AIR"


def test_preheat_setpoint_is_carried_to_a_later_bake(binder):
    ev = _ev(binder.bind_text("Preheat the oven to 180C. Put the tray in. Bake for 30 minutes."), "bake")
    tp = ev["inputs"]["temperature_profile"]
    assert tp["value"] == Fraction(180) and tp["basis"] == "CARRIED_SETPOINT"


def test_boil_is_100c_by_physical_definition(binder):
    ev = _ev(binder.bind_text("Boil the potatoes for 20 minutes."), "boil")
    tp = ev["inputs"]["temperature_profile"]
    assert tp["value"] == Fraction(100) and tp["basis"] == "PHYSICAL_DEFINITION"
    assert ev["inputs"]["medium"]["value"] == "WATER"


def test_duration_range_kept_and_simmer_temperature_unknown(binder):
    ev = _ev(binder.bind_text("Simmer the sauce for 15-20 minutes."), "simmer")
    assert ev["inputs"]["duration"]["value"] == (Fraction(15), Fraction(20))
    assert ev["inputs"]["duration"]["status"] == "RANGE"
    assert ev["inputs"]["temperature_profile"]["status"] == "UNKNOWN"


def test_lid_cues(binder):
    assert _ev(binder.bind_text("Cover and simmer the beans for 10 minutes."), "simmer")["inputs"]["lid_state"]["value"] \
        == "COVERED"
    assert _ev(binder.bind_text("Simmer the beans uncovered for 10 minutes."), "simmer")["inputs"]["lid_state"]["value"] \
        == "UNCOVERED"
    assert _ev(binder.bind_text("Simmer the beans for 10 minutes."), "simmer")["inputs"]["lid_state"]["status"] \
        == "UNKNOWN"


def test_gas_mark_is_a_code_not_a_number_in_layer_1(binder):
    ev = _ev(binder.bind_text("Preheat the oven to gas mark 4. Bake the cake for 20 minutes."), "bake")
    assert ev["inputs"]["temperature_profile"]["status"] == "UNKNOWN"
    assert ev["oven_setpoint_code"] == "GAS_4"


def test_nothing_defaulted(binder):
    ev = _ev(binder.bind_text("Fry the onions."), "fry")
    assert ev["inputs"]["duration"]["status"] == "UNKNOWN"
    assert ev["inputs"]["temperature_profile"]["status"] == "UNKNOWN"
    assert ev["inputs"]["water_ratio"]["status"] == "UNKNOWN"
    assert ev["inputs"]["medium"]["value"] == "PAN_CONTACT_OIL"


def test_contract_bindings_validate_and_are_recipe_side(binder):
    res = binder.bind_text("Boil the potatoes for 20 minutes. Bake at 200C for 25 mins.")
    assert res["bindings"]
    for b in res["bindings"]:
        assert isinstance(b, RA.ConditionBinding) and b.source_class is SourceClass.STRUCTURAL_RECIPE
    names = {b.input_name for b in res["bindings"]}
    assert {"duration", "temperature_profile", "medium"} <= names


def test_only_heat_events_get_heat_inputs(binder):
    res = binder.bind_text("Chop the onions. Boil the potatoes for 20 minutes.")
    chop = _ev(res, "chop")
    assert chop["inputs"] == {} and chop["heat"] is False
