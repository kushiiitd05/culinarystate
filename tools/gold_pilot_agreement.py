#!/usr/bin/env python3
"""S101 step 6: Kush vs Parv agreement on pilot_20. REFUSES to run until both annotators have 20 DONE files.

  /opt/anaconda3/bin/python tools/gold_pilot_agreement.py
Reads annotation/gold/pilot_20/{Kush,Parv}/<id>.<Name>.json; validates each; writes annotation/gold/pilot_20_agreement.json
(per-recipe + pooled metrics) and annotation/gold/pilot_20_disagreements.csv (one row per disagreement, 9 categories, empty
adjudication columns). Does not adjudicate and never edits either annotator's file.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.gold import to_events, validate_gold  # noqa: E402
from culinarystate.annotation.pilot_agreement import CATEGORIES, _align, disagreements, recipe_metrics  # noqa: E402
from culinarystate.scoring.metrics import corpus_span_scores  # noqa: E402
from culinarystate.state_graph.engine import replay  # noqa: E402

GOLD = ROOT / "annotation" / "gold"


def main() -> int:
    ids = [r["recipe_id"] for r in csv.DictReader((GOLD / "pilot_20_manifest.csv").open())]
    docs, blocked = {}, []
    for who in ("Kush", "Parv"):
        for rid in ids:
            p = GOLD / "pilot_20" / who / f"{rid}.{who}.json"
            d = json.loads(p.read_text()) if p.exists() else None
            if not d or d["status"] != "DONE":
                blocked.append(f"{who}:{rid}:{d['status'] if d else 'MISSING'}")
                continue
            errs = validate_gold(d) or [f"replay: {x}" for x in replay(to_events(d)).issues]
            if errs:
                blocked.append(f"{who}:{rid}:INVALID:{errs[0]}")
                continue
            docs[(who, rid)] = d
    if blocked:
        print(f"BLOCKED_HUMAN: {len(blocked)} of {2 * len(ids)} annotator files are not DONE+valid")
        print("  e.g.", "; ".join(blocked[:5]))
        return 2
    per, rows = [], []
    for rid in ids:
        a, b = docs[("Kush", rid)], docs[("Parv", rid)]
        per.append(recipe_metrics(a, b))
        rows += disagreements(a, b, _align(a, b))
    pairs = []
    for rid in ids:
        a, b = docs[("Kush", rid)], docs[("Parv", rid)]
        for ua, ub in list(zip(a["ingredient_lines"], b["ingredient_lines"])) + list(zip(a["steps"], b["steps"])):
            pairs.append(([(s["start"], s["end"], s["label"]) for s in ua["spans"]],
                          [(s["start"], s["end"], s["label"]) for s in ub["spans"]]))
    pooled = {"spans_exact": corpus_span_scores(pairs, "exact"), "spans_relaxed": corpus_span_scores(pairs, "relaxed"),
              "disagreements_by_category": {c: sum(r["category"] == c for r in rows) for c in CATEGORIES},
              "disagreements_by_recipe": dict(Counter(r["recipe_id"] for r in rows))}
    (GOLD / "pilot_20_agreement.json").write_text(json.dumps({"pooled": pooled, "per_recipe": per}, indent=1, default=str))
    with (GOLD / "pilot_20_disagreements.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["recipe_id", "category", "where", "field", "kush", "parv", "adjudicated",
                                           "rationale", "handbook_rule"])
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(pooled["disagreements_by_category"]), f"total {len(rows)}")
    print("span F1 exact", pooled["spans_exact"]["micro"]["f1"], "relaxed", pooled["spans_relaxed"]["micro"]["f1"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
