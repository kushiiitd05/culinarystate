#!/usr/bin/env python3
"""S119 E0 aggregation (laptop): reads pulled gpu/ner_bench runs, builds the model table, CRF paired tests (Holm), Pareto view.

  /opt/anaconda3/bin/python tools/aggregate_e0.py tasteset [runs_dir]     # writes reports/ner/_e0_<dataset>.json (+ prints a markdown table)
Run JSONs: <dataset>__<model>[_crf]__seed<k>.json and .pred.json (spans per split). Per-doc exact counts are recomputed from the frozen split + preds,
so paired grouped bootstrap resamples TEST DOCUMENTS (the independence unit for TASTEset; masked-family docs for RecipeDB3).
"""
import glob
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from culinarystate.ner import benchmark as B  # noqa: E402
from culinarystate.ner.router import holm, paired_grouped_bootstrap  # noqa: E402
import freeze_ner_benchmark as F  # noqa: E402
import pandas as pd  # noqa: E402


def test_docs(ds):
    sp = json.loads((ROOT / "benchmark/ner/splits" / f"{ds}_split_v1.json").read_text())["indices"]["test"]
    if ds == "tasteset":
        return sp, F.docs_taste(pd.read_csv(F.TASTE), sp)
    df, _ = F.load_rdb3()
    return sp, F.docs_rdb3(df, sp)


def doc_counts(gold, pred, labels):
    g = {tuple(x) for x in gold if x[2] in labels}
    p = {tuple(x) for x in pred if x[2] in labels}
    return len(g & p), len(p - g), len(g - p)


def f1(tp, fp, fn):
    return 2 * tp / (2 * tp + fp + fn) if tp else 0.0


