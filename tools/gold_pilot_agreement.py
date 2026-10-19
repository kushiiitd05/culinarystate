#!/usr/bin/env python3
"""Kush vs Parv agreement on pilot_20 (S101) with an optional deterministic subset (S102). REFUSES to run until every
selected recipe has a DONE + valid file from BOTH annotators; unfinished non-selected recipes are never read or required.

  /opt/anaconda3/bin/python tools/gold_pilot_agreement.py                       # all 20 -> pilot_20_agreement.json / _disagreements.csv
  /opt/anaconda3/bin/python tools/gold_pilot_agreement.py --calibration         # the frozen 7 -> pilot_20_calibration7_*
  /opt/anaconda3/bin/python tools/gold_pilot_agreement.py --only R001,R002 [--tag name]   # any subset -> pilot_20_<tag>_*
Exit 2 = BLOCKED_HUMAN. Writes metrics, a categorised disagreement CSV and per-category rates with a mechanical handbook
gate flag (rate > 20% of the relevant units). Does not adjudicate and never edits an annotator file.
"""
import argparse
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
from culinarystate.scoring.state_metrics import final_fields  # noqa: E402
from culinarystate.state_graph.engine import replay  # noqa: E402

GOLD = ROOT / "annotation" / "gold"
GATE_RATE = 0.20
SCALARS = ("concept_agreement", "unknown_disagreement_rate")
F1_KEYS = ("process_link_f1", "event_f1_strict", "event_f1_loose", "structural_relation_f1", "intermediate_entity_f1",
           "alive_entity_f1")


def select_ids(manifest_ids: list[str], only: str | None, calibration: bool, gold: Path) -> list[str]:
    if calibration:
        cal = [r["recipe_id"] for r in csv.DictReader((gold / "pilot_7_calibration_manifest.csv").open())]
        return [i for i in manifest_ids if i in cal]
    if not only:
        return manifest_ids
    want = [x.strip() for x in only.split(",") if x.strip()]
    unknown = [x for x in want if x not in manifest_ids]
    if unknown:
        raise SystemExit(f"--only ids not in the frozen manifest: {unknown}")
    return [i for i in manifest_ids if i in want]


def load_done(gold: Path, ids: list[str]):
    docs, blocked = {}, []
    for who in ("Kush", "Parv"):
        for rid in ids:
            p = gold / "pilot_20" / who / f"{rid}.{who}.json"
            d = json.loads(p.read_text()) if p.exists() else None
            if not d or d["status"] != "DONE":
                blocked.append(f"{who}:{rid}:{d['status'] if d else 'MISSING'}")
                continue
            errs = validate_gold(d) or [f"replay: {x}" for x in replay(to_events(d)).issues]
            if errs:
                blocked.append(f"{who}:{rid}:INVALID:{errs[0]}")
                continue
            docs[(who, rid)] = d
    return docs, blocked


def denominators(docs: dict, ids: list[str]) -> dict:
    n = Counter()
    for rid in ids:
        a, b = docs[("Kush", rid)], docs[("Parv", rid)]
        units = list(a["ingredient_lines"]) + list(a["steps"]) + list(b["ingredient_lines"]) + list(b["steps"])
        n["spans"] += sum(len(u["spans"]) for u in units)
        n["events"] += sum(len(s["events"]) for d in (a, b) for s in d["steps"])
        n["lines"] += len(a["ingredient_lines"])
        n["coref"] += sum(len(s.get("coref", [])) for d in (a, b) for s in d["steps"])
        n["state"] += len(final_fields(replay(to_events(a)))) + len(final_fields(replay(to_events(b))))
    return n


CAT_DENOM = {"boundary": "spans", "entity_type": "spans", "quantity": "spans", "canonical_identity": "lines",
             "event_type": "events", "event_argument": "events", "intermediate_identity": "events", "coref": "coref",
             "final_state": "state"}


