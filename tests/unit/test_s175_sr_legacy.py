"""S175: USDA SR Legacy loader (composition per 100 g, portions) for the lot-state layer. Fixture CSVs only."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from culinarystate.composition import sr_legacy as SR


def _write(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(header)
        w.writerows(rows)


@pytest.fixture()
def sr_dir(tmp_path: Path) -> Path:
    _write(tmp_path / "food.csv", ["fdc_id", "data_type", "description", "food_category_id", "publication_date"], [
        [170000, "sr_legacy_food", "Onions, raw", 11, "2019-04-01"],
        [169655, "sr_legacy_food", "Sugars, granulated", 19, "2019-04-01"],
        [170700, "sr_legacy_food", "McDONALD'S, Hamburger", 21, "2019-04-01"],
    ])
    _write(tmp_path / "food_nutrient.csv",
           ["id", "fdc_id", "nutrient_id", "amount", "data_points", "derivation_id", "min", "max", "median",
            "footnote", "min_year_acquired"], [
        [1, 170000, 1051, "89.11", "", "", "", "", "", "", ""],
        [2, 170000, 1003, "1.1", "", "", "", "", "", "", ""],
        [3, 170000, 1093, "4", "", "", "", "", "", "", ""],
        [4, 170000, 1008, "40", "", "", "", "", "", "", ""],      # energy: not in the roster, dropped
        [5, 169655, 1051, "0.02", "", "", "", "", "", "", ""],
        [6, 169655, 2000, "99.8", "", "", "", "", "", "", ""],
        [7, 170700, 1051, "45", "", "", "", "", "", "", ""],
    ])
    _write(tmp_path / "food_portion.csv",
           ["id", "fdc_id", "seq_num", "amount", "measure_unit_id", "portion_description", "modifier",
            "gram_weight", "data_points", "footnote", "min_year_acquired"], [
        [1, 170000, 1, "1", 9999, "", "cup, chopped", "160", "", "", ""],
        [2, 170000, 2, "1", 9999, "", "medium (2-1/2\" dia)", "110", "", "", ""],
        [3, 169655, 1, "1", 1000, "", "", "200", "", "", ""],
        [4, 169655, 2, "1", 1001, "", "", "12.5", "", "", ""],
    ])
    _write(tmp_path / "measure_unit.csv", ["id", "name"], [[1000, "cup"], [1001, "tablespoon"], [9999, "undetermined"]])
    return tmp_path


def test_loads_roster_nutrients_per_100g_and_drops_others(sr_dir: Path) -> None:
    foods = SR.load_sr(sr_dir)
    onion = foods[170000]
    assert onion.description == "Onions, raw" and onion.category_id == 11
    assert onion.nutrients == {"water_g": 89.11, "protein_g": 1.1, "sodium_mg": 4.0}


def test_absent_nutrient_is_unknown_not_zero(sr_dir: Path) -> None:
    onion = SR.load_sr(sr_dir)[170000]
    assert onion.nutrient("fat_g") is None
    assert onion.nutrient("water_g") == pytest.approx(89.11)
    with pytest.raises(KeyError):
        onion.nutrient("not_a_roster_name")


def test_excluded_categories_are_dropped(sr_dir: Path) -> None:
    foods = SR.load_sr(sr_dir)
    assert 170700 not in foods and set(foods) == {170000, 169655}
    assert 21 in SR.EXCLUDED_CATEGORIES and 11 not in SR.EXCLUDED_CATEGORIES


def test_portions_use_modifier_for_9999_and_unit_name_otherwise(sr_dir: Path) -> None:
    foods = SR.load_sr(sr_dir)
    onion = {p.description: p.gram_weight for p in foods[170000].portions}
    assert onion == {"cup, chopped": 160.0, "medium (2-1/2\" dia)": 110.0}
    sugar = {p.description: p.gram_weight for p in foods[169655].portions}
    assert sugar == {"cup": 200.0, "tablespoon": 12.5}
    assert foods[169655].portions[0].unit_name == "cup"


def test_records_are_immutable(sr_dir: Path) -> None:
    onion = SR.load_sr(sr_dir)[170000]
    with pytest.raises(Exception):
        onion.description = "x"  # type: ignore[misc]
    with pytest.raises(TypeError):
        onion.nutrients["water_g"] = 1.0  # type: ignore[index]


def test_missing_file_fails_loudly(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        SR.load_sr(tmp_path)


def test_bad_amount_fails_loudly(sr_dir: Path) -> None:
    p = sr_dir / "food_nutrient.csv"
    p.write_text(p.read_text(encoding="utf-8") + '"9","170000","1004","abc","","","","","","",""\n', encoding="utf-8")
    with pytest.raises(ValueError, match="170000"):
        SR.load_sr(sr_dir)
