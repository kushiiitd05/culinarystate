#!/usr/bin/env python3
"""Fresh linker set step 2: pooled-candidate annotation sheets (blank, human-only), segregated by stratum, identical copies for Kush and Parv. Candidates = union of BGE top-5, E5 top-5, cross-encoder pick, Tev1-4B pick, Nimble pick
(shuffled by hash, source hidden; source membership kept in pool_key.json, not given to annotators). Output local-only: annotation/gold/fresh_linker_set/."""
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import string  # noqa: E402

from culinarystate.ledgers.store import LedgerStore  # noqa: E402

RAW = ROOT / "reports/ner_v2/_dm_raw"
st = LedgerStore()
name, alias = {}, defaultdict(list)
for i in st.all_latest("ING"):
    if i["status"] == "ACTIVE":
        name[i["id"]] = i["canonical_name"]
for a in st.all_latest("ALIAS"):
    if a["status"] == "ACTIVE" and a.get("ingredient_id") in name:
        alias[a["ingredient_id"]].append(a["normalized"])
frame = {json.loads(l)["mention"]: json.loads(l) for l in open(ROOT / "features/v2dm/fresh_link_frame.jsonl")}
tasks = [json.loads(l) for l in open(ROOT / "features/v2dm/fresh_tasks_k10.jsonl")]
e5 = json.load(open(RAW / "fresh_export_e5-large-v2.json"))["scores"]
ce = {json.loads(l)["id"]: json.loads(l)["scores"] for l in open(RAW / "ce_fresh_k10.jsonl")}


def dm(path):
    out = {}
    keys = list(string.ascii_uppercase[:5])
    for l in open(path):
        r = json.loads(l)
        if r["resp"]:
            a = r["resp"]["answers"]["link"]
            p = a["probabilities"]
            out[r["id"]] = keys.index(max(keys, key=lambda k: p.get(k, 0)))
    return out


tev, nim = dm(RAW / "dm_fresh_tev4b_k5.jsonl"), dm(RAW / "dm_fresh_nimble_k5.jsonl")
rows, key = [], {}
for t in tasks:
    src = defaultdict(list)
    for c in t["cands"][:5]:
        src[c["id"]].append("BGE_top5")
    for c, _ in e5[t["mention"]][:5]:
        src[c].append("E5_top5")
    if t["id"] in ce:
        src[t["cands"][max(range(len(ce[t["id"]])), key=lambda i: ce[t["id"]][i])]["id"]].append("CE_pick")
    if t["id"] in tev:
        src[t["cands"][tev[t["id"]]]["id"]].append("Tev_pick")
    if t["id"] in nim:
        src[t["cands"][nim[t["id"]]]["id"]].append("Nimble_pick")
    order = sorted(src, key=lambda c: hashlib.sha256((t["id"] + c).encode()).hexdigest())
    fr = frame[t["mention"]]
    key[t["id"]] = {c: src[c] for c in order}
    rows.append({"item_id": t["id"], "stratum": t["stratum"], "dataset": fr["dataset"], "mention": t["mention"], "context_line": fr["context"],
                 **{f"cand_{k + 1}": (f"{c} | {name.get(c, c)}" + (f" (also: {', '.join([a for a in alias[c] if a != name.get(c)][:3])})" if [a for a in alias[c] if a != name.get(c)] else "")) for k, c in enumerate(order)}, "_n": len(order)})
ncols = max(r["_n"] for r in rows)
cols = ["item_id", "stratum", "dataset", "mention", "context_line"] + [f"cand_{k + 1}" for k in range(ncols)]
rev = ["decision(MATCH:<n> | PARENT:<n> | NONE | AMBIGUOUS)", "if_NONE_ingredient_name", "if_AMBIGUOUS_readings", "confidence(1-3)", "note"]
out = ROOT / "annotation/gold/fresh_linker_set"
out.mkdir(parents=True, exist_ok=True)
by = defaultdict(list)
for r in rows:
    by[r["stratum"].split("_")[0]].append(r)
for s, rs in by.items():
    for who in ("Kush", "Parv"):
        with open(out / f"{who}_{s}_{len(rs)}items.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols + rev, extrasaction="ignore")
            w.writeheader()
            for r in rs:
                w.writerow({**r, **{k: "" for k in rev}})
json.dump(key, open(out / "pool_key_DO_NOT_SHARE.json", "w"))
print({s: len(rs) for s, rs in by.items()}, "max candidates per item", ncols, "mean", round(sum(r["_n"] for r in rows) / len(rows), 1), "| files", len(list(out.glob("*.csv"))))
