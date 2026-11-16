#!/usr/bin/env python
"""Draft the D5 P1/P2/P3 and C blocks (reports/del5/d5_benchmark_preregistration_DRAFT.md §1). AI DRAFT for review.

Writes benchmark/d5/d5_draft_PC_v1.csv (our own question text + ids + gold; no third-party text) and refuses to
overwrite. Gold = stratum from exact or parent-ingredient EVD rows with a measured retention value; humans review.

    python tools/d5_draft_pc.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.decision.pipeline import load_lexicon  # noqa: E402
from culinarystate.evaluation import d5_draft as D5  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

SEED = "d5-bench-2026-11-08"
OUT = ROOT / "benchmark/d5/d5_draft_PC_v1.csv"
TARGETS = {"vitamin C": ("SVAR-000009", "SVAR-000215"), "thiamin": ("SVAR-000010",), "riboflavin": ("SVAR-000011",),
           "folate": ("SVAR-000014", "SVAR-000016", "SVAR-000212"), "iron": ("SVAR-000002",),
           "polyphenols": ("SVAR-000050",)}
PROCS = {"boil": ("boiled", "PROC-000019"), "steam": ("steamed", "PROC-000022"), "deep fry": ("deep-fried", "PROC-000011"),
         "fry": ("pan-fried", "PROC-000013"), "bake": ("baked", "PROC-000001"), "stew": ("stewed", "PROC-000025")}
QUOTA = {"DIRECT": 15, "SIMILAR_ONLY": 15, "NONE": 15}  # 10 enter per block; 5 ranked reserves (prereg §3)
COLS = ["qid", "block", "rank_in_block", "question", "ingredient_id", "food", "process", "process_id", "process_2", "process_id_2",
        "target", "target_svars", "stratum", "gold_mode", "gold_evd_ids", "gold_retention_range", "gold_evd_ids_2",
        "gold_retention_range_2", "drafted_by", "status"]


def main() -> int:
    if OUT.exists():
        sys.exit("refusing to overwrite an existing draft")
    st = LedgerStore()
    lex, _ = load_lexicon(st)
    vals, pairs = {}, {t: {} for t in TARGETS}
    for r in st.all_latest("EVD"):
        rf = (r.get("derived") or {}).get("retention_factor") or {}
        ing, proc = (r.get("matrix") or {}).get("ingredient_id"), (r.get("process") or {}).get("process_id")
        if r["status"] != "ACTIVE" or rf.get("status") != "MEASURED" or not ing or not proc:
            continue
        for t, svars in TARGETS.items():
            if r["target"]["state_variable_id"] in svars:
                pairs[t].setdefault((ing, proc), []).append(r["id"])
                v = rf.get("value")
                vals[r["id"]] = None if v is None else (v / 100.0 if rf.get("unit") == "%" else v)  # fraction
    known = {ing for t in pairs for ing, _ in pairs[t]}
    pool = sorted(known | {c for c, ps in lex.parents.items() if set(ps) & known})
    cells = []
    for t in TARGETS:
        for verb, (past, pid) in PROCS.items():
            for ing in pool:
                s, ids = D5.stratum(ing, pid, pairs[t], lex.parents)
                cells.append({"cell": f"{ing}|{pid}|{t}", "stratum": s, "ingredient_id": ing, "target": t,
                              "verb": verb, "past": past, "process_id": pid, "ids": ids})
    picked = D5.seeded_pick(cells, seed=SEED, quota=QUOTA, max_per_ingredient=2)

    def rng(ids):
        v = sorted(float(vals[i]) for i in ids if vals.get(i) is not None)
        return f"{v[0]:.2f}-{v[-1]:.2f} fraction retained (n={len(v)})" if v else ""
    rows = []
    for n, c in enumerate(picked, 1):
        block = {"DIRECT": "P1", "SIMILAR_ONLY": "P2", "NONE": "P3"}[c["stratum"]]
        food = lex.ing_names.get(c["ingredient_id"], c["ingredient_id"])
        rows.append({"qid": f"D5-{block}-{n:03d}", "block": block, "rank_in_block": (n - 1) % 15 + 1,
                     "question": D5.phrase_effect(n, food, c["past"], c["verb"], c["target"]),
                     "ingredient_id": c["ingredient_id"], "food": food, "process": c["verb"],
                     "process_id": c["process_id"], "target": c["target"], "target_svars": "|".join(TARGETS[c["target"]]),
                     "stratum": c["stratum"], "gold_mode": D5.GOLD_MODE[c["stratum"]], "gold_evd_ids": "|".join(c["ids"]),
                     "gold_retention_range": rng(c["ids"])})
    direct = {(c["ingredient_id"], c["target"]): [] for c in cells if c["stratum"] == "DIRECT"}
    for c in cells:
        if c["stratum"] == "DIRECT":
            direct[(c["ingredient_id"], c["target"])].append(c)
    comp = [{"cell": f"{k[0]}|{k[1]}", "stratum": "DIRECT", "ingredient_id": k[0], "pair": v[:2]}
            for k, v in sorted(direct.items()) if len(v) >= 2]
    for n, c in enumerate(D5.seeded_pick(comp, seed=SEED + "-C", quota={"DIRECT": 15}, max_per_ingredient=1), 1):
        a, b = c["pair"]
        food = lex.ing_names.get(c["ingredient_id"], c["ingredient_id"])
        rows.append({"qid": f"D5-C-{n:03d}", "block": "C", "rank_in_block": n, "question": D5.phrase_compare(n, food, (a["verb"], b["verb"]),
                                                                                         a["target"]),
                     "ingredient_id": c["ingredient_id"], "food": food, "process": a["verb"], "process_id": a["process_id"],
                     "process_2": b["verb"], "process_id_2": b["process_id"], "target": a["target"],
                     "target_svars": "|".join(TARGETS[a["target"]]), "stratum": "DIRECT", "gold_mode": "COMPARE",
                     "gold_evd_ids": "|".join(a["ids"]), "gold_retention_range": rng(a["ids"]),
                     "gold_evd_ids_2": "|".join(b["ids"]), "gold_retention_range_2": rng(b["ids"])})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({**{k: "" for k in COLS}, **r, "drafted_by": "AI_AGENT_S171", "status": "DRAFT_FOR_REVIEW"})
    print({b: sum(r["block"] == b for r in rows) for b in ("P1", "P2", "P3", "C")}, "pool", len(pool), "cells", len(cells))
    return 0


if __name__ == "__main__":
    sys.exit(main())
