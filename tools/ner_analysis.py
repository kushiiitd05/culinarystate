"""E16-A NER error analysis + paired bootstrap significance (plan Part K, §245).

Reads all .pred.jsonl and .json run files. Outputs:
  reports/ner/e16a_error_analysis.md — per-label errors, confusion, systematic failures
  reports/ner/e16a_significance.md — paired bootstrap comparison table

Usage: /opt/anaconda3/bin/python -I tools/ner_analysis.py
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

RUNS = Path("gpu/ner_tasteset/runs")
TSET = Path("gpu/ner_tasteset/TASTEset.csv")
OUT = Path("reports/ner")
MODELS = [
    "bert-base-cased", "roberta-base", "deberta-v3-base",
    "deberta-v3-base_crf", "deberta-v3-base_knn",
    "deberta-v3-large", "deberta-v3-large_crf",
]
LABELS = ["FOOD", "QUANTITY", "UNIT", "PROCESS", "PHYSICAL_QUALITY",
          "COLOR", "TASTE", "PURPOSE", "PART"]
SEEDS = 5
SPLIT_SEED = 7
WORD = re.compile(r"\w+|[^\w\s]")


def load_tasteset() -> dict[int, str]:
    """recipe_id (= row index) -> ingredient text"""
    import csv
    texts = {}
    with open(TSET) as f:
        for i, row in enumerate(csv.DictReader(f)):
            texts[i] = row["ingredients"]
    return texts


def load_preds(model: str, seed: int) -> list[dict]:
    p = RUNS / f"{model}_seed{seed}.pred.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().strip().split("\n") if l.strip()]


def load_run_json(model: str, seed: int) -> dict:
    p = RUNS / f"{model}_seed{seed}.json"
    return json.loads(p.read_text()) if p.exists() else {}


def span_match(g, p, mode="exact"):
    gs, ge, gl = g
    ps, pe, pl = p
    if gl != pl:
        return False
    if mode == "exact":
        return gs == ps and ge == pe
    return max(gs, ps) < min(ge, pe)  # relaxed: any overlap


def score_per_recipe(preds: list[dict], mode="exact") -> dict[int, dict]:
    """recipe_id -> {label: {tp, fp, fn}}"""
    per_rec = {}
    for row in preds:
        rid = row["recipe"]
        gold = [tuple(s) for s in row["gold"]]
        pred = [tuple(s) for s in row["pred"]]
        counts = {}
        for lab in LABELS:
            gl = [s for s in gold if s[2] == lab]
            pl = [s for s in pred if s[2] == lab]
            matched_g = set()
            matched_p = set()
            for i, g in enumerate(gl):
                for j, p in enumerate(pl):
                    if j not in matched_p and span_match(g, p, mode):
                        matched_g.add(i)
                        matched_p.add(j)
                        break
            tp = len(matched_g)
            counts[lab] = {"tp": tp, "fp": len(pl) - tp, "fn": len(gl) - tp}
        per_rec[rid] = counts
    return per_rec


def micro_f1_from_counts(counts_list: list[dict]) -> float:
    tp = sum(c["tp"] for cs in counts_list for c in cs.values())
    fp = sum(c["fp"] for cs in counts_list for c in cs.values())
    fn = sum(c["fn"] for cs in counts_list for c in cs.values())
    if tp == 0:
        return 0.0
    p = tp / (tp + fp)
    r = tp / (tp + fn)
    return 2 * p * r / (p + r)


def grouped_bootstrap_paired(scores_a: dict, scores_b: dict, n_boot=2000, seed=42):
    """Paired bootstrap: is model A better than B? Returns (delta, p_value, ci_low, ci_high)."""
    rng = np.random.RandomState(seed)
    rids = sorted(set(scores_a) & set(scores_b))
    n = len(rids)
    rids_arr = np.array(rids)

    obs_a = micro_f1_from_counts([scores_a[r] for r in rids])
    obs_b = micro_f1_from_counts([scores_b[r] for r in rids])
    obs_delta = obs_a - obs_b

    deltas = []
    count_b_wins = 0
    for _ in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        sampled = rids_arr[idx]
        sa = micro_f1_from_counts([scores_a[r] for r in sampled])
        sb = micro_f1_from_counts([scores_b[r] for r in sampled])
        d = sa - sb
        deltas.append(d)
        if d <= 0:
            count_b_wins += 1

    deltas = np.array(deltas)
    p_val = count_b_wins / n_boot
    ci = (np.percentile(deltas, 2.5), np.percentile(deltas, 97.5))
    return obs_delta, p_val, ci[0], ci[1]


def error_classification(gold: list, pred: list, text: str) -> list[dict]:
    """Classify each error into a category."""
    errors = []
    gold_set = {(s, e, l) for s, e, l in gold}
    pred_set = {(s, e, l) for s, e, l in pred}

    # FP: in pred not in gold
    for ps, pe, pl in pred_set:
        if (ps, pe, pl) not in gold_set:
            span_text = text[ps:pe] if text else ""
            # check if boundary error (same label, overlapping gold)
            boundary = False
            label_confusion = None
            for gs, ge, gl in gold_set:
                if max(gs, ps) < min(ge, pe):  # overlap
                    if gl == pl:
                        boundary = True
                    else:
                        label_confusion = gl
            if boundary:
                cat = "BOUNDARY_FP"
            elif label_confusion:
                cat = f"LABEL_CONFUSION_{label_confusion}->{pl}"
            else:
                cat = "SPURIOUS_FP"
            errors.append({"type": "FP", "cat": cat, "label": pl, "span": span_text, "pos": (ps, pe)})

    # FN: in gold not in pred
    for gs, ge, gl in gold_set:
        if (gs, ge, gl) not in pred_set:
            span_text = text[gs:ge] if text else ""
            boundary = False
            label_confusion = None
            for ps, pe, pl in pred_set:
                if max(gs, ps) < min(ge, pe):
                    if pl == gl:
                        boundary = True
                    else:
                        label_confusion = pl
            if boundary:
                cat = "BOUNDARY_FN"
            elif label_confusion:
                cat = f"LABEL_CONFUSION_{gl}->{label_confusion}"
            else:
                cat = "MISSED_FN"
            errors.append({"type": "FN", "cat": cat, "label": gl, "span": span_text, "pos": (gs, ge)})
    return errors


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    texts = load_tasteset()

    # --- Load all predictions (seed 1 for error analysis, all seeds for stats) ---
    all_scores = {}  # model -> {recipe_id -> counts}
    all_preds_s1 = {}  # model -> list[dict] (seed 1 only, for error analysis)
    per_model_f1 = {}  # model -> [f1_seed1, ..., f1_seed5]

    for model in MODELS:
        seeds_f1 = []
        for s in range(1, SEEDS + 1):
            preds = load_preds(model, s)
            if not preds:
                continue
            scores = score_per_recipe(preds)
            f1 = micro_f1_from_counts(list(scores.values()))
            seeds_f1.append(f1)
            if s == 1:
                all_scores[model] = scores
                all_preds_s1[model] = preds
        per_model_f1[model] = seeds_f1

    # ===== ERROR ANALYSIS (best model: deberta-v3-large_crf, seed 1) =====
    best = "deberta-v3-base_crf"  # local model — most relevant for deployment
    preds_best = all_preds_s1.get(best, [])

    all_errors = []
    error_by_label = defaultdict(list)
    error_cats = Counter()
    fp_spans = Counter()
    fn_spans = Counter()

    for row in preds_best:
        rid = row["recipe"]
        text = texts.get(rid, "")
        gold = [tuple(s) for s in row["gold"]]
        pred = [tuple(s) for s in row["pred"]]
        errs = error_classification(gold, pred, text)
        for e in errs:
            all_errors.append({**e, "recipe": rid})
            error_by_label[e["label"]].append(e)
            error_cats[e["cat"]] += 1
            if e["type"] == "FP":
                fp_spans[e["span"].lower()] += 1
            else:
                fn_spans[e["span"].lower()] += 1

    # Per-label error breakdown
    label_stats = {}
    scores_best = all_scores.get(best, {})
    for lab in LABELS:
        tp = sum(c[lab]["tp"] for c in scores_best.values())
        fp = sum(c[lab]["fp"] for c in scores_best.values())
        fn = sum(c[lab]["fn"] for c in scores_best.values())
        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        lab_errors = error_by_label.get(lab, [])
        cats = Counter(e["cat"] for e in lab_errors)
        label_stats[lab] = {"tp": tp, "fp": fp, "fn": fn, "p": p, "r": r, "f1": f1,
                           "n_errors": len(lab_errors), "cats": dict(cats)}

    # ===== WRITE ERROR ANALYSIS REPORT =====
    lines = [f"# E16-A NER Error Analysis ({best}, seed 1)\n",
             f"Test set: 105 recipes. Total errors: {len(all_errors)} "
             f"({sum(1 for e in all_errors if e['type']=='FP')} FP, "
             f"{sum(1 for e in all_errors if e['type']=='FN')} FN).\n"]

    lines.append("\n## Per-label breakdown\n")
    lines.append("| Label | TP | FP | FN | P | R | F1 | Errors | Top error type |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for lab in LABELS:
        s = label_stats[lab]
        top_cat = max(s["cats"], key=s["cats"].get) if s["cats"] else "-"
        lines.append(f"| {lab} | {s['tp']} | {s['fp']} | {s['fn']} | "
                     f"{s['p']:.3f} | {s['r']:.3f} | {s['f1']:.3f} | {s['n_errors']} | {top_cat} |")

    lines.append("\n## Error category distribution\n")
    lines.append("| Category | Count | % |")
    lines.append("|---|---|---|")
    total_err = len(all_errors) or 1
    for cat, cnt in error_cats.most_common():
        lines.append(f"| {cat} | {cnt} | {cnt/total_err*100:.1f}% |")

    lines.append("\n## Most common FP spans (spurious)\n")
    lines.append("| Span | Count |")
    lines.append("|---|---|")
    for span, cnt in fp_spans.most_common(15):
        lines.append(f"| `{span}` | {cnt} |")

    lines.append("\n## Most common FN spans (missed)\n")
    lines.append("| Span | Count |")
    lines.append("|---|---|")
    for span, cnt in fn_spans.most_common(15):
        lines.append(f"| `{span}` | {cnt} |")

    # Weak label deep dive
    lines.append("\n## Weak label analysis\n")
    for lab in ["PART", "TASTE", "PURPOSE"]:
        s = label_stats[lab]
        lab_errs = error_by_label.get(lab, [])
        lines.append(f"\n### {lab} (F1 {s['f1']:.3f})\n")
        lines.append(f"TP={s['tp']}, FP={s['fp']}, FN={s['fn']}. "
                     f"Errors: {s['n_errors']}.\n")
        if lab_errs:
            lines.append("Sample errors:")
            for e in lab_errs[:8]:
                lines.append(f"- [{e['type']}] `{e['span'][:40]}` — {e['cat']}")

    # ===== PAIRED BOOTSTRAP SIGNIFICANCE =====
    sig_lines = ["# E16-A Paired Bootstrap Significance\n",
                 f"2000 bootstrap resamples over 105 recipe groups (seed 42).\n",
                 "| Comparison | Δ F1 | p-value | 95% CI | Significant? |",
                 "|---|---|---|---|---|"]

    pairs = [
        ("deberta-v3-base_crf", "deberta-v3-base", "CRF vs base"),
        ("deberta-v3-base_crf", "deberta-v3-base_knn", "CRF vs kNN"),
        ("deberta-v3-large_crf", "deberta-v3-base_crf", "large+CRF vs base+CRF"),
        ("deberta-v3-large_crf", "deberta-v3-large", "large+CRF vs large"),
        ("deberta-v3-base_crf", "roberta-base", "base+CRF vs RoBERTa"),
        ("deberta-v3-base_crf", "bert-base-cased", "base+CRF vs BERT"),
        ("deberta-v3-large_crf", "roberta-base", "large+CRF vs RoBERTa"),
        ("deberta-v3-base_knn", "deberta-v3-base", "kNN vs base"),
    ]

    for ma, mb, name in pairs:
        if ma not in all_scores or mb not in all_scores:
            continue
        delta, pval, ci_lo, ci_hi = grouped_bootstrap_paired(all_scores[ma], all_scores[mb])
        sig = "YES" if ci_lo > 0 else ("NO" if ci_hi < 0 else "n.s.")
        sig_lines.append(f"| {name} | {delta:+.4f} | {pval:.3f} | [{ci_lo:+.4f}, {ci_hi:+.4f}] | {sig} |")

    # Cross-seed variance
    sig_lines.append("\n## Per-model variance (5 seeds)\n")
    sig_lines.append("| Model | Mean F1 | Std | Min | Max |")
    sig_lines.append("|---|---|---|---|---|")
    for model in MODELS:
        f1s = per_model_f1.get(model, [])
        if f1s:
            sig_lines.append(f"| {model} | {np.mean(f1s):.4f} | {np.std(f1s):.4f} | "
                           f"{min(f1s):.4f} | {max(f1s):.4f} |")

    # Write reports
    (OUT / "e16a_error_analysis.md").write_text("\n".join(lines) + "\n")
    (OUT / "e16a_significance.md").write_text("\n".join(sig_lines) + "\n")
    print(f"Wrote {OUT}/e16a_error_analysis.md ({len(all_errors)} errors)")
    print(f"Wrote {OUT}/e16a_significance.md ({len(pairs)} comparisons)")


if __name__ == "__main__":
    main()
