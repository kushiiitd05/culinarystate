# S178 INGCAT: AI-drafted category proposals for the ING that have none

Status: **AI_DRAFTED / PROPOSED / NON_CITABLE.** Nothing here is a human decision, signature, approval or nonce. `human_decision` is empty in every row.
- Worktree `max/s176-orchestration` @ `2d45f68+uncommitted`, host manjot-server, 2026-11-09.
- **No ledger was written.** `ledgers/data/ING.jsonl` is byte-identical (sha256 `ef439951982b98efa9a21787f7b646a162c3c4912718405cdae6ed56dc1cd574` at the start, at the end, and before and after the simulation). The protected-ledger baseline check passed before and after the simulation. `composition/`, `registry/ing_sr_defaults_v1.csv` and `reports/s175/*` were only read; `git status` shows no change to any of them.
- A category overlay was used only in memory inside the simulation. The shipped content table, the crosswalk and the router code are untouched.
- Board items: the brief listed none for this lane and `registry/execution_board_S178.csv` has no INGCAT row, so there is no item status to report.

## 1. What was built

| File | What |
|---|---|
| `tools/s178_ingcat_propose.py` | The proposer, top-100 sheet writer, summary, backtest and the router-census overlay simulation. Refuses to write under `ledgers/`, `data/`, `exports/`, `annotation/gold/` or `src/culinarystate/composition/` (`checked_output`). Reads the composition layer only through `ing_sr_match.load_registry` and `normalise`. |
| `registry/ing_category_proposals_S178_DRAFT.csv` | 1,417 rows, one per ACTIVE ING without a category. sha256 `2b464677f7a695be9ae10121bb8546b700ca97b76a3f720a6be45d1f0706b80a`. |
| `reports/s178/ingcat/top100_for_human_confirmation.md` | One tickable line per ING for the first 100 by impact, plus the suggested NEW values. sha256 `c54c18f18a61cf53009f35b388cbe5afaecd942c0bb6ac53510ce9863cbb62ea`. |
| `reports/s178/ingcat/ingcat_summary_S178.json` | Counts only. sha256 `602e62a837ff34cc44224f3c724f16782ef1ee70a169c75e53339cba47d8f80f`. |
| `reports/s178/ingcat/ingcat_router_simulation_1000_S178.json` | Counts only (checked with `assert_counts_only`). sha256 `0c76fb7e9adeaa8c8ad363f4fd7793ed964c7b005d0ebf61dc3a08ce24bb9e4d`. |
| `tests/unit/test_s178_ingcat_rules.py`, `test_s178_ingcat_build.py` | 57 + 22 tests (two of the 22 are `-m ledgers` checks on the shipped outputs). |

CSV columns: the eight requested (`ing_id, name, proposed_category, basis, confidence, sr_food_group, mention_items, human_decision`), then `rank, mention_nonbbc, mention_all_families, conflicts, alt_category, new_category_suggestion, registry_kind, sr_description, legacy_band, crosswalk_confirms, unlocks_absent_vitc, status`.

**Scope correction.** The S177 figure "1,452 of 2,110 ING rows have no category" counts the latest row of every id, including 49 SUPERSEDED and 13 DEPRECATED. The ACTIVE set is **1,417 of 2,048 without a category** (631 have one). The 14-value vocabulary is read from those 631 rows: BEVERAGE, CEREAL, CONDIMENT, DAIRY, EGG, FAT_OIL, FRUIT, HERB_SPICE, LEGUME, MEAT, NUT_SEED, SEAFOOD, SWEETENER, VEGETABLE. A proposal outside it is refused in code and tested.

## 2. How a proposal is made

