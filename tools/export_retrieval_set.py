#!/usr/bin/env python3
"""DEL-4 silver retrieval dev set: evidence texts + templated questions with cell-level relevance.

  /opt/anaconda3/bin/python tools/export_retrieval_set.py
Relevance unit = (matrix name, primary process id, target name) over ACTIVE retention-bearing EVD. One question per
sampled cell (≥ 2 rows, ≤ 600 cells, stratified by source family, seed 20261018), worded from a template that does
not copy the row's process string. SILVER: it ranks lexical vs dense vs hybrid retrieval on dev; the human benchmark
(D-008) is the evaluation of record. Writes data/interim/retrieval/{evd_texts,silver_queries}.jsonl (local).
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.retrieval.retriever import evd_text  # noqa: E402

OUT = ROOT / "data" / "interim" / "retrieval"
SEED, MAX_CELLS = 20261018, 600
PAST = {"boil": "boiled", "steam": "steamed", "fry": "fried", "roast": "roasted", "bake": "baked", "stew": "stewed",
        "simmer": "simmered", "microwave": "microwaved", "braise": "braised", "grill": "grilled", "broil": "grilled",
        "pan-fry": "pan-fried", "deep-fry": "deep-fried", "blanch": "blanched", "saute": "sautéed", "can": "canned",
        "dry": "dried", "freeze": "frozen", "store": "stored", "reheat": "reheated", "brown": "browned"}


def main() -> None:
    st = LedgerStore()
    cond = {c["id"]: c for c in st.all_latest("COND")}
    pname = {p["id"]: p["canonical_name"] for p in st.all_latest("PROC")}
    evd = [e for e in st.all_latest("EVD") if e["status"] == "ACTIVE"]
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "evd_texts.jsonl").open("w") as fh:
        for e in evd:
            fh.write(json.dumps({"id": e["id"], "text": evd_text(e, cond.get(e["process"].get("condition_id") or ""))}) + "\n")
    cells = defaultdict(list)
    for e in evd:
        if "retention_factor" in e["derived"] and e["process"].get("process_id"):
            cells[(e["matrix"]["raw_name"].lower(), e["process"]["process_id"], e["target"]["raw_name"].lower(),
                   e["source_family_id"])].append(e["id"])
    by_fam = defaultdict(list)
    for k, ids in cells.items():
        if len(ids) >= 2:
            by_fam[k[3]].append(k)
    rng = random.Random(SEED)
    per = MAX_CELLS // max(1, len(by_fam))
    picked = [k for f in sorted(by_fam) for k in rng.sample(sorted(by_fam[f]), min(per, len(by_fam[f])))]
    rel = defaultdict(set)                                   # relevance pools across families for the same cell
    for (m, p, t, _), ids in cells.items():
        rel[(m, p, t)] |= set(ids)
    with (OUT / "silver_queries.jsonl").open("w") as fh:
        for i, (m, p, t, fam) in enumerate(picked):
            proc = pname.get(p, p)
            q = f"How much {t.split(',')[0]} is left in {m.split(',')[0]} after it is {PAST.get(proc, proc)}?"
            fh.write(json.dumps({"qid": f"SQ-{i:04d}", "question": q, "matrix": m, "process_id": p, "target": t,
                                 "family": fam, "relevant": sorted(rel[(m, p, t)])}) + "\n")
    print(f"evd texts {len(evd):,}; cells ≥2 rows {sum(len(v) for v in by_fam.values()):,}; queries {len(picked)} "
          f"by family {{{', '.join(f'{f}: {min(per, len(v))}' for f, v in sorted(by_fam.items()))}}}")


if __name__ == "__main__":
    main()
