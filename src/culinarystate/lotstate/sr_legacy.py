"""USDA SR Legacy (FoodData Central 2018-04 CSV export, public domain) reader for the lot-state layer.

Reads food.csv, food_category.csv, food_nutrient.csv and food_portion.csv from a directory (read-only).
Nutrient values stay exact (Fractions from the decimal text); a nutrient with no row for a food is UNKNOWN
(absent from the dict), never 0. Portions are parsed into volume / count / mass kinds; ``grams_per_unit`` is
gram_weight / amount.

Nutrient keys (per 100 g edible portion): water g, protein g, fat g, carbohydrate g, sugars g (nutrient 2000,
else 1063), starch g, fibre g, ash g, sodium mg, vitamin_c mg.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from culinarystate.quantity.units import (US_CUP, US_FLOZ, US_TBSP, US_TSP, UNITS, lookup)

from .intervals import frac
from .text import strip_marks

SR_DIRNAME = "FoodData_Central_sr_legacy_food_csv_2018-04"
NUTRIENT_IDS: dict[str, tuple[tuple[int, ...], str]] = {
    "water": ((1051,), "g"), "protein": ((1003,), "g"), "fat": ((1004,), "g"), "carbohydrate": ((1005,), "g"),
    "sugars": ((2000, 1063), "g"), "starch": ((1009,), "g"), "fibre": ((1079,), "g"), "ash": ((1007,), "g"),
    "sodium": ((1093,), "mg"), "vitamin_c": ((1162,), "mg"),
}
NUTRIENT_UNITS = {k: v[1] for k, v in NUTRIENT_IDS.items()}
NUTRIENT_KEYS = tuple(NUTRIENT_IDS)

# mL per SR volume unit (US customary, as USDA household measures; constants from quantity.units, NIST HB44 / exact)
ML_PER_UNIT: dict[str, Fraction] = {
    "cup": frac(US_CUP), "tbsp": frac(US_TBSP), "tsp": frac(US_TSP), "fl_oz": frac(US_FLOZ),
    "ml": Fraction(1), "l": Fraction(1000), "cubic_inch": Fraction("16.387064"),
    "pint": frac(473.176473), "quart": frac(946.352946), "gallon": frac(3785.411784),
}
SIZE_WORDS = ("extra large", "extra small", "jumbo", "large", "medium", "small", "mini")
GENERIC_COUNT = frozenset({"item", "unit", "whole", "each", "fruit", "piece", "pieces", "egg", "bulb"})
COUNT_UNIT_KEYS = frozenset(u.key for u in UNITS if u.unit_type == "COUNT_PORTION")
PACKAGE_WORDS = frozenset({"can", "jar", "package", "packet", "bag", "bottle", "box", "container", "carton", "pouch",
                           "tub", "tray", "pot", "pack"})
MASS_WORDS = frozenset({"oz", "lb", "g", "kg", "ounce", "pound"})
_VOL_ALIASES = {"cup": "cup", "cups": "cup", "tbsp": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
                "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp", "fl oz": "fl_oz", "fluid ounce": "fl_oz",
                "liter": "l", "litre": "l", "ml": "ml", "milliliter": "ml", "cubic inch": "cubic_inch",
                "pint": "pint", "quart": "quart", "gallon": "gallon"}
_PAREN = re.compile(r"\(([^)]*)\)")


@dataclass(frozen=True)
class Portion:
    portion_id: int
    fdc_id: int
    amount: Fraction
    modifier: str            # SR text (public domain), kept for provenance
    kind: str                # VOLUME | COUNT | MASS | PACKAGE | OTHER
    unit_key: str | None     # volume: ML_PER_UNIT key; count: item | clove | slice | ...
    size: str | None
    descriptor: str          # words after the unit (chopped, sliced, ...), lower case
    grams_per_unit: Fraction
    ml_per_unit: Fraction | None = None

    @property
    def g_per_ml(self) -> Fraction | None:
        return None if self.ml_per_unit is None else self.grams_per_unit / self.ml_per_unit


def parse_portion(portion_id: int, fdc_id: int, amount, modifier: str, gram_weight) -> Portion | None:
    amt, gw = frac(amount), frac(gram_weight)
    if amt <= 0 or gw <= 0:
        return None
    m = strip_marks(modifier or "").lower().strip()
    yield_note = "yield from" in m or "excluding refuse" in m or "edible portion" in m
    base = _PAREN.sub(" ", m)
    head, _, rest = base.partition(",")
    head = re.sub(r"\s+", " ", head).strip()
    descriptor = re.sub(r"\s+", " ", rest).strip()
    size = None
    for s in SIZE_WORDS:
        if head == s or head.startswith(s + " "):
            size, head = s, head[len(s):].strip()
            break
    if size is None:
        for s in SIZE_WORDS:
            if re.search(rf"\b{s}\b", descriptor):
                size = s
                break
    words = head.split()
    first = words[0] if words else ""
    two = " ".join(words[:2])
    after = " ".join(words[1:]) if first else ""
    kind, unit_key = "OTHER", None
    if yield_note:
        kind = "OTHER"
    elif two in _VOL_ALIASES:
        kind, unit_key, after = "VOLUME", _VOL_ALIASES[two], " ".join(words[2:])
    elif first in _VOL_ALIASES:
        kind, unit_key = "VOLUME", _VOL_ALIASES[first]
    elif first in MASS_WORDS:
        kind = "MASS"
    elif first in PACKAGE_WORDS:
        kind = "PACKAGE"
    elif size is not None and not first:
        kind, unit_key = "COUNT", "item"
    elif first in GENERIC_COUNT:
        kind, unit_key = "COUNT", "item"
    else:
        u = lookup(first) if first else None
        if u is not None and u.key in COUNT_UNIT_KEYS:
            kind, unit_key = "COUNT", u.key
        elif size is not None:
            kind, unit_key = "COUNT", "item"      # "medium head", "large leaf" style: size-qualified count
    desc = " ".join(x for x in (after, descriptor) if x).strip()
    return Portion(portion_id, fdc_id, amt, modifier or "", kind, unit_key, size, desc, gw / amt,
                   ML_PER_UNIT.get(unit_key) if kind == "VOLUME" else None)


@dataclass(frozen=True)
class SRFood:
    fdc_id: int
    description: str
    category: str
    nutrients: dict = field(default_factory=dict, hash=False, compare=False)  # key -> Fraction per 100 g (absent = UNKNOWN)


class SRLegacy:
    def __init__(self, foods: dict[int, SRFood], portions: dict[int, list[Portion]], source_dir: str):
        self.foods, self.portions, self.source_dir = foods, portions, source_dir

    def nutrient(self, fdc_id: int, key: str) -> Fraction | None:
        f = self.foods.get(fdc_id)
        return None if f is None else f.nutrients.get(key)

    def volume_portions(self, fdc_id: int) -> list[Portion]:
        return [p for p in self.portions.get(fdc_id, ()) if p.kind == "VOLUME"]

    def count_portions(self, fdc_id: int) -> list[Portion]:
        return [p for p in self.portions.get(fdc_id, ()) if p.kind == "COUNT"]


def default_dir(root: Path) -> Path:
    base = Path(root) / "data" / "raw" / "fdc" / "sr_legacy"
    cand = base / SR_DIRNAME
    return cand if cand.exists() else next(base.glob("FoodData_Central_sr_legacy_food_csv_*"))


def _rows(path: Path) -> Iterable[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        yield from csv.DictReader(fh)


def load_sr(sr_dir: Path) -> SRLegacy:
    d = Path(sr_dir)
    cats = {r["id"]: r["description"] for r in _rows(d / "food_category.csv")}
    foods: dict[int, SRFood] = {}
    for r in _rows(d / "food.csv"):
        foods[int(r["fdc_id"])] = SRFood(int(r["fdc_id"]), r["description"], cats.get(r["food_category_id"], ""), {})
    wanted: dict[int, list[tuple[str, int]]] = {}
    for key, (ids, _unit) in NUTRIENT_IDS.items():
        for rank, nid in enumerate(ids):
            wanted.setdefault(nid, []).append((key, rank))
    best: dict[tuple[int, str], tuple[int, Fraction]] = {}
    for r in _rows(d / "food_nutrient.csv"):
        nid = int(r["nutrient_id"])
        if nid not in wanted:
            continue
        fdc = int(r["fdc_id"])
        if fdc not in foods or r["amount"] == "":
            continue
        for key, rank in wanted[nid]:
            cur = best.get((fdc, key))
            if cur is None or rank < cur[0]:
                best[(fdc, key)] = (rank, frac(r["amount"]))
    for (fdc, key), (_rank, val) in best.items():
        foods[fdc].nutrients[key] = val
    portions: dict[int, list[Portion]] = {}
    for r in _rows(d / "food_portion.csv"):
        p = parse_portion(int(r["id"]), int(r["fdc_id"]), r["amount"], r["modifier"], r["gram_weight"])
        if p is not None:
            portions.setdefault(p.fdc_id, []).append(p)
    return SRLegacy(foods, portions, str(d))
