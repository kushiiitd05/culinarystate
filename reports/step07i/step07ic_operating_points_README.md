# 07I-C operating points and recipe split groups (2026-10-27)

**Basis: SINGLE-REVIEWER (Kush) adjudicated labels, D-033.** All precision/recall figures below are single-reviewer-basis estimates; blind agreement was below target (Y_copy kappa 0.571, Y_dish 0.588 vs 0.70). The 0.88 figure of D-033 is Kush-declared, not computed. Parv's agreement is relayed, not verified.

Tool: `tools/step07ic_operating_points.py`; tests: `tests/unit/test_step07ic_operating_points.py`. Outputs (new dir `ledgers/recipe_identity_v2/`): `recipe_split_groups_v1.parquet`, `op_selection_report_v1.json` (sha256 of every input, per-stratum n, folds, ambiguities), `op_merge_pairs_v1.parquet`. Sealed key sha256 before = after = `f7973d7d...` (unchanged). No existing file touched.

Method: 400 pairs, 43 UNCERTAIN excluded (THR-07IC-03), 357 used; joined to the sealed key for score/stratum. Stratum weight = pool/n_used; Wilson 95% on weighted proportion with Kish n_eff. Cut rule: predict positive iff score >= cut.

| Operating point | Target | Cut | Estimate (95% Wilson) |
|---|---|---|---|
| OP-MERGE (THR-07IC-05/07) | Y_copy | 0.8469 | precision 0.974 [0.900, 0.994]; recall 0.118 [0.024, 0.420] (unweighted recall 0.53) |
| OP-SPLIT (THR-07IC-06/08) | Y_dish (RELATED=0) | 0.1765 (lowest observed score) | recall 1.00 [0.944, 1.00]; precision 0.88 [0.79, 0.94] |

OP-MERGE LB 0.9003 only just clears 0.90 and the recall CI is very wide. OP-SPLIT: weighted recall falls to 0.82 at cut 0.19, 0.55 at 0.25, 0.11 at 0.5, so the 0.95 target forces the lowest cut: every kept candidate pair becomes a split edge. Grouped 5-fold CV (diagnostic): OP-MERGE out-of-fold cut found in 1/5 folds only (unstable); OOF precision 0.91 [0.69, 0.98].

## Split groups (finding, not a target)
Edges = exact duplicate groups + candidate pairs with score >= OP-SPLIT cut (727,224 pairs). 612,782 recipes -> 450,775 split groups; largest 42,351 (6.9%); 45,154 groups of size >=2; p99 = 6. Fallback grouping of `tools/step16b_build_frame.py` (dup+family+dish+title components): 456,518 groups, largest 292; the two partitions are not nested (113,541 recipes sit in a fallback group split by split_group_id; 116,987 in a split group spanning several fallback groups), so split_group_id is not a refinement or coarsening of the fallback. `split_group_id` = `SPLITGRP-REC-<min recipe_id>`; flags `calibrated=true`, `single_reviewer_basis=true`.
OP-MERGE: 4,920 candidate pairs at/above cut (non-transitive, non-destructive; no merge applied).

## CONTRACT-AMBIGUITIES (full list in the JSON)
CA-1 target per operating point (used Y_copy / Y_dish primary; alternates in JSON: Y_dish sensitivity gives the same cut). CA-2 "grouped CV, calibrator" is vacuous for a single score cut; selected on all labels, CV diagnostic only. CA-3 candidate_pairs_v1 holds only pairs kept at score>=0.50 (or family/title flags); the OP-SPLIT cut of 0.176 is below that, so recall is relative to the kept set and corpus-level recall is lower. CA-4 strata treated as disjoint. CA-5 THR-06 is a target with CI, not pass/fail. CA-6 label reasons are "AI draft" text (anchoring risk).

## Downstream
07I-C numerical outputs now exist, so the hard dependency of Steps 16-20/35/36 on `recipe_split_groups_v1` is satisfiable mechanically, but the caveat travels: single-reviewer basis, blind kappa below THR-07IC-04, no sealed v2 recall probes, OP-SPLIT recall unverified beyond the kept pair set. Plan fail-action wording ("near-duplicate leakage not controlled") applies in claims until v2 probes / second-reviewer evidence exist.
