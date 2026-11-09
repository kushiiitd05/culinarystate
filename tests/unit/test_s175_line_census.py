"""S175: counts-only line-mass census over recipe records (food finder injected)."""
from __future__ import annotations

from types import MappingProxyType

from culinarystate.composition import line_census as LC
from culinarystate.composition.sr_legacy import Portion, SRFood

GARLIC = SRFood(9, "Garlic, raw", 11, MappingProxyType({}), (Portion("clove", 3.0, 1.0, 9999, "undetermined"),))
FOODS = {9: GARLIC}


def find_food(line: str) -> str | None:
    return "garlic" if "garlic" in line else ("flour" if "flour" in line else None)


def resolve(name: str):
    return LC.Resolved(9, "REGISTRY_MAPPED") if name == "garlic" else LC.Resolved(None, "NO_MATCH")


RECS = [
    {"recipe_id": "R1", "source_family": "A1_BBC_GOOD_FOOD", "ingredient_lines": ["3 garlic cloves", "200g flour"]},
    {"recipe_id": "R2", "source_family": "A1_BBC_GOOD_FOOD", "ingredient_lines": ["2 tbsp flour", "a pinch of salt"]},
    {"recipe_id": "R3", "source_family": "FOODCOM", "ingredient_lines": ["garlic"]},
]


def test_census_counts_by_basis_and_q_level() -> None:
    out = LC.census(RECS, find_food=find_food, resolve=resolve, foods=FOODS)
    bbc = out["families"]["A1_BBC_GOOD_FOOD"]
    assert bbc["recipes"] == 2 and bbc["lines"] == 4
    assert bbc["basis"] == {"COUNT_x_SR_PORTION": 1, "TEXT_STATED_MASS": 1, "UNKNOWN": 1, "QUALITATIVE": 1}
    assert bbc["q_level"] == {"Q1": 1, "Q0": 1, "Q6": 2}
    assert bbc["reason"] == {"NO_SR_FOOD": 1}
    assert bbc["match_status"] == {"REGISTRY_MAPPED": 1, "NO_MATCH": 2, "NO_FOOD_MENTION": 1}
    assert bbc["lines_with_grams"] == 2 and bbc["lines_with_grams_link_unverified"] == 1
    assert bbc["recipes_all_quantified_lines_with_grams"] == 1     # R1 yes; R2 has an unknown line
    fc = out["families"]["FOODCOM"]
    assert fc["basis"] == {"UNIT_MISSING_IN_SOURCE": 1}


def test_census_output_is_counts_only_and_deterministic() -> None:
    a = LC.census(RECS, find_food=find_food, resolve=resolve, foods=FOODS)
    b = LC.census(list(reversed(RECS)), find_food=find_food, resolve=resolve, foods=FOODS)
    assert a == b
    LC.assert_counts_only(a)
    assert a["labels"] == ["COUNTS_ONLY", "MODEL_DERIVED_GRAMS", "SR_LINK_UNVERIFIED"]


def test_locale_per_family() -> None:
    assert LC.LOCALE["A1_BBC_GOOD_FOOD"] == "UK" and LC.LOCALE["FOODCOM"] == "US"
    assert LC.UNITS_MISSING == frozenset({"FOODCOM"})
