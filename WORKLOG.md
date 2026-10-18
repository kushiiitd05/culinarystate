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
