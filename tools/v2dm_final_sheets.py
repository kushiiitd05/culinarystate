#!/usr/bin/env python3
"""CulinaryLinkDecision final set: blinded annotation sheets (blank), candidate pool = union of BGE top-5, E5 top-5, cross-encoder pick, Tev, Nimble, CD-L2 (3 seeds), CD-L1 (3 seeds) picks, shuffled; no system names, no strata in the sheet.
Identical copies for Kush and Parv. Key (provenance + stratum) stays in pool_key_FINAL_DO_NOT_SHARE.json."""
import csv
import hashlib
import json
import string
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

RAW, V = ROOT / "reports/ner_v2/_dm_raw", ROOT / "reports/ner_v2/_final_sys"
st = LedgerStore()
name, alias = {}, defaultdict(list)
for i in st.all_latest("ING"):
    if i["status"] == "ACTIVE":
        name[i["id"]] = i["canonical_name"]
for a in st.all_latest("ALIAS"):
    if a["status"] == "ACTIVE" and a.get("ingredient_id") in name:
        alias[a["ingredient_id"]].append(a["normalized"])
frame = {json.loads(l)["mention"]: json.loads(l) for l in open(ROOT / "features/v2dm/final_link_frame.jsonl")}
tasks = [json.loads(l) for l in open(ROOT / "features/v2dm/final_tasks_k10.jsonl")]
e5 = json.load(open(RAW / "final_export_e5-large-v2.json"))["scores"]
ce = {json.loads(l)["id"]: json.loads(l)["scores"] for l in open(V / "final_ce_k10.jsonl")}
K5 = list(string.ascii_uppercase[:5])


def dm(path):
    out = {}
    for l in open(path):
        r = json.loads(l)
        if r["resp"]:
            p = r["resp"]["answers"]["link"]["probabilities"]
            out[r["id"]] = K5.index(max(K5, key=lambda k: p.get(k, 0)))
    return out


tev, nim = dm(V / "final_tev4b_k5.jsonl"), dm(V / "final_nimble_k5.jsonl")
stu = {f"CDL{lam}_s{s}": {r["id"]: r["forced"] for r in json.load(open(V / f"final_stu_lam{lam}_s{s}.json"))["results"]} for lam in ("1.0", "0") for s in (1, 2, 3)}
rows, key = [], {}
for t in tasks:
    src = defaultdict(list)
    for c in t["cands"][:5]:
        src[c["id"]].append("BGE_top5")
    for c, _ in e5[t["mention"]][:5]:
        src[c].append("E5_top5")
    src[t["cands"][max(range(len(ce[t["id"]])), key=lambda i: ce[t["id"]][i])]["id"]].append("CE_pick")
    if t["id"] in tev:
        src[t["cands"][tev[t["id"]]]["id"]].append("Tev_pick")
    if t["id"] in nim:
        src[t["cands"][nim[t["id"]]]["id"]].append("Nimble_pick")
    for k, v in stu.items():
        src[v[t["id"]]].append(k + "_pick")
    order = sorted(src, key=lambda c: hashlib.sha256(("final|" + t["id"] + c).encode()).hexdigest())
    fr = frame[t["mention"]]
    key[t["id"]] = {"stratum": t["stratum"], "split": fr["split"], "pool": {c: src[c] for c in order}}
    rows.append({"item_id": t["id"], "dataset": fr["dataset"], "mention": t["mention"], "context_line": fr["context"],
                 **{f"cand_{k + 1}": f"{c} | {name.get(c, c)}" + (f" (also: {', '.join([a for a in alias[c] if a != name.get(c)][:3])})" if [a for a in alias[c] if a != name.get(c)] else "") for k, c in enumerate(order)}, "_n": len(order)})
ncols = max(r["_n"] for r in rows)
cols = ["item_id", "dataset", "mention", "context_line"] + [f"cand_{k + 1}" for k in range(ncols)]
rev = ["decision(MATCH:<n> | PARENT:<n> | NONE | AMBIGUOUS)", "if_NONE_ingredient_name", "acceptable_concepts(for AMBIGUOUS: ING-ids separated by ; or the word NONE)", "confidence(1-3)", "note"]
out = ROOT / "annotation/gold/final_link_set"
out.mkdir(parents=True, exist_ok=True)
for who in ("Kush", "Parv"):
    with open(out / f"{who}_ALL_{len(rows)}items_BLINDED.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols + rev, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({**r, **{k: "" for k in rev}})
json.dump(key, open(out / "pool_key_FINAL_DO_NOT_SHARE.json", "w"))
print(len(rows), "items; max candidates", ncols, "mean", round(sum(r["_n"] for r in rows) / len(rows), 1))
