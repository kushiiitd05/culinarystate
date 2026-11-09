# 29-diag pre-registration: pre-signature amendment draft (S178)

Status: **AI_DRAFTED / PROPOSED. Not a decision, not a signature, not an approval (D-071).** Written 2026-11-09 by the
S178 PREREG lane (an AI agent) for the 9-10 Nov decision sitting: ops pack item **#7** (T6-C03-R5), the rung-label fix
**T6-C02-R1**, REV-A **Q18** (cap sensitivity) and **Q19 / N6** (imputation-duplicate control), and REV-B **F-08**
(the freeze record name). Nothing here edits `reports/step29/29diag_preregistration_DRAFT.md` or
`registry/freezes/15A-BOOT-2026-11-08.json`.

- Base text amended: `reports/step29/29diag_preregistration_DRAFT.md`, sha256
  `b78704aeab3b4177ed3fea4f5b130e36a5cc2bdac06f371cee0e2965bd03f2a3` (server worktree, 2026-11-09).
- **The signature checker binds this one file.** `evaluation/freeze_records.prereg_signed` compares
  `reports/step29/29diag_prereg_signature.json` with the sha256 of `reports/step29/29diag_preregistration_DRAFT.md`
  only. So the chosen options must be written **into that file** before Kush signs; this draft cannot be signed
  beside it.

## 0. What the sitting must decide

| Id | Question | Options here | Type | Pack rec. |
|---|---|---|---|---|
| D-29-1 | Rung labels (T6-C02-R1) | fix to what `transition/baselines.py` computes (no choice; see the finding) | text fix | adopt |
| D-29-2 | The D2-vs-"ingredient" contrast (#7) | **K-A** add the TB-V0 B-2 ingredient mean and contrast D2 vs B-2 · **K-B** contrast D2 vs D3 as the code defines D3 · **K-C** no contrast | choice | K-A |
| D-29-3 | Split list | **S-A** add S-5 food-group-disjoint · **S-B** list only the splits the runner has | choice | S-A |
| D-29-4 | Cap sensitivity (REV-A Q18) | add (0.95 / 0.975 / 1.0) · leave out | choice | add |
| D-29-5 | Imputation-duplicate control (REV-A Q19) | add · leave out | choice | add |
| D-29-6 | Note on the freeze record (REV-B F-08) | add | text | add |

## 1. Finding the sitting needs first: the draft's rung text does not match the code

The draft (L30-L32) says "D2 = B-3 process-conditioned mean, D3 = B-2 ingredient-conditioned mean with food-group
shrinkage". In `src/culinarystate/transition/baselines.py`:

- `D2ProcessMean` (L47-L58) is the mean per process signature: TB-V0 **B-3**. Correct.
- `D3Hierarchical` (L60-L91) is a **target x process** cell mean shrunk to the process mean (k_proc 5, k_cell 3),
  falling back to process, then target, then global. It **never reads the matrix or food group**. It is not B-2.
- No class in the code is an ingredient- or matrix-conditioned mean. TB-V0 B-2
  (`reports/h_state/transition_bootstrap_v0_contract.md` L17) is **not implemented**.
- The consensus crosswalk wording "B-2 = D3 matrix arm" (T6-C02-R1) therefore has nothing to point at: D3 has no
  matrix arm. Whoever writes `registry/transition_ladder_crosswalk_v1.csv` should map D3 to "B-3 variant (target x
  process, hierarchical)" and B-2 to "not implemented" unless K-A lands.
- Consequence for #7: "D2 process-mean vs D3 ingredient-mean (process information vs food identity only)" is **not
  computable with the current code**. D2 vs D3 as coded compares two process-only models.

Also: the draft lists S-5 "food-group disjoint", but `transition/splits.all_splits` (L100-L111) builds random,
pair_holdout, matrix_disjoint, process_disjoint and, where possible, study_disjoint (TB-V0 S-6). There is no
food-group split in the runner.

## 2. Changes (old text -> new text)

### C1. Header (L3-L6): freeze-record note (REV-B F-08)

```diff
 (D-068). It counts as signed only through `reports/step29/29diag_prereg_signature.json` carrying the SHA-256 of this
 exact text (`evaluation/freeze_records.py`); any edit after signing voids it.
+Amended before signature with the S178 options the 9-10 Nov sitting chose
+(`reports/step29/29diag_preregistration_AMENDMENT_S178_DRAFT.md`). Until Kush signs, this file is a dated AI draft.
+
+Note on the snapshot record: `registry/freezes/15A-BOOT-2026-11-08.json` is named `FREEZE_15A_BOOTSTRAP`, but
+approving it **does not satisfy Step 15a**: Step 15a has a hard dependency on 08a, whose G08-3 FAILED (D-034). The
+approval fixes a snapshot for this diagnostic only.
```

