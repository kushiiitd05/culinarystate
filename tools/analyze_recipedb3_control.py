#!/usr/bin/env python3
"""S118C: aggregate the RecipeDB3 control runs (theirs / clean / clean+SIZE) and recompute split leakage locally.

  /opt/anaconda3/bin/python tools/analyze_recipedb3_control.py   # reads reports/ner/_raw/*.json, writes reports/ner/recipedb3_control_summary.json
Leakage is recomputed by replaying each seed's split (same sklearn calls and cleaning as gpu/ner_recipedb3/repro.py) so it does not
depend on which fields an older run wrote.
"""
import glob
import hashlib
import json
import re
import statistics as st
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import GroupShuffleSplit, train_test_split

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "reports" / "ner" / "_raw"
DATA = ROOT / "data" / "external" / "recipedb3_ner" / "Ingredient_Annotated_Dataset.csv"
NUM = re.compile(r"\d+(?:[./]\d+)?|[¼½¾⅓⅔⅛]")


def fam(s):
    return re.sub(r"\s+", " ", NUM.sub("#", s.lower())).strip()


def cleaned():
    df = pd.read_csv(DATA).dropna()
    df = df[df.sentence.astype(str).str.strip() != ""].reset_index(drop=True)
    df["tags"] = df.tags.astype(str)
    df = df[df.apply(lambda r: len(r.sentence.split()) == len(r.tags.split()), axis=1)].reset_index(drop=True)
    df["fam"] = df.sentence.map(fam)
    return df


def split(df, protocol, seed):
    if protocol == "theirs":
        tr, te = train_test_split(df, test_size=0.20, random_state=seed)
        return tr, te, te
    g = GroupShuffleSplit(1, test_size=0.2, random_state=seed)
    a, b = next(g.split(df, groups=df.fam))
    train, rest = df.iloc[a], df.iloc[b].reset_index(drop=True)
    g2 = GroupShuffleSplit(1, test_size=0.5, random_state=seed)
    d, t = next(g2.split(rest, groups=rest.fam))
    return train, rest.iloc[d], rest.iloc[t]


def ci(v):
    n = len(v)
    if n < 2:
        return [None, None]
    h = stats.t.ppf(0.975, n - 1) * st.stdev(v) / n ** 0.5
    return [round(st.mean(v) - h, 4), round(st.mean(v) + h, 4)]


def main():
    df = cleaned()
    runs = []
    for f in sorted(glob.glob(str(RAW / "*seed*.json"))):
        d = json.load(open(f))
        prot = d["protocol"] + ("_size" if d.get("with_size") else "")
        base = "clean" if d["protocol"] == "clean" else "theirs"
        tr, dev, te = split(df, base, d["seed"])
        trs = set(tr.sentence)
        row = {"protocol": prot, "seed": d["seed"], "selection": d["selection_split"], "best_epoch": d["best_epoch"],
               "n": [d["n_train"], d["n_dev"], d["n_test"]], "test_macro_best": d["test_at_best"]["macro_f1"], "test_micro_best": d["test_at_best"]["micro_f1"],
               "test_macro_last": d["test_at_last"]["macro_f1"], "test_micro_last": d["test_at_last"]["micro_f1"],
               "per_label_best": {k: round(v["f1"], 4) for k, v in d["test_at_best"].get("per_label", {}).items()},
               "exact_duplicate_frac_test": round(float(te.sentence.isin(trs).mean()), 4), "masked_family_leak_frac_test": round(float(te.fam.isin(set(tr.fam)).mean()), 4),
               "leaked_micro": (d.get("test_at_best_leaked") or {}).get("micro_f1"), "nonleaked_micro": (d.get("test_at_best_non_leaked") or {}).get("micro_f1"),
               "leaked_macro": (d.get("test_at_best_leaked") or {}).get("macro_f1"), "nonleaked_macro": (d.get("test_at_best_non_leaked") or {}).get("macro_f1"),
               "runtime_s": d.get("runtime_s"), "gpu": d.get("gpu", "A100 (not logged by this run)"), "model": d["model"],
               "split_hash": hashlib.sha256(",".join(map(str, sorted(te.index))).encode()).hexdigest()[:16]}
        runs.append(row)
    out = {"dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(), "code_sha256_repro": hashlib.sha256((ROOT / "gpu/ner_recipedb3/repro.py").read_bytes()).hexdigest(),
           "runs": runs, "agg": {}}
    for prot in sorted({r["protocol"] for r in runs}):
        rs = [r for r in runs if r["protocol"] == prot]
        a = {}
        for k in ("test_macro_best", "test_micro_best", "test_macro_last", "test_micro_last", "leaked_micro", "nonleaked_micro", "nonleaked_macro",
                  "exact_duplicate_frac_test", "masked_family_leak_frac_test"):
            v = [r[k] for r in rs if r[k] is not None]
            if v:
                a[k] = {"n": len(v), "mean": round(st.mean(v), 4), "sd": round(st.stdev(v), 4) if len(v) > 1 else None, "ci95": ci(v)}
        labs = sorted({k for r in rs for k in r["per_label_best"]})
        a["per_label_mean_f1"] = {l: round(st.mean(r["per_label_best"][l] for r in rs if l in r["per_label_best"]), 4) for l in labs}
        out["agg"][prot] = a
    T = {r["seed"]: r for r in runs if r["protocol"] == "theirs"}
    C = {r["seed"]: r for r in runs if r["protocol"] == "clean"}
    if T and C:
        t, c = [r["test_macro_best"] for r in T.values()], [r["test_macro_best"] for r in C.values()]
        out["theirs_vs_clean_macro"] = {"delta": round(st.mean(t) - st.mean(c), 4), "welch_p": round(float(stats.ttest_ind(t, c, equal_var=False).pvalue), 4)}
    CS = {r["seed"]: r for r in runs if r["protocol"] == "clean_size"}
    common = sorted(set(CS) & set(C))
    if common:
        dm = [CS[s]["test_macro_best"] - C[s]["test_macro_best"] for s in common]
        out["size_effect_paired_seeds"] = {"seeds": common, "macro_delta_mean": round(st.mean(dm), 4), "per_seed": [round(x, 4) for x in dm],
                                           "note": "macro averages over 7 labels with SIZE vs 6 without, so compare per-label F1 and micro too"}
    (ROOT / "reports" / "ner" / "recipedb3_control_summary.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
