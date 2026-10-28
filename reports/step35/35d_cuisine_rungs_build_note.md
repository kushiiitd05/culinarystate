# 35d cuisine rungs: build note (pre-signature, synthetic-fixture only)

Code: `src/culinarystate/representation/cuisine_rungs.py`. Tests: `tests/unit/test_representation_cuisine_rungs.py` (12, synthetic data only). Draft basis: 35.0 v1 draft section 7 (UNSIGNED), D-036, D-037. Permitted by section 1.3 / THR-35P-02 (specs and unit tests on synthetic fixtures). No real recipe, ledger or registry/cuisine file was opened; no statistic on real data was computed.

## API (pure functions, in-memory input only)
- `LabelledRecipe(recipe_id, ingredients, label_level, cuisine)`; `build_corpus(recipes, strict=False)` keeps CUISINE-level only; REGION / UNKNOWN / CONFLICTING / NEEDS_HUMAN are dropped and counted in `corpus.excluded` (never guessed). `strict=True` raises on REGION. `require_single_cuisine` raises on REGION (D-037).
- `c0_prevalence(corpus, exclude=())`: P(i|c).
- `c1_specificity(corpus, exclude=())`: A_i^c = P(i|c) - (1/(K-1)) sum_{c'!=c} P(i|c'); K = retained classes after `exclude`; needs K >= 2; computed over the full retained vocabulary (absent ingredient P = 0, so A can be negative).
- `idf_cuis(corpus, exclude=())`: cuisine-level IDF, ln(K / n cuisines containing i). Distinct from recipe-level `idf_rec`.
- `c2_motifs(corpus, cuisine, min_pair=20, min_triplet=10)`: motifs with support and NPMI, inside one cuisine. `npmi(n_joint, n_each, n_total)`.
- Leakage: `assert_no_heldout(used_cuisines, heldout)` and `assert_weight_not_target_derived(weight_source, predicting)` raise `LeakageError`; `exclude=` removes a held-out cuisine from every feature and from K.
- Nulls: `curveball(incidence, seed, n_trades)` (row and column sums preserved, input not mutated); `null_draw(incidence, model, seed, categories)` with `NULL_MODELS = (U, F, C, FC)` = draft M0 / MF / MC / MFC (recipe size preserved; C and FC also preserve per-recipe category counts; F and FC weight by ingredient frequency).

## Definitions pinned, and SSOT conflict
- C1 uses K-1 with K = number of retained cuisine classes (draft 7.1). SSOT writes the denominator as C-1 at L13874 and K-1 at L14129; the draft pins K-1 (one definition). Not re-opened here.
- NOT defined in the draft, chosen here and flagged for sign-off: (1) `idf_cuis = ln(K / df)` with cuisines as documents; (2) NPMI = ln(p_joint / prod p_i) / -ln p_joint, joint p = 1 returns 1.0, triplet NPMI is the direct generalisation; (3) null_draw samples without replacement per recipe; MX and the Curveball-calibrated Z p-value path (THR-35P-37) are not implemented.
- Support thresholds are parameters; 20 / 10 are defaults from THR-35P-24 (draft, unsigned).

## Blocked until signature (G35-PRE, THR-35P-01)
- Any run on real labels/recipes; the evaluation entry point (must sit behind prereg_guard); Food.com tag-to-cuisine map and ontology review (D-036/D-037 mapping still DRAFT_PENDING_SIGN); THR-35P-22 class eligibility (>= 100 recipes and >= 2 source families), source-identity baseline, S-cui-src / S-cui-hold splits, classifier, metrics, BH/null-draw counts B, and the open choice for CONFLICTING recipes (dropped and counted here).
- Headline claims also wait for the 07I-C split_group_id (THR-35P-03).
# AI review follow-up (2026-10-28)

NPMI now rejects impossible/nonfinite support counts rather than returning a
score. The existing direct triplet generalisation can exceed 1; its formula is
unchanged and explicitly queued for expert review. Existing CONFLICTING
exclusion/counting agrees with D-040. No real cuisine score was computed.
See `reports/review/AI_REVIEW_2026-10-28.md`.
