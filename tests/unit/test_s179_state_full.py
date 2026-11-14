"""State v2: per (food, step) state from existing producers; history variables; honest UNKNOWNs."""
import pytest

from culinarystate.composition.state_full import StateBuilder

TXT = ("Chop the tomatoes.\nFry the onion in oil for 5 minutes.\nAdd the tomatoes and salt to the onion.\n"
       "Boil the mixture for 20 minutes.\nStir in the vinegar and boil the sauce for 5 minutes.")


@pytest.fixture(scope="module")
def tomato():
    return {s["step"]: s for s in StateBuilder().build(TXT) if s["food"] == "tomato"}


def test_boil_step_physics_from_l1_l2(tomato):
    q = tomato[5]["Q"]
    assert q["medium"]["v"] == "WATER" and float(q["temperature_C"]["v"]) == 100.0 and float(q["duration_min"]["v"]) == 20
    assert q["piece_size_class"]["v"] == "CHOPPED" and q["thermal_dose_typical_min"]["b"] == "SCENARIO_DEFAULT"


def test_history_variables_accumulate(tomato):
    assert tomato[1]["G"]["cell_integrity"]["v"] == "CUT"
    assert tomato[5]["G"]["heat_steps_so_far"]["v"] == 1 and tomato[4]["G"]["heat_steps_so_far"]["v"] == 0
    assert tomato[6]["Q"]["hot_aqueous_minutes"]["v"] == 20.0
    assert tomato[6]["Q"]["cumulative_thermal_dose_min"]["v"] == tomato[5]["Q"]["cumulative_thermal_dose_min"]["v"]


def test_evidence_found_but_not_applied_on_merged_boil(tomato):
    y = tomato[5]["Y"]
    assert y["vitc_route"]["v"] == "UNKNOWN" and y["vitc_evidence"] == {"v": ["EVD-002765"], "b": "FOUND_NOT_APPLIED"}


def test_formula_out_of_domain_stays_unknown(tomato):
    assert tomato[5]["Y"]["vitc_formula_retention_typical"] == {"v": None, "u": "MATRIX_NOT_ACIDIC_FRUIT"}


def test_acid_joins_at_stir(tomato):
    assert tomato[6]["C"]["acid_present"]["v"] is True and tomato[5]["C"]["acid_present"]["v"] != True
