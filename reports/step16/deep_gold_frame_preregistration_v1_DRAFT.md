# Step 16b — Deep-Gold sampling-frame pre-registration (v1 DRAFT)

**Status: DRAFT, unsigned, design only.** Written 2026-10-27, before any recipe is drawn. Nothing here is a Kush or Parv decision until signed. No sample was drawn, nothing was annotated, no recipe text was opened (ids, source labels, structural counts, group keys and hashes only; `title_key` is used inside the generator only as a hash-equality edge and is never printed or written). Shared with 19-D / 19-pilot (`reports/step19/deep_gold_pilot_design_v1_draft.md`); where the two differ, the Step 19 draft's numbers are kept and this file says so.

## 1. Eligible sources and licence limits

| Source family | In base | Eligible for frame | Usage class (`registry/recipe_source_usage_registry_v1.csv`) | Rule |
|---|---|---|---|---|
| A1_BBC_GOOD_FOOD (SRC-000002) | 11,934 | yes | LOCAL_RESEARCH_ONLY | text stays in git-ignored `data/raw/`; no release; training UNKNOWN (H2) |
| FOODCOM (UNREGISTERED:FOODCOM_KAGGLE_IRKAAL) | 522,517 | yes, with caveat | LICENCE_UNVERIFIED (source UNREGISTERED) | LOCAL research use only (S116 Gate 1); eligibility screen HV-005 unconfirmed; Gold text release blocked until H2 |
| WIKIBOOKS (SRC-000140) | 3,676 | yes | REDISTRIBUTABLE_WITH_ATTRIBUTION (CC BY-SA) | release only after H2 review |
| GUTENBERG_SEGMENT | 73,955 | no | PUBLIC_OPEN | 0 ingredient lines in every row; cannot fit the gold-1.0 template (Step 19 draft F4). Logged as a representability gap, not sampled |
| TASTESET | 700 | no | LICENCE_UNVERIFIED | 0 steps; same reason |

No external LLM service sees any recipe text at any stage of the frame, the draw or the annotation. The frame file holds no text. The Step 16 card also lists Gutenberg PD as a possible pilot text source; this pre-registration follows the Step 19 draft and excludes it for the structural reason above (open question Q2).

## 2. Eligibility (fixed before the frame was built; not tuned to outcomes)

A recipe is in the frame if all hold, in this order: source in the three eligible families; `has_ingredients` and `has_instructions`; it is the exact-duplicate representative of its group (`recipe_id == representative_recipe_id`, `recipe_identity_fk_v1`); 4–20 ingredient lines; 2–15 steps; and it is not in a group containing an excluded id (section 5). "Text present on the annotating machine" cannot be checked without reading text and is deferred to packet building.

## 3. Strata (only those named by the Step 16 card or the Step 19 draft)

- Source family (Step 19 quota 6 / 10 / 4 BBC / FOODCOM / WIKIBOOKS applies at draw time, not here).
- Complexity tier: c = ingredient lines + 2 x steps; LOW c <= 14, MID 15–24, HIGH >= 25 (THR-19P-06).
- Existing 7 dish-type strata. Structural ones are computed: `simple` (<= 3 steps and <= 6 lines), `indian` (an explicit `cuisine_if_explicit` token equal to Indian, South Indian or Indic; Food.com has no label), `random` (every row). The four regex strata (baking, drain_discard, reserve_split, multi_component) need recipe text, which was NOT read. They are not in the frame: column `text_regex_strata_status` = `NOT_COMPUTED_TEXT_NOT_READ`. They must be added in a separate, hash-committed step run by the person who may read text, using the regexes of `tools/make_gold_batch.py` unchanged (Step 19 draft section 4.4). Until then the regex cells cannot be drawn.

No stratum was added.

## 4. Unit of independence

The unit is the recipe `split_group_id` from the 07I-C identity layer (R-08). **That layer does not exist yet**: no `recipe_split_groups_v1` file is in the repo, so `split_group_id` is empty in all rows and every row uses the conservative fallback (`group_basis = FALLBACK_COMPONENT_V1`).

Fallback grouping, exactly: connected components over the whole base (612,782 recipes), where two recipes are linked if they share any of: `duplicate_group_id` (`recipe_identity_fk_v1`), `recipe_family_id` (provisional star family, same file), `dish_family_candidate_id` (same file, null ignored), or the same non-empty normalised `title_key` (`recipe_identity_features_v1`). `group_id` = `FBG-` + the smallest `recipe_id` in the component (string order). `group_size` is the component size in the full base. Files are read only. Components are built over the full base, not only the eligible rows, so an excluded recipe's group is excluded whatever its members' sources. Largest component: 292 recipes (no giant component). No size cap or sub-blocking rule is applied: the stricter reading (whole component) is used, which avoids the tuning issue in Step 19 draft D19-17.

When 07I-C groups exist, each drawn recipe's 07I-C group is looked up and the whole group is locked; the fallback `group_id` is kept as an additional column.