Bases, with every one used and every conflict written into `basis` and `conflicts`:
1. **REGISTRY_SR.** The SR food group of the curated identity in `ing_sr_defaults_v1.csv` (DIRECT, UK_US, DEFAULT_FORM, APPROX). NO_SR_EQUIVALENT, NOT_A_FOOD and AMBIGUOUS give no identity and no fallback, as in `sr_identity.py`. The group maps to a vocabulary value through a table that is checked against the S177 crosswalk. Dairy-and-Egg splits on the SR description, and fruit juice maps to BEVERAGE (the ledger files lemon and orange juice there).
2. **LEGACY_SR.** The legacy match's rank-1 group, only for terms the registry does not hold and only for a HIGH or MEDIUM band. It never gets better than LOW confidence alone: on the 631 labelled ING the legacy-only HIGH matches agree with the ledger 11 of 16 times.
3. **LEXICAL culinary class.** Head-word scan, phrase overrides and special classes (water, salt, leavening, additives, utensils). This is the check against the SR group, because SR groups leak: salt is filed under "Spices and Herbs", water under "Beverages", baking powder under "Baked Products", mayonnaise under "Fats and Oils", soy sauce under "Legumes", ketchup under "Vegetables".

When the culinary class and the SR group differ, the culinary class wins, the conflict is recorded (`SR_GROUP_DISAGREES`, with the SR-derived value in `alt_category`) and confidence is capped at MEDIUM (LOW for an ambiguous word).

Confidence:
- **HIGH.** Two bases agree on one existing value, the fit is exact and the word is unambiguous. Or a curated DIRECT, UK_US or DEFAULT_FORM identity in a clean SR group with no lexical rule against it.
- **MEDIUM.** One decent basis, or the bases agree but the fit is approximate or the word is dual-use.
- **LOW.** Weak or conflicting, or no existing value fits. The proposal may be empty.

Further columns:
- `crosswalk_confirms`: would the S177 `CATEGORY_CROSSWALK` accept the proposed value against the SR group of the router's own rank-1 identity.
- `unlocks_absent_vitc`: the ING is in the S177 category-blocked list and the crosswalk would accept the value.

### Result

| | ING |
|---|---:|
| ACTIVE ING without a category | 1,417 |
| HIGH | 193 |
| MEDIUM | 914 |
| LOW | 310 (168 of them with no proposal) |

- By proposed value: VEGETABLE 163, CEREAL 234, HERB_SPICE 143, MEAT 131, CONDIMENT 97, SWEETENER 88, FRUIT 85, BEVERAGE 83, DAIRY 93, SEAFOOD 41, NUT_SEED 37, LEGUME 24, FAT_OIL 22, EGG 8, none 168.
- Impact order is the ING's non-BBC corpus mention count (FOODCOM, GUTENBERG_SEGMENT, WIKIBOOKS, TASTESET ingredient lines, from `vocab_corpus_frequency_v1.parquet`), then the all-family count, then id. The 1,417 ING hold 1,528,105 non-BBC mentions; **the top 100 hold 89.9% of them**. 605 of the 1,417 have no non-BBC mention at all.
- Top 100 by confidence: 46 HIGH, 37 MEDIUM, 17 LOW. Non-BBC mentions by tier: HIGH 668,284, MEDIUM 653,037, LOW 206,784.
- `mention_items` is the S177 **full-census item count**. It exists only for the 52 uncategorised ING among the 63 that S177 counted as blocked only by the category. The other 11 of the 63 have a category that the crosswalk rejects (section 4), so they are outside this lane.

### Backtest (agreement, not truth)

The engine was run on the 631 labelled ACTIVE ING with the label hidden and the ING's own label removed from the precedent counts.

| tier | ING | proposed | agree with the ledger | rate |
|---|---:|---:|---:|---:|
| HIGH | 257 | 257 | 242 | 0.942 |
| MEDIUM | 307 | 307 | 276 | 0.899 |
| LOW | 67 | 36 | 20 | 0.556 (31 with no proposal) |

- The ledger labels are FoodOn-derived and visibly noisy. Examples: whisky, gin and spelt under CEREAL or FAT_OIL, brandy and every mushroom under FRUIT, white chocolate under SEAFOOD, mustard oil under HERB_SPICE. By my reading most of the 15 HIGH disagreements are ledger errors, but that is an AI judgement.
- The labelled set is also the easier set, since FoodOn could classify it. The uncategorised set is harder: egg, salt, water, ginger.
- I tuned rules by reading the top 150 and the HIGH and MEDIUM disagreements, so the backtest is not independent of the rule design. Treat it as a sanity check.

## 3. Conflicts and vocabulary gaps (needs a human)

