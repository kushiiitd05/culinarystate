#!/usr/bin/env python3
"""DESCRIPTIVE ONLY. Why did the DEV n=61 / fresh-441 Tev advantage over BGE not appear on the 850 set? Compares composition and per-slice accuracy of the two sealed human sets. Nothing here is a tuning input."""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import v2dm_fresh_score as F  # noqa: E402
import v2dm_final_score as N  # noqa: E402

out = {}
# ---- 441 (fresh) ----
G1 = pd.read_csv(ROOT / "annotation/gold/fresh_linker_set/FRESH_LINKER_GOLD_FINAL.csv", dtype=str, keep_default_na=False)
S1 = F.load_systems(G1)
T1 = {r["mention"]: r for r in map(json.loads, open(ROOT / "features/v2dm/fresh_tasks_k10.jsonl"))}
# ---- 850 (final) ----
G2 = pd.read_csv(N.GOLD, dtype=str, keep_default_na=False)
S2 = N.load(G2)
T2 = {r["id"]: r for r in map(json.loads, open(ROOT / "features/v2dm/final_tasks_k10.jsonl"))}


def rows441():
    for _, g in G1.iterrows():
        t = T1[g["mention"]]
        yield {"id": t["id"], "cls": g["final_class"], "con": g["final_concept"], "stratum": g["stratum"].split("_")[0], "t": t, "bge": S1["BGE"][t["id"]]["pick"], "tev": S1["Tev1-4B"][t["id"]]["pick"]}


def rows850():
    for _, g in G2.iterrows():
        t = T2[g.item_id]
        yield {"id": g.item_id, "cls": g.final_class, "con": g.final_concept, "ids": set(x for x in g.final_acceptable_set.split(";") if x) - {"NONE"}, "stratum": g.stratum, "t": t,
               "bge": S2["BGE"][g.item_id]["pick"], "tev": S2["Tev1-4B"][g.item_id]["pick"], "cd": [S2[f"CD-L2_s{s}"][g.item_id]["pick"] for s in (1, 2, 3)], "mention": g.mention}


A, B = list(rows441()), list(rows850())
for nm, R in (("fresh441", A), ("final850", B)):
    o = {}
    o["class_counts"] = dict(Counter(r["cls"] for r in R))
    o["NONE_prevalence"] = round(sum(r["cls"] == "NONE" for r in R) / len(R), 3)
    o["stratum_counts"] = dict(Counter(r["stratum"] for r in R))
    m = [r for r in R if r["cls"] == "MATCH"]
    o["MATCH_n"] = len(m)
    o["MATCH_only_acc"] = {"BGE": round(np.mean([r["bge"] == r["con"] for r in m]), 3), "Tev": round(np.mean([r["tev"] == r["con"] for r in m]), 3)}
    if nm == "final850":
        o["MATCH_only_acc"]["CD-L2"] = round(float(np.mean([[c == r["con"] for c in r["cd"]] for r in m])), 3)
    # candidate-set difficulty: BGE top-1 exact (score >= 0.999), margin top1-top2, gold rank in BGE list
    sc = [[x["score"] for x in r["t"]["cands"]] for r in m]
    o["MATCH_BGE_top1_exact_share(score>=0.999)"] = round(float(np.mean([s[0] >= 0.999 for s in sc])), 3)
    o["MATCH_BGE_median_top1_score"] = round(float(np.median([s[0] for s in sc])), 3)
    o["MATCH_BGE_median_margin"] = round(float(np.median([s[0] - s[1] for s in sc])), 3)
    rk = [next((k for k, x in enumerate(r["t"]["cands"]) if x["id"] == r["con"]), 99) for r in m]
    o["MATCH_gold_BGE_rank_share"] = {"1": round(float(np.mean([k == 0 for k in rk])), 3), "2-5": round(float(np.mean([1 <= k < 5 for k in rk])), 3), "6-10": round(float(np.mean([5 <= k < 10 for k in rk])), 3), "absent": round(float(np.mean([k == 99 for k in rk])), 3)}
    o["MATCH_mention_tokens_ge3_share"] = round(float(np.mean([len(r["t"]["mention"].split()) >= 3 for r in m])), 3)
    # BGE-wrong items: where Tev rescues vs breaks
    bw = [r for r in m if r["bge"] != r["con"]]
    tw = [r for r in m if r["tev"] != r["con"]]
    o["MATCH_Tev_rescues(BGE wrong, Tev right)"] = sum(r["tev"] == r["con"] for r in bw)
    o["MATCH_Tev_breaks(BGE right, Tev wrong)"] = sum(r["bge"] == r["con"] for r in tw)
    o["MATCH_per_stratum_BGE_vs_Tev"] = {s: {"n": sum(r["stratum"] == s for r in m), "BGE": round(float(np.mean([r["bge"] == r["con"] for r in m if r["stratum"] == s])), 3), "Tev": round(float(np.mean([r["tev"] == r["con"] for r in m if r["stratum"] == s])), 3)} for s in sorted({r["stratum"] for r in m})}
    if nm == "final850":
        am = [r for r in R if r["cls"] == "AMBIGUOUS" and r["ids"]]
        o["AMBIGUOUS_with_ids_n"] = len(am)
        o["AMBIGUOUS_set_size_median"] = int(np.median([len(r["ids"]) for r in am]))
        o["AMBIGUOUS_acc"] = {"BGE": round(float(np.mean([r["bge"] in r["ids"] for r in am])), 3), "Tev": round(float(np.mean([r["tev"] in r["ids"] for r in am])), 3),
                              "CD-L2": round(float(np.mean([[c in r["ids"] for c in r["cd"]] for r in am])), 3)}
        o["AMBIGUOUS_share_of_ViewA_strict"] = round(len(am) / (len(am) + len(m)), 3)
        # teacher / student agreement on picks
        o["pick_agreement"] = {"Tev==BGE": round(float(np.mean([r["tev"] == r["bge"] for r in R])), 3), "CD-L2(s1)==Tev": round(float(np.mean([r["cd"][0] == r["tev"] for r in R])), 3), "CD-L2(s1)==BGE": round(float(np.mean([r["cd"][0] == r["bge"] for r in R])), 3)}
        # Tev - BGE with and without ambiguous
        o["ViewA_strict_Tev_minus_BGE_MATCH_only"] = round(o["MATCH_only_acc"]["Tev"] - o["MATCH_only_acc"]["BGE"], 3)
    out[nm] = o
Path(ROOT / "reports/ner_v2/_link_d3_descriptive.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str))
