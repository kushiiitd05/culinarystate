"""S175: counts-only lot census, one RECIPE_POOL lot per recipe (all ingredient lines as members)."""
from __future__ import annotations

from types import MappingProxyType

from culinarystate.composition import lot_census as LC2
from culinarystate.composition.food_ph import PHRow, PHTable
from culinarystate.composition.line_census import Resolved, assert_counts_only
from culinarystate.composition.sr_legacy import SRFood

FOODS = {1: SRFood(1, "Onions, raw", 11, MappingProxyType({"water_g": 89.0, "sodium_mg": 4.0}), ()),
         2: SRFood(2, "Lemon juice, raw", 9, MappingProxyType({"water_g": 92.0, "sodium_mg": 1.0}), ())}
PH = PHTable([PHRow("Lemon juice", 2.0, 2.6, "INTERVAL", "2.00 - 2.60"), PHRow("Onions, red", 5.3, 5.8, "INTERVAL", "")])


def find_food(line: str) -> str | None:
    return "onion" if "onion" in line else ("lemon juice" if "lemon" in line else None)


def resolve(name: str) -> Resolved:
    return Resolved({"onion": 1, "lemon juice": 2}[name], "REGISTRY_MAPPED")


RECS = [
    {"recipe_id": "R1", "source_family": "A1_BBC_GOOD_FOOD", "ingredient_lines": ["100g onion", "30ml lemon juice"]},
    {"recipe_id": "R2", "source_family": "A1_BBC_GOOD_FOOD", "ingredient_lines": ["100g onion", "a pinch of salt"]},
    {"recipe_id": "R3", "source_family": "A1_BBC_GOOD_FOOD", "ingredient_lines": []},
]


def test_lot_census_counts() -> None:
    out = LC2.census(RECS, find_food=find_food, resolve=resolve, foods=FOODS, ph=PH)
    f = out["families"]["A1_BBC_GOOD_FOOD"]
    assert f["recipes"] == 3 and f["lots"] == 2                      # R3 has no lines: no lot
    assert f["water_g_status"] == {"INTERVAL": 1, "UNKNOWN": 1}       # R2: salt line has no SR food
    assert f["water_g_width"] == {"lt_0.05": 1}
    assert f["ph_flags"] == {"CONTAINS_ACID_MEMBER": 1, "ANY_MEMBER_PH_UNKNOWN": 1}
    assert f["provisional"] == 2
    assert_counts_only(out)
    assert out["lot_kind"] == "RECIPE_POOL"


def test_width_buckets() -> None:
    assert LC2.width_bucket(0.0, 0.01) == "lt_0.05"
    assert LC2.width_bucket(0.1, 0.4) == "lt_0.5"
    assert LC2.width_bucket(0.1, None) == "unbounded"
    assert LC2.width_bucket(0.0, 0.9) == "ge_0.5"
