#!/usr/bin/env python3
"""D-116 C_t v1.2: per-ingredient composition from USDA SR Legacy (2018-04, public domain) for the rank-1 SR match
of each ACTIVE ING with confidence HIGH or MEDIUM. Values are copied, never estimated; locator = fdc_id + nutrient_id.
The match itself is AI_DRAFTED (registry/ing_sr_legacy_match_draft_v1.csv), so rows carry that status.

    python tools/s179_build_ing_sr_composition.py --out registry/ing_sr_composition_v1.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SR_DIR = ROOT / "data/raw/fdc/sr_legacy/FoodData_Central_sr_legacy_food_csv_2018-04"
MATCH = ROOT / "registry/ing_sr_legacy_match_draft_v1.csv"
NUTRIENTS = {"1004": ("fat_g_per_100g", "g"), "1051": ("water_g_per_100g", "g"), "1093": ("sodium_mg_per_100g", "mg"),
             "1003": ("protein_g_per_100g", "g"), "2000": ("sugars_g_per_100g", "g")}
USABLE = ("HIGH", "MEDIUM")
COLUMNS = ["ing_id", "canonical_name", "fdc_id", "sr_description", "confidence_band", "nutrient_key", "nutrient_id",
           "unit", "amount", "source_release", "licence", "status"]


def matches(path: Path = MATCH) -> dict[str, list[dict]]:
    out = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["rank"] == "1" and r["confidence_band"] in USABLE and r["fdc_id"]:
                out.setdefault(r["fdc_id"], []).append(r)
    return out


def build(match_by_fdc: dict[str, list[dict]], food_nutrient: Path) -> list[dict]:
    rows = []
    with food_nutrient.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["nutrient_id"] not in NUTRIENTS:
                continue
            key, unit = NUTRIENTS[r["nutrient_id"]]
            rows.extend({"ing_id": m["ing_id"], "canonical_name": m["canonical_name"], "fdc_id": r["fdc_id"],
                         "sr_description": m["sr_description"], "confidence_band": m["confidence_band"],
                         "nutrient_key": key, "nutrient_id": r["nutrient_id"], "unit": unit, "amount": r["amount"],
                         "source_release": "USDA_SR_LEGACY_2018_04", "licence": "PUBLIC_DOMAIN_CC0",
                         "status": "SR_VALUE_COPIED; ING_MATCH_AI_DRAFTED"}
                        for m in match_by_fdc.get(r["fdc_id"], ()))
    return sorted(rows, key=lambda x: (x["ing_id"], x["nutrient_key"]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    rows = build(matches(), SR_DIR / "food_nutrient.csv")
    with out.open("x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "rows,", len({r["ing_id"] for r in rows}), "ingredients")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
