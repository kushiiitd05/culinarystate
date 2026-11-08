# S176 lane L-LOT: lot-state layer [K], build steps 1 to 3 and the pH-flag interface

Status: DRAFT / AI_DRAFTED. No ledger was edited (EVD, COND, SRC, MEAS, SNAP re-hashed before and after every census run: unchanged; no `ledgers/data/*.jsonl` written).
Built 2026-11-08 in worktree `~/kush_work/culinarystate/.orch` (branch `max/s176-orchestration`, base `07fc0d2`, uncommitted).
Every derived value is `MODEL_DERIVED` and `NON_CITABLE` and carries (value or interval, unit, type, mask, basis, provenance), SSOT 199.5 / 199.7. Nothing here is a human verification or a signature.

## 0. Result in numbers

| Question | Answer |
|---|---|
| ING rows to verify to cover 80 % of corpus mentions | **147** of 2,048 active ING concepts (all sources); 119 if only Food.com + Wikibooks + TASTEset ingredient lines are counted; 274 if ordered by the BBC ledger frequency alone |
| What the 147 look like (AI proposal bands) | 105 HIGH, 41 MEDIUM, 1 LOW; my reading flags about 12 of the 147 as wrong or too generic (see 3.4) |
| Food.com source drops units? | **CONFIRMED**: 0 unit tokens in 7,950 quantity strings (859 sampled recipes); 0 stated masses in 1,445 paired lines; 1,378 of them are a bare number. Plus a second defect: the quantity list and the parts list differ in length in 683 of 859 recipes (79.5 %), so positional pairing is unreliable |
| 1,000-recipe sample, lines with grams | **0.13 %** (9 of 6,729): 4 STATED_MASS, 5 SR_PORTION usable. Food.com contributes 0 of 6,682 lines |
| Same, on unit-bearing sources (supplementary 600 Wikibooks + TASTEset recipes) | **21.2 %** of 4,819 lines (9.2 % STATED_MASS, 12.0 % SR_PORTION); 41 % of those lines are blocked by `LOCALE_AMBIGUOUS` |
| Lots with interval composition | 0.00 % of 24,280 lots (1,000 sample); 0.41 % (51 of 12,491) in the supplementary sample |
| Lots with single-member point composition / presence-only | 57.3 % / 42.7 % (1,000 sample) |
| pH flags with no registry | 100 % UNKNOWN (all three flags) |
| pH flags with the other lane's DRAFT registry (provisional) | CONTAINS_ACID TRUE 13.1 %, UNKNOWN 77.9 %; CONTAINS_ALKALINE TRUE 0.7 %, UNKNOWN 85.9 %; ALL_MEMBERS_ACID TRUE 3.4 %, UNKNOWN 64.4 % |
| Water activity | 100 % UNKNOWN by default (constants unsourced; switch off) |
| Tests | 105 passed (7 files) |

The honest reading: the layer works end to end and the exact-interval machinery is tested, but on the corpus as it stands almost no lot has mass-weighted composition. The blockers are data, not code: Food.com has no units, quantity-less seasoning lines ("to taste") sit in most recipes, and the cup/tablespoon locale is unknown outside BBC and Food.com.

## 1. Findings that change the plan (read these first)

1. **"5,387 ING rows" are ledger lines, not concepts.** `ING.jsonl` is append-only with versions: 5,387 lines = 2,110 unique ids = 2,048 ACTIVE concepts (49 SUPERSEDED, 13 DEPRECATED). All counts below use the latest ACTIVE version per id.
2. **Food.com units: confirmed absent** (counts only, seeded 1,000 sample, 859 Food.com recipes, 6,682 ingredient parts, 7,950 quantity strings; file `reports/lotstate/foodcom_units_check_S176.json`):
   - 7,476 quantity strings are numeric only, 474 are missing, **0 contain any letter or unit word**; 0 ingredient parts contain a mass or volume unit word (304 parts, 4.5 %, contain a count noun such as clove or leaf inside the ingredient name, which is not a unit of the quantity).
   - Of 1,445 pairs in recipes whose two lists are equally long: 0 stated masses, 4 other units, 1,378 bare numbers (95 %), 63 with no quantity. Compare Wikibooks: 18 of 30 sampled lines carry a unit, 1 a stated mass; TASTEset 13 of 17 a unit, 3 stated masses.
   - Consequence: Food.com masses stay UNKNOWN; a bare number is **not** treated as a count (`FOODCOM_UNIT_STRIPPED`); composition for those lines is presence-only. Option (c) (infer units) was not built.