def main(argv=None, gold: Path = GOLD) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--calibration", action="store_true")
    ap.add_argument("--tag", default=None)
    a = ap.parse_args(argv)
    manifest = [r["recipe_id"] for r in csv.DictReader((gold / "pilot_20_manifest.csv").open())]
    ids = select_ids(manifest, a.only, a.calibration, gold)
    tag = "calibration7" if a.calibration else (a.tag or ("partial" if a.only else None))
    docs, blocked = load_done(gold, ids)
    if blocked:
        print(f"BLOCKED_HUMAN: {len(blocked)} of {2 * len(ids)} required annotator files are not DONE+valid "
              f"({len(ids)} recipes selected)")
        print("  e.g.", "; ".join(blocked[:5]))
        return 2
    per, rows, pairs = [], [], []
    for rid in ids:
        ka, pa = docs[("Kush", rid)], docs[("Parv", rid)]
        per.append(recipe_metrics(ka, pa))
        rows += disagreements(ka, pa, _align(ka, pa))
        for ua, ub in list(zip(ka["ingredient_lines"], pa["ingredient_lines"])) + list(zip(ka["steps"], pa["steps"])):
            pairs.append(([(s["start"], s["end"], s["label"]) for s in ua["spans"]],
                          [(s["start"], s["end"], s["label"]) for s in ub["spans"]]))
    den = denominators(docs, ids)
    by_cat = {c: sum(r["category"] == c for r in rows) for c in CATEGORIES}
    rates = {c: (round(by_cat[c] / den[CAT_DENOM[c]], 4) if den[CAT_DENOM[c]] else None) for c in CATEGORIES}
    flagged = [c for c, r in rates.items() if r is not None and r > GATE_RATE]
    macro = {k: round(sum(m[k] for m in per if m[k] is not None) / max(1, sum(m[k] is not None for m in per)), 4)
             for k in SCALARS}
    macro |= {k: round(sum(m[k]["f1"] for m in per) / len(per), 4) for k in F1_KEYS}
    macro["relation_f1_all_macro"] = round(sum(m["relation"]["overall"]["f1"] for m in per) / len(per), 4)
    macro["coref_b_cubed_f1_macro"] = round(sum((m["coref_b_cubed"]["f1"] if m["coref_b_cubed"] else 1.0) for m in per)
                                            / len(per), 4)
    macro["state_field_agreement_macro"] = round(sum(m["state_field_agreement"]["agree"] or 0 for m in per) / len(per), 4)
    macro["replay_consistent_fraction"] = round(sum(m["replay_consistent"]["ok"] for m in per) / len(per), 4)
    pooled = {"recipes": ids, "spans_exact": corpus_span_scores(pairs, "exact"),
              "spans_relaxed": corpus_span_scores(pairs, "relaxed"), "macro_over_recipes": macro,
              "disagreements_by_category": by_cat, "disagreement_rate_by_category": rates,
              "denominators": dict(den), "handbook_gate": {"threshold": GATE_RATE, "flagged_categories": flagged,
                                                           "verdict": "HANDBOOK_REVISION_REQUIRED" if flagged else
                                                           "NO_MECHANICAL_FLAG (read the table before CALIBRATION_PASS)"},
              "disagreements_by_recipe": dict(Counter(r["recipe_id"] for r in rows))}
    stem = f"pilot_20_{tag}" if tag else "pilot_20"
    (gold / f"{stem}_agreement.json").write_text(json.dumps({"pooled": pooled, "per_recipe": per}, indent=1, default=str))
    with (gold / f"{stem}_disagreements.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["recipe_id", "category", "where", "field", "kush", "parv", "adjudicated",
                                           "rationale", "handbook_rule"])
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(by_cat), f"total {len(rows)}; rates {json.dumps(rates)}")
    print("gate:", pooled["handbook_gate"]["verdict"], flagged)
    return 0


if __name__ == "__main__":
    sys.exit(main())