**SINGLE-REVIEWER-BASIS CAVEAT (D-033).** Any grouping derived from 07I-C inherits the 07I-C label basis: the 0.88 agreement is a Kush-declared adjudicated-basis figure, not computed by any file and not an inter-reviewer kappa (agreement with Kush's own labels is 1.0 by construction). The blind figures stay in the record: Y_copy kappa 0.571, Y_dish 0.588 (`reports/step07i/step07ic_reviewer_agreement_v1.json`), below the 0.70 target. The frame as built uses no 07I-C label at all, only the unlabelled 07I-R structure, so it is not affected today. Any later 07I-C split group must be reported next to this caveat.

## 5. Exclusions (before any draw)

Excluded by id and then by whole fallback group: the 50 ids of `gold_recipe_index_v1` (40 AI-assisted + 10 expansion reserves; includes the 7 calibration recipes) and the 120 distinct recipes in the S116 screening log (only the `source_recipe_id` column was read). The union is 140 ids in 140 distinct components (the two sets overlap on 30). Normalised-title twins are caught by the title edge. These groups are removed from the frame (318 recipes at the last funnel step).

## 6. DESIGN_PILOT tagging

Every pilot recipe and its whole group (fallback group now, 07I-C group when it exists) is tagged `DESIGN_PILOT` in the draw manifest: dev and error analysis only; never sealed test, calibration or training; never reused as an independent test item; excluded from Silver, Gold-Light, demo and retrieval exemplar sets (THR-19P-30). The tag is not in the frame (nothing is drawn yet).

## 7. Hash commitments

| What | When | By whom |
|---|---|---|
| sha256 of the frame CSV (`frame_sha256`), of `tools/step16b_build_frame.py`, of the six input files (section 9), of this document | after Kush has read and approved this document, before any seed exists | the coding agent computes and writes them; Kush signs (H4/H5) and commits from his own account |
| `nonce` string | written into the signed 01.6 threshold row BEFORE the frame is rebuilt or re-hashed | Kush (the agent never chooses it) |
| seed = first 8 bytes of SHA-256(`frame_sha256` + wave label + `nonce`) | after the above are committed | derived, not chosen |
| draw manifest (text-free: ids, cells, tags, seed, reserves) and its sha256 | at the draw, before any packet is built | script output, committed by Kush |

A changed frame hash invalidates the nonce and restarts the sequence.

## 8. Draw procedure (specified, NOT executed)

Per Step 19 draft section 4.5: inside each fixed cell, shuffle eligible candidates with a stable seeded order; skip any whose group is already used; take the first; the next two are ordered reserves; at most one recipe per group. P1 cells and P2 coverage rule are as in that draft. Same seed and same frame give the same draw (frame sorted by `recipe_id`, stable shuffle). The draw script does not exist yet.

**Not done yet:** no draw; no seed or nonce; regex strata not computed; no `DESIGN_PILOT` tags; 07I-C split groups absent (so the single-reviewer caveat is only a forward flag); no signature; the thresholds and quotas are `PROPOSED_PILOT` in the Step 19 draft and unregistered; Food.com eligibility (HV-005) and H2 unresolved; text-presence check deferred.

## 9. Frame produced (one run, `tools/step16b_build_frame.py`)

File `registry/recipe_semantics/deep_gold_sampling_frame_v1_DRAFT.csv`, 431,458 rows, 19 columns, ids and structural counts only.
**sha256 `513fda2858a19a57d27c772c6f8112aecd412b78437f4aac3d22436ca71266b0`** (identical on three runs and in the test's two rebuilds).
Generator sha256 `99c3cfba51deb64f90f5c264e64c36892969e0bbfe092deee6eb1f6083394b76`. Inputs (sha256 unchanged before/after, tested): `recipe_identity_fk_v1.parquet` e3b2a9aef6afab4e609366a139b201399c4a810e919924ccf26322282fdf5a53, `recipe_identity_features_v1.parquet` 10c15cd1b4169ac10d96ab3a745bc7c4d309a848009df3ad11a4a4a871e254f9, `gold_recipe_index_v1.parquet` 4832d7a91bcfd01bd32d643e84f5dcc3afef9373ac4d65fe360390eff62429cb, `recipe_base_v1.parquet` 5545da589d9c77891d3aefcebf21374d75a03632d14a4e8231603c68c9c824f0, screening log b1d4140da7dec38ef0613a0d7af488e67b2da67d72e2796360685f6199133511, usage registry 325238d610fffdcaffec768c4ee26abd3fe6a9f71396a3987b97f0007793f1c7.

Funnel (cumulative): source 538,127 -> has text flags 535,907 -> exact-dup representative 530,725 -> 4–20 lines 467,084 -> 2–15 steps 431,776 -> not in excluded group 431,458.

| Source | Rows | LOW | MID | HIGH | simple | indian |
|---|---|---|---|---|---|---|
| A1_BBC_GOOD_FOOD | 10,581 | 4,061 | 5,413 | 1,107 | 1,495 | 342 |
| FOODCOM | 417,710 | 79,305 | 208,391 | 130,014 | 30,572 | 0 |
| WIKIBOOKS | 3,167 | 509 | 1,586 | 1,072 | 163 | 136 |
| Total | 431,458 | 83,875 | 215,390 | 132,193 | 32,230 | 478 |

`stratum_random` = Y for all rows. All simple rows are tier LOW by definition. Indian by tier: BBC 91 / 200 / 51, Wikibooks 16 / 57 / 63 (LOW / MID / HIGH). Wikibooks Indian MID is 57, not the draft's 45, because the label set here is wider (South Indian, Indic, multi-label tokens).

Grouping: 431,458 of 431,458 rows (100%) use FALLBACK_COMPONENT_V1; 0 use a 07I-C split group; 342,072 distinct groups; 130,188 rows sit in a group of more than one recipe in the full base; some groups span sources.

## 10. Open questions for Kush

1. Who runs the text-reading step for the four regex strata, and may Claude read step text for that, or do you want it done by hand/script on your side?
2. Gutenberg PD: keep excluded (0 ingredient lines, cannot fit the template) as in the Step 19 draft, or allow a separate text-only track?
3. Is the Indian label set (Indian, South Indian, Indic as tokens) right, and is Food.com (0 labels, so no Indian cell) acceptable?