### C2. §3 Ladder (L30-L32): labels as the code computes them

**OPTION K-A (recommended): add the TB-V0 B-2 rung**
```diff
-- Ladder: D0 = B-0 persistence, D1 = B-1 global mean, D2 = B-3 process-conditioned mean, D3 = B-2
-  ingredient-conditioned mean with food-group shrinkage, D5 = DEL-2 HistGB with categorical and mask features. No
-  new model family.
+- Ladder (names as in `transition/baselines.py`): D0 = B-0 persistence; D1 = B-1 global mean; D2 = B-3
+  process-conditioned mean (per process signature); D3 = target x process cell mean shrunk to the process mean
+  (k_proc 5, k_cell 3) — a B-3 variant, **not** B-2, and it does not read the food; D4 = nearest compatible
+  evidence; D5 = DEL-2 HistGB with categorical and mask features; D7 = biased matrix factorisation (for the
+  D7-vs-D1 review only). Added before signature: **B2 = TB-V0 B-2 ingredient-conditioned mean**, the mean per
+  matrix shrunk to its food-group mean, the food-group mean shrunk to the global mean, both with k = 5, falling back
+  to food group, then global, for an unseen matrix. It is a deterministic mean from the TB-V0 contract, written
+  because the code lacked it; no learned model family is added.
```
**OPTION K-B:** the same corrected labels without the B2 rung; the "ingredient-conditioned" wording is deleted.
**OPTION K-C:** corrected labels only, and §4 item 3 below is not added.

### C3. §3 Splits (L33-L35)

**OPTION S-A (recommended)**
```diff
-- Splits: S-1 random (reference), S-2 pair holdout, S-3 matrix-disjoint, S-4 process-disjoint, S-5 food-group
-  disjoint, all grouped by `independence_group`. Seeds and group keys are hashed in the run manifest before
-  scoring.
+- Splits (TB-V0 names; runner names in brackets): S-1 random (reference) [random]; S-2 pair holdout
+  [pair_holdout]; S-3 matrix-disjoint [matrix_disjoint]; S-4 process-disjoint [process_disjoint]; S-5 food-group
+  disjoint [food_group_disjoint, added before signature: grouped by `food_group`]; S-6 study-disjoint
+  [study_disjoint; Phenol-Explorer only, NOT POSSIBLE for USDA and Bognar, which are single source clusters].
+  Seed 7 (the runner default) and every group key are hashed in the run manifest before scoring.
```
**OPTION S-B:** the same list without S-5; the text says "S-5 food-group disjoint is not run".

(The draft's "all grouped by `independence_group`" is also not what the runner does: each split groups by its own
key, e.g. matrix for S-3. The new text drops the phrase.)

### C4. §4: add three diagnostics after L44 (each optional per D-29-2/4/5)

```diff
 2. **Shortcut and D7 ≡ D1 review (`d7_vs_d1_review.md`):** rerun with source family and basis removed, as TB §6
    requires. Explain why DEL-2's D7a matched D1 to four decimals on Phenol-Explorer.
+3. **Process vs food-identity contrast (`contrast_d2_vs_b2.md`) [K-A]:** per source family, on S-3, S-4 and S-6,
+   the paired loss difference D2 (process mean) minus B2 (ingredient mean) on the same test rows, with
+   `evaluation/bakeoff.paired_cluster_bootstrap` (margin 0.0, 2,000 resamples, confidence 0.95, seed
+   `29diag-contrast-2026-11-10`, weighting CLUSTER). Clusters = `independence_group` where a split's test set has
+   >= 2 of them; otherwise (matrix, process) groups, labelled `ONE_LINEAGE_CLUSTER`. Every row reports n_rows and
+   n_clusters; with n_clusters < 10 (K_min, PROPOSED) the row is `DIAGNOSTIC_ONLY` and no direction is read from it.
+   Stated before any run: the contrast is lopsided by construction. On S-3 every test matrix is unseen, so B2 can
+   only use the food-group mean; on S-4 every process is unseen, so D2 can only use the global mean. Each split
+   therefore favours one arm; only S-6 (study-disjoint, Phenol-Explorer) compares them on equal terms.
+   [K-B instead: the same procedure for D2 vs D3, titled "process mean vs target-specific process mean"; it says
+   nothing about food identity.]
+4. **Cap sensitivity (`cap_sensitivity.md`) [REV-A Q18]:** the censored GT_CAP rows (USDA "100", read as >= 0.975)
+   are refitted and rescored with the bound set to 0.95, 0.975 and 1.0; every rung's MAE (all, below cap, at cap) is
+   reported for each value. R6 values are rounded to the nearest 5 %, so differences below 0.025 are not
+   interpreted. The cap is meaningful for true retention only; apparent retention can exceed 1, and R6 does not say
+   which a row is (RT-004).
+5. **Imputation-duplicate control (`duplicate_control.md`) [REV-A Q19 / N6]:** a duplicate group is >= 2 rows of
+   one source family with the same process signature, the same target and the same retention value at the
+   reported precision, on >= 2 distinct matrices. Reported: number of groups, rows in groups, share of rows. Then
+   S-2 and S-3 (and item 3) are rerun with each duplicate group kept inside one fold (fold units = connected
+   components of the split key and the duplicate group), and D2, D3, B2 [K-A] and D5 MAE are shown both ways.
```

