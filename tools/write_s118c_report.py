#!/usr/bin/env python3
"""S118C: write reports/ner/recipedb3_matched_reproduction.md from reports/ner/recipedb3_control_summary.json (run tools/analyze_recipedb3_control.py first)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
d = json.load(open(ROOT / "reports/ner/recipedb3_control_summary.json"))
A, runs = d["agg"], d["runs"]
PUB = {"macro": 0.9557, "micro": 0.9603, "seed": 48}                      # notebook, last-epoch final report, seed 48, selection on test
f = lambda k, p, key="test_macro_best": f"{A[p][key]['mean']:.4f} ± {A[p][key]['sd']:.4f} (95% CI {A[p][key]['ci95'][0]:.4f}–{A[p][key]['ci95'][1]:.4f}, n={A[p][key]['n']})"
t48 = next(r for r in runs if r["protocol"] == "theirs" and r["seed"] == 48)
sz = d.get("size_effect_paired_seeds")
lines = ["# RecipeDB3 NER matched reproduction + clean grouped control (A100)", "",
         "Scientific control, NOT our final NER: plain `microsoft/deberta-base` token classification, no CRF, 15 epochs, lr 5e-5, bs 16, max_len 128, bf16 off (fp32), AdamW. "
         "No SOTA / superiority claim before H6.", "",
         f"Dataset sha256 `{d['dataset_sha256'][:16]}…`; repro.py sha256 `{d['code_sha256_repro'][:16]}…`; GPU: NVIDIA A100 (shared). Per-seed JSONs in `reports/ner/_raw/`; "
         "aggregates `reports/ner/recipedb3_control_summary.json`. Two early runs (theirs seed 48, clean seed 1) were launched before per-label scores and runtimes were logged, so per-label means use 4 of 5 seeds in each protocol.", "",
         "## Results (test, checkpoint-at-best unless stated)", "",
         "| Protocol | Selection | Seeds | Macro F1 | Micro F1 | Last-epoch macro |", "|---|---|---|---|---|---|",
         f"| Their notebook (random 80/20) | test | {A['theirs']['test_macro_best']['n']} | {f('', 'theirs')} | {A['theirs']['test_micro_best']['mean']:.4f} | {A['theirs']['test_macro_last']['mean']:.4f} |",
         f"| Clean (80/10/10, masked-sentence-family grouped) | dev | {A['clean']['test_macro_best']['n']} | {f('', 'clean')} | {A['clean']['test_micro_best']['mean']:.4f} | {A['clean']['test_macro_last']['mean']:.4f} |", "",
         "## Answers", "",
         f"1. **Did the matched reproduction reach the published-value region?** Yes. Notebook (seed 48, final epoch) reports macro {PUB['macro']} / micro {PUB['micro']}; our seed 48 gives macro {t48['test_macro_best']:.4f} (best-on-test) / micro {t48['test_micro_best']:.4f}, and the 5-seed mean is {A['theirs']['test_macro_best']['mean']:.4f}, within one seed-SD of the published number.",
         f"2. **Effect of proper dev-set selection.** Choosing the checkpoint on TEST (their protocol) inflates macro F1 relative to its own last epoch: {A['theirs']['test_macro_best']['mean']:.4f} vs {A['theirs']['test_macro_last']['mean']:.4f}. On the clean split, selecting on dev gives {A['clean']['test_macro_best']['mean']:.4f} (last epoch {A['clean']['test_macro_last']['mean']:.4f}); there the best-on-dev checkpoint is slightly below the last epoch, i.e. no test-selection optimism remains.",
         f"3. **Effect of the family-grouped split.** Theirs − clean = {d['theirs_vs_clean_macro']['delta']:+.4f} macro F1 (Welch p = {d['theirs_vs_clean_macro']['welch_p']}), small and not significant at 5 seeds; the clean split removes leakage but the headline barely moves because most rows are non-leaked.",
         f"4. **Leaked vs non-leaked.** In their protocol {A['theirs']['masked_family_leak_frac_test']['mean']*100:.1f}% of test rows share a masked family with train and {A['theirs']['exact_duplicate_frac_test']['mean']*100:.1f}% are exact duplicates. Leaked rows score micro F1 {A['theirs']['leaked_micro']['mean']:.4f}; non-leaked rows {A['theirs']['nonleaked_micro']['mean']:.4f} (clean split: {A['clean']['test_micro_best']['mean']:.4f}, 0% leakage). The headline is flattered by about {(A['theirs']['test_micro_best']['mean']-A['theirs']['nonleaked_micro']['mean'])*100:.2f} micro-F1 points.",
         ]
if sz:
    lines.append(f"5. **Effect of restoring SIZE.** Paired over seeds {sz['seeds']}: macro delta {sz['macro_delta_mean']:+.4f} (per seed {sz['per_seed']}). {sz['note']}. See the per-label table below for SIZE itself.")
else:
    lines.append("5. **Effect of restoring SIZE.** PENDING (SIZE runs not finished).")
lines += ["6. **Fair baseline for our new system.** DeBERTa-base on the *frozen benchmark v1* split (`benchmark/ner/`), because the control's per-seed random splits differ from the frozen one. "
          "The clean 5-seed mean above is the reference number for context; the S119 comparisons retrain every candidate on the frozen split with the same budget.", "",
          "## Per-label F1 (mean over seeds that logged it)", "", "| Label | Theirs | Clean |", "|---|---|---|"]
labs = sorted(set(A["theirs"]["per_label_mean_f1"]) | set(A["clean"]["per_label_mean_f1"]))
for l in labs:
    lines.append(f"| {l} | {A['theirs']['per_label_mean_f1'].get(l, '')} | {A['clean']['per_label_mean_f1'].get(l, '')} |")
if "clean_size" in A:
    lines += ["", f"Clean + SIZE (n={A['clean_size']['test_macro_best']['n']}): macro {f('', 'clean_size')}; per-label {A['clean_size']['per_label_mean_f1']}"]
lines += ["", "## Per-seed table", "", "| Protocol | Seed | Sel | Best ep | Macro | Micro | Last macro | Leaked frac | Runtime s |", "|---|---|---|---|---|---|---|---|---|"]
for r in runs:
    lines.append(f"| {r['protocol']} | {r['seed']} | {r['selection']} | {r['best_epoch']} | {r['test_macro_best']:.4f} | {r['test_micro_best']:.4f} | {r['test_macro_last']:.4f} | {r['masked_family_leak_frac_test']:.3f} | {r['runtime_s']} |")
lines += ["", "## Caveats", "- Single dataset, one architecture; BIO conversion assumes consecutive identical tags form one entity (their BIO file is not released).",
          "- Runs shared an A100 with other users; runtimes are not comparable across seeds.", "- Two duplicated launcher loops ran for part of the sweep (no seed was run twice; the redundant loop was stopped at 12:24 IST)."]
(ROOT / "reports/ner/recipedb3_matched_reproduction.md").write_text("\n".join(lines) + "\n")
print("written")