3. **Food.com quantity and parts lists are not index-aligned.** `len(quantities) != len(parts)` in 683 of 859 recipes (645 longer, 38 shorter; only 176 equal). `recipes.corpus.iter_foodcom` pads or truncates the quantity list to the parts list and pairs by index, so its `ingredient_lines` mis-pair quantity and ingredient in most recipes (and the length difference is invisible there). The lot-state reader (`lotstate/corpus.py`) keeps the raw lengths; in unequal recipes **no quantity is paired** (`FOODCOM_QP_LENGTH_MISMATCH`, 5,237 of 6,682 Food.com lines). Anything built on the corpus iterator's Food.com ingredient lines (rc2 dry-run line counts, ingredient-line NER export) inherits the mis-pairing. I did not touch `corpus.py`.
4. **rc2 does not read the Unicode fraction slash (U+2044), which Food.com uses.** 163,708 of the first 504,111 Food.com quantity strings (32.5 %) contain it. `1⁄4 cup sugar` gives an UNKNOWN volume; a bare `1⁄4 sugar` is parsed as the number 1 (a wrong value, not an unknown). 174 of 195 distinct tested fraction strings parse differently once U+2044 is replaced by `/`. The lot-state line reader normalises U+2044 before calling rc2; the rc2 normaliser itself is untouched (not my lane). Recommend the fix at the source and a note in any earlier Food.com rc2 count.
5. The SR Legacy tap-water entry exists (`Beverages, water, tap, drinking`), so water needs no special case. Starch is present for only 1,167 of 7,793 SR foods (15 %), total sugars for 6,007 (77 %), fibre 93 %, vitamin C 94 %, sodium 99 %; a missing SR value is UNKNOWN for the lot (81.7 % of point-composition lots have starch UNKNOWN).

## 2. What was built

Package `src/culinarystate/lotstate/` (new; nothing existing was edited):

| File | Role |
|---|---|
| `text.py`, `sr_legacy.py` | normalisation; SR Legacy reader (food, category, 10 nutrients exact as Fractions, portions parsed into volume / count / mass / package kinds) |
| `ing_match.py` | step 1 matcher (deterministic, top-3 with score, band and reason) |
| `mention_freq.py`, `linker.py` | corpus mention counts and the ingredient-line linker (same algorithm as `vocab.line_link`, re-implemented because that module needs `lxml`, absent from the venv) |
| `line_grams.py` | step 2: line to (ING, grams interval, basis) |
| `intervals.py`, `values.py`, `composition.py` | step 3: exact interval bounds, value records, composition, solute load, gated water activity |
| `ph.py` | step 4: pH registry interface and lot flags |
| `lots.py`, `corpus.py`, `census.py`, `units_check.py` | lot assembly from the state graph, record stream with seeded sampling, counts-only census, Food.com units check |

Tools: `tools/lotstate_match_ing.py`, `tools/lotstate_census.py` (also writes the units check with `--units-out`). Registries: `registry/ing_sr_legacy_match_draft_v1.csv`, `registry/ing_sr_legacy_verification_queue_v1.csv`, `registry/lotstate_aw_constants_draft_v1.csv`. Tests: `tests/unit/test_lotstate_{intervals,sr_match,line_grams,composition,ph,lots,census_units}.py` plus `tests/unit/_lotstate_fx.py` (synthetic SR fixture; invented values, test only). Reports: `reports/lotstate/*.json`. Records: `data/derived/lotstate_1000_S176/` (66 MB, 192 files) and `data/derived/lotstate_600_WB_TS_S176/` (35 MB), git-ignored, ids and numbers only, no recipe text.