### C5. §5 Outputs (L48-L50)

```diff
-`reports/step29/diag/{diag_audit.md, diag_results.md, cap_artefact_stratified.md, d7_vs_d1_review.md}` plus a
-manifest (code hashes, snapshot id, split hashes). The run is deterministic and repeated twice; the two outputs must
-match byte for byte (G15-R). No result changes the TB-V0 contract or any paper-grade Step 29 threshold.
+`reports/step29/diag/{diag_audit.md, diag_results.md, cap_artefact_stratified.md, d7_vs_d1_review.md}` plus, as
+chosen, `{contrast_d2_vs_b2.md, cap_sensitivity.md, duplicate_control.md}` and a manifest (code hashes, snapshot id,
+split hashes, the duplicate-group hash). The run is deterministic and repeated twice; the two outputs must match
+byte for byte (G15-R). No result changes the TB-V0 contract or any paper-grade Step 29 threshold. Any analysis not
+named in this file is `EXPLORATORY_POST_HOC` and is not shown in the talk.
```

Signature section (L52-L55): unchanged. It already uses a hash-bound file.

## 3. Code needed so every diagnostic is computable (Mac agent; not done by this lane)

| Item | Where | Option |
|---|---|---|
| B2 ingredient mean | new class in `transition/baselines.py` (about 20 lines, the D3 pattern with matrix and food_group); add to the 29-diag model list only (DEL-2 history untouched) | K-A |
| Food-group split | `transition/splits.all_splits` or a 29-diag-local list: `grouped_split(df, ["food_group"], "food_group_disjoint", seed)` | S-A |
| Contrast | `evaluation/diag29_runner._family`: per-row losses from `transition.evaluate.abs_errors`, clusters from the `group` column, `bakeoff.paired_cluster_bootstrap` (exists; refuses with TOO_FEW_CLUSTERS below 2) | K-A, K-B |
| Cap sensitivity | `diag29_runner`: set `y_lower` of censored rows to c before fit and before `abs_errors` | Q18 |
| Duplicate groups | union-find as `transition/splits.study_components`; fold assignment by component | Q19 |
| Environment | `D5Boosting` imports scikit-learn (`baselines.py` L142), which is not in the manjot `.venv312`; the run stays on the Mac (install decision #20) | all |

## 4. Hash after lock

```bash
git show <LOCK>:reports/step29/29diag_preregistration_DRAFT.md | sha256sum      # macOS: | shasum -a 256
sha256sum reports/step29/29diag_preregistration_DRAFT.md                        # must match
git diff --exit-code <LOCK> -- reports/step29/29diag_preregistration_DRAFT.md   # must print nothing
sha256sum reports/step29/29diag_preregistration_AMENDMENT_S178_DRAFT.md         # provenance, for the lock record
PYTHONPATH=src python -c "from culinarystate.evaluation.freeze_records import prereg_signed, freeze_problems; print(prereg_signed('.'), freeze_problems('.', '15A-BOOT-2026-11-08'))"
# after Kush's freeze approval (S4) and signature (S5): True []
```
The signature file has exactly three keys: `{"prereg_sha256": "<hash>", "signed_by": "Kush Tokas", "signed_date":
"YYYY-MM-DD"}`. Kush approves the freeze record (three fields, on the Mac) before signing.

Sources: ops pack #7, §3.2, S4/S5; consensus T6-C02-R1, T6-C03-R2, T6-C03-R5, T9-C26-R5; REV-A Q18, Q19, N6;
REV-B F-08; TB-V0 contract L17, L20, L23-L28; `transition/baselines.py`, `transition/splits.py`,
`transition/dataset.py`, `evaluation/diag29_runner.py`, `evaluation/bakeoff.py`, `evaluation/freeze_records.py`.
