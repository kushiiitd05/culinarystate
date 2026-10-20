# Evidence-first Gold selection protocol v1 (frozen S116, 2026-10-20)
Implemented by `tools/select_evidence_first_gold.py` (deterministic: ties by recipe id, no randomness, no external state). Decision from Kush (S116 Gate 1): Food.com may be used LOCALLY for research; recipe text is never committed or redistributed; Kaggle's CC0 label is the uploader's and the uploader's authority over Food.com user text is unresolved; exact ingredient x process evidence compatibility remains the H_STATE support definition (no process-family tier).

## Allowed inputs
Evidence compatibility (an ACTIVE EVD retention cell for the exact ingredient and exact process); explicit instruction-level ingredient x process match; recipe-family deduplication; ingredient, process-family and evidence-source diversity; annotation feasibility.
## Forbidden inputs
B3/B4 results, future H_STATE outputs, NER or compiler error/score data (the rule compiler is only the candidate GENERATOR that proposes matches; its confidence is not used and the ranking below does not read it), and any desired publication result.

## Step 1 — mechanical candidate filter (Food.com `recipes.parquet`, 150k hash-ordered sample scanned in S115)
A candidate row is a (recipe, ingredient, process) match where: process family is DRY_HEAT, WET_HEAT or FAT_HEAT (generic cook/heat excluded); at least 2 events follow the match (a meaningful cut exists); 4-12 steps; 5-18 ingredient lines; instruction text <= 2,500 characters and no URL; and the matched sentence itself names the ingredient (ingredient-list co-occurrence is never a process match; the process event must act on the ingredient or a descendant).
## Step 2 — diverse candidate pool (120 recipes)
One recipe per normalised-title family; reject ingredient-part Jaccard >= 0.8 against any already picked recipe. Greedy: marginal gain of a recipe = sum over its best <=3 cells of 1/(1+times the cell is already covered) + 0.5 per new ingredient + 0.5 per new process family + 0.5 per new evidence source (EVD `source_family_id`); caps in the pool: <=5 recipes per ingredient, <=6 per cell. Ties by recipe id.
## Step 3 — source-text eligibility screen
Each pool candidate is classified ELIGIBLE, INELIGIBLE_FALSE_MATCH, INELIGIBLE_AMBIGUOUS_PROCESS, INELIGIBLE_DUPLICATE_FAMILY, INELIGIBLE_NO_MEANINGFUL_CUT or INELIGIBLE_OTHER by reading only the matched sentence, the ingredient line and the step count. The screen never edits an evidence label. The reviewer of record is stated per row (`claude-ai` is NOT a human); status `AI_SCREENED_PENDING_HUMAN_CONFIRM` until Kush confirms. Kush may overturn a decision only BEFORE annotation starts, with a logged reason, and the selection is re-run unchanged.
## Step 4 — final selection from ELIGIBLE candidates
Same greedy gain, with caps: <=3 recipes per ingredient, <=4 per cell, no process family above 40% of the (recipe, cell) pairs picked so far (applied from the 5th recipe on; a first implementation divided cells by recipes and was corrected before any freeze). 20 PRIMARY then up to 10 RESERVE continuing the same greedy (share cap relaxed for reserves).
## Reserves
Used only before annotation begins and only for: source corruption; duplicate discovered after freeze; claimed ingredient/process match proven false; recipe cannot be represented under the annotation schema; source unavailable locally. Never because annotation is difficult or a model performs badly on it. Replacement = the next RESERVE in selection order; log the reason in `selection_replacements.csv`.
## Frozen outputs
`selection_manifest_v1.csv` (+ `.sha256`), `screening_log.csv`; recipe text lives only in git-ignored local files.
