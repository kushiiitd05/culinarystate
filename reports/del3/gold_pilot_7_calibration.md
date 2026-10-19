# Gold pilot — 7-recipe calibration round (S102, 2026-10-19)

**Status: BLOCKED_HUMAN.** The seven recipes are fixed and recorded; Kush and Parv have not annotated them. Nothing below is a result.

## Correction accepted
S101 recommended "5 recipes, one per stratum" but pilot_20 has 7 strata (baking, drain_discard, indian, multi_component, random,
reserve_split, simple). The calibration round is therefore **7 recipes, one per stratum**.

## Selection (fixed before any annotation, not by difficulty)
Rule: sort the frozen manifest by (stratum, recipe_id); take the first recipe in each stratum. Recorded in the committed, text-free file
`annotation/gold/pilot_7_calibration_manifest.csv` (id, stratum, family, raw-content SHA256, handbook version).

| stratum | recipe_id | family | ingredient lines | steps |
|---|---|---|---|---|
| baking | R003595 | FAM-R003595 | 14 | 8 |
| drain_discard | R002919 | FAM-R002919 | 9 | 1 |
| indian | R000387 | FAM-R000387 | 12 | 2 |
| multi_component | R002843 | FAM-R002843 | 5 | 7 |
| random | R000312 | FAM-R000312 | 9 | 2 |
| reserve_split | R008469 | FAM-R008469 | 11 | 4 |
| simple | R001894 | FAM-R001894 | 5 | 2 |

These 7 are annotated under handbook v1 + Addendum A. The remaining 13 are annotated after the gate below, under whatever handbook version
results; any rule change is logged and not applied retroactively to these 7.

## Tooling change (minimal)
`tools/gold_pilot_agreement.py` gains `--only id,id`, `--calibration` (the frozen 7) and `--tag`. Default is still all 20. A subset run
requires DONE + valid files from both annotators for the selected recipes only and never reads other recipes. Metric and disagreement logic
are unchanged. It also writes per-category disagreement **rates** (count / relevant units: spans, events, lines, coref mentions, state
fields) and a mechanical gate flag (> 20%). Tests: subset ignores unfinished non-selected recipes; selected-unfinished blocks (exit 2);
default stays all-20; calibration flag uses the frozen list; unknown ids rejected; identical documents give F1 1.0 on every metric (this
caught a wrong dictionary key in the first draft, fixed before commit).
Current state: `--calibration` exits 2 (14 of 14 files not DONE); the all-20 run exits 2 (40 of 40).

## What the humans do
Annotate the same 7 recipes independently in `annotation/gold/pilot_20/Kush|Parv/`, run `validate` and `replay` on each, set `DONE`.
No AI completes, repairs, infers or signs any annotation. Then run `tools/gold_pilot_agreement.py --calibration`.

## Gate rules (declared now)
Report span F1 (exact/relaxed, per label), canonical-link agreement, UNKNOWN disagreement, process-link F1, event F1 (strict/loose),
relation F1, structural merge/split/reserve/recombine F1, coref B³, intermediate-entity F1, alive-entity F1, state-field agreement,
replay consistency, and counts and rates for the nine disagreement categories. Verdicts: **HANDBOOK_REVISION_REQUIRED** if a category
exceeds 20% of its relevant units or a systematic unresolved rule is visible in the table (human reading, not only the flag);
otherwise **CALIBRATION_PASS** and annotate the remaining 13. Proposed clarifications only; prior annotations are never silently changed.

## Final answers
1. Selected 7: R003595 (baking), R002919 (drain_discard), R000387 (indian), R002843 (multi_component), R000312 (random), R008469 (reserve_split), R001894 (simple)
2. Completed Kush / 7: **0**
3. Completed Parv / 7: **0**
4. Agreement metrics: none (BLOCKED_HUMAN)
5. Systematic disagreement categories: not measurable yet
6. Handbook gate verdict: **pending** (BLOCKED_HUMAN)
7. Next: **Kush and Parv annotate the 7 recipes, validate and replay each, then run `tools/gold_pilot_agreement.py --calibration`.**
