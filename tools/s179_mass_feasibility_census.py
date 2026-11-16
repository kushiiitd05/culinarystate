#!/usr/bin/env python3
"""Feasibility census (no implementation): could salt/fat fractions be computed WITHOUT assumptions?

Per ingredient line (seeded sample per family): quantity parsed? unit class (MASS / VOLUME / COUNT_OR_NONE)? ING
linked (lexicon, exactly one)? SR match (rank 1, HIGH/MEDIUM)? For VOLUME: a food-specific SR food_portion row whose
unit word matches (cup / tablespoon / teaspoon / fl oz / ml); INFOODS density is counted only as an exact
canonical-name match (no crosswalk exists, so this is expected ~0). A line is GROUNDED if mass is stated, or volume
+ SR portion for that food and unit. A recipe is FULLY_GROUNDED if every line is. Counts only, no text.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
SR = ROOT / "data/raw/fdc/sr_legacy/FoodData_Central_sr_legacy_food_csv_2018-04"
MASS = {"g", "gram", "grams", "kg", "oz", "ounce", "lb", "pound", "mg"}
VOLUME = {"cup": "cup", "c": "cup", "tbsp": "tablespoon", "tablespoon": "tablespoon", "tsp": "teaspoon",
          "teaspoon": "teaspoon", "fl_oz": "fl oz", "floz": "fl oz", "ml": "ml", "l": "ml", "litre": "ml", "liter": "ml",
          "pint": "pint", "quart": "quart", "gill": "gill", "dessertspoon": "dessertspoon"}
NUMERIC = {"NUMBER", "RANGE", "FRACTION", "MIXED", "MULTIPLIER"}


def _portions() -> dict[str, set[str]]:
    units = {}
    with (SR / "measure_unit.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            units[r["id"]] = r["name"].lower()
    out: dict[str, set[str]] = defaultdict(set)
    with (SR / "food_portion.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            text = " ".join((units.get(r["measure_unit_id"], ""), r["modifier"] or "", r["portion_description"] or "")).lower()
            for u in ("cup", "tablespoon", "tbsp", "teaspoon", "tsp", "fl oz", "ml", "pint", "quart"):
                if re.search(rf"\b{re.escape(u)}\b", text):
                    out[r["fdc_id"]].add({"tbsp": "tablespoon", "tsp": "teaspoon"}.get(u, u))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-family", type=int, default=1000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.lotstate import corpus as C
    from culinarystate.quantity.grammar import parse_line
    lex = RungA().lexicon
    match = {}
    with (ROOT / "registry/ing_sr_legacy_match_draft_v1.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            if r["rank"] == "1" and r["confidence_band"] in ("HIGH", "MEDIUM") and r["fdc_id"]:
                match[r["ing_id"]] = r["fdc_id"]
    portions = _portions()
    import openpyxl
    ws = openpyxl.load_workbook(ROOT / "data/external/infoods/density_v2.xlsx", read_only=True)["Density DB"]
    infoods = {str(r[0]).strip().lower() for r in ws.iter_rows(values_only=True) if r and r[0] and r[1]}
    ing_name = {}
    for line in (ROOT / "ledgers/data/ING.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            ing_name[r["id"]] = r["canonical_name"].lower()
    res = defaultdict(Counter)
    seen = Counter()
    for rec in C.stream(("FOODCOM", "WIKIBOOKS", "GUTENBERG_SEGMENT", "TASTESET", "A1_BBC_GOOD_FOOD"), ROOT):
        fam = rec.get("source_family", "?")
        if seen[fam] >= a.per_family:
            continue
        seen[fam] += 1
        c = res[fam]
        c["recipes"] += 1
        lines = [str(x) for x in (rec.get("ingredient_lines") or []) if str(x).strip()]
        all_ok = bool(lines)
        for ln in lines:
            c["lines"] += 1
            p = parse_line(ln)
            num = p.kind in NUMERIC
            c["qty_parsed"] += num
            uk = (p.unit_key or "").lower()
            ucls = "MASS" if uk in MASS else "VOLUME" if uk in VOLUME else "COUNT_OR_NONE"
            c[f"unit:{ucls}"] += num
            ids = lex.food_ids(p.rest or ln)
            ing = next(iter(ids)) if len(ids) == 1 else None
            c["ing_linked"] += ing is not None
            fdc = match.get(ing) if ing else None
            c["sr_matched"] += fdc is not None
            c["infoods_exact_name"] += bool(ing and ing_name.get(ing) in infoods)
            ok = num and (ucls == "MASS" or (ucls == "VOLUME" and fdc is not None and VOLUME[uk] in portions.get(fdc, ())))
            c["grounded"] += bool(ok)
            c["grounded_volume_via_sr_portion"] += bool(ok and ucls == "VOLUME")
            all_ok &= bool(ok)
        c["recipes_fully_grounded"] += all_ok
    tot = Counter()
    for c in res.values():
        tot.update(c)
    pct = lambda c: {k: round(100 * c[k] / max(1, c["lines"]), 1) for k in ("qty_parsed", "ing_linked", "sr_matched",
                                                                           "grounded", "infoods_exact_name")}
    report = {"per_family": {f: {**dict(c), "pct_of_lines": pct(c),
                                 "pct_recipes_fully_grounded": round(100 * c["recipes_fully_grounded"] / max(1, c["recipes"]), 1)}
                             for f, c in res.items()},
              "total": {**dict(tot), "pct_of_lines": pct(tot),
                        "pct_recipes_fully_grounded": round(100 * tot["recipes_fully_grounded"] / max(1, tot["recipes"]), 1)},
              "rule": "no generic density; volume only via a food-specific SR portion row; count units never grounded",
              "contains_text": False}
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps(report["total"]))
    for f, v in report["per_family"].items():
        print(f, v["pct_of_lines"], "fully grounded recipes %", v["pct_recipes_fully_grounded"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
