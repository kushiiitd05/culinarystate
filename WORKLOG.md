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
