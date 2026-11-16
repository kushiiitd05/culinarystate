#!/usr/bin/env python3
"""S178 CORPUS lane: Food.com quantity / part misalignment diagnostic and proposed alignment rule (no behaviour change by default).

`recipes.corpus.iter_foodcom` pairs `RecipeIngredientQuantities[i]` with `RecipeIngredientParts[i]` by position. This tool measures,
over the full corpus (counts only), how often the two lists differ in length and what that does to the lines, then evaluates the
pairing rules in `culinarystate.quantity.foodcom_pairing`:

  POSITIONAL          the current behaviour
  EQUAL_LENGTH_ONLY   proposed default: pair only equal-length recipes, otherwise no quantity (UNKNOWN)
  ALIGN_MODEL         experimental monotone alignment, scored by a bucket model trained on equal-length recipes, kept only above a
                      forward-backward posterior threshold. Validated by SIMULATION on held-out equal-length recipes (drop k parts or
                      k quantities, truth known) and by a likelihood diagnostic on the real unequal recipes.

Splits: recipe id hash (seed 20261104) -> train 60 % / dev 20 % / test 20 %; the model is trained on train-split equal-length recipes,
the skip costs are chosen on dev, all reported simulation numbers are on test. The real mechanism that produced the mismatch is not
known (the lists carry no link to the source lines), so a simulation result is evidence about the method under an assumption, not
about the corpus. Output: reports/s178/corpus/foodcom_quantity_alignment_v1.{json,md}. Counts and rates only.

  python tools/s178_corpus_foodcom_alignment.py [--sample N] [--eval-recipes N]
AI_DRAFTED / PROPOSED. NON_CITABLE.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TOOL_VERSION = "s178-corpus-foodcom-alignment-0.1.0-draft"
OUT_DIR = "reports/s178/corpus"
FOODCOM = "data/external/foodcom/recipes.parquet"
SEED = "20261104"
THRESHOLDS = (0.5, 0.7, 0.9, 0.95, 0.99)
COST_GRID = (1.5, 3.0, 4.5)
FS = "⁄"


def tk(t) -> str:
    """Code-safe key for a threshold (counts-only reports allow [A-Za-z0-9_] keys)."""
    return "T_" + str(t).replace(".", "_")


def dk(d: int) -> str:
    return ("M" if d < 0 else "P") + str(abs(d))


PROSE_KEYS = frozenset({"note", "reading", "description", "statement", "consequence", "length_difference_note", "experimental_alternative",
                        "equal_length_is_not_proof", "verdict", "proposed_rule", "mechanism_hypothesis"})


def strip_prose(obj):
    """Drop the explanatory-prose fields (written by this tool, never from the corpus) so the counts-only guard can check the rest."""
    if isinstance(obj, dict):
        return {k: strip_prose(v) for k, v in obj.items() if k not in PROSE_KEYS}
    if isinstance(obj, list):
        return [strip_prose(v) for v in obj]
    return obj


def pct(a, b):
    return round(100.0 * a / b, 3) if b else None


def split_of(rid: int) -> str:
    h = int(hashlib.sha256(f"{SEED}:{rid}".encode()).hexdigest()[:8], 16) % 10
    return "train" if h < 6 else ("dev" if h < 8 else "test")


def read_lists(root: Path, limit: int | None):
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(root / FOODCOM)
    n = 0
    for b in pf.iter_batches(batch_size=20000, columns=["RecipeId", "RecipeIngredientQuantities", "RecipeIngredientParts"]):
        for row in b.to_pylist():
            yield int(row["RecipeId"]), list(row["RecipeIngredientQuantities"] or []), list(row["RecipeIngredientParts"] or [])
            n += 1
            if limit and n >= limit:
                return


# ----------------------------------------------------------------------------- part A: diagnostic counts
def diagnostic(recs: list) -> dict:
    n_rec = len(recs)
    lines = sum(len(p) for _, _, p in recs)
    rel = Counter()
    diff_hist = Counter()
    by_len_total, by_len_equal = Counter(), Counter()
    lines_in_mismatch = padded = dropped_q = paired_q = 0
    null_q_in_equal = lines_in_equal = 0
    fs_paired = fs_dropped = 0
    for _, q, p in recs:
        m, n = len(p), len(q)
        d = n - m
        rel["EQUAL" if d == 0 else ("QUANTITIES_LONGER" if d > 0 else "QUANTITIES_SHORTER")] += 1
        diff_hist[max(-5, min(10, d))] += 1
        bl = "1" if m == 1 else "2" if m == 2 else "3_4" if m <= 4 else "5_8" if m <= 8 else "9_15" if m <= 15 else "16_PLUS"
        if m:
            by_len_total[bl] += 1
            by_len_equal[bl] += d == 0
        if d != 0:
            lines_in_mismatch += m
        else:
            lines_in_equal += m
            null_q_in_equal += sum(1 for x in q if not x)
        padded += max(0, m - n)
        dropped_q += max(0, n - m)
        for i in range(min(m, n)):
            if q[i]:
                paired_q += 1
                fs_paired += FS in q[i]
        for i in range(m, n):
            fs_dropped += bool(q[i]) and FS in q[i]
    rec_equal = rel["EQUAL"]
    q_total = sum(len(q) for _, q, _ in recs)
    q_null = sum(1 for _, q, _ in recs for x in q if not x)
    return {
        "recipes": n_rec, "lines_parts_total": lines,
        "quantity_strings_total": q_total, "quantity_strings_null": q_null,
        "quantities_minus_parts_total": q_total - lines,
        "mean_quantities_minus_parts_per_recipe": round((q_total - lines) / n_rec, 3) if n_rec else None,
        "mechanism_hypothesis": "the quantity list looks like one entry per source ingredient line (null when the line has no "
                                "quantity) and the parts list like the lines in which a food part was extracted; lines with no extracted part "
                                "(quantities longer, 73.8 percent of recipes, even for recipes with one part) and lines with two foods (parts longer) "
                                "would shift every later position. The lists carry no line index, so this cannot be checked against the source",
        "recipes_by_length_relation": dict(rel),
        "pct_recipes_unequal": pct(n_rec - rec_equal, n_rec),
        "recipes_unequal": n_rec - rec_equal,
        "length_difference_quantities_minus_parts_histogram": {dk(k): v for k, v in sorted(diff_hist.items())},
        "length_difference_note": "keys clipped to -5..10",
        "recipes_with_zero_parts": sum(1 for _, _, p in recs if not p), "recipes_with_zero_quantities": sum(1 for _, q, _ in recs if not q),
        "lines_in_unequal_recipes": lines_in_mismatch, "pct_lines_in_unequal_recipes": pct(lines_in_mismatch, lines),
        "positional_pairing": {"lines_with_a_paired_quantity": paired_q, "lines_without_quantity_text_padded_or_null": lines - paired_q,
                               "padding_positions_parts_without_a_quantity_slot": padded,
                               "quantity_strings_dropped_beyond_the_parts_list": dropped_q,
                               "quantities_with_u2044_paired": fs_paired, "quantities_with_u2044_dropped": fs_dropped},
        "equal_length_only_rule": {"recipes_paired": rec_equal, "lines_paired": lines_in_equal,
                                   "pct_of_lines": pct(lines_in_equal, lines), "lines_with_null_quantity_in_those_recipes": null_q_in_equal,
                                   "lines_left_without_quantity": lines - lines_in_equal},
        "p_equal_length_by_recipe_length": {k: {"recipes": by_len_total[k], "equal": by_len_equal[k], "pct_equal": pct(by_len_equal[k], by_len_total[k])}
                                            for k in ("1", "2", "3_4", "5_8", "9_15", "16_PLUS") if by_len_total[k]},
    }


# ----------------------------------------------------------------------------- part B: model, simulation, real-data diagnostic
def train_model(recs):
    from culinarystate.quantity.foodcom_pairing import AlignmentModel
    model = AlignmentModel()
    n_rec = n_lines = 0
    for rid, q, p in recs:
        if split_of(rid) != "train" or len(q) != len(p) or not p:
            continue
        n_rec += 1
        for qi, pi in zip(q, p):
            model.add(pi, qi)
            n_lines += 1
    return model, n_rec, n_lines


def corrupt(rng, q, p, kind: str, k: int):
    """Drop k random parts ('PARTS') or k random quantities ('QUANTITIES'). Returns (q2, p2, truth) with truth[i] = original
    quantity index of part i in q2's frame, or None when that part's quantity was dropped."""
    m = len(p)
    if m <= k + 1:
        return None
    if kind == "PARTS":
        drop = set(rng.sample(range(m), k))
        keep = [i for i in range(m) if i not in drop]
        return list(q), [p[i] for i in keep], list(keep)       # truth: part r pairs with q[keep[r]]
    drop = set(rng.sample(range(m), k))
    keep_q = [i for i in range(m) if i not in drop]
    q2 = [q[i] for i in keep_q]
    new_index = {orig: new for new, orig in enumerate(keep_q)}
    return q2, list(p), [new_index.get(i) for i in range(m)]


def evaluate(model, recs_test, kind, k, rng, cost, n_max, thresholds=THRESHOLDS):
    from culinarystate.quantity.foodcom_pairing import alignment_posteriors
    tot = Counter()
    nll_pos = nll_post = 0.0
    n_nll = n_post = 0
    done = 0
    for _rid, q, p in recs_test:
        if done >= n_max:
            break
        c = corrupt(rng, q, p, kind, k)
        if c is None:
            continue
        done += 1
        q2, p2, truth = c
        post = alignment_posteriors(model, q2, p2, skip_part_cost=cost, skip_qty_cost=cost)
        for i in range(len(p2)):
            tot["parts"] += 1
            # positional baseline: pair with index i when it exists
            pos_ok = i < len(q2) and truth[i] is not None and truth[i] == i
            tot["positional_correct"] += pos_ok
            tot["positional_has_pair"] += i < len(q2)
            j = max(range(len(q2)), key=lambda jj: post[i][jj])
            pj = post[i][j]
            correct = truth[i] is not None and j == truth[i]
            tot["map_correct"] += correct
            for t in thresholds:
                if pj >= t:
                    tot[f"paired_{t}"] += 1
                    tot[f"correct_{t}"] += correct
            # likelihood diagnostic
            from culinarystate.quantity.foodcom_pairing import bucket_of
            if i < len(q2):
                nll_pos += -math.log(model.prob(p2[i], bucket_of(q2[i])))
                n_nll += 1
            z = sum(post[i])
            if z > 0:
                nll_post += sum(post[i][jj] * -math.log(model.prob(p2[i], bucket_of(q2[jj]))) for jj in range(len(q2))) / z
                n_post += 1
    out = {"recipes": done, "parts": tot["parts"], "positional_accuracy_pct": pct(tot["positional_correct"], tot["parts"]),
           "map_alignment_accuracy_pct": pct(tot["map_correct"], tot["parts"]),
           "thresholds": {tk(t): {"coverage_pct": pct(tot[f"paired_{t}"], tot["parts"]),
                                   "precision_pct": pct(tot[f"correct_{t}"], tot[f"paired_{t}"])} for t in thresholds},
           "positional_mean_nll_nats": round(nll_pos / n_nll, 4) if n_nll else None,
           "posterior_weighted_mean_nll_nats": round(nll_post / n_post, 4) if n_post else None}
    return out


def real_unequal_diag(model, recs, cost, n_max, rng):
    """Mean -log P(bucket | part) per part: equal-length recipes (positional = the aligned reference), unequal recipes
    positional (prefix) and posterior-weighted under the alignment model."""
    from culinarystate.quantity.foodcom_pairing import alignment_posteriors, bucket_of
    ref = Counter()
    eq = [r for r in recs if len(r[1]) == len(r[2]) and r[2] and split_of(r[0]) == "test"]
    ne = [r for r in recs if len(r[1]) != len(r[2]) and r[2] and r[1] and split_of(r[0]) == "test"]
    rng.shuffle(eq)
    rng.shuffle(ne)
    s = n = 0
    sp = nsp = 0.0
    for _, q, p in eq[:n_max]:
        pr = alignment_posteriors(model, q, p, skip_part_cost=cost, skip_qty_cost=cost)
        for i, (qi, pi) in enumerate(zip(q, p)):
            s += -math.log(model.prob(pi, bucket_of(qi)))
            n += 1
            z = sum(pr[i])
            if z > 0:
                sp += sum(pr[i][j] * -math.log(model.prob(pi, bucket_of(q[j]))) for j in range(len(q))) / z
                nsp += 1
    ref_nll = s / n if n else None
    ref_post = sp / nsp if nsp else None
    pos = post = 0.0
    npos = npost = 0
    for _, q, p in ne[:n_max]:
        pr = alignment_posteriors(model, q, p, skip_part_cost=cost, skip_qty_cost=cost)
        for i in range(len(p)):
            if i < len(q):
                pos += -math.log(model.prob(p[i], bucket_of(q[i])))
                npos += 1
            z = sum(pr[i])
            if z > 0:
                post += sum(pr[i][j] * -math.log(model.prob(p[i], bucket_of(q[j]))) for j in range(len(q))) / z
                npost += 1
    return {"equal_length_recipes_used": min(len(eq), n_max), "unequal_recipes_used": min(len(ne), n_max),
            "mean_nll_equal_length_positional": round(ref_nll, 4) if ref_nll is not None else None,
            "mean_nll_equal_length_alignment_posterior_weighted": round(ref_post, 4) if ref_post is not None else None,
            "mean_nll_unequal_positional_prefix": round(pos / npos, 4) if npos else None,
            "mean_nll_unequal_alignment_posterior_weighted": round(post / npost, 4) if npost else None,
            "reading": "compare like with like: positional with positional, posterior-weighted with posterior-weighted (the latter is lower "
                       "even on aligned recipes because it picks the best-fitting quantity). A real-unequal positional value clearly above the "
                       "equal-length one means positional pairing fits the unequal recipes worse, as in the simulation; it is a likelihood "
                       "diagnostic, not a pairing accuracy"}


def run(root: Path, limit: int | None, eval_recipes: int, workers_note: str) -> dict:
    from culinarystate.quantity import foodcom_pairing as FP
    t0 = time.time()
    recs = list(read_lists(root, limit))
    res = {"record": "FOODCOM_QUANTITY_ALIGNMENT_S178", "tool_version": TOOL_VERSION, "pairing_version": FP.PAIRING_VERSION,
           "status": "AI_DRAFTED_PROPOSED_COUNTS_ONLY", "contains_text": False, "contains_ids": False, "counts_as_human_gate": False,
           "sample_limit_recipes": limit, "split_seed": SEED, "rules": list(FP.RULES)}
    res["diagnostic"] = diagnostic(recs)
    model, n_train_rec, n_train_lines = train_model(recs)
    res["model"] = {"trained_on_equal_length_recipes": n_train_rec, "trained_on_lines": n_train_lines,
                    "distinct_part_phrases": len(model.phrase), "distinct_head_words": len(model.head),
                    "bucket_counts": dict(sorted(model.glob.items())), "alpha": model.alpha, "min_phrase_count": model.min_phrase}
    rng = random.Random(20261104)
    dev = [r for r in recs if split_of(r[0]) == "dev" and len(r[1]) == len(r[2]) and len(r[2]) >= 4]
    test = [r for r in recs if split_of(r[0]) == "test" and len(r[1]) == len(r[2]) and len(r[2]) >= 4]
    rng.shuffle(dev)
    rng.shuffle(test)
    # choose the skip cost on dev (mean of precision at 0.9 weighted by coverage, both scenarios, k=1..2)
    grid = {}
    for cost in COST_GRID:
        score = 0.0
        for kind in ("PARTS", "QUANTITIES"):
            for k in (1, 2):
                e = evaluate(model, dev, kind, k, random.Random(1), cost, max(200, eval_recipes // 5), thresholds=(0.9,))
                t = e["thresholds"][tk(0.9)]
                score += (t["coverage_pct"] or 0) * (t["precision_pct"] or 0) / 1e4
        grid[str(cost).replace(".", "_")] = round(score / 4, 4)
    best = max(COST_GRID, key=lambda c: grid[str(c).replace(".", "_")])
    res["cost_selection_on_dev"] = {"grid_score_coverage_x_precision_at_0_9": grid, "chosen_skip_cost_nats": best}
    sim = {}
    for kind in ("PARTS", "QUANTITIES"):
        for k in (1, 2, 3):
            sim[f"{kind}_dropped_{k}"] = evaluate(model, test, kind, k, random.Random(100 + k), best, eval_recipes)
    res["simulation_on_test_split"] = {"description": "equal-length test recipes with >= 4 parts; k parts (PARTS) or k quantities (QUANTITIES) removed at random; "
                                                      "truth = original pairing. positional = current rule; thresholds = ALIGN_MODEL gated by posterior",
                                       "scenarios": sim}
    res["real_unequal_likelihood_diagnostic"] = real_unequal_diag(model, recs, best, eval_recipes, random.Random(5))
    d = res["diagnostic"]
    sim1 = sim["PARTS_dropped_1"]
    res["proposed_rule"] = {
        "default": "EQUAL_LENGTH_ONLY",
        "statement": ("Pair quantity and part only when the two lists have the same length (%s of %s recipes, %s %% of lines); in every other recipe give "
                      "the parts NO quantity (UNKNOWN). The current positional rule mispairs lines after the first drop in the other %s %% of recipes (%s %% of lines)."
                      % (f"{d['recipes'] - d['recipes_unequal']:,}", f"{d['recipes']:,}", d["equal_length_only_rule"]["pct_of_lines"],
                         d["pct_recipes_unequal"], d["pct_lines_in_unequal_recipes"])),
        "experimental_alternative": "ALIGN_MODEL at posterior >= 0.9 (see simulation); adopt only after a human spot-check of the pairs; the "
                                    "simulation assumes the mismatch is a few dropped parts or quantities",
        "equal_length_is_not_proof": "equal length is necessary, not sufficient: a recipe that lost one part AND gained one stray quantity is "
                                     "indistinguishable; the rate of that case is unknown",
        "simulated_one_part_dropped": {"positional_accuracy_pct": sim1["positional_accuracy_pct"], "align_map_accuracy_pct": sim1["map_alignment_accuracy_pct"],
                                       "align_0_9": sim1["thresholds"][tk(0.9)]}}
    res["seconds"] = round(time.time() - t0, 1)
    from culinarystate.quantity.rc2_dryrun import assert_counts_only
    assert_counts_only(strip_prose(res))
    return res


def md(res: dict) -> str:
    d = res["diagnostic"]
    L = ["# Food.com quantity / part misalignment: diagnostic and proposed rule (S178)", "",
         "Status: AI_DRAFTED / PROPOSED. Counts and rates only; no recipe text. NON_CITABLE. No behaviour change: `recipes.corpus.iter_foodcom` is untouched; "
         f"the rules are opt-in in `culinarystate.quantity.foodcom_pairing` (`{res['pairing_version']}`).", "",
         f"Recipes: {d['recipes']:,}{' (sample)' if res['sample_limit_recipes'] else ''}; part lines: {d['lines_parts_total']:,}.", "",
         "## Diagnostic", "", "| relation (quantities vs parts) | recipes | % |", "|---|---:|---:|"]
    for k, v in sorted(d["recipes_by_length_relation"].items()):
        L.append(f"| {k} | {v:,} | {pct(v, d['recipes'])} |")
    L += ["", f"- Quantity strings {d['quantity_strings_total']:,} (null {d['quantity_strings_null']:,}) against {d['lines_parts_total']:,} parts: the quantity list is longer by {d['quantities_minus_parts_total']:,} entries ({d['mean_quantities_minus_parts_per_recipe']} per recipe).",
          f"- Mechanism (hypothesis, not established): {d['mechanism_hypothesis']}.",
          f"- Unequal recipes: **{d['recipes_unequal']:,} ({d['pct_recipes_unequal']} %)**; lines inside them: {d['lines_in_unequal_recipes']:,} ({d['pct_lines_in_unequal_recipes']} %).",
          f"- Positional pairing today: {d['positional_pairing']['lines_with_a_paired_quantity']:,} lines get a quantity, "
          f"{d['positional_pairing']['lines_without_quantity_text_padded_or_null']:,} none; {d['positional_pairing']['quantity_strings_dropped_beyond_the_parts_list']:,} "
          f"quantity strings are dropped beyond the parts list (of them {d['positional_pairing']['quantities_with_u2044_dropped']:,} with U+2044).",
          f"- Recipes with zero parts: {d['recipes_with_zero_parts']:,}; with zero quantities: {d['recipes_with_zero_quantities']:,}.", "",
          "Length difference (quantities minus parts), recipes:", "", "| diff | recipes |", "|---:|---:|"]
    for k, v in d["length_difference_quantities_minus_parts_histogram"].items():
        L.append(f"| {k} | {v:,} |")
    L += ["", "Share of recipes with equal lists by recipe length (a per-line drop mechanism makes long recipes unequal more often):", "",
          "| parts | recipes | equal | % equal |", "|---|---:|---:|---:|"]
    for k, v in d["p_equal_length_by_recipe_length"].items():
        L.append(f"| {k} | {v['recipes']:,} | {v['equal']:,} | {v['pct_equal']} |")
    r = d["equal_length_only_rule"]
    pr = res["proposed_rule"]
    L += ["", "## Proposed rule (default: EQUAL_LENGTH_ONLY)", "", pr["statement"], "",
          f"Lines paired: {r['lines_paired']:,} ({r['pct_of_lines']} %); lines left without a quantity: {r['lines_left_without_quantity']:,}. {pr['equal_length_is_not_proof']}.", "",
          "## Experimental alternative: ALIGN_MODEL (validated by simulation only)", "",
          f"Model trained on {res['model']['trained_on_equal_length_recipes']:,} equal-length train-split recipes ({res['model']['trained_on_lines']:,} lines); skip cost "
          f"{res['cost_selection_on_dev']['chosen_skip_cost_nats']} nats chosen on dev. Test-split simulation (truth known):", "",
          "| scenario | recipes | parts | positional correct % | MAP alignment correct % | gated 0.9: coverage % | gated 0.9: precision % | gated 0.99: coverage % | gated 0.99: precision % |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, e in res["simulation_on_test_split"]["scenarios"].items():
        t9, t99 = e["thresholds"][tk(0.9)], e["thresholds"][tk(0.99)]
        L.append(f"| {name} | {e['recipes']:,} | {e['parts']:,} | {e['positional_accuracy_pct']} | {e['map_alignment_accuracy_pct']} | {t9['coverage_pct']} | {t9['precision_pct']} | {t99['coverage_pct']} | {t99['precision_pct']} |")
    x = res["real_unequal_likelihood_diagnostic"]
    L += ["", "Real unequal recipes (likelihood diagnostic, mean -log P(quantity bucket | part), nats per part):", "",
          f"- equal-length recipes, positional (aligned reference): {x['mean_nll_equal_length_positional']}; posterior-weighted: {x['mean_nll_equal_length_alignment_posterior_weighted']}",
          f"- unequal recipes, positional prefix pairing: {x['mean_nll_unequal_positional_prefix']}; posterior-weighted: {x['mean_nll_unequal_alignment_posterior_weighted']}",
          "- simulated (test split, equal-length recipes corrupted), positional / posterior-weighted: " + "; ".join(
              f"{n} {e['positional_mean_nll_nats']} / {e['posterior_weighted_mean_nll_nats']}" for n, e in res["simulation_on_test_split"]["scenarios"].items()),
          "", x["reading"] + ".", "",
          "## Limits", "",
          "- No ground truth exists for any Food.com pairing; the simulation corrupts equal-length recipes, so it measures the method on the corruption it assumes.",
          "- The model sees only the magnitude bucket of the quantity and the food name; it never sees a unit (there is none).",
          "- A human spot-check of 100 aligned pairs per rule would be the first real accuracy estimate (not done)."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=None, help="first N recipes (smoke test)")
    ap.add_argument("--eval-recipes", type=int, default=3000)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root)
    out = Path(a.out_dir) if a.out_dir else root / OUT_DIR
    res = run(root, a.sample, a.eval_recipes, "")
    out.mkdir(parents=True, exist_ok=True)
    suffix = f"_sample{a.sample}" if a.sample else ""
    (out / f"foodcom_quantity_alignment_v1{suffix}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out / f"foodcom_quantity_alignment_v1{suffix}.md").write_text(md(res), encoding="utf-8")
    d = res["diagnostic"]
    print(json.dumps({"recipes": d["recipes"], "unequal": d["recipes_unequal"], "pct_unequal": d["pct_recipes_unequal"],
                      "lines_paired_equal_rule": d["equal_length_only_rule"]["lines_paired"], "seconds": res["seconds"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
