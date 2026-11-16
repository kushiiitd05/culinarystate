#!/usr/bin/env python
"""S178 (T8-C04-R2): gold-independence audit of the D5 S1/S2 draft. Counts only; refuses to overwrite.

For each of the 40 drafted S questions it recomputes the engine outputs at the cut and builds the B1/B2/B4 contexts in
three modes: legacy (S173: all steps retrievable, B4 prints "Heated so far"), independent_minimal (S178: steps up to the
cut; B4 prints ingredients used + last action) and independent_primitives (same, plus the engine's action list). It counts,
per rung and mode, the contexts that share an engine output with the gold or leak an answer field / a post-cut step, the
provenance of the gold (all ENGINE_DRAFT), a text-only heat-verb plausibility check, how often the printed action list
still lets a plain heat-verb rule rebuild the S1 gold, and how often the ingredients-used line equals the gold set (the
residual circularity that blind-first human gold removes).

The embedder is a deterministic hashed bag of words (no model on this server): the retrieval part is a lexical proxy,
NON_CITABLE; the state-block and pre-cut results do not depend on it. Recipe text is read to run the engine and is not
written anywhere.

    python tools/s178_h1_gold_independence.py [--out reports/s178/h1_gold_independence_d5_draft_v2.json]

S178 FIX-EVAL (SCI-B E1): ``--out`` writes a new version (the tool still refuses to overwrite); the provenance block now
comes from ``h1_independence@0.2`` (evidence-based HUMAN_BLIND, ENGINE_DRAFT_KEPT reasons, refusals).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evaluation import h1_independence as I  # noqa: E402
from culinarystate.evaluation import h1_rungs as H  # noqa: E402
from culinarystate.evaluation import split_registry as SR  # noqa: E402
from culinarystate.recipes import corpus  # noqa: E402
from culinarystate.recipes.ledgers import LOCALE  # noqa: E402

OUT = ROOT / "reports/s178/h1_gold_independence_d5_draft.json"
S_DRAFT = ROOT / "benchmark/d5/d5_draft_S_v1.csv"
DIM = 512
Q = {"S1": "I have just finished step {k} of this recipe. Which ingredients have been heated so far?",
     "S2": "I have just finished step {k} of this recipe. What do I do next?"}


def hash_embed(texts):
    out = []
    for t in texts:
        v = [0.0] * DIM
        for w in re.findall(r"[a-z]+", t.lower()):
            v[int(hashlib.sha256(w.encode()).hexdigest()[:8], 16) % DIM] += 1.0
        out.append(v)
    return out


def steps_of(r) -> list[str]:
    return [s.strip() for s in r.get("steps") or [] if isinstance(s, str) and s.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    out_path = Path(ap.parse_args(argv).out)
    if out_path.exists():
        sys.exit(f"refusing to overwrite {out_path}")
    with open(S_DRAFT, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    want = {r["recipe_id"] for r in rows}
    recipes = {r["recipe_id"]: r for r in corpus.iter_rec_corpora(families=("WIKIBOOKS", "GUTENBERG_SEGMENT"))
               if r["recipe_id"] in want}
    fam = H._family()
    modes = {"legacy": {}, "independent_minimal": {"pre_cut_only": True, "state_view": "MINIMAL"},
             "independent_primitives": {"pre_cut_only": True, "state_view": "PRIMITIVES"}}
    stats = {m: {rung: Counter() for rung in ("B1", "B2", "B4")} for m in modes}
    drift = Counter()
    heat_plaus, recon = Counter(), Counter()
    for row in rows:
        rec = recipes[row["recipe_id"]]
        steps, k, blk = steps_of(rec), int(row["cut_after_step"]), row["block"]
        loc = LOCALE.get(rec.get("source_family"))
        if len(steps) != int(row["n_steps"]):
            drift["recipe_steps_changed"] += 1
        eng = I.engine_outputs(steps, k, locale=loc, family=fam)
        drift["gold_equals_current_engine"] += bool(I.gold_engine_outputs(row, eng))
        q = Q[blk].format(k=k)
        for mode, kw in modes.items():
            for rung in ("B1", "B2", "B4"):
                ctx = H.context(rung, q, steps, cut=k, embed=hash_embed, locale=loc, **kw)
                st = stats[mode][rung]
                st["contexts"] += 1
                shared = I.shared_engine_outputs(row, ctx, eng)
                leaks = I.context_leaks(row, ctx, cut=k)
                st["shares_engine_output_with_gold"] += bool(shared)
                st["s1_aggregate_answer_field_in_context"] += any(x.startswith("AGGREGATE_ANSWER_FIELD") for x in leaks)
                st["s1_contexts"] += blk == "S1"
                st["post_cut_step_in_context"] += any(x.startswith("POST_CUT_STEP") for x in leaks)
                if blk == "S2":
                    st["s2_contexts"] += 1
                    st["s2_next_step_text_in_context"] += "next_process_id" in I.context_engine_outputs(row, ctx, eng)
        if blk == "S1":
            gold = {x for x in row["gold_ingredient_ids"].split("|") if x}
            heat_plaus[I.heat_presence_agreement(steps, k, gold)] += 1
            ev = I.primitive_events(steps, k, locale=loc)
            recon["s1_rows"] += 1
            recon["gold_rebuilt_exactly_from_printed_actions_by_heat_verb_rule"] += I.heated_from_primitives(ev) == gold
            recon["gold_rebuilt_as_superset_or_equal"] += I.heated_from_primitives(ev) >= gold
            recon["minimal_view_used_set_equals_gold"] += set(eng["used_ids"]) == gold
            recon["minimal_view_used_set_superset_of_gold"] += set(eng["used_ids"]) >= gold
    report = {
        "tool": "tools/s178_h1_gold_independence.py", "module": I.VERSION, "status": "AI_DRAFTED_COUNTS_ONLY_NON_CITABLE",
        "input": {"s_draft_sha256": SR.sha256_file(S_DRAFT), "n_questions": len(rows),
                  "by_block": dict(Counter(r["block"] for r in rows)), "by_family": dict(Counter(r["source_family"] for r in rows))},
        "gold_provenance": I.gold_independence_report(rows),
        "gold_vs_current_engine": {"n": len(rows), "gold_equals_current_engine_output": drift["gold_equals_current_engine"],
                                   "recipes_with_changed_step_count": drift["recipe_steps_changed"],
                                   "reading": "the draft gold is the engine output (by construction); a mismatch would mean engine drift"},
        "contexts": stats,
        "text_only_heat_check_s1": dict(heat_plaus),
        "residual_circularity_s1": dict(recon),
        "embedder": f"hashed bag of words, {DIM} dims (lexical proxy; retrieval counts are indicative only)",
        "reading": ["legacy B4 contexts print an aggregate answer field ('Heated so far') for S1 and legacy B1/B2/B4 retrieval can "
                    "return steps after the cut (for S2 the step that holds the answer)",
                    "independent contexts retrieve only steps up to the cut and carry no aggregate answer field; "
                    "shares_engine_output_with_gold is 0 by construction in both views",
                    "the printed action list is still engine output: where residual_circularity_s1 shows a plain heat-verb rule "
                    "rebuilding the gold, only blind-first human gold (gold_origin HUMAN_BLIND) makes that row non-circular"]}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(report, indent=1, sort_keys=True) + "\n").encode()
    with open(out_path, "xb") as fh:
        fh.write(data)
    print(json.dumps({"out": str(out_path), "sha256": hashlib.sha256(data).hexdigest()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
