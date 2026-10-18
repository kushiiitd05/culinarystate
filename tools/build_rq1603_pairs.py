#!/usr/bin/env python3
"""EXP-000006 (RQ16-03 pilot): query / evidence pairs with typed scientific hard negatives (SSOT §241.4). SILVER.

  /opt/anaconda3/bin/python tools/build_rq1603_pairs.py [--n 800]
Positive = a row of the query's (ingredient, process, target) cell. Negatives, one each when they exist:
WRONG_PROCESS (same food + target), WRONG_TARGET (same food + process), RELATED_FOOD (same process + target, food
related in the R4 graph incl. siblings), EASY (random row). Writes data/interim/rq1603/pairs.jsonl (local: rows carry
ledger text only, no third-party prose).
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.retrieval.food_graph import FoodGraph  # noqa: E402
from culinarystate.retrieval.retriever import evd_text  # noqa: E402
from culinarystate.vocab.off import parse as parse_off  # noqa: E402

OFF = ROOT / "data" / "raw" / "off" / "ingredients_a1ce1d36.txt"
OUT = ROOT / "data" / "interim" / "rq1603"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=800)
    a = ap.parse_args()
    st = LedgerStore()
    cond = {c["id"]: c for c in st.all_latest("COND")}
    pname = {p["id"]: p["canonical_name"] for p in st.all_latest("PROC")}
    ings = [i for i in st.all_latest("ING") if i["status"] == "ACTIVE"]
    iname = {i["id"]: i["canonical_name"] for i in ings}
    graph = FoodGraph(ings, {k: e.parents for k, e in parse_off(OFF).items()})
    evd = [e for e in st.all_latest("EVD") if e["status"] == "ACTIVE" and e["matrix"].get("ingredient_id")
           and e["process"].get("process_id")]
    cell, by_ft, by_fp, by_pt = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    for e in evd:
        f, p, t = e["matrix"]["ingredient_id"], e["process"]["process_id"], e["target"]["raw_name"].lower()
        cell[(f, p, t)].append(e)
        by_ft[(f, t)].append(e)
        by_fp[(f, p)].append(e)
        by_pt[(p, t)].append(e)
    rng = random.Random(7)
    keys = rng.sample(sorted(cell), min(a.n, len(cell)))
    OUT.mkdir(parents=True, exist_ok=True)
    counts = defaultdict(int)
    with (OUT / "pairs.jsonl").open("w") as fh:
        for qi, (f, p, t) in enumerate(keys):
            pos = rng.choice(cell[(f, p, t)])
            rel = graph.related(f, siblings=True)
            pools = {"WRONG_PROCESS": [e for e in by_ft[(f, t)] if e["process"]["process_id"] != p],
                     "WRONG_TARGET": [e for e in by_fp[(f, p)] if e["target"]["raw_name"].lower() != t],
                     "RELATED_FOOD": [e for e in by_pt[(p, t)] if e["matrix"]["ingredient_id"] in rel],
                     "EASY": [e for e in (rng.choice(evd) for _ in range(5)) if e["matrix"]["ingredient_id"] != f]}
            cands = [("POSITIVE", pos)] + [(k, rng.choice(v)) for k, v in pools.items() if v]
            for k, _ in cands:
                counts[k] += 1
            q = {"qid": f"Q{qi:04d}", "question": f"How does {pname.get(p, p)} affect {t} in {iname.get(f, f)}?",
                 "ingredient_id": f, "ingredient_name": iname.get(f), "process_id": p, "target": t,
                 "relations": sorted(rel.items()), "parents": sorted(graph.related(f).keys() & set(
                     next(i for i in ings if i["id"] == f).get("parent_ids") or ())),
                 "candidates": [{"evd_id": e["id"], "type": k, "related_kind": rel.get(e["matrix"]["ingredient_id"]),
                                 "text": evd_text(e, cond.get(e["process"].get("condition_id") or ""))}
                                for k, e in cands]}
            fh.write(json.dumps(q, ensure_ascii=False) + "\n")
    print(f"{len(keys)} queries; candidates by type: {dict(counts)}")


if __name__ == "__main__":
    main()
