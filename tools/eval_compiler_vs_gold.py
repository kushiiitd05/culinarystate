#!/usr/bin/env python3
"""First text -> events -> state evaluation of the rule compiler against the pilot_20 Gold-v1 (S107). No tuning.

  /opt/anaconda3/bin/python tools/eval_compiler_vs_gold.py
Gold = annotation/gold/pilot_20_adjudicated (AI-assisted, human-reviewed; NOT independent, NOT a test set; D-016/D-017).
Cascade (SSOT 245.14 oracle decomposition):
  P  predicted        compile_recipe(raw text, ING registry names)           -> replay
  O1 oracle concepts  compile_recipe(raw text, names = gold concepts)         -> replay      (isolates ingredient linking)
  O2 gold Adds        gold Add events + predicted step events (relabelled)    -> replay      (isolates step-event construction)
  G  gold events      replay(gold)                                            -> sanity ceiling = 1.0
Entity labels are aligned (scoring.align_entities) so naming choices are not errors. Outputs reports/del3/compiler_vs_gold_v1.{json,md}.
"""
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.gold import to_events  # noqa: E402
from culinarystate.scoring.metrics import tuple_prf  # noqa: E402
from culinarystate.scoring.state_metrics import aligned_state_scores, align_entities, relabel  # noqa: E402
from culinarystate.state_graph.engine import Add, replay  # noqa: E402
from culinarystate.state_graph.rule_compiler import compile_recipe  # noqa: E402

GOLD = ROOT / "annotation" / "gold" / "pilot_20_adjudicated"
LEVELS = ("P", "O1", "O2", "G")


def etuple_loose(ev):
    d = ev.__dict__ if hasattr(ev, "__dict__") else {}
    tgt = getattr(ev, "target", None) or getattr(ev, "source", None) or getattr(ev, "reserved", None) or \
        "+".join(getattr(ev, "inputs", ()) or ()) or getattr(ev, "label", "")
    return (type(ev).__name__, tgt)


def event_scores(g_events, p_events):
    mapping = align_entities(g_events, p_events)
    pr = relabel(p_events, mapping)
    ga = [etuple_loose(e) for e in g_events if not isinstance(e, Add)]
    pa = [etuple_loose(e) for e in pr if not isinstance(e, Add)]
    gt = [e[0] for e in ga]
    pt = [e[0] for e in pa]
    return {"loose": tuple_prf(ga, pa).as_dict(), "type_only": tuple_prf(Counter(gt).elements(), Counter(pt).elements()).as_dict(),
            "gold_types": dict(Counter(gt)), "pred_types": dict(Counter(pt))}


def build(level, doc, lines, steps, reg_names):
    g = to_events(doc)
    if level == "G":
        return g
    if level == "P":
        return compile_recipe(lines, steps, reg_names)
    if level == "O1":
        return compile_recipe(lines, steps, {li["concept"] for li in doc["ingredient_lines"] if li["concept"] != "UNKNOWN"})
    p = compile_recipe(lines, steps, reg_names)                                   # O2
    p_adds = [e.label for e in p if isinstance(e, Add)]
    g_adds = [e for e in g if isinstance(e, Add)]
    mp = dict(zip(p_adds, [e.label for e in g_adds]))
    return g_adds + relabel([e for e in p if not isinstance(e, Add)], mp)


def boot(vals, n=1000, seed=7):
    rng = random.Random(seed)
    m = sorted(sum(rng.choice(vals) for _ in vals) / len(vals) for _ in range(n))
    return [round(m[int(0.025 * n)], 4), round(m[int(0.975 * n)], 4)]


def main():
    reg = {r["canonical_name"] for r in csv.DictReader((ROOT / "registry" / "ingredients" / "ingredient_registry_v1.csv").open())}
    docs = [json.loads(p.read_text()) for p in sorted(GOLD.glob("*.ADJUDICATED.json"))]
    man = {r["recipe_id"]: r["stratum"] for r in csv.DictReader((ROOT / "annotation" / "gold" / "pilot_20_manifest.csv").open())}
    res = {lv: [] for lv in LEVELS}
    for d in docs:
        lines, steps = [x["text"] for x in d["ingredient_lines"]], [x["text"] for x in d["steps"]]
        g = to_events(d)
        for lv in LEVELS:
            p = build(lv, d, lines, steps, reg)
            s = aligned_state_scores(g, p)
            ev = event_scores(g, p)
            res[lv].append({"recipe_id": d["recipe_id"], "stratum": man[d["recipe_id"]], "n_gold_events": len(g),
                            "n_pred_events": len(p), "state_field_accuracy": s["state_field_accuracy"] or 0.0,
                            "alive_f1": s["alive_entities"]["f1"], "merge_split_f1": s["merge_split_f1"]["f1"],
                            "relation_f1": s["all_edges"]["overall"]["f1"] if s["all_edges"] else 0.0,
                            "event_loose_f1": ev["loose"]["f1"], "event_type_f1": ev["type_only"]["f1"],
                            "replay_issues": len(s["pred_issues"]), "gold_types": ev["gold_types"], "pred_types": ev["pred_types"]})
    keys = ("state_field_accuracy", "alive_f1", "merge_split_f1", "relation_f1", "event_loose_f1", "event_type_f1")
    summary = {lv: {k: {"mean": round(sum(r[k] for r in rows) / len(rows), 4), "ci95": boot([r[k] for r in rows])} for k in keys}
               | {"recipes_with_replay_issues": sum(r["replay_issues"] > 0 for r in rows)} for lv, rows in res.items()}
    conf = {lv: {"gold": Counter(), "pred": Counter()} for lv in ("P",)}
    for r in res["P"]:
        conf["P"]["gold"].update(r["gold_types"])
        conf["P"]["pred"].update(r["pred_types"])
    by_stratum = {}
    for r in res["P"]:
        by_stratum.setdefault(r["stratum"], []).append(r["state_field_accuracy"])
    out = {"n_recipes": len(docs), "gold": "pilot_20 Gold-v1 (AI-assisted, human-reviewed; not independent; not a test set)",
           "summary": summary, "event_types_P": {k: dict(v) for k, v in conf["P"].items()},
           "state_field_accuracy_by_stratum_P": {k: round(sum(v) / len(v), 4) for k, v in by_stratum.items()},
           "per_recipe": res}
    (ROOT / "reports" / "del3" / "compiler_vs_gold_v1.json").write_text(json.dumps(out, indent=1))
    for lv in LEVELS:
        print(lv, {k: summary[lv][k]["mean"] for k in keys}, "replay-issue recipes", summary[lv]["recipes_with_replay_issues"])
    print("types P gold:", dict(conf["P"]["gold"]), "\n        pred:", dict(conf["P"]["pred"]))
    print("by stratum:", out["state_field_accuracy_by_stratum_P"])


if __name__ == "__main__":
    main()
