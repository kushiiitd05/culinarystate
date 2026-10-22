# STEP 07I -- pre-registration (written and committed BEFORE any identity/family computation)

Everything below is fixed in advance. None of it may be changed after the global duplicate/family counts are seen. The resulting database size is a FINDING (not a target). No threshold was chosen to reach a particular size.

## 1. Levels
- **Level A DUPLICATE_GROUP (deterministic only):** union of records linked by (i) equal `raw_hash` (EXACT_BINARY_COPY), (ii) equal `rec_content_sha256` across different recipe ids (EXACT_BINARY_COPY), (iii) equal `norm_text_hash` = sha256 of lower-cased title+ingredient lines+steps with all non-alphanumerics removed (EXACT_NORMALIZED_COPY), (iv) A1 records sharing the same `canonical_url` with different `source_url` (MIRRORED_COPY, explicit source identifier). Every recipe belongs to exactly one group (singletons included). **No near-duplicate is auto-coalesced** (no calibrated threshold exists; the human calibration packet is created but unlabeled).
- **Level B RECIPE_FAMILY (provisional, uncalibrated, conservative):** built on duplicate-group representatives only, with the rule in section 3. Flag `family_method=PROVISIONAL_STAR_V1`, `calibrated=false`. Members are never merged or deleted.
- **Level C DISH_FAMILY_CANDIDATE (exploratory):** families sharing the same dish-name key (section 4); provenance class INFERRED_CANDIDATE; never collapsed.

## 2. Relation classes (controlled)
EXACT_BINARY_COPY, EXACT_NORMALIZED_COPY, MIRRORED_COPY, NEAR_DUPLICATE_SAME_RECIPE (reserved; unused until calibrated), SCALED_VARIANT, MINOR_FORMULATION_VARIANT, SAME_DISH_VARIANT, RELATED_DISH, DISTINCT, UNCERTAIN. Only the first three coalesce. Candidate pairs carry status `CANDIDATE_NEAR_DUPLICATE` plus a descriptive hint (SCALED_VARIANT_HINT when >=3 shared mass-grounded ingredients have proportional masses with CV<=0.10 and median ratio outside [0.87,1.15]).

## 3. Candidate generation, features, ranking score, provisional family rule
- Candidates (on duplicate-group representatives): (a) equal normalized title (blocks >300 are sub-blocked by the rarest shared ingredient token), (b) instruction-shingle MinHash LSH (64 perms, 16 bands x 4 rows, word 4-grams), (c) ingredient-token MinHash LSH (32 perms, 8 bands x 4 rows), (d) existing REC `family_id` co-membership. LSH buckets larger than 200 are skipped and counted (reported as a recall diagnostic).
- Pair features (missing stays missing, never 0, with explicit `*_missing` flags): title token Jaccard; title char-trigram Jaccard; ingredient-id Jaccard; ingredient-token Jaccard; IDF-weighted ingredient-token Jaccard; ingredient multiset similarity; process-set Jaccard; ordered process-sequence similarity (LCS/max length); instruction-shingle MinHash estimate; condition-profile Jaccard (rounded T/time canonical values); quantity-profile cosine on shared mass-grounded ingredients and the scale ratio; same_source; cross_source; locale agreement; explicit cuisine agreement.
- **Ranking score** = weighted mean of the AVAILABLE features with fixed weights: title_token 0.15, ingredient_idf 0.30, ingredient_id 0.10, multiset 0.10, instruction_shingle 0.20, process_seq 0.05, condition 0.05, quantity_profile 0.05 (weights renormalised over available features). It ranks pairs; it is NOT a duplicate decision.
- **Provisional family edge (all must hold):** (1) both records have >=4 ingredient tokens; (2) IDF-weighted ingredient-token Jaccard >= 0.80; (3) title token Jaccard >= 0.50; (4) support from procedure: instruction-shingle estimate >= 0.30 OR ordered process-sequence similarity >= 0.70 with both having >=3 mapped processes; (5) not (both have explicit cuisine and cuisines differ).
- **Clustering:** star clustering, centers chosen by (degree desc, representative recipe_id asc); a member joins only if it has a DIRECT edge to its center (no chaining). Edge confidence = ranking score to center; a cluster is flagged HETEROGENEOUS if any member-to-center score < 0.60 or the cluster spans >2 usage classes.

