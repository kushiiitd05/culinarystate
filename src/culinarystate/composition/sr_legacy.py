"""USDA FoodData Central SR Legacy (2018-04, public domain) loader for the lot-state layer (S175).

Reads food.csv, food_nutrient.csv, food_portion.csv and measure_unit.csv from an unpacked SR Legacy CSV directory.
Amounts are SR values per 100 g edible portion (MEASURED by USDA, provenance = fdc_id). A roster nutrient missing
from SR is UNKNOWN (``None``), never 0. Categories that are branded, restaurant, fast food, prepared meals, baby
food, American Indian or QC are dropped: they are not ingredients.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

NUTRIENTS: Mapping[str, int] = MappingProxyType({
    "water_g": 1051, "protein_g": 1003, "fat_g": 1004, "carbohydrate_g": 1005, "sugars_g": 2000,
    "starch_g": 1009, "fibre_g": 1079, "ash_g": 1007, "sodium_mg": 1093, "vitamin_c_mg": 1162,
    "calcium_mg": 1087,
})
_BY_ID = {v: k for k, v in NUTRIENTS.items()}
EXCLUDED_CATEGORIES = frozenset({3, 21, 22, 24, 25, 26, 27})
UNDETERMINED_UNIT = 9999
SOURCE = "USDA FoodData Central SR Legacy 2018-04 (public domain)"


@dataclass(frozen=True)
class Portion:
    description: str
    gram_weight: float
    amount: float
    unit_id: int
    unit_name: str


@dataclass(frozen=True)
class SRFood:
    fdc_id: int
    description: str
    category_id: int
    nutrients: Mapping[str, float]
    portions: tuple[Portion, ...]

    def nutrient(self, name: str) -> float | None:
        if name not in NUTRIENTS:
            raise KeyError(f"not a roster nutrient: {name}")
        return self.nutrients.get(name)


def _rows(path: Path):
    with open(path, newline="", encoding="utf-8") as fh:
        yield from csv.DictReader(fh)


def _float(text: str, what: str, fdc: str) -> float:
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"bad {what} {text!r} for fdc_id {fdc}") from exc


def _foods(d: Path) -> dict[int, tuple[str, int]]:
    out = {}
    for r in _rows(d / "food.csv"):
        cat = int(r["food_category_id"])
        if cat not in EXCLUDED_CATEGORIES:
            out[int(r["fdc_id"])] = (r["description"], cat)
    return out


def _nutrients(d: Path, keep: dict) -> dict[int, dict[str, float]]:
    out: dict[int, dict[str, float]] = {}
    for r in _rows(d / "food_nutrient.csv"):
        fdc, nid = int(r["fdc_id"]), int(r["nutrient_id"])
        if fdc in keep and nid in _BY_ID and r["amount"].strip():
            out.setdefault(fdc, {})[_BY_ID[nid]] = _float(r["amount"], "amount", r["fdc_id"])
    return out


def _portions(d: Path, keep: dict) -> dict[int, list[tuple[int, Portion]]]:
    units = {int(r["id"]): r["name"] for r in _rows(d / "measure_unit.csv")}
    out: dict[int, list[tuple[int, Portion]]] = {}
    for r in _rows(d / "food_portion.csv"):
        fdc = int(r["fdc_id"])
        if fdc not in keep or not r["gram_weight"].strip():
            continue
        uid, mod = int(r["measure_unit_id"]), r["modifier"].strip()
        unit = units.get(uid, "")
        if uid == UNDETERMINED_UNIT:
            desc = mod or r["portion_description"].strip()
        else:
            desc = f"{unit}, {mod}" if mod else unit
        amount = _float(r["amount"], "amount", r["fdc_id"]) if r["amount"].strip() else 1.0
        p = Portion(desc, _float(r["gram_weight"], "gram_weight", r["fdc_id"]), amount, uid, unit)
        out.setdefault(fdc, []).append((int(r["seq_num"] or 0), p))
    return out


def load_sr(directory: Path | str) -> dict[int, SRFood]:
    d = Path(directory)
    foods = _foods(d)
    nutr = _nutrients(d, foods)
    por = _portions(d, foods)
    return {fdc: SRFood(fdc, desc, cat, MappingProxyType(dict(nutr.get(fdc, {}))),
                        tuple(p for _, p in sorted(por.get(fdc, []), key=lambda t: t[0])))
            for fdc, (desc, cat) in foods.items()}
