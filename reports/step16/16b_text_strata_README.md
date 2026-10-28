# 16b text-regex strata (DRAFT, D-037 item 2)

Output: `registry/recipe_semantics/deep_gold_text_strata_v1_DRAFT.csv` (431,458 rows = the frame ids, columns recipe_id, baking, drain_discard, reserve_split, multi_component; Y/N/NA only; no text).
sha256: `fae4faca991b24a694148302c360752cea02a06493ab52a1d0bf0e304e8d7ab3`
Generator: `tools/step16b_text_strata.py` (regexes copied verbatim from `tools/make_gold_batch.py` STRATA, which cannot be imported because it runs argparse at import; text built as in that script: steps joined + space + ingredient lines joined, lower-cased). Computed locally; no external service; no sample drawn; frame and all other files untouched.

Sources: Food.com `data/external/foodcom/recipes.parquet` (ingredient line = quantity + part, as in `tools/evidence_first_candidates.py`); BBC via base `source_record_id` -> `recipes_processed.jsonl` source_url -> `recipes_raw.jsonl` (as make_gold_batch.py); Wikibooks `data/interim/wikibooks/recipes.jsonl` by pageid.

## Y counts (of frame rows)
| source | rows | baking | drain_discard | reserve_split | multi_component |
|---|---|---|---|---|---|
| A1_BBC_GOOD_FOOD | 10,581 | 5,045 | 2,915 | 6,171 | 311 |
| FOODCOM | 417,710 | 185,622 | 84,584 | 147,196 | 3,215 |
| WIKIBOOKS | 3,167 | 883 | 709 | 915 | 15 |

## Unreadable text
None: 0 `NA` cells; every frame recipe resolved to text. Rule if it happened: no steps and no ingredient lines -> all four flags `NA` (never `N`).

## Cells with >= 30 eligible (Step 19 fall-through rule; Y per source x tier, frame rows)
All 7 P1 regex cells pass: baking FOODCOM MID 90,165; drain_discard BBC LOW 1,021; multi_component FOODCOM HIGH 1,765; reserve_split FOODCOM HIGH 60,952. No fall-through needed for P1.
Full table (HIGH / LOW / MID): multi_component BBC 80/40/191, FOODCOM 1,765/175/1,275, WIKIBOOKS 8/1/6 (the three WIKIBOOKS cells are < 30). All baking, drain_discard and reserve_split cells (every source x tier) are >= 52; smallest is baking WIKIBOOKS LOW 52.

## Caveat for review
The verbatim `reserve_split` pattern `\b(reserv|...)\b` has a word boundary right after "reserv", so "reserve"/"reserved" do NOT match (only the literal token "reserv"); the stratum is fed by "set aside", "remaining", "the rest", "divide", "half the". Kept as is for comparability with the old pilot; flag for Kush/Parv strata-regex review.

## Update D-038 (2026-10-27): corrected twin `reserve_split_v2`
The original `reserve_split` regex (verbatim from `make_gold_batch.py`) cannot match "reserve", "reserved" or "reserving" because the word boundary falls right after "reserv". The v1 column is kept unchanged so the strata stay comparable with the old pilot (counts unchanged: BBC 6,171; Food.com 147,196; Wikibooks 915). A new column `reserve_split_v2` uses `\b(reserv\w*|set aside|remaining|the rest|divide|half the)\b`.
Y counts for v2: BBC 6,410; Food.com 155,694; Wikibooks 989.
Output sha256 after the change: `ddbd302801e5bebd1bccb563fe3223eadb24bca1f70bf09b3ca761e041580728` (the earlier hash in this README, `fae4faca...`, is for the file before the column was added).
Which column the pilot draws from (v1 for comparability or v2 for correctness) is a pre-registration choice for Kush and Parv before any sample is drawn; nothing was drawn.

## Parv's pilot-column choice (2026-10-28, D-040; DRAFT_PENDING_KUSH)

Parv selects `reserve_split_v2` for the pilot and retains `reserve_split` v1
for comparison. This is a recorded draft choice for Kush to confirm, not Step 19
start/seal approval. No sample has been drawn and neither strata column nor the
sampling frame was changed. The D-038 output hash above remains current.