| ING | non-BBC mentions | S177 items | proposal | what the conflict is |
|---|---:|---:|---|---|
| salt | 259,661 | 982,601 | HERB_SPICE, MEDIUM, alt CONDIMENT | SR says "Spices and Herbs". Culinary class is a mineral seasoning. **No exact fit.** The ledger already files celery salt, garlic salt and "seasoning" under HERB_SPICE. CONDIMENT also passes the crosswalk. Suggest NEW `SALT_MINERAL` (5 ING, 259,919 mentions). |
| water | 123,220 | 1,427,479 | BEVERAGE, MEDIUM | SR says "Beverages". Cooking water and ice are a medium, not a drink. **No exact fit.** Suggest NEW `WATER` (water, ice, ice cube; 3 ING, 126,740 mentions). Sparkling, soda, mineral and tonic water stay BEVERAGE, HIGH. |
| baking powder, bicarbonate of soda, cream of tartar, yeast (5 forms) | 85,542 | 26,091 + 11,958 + 238 | none | SR files them under "Baked Products", which the crosswalk reads as CEREAL. **None fits.** Suggest NEW `LEAVENING_AGENT` (13 ING). |
| gelatine, xanthan gum, msg, pectin, food colourings, glitter | 2,649 | 11,642 (gelatine) | none | None fits. Suggest NEW `ADDITIVE` (29 ING, mostly food colourings with no non-BBC mention). |
| chicken, beef, fish stock, bouillon | 32,672 | 132,697 + 29,036 + 2,682 | CONDIMENT, MEDIUM | The S177 crosswalk pairs CONDIMENT with "Soups, Sauces, and Gravies", so it passes. A stock is a cooking liquid. Suggest NEW `STOCK_BROTH` (21 ING). |
| soy sauce, light and dark soy sauce, ketchup, tahini paste | 20,505 (soy sauce) | 126,286 (soy sauce) | CONDIMENT, MEDIUM | The culinary class wins over SR "Legumes", "Vegetables" and "Nut and Seed". **The current crosswalk would NOT confirm these**, so confirming them does not restore the abstention (`CROSSWALK_WOULD_NOT_CONFIRM`, 53 rows). |
| ginger, chilli, mustard, clove, corn, mushroom, olive | | | LOW or MEDIUM | Dual-use words, flagged `DUAL_USE` with the other reading in `alt_category`. Ginger is HERB_SPICE LOW with alt VEGETABLE. |
| 13 ING (saucepan, colander, bowl, wooden spoon, muslin, scale, label and so on) | | | none | Not foods (`NOT_A_FOOD_SUSPECT`). Consider deprecating them rather than categorising them. |

Suggested new values: WATER, SALT_MINERAL, LEAVENING_AGENT, ADDITIVE, STOCK_BROTH (71 ING). **None was added.** Adopting any of them also needs a `CATEGORY_CROSSWALK` row, or the ING stays UNKNOWN under the ABSENT rule.

Other flags (counts in the summary JSON):
- SR_GROUP_DISAGREES 46
- PRECEDENT_DISAGREES 41
- NO_EXACT_FIT 34
- NO_VOCABULARY_FIT 55
- LEAKY_SR_GROUP 25
- LEGACY_MATCH_ONLY 34
- NO_BASIS 113

## 4. Router census if the proposals were confirmed (1,000-recipe sample, counts only)

Setup:
- The sample is seed 20261104, the non-BBC families, 997 texts with steps, 57,511 items, target SVAR-000009 (vitamin C), floor 1.0, margin 0.15.
- The no-overlay pass **reproduces the published S177 1,000-sample census exactly** (route, reasons, member presence, blockers, ABSENT and category-blocked counters, gate cross-tab; `baseline_reproduces_s177_1000` is true).
- Each scenario overlays the proposed category on the shipped presence screen in memory, then re-runs the same census.

