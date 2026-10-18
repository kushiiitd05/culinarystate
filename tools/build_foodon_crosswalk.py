#!/usr/bin/env python3
"""X1: ING -> FoodOn crosswalk + coarse category from FoodOn ancestry (D-009).

  /opt/anaconda3/bin/python tools/build_foodon_crosswalk.py
Status per ING: LINKED (unique exact label, non-polysemous) · CANDIDATE (synonym / qualified label / tie /
polysemous) · NO_MATCH. category only from LINKED or unique ≥ 0.9 matches. Writes ING revisions,
registry/ingredients/foodon_crosswalk_v1.csv (human_decision column), reports/foodon_crosswalk_v1.md.
"""
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.vocab.fdc import UK_US  # noqa: E402
from culinarystate.vocab.foodon import ancestors, name_index, norm, parse  # noqa: E402
from culinarystate.vocab.registry_build import POLYSEMOUS  # noqa: E402

OWL = ROOT / "data" / "raw" / "foodon" / "foodon.owl"
CATEGORY_RULES = (  # applied to the NEAREST matching label (self, then ancestors breadth-first); rule order only
    # breaks ties within one label ("wine vinegar" -> CONDIMENT)
    ("VEGETABLE", r"as vegetable"), ("DAIRY", r"dairy|milk|cheese"), ("EGG", r"\begg"),
    ("SEAFOOD", r"fish|shellfish|seafood|crustacean|mollus"), ("MEAT", r"\bmeat|poultry|sausage"),
    ("SWEETENER", r"sugar|sweetener|honey|syrup"), ("CONDIMENT", r"sauce|condiment|vinegar|dressing"),
    ("FAT_OIL", r"\boil\b|\bfat\b|fat or oil"), ("HERB_SPICE", r"spice|herb|seasoning"),
    ("BEVERAGE", r"beverage|alcoholic|\bwine\b|juice|\btea\b|coffee"),
    ("CEREAL", r"cereal|grain|flour|bread|pasta|\brice\b|noodle"), ("LEGUME", r"legume|pulse|\bbean|soybean|lentil"),
    ("NUT_SEED", r"\bnut\b|\bnuts\b|seed"), ("VEGETABLE", r"vegetable|tuber"), ("FRUIT", r"\bfruit"))


def category(tid: str, terms: dict) -> str | None:
    labels = [terms[tid].label] + [terms[a].label for a in ancestors(tid, terms) if a in terms]
    if any("as vegetable" in lab for lab in labels):
        return "VEGETABLE"
    if any(lab == "spice or herb" for lab in labels):
        return "HERB_SPICE"
    for lab in labels:
        for cat, pat in CATEGORY_RULES:
            if re.search(pat, lab.lower()):
                return cat
    return None


def match(name: str, idx: dict, terms: dict) -> tuple[str, list[tuple[str, float]]]:
    cands: dict[str, float] = {}
    for n in [name, *UK_US.get(name, []), name.replace("-", " ")]:
        for tid, sc in idx.get(norm(n), {}).items():
            cands[tid] = max(sc * (1.0 if n == name else 0.95), cands.get(tid, 0))
    ranked = sorted(cands.items(), key=lambda x: (-x[1], len(terms[x[0]].label), x[0]))
    if not ranked:
        return "NO_MATCH", []
    top = [r for r in ranked if r[1] == ranked[0][1]]
    if ranked[0][1] == 1.0 and len(top) == 1 and name not in POLYSEMOUS:
        return "LINKED", ranked
    return "CANDIDATE", ranked


def main() -> None:
    terms = parse(OWL)
    idx = name_index(terms)
    st = LedgerStore()
    rows, writes, bands = [], Counter(), Counter()
    for ing in st.all_latest("ING"):
        if ing["status"] != "ACTIVE":
            continue
        name = ing["canonical_name"]
        status, ranked = match(name, idx, terms)
        freq = ing.get("corpus_frequency") or 0
        bands[status] += 1
        bands[f"{status}_mentions"] += freq
        best = ranked[0] if ranked else (None, None)
        unique_top = len([r for r in ranked if r[1] == best[1]]) == 1 if ranked else False
        cat = category(best[0], terms) if best[0] and (status == "LINKED" or (unique_top and best[1] >= 0.9)) else None
        cw = {**(ing.get("crosswalks") or {}),
              "foodon": {"status": status, "external_id": best[0], "score": round(best[1], 3) if best[1] else None}}
        refs = [r for r in (ing.get("external_refs") or []) if not r.startswith("FOODON:")]
        if status == "LINKED":
            refs.append(f"FOODON:{best[0].split('_', 1)[1]}")
        new = {**ing, "crosswalks": cw, "external_refs": sorted(refs), "category": cat or ing.get("category")}
        writes[st.upsert(new)[0]] += 1
        rows.append({"ing_id": ing["id"], "canonical_name": name, "corpus_frequency": freq, "status": status,
                     "foodon_id": best[0], "foodon_label": terms[best[0]].label if best[0] else None,
                     "score": best[1], "category": cat,
                     "alternatives": " | ".join(f"{t}:{terms[t].label}:{s:.2f}" for t, s in ranked[1:4]),
                     "human_decision": ""})
    df = pd.DataFrame(rows).sort_values("corpus_frequency", ascending=False)
    out = ROOT / "registry" / "ingredients" / "foodon_crosswalk_v1.csv"
    df.to_csv(out, index=False)
    total, mentions = len(df), df.corpus_frequency.sum()
    lines = ["# FoodOn crosswalk v1 (X1, D-009)", "",
             f"FoodOn terms parsed: {len(terms):,} · names indexed: {len(idx):,} · ING concepts: {total:,}", "",
             "| status | concepts | % concepts | % corpus mentions |", "|---|---|---|---|"]
    for s in ("LINKED", "CANDIDATE", "NO_MATCH"):
        lines.append(f"| {s} | {bands[s]:,} | {100 * bands[s] / total:.1f}% | "
                     f"{100 * bands[s + '_mentions'] / max(mentions, 1):.1f}% |")
    cats = df.category.value_counts()
    lines += ["", "Categories (from FoodOn ancestry): " + ", ".join(f"{k} {v}" for k, v in cats.items()), "",
              "LINKED = unique exact FoodOn label, non-polysemous (rule-based, not human-verified).",
              "Top unmatched by frequency: " + ", ".join(df[df.status == "NO_MATCH"].canonical_name.head(25))]
    (ROOT / "reports" / "foodon_crosswalk_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[2:9]), "\nING writes:", dict(writes))


if __name__ == "__main__":
    main()
