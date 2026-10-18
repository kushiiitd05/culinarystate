#!/usr/bin/env python3
"""Select a stratified pilot batch from the A1 BBC corpus and write blank gold templates (text only).

  /opt/anaconda3/bin/python tools/make_gold_batch.py --n 20 --name pilot_20 --seed 7
Templates contain recipe text + empty spans/events; entity/concept = "TODO". No labels are pre-filled.
Templates and gold files hold third-party text -> annotation/gold/ is git-ignored (D-007).
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT.parent / "a1" / "A1 3" / "data" / "raw" / "recipes_raw.jsonl"
STRATA = {
    "reserve_split": r"\b(reserv|set aside|remaining|the rest|divide|half the)\b",
    "drain_discard": r"\b(drain|strain|discard)\b",
    "baking": r"\b(bake|oven)\b",
    "indian": None,
    "simple": None,
    "multi_component": r"\b(for the (sauce|dressing|topping|filling|marinade))\b",
}

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=20)
ap.add_argument("--name", default="pilot_20")
ap.add_argument("--seed", type=int, default=7)
a = ap.parse_args()

A1_IDS = {}
with (ROOT.parent / "a1" / "A1 3" / "data" / "processed" / "recipes_processed.jsonl").open() as fh:
    for line in fh:
        row = json.loads(line)
        A1_IDS[row["source_url"]] = row["recipe_id"]          # A1 ids are NOT raw line numbers

recs = []
with RAW.open() as fh:
    for line in fh:
        r = json.loads(line)
        if r["source_url"] not in A1_IDS:
            continue
        steps, ings = r.get("instruction_steps_raw") or [], r.get("ingredient_phrases_raw") or []
        if not steps or not ings or len(ings) > 14 or len(steps) > 8:
            continue
        text = " ".join(steps).lower() + " " + " ".join(ings).lower()
        tags = [k for k, pat in STRATA.items() if pat and re.search(pat, text)]
        if (r.get("cuisine_raw") or "").lower() == "indian":
            tags.append("indian")
        if len(steps) <= 3 and len(ings) <= 6:
            tags.append("simple")
        recs.append({"recipe_id": A1_IDS[r["source_url"]], "title": r["title"], "url": r["source_url"], "tags": tags,
                     "ings": ings, "steps": steps})

rng = random.Random(a.seed)
per = max(1, a.n // len(STRATA))
chosen, seen = [], set()
for stratum in STRATA:
    pool = [x for x in recs if stratum in x["tags"] and x["recipe_id"] not in seen]
    for x in rng.sample(pool, min(per, len(pool))):
        chosen.append({**x, "stratum": stratum})
        seen.add(x["recipe_id"])
rest = [x for x in recs if x["recipe_id"] not in seen]
for x in rng.sample(rest, max(0, a.n - len(chosen))):
    chosen.append({**x, "stratum": "random"})

batch_dir = ROOT / "annotation" / "batches"
batch_dir.mkdir(parents=True, exist_ok=True)
pd.DataFrame([{k: x[k] for k in ("recipe_id", "stratum", "title", "url")} | {"tags": "|".join(x["tags"])}
              for x in chosen]).to_csv(batch_dir / f"{a.name}.csv", index=False)
gold = ROOT / "annotation" / "gold" / "templates"
gold.mkdir(parents=True, exist_ok=True)
for x in chosen:
    doc = {"schema_version": "gold-1.0", "recipe_id": x["recipe_id"], "source_ref": x["url"],
           "annotator": "Kush", "status": "DRAFT", "locale": "UK",
           "ingredient_lines": [{"line_index": i, "text": t, "spans": [], "entity": "TODO", "concept": "TODO"}
                                for i, t in enumerate(x["ings"])],
           "steps": [{"step_index": i, "text": t, "spans": [], "events": [], "coref": []}
                     for i, t in enumerate(x["steps"])],
           "unknowns": [], "notes": ""}
    (gold / f"{x['recipe_id']}.TEMPLATE.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print(pd.read_csv(batch_dir / f"{a.name}.csv")[["recipe_id", "stratum", "title"]].to_string())
