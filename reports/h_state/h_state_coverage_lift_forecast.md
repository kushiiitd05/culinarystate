# H_STATE coverage-lift forecast (S116, 2026-10-20)
Baseline (frozen S114, `benchmark/h_state/s114_snapshot_freeze.json`): 20 Gold recipes, 8 with a supported valid cut, **14** distinct supported recipe/evidence pairs, 17,978 active EVD rows.
Nothing here uses B3/B4 output. All numbers are forecasts from compiler-proposed matches (see "How reliable").

## Evidence-first scan results (instruction-level: the process event must act on an entity descended from the ingredient)
| pool | recipes scanned | with >=1 match | distinct ledger cells matched (of 338) | note |
|---|---|---|---|---|
| BBC (local only) | 11,934 | 4,256 | 241 | third-party text, never off this Mac |
| Wikibooks (CC BY-SA) | 3,797 | 1,051 | 136 | |
| Food.com (Kaggle, CC0 declared) | 150,000 (hash-ordered sample of 451,554 prefilter survivors of 522,517) | 48,969 | 243 (73 ingredients, 28 processes) | 0 compile failures; A100, 100 workers |
Food.com deduplicated candidates: 41,606 recipe families, 77,747 (family, ingredient, process) rows. Top strata (`evidence_first_foodcom_strata.csv`): egg x bake, onion x boil, onion x bake, chicken x boil/simmer/brown, milk x heat, cheese x bake. By process family: WET_HEAT 31k, DRY_HEAT 25k, FAT_HEAT 13k, HEAT_GENERAL 8k (generic cook/heat: flagged), the rest small.

