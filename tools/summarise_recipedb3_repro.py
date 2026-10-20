#!/usr/bin/env python3
"""S116: summarise the RecipeDB3 matched reproduction (A100) into reports/ner/recipedb3_matched_reproduction.md.

  scp 'vinayak-server:/home/vinayak23597/Kush/culinarystate-ner-rdb3/runs/*.json' data/interim/recipedb3_repro/
  /opt/anaconda3/bin/python tools/summarise_recipedb3_repro.py
Reads theirs_seed*.json (their protocol: random 80/20 split, selection on TEST), clean_seed*.json (family-grouped 80/10/10, selection on DEV),
optionally clean_size_seed*.json. Status is COMPLETE only with 5 seeds per main protocol; otherwise PARTIAL. No claim beyond the numbers (H6).
"""
import glob
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "data" / "interim" / "recipedb3_repro"
OUT = ROOT / "reports" / "ner" / "recipedb3_matched_reproduction.md"
REPORTED_THEIRS_MACRO = 0.9557          # their notebook headline (epoch 15, selection on test), see recipedb3_vulnerability_analysis.md


def ms(xs):
    return (round(st.mean(xs), 4), round(st.stdev(xs), 4) if len(xs) > 1 else None) if xs else (None, None)


def load(pattern):
    return [json.loads(Path(f).read_text()) for f in sorted(glob.glob(str(RUNS / pattern)))]


def row(label, runs, key):
    m = [r[key]["macro_f1"] for r in runs if key in r]
    u = [r[key]["micro_f1"] for r in runs if key in r]
    (mm, ms_), (um, us) = ms(m), ms(u)
    return f"| {label} | {len(m)} | {mm} +- {ms_} | {um} +- {us} |"


def per_label(runs, key="test_at_best"):
    labs = sorted({k for r in runs for k in r.get(key, {}).get("per_label", {})})
    return {l: ms([r[key]["per_label"][l]["f1"] for r in runs if l in r.get(key, {}).get("per_label", {})])[0] for l in labs}


def main():
    theirs, clean, size = load("theirs_seed*.json"), load("clean_seed*.json"), load("clean_size_seed*.json")
    complete = len(theirs) >= 5 and len(clean) >= 5
    L = ["# RecipeDB3 NER matched reproduction (A100)", "", f"Status: **{'COMPLETE' if complete else 'PARTIAL'}** - theirs seeds {len(theirs)}/5, clean seeds {len(clean)}/5, clean+SIZE seeds {len(size)}.",
         "This is an apples-to-apples BASELINE (DeBERTa-base, 15 epochs, lr 5e-5, bs 16, max_len 128), NOT our final NER model. No 'beats RecipeDB3 / CoSyLab / SOTA' claim before H6.", "",
         "## Headline (entity-level seqeval; mean +- sd over seeds)", "| protocol / selection | n seeds | macro-F1 | micro-F1 |", "|---|---|---|---|",
         row("theirs: random 80/20, selected on TEST (best epoch)", theirs, "test_at_best"), row("theirs: same runs, LAST epoch (no test selection)", theirs, "test_at_last"),
         row("clean: grouped 80/10/10, selected on DEV, TEST at best-dev epoch", clean, "test_at_best"), row("clean: LAST epoch", clean, "test_at_last"),
         row("clean + SIZE label", size, "test_at_best"), "", f"Reported by RecipeDB3 notebook: macro-F1 {REPORTED_THEIRS_MACRO} (selection on test)."]
    if theirs:
        d = [r["test_at_best"]["macro_f1"] - REPORTED_THEIRS_MACRO for r in theirs]
        L += ["", "## Q1 Reproduction", f"Our matched runs differ from the reported macro-F1 by {ms(d)[0]:+} (sd {ms(d)[1]}) across seeds; seed 48 is their random_state."]
    if theirs and clean:
        a, b = ms([r["test_at_best"]["macro_f1"] for r in theirs])[0], ms([r["test_at_best"]["macro_f1"] for r in clean])[0]
        a2, b2 = ms([r["test_at_last"]["macro_f1"] for r in theirs])[0], ms([r["test_at_last"]["macro_f1"] for r in clean])[0]
        L += ["", "## Q2/Q3 What changes under proper dev/test separation and family grouping",
              f"theirs(best-on-test) {a} -> theirs(last epoch) {a2} isolates test-selection; clean(best-on-dev) {b} / clean(last) {b2} adds grouped splitting. "
              f"Difference theirs-best minus clean-best = {round(a - b, 4)} macro-F1 (reported only; seeds and splits differ, so the two effects are not separable without a grouped/theirs 2x2)."]
    lk = [r["test_at_best_leaked"]["macro_f1"] for r in theirs if "test_at_best_leaked" in r]
    nl = [r["test_at_best_non_leaked"]["macro_f1"] for r in theirs if "test_at_best_non_leaked" in r]
    if lk and nl:
        L += ["", "## Q4 Leaked vs non-leaked test rows (masked-sentence family also in train), theirs protocol",
              f"leaked fraction of test: {ms([r['leaked_frac_of_test'] for r in theirs])[0]}; macro-F1 leaked {ms(lk)[0]} vs non-leaked {ms(nl)[0]}.",
              f"Exact-duplicate fraction of test in train: {ms([r.get('exact_duplicate_frac_of_test') for r in theirs if r.get('exact_duplicate_frac_of_test') is not None])[0]}."]
    if size:
        L += ["", "## Q5 SIZE included", f"clean+SIZE macro-F1 {ms([r['test_at_best']['macro_f1'] for r in size])[0]} vs clean {ms([r['test_at_best']['macro_f1'] for r in clean])[0] if clean else 'n/a'}; per-label SIZE F1 in the table below."]
    if clean or theirs:
        L += ["", "## Per-label F1 (test at selected epoch, mean over seeds)", "| label | theirs | clean | clean+SIZE |", "|---|---|---|---|"]
        pt, pc, ps = per_label(theirs), per_label(clean), per_label(size)
        for l in sorted(set(pt) | set(pc) | set(ps)):
            L.append(f"| {l} | {pt.get(l, '-')} | {pc.get(l, '-')} | {ps.get(l, '-')} |")
    L += ["", "## Q6 Is DeBERTa+CRF still the strongest justified span-model candidate?",
          "Not answered by this report: these runs are DeBERTa-base without CRF on RecipeDB3. TASTEset evidence (separate, exact F1): DeBERTa-v3-large+CRF 0.933, CRF significant (p=0.003). A CRF/large run on the clean RecipeDB3 split is the next NER block, not started."]
    allr = theirs + clean + size
    if allr:
        L += ["", "## Run metadata", f"model {allr[0].get('model')}; gpu {sorted({r.get('gpu') for r in allr})}; code revision {sorted({r.get('code_revision') for r in allr})}; torch {sorted({r.get('torch') for r in allr})}; runtime per run (s) {sorted(r.get('runtime_s', 0) for r in allr)}",
              f"selection rule: theirs = {sorted({r['selection_split'] for r in theirs})}, clean = {sorted({r['selection_split'] for r in clean})}; skipped (word/tag length mismatch) {sorted({r.get('skipped_len_mismatch') for r in allr})}"]
    OUT.write_text("\n".join(L) + "\n")
    print(OUT, "COMPLETE" if complete else "PARTIAL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
