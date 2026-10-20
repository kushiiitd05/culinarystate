#!/usr/bin/env python3
"""S116: cleaned missing-evidence ranking for the 20 Gold-v1.1 recipes (replaces the raw missing_cells_gold20.csv ranking).

A cell (ingredient, process) is an evidence-acquisition TARGET only if (1) the ingredient is a physically meaningful carrier of a
measurable state variable, (2) the process is a specific thermal process (generic 'cook'/'heat' stay UNRESOLVED, never guessed),
and (3) the current Gold state at some valid cut actually needs it (cut counts come from hstate_missing_cells.py).
Everything else is listed as excluded with the reason. No system output is used.
  /opt/anaconda3/bin/python tools/hstate_missing_evidence_ranked.py
"""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reports" / "h_state" / "missing_cells_gold20.csv"
OUT = ROOT / "reports" / "h_state" / "hstate_missing_evidence_cells_ranked.csv"
THERMAL = {"DRY_HEAT", "WET_HEAT", "FAT_HEAT"}
GENERIC = {"HEAT_GENERAL"}
# ING.category where set; otherwise this explicit allow-map (documented: these ING rows have no category yet)
NAME_GROUP = {"garlic": "VEGETABLE", "carrot": "VEGETABLE", "spring onion": "VEGETABLE", "ginger": "VEGETABLE", "rocket": "VEGETABLE",
              "green beans": "VEGETABLE", "sweetcorn": "VEGETABLE", "leaf spinach": "VEGETABLE", "asparagus tip": "VEGETABLE",
              "garden pea": "VEGETABLE", "courgette flower": "VEGETABLE", "egg": "EGG", "lamb chop": "MEAT", "basmati rice": "CEREAL",
              "wild rice mix": "CEREAL"}
MEANINGFUL = {"VEGETABLE", "FRUIT", "MEAT", "SEAFOOD", "LEGUME", "CEREAL", "EGG", "NUT_SEED"}
NEED = {"VEGETABLE": ("THERMAL_RETENTION", "vitamin C / carotenoid / polyphenol retention and water loss"),
        "FRUIT": ("THERMAL_RETENTION", "vitamin C / anthocyanin retention"),
        "MEAT": ("YIELD/MASS", "cooking yield, moisture and fat change"),
        "SEAFOOD": ("YIELD/MASS", "cooking yield and nutrient change"),
        "LEGUME": ("YIELD/MASS", "water uptake / yield and nutrient retention"),
        "CEREAL": ("YIELD/MASS", "water uptake / cooked yield"),
        "EGG": ("THERMAL_RETENTION", "nutrient retention and protein-set endpoint"),
        "NUT_SEED": ("MOISTURE", "moisture / texture change on roasting")}
SOURCES = {"MEAT": "USDA Cooking Yields Meat&Poultry R2 (CC0); AFCD recipe weight-change; FNDDS input-food retention codes",
           "SEAFOOD": "FAO uFiSh 09 Yield Factors (compiled); USDA R6 seafood rows",
           "VEGETABLE": "FNDDS inputFoods retentionCode -> USDA R6; AFCD; primary literature (vitamin C / carotenoid kinetics)",
           "FRUIT": "USDA R6; primary literature",
           "LEGUME": "USDA AH-102 / R6; FAO uPulses (raw vs processed)",
           "CEREAL": "USDA AH-102 yields; FNDDS portions",
           "EGG": "USDA R6; FNDDS", "NUT_SEED": "primary literature"}
COST = {"MEAT": "LOW (compiled CC0 table, digitised)", "SEAFOOD": "LOW-MEDIUM (compiled, needs species mapping)", "VEGETABLE": "MEDIUM (R6 gap: literature)",
        "FRUIT": "MEDIUM", "LEGUME": "MEDIUM", "CEREAL": "LOW-MEDIUM", "EGG": "MEDIUM", "NUT_SEED": "HIGH"}


def classify(row, category):
    group = category or NAME_GROUP.get(row["ingredient"])
    if row["ingredient"].endswith((" oil", " butter", " fat")) or row["ingredient"] in {"oil", "butter", "water"}:
        group = "FAT_OIL"                                              # category data can be wrong (e.g. avocado oil as FRUIT)
    fam = row["process_family"]
    if fam in GENERIC:
        return None, "GENERIC_PROCESS_UNRESOLVED"
    if fam not in THERMAL:
        return None, "NON_THERMAL_STRUCTURAL_ONLY"
    if group not in MEANINGFUL:
        return None, "INGREDIENT_NOT_RETENTION_MEANINGFUL" if group else "INGREDIENT_UNCATEGORISED"
    return group, ""


def main():
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from culinarystate.ledgers.store import LedgerStore
    cat = {i["id"]: i.get("category") for i in LedgerStore().all_latest("ING")}
    rows = list(csv.DictReader(SRC.open()))
    kept, excluded = [], Counter()
    for r in rows:
        group, why = classify(r, cat.get(r["ingredient_id"]))
        if group is None:
            excluded[why] += 1
            continue
        need, attr = NEED[group]
        kept.append({"ingredient_id": r["ingredient_id"], "ingredient": r["ingredient"], "process_id": r["process_id"], "process": r["process"],
                     "process_family": r["process_family"], "state_attribute_needed": attr, "recipes_unlocked": r["recipes_unlocked"],
                     "cuts_unlocked": r["cuts_unlocked"], "evidence_type_needed": need, "candidate_sources": SOURCES[group],
                     "estimated_verification_cost": COST[group], "priority": 0,
                     "notes": f"group={group}; a source row only counts if it names this ingredient AND this process; raw/cooked pairs need provenance"})
    kept.sort(key=lambda k: (-int(k["recipes_unlocked"]), -int(k["cuts_unlocked"]), k["estimated_verification_cost"], k["ingredient"]))
    for i, k in enumerate(kept, 1):
        k["priority"] = i
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(kept[0]))
        w.writeheader()
        w.writerows(kept)
    print(len(rows), "raw cells ->", len(kept), "targets; excluded:", dict(excluded))
    for k in kept[:15]:
        print(k["priority"], k["ingredient"], k["process"], k["recipes_unlocked"], k["cuts_unlocked"], k["evidence_type_needed"])


if __name__ == "__main__":
    main()
