# Evidence-first Gold expansion plan (design only; NOTHING annotated; S116, 2026-10-20)
Goal: the first publication-quality INDEPENDENT Gold subset, chosen to carry evidence cells, so H_STATE-R can reach a defensible size. Gold-v1.1 (20 BBC recipes) stays the AI-assisted, human-reviewed DEVELOPMENT Gold and is not relabelled.

## Pool and selection (before any annotation)
- Pool: Food.com `recipes.parquet` (Kaggle irkaal; CC0 declared by the uploader, authority over Food.com user text unverified). Packs are local-only and git-ignored; committed files hold recipe ids, hashes and counts, never text.
- Candidate generation: `tools/evidence_first_candidates.py` (instruction-level ingredient x process match to an ACTIVE EVD retention cell; ingredient-list co-occurrence is not enough). Candidate families after dedupe: 41,606.
- Algorithm (frozen BEFORE annotation, tools/hstate_coverage_forecast.py logic): one recipe per normalised-title family; also exclude pairs with ingredient-set Jaccard >= 0.8 to an already selected recipe; greedy maximisation of new (ingredient, process) cells with +0.5 for a new ingredient and +0.5 for a new process family; <=3 cells per recipe; cell cap = ceil(n/6) recipes per cell; ties by recipe_id; no B3/B4 output used.
- Screening: because compiler precision is 0.25, a human (Kush) screens about 4 candidates per target recipe by reading ONLY the matched sentence + ingredient line (3-5 min each) and confirms that the process really acts on the ingredient. Screening decisions are logged before annotation starts. Annotators never see which cell was targeted.
- Target n: 20 (primary), +10 reserve; stratify so that no process family exceeds 40% and no ingredient appears in more than 3 recipes. Source diversity: Food.com only for this set (BBC reserved for dev; Wikibooks optional as 5-recipe CC BY-SA add-on).

## Independent double annotation (no sharing)
1. Selection freeze: recipe ids + sha256 of each pack -> `annotation/gold/evidence_first_selection_frozen.csv` (committed, text-free).
2. Annotator A (Kush) and annotator B (Parv) each annotate ALL recipes independently with handbook v1 + Addendum A, no AI drafts, in separate folders; neither sees the other's files or an AI draft.
3. FREEZE A and FREEZE B (hash each file) before any comparison.
4. Agreement with the existing scorers (`tools/gold_pilot_agreement.py`, B-cubed coreference, aligned state scores, per-category rates); report honestly, no AI-assisted claim.
5. Adjudication by the two annotators with a written change log (as in S109); the adjudicated set becomes Gold-v2-evidence-first, frozen with hashes.
Handbook gate: the handbook must not change after A/B freeze; ambiguities go to Addendum B with date.

## Timing and decision gates
- Time the first 5 recipes (screening + annotation) and replace the hour ranges in the forecast with measured numbers.
- Gate 1: Kush approves Food.com local use and the selection algorithm. Gate 2: selection frozen. Gate 3: both annotators freeze. Gate 4: adjudicated Gold frozen. Only then rebuild H_STATE candidates on Gold-v2 and write questions.
- Out of scope here: question authoring, B3/B4 runs, compiler tuning (SSOT: no tuning while building Gold).