| scenario | ING overlaid (with a router identity) | DIRECT | NOT_APPLICABLE | UNKNOWN | recipes with any DIRECT | items whose own ING flips UNKNOWN to ABSENT |
|---|---|---:|---:|---:|---:|---:|
| baseline (S177) | 0 | 73 | 1,345 | 56,093 | 67 | 0 |
| **A. HIGH among the top-100 sheet** | 46 (46) | 63 | 1,899 | 55,549 | 60 | 3,379 |
| B. the first 100 HIGH proposals | 100 (100) | 63 | 2,048 | 55,400 | 60 | 4,072 |
| C. all 193 HIGH | 193 (193) | 63 | 2,072 | 55,376 | 60 | 4,188 |
| D. HIGH and MEDIUM among the top-100 sheet | 83 (70) | 63 | 2,915 | 54,533 | 60 | 7,946 |
| E. all HIGH and MEDIUM | 1,107 (370) | 63 | 3,093 | 54,355 | 60 | 8,768 |

Scenario A, the answer to "confirm the top-100 HIGH proposals":
- The CATEGORY_EMPTY blocker falls from 8,970 to 5,591 items (−3,379), and TARGET_PRESENCE_UNKNOWN falls by 554.
- **554 items move UNKNOWN to NOT_APPLICABLE** (TARGET_ABSENT 1,345 to 1,899).
- **10 DIRECT items move to NOT_APPLICABLE** (DIRECT 73 to 63, recipes with any DIRECT 67 to 60). These are retention rows applied to an ING whose SR identity has no vitamin C. So confirming the categories restores the S176 kind of abstention that S177 lost.
- 4 prior-process-withheld items and 1 merged-lot item also become NOT_APPLICABLE.
- 12 ING become newly ABSENT in the sample: egg, plain flour, vanilla extract, parmesan, honey, cheddar, cornflour, turmeric, mozzarella, paprika, feta, ricotta.
- No item is created or lost: the deltas sum to zero.
- Only 13 of the sheet's 46 HIGH ING sit in the S177 blocked list. The other 33 (garlic, nutmeg, cumin, carrot and so on) are not blocked by category today, so confirming them changes no router count. Their value is the category itself.

**What the water, salt and stock decision is worth** (D minus A): 4,567 more items in the sample, and in the full census 2,632,622 items (water 1,427,479, salt 982,601, chicken stock 132,697, ice 60,809, beef stock 29,036). That is 7.5% of all 35,256,601 items. D and E also show the one effect that does not help: soy sauce proposed as CONDIMENT moves 174 items from CATEGORY_EMPTY to CATEGORY_MISMATCH, which is still UNKNOWN.

**Exact member-level projection on the S177 full census** (items whose own ING is no longer blocked by its category; not a route count, which needs a census run):

| scenario | ING clearing the block | S177 full-census items |
|---|---:|---:|
| A | 13 | 1,994,605 |
| B | 24 | 2,354,927 |
| C | 39 | 2,408,533 |
| D | 18 | 4,627,227 |
| E | 45 | 5,043,837 |

Of the 5,220,426 items blocked for the 52 uncategorised ING, the 45 cleared by E are 5,043,837. The 7 that stay blocked are bicarbonate of soda, cream of tartar, gelatine, dried yeast (no value fits), soy sauce, soya milk and tahini paste (crosswalk rejects).

**Not covered.** This is vitamin C only. A category matters for every nutrient the presence screen covers. A full-corpus route census was not re-run (about 2 h 17 min).

## 5. Related finding: 11 labelled ING are also blocked

Eleven of the 63 S177 category-blocked ING already have a category that the crosswalk rejects. They are out of scope here and nothing was changed.
- **Crosswalk question (widen the crosswalk or relabel):** mayonnaise (CONDIMENT vs SR "Fats and Oils", 75,654 items), peanut butter (NUT_SEED vs "Legumes", 66,242), cocoa (73,115) and cocoa powder (32,722), tahini (CONDIMENT vs "Nut and Seed", 5,166), ice cream (DAIRY, 32,241), milk chocolate (DAIRY, 3,609), green olives (VEGETABLE vs "Fruits", 1,111), fish sauce (SEAFOOD vs "Soups, Sauces", 19,383), chestnut mushroom (FRUIT, 47).
- **Ledger label error:** white chocolate is filed under SEAFOOD (14,789 items).

## 6. Tests and runs

