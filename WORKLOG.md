# WORKLOG — CulinaryState (Group 17: Kush + Parv)

Append-only, sequential, timestamped (IST). One entry per step. Written by `tools/log_step.py`; never edit past entries — add a correcting step instead.

Presentation: **25–26 Nov 2026**.

### S001 · 2026-10-18 10:43 IST · B00 · Repo scaffold + Bible docs
- **Who:** Kush+Claude
- **Did:** Created culinarystate/ repo (git init, main). Copied SSOT v15, master plan v4.0, R&D plan v2, Max prompt v2, proposal PDF into docs/. Package skeleton src/culinarystate/* and tests/. Found Parv's old repo absent on this machine → rebuild here (D-001).
- **Files:** `docs/`, `src/culinarystate/`, `.gitignore`
- **Verified:** ls tree present

### S002 · 2026-10-18 10:43 IST · B00 · Step logger
- **Who:** Kush+Claude
- **Did:** tools/log_step.py appends timestamped (IST), sequential S### entries to WORKLOG.md; append-only.
- **Files:** `tools/log_step.py`, `WORKLOG.md`
- **Verified:** this entry written by it

### S003 · 2026-10-18 10:43 IST · B01 · SSOT index built and verified
- **Who:** Kush+Claude
- **Did:** tools/build_ssot_index.py: H1–H3 headings with line ranges, ID anchors (RQ16, RQ13E, E16, E13E, G13E, G16, G15, G14, G13, RISK-E, R13E), boxed statements. Checked against plan Appendix 1.
- **Files:** `tools/build_ssot_index.py`, `docs/SSOT_INDEX.md`
- **Verified:** all 14 inventory checks OK (1,799,542 bytes; 45,697 lines; 309 H1; 30/30 RQ16; 14/14 G16; 18/18 G15 …)

### S004 · 2026-10-18 10:43 IST · B02 · Source reachability probe (no API key)
- **Who:** Kush+Claude
- **Did:** Single requests only. Reachable: RecipeDB/FlavorDB/CulinaryDB web pages (200), USDA R6 PDF (200), Phenol-Explorer (200), FDC API DEMO_KEY (200), PubChem PUG-REST (200), FoodOn OWL (200), HF datasets API (200). RecipeDB recipe2-api: timeout. cosylab robots.txt: 404. Local: A1 11,934 BBC recipes + TASTEset NER gold.
- **Verified:** HTTP codes recorded
- **Next:** SNAP-/API- records when ingesting

### S005 · 2026-10-18 10:43 IST · B00 · STATUS / DECISIONS / CLAUDE.md
- **Who:** Kush+Claude
- **Did:** STATUS.md with COMPLETE/ACTIVE/BLOCKED, dated W1–W6 plan to 25–26 Nov, next 20 tasks. DECISIONS D-001…D-004 (rebuild here; JSON Schema over pydantic; A1 BBC + TASTEset as RecipeDB stand-ins; base python).
- **Files:** `STATUS.md`, `DECISIONS.md`, `CLAUDE.md`

### S006 · 2026-10-18 10:49 IST · B00/P2 · Core ledger schemas + ID minter + validators
- **Who:** Kush+Claude
- **Did:** 36 record types (SRC SNAP API STUDY MEAS ING ALIAS ENTITY MOL IMAP PROC TOOL COND SVAR UNIT QNT POR ALLOC REC INST EVT STATE REF GRAPH EVD RXN WARN ALLERGEN DATASET SPLIT MODEL EXP GATE RQ RS CLM) as JSON Schema 2020-12 with common envelope (version, status, provenance, verification). UNKNOWN-aware QVALUE (UNKNOWN/QUALITATIVE can't carry numbers). Laws in rules.py: AI≠human verification; E4 needs HUMAN_VERIFIED; AH1 origin_type/study_ids; locator for E1–E4; percent-change consistency; censor flag; no invented grams (QNT needs POR for non-mass units); POR needs source; IMAP 4 relation types; 'medium heat' never numeric; STATE append-only + observation override; FlavorDB never allergen authority; SOTA claim needs GATE; TEST-selected checkpoint ≠ clean reproduction. Append-only JSONL store with versioned revise(); IdMinter dedups by key, never reuses numbers.
- **Files:** `src/culinarystate/ledgers/`, `tests/unit/test_ledgers.py`, `tests/fixtures/ledger_examples.py`, `ledgers/schemas/`, `tools/export_schemas.py`, `pyproject.toml`
- **Verified:** pytest 103 passed; mutation check: disabling each of 10 rules makes ≥1 test fail
- **Next:** S007 DEL-1: USDA R6 retention factors → EVD (E3)

### S007 · 2026-10-18 10:55 IST · DEL-1/B02/B06 · USDA Retention Factors R6 → 7,018 EVD rows (E3)
- **Who:** Kush+Claude
- **Did:** Fetched retn06.txt + retn06.pdf (sha256 pinned, SNAP records). Read PDF methods: mostly %TR, some %AR (basis RETENTION_TR_OR_AR); rounded to 5% (±2.5); >100 reported as 100 → CENSORED GT_CAP ≥97.5 (2,620 rows, direction UNKNOWN, no fake 100); 24 blank → UNKNOWN; all rows dated 09/1975 (placeholder). Deterministic description parser: matrix / ordered steps / forms / modifiers (drippings, coating, cooking water consumed/drained, skin, shell, medium) / duration; 270/270 descriptions parse with 0 unparsed. Built SRC×1, SNAP×2, MEAS×1, SVAR×26 nutrients, COND×270 (duration measured/range/unknown, temperature UNKNOWN), EVD×7,018. ingredient_id/process_id null until ING/PROC registries (AH2). Added store.upsert (idempotent; changed content → new version). Schema: GT_CAP censor, EVD process.steps/modifiers, matrix.food_group, basis enum, censored-flag rule now covers derived values.
- **Files:** `src/culinarystate/ingest/acquire.py`, `src/culinarystate/ingest/usda_r6.py`, `src/culinarystate/ingest/usda_r6_build.py`, `tools/ingest_usda_r6.py`, `tests/unit/test_usda_r6.py`, `ledgers/data/`
- **Verified:** pytest 119 passed; counts 4,374 measured + 2,620 censored + 24 unknown = 7,018 = raw; 0 re-validation errors; rerun = all unchanged
- **Next:** S008 Phenol-Explorer retention data → EVD (E3); DEL-1 ≥1,000 DB-row minimum already met by R6 alone

### S008 · 2026-10-18 11:11 IST · B10/P3 · Quantity system v0: unit catalogue + grammar + normalizer + corpus coverage
- **Who:** Kush+Claude
- **Did:** units.py: 72 units (physical, locale culinary volume, count/portion, package, verbal, regional, length); exact definitions cited (NIST HB44 App C, UK WMA 1985, 21 CFR 101.9, SI); metric spoon / AU tbsp / metric cup marked NEEDS_SOURCE; katori/glass/mug carry no number. grammar.py: numbers/fractions/unicode+HTML-entity fractions/ranges/multipliers ('2 x 400g cans'), sized units ('375g sheet'), packages, dual units ('250ml/9fl oz'), parenthetical stated mass ('(about 500g)'), size/approx/heaped qualifiers, 'juice of', word numbers, implicit one ('small bunch'). normalize.py: mass/volume/count channels (SSOT §235.7); EXACT_PHYSICAL / LOCALE_CONVENTION / SOURCE_STATED; ambiguous locale → RANGE; counts/volumes never become grams (Q6) without POR; contradictions flagged, never rewritten (§235.9). QNT schema: mass_g/volume_ml/count, qualifiers, conversion_method; rule blocks non-mass→grams without SOURCE_STATED/PORTION_RECORD. Iterated twice on corpus failures (HTML entities, optional-group bug, fraction order, sized units, 'gram flour').
- **Files:** `src/culinarystate/quantity/`, `tests/unit/test_quantity.py`, `tools/quantity_coverage.py`, `reports/quantity_coverage_v0.md`, `reports/quantity_coverage_v0.json`
- **Verified:** pytest 180 passed; BBC 116,997 lines: 90.2% ≥1 numeric channel, mass Q0 29.8% (exact or source-stated), 0 invented grams by construction; remaining NONE 5.7% mostly genuinely unquantified
- **Next:** POR- records from FDC portions (sourced) to lift count/volume→mass; S010 ingredient registry

### S009 · 2026-10-18 11:15 IST · B09/P3 · Ingredient registry v1 (ING/ALIAS) from A1 corpus
- **Who:** Kush+Claude
- **Did:** 2,009 ING concepts = A1 canonicals in ≥3 recipes (corpus-supported only, no padding); 2,031 ALIAS rows (EXACT/PLURAL/SPELLING/SYNONYM bands). Structural parents only: FORM_OF (turmeric powder→turmeric) and VARIANT_OF (unsalted butter→butter, roast potato→potato) = 325 parent links; 711 head-noun groups kept for review only (almond milk is not dairy milk). 17 curated polysemous concepts (coriander, pepper, squash, chips…) ambiguity HIGH, AI-drafted → human review. 32 rejects for review: utensils (10), edible food parts needing a part model (17: pork skin, salmon trimmings…), adjective-only (5). Crosswalks FoodOn/FDC/FlavorDB/RecipeDB all UNRESOLVED_EXTERNAL; scientific identity UNKNOWN. Rebuild deprecates dropped concepts (new version), never deletes.
- **Files:** `src/culinarystate/vocab/registry_build.py`, `tools/build_ingredient_registry.py`, `tests/unit/test_registry_build.py`, `registry/ingredients/`, `reports/ingredient_registry_v1.md`, `ledgers/data/ING.jsonl`, `ledgers/data/ALIAS.jsonl`
- **Verified:** pytest 184 passed; mention coverage 95.4% (top50 43.8%, top500 84.9%); surface collisions 0 (A1 normalization deterministic — semantic ambiguity tracked separately); rerun = all unchanged
- **Next:** FDC SR Legacy bulk download → crosswalk candidates + POR portion records

### S010 · 2026-10-18 11:19 IST · B09/B10/P3 · FDC SR Legacy: crosswalk candidates + portion candidates + gain estimate
- **Who:** Kush+Claude
- **Did:** Downloaded FDC SR Legacy CSV 2018-04 (CC0, 6.07 MB, sha256 b8081729…; router DNS SERVFAIL for usda.gov → pinned public-DNS IP). Matcher: exact head segment incl. inverted SR names ('Oil, olive'), category-prefix skip ('Spices, …'), raw preference, extra-token and brand penalties, UK→US synonym expansion (plain flour→all-purpose, double cream→heavy whipping, coriander→cilantro…), form synonyms (powder→ground, unsalted→without salt). Portion modifier parser → unit/size/note, grams per unit = gram_weight/amount. Outputs ranked top-3 candidates per ING with empty human_decision column; portion candidates from top-1 HIGH (locale US).
- **Files:** `src/culinarystate/vocab/fdc.py`, `tools/build_fdc_crosswalk.py`, `tests/unit/test_fdc.py`, `registry/ingredients/fdc_crosswalk_candidates_v0.csv`, `registry/ingredients/fdc_portion_candidates_v0.csv`, `reports/fdc_crosswalk_v0.md`, `DECISIONS.md`
- **Verified:** pytest 188 passed; top-1 bands HIGH 550 / MEDIUM 241 / LOW 850 / none 368 (paneer, garam masala absent in SR = correct UNRESOLVED); HIGH carries 67% of recipe-frequency weight; verified links would ground 30,714 more lines (24.8%)
- **Next:** HUMAN: tick human_decision for top ~300 HIGH rows. Code: density path (cup→g/mL→tbsp, Q2) for 22,646 unit-mismatch lines; promote verified rows → POR-

### S011 · 2026-10-18 11:22 IST · DEL-3/B11/P6 · Event-sourced state engine core + symbolic quantities
- **Who:** Kush+Claude
- **Did:** symqty.py: SymQty = Σ coef×Base(dim g/mL/count/qual, interval, raw label); scale/plus/minus with Fraction coefficients; evaluate() numeric only when all terms numeric and one dimension, else UNKNOWN with symbolic render ('50 g − 1 tbsp'); interval propagation for fractions (½×100–120 g = 50–60 g). engine.py: immutable events Add/Transform/Merge/Split/Reserve/Discard/Recombine/Transfer/Observe/Predict/OmittedStepCandidate/AcceptCandidate; pure replay() → Graph (append-only versions per entity, concept map, edges with SSOT §233.5 relations, audit log, issues, candidates); observation overrides prediction with superseded belief kept in audit, later predictions cannot override an observation; omitted-step candidates applied only after AcceptCandidate (by human); canonical JSON + sha256 for replay determinism; validation issues for unknown/consumed entities, split fractions >1, label reuse. Self-review found label-overwrite hole (Merge/Split onto existing label replaced history) → fixed + regression test.
- **Files:** `src/culinarystate/state_graph/symqty.py`, `src/culinarystate/state_graph/engine.py`, `tests/unit/test_state_engine.py`
- **Verified:** pytest 204 passed (15 engine/symqty tests: pancake merge+reserve+transfer, dough split 500→125/375 g, pasta water discard+recombine with all relation types, observe>predict audit, candidate gating, determinism sha256)
- **Next:** Recipe→events compiler (A1 instruction_events + quantity parser); ledger export ENTITY/STATE/EVT/GRAPH; DEL-3 scorer

### S012 · 2026-10-18 11:24 IST · B08/B17/P5-B · Common scorer: spans, linking, relations, coref, quantities, state, grouped bootstrap
- **Who:** Kush+Claude
- **Did:** scoring/metrics.py: span PRF exact/relaxed (1:1 greedy), micro/macro/per-label, label filter (SIZE excluded vs included); linking Acc@1/Recall@k/MRR with NIL gold (correct abstention) + over-link rate; tuple/relation PRF per relation; coreference B³ + pairwise; quantity channel scoring with invented_value_rate (numeric where gold UNKNOWN) and missed_value_rate; grouped bootstrap CI over families/sources/studies (seeded). scoring/state_metrics.py: DEL-3 state-field accuracy on alive entities (fields, location, symbolic qty), alive-entity PRF, merge/split F1 on structural relations, all-edge relation scores (version-agnostic), replay consistency (sha256 + issues).
- **Files:** `src/culinarystate/scoring/metrics.py`, `src/culinarystate/scoring/state_metrics.py`, `tests/unit/test_scoring.py`
- **Verified:** pytest 215 passed; hand-computed checks: B³ P/R, MRR, macro≠micro, relaxed 1:1, missed-reserve degrades merge/split recall + field accuracy
- **Next:** Phenol-Explorer ingest when crawl finishes; recipe→events compiler; annotation handbook + gold schema

### S013 · 2026-10-18 11:28 IST · P4/DEL-3/B07 · Gold annotation foundation: schema, compiler, agreement, handbook, pilot batch
- **Who:** Kush+Claude
- **Did:** annotation/gold.py: gold-1.0 JSON Schema (15 span labels, 8 event types, coref, unknowns; annotator ∈ {Kush, Parv, ADJUDICATED}), validator (offset/text match, unique entities, required event fields, TODO guard), compiler to engine events (quantities via grammar+normalizer, never invented). agreement.py: span exact/relaxed F1, char-level Cohen κ, concept agreement, coref B³, replayed state comparison; adjudication rows. examples.py: 3 synthetic worked recipes (white sauce reserve+remaining, pasta drain-reserve-discard-recombine, roast veg with fan-oven setpoint + endpoints). Docs: annotation_handbook_v1.md, annotation_checklist.md, hard_examples.md (16), UNKNOWN_examples.md (12), adjudication_template.csv, gold_schema.json. tools/gold_cli.py validate/agree/schema/examples. tools/make_gold_batch.py: stratified pilot_20 (reserve/split, drain, baking, Indian, simple, multi-component) → text-only templates (no label pre-fill). Fixed: A1 recipe_id ≠ raw line number → map by URL.
- **Files:** `src/culinarystate/annotation/`, `tools/gold_cli.py`, `tools/make_gold_batch.py`, `annotation/`, `tests/unit/test_gold.py`, `.gitignore`, `DECISIONS.md`
- **Verified:** pytest 225 passed; 3 examples validate + replay with 0 issues; demo agree shows concept disagreement row; templates fail validation until TODOs filled
- **Next:** HUMAN: Kush + Parv annotate pilot_20 independently (≈15–25 min each) → agree → adjudicate → handbook v1.1

### S014 · 2026-10-18 11:39 IST · DEL-3/B11/P5 · Rule baseline recipe→events compiler (B-rules) + entity alignment for scoring
- **Who:** Kush+Claude
- **Did:** state_graph/rule_compiler.py: ingredient lines → Add (cleaned food label, longest registry concept), per-sentence processes (phrases first; case-insensitive verb matching with light inflection; noun-like aliases (butter/oil/salt/heat…) only in verb position; 'the reserved X' is an adjective), rules for Reserve (portion from sentence), drain/strain → Split+Discard (+Reserve if 'reserving'), divide into N (fractions only if 'equal'), combination verbs or 'X in/with Y' → Merge into running mixture, reserved mention → Recombine, tool words → Transfer, other actions → Transform. scoring/state_metrics.py: align_entities (ingredients by line order, intermediates by Jaccard of aligned ingredient ancestors, greedy 1:1), relabel, aligned_state_scores. Iterated 4× against gold examples: fixed case-sensitive regex (lost all sentence-initial imperatives), noun-as-verb, reserved butter merged into roux, missing drain target.
- **Files:** `src/culinarystate/state_graph/rule_compiler.py`, `src/culinarystate/scoring/state_metrics.py`, `tests/unit/test_rule_compiler.py`
- **Verified:** pytest 234 passed; smoke scores on 3 synthetic gold: merge/split F1 1.00 / 0.35 / 1.00 (pasta fails on hypernym 'pasta'→spaghetti — known baseline gap); NOT a result until 40 human Gold recipes
- **Next:** Phenol-Explorer ingest after crawl; process registry commit; EDA generator

### S015 · 2026-10-18 11:40 IST · B05/P3 · Process registry v1 (PROC) with corpus + evidence coverage
- **Who:** Kush+Claude
- **Did:** spaCy en_core_web_sm verb discovery on 15k BBC steps → curated process vocab (148 processes, 18 families; ACTION vs ENDPOINT; lemma aliases; phrase patterns 'bring … to the boil', 'set … aside', 'leave to cool', 'turn down the heat'; IGNORE list of non-process verbs). Required condition axes per family (structural); mechanism families AI-drafted, flagged to verify vs R3 notes. Evidence step names (USDA/PE) mapped via map_step_name (0 unmapped). Iterated once on top unmapped verbs (break/crack, scoop, pop, smooth, taste) and gap regex ('set the chicken aside').
- **Files:** `src/culinarystate/process/vocab.py`, `tools/build_process_registry.py`, `tests/unit/test_process_vocab.py`, `registry/processes/`, `reports/process_registry_v1.md`, `ledgers/data/PROC.jsonl`
- **Verified:** 39,540 BBC steps: recognised process: 39,252 (99.3%); EVD step mentions 8,655 mapped / 0 unmapped; 109 corpus actions with ZERO state-change evidence (put, add, mix, cool, melt, chop, beat …) → sparsity finding for DEL-1/2
- **Next:** EDA cell-key fix; Phenol-Explorer ingest

### S016 · 2026-10-18 11:41 IST · P14/Part-M · Reusable ledger EDA report generator
- **Who:** Kush+Claude
- **Did:** eda/report.py: generic per-ledger profile (records/versions, status, verification, provenance method, top sources, field missingness incl. UNKNOWN/NOT_APPLICABLE), evidence section (tiers, origin, source family, study lineage, independent groups, censoring, RF status, direction, basis, ING/PROC link rates, condition-axis completeness, rows with temperature, unique matrices/steps/targets/cells, matrix×process density, long tail, replicate rows per cell, conflict candidates = same cell with opposite directions across independent groups), ingredient section (crosswalk status, ambiguity, parents, scientific identity, frequency concentration), process section (corpus actions without evidence). HTML (self-contained, dark-mode aware) + markdown + JSON. tools/eda_report.py. Self-caught bug: cell key ignored modifiers and form → reported 2,573 then 780 false duplicates in USDA; key now (matrix, form, steps, target, structural modifiers, duration).
- **Files:** `src/culinarystate/eda/report.py`, `tools/eda_report.py`, `tests/unit/test_eda.py`, `reports/eda/`
- **Verified:** pytest 236 passed; USDA: 7,018 unique cells, 0 replicates, 0 conflicts (single source); density 0.107; temperature known in 0 rows; ING/PROC link 0% (linking step pending)
- **Next:** Phenol-Explorer ingest + link EVD→ING/PROC + DEL-1 data card

### S017 · 2026-10-18 11:45 IST · DEL-2/B13/P8 · DEL-2 pipeline: cells, splits, D0–D7 baselines, censor-aware eval, conformal, MNAR — first USDA run
- **Who:** Kush+Claude
- **Did:** transition/dataset.py: explicit course-cell projection per source family (no USDA/PE merging; RF>1 not clipped; censored rows keep y_lower). splits.py: random, pair_holdout, matrix_disjoint, process_disjoint, study_disjoint via row→study connected components (refuses when single source/giant component, AM3); leakage check; split sha256. baselines.py: D0 persistence, D1 global, D2 process mean, D3 hierarchical shrinkage, D4 nearest compatible evidence (vectorised), D5 HistGradientBoosting (categorical+masks), D7 biased MF with side-info biases; D6 TabPFN SKIPPED (not installed/GPU). evaluate.py: censor-aware MAE, observed RMSE, grouped bootstrap CI, IPW MAE beside unweighted (propensity from marginal frequencies; degenerate grids handled), split-conformal 90% empirical coverage. tools/run_del2.py one command.
- **Files:** `src/culinarystate/transition/`, `tools/run_del2.py`, `tests/unit/test_transition.py`, `reports/del2/USDA-RETN-R6_results.md`, `reports/del2/USDA-RETN-R6_results.json`
- **Verified:** pytest 7 DEL-2 tests pass; USDA 7,018 rows run in 23 s. random: D5 0.025 vs D0 0.121; matrix_disjoint: D0 0.059 ≈ D4 0.057 (CIs overlap) — cold-food gains vanish; process_disjoint: D0 0.073 vs D5 0.067; conformal-90 empirical coverage 0.72–0.87 on cold splits (AH4). study_disjoint NOT POSSIBLE for USDA (single source). Caveat: USDA factors largely imputed.
- **Next:** Re-run on Phenol-Explorer (study-disjoint possible); experiment cards EXP-D0…D7

### S018 · 2026-10-18 11:49 IST · B05/X1/ledger-queue#6 · TOOL ledger v1 (utensils/cookware/appliances/materials) + corpus-measured process↔tool links
- **Who:** Kush+Claude
- **Did:** Mined BBC steps for heads after 'in/into/on/with/using a …' → curated 76 tools in 7 categories (heat sources, appliances, cookware, vessels, utensils, consumables, measurement) incl. Indian equipment (tawa, kadai, handi, tadka pan, pressure cooker). find_tools(): multi-word aliases, material capture (non-stick, cast-iron, ovenproof…), weak/verb-like aliases (whisk, grill, microwave, sieve, pan, tin, dish…) counted only after article/adjective. Process→tool links from sentence co-occurrence (count ≥20, lift ≥2) written into PROC.tool_ids (115 processes revised). Material reactivity / max temperature deliberately UNKNOWN (needs authority → WARN). Fixed verb-as-tool (Whisk the eggs) and material-inside-alias bugs found by tests.
- **Files:** `src/culinarystate/process/tools.py`, `tools/build_tool_registry.py`, `tests/unit/test_tools.py`, `registry/tools/`, `reports/tool_registry_v1.md`, `ledgers/data/TOOL.jsonl`, `ledgers/data/PROC.jsonl`
- **Verified:** pytest 246 passed; 83.7% of 39,540 steps mention ≥1 tool; 535 process↔tool links (fry→frying pan lift 21.3, line→baking parchment 27.3, preheat→oven 14.9)
- **Next:** Phenol-Explorer ingest (crawl nearly done); UNIT ledger records; REC ledger

### S019 · 2026-10-18 11:49 IST · B10/ledger-queue#7 · UNIT ledger records + unit-authority SRC records
- **Who:** Kush+Claude
- **Did:** tools/build_unit_registry.py: 74 UNIT records from quantity/units.py (physical / locale culinary volume with per-locale conventions / count-portion / package / verbal / regional / length) each linked to SRC records for its authority: NIST HB44 App C, UK WMA 1985 Sch1, 21 CFR 101.9, SI brochure (AI_PRECHECKED — definitions recalled by AI, human to confirm citation) and 4 conventions (metric spoon, AU tbsp, metric cup, UK dsp) marked NEEDS_SOURCE. Regional vessels (katori, glass, mug) carry no volume.
- **Files:** `tools/build_unit_registry.py`, `registry/units/unit_registry_v1.csv`, `ledgers/data/UNIT.jsonl`, `ledgers/data/SRC.jsonl`
- **Verified:** 74 UNIT + 8 SRC created; rerun all unchanged; 4 units flagged NEEDS_SOURCE (tsp, tbsp, dsp, cup)
- **Next:** HUMAN: cite authorities for metric spoon/cup conventions. Code: Phenol-Explorer ingest; REC ledger

### S020 · 2026-10-18 11:51 IST · B07/ledger-queue#8 · REC ledger (11,934 recipes) + near-duplicate families + REC↔ING links
- **Who:** Kush+Claude
- **Did:** ingest/recipe_families.py: word-5-shingle MinHash (64 perms) + 16-band LSH + exact Jaccard ≥0.8 confirmation + union-find families (plan H1). tools/build_recipe_registry.py: REC record per A1 recipe (title, url, sha256 of title+ingredients+steps, family_id, cuisine, counts, raw_location pointer; raw text stays local per D-003; A1 id in external_refs). recipe_ingredient_links_v1.csv joins every A1 mention to REC and ING ids.
- **Files:** `src/culinarystate/ingest/recipe_families.py`, `tools/build_recipe_registry.py`, `tests/unit/test_recipe_families.py`, `registry/recipes/`, `reports/recipe_registry_v1.md`, `ledgers/data/REC.jsonl`
- **Verified:** pytest 248 passed; 11,934 REC created; 7 near-duplicate pairs → 5 multi-recipe families (largest 3); REC↔ING: 123,598 mention rows, 95.4% linked
- **Next:** Phenol-Explorer ingest + EVD→ING/PROC linking

### S021 · 2026-10-18 11:54 IST · B16/AH3/ledger-queue#10 · ALLERGEN ledger from FSSAI Labelling & Display Regs 2020, Reg 5(14)
- **Who:** Kush+Claude
- **Did:** Downloaded official FSSAI compendium (Version-I 23.09.2021, sha256 ca2df1df…) → SRC (AUTHORITY_STANDARD) + SNAP. Extracted Reg 5(14) verbatim: 8 groups — cereals containing gluten (wheat, rye, barley, oats, spelt; glucose-syrup/maltodextrin/distillate exceptions ≤20 mg/kg), crustacean, milk, egg, fish, nut (peanuts + tree nuts), soy, sulphite ≥10 mg/kg; 'May contain' for cross-contamination; exemptions for derived oils, distilled spirits, product-is-allergen, raw agricultural commodities. 8 ALLERGEN records with quoted legal_reference. ING membership = AI-drafted keyword mapping with exceptions (coconut/almond milk, nutmeg, butternut, derived oils, chocolate eggs, pine nut → review), verification UNVERIFIED; sulphite review-only (concentration-dependent). Memory of the list confirmed only after reading the gazette text.
- **Files:** `tools/build_allergen_registry.py`, `registry/allergens/ing_allergen_review.csv`, `ledgers/data/ALLERGEN.jsonl`, `ledgers/data/SRC.jsonl`, `ledgers/data/SNAP.jsonl`
- **Verified:** 8 ALLERGEN records; memberships gluten 177, milk 136, fish 43, nut ~40, soy ~22, egg ~14, crustacean 13 ING concepts; spot-check fixed groundnut oil / chocolate egg / pine nut errors
- **Next:** HUMAN: tick ing_allergen_review.csv before DEL-5 hard constraints. Code: Phenol-Explorer ingest

### S022 · 2026-10-18 12:01 IST · P1/DEL-1/B06 · Literature candidate harvest (OpenAlex) + verification queue + precheck report + DEL-1 data card tool
- **Who:** Kush+Claude
- **Did:** evidence/literature.py: 25 gap-driven queries (plan I3 worked examples: allium cutting, PPO browning, acrylamide frying, vitamin/folate leaching, chlorophyll→pheophytin, glucosinolates, carotenoids, lycopene, anthocyanin kinetics, pressure/microwave/stir-fry/sous-vide, tadka volatiles, curcumin, phytate soaking, idli/dosa fermentation), OpenAlex polite-pool harvest with cache, abstract reconstruction, transparent precheck (process/target hit, numeric results, primary-study language, OA, review→NEEDS_SOURCE, off-topic→REJECT). tools/build_verification_queue.py: Route A (Phenol-Explorer primary publications, ranked by condition completeness/rows/linking) + Route B (OpenAlex, DOI+title dedup, lineage-duplicate flag vs PE) → verification_queue_ranked_v1.csv (human_status/verifier/verified_at columns), conflict_queue.csv (same cell opposite directions across independent groups), rejected_candidates.csv, reports/evidence_precheck_report.html (with 10-minute verification protocol). tools/del1_data_card.py computes the DEL-1 acceptance table. Also prepared tools/ingest_phenol_explorer.py (tested on partial cache: 894 pages → 2,972 valid EVD rows, 107 studies) and tools/build_molecule_registry.py; fixed PER_VOLUME basis and month/year durations found in that test.
- **Files:** `src/culinarystate/evidence/literature.py`, `tools/build_verification_queue.py`, `tools/del1_data_card.py`, `tools/ingest_phenol_explorer.py`, `tools/build_molecule_registry.py`, `src/culinarystate/molecules/pubchem.py`, `registry/evidence/`, `reports/evidence_precheck_report.html`, `reports/DEL1_data_card.md`, `tests/unit/`
- **Verified:** pytest 257 passed; Route B: 509 candidates (130 VERIFY_NOW / 245 STRONG / 134 NEEDS_SOURCE), 73 rejected; data card 4/6 clauses pass (0/40 human-verified rows = human task)
- **Next:** Full PE ingest → link EVD → MOL/IMAP → refresh queue (Route A) + data card + EDA + DEL-2 on PE

### S023 · 2026-10-18 12:03 IST · P15 · Handoff docs: SOURCE_ACCESS, API_BLOCKERS, MANUAL_NEXT_STEPS
- **Who:** Kush+Claude
- **Did:** handoff/SOURCE_ACCESS.md (13 sources: access route, status, licence, storage rule, ledger, command; DNS-pinning note; books policy). handoff/API_BLOCKERS.md (8 blockers with impact/workaround/unblock owner — RecipeDB key, FlavorDB, FSIS/FoodSafety.gov 403 to scripts (tried twice, stopped, manual download), router DNS, FDC rate limit, rdkit, TabPFN, human verification). handoff/MANUAL_NEXT_STEPS.md (10 human tasks with input file, exact steps, time estimate, owner). Tried FSIS and FoodSafety.gov charts → HTTP 403 (CDN refuses automated clients) → not circumvented.
- **Files:** `handoff/SOURCE_ACCESS.md`, `handoff/API_BLOCKERS.md`, `handoff/MANUAL_NEXT_STEPS.md`
- **Verified:** docs written; every command path exists in repo
- **Next:** PE ingest when crawl completes

### S024 · 2026-10-18 12:04 IST · DEL-4/DEL-5/B17 · Benchmark task-type proposal (D-008) + registry template
- **Who:** Kush+Claude
- **Did:** Proposal promises ~80 questions × 8 task types but never names them → proposed T1 CURRENT_STATE, T2 NEXT_ACTION, T3 PROCESS_EFFECT_DIRECT, T4 COMPARE_PROCESSES, T5 UNSUPPORTED_MUST_ABSTAIN, T6 FEASIBILITY_CONSTRAINTS, T7 DIAGNOSE_RECOVER, T8 ASK_CLARIFY (maps H1–H4 + decision modes). benchmark/benchmark_registry_template.csv with plan AI6 registry fields (task type, difficulty, source family, ingredient/process family, evidence regime, answer kind, must-abstain, gold decision mode/evidence/constraints) + 2 example rows. Tiers: min 104 / target 320 / stretch 440 (AH5).
- **Files:** `DECISIONS.md`, `benchmark/benchmark_registry_template.csv`
- **Verified:** template columns match plan AI6
- **Next:** HUMAN: confirm D-008, then author DEV items

### S025 · 2026-10-18 12:06 IST · DEL-1/B06 · Phenol-Explorer 3.6 ingested: 3,870 primary-study EVD rows, 125 publications
- **Who:** Kush+Claude
- **Did:** Crawl completed (1,130 detail pages, 0 failures, survived one network drop via backoff). tools/ingest_phenol_explorer.py: 3,870 EVD (origin PRIMARY_STUDY, tier E3 curated, study lineage PRESENT), 125 STUDY + 126 SRC (1 database + 125 papers), 161 SVAR compounds, 3,870 COND (durations/temperatures/power/pressure from 'food after processing' text; PER_VOLUME basis for liquids). Before/after content, PE RF (incl. yield) and yield factor stored separately. Open discrepancy: list pages advertise 4,407 data points vs 3,870 per-publication values parsed (detail paths deduplicated) — to investigate, not assumed.
- **Files:** `tools/ingest_phenol_explorer.py`, `ledgers/data/EVD.jsonl`, `ledgers/data/COND.jsonl`, `ledgers/data/STUDY.jsonl`, `ledgers/data/SRC.jsonl`, `ledgers/data/SVAR.jsonl`
- **Verified:** all rows schema+law validated on write; rerun all unchanged
- **Next:** link EVD→ING/PROC; MOL/IMAP; queue refresh; EDA; DEL-2 on PE (study-disjoint possible)

### S026 · 2026-10-18 12:12 IST · DEL-1/AH2/ledger-queue#5 · EVD → ING / PROC linking (strict) + registry adjective cleanup
- **Who:** Kush+Claude
- **Did:** evidence/linker.py + tools/link_evidence.py: every EVD step → PROC (primary = first heat step); ING link only if concept head is the food (first segment, brackets removed), no identity-changing extra tokens/forms (juice, jam, oil, grits…), not polysemous (pepper, squash) — else MEDIUM → review table. Spot-check caught FINFISH→'fat', Maize→'grain'/'white', Chinese bayberry→'chinese', Chilli pepper [Yellow]→'yellow pepper', Blackcurrant juice→blackcurrant, grits plural; all fixed with regression tests. Registry: colour/nationality words now adjective-only rejects (12 ING deprecated by new version).
- **Files:** `src/culinarystate/evidence/linker.py`, `tools/link_evidence.py`, `src/culinarystate/vocab/registry_build.py`, `tests/unit/test_linker.py`, `registry/evidence/evd_ingredient_link_review.csv`, `registry/ingredients/`, `ledgers/data/`
- **Verified:** EXACT+HIGH: USDA 3,978/7,018 (57%), PE 1,817/3,870 (47%); 94 matrices for human review; process linked 100% of mapped steps; rerun unchanged; pytest passes
- **Next:** MOL/IMAP; refresh queue + data card + EDA

### S027 · 2026-10-18 12:17 IST · B04/AH9/ledger-queue#9 · MOL (PubChem) + typed IMAP
- **Who:** Kush+Claude
- **Did:** molecules/pubchem.py (cached PUG-REST, handles 2025 field rename ConnectivitySMILES/SMILES, refuses aggregates). tools/build_molecule_registry.py: 131 MOL (InChIKey, CID, SMILES, formula, MW, stereo status, XLogP/TPSA/HBD/HBA/rot/heavy atoms, CACTVS-881 fingerprint; ECFP pending rdkit), SVAR→MOL links, 592 IMAP (MEASURED_CONCENTRATION from before-processing contents with basis; PROCESS_CHANGE → EVD ids). 34 aggregate targets SVAR-only; 22 unresolved (proanthocyanidin n-mers, rare glycosides) listed.
- **Files:** `src/culinarystate/molecules/pubchem.py`, `tools/build_molecule_registry.py`, `tests/unit/test_pubchem.py`, `registry/molecules/`, `ledgers/data/MOL.jsonl`, `ledgers/data/IMAP.jsonl`
- **Verified:** quercetin–kaempferol Tanimoto 0.935 vs quercetin–ascorbic 0.297 (sanity)
- **Next:** retriever; queue refresh

### S028 · 2026-10-18 12:17 IST · DEL-4/P10 · Retrieval core: BM25 + inspectable compatibility vector + Evidence Packet
- **Who:** Kush+Claude
- **Did:** retrieval/bm25.py (dependency-free), compatibility.py (9 axes MATCH/NEAR/MISMATCH/UNKNOWN; unknown never mismatch; parent concepts NEAR; process family NEAR), retriever.py (BM25 ∪ structured candidates, rank 0.35 bm25 + 0.65 compat, hard-mismatch demotion, lineage dedup, evidence class DIRECT/INTERPOLATED/QUALITATIVE/CONFLICT/UNSUPPORTED, packet with known unknowns, condition differences, disallowed claims, citation map); dense slot for A100 embeddings later.
- **Files:** `src/culinarystate/retrieval/`, `tests/unit/test_retrieval.py`
- **Verified:** pytest 265 passed
- **Next:** dense embeddings (A100), calibration/abstention eval, benchmark

### S029 · 2026-10-18 12:18 IST · DEL-1/DEL-2 · Refresh: verification queue (Route A+B), DEL-1 card, EDA, DEL-2 on Phenol-Explorer
- **Who:** Kush+Claude
- **Did:** Queue now 634 rows (Route A PE publications + Route B OpenAlex), 17 conflict cells, 73 rejected. DEL-1 card: 10,888 DB rows; ING normalised 53.2%; human-verified 0/40. DEL-2 PE run incl. study_disjoint (125 publications): MAE ~0.4–0.9 dominated by formation outliers (RF up to 102); persistence often best → metric/target must change (log-RF, median AE) before any claim. STATUS updated with done list + next 5.
- **Files:** `registry/evidence/`, `reports/`, `STATUS.md`
- **Verified:** pytest 265 passed
- **Next:** AI pre-check pass of queue; DEL-2 log-RF; A100 for dense/NER (VPN)

### S030 · 2026-10-18 12:42 IST · P1/DEL-1 · AI pre-check Route A + human review pack + temperature sign fix
- **Who:** Kush+Claude
- **Did:** Crossref/OpenAlex DOI resolver (strict title+year); 121/125 PE papers resolved, 15 OA. Rule pre-check of 3,870 PE rows -> AI_PRECHECKED (3,791 LIKELY_CONFIRM, 79 CHECK_VALUES). Found+fixed bug: '-20°C' parsed as +20 -> 266 COND revised. Human review pack 55 rows (40 MAIN) from 15 OA papers. apply_human_review.py (CONFIRM -> new E1/E2 HUMAN_VERIFIED mirror row; REJECT/CORRECT). EVIDENCE_REVIEW_GUIDE.md.
- **Files:** `src/culinarystate/evidence/{doi_resolve`, `precheck`, `conditions}.py tools/{precheck_route_a`, `reextract_conditions`, `apply_human_review}.py registry/evidence/{human_review_pack_v1`, `route_a_paper_precheck`, `verification_queue_ranked_v1}.csv handoff/EVIDENCE_REVIEW_GUIDE.md`
- **Verified:** 271 tests pass; 0 invalid EVD/COND/SRC; reextract idempotent (2nd run 0 writes); apply dry-run rejects verifier=Claude and CONFIRM w/o locator
- **Next:** Humans: 40 rows in human_review_pack_v1.csv. AI: data expansion (OFF ingredient taxonomy, open recipes, public-domain books, Bognar retention table)

### S031 · 2026-10-18 12:50 IST · X1/P3 · FoodOn crosswalk + ING categories
- **Who:** Kush+Claude
- **Did:** Parsed FoodOn (28,684 live FOODON terms, 42,658 names). ING->FoodOn: 534 LINKED (unique exact label, non-polysemous), 287 CANDIDATE, 1,176 NO_MATCH; linked+candidate = 75.4% of corpus mentions. ING.category filled for 572 concepts from nearest FoodOn ancestor (14 coarse classes). D-009 recorded (open-resource expansion, sequential X1-X8).
- **Files:** `src/culinarystate/vocab/foodon.py tools/build_foodon_crosswalk.py registry/ingredients/foodon_crosswalk_v1.csv reports/foodon_crosswalk_v1.md tests/unit/test_foodon.py DECISIONS.md STATUS.md`
- **Verified:** tests pass; 0 invalid ING; categories spot-checked (lemon FRUIT, sugar SWEETENER, tomato VEGETABLE, wine vinegar CONDIMENT)
- **Next:** X2 Open Food Facts taxonomy -> aliases (UK/US, Hindi) to reduce NO_MATCH

### S032 · 2026-10-18 12:56 IST · X2/P3 · Open Food Facts taxonomy -> aliases + external refs
- **Who:** Kush+Claude
- **Did:** Pinned OFF ingredients.txt (git a1ce1d36, ODbL) with SRC+SNAP. 835 ING linked to unique OFF entry (81.1% corpus mentions); +1,770 ALIAS (en 384 + 13 Indian languages: hi 164, ta 146, bn 137 ...); 560 Wikidata QIDs, 215 OFF->FDC codes + Ecobalyse densities listed (candidates). 475 alias collisions skipped, 135 flagged SAME_CONCEPT_MERGE -> reveals ~30 duplicate ING pairs (pea/peas, feta/feta cheese). Fixed ING builder so rebuilds only deprecate A1-owned aliases.
- **Files:** `src/culinarystate/vocab/off.py tools/build_off_aliases.py tools/build_ingredient_registry.py registry/ingredients/off_crosswalk_v1.csv registry/ingredients/off_alias_collisions.csv reports/off_taxonomy_v1.md tests/unit/test_off.py`
- **Verified:** tests pass; 0 invalid; 2nd run 0 writes
- **Next:** X2b merge duplicate ING concepts at builder level

### S033 · 2026-10-18 13:03 IST · X2b/P3 · Merge duplicate ingredient concepts at builder level
- **Who:** Kush+Claude
- **Did:** merge_map in registry_build (plural-only, named-cheese 'X cheese', explicit bay->bay leaf); builder folds mention table before counting, marks losers SUPERSEDED with superseded_by keeper, repoints aliases from any source, preserves X1/X2 enrichment fields. Fixed two version-churn bugs found on the way (null-vs-missing category copy; external_refs order ping-pong between FoodOn/OFF tools -> sorted). Reran FoodOn, OFF, link_evidence (183 EVD relinked), recipe, molecule (+46 IMAP), allergen, FDC CSV.
- **Files:** `src/culinarystate/vocab/registry_build.py tools/build_ingredient_registry.py tools/build_foodon_crosswalk.py tools/build_off_aliases.py ledgers/data/*.jsonl registry/*`
- **Verified:** 276 tests; 0 invalid; 0 dangling ING refs across all ledgers; every builder 2nd run = 0 writes
- **Next:** X3 Wikibooks Cookbook recipes (MediaWiki API, CC BY-SA)

### S034 · 2026-10-18 13:18 IST · X3/DEL-3 · Wikibooks Cookbook recipes ingested (source family 2)
- **Who:** Kush+Claude
- **Did:** MediaWiki API crawl (cached, 1 req/s): 3,797 recipe + 130 equipment + 749 ingredient + 81 technique pages; cuisine tree (155) + technique tree (26). Parser keeps [[Cookbook:X]] links as spans and sub-section groups (dough/filling = intermediate components). REC +3,676 (family WIKIBOOKS-COOKBOOK; cuisines incl. Indian 143; technique refs). REC<->ING 97.7% of 32,036 lines (wiki link 28k, ngram 3k). +97 ING from editor-linked ingredient pages (>=3 recipes, category pages filtered), +155 aliases. Silver NER export (local) ~49k spans INGREDIENT/TOOL/UNIT/PROCESS. Cross-source near-dups with BBC: 1. Fixes: norm() folds accents (crème fraîche), shown text before link target (lumped pages).
- **Files:** `src/culinarystate/ingest/wikibooks.py src/culinarystate/vocab/{line_link`, `foodon}.py tools/{crawl_wikibooks`, `ingest_wikibooks}.py tools/build_off_aliases.py tools/build_ingredient_registry.py registry/recipes/wikibooks_ingredient_links_v1.csv reports/wikibooks_v1.md`
- **Verified:** 282 tests; 0 invalid; ingest 2nd run 0 writes; 40-line spot check ~90% correct before shown-text fix
- **Next:** X3b equipment/technique pages -> TOOL/PROC; then X4 Gutenberg cookbooks

### S035 · 2026-10-18 13:47 IST · X3b/P3 · Wikibooks equipment + techniques -> TOOL/PROC; polysemy splits; timestamp fix
- **Who:** Kush+Claude
- **Did:** TOOL vocab +40 tools (double boiler, idli steamer, tandoor, rice cooker, garlic press, food mill, ...) and US aliases (cutting board, plastic wrap, loaf pan ...); 97 tools carry WIKIBOOKS refs; tool co-occurrence corpus = BBC 39.5k + Wikibooks 26.2k steps -> 605 proc<->tool links. PROC +8 (sous-vide, scald, render, baste, blind-bake, temper, brine, degorge); split polysemy: 'temper' no longer = tadka, 'brine' no longer = pickle; curated 63-page technique map -> PROC external_refs; 487 EVD relinked. Builders now preserve fields owned by other builders (tool_ids, evidence_coverage). Fixed store bug: upsert revisions kept v1 created_at (D-010).
- **Files:** `src/culinarystate/process/{tools`, `vocab}.py src/culinarystate/ledgers/store.py tools/build_{tool`, `process}_registry.py tests/unit/test_ledgers.py DECISIONS.md`
- **Verified:** 283 tests; 0 invalid TOOL/PROC/EVD; full builder cycle 2nd pass 0 writes
- **Next:** X3c typed link sub-ledgers with support/confidence

### S036 · 2026-10-18 13:50 IST · X3c/P3 · KGE edge ledger foundation (schema, rules, stats, corpus adapter)
- **Who:** Kush+Claude
- **Did:** Added KGE record type (13 predicates) + rule_kge + example + tests; kg/edges.py (PairCounter with lift/PMI/Wilson confidence/bands/per-source support, quantiles for timer/temperature profiles); kg/corpus.py (BBC + Wikibooks unified RecipeView incl. components from sub-section groups). D-011.
- **Files:** `src/culinarystate/ledgers/{registry`, `rules}.py src/culinarystate/kg/{__init__`, `corpus`, `edges}.py ledgers/schemas/KGE.schema.json tests/unit/test_kg_edges.py tests/unit/test_ledgers.py tests/fixtures/ledger_examples.py DECISIONS.md`
- **Verified:** all tests pass
- **Next:** tools/build_kg_edges.py: compute 13 predicates over BBC+Wikibooks, write KGE records (top-k per subject, min support), report reports/kg_edges_v1.md; then X4 Gutenberg

### S037 · 2026-10-18 15:34 IST · X3c/P3 · KGE edges built over BBC + Wikibooks
- **Who:** Kush+Claude
- **Did:** tools/build_kg_edges.py: 8,824 typed edges with support, lift/PMI, Wilson confidence, band, per-source support: ING_CO_OCCURS 3,683, ING_USED_IN_CUISINE 1,564, ING_MEASURED_IN_UNIT 1,137, ING_PROCESSED_BY 776, ING_HAS_CATEGORY 631, PROC_USES_TOOL 334, ING_PARENT 315, PROC_IN_FAMILY 156, TOOL_HAS_CATEGORY 116, COMPONENT_CONTAINS_ING 49, PROC_FOLLOWED_BY 30, PROC_TYPICAL_DURATION 28 (bake p50 25 min n=847; simmer 15; chill 60), PROC_TYPICAL_TEMPERATURE 5. Stale edges auto-deprecated.
- **Files:** `tools/build_kg_edges.py ledgers/data/KGE.jsonl registry/kg/kg_edges_v1.csv reports/kg_edges_v1.md`
- **Verified:** 289 tests; 0 invalid KGE; 2nd run 0 writes
- **Next:** review PROC_FOLLOWED_BY (few edges, some odd pairs e.g. insert->rinse); X4 Gutenberg cookbooks

### S038 · 2026-10-18 15:55 IST · X5/DEL-1 · Bognár (2002) retention factors -> EVD (third source family)
- **Who:** Kush+Claude
- **Did:** Downloaded BFE-R-02-03 PDF (KIT repository, sha pinned in SNAP); pdftotext -layout; parser recovers method columns from the A/B basis row (new method at each A or B-after-B, must equal header method count) and skips 11 tables with column-specific sub-variants (logged). 6,594 EVD rows (tier E3, DATABASE_AGGREGATE, TRUE_RETENTION, portion A/B modifier, estimated flag from preface list, 1.00 stored CENSORED GT_CAP 0.995), 36 SVAR, 123 COND (core temperature from table titles as CORE). Linker: 2,251 HIGH. DEL-2 on BOGNAR runs (D5 matrix-disjoint MAE 0.046 vs D0 0.062; process_disjoint degenerate). Gutenberg crawl (X4) running in background with zip downloads.
- **Files:** `src/culinarystate/ingest/{bognar`, `bognar_build`, `gutenberg`, `old_recipes}.py src/culinarystate/vocab/line_link.py tools/{ingest_bognar`, `crawl_gutenberg`, `ingest_gutenberg}.py reports/bognar_v1.md reports/del2/BOGNAR-2002_results.* tests/unit/test_{bognar`, `gutenberg`, `old_recipes`, `line_link}.py`
- **Verified:** 298 tests; 0 invalid; 8/8 random cells match raw PDF text columns
- **Next:** finish X4 ingest when crawl completes; cross-source DEL-2 (train USDA/PE, test Bognár); Bognár Part-1 yield tables

### S039 · 2026-10-18 15:57 IST · DEL-2 · Cross-source agreement USDA vs Bognár (source-disjoint)
- **Who:** Kush+Claude
- **Did:** transition/cross_source.py: explicit harmonisation (nutrient keys, Bognár portion A, no breaded). L1 ingredient-level overlap 67 cells (roast poultry only): MAE 0.075, 69% within 0.10, Spearman 0.61. L2 food-group x step-family: 249 cells, MAE 0.083, median 0.056, 70% within 0.10, Spearman 0.69; USDA step-nutrient means predict Bognár (0.097) better than Bognár's global mean (0.116). Systematic conflict: minerals in boiled vegetables/poultry (USDA ~0.9 vs Bognár ~0.5).
- **Files:** `src/culinarystate/transition/cross_source.py tools/run_cross_source.py reports/del2/cross_source_v1.* tests/unit/test_cross_source.py`
- **Verified:** 300 tests pass
- **Next:** X4 Gutenberg ingest after crawl; Bognár Part-1 yields; DEL-2 log-RF for PE

### S040 · 2026-10-18 16:10 IST · DEL-2 · Log-RF target, median/log errors, experiment cards
- **Who:** Kush+Claude
- **Did:** LogTarget wrapper (fit on log RF, predict exp) + median AE + MAE-log metrics; runner --log-target; D7 divergence guard (raw PE NaN fixed). Reran USDA, PE raw, PE log, Bognár. Experiment cards experiments/EXP-000001..4 + EXP ledger: USDA supported on random only; PE (raw+log) not supported (study_disjoint best = global mean, median AE 0.21; D5 worse than persistence); Bognár supported but caveated (templated factors; process split degenerate -> n/a).
- **Files:** `src/culinarystate/transition/{baselines`, `evaluate}.py tools/{run_del2`, `register_experiments}.py experiments/ reports/del2/ tests/unit/test_del2.py`
- **Verified:** 301 tests; cards regenerate deterministically
- **Next:** X4 Gutenberg ingest when crawl finishes

### S041 · 2026-10-18 16:14 IST · X6/P3 · TOOL -> Wikidata QIDs
- **Who:** Kush+Claude
- **Did:** Exact label/alias SPARQL lookup restricted to kitchen roots (kitchenware, cookware, kitchen utensil, appliance, container). 73 LINKED (unique + label equals canonical/alias), 31 CANDIDATE (several items, e.g. grill vs automobile grille; tea towel->wrapper downgraded), 12 NO_MATCH (handi, tadka pan, idli steamer ...). Tool builder now preserves non-Wikibooks refs.
- **Files:** `tools/build_tool_wikidata.py tools/build_tool_registry.py registry/tools/tool_wikidata_v1.csv reports/tool_wikidata_v1.md`
- **Verified:** 301 tests; both builders 2nd run 0 writes
- **Next:** X4 ingest after crawl; handoff docs RUNBOOK/DATASETS

### S042 · 2026-10-18 16:16 IST · P15 · Handoff RUNBOOK + DATASETS; SRC for FoodOn/Wikidata
- **Who:** Kush+Claude
- **Did:** handoff/RUNBOOK.md (acquisition, dependency-ordered ledger build, review/report commands, field ownership, logging). handoff/DATASETS.md (13 source families with licence, storage rule, local path, feeds; unused sources and why). Added SRC records for FoodOn (CC BY 4.0) and Wikidata (CC0).
- **Files:** `handoff/RUNBOOK.md handoff/DATASETS.md tools/build_foodon_crosswalk.py tools/build_tool_wikidata.py`
- **Verified:** tests pass; builders unchanged on rerun
- **Next:** X4 Gutenberg ingest when crawl finishes

### S043 · 2026-10-18 16:39 IST · X4/DEL-3 · Gutenberg public-domain cookbooks ingested (partial, silver)
- **Who:** Kush+Claude
- **Did:** PGLAF mirror crawl (zip, 2 s/req) of 347 catalog-selected cookbooks (205 done so far). Heuristic segmenter (headings + Beeton fields) + evidence filter (>=2 ING mentions, >=1 process) + index/menu/date/non-food filters: 49,520 REC (family GUTENBERG-PD), 484k REC<->ING mention links, 1,147 with Beeton ingredient field; precision ~80-85% on 30-sample (D-012 silver). Tool matcher hyphen-insensitive (stew-pan, sauce-pan); +3 historic tools (chafing dish, fish kettle, preserving pan) and aliases (stewpan, dripping pan, farina kettle).
- **Files:** `src/culinarystate/ingest/{gutenberg`, `old_recipes}.py src/culinarystate/process/tools.py tools/{crawl_gutenberg`, `ingest_gutenberg}.py registry/recipes/gutenberg_ingredient_links_v1.csv registry/tools/historic_tool_candidates.csv reports/gutenberg_v1.md DECISIONS.md`
- **Verified:** 301 tests; 0 invalid REC/SRC/SNAP; 3 samples of 25-30 reviewed
- **Next:** SSOT deep-dive for more resources + graph edge types; re-run ingest after crawl; add Gutenberg to tool/KG corpora

### S044 · 2026-10-18 16:42 IST · X/SSOT · SSOT deep-dive: resource + relation gap map
- **Who:** Kush+Claude
- **Did:** Read SSOT data-inventory/licence/KG/relation sections; docs/RESOURCE_GAP_MAP.md lists 18 named resources with role, licence, status, and maps the 15 SSOT core relations to KGE predicates (6 present, 6 planned: ALTERNATIVE_TO, OFTEN_OPTIONAL, PREP_FORM, USES_MEDIUM, ENDPOINT_STATE, CONTAINS_COMPOUND). Checked availability: FlavorGraph Apache-2.0, FoodAtlas Apache-2.0, TASTEset MIT, OpenPI MIT, ChemTastesDB CC BY 4.0; FooDB 403 (manual); r-FG repo not found. Queue X14, X9-X13, X15 added to STATUS.
- **Files:** `docs/RESOURCE_GAP_MAP.md STATUS.md`
- **Verified:** licences checked via GitHub/Zenodo APIs
- **Next:** X14 corpus-mined predicates

### S045 · 2026-10-18 18:14 IST · X4/X14 · Gutenberg complete; SSOT relations mined into KGE
- **Who:** Kush+Claude
- **Did:** Crawl finished (346/347 books); re-ingest: 71k silver REC from 306+ books, 675k REC<->ING links, 1,065 near-dup families. X14: ING_ALTERNATIVE_TO, ING_OFTEN_OPTIONAL, ING_PREP_FORM, PROC_USES_MEDIUM, PROC_ENDPOINT_STATE mined with closed vocabularies over BBC+Wikibooks+Gutenberg. Fix: 'chicken or vegetable stock' shares the head noun only when the pair names a more specific concept (now chicken stock<->vegetable stock n=106, lift 11.3). Historic-tool review list drops units and modifier+known-tool phrases.
- **Files:** `src/culinarystate/kg/{mine`, `edges`, `corpus}.py tools/{build_kg_edges`, `ingest_gutenberg}.py src/culinarystate/vocab/line_link.py registry/kg/kg_edges_v1.csv reports/{kg_edges`, `gutenberg}_v1.md`
- **Verified:** tests pass; KGE 0 invalid; Gutenberg 2nd run created only books missed by the earlier partial run
- **Next:** X9 FlavorGraph

### S046 · 2026-10-18 18:14 IST · X9 · FlavorGraph compounds and co-occurrence
- **Who:** Kush+Claude
- **Did:** Pinned 8d3472d; counts match release (8,298 nodes, 147,179 edges). +1,595 MOL by InChIKey (PubChem), 29,656 IMAP PRESENCE (qualitative), 27,530 ING_CO_OCCURS|FLAVORGRAPH (NPMI). Fix: several FlavorGraph nodes map to one ING, so edges are aggregated per ledger key before writing (was flip-flopping 5.4k KGE / 354 IMAP per run). NC upstream (FlavorDB): no redistribution.
- **Files:** `tools/ingest_flavorgraph.py src/culinarystate/molecules/pubchem.py src/culinarystate/ledgers/{registry`, `rules}.py reports/flavorgraph_v1.md`
- **Verified:** second run: 27,530 KGE + 29,656 IMAP unchanged
- **Next:** X10 TASTEset

### S047 · 2026-10-18 18:14 IST · X10/P5 · TASTEset rule NER floor
- **Who:** Kush+Claude
- **Did:** Rule tagger in TASTEset labels (quantity grammar, closed lists, prep forms, ING lexicon for FOOD). TASTEset @80bb783: micro F1 0.791 exact / 0.898 relaxed; FOOD 0.753/0.952; PHYSICAL_QUALITY 0.554 weakest. NER_RUNBOOK for A100 encoder runs (VPN first).
- **Files:** `src/culinarystate/ner/rule_ner.py tools/eval_tasteset.py reports/ner/ handoff/NER_RUNBOOK.md`
- **Verified:** unit tests; scorer = common span metrics
- **Next:** X11

### S048 · 2026-10-18 18:14 IST · X11 · ChemTastesDB taste classes
- **Who:** Kush+Claude
- **Did:** Zenodo 15051366 (CC BY 4.0): 204 MOL_HAS_TASTE for MOL matched by PubChem CID; object = curated 'Class taste' (Bitterness 138 ...), free-text label in notes; v0 free-text edges deprecated.
- **Files:** `tools/ingest_chemtastesdb.py reports/chemtastesdb_v1.md`
- **Verified:** second run 204 unchanged
- **Next:** X12

### S049 · 2026-10-18 18:14 IST · X12/DEL-3 · OpenPI food subset
- **Who:** Kush+Claude
- **Did:** OpenPI 2.0 (MIT) Food and Entertaining: 174/15/8 procedures, 7,629 entity-attribute before->after changes, 46% entities linked to ING. External check for DEL-3, not Gold.
- **Files:** `tools/build_openpi_food.py reports/openpi_food_v1.md`
- **Verified:** counts per split
- **Next:** X15

### S050 · 2026-10-18 18:14 IST · X15/DEL-2 · FDC SR Legacy raw/cooked pairs vs R6
- **Who:** Kush+Claude
- **Did:** 867 description pairs (state tokens stripped, unsalted twin preferred), 16,365 dry-basis ratios (= true retention iff solids conserved), 4,984 analytical-only (source codes 1/6/13; imputed values circular vs R6). Group level vs R6: within 0.10 for 46% (analytical), Spearman 0.31. Candidates, not EVD.
- **Files:** `src/culinarystate/evidence/fdc_pairs.py tools/build_fdc_pairs.py registry/evidence/fdc_raw_cooked_pairs_v1.csv reports/del2/fdc_pairs_v1.md`
- **Verified:** unit tests; analytical/all tiers reported separately
- **Next:** X13

### S051 · 2026-10-18 18:14 IST · X13 · FoodAtlas access check: manual
- **Who:** Kush+Claude
- **Did:** Data relicensed CC BY-NC 4.0 on 2026-10-09 (repo LICENSE-DATA.md); bundles are private S3 objects pre-signed for key holders; site behind bot checkpoint -> not scripted. MANUAL_NEXT_STEPS #11 FooDB, #12 FoodAtlas.
- **Files:** `docs/RESOURCE_GAP_MAP.md handoff/MANUAL_NEXT_STEPS.md`
- **Verified:** GitHub API reads only
- **Next:** Bognar yields

### S052 · 2026-10-18 18:14 IST · X5b/D-013 · Bognar Part-1 yields; stated temperature bounds
- **Who:** Kush+Claude
- **Did:** Parser for weight-yield tables: 444 rows / 30 tables (~94%), core temperature kept as printed; 496 EVD derived.yield_factor (edible + with-waste), key includes core temperature (same roast at 80-90 vs >90 C). D-013: '> 75 C' was MEASURED 75 -> CENSORED GT_STATED/LT_STATED, qualifier in raw; KG quantiles skip bounds. Found + fixed: ingest_bognar rerun cleared 6,594 process / 2,251 ingredient links -> keep_linker_fields; link_evidence restored them.
- **Files:** `src/culinarystate/ingest/{bognar_yield`, `bognar_build`, `phenol_explorer_build}.py tools/{ingest_bognar_yields`, `reextract_conditions`, `build_kg_edges}.py src/culinarystate/evidence/{conditions`, `linker}.py src/culinarystate/ledgers/common.py ledgers/schemas DECISIONS.md`
- **Verified:** second pass of every touched builder writes nothing; 10 ledgers 0 invalid; Bognar links 6,594/2,251 restored
- **Next:** DEL-4/5 layer

### S053 · 2026-10-18 18:14 IST · DEL-4 · Calibration metrics and confidence vector
- **Who:** Kush+Claude
- **Did:** scoring/calibration.py: Brier, ECE (+reliability bins), risk-coverage, AURC, error-detection AUROC, UCR. decision/confidence.py: SSOT 242.1 vector (unknown stays None), 242.6 sufficiency modes, 242.7 output precision <= evidence precision. Retrieval: ingredient named inside a group row ('vegetables, such as broccoli') = matrix NEAR.
- **Files:** `src/culinarystate/scoring/calibration.py src/culinarystate/decision/confidence.py src/culinarystate/retrieval/compatibility.py`
- **Verified:** unit tests
- **Next:** DEL-5 decision layer

### S054 · 2026-10-18 18:14 IST · DEL-5 · Relevance gate, feasibility filter, decision policy, ask tool
- **Who:** Kush+Claude
- **Did:** decision/relevance.py (SSOT 7 rule gate + intent), feasibility.py (C11: malformed->REJECT, OOD->UNKNOWN, tools from HIGH PROC_USES_TOOL, time from duration quantiles, FSSAI allergens; unstated constraint = NOT_APPLICABLE), policy.py (243: ASK on missing slot, feasibility before utility, alternatives without hidden weights, diagnosis QUALIFIED, RECOVER = cause evidence + recoverability UNKNOWN), pipeline.py + tools/ask.py --demo. Demo exposed + fixed: question homographs (keep/split/can).
- **Files:** `src/culinarystate/decision/ tools/ask.py`
- **Verified:** unit tests; 8 demo questions give expected modes on real ledgers
- **Next:** DEL-3 sessions

### S055 · 2026-10-18 18:14 IST · DEL-3 · 30 scripted sessions (AI-drafted)
- **Who:** Kush+Claude
- **Did:** annotation/sessions.py: session schema (gold event vocabulary, expected alive/dead/fields/edges/issue count), replay check; gold.compile_event shared. 30 sessions over 10 scenario types; all pass (237 checks, deterministic replay). Contract counts HUMAN_REVIEWED only: 0/30.
- **Files:** `src/culinarystate/annotation/{sessions`, `gold}.py annotation/sessions/ tools/run_sessions.py reports/del3/`
- **Verified:** tests 355 passed
- **Next:** humans review sessions (#10b); D-012 storage decision

### S056 · 2026-10-18 18:15 IST · DEL-5/D-008 · Doubts resolved from SSOT first (D-008, D-012)
- **Who:** Kush+Claude
- **Did:** Kush: resolve doubts from SSOT + md first, ask only if unresolved. D-008: SSOT §12 names 9 benchmark tasks; draft list replaced by SSOT-aligned 8 (one merge) with evidence regimes as slices. D-012: SSOT §226.3/§226.10 (versioned schema, DVC/versioned snapshots) + plan law 15 (append-only) settle the method; remote/account choice left to humans.
- **Files:** `DECISIONS.md`
- **Verified:** SSOT lines 1258-1288, 24515-24530, 24590-24602; plan H2, AI9
- **Next:** Kush: confirm D-008 merge; pick snapshot remote for D-012

### S057 · 2026-10-18 21:23 IST · DEL-4/RQ16-02 · Silver retrieval comparison; dense + hybrid rungs
- **Who:** Kush+Claude
- **Did:** 600 templated cell-level questions over 17,978 EVD texts (silver, dev only). Embeddings on M2 MPS (bge-small/base/large, e5-small/large, gte-large). MRR@10: BM25 0.597, dense bge-small 0.668, RRF hybrid 0.704 (CI separated from BM25), structured with oracle slots 0.856; adding dense to structured not separated. R5 cross-encoder tool ready. Finding: common vegetables (potato/carrot/spinach x boil) have no ingredient-linked rows until the 198 AI-ACCEPT link rows are human-signed.
- **Files:** `tools/{export_retrieval_set`, `embed_texts`, `eval_retrieval_silver`, `rerank_silver}.py reports/del4/`
- **Verified:** bootstrap CIs over queries
- **Next:** R5 rerank results; human sign-off of link review

### S058 · 2026-10-18 21:23 IST · 257I/C14 · SSOT 257I test layers + OOD gate; adversarial testing
- **Who:** Kush+Claude
- **Did:** C14 OOD gate (support per axis, cap at QUALITATIVE when pair unsupported + cold axis). Tests added per SSOT 257I: property-based quantity (kg/g, L/mL, lb/oz, fractions, ranges, cup stays ambiguous, C/F), 1.7k seeded fuzz cases over every text entry point, 257B 12-case module contracts (C1/C3/C7/C11/C13/C14/policy), replay prefix-consistency + correction propagation over 30 sessions, release audit (provenance, checksums, dangling refs, DEL-1 clause, no BBC text, unique ids), retrieval regression with hard negatives, e2e incl. hostile inputs. Bugs found and fixed: '1/0 cup' crash; double-space bypassed gate; LineLinker silently mis-linked raw keys; regex word boundary failed on names ending in punctuation; process-effect answer with no target mixed all nutrients (now ASK); 'boiled and not boiled' ignored (now ASK).
- **Files:** `src/culinarystate/decision/{ood`, `policy`, `pipeline`, `relevance}.py src/culinarystate/quantity/grammar.py src/culinarystate/vocab/line_link.py src/culinarystate/retrieval/compatibility.py tests/{property`, `contract`, `integration}/ pyproject.toml`
- **Verified:** 2,338 fast + 35 ledger integration tests pass
- **Next:** NER sweep summary; Part K layers

### S059 · 2026-10-18 21:29 IST · C5/C11 · Goal/constraint parser; unavailable tools in feasibility
- **Who:** Kush+Claude
- **Did:** decision/constraints.py: 'only have X' = closed-world tools, 'no oven' = unavailable (rejects even open-world), time budget (word forms, ranges -> lower end, cue-gated), 8 FSSAI allergen categories via cue patterns; diets (vegan/jain/keto/lactose...) returned UNRESOLVED. ask.py --constraints. NER layers: CRF (verified vs brute force) and kNN-NER (train-only datastore, dev-tuned) added; DeBERTa-large queued.
- **Files:** `src/culinarystate/decision/{constraints`, `feasibility}.py tools/ask.py gpu/ner_tasteset/{crf`, `train_ner}.py tests/unit/test_constraints.py`
- **Verified:** 2,767 fast tests pass; real-registry spot checks
- **Next:** NER layer results; ingredient exclusions; C12 comparator

### S060 · 2026-10-18 21:34 IST · C12 · Outcome comparator; compare intent for 'X or Y ... more'
- **Who:** Kush+Claude
- **Did:** decision/comparator.py: per option, retention medians per independence group, range of group medians, censored share; verdict SEPARATED only when ranges are disjoint, OVERLAPPING otherwise, INSUFFICIENT under 2 independent sources. Real data: spinach folate steam 0.70 [0.65-0.75] vs boil 0.65 [0.60-0.70] -> OVERLAPPING; beef thiamin roast vs braise -> INSUFFICIENT (USDA only). Intent fix: 'does roasting or braising keep more' is COMPARE. Retrieval large embeddings + rerankers moved to A100 (Mac swap 8.5/9.2 GB).
- **Files:** `src/culinarystate/decision/{comparator`, `policy`, `relevance}.py tests/unit/{test_comparator`, `test_policy`, `test_relevance}.py`
- **Verified:** 2,777 tests pass
- **Next:** A100 retrieval + NER results

### S061 · 2026-10-18 21:36 IST · RQ16-17 · VOI-aware target clarification
- **Who:** Kush+Claude
- **Did:** SSOT 243.8: ask only with decision value. Missing target on a process-effect question: candidate targets = targets with retention evidence for the (ingredient, process) pair (SupportIndex.targets_for). None -> ABSTAIN (asking cannot help), one -> answer with it, several -> ASK listing up to 5 evidenced options (broccoli+boil -> total polyphenols, quercetin, amino acids, biotin, calcium).
- **Files:** `src/culinarystate/decision/{ood`, `policy`, `pipeline}.py tools/ask.py`
- **Verified:** 2,779 fast + 39 integration tests pass
- **Next:** diagnosis verifier + recovery KB (RQ16-18/19)

### S062 · 2026-10-18 21:40 IST · RQ16-18/19 · Troubleshooting candidates: cause / prevention / recovery mined
- **Who:** Kush+Claude
- **Did:** kg/troubleshoot.py: closed failure vocabulary (curdle, split, burn, stick, sink, lumpy, too thick/thin/salty/dry, tough, heavy, ...) and three relations kept separate (CAUSE 'will curdle if boiled', PREVENTION 'stir to prevent sticking' / ', or it will curdle', RECOVERY 'if it curdles, beat in cold milk'). Over 73,778 Gutenberg + 4,757 Wikibooks docs: ~1.7k statements, ~105 keys with >=2 independent sources. AI-judged precision on random samples: 35/40 then, after fixing 3 systematic errors (keep-it-burning, heavy adjective, non-action clause) and 'grains', 37/40 on a fresh sample. Registry CSV keeps public-domain text only.
- **Files:** `src/culinarystate/kg/troubleshoot.py tools/mine_troubleshooting.py registry/kg/troubleshooting_candidates_v1.csv reports/troubleshooting_v1.md`
- **Verified:** unit tests incl. sample regressions; precision samples local
- **Next:** proposer + verifier over candidates; failure gold (humans)

### S063 · 2026-10-18 21:43 IST · X8/E16-A · Encoder NER on A100: base, CRF, kNN, large (5 seeds each)
- **Who:** Kush+Claude
- **Did:** TASTEset, same recipe split as the rule floor, dev selection, grouped CI. Test exact F1 (mean of 5 seeds): rules 0.774; BERT 0.919; RoBERTa 0.925; DeBERTa-base 0.922; +kNN-NER 0.924; +CRF 0.929; DeBERTa-large 0.928. CRF earns its place (+0.007 dev and test); kNN marginal; large ties base+CRF on dev at 2x cost. Server: system torch env lacks protobuf for DeBERTa -> mh-copilot venv (py3.8) used read-only; metrics alias made py3.8-safe. Large+CRF running.
- **Files:** `gpu/ner_tasteset/ tools/summarise_ner_runs.py reports/ner/tasteset_encoders_v1.md`
- **Verified:** 30 runs pulled; summariser selects only complete seed sets
- **Next:** large+CRF; GLiNER layer needs package approval; EXP card

### S064 · 2026-10-18 21:46 IST · RQ16-18/19 · Diagnosis proposer + verifier; separate recovery index
- **Who:** Kush+Claude
- **Did:** decision/diagnosis.py: symptom -> failure key (statement vocabulary + symptom adjectives); proposer = cited CAUSE candidates with >=2 independent sources (single-source mined statements proved noisy on real data); verifier = named non-generic process vs session history, negated causes flip ('not stirred'); unverifiable causes -> next observations. RECOVER takes options from the RECOVERY relation only; recoverability UNKNOWN; all QUALIFIED. Real: custard curdle -> 'boiled' CONSISTENT + 'begin again with a fresh yolk'; lumpy gravy -> 'strain through a hair sieve'; burnt jam -> prevention 'stir frequently' (7 sources), no recovery claimed.
- **Files:** `src/culinarystate/decision/{diagnosis`, `policy`, `pipeline}.py tools/ask.py tests/unit/test_diagnosis.py tests/integration/test_e2e_scenarios.py`
- **Verified:** 2,797 fast + 40 integration pass
- **Next:** large+CRF results; EXP cards; GLiNER needs approval

### S065 · 2026-10-18 21:54 IST · C16/C17/DEL-5 · Grounded generator, claim checker, ladder smoke (negative result)
- **Who:** Kush+Claude
- **Did:** generation/prompts.py (B0, B2 hybrid RAG, B5 packet + mode + precision cap + disallowed claims), generation/claims.py (numeric claims must cite packet rows and match values; fabricated ids; UCR), generation/llm.py (Ollama on A100 via SSH tunnel, temperature 0, fixed seed). tools/run_ladder.py smoke on 8 demo questions with qwen2.5:7b: B0 0 numeric claims, B2 UCR 0.80 (3 fabricated ids), B5 UCR 0.71. Causes: checker missed multi-id brackets (fixed), real model overreach on NEAR rows / RECOVER, non-evidence routes given the evidence prompt. Kept as a negative result.
- **Files:** `src/culinarystate/generation/ tools/run_ladder.py reports/del5/ tests/unit/test_generation.py`
- **Verified:** unit tests; smoke outputs in reports/del5
- **Next:** per-route prompts + precision-cap enforcement + rerun; large+CRF card

### S066 · 2026-10-18 22:45 IST · DEL-5 · C16/C17 generator ablation: template promoted, LLM rephrase unpromoted
- **Who:** Kush
- **Did:** Deterministic verbaliser (verbalize@0.1), per-route fact prompt (b5f), post-hoc enforcer (enforce@0.1), claims@0.2 fixes (bare '1', 7-digit ids, citations after full stop); ladder v2 on 20 dev questions with qwen2.5 7B and 32B on private GPU Ollama (shared service was CPU-only). B5F+E and B5T both 0 unsupported/0 violations; template keeps all facts -> promoted. Fixed miner v1.1, diagnosis no-history verdict, out-of-scope gate, enforcer ASK/malformed-id gaps.
- **Files:** `src/culinarystate/generation/{verbalize`, `enforce`, `claims`, `prompts`, `llm}.py`, `src/culinarystate/decision/{diagnosis`, `policy`, `relevance}.py`, `tools/run_ladder.py`, `tests/contract/test_generation_contracts.py`, `tests/unit/test_{verbalize`, `enforce`, `generation`, `diagnosis`, `policy}.py`, `reports/del5/generator_c16_v1.md`, `ladder_v2_qwen{7b`, `32b}.*`
- **Verified:** pytest 2857 fast + 40 ledgers pass; ladder rescored with final checker
- **Next:** retrieval report v2 (6 dense + R5 base/large); wire e5-large free-text fallback decision; R4 graph expansion

### S067 · 2026-10-18 22:51 IST · DEL-5 · C5 ingredient exclusions + weak tool aliases in constraints
- **Who:** Kush
- **Did:** parse 'no onion' / 'without garlic' / 'out of coconut milk' to ING ids (longest phrase, norm plurals, lookahead so cues in a phrase are not swallowed); feasibility EXCLUDED_INGREDIENT over the ING or any ancestor (Requirements.ingredient_parents); unknown names UNRESOLVED; tools beat ingredients; 'no microwave' now resolves (weak alias accepted after constraint cue). Real run: microwave REJECT, braise kept, blorpfruit unresolved.
- **Files:** `src/culinarystate/decision/{constraints`, `feasibility}.py`, `src/culinarystate/process/tools.py`, `tools/ask.py`, `tests/unit/test_constraints.py`, `tests/property/test_fuzz_entry_points.py`
- **Verified:** pytest 2863 fast + 40 ledgers pass
- **Next:** retrieval report v2 once reranker-large lands; R4 graph expansion

### S068 · 2026-10-18 22:53 IST · DEL-4 · Retrieval: 6 dense models + 2 cross-encoders, paired bootstrap
- **Who:** Kush
- **Did:** A100: e5-large-v2, gte-large, bge-large, bge-small embeddings + bge-reranker-base/large over RRF top-50. Paired MRR@10: RRF+e5-large +0.057 [+0.035,+0.082] vs RRF+bge-small; rerankers -0.056/-0.091 (negative); structured+dense +0.005 n.s. Decision: e5-large free-text fallback; structured primary; no reranker; no dense blend.
- **Files:** `tools/eval_retrieval_silver.py`, `reports/del4/retrieval_silver_v1.{md`, `json}`, `reports/del4/retrieval_silver_v2_analysis.md`, `docs/BUILD_TRACKER.md`
- **Verified:** eval rerun with all 6 embeddings + 2 rerank files; paired CIs in report
- **Next:** R4 graph expansion; RQ16-03 hard-negative compatibility reranker

### S069 · 2026-10-18 23:28 IST · DEL-1 · Ingredient-link review signed off by Kush and applied (D-014)
- **Who:** Kush
- **Did:** Kush confirmed bulk sign-off of the 389 AI-prechecked link rows. apply_link_review.py (--sign-as Kush) filled human_decision=AI recommendation with basis; decisions: 237 LINKED, 129 HELD, 23 CONCEPT_MISSING (no concepts minted). link_evidence.py now applies signed decisions every run: 2,806 EVD rows revised; second pass writes nothing; KGE rebuilt. Potato vitamin C now DIRECT; carrot beta-carotene / spinach folate stay NEAR (linked rows are polyphenols; nutrient rows are held USDA/Bognar categories) — genuine data gap.
- **Files:** `src/culinarystate/evidence/link_review.py`, `tools/{apply_link_review`, `link_evidence}.py`, `registry/evidence/evd_ingredient_link_{review_AI_prechecked`, `decisions`, `review}.csv`, `DECISIONS.md D-014`, `handoff/RUNBOOK.md`, `STATUS.md`, `tests/unit/test_link_review.py`
- **Verified:** pytest 2866 fast + 40 ledgers (release audit) pass; link_evidence idempotent
- **Next:** R4 graph expansion; RQ16-03 hard-negative compatibility reranker

### S070 · 2026-10-18 23:40 IST · DEL-4 · R4 food-graph expansion + strict near-evidence rule
- **Who:** Kush
- **Did:** FoodGraph over ING parents + OFF taxonomy (ODbL) with categorical match types; leave-cell-out eval of 1,500 cells: vertical relations promoted (new cells MAE 0.032 vs 0.058 global median, Δ -0.026 CI excludes 0), siblings off (worse than baseline), unlinked-food rows no longer NEAR when a food is asked (old rule Δ +0.018 worse than baseline) -> BROAD_QUALITATIVE with 'relation unknown' wording. Lexicon carries relations; Query.ingredient_relations; compat match record.
- **Files:** `src/culinarystate/retrieval/{food_graph`, `compatibility`, `retriever}.py`, `src/culinarystate/decision/pipeline.py`, `src/culinarystate/generation/verbalize.py`, `tools/eval_graph_expansion.py`, `reports/del4/graph_expansion_v1{.md`, `.json`, `_analysis.md}`, `tests/unit/test_{food_graph`, `retrieval`, `pipeline`, `verbalize}.py`
- **Verified:** pytest 2875 fast + 40 ledgers pass; demo answers re-checked
- **Next:** paired test for GROUP_ROW; RQ16-03 hard-negative compatibility reranker; benchmark authoring (D-008) still human-gated

### S071 · 2026-10-18 23:51 IST · DEL-5 · C2 target slot: closed-world ledger target lexicon
- **Who:** Kush
- **Did:** EXP-000006 predicted-slot run showed parse_query got the target right 20.5% of the time (regex nutrient list misses lycopene/choline/polyphenols/weight yield; 'carot' ambiguous). targets@0.1: variants of the 223 ledger target names (head before qualifier, beta-carotene forms, a + b), longest word-bounded match, shared key when ambiguous; 'fat'/'water' excluded. Accuracy 0.994 on templated questions (optimistic); natural phrasings checked.
- **Files:** `src/culinarystate/decision/{targets`, `pipeline}.py`, `tests/unit/test_targets.py`
- **Verified:** pytest 2879 fast + 40 ledgers pass
- **Next:** RQ16-03 pilot record

### S072 · 2026-10-18 23:51 IST · DEL-4 · RQ16-03 silver pilot (EXP-000006): structured compatibility vs generic cross-encoder
- **Who:** Kush
- **Did:** Pre-registered card committed before running. 800 queries with typed hard negatives (§241.4); CE scores on A100 (large 20 s, base 10 s). HARD AUROC: CE-large 0.924, structured oracle 0.995 (+0.071), structured predicted slots 0.975 (+0.051), struct+CE LR 0.996 (food-/process-cold). Verdict: success gate met on silver; mostly by construction; KEEP structured, no learned reranker; headline NEED_DATA.
- **Files:** `experiments/EXP-000006/card.md`, `tools/{build_rq1603_pairs`, `score_pairs_ce`, `eval_rq1603}.py`, `reports/del4/rq1603_pilot_v1.{md`, `json}`, `docs/BUILD_TRACKER.md`
- **Verified:** eval reproducible from pairs + CE files; ledger audit (card contract) passes
- **Next:** benchmark authoring for human labels (D-008); C10/C15/C18 per tracker

### S073 · 2026-10-19 01:33 IST · DEL-5 · NER runtime replay verified on Mac
- **Who:** Kush+Claude
- **Did:** Pulled deberta-v3-base+CRF model from A100 (scp). Ran --replay on TASTEset test split (105 docs, seed 7). Got 0.9266 exact F1, matches tagger.json exactly. MPS device. Sample tag of '2 cups finely chopped fresh spinach' correct.
- **Files:** `data/interim/models/ner/deberta-v3-base_crf/ tools/ner_tag.py`
- **Verified:** replay_test_exact_f1==trained_test_exact_f1==0.9266

### S074 · 2026-10-19 01:44 IST · DEL-5 · C18 session-state updater wired to pipeline and ask
- **Who:** Kush+Claude
- **Did:** SessionState class wraps engine replay; from_session() auto-injects Add events from ingredients list; process_history() feeds diagnosis verifier with actual session steps (was using question processes). Pipeline.answer() accepts session kwarg. ask.py takes --session and --turn flags. Diagnosis now marks causes CONSISTENT/INCONSISTENT against real cooking history (demo: boil in session → 'boiled' cause CONSISTENT for curdle). 16 unit tests (12 mandatory + 4 extra).
- **Files:** `src/culinarystate/decision/session_state.py src/culinarystate/decision/pipeline.py tools/ask.py tests/unit/test_session_state.py`
- **Verified:** 2897 fast tests pass; diagnosis CONSISTENT with session history

### S075 · 2026-10-19 01:48 IST · DEL-5 · C10 candidate action generator
- **Who:** Kush+Claude
- **Did:** candidates@0.1: three candidate families (PROCESS from ING_PROCESSED_BY, SUBSTITUTION from ING_ALTERNATIVE_TO, SEQUENCE from PROC_FOLLOWED_BY). Ranks by evidence_count then confidence. Nothing invented. 15 unit tests (12 mandatory + 3 extra).
- **Files:** `src/culinarystate/decision/candidates.py tests/unit/test_candidates.py`
- **Verified:** 2912 fast tests pass

### S076 · 2026-10-19 01:50 IST · DEL-5 · C15 multi-objective selector (Pareto front)
- **Who:** Kush+Claude
- **Did:** selector@0.1: Pareto front over retention (higher better), time (lower better), feasibility (ALLOWED>CONSTRAINED>UNKNOWN; REJECTED excluded). No hidden weights. UNKNOWN objectives neutral. 14 unit tests (12 mandatory + 2 extra).
- **Files:** `src/culinarystate/decision/selector.py tests/unit/test_selector.py`
- **Verified:** 2926 fast tests pass

### S077 · 2026-10-19 02:15 IST · E16-A · NER error analysis, paired bootstrap, hybrid pipeline
- **Who:** Kush+Claude
- **Did:** Error analysis of 301 test errors (deberta-v3-base_crf seed 1): 46.5% boundary, FOOD↔PHYSICAL_QUALITY top confusion, PART/TASTE weakest. Paired bootstrap significance: CRF sig p=0.003, kNN-NER null (Δ=0 all 5 seeds, excluded). Built NER hybrid pipeline module (rules → encoder cascade, GLiNER/verifier stubs). 14 new tests (2940 total).
- **Files:** `src/culinarystate/ner/pipeline.py`, `tools/ner_analysis.py`, `reports/ner/e16a_error_analysis.md`, `reports/ner/e16a_significance.md`, `tests/unit/test_ner_pipeline.py`
- **Verified:** pytest 2940 pass; error analysis covers 7 models × 5 seeds; bootstrap CIs match report

### S078 · 2026-10-19 10:29 IST · RS · S078: CoSyLab public data audit + RecipeDB3 NER vulnerability analysis
- **Who:** Kush+Claude
- **Did:** Surveyed all 26 cosylabiiit GitHub repos via API. Found 10 AI/data-science vulnerabilities in RecipeDB3 NER pipeline (test-set model selection, SIZE dropped, augmentation leakage, head-heavy test, no validation set, etc). Discovered RecipeDB2 category errors (shallot=Seafood). Mapped 18 CoSyLab web services. Identified Foodoscope as main API. Only 4/26 repos have licenses. Created vulnerability analysis + full data audit reports.
- **Files:** `reports/ner/recipedb3_vulnerability_analysis.md reports/cosylab_data_audit.md`
- **Verified:** All findings verifiable from public GitHub repos

### S079 · 2026-10-19 11:00 IST · RS · S078: CoSyLab audit + data download
- **Who:** Kush+Claude
- **Did:** Surveyed 26 cosylabiiit repos, downloaded 10 datasets, found 10 NER vulnerabilities + category errors
- **Files:** `reports/ner/recipedb3_vulnerability_analysis.md reports/cosylab_data_audit.md data/external/`
- **Verified:** Analysis scripts prove claims

### S080 · 2026-10-19 11:12 IST · S080 · CoSyLab data → ledger alignment
- **Who:** Kush+Claude
- **Did:** Aligned downloaded CoSyLab data with ledgers: (1) 5,191 taste molecule edges from bittersweet/SweetpredDB, 632 matched to MOL ledger; (2) 19,019 RecipeDB2 categories crosswalked to ING registry — 236 agree, 227 disagree, 582 no FoodOn; (3) NER tag distribution comparison confirms SIZE dropped; (4) Ingested 616 MOL_HAS_TASTE + 809 ING_COSYLAB_CATEGORY KG edges (KG: 15,339→16,764)
- **Files:** `tools/align_cosylab_ledgers.py`, `tools/ingest_cosylab_kg.py`, `registry/molecules/taste_molecule_alignment.csv`, `registry/ingredients/cosylab_category_crosswalk.csv`, `registry/kg/kg_edges_v1.csv`
- **Verified:** KG edge count 16764; taste alignment CSV 5191 rows; crosswalk CSV 19019 rows

### S081 · 2026-10-19 11:24 IST · S081 · Clone large CoSyLab files + augmentation leakage verification
- **Who:** Kush+Claude
- **Did:** Cloned 5 CoSyLab repos (shallow), filled all 15 empty files (102MB total). Verified V3 augmentation leakage: 128 exact dupes (5.9%), 322 masked dupes (15.5%), 915 internal dupes. Machine_Annotated_train 84K rows zero overlap with manual data. New data: SustainableFoodDB 118K recipes + 1.15M recipe-ingredient pairs, spice-disease 6.7K sentences, AllerStack 4.3K proteins, NOVA 2970×103 nutrients.
- **Files:** `data/external/recipe_ner_dl/*`, `data/external/sustainablefooddb/*`, `data/external/spice_disease/*`, `data/external/allerstack/*`, `data/external/nova_food_processing/*`, `reports/ner/recipedb3_vulnerability_analysis.md`
- **Verified:** 0 empty files remain; V3 numbers verified from actual data

### S082 · 2026-10-19 11:26 IST · S082 · Spice-disease KG + GLiNER script prep + SustainableFoodDB analysis
- **Who:** Kush+Claude
- **Did:** Ingested 481 ING_HEALTH_ASSOCIATION KG edges from spice-disease PubMed data (45 foods × diseases, ≥2 mentions). KG now 17,245 edges. Analyzed SustainableFoodDB: 118K recipes (26 cuisines), 1.15M ingredient pairs (86% coverage via substring match). Sueatable: 3,338 food items with CO2 data. Prepared GLiNER zero-shot run script for A100.
- **Files:** `tools/ingest_spice_disease_kg.py`, `registry/kg/kg_edges_v1.csv`, `gpu/ner_tasteset/run_gliner.sh`
- **Verified:** KG edges 17245; 481 health association edges; GLiNER script ready

### S083 · 2026-10-19 11:30 IST · S083 · GLiNER zero-shot results retrieved from A100
- **Who:** Kush+Claude
- **Did:** GLiNER already ran on server. Results: large-v2.1 zero-shot exact F1 0.232 [0.212-0.254], relaxed 0.643. Per-label: FOOD exact 0.470/relaxed 0.801, PROCESS 0.532/0.631, QUANTITY 0.051/0.872. Confirms GLiNER is strong for entity detection (high relaxed) but weak for exact boundaries — validates hybrid pipeline design where GLiNER is fallback only. Copied results to gpu/ner_tasteset/runs/. Also ingested 481 ING_HEALTH_ASSOCIATION KG edges from spice-disease data.
- **Files:** `gpu/ner_tasteset/runs/gliner_gliner_large-v2.1_zeroshot_seed1.json`, `gpu/ner_tasteset/runs/gliner_gliner_medium-v2.1_zeroshot_seed1.json`, `STATUS.md`
- **Verified:** GLiNER large exact F1 0.2317; relaxed F1 0.6429; FOOD exact 0.4704

### S084 · 2026-10-19 11:31 IST · S084 · GLiNER wired into hybrid NER pipeline
- **Who:** Kush+Claude
- **Did:** Replaced GLiNER stub with real implementation using eval results: threshold 0.2, confidence 0.40 (fallback-only). Labels mapped: 9 TASTEset types via natural-language prompts. Lazy model loading. 2940 tests pass.
- **Files:** `src/culinarystate/ner/pipeline.py`
- **Verified:** 2940 passed 0 failed; GLiNER default layers still (RULE, ENCODER)

### S085 · 2026-10-19 11:37 IST · B-NER · S085 commit CoSyLab alignment + GLiNER wiring
- **Who:** claude
- **Did:** Committed S078-S084 work in 16 per-file commits; gitignored data/external (mixed licences incl AGPL)
- **Files:** `.gitignore`, `tools/*`, `registry/*`, `reports/*`, `src/culinarystate/ner/pipeline.py`
- **Verified:** git status clean; 2940 tests passed pre-commit
- **Next:** Wire C10+C15 into decision/pipeline.answer()

### S086 · 2026-10-19 11:38 IST · B-DEC · S086 C15 Pareto view wired into answer()
- **Who:** claude
- **Did:** pareto_view(): median MEASURED retention + feasibility -> selector.select; added as answer()['pareto'] for COMPARE/RECOMMEND; time axis not wired (neutral)
- **Files:** `src/culinarystate/decision/pipeline.py`, `tests/test_pareto_view.py`
- **Verified:** 2943 passed, 40 deselected
- **Next:** Wire C10 substitution/sequence candidates; ingest 4,559 unmatched taste molecules; human queue

### S087 · 2026-10-19 11:42 IST · B-DEC · S087 C10 candidates wired into answer()
- **Who:** claude
- **Did:** Lexicon gains alternatives/followed_by/ing_names from KGE (220 ALT_TO, 63 FOLLOWED_BY); extra_candidates() -> answer()['candidates'] for RECOMMEND/COMPARE/RECOVER
- **Files:** `src/culinarystate/decision/pipeline.py`, `tests/test_extra_candidates.py`
- **Verified:** 2945 passed
- **Next:** Ingest unmatched taste molecules; human queue; H1 email

### S088 · 2026-10-19 11:54 IST · B-LIC · S088 licence + ledger-bypass fix for CoSyLab ingests
- **Who:** claude
- **Did:** Found S080-S082 edges came from unlicensed sources (RecipeDB2, spice-disease, SweetpredDB) and bypassed ledger; reverted kg_edges CSV to ledger-derived, removed crosswalk/alignment CSVs and 2 ingesters; added ledger-based tools/ingest_bittersweet_kg.py (AGPL SRC, 524 MOL_HAS_TASTE edges, InChIKey match via rdkit); rdkit installed in base anaconda (user-approved)
- **Files:** `tools/ingest_bittersweet_kg.py`, `ledgers/data/*`, `registry/kg/kg_edges_v1.csv`, `STATUS.md`
- **Verified:** 2945 passed; build_kg_edges rebuild ok
- **Next:** H1 email must request RecipeDB2/spice-disease/SweetpredDB/SustainableFoodDB/RecipeDB3 permission

### S089 · 2026-10-19 11:58 IST · H1 · S089 H1 email draft updated
- **Who:** claude
- **Did:** Added item 4 (RecipeDB2, spice-disease, SweetpredDB, SustainableFoodDB permission); note to withhold NER findings (H6)
- **Files:** `handoff/H1_email_bagler.md`
- **Verified:** draft only; Kush sends
- **Next:** Kush review+send H1

### S090 · 2026-10-19 12:11 IST · B-LIC · S090 CoSyLab data re-ingested under D-015
- **Who:** claude
- **Did:** Kush reports Prof. Bagler permitted use. Recorded D-015 (ASSUMED/DERIVED_ONLY, written confirmation still requested); added 2 value predicates; ledger ingest of RecipeDB2 categories, spice-disease, SweetpredDB (1470 KGE created, 229 categories agree)
- **Files:** `tools/ingest_cosylab_permitted.py`, `DECISIONS.md`, `ledgers/data/*`
- **Verified:** 2945 passed
- **Next:** Download RecipeDB3 NER annotations for matched reproduction on A100 (needs VPN confirm); SustainableFoodDB/companion use

### S091 · 2026-10-19 12:14 IST · B-NER · S091 RecipeDB3 NER data + reproduction harness
- **Who:** claude
- **Did:** Downloaded RecipeDB3 NER annotation + notebooks to data/external/recipedb3_ner (permission D-015). Finding: released Ingredient_Annotated_Dataset.csv == final_train_augmented (26,444 rows, 25,529 unique); their notebook random 80/20 split (seed 48) and selects best epoch on the TEST set (reported macro F1 0.9557, 15 ep, deberta-base). Local dry-run: 13.3% of their test rows have a masked family in train (4.9% exact); grouped split gives 0%. Wrote gpu/ner_recipedb3/repro.py (theirs vs clean, leaked/non-leaked breakdown) + run_all.sh
- **Files:** `gpu/ner_recipedb3/*`
- **Verified:** syntax ok; data prep dry-run local; not yet run on GPU
- **Next:** VPN confirm -> scp + run on A100

### S092 · 2026-10-19 16:00 IST · B-NER · S092 RecipeDB3 protocol verified locally; server unreachable
- **Who:** claude
- **Did:** VPN not working (SSH timeout, no route; user confirmed). Verified locally: selection on test, random split, 13.5%+-0.4% masked-family leakage over 100 splits, SIZE excluded. Report section added; GPU runs deferred
- **Files:** `reports/ner/recipedb3_vulnerability_analysis.md`
- **Verified:** 100-split local stats
- **Next:** when VPN works: scp gpu/ner_recipedb3 + data, run_all.sh

### S093 · 2026-10-19 16:03 IST · PLAN · S093 dataset+ledger status and model plan
- **Who:** claude
- **Did:** Read SSOT §190.4/§245/§257B + Plan Parts K/L/N + BUILD_TRACKER; wrote docs/plan/S093 (ledger counts, unused datasets and routes, sequence, NER/bi-encoder/AE reasoning)
- **Files:** `docs/plan/S093_dataset_ledger_status_and_model_plan.md`
- **Verified:** counts from LedgerStore
- **Next:** mention->ING bi-encoder linking baseline (Mac MPS), C15 time axis, SustainableFoodDB carbon attr

### S094 · 2026-10-19 16:05 IST · B-LINK · S094 mention->ING bi-encoder baseline
- **Who:** claude
- **Did:** Leave-one-alias-out: 623 EN alias queries; e5-large-v2 zero-shot Acc@1 0.607 vs char TF-IDF 0.555 (paired +0.051 CI [0.014,0.090]); RRF no gain
- **Files:** `tools/eval_alias_linking.py`, `reports/ner/alias_linking_v1.json`
- **Verified:** ran on Mac MPS recsys_env
- **Next:** contrastive fine-tune w/ sibling hard negatives (A100, ING-grouped); C15 time axis; SustainableFoodDB carbon attr

### S095 · 2026-10-19 16:06 IST · B-DEC · S095 C15 time axis wired
- **Who:** claude
- **Did:** Lexicon.durations (PROC id -> p50 min from 39 duration KGE); pareto_view uses it as time objective
- **Files:** `src/culinarystate/decision/pipeline.py`, `tests/test_pareto_view.py`
- **Verified:** 2946 passed
- **Next:** SustainableFoodDB carbon attr as 2nd objective; contrastive linker fine-tune (needs VPN)

### S096 · 2026-10-19 16:13 IST · B-KG · S096 carbon footprint edges + substitution context
- **Who:** claude
- **Did:** ING_CARBON_FOOTPRINT stat predicate; 134 ING with literature kgCO2e/kg quantiles (exact item match only); Lexicon.carbon; substitution candidate reasons show carbon vs original
- **Files:** `tools/ingest_carbon_footprint.py`, `src/culinarystate/decision/pipeline.py`, `ledgers/data/*`
- **Verified:** 2947 passed; 40 ledger tests passed
- **Next:** contrastive linker fine-tune + RecipeDB3 runs (VPN); AllerStack/NOVA after sign-off; B0-B5 ladder prep

### S097 · 2026-10-19 16:15 IST · PLAN · S097 DONE_FROM_SSOT handoff list
- **Who:** claude
- **Did:** Wrote docs/DONE_FROM_SSOT.md from WORKLOG S001-S096, BUILD_TRACKER, ledgers; ask.py now shows tradeoff/alternatives
- **Files:** `docs/DONE_FROM_SSOT.md`, `tools/ask.py`
- **Verified:** counts from LedgerStore/WORKLOG
- **Next:** user supplies continuation prompt

### S098 · 2026-10-19 16:17 IST · PLAN · S098 master-chat handoff prompt
- **Who:** claude
- **Did:** Wrote docs/MASTER_CHAT_HANDOFF_PROMPT.md: rules, built items with numbers, blockers, open units, asks for audit + ordered continuation prompt + re-plan
- **Files:** `docs/MASTER_CHAT_HANDOFF_PROMPT.md`
- **Verified:** numbers from WORKLOG/ledgers
- **Next:** user pastes into master chat

### S099 · 2026-10-19 16:19 IST · PLAN · S099 removed master-chat handoff file
- **Who:** claude
- **Did:** Deleted docs/MASTER_CHAT_HANDOFF_PROMPT.md on Kush's request (recoverable from git history, commit after S098); update prompt delivered in chat instead
- **Files:** `docs/MASTER_CHAT_HANDOFF_PROMPT.md`
- **Verified:** git rm + commit
- **Next:** user pastes update into SSOT chat

### S100 · 2026-10-19 17:02 IST · DEL-3/4/5 · S100 state-awareness readiness audit + H_STATE pre-registration
- **Who:** claude
- **Did:** Audited the 12-stage raw-recipe-to-decision path. VERIFIED: replay determinism only. Not verified: text->events (n=3 single-annotator dev-contaminated examples; state-field acc 0.43/0.00/0.40, merge-split F1 1.0/0.35/1.0), coreference (runtime C2 not built), merge/split/observation sessions (30 AI_DRAFT, hand-authored events, 0 human-reviewed), calibration (no labels). Key finding: B4 did not exist - Query state fields were never populated and session only fed diagnosis history. Added minimum code: decision/state_conditioning.py + answer(use_state) + ask.py --use-state + 4 tests (default = B3). No test set exists for H_STATE (ladder Qs are AI-authored, single-turn). Wrote claim gate (12 rows), EXP-000007 card (20 Gold recipes, 60 state-dependent Qs + 20 controls, B3 vs B4-pred vs B4-oracle, CC@5 primary, paired grouped bootstrap, success/null/negative/invalid gates). Card kept in experiments/ (not registry/experiments, which does not exist); EXP-000005/6/7 not yet in EXP ledger. Not run: final experiment.
- **Files:** `reports/state_awareness_readiness_v1.md`, `experiments/EXP-000007/card.md`, `src/culinarystate/decision/state_conditioning.py`, `src/culinarystate/decision/pipeline.py`, `tools/ask.py`, `tests/unit/test_state_conditioning.py`
- **Verified:** 2951 passed, 40 deselected; B3 vs B4 smoke n=1 on a boiled-broccoli session
- **Next:** Human Gold G1-G6 (adjudicate 20 pilot recipes, author 60+20 questions and cells); then build the cut-point harness and run EXP-000007. Recommended single step: Kush+Parv annotate the first 5 pilot_20 recipes in full (events + 3 questions each) as a dry run of G1-G3.

### S101 · 2026-10-19 17:11 IST · DEL-3 · S101 freeze pilot_20 Gold input; register EXP-5/6/7; BLOCKED_HUMAN
- **Who:** claude
- **Did:** Registered EXP-000005/6/7 in the EXP ledger under their existing IDs (minter asserted; ledger 1-7 contiguous, cards+results paths verified, no replacement IDs, card text untouched). Froze pilot_20 unchanged: manifest with raw-content SHA256 identical to REC content_sha256 for 20/20, 20 distinct families; created 20 blank DRAFT files each in annotation/gold/pilot_20/Kush and Parv (local only; freeze tool never overwrites annotator work). Added handbook Addendum A (S100 clarifications only), PILOT_20_TASK.md with exact commands, gold_cli replay, categorised agreement module (9 disagreement categories, label-invariant entity alignment) + batch runner that exits BLOCKED_HUMAN until 40 files are DONE+valid. No annotation, agreement or adjudication performed or fabricated. H_STATE questions, compiler tuning, GPU work not started.
- **Files:** `tools/register_exp_cards.py`, `tools/freeze_gold_pilot.py`, `tools/gold_pilot_agreement.py`, `tools/gold_cli.py`, `src/culinarystate/annotation/pilot_agreement.py`, `annotation/PILOT_20_TASK.md`, `annotation/annotation_handbook_v1.md`, `annotation/gold/pilot_20_manifest.csv`, `reports/del3/gold_pilot_20_v1.md`, `ledgers/data/EXP.jsonl`
- **Verified:** 2954 passed, 40 deselected; gold_pilot_agreement.py exits 2 BLOCKED_HUMAN (40/40 not DONE); blank files fail validate as intended
- **Next:** S102: Kush and Parv annotate the same first 5 recipes (R011207, R002919, R010532, R006967, R007017), validate+replay, then request a partial agreement run to expose handbook gaps before the remaining 15.

### S102 · 2026-10-19 17:35 IST · DEL-3 · S102 Gold calibration round: 7 recipes, one per stratum (BLOCKED_HUMAN)
- **Who:** claude
- **Did:** Accepted audit correction (7 strata, not 5). Selected the 7 mechanically before any annotation: first recipe_id per alphabetically sorted stratum -> R003595 baking, R002919 drain_discard, R000387 indian, R002843 multi_component, R000312 random, R008469 reserve_split, R001894 simple; recorded in text-free annotation/gold/pilot_7_calibration_manifest.csv. Added --only/--calibration/--tag to gold_pilot_agreement.py (default all 20; subset needs DONE+valid for selected recipes only), per-category rates and a mechanical >20% gate flag; 4 tests (a wrong dict key for relation F1 was caught by the identical-docs test and fixed). Both runs currently exit 2 BLOCKED_HUMAN. No annotation, agreement, adjudication, compiler tuning, H_STATE or B3/B4 work.
- **Files:** `tools/gold_pilot_agreement.py`, `tests/unit/test_gold_pilot_runner.py`, `annotation/gold/pilot_7_calibration_manifest.csv`, `annotation/PILOT_20_TASK.md`, `reports/del3/gold_pilot_7_calibration.md`
- **Verified:** full suite passes; --calibration and all-20 runs exit 2
- **Next:** Kush and Parv annotate the 7 recipes, validate+replay, then run gold_pilot_agreement.py --calibration; gate verdict decides the other 13.

### S103 · 2026-10-19 18:45 IST · DEL-3 · S103 filed OpenAI GPT-5.6 Sol AI pre-annotation for pilot_20 as review material (not Gold)
- **Who:** claude
- **Did:** Moved pilot20_AI_REVIEW_combined.json and AI_REVIEW_INDEX.csv from Downloads to annotation/ai_review/pilot_20/ (local, gitignored). File self-declares blind_human_gold=false, human_verified=false, do-not-treat-as-independent. Checked: 20/20 recipe texts identical to the frozen input; schema-invalid only because of review wrapper fields; replay clean. Wrote review_status_log.csv: Kush = REVIEWED_ACCEPTED per Kush's statement (not independently verified), Parv = PENDING_PARV_REVIEW. Did NOT write into annotation/gold/pilot_20/Kush or Parv and did NOT set any Gold file DONE: the gate stays BLOCKED_HUMAN because an AI draft shown to a human is not a blind independent annotation. Decision needed from Kush: keep blind double annotation, or switch pilot_20 to an AI-draft + human-review design (new provenance class, agreement replaced by correction rates).
- **Files:** `annotation/ai_review/pilot_20/review_status_log.csv`
- **Verified:** 20/20 text==frozen; 0 replay issues; Gold folders untouched
- **Next:** Kush decides design (blind vs AI-draft+review); Parv should not open ai_review if blind pass is kept.

### S104 · 2026-10-19 18:48 IST · DEL-3 · S104 AI draft is not handbook-conformant; no Gold files written
- **Who:** claude
- **Did:** Tried to convert the OpenAI GPT-5.6 Sol review draft into gold-1.0 files (Kush DONE / Parv DRAFT per Kush's instruction). Aborted before writing: the draft uses another model (labels AMOUNT/FOOD_MENTION/HEAT_TEMPERATURE/DURATION/PREP_STATE/PURPOSE/QUALITATIVE_AMOUNT/INTERMEDIATE_MENTION; ingredient 'concept_candidate' surface strings, 58/179 not in ING registry, no 'concept'; events in free-text operation/action/inputs/output/conditions form where every event names an output, TRANSFORM with 2-3 inputs (15), RECOMBINE used for 'serve with' (18), RESERVE for 'keep warm' (6), plus WAIT). Mapping those to handbook Reserve/Recombine/Merge semantics needs human decisions; writing them as Kush DONE would put wrong state labels into Gold. Nothing in annotation/gold/pilot_20/Kush|Parv changed (still blank DRAFT). Draft kept in annotation/ai_review/pilot_20 as reading aid.
- **Files:** `annotation/ai_review/pilot_20/`
- **Verified:** validate_gold rejected all 20 (missing concept, extra fields) before any write
- **Next:** Kush chooses: (a) AI-assisted conversion draft with every ambiguous event flagged, Kush reviews via replay and marks DONE himself; (b) annotate in gold schema using the draft as reading aid.

### S105 · 2026-10-19 18:54 IST · DEL-3 · S105 Kush's AI-assisted pilot_20 set written; Parv's folder restored to blank
- **Who:** claude
- **Did:** Per Kush's instruction and the GPT plan: converted the OpenAI GPT-5.6 Sol draft to gold-1.0 (tools/convert_ai_review.py): 20/20 Kush files DONE, validate OK, replay issue-free; 183 gold events from 189 draft events (13 draft events not convertible, 8 of them in R003595); 108 of 113 coref mentions stored as UNKNOWN (draft gave no entity labels); every rule decision logged locally in conversion_log.csv and summarised in reports/del3/ai_review_conversion_v1.md. Restored all 20 Parv files to blank drafts (blind pass; Parv must not see the draft or Kush's set). D-016 records the provenance: Kush set = AI_ASSISTED_HUMAN_REVIEWED, not independent. Agreement runner now labels such comparisons NOT_INDEPENDENT. calibration run still BLOCKED_HUMAN (Parv 0/7).
- **Files:** `tools/convert_ai_review.py`, `tools/gold_pilot_agreement.py`, `DECISIONS.md`, `reports/del3/ai_review_conversion_v1.md`, `annotation/gold/pilot_20_manifest.csv`
- **Verified:** 2959 passed; 20/20 Kush validate OK; --calibration exits 2 (Parv blank)
- **Next:** Kush sends one-line corrections per recipe (applied + logged); Parv annotates the 7 calibration recipes blind; then gold_pilot_agreement.py --calibration.

### S106 · 2026-10-19 18:56 IST · DEL-3 · S106 Kush approval recorded; Parv blind pack built; chain stops at Parv
- **Who:** claude
- **Did:** Kush reported all 20 AI-assisted annotations reviewed and good (no corrections). Recorded kush_correction_log.csv (20 x approve, 0 corrections; local) and hash-frozen annotation/gold/pilot_20_kush_ai_assisted_manifest.csv (sha256 per Kush file + source draft sha, set name Kush_AI_ASSISTED_REVIEWED). Built annotation/parv_pack/culinarystate_parv.zip (gitignored): src, gold_cli, handbook+Addendum A, checklists, examples, registries, 20 blank Parv files, PARV_START_HERE.md; no AI draft, Kush files, decisions or reports in it (scanned; only generic 'AI_DRAFT' status strings in library code); tested from a clean unzip (validate fails on blank as intended, passes on worked example). Plan steps 4-8 need Parv's blind pass and human adjudication; not run.
- **Files:** `annotation/gold/pilot_20_kush_ai_assisted_manifest.csv`, `annotation/parv_pack/culinarystate_parv.zip`, `STATUS.md`
- **Verified:** unzip test; leak scan; 20 recipes recorded
- **Next:** Parv blind-annotates the 7 calibration recipes; then gold_pilot_agreement.py --calibration; handbook gate; remaining 13; adjudicate; freeze Gold-v1; then compiler/state evaluation; then H_STATE.

### S107 · 2026-10-19 19:03 IST · DEL-3 · S107 Gold-v1 pilot frozen; first compiler vs Gold-v1 oracle cascade
- **Who:** claude
- **Did:** Per Kush: Parv's review was done by Kush on Parv's checklist, so Parv's 20 files = the AI-assisted set (annotator Parv, DONE, honest note), adjudicated files identical (vacuous), D-017. Agreement run: 0 disagreements, labelled NOT_INDEPENDENT; handbook gate NOT_EVALUATED. Applied Addendum A5 process canonicalisation (reconverted, refrozen, 60 files validate OK). Eval (tools/eval_compiler_vs_gold.py, no tuning, n=20, bootstrap CI): P state-field acc 0.102, alive F1 0.312, merge/split/reserve F1 0.343, relation F1 0.289, event loose F1 0.199; oracle concepts O1 0.130/0.342/0.349; gold Adds O2 ~same as P; gold sanity 1.0. Conclusion: ingredient linking not the bottleneck; step-event construction/state tracking is; compiler over-generates Transform (169 vs 64). Reference-noise caveats listed (13 unconverted events, padded remainders, coref 108/113 UNKNOWN). H_STATE question authoring and B3/B4 run not done (human-written questions required by EXP-000007).
- **Files:** `tools/freeze_gold_v1_pilot.py`, `tools/eval_compiler_vs_gold.py`, `tools/convert_ai_review.py`, `annotation/gold/gold_v1_pilot_manifest.csv`, `reports/del3/compiler_vs_gold_v1.md`, `DECISIONS.md`
- **Verified:** 60 gold files validate OK; gold-vs-gold sanity 1.0; suite passes
- **Next:** Choose: (a) correction pass on the Gold artefacts, then re-run the cascade, or (b) author the H_STATE questions (human) and run B3 vs B4-pred vs B4-gold.

### S108 · 2026-10-19 19:13 IST · DEL-3 · S108 Gold-v1 reference repair: correction queue, provisional v1.1, clean compiler rerun (GOLD_ORACLE_NOT_READY)
- **Who:** claude
- **Did:** Built annotation/gold/gold_v1_correction_queue.csv (67 rows, all AI_PROPOSED, decision/reviewer empty): 13 unconverted events + 4 padded splits + downstream artefacts in 7 recipes (reading them against source text also found draft ANNOTATION errors in R003595 glaze/anti-curdle/batter and R004275 purée/reserved peas), 25 coref proposals, 25 automated AUDIT_FLAGs, 1 schema limitation (R009647 tool state, no change). Provisional v1.1 in pilot_20_adjudicated_v1_1_proposed (validates, replays, status DRAFT); Gold-v1 untouched. tools/apply_gold_corrections.py applies ONLY rows Kush marks approve (validate+replay gated, writes nothing otherwise; 4 tests). Converter fixed: single-output draft split -> Transform, no synthetic remainder (2 tests). Coref audit: explicit 1, structural 26, ambiguous 86, N/A 0 (87 of 108 UNKNOWN are pronouns, 86 are 'it'). Split audit: 3 converter problems, 1 annotation problem, 0 engine limitations. Same compiler (diff empty) rerun vs proposed v1.1: P state-field 0.102->0.140, alive F1 0.312->0.395, merge/split 0.343->0.368; O1 gain +0.019/-0.002; Transform 83 gold vs 169 predicted, Reserve 1 vs 8, Merge 85 vs 60. Verdict GOLD_ORACLE_NOT_READY: corrections unapproved, 12 recipes not read line by line, coref mostly UNKNOWN, set not independent. No H_STATE questions, no B3/B4.
- **Files:** `tools/build_gold_correction_queue.py`, `tools/apply_gold_corrections.py`, `tools/convert_ai_review.py`, `reports/del3/gold_v1_to_v1_1_changes.md`, `annotation/gold/gold_v1_1_proposed_manifest.csv`
- **Verified:** 2965 passed; proposed set validates+replays; apply tool writes nothing without approval; rule_compiler.py diff empty
- **Next:** Kush fills the decision column (approve/reject) in gold_v1_correction_queue.csv (41 proposal rows; read the 25 AUDIT_FLAG rows), then run tools/apply_gold_corrections.py.

### S109 · 2026-10-19 21:52 IST · DEL-3 · S109 full source audit of Gold-v1 + review gate prepared; Gold-v1.1 not created (GOLD_ORACLE_NOT_READY)
- **Who:** claude
- **Did:** Read all 20 recipes against source text (18 need substantive corrections, 2 coref-noise only, 0 clean). Found: lineage errors in most recipes; 9 ingredient lines with the word 'or' as ALTERNATIVE; optional grill as event; and that 78 of the 113 draft coref mentions are the letters 'it' inside words (S108's coref counts and structural proposals withdrawn). Queue now 119 rows: 95 need a decision (42 coref-noise removals, 4 genuine coref, 49 event/line corrections), 25 flags classified (no flag valid-as-is; 3 converter-origin, rest true annotation errors). Review sheet generated (annotation/gold/gold_v1_1_review_sheet.md). apply tool extended (drop_coref/set_coref/set_line_alt, tested). Provisional proposed set validates and replays 20/20; same compiler rerun vs proposed: P state-field 0.132, alive F1 0.340, merge/split 0.380; O1/O2 no gain; Transform 94 gold vs 169 predicted. No decisions recorded, nothing applied, v1.1 not written, v1 untouched.
- **Files:** `tools/build_gold_correction_queue.py`, `tools/make_gold_review_sheet.py`, `tools/apply_gold_corrections.py`, `reports/del3/gold_v1_full20_source_audit.md`, `reports/del3/gold_v1_to_v1_1_changes.md`
- **Verified:** suite passes; proposed set 20/20 validate+replay; apply tool writes nothing without approvals
- **Next:** Kush records decisions for the 95 rows (or says approve all proposals), then tools/apply_gold_corrections.py creates Gold-v1.1 and the S109 final rerun.

### S110 · 2026-10-19 22:39 IST · DEL-3 · S109 final: Kush's decisions applied, Gold-v1.1 created, three-way compiler comparison, GOLD_ORACLE_READY_FOR_H_STATE
- **Who:** claude
- **Did:** Recorded Kush's decisions (made after review with ChatGPT): 76 APPROVE, 19 MODIFY with his modification rules (AI-written patches, rationale per row in the queue), GC-017 documented schema limitation, 25 audit flags info only, 0 rejected, 0 unresolved. Moved gold_v1_1_AI_review_recommendations.csv to annotation/gold. Extended tools/apply_gold_corrections.py (MODIFY rows, multi-op patches, drop_coref key fix) and wrote tools/record_s109_decisions.py. Gold-v1.1 written (annotation/gold/pilot_20_adjudicated_v1_1) with manifest (v1 hash, v1.1 hash, change ids, provenance AI-assisted + human-reviewed development Gold); v1 hashes verified unchanged. validate 20/20, replay 20/20, deterministic 20/20, no converter-looking entities. Same compiler (rule_compiler.py diff empty) vs v1.1: P state-field 0.106, alive F1 0.294, merge/split/reserve F1 0.351, relation 0.324, event loose 0.247; O1/O2 no gain; Transform 169 pred vs 97 gold, Reserve 8 vs 1, Merge 60 vs 86. S107 -> S108 provisional -> S109 final conclusions stable. Verdict GOLD_ORACLE_READY_FOR_H_STATE with caveats: dev oracle, single AI audit reader, one human decision pass, coref mostly UNKNOWN, not independent. No compiler tuning, no H_STATE work.
- **Files:** `annotation/gold/pilot_20_adjudicated_v1_1/`, `annotation/gold/gold_v1_1_pilot_manifest.csv`, `tools/apply_gold_corrections.py`, `tools/record_s109_decisions.py`, `reports/del3/gold_v1_to_v1_1_changes.md`
- **Verified:** 2966 passed; v1.1 validate/replay/determinism 20/20; apply tool refuses invalid approvals
- **Next:** Author the H_STATE question set for EXP-000007 (60 state-dependent + 20 control questions from the v1.1 cut points, with gold evidence cells), human-written, then run B3 vs B4-predicted vs B4-gold.

### S111 · 2026-10-19 22:44 IST · X-API · S111 Foodoscope/CoSyLab API check (read-only, no key)
- **Who:** claude
- **Did:** Probed 19 endpoint rows with one unauthenticated request each (1 req/s). Findings: the cosylab.iiitd.edu.in/<db>/ bases from the integration sheet are web UIs (nginx HTML 404 on 12 API paths); SpiceRx search_plants is an HTML page; the real RecipeDB API host is api.foodoscope.com/recipe2-api (from public client code) and answers 400 {error: ApiKey is not provided} = AUTH_REQUIRED; auth header unverified (Bearer vs x-api-key both seen); FlavorDB/SpiceRx/SustainableFoodDB/DietRxDB/CocktailDB API hosts unknown, not guessed; id/region routes not called. A public repo hard-codes someone else's live key: not used, not stored. FOODOSCOPE_API_KEY not set. No ingestion.
- **Files:** `tools/probe_foodoscope.py`, `registry/sources/foodoscope_api_registry.csv`, `reports/sources/foodoscope_api_audit_v1.md`, `handoff/API_BLOCKERS.md`
- **Verified:** registry 19 rows; AUTH_REQUIRED x3 on api host; WRONG_HOST x12
- **Next:** Get our own Foodoscope key (H1), then rerun the probe and record header, id routes and the other databases' hosts from the Playground.

### S112 · 2026-10-19 22:47 IST · EXP-000007 · S112 H_STATE authoring pack built; question writing BLOCKED_HUMAN (prompt's S111 = this step)
- **Who:** claude
- **Did:** Built authoring packs for 20 Gold-v1.1 recipes (one deterministic mid-trajectory cut each, gold_state_hash, alive state, eligible evidence cells), a text-free manifest, a blank 80-slot question template (3 STATE_DEPENDENT + 1 CONTROL per recipe) and tools/validate_hstate_questions.py (+2 tests; exits 2 while empty). No question generated, no B3/B4 run, nothing frozen. Finding: only 10/20 recipes have ANY ledger retention cell across all cut points and 5 at the chosen cuts, so >=40 supported of 60 (card) is infeasible; options (a) keep + more abstention, (b) re-cut evidence recipes + abstention items, (c) add covered recipes with new Gold; recommended (b).
- **Files:** `tools/build_hstate_authoring_pack.py`, `tools/validate_hstate_questions.py`, `benchmark/h_state/questions_to_write.csv`, `reports/h_state/h_state_benchmark_v1.md`
- **Verified:** 20 recipes cut; validator blocks with exit 2; suite passes
- **Next:** Kush picks (a)/(b)/(c) and writes the 80 questions; validator; freeze.

### S113 · 2026-10-19 22:51 IST · X-API · S113 API-RECON-01: public Foodoscope implementations audited; env-only client built
- **Who:** claude
- **Did:** GitHub code search + file reads (no API calls with anyone's key): 30 files/19 repos; hosts api.foodoscope.com/recipe2-api and /flavordb (current), cosylab web UIs + :6969 (legacy); auth Bearer (most) or x-api-key; 3 files hold committed keys (redacted, compromised, unused; 0 token-like strings in the registry). One unauthenticated probe of api.foodoscope.com/flavordb: 400 ApiKey is not provided, so FlavorDB also needs a key on the current host. Contract facts (paths, entity_alias_readable/page/size paging, flavor_profile mismatch) recorded as UNVERIFIED. Built src/culinarystate/sources/foodoscope_client.py (env-only key, configurable header, retries, rate limit 25/min, bounded paging, snapshots without key) with 5 mocked tests. SustainableFoodDB/DietRxDB reported coming-soon; SpiceRx/CocktailDB hosts not found. No ingestion.
- **Files:** `tools/recon_foodoscope_public.py`, `src/culinarystate/sources/foodoscope_client.py`, `registry/sources/foodoscope_public_usage_registry.csv`, `reports/sources/foodoscope_public_implementations.md`
- **Verified:** suite passes; registry has no token-like string
- **Next:** Obtain our own Foodoscope key (H1/Starter plan), then verify the contracts with one request each.

### S114 · 2026-10-20 00:50 IST · DEL-3 · S114 EXP-000007 amendment A1 + evidence cut candidates
- **Who:** claude
- **Did:** Registered amendment (card + EXP rev 2); 111 candidate rows; max supported H_STATE-R = 14 over 8 recipes (target 40 not forced); 14 R / 19 A / 20 CONTROL slots, blank for Kush. S115 API/dataset terms survey (Spoonacular ToS forbids storage; keys not stored).
- **Files:** `tools/build_hstate_r_candidates.py`, `benchmark/h_state/evidence_cut_candidates.csv`, `reports/sources/api_and_dataset_survey_s115.md`
- **Verified:** no B3/B4 run; no question text written
- **Next:** Kush writes questions; update validator to strata; find retention/yield evidence sources

### S115 · 2026-10-20 10:12 IST · DEL-3 · External data audit + H_STATE coverage-lift decision (evidence-first scan, forecasts A/B/C)
- **Who:** claude
- **Did:** Food.com downloaded (Kaggle CLI, CC0 declared, authority unverified); official FNDDS/uFiSh/Density/AnFooD/USDA Cooking Yields R2 downloaded; registry 27 sources; Kaggle 17 process queries -> none relevant; GH/HF 29 rows; evidence-first scan BBC 11,934 (4,256 hit), Wikibooks 3,797 (1,051), Food.com 150k on A100 (48,969 hit, 243/338 cells); calibration precision 0.25; cleaned missing cells 810->58; forecasts A/B/C; decision: Path A +20 evidence-first Gold with screening, parallel +5 curated cells, do not write H_STATE questions yet; simulator contract + ingest policy; RecipeDB3 NER repro launched on A100 (running).
- **Files:** `registry/sources/external_data_source_registry.csv`, `reports/sources/external_data_landscape_v1.md`, `reports/h_state/h_state_coverage_lift_forecast.md`, `annotation/gold/evidence_first_gold_expansion_plan.md`, `tools/evidence_first_candidates.py`
- **Verified:** 2984 tests passed (11 new); no credentials in tracked files; S114 freeze hashes verified; no B3/B4, no questions, no compiler tuning
- **Next:** Kush approves Food.com local use + selection algorithm (Gate 1); then selection freeze and blinded A/B packs

### S116 · 2026-10-20 10:36 IST · DEL-3 · Gate 1 approval + evidence-first independent Gold expansion prepared
- **Who:** claude
- **Did:** Gate 1 (Kush): Food.com LOCAL research use only, no commit/redistribution of text, exact ingredient x process support definition kept (no family tier). Selection protocol v1 frozen; mechanical filters -> 120-recipe diverse pool (210 candidate rows); AI source-text screen (reviewer claude-ai, NOT human; pending Kush confirm): 114 ELIGIBLE / 52 ambiguous process / 42 false match / 2 other; selected 20 PRIMARY + 10 RESERVE (37 distinct ingredient x process cells, 25 ingredients, 3 process families WET 41/FAT 35/DRY 24%, 12 processes, 170 EVD ids from R6/Phenol-Explorer/Bognar, max ingredient share 15%); blank identical DRAFT_HUMAN_INDEPENDENT packs for Kush and Parv (20/20 each, hashes equal, schema-valid, no AI/compiler/model content); manifests hashed; top-5 evidence queue (onion simmer, carrot roast, garlic fry, garden pea steam, ginger fry); RecipeDB3 matched reproduction restarted on A100 after int64 JSON bug (per-label F1, duplicates, runtime, GPU, revision added; SIZE variant script ready), running.
- **Files:** `annotation/gold/evidence_first_expansion/selection_manifest_v1.csv`, `annotation/gold/evidence_first_expansion/preannotation_manifest.csv`, `evidence/queues/hstate_top5_process_state_evidence.csv`, `tools/select_evidence_first_gold.py`, `tools/make_independent_gold_packs.py`
- **Verified:** 2992 tests passed (19 new in S115-S116); recipe text only in git-ignored local files; no secrets in tracked files
- **Next:** Kush and Parv annotate the 20 recipes independently (no sharing), freeze, then agreement + adjudication; Kush confirms or overturns the AI eligibility screen BEFORE starting

### S117 · 2026-10-20 11:38 IST · DEL-3 · S117 Food.com 20 recipes: sheet converted to gold-1.0 (AI-assisted, human batch-approved)
- **Who:** claude
- **Did:** Converted Kush_Parv_joint_review_sheet.csv (402 rows) to gold-1.0 for Kush and Parv: 40/40 validate+replay clean, 281 events, 126 proposed events not written (unresolved refs). Provenance AI_ASSISTED_HUMAN_REVIEWED: Kush chat batch approval, Parv relayed, no row-level remarks, sets identical so agreement non-informative. Blank independent bundles and freeze hashes untouched. A100 RecipeDB3 reproduction still running (epoch ~11/15 first seed per protocol, 2 logs).
- **Files:** `tools/convert_foodcom_sheet.py`, `reports/gold/foodcom_ai_assisted_human_review.md`
- **Verified:** 2993 tests passed; 40/40 DONE
- **Next:** Pass 2 audit of 126 dropped events; pull RecipeDB3 results and finish reproduction report; span-model bake-off

### S118 · 2026-10-20 12:11 IST · DEL-3 · S118A Food.com Gold v1->v1.1 repair: 126 dropped events audited, all 20 recipes re-authored, H_STATE coverage recomputed
- **Who:** claude
- **Did:** Audit: 410 proposed events (not 407), 126 dropped (64 cascades, 22 root causes); S117 survivors also unsound (wrong inputs, mechanical output names) so all 20 recipes re-authored from source (310 events, step-only entities with UNKNOWN quantity, water/oil as medium). Outcomes: 57 restored, 36 superseded, 33 rejected by policy, 0 unresolved. 20/20 validate+replay+deterministic. H_STATE coverage observed: 15 recipes, 51 pairs, 37 cells (S114: 8/14). Verdict H_STATE_AUTHORING_READY with caveats (AI-authored, not human-verified; AI screen unconfirmed). No questions, no B3/B4.
- **Files:** `tools/audit_foodcom_dropped.py`, `tools/repair_foodcom_gold.py`, `tools/score_foodcom_repair.py`, `tools/hstate_coverage_foodcom.py`, `reports/gold/foodcom_ai_assisted_v1_to_v1_1.md`
- **Verified:** 2997 passed
- **Next:** S118B RecipeDB3 control; S118C freeze semantic NER benchmark

### S119 · 2026-10-20 12:14 IST · DEL-4 · S118C Semantic NER benchmark v1 frozen (splits, views, metrics, seeds, selection/statistics/Pareto rules)
- **Who:** claude
- **Did:** Froze before any candidate run: RecipeDB3 grouped split by masked-sentence family (train 18700 / CALIBRATION 2592 / dev 2597 / test 2555, 0 group overlap), TASTEset legacy seed-7 recipe split plus grouped CALIBRATION (424/65/106/105, 0 identical-recipe leaks). Label views, adapter to unified core, metric code hashes, seeds 1-5, dev-only checkpoint rule, min effect 0.003 + paired grouped bootstrap + Holm, Pareto promotion rule, router epsilon 0.02, train-only/out-of-fold feature rules. No model output read.
- **Files:** `src/culinarystate/ner/benchmark.py`, `tools/freeze_ner_benchmark.py`, `benchmark/ner/semantic_benchmark_v1.json`, `benchmark/ner/semantic_benchmark_manifest.csv`, `tests/test_ner_benchmark.py`
- **Verified:** 9 new tests pass
- **Next:** S118B finish RecipeDB3 control from A100 results

### S120 · 2026-10-20 12:25 IST · DEL-3 · S118 corrections (labels, counts, provenance, A100 launcher) per Kush review
- **Who:** claude
- **Did:** Correcting entry (WORKLOG is append-only): block labels are S118A = Food.com repair (worklog id S118), S118B = NER benchmark freeze (worklog id S119; its title mislabelled S118C), S118C = RecipeDB3 control (not complete). Worklog IDs are tool-sequential; 'S119 block' in the master prompt = backbone/CRF/KF experiments, starts only after S118C report. Canonical Food.com count: 410 proposed, 126 initially dropped, 284 written/by-design, 310 final v1.1 events (407 was wrong). Food.com v1.1 provenance = AI_REAUTHORED_SOURCE_GROUNDED + HUMAN_REVIEW_PENDING (Kush approval covered v1 only); coverage verdict H_STATE_COVERAGE_READY, H_STATE_GOLD_PROVENANCE_GATE not cleared until Kush reviews v1.1 and the S116 screen. A100: inspected job tree (no duplicate seeds), killed only the redundant 10:34 launcher shells (PIDs 2426075/2426076), 4 running jobs and 2 completed JSONs untouched; remaining seeds run from the 09:44 loops (theirs 3,4; clean 4,5).
- **Files:** `tools/repair_foodcom_gold.py`, `tests/test_foodcom_gold_repair.py`, `reports/gold/foodcom_ai_assisted_v1_to_v1_1.md`
- **Verified:** 3006 passed; v1.1 regenerated 20/20 DONE
- **Next:** S118C: wait for the 8 remaining control runs, run SIZE analysis, write reports/ner/recipedb3_matched_reproduction.md, stop and report; no S119 before that

### S121 · 2026-10-20 13:06 IST · DEL-3 · S118A format: Food.com v1.1 as ONE joint JSON (annotator JOINT)
- **Who:** claude
- **Did:** Per Kush: joint file from now on. Added JOINT to the gold-1.0 annotator enum; repair tool now writes foodcom_v1_1_joint.json (20 recipes, provenance block AI_REAUTHORED_SOURCE_GROUNDED / HUMAN_REVIEW_PENDING); removed the identical Kush/Parv per-recipe v1.1 copies; scorer, coverage tool and tests read the bundle. Results unchanged (310 events, 20/20 DONE, 15 recipes / 51 pairs / 37 cells). S117 files untouched.
- **Files:** `src/culinarystate/annotation/gold.py`, `tools/repair_foodcom_gold.py`, `tools/score_foodcom_repair.py`, `tools/hstate_coverage_foodcom.py`, `tests/test_foodcom_gold_repair.py`
- **Verified:** 3006 passed
- **Next:** S118C when A100 control finishes

### S122 · 2026-10-20 13:33 IST · DEL-3 · S118A Food.com v1.1 review ingested: AI_ASSISTED_HUMAN_REVIEWED (batch-level), provenance gate cleared
- **Who:** claude
- **Did:** Kush_Parv_foodcom_v1_1_joint_review.csv (474 rows: 258 ingredient, 157 step, 59 unknown) has no row-level decisions or remarks; Kush states he reviewed and approves v1.1, Parv approved (relayed). Recorded batch-level approval (reports/gold/foodcom_v1_1_review_record.json, sheet sha256 kept, sheet copy local), 0 events changed, joint bundle provenance updated to AI_ASSISTED_HUMAN_REVIEWED (batch-level, not independent). H_STATE_GOLD_PROVENANCE_GATE cleared at batch level; S116 eligibility screen still unconfirmed. Kush also shared the Aprilab metadata-fused NER strategy; its differences from the frozen benchmark v1 are logged for the S119 block.
- **Files:** `tools/repair_foodcom_gold.py`, `tests/test_foodcom_gold_repair.py`, `reports/gold/foodcom_ai_assisted_v1_to_v1_1.md`, `reports/gold/foodcom_v1_1_review_record.json`
- **Verified:** 3006 passed; 20/20 DONE
- **Next:** S118C when A100 control finishes

### S123 · 2026-10-20 16:14 IST · DEL-4 · S119 prep: execution plan, E0 trainer on frozen benchmark, TASTEset queue launched, laptop-side span/router/stats modules
- **Who:** claude
- **Did:** reports/ner/s119_execution_plan.md (A100 vs Mac split, rung ownership, gates, permissions needed: ModernBERT needs transformers>=4.48, gliner install, FoodBase). gpu/ner_bench/bench_train.py = E0 encoder(+CRF) on benchmark v1 splits (dev-only checkpoint, evaluate() metrics, CI, calibration/dev/test span predictions saved); smoke-tested; TASTEset queue (deberta-base+/-CRF, bert, roberta, v3-large+/-CRF, 5 seeds) running one job per GPU. Mac modules: ner/spans.py (n-gram candidates, train-only gazetteer, 5-fold cross-fit, B/I projection, metadata dropout), ner/router.py (cross-fitted calibrator, risk-control thresholds, ACCEPT/REVIEW/NOVEL/REJECT, paired bootstrap, Holm, promotion rule). 8 new tests.
- **Files:** `gpu/ner_bench/`, `src/culinarystate/ner/spans.py`, `src/culinarystate/ner/router.py`, `tests/test_ner_spans_router.py`, `reports/ner/s119_execution_plan.md`
- **Verified:** full suite passes
- **Next:** aggregate TASTEset E0; finish S118C report after SIZE runs; amendment A1

### S124 · 2026-10-20 17:24 IST · DEL-4 · S119 ladder: E0 TASTEset, DEV-only discipline, server chain, K4 prompt, linker grid, leakage audit, amendment A1
- **Who:** claude
- **Did:** TASTEset E0 (30 runs) done; model conclusions redone on DEV after a TEST-selection slip (CRF not significant on DEV; v3-large +0.0047 not significant). Design contract adopted (reports/ner/culinaryner_kf_design_contract.md). Built and tested: span candidates + cross-fitted features, calibrator/router/statistics, CRF span marginals, span head, gated/concat fusion, knowledge prompts K1-K4, contrastive linker (+0.035 Acc@1 over zero-shot e5), OOF mode, alias leakage audit (ledger ALLOWED), amendment A1. Automated server chain: lane A (wave2/3 -> DEV shortlist -> RecipeDB3 elimination -> OOF -> seeds), K4 lane, linker re-run with dev selection. No promotion yet; no TEST opened since E0.
- **Files:** `benchmark/ner/amendment_A1.json`, `reports/ner/culinaryner_kf_design_contract.md`, `reports/ner/alias_leakage_audit.md`, `gpu/ner_bench/`, `tools/aggregate_e0.py`, `tools/e1_e2_calibration.py`
- **Verified:** benchmark hash tests pass
- **Next:** when VPN returns: pull results, close S118C, wave-2 DEV shortlist, linker report

### S125 · 2026-10-21 00:25 IST · S119 · NER block: Lane S, backbone+linker freeze, OOF BGE export, E2 linker calibration
- **Who:** claude
- **Did:** Pulled lane S; rejected K-TS, RoBERTa-large, ING-format, reranker; DeBERTa-base+CRF kept, v3-large Pareto challenger; fixed linker_train f-string bug; BGE export for 911 FOOD surfaces; feature-by-feature calibration on TASTEset DEV: M6 promote, M1 promote (FOOD scope), M2/M5 inconclusive, M3/M4 reject; BGE vs E5 not distinguishable (n=61)
- **Files:** `reports/ner/linker_signal_calibration.md`, `reports/ner/span_backbone_and_linker_freeze.md`, `tools/e2_linker_calibration.py`, `gpu/ner_bench/linker_train.py`
- **Verified:** TEST untouched; 3 linker seeds give identical decisions
- **Next:** ledger alias leakage-gated test, rule agreement, fusion on promoted only

### S126 · 2026-10-21 01:03 IST · S119 · Cross-dataset calibration, ledger aliases, M7, fusion rejected
- **Who:** claude
- **Did:** RecipeDB3 confirmation of M1/M2/M5/M6: M1,M2 reverse, M6 neutral; G1/G2 ledger aliases and M7 rejected; tie-aware AURC fix; linker dev-NIL set found invalid; M6-only fusion rejected (-0.0027/-0.0028, 1/5 seeds); metadata frozen = [M6]
- **Files:** `reports/ner/metadata_calibration_crossdataset.md`, `reports/ner/fusion_decision.md`, `tools/e2_signal_calibration.py`
- **Verified:** TEST and CALIBRATION untouched; tie-aware metrics unit-checked by hand
- **Next:** linker data v2 (true dev NIL), final calibration of mainline, router on CALIBRATION

### S127 · 2026-10-21 01:40 IST · S119 · Evidence-closing: linker v2, calibrator choice, M6 analysis, router baselines, latency; router frozen
- **Who:** claude
- **Did:** linker_data_v2 (valid NIL), BGE=E5 Pareto, calibrator = logistic+isotonic on conf+M6, M6 = unseen-mention detector, router R6 label x unseen strata + REJECT, linker advisory only, latency table
- **Files:** `reports/ner/router_and_freeze.md`, `tools/router_eval.py`, `tools/linker_v2_eval.py`, `tools/calibrator_robustness.py`, `tools/m6_analysis.py`, `tools/build_linker_data.py`, `gpu/ner_bench/latency_bench.py`
- **Verified:** TEST untouched; thresholds on CALIBRATION only; NIL sets validated 0 overlap
- **Next:** user go-ahead: TEST once, external/unseen validation, A-N report

### S128 · 2026-10-21 01:55 IST · S119 · Final TEST (single run), challenger, A-N report, H6-C
- **Who:** claude
- **Did:** Frozen manifest committed first; TEST run once on TASTEset+RecipeDB3: router R6 ACCEPT err 2.13%/2.09%, coverage 0.59/0.72; v3-large challenger no TEST gain; BGE frozen linker; NOVEL advisory; H6-C
- **Files:** `reports/ner/culinaryner_kf_final_report.md`, `reports/ner/_final_test.json`, `reports/ner/test_freeze_manifest.json`, `tools/final_test_eval.py`, `tools/write_final_report.py`
- **Verified:** frozen thresholds matched S127 on both datasets; no post-TEST changes
- **Next:** no more model development; external-domain validation (future work)

### S129 · 2026-10-22 00:13 IST · ES-1.1 · EVD export implementing the frozen MP-1 contract (gate PASS)
- **Who:** claude
- **Did:** Built a non-destructive normalised EVD export (17,978 of 17,978 active rows; tier, verification, design strength, provenance class as separate fields; matrix_id, prior_state_id, explicit LOD/LOQ=null; deterministic delta/log_fold_change/log_retention only where defined), the reversible 11-pair duplicate-SVAR mapping, an independent validator, tests and the audit; ledgers byte-identical before/after; C1 ruling applied
- **Files:** `src/culinarystate/evidence/evd_export.py`, `tools/build_evd_export_v1.py`, `tools/validate_evd_export_v1.py`, `tools/write_es1_1_report.py`, `registry/svar_duplicate_mapping_v1.csv`, `registry/schemas/evd_export_v1.schema.json`, `tests/unit/test_evd_export.py`, `reports/es1/es1_1_audit.md`, `DECISIONS.md`
- **Verified:** validator PASS 9/9 gating checks; pytest tests/unit 575 passed + ledger integration test passed; export sha256 identical on two rebuilds
- **Next:** ES-1.2 source acquisition manifest and literature/data-source census (not started)

### S130 · 2026-10-22 00:49 IST · ES-1.2 · Source acquisition manifest and evidence-source census (research/planning only)
- **Who:** claude
- **Did:** Built the 64-source acquisition manifest with explicit licence verification levels, the 20-claim capability matrix, 30 literature query templates with Europe PMC metadata counts, the 16-row priority-cell source coverage, the 21-item H2 approval queue and the census report; reconciled current EVD origins (USDA 7,018, Bognar 7,090, Phenol-Explorer 3,870 / 125 papers); nothing acquired or ingested
- **Files:** `registry/data_source_acquisition_manifest.csv`, `registry/source_claim_capability_matrix.csv`, `registry/evidence_query_matrix_v1.csv`, `reports/h_state/es_1_2_priority_cell_source_coverage.csv`, `reports/h_state/es_1_2_h2_approval_queue.md`, `reports/h_state/es_1_2_source_census.md`, `docs/BACKLOG_NONBLOCKING.md`, `DECISIONS.md`
- **Verified:** tests/unit/test_es12_registries.py 5 passed; ES-1.1 export and ledgers untouched
- **Next:** STEP 10 / ES-1.3 pilot after review of the census and H2 decisions (not started)

### S131 · 2026-10-22 06:47 IST · STEP-07 · Condition and measurement normalization (automated gate PASS; human audit sub-gate pending)
- **Who:** claude
- **Did:** Built 10 controlled vocabularies, condition schema, deterministic normalizer (units, bases, retention types, censoring, methods), read-only coverage audit over 4,414 conditions / 17,978 EVD rows (0 invalid, ledgers unchanged), deterministic 100-condition human audit packet + protocol (kappa >= 0.8 pending), Step-06 source-note corrections, NER status correction
- **Files:** `src/culinarystate/evidence/condition_normalizer.py`, `registry/*_registry_v1.csv`, `registry/schemas/condition_value_v1.schema.json`, `tools/step07_*.py`, `tools/build_step07_registries.py`, `tests/unit/test_condition_normalizer.py`, `reports/step07/*`, `DECISIONS.md`
- **Verified:** pytest test_condition_normalizer 11 passed, test_es12_registries 5 passed; ledger sha256 unchanged
- **Next:** STEP 08 source lineage (not started); human condition audit pending

### S132 · 2026-10-22 07:41 IST · ES-1 · Step 07H normalizer hardening + packet v3
- **Who:** Kush
- **Did:** Raw parser/semantic/dialect layers; open-bound fix; calendar durations; hard vs plausibility bounds; first-class trajectories; uncertainty; strict schema; golden/property tests; regression 0 unexplained; frozen; packet v3 built. Human gate pending.
- **Files:** `src/culinarystate/evidence/condition_*.py`, `source_dialect.py`, `registry/*bounds*`, `*dialect*`, `reports/step07/step07h_*`
- **Verified:** gate 10/10 PASS; combined hash a5991a9cda56; freeze commit 4e7db13
- **Next:** Kush+Parv blind review of packet v3, then tools/step07_agreement.py; Step 08 NOT authorised

### S133 · 2026-10-22 09:13 IST · ES-1 · STEP 07H-R full recipe-base consolidation + ledger sync + parser freeze
- **Who:** Kush
- **Did:** 612,782 indexed recipes (89,565 REC ids + 522,517 Food.com + 700 TASTEset), 8.17M expressions via final parser, derived recipe ledgers, DATASET rows, sync matrix, Gold index (40 GOLD_PENDING), gate 7/7, deterministic x2, frozen, packet v4. Human gate pending; Step 08 NOT started.
- **Files:** `src/culinarystate/recipes/*`, `tools/build_recipe_base.py`, `tools/step07hr_*.py`, `registry/recipe_*`, `ledgers/recipe_*`, `reports/step07/step07h*`
- **Verified:** 450 tests pass; 4414 regression 0 unexplained; 2 rebuilds byte-identical; freeze fingerprint e7d58913
- **Next:** Kush+Parv blind review of packet v4 -> tools/step07_agreement.py; Step 08 only after the gate

### S134 · 2026-10-22 16:22 IST · ES-1 · STEP 07I-R recovery + MAX-plan consensus + memory-safe recipe identity
- **Who:** Kush+Claude
- **Did:** Plan authority map + MAX consensus (no SSOT conflict); stalled-run diagnosis (likely memory pressure/swap thrashing, not proven OOM); feature file COMPLETE_REUSABLE; identity redesigned as phased resumable pipeline (exact/candidates/features/score/family) with atomic partitions, manifest and memory guard; full run: 612,782 recipes -> 611,714 exact reps, 8,639,518 candidate pairs scored in 187 s at 1.9 GB peak, 744,615 kept, 6,589 provisional edges, 605,476 families, 46,697 dish candidates; identical hashes on rerun and after SIGKILL; consensus FK moved to recipe_identity_fk_v1 (frozen base untouched); 400-pair blind packet unlabeled
- **Files:** `src/culinarystate/identity/*`, `tools/step07i_*.py`, `tests/unit/test_identity_pipeline.py`, `reports/step07i/*`, `registry/plan_authority_map_v1.csv`, `ledgers/recipe_identity/run_manifests/*`
- **Verified:** 11 identity tests + 3482 suite tests pass (1 pre-existing unrelated hang in test_transition deselected); sample output bit-identical to old script; final_hash 963466d8f207
- **Next:** Kush+Parv blind review of duplicate packet v1 and condition packet v4; Step 08 NOT authorised

### S135 · 2026-10-22 · Usage decision D-026 and master-plan audit intake
Recorded D-026 (owner decision: all 612,782 recipes usable for project use; overlay registry, frozen files untouched). Received the untracked master-plan research audit from manjot-server (reports/master_plan/, registry/master_plan_confidence_v2.csv): DRAFT, critique round skipped; staged outside the repo, not adopted. Step 08 still not started; condition gate still PENDING_HUMAN_REVIEW.

### S136 · 2026-10-22 · Adapted Master Plan v2 and SSOT v16 change set (DRAFTS)
Wrote `docs/plan/CulinaryState_Master_Plan_v2_ADAPTED_DRAFT.md` and `docs/SSOT/ssot_v16_change_set_DRAFT.md` from the master-plan audit (DRAFT, critique round skipped) plus the Claude and ChatGPT verdicts. Nothing adopted: SSOT v15 and Master Plan v4.0 untouched; all 65 CRs PROPOSED_ONLY. Audit raw files stay outside the repo. Needs human D-027 (07-DEP, Step 03/04 base, 04.L/04.K) before Step 08.

### S137 · 2026-10-23 · Step-07 provenance precheck tool and unsigned planning drafts
Added `tools/step07_provenance_precheck.py` + `tests/unit/test_step07_provenance_precheck.py` (6 tests, 8 passing with the agreement tests): read-only validity precheck for the two returned v4 files; the gate and `step07_agreement.py` are unchanged. Drafted (UNSIGNED, not in force): D-027 authority rulings, 07.A amendment v4.1, `registry/preregistered_thresholds_v1_DRAFT.csv`, next-steps runbook. Packet v4 untouched; STEP 08 NOT STARTED.

### S138 · 2026-10-26 12:45 IST · ES-1 · Execution Plan v2 reconciliation (original 36-step spine + selected Audit-v2 amendments; D-027) [merged from server branch plan/v2-reconciliation; renumbered from S135-S138]
- **Who:** Kush+Claude
- **Did:** Recorded Kush's rulings R-01..R-20 as D-027; four-way reconciliation (original spine titles / SSOT v15 / Final Master Plan v4.0 / Audit v2); wrote Definitive 36-Step Execution Plan v2 with per-step contracts, change log (139 CHG rows), artifact DAG, critical path, parallel lanes, human gates, cross-phase conflict register; Step-07 gate unchanged (pooled kappa>=0.80 AND no systematic critical-field failure); 07-DEP soft for 08 / hard for 15,23,26d-27,29-33; 08 split 08a/08b. Original 36-step card text not on this server (titles only).
- **Files:** `docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`, `docs/plan/CulinaryState_36_Step_Execution_Plan_v2_changelog.md`, `registry/execution_spine_v2.csv`, `reports/master_plan/*`, `registry/master_plan_confidence_v2.csv`, `DECISIONS.md`
- **Verified:** 36 top-level steps present; STEPDATA parsed (102 entries); two-persona review pending at time of logging
- **Next:** Step 04 v1.1 contracts (04.1 lineage, 04.3 kinetic) + 01.6 thresholds + 02.4 negative-results register; then 08a only after Kush authorises; Step 08 NOT started

### S139 · 2026-10-26 13:26 IST · ES-1 · Plan v2 two-persona review applied (corrects S138 counts)
- **Who:** Kush+Claude
- **Did:** Governance & Laws review (29 issues: 3 blocker) and Methods & DAG review (30 issues: 4 blocker) applied: 36 applied / 23 adapted / 0 rejected. Spine CSV normalised (0 unknown dependency tokens, 0 hard or soft cycles, topological order 123/123). Added review substeps marked needs-human-approval: 15a.R reserved-group seal, 08b-v0, 26g recipe-event to simulation adapter + link table + simulability census, 16a event-modifier/history fields, 35e similarity schema, 4.5 capacity table. Section 7 limited to contract/doc work; 07.A labelling only after 01.6 rows + pre-label decision. Corrects S138: 154 CHG rows (not 139), 123 STEPDATA rows (not 102).
- **Files:** `docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`, `docs/plan/CulinaryState_36_Step_Execution_Plan_v2_changelog.md`, `registry/execution_spine_v2.csv`, `DECISIONS.md`
- **Verified:** dagcheck: 0 unknown tokens, no cycles; 36 STEP headings; 4 STEPDATA blocks parse; changelog CHG rows identical to plan
- **Next:** Step 04 v1.1 contracts (04.1 lineage + JSON schema drafts DOC/LIN/SEXP/SMP/OBS/AGG/DRV, 04.3 kinetic/trajectory), 04.2-min/04.6-min/04.9-min, 01.6 thresholds (PROPOSED_PILOT), 02.4 negative-results register, v3 agreement archive; Step 08 NOT started

### S140 · 2026-10-26 15:11 IST · ES-1 · Step 04 v1.1 DRAFT contracts (04.1 lineage, 04.3 kinetic/trajectory, 04.2/04.6/04.9-min) + 01.6 thresholds + 02.4 negative-results register + 02.R-min + v3 archive (D-027 contract/doc work; DRAFT_PENDING_H4)
- **Who:** Kush+Claude
- **Did:** Drafted lineage contract SRC->DOC->STUDY->SEXP->SMP->OBS->AGG/DRV with typed LIN edges, study_id/lineage_root_id/split_group_id (SPLITGRP-EVD-/SPLITGRP-REC-), compilation-hub rule, UNKNOWN-independence leakage screen; kinetic/trajectory contract (KIN/KINPT: raw time units kept, temperature profiles with clock tags, C0/value scale, companion series, lab_group_id); 9 JSON Schema drafts in registry/schemas/*draft*; 47-row preregistered_thresholds_v1.csv (Step-07 gate rows verbatim and unsigned; all others PROPOSED_PILOT unsigned); 30-row negative_results_register_v1.csv (agent-checked); 08a input classification; byte-identical archive of the v3 NOT_COUNTED gate result. Two-persona review (governance 28 findings, science 32 findings) applied: 43 applied / 17 adapted / 0 rejected. Nothing approved, signed or frozen; no ledger, data, tool, packet or existing schema touched.
- **Files:** `reports/step04/*`, `registry/schemas/*draft*`, `registry/preregistered_thresholds_v1.csv`, `registry/negative_results_register_v1.csv`, `reports/step02/r_min_08a_input_classification.md`, `reports/step07/v3_not_counted_archive/*`
- **Verified:** 9 schemas parse, no default keyword; stdlib contract shim 220 cases pass; sanity 48 checks OK; archive sha256 b1c856ba... matches; git diff on tracked files empty
- **Next:** Human: H4 review of reports/step04/README.md checklist, sign 01.6 rows, pre-label decision then 07.A and 07I-C labelling; agent: Step 21 mechanism schema draft, 19-D pilot design, 35.0 pre-registration draft; Step 08 NOT started

### S141 · 2026-10-26 16:23 IST · ES-1 · Round 3 DRAFTS (Step 21 mechanism ontology, 19-D Deep Gold pilot design, 35.0 pre-registration) + reviews; anchor for usage-limit stop
- **Who:** Kush+Claude
- **Did:** Drafted Step 21 MECH ontology/schema/vocab (R-15 property-tested), 19-D pilot design (20 recipes, blind, hash-committed, 40 h cap), 35.0 explicit-first pre-registration (nine notions, 35g deferred). Two-persona reviews written (governance 39 findings, science 43). Fix pass interrupted: step19/35 partially revised, step21 and K-1 jsonschema corrections pending. Resume file reports/master_plan/RESUME_ANCHOR_2026-10-26.md.
- **Files:** `reports/step19/*`, `reports/step21/*`, `reports/step35/*`, `registry/schemas/MECH.draft_v1.schema.json`, `registry/*_draft_v1.csv`, `reports/master_plan/review_queue/*`, `reports/master_plan/RESUME_ANCHOR_2026-10-26.md`
- **Verified:** Step-21 contract test 21/21 before review; reviews pending application; git diff on tracked files empty
- **Next:** Re-run round-3 fixer over both reviews; then pause for human gates (H4, 01.6 signatures, 07.A, 07I-C, H2, 08a authorisation); Step 08 NOT started

### S142 · 2026-10-26 · ES-1 · Merge of server branch plan/v2-reconciliation, Step 21 round-3 fixes, repo housekeeping
- **Who:** Kush + Claude (operator/reviewer); Max (server) wrote S138-S141
- **Did:** Merged `origin/max/plan-v2-reconciliation` into main (e679bdf); server S135-S138 renumbered S138-S141; D-027 kept as Execution Plan v2 rulings; Mac residual-rulings draft renamed D-028 (items superseded by D-027 marked); runbook ids aligned with `execution_spine_v2.csv`; STATUS.md refreshed; NER dumps triaged (3 ignored, small results and dm_raw committed); Step 21 round-3 review items fixed by a separate agent, then re-run independently
- **Files:** `DECISIONS.md`, `WORKLOG.md`, `STATUS.md`, `docs/plan/D-028_DRAFT_residual_rulings.md`, `docs/plan/NEXT_STEPS_RUNBOOK_DRAFT.md`, `reports/step21/*` (+ `FIX_LOG_round3.md`), `registry/schemas/MECH.draft_v1.schema.json`, three Step-21 registry CSVs, `reports/step04/*`, `reports/step02/*`, `.gitignore`
- **Verified:** merge dry-run conflicted only in DECISIONS.md and WORKLOG.md; Step 21 contract test 22 passed (87 negative controls, 23 accepted variants) when extracted from `reports/step21/README.md` and run with `/opt/anaconda3/bin/python` (jsonschema 4.19.2); all schema JSON parses; no secrets in the server diff
- **Open:** Step 21 OPEN_QUESTION chemistry items (DHA step, chlorophyllase pathway, SBO promoter id, analyte-form token list) need a domain check; Step 19/35 items B 35-3, 35-4, 35-9, 19-5 not re-checked; all human gates unchanged (D-028 items 4-5, thresholds signing, 07.A and 07I-C blind labelling, 08a written authorisation, H2 licences); Step 08 NOT authorised; nothing pushed to GitHub (H7)
- **Next:** Kush signs D-027/D-028/thresholds and decides how to run the two-person labelling passes with Parv away; then Step 08a on the Mac

### S143 · 2026-10-27 · ES-1 · H4 walk-through, Step 08a authorised, 07.A and 07I-C audits returned
- **Who:** Kush + Claude (scribe/operator); Parv (labels for 07.A and 07I-C)
- **Did:** Kush answered the Step 04 H4 checklist (`docs/plan/H4_ANSWERS_LOG.md`) and signed THR-08A-01..23, THR-07A-01..08, THR-07IC-01..09; DECISIONS D-029..D-032 (+ addendum); baseline hashes of the seven 08a ledgers; first 08a work package (lineage guard, union-find, Wilson, 34 tests); 07.A packet v4: both reviewers returned, precheck VALID, agreement run, 5 disputes adjudicated, outcome FAIL_REVIEWER_DISAGREEMENT on the signed statistic; 07I-C: both returned, kappa 0.571 / 0.588 vs 0.70, reported as target not met; 08a.0 preregistration written
- **Files:** `DECISIONS.md`, `registry/preregistered_thresholds_v1.csv`, `registry/baseline_ledger_hashes_08a_v1.csv`, `src/culinarystate/lineage/*`, `tools/step07ic_agreement.py`, `reports/step07/step07_v4_*`, `reports/step07i/step07ic_reviewer_agreement_v1.json`, `reports/step08/step08_preregistration_v1.md`
- **Verified:** 34 lineage tests + 7 07I-C tests pass; 7 ledger hashes unchanged; precheck VALID; no label was edited by the agent
- **Open:** 07.A statistical gate not met (hard gates for Steps 15, 23, 26d/27, 29-33 stay closed); Parv's confirmations (amendment signature, "go with Kush's") are relayed, unverified; 07I-C operating points cannot be chosen on these labels; 08a work packages 08a.1-08a.9 not built; edge audit and 200-pair recall review need two people
- **Next:** build 08a.1-08a.3 on a scratch copy, show Kush the dry-run counts before the real run

### S144 · 2026-10-27 15:37 IST · ES-1 · Step 08a built (08a.1-08a.9) and real run applied
- **Who:** Kush+Claude
- **Did:** Added --scratch-root to edge/keys/feasibility tools; built 08a.9 gate report + two-rebuild check (G08-6 pass, 0 diffs); real run published scratch rebuild: new DOC.jsonl (1967), SRC_08A_YIELD.jsonl, STUDY +125 versions +7 studies, _ids append. Gates: G08-1,2,4,5,6,8,10 PASS; G08-7 label forced publication-component CV, weakest leave-one-source-family-out; G08-9 recorded; G08-3 and G08-H PENDING_HUMAN. Keys marked SCRATCH_PROVISIONAL.
- **Files:** `tools/step08a_gate.py`, `tools/step08a_publish.py`, `src/culinarystate/lineage/gates.py`, `src/culinarystate/lineage/publish.py`, `exports/lineage/step08a_v1/*`, `ledgers/data/{DOC`, `SRC_08A_YIELD`, `STUDY`, `_ids}.jsonl`
- **Verified:** 233+4 lineage tests pass; EVD/COND/SRC/MEAS/SNAP hashes equal baseline; ledgers equal scratch rebuild
- **Next:** Edge audit packets (Kush+Parv), 200-pair recall review, expert reading of USDA-Bognar; push only on Kush go

### S145 · 2026-10-27 20:50 IST · ES-1 · 08a edge audit scored, G08-3 FAIL recorded, B3 cut kept (D-033, D-034)
- **Who:** Kush+Claude
- **Did:** Kush+Parv returned edge-audit (150) and unlinked-pair (200) files; code synonyms mapped by scribe (originals untouched); Parv rechecked. G08-3 FAIL (B3 13/50 Kush, 0/50 Parv; B2 49/50 vs 0/50 with 49 UNCERTAIN; STRONG 50/50 both). Recall report: Kush 2/200, Parv 0/200. D-033: 07I-C 0.88 recorded as Kush-stated adjudicated figure. D-034: B3 cut stays 0.75, no gate loosened.
- **Files:** `tools/step08a_audit_packets.py`, `tools/step08a_score_audit.py`, `reports/step08/step08a_audit_result_v1.json`, `reports/step08/step08a_audit_result_v2.json`, `DECISIONS.md`
- **Verified:** provenance VALID after mapping; sealed keys read only by the scorer
- **Next:** Step 08a closes with G08-3 FAIL disclosed; Step 35.0 sign-off (cuisine = source confound, Food.com has no cuisine labels); Step 16 schema; A100 for 17/20 after VPN confirmation

### S146 · 2026-10-28 18:24 IST · ES-1 · Step 35e typed similarity registry and lint built (synthetic fixtures only)
- **Who:** Parv+Claude
- **Did:** Built the 35e row schema (draft 8.1; nine notions, six statuses), registry lint (8.4: notion mixing, fusion, PROMOTED without decision, same own target for two notions, 8.2b split sharing, Open Babel never SIM-06) and column lint (one notion per sim/score column); tests first; no real registry rows (sim_id scheme H4, D35-12)
- **Files:** `src/culinarystate/representation/similarity_registry.py`, `tests/unit/test_representation_similarity_registry.py`, `reports/step35/35e_similarity_registry_build_note.md`
- **Verified:** 20 new tests pass; tests/unit 1510 passed, 1 skipped, test_transition deselected; no real data opened
- **Next:** Kush: rule on the six conventions and open points in the build note; 35.0 sign-off D2-D8 continues

### S147 · 2026-10-28 21:54 IST · ES-1 · Takeover recheck, unsigned review workspace and Step 16 technical review
- **Who:** Parv
- **Did:** Reproduced and fixed duplicate CSV headers silently overwriting similarity registry fields, tests first on synthetic fixtures; aligned guard documentation; preserved D1 as an unsigned review choice with D2-D8 pending (D5 reserved to Kush); prepared unsigned draft hash template and confirmed guard refusal; reviewed Step 16 schemas, vocabularies and hierarchy structure without changing human labels or schema semantics.
- **Files:** `tests/unit/test_representation_similarity_registry.py`, `src/culinarystate/representation/similarity_registry.py`, `reports/step35/35e_similarity_registry_build_note.md`, `reports/step35/g35_pre_guard_README.md`, `reports/step35/35_0_parv_review_DRAFT.md`, `reports/step35/preregistration_35_0_v1_draft.sha256.UNSIGNED.json`, `reports/step16/parv_review_comments.md`, `handoff/PARV_SESSION_NOTES.md`
- **Verified:** Two regression cases failed before the fix; targeted suite 147 passed; final unit suite 1512 passed, 1 skipped, 8 deselected (test_transition). EVD/COND/SRC/MEAS/SNAP full baseline hashes match; STUDY/_ids baseline prefixes match. Hierarchies have no missing parents or cycles. Text-strata D-038 hash matches. No real Step 35 evaluations.
- **Next:** Parv answers the batched review questions; apply explicit rulings and record draft pilot-column choice for Kush. Kush resolves 35e conventions, Step 16 family-ID/metadata/AST semantics, toolkit and licence decisions, and signature/override. No push.

### S148 · 2026-10-28 21:56 IST · ES-1 · Record batch review answers and prepare approved local RDKit toolkit
- **Who:** Parv
- **Did:** Recorded D-039 and D2/D3/D4/D6/D7/D8 review answers without inferring missing mappings, reviewer names, audit ownership or signatures. Parv explicitly instructed D5 go without waiting; found RDKit already installed and pinned distribution 2026.3.6 as optional step35 extra. Kept protocol draft bytes and unsigned record unchanged.
- **Files:** `DECISIONS.md`, `pyproject.toml`, `reports/step35/35_0_parv_review_DRAFT.md`, `reports/step35/parv_toolkit_environment_2026-10-28.md`, `handoff/PARV_SESSION_NOTES.md`
- **Verified:** Synthetic Morgan 2048-bit chiral radius-2 fingerprint and Murcko scaffold checks passed. TOML parses and pin matches installed version. Guard/registry tests: 43 passed. Protocol hash still matches; signers and date empty. Prior full suite S147: 1512 passed, 1 skipped, 8 deselected. No installation, real evaluation or ledger changes.
- **Next:** Parv supplies remaining cuisine rulings, reviewer names, audit owner, pilot column and own adjudication statement; these were requested together. Protocol signatures and Kush-only H2 decisions remain pending; no push.

### S149 · 2026-10-28 22:05 IST · ES-1 · Apply D040 single-reviewer cuisine rulings and draft pilot-column choice
- **Who:** Parv
- **Did:** Applied exactly 15 explicit Parv lookup choices with PARV_REVIEW_D040 provenance; extended draft REGION definition to below-country terms; retained reviewed ambiguous terms as UNKNOWN. Regenerated aggregate local tag map, all statuses unsigned. Recorded conflict exclusion/counting policy, v2 pilot preference pending Kush, Parv crosswalk audit ownership not completion, pending chemistry/cuisine reviewers and pending own adjudication statement/Step16 comments. No raw text exported, no real Step35 scoring or sample draw.
- **Files:** `tests/unit/test_step35_cuisine_census.py`, `registry/cuisine/cuisine_lookup_v1_DRAFT.csv`, `registry/cuisine/foodcom_tag_cuisine_map_v1_DRAFT.csv`, `reports/step35/foodcom_cuisine_derivation_README.md`, `reports/step16/16b_text_strata_README.md`, `reports/step35/35_0_parv_review_DRAFT.md`, `reports/step35/35_0_signoff_sheet_DRAFT.md`, `DECISIONS.md`, `handoff/PARV_SESSION_NOTES.md`
- **Verified:** Cuisine census tests 9 passed; full unit suite 1512 passed, 1 skipped, 8 deselected (test_transition). Exactly 15 lookup rows changed; tag counts and unsigned statuses unchanged. Cuisine coverage 67216/522517 and conflicts 2643 unchanged; continent coverage 123812/522517, conflicts 3386. Existing synthetic corpus test verifies CONFLICTING exclusions counted. Protocol hash/template unsigned unchanged; D038 strata hash and protected ledger baseline checks pass.
- **Next:** Kush/expert review expanded REGION and lookup; confirm draft pilot v2; humans complete protocol/mapping signatures. Kush arranges chemistry reviewer; cuisine expert pending. Parv performs crosswalk audit and supplies own adjudication statement/Step16 review. No push.

### S150 · 2026-10-28 22:32 IST · ES-1 · AI scientific precheck, provenance audit, consistency fixes and project roadmap
- **Who:** Parv
- **Did:** D041: completed scoped AI review of Steps16/35 and project completion blockers. Source-backed all204 deprecated ChemTastesDB edges as free-text-to-class migration; reconstructed307 compound-linked crosswalks covering298 ING and isolated one collision. Built ignored50-row human worksheet and supplemental priority sheet, verdicts blank and overwrite-protected. Tests-first fixes for invalid ranking/mass/profile/NPMI inputs; draft FAM family schema correction; pure semantic review overlay. Added optional companion hash binding and required-file guard checks; new package unsigned. Proposed molecule-level negative evidence and triplet-statistic amendments for expert review without changing old protocol or thresholds. Refreshed stale status and supplied36-step roadmap.
- **Files:** `DECISIONS.md`, `STATUS.md`, `reports/review/AI_REVIEW_2026-10-28.md`, `reports/review/machine_evidence.json`, `reports/review/protocol_review_addendum_DRAFT.md`, `reports/review/project_completion_roadmap.md`, `tools/review_takeover.py`, `src/culinarystate/annotation/schema_review.py`, `src/culinarystate/representation/recipe_rungs.py`, `src/culinarystate/representation/cuisine_rungs.py`, `src/culinarystate/representation/prereg_guard.py`, `reports/step16/schema_drafts/EVT.draft_v1.schema.json`, `tests/unit/test_schema_semantic_review.py`, `tests/unit/test_takeover_review_audit.py`, `tests/unit/test_representation_recipe_rungs.py`, `tests/unit/test_representation_cuisine_rungs.py`, `tests/unit/test_representation_prereg_guard.py`, `tests/unit/test_step16a_schema_drafts.py`, `reports/step35/preregistration_35_0_review_package.sha256.UNSIGNED.json`, `reports/step35/g35_pre_guard_README.md`, `reports/step35/35c_recipe_rungs_build_note.md`, `reports/step35/35d_cuisine_rungs_build_note.md`, `reports/step16/16a_batch1_README.md`, `reports/step16/16a_batch2_README.md`, `reports/step16/parv_review_comments.md`, `handoff/PARV_SESSION_NOTES.md`
- **Verified:** Full unit suite1562 passed,1 skipped,1 deselected in76.89s with OMP_NUM_THREADS/OPENBLAS_NUM_THREADS/MKL_NUM_THREADS=1; transition tests included, existing not-ledgers marker policy retained.43 additional synthetic controls; targeted failures reproduced before fixes. Audit rerun byte-identical; input hashes valid; source XLSX MD5 matches published Zenodo file. Seven ledger baseline checks pass (STUDY/_ids prefix), frozen schema hashes pass. Thresholds, cuisine lookup, strata/frame and original protocol untouched; both package records unsigned and hashes match. git diff --check clean.
- **Next:** Experts verify migration meaning, negative-evidence correction, cuisine scope, crosswalk collision and triplet statistic; humans complete crosswalk/07A-07IC statement and Step16 review. Integrate accepted changes and sign a final bound protocol; H5 pilot then16c. Follow roadmap without weakening G08-3/07A or bypassing licences/signatures; no push.

### S151 · 2026-10-28 23:04 IST · ES-1 · Step16 rc2 metadata and typed quantity AST contract, synthetic only
- **Who:** Parv
- **Did:** D042: implemented separate QNT/STATE rc2 proposal schemas with exact per-claim metadata, typed payloads for all11 AST nodes and combined structural/semantic/arithmetic validation. Added exact fraction/interval/package/remainder arithmetic, alternatives preserved and exact JSON-safe results with provenance retained. No metadata backfill, unit conversion, density/default grams, source verification or ledger migration. Existing review overlay gains opt-in JSON Pointer paths while preserving default behavior. Wrote seven synthetic demonstrations and H4 contract choices. Recorded legacy zero-multiplier normaliser bug without changing frozen path.
- **Files:** `tests/unit/test_step16_quantity_contract.py`, `src/culinarystate/quantity/draft_contract.py`, `src/culinarystate/annotation/schema_review.py`, `reports/step16/schema_drafts/QNT.draft_v2.schema.json`, `reports/step16/schema_drafts/STATE.draft_v2.schema.json`, `reports/step16/quantity_contract_synthetic_examples.json`, `reports/step16/metadata_quantity_contract_v2_DRAFT.md`, `reports/step16/parv_review_comments.md`, `reports/review/project_completion_roadmap.md`, `DECISIONS.md`, `STATUS.md`, `handoff/PARV_SESSION_NOTES.md`
- **Verified:** 54 new synthetic cases pass, tests first; full unit suite1616 passed,1 skipped,1 deselected in76.69s with CPU thread caps, transition tests included and existing not-ledgers marker retained. Both rc2 schemas regenerate identically; seven examples reproduce. All ten rc1 draft files unchanged; frozen schema tests and protected ledger baseline/prefix checks pass. Original Step35 protocol and unsigned package hashes valid; thresholds/cuisine/strata untouched; git diff --check clean.
- **Next:** H4 reviews metadata scope/payload/arithmetic/wire conventions; Step19 human pilot then16c. Build explicit parsing/grounding integration and versioned legacy zero-multiplier fix before new extraction. Source/POR verification and history policy remain open; no real recipes, pilot draw, signatures, expert approvals, GPU work or push.

### S152 · 2026-10-29 14:51 IST · ES-1 · Engineering bridge, delegated AI review fixes and synthetic pilot preparation
- **Who:** Parv
- **Did:** D043: separate v2 normaliser corrects zero multiplier and masks malformed/overflow inputs; conservative parse-to-rc2 AST bridge retains raw/exact supported quantities and flags unsupported expressions/precision limits. Three delegated AI reviews recorded original evidence, recommendations and independently reverified code fixes. Added six-stage fixture-only pilot rehearsal, draft handbook,17 synthetic hard cases and unsigned bound pilot-start record. Real pilot nonce/capacity/budget facts requested; no signatures, labels or actual draw. Additional chemistry/cuisine review attempts hit usage limits and are not reported complete. D044 separately authorises publishing on new branch.
- **Files:** `src/culinarystate/quantity/versioned_normalizer.py`, `src/culinarystate/quantity/parse_adapter.py`, `src/culinarystate/quantity/draft_contract.py`, `src/culinarystate/annotation/schema_review.py`, `src/culinarystate/annotation/pilot_rehearsal.py`, `tests/unit/test_step16_quantity_contract.py`, `tests/unit/test_quantity_v2_pipeline.py`, `tests/unit/test_step19_pilot_rehearsal.py`, `tools/step19_pilot_rehearsal.py`, `reports/step16/schema_drafts/QNT.draft_v2.schema.json`, `reports/step16/schema_drafts/STATE.draft_v2.schema.json`, `reports/step16/rc2_independent_agent_review.md`, `reports/step16/engineering_and_pilot_lane_build_note.md`, `reports/step16/metadata_quantity_contract_v2_DRAFT.md`, `reports/step19/pilot_methods_agent_review.md`, `reports/step19/pilot_readiness_and_ai_review.md`, `reports/step19/pilot_start_record.UNSIGNED.json`, `reports/step19/README.md`, `reports/step19/synthetic_rehearsal/SYNTHETIC-rehearsal-v1.json`, `annotation/annotation_handbook_v2_DRAFT.md`, `annotation/hard_case_catalog_v2_DRAFT.jsonl`, `DECISIONS.md`, `STATUS.md`, `reports/review/project_completion_roadmap.md`, `handoff/PARV_SESSION_NOTES.md`
- **Verified:** Full unit suite1681 passed,1 skipped,1 deselected in76.47s with CPU thread caps, transition tests included.132 targeted controls pass. Agent independently verified code fixes and synthetic extrema. Six planted rehearsal failures detected; fixture report reproduces;17 catalog entries have no expert/human outcomes. Legacy grammar/normaliser/units and protected ledger baseline/prefix checks unchanged; pilot and Step35 records unsigned/hash-valid;35 pilot threshold rows unsigned and not written to registry; git diff --check clean.
- **Next:** Publish requested branch without updating main. Later finish approved real-pilot tooling/method choices, obtain actual pre-frame nonce/capacity/signatures and independent human annotations; retain v0 measurement boundary unless explicitly amended. Step35 domain reviews remain open after agent service limit; no false human/expert gate passage.

### S153 · 2026-10-29 17:45 IST · ES-1 · Publish requested takeover branch in Kush repository
- **Who:** Parv
- **Did:** D044: created parv/engineering-pilot-prep-2026-10-29 and pushed95 local takeover commits to kushiiitd05/culinarystate, including recorded engineering/pilot work. Added no PR, merge or force push. This entry records the independently verified first publication; publication notes are committed separately and pushed on the same branch.
- **Files:** `WORKLOG.md`, `handoff/PARV_SESSION_NOTES.md`
- **Verified:** git push reported new remote branch; git ls-remote confirmed branch d5b983acffb1876bf4afb01ba28fdf78415605dd equals local HEAD and remote main remains c5d72881af381ca5764faf7aad78734c42d24b08. Clean tree. Outbound diff61 files, largest156324 bytes; no raw data/features/ledger-data archives included. Latest unit result1681 passed,1 skipped,1 deselected.
- **Next:** Branch ready for Kush review. Real pilot still requires actual pre-frame nonce, capacity/budget and signatures/independent human annotations; no AI review substitutes for those facts.

### S154 · 2026-11-03 19:18 IST · ES-1 · Step16 opt-in rc2 grounding pipeline, history check, counts-only dry-run; Step19 real-pilot gate
- **Who:** Kush (cloud agent session)
- **Did:** Tests first on synthetic fixtures. Wired parse_adapter + versioned_normalizer into explicit opt-in rc2 grounding (parse, unit resolution with caller locale else AMBIGUOUS, exact Q0, POR hard filters over HUMAN_VERIFIED records only, rc2 record + invented-value audit). Added rc2 history-variable check (inline+sidecar, source-text origin rejected, external history and origin/route mismatches PENDING_H4). Added read-only counts-only dry-run CLI with ledger baseline check before/after and no-text guard. Added Step19 real-pilot gate: check lists every missing human prerequisite with owner; P1 draw refuses without signatures of both annotators, H5, Kush nonce+commitment, capacity, B_h, signed THR-19P rows, instrument, pilot column, method ruling and bound draw spec; P2 refused. Data bundle unavailable (Drive host denied by network policy): real-data dry-run NOT run. No decision, signature, label or nonce supplied; no existing file modified.
- **Files:** `src/culinarystate/quantity/rc2_history.py`, `src/culinarystate/quantity/rc2_grounding.py`, `src/culinarystate/quantity/rc2_dryrun.py`, `tools/step16_rc2_grounding_dryrun.py`, `src/culinarystate/annotation/pilot_real.py`, `tools/step19_real_pilot.py`, `tests/unit/test_step16_rc2_history.py`, `tests/unit/test_step16_rc2_grounding.py`, `tests/unit/test_step16_rc2_dryrun.py`, `tests/unit/test_step19_real_pilot.py`, `reports/step16/S154_build_note.md`, `STATUS.md`
- **Verified:** 144 new tests pass (history 18, grounding 78 incl. hypothesis property, dry-run 16, pilot 32). Full unit suite with CPU thread caps: 1797 passed, 17 skipped, 1 deselected; 1 failed + 11 errors are missing bundle files, identical to pre-change baseline 1653 passed. Protected ledger baseline 7/7 match; 0 existing files modified; git diff --check clean. Real start record read-only: 10 blockers, design/bound hashes match. Python 3.13 container, not the Mac env.
- **Next:** Kush: run tools/step16_rc2_grounding_dryrun.py --workers 8 locally with data and review counts; rerun unit suite on the Mac. Humans: H4 on rc2/history/grounding choices listed in S154 build note; supply Step19 blockers (nonce before frame rebuild, H5, both signatures, capacity, B_h, THR-19P, instrument, pilot column, methods ruling). G08-3 and 07.A FAIL unchanged.

### S155 · 2026-11-03 20:13 IST · ES-1 · Step17a interfaces/validators/auditor and 17b Rung A baseline (DRAFT_PENDING_16c); D-045/D-046 recorded
- **Who:** Kush (cloud agent session; workers ksh/prv)
- **Did:** ksh built 17a (six-stage interface, V1-V4, invented-value auditor); prv built 17b deterministic Rung A, counts-only synthetic measurement and seeded 1,000-recipe real dry-run CLI, and AI cross-reviewed 17a (R1-R7 fixed test-first, O1-O9 open). Coordinator verified. Recorded Kush's D-045 workflow and D-046 acceptance of review blocks W/A/B/C; signed THR-19P-01..35 by append only. Real-data dry-runs not run (data bundle absent).
- **Files:** `src/culinarystate/extraction/*`, `tools/step17b_rung_a_dryrun.py`, `tools/step17b_rung_a_synthetic_report.py`, `reports/step17/*`, `tests/unit/test_step17a_*.py`, `tests/unit/test_step17b_*.py`, `DECISIONS.md`, `registry/preregistered_thresholds_v1.csv`, `handoff/REVIEW_SHEET_AI_VERDICTS.md`, `STATUS.md`
- **Verified:** Full unit suite 2000 passed, 17 skipped, 1 deselected; 1 failed + 11 errors = missing bundle files (unchanged). invented_count 0 on synthetic fixtures and hard cases (SYNTHETIC_NOT_GOLD). Ledger baseline 7/7; 0 attribution lines; files < 800 lines; THR registry diff insertions only.
- **Next:** Parv: review block D. Kush: run both dry-runs locally with data; supply N1-N3. Next session S156 Step 18 event engine + 26g adapter.

### S156 · 2026-11-03 20:48 IST · ES-1 · Step18 event log/replay/adapter and 26g simulation-input contract (DRAFT); AI review R1-R6 fixed
- **Who:** Kush (cloud agent session; workers ksh/prv)
- **Did:** ksh audited the engine (L1-L8 left unchanged per Kush), could not reproduce the test_transition hang, built append-only event log, deterministic replay with transactions/snapshot hashes, and extraction->engine adapter. prv built 26g sim-input contract, null-sim_run_id link records and counts-only simulability census; cross-reviewed Step 18 (R1-R6 fixed test-first, O1-O7 open).
- **Files:** `src/culinarystate/state_graph/{event_log`, `replay`, `event_adapter}.py`, `src/culinarystate/simulation/*`, `tests/unit/test_step18_*.py`, `tests/unit/test_step26g_recipe_adapter.py`, `reports/step18/*`, `handoff/REVIEW_SHEET_AI_VERDICTS.md`
- **Verified:** Full unit suite 2166 passed, 17 skipped, 1 deselected; 1 failed + 11 errors = missing bundle files. Ledger baseline 7/7; 0 existing engine files edited; 0 attribution lines.
- **Next:** Kush/Parv: review block E; run Mac hang diagnostic. Next S157 evidence machinery (09, 12.0 staging rows only, 12-local parsers, 13a-0).

### S157 · 2026-11-03 21:33 IST · ES-1 · Evidence machinery: Step 09 queue, 12.0 proposed registration, 12-local parsers, 13a-0 seed corpus (PROVISIONAL)
- **Who:** Kush (cloud agent session; workers ksh/prv)
- **Did:** ksh built Step 09 machinery (human-derived status only), 12.0 proposed SRC/SNAP rows in staging, R2 and Bognar 12-local parsers with read-only EVD diff. prv built 13a-0 offline exact-DOI seed corpus (713 seeds from tracked artifacts, no abstracts) and cross-reviewed (R1-R4 fixed test-first). No ledger write, no id minted.
- **Files:** `src/culinarystate/evidence/{machinery`, `extraction_fields`, `registration`, `step12_local`, `seed_corpus}.py`, `src/culinarystate/ingest/{usda_yields_r2`, `bognar_remaining}.py`, `tools/step12_*.py`, `tools/step13a0_seed_corpus.py`, `registry/evidence/`, `registry/schemas/evidence_verification_queue_item.provisional_v1.schema.json`, `reports/step09/*`, `reports/step13/*`, `tests/unit/test_step09_*`, `test_step12_*`, `test_step13a0_*`, `test_s157_*`
- **Verified:** Full unit suite 2341 passed, 17 skipped, 1 deselected; 1 failed + 11 errors = missing bundle files. Ledger guard 7/7; 0 pre-S157 files modified; 0 attribution lines.
- **Next:** Kush/Parv: review block F (re-baseline, H2, E4 rule, review authenticity). Kush: run the three tools locally. Next S158 kinetic contract + mechanism stack (04.3, 21, 22a, 23a).

### S158 · 2026-11-03 22:31 IST · ES-1 · Kinetic contract 04.3 v1.1, MECH v1.1, 22a signatures, 23a applicability engine (DRAFT; 23b blocked)
- **Who:** Kush (cloud agent session; workers ksh/prv)
- **Did:** ksh built KIN/KINPT v1.1 with cross-record validator and MECH v1.1 with expert question list (14, sources UNVERIFIED: hosts blocked). prv built sign-only 22a signatures + case-seal helper, three-valued 23a engine with APPDEC schema and 56 reason codes compatible with 26g, and cross-reviewed (R1-R6 fixed test-first).
- **Files:** `registry/schemas/{KIN`, `KINPT`, `MECH}.draft_v1_1.schema.json`, `registry/schemas/APPDEC.draft_v1.schema.json`, `registry/mechanisms/*`, `src/culinarystate/lineage/kinetic_contract.py`, `src/culinarystate/mechanism/*`, `reports/step04/kinetic_trajectory_contract_v1_1_DRAFT.md`, `reports/step21/*`, `reports/step23/*`, `tests/unit/test_step04_3_*`, `test_step21_*`, `test_step22a_*`, `test_step23a_*`, `test_s158_*`
- **Verified:** Full unit suite 2574 passed, 17 skipped, 1 deselected; 1 failed + 11 errors = missing bundle files. Ledger guard 7/7; 0 attribution lines.
- **Next:** Kush/Parv/expert: block G. Next S159 simulator core (24a, 26a-c) data-free.

### S159 · 2026-11-03 23:30 IST · ES-1 · Formula registry 24a, kinetic fitting 26a, simulators sim_aa_1/sim_chl_1 26b, verification 26c, 26.0 template (data-free DRAFT)
- **Who:** Kush (cloud agent session; workers ksh/prv)
- **Did:** ksh built FORM/PARAM/VAL drafts and the 26a fitting/identifiability library with synthetic recovery. prv built sim_aa_1 and sim_chl_1 behind one APPDEC-gated interface (no parameter values in code), the 26c verification harness, an unsigned 26.0 selection template, and cross-reviewed 24a/26a (R1-R5 fixed test-first). D-050 (block G, scipy) and D-051 (THR-04K signed) recorded.
- **Files:** `registry/schemas/{FORM`, `PARAM`, `VAL}.draft_v1.schema.json`, `src/culinarystate/mechanism/form_param_val.py`, `src/culinarystate/simulation/kinetics/*`, `src/culinarystate/simulation/{sim_core`, `sim_aa_1`, `sim_chl_1`, `systems`, `choi_okos`, `verification}.py`, `reports/step26/*`, `tests/unit/test_step24a_*`, `test_step26*`, `test_s159_*`, `pyproject.toml`, `registry/preregistered_thresholds_v1.csv`, `DECISIONS.md`
- **Verified:** Full unit suite 2994 passed, 17 skipped, 1 deselected; 1 failed + 11 errors = missing bundle files. Ledger guard 7/7; 0 attribution lines; no literature/fitted values in code.
- **Next:** Kush/Parv: block H (26.0 selection, model questions). Next S160 freeze prep (15.0, 15a.R tool), Step 35 final package for signature, 29/30/34 harness scaffolds.

### S160 · 2026-11-04 00:13 IST · ES-1 · Freeze prep: 15.0 rulings draft, 15a.R seal tool (refusing), Step 35 v2 package for signature, evaluation scaffolds 29-diag/30/34a/34c
- **Who:** Kush (cloud agent session; workers ksh/prv)
- **Did:** ksh drafted 15.0 options/recommendations (RESERVED fraction UNKNOWN), built the 15a.R seal tool that refuses without a signed 15.0, and the Step 35 v2 package (v1 unchanged, D1-D8/D-040 integrated, amendments as unadopted appendix, 21 inputs bound, runner refuses until signed). prv built group-disjoint splits, leakage checks, NON_CITABLE 29-diag runner, Step 30 bake-off, 34a/34c scaffolds, and cross-reviewed (R1-R4 fixed; v2 hashes regenerated). D-049..D-052 recorded; sim_aa_1 selected.
- **Files:** `reports/step15/*`, `src/culinarystate/lineage/reserved_seal.py`, `tools/step15a_R_seal.py`, `reports/step35/*v2*`, `src/culinarystate/representation/explicit_runner.py`, `src/culinarystate/evaluation/*`, `reports/step34/*`, `reports/step26/system_selection_record.SIGNED.json`, `tests/unit/test_step15a_*`, `test_step35_v2_*`, `test_eval_*`, `test_s160_*`, `DECISIONS.md`, `handoff/*`
- **Verified:** Full unit suite 3185 passed, 17 skipped, 1 deselected; 1 failed + 11 errors = missing bundle files. Ledger guard 7/7; 0 attribution lines; no SIGNED Step 35 record (all tasks refused).
- **Next:** STOP at checkpoint H-A: Kush/Parv review block I (15.0 rulings + RESERVED fraction + seed policy; Step 35 v2 signature with P-1..P-5 and S-1/S-2; scaffold values). Then C1/C2 where the data bundle exists, H-B, S161-S163.

### S161 · 2026-11-04 15:16 IST · ES-1 · Fix Step 35 v2 package tests that failed on the Mac with real data present
- **Who:** Kush (cloud agent session)
- **Did:** Parv was blocked by a failing data/approval test on the Mac. Reproduced in a simulated Mac tree: test_step35_v2_package::test_unsigned_record_matches_current_bytes_and_is_refused and ::test_unsigned_record_is_reproducible_from_the_builder assumed the three Mac-only recipe files were absent (true only in the cloud). Rewrote both to check record self-consistency and, where Mac-only files exist, that a rebuild keeps every committed hash and adds only Mac-only inputs (Route B). Tampering is still detected. No data, record, signature or threshold changed; no human review supplied.
- **Files:** `tests/unit/test_step35_v2_package.py`
- **Verified:** 22/22 pass in the cloud and in the Mac simulation; tampering a bound ledger byte still fails both tests; all 1,532 tests added since main pass in the Mac simulation; full cloud suite 3185 passed, 17 skipped, 1 deselected, 1 failed + 11 errors = missing bundle files (unchanged).
- **Next:** Parv pulls cloud/s160-freeze-prep and reruns tests; checkpoint H-A (block I) continues.

### S162 · 2026-11-04 22:09 IST · ES-1 · Real-data runs of the S154–S160 tools; auditor fix for ºF/ºC; D-053 (H-A AI recommendations accepted)
- **Who:** Kush (cloud agent session)
- **Did:** Downloaded the Drive bundle (4 archives, checksums OK, paths safe, 3,814 macOS ._ files removed, no tracked file changed; baseline 7/7). Ran on real data: Step 16 rc2 grounding (612,782 recipes, 4,281,956 lines, 0 exceptions, invented grams 0, Q0 mass 33,373 lines, 21,172 unsupported); Step 17b seed 20261104 1,000 sample (invented_count 23 UNIT_NOT_IN_SPAN from ºF/ºC written with U+00BA, an auditor false positive; test first d09a3aa, fix 95e8401; rerun invented_count 0, V2 5 inverted intervals); 12.0 (3 SRC + 7 SNAP proposed, staging only); 12-local (173 R2 rows, 1,693 Bognar cells, T36 unparsed); 13a-0 (715 seeds, 703 DOI). Extra full-corpus Rung A run stopped at the 2 h session limit, no output. Recorded D-053 from Kush's words (Parv relayed): AI recommendations of block I accepted; human-only values, S-1/S-2 and the Step 35 signature stay open; nothing signed. Old branches s154–s158 confirmed contained in main via s160; their deletion was refused by the git proxy (Kush to delete on GitHub).
- **Files:** `reports/step16/S161_real_data_runs.md; reports/step16/rc2_grounding_dryrun_counts.json; reports/step17/rung_a_dryrun_counts.json; reports/step17/rung_a_dryrun_counts_prefix_S161.json; registry/staging/step12_0_src_snap_proposed_v1.jsonl; reports/step12/step12_local_counts_v1.json; registry/evidence/seed_corpus_13a0_full_v0.jsonl; reports/step13/S157_13a0_seed_corpus_full_counts.json; reports/step13/S157_13a0_seed_corpus_full_report.md; src/culinarystate/extraction/auditor.py; tests/unit/test_s161_ordinal_degree_unit.py; DECISIONS.md (D-053); STATUS.md`
- **Verified:** Full unit suite with data 3215 passed, 2 skipped, 1 deselected, 0 failed (before the fix 3212 passed); verify_baseline 7/7 and every tool's before/after ledger check PASS; 15a.R check --decision D-053 refuses with 7 blockers; all committed outputs counts/hashes/ids or paper metadata only
- **Next:** Merge cloud/s161-real-data-runs into main (one PR). Humans: remaining H-A values (RESERVED fraction, seed, δ_30, ρ, c_floor, 34c), P-1..P-5, S-1/S-2, Step 35 Route B signature on the Mac; review S161 outputs and the 12.0 file (D-049 re-baseline); go for C2 (P1 frame rebuild and draw).

### S163 · 2026-11-05 15:49 IST · ES-1 · Full-corpus Step 17b Rung A real-data run on vinayak-server; auditor fixes for deg-prefix temperature units
- **Who:** Kush
- **Did:** Ran tools/step17b_rung_a_dryrun.py --seed 20261104 --sample-size 612782 on vinayak-server (CPU only, 1 process, nice 10, no GPU; ThyroGenUS untouched) from a checksummed 14-part Drive bundle of the Mac tree (setup check: baseline 7, 1,000 sample identical to the committed file). Original auditor: invented_count 626 (UNIT_NOT_IN_SPAN; 624 Food.com, 2 A1/BBC); after the deg-prefix fix: 4 (2 Food.com texts); exceptions 0, baseline PASS before and after, contains_text/ids false, 89,316,045 values checked, V2 INVERTED_INTERVAL 4,511 in 3,848 texts. Root cause by shape masks only (no text printed): TEMP_RE accepts deg/degree(s)/deg. straight before C/F (<digits>degF) and keeps the unit's case (<digits> degree<c|f>), but the auditor whole-token check refused them: false positives, not invented values. Three test-first fix pairs in _unit_token_in (32d9a90/24bb227, fa0d19e/4608c4c after code review limited the prefix to temperature units, f40a982/a567a92 lowercase c/f). After a567a92: 1,000 check invented 0 and identical to the committed file; sharded census of all 612,782 recipes invented 0. The tool keeps the full sample in memory (~3.3 GB), so the 8 GB Mac swapped and its run was stopped.
- **Files:** `src/culinarystate/extraction/auditor.py; tests/unit/test_s163_deg_prefix_unit.py; reports/step17/rung_a_dryrun_counts_full_corpus.json; reports/step17/rung_a_dryrun_counts_full_corpus_prefix_S163.json; reports/step16/S161_real_data_runs.md (3.2b)`
- **Verified:** test_s163 + test_s161 8 passed; auditor/Rung A subset 212 passed, 1 skipped; server full suite 5,656 passed (5 failed + 11 errors are server-only: no .git, bundle-excluded identity files; the same 42 pass on the Mac); verify_baseline 7 on Mac and server
- **Next:** Commit the tool's own full rerun on a567a92 (running on vinayak-server, reports/step17/rung_a_dryrun_counts_full_corpus_final.json) when it finishes; optional sharded Step 17b tool (current one is single-process, ~3.5 h); review the V2 INVERTED_INTERVAL counts; H-A human values; go C2.

### S164 · 2026-11-05 19:33 IST · ES-1 · S163 AI cross-review (ksh/prv personas) and review block J
- **Who:** Kush
- **Did:** Two read-only AI reviewers cross-checked the 2026-11-04/05 work. ksh (Kush persona) reviewed Parv's PR #5 items: 15.0 draft ACCEPT_WITH_CHANGES (parses in the seal; seed custody and pre-seal bake-off exposure); P1 draw ACCEPT (independent re-draw identical, gate 0 blockers); packet maker ACCEPT_WITH_CHANGES (the sealed key can be rebuilt from public data; commit/snapshot step not built); diagnostics ACCEPT_WITH_CHANGES (bake-off pre-seal, not citable; 26g stale). prv (Parv persona) reviewed S163: auditor fixes, full-corpus results and the PR #5 merge, all ACCEPT_WITH_CHANGES (tests fail before each fix; the three JSONs differ only in auditor counts; documents match); V2 review plan. Applied the AI-remit changes: refusal regression tests, 3.2b provenance and evidence scope, STATUS wording. The tool's own full rerun on a567a92 gave invented_count 0 (committed in PR #6), closing the S163 'Next' item.
- **Files:** `reports/review/S163_ai_review.md; handoff/REVIEW_SHEET_AI_VERDICTS.md (block J); tests/unit/test_s163_deg_prefix_unit.py; reports/step16/S161_real_data_runs.md; STATUS.md`
- **Verified:** test_s163_deg_prefix_unit.py 6 passed; reviewers ran test_step19_pilot_packets (7 passed), step19_real_pilot check (ready, 0 blockers), in-memory P1 re-draw (identical 21 rows)
- **Next:** Kush and Parv reply to block J (J5 fraction and seed, J6 ratify C2, J7 packet salt and snapshot step, J4 V2 census); then D-054; 15a.R seal; annotator A packets; P1 annotation; block I values (delta_30, rho, c_floor, 34a.0, 34c); Step 35.

### S165 · 2026-11-05 19:56 IST · ES-1 · Block J accepted; Step 19 packet salt, guards and commit step; V2 inverted-interval census
- **Who:** Kush
- **Did:** Recorded Kush's acceptance of block J for both. J7: packet order now uses a secret per-annotator salt (>=64 hex, >=8 distinct digits, private 0600 file outside the repo, symlink/case-safe check; only its sha256 tracked as salt_P1_<letter>.sha256). The packet maker refuses if the local folder or key is not git-ignored or the other letter is present. New commit step (pilot_commit.py + tools/step19_commit_step.py): FIRST_VALIDATE/DONE snapshots in log order, design-shaped text-free commitments_<letter>_<wave>.json, refusal of unfinished/invalid/wrong-annotator files, stale or out-of-order snapshots, missing or extra packets vs the issued list, empty question log; exclusive writes; validated wave and packet ids. A python-reviewer pass found 2 HIGH + 5 MEDIUM, all fixed test-first. B's unsalted packet list and key hash moved to superseded_s164_unsalted/ for re-issue. J4: 62-shard counts-only census on vinayak-server reproduces V2 INVERTED_INTERVAL 4,511 issues in 3,848 texts (Food.com 2,786, Gutenberg 1,721, A1 2, Wikibooks 2); about 94% have the shape '9-9/9 <unit>' (hyphenated mixed numbers such as 1-1/2 read as an inverted range). The fix belongs to the versioned rc2 quantity grammar and needs a human decision after the J4 sample. J8: the 26g rerun is deferred, because Parv's census was ad hoc (no committed tool).
- **Files:** `src/culinarystate/annotation/pilot_packets.py; src/culinarystate/annotation/pilot_commit.py; tools/step19_packet_maker.py; tools/step19_commit_step.py; tests/unit/test_s164_pilot_salt_commit.py; tests/unit/test_step19_pilot_packets.py; registry/recipe_semantics/deep_gold_pilot_v1/superseded_s164_unsalted/; handoff/REVIEW_SHEET_AI_VERDICTS.md`
- **Verified:** test_s164 + test_step19 35 passed; step19/pilot/gold/annotation/s163/s164 subset 528 passed; tool refusals smoke-tested (missing/bad salt, ../ wave, bad packet id, no issued list); census totals equal the full-run JSON (4,511 / 3,848)
- **Next:** Kush: generate the 15a.R seed (own session), then D-054 and the 15a.R check/seal on Kush's Mac; Kush: P1 salt and annotator A packets; Parv: salt and re-issue B on his Mac; J4 human sample focusing on the 9-9/9 shape, then an rc2 grammar decision; build a committed 26g census tool; record the code commit in Step 17b reports.

### S166 · 2026-11-06 12:27 IST · ES-1 · PR #8 review and leak fix; Step 17b code provenance; committed Step 26g census tool; block K, D-054
- **Who:** Kush
- **Did:** PR #8 checked (Mac subset 437 passed; vinayak-server full suite 3,242 passed, 3 failed + 11 errors all no-.git or Mac-only git-ignored files). AI reviewers prv and ksh cross-reviewed (reports/review/S166_ai_review.md). prv P1: the S165 salt did not hide the packet->recipe map: tracked content_sha256 was a plain hash of public recipe content (7/7 superseded B packets mapped); the main session found the same for file_sha256 and the plain sealed-key hash (7! = 5,040 mappings). Fixed test-first: tracked values are salted commitments sha256(salt|hash), per-packet counts dropped, patterned or reused salts refused, issued list required, re-issue note added. Step 17b report now carries code_provenance (git commit, dirty flag, module and src-tree hashes; null commit on the no-.git server copy; re-checked after the run). New committed 26g census (census_chain.py, tools/step26g_census.py): on Parv's 1,000 sample (seed dryrun-2026-11-04) the census block and census_sha256 7e660634... equal Parv's file; adapter_invented_excluded 2 -> 0 comes from the S161 º auditor rule (ksh K2, three-auditor rerun), not the S163 fixes as first stated. The JSON states that all-SIM_PROHIBITED is by construction (no bindings yet). D-054: Kush passed the prv items for himself and Parv (relayed), incl. J7 re-confirmed and the PR #8 merge; the merge itself was blocked by the auto-mode classifier and is left to Kush.
- **Files:** `src/culinarystate/annotation/pilot_packets.py; src/culinarystate/annotation/pilot_commit.py; tools/step19_packet_maker.py; tools/step17b_rung_a_dryrun.py; src/culinarystate/simulation/census_chain.py; tools/step26g_census.py; tests/unit/test_s166_*.py; tests/unit/test_s164_pilot_salt_commit.py; tests/unit/test_step19_pilot_packets.py; reports/step26/simulability_census_real_sample_counts_S166.json; reports/review/S166_ai_review.md; handoff/REVIEW_SHEET_AI_VERDICTS.md (block K); DECISIONS.md (D-054)`
- **Verified:** step19/pilot/gold/annotation/s163/s164/s166 subset 447 passed; s166 + step17b tests 31 passed, 1 skipped; leak test runs the public-data attack (unsalted values reachable, tracked values not); real 1,000 census identical to Parv's (sha 7e660634...), 0 exceptions, baseline PASS before and after
- **Next:** Kush merges PR #8 (gh pr merge 8 --merge), then opens a PR for kush/s166-17b-provenance; Kush and Parv reply to block K4-K10; commit the full-corpus 26g census JSON from vinayak-server (~/Kush/cs_runs/step26g_census_full_corpus_S166.json) when it finishes; then P1 salts and packets with the fixed maker (Parv re-issues B, Kush builds A), the 15a.R seed and the 15.0 ruling (next free D-number), J4 sample once a reader is named

### S167 · 2026-11-06 19:19 IST · ES-1 · Step 19 P1 run end to end (model-assisted), P1 score and handbook gate, full-corpus 26g census, SP triage, Addendum B draft, J4 tool
- **Who:** Kush
- **Did:** PR #8 merged (db2cd3e). A's P1 salt and packets built (D-057/D-058; ksh/prv attacker and owner checks passed). P1 run as D-045 W2 model-assisted (D-060): ksh first pass for A, prv cross-check (21 must-fix), ksh pass 2/3, Kush stamp; commitments_A_P1.json committed (D-061..D-063). Parv's laptop down: B built on Kush's Mac in a separate clone after A's commitment (deviation D-064); prv first pass for B, ksh cross-check (18 must-fix), prv pass 2, ksh re-check; commitments_B_P1.json committed (D-065/D-066). New committed P1 scorer (key pairing, commitment and salted-key checks, counts only, tool denominators, THR-19P-16/-31 gate) found and fixed an S101 disagreements() arity crash; P1 (7 pairs, human-accepted AI drafts, not blind): spans 0.84, concept 0.90, coref 0.84, strict events 0.56, final state 0.26; gate HANDBOOK_REVISION_REQUIRED (coref, final_state, event_type, entity_type, event_argument). prv read THR-19P: mostly NOT_EVALUABLE under W2/D-064; THR-25 FAIL until triage. Schema-problem log opened (SP-001 step-only ingredient, SP-002 U+2044 fraction parsed as 1 - also affects A's committed quantities, SP-003 unstated shares, SP-004 alternative values) with ksh/prv AI triage; Addendum B drafted (B.1-B.23). Full-corpus 26g census committed (612,782 recipes, 14,594,812 events, 0 SIMULATE by construction, 0 exceptions). J4 sharded extraction tool built and launched on vinayak-server (D-059). Blocks L, M (D-058, D-067) passed; block N pending.
- **Files:** `src/culinarystate/annotation/pilot_p1_score.py; tools/step19_p1_score.py; src/culinarystate/annotation/pilot_agreement.py; src/culinarystate/extraction/j4_inverted_sample.py; tools/j4_inverted_interval_sample.py; tools/step19_packet_maker.py; registry/recipe_semantics/deep_gold_pilot_v1/{packets`, `sealed_key`, `salt}_P1_{A`, `B}*`, `commitments_{A`, `B}_P1.json; reports/step19/p1_agreement_counts_S166.json; reports/step19/pilot_schema_problem_log.md; annotation/annotation_handbook_v1_addendum_B_DRAFT.md; reports/step26/simulability_census_full_corpus_S166.json; handoff/REVIEW_SHEET_AI_VERDICTS.md (blocks L`, `M`, `N); DECISIONS.md D-057..D-067`
- **Verified:** P1 score tests 13 passed + agreement fix test; J4 tests 7 passed (1 vs 2 workers identical); P1 rerun reproduces the committed numbers (ksh); both sealed keys verified against salted commitments; label files equal their commitments; all 14 labelled packets validate with 0 replay issues; census JSON counts-only, baseline PASS before and after
- **Next:** Humans: block N (SP severities, Addendum B stamp, SP-002 parser fix approval + ledger diff, SP-001 route, P1b yes/no); the 15a.R seed and 15.0 ruling (D-068); Parv reads the J4 sample first, then Kush. Agent: commit the J4 manifest when the server run lands; merge PR #9 on Kush's ok; clean up the cs_annotator_B scratch folder.

### S168 · 2026-11-06 23:45 IST · ES-1 · J4 sample, SP stamp and Addendum B issued, SP-002 scale and design, P1b tooling, final report draft
- **Who:** Kush
- **Did:** PR #9 merged. J4: sharded tool on vinayak-server (32 workers, ~3 min) found 4,511 cases in 3,848 texts, equal to the census; 94.8 % shape 9-9/9; 69-case stratified sample (P1 excluded) with private excerpts (git-ignored) and a text-free manifest. Blocks M-O passed (D-067, D-069, D-070): P1 score gained tool denominators and the THR-19P-16/-31 gate (HANDBOOK_REVISION_REQUIRED) and an SP-002 sensitivity block (no P1 number moves); SP-001..004 stamped (THR-19P-25 satisfied); Addendum B issued (8 rules, recurrence >= 3; 10 held). SP-002 measured: 1,275,782 of 4,281,956 ingredient lines (29.8 %) carry U+2044 and the Step 16 rc2 adapter shares the parser; ksh's versioned adapter-level fix design approved for after the presentation (grammar.py untouched). 15a.R seed generated on Kush's Mac (never printed); D-068 15.0 block prepared for Kush to append himself. P1b: amendment proposal; wave-scoped paths, --wave in packet maker/commit step/scorer, draw_wave (cell subset, wave seed, earlier waves excluded; P1 unchanged; real record refuses P1b until authorised). Final report drafted by an agent, fact-checked by ksh (~190/192 matched, 2 corrected, 3 UNVERIFIED resolved) and reviewed by prv (2 MUST_FIX + 6 SHOULD_FIX applied); review blocks P and Q added.
- **Files:** `src/culinarystate/extraction/j4_inverted_sample.py; tools/j4_inverted_interval_sample.py; reports/step17/j4_inverted_interval_*_S166.*; src/culinarystate/annotation/{pilot_p1_score`, `pilot_packets`, `pilot_commit`, `pilot_real}.py; tools/step19_{p1_score`, `packet_maker`, `commit_step`, `real_pilot}.py; reports/step19/{p1_agreement_counts_S166.json`, `pilot_schema_problem_log.md`, `sp_stamp_proposal_ksh_S168.md`, `P1b_design_amendment_PROPOSED.md}; annotation/annotation_handbook_v1_addendum_B*.md; reports/step16/sp002_fix_design_ksh_S168.md; reports/final/FINAL_REPORT_DRAFT_S168.md; DECISIONS.md D-067..D-070; handoff/REVIEW_SHEET_AI_VERDICTS.md blocks N-Q`
- **Verified:** Mac subset (Step 16-19/26/J4) 583 passed, 1 skipped; P1b draw tests + existing P1 draw tests 36 passed; P1 rerun numbers unchanged after each scorer change; J4 totals equal the census; report leak-scan clean
- **Next:** Kush: append D-068 then 'seal'; P1b size, nonce and signed amendment; review blocks P and Q (report edits, UNVERIFIED items); Parv first, then Kush, read the J4 sample. Agent: P1b run once the human facts exist; SP-002 fix after the presentation; slide figures.

### S169 · 2026-11-07 00:04 IST · ES-1 · Delegation rule D-071; J4 read and decided; census reason fix (lot introductions); P1b draw and wave tooling; slide figures
- **Who:** Kush
- **Did:** D-071: ksh/prv verdicts count as Kush's/Parv's decisions (recorded as AI under delegation); signatures, nonces and person-only facts stay human. J4 read by prv then ksh independently (62 mixed-number misreads, 3 true reversed ranges, 4 other; 69/69 agreement, same model family): mixed numbers will be parsed as mixed numbers in the versioned rc2 change after the presentation (D-072). ksh engine diagnosis: 83 % of census NO_CONSUMED_ENTITY were synthetic lot introductions; fixed test-first (LOT_INTRODUCTION reason; census/contract 0.2.0); 1,000 sample: real gap 7.1 %, lot introductions 35.1 %; report draft and figure 2 corrected; implicit-object binding rules need a precision check (D-073). P1b tooling: wave_paths, --wave in packet maker/commit step/scorer, draw_wave (cell subset, wave seed, earlier waves excluded; P1 unchanged; signed record refuses P1b until amended). Final report draft revised after ksh fact-check and prv review; three slide figures (tools/make_final_figures.py).
- **Files:** `src/culinarystate/simulation/recipe_adapter.py; src/culinarystate/annotation/{pilot_real`, `pilot_packets`, `pilot_commit}.py; tools/step19_{real_pilot`, `packet_maker`, `commit_step`, `p1_score}.py; tools/make_final_figures.py; reports/final/*; reports/step26/simulability_census_real_sample_counts_S168.json; reports/step17/j4_reading_counts_S168.json; DECISIONS.md D-071..D-073; tests/unit/test_s168_*.py`
- **Verified:** Step 16-19/26/J4 subset 583 passed (before the census fix); census/adapter tests 49 passed after it; P1b draw + P1 draw tests 36 passed; 1,000 census rerun from a clean commit (census 0.2.0); figures inspected after render
- **Next:** Commit the full-corpus census 0.2.0 when the vinayak-server run lands (~4 h, ~/Kush/cs_runs/step26g_census_full_corpus_S168.json); precision check for the two Rung A implicit-object rules; humans: append D-068 then seal; Step 35 signature; P1b nonce + signed amendment; merge PR #10.

### S170 · 2026-11-07 21:22 IST · ES-1 · Census 0.2.0 full run committed; seal unlock check; D-073 precision check (R1 not landed)
- **Who:** Kush
- **Did:** Committed the full-corpus census 0.2.0 run (612,782 recipes, 14,594,812 events, exceptions 0, baseline PASS; NO_CONSUMED_ENTITY 7.0 %, LOT_INTRODUCTION 35.1 %, the exact split of S166's 6,152,456; module hashes match the repo). Seal check: the 15a.R seal clears NO_SIGNED_15_0, SEAL_COMMITMENT_MISSING and SEALED_LIST_MISSING for 29-diag (sealed list verifies); still blocked by SNAPSHOT_NOT_FROZEN (no freeze-record format) and DIAG_PREREG_UNSIGNED (Kush). Step 30 does not gate on the seal; its S160 exploratory run predates the seal (PRIOR_EXPOSURE_REANALYSIS label). D-073: exploration on a separate seed, pre-registration (+ Amendment 1) before the draw, observer-only sampler, 60-item ksh labelling: R1 4/60 CORRECT, DO_NOT_LAND; R2 withdrawn (D-074).
- **Files:** `reports/step26/{simulability_census_full_corpus_S169.json`, `CENSUS_FILES.md}; reports/step17/{d073_implicit_binding_precision_PREREG.md`, `d073_r1_sample_counts_S170.json`, `d073_r1_precision_S170.json}; src/culinarystate/extraction/d073_current_sample.py; tools/d073_precision_sample.py; tests/unit/test_s170_d073_sample.py; DECISIONS.md D-074`
- **Verified:** census provenance hashes all match; no free-text strings in the census file; new tests 12 passed; rung_a/binding/census subset 92 passed 1 skipped; private sample csv git-ignored; 29-diag blockers re-run after D-074
- **Next:** Kush: P1b nonce; Step 35 v2 signature; then report block Q + slide deck

### S171 · 2026-11-08 02:36 IST · ES-1 · M1 done (router census), M2 07.A-R1 packet ready, M3 AA CAL packet ready, M4 router + front door; manjot reviewed
- **Who:** Kush
- **Did:** manjot-server reviewed read-only: stale 26 Oct snapshot, 0 server-only files. M1: counts-only router demo census (router_census.py, tools/router_demo_census.py, --workers fork pool, identical to 1 worker); 1,000 seeded recipes vit C: 60,882 checks, DIRECT 421 (0.69 %), UNKNOWN 60,461, 0 exceptions, baseline PASS; EVD vit-C pairs 115 over 25 ingredients, sample used 53 = 0.39 % of its 13,652 distinct pairs. code_unchanged_during_run=false only because HEAD moved by tests/report commits during the run (src and code hashes identical, checked). Server (vinayak ~/Kush/culinarystate, tracked-file rsync to HEAD) reproduced the 1,000 file exactly; full corpus launched. M2: 07.A-R1 prereg (pooled Gwet AC1 >= 0.80 + critical-field AC1/exact/repeat rule; kappa diagnostic only), packet of 100 fresh conditions disjoint from v1-v4 (v4 rows reproduce 100/100, freeze intact, fingerprint e7d589136275), scorer + CLI. M3: CC-BY source search (Europe PMC + OpenAlex), 12 include/maybe; prereg with row definition, paper-level seeded split (VAL AAK-12/07/03/05) and fit spec fixed before any fit; 7/12 PDFs fetched, 5 refuse scripted download (not bypassed); 16 CAL rows from 4 papers, spans 16/16 verbatim; verification packets for Kush and Parv (git-ignored); Model A fit module + freeze CLI. M4: SSOT 39 query router + front door with explicit abstention. Two stale pre-seal tests updated (bootstrap diag blockers, D-068 ruling).
- **Files:** `src/culinarystate/mechanism/router_census.py; tools/router_demo_census.py; reports/step23/router_demo_census_vitc_1000_S171.json; reports/step07/07A_R1_*; src/culinarystate/evidence/condition_{agreement`, `audit_packet}.py; tools/step07ar_*.py; reports/step10/aa_pilot_*; registry/evidence/aa_kinetics_source_candidates_v1.csv; src/culinarystate/simulation/aa_pilot_fit.py; tools/aa_pilot_fit.py; src/culinarystate/decision/{query_router`, `front_door}.py; tests/unit/test_s171_*.py`
- **Verified:** S171 tests + router demo + the two updated test files: 135 passed together; full suite run with -x stopped at the stale D-068 test (4,501 passed, 1 failed), fixed; full rerun still pending; server 1,000 census identical to Mac
- **Next:** Humans: sign 07A_R1 prereg then label R1 packet (by 13 Nov); verify AA CAL packet (by 15 Nov); browser-download AAK-02/04/05/08/10 into data/raw/aa_pilot/; sign AA prereg. Agent: commit full-corpus router census; M4 wire TRANSFORMATION handler (pipeline.answer + router_demo); M5 re-cut h_state questions with current engine + draft ~80 questions; M6 FastAPI demo (B5T needs no LLM key).

### S172 · 2026-11-08 02:56 IST · DEL-5 · M1 full corpus committed; M4 core (router, front door, handlers); M5 prereg + 100 drafted questions
- **Who:** Kush
- **Did:** Full-corpus router census committed (612,782 recipes, 36,359,902 checks, DIRECT 274,058 = 0.754 %, 0 exceptions, baseline PASS, module hashes match). M4: demo_context loads once and answers through the front door: TRANSFORMATION = DEL-5 pipeline + B5T template + router demo per recipe step; RELATIONSHIP = corpus substitution edges labelled as a pattern with the raw co-occurrence score (first draft printed it as a percent: fixed test-first); METADATA/SEMANTIC/MULTIMODAL abstain. M5: D5/H1/H3 prereg before any question; P/C drafter (EVD strata DIRECT/SIMILAR_ONLY/NONE, rotating phrasings, seeded, <=2 per ingredient, USDA % normalised to fractions) and S drafter (Wikibooks/Gutenberg only, seeded cut, Rung A heated-so-far and next-action gold); 100 questions; review sheets for Kush and Parv.
- **Files:** `reports/step23/{router_demo_census_vitc_full_corpus_S171.json`, `ROUTER_CENSUS_FILES.md}; src/culinarystate/decision/demo_context.py; src/culinarystate/evaluation/{d5_draft`, `d5_state}.py; tools/d5_draft_{pc`, `s}.py; benchmark/d5/*; reports/del5/d5_benchmark_preregistration_DRAFT.md; tests/unit/test_s171_{demo_context`, `d5_draft`, `d5_state}.py`
- **Verified:** demo_context unit 4 + real-ledger 1 passed (38 s); d5_draft 5, d5_state 4 passed; draft spot-checked (gold ranges in fractions)
- **Next:** Humans: sign + review D5 sheets by 16 Nov (plus M2/M3 items). Agent: M6 FastAPI demo on demo_context (B5T, no LLM key); then ladder rungs B1/B2/B4 prompt code for H1 so runs start the moment the benchmark freezes.

### S173 · 2026-11-08 12:43 IST · ES-1 · D-077 physical-state dataset: verdict, Layer 1 binder, physics drivers, Layer 2 scenarios, run tracking
- **Who:** Kush
- **Did:** Project flow verdict written (handoff/PROJECT_FLOW_VERDICT_2026-11-08.md): NER trained but never deployed on the corpus; all 14.6 M events lacked every simulator input. D-077 recorded (two layers never mixed; D-003 kept; parallel; tracked). Layer 1 binder over the frozen Rung A graph (stated duration/temperature incl. exact F->C, carried preheat setpoints, boil/steam 100 C by definition, process medium map, lid/start cues, cut-history size class, ING category; gas marks kept as codes). Physics drivers: slab conduction series (verified eigen-roots, known values) + equivalent-time dose. Layer 2 scenarios GENTLE/TYPICAL/INTENSE from registry/scenario_defaults_v1.csv (28 rows, SOURCE_UNVERIFIED_AGENT_RECALLED) and corpus duration quantiles (KGE), labelled SCENARIO/MODEL_DERIVED/NON_CITABLE, transition physically_possible, no nutrient numbers. 1,000 recipes: 2,850 heat events; L1 time+T 3.3 %; L2 drivers 47 %; core T 102 events (size class limits). registry/compute_runs_v1.csv + logger. One bug (ING category field) found and fixed test-first; buggy uncommitted output discarded.
- **Files:** `handoff/PROJECT_FLOW_VERDICT_2026-11-08.md; DECISIONS.md D-077; registry/{process_medium_map_v1`, `scenario_defaults_v1`, `compute_runs_v1}.csv; src/culinarystate/simulation/{condition_binding`, `binding_census`, `physics_drivers`, `scenario_layer}.py; tools/{binding_census`, `scenario_layer_run`, `log_compute_run}.py; reports/step26/{binding_census_L1_1000_S172`, `scenario_L2_1000_S172}.json; tests/unit/test_s172_*.py`
- **Verified:** S172 tests: binder 10, census 3, physics 6, scenario 6 passed; L1 census baseline PASS before/after, code unchanged
- **Next:** VPN: full-corpus L1 + L2 on vinayak (non-BBC; BBC on the Mac), NER inference on the A100; humans verify scenario sources; then L1/L2 -> router re-run and Step 31 features.

### S174 · 2026-11-08 13:40 IST · ES-1 · Mac-side M9 families, NER prep, H1/H3 stats, 29-diag formats + runner; demo stopped
- **Who:** Kush
- **Did:** VPN route missing all session (192.168.3.x via en0), so Food.com and GPU NER wait. Mac: L1+L2 for BBC (D-003), Wikibooks, Gutenberg, TASTESET; runs logged. Ingredient-line exporter (refuses BBC off the Mac) + corpus NER inference script. Local demo built, then stopped at Kush's request (core before demo; memory saved); it surfaced a real verbaliser bug (other-process rows presented as the asked process), fixed test-first (verbalize@0.2). H1 rung contexts/prompts/id scoring, exact McNemar + Newcombe interval, H3 UCR question bootstrap. 29-diag: freeze-record and prereg-signature formats (human approval only, hash-checked) wired into the gate; proposed freeze record and prereg draft committed; runner (seal filter at CELL level, cap-stratified ladder, basis shortcut rerun, D7 vs D1).
- **Files:** `src/culinarystate/evaluation/{h1_rungs`, `paired_stats`, `freeze_records`, `diag29_runner}.py; src/culinarystate/generation/verbalize.py; tools/export_ingredient_lines.py; gpu/ner_bench/corpus_ner_infer.py; reports/step26/*_full_S173.json; reports/step29/29diag_preregistration_DRAFT.md; registry/freezes/15A-BOOT-2026-11-08.json`
- **Verified:** new tests: export 3, NER chunking 2, H1 5, paired stats 5, freeze 5, diag29 3, verbaliser 2 added; related suites 217 + 42 passed; L1 runs baseline PASS
- **Next:** Kush: fix VPN route; approve freeze record + sign 29-diag prereg (then 29-diag runs); earlier sign/label/verify/review items. Agent on VPN: Food.com L1/L2 on vinayak; NER on A100; merge full-corpus physical summary.

### S175 · 2026-11-09 11:48 IST · S175 · Lot composition: SR loader, ING->SR registry, line grams, BBC census
- **Who:** Kush+Claude
- **Did:** SR Legacy loader; lexical ING->SR matcher + 298-term defaults registry (AGENT_PROPOSED/UNVERIFIED; 76.3% of mentions); line->grams interval (stated / volume x SR density / count x SR portion; SSOT 235.3 q-levels, link-verification flag); counts-only census. BBC: 116,699 lines, 83,088 with grams (71.2% vs 33.7% in fdc_crosswalk_v0), 48,266 rest on unverified SR links, 1,517/11,934 recipes fully gram-resolved. v0 crosswalk has 0 human decisions; v1 registry is the review sheet.
- **Files:** `src/culinarystate/composition/*`, `registry/ing_sr_defaults_v1.csv`, `tools/s175_line_mass_census.py`, `reports/s175/line_mass_census_BBC.json`
- **Verified:** pytest tests/unit/test_s175_*.py: 33 passed; full suite not rerun (Mac memory low, earlier run reaped)
- **Next:** registry tier 2 for NO_MATCH/LOW names; FDA pH registry; lot_state; human check of ing_sr_defaults_v1

### S176 · 2026-11-09 11:57 IST · S175 · Lot state: FDA pH registry, exact lot bounds, BBC recipe-pool census
- **Who:** Kush+Claude
- **Did:** Registry tier 2 (490 terms) + SR head-noun/alias portion rules: BBC lines with grams 75.3%, recipes fully gram-resolved 2064/11934. FDA approximate-pH registry 479 items (2 source typos UNPARSED, not guessed); lookup item->head-union; 21 CFR 113/114 4.6 acid class. lot_state: exact linear-fractional bounds (mass fractions, sodium/sugars per g water), unknown grams = [0,inf), pH flags only (no mixture pH), PROVISIONAL while SR links unverified. RECIPE_POOL census: water bounded 15.9%, acid member 45.5%, any member pH unknown 99.4%.
- **Files:** `src/culinarystate/composition/{food_ph`, `lot_state`, `lot_census}.py`, `registry/food_ph_fda2003_v1.csv`, `tools/build_food_ph_registry.py`, `reports/s175/lot_census_BBC.json`
- **Verified:** pytest tests/unit/test_s175_*.py: 54 passed (ratio bounds cross-checked vs vertex enumeration, 300 random cases); full suite not rerun (Mac memory)
- **Next:** event-level lots via router lineage; drop NOT_A_FOOD fragments as non-members; decide pH NOT_APPLICABLE for anhydrous members (needs human/Max ruling); mechanism condition windows

### S177 · 2026-11-08 23:37 IST · ES-1 · S175 server orchestration (D-078): SSOT-vs-repo consensus plan, review-packet answers, SSOT v16 draft, physical-layer and router fixes, non-heat families, lot state, FDA pH
- **Who:** Kush+Claude (manjot orchestrator)
- **Did:** Took over orchestration on manjot (worktree .orch, branch max/s176-orchestration from kush/s169-seal-p1b@07fc0d2). 9-topic SSOT-vs-repo inventory + 3-reviewer consensus (217 components, 493 ledger rows, all 3/3). REV-A/REV-B answers to the 40-question packet. Lanes: non-heat families L1/L2 full non-BBC runs (3.03M events); lot-state [K] steps 1-3 (Food.com units confirmed absent; list misalignment 79.5 %); FDA pH registry (488); defaults + mechanism-window sourcing; evaporation/phase-change cap (cores >100 C 68.6 % -> 1.8 %, all dry-class); router target-presence + lot-context gates (vitamin-C DIRECT 267,933 -> 34,537 non-BBC) and demo honesty; SSOT v16.0 DRAFT (v15 text intact + PART XIV, 36 proposals); human ops pack; deployment plan; D-078. Final 2-persona review: GOV 0 blockers/9 major (fixed), SCI 1 blocker (salt load 100x, fixed) + 8 major queued.
- **Files:** `reports/orchestration/*`, `registry/component_ledger_v1.csv`, `docs/SSOT/computational_gastronomy_master_ssot_v16_0_DRAFT.md`, `handoff/*2026-11-0[89]*`, `src/culinarystate/{lotstate`, `simulation`, `mechanism`, `decision}/*`, `registry/*S176*`, `registry/compute_runs_v1.csv`, `DECISIONS.md`
- **Verified:** full suite on manjot: 3,554 passed; the 6 failures + 5 errors are identical on base 07fc0d2 (missing sklearn/lxml/requests/hypothesis or Mac-only data); 42 collection errors = missing modules; lane suites 380+ pass; protected ledgers byte-identical; v15 body byte-identical in v16
- **Next:** Mac: merge bundle, BBC re-runs (L2 v02, router census, non-heat), push + PR to main (ask Kush); humans: decision sitting 9-10 Nov, signatures 10-11 Nov; agent: FINAL-SCI majors #2-#5, #7-#9, public-mode BBC edge filter
- **Note:** logged on manjot as S175 on branch max/s176-orchestration; renumbered S177 at the merge with the Mac's S175/S176 (ids never reused).

### S178 · 2026-11-09 19:11 IST · ES-1 · S178 server lanes: board, prereg amendments, analysis, evaluation, related work, router fixes, EVD, governance docs, corpus, AA simulate guard, ING categories, physical-layer close-out; GOV review
- **Who:** Kush+Claude (manjot orchestrator)
- **Did:** Merged the Mac S175/S176 (a0a5b49); consolidation: composition/ canonical, lotstate/ SUPERSEDED. S177 SCIFIX-PHYS (zone doses, boiling scope, F0/acid scope, v03) and SCIFIX-ROUTER (prior-process context, full ABSENT rule, SR identity adapter, public mode; non-BBC vitamin-C DIRECT 40,308 of 267,933). S178 lanes: execution board (252 MUST+SHOULD, W1-W4); prereg AMENDMENT drafts + exact power; EVD card + NEG-0031..0046; H1 circularity check (40/40 ENGINE_DRAFT), independent H3 scorer, split registry, D5 leakage audit; related work (67 works); EVD conformance/SVAR reconcile/D5 U-X drafts; STATUS/G16 (0/14)/coverage map; SP-002 opt-in, Food.com pairing proposal, replay invariants; AA FORM drafts + refusing SIMULATE guard; ING category proposals (1,417); PHYS2 Layer 1 0.2.0 / Layer 2 0.4.0 (temperature ownership, provenance 100 %, endpoint cues, verification 15/15, sensitivity), v04 non-BBC re-runs. GOV review 0 BLOCKER / 6 MAJOR; orchestrator fixes (34 run rows, errata, NEG-0046, board DONE 10 -> 30). All AI_DRAFTED.
- **Files:** `reports/orchestration/S177_*`, `S178_*`, `review/S178_REV_GOV.md; registry/execution_board_S178.csv; registry/compute_runs_v1.csv; registry/negative_results_register_v1.csv; src/culinarystate/{simulation`, `mechanism`, `decision`, `evaluation`, `quantity}/*; reports/{step07`, `del5`, `step29`, `step10}/*AMENDMENT_S178_DRAFT*; reports/s178/*; reports/step26/*_S178_v04.json; handoff/{RESUME_ANCHOR_2026-11-09_ORCH`, `MAC_CLAUDE_MERGE_PROMPT_2026-11-09}.md`
- **Verified:** full suite at 32415c4: 4,485 passed; 6 failed + errors identical to base (missing lxml/requests/hypothesis/sklearn, Mac-only data); protected ledgers byte-identical (GOV review); 57/57 kept-output sha256 match
- **Next:** SCI-A/SCI-B reviews -> fixers; MECH, H1H3H (synthetic only), PHYS3 lanes; Mac: bundle fast-forward, BBC v04/router re-runs, composition tickets; humans: decision sitting, signatures, AA threshold, ING top-100

### S179 · 2026-11-09 21:01 IST · ES-1 · S178c round and anchor: reviews fixed (FIX-GOV committed), H1H3H harness, PHYS3 shapes/26g/diffusion; unfinished FIX-PHYS/FIX-ROUTER/FIX-EVAL + MECH saved on max/s178-wip
- **Who:** Kush+Claude (manjot orchestrator)
- **Did:** Committed H1H3H (D5/H1/H3/D4 scoring harness, frozen guard, synthetic only), PHYS3 (shape series 15/15, 26g census 1,000 sample SIMULATE 0, 45 sourced diffusion rows), FIX-GOV (SCI-B B1 blocker: EVD card 0.2.0 + reports/step15 copies; superseded guard + 53 rows; local server refuses tunnels; transition firewall; NEG-0047..0049), deployment plan --public, board S178c (DONE 34, BLOCKED_HUMAN 109). Session restarted twice (VS Code); FIX-PHYS (v05 code done, re-runs not), FIX-ROUTER (code + 1,000 census, full not), FIX-EVAL (code done, replay re-run killed, 2 outputs to regenerate) and the finished MECH lane are saved as one UNREVIEWED snapshot on branch max/s178-wip (own tests 86/68/71/46 pass). Lane briefs saved (paths cleaned) in handoff/orch_briefs_S178/.
- **Files:** `handoff/RESUME_ANCHOR_2026-11-09_ORCH.md; handoff/MAC_CLAUDE_MERGE_PROMPT_2026-11-09.md; handoff/orch_briefs_S178/*; registry/execution_board_S178.csv; branch max/s178-wip`
- **Verified:** lane suites green at each commit; WIP touched suites 843 passed, 2 failed (outputs to regenerate after FIX-EVAL); full suite last at 32415c4 (4,485 passed, failures pre-existing env/Mac-data)
- **Next:** Finish WIP lanes (v05 + router 0.4.0 full runs on manjot, reports, separate commits), short re-review, BBC re-runs on the Mac after that; humans: decision sitting, signatures, D5 review + gold columns, freeze record

### S180 · 2026-11-09 23:08 IST · S179 · Merge manjot S176-S178, composition tickets, finish WIP lanes (v05, router 0.4.0, FIX-EVAL, MECH), BBC legs
- **Who:** Kush+Claude (Mac, manjot, vinayak)
- **Did:** Fast-forwarded to max/s176-orchestration; branch kush/s179-finish-fixes = max/s178-wip + Mac fixes. Composition tickets A1-A11, F1-F5, P1/P3/P4/P5/P9 (tests first; reply in MAC_TASKS file). FIX-EVAL: regenerated D5 fixture output + prompt registry; replay invariants v2 full families (0 unexplained). FIX-PHYS: v05 sample + full non-BBC on manjot (schema 100%, moist-piece core above Tboil 12->0), BBC v05 on Mac. FIX-ROUTER: census 0.4.0 full non-BBC on vinayak (host equivalence proven on the 1,000 sample), BBC leg on Mac; DIRECT 40,308->30,248, ABSENT ING 52->13. MECH screen on v05 incl. first FOODCOM full run. Non-BBC composition censuses on vinayak (TASTESET grams lines +284 from U+2044). Lane reports FIX-EVAL/FIX-PHYS/FIX-ROUTER; supersessions registered; GOV re-review no blockers.
- **Files:** `src/culinarystate/composition/*; tests/unit/test_s179_*; reports/orchestration/S178_FIX-{EVAL`, `PHYS`, `ROUTER}_report.md; reports/s179/*; reports/step26/*_v05.json; reports/step23/*_S179*.json; reports/s178/mech/*_v05*; registry/compute_runs_v1.csv; registry/superseded_outputs_S176.csv`
- **Verified:** manjot full suite 4,968 passed (failures env gaps only); the 48 env-gap modules on Mac 2,881 passed 0 failed; composition 72+4 tests; governance superseded 9 passed; GOV re-review 0 blockers
- **Next:** SCI re-review result; push max/s176-orchestration + PR (ask Kush before merging main); push kush/s179-finish-fixes after re-review; humans: verify ing_sr_defaults via reports/s179/ing_sr_review_queue_BBC.csv, A6b hull choice, F1 grammar.py OK, deleting v04 per-record dirs on manjot

### S181 · 2026-11-10 02:03 IST · S179 · SCI re-review fixes and v06 / router 0.4.1 re-runs
- **Who:** Kush+Claude (Mac, manjot, vinayak)
- **Did:** SCI re-review: no blockers; fixed #1 M1 residual (endpoint-cues 0.3.0, L1 0.3.1), #3 audit counter by role, #4 post-food prior-state cues (router 0.4.1), #5 pH lookup size words / parent family, #6 split-sum marked not checkable; tests first each. Re-runs: non-BBC physics v06 + reports + MECH v06 on manjot (schema 100%, events unchanged; text-stated medium temperatures 51,121->51,001, food-target cues up, oven<77C 189->171), router 0.4.1 full non-BBC on vinayak (DIRECT 30,248->30,220), composition re-run byte-identical, BBC v06 + router 0.4.1 + lot S179b on Mac. 29 run rows, 55 supersession rows (89 older rows re-pointed to the live file). Lane reports FIX-PHYS sec 5, FIX-ROUTER sec 6.
- **Files:** `reports/step26/*_S179_v06.json; reports/s178/phys/*S179_v06*; reports/s178/mech/*S179_v06*; reports/step23/*_S179b.json; registry/compute_runs_v1.csv; registry/superseded_outputs_S176.csv; reports/orchestration/S178_FIX-{PHYS`, `ROUTER}_report.md; reports/orchestration/review/S179_REV_{GOV`, `SCI}.md`
- **Verified:** physics suites 641 passed; governance/register/S179/report-reading tests 76 + 79 passed; schema validator 0 problems all kinds; MECH 0 invariant violations, 0 exceptions
- **Next:** Kush: SCI #2 lift gate (Q1), SCI #7 SR analytical zero, A6b hull, F1 grammar.py OK, ing_sr review queue, delete v04/v05 per-record dirs on manjot, PR #11 merge OK, demo stash