## 3. Step 1: ING to SR Legacy match

### 3.1 Method
SR descriptions are split on commas into segments (head noun first). Words that name a state (raw, cooked, canned, dried, frozen, salted, unsalted, unprepared) are facets, not identity, on both sides. Score = 0.45 IDF-weighted token coverage + 0.25 head-noun position (segment 0 / 1 / later) + 0.20 precision of the first two segments + 0.10 facet agreement + 0.05 ING-category agreement, minus penalties (brand, baby / fast-food / restaurant / meal categories, a processed-state conflict). Synonym variants (UK to US names; the table is AI-drafted and imported in part from `vocab.fdc.UK_US`) are scored separately and the best variant is named in `via`. A curated phrase that reproduces an SR entry exactly gets a bonus. A one-word ING name that heads at least 25 SR foods (cheese, beef) or has six or more near-ties is capped at MEDIUM. Bands: HIGH (all tokens covered, head noun in segment 0/1, margin over the next candidate), MEDIUM, LOW, NONE. **Bands are rule-defined and not calibrated against any human-verified set.** Rows are always `status = AI_DRAFTED` with an empty `human_decision`; nothing is auto-ACCEPTED.

### 3.2 Results (`reports/lotstate/ing_sr_match_summary_S176.json`)
2,048 ACTIVE ING: 406 HIGH, 387 MEDIUM, 1,009 LOW top-1 candidates, 246 with no candidate. By mention weight (4,912,063 mentions): HIGH 71.5 %, MEDIUM 22.8 %, LOW 4.3 %, NONE 1.4 %.

### 3.3 Verification queue and the 80 % cut
Ordered by `mentions_total` (descending, ties by ING id), with `cum_mentions_share` and a `within_80pct` flag. Mentions used, exactly (all counts only, per ING id; sum of five columns, units differ slightly):
- `bbc_ledger`: `corpus_frequency` of the latest ACTIVE ING rows (BBC line mentions counted when the registry was built; 113,319; BBC text is not on this server);
- `foodcom_parts`: every Food.com ingredient part, all 522,517 recipes (column `RecipeIngredientParts`), 4,129,433 part mentions over 7,368 unique strings, each unique string linked once; 4,088,826 linked, 40,607 unlinked (1.0 %);
- `wikibooks_lines`: rows of `registry/recipes/wikibooks_ingredient_links_v1.csv` (31,285);
- `tasteset_lines`: TASTEset ingredient lines linked with the lot-state linker (3,530 linked, 258 unlinked);
- `gutenberg_recipes`: rows of `registry/recipes/gutenberg_ingredient_links_v1.csv` (675,103 recipe x ING pairs from step text; Gutenberg has no ingredient lines).
The Food.com part scan is a counts-only aggregate (one pass over one column), not a lot-state run.

**Rows needed for 80 % of mentions: 147** (all sources). Variants: 119 (Food.com + Wikibooks + TASTEset lines only; Food.com alone also 119); 274 (BBC ledger only). The three orderings are in the summary JSON; the queue file carries each source as a column so a human can re-sort.

### 3.4 AI face-validity read (not a human check)
I read two random samples with seed 176: 45 HIGH and 45 MEDIUM rows each, twice (an earlier draft, then the final one). Plausible matches: HIGH about 93 % (roughly 84 of 90), MEDIUM about 67 % (60 of 90). Typical HIGH misses: a generic word (`extract`, `pod`), a cereal brand (`all-bran` to oat bran). Typical MEDIUM misses: a generic or junk ING (`cube`, `bowl`, `sauce`, `seed`), a processed product for a raw food (`dessert apple` to apple crisp), a brand entry. In the 147-row queue my reading flags about 12 as wrong or too generic: meat (coconut meat), fat (chicken fat), fruit (passion fruit), sauce, cake, beef (cured, dried), pork (belly), cheese (queso fresco), stock (beef), seasoning (poultry), coconut, bell pepper (red only). This is a screening aid for the human reviewer, not an accuracy claim. The default composition band floor is therefore MEDIUM and every census reports the floor and the HIGH-only alternative.