- `pytest -q tests/unit/test_s178_ingcat_rules.py tests/unit/test_s178_ingcat_build.py`: **77 passed** (2 `-m ledgers` tests deselected by default). With `-m "ledgers or not ledgers"`: **79 passed**.
- **Rules (57):**
  - The brief's cases: salt, water and ice, leavening, soy sauce, mayonnaise, stock.
  - HIGH versus MEDIUM versus LOW.
  - Dual-use words, the vocabulary guard, utensils, 36 parametrised lexical cases.
  - The SR group table agrees with the S177 crosswalk.
- **Build (22):**
  - Scope (latest version, ACTIVE, no category) and order.
  - Columns and empty `human_decision`.
  - S177 counts and the crosswalk columns.
  - The output guard.
  - A full `main` run leaves every file under `ledgers/` byte-identical.
  - Sheet length, summary arithmetic, backtest label hiding.
  - Overlay flips EMPTY to ABSENT only when the crosswalk confirms, and leaves the base screen untouched.
  - Scenario selection.
  - The shipped CSV and simulation against the real ledger.

Run records, host `manjot-server`, tree `~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)`, git_commit `2d45f68+uncommitted`. Columns: `run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes`.

```
RUN-S178-INGCAT-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),2d45f68+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS|TASTESET,4,tools/s178_ingcat_propose.py --overwrite --simulate --workers 4,registry/ing_category_proposals_S178_DRAFT.csv,2b464677f7a695be9ae10121bb8546b700ca97b76a3f720a6be45d1f0706b80a,2026-11-09T11:04:53Z,2026-11-09T11:14:15Z,DONE,"INGCAT; also writes the top-100 sheet c54c18f1... and summary 602e62a8...; ING.jsonl sha256 ef439951... identical before and after; an earlier run 11:00:52Z-11:03:34Z (CSV 94a9c851...) is superseded by a second batch of lexical words and phrases (pasta shapes, spirits, curry pastes, colourings and similar)"
RUN-S178-INGCAT-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),2d45f68+uncommitted,FOODCOM|GUTENBERG_SEGMENT|WIKIBOOKS|TASTESET,4,tools/s178_ingcat_propose.py --overwrite --simulate --workers 4,reports/s178/ingcat/ingcat_router_simulation_1000_S178.json,0c76fb7e9adeaa8c8ad363f4fd7793ed964c7b005d0ebf61dc3a08ce24bb9e4d,2026-11-09T11:04:53Z,2026-11-09T11:14:15Z,DONE,"1000-sample seed 20261104 target SVAR-000009; baseline reproduces the S177 1000 census; overlay runtime only; protected-ledger baseline PASS before and after; load average 60-70 during this run"
RUN-S178-INGCAT-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),2d45f68+uncommitted,—,1,python -m pytest -q tests/unit/test_s178_ingcat_rules.py tests/unit/test_s178_ingcat_build.py -m "ledgers or not ledgers",,,,DONE,"79 passed (rules 57, build 22); start/end not recorded (about 5 s)"
```

## 7. Open questions and decisions for a human

1. **Water, salt, stock, leavening, additives.** Pick between the closest existing value (water to BEVERAGE, salt to HERB_SPICE or CONDIMENT, stock to CONDIMENT) and a new value. New values need `CATEGORY_CROSSWALK` rows. Stake: about 2.63M full-census items for water, ice, salt and stock.
2. **Crosswalk.** Does a human want CONDIMENT to accept "Legumes" (soy sauce), "Vegetables" (ketchup) or "Nut and Seed" (tahini), and mayonnaise or peanut butter to pass? Today they stay UNKNOWN whatever their category.
3. **The 11 labelled-but-blocked ING** in section 5, including the white chocolate label error.
4. **The 13 non-food ING.** Deprecate or leave.
5. **How confirmed values enter the ledger.** Out of scope: no tool here writes an ING version. The ledger is append-only, so a human-approved batch would be a new ING version per id by whoever owns that write.
6. **Rules are AI-authored.** The lexical tables were written and tuned by an AI. A reviewer who wants more than the top 100 should read the MEDIUM rows flagged `DUAL_USE` or `SR_GROUP_DISAGREES` first.
7. **Mention counts.** They are ingredient-line counts (`vocab_corpus_frequency_v1.parquet`), not router items. The BBC-derived count is used only as a tie-break and is not shown in the order key.
