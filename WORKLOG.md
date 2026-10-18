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
