#!/usr/bin/env python
"""Draft the D5 S1 (current state) and S2 (next action) blocks. AI DRAFT gold for human review (prereg §1, §3).

Recipes: Wikibooks and Gutenberg only (D-003), >= 4 steps, <= 3,000 characters, ranked by sha256(seed || recipe_id).
Cut after a seeded step. S1 gold = ingredients heated so far (Rung A lots through heat events); S2 gold = first action
after the cut. Writes benchmark/d5/d5_draft_S_v1.csv (ids, questions, gold; no recipe text) and the review context
annotation/d5_review/d5_S_context_v1.jsonl (recipe steps; git-ignored). Refuses to overwrite.

    python tools/d5_draft_s.py
"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.decision.pipeline import load_lexicon  # noqa: E402
from culinarystate.evaluation import d5_state as DS  # noqa: E402
from culinarystate.extraction.rung_a_measure import seeded_sample  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.recipes.ledgers import LOCALE  # noqa: E402

_spec = importlib.util.spec_from_file_location("_t17", ROOT / "tools/step17b_rung_a_dryrun.py")
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)

SEED = "d5-bench-2026-11-08"
PER_BLOCK = 20  # 15 enter; 5 ranked reserves
OUT = ROOT / "benchmark/d5/d5_draft_S_v1.csv"
CTX = ROOT / "annotation/d5_review/d5_S_context_v1.jsonl"
COLS = ["qid", "block", "rank_in_block", "recipe_id", "source_family", "n_steps", "cut_after_step", "question",
        "gold_ingredient_ids", "gold_ingredients", "gold_next_action", "gold_next_process_id", "gold_next_step_index",
        "drafted_by", "status"]
Q1 = "I have just finished step {k} of this recipe. Which ingredients have been heated so far?"
Q2 = "I have just finished step {k} of this recipe. What do I do next?"


def _steps(r):
    return [s.strip() for s in r.get("steps") or [] if isinstance(s, str) and s.strip()]


def main() -> int:
    if OUT.exists() or CTX.exists():
        sys.exit("refusing to overwrite an existing draft")
    lex, family = load_lexicon(LedgerStore())
    recs = (r for r in T17.corpus_records(["WIKIBOOKS", "GUTENBERG_SEGMENT"], ROOT)
            if len(_steps(r)) >= 4 and len("\n".join(_steps(r))) <= 3000)
    ranked = seeded_sample(recs, SEED, 400)
    rows, ctx = [], []
    for r in ranked:
        steps, rid = _steps(r), r["recipe_id"]
        k = DS.seeded_cut(rid, len(steps), seed=SEED)
        loc = LOCALE.get(r.get("source_family"))
        s1 = sum(x["block"] == "S1" for x in rows)
        s2 = sum(x["block"] == "S2" for x in rows)
        if s1 >= PER_BLOCK and s2 >= PER_BLOCK:
            break
        base = {"recipe_id": rid, "source_family": r["source_family"], "n_steps": len(steps), "cut_after_step": k,
                "drafted_by": "AI_AGENT_S171", "status": "DRAFT_FOR_REVIEW"}
        if s1 < PER_BLOCK:
            heated = sorted(DS.heated_ingredient_ids(DS.graph("\n".join(steps[:k]), loc), family))
            if heated:
                rows.append({**base, "qid": f"D5-S1-{s1 + 1:03d}", "block": "S1", "rank_in_block": s1 + 1,
                             "question": Q1.format(k=k), "gold_ingredient_ids": "|".join(heated),
                             "gold_ingredients": "|".join(lex.ing_names.get(i, i) for i in heated)})
                ctx.append({"qid": rows[-1]["qid"], "recipe_id": rid, "title": r.get("title"), "steps": steps})
                continue
        if s2 < PER_BLOCK:
            na = DS.next_action(steps, k, loc)
            if na and na["process_id"]:
                rows.append({**base, "qid": f"D5-S2-{s2 + 1:03d}", "block": "S2", "rank_in_block": s2 + 1,
                             "question": Q2.format(k=k), "gold_next_action": na["action"],
                             "gold_next_process_id": na["process_id"], "gold_next_step_index": na["step_index"] + 1})
                ctx.append({"qid": rows[-1]["qid"], "recipe_id": rid, "title": r.get("title"), "steps": steps})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    CTX.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows({**{c: "" for c in COLS}, **x} for x in rows)
    with open(CTX, "x", encoding="utf-8") as fh:
        fh.writelines(json.dumps(c, ensure_ascii=False) + "\n" for c in ctx)
    print({b: sum(x["block"] == b for x in rows) for b in ("S1", "S2")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
