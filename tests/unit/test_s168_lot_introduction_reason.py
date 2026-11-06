"""S168 (ksh engine diagnosis, D-071): a lot-introduction event is not a "no consumed entity" gap.

The adapter adds one synthetic INTRO/<entity> (INTRODUCE_LOT) event per ingredient lot; it produces a version-0 lot and
by design consumes nothing. Counting it as NO_CONSUMED_ENTITY made 83 % of that reason (and 42 % of all census events)
look like an extraction gap. It now carries LOT_INTRODUCTION; real actions without a consumed input keep
NO_CONSUMED_ENTITY. Synthetic only.
"""
import importlib.util
from pathlib import Path

from culinarystate.simulation import recipe_adapter as ra

_spec = importlib.util.spec_from_file_location("_t26g", Path(__file__).with_name("test_step26g_recipe_adapter.py"))
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)


def test_intro_events_carry_lot_introduction_not_no_consumed_entity():
    s = ra.build_simulation_inputs(T.replay_ok(), recipe_id=T.REC, system_id=T.AA)
    intro = T.by_event(s)["INTRO/N1"]
    assert "LOT_INTRODUCTION" in intro.reasons and "NO_CONSUMED_ENTITY" not in intro.reasons
    assert intro.route == "SIM_PROHIBITED"


def test_reason_is_registered_and_versions_bumped():
    assert "LOT_INTRODUCTION" in ra.EVENT_REASONS and "LOT_INTRODUCTION" in ra.REASON_CODES
    assert ra.CENSUS_VERSION == "step26g-census-0.2.0-draft"
    assert ra.CONTRACT_VERSION == "step26g-sim-input-0.2.0-draft"