## 4. Dish-family candidates
Key = normalised title with generic modifier words removed {easy, quick, best, simple, homemade, classic, perfect, the, a, my, our, recipe, recipes, how, to, make, delicious, super, favourite, favorite, ultimate, authentic, traditional, old, fashioned, style} and tokens sorted; keys with >=4 characters. Families with the same key (>=2 families) form a candidate; label INFERRED_CANDIDATE.

## 5. Consensus
Support level of a field value in a multi-member family (n members): UNANIMOUS if support fraction = 1.0 and n>=2; HIGH_SUPPORT >= 0.80; MAJORITY >= 0.50; SINGLETON_VARIANT if support count = 1 (n>=2); MINORITY_VARIANT otherwise; CONFLICTING for condition-value fields with >=2 distinct values and top value fraction < 0.50. Field support rows are written for multi-member families only (singleton families are trivially supported by their one member; the consensus table has one summary row for every family). Quantities: distributions over mass-grounded values only; incompatible bases/units are never averaged. Confidence vector (not multiplied): source_count, independent_source_count (distinct source ids), member_count, agreement_fraction (mean ingredient support), structured_field_coverage, mapping_quality (mapped ingredient fraction), source_usage_quality (best usage class), duplicate_certainty (min relation class), human_verification_status.

## 6. Representative recipe
Deterministic max of the tuple: (quality tier rank GOLD_PENDING>SILVER_AUTO>SOURCE_RAW, usage-scope rank, has_instructions + has_ingredients + has_quantities + has_conditions completeness, ingredient count (capped 30), step count (capped 30), -recipe_id). Never shortest text / first row.

## 7. Views
RECIPE_SOURCE_ALL = every indexed record (with its usage scope); RECIPE_DEDUP_EXACT = one representative per deterministic group; RECIPE_FAMILY_VIEW = family + members; RECIPE_MODEL_ELIGIBLE = `training_allowed == YES` in the usage registry (no licence is invented); RECIPE_RELEASE_ELIGIBLE = `raw_redistribution_allowed == YES` (CONDITIONAL reported separately); RECIPE_GOLD = records in the Gold index.

## 8. Calibration packet
~400 unlabeled pairs, stratified: very-high / high / boundary-around-0.80 IDF-ingredient / moderate scores, same-title-low-structure, cross-source, same-source, cultural/regional hints, scaled recipes, high-ingredient-overlap-different-process, high-text-overlap-different-ingredients. Score and stratum are hidden from reviewers (separate sealed key). Labels: SAME_RECIPE_COPY, SAME_RECIPE_MINOR_VARIANT, SAME_DISH_DIFFERENT_RECIPE, RELATED, DISTINCT, UNCERTAIN. No label is invented.

## 9. Not allowed
Editing the frozen Step-07H-R parser/normalizer/schema/mappings; tuning on family results; deleting or rewriting REC; promoting Gold to relatives; inventing licences; starting Step 08.

## Amendment A1 (committed BEFORE the full-corpus identity run; feasibility only)
A 1-in-20 sample test showed the ingredient-token LSH (8 bands x 4 rows) producing ~660k candidate pairs from 30k recipes, dominated by tiny ingredient sets, which scales to an infeasible number of pairs on 612k recipes. Amended candidate-generation parameters only: ingredient-LSH is restricted to representatives with >=4 ingredient tokens (consistent with the family rule's own >=4 requirement) and its bucket cap is 50 instead of 200 (steps-LSH cap stays 200). The amendment changes which pairs are *retrieved* for scoring; it does not change any decision rule, weight or threshold, was made from computational blow-up on a sample (no family/duplicate counts were consulted), and skipped buckets are reported as a recall diagnostic.
