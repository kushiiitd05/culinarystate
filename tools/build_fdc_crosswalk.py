#!/usr/bin/env python3
"""ING -> FDC SR Legacy crosswalk candidates + portion candidates + potential mass-grounding gain.

  /opt/anaconda3/bin/python tools/build_fdc_crosswalk.py
Outputs (for human verification; nothing is LINKED automatically):
  registry/ingredients/fdc_crosswalk_candidates_v0.csv   top-3 FDC foods per ING, ranked by corpus frequency
  registry/ingredients/fdc_portion_candidates_v0.csv     FDC portions of each ING's top-1 HIGH candidate
  reports/fdc_crosswalk_v0.md                            bands + how many BBC lines would gain sourced grams
"""
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.quantity.grammar import parse_line  # noqa: E402
from culinarystate.quantity.normalize import normalize  # noqa: E402
from culinarystate.vocab.fdc import candidates_for, load_sr, parse_portion_modifier, token_index  # noqa: E402

SR = ROOT / "data" / "raw" / "fdc" / "sr_legacy" / "FoodData_Central_sr_legacy_food_csv_2018-04"
food, por = load_sr(SR)
idx = token_index(food)
reg = pd.read_csv(ROOT / "registry" / "ingredients" / "ingredient_registry_v1.csv")

rows, top1 = [], {}
for r in reg.itertuples(index=False):
    cands = candidates_for(r.canonical_name, food, idx)
    if not cands:
        rows.append({"ing_id": r.ing_id, "canonical": r.canonical_name, "recipe_freq": r.recipe_freq, "rank": None,
                     "fdc_id": None, "description": None, "category": None, "score": None, "band": "NO_CANDIDATE",
                     "via_synonym": None, "human_decision": ""})
    for k, c in enumerate(cands, 1):
        rows.append({"ing_id": r.ing_id, "canonical": r.canonical_name, "recipe_freq": r.recipe_freq, "rank": k,
                     "fdc_id": c.fdc_id, "description": c.description, "category": c.category, "score": c.score,
                     "band": c.band, "via_synonym": c.via or None, "human_decision": ""})
    if cands and cands[0].band == "HIGH":
        top1[r.canonical_name] = cands[0].fdc_id
cw = pd.DataFrame(rows).sort_values(["recipe_freq", "canonical", "rank"], ascending=[False, True, True])
out = ROOT / "registry" / "ingredients"
cw.to_csv(out / "fdc_crosswalk_candidates_v0.csv", index=False)

prow = []
por_by_fdc = por.groupby("fdc_id")
portion_lookup: dict[str, list[tuple[str | None, str | None, float]]] = {}
for name, fdc_id in top1.items():
    if fdc_id not in por_by_fdc.groups:
        continue
    for p in por_by_fdc.get_group(fdc_id).itertuples(index=False):
        pu = parse_portion_modifier(p.modifier if isinstance(p.modifier, str) else "")
        g = p.gram_weight / p.amount if p.amount else None
        prow.append({"canonical": name, "fdc_id": fdc_id, "fdc_portion_id": p.id, "amount": p.amount,
                     "modifier": p.modifier, "unit_key": pu.unit_key, "size": pu.size, "note": pu.note,
                     "grams_per_unit": round(g, 4) if g else None, "data_points": p.data_points,
                     "locale": "US", "status": "CANDIDATE_UNVERIFIED_LINK"})
        portion_lookup.setdefault(name, []).append((pu.unit_key, pu.size, g))
pd.DataFrame(prow).to_csv(out / "fdc_portion_candidates_v0.csv", index=False)

# potential gain on BBC lines: mass UNKNOWN now, but a top-1 HIGH candidate has a matching portion
m = pd.read_csv(ROOT.parent / "a1" / "A1 3" / "data" / "processed" / "ingredient_mentions.csv",
                usecols=["raw_phrase", "ingredient_canonical"])
gain, total, unknown = Counter(), 0, 0
for r in m.itertuples(index=False):
    total += 1
    p = parse_line(r.raw_phrase)
    z = normalize(p, locale="UK")
    if z.mass_g["status"] != "UNKNOWN":
        continue
    unknown += 1
    ports = portion_lookup.get(r.ingredient_canonical)
    if not ports:
        gain["no_verified_candidate_portion"] += 1
        continue
    unit = p.unit_key
    hit = any((u == unit and unit is not None) for u, _, _ in ports) or \
          (unit is None and p.size and any(sz == p.size for _, sz, _ in ports)) or \
          (unit is None and p.kind in ("NUMBER", "RANGE", "FRACTION", "MIXED") and
           any(u is None and sz in ("medium", None) for u, sz, _ in ports))
    gain["portion_match" if hit else "portion_but_unit_mismatch"] += 1

bands = cw[cw["rank"].isin([1]) | cw["band"].eq("NO_CANDIDATE")]["band"].value_counts().to_dict()
freq_w = cw[cw["rank"].isin([1]) | cw["band"].eq("NO_CANDIDATE")].groupby("band")["recipe_freq"].sum().to_dict()
lines = ["# FDC SR Legacy crosswalk v0 (candidates only — human verification required)", "",
         f"- ING concepts: {len(reg):,}; top-1 band counts: {bands}",
         f"- recipe-frequency-weighted top-1 bands: {freq_w}",
         f"- portion candidates (from top-1 HIGH): {len(prow):,} rows over {len(portion_lookup):,} concepts",
         f"- BBC mention lines: {total:,}; mass UNKNOWN now: {unknown:,} ({unknown/total:.1%})",
         f"- of those, a verified crosswalk would give a matching sourced portion for: {gain['portion_match']:,} "
         f"({gain['portion_match']/total:.1%} of all lines); unit mismatch: {gain['portion_but_unit_mismatch']:,}; "
         f"no candidate portion: {gain['no_verified_candidate_portion']:,}",
         "- Until a human ticks `human_decision`, grams stay UNKNOWN (Q6). Verified links -> POR- records (Q1)."]
(ROOT / "reports" / "fdc_crosswalk_v0.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