def main():
    ds = sys.argv[1]
    runs_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "reports" / "ner" / "_raw_e0"
    labels = B.VIEWS[{"tasteset": "tasteset_native", "recipedb3": "recipedb3_published"}[ds]]
    _, docs = test_docs(ds)
    rows, per = defaultdict(list), defaultdict(dict)
    for f in sorted(glob.glob(str(runs_dir / f"{ds}__*__seed*.json"))):
        if f.endswith(".pred.json"):
            continue
        d = json.load(open(f))
        key = d["model"].split("/")[-1] + ("+CRF" if d["crf"] and not d.get("fusion") else "") + (f"+{d['knowledge']}" if d.get("knowledge", "K0") != "K0" else "") + (f"+fusion-{d['fusion']}" if d.get("fusion") else "")
        pred = json.load(open(f.replace(".json", ".pred.json")))["test"]
        c = np.array([doc_counts(g, p, labels) for (_, g), p in zip(docs, pred)])
        per[key][d["seed"]] = c
        t = d["test"]
        rows[key].append({"micro": t["exact"]["micro"]["f1"], "macro": t["exact"]["macro_f1"], "relaxed": t["relaxed"]["micro"]["f1"], "boundary": t["boundary_error_rate"],
                          "unseen": t["strata"]["unseen_alias"]["f1"], "tail": t["strata"]["tail"]["f1"], "head": t["strata"]["head"]["f1"],
                          "min": d["minutes"], "gb": d["peak_gpu_gb"], "per_label": {k: v["f1"] for k, v in t["exact"]["per_label"].items()}})
    agg = {}
    for k, rs in rows.items():
        m = lambda f: (round(st.mean(r[f] for r in rs), 4), round(st.stdev([r[f] for r in rs]), 4) if len(rs) > 1 else None)
        agg[k] = {"n_seeds": len(rs), **{f: m(f) for f in ("micro", "macro", "relaxed", "boundary", "unseen", "tail", "head", "min", "gb")}}
    B0 = "deberta-base"
    PAIRS = [(f"{B0}+CRF", B0, "E0 CRF vs softmax"), (f"{B0}+CRF+K1", f"{B0}+CRF", "K1 vs K0"), (f"{B0}+CRF+K2", f"{B0}+CRF", "K2 vs K0"),
             (f"{B0}+CRF+K3", f"{B0}+CRF", "K3 vs K0"), (f"{B0}+fusion-concat", f"{B0}+CRF", "E3 concat vs E0 CRF"),
             (f"{B0}+fusion-gated", f"{B0}+CRF", "E4 gated vs E0 CRF"), (f"{B0}+fusion-gated", f"{B0}+fusion-concat", "E4 gated vs E3 concat"),
             (f"{B0}+fusion-gated", f"{B0}+fusion-zero", "metadata ON vs OFF (same architecture)"),
             (f"{B0}+fusion-zero+span0.5", f"{B0}+fusion-zero", "span head vs none (CRF decodes)"),
             ("deberta-v3-large+CRF", "deberta-v3-large", "v3-large CRF vs softmax")]
    tests, names = {}, []
    for cand, base, label in PAIRS:
        seeds = sorted(set(per.get(cand, {})) & set(per.get(base, {})))
        if len(seeds) < 2:
            continue
        a = np.array([per[cand][s] for s in seeds])        # [S, D, 3]
        b = np.array([per[base][s] for s in seeds])
        rng = np.random.RandomState(20261018)
        deltas = []
        for _ in range(1000):
            ix = rng.randint(0, a.shape[1], a.shape[1])
            deltas.append(np.mean([f1(*a[s][ix].sum(0)) - f1(*b[s][ix].sum(0)) for s in range(len(seeds))]))
        deltas = np.sort(deltas)
        pt = np.mean([f1(*a[s].sum(0)) - f1(*b[s].sum(0)) for s in range(len(seeds))])
        p = max(2 * min((deltas <= 0).mean(), (deltas >= 0).mean()), 1e-3)
        wins = sum(f1(*a[s].sum(0)) > f1(*b[s].sum(0)) for s in range(len(seeds)))
        key = f"{label}"
        tests[key] = {"cand": cand, "base": base, "seeds": seeds, "delta_micro": round(float(pt), 4), "ci95": [round(float(deltas[25]), 4), round(float(deltas[974]), 4)], "p": round(float(p), 4),
                      "seeds_won": f"{wins}/{len(seeds)}", "delta_unseen_f1": round(agg[cand]["unseen"][0] - agg[base]["unseen"][0], 4),
                      "delta_macro": round(agg[cand]["macro"][0] - agg[base]["macro"][0], 4)}
        names.append(key)
    ok = holm([tests[n]["p"] for n in names]) if names else []
    for n, o in zip(names, ok):
        t = tests[n]
        t["holm_significant"] = bool(o)
        t["promoted"] = bool(o and t["delta_micro"] >= 0.003 and t["ci95"][0] > 0 and int(t["seeds_won"].split("/")[0]) >= 4 and t["delta_unseen_f1"] >= -0.005 and t["delta_macro"] >= -0.003)
    out = {"dataset": ds, "agg": agg, "crf_vs_softmax": tests}
    (ROOT / "reports" / "ner" / f"_e0_{ds}.json").write_text(json.dumps(out, indent=1) + "\n")
    print("| model | seeds | exact micro | exact macro | relaxed | boundary err | unseen F1 | tail F1 | min | GB |\n|---|---|---|---|---|---|---|---|---|---|")
    for k, a_ in sorted(agg.items(), key=lambda kv: -kv[1]["micro"][0]):
        pm = lambda t: f"{t[0]:.4f}" + (f" ± {t[1]:.4f}" if t[1] is not None else "")
        print(f"| {k} | {a_['n_seeds']} | {pm(a_['micro'])} | {pm(a_['macro'])} | {pm(a_['relaxed'])} | {pm(a_['boundary'])} | {pm(a_['unseen'])} | {pm(a_['tail'])} | {a_['min'][0]} | {a_['gb'][0]} |")
    print(json.dumps(tests, indent=1))


if __name__ == "__main__":
    main()