## How reliable (measured, `evidence_first_calibration.json`)
On the 20 Gold recipes the rule compiler on raw text proposed 16 (recipe, ingredient, process) cells; 4 are in the 14 Gold-derived cells: **precision 0.25, recall 0.29**. Aggregate counts agree (16 vs 14) but per-recipe matches are noisy. So: *conservative* = x0.25. *Optimistic* = a human screens candidates BEFORE annotation (about N/0.25 = 4N screenings) so only true matches are annotated. Matches selected for high predicted counts may have lower precision than 0.25 (winner's curse): treat conservative as the planning number.

## Forecast A: new evidence-first Gold (Food.com, existing evidence)
Greedy selection (one recipe per title family; gain rewards new cells, ingredients, process families; <=3 cells per recipe). Totals include the 14 existing pairs.
| +N Gold | unique families | ingredients | process families | distinct cells | distinct EVD ids | new pairs optimistic / conservative | TOTAL supported optimistic / conservative | screenings for optimistic | effective clusters (families) |
|---|---|---|---|---|---|---|---|---|---|
| +10 | 10 | 19 | 9 | 30 | 134 | 30 / 7.5 | 44 / 21.5 | 40 | 18 |
| +20 | 20 | 35 | 9 | 60 | 283 | 60 / 15 | 74 / 29 | 80 | 28 |
| +30 | 30 | 48 | 10 | 90 | 411 | 90 / 22.5 | 104 / 36.5 | 120 | 38 |
| +40 | 40 | 55 | 10 | 119 | 530 | 120 / 30 | 134 / 44 | 160 | 48 |
Diversity: ingredient count grows ~1.4 per recipe; process families saturate at 9-10 (WET/DRY/FAT_HEAT dominate); only ~60% of matched steps state a time or temperature, so TIME/TEMPERATURE dependencies exist for a subset.

## Forecast B: current Gold + new evidence (cleaned missing-cell ranking: 810 raw cells -> 58 real targets)
Pairs unlocked = distinct (recipe, cell). Optimistic = every target finds a verifiable same-ingredient same-process source; conservative = **ASSUMED** 1/3 do (not measured).
| top-K cells | Gold recipes newly supported | cuts | new pairs optimistic / conservative | ingredients | processes | cost mix |
|---|---|---|---|---|---|---|
| 5 | 5 | 56 | 11 / 3.7 | 4 | 4 | medium, literature (R6 gap) |
| 10 | 6 | 78 | 19 / 6.3 | 6 | 5 | medium |
| 20 | 8 | 99 | 29 / 9.7 | 14 | 7 | mostly medium, 2 low (compiled CC0 table) |
Best targets: onion simmer, carrot roast, garlic fry/boil/simmer, ginger fry/simmer, garden pea steam. Many are botanical/culinary vegetables where USDA R6 has no row, so evidence must come from primary literature (human verification cost).
**Free option D (design choice, not data):** relax compatibility from the exact process to the same ingredient + same process FAMILY (e.g. simmer ~ boil, both WET_HEAT) as an explicit lower evidence tier. On Gold thermal pairs: EXACT 11, FAMILY-only 10, none 153 (recipes with exact 7, with exact-or-family 8). This nearly doubles thermal pairs but weakens "compatible" and must be preregistered as a separate tier before use.

## Forecast C: hybrid (new evidence-first Gold + curated cells; sources are disjoint so counts add)
| strategy | supported optimistic / conservative | effective clusters | annotation recipes | cells to curate |
|---|---|---|---|---|
| +10 Gold +5 cells | 55 / 25.2 | 23 | 10 | 5 |
| +20 Gold +5 cells | 85 / 32.7 | 33 | 20 | 5 |
| +20 Gold +10 cells | 93 / 35.3 | 34 | 20 | 10 |
| +30 Gold +10 cells | 123 / 42.8 | 44 | 30 | 10 |
Pareto-efficient: +10 Gold +5 cells (cheapest to roughly double the conservative count), +20 Gold +5 cells (best conservative per human hour), +30 Gold +10 cells (the only option that reaches >=40 under the conservative assumption).

## Human-hour model (ranges, NOT measured; to be replaced by timing the first 5 recipes)
Assumptions: screening 3-5 min per candidate; annotation 30-45 min per recipe per annotator (handbook v1 + Addendum A); adjudication 15-25 min per recipe; evidence discovery+extraction+verification 2-5 h per cell; QA/replay 10 min per recipe.
| path | work units | human effort | compute | licence risk | expected supported (cons / opt) | independence | process / ingredient diversity | L14/L15 reuse | publication value |
|---|---|---|---|---|---|---|---|---|---|
| A +20 Gold only | 80 screenings, 20 recipes x2 annotators, adjudication | screening 4-7 h; annotation 20-30 h (two people); adjudication 5-8 h; QA 3-4 h => ~32-49 h | negligible (done) | Food.com authority unverified (keep text local) | 29 / 74 | HIGH: first independent Gold | 9 proc fam / 35 ingredients | medium: recipe contexts, not magnitudes | HIGH |
| B top-10 cells only | 10 sources | 20-50 h evidence work + verification gate | low | low (paper tables) | 20 / 33 | n/a (still AI-assisted Gold) | 5 proc / 6 ingredients | HIGH: reusable evidence | medium |
| C +20 Gold +10 cells | both | ~52-99 h | low | as above | 35 / 93 | HIGH | best | HIGH | HIGH |
| D family-level relaxation | 0 | ~1-2 h (preregister tier) | none | none | ~+10 weaker pairs | no change | no change | none (could blur L15) | low |

## Decision
1. Do not write H_STATE questions now. Frozen at current coverage H_STATE-R would have n=14 over 8 families: too weak for the planned inference.
2. Cheapest defensible route: **Path A at +20 (with a buffer of screened candidates), then reassess.** It is the only route that also produces the independent Gold needed for publication, costs the fewest scarce hours per supported item, and removes the dependency on the AI-assisted Gold. Path B has the highest L14/L15 reuse and should run in parallel at +5 cells chosen from compiled CC0 sources (USDA Cooking Yields R2 for meat) and R6 gaps.
3. Strongest L14/L15 simulator value: Path B / hybrid (reusable measured evidence). Strongest benchmark and publication value: Path A.
4. Do not force 40: conservative +30 Gold +10 cells = 42.8 is the first plan that clears it.
