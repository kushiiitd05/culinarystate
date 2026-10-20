#!/usr/bin/env python3
"""Convert the Food.com joint review sheet (AI proposals, batch-approved by Kush in chat) into gold-1.0 files.

  /opt/anaconda3/bin/python tools/convert_foodcom_sheet.py [--sheet PATH]

Reuses the mechanical rules of tools/convert_ai_review.py. Writes annotation/gold/foodcom_ai_assisted/{Kush,Parv}/<id>.<who>.json and
conversion_log.csv. The blank independent bundles (Kush_all_20.json / Parv_all_20.json, frozen hashes) are never touched. Provenance is
AI_ASSISTED_HUMAN_REVIEWED, NOT independent: both sets come from the same AI proposal, so Kush-vs-Parv agreement is non-informative.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))
import convert_ai_review as car  # noqa: E402
from culinarystate.annotation.gold import validate_gold, to_events  # noqa: E402
from culinarystate.state_graph.engine import replay  # noqa: E402

D = ROOT / "annotation" / "gold" / "evidence_first_expansion"
OUT = ROOT / "annotation" / "gold" / "foodcom_ai_assisted"
SHEET = Path.home() / "Downloads" / "Kush_Parv_joint_review_sheet.csv"
PROVENANCE = ("AI_ASSISTED_HUMAN_REVIEWED: proposal drafted by an AI reviewer (Pass 1, schema-mechanical for hard cases); Kush stated in chat "
              "that he reviewed it all and accepts it (batch-level approval, no row-level remarks in Kush_Rem/Parv_Rem); "
              "{parv}. Converted by Claude to gold-1.0 (tools/convert_foodcom_sheet.py, log: conversion_log.csv). "
              "NOT an independent annotation; Kush and Parv sets share one AI proposal, agreement is non-informative.")


def rebuild(rows, template):
    """Sheet rows -> the combined-review dict shape that convert_ai_review.convert expects."""
    by = {}
    for r in rows:
        by.setdefault(r["recipe_id"], []).append(r)
    out = []
    for rec in template["recipes"]:
        rid, rs = rec["recipe_id"], by[rec["recipe_id"]]
        ings = sorted((r for r in rs if r["section"] == "INGREDIENT"), key=lambda r: int(r["item_index"]))
        steps = sorted((r for r in rs if r["section"] == "STEP"), key=lambda r: int(r["item_index"]))
        chk = next(r for r in rs if r["section"] == "RECIPE_CHECK")
        assert [r["source_text"] for r in ings] == [l["text"] for l in rec["ingredient_lines"]], rid
        assert [r["source_text"] for r in steps] == [s["text"] for s in rec["steps"]], rid
        x = {"recipe_id": rid, "source_ref": rec["source_ref"], "locale": rec.get("locale"), "unknowns": [],
             "final_state_summary": json.loads(chk["proposed_annotation"]).get("final_state_summary"),
             "review_note": chk["source_text"], "ingredient_lines": [], "steps": []}
        for r in ings:
            p = json.loads(r["proposed_annotation"])
            x["ingredient_lines"].append({"line_index": int(r["item_index"]), "text": r["source_text"], "spans": p["spans"],
                                          "entity": p["entity"], "concept_candidate": p.get("concept_candidate")})
        for r in steps:
            p = json.loads(r["proposed_annotation"])
            for j, e in enumerate(p["events"]):
                e.setdefault("event_id", f"E{j}")
            x["steps"].append({"step_index": int(r["item_index"]), "text": r["source_text"], "spans": p["spans"],
                               "events": p["events"], "coref": p.get("coref", [])})
        out.append(x)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default=str(SHEET))
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.sheet, encoding="utf-8-sig")))
    template = json.loads((D / "Kush_all_20.json").read_text())
    names = car.registry()
    summary = []
    for x in rebuild(rows, template):
        doc, fs, rn = car.convert(x, names)
        rid = doc["recipe_id"]
        tpl = next(r for r in template["recipes"] if r["recipe_id"] == rid)
        assert [l["text"] for l in doc["ingredient_lines"]] == [l["text"] for l in tpl["ingredient_lines"]]
        for who in ("Kush", "Parv"):
            e = json.loads(json.dumps(doc))
            e["annotator"] = who
            parv = ("Parv's approval relayed by Kush, not recorded by Parv directly" if who == "Parv" else "Kush is the reviewer of record")
            e["notes"] = (f"[{car.skipped.get(rid, 0)} proposed events could not be converted] " + PROVENANCE.format(parv=parv)
                          + f" Proposed final state: {fs}. Reviewer check: {rn}").strip()
            errs = validate_gold({**e, "status": "DONE"})
            iss = [] if errs else list(replay(to_events(e)).issues)
            e["status"] = "DONE" if not errs and not iss else "DRAFT"
            p = OUT / who / f"{rid}.{who}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n")
            summary.append((rid, who, e["status"], errs[:1], iss[:2]))
    with (OUT / "conversion_log.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["recipe_id", "where", "kind", "detail"])
        w.writeheader()
        w.writerows(car.log)
    for s in summary:
        if s[1] == "Kush":
            print(s)
    from collections import Counter
    print(Counter(s[2] for s in summary), Counter(r["kind"] for r in car.log))


if __name__ == "__main__":
    main()
