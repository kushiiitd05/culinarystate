"""S179 SCI re-review #4 (R2 residual): a prior state stated AFTER the food, and two-word "left over"."""
from __future__ import annotations

import pytest

from culinarystate.mechanism import evidence_gates as EG
from tests.unit.test_s178_fixrouter_gates import FRY, POTATO, _items, _one


@pytest.mark.parametrize("text,kind", [
    ("Fry the potatoes that you boiled yesterday.", "HEAT"),
    ("Fry the potatoes (already boiled).", "HEAT"),
    ("Fry the potatoes, previously boiled, in the oil.", "HEAT"),
    ("Fry the potatoes left over from dinner.", "PROCESSED"),
    ("Fry the left over potatoes.", "PROCESSED"),
])
def test_r2r_prior_state_after_the_food_withholds_direct(text, kind):
    it = _one(_items(text), FRY, POTATO)
    assert it["route_ungated"] == "DIRECT" and it["route"] != "DIRECT", it["reasons"]
    assert kind in it["prior_process"] and EG.PB_TEXT in it["prior_basis"]


@pytest.mark.parametrize("text", ["Fry the potatoes until golden.", "Fry the potatoes in the oil, then drain.",
                                  "Fry the potatoes that are not cooked."])
def test_r2r_controls_keep_direct(text):
    it = _one(_items(text), FRY, POTATO)
    assert it["route"] == "DIRECT" and it["prior_process"] == []
