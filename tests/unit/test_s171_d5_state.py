"""S171 / M5: D5 S-block gold helpers on a Rung A graph (heated-so-far set; next action after the cut). Synthetic."""
from __future__ import annotations

from culinarystate.evaluation import d5_state as DS

FAM = {"PROC-000019": "WET_HEAT"}  # boil


def test_heated_ingredients_follow_lots_through_heat_events():
    g = DS.graph("Peel the potatoes. Boil the potatoes for 20 minutes. Chop the parsley.")
    heated = DS.heated_ingredient_ids(g, FAM)
    linked = DS.linked_ingredient_ids(g)
    assert heated and heated <= linked and len(linked) >= 2  # parsley is linked but not heated


def test_no_heat_event_gives_empty_set():
    assert DS.heated_ingredient_ids(DS.graph("Chop the parsley. Peel the potatoes."), FAM) == set()


def test_next_action_is_first_event_after_the_cut():
    steps = ["Peel the potatoes.", "Boil the potatoes for 20 minutes.", "Drain and mash them."]
    na = DS.next_action(steps, cut=2)
    assert na["action"].lower() == "drain" and na["step_index"] == 2
    assert DS.next_action(steps, cut=3) is None


def test_seeded_cut_is_inside_and_deterministic():
    c1 = DS.seeded_cut("R1", 6, seed="s")
    assert c1 == DS.seeded_cut("R1", 6, seed="s") and 2 <= c1 <= 5
