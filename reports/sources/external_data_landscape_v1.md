# External data landscape (S116, 2026-10-20)
Registry: `registry/sources/external_data_source_registry.csv` (27 sources: licence, role, status). Kaggle survey: `reports/sources/kaggle_survey_s116.csv`. GitHub/HF: `github_hf_food_resources_v1.csv` (29 rows, licences from the GitHub API / HF tags). Transition candidates: `infoods_transition_candidates.csv`.
Principle: we are not short of recipes; we are short of trustworthy process->state evidence aligned to recipes.

## Downloads performed (all under git-ignored data/external/, hashed in the registry)
Food.com `recipes.parquet` (522,517 rows; Kaggle CLI with the machine's configured credentials, no terms gate; metadata: CC0-1.0); FNDDS 2021-2023 JSON (official FDC); FAO uFiSh 1.0, Density v2, AnFooD 2.0 (official FAO); USDA Cooking Yields Meat & Poultry R2 CSV (CC0, Ag Data Commons). Not obtained: AH-102 PDF (3 URLs 404), FNDDS CSV (200 MB, not needed yet), official FSANZ AFCD files, Recipe1M/RecipeNLG (gated or non-commercial).

## Findings
- **Food.com**: instruction-level candidate pool. 150k sampled recipes: 48,969 contain an ingredient x process match to 243 of 338 ledger cells. The CC0 label is the uploader's; the underlying text is Food.com user content, so analysis stays local and committed files are text-free.
- **FNDDS**: 5,432 survey foods with 18,584 ingredient rows; each ingredient row carries a `retentionCode` (about 3,000 non-zero, 138 distinct) linking a raw SR ingredient to USDA R6 retention. This is STRUCTURAL LINKAGE for canonical linking, CQPO and initial composition. It contains no measured before/after magnitudes; it is not transition truth.
- **USDA Cooking Yields R2 (CC0)**: 173 rows, yield %, n, SD, min, max, moisture and fat change for meat/poultry cuts by method; 16 rows are the AH-102 1975 values. COMPILED_REFERENCE, directly usable for YIELD/MASS transitions of meat. Narrow (meat only).
- **uFiSh**: raw/cooked/processed fish rows. Cooked rows are mostly "calc. from <raw id>", i.e. calculated, not measured pairs (752 rows classed COMPILED_REFERENCE, 5 CROSS_STUDY). Sheet "09 Yield Factors" gives method, n and reference per species: COMPILED_REFERENCE. Only one Gold recipe is likely seafood.
- **AnFooD 2.0**: r/d/p processing codes without process detail: 126 SAME_STUDY_UNMATCHED, 179 QUALITATIVE_ONLY.
- **Density v2**: volume<->mass, useful for the quantity engine (licence not stated; cite).
- **Kaggle**: 17 process-type queries (retention, yield, kinetics, Maillard, texture, volatile, density...) returned NO dataset carrying process-effect data; 213 datasets seen, 35 in process-category hits, none relevant. Beyond Food.com the useful hits are an AFCD mirror (CC-BY-SA, prefer the official FSANZ files) and UmamiDB amino acids (CC0 declared); Food.com mirrors and the BitterSweet set duplicate what we hold.
- **GitHub/HF**: `strangetom/ingredient-parser` (MIT) is a free, key-less B08 baseline; FoodKG is Apache-2.0 but its recipe layer is gated Recipe1M; SKIP (Apache-2.0) is a published entity-state baseline; OpenPI (MIT) and ProPara (Apache-2.0) are already or optionally used; recipe-scrapers (MIT) is not used (third-party scraping, D-003). No public parser for USDA retention/yield tables exists beyond our own.

## Answers
1. Strongest legally usable new recipe corpus: **Food.com (Kaggle irkaal)**, with the authority caveat; Wikibooks (CC BY-SA) is already ledgered.
2. Strongest new transition-evidence source: **USDA Cooking Yields R2** (structured, CC0, n/SD, moisture and fat change) for meat; for vegetables nothing structured exists: literature curation is needed.
3. Strongest quantity/yield source: **FNDDS portions/weights + USDA yields + FAO Density**.
4. Strongest external parser baseline: **strangetom/ingredient-parser** first (MIT, no quota), Zestful second (ToS allows storing results).
5. Useful Kaggle beyond Food.com: none for process evidence; see the survey for the AFCD mirror and UmamiDB.
6. Missed GitHub/HF resources: ingredient-parser, SKIP, FoodKG mapping files, OpenPI/ProPara code.
7. Duplicates: Food.com mirrors on HF/Kaggle, BitterSweet Kaggle set, Open Food Facts code/data (aliases already ingested), R6 CSV (ingested).
8. Do not use: Spoonacular (LIVE_ONLY), RecipeNLG and Recipe1M derivatives (research-only), MISKG, Tiny Plates bulk/training without permission, Lexis (no licence), Yummly/What's Cooking.
9-15 are in `reports/h_state/h_state_coverage_lift_forecast.md` (current 14; +10/+20/+30/+40 Gold: 21.5/29/36.5/44 conservative, 44/74/104/134 optimistic; +5/+10/+20 cells: 17.7/20.3/23.7 conservative; best hybrid +30 Gold +10 cells = 42.8 conservative; question authoring should wait).

## Roles (one or more per resource; full list in the registry)
B07 recipe corpus: Food.com, Wikibooks. B08 semantic engine: RecipeNLG (research only). B09 vocabulary: FoodOn, FNDDS, OFF. B10 quantity/portion: FNDDS, Density v2. L12 molecular: FooDB/UmamiDB (research). L13E cultural: XiaChuFang, endangered recipes (later). L14 process evidence: R6, Phenol-Explorer, Bognar, USDA Cooking Yields R2, uFiSh yield factors. L15 transition/kinetic: R6, Phenol-Explorer (no new kinetic dataset found). EXTERNAL_BASELINE: ingredient-parser, Zestful, SKIP. ROBUSTNESS_TEST: TheMealDB, TheCocktailDB, Epicurious, OpenPI. LIVE_ONLY: Spoonacular, Tiny Plates. DO_NOT_USE: ReceptAPI, MISKG, Lexis, Yummly.

## Boundaries
Foodoscope RecipeDB: recipe/procedure prior. FlavorDB: molecule/flavour prior. Open Food Facts: product/vocabulary/nutrition under ODbL. None of these is measured cooking-transition truth. Simulator contract: `docs/simulator_data_contract.md`, code `src/culinarystate/state_graph/source_class.py`; ingest policy `src/culinarystate/sources/policy.py`.

## Kinetic/transition source search (honest gap)
Searches for machine-readable thermal-degradation kinetics (vitamin C, anthocyanin, chlorophyll, acrylamide, Maillard, lipid oxidation, gelatinisation, enzymatic browning) found only per-paper tables (e.g. anthocyanin Ea in berry puree, MDPI Foods 2020; vitamin C/anthocyanin Ea in beet stems; blueberry juice 80.4 kJ/mol). No database exists. Traceable review tables and supplementary spreadsheets are the realistic route; each needs human extraction and verification. Ranking by relevance/measured data/time-temperature info: (1) vitamin C and anthocyanin degradation in vegetables/fruit (matches our top missing targets), (2) polyphenol retention (already Phenol-Explorer), (3) acrylamide/Maillard model systems (needs chemistry scoping), the rest later. Not ingested.
