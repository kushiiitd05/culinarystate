# 35c recipe rungs build note (synthetic-only)

Code: `src/culinarystate/representation/recipe_rungs.py`; tests: `tests/unit/test_representation_recipe_rungs.py` (toy data only; no real file read, nothing computed on real data). Draft = `reports/step35/preregistration_35_0_v1_draft.md` (D). Allowed pre-signature: specs and unit tests on synthetic fixtures (D s1.3, THR-35P-02).

## API (all pure; UNKNOWN returned as None, never 0)
- R0: `r0_jaccard`, `r0_cosine` (D L192).
- idf_rec: `compute_idf_rec(train_recipes)`, `idf_rec_weight`; named apart from idf_cuis (D L223, THR-35P-23).
- R2-explicit: `r2_tfidf_cosine` (binary tf, IDF from training partition only; D L193); `idf_jaccard` for the kNN alarm (D L195, THR-35P-20).
- R1: `r1_mean_profile(recipe, z)` mean of z_i over profiled ING only, returns coverage and a COVERAGE_LIMITED label (D L197).
- R3: `r3_mass_shares` masked (None) if any mass missing (D L198; real data is NEED_DATA).
- Control: `frequency_only_ranking` (training prevalence, ties by id; D L194).
- Masking: `apply_link_coverage_floor({id: (linked, total)}, floor=0.80)`: below floor or zero lines excluded and counted, never imputed; equal to floor is kept (D L202, THR-35P-19). Caller reports results with and without.
- Metrics: `hit_at_k`, `recall_at_k`, `mrr`, `ndcg_at_k` (binary gain, log2(rank+1)); `frequency_bin`, `frequency_stratified_macro_recall` (edges supplied by caller; D L206).
- Splitter: `split_by_group(recipe->group, seed, fractions=(.6,.2,.2), strata=None)` sha256 hash order per group; result carries `grouping_label=DESCRIPTIVE_CONSERVATIVE_GROUPING`, `headline_eligible=False`, and the D-033 single-reviewer caveat. `assert_group_disjoint` raises `LeakageError` on any group spanning partitions or unassigned recipe (D L208, THR-35P-21, D s1.3).

## Blocked until signature (G35-PRE, THR-35P-01)
Any run on real recipes, mentions parquet, split groups or ledgers; PE-35c; kNN alarm values; LightGBM/logistic baselines; headline claims (wait for 07I-S); R3 data (QNT empty); cross-source identity retrieval (needs 07I-C). Entry-point hash guard is another agent's work.

## Ambiguities (nothing invented beyond these choices, all flagged)
1. The draft does not pin the recipe-level IDF formula; I reused THR-35P-12's `max(0, ln(N/(1+df)))` (N = training recipes). Needs a registry row or confirmation.
2. Unseen-in-train ingredients get df = 0 weight; draft is silent.
3. Draft says R2 "z_i-free" TF-IDF but not tf form; binary tf used.
4. R3 "masked where missing": whole share vector masked if any mass missing (total unknown); per-ingredient partial masking is an alternative.
5. Frequency bin edges are not pinned ("bins by corpus frequency"); the function requires them as arguments.
6. Source-stratum rule (lowest recipe_id member, THR-35P-42) not implemented; callers pass `strata` per group. 60/20/20 is PROPOSED_PILOT; cut by rounding within stratum.
7. Floor at exactly 0.80 is treated as kept ("below" is excluded); zero-line recipes excluded as a separate counted case.
8. Idf-Jaccard with zero union weight returns None (by analogy with THR-35P-12 masking).
9. Gold-firewall / DESIGN_PILOT group exclusion is not done here (needs real id lists); caller must pre-filter.
# AI review follow-up (2026-10-28)

Synthetic regression controls now reject duplicate ranking candidates (which
could inflate nDCG above 1), invalid known masses and incompatible/nonfinite
profile vectors. Missing quantities remain masked. No real recipe was scored.
See `reports/review/AI_REVIEW_2026-10-28.md` and the updated recipe-rung tests.