## 4. Step 2: ingredient line to (ING, grams interval, basis)

Basis codes: `STATED_MASS` (a mass unit in the text; exact interval from the rc2 grammar; Q0; layer 1 TEXT_STATED); `SR_PORTION` (volume or count converted with the SR food_portion weights of the ING's PROPOSED SR match; **PROPOSED basis, pending a human ruling (packet Q9)**; Q-level `Q2_PROPOSED`, below stated mass; layer 2 style ASSUMED_DEFAULT); `UNKNOWN` (with a reason code). Rules:
- A grams value is never a point from a guess: "1 onion" gives 70 to 150 g (SR small to large), "3 eggs" 114 to 189 g; a named size ("1 large onion") narrows to that SR item; "1/2 cup chopped onion" uses the SR cup-chopped density, "1 cup onion" spans the SR cup-chopped and cup-sliced densities.
- A count unit written elsewhere in the line is honoured ("2 garlic cloves" uses the SR clove weight).
- An SR_PORTION conversion is usable downstream only when the ING's SR band meets the floor (default MEDIUM); stated masses are always usable.
- Food.com: bare number gives UNKNOWN; unequal-length recipes pair no quantity; a unit that is present in the text is still honoured (unit-tested).
- Qualitative and quantity-less lines stay UNKNOWN (SSOT 235.5). Packages without a stated size, regional vessels, and locale-ambiguous culinary volumes stay UNKNOWN (rc2 rule: only BBC = UK and Food.com = US have a locale).
- The rc2 module, the legacy parser and `corpus.py` are untouched; the only pre-processing is U+2044 to `/`.

Results (reason codes, 1,000 sample): Food.com 6,682 lines: 5,237 `FOODCOM_QP_LENGTH_MISMATCH`, 1,378 `FOODCOM_UNIT_STRIPPED`, 63 `NO_QUANTITY`, 4 `NO_SR_PORTION`, 0 with grams. Wikibooks 30 and TASTEset 17 lines: 4 STATED_MASS, 6 SR_PORTION (5 usable at floor MEDIUM), 27 `LOCALE_AMBIGUOUS`. ING linking: 99.3 % of lines link to an ING concept (Food.com 99.3 %), so linking is not the bottleneck. Supplementary 600 Wikibooks + TASTEset recipes (4,819 lines): 381 + 63 STATED_MASS, 550 + 72 SR_PORTION (all families), 1,968 `LOCALE_AMBIGUOUS` (41 %), 609 `UNSUPPORTED_EXPRESSION`, 571 `NO_QUANTITY`, 291 `NO_SR_PORTION`, 232 `QUALITATIVE`; 327 of the usable SR_PORTION lines are genuine intervals (portion ambiguity), only 4 of the stated-mass lines are intervals.

## 5. Step 3: lot composition, solute load, water activity

**Lots** are state-graph entities (INGREDIENT_LOT, MIXTURE, INTERMEDIATE, RESERVED_PORTION; Rung A, event adapter, Step 18 replay) plus one `RECIPE_POOL` bookkeeping lot per recipe with ingredient lines (all lines together; not a physical lot). Members are the INGREDIENT_LOT ancestors of the entity; each carries a share interval of its root lot (1 through transforms and merges, [0, 1] through split / reserve / remainder / discard / recombine unless an allocation states an exact mass fraction). Member mass = the ingredient-line mass of that ING (summed over lines) times the share; two lots of one ING in a graph share the line mass as [0, total]. Each lot record carries the replay status of its recipe (28 of 1,000 recipes FAIL replay invariants: 615 lots flagged; they are kept, not repaired).

Composition kinds (`composition.kind`), all water, protein, fat, carbohydrate, sugars, starch, fibre, ash (g per 100 g) and sodium, vitamin C (mg per 100 g):
- `SINGLE_MEMBER_POINT`: one usable member, its SR values, independent of its mass (POINT).
- `INTERVAL_EXACT_BOUNDS`: two or more usable members, **every member mass an interval**: exact minimum and maximum of the mass-weighted fraction over the box of member masses. The solver (`ratio_bounds`) is exact for linear-fractional objectives (threshold configurations of the members sorted by ratio); 40 random boxes are checked against brute-force vertex enumeration in the tests.
- `PRESENCE_ONLY` (QUALITATIVE): any member unmatched, below the band floor or without mass; per nutrient PRESENT / ABSENT / UNKNOWN (ABSENT only when every member's SR value is a known zero).
A nutrient missing in SR for any member is UNKNOWN for the lot, never 0. Composition is **as listed** (SR values of the ingredients); process effects (evaporation, leaching, fat loss) are not modelled, flag `AS_LISTED_NO_PROCESS_EFFECTS`, so a cooked lot carries its ingredients' as-introduced composition. This is a design limit, see Q11.

**Solute load**: g salt-equivalent per g water (sodium x NaCl/Na mass ratio, all sodium taken as NaCl, therefore an upper bound on NaCl) and g total sugars per g water, as exact intervals (`open_upper` when the lot may contain no water). The constant 2.5421 is recalled from atomic weights and flagged `NACL_PER_NA_SOURCE_UNVERIFIED_AGENT_RECALLED`.

**Water activity**: Norrish (1966) for a sugar-water system, bracketed over the sugar constants, only behind `registry/lotstate_aw_constants_draft_v1.csv` (every row `SOURCE_UNVERIFIED_AGENT_RECALLED`; I did not open Norrish). Default: UNKNOWN (`AW_CONSTANTS_UNSOURCED_SWITCH_OFF`); with the switch the output is a MODEL_DERIVED interval flagged `SOURCE_UNVERIFIED_CONSTANTS`; any lot with a salt-equivalent above 0 is UNKNOWN (Norrish treats solutes as non-electrolytes). Ross is not implemented: it needs per-solute binary tables not in the repository.

Results, 1,000-recipe sample (24,280 lots: 8,254 INGREDIENT_LOT, 12,126 INTERMEDIATE, 2,875 MIXTURE, 861 RECIPE_POOL, 164 RESERVED_PORTION; 4,739 leaf lots; Food.com 20,733, Gutenberg 3,433, Wikibooks 111, TASTEset 3):
- SINGLE_MEMBER_POINT 13,923 (57.3 %), PRESENCE_ONLY 10,357 (42.7 %), INTERVAL_EXACT_BOUNDS **0**. Leaf lots: 2,769 point, 1,970 presence-only.
- Only 9 lots in the whole sample have every member mass known. Member band floor of the lots: HIGH 9,351, MEDIUM 11,711, LOW 1,717, NONE 1,501.
- Solute load: salt POINT 13,391 / UNKNOWN 10,889; sugar POINT 12,357 / UNKNOWN 11,923 (reasons: member mass unknown 7,139, member not matched or below band 3,218, no water 526 to 529, SR sugars missing 1,040). Water activity 24,280 UNKNOWN.
- Nutrient availability among the 13,923 point lots: water, protein, fat, carbohydrate, ash always; sodium 3 UNKNOWN; vitamin C 250; fibre 384; sugars 1,040; starch 11,370 UNKNOWN (81.7 %).
Supplementary 600 Wikibooks + TASTEset recipes (12,491 lots): SINGLE_MEMBER_POINT 6,923, PRESENCE_ONLY 5,517, **INTERVAL_EXACT_BOUNDS 51** (3 recipe pools, 23 mixtures, 25 intermediates); 5 of them are leaf lots. Lots whose members all have a mass: 1,220 (902 at floor HIGH, 281 MEDIUM). The main reason a mixture does not reach an interval is one quantity-less member (salt, pepper "to taste", "a pinch") that makes the whole lot presence-only; the 106 TASTEset recipes have ingredient lists only, so their only lot is the pool and all 106 are presence-only.

## 6. Step 4: pH registry interface and flags

`ph.py` reads a CSV with a key column (`ing_id` | `name` | `item_norm` | `food_name`), `ph_low`, `ph_high` (empty = lower bound only, an open range, never a POINT) and `source_id`; an optional crosswalk (`ph_id` to `ing_id`, `confidence_band`, rank 1 only, band floor a parameter) maps name-keyed rows to ING ids. The registry is a parameter of `tools/lotstate_census.py` (`--ph-registry`, `--ph-crosswalk`); tests use a synthetic fixture. Member status against a threshold is three-valued: acid YES if `ph_high <= 4.6`, NO if `ph_low > 4.6`, MAYBE if straddling; alkaline YES if `ph_low > 7.0`, NO if `ph_high <= 7.0`. Lot flags (Kleene): CONTAINS_ACID_MEMBER (TRUE if any member YES, FALSE if all NO, else UNKNOWN), CONTAINS_ALKALINE_MEMBER (same), ALL_MEMBERS_ACID (TRUE if all YES, FALSE if any NO). **No mixture pH number is computed**; the record states `mixture_ph: NOT_COMPUTED` and keeps the member ranges with source ids.

- Primary census: registry absent, so all three flags are UNKNOWN in 100 % of lots.
- Provisional interface check with the L-PH lane's DRAFT files (`registry/food_ph_fda_draft_v1.csv`, 541 registry entries (name-keyed rows plus crosswalk-mapped ING ids), plus `food_ph_fda_ing_crosswalk_draft_v1.csv`, rank-1 rows with band HIGH only; the brief named `food_ph_fda_2003_draft_v1.csv`, the lane produced these two names): CONTAINS_ACID_MEMBER TRUE 3,182, FALSE 2,192, UNKNOWN 18,906 of 24,280 lots; CONTAINS_ALKALINE_MEMBER TRUE 178, FALSE 3,240, UNKNOWN 20,862; ALL_MEMBERS_ACID TRUE 837, FALSE 7,814, UNKNOWN 15,629; 704 of 4,739 leaf lots contain an acid member. These numbers use an unreviewed registry and an AI-drafted crosswalk: they show that the interface works, not what the corpus contains. File `reports/lotstate/lotstate_census_1000_S176_ph_provisional.json`.

## 7. Tests

`/home/manjot23309/kush_work/culinarystate/.venv312/bin/python -m pytest -q tests/unit/test_lotstate_*.py`: **105 passed** (by file: intervals and value contract 46, matcher and portion parser 20, line grams 11, composition 13, pH 6, lots end to end on the real lexicon with a synthetic SR 6, census and units check 3). They cover: exact bounds against brute force, unbounded and undefined ratios, outward float rounding, UNKNOWN never 0, facet and head-noun rules, generic head capped below HIGH, determinism, AI_DRAFTED status, portion parsing, interval grams for count ambiguity, Food.com unit-stripped and length-mismatch handling, stated mass Q0 versus SR_PORTION Q2_PROPOSED, band floor, presence-only logic, solute load incl. unbounded, water activity default UNKNOWN and flagged when enabled, the constants registry marked unverified, pH Kleene tables incl. open-ended ranges and absent registry, no recipe text in records, and counts-only census output.

## 8. Runs (rows for `registry/compute_runs_v1.csv`, host manjot-server, nice 10, no GPU)

```csv
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S176-LOT-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,ING ledger + SR Legacy + FOODCOM parts scan,1,tools/lotstate_match_ing.py --overwrite,registry/ing_sr_legacy_match_draft_v1.csv,d577a3d7436723f25314db8aff8717f7627c537b05e1037e7ee8fe24dc94b9cc,2026-11-08T14:11:49Z,2026-11-08T14:12:39Z,DONE,"2,048 active ING; 406 HIGH 387 MEDIUM 1009 LOW; queue sha256 6e75713789370b23fccdcf6fa02fe3fed33eb11f1eeeb473e4fcaccab5f6f382; summary reports/lotstate/ing_sr_match_summary_S176.json sha256 62aeecb12d9d1373f44e379b2214d9a9f1399d96cd9a39f76157c2311d428f32; 147 rows for 80 % of mentions"
RUN-S176-LOT-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,24,tools/lotstate_census.py --seed 20261104 --sample-size 1000 --workers 24 --records-dir data/derived/lotstate_1000_S176 --units-out reports/lotstate/foodcom_units_check_S176.json,reports/lotstate/lotstate_census_1000_S176.json,fadbd71ba9402f1ffbe0cff86359ebf47576ef2662b1c9bdb502252661449ea3,2026-11-08T14:12:39Z,2026-11-08T14:13:59Z,DONE,"1,000 recipes; 6,729 lines; 24,280 lots; units check sha256 0281bbde57840919eba0bb022f1f02b2e868ad499cc7ea596986cd76cf7eaad1; records 66 MB git-ignored; protected ledgers unchanged"
RUN-S176-LOT-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,WIKIBOOKS TASTESET,16,tools/lotstate_census.py --seed 20261104 --sample-size 600 --families WIKIBOOKS TASTESET --workers 16 --records-dir data/derived/lotstate_600_WB_TS_S176,reports/lotstate/lotstate_census_600_WB_TS_S176.json,7636f4c057e5f6dda6f4e244ab10f3c8448d8b4fec4e704e6b965132adb66761,2026-11-08T14:13:59Z,2026-11-08T14:14:49Z,DONE,"supplementary stratified sample of the unit-bearing families (494 Wikibooks + 106 TASTEset); 4,819 lines; 12,491 lots; 51 interval-composition lots"
RUN-S176-LOT-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,24,tools/lotstate_census.py --seed 20261104 --sample-size 1000 --workers 24 --ph-registry registry/food_ph_fda_draft_v1.csv --ph-crosswalk registry/food_ph_fda_ing_crosswalk_draft_v1.csv --ph-crosswalk-min-band HIGH,reports/lotstate/lotstate_census_1000_S176_ph_provisional.json,da05ff46dae4377805da5daef42adc0b389534821100688a3dd24853bcf18f3a,2026-11-08T14:14:49Z,2026-11-08T14:15:50Z,DONE,"PROVISIONAL: L-PH draft registry (sha256 6c591cfdd0dd5dc2ee1300eea0a50582d173f8c39c0345dd62660d6f51ebc0d8); interface check only; no records written"
```

Discarded, for the record: an earlier 30-recipe smoke run and one 1,000-recipe run were made with an earlier matcher draft and an earlier line-record format (a band-override bug put `NONE` on Food.com lines with unpaired quantities); they were deleted and everything above was re-run after the final matcher. The first attempt to stop a run with `pkill -f` also terminated my own shell; no other process of mine or anyone else's was affected.

Cost for the orchestrator (measured on 200 recipes, single process, CPU time): about 0.14 CPU-seconds per recipe for the census core, so the roughly 600,000 non-BBC recipes need about 20 CPU-hours (on the order of 20 to 40 minutes on 64 workers, longer on a loaded server). Per-lot records are 66 KB per recipe uncompressed (about 40 GB for 600,000 recipes, over the 15 GB lane budget); gzip compresses them about 30 times (measured on one part file), so a full run must write `.jsonl.gz` or keep only leaf, pool and INGREDIENT lots (INTERMEDIATE lots are 50 % of the bytes and mostly repeat their parent's composition). I did not run the full corpus.

## 9. What this says about packet questions Q7 to Q14

- **Q7** (how much to verify): 147 ING rows cover 80 % of mentions (119 for the non-BBC ingredient lines). 41 of them are MEDIUM and I flag about 12 as wrong or generic, so the human work is a correction pass over a mostly plausible list, not a blank-page match. Below that the draft stays LOW and composition ignores it (floor MEDIUM).
- **Q8** (Food.com units): the packet's claim is right and understated: the quantity list is also misaligned in 79.5 % of recipes. Option (a) is what is built; (b) is the only route to Food.com grams and needs a human decision about another source; (c) not built.
- **Q9** (SR as portion authority): built as `SR_PORTION`, `Q2_PROPOSED`, intervals under ambiguity, usable only at band floor; the rc2 HUMAN_VERIFIED rule is not bypassed (rc2 is not used for SR portions). Needs the ruling.
- **Q10** (mixture pH): flags built exactly as designed, no mixture number; whether they gate chlorophyll / pectin / anthocyanin / protein-acid mechanisms is for the mechanism-screen step. The flags need real member ranges (the L-PH registry) and a rule for lower-bound-only rows.
- **Q11** (missing state variables): composition is as listed; moisture change, cell integrity, thermal dose and so on are absent by construction. A cooked lot must not be read as cooked composition.
- **Q13** (factorisation): implemented as "both": every lot keeps its member list (ING, share, mass interval, basis, SR match) and carries the mixture-level fields (composition, solute load, water activity, pH flags).
- **Q12, Q14, Q15**: not in this lane. Order effects (Q14) are not modelled: member shares follow the graph's allocations only, there is no contact time.

## 10. Human decisions needed

1. **Verify the 147-row queue** (`registry/ing_sr_legacy_verification_queue_v1.csv`, `human_decision` column) or rule that a smaller list is enough; until then every SR-based number stays AI_DRAFTED.
2. **Rule on `SR_PORTION`** (Q9): acceptable portion authority? Which rung (Q1, Q2 or Q3) and is `Q2_PROPOSED` right? Is an interval over all SR portions of the matched food acceptable when the line names no prep state or size?
3. **Composition band floor**: MEDIUM (default; about 67 % plausible by my read) or HIGH (about 93 %, but 25 % of linked mentions fall below it).
4. **Locale for Wikibooks, TASTEset and Gutenberg** (cups and spoons): 41 % of the lines in the unit-bearing sample are blocked by it. The rc2 rule leaves them ambiguous; a locale assignment is a human call.
5. **Food.com**: is another Food.com source with units and aligned ingredient lists obtainable and licensable? Should the length mismatch (79.5 % of recipes) and the U+2044 gap be fixed at the source (`recipes.corpus.iter_foodcom`, rc2 normaliser)? Both are outside this lane and untouched.
6. **Quantity-less lines** ("to taste", "a pinch") make most mixtures presence-only. Options: keep presence-only (current, honest); allow a human-ruled, sourced ceiling per qualitative unit; or add the exact convex-hull bounds for unknown masses (every mass-weighted fraction lies between the smallest and largest member value; cheap and exact, but weak). Not built; decide whether to.
7. **pH**: confirm the thresholds (acid 4.6 from the packet; alkaline 7.0 is the neutrality definition I chose), the treatment of lower-bound-only rows, the crosswalk band floor, and which registry file is the real one.
8. **Water activity constants**: someone must open Norrish (1966) (and a molar-mass table) before the switch is turned on; Ross needs per-solute tables.
9. **Starch** is UNKNOWN for 82 % of point lots (SR has it for 15 % of foods). Accept UNKNOWN, or authorise a different carbohydrate split.
10. **Orchestrator**: approve the full non-BBC run (records must be gzip or reduced, see section 8) and decide whether lots from recipes that fail replay invariants (28 of 1,000) are excluded downstream.

## 11. Limits and negative results

- The 1,000-recipe sample is 86 % Food.com, so its census mostly measures the Food.com data gap; the 600-recipe supplementary sample is the one that exercises the gram and interval paths. Neither is a gold score.
- Interval composition on real data: 0 of 24,280 lots in the specified sample (the specified result), 51 of 12,491 in the supplementary one.
- Bands are uncalibrated and the synonym table is AI-drafted; the matcher was tuned by me on the most frequent ING rows (a development step, not an evaluation), and my plausibility reading is not independent of that tuning.
- Rung A lots come from instruction text only (no ingredient-list lots exist in the graph, H4); masses are joined to graph lots by ING id from the ingredient lines. A recipe whose steps name an ING that has no ingredient line gets an UNKNOWN mass.
- pH and water-activity results are interface demonstrations, not findings. No mixture pH, no kinetics, no mechanism screen, no interaction edges (steps 5 to 7 of the build order are not started).
