# DECISIONS (ADR log)

Format: ID · date · decision · options considered · evidence · approver. Append-only.

### D-001 · 2026-10-18 · Rebuild programme repo locally in `CGAS/culinarystate`
- **Options:** (a) wait for Parv's Max-plan repo; (b) rebuild here, Parv continues from this repo.
- **Evidence:** no STATUS/DECISIONS/evidence-candidate files on this machine; Kush instructed "forget whatever github we have, he can pick or take from here".
- **Approver:** Kush.

### D-002 · 2026-10-18 · Ledger schemas are JSON Schema (draft 2020-12) + Python semantic validators, not pydantic
- **Options:** pydantic v1 (base env) / pydantic v2 (other envs) / JSON Schema.
- **Evidence:** base env has pydantic 1.10, other envs 2.12 → API split. JSON Schema is language-neutral and `jsonschema 4.19` is in base.
- **Approver:** Claude (reversible; flag for Kush/Parv review).

### D-003 · 2026-10-18 · Recipe corpus without RecipeDB = A1 BBC Good Food (11,934 recipes); NER gold proxy = TASTEset
- **Evidence:** RecipeDB API endpoint timed out; no key. A1 corpus has raw ingredient lines + instruction steps. TASTEset has span-level FOOD/QUANTITY/UNIT/PROCESS labels.
- **Constraint:** BBC text is third-party copyrighted → raw text stays local-only (`data/raw`, git-ignored); only derived annotations/statistics are committed.
- **Approver:** Kush (pending confirmation).

### D-004 · 2026-10-18 · Interpreter = `/opt/anaconda3/bin/python` (base); heavy ML (transformers/lightgbm) = `recsys_env`. No new venvs.
- **Approver:** standing user rule.

### D-005 · 2026-10-18 · Scrape Phenol-Explorer retention-factor pages (H2 for this one target)
- **Why:** retention factors (with per-publication before/after values, needed for DEL-1 study lineage and DEL-2 study-disjoint splits) are excluded from the bulk downloads.
- **Checks:** robots.txt has no disallow; terms = free resource, commercial use/redistribution needs permission, cite Phenol-Explorer + original publications. ~1,900 pages, 1.5 s spacing, cached, never re-fetched.
- **Storage:** raw HTML local-only (`data/raw/`, git-ignored); derived EVD rows committed with citation; SRC storage_rule DERIVED_ONLY.
- **Approver:** Kush ("if possible you can scrape", 2026-10-18).

### D-006 · 2026-10-18 · FDC crosswalk is CANDIDATE-only; FDC portions become POR- records only after human verification
- **Why:** an ING↔FDC link decides which food's gram weights apply; a wrong link invents grams. Top-1 HIGH covers 550 concepts / 67% of recipe-frequency weight, so ~1–2 h of human ticking lifts sourced mass coverage ≈30% → ≈55% of BBC lines.
- **Also:** UK→US synonym table and polysemy list are AI-drafted linguistic aids, flagged for review.
- **Network note:** home router DNS returns SERVFAIL for *.usda.gov; downloads used public-DNS-resolved IP pinning (`curl --resolve`). Not a site block.
- **Approver:** Claude (process); humans own each link decision.

### D-007 · 2026-10-18 · Gold files and adjudication sheets stay out of git (they contain BBC recipe text)
- **Why:** third-party copyrighted text (D-003). Templates/gold live in `annotation/gold/` (git-ignored); share between Kush and Parv via private drive/zip. Committed: handbook, schema, examples (synthetic), agreement reports, derived metrics.
- **Also:** gold recipe IDs are A1 `recipe_id`s (mapped by URL), not raw-file line numbers (they differ for 11,980/11,983 rows).
- **Approver:** Claude (reversible; confirm with Kush/Parv).

### D-008 · 2026-10-18 · Benchmark task types (proposal says "8 task types" but never names them) — PROPOSED
- T1 CURRENT_STATE (H1) · T2 NEXT_ACTION (H1) · T3 PROCESS_EFFECT_DIRECT (H2/H3) · T4 COMPARE_PROCESSES (H2, mode COMPARE)
  · T5 UNSUPPORTED_MUST_ABSTAIN (H3, mode ABSTAIN) · T6 FEASIBILITY_CONSTRAINTS (H4: tools/allergens/time)
  · T7 DIAGNOSE_RECOVER (H4: state divergence, e.g. "boiled instead of browned") · T8 ASK_CLARIFY (VOI, mode ASK).
- Covers H1–H4 and all decision modes (RECOMMEND inside T6/T7). Registry fields per plan AI6.
- **Approver:** Kush + Parv to confirm before authoring starts.
- **REVISED 2026-10-18 (SUPERSEDES the list above): follow SSOT §12, which names 9 Project-A tasks.** Course contract says
  "8 task types", so one merge is needed. Proposal: T1 CURRENT_STATE · T2 NEXT_ACTION · T3 TRANSFORMATION_EXPLANATION
  ("why brown the onions?") · T4 PROCESS_SUBSTITUTION · T5 ADAPTATION (SSOT T5 equipment + T6 ingredient, both via the
  feasibility filter) · T6 MISTAKE_RECOVERY · T7 PROCESS_COMPARISON · T8 CHEMISTRY_RELEVANCE (relevance gate, SSOT §7).
  Evidence regimes are slices across all types, not types: DIRECT / NEAR / UNSUPPORTED (must ABSTAIN) / CONFLICT /
  AMBIGUOUS (must ASK) — plan AI9 "covering all task types and evidence regimes"; §245.1 CONF/DEC families.
  Open for Kush/Parv: which two SSOT tasks to merge (proposal: equipment + ingredient adaptation).

### D-009 · 2026-10-18 · Open-resource expansion, done sequentially (Kush: "web, cookbooks, websites, scrapers … sequentially")
- **Approved source classes (H2 satisfied by Kush's request):** open ontologies/taxonomies (FoodOn CC BY 4.0, Open Food Facts taxonomy ODbL,
  Wikidata CC0), openly licensed recipe wikis via official API (Wikibooks Cookbook CC BY-SA), public-domain books (Project Gutenberg),
  open-access retention tables (e.g. Bognár 2002 / OpenAgrar), schema.org recipe markup via `recipe-scrapers` (GitHub hhursev) **only on sites whose
  robots.txt allows it**, polite rate (≥ 2 s/page), raw text local only.
- **Not allowed:** 403/paywall circumvention, login-walled datasets without a human accepting terms (RecipeNLG, Kaggle), pirated books.
- **Order (one at a time, each validated + committed + logged):** X1 FoodOn crosswalk → X2 OFF taxonomy aliases → X3 Wikibooks recipes →
  X4 Gutenberg cookbooks (procedures/tools) → X5 Bognár retention table (PDF table extraction) → X6 Wikidata kitchenware → X7 recipe-scrapers
  (Indian + world sites, robots-checked) → X8 SOTA ingredient NER on A100 (VPN) over all recipe sources.
- **Approver:** Kush.

### D-010 · 2026-10-18 · Ledger version timestamps
- Before S035, `LedgerStore.upsert` revisions inherited the record's original `created_at`; from S035 every new version gets its own timestamp.
- Older history is not rewritten (append-only). Version number is the authoritative order; pre-S035 `created_at` on v≥2 means "v1 time".
- **Approver:** Claude (bug fix; Kush/Parv informed via WORKLOG).

### D-011 · 2026-10-18 · KGE ledger: typed concept-level edges with support + confidence (Kush: "link confidence, usage support, categories, timers")
- New record type `KGE` (13 predicates: categories, parent, processed-by, co-occurs, cuisine, unit, component, proc↔tool, proc→next proc, typical duration/temperature, family).
- Association confidence = 95% Wilson lower bound of P(object|subject); bands HIGH (support ≥ 30, lift ≥ 2) / MEDIUM (≥ 10, ≥ 1.5) / LOW. Quantile edges: n/(n+20).
- LLM-proposed edges can never be HIGH without human verification (rule_kge).
- **Approver:** Claude (schema addition; Kush/Parv to confirm).

### D-012 · 2026-10-18 · Gutenberg recipes are silver; ledger file size watch
- Gutenberg REC come from heuristic segmentation of free text (measured precision ≈ 80–85% on 30-sample after
  index/menu/non-food/date filters). They are recipe *candidates* for procedure/tool/verb statistics, not Gold.
- `ledgers/data/REC.jsonl` is ~54 MB after X4. GitHub rejects files > 100 MB: before H7 push, if any ledger file
  exceeds 90 MB, shard by source family (`REC.<family>.jsonl`) or move to git-lfs (decide then).
- **Approver:** Claude (Kush/Parv to confirm before push).

### D-013 · 2026-10-18 · Stated temperature bounds are CENSORED, not exact
- Text such as "core temperature > 75 °C" or "stored below 4 °C" was extracted as MEASURED 75 / 4 (16 of 555
  temperatures in evidence texts). New censor kinds `GT_STATED` / `LT_STATED` (shared QVALUE enum) record a bound
  the source states; the qualifier stays in `raw`. Approximations ("~ 66 °C", "around 100°C") stay MEASURED with the
  qualifier in `raw`. Completeness mask maps CENSORED → RANGE (half-open interval). KG timer/temperature quantiles
  use MEASURED/RANGE only. "min"/"max" are not qualifiers ("10 min 100 °C").
- Builders that rewrite EVD from source keep link_evidence / review-owned fields (`keep_linker_fields`); found
  when an ingest_bognar rerun cleared 6,594 process links and 2,251 ingredient links (repaired by link_evidence).
- **Approver:** Claude (Kush/Parv to confirm).

### D-014 · 2026-10-18 · Ingredient-link review signed off by Kush (bulk, on the AI pre-check)
- **What:** all 389 MEDIUM/NONE-band EVD matrices in `registry/evidence/evd_ingredient_link_review_AI_prechecked.csv`
  carry `human_decision` = the AI recommendation, reviewer Kush, 2026-10-18. Kush confirmed in session
  ("Yes, sign off as Kush") after the AI + human consensus review; the basis is stored per row
  (`human_signoff_basis`). Claude did not re-verify rows individually.
- **Effect:** ACCEPT/CORRECT -> LINK (237 matrices, 2,806 EVD rows linked); HOLD_* / UNRESOLVED -> stay unlinked
  (129: categories, multi-matrix rows, composite dishes); 23 LINK rows whose concept is not in the ING registry
  (hare, plaice, bilberry, meat loaf …) are CONCEPT_MISSING: recorded, not linked, no concepts minted.
- **Mechanism:** `tools/apply_link_review.py` -> `registry/evidence/evd_ingredient_link_decisions.csv`;
  `tools/link_evidence.py` applies LINKED decisions on every run (idempotent; second pass writes nothing).
  The EVD schema is unchanged; link provenance for these rows is the decisions file.
- **Approver:** Kush.

### D-015 · 2026-10-19 · CoSyLab unlicensed datasets: use permitted by Prof. Bagler (reported by Kush)
Kush reports that when the project was accepted Prof. Bagler said CoSyLab resources may be used. No written licence exists on RecipeDB2, spice-disease-associations, SweetpredDB, SustainableFoodDB, or the RecipeDB3 NER repo. Recorded as `licence_status: ASSUMED`, `storage_rule: DERIVED_ONLY` (derived edges in ledgers; raw files stay in gitignored `data/external/`). Supersedes the S088 revert for these sources. Still no GitHub push before H7; the H1 email asks for written confirmation. AI recorded this from Kush's statement; it is not independently verified.

### D-016 · 2026-10-19 · pilot_20 Kush set is AI-assisted and human-reviewed; Parv's pass stays blind (decided by Kush)
OpenAI GPT-5.6 Sol drafted all 20 pilot_20 annotations (`annotation/ai_review/pilot_20/`, self-declared `blind_human_gold=false`). Kush read them and accepted them as his set; the coding agent converted them mechanically to gold-1.0 (`tools/convert_ai_review.py`, every judgment call in `conversion_log.csv`: draft event model → handbook Merge/Split/Transform, RECOMBINE "serve with" → Merge, whole-item RESERVE not written, unresolved references, coref targets → UNKNOWN). Kush's 20 files are `DONE` with `notes` marker `AI_DRAFT_HUMAN_REVIEWED`; corrections Kush sends later are applied as logged human corrections. Parv annotates the 7 calibration recipes independently and must not see the draft or Kush's set; Parv's folder holds blank drafts. Consequence stated in the agreement output: Kush-vs-Parv is "concordance with an AI-assisted set", not inter-annotator agreement. Gold-v1 is labelled AI-assisted pilot/development Gold; a publication-grade Gold needs a fresh blind human pass on unseen recipes.

### D-017 · 2026-10-19 · Gold-v1 pilot_20 frozen as AI-assisted, human-reviewed development Gold (decided by Kush)
Parv delegated his review of the AI-assisted set to Kush, who checked it on Parv's list and reported it good (Kush's statement). Parv's 20 files are therefore the same content as Kush's (annotator Parv, status DONE, notes say who reviewed); the 20 adjudicated files are the same again. Consequences recorded: (1) Kush-vs-Parv agreement is 1.0 by construction and is **not** inter-annotator agreement; the runner labels it NOT_INDEPENDENT; (2) the S102 handbook gate is NOT_EVALUATED, no calibration information was obtained, handbook stays v1 + Addendum A; (3) adjudication is vacuous; (4) Gold-v1 is a development reference, not a test set and not publication-grade Gold; a blind independent pass on unseen recipes is still needed for any claim that depends on annotation quality; (5) known artefacts (13 unconverted draft events, padded remainders, 108/113 coref UNKNOWN) are listed in `reports/del3/ai_review_conversion_v1.md` and `compiler_vs_gold_v1.md`. Manifest: `annotation/gold/gold_v1_pilot_manifest.csv`.

### D-018 · 2026-10-22 · ES-1.1: EVD export implements the MP-1 contract; ruling C1 applied (decided by Kush; implemented by the coding agent)
Evidence tier, verification status, design strength and provenance class are four separate export fields (`evidence_tier`, `verification_status`, `design_strength`, `provenance_class`). A human review never changes the tier or erases design metadata; E3 database aggregates are never promoted to E1/E2; E1-E7 ontology unchanged. Implementation choices within the contract: (1) `delta_value` and `log_fold_change` only from MEASURED, uncensored, same-unit before/after values (log needs both > 0); (2) retention rows get a **separate** `log_retention_factor` = ln(reported MEASURED retention > 0), not `log_fold_change`, because a reported retention factor may include a yield correction or be apparent (conflict C4; 278 of 3,859 Phenol-Explorer rows deviate from after/before x yield by > 0.02); (3) `lod`/`loq` are null everywhere (the sources record only GT_CAP caps); (4) `prior_state_id` and `matrix_id` are hashes of the normalised raw descriptors with reversible lookup tables (controlled vocabulary pending); (5) the 11 duplicate SVAR pairs are a provisional name-rule mapping (`registry/svar_duplicate_mapping_v1.csv`), both ids kept per row, 7 equivalent-candidates are not merged; (6) the 37 MB export is derived and git-ignored, identified by sha256 in `exports/evd/evd_export_v1.manifest.json`. Gate: PASS (`reports/es1/es1_1_audit.md`). No evidence acquired, verified or edited.

### D-019 · 2026-10-22 · ES-1.2: source census rules (decided by Kush's instruction; implemented by the coding agent)
Research and planning only: no source acquired, scraped, ingested or verified. Rules applied: (1) licence/access status is never inferred; each entry records its verification level (`licence_verification`) and unconfirmed ones are marked UNVERIFIED / UNKNOWN / CONFLICT / BLOCKED_LICENSE / BLOCKED_ACCESS; (2) recipe, ontology, molecular identity and measured evidence are separate planes and the capability matrix credits only documented capabilities (`capability_basis` records whether a row was inspected locally); (3) priority classes P0/P1/P2/PARK/BLOCKED plus EXISTING for ingested sources, with seven separate scores and no composite; (4) Europe PMC hit counts are metadata-only discovery indicators (upper bounds; relevance and per-article licence unassessed); (5) 21 actions are isolated in the H2 queue; (6) `reports/ner/ner_program_closeout.md` moved to `docs/BACKLOG_NONBLOCKING.md`. Outcome: 64 sources; structured open sources for mechanism/kinetic/physical time series not found (SOURCE_GAP for 13 of 16 priority-cell rows; literature route available); 34% of manifest cells are UNKNOWN by design.

### D-020 · 2026-10-22 · Step 07: condition and measurement normalization; NER status correction (decided by Kush's instruction; implemented by the coding agent)
Canonical condition representation (POINT/INTERVAL/TRAJECTORY/QUALITATIVE/UNKNOWN) and a deterministic normalizer with VALID/INVALID/AMBIGUOUS/UNKNOWN + reason codes; ten controlled vocabularies with stable ids (raw strings always kept). Choices: gauge/absolute pressure must be stated in the unit text (bare psi = AMBIGUOUS, no atmospheric assumption); temperature locations are separate variables and UNSPECIFIED is never promoted; qualitative terms need an explicit sourced mapping; reversed intervals are INVALID, never swapped; basis and retention types are non-combinable unless identical and informative; Phenol-Explorer retention type recorded as yield-adjusted (RT-003) but AMBIGUOUS pending a primary-source check; the 278 retention discrepancies stay an audit signal. Current data (4,414 conditions) normalised read-only with 0 INVALID; ledgers unchanged. Human sub-gate (100-condition audit, kappa >= 0.8) PENDING. Status correction recorded: NER v1, linker D3 and span CSD-C are CLOSED/FROZEN; Steps 16-17 reuse them for instruction/event semantics only.

### D-021 · 2026-10-22 · Step 07 normaliser fixes after reading returned audit files (decided by Kush; implemented by the coding agent)
The returned v1 audit files were not accepted as the human sub-gate (provenance unconfirmed; near-identical Kush/Parv field columns; Kush_REVIEWED contradicts both), but the flagged cases were checked against the raw strings and were genuine: (1) raw text present but unparsed was reported as NOT_STATED -> now AMBIGUOUS RAW_TEXT_PRESENT_BUT_NOT_PARSED; (2) slash durations ("45/75MIN") read as VALID intervals -> AMBIGUOUS SLASH_NOTATION_RANGE_OR_ALTERNATIVES; (3) spaced-dash temperature fragments -> AMBIGUOUS; (4) repeated values at one temperature location -> AMBIGUOUS MULTIPLE_VALUES_SAME_LOCATION. The five power "errors" were a packet display defect (v1 lacked normalised power/medium columns); packet v2 fixes it. Source rows unchanged. The kappa >= 0.8 gate remains PENDING on a fresh blind human pass over packet v2.

## D-022 (Step 07) Notation-rule registry
Normaliser notation handling moved from hard-coded regexes to `registry/notation_rule_registry_v1.csv` (13 rules mined from COND raw strings). Executed actions: FLAG (slash numbers, spaced dash), QUALIFY (~/approx/around -> `approximate=True`, value kept), SPLIT (`;` duration lists -> `components`, roles unknown, AMBIGUOUS). INFO rows (negative sign, dash range, `>`/`<`, USDA abbreviations, `+`, `BKD/SIMMRD`, pressure units) document meaning only; USDA expansions stay UNKNOWN_UNVERIFIED until checked against USDA documentation. No source rows changed; no new value type. Human 100-condition audit κ gate still pending.

### D-023 · 2026-10-22 · Step 07H: production hardening of the condition normalizer (bounded completion substep of Step 07; decided by Kush's instruction)
Three layers: raw parser (`condition_parser.py`, syntax only) -> semantic normalizer (`condition_normalizer.py` + `condition_units.py` + bounds registry) -> source dialect adapter (`source_dialect.py` + `registry/source_dialect_mapping_registry_v1.csv`, statuses VERIFIED/CANDIDATE/UNVERIFIED/DEPRECATED). Fixes: censor/open-bound flags were reversed (`> x` is now low=x, open_low=True; GE/LE closed; unknown censor kinds are AMBIGUOUS, never guessed); month/year are calendar durations, never converted to seconds; hard bounds (INVALID, PHYSICALLY_IMPOSSIBLE) separated from plausibility bounds (AMBIGUOUS, OUTSIDE_TYPICAL_CULINARY_RANGE) in `condition_variable_bounds_registry_v1.csv` -- pH 0-14 is plausibility only; trajectories normalise every point inside the normalizer (no caller bypass; common time axis; location required); uncertainty kept separate from range; pressure DIFFERENTIAL added, negative unspecified-reference pressure AMBIGUOUS not INVALID; psi factor exact; unknown temperature unit now INVALID instead of raising (found by property test); strict JSON schema (additionalProperties false, conditional contracts). Pint evaluated and NOT adopted as a runtime dependency (installed only as an independent test oracle); Hypothesis added for property tests (both installed into the base env). USDA abbreviations stay UNVERIFIED. `<` rule kept despite zero current hits. Human packet v3 supersedes v1/v2; normalizer frozen before review. Source ledgers untouched.

### D-024 · 2026-10-22 · STEP 07H-R: full recipe-base consolidation, ledger synchronisation, parser freeze (decided by Kush's instruction; implemented by the coding agent)
**Correction:** the "107,760 recipes" figure counted REC history lines; unique recipe ids are 89,565 (A1/BBC 11,934; Wikibooks 3,676; Gutenberg segments 73,955; 18,195 extra version-2 lines). **Canonical base** `ledgers/recipe_base/recipe_base_v1.parquet` = 612,782 indexed members: those 89,565 REC ids + 522,517 Food.com recipes (local parquet, not in REC; CC0 declared by uploader, authority unverified, local-only) + 700 TASTEset recipes; REC stays immutable, the base holds pointers + hashes. Food.com/TASTEset have no SRC rows -> `source_id=UNREGISTERED:*` and an H2 approval item (no licence assumption). 177 REC Gutenberg ids have no raw segment in the local interim file -> kept as members flagged RAW_SEGMENT_MISSING_LOCALLY.
**Tiers:** SOURCE_RAW 600,828; SILVER_AUTO 11,914 (A1 recipes with existing model/rule annotations, unverified); GOLD_PENDING_INDEPENDENT_IAA 40 (20 A1 pilot + 20 Food.com; all AI-drafted + human-reviewed, D-016/D-017, NOT independent); no DEEP_GOLD / GOLD_LIGHT. Parsing success never promotes. 10 further Food.com Gold-expansion candidates are indexed as GOLD_CANDIDATE_SCREENED_NOT_ANNOTATED (tier stays SOURCE_RAW). Sealed linker sets were not read. 7 of 40 Gold recipes have a bulk-corpus exact-title twin (leakage proxy; NO split frozen).
**Derived recipe ledgers** (local parquet, git-ignored; hashes committed): expression probe (8.17M candidate expressions, normalised with the final 07H parser/normalizer; `source_plane=RECIPE`, `observation_class=TEXT_STATED`, no E-tier), condition mentions, ingredient mentions (exact-alias link status only; the frozen NER/linker/router were NOT re-run -- needs a GPU-server run), quantity mentions (EXISTING `quantity.grammar` v0, locale-aware, q_levels, no CQPO preemption), process mentions (PROC verb-form candidates, POS unchecked; unknown -> UNMAPPED), simulation-readiness (text availability only, not permission to simulate), vocab corpus-frequency index (ING/PROC/UNIT counts; canonical vocab ledgers unchanged). DATASET ledger populated with 5 recipe-corpus releases (append-only). EVT/STATE/ENTITY/INST/QNT/POR/SPLIT/RXN/KINETIC/SIM not created (BLOCKED_FUTURE_STEP); EVD/COND/MEAS/SVAR/REC/SRC/ING/ALIAS/PROC/TOOL/UNIT byte-identical.
**Parser (two passes + final fix):** pass 1 ranked failures; deterministic-syntax fixes only (bare `350°`/`350 degrees` -> TEMPERATURE_SCALE_NOT_STATED, `degrees Fahrenheit`, `8″`, `watts`, compound `1 hr 30 mins`, vulgar/mixed/hyphen/simple fractions, U+2044, `to10`, false temperature `1/2 c.`); calendar-at-ingest guard (956 conditions whose ledger stored months/years as fixed seconds are now AMBIGUOUS, raw preserved); remaining ambiguity is semantic by design (tsp/tbsp/cup not converted in the expression ledger, multi-dimension sizes, calendar months, no stated location/scale, bare psi). Gas marks never numerically mapped; USDA abbreviations stay UNVERIFIED. The two returned v3 audit files were not used (provenance); packet v4 supersedes v1-v3.

### D-025 · 2026-10-22 · STEP 07I-R: identity recovery, plan consensus, memory-safe pipeline (decided by Kush's instruction; implemented by the coding agent)
**Plan consensus:** SSOT v15 (257A.15, 264, 192.5) + Master Plan v4.0 + Detailed Plan v2 + Parv's `parv-origin/main` (separate history, no merge-base) agree on: exact hashes first; near-duplicates are candidates until calibrated (no universal threshold); families provisional; groups lock splits. Conflicts found: all IMPLEMENTATION_DETAIL or STALE_PLAN (see `reports/step07i/max_plan_consensus.md`); no SSOT_CONFLICT.
**Failure:** the 8.64M-pair scoring stage of the old single-script run held O(P) Python objects in a forked pool; verdict LIKELY_MEMORY_PRESSURE + LIKELY_SWAP_THRASHING (not proven OOM). **Fix:** phased pipeline `tools/step07i_identity.py` (`src/culinarystate/identity/*`), partitions <= 100k pairs, per-partition atomic outputs, manifest `ledgers/recipe_identity/run_manifests/step07i_identity_run_v1.json`, memory guard exit 75. Measured peak 1.91 GB for the whole run; sample output bit-identical to the old logic.
**Ledger policy:** the frozen 07H-R `recipe_base_v1.parquet` is NOT rewritten (the earlier consensus tool did); identity foreign keys are the join table `ledgers/recipe_identity/recipe_identity_fk_v1.parquet`. No near-duplicate is coalesced; family method `PROVISIONAL_STAR_V1`, `calibrated=false`. The 400-pair duplicate calibration packet is created and UNLABELED. Step 08 remains unauthorised; the Step-07 condition packet v4 is untouched.
**Not done / open:** A100 replicate (VPN throughput 13-90 KB/s made pushing 300 MB impractical; the Mac completed in minutes); `sustainablefooddb` ingredient-list corpus (118,083) left un-indexed (SCOPE_CHANGE_REQUIRED).

### D-026 · 2026-10-22 · Recipe-source usage: owner decision to treat all 612,782 recipes as usable for project use (decided by Kush's instruction)
**Decision:** all five source families in the frozen 07H-R base (A1/BBC 11,934; Food.com 522,517; Gutenberg 73,955; Wikibooks 3,676; TASTEset 700; total 612,782) are marked `USABLE_FOR_PROJECT_USE` (training, local analysis, derived statistics). Recorded in the overlay `registry/recipe_usage_owner_decision_v1.csv`.
**Basis:** Kush's statement that the sources are verified and there is no usage issue. This is an owner assertion; the agent did NOT independently verify licences (no licence terms were re-read). It resolves the H2 "use" question only.
**Not changed:** `registry/recipe_source_usage_registry_v1.csv` and the frozen `recipe_base_v1.parquet` (usage_class / licence_status / local_only stay as frozen, so the 07H-R freeze manifest still verifies). Raw/derived REDISTRIBUTION is not asserted: the registry's redistribution columns stay in force (BBC and Food.com raw = NO), so nothing third-party goes into a public release without a separate decision.
**Open:** the TASTEset MIT-vs-unverified inconsistency and the CoSyLab / Phenol-Explorer permissions are untouched by this decision.

### D-027 · 2026-10-26 · Execution Plan v2: original 36-step spine governs; audit v2 adopted only as listed; Step-08 dependency/lineage ruling (decided by Kush; reconciled by the coding agent)
- **Decision:** The original 36-step execution spine is the governing plan (numbering preserved). The Master Plan Research & Architecture Audit v2 (`reports/master_plan/master_plan_research_audit_v2.md`) is a PROPOSED research/amendment layer, NOT approved verbatim; only rulings R-01..R-20 (`docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md` §0) are adopted.
- **Step-08 ruling (07-DEP):** the Step-07 human condition audit is a SOFT dependency of Step 08 and remains a HARD gate before condition-dependent scientific use (Steps 15, 23, 26d/27, 29–33). The Step-07 gate is unchanged: pooled Cohen's κ ≥ 0.80 AND no systematic critical-field failure; PABAK/AC1/raw agreement/prevalence are diagnostics only. Frozen packet v4 is not altered (any change = new version).
- **Lineage ruling:** Step-04 lineage extension adopted as an additive v1.1 contract: SRC → DOC → STUDY → SEXP → SMP → OBS → AGG/DRV, typed lineage edges, separate `study_id`, `lineage_root_id`, `split_group_id`. Kinetic/trajectory schema adopted before Step 09/11. Step 08 split into 08a (lineage resolution for the existing 17,978 EVD rows) and 08b (reusable lineage/dedup library for Steps 11–14).
- **Other rulings:** 07I-C identity calibration + recall-oriented `split_group_id` (no destructive merges; no thresholds chosen for corpus size); Steps 12/13/21/35-explicit parallel where inputs exist; Step 25 kept numbered, may be implemented in a 24/25 package; Step 29 earlier only as a diagnostic on frozen bootstrap data; Step 28 deferred until a simulator passes real held-out validation; SIM-AA-1 = leading candidate, chlorophyll = preregistered fallback, final choice after Step 10/11 evidence; applicability three-valued (UNKNOWN never → SIMULATE); Step 35 explicit-first with nine distinct similarity notions; only the design/pilot of Deep Gold moves earlier; no breaking Step-36 schema migrations; negative results and core laws preserved.
- **Options considered:** (a) adopt audit v2 verbatim; (b) keep original plan unchanged; (c) original spine + selected additive amendments (chosen).
- **Evidence:** audit v2 Parts A/E; `reports/step07/step07h_human_gate_result.json` (NOT_COUNTED_PROVENANCE_INVALID); STUDY ledger 125 rows `design=UNKNOWN`; EVD endpoint-only; 400-pair identity packet unlabeled.
- **Note on numbering:** written on server branch `plan/v2-reconciliation` where D-026 was absent; on merge it follows the Mac D-026 (recipe-usage decision) unchanged.
- **Step 08 NOT started by this decision;** next authorised implementation step is defined in Plan v2 §7.
- **Scope of authorisation:** Plan v2 §7 items are authorised only as contract/documentation work (Step 04 v1.1 contracts and schema drafts, 01.6 threshold pre-registration with PROPOSED_PILOT values, 02.4 negative-results register, archive of the v3 agreement output). Step 08a requires Kush's separate explicit authorisation. Step-07 gate reading confirmed against `tools/step07_agreement.py` L5/L68/L85 and `reports/step07/condition_audit_protocol.md` L25: the preregistered critical-field flag (per-field κ<0.8 unless prevalence≥0.95, raw agreement<0.9, or a repeated disagreement pair) is PART of the unchanged gate; only PABAK/AC1 and other added statistics are diagnostics.
- **Approver:** Kush.

### D-029 · 2026-10-26 · H4 approval: Step 04.1 lineage, 04.2-min value documentation, 04.6-min data planes, 04.9-min namespaces (decided by Kush; entered by the coding agent as scribe)
- **Decision:** approved as drafted in `reports/step04/` (answers 4-26 in `docs/plan/H4_ANSWERS_LOG.md`). 04.1: entity chain SRC > DOC > STUDY > SEXP > SMP > OBS > AGG/DRV with typed edges; D-2 AGG/DRV as export-v2 fields (no separate ledgers); D-3 reserve LROOT-, CGRID-, DFORM-; D-4 same-lab grouping optional, shared-reference grouping default; D-5 UNKNOWN independence = TRAIN-only; D-6 port schemas into `registry.py` at 08a; D-8 unidentifiable-member aggregate = one lineage root per release; D-9 STUDY authoritative for DOC-STUDY links; D-10 Phenol-Explorer = PUBLICATION_ONLY; D-11 DOC key `<src_id>|sha256:<hex>`; D-12 hub rule; D-13 UNKNOWN leakage screen plus sensitivity run; D-14 giant-component rule (largest share <= 0.40, n_eff >= 10, weaker label wins); D-15 mandatory `lab_group_id` (UNKNOWN allowed), reserve LABGRP-, MBSET-; D-16 `retention_definition` split with evidence field; D-17 absent SEXP.context = UNKNOWN.
- **04.2-min:** field set and enumerations approved; censor ids CS-011..CS-014 added; lod/loq on OBS; bases MB-009..011 with alias settlements; digitisation record with two-read rule (THR-04K-03). Registry files `censoring_registry_v1_1.csv`, `value_origin_registry_v1_1.csv`, `measurement_basis_registry_v1_1.csv` to be created as drafts.
- **04.6-min:** six-plane codes; DOC in P-SRC; `ESTIMATED_FROM_SUMMARY` never a label or test value; PQ-1 ratified (`SPLITGRP-EVD-######` / `SPLITGRP-REC-######`, no cross-plane join); data-plane registry created now as DRAFT_PENDING_H4.
- **04.9-min:** the 13 prefixes reserved (including THR-, NEG-, MECH-, DGP-, TASK-); no KINETIC- prefix. AGG- / DRV- are minted only as export-view keys (follows D-2).
- **Not covered:** 04.3 kinetic/trajectory (needed before Step 09, not before 08a); D-7 numbers are covered by D-030. Parv has not reviewed; Kush approved alone.
- **Approver:** Kush.

### D-030 · 2026-10-26 · Step 08a.0 pre-registration signed: THR-08A-01..23 (decided by Kush; entered by the coding agent as scribe)
- **Decision:** the 23 rows `THR-08A-01..23` in `registry/preregistered_thresholds_v1.csv` are signed (`signed_by` Kush Tokas, `signed_at` 2026-10-26, status `PREREGISTERED_2026-10-26`). Rows 01-15 are the original plan's numbers, unchanged. Rows 16-18, 20, 21, 23 are the agent drafts, signed as written. Row 19 (UNKNOWN-row screen) value set as a rule: the loosest B3 score with seeded-copy recall >= 0.95 on scratch seeded data (same level as THR-08A-05), frozen before any real UNKNOWN row is screened. Row 22 (SAME_LAB_AS): N = 3 years.
- **Ruling:** `data_seen_before_registration = DESCRIPTIVE_COUNTS_SEEN` satisfies the Step 01.6 rule for these rows (only source-family group sizes were seen; no lineage component, edge or label was computed). No second signer required.
- **Not signed:** the other 24 rows (07.A, 07I-C, 04.3 and pilot rows) stay `DRAFT_PENDING_H4`.
- **Approver:** Kush.

### D-031 · 2026-10-26 · Step 08a execution environment, manifest, baseline hashes (decided by Kush; entered by the coding agent as scribe)
- **Environment:** 08a runs on the Mac (CPU, seconds to minutes); the vinayak server only if a run proves heavy (confirm VPN first). The Mac holds the authoritative ledgers and D-026.
- **Manifest:** `registry/data_source_acquisition_manifest_v1_1.csv` (planned 06.3-min) is NOT a precondition of 08a; the v1 manifest suffices.
- **Baseline hashes:** sha256 of the seven ledger files recorded in `registry/baseline_ledger_hashes_08a_v1.csv`. EVD, COND, SRC, MEAS match earlier recorded hashes; STUDY, SNAP and `_ids` are new baselines. Gate G08-5 (THR-08A-06) compares against this file.
- **Approver:** Kush.

### D-032 · 2026-10-26 · Written authorisation of Step 08a (decided by Kush)
- **Decision:** Step 08a (lineage resolution for the existing 17,978 EVD rows) is AUTHORISED. The coding agent implements the lineage library and runs 08a on the Mac. It writes only NEW files. EVD, COND, SRC and MEAS must stay byte-identical (THR-08A-06), checked against D-031's baseline hashes; STUDY is append-only. 07.A and 07I-C labels are not used (D-027 R-05: soft dependency). The run stops and reports on any failed gate; no gate is loosened (D-027 R-20).
- **Not authorised:** Step 08b, 07.A, 07I-C, 07I-S, any push to GitHub (H7).
- **Approver:** Kush (answer to the walk-through question, 2026-10-26).
- **Addendum 2026-10-26 (Kush, answers to the 08a scoping questions):** (1) 08a MAY edit `src/culinarystate/ledgers/registry.py` to port the DOC/LIN/SEXP/SMP/OBS schemas (D-029 D-6) and regenerate `ledgers/schemas`; the edit is tested and touches no ledger data file. (2) The real run MAY append new ids to `ledgers/data/_ids.jsonl`, after a full dry run on a scratch copy whose counts are shown to Kush before the real run.

### D-033 · 2026-10-27 · 07I-C agreement figure 0.88 on the adjudicated Kush-basis labels (decided by Kush; entered by the coding agent as scribe)
- **Decision:** Kush states that the agreed 07I-C agreement score is 0.88, on the adjudicated label set (Kush's labels, Parv's after-the-fact agreement). 07I-C proceeds on that basis for calibration and operating-point work (THR-07IC-05..08) and for the Step 35 recipe/cuisine freeze dependency.
- **Recorded as stated, not computed:** no file in the repo produces 0.88; the coding agent did not compute it. It is a Kush-declared adjudicated-basis figure, not an inter-reviewer kappa (agreement with Kush's own labels is 1.0 by construction).
- **Kept unchanged:** the original blind-label values in `reports/step07i/step07ic_reviewer_agreement_v1.json` (Y_copy kappa 0.571, Y_dish 0.588) stay in the record and in any report next to this figure. Single-reviewer-basis caveat carries into reports.
- **Approver:** Kush (message of 2026-10-27).

### D-034 · 2026-10-27 · B3 cut stays at 0.75 after the edge audit; G08-3 recorded as FAIL (decided by Kush; entered by the coding agent as scribe)
- **Decision:** the B3 detector cut stays at 0.75 (frozen on seeded recall, `detectors.py`). No retune, no change to the signed THR-08A-03/04/16 thresholds.
- **Audit result stays as scored:** `reports/step08/step08a_audit_result_v2.json` (Parv rechecked files). G08-3 = FAIL: B3 correct 13/50 (Kush) and 0/50 (Parv; 14 UNCERTAIN, 2 NOT_SUPPORTED); B2 49/50 (Kush, Wilson lower 0.895) and 0/50 correct (Parv; 49 UNCERTAIN); STRONG 50/50 both. G08-H reviewer files valid after the code mapping. Unlinked-pair recall (report only): Kush 2/200, Parv 0/200.
- **Consequence:** B3 and B2 edges stay PROVISIONAL and merge conservatively (THR-08A-14); keys stay `SCRATCH_PROVISIONAL`; no claim that depends on G08-3 passing (Step 08a "PASS", study-disjoint labels) may be made. R-20: no gate loosened.
- **Approver:** Kush (message of 2026-10-27).

### D-035 · 2026-10-27 · Written authorisation of Step 08b-v0 (decided by Kush; entered by the coding agent as scribe)
- **Decision:** Step 08b-v0 is AUTHORISED as drafted in `docs/plan/D-035_DRAFT_08b_authorisation.md`: reusable lineage/dedup library (API `register_document`, `propose_edges`, `assign_keys`, `check_disjointness`; hashed `rule_version` on every output; offline, deterministic, bounded memory; seeded fixture; no precision/recall claim). Mac, CPU only; new files only; 08a detector code reused unchanged. Basis: 04.1 approved in D-029.
- **Answers to the six draft questions (Kush: "yes all authorisation", read as yes to the recommended answers):** (1) a G08-3 FAIL does NOT release 08b v1; (2) D-035 signed; (3) G08b-1, 2, 4 apply fully to v0 and G08b-3 as a fixture unit test only; (4) the G08b-3 threshold is the frozen B3 cut 0.75 (D-034); (5) 08b-v0 may wrap the 08a detector modules without editing them; (6) open numbers stay UNKNOWN except the fixture classes, which reuse the seven THR-08A-17 perturbation classes.
- **Gates:** THR-08B-01..04 signed with those readings; unknown values stay `NOT GIVEN IN PLAN` (no number invented). THR-08B-05 (v1 release) NOT signed.
- **Not authorised:** 08b v1 release; any edit to ledgers, `_ids`, `registry.py`, 08a detector modules, the B3 cut or signed THR-08A rows; wiring into Steps 10-14; 07.A, 07I-C, 07I-S; A100 use; any push (H7). No 08b-v0 output may be called detector precision/recall on real data or an 08a PASS.
- **Approver:** Kush (message of 2026-10-27).

### D-036 · 2026-10-27 · Food.com cuisine for Step 35 to be derived from Food.com tags (decided by Kush; entered by the coding agent as scribe)
- **Decision:** Food.com recipes (522,517, no `cuisine_if_explicit`) get a cuisine label derived from Food.com's own tags through a written, pre-registered tag-to-cuisine mapping (and cuisine-to-continent grouping), signed by Kush and Parv BEFORE any cuisine statistic is computed (Step 35.0, 35d). Not "leave Food.com out".
- **Rules carried in:** derived labels are flagged `DERIVED_FROM_TAG` and never mixed with explicit labels in one claim; recipes with no mappable tag stay `UNKNOWN` (not guessed); source confound (cuisine = website) controlled as in the 35.0 draft section 7; Food.com remains LOCAL research use only (H2 licence open, source UNREGISTERED).
- **Not decided here:** the mapping itself, the continent grouping, and the minimum tag support; these are drafted for review, unsigned.
- **Approver:** Kush (message of 2026-10-27, answering the option 1 / option 2 question).

### D-037 · 2026-10-27 · Pan-regional tags, text-strata computation, Gutenberg in the Deep-Gold pilot (decided by Kush by delegation; entered by the coding agent as scribe)
- **Decision (Kush: "yes ... do as better as you can think"):** (1) pan-regional Food.com tags (European, Asian, African, Caribbean, Southwestern U.S., Middle East and similar) are kept as continent/region-level labels only (`DERIVED_FROM_TAG`, cuisine UNKNOWN); they are used for continent analysis and never for single-cuisine analysis. (2) The four text-regex strata of the 16b frame (baking, drain_discard, reserve_split, multi_component) are computed locally on the Mac by the coding agent with fixed, saved regexes; only per-recipe stratum flags are written, never recipe text; no external LLM service reads recipe text. (3) Gutenberg stays excluded from the Deep-Gold pilot frame (no ingredient lines, matches the Step 19 draft); a separate text-only track is not opened.
- **Why delegated:** these are scope and mechanics choices inside the already-signed 35.0/16b design; the mapping itself and the strata regexes still go to Kush and Parv for review before any sample is drawn.
- **Not decided here:** the final lookup terms, the continent grouping, any sample draw, Step 19 start.
- **Approver:** Kush (message of 2026-10-27).

### D-038 · 2026-10-27 · `reserve_split` regex boundary bug: add a corrected twin, keep v1 (decided by Kush, "ok" to the fix recommendation; entered by the coding agent as scribe)
- **Decision:** the pilot stratum regex `\b(reserv|set aside|...)\b` never matches "reserve/reserved/reserving". A corrected column `reserve_split_v2` (`reserv\w*`) is added next to the unchanged v1 column in `registry/recipe_semantics/deep_gold_text_strata_v1_DRAFT.csv`.
- **Open:** which column the pilot draw uses stays a pre-registration choice before any sample is drawn (recommended: v2 for the pilot, v1 reported for comparability). Nothing has been drawn.
- **Approver:** Kush (message of 2026-10-27).

### D-039 · 2026-10-28 · Parv's Step 35 review choices and local toolkit preparation (UNSIGNED review; not G35-PRE approval)
- **Source:** Parv's reply: "D2 Approved D3 yes D4 yes d5 Go. Dont wait, but record the decision D6 Yes to both rules D7 yes to all D8 Yes". Detailed interpretation and remaining questions: `reports/step35/35_0_parv_review_DRAFT.md`.
- **Review choices:** D2 taste-label/confirmed-negative/source-control rules approved; deprecated-edge audit reviewer still pending. D3 banned-input and local-output stance accepted (H2 licence approval remains separate). D4 separate derived/explicit claims and source controls accepted, including a possibly empty headline set; specific mapping, conflict, continent, coverage and reviewer choices not answered. D6 descriptive-only until 07I-S and 0.80 linking floor accepted; crosswalk audit commitment not supplied. D7 all four proposed claim/profile rules accepted. D8 learned models stay deferred until explicit results and signed addendum. D1 remains the earlier choice (a), not a signature.
- **D5 action:** Parv explicitly directs proceeding without waiting, superseding the earlier session instruction reserving the toolkit choice to Kush. RDKit is already present in the existing Mac environment; pin its installed distribution version 2026.3.6 as optional project extra `step35`. Synthetic Morgan and Murcko checks pass. No dependency installation needed. This is Parv's instruction, not a claim of Kush approval. Environment evidence: `reports/step35/parv_toolkit_environment_2026-10-28.md`.
- **Still closed:** G35-PRE is unsigned; no real Step 35 evaluation, split, similarity, cuisine statistic or learned run is authorised. The current protocol bytes and unsigned hash remain unchanged. No signatures/override, human labels, licence approvals or threshold amendments supplied. Pilot column and Parv's own 07.A/07I-C confirmation remain pending. No push authorised.
- **Decision maker:** Parv (review answers and toolkit preparation only); protocol sign-off remains incomplete.

### D-040 · 2026-10-28 · Parv's cuisine lookup review, pilot-column draft and crosswalk audit ownership (single-reviewer; UNSIGNED)
- **Lookup rulings:** Tex Mex, Cajun, Pennsylvania Dutch and Native American -> REGION/Americas; Cantonese, Szechuan and Hunan -> REGION/Asia; Creole, Hawaiian and Jewish -> REGION/MIXED. All REGION rows carry cuisine UNKNOWN. American -> CUISINE/American/Americas. Georgian, Southern, Roman and Oriental -> UNKNOWN for cuisine, continent and level. These are Parv's explicit review choices, not agent-inferred labels. Exact rows: `registry/cuisine/cuisine_lookup_v1_DRAFT.csv`, basis `PARV_REVIEW_D040_*`.
- **REGION definition:** extends to below-country regions, following the existing D-037 Southwestern U.S. precedent. Unclear continent -> MIXED; unclear meaning -> UNKNOWN. The prior README's more-than-one-country definition is broadened in the draft; highlight this for Kush/expert review. Creole includes Louisiana/Caribbean/Indian Ocean ambiguity; Hawaiian retains US-state/Polynesia ambiguity. The cuisine expert is pending (plan expects 4-6 h); these are single-reviewer choices, not an expert sign-off.
- **Other cuisine choices:** accepts Middle East/Southwest Asia, Southwest Pacific and Mediterranean = REGION/MIXED; Polynesian = REGION/Oceania, without exceptions. Accepts the 20-recipe tag reporting cut and 12.9% mapped cuisine coverage with the limitation disclosed. Exclude conflicting-cuisine recipes from single-cuisine scoring while retaining their CONFLICTING flag and count; no scored CONFLICTING class. Draft local tag census may be rerun for review as in the takeover guide; no scored cuisine result authorised.
- **Pilot column (DRAFT_PENDING_KUSH):** Parv selects `reserve_split_v2`, retaining v1 for comparison. Record for Kush to confirm before any draw; no sample or Step 19 start/seal authorised. Strata/frame bytes unchanged.
- **Owners:** Parv owns the 50-crosswalk audit (D35-7, approximately 2 h), not yet done. Chemistry reviewer pending, Kush to arrange; Parv will not nominate someone who has not agreed. Cuisine expert also pending. Neither audit is treated as complete or waived.
- **Still pending:** Parv's own written 07.A/07I-C statement and Step 16 comments; he will review and write them himself. AI findings remain explicitly AI review. Protocol/mapping signatures and Kush's outstanding confirmations remain open; no override or real Step 35 evaluation supplied by these choices.
- **Decision maker:** Parv, explicit follow-up reply on 2026-10-28; single-reviewer draft mapping and pilot recommendation only.

### D-041 · 2026-10-28 · Parv requests AI expert-style precheck and conflict resolution (not human/expert sign-off)
- **Instruction:** Parv requests that the agent review the work, verify evidence, resolve inconsistencies and record results for later expert verification, with project completion as the objective. This authorises technical review and draft engineering corrections; it does not supply human labels, signatures or agreement statistics.
- **Evidence:** `reports/review/AI_REVIEW_2026-10-28.md`, `machine_evidence.json` and `project_completion_roadmap.md`. All 204 deprecated ChemTastesDB taste edges are source-backed free-text-to-class migrations; this is a provenance explanation, not expert confirmation of taste validity. All 307 reconstructed compound-linked crosswalks cover the same 298 ING as 29,656 active FlavorGraph PRESENCE rows. One name collision is queued separately alongside a local 50-crosswalk worksheet; human fields are blank.
- **Engineering corrections:** draft EVT family reference aligned to existing FAM: hierarchy roots (no ledger IDs minted); pure semantic review overlay exposes bounds, metadata, AST and referential gaps; recipe/cuisine helpers reject invalid mass/profile/ranking/support inputs; preregistration guard can bind and require companion-file hashes. Synthetic controls fail before and pass after fixes. Frozen schemas/ledgers, labels and thresholds untouched.
- **Scientific corrections proposed, not adopted:** molecule-level negative evidence must replace the draft's insufficient database-level negative rule; direct triplet NPMI scale needs an explicit convention. Exact proposals in `reports/review/protocol_review_addendum_DRAFT.md`. Parv's prior D1 answer is not retroactively treated as acceptance of these later amendments. Experts/H4 still resolve metadata/AST/history contracts and cuisine scope.
- **Gates unchanged:** Step 35 protocol and review package remain unsigned; no real benchmark, similarity, split, recipe/cuisine score, pilot draw, human annotation or licence approval performed. Human crosswalk/chemistry/cuisine reviews remain pending. G08-3 and 07.A failures stay on record; 08b-v1/16c/Step 19 gates remain closed. No push authorised.

### D-042 · 2026-10-28 · Parv authorises Step 16 metadata/quantity-AST implementation as reviewable drafts
- **Instruction:** Parv's "Go" follows the offer to continue the Step 16 metadata and quantity-AST contracts. This authorises implementation and synthetic checks, not H4 acceptance, human labels or a freeze.
- **Draft result:** separate QNT/STATE rc2 schemas, explicit per-claim metadata, typed payloads for all eleven AST node kinds, exact interval/fraction arithmetic, structured alternatives and JSON-safe rational results. Combined validation reports metadata gaps/conflicts, interval/order errors, invalid payloads and incompatible arithmetic without rewriting inputs. Full scope, code, synthetic examples and H4 choices: `reports/step16/metadata_quantity_contract_v2_DRAFT.md`.
- **Version boundary:** old rc1/frozen schemas, ledgers and normalisation path unchanged. rc2 is explicitly selected and pins 1.0.0-rc2; metadata is supplied, never inferred or backfilled. New values in demonstrations are synthetic, not Gold or real recipe annotations. Existing metadata enum membership and history-route restriction are preserved.
- **New legacy finding:** an explicit zero package multiplier is defaulted to one by the old normaliser; synthetic reproduction is recorded in the build note. New AST arithmetic handles zero correctly. A versioned normaliser/adapter correction is still needed before that legacy path is used for new extraction; no real recipe base was recomputed or incidence estimated.
- **Still pending:** H4 reviews coverage, payload and arithmetic/wire conventions; POR grounding, source verification, parsing/integration and history policy remain separate work. Step 19 human pilot precedes 16c. No pilot, Step 35 signature/evaluation, threshold amendment, expert acceptance, GPU work or push is authorised by this entry.

### D-043 · 2026-10-29 · Engineering/pilot preparation and delegated AI reviews
- **Instruction:** Parv requested both engineering and pilot lanes, delegating blocking review to agents and requiring their evidence, changes and recommendations to be preserved for later expert verification.
- **Delivered:** separate versioned normaliser fixes the zero-multiplier defect and masks invalid numeric/unit/overflow cases; conservative parsing-to-rc2 adapter preserves exact supported quantities and flags unsupported or precision-limited expressions. Legacy grammar/normaliser/catalogue unchanged. Six-stage synthetic pilot rehearsal, draft handbook, 17 synthetic hard cases and unsigned pilot start record prepared.
- **Agent evidence:** `reports/step16/rc2_independent_agent_review.md`, `reports/step19/pilot_readiness_and_ai_review.md`, `reports/step19/pilot_methods_agent_review.md`. Contract and adapter defects were reproduced, corrected by root and independently reverified. Pilot-method and handbook recommendations remain explicitly AI drafts, not signed scientific changes. Two subsequent Step 35 chemistry/cuisine follow-up reviews hit the service usage limit before producing reports; they are NOT completed reviews.
- **Limits:** no agent supplies a human signature, blind human annotation, verified scientific value or H4/H5 pass. The real pilot retains the v0/handbook-v1 measurement boundary pending an explicit version decision; no real frame/draw or recipe text processed. Pre-frame nonce/supplier, capacity and per-annotator budget requested and remain null in the start record. Existing gates/thresholds/labels/ledgers unchanged.
- **Verification:** 1681 unit tests passed, 1 skipped, 1 deselected (existing not-ledgers policy), with transition tests included. Full implementation and remaining work: `reports/step16/engineering_and_pilot_lane_build_note.md`.

### D-044 · 2026-10-29 · Parv requests publishing the prepared work on a new branch in Kush's repository
- **Instruction:** "Make a branch on Kush's repo and push changes on it". This explicit current instruction supersedes the earlier session restriction on pushing for this action. It is Parv's authorisation, not a claim that Kush personally approved.
- **Scope:** publish reviewed, committed code/tests/draft reports on a new branch of `kushiiitd05/culinarystate`; do not force-push, update remote main, merge, publish restricted source data or supply any scientific signature. Include the preceding local takeover commits and this prepared engineering/pilot work.
- **Branch:** `parv/engineering-pilot-prep-2026-10-29`. Remote outcome is recorded separately after the attempted publication; this decision itself is not evidence of a successful push.

### D-045 · 2026-11-03 · Working order: AI verdict first, then Kush and Parv review (decided by Kush; Parv's agreement relayed by Kush; entered by the coding agent as scribe)
- **Decision (Kush, 2026-11-03):** "the laws are decided by me and reviewed after the AI agents verdict and we got the permission from the prof ... after AI verdict me and parv will review and give the feedbacks and this is basically how we proceed in this order". Kush and Parv OK'd the workflow block W of `handoff/REVIEW_SHEET_AI_VERDICTS.md`.
- **W1:** every gate, choice and label first gets an AI agent verdict, labelled as AI; Kush and Parv then review it, and their review is final. AI worker labels "ksh"/"prv" are agents, not the humans.
- **W2:** annotations are first-pass AI labels reviewed by both humans, recorded as `MODEL_ASSISTED` with the AI pass and human edits kept separately; pilot agreement/timing is reported as "human review of AI drafts", not blind independent annotation (this changes the measurement the original Step 19 design assumed; reports must say so).
- **W3:** the course professor's permission for this workflow is as stated by Kush; no written copy is in the repository.
- **Unchanged:** historical failed gates (G08-3, 07.A) and earlier signed records stay as recorded; facts only a human can supply (nonce, capacity, budget) are not produced by any verdict.
- **Approver:** Kush (Parv relayed).

### D-046 · 2026-11-03 · Kush and Parv accept the S154/S155-17a AI verdicts and sign THR-19P-01..35 (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "the pendings you have are okked by parv and me - kush", applied to blocks W, A, B and C of `handoff/REVIEW_SHEET_AI_VERDICTS.md` (commit 6f267f6). Separately Kush relayed "parv said pass for the above file you gave me", recorded as Parv's pass on the S154 work (bundle and branch `cloud/s154-step16-integration-2026-11-03`).
- **Accepted as drafted:** A1–A7 (S154 build-note engineering choices); B1 instrument `CURRENT_V0_PLUS_HANDBOOK_V1_ADDENDUM_A`; B2 pilot column `reserve_split_v2` confirmed by Kush; B3 AI methods/readiness recommendations PM-01..12 / PR01..10 as the method ruling under D-045 W2; B4 draw spec `STEP19_P1_DRAW_SHA256_RANK_V1_DRAFT`; C1–C7 (S155 Step 17a open items).
- **B5 signed:** THR-19P-01..35 appended to `registry/preregistered_thresholds_v1.csv` exactly as the design Appendix A bytes bound in the start record (sha256 93d781cc…), status `PREREGISTERED_2026-11-03`, signed_by Kush Tokas; Parv Goyal (relayed), `data_seen_before_registration` unchanged. No existing row edited.
- **Not covered:** B6 (H5 start of wave P1) waits for N1 nonce (Kush), N2 weekly capacity and N3 budget B_h (both). Block D (S155 17b and prv's 17a review, R1–R7 / O1–O9) is pending Parv's review. The signed pilot start record is not yet written.
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-047 · 2026-11-03 · Kush and Parv accept S155 (block D) (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "all given files seen and reviewed by parv ok and mine are also okay and passed". The files given were the S154 bundle, `reports/step17/S155_17a_ai_review.md` and the S155 bundle (branch `cloud/s155-step17ab`, head d026b80).
- **Accepted as drafted (block D of `handoff/REVIEW_SHEET_AI_VERDICTS.md`):** D1, prv's fixes R1–R7 to the 17a code, confirmed. D2, O1–O9 kept as currently implemented and documented, so the listed open behaviours stand as draft behaviour until H4/16c. D3, the Rung A draft choices. D4, lexicon gaps stay gaps and no entries are invented. S155 work passed by both.
- **Still not supplied:** N1 pilot nonce (Kush), N2 weekly capacity and N3 budget B_h (Kush and Parv). An "ok" cannot stand in for these values, so B6/H5 and the signed pilot start record still wait. Real-data dry-runs (S154, S155) have still not been run.
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-048 · 2026-11-03 · H5: Step 19 pilot wave P1 authorised; signed start record written (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** block B6 ("authorise wave P1 once N1–N3 are supplied"), OK'd by both (D-046). Kush then supplied N2/N3: "Kush 15h/week budget 40h; Parv 15h/week budget 40h" ("we can spend 15-20 hrs per week"). N1 strings were supplied by both: Parv "BlindedByTheRecipes_05", Kush "Houdini_loves_hustin_crepes_07".
- **Nonce:** the joint nonce is `Houdini_loves_hustin_crepes_07|BlindedByTheRecipes_05` (Kush's string, then Parv's). Kush is the supplier per design §4.5 and Parv a co-contributor; the joining rule is the scribe's choice, recorded so that neither party alone determines the seed. Commitment = SHA-256 of its UTF-8 bytes, stored with a UTC commitment time in the signed record.
- **Record:** `reports/step19/pilot_start_record.SIGNED.json`. It binds the same design and bound files as the unsigned template (kept unchanged), instrument v0 + handbook v1 / Addendum A, annotation mode MODEL_ASSISTED (D-045 W2), pilot column `reserve_split_v2`, draw spec `STEP19_P1_DRAW_SHA256_RANK_V1_DRAFT`, and the signed THR-19P-01..35.
- **Next, unchanged by this entry:** the P1 frame must be (re)built **after** this commitment, where the data bundle exists; the gate refuses an older frame. No draw or annotation has happened. P2 stays unauthorised.
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-049 · 2026-11-03 · Kush and Parv accept S157 review block F (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "block F all ok by parv and me, keep going". Where an item offered options, "ok" is recorded as the as-built conservative default written below. Kush may correct any reading by a later entry.
- **F1 re-baseline:** approved in principle. It is executed only after Kush reviews `registry/staging/step12_0_src_snap_proposed_v1.jsonl` from a real local run. Real ids are minted, and `registry/baseline_ledger_hashes_08a_v1.csv` is re-baselined, in a separate recorded step. No rows exist yet, so nothing is appended now.
- **F2 licences:** INFOODS (H2 #9) stays LOCAL_ONLY. The Bognar licence re-check is still required before ingestion. Catalog-reported CC0/PD stays UNKNOWN (not ASSUMED).
- **F3 E4:** kept as built. Under D-045 (AI draft, then human review) no evidence item reaches E4; E4 needs a separately recorded blind review.
- **F4 old tools:** `apply_link_review.py --sign-as` and `apply_human_review.py` stay unchanged and are not to be used for new reviews. New reviews go through the S157 machinery.
- **F5 review authenticity:** a review CSV counts as a person's review only when that person commits it from their own git identity or session. The agent never writes reviewer fields.
- **F6 Bognar >1.00, method labels, R2 censoring:** both readings are reported until the G12 audit decides. No value is changed.
- **F7:** R1–R4 fixes accepted; ksh's audit O-1–O-6 accepted as AI proposals pending H4.
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-050 · 2026-11-03 · Kush and Parv accept S158 review block G and approve scipy for Step 26a (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "block G and scipy ok by parv and me, keep going".
- **Accepted as drafted:** G1, H4 acceptance of the 04.3 KIN/KINPT v1.1 draft contract for continued engineering. THR-04K-01..04 are **not** signed by this entry (they were not part of block G's ok); Step 09 still must not freeze KIN/KINPT against unsigned thresholds. G2, the draft readings stand: a same-reader repeat is UNKNOWN; a missing inter-read SD and an unverified series are not eligible, as built. G3, MECH v1.1 drafted choices (target_class field, token-registry slot) stand pending a token registry. G6, the 8 AI readings of the 23a engine, the 45 AI-draft reason codes and the route enum as drafted. G7, fixes R1–R6.
- **Cannot be closed by this ok:** G4 needs the chemistry expert's own answers to EQ21-01..14. G5 sealing needs an authored shared case set, which does not exist yet; sealing is approved in principle, to be run once the cases are written.
- **scipy:** approved as a Step 26 dependency, declared as optional extra `step26 = ["scipy>=1.11"]` in `pyproject.toml`, following the existing `step35` RDKit pattern. The cloud container has scipy 1.18.1.
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-051 · 2026-11-03 · THR-04K-01..04 signed (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "ok sign THR-04K too, keep going", after D-050 noted that these rows were not part of block G.
- **Change:** in `registry/preregistered_thresholds_v1.csv`, only `registry_status` (now PREREGISTERED_2026-11-03), `signed_by` and `signed_at` changed on THR-04K-01..04. Value, rationale, source and data-seen fields are unchanged; no other row changed. `kinetic_contract.py` threshold references updated to match; its eligibility label stays `ELIGIBLE_UNDER_DRAFT_RULES`, because the KIN/KINPT v1.1 contract itself remains a draft (D-050 G1).
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-052 · 2026-11-03 · 26.0 system selection: sim_aa_1 (ascorbic acid); S159 review block H accepted (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "block H ok by parv and me, AA selected, keep going".
- **Selection (H1):** `sim_aa_1` is the Step 26 system. Record: `reports/step26/system_selection_record.SIGNED.json`, written from the S159 template, which is left unchanged; the template's sha256 is stored in the record. This is a **direct human selection made before the Step 10/11 census (11.D)**; D-027 had expected the final choice after Step 10/11 evidence. The R-14 rule stays: at most one switch to `sim_chl_1`, only after a recorded 11.D entry with written rationale. No selection criterion is claimed as met: the criteria are NOT_EVALUATED.
- **Accepted as drafted:** H2, the 24a drafts and AI vocabulary proposals and the Weibull (α scale, β shape) parameterisation. The FORM- vs MODEL- prefix is **not chosen** by this ok: both stay supported, and the decision stays open. H3, the sim_aa_1 assumptions as implemented: K_p in m³/kg with r in mL/g, temperature-independent k_L, first-order k_dw. H4, sim_chl_1: g(pH) caller-supplied, one g shared by Chl a and b as implemented (relevant only to the fallback). H6, fixes R1–R5; O1–O5 and O7 kept as currently implemented and documented.
- **Cannot be closed by this ok (stay open):** the exact "no-water-assay" design definition and the 26.0 pre-registration numbers (O6, G26-VER/G26-CAL); H5 inputs (Choi–Okos coefficients and mixing-rule check, τ_h per size class, M&S limits, solver tolerances, KiSAO id check).
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-053 · 2026-11-04 · Checkpoint H-A (block I): AI recommendations accepted; human-only values still open (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "all ok and passed by us both as well by pav and me u can use prv and ksh".
- **Accepted as drafted (AI recommendations in `reports/step15/pre_freeze_rulings_DRAFT.md` and `reports/step35/35_0_v2_signature_sheet.md`):** I1: C2-a (E3 bootstrap use only, tagged `BOOTSTRAP_UNVERIFIED`, 15b still needs human-verified held-out labels), H-3, X-1, G-1, K-1 (K = 10 recorded as a pilot convention, with the cluster sign-flip inference rule), RESERVED unit STUDY_THEN_CELL and stratification SOURCE_FAMILY. I3: Route B (regenerate the Step 35 v2 template on the Mac, where the three Mac-only recipe files exist). I5: fixes R1–R4 accepted; O3 and O5 kept as implemented and documented.
- **Not a 15.0 ruling for the seal:** this entry carries no seal marker lines, because the RESERVED fraction and the seed are not supplied. 15a.R stays refused.
- **Cannot be closed by this ok (no value, no recommendation, or a person is required; stay open):** I1 the RESERVED fraction and the seed generation method (O1); I2 whether and when to run the seal, the seed-file and sealed-list locations, and O2; I3 the answers to P-1..P-5 (options only, no AI recommendation), S-1 (a chemistry-aware reviewer for the taste map) and S-2 (a human finding on the 204 deprecated edges), or a recorded deviation, plus Q-1, Q-3 and Q-4; I4 δ_30, ρ, c_floor, the 34a.0 circularity check, the 34c thresholds and actions, and the 15a freeze-record and 29-diag pre-registration formats. Under O5 the Step 35 SIGNED record is committed only from the signer's own session, never by the agent, so this entry signs nothing.
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-054 · 2026-11-06 · S166 review block K: prv items passed (PR #8 leak fix, J7 re-confirmed, PR #8 merge) (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush, after the main session reported prv's P1 finding and the S166 fix: "passed adn connitue for me and prv". Read as Kush's pass for himself and, relayed, for Parv ("prv" taken to mean Parv, not the AI reviewer label; Parv to correct if not).
- **Passed:** block K items K1–K3: the S166 fix of prv P1–P7 (tracked packet rows and key hash are salted commitments `sha256(salt|hash)`; no per-packet counts; patterned or reused salts refused; issued list required; re-issue note); J7 re-confirmed on this design (the S165 acceptance rested on an order that the tracked csv leaked); merge of PR #8; no packets built or re-issued from the superseded unsalted list.
- **Not covered:** ksh items (block K4–K8), prv P8 (K9) and the J4 reader question (K10), which reached the humans after this pass. No value, seed, salt or signature is supplied by this entry. This entry is not the 15.0 ruling; that ruling takes the next free D-number.
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-055 · 2026-11-06 · S166 review block K4–K9 passed (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "passed by prv and ksh". Read as Kush's pass and, relayed, Parv's ("prv"/"ksh" taken as Parv and Kush, as in D-054; under D-045 the AI reviewer labels cannot approve anything, so correct this entry if the AI reviewers were meant).
- **Passed:** K4 (accept the committed 26g census tool; J8 closed), K5 (2 → 0 attributed to the S161 `º` rule), K6 (stage-order/locale/sample tests and the structural-reading fields), K7 (rerun the 1,000 census from a clean commit; mark Parv's file superseded, keep both), K8 (commit the full-corpus census JSON when done), K9 (post-run provenance re-check; Finder files out of the tree hash).
- **Still open:** K10 (who reads the J4 sample; extraction on vinayak-server).
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-056 · 2026-11-06 · Parv confirms the D-054/D-055 reading and the PR #8 merge (Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "ok merge" (PR #8 merged as `db2cd3e`), then "yes parv say it slright conitue".
- **Confirmed:** "prv" in D-054/D-055 meant Parv; his passes of block K1–K9 stand. K10 (J4 reader) stays open. The 15.0 ruling takes the next free D-number (D-057 or later).
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-057 · 2026-11-06 · Annotator A's P1 packet salt generated by the coding agent at Kush's instruction (entered by the coding agent as scribe)
- **Source:** Kush: "you can do salt".
- **What was done:** `secrets.token_hex(32)` written directly to `~/.culinarystate_private/p1_salt_A.txt` (mode 0600, directory 0700, outside the repository, exclusive create) on Kush's Mac. The value was never printed or logged; the session printed only `salt_ok True`, length 64 and no reuse of B's salt. Only its sha256 will be tracked (`salt_P1_A.sha256`, written by the packet maker).
- **Custody note (J5):** the salt was made by an agent process, not typed by Kush; Kush authorised this. Annotator B's salt is Parv's to make on his own Mac.
- **Not covered:** building A's packets, the 15a.R seed, the 15.0 ruling (next free D-number: D-058).
- **Approver:** Kush.

### D-058 · 2026-11-06 · Review block L passed: annotator A's packet build and the L2–L5 AI verdicts (decided by Kush; L3 as Parv's item relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "ok passe dblock l coniutnue".
- **Passed:** L1 A's P1 packet build (Kush may annotate); L2 packet-maker `main()` guard (`5580b93`); L3 keep `superseded_s164_unsalted/` with a "superseded, never use" README (prv verdict); L4 Kush's question log and representability file live in `~/.culinarystate_private/` as CSVs with the design Appendix C headers, no recipe text, only their sha256 in `commitments_A_P1.json`, handbook version `v1+AddendumA` (ksh verdict); L5 delete `tests/unit/.probe`.
- **Still open:** K10 (who reads the J4 sample: ksh said both with Parv first, prv said Parv only; both say drop the 14 P1 recipes and extract on vinayak-server). Parv's own salt and B re-issue. The 15a.R seed and the 15.0 ruling (next free D-number: D-059).
- **Approver:** Kush (L3 relayed for Parv).

### D-059 · 2026-11-06 · K10: both humans read the J4 inverted-interval sample (decided by Kush and Parv; Parv's ok relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "both passsed k10" (answering "Parv only or both").
- **Decided:** Kush and Parv each read the J4 sample independently, Parv first (ksh verdict); every P1 manifest recipe is dropped from the sample; extraction runs on vinayak-server; recipe excerpts stay in a git-ignored file; git gets a text-free manifest only.
- **Next free D-number for the 15.0 ruling:** D-060.
- **Approver:** Kush and Parv (Parv relayed by Kush).

### D-060 · 2026-11-06 · P1 annotation runs as D-045 W2 model-assisted: AI first pass (ksh for A, prv for B), then human stamp (decided by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "what3wver is left conintue doing annotation anad aks for stamo use ksh adn prv for it we need to pusht eh working speed".
- **Applied under D-045 W2:** ksh drafts annotator A's 7 P1 packets on Kush's Mac into the git-ignored `annotation/gold/deep_gold_pilot_v1/A_ai_draft/` (source_ref `annotation_status=MODEL_ASSISTED_AI_PASS; ai_prefill=ksh_sonnet_2026-11-06`); Kush's blank packets in `A/` are not touched until Kush reviews; prv cross-checks the drafts; Kush stamps (accepts or edits) and his edits are kept separately from the AI pass. B's AI pass is made by prv in Parv's own session on Parv's Mac (B packets must not be on Kush's Mac).
- **Measurement consequence (W2):** P1 agreement and timing are reported as "human review of AI drafts", not blind independent annotation. Both AI passes come from the same model family, so A–B agreement is not independent evidence; reports must say so.
- **Next free D-number for the 15.0 ruling:** D-061.
- **Approver:** Kush.

### D-061 · 2026-11-06 · Kush stamps ksh's AI pass for annotator A's 7 P1 packets without edits (decided by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "ksh all passed and ok no flags".
- **Done:** the 7 drafts in `A_ai_draft/` (kept unchanged as the AI pass) were copied into Kush's packet files `A/DGP-A-0001..0007.json` with `annotation_status=MODEL_ASSISTED_HUMAN_ACCEPTED; human_edits=NONE`; each validates with 0 replay issues; FIRST_VALIDATE and DONE snapshots were logged by the agent in one run.
- **Stated limits (W2):** Kush accepted ksh's 62 flagged judgement calls without line-by-line edits, so P1 A labels are "human-accepted AI drafts", not human annotation; the snapshot times are seconds apart and are not annotation timing; P1 timing must not be reported from them.
- **Held:** the tracked commitment `commitments_A_P1.json` is written only after prv's cross-check reports no must-fix error (it cannot be overwritten). The question log and representability file are still header-only.
- **Next free D-number for the 15.0 ruling:** D-062.
- **Approver:** Kush.

### D-062 · 2026-11-06 · Kush passes prv's cross-check of A's AI pass; must-fix edits applied as AI pass 2; representability all FAITHFUL (decided by Kush; entered by the coding agent as scribe)
- **Source:** after prv graded 0001 ACCEPT and 0002–0007 ACCEPT_WITH_EDITS (21 must-fix, mostly missing spans/coref, plus an inferred "hot" value, an unused `oil` entity in 0006 and no crescent-roll entity in 0007), Kush: "all faithfukll as said by the ksh flags adn all from prv said all ok adn passed adn faithfull as well".
- **Read as:** ksh's own flagged judgement calls stay; prv's verdict (with its must-fix edits) is passed, so ksh applies only the 21 must-fix items as AI pass 2 in `A_ai_draft_v2/` (pass 1 in `A_ai_draft/` kept unchanged); every representability rating is FAITHFUL. Kush to correct if "passed" meant committing pass 1 unchanged.
- **Sequence:** prv re-checks pass 2; if no must-fix remains, pass 2 is copied into `A/` as `MODEL_ASSISTED_HUMAN_ACCEPTED`, new DONE snapshots are logged, and `commitments_A_P1.json` is written and committed. D-061's limits (accepted AI drafts, no timing) still apply.
- **Next free D-number for the 15.0 ruling:** D-063.
- **Approver:** Kush.

### D-063 · 2026-11-06 · Annotator A's P1 labels committed: prv re-check package accepted (decided by Kush; entered by the coding agent as scribe)
- **Source:** after prv's re-check of AI pass 2 (0001–0005 ACCEPT; 0006 one new must-fix, an inferred oil Merge input; 0007 crescent rolls cannot be an entity), Kush: "pk ok conyinuew as per it".
- **Done:** 0006 AI pass 3 drops the inferred oil input (oil stays the brown Transform's medium); final set = 0001 pass 1, 0002–0005 and 0007 pass 2, 0006 pass 3, copied into `A/` as `MODEL_ASSISTED_HUMAN_ACCEPTED; human_edits=NONE`; DONE snapshots logged; `commitments_A_P1.json` written by `tools/step19_commit_step.py` (7 files, handbook `v1+AddendumA`, 0 recipe ids) and committed from Kush's session.
- **Representability (prv's verdict, overriding D-062's "all FAITHFUL"):** 0001, 0004, 0005 FAITHFUL; 0002, 0003 WORKAROUND (process vocabulary); 0006 WORKAROUND (implicit herbs Merge); 0007 WORKAROUND with SP-001 (strict reading IMPOSSIBLE). Question log: one line "no questions in P1". Both files stay private; only their sha256 are in the commitment.
- **SP-001 opened** in `reports/step19/pilot_schema_problem_log.md`: an ingredient absent from the ingredient lines cannot be an entity; needs a schema/engine decision before P2.
- **Limits (D-060/D-061):** labels are human-accepted AI drafts; snapshot times are not annotation timing; A–B agreement will not be independent evidence.
- **Next free D-number for the 15.0 ruling:** D-064.
- **Approver:** Kush.

### D-064 · 2026-11-06 · Annotator B's P1 packets built on Kush's Mac in a separate clone because Parv's laptop is not working (deviation; decided by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "no you can make parv laptop is not working and continuw".
- **Done:** a separate clone `~/Desktop/CGAS/cs_annotator_B` (corpora symlinked read-only from the main checkout); B's salt generated by the agent into `~/.culinarystate_private_B/p1_salt_B.txt` (0600, directory 0700, value never printed; differs from A's); `tools/step19_packet_maker.py --letter B` built 7 blank packets and the sealed key inside the clone (git-ignored there); the three tracked, text-free B files (packet list, salted key hash, salt hash; 0 recipe ids) were copied into the main repository and committed.
- **Deviation from the one-annotator-per-machine rule (design; S164 guard):** A's and B's private material are on the same Mac. Mitigations: B was built only after `commitments_A_P1.json` was committed (A's labels cannot change); B's AI pass (prv) runs only inside the B clone and must not read A's packets, drafts, key or salt; the packet maker's folder guard is satisfied per clone but its intent is not, and reports must say so. Parv stamps B's labels (relayed) when available.
- **Next free D-number for the 15.0 ruling:** D-065.
- **Approver:** Kush.

### D-065 · 2026-11-06 · ksh cross-check package for annotator B accepted (decided by Kush; Parv's stamp relayed by Kush per D-064; entered by the coding agent as scribe)
- **Source:** after ksh graded B-0001..0007 ACCEPT_WITH_EDITS (18 must-fix) and proposed SP-002..SP-004, Kush: "all passedd across th ksh pacakge".
- **Package:** prv AI pass 2 applies only the 18 must-fix items in `B_ai_draft_v2/` (pass 1 kept); ksh re-checks; SP-002 (U+2044 fraction slash parsed as count 1; also affects the committed A labels, whose affected quantities must be treated as unreliable in scoring), SP-003 (unstated shares) and SP-004 (alternative/conditional values) logged; representability per ksh: all seven WORKAROUND (B-0004 and B-0005 WORKAROUND, strict reading IMPOSSIBLE); then copy into `B/` as `MODEL_ASSISTED_HUMAN_ACCEPTED`, DONE snapshots and `commitments_B_P1.json`.
- **Limits:** as D-060/D-061/D-064 (human-accepted AI drafts; no timing; same machine; same model family for both passes).
- **Next free D-number for the 15.0 ruling:** D-066.
- **Approver:** Kush (Parv relayed).

### D-066 · 2026-11-06 · Annotator B's P1 labels committed (decided by Kush; Parv's stamp relayed by Kush per D-064/D-065; entered by the coding agent as scribe)
- **Source:** after ksh's re-check of prv's pass 2 (18/18 must-fix fixed, no new must-fix, 7/7 validate and replay clean), Kush: "okkconintue as planed and keep working".
- **Done (in the B clone):** pass 2 copied into `B/` as `MODEL_ASSISTED_HUMAN_ACCEPTED; human_edits=NONE` (ksh's nit applied: a stale `unknowns[0]` wording in B-0003); FIRST_VALIDATE and DONE snapshots; `commitments_B_P1.json` written by the commit step (7 files, `v1+AddendumA`, 0 recipe ids) and committed to the main repository. Private question log and representability file in `~/.culinarystate_private_B/` (all WORKAROUND; B-0004/B-0005 strict IMPOSSIBLE).
- **Both P1 commitments now exist** (A: D-063; B: this entry), so the sealed keys may be opened for P1 scoring (PV-6, PV-9).
- **Limits:** as D-060, D-061, D-063, D-064 (human-accepted AI drafts; no timing; same machine; same model family; SP-002 affects A's committed quantities).
- **Next free D-number for the 15.0 ruling:** D-067.
- **Approver:** Kush (Parv relayed).

### D-067 · 2026-11-06 · Review block M passed (decided by Kush; Parv relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "ok sll snf conitnue working i will b joining back after few hrs yo u keep wroking".
- **Passed:** M1 (P1 scoring code, fixes and hardening), M2 (P1 numbers as an engineering score of human-accepted AI drafts), M3 (prv's THR-19P reading: mostly NOT_EVALUABLE under W2/D-064; THR-23 PASS; THR-25 FAIL until SP triage; STOP-SCHEMA not triggered), M4 (revise the handbook — Addendum B — before P2; schema/tooling decisions on SP-001/SP-002 first; add per-category denominators to the scorer), M5 (ksh/prv triage SP-001..SP-004 as AI verdicts, then human stamp), M6 (prv's report wording).
- **Next free D-number for the 15.0 ruling:** D-068.
- **Approver:** Kush (Parv relayed).

### D-069 · 2026-11-06 · Block N answers: ksh handles SP stamp, Addendum B and SP-002; P1b yes; SP-002 sensitivity ok; 15.0 "whatever is best"; PR #9 merged (decided by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "use ksh for the sp one and then iw ill review it and the addendum b sp 002 kr lie bhoi ksh presona ude and the p1b yes ohelast senseitvity is fine  2 ok whatever might be the best and merd pr 9".
- **Done:** PR #9 merged (`d5a5eef`). ksh's SP stamp proposal (`reports/step19/sp_stamp_proposal_ksh_S168.md`: all WORKAROUND; SP-001 SCHEMA_GAP → 16A; SP-002 TOOLING → parser fix; SP-003 HANDBOOK_GAP → Addendum B; SP-004 SCHEMA_GAP → 16B) and ksh's consolidated Addendum B (`annotation/annotation_handbook_v1_addendum_B_PROPOSED.md`: 8 issued rules with recurrence >= 3, 10 held) committed for Kush's review. N7: P1 score carries `sensitivity_sp002` (U+2044 normalised at scoring; labels and headline unchanged).
- **SP-002 scale (measured):** 1,275,782 of 4,281,956 corpus ingredient lines (29.8 %, almost all Food.com) contain U+2044; all parse differently once it is normalised; the Step 16 rc2 path (`quantity/parse_adapter.py`) uses the same `grammar.parse_line`, so committed Step 16 quantity coverage is affected. `grammar.py` is protected by the S154 rule ("old grammar/normaliser untouched"), so the fix waits for ksh's versioned design and Kush's decision; nothing parsed was changed.
- **15.0:** Kush's 15a.R seed generated on Kush's Mac (`~/.culinarystate_private/15aR_seed_kush.txt`, never printed; sha256 `73d3ed4d…`); the 15.0 ruling block (D-068) is prepared for Kush to append himself, because the 15a.R rule says no agent may write it.
- **P1b: yes**; size and draw follow (prv suggested 3–4 NEW recipes, fresh packets and salts; a design amendment).
- **Approver:** Kush.

### D-070 · 2026-11-06 · Review block O passed as proposed (decided by Kush; Parv relayed by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "passok continue".
- **O1 SP-002:** ksh's design approved (adapter-level pre-normalisation in `parse_quantity_v2`, version bumps, `grammar.py` untouched, glued "11⁄2" REFUSE, legacy ledgers/KGE keep the defect with a documented caveat); implemented **after the presentation** as a new versioned rc2 result beside S161; until then every quantity figure carries the SP-002 caveat.
- **O2 SP stamp:** SP-001 WORKAROUND / SCHEMA_GAP → 16A; SP-002 WORKAROUND / TOOLING → parser fix (TOOLING_BACKLOG); SP-003 WORKAROUND / HANDBOOK_GAP → Addendum B; SP-004 WORKAROUND (BLOCKING risk) / SCHEMA_GAP → 16B. THR-19P-25 (100 % triage) satisfied. STOP-SCHEMA not triggered.
- **O3 Addendum B:** the 8 issued rules of `annotation_handbook_v1_addendum_B_PROPOSED.md` are stamped and in force from P1b/P2; the 10 held rules (incl. H.1) stay held. P1 labels are never edited or re-scored.
- **O4 15.0:** unchanged — waits for Kush to append D-068 himself (15a.R rule); the seal runs only after a clean check.
- **O5 P1b:** design amendment approved in principle (fresh draw excluding all 21 P1 rows, new salts, `--wave` support); the size (3–4) and the draw nonce/seed still come from a human.
- **Approver:** Kush (Parv relayed).

### D-071 · 2026-11-06 · Kush delegates decisions to the AI personas: "prv is Parv and ksh is Kush" (decided by Kush; entered by the coding agent as scribe)
- **Source:** Kush: "ok then prv i parv and ksh is kush this is the rule and keep workkking dont disturb untill very urgent or importna keep working hogh on the engines".
- **Rule from now on:** a ksh verdict counts as Kush's decision and a prv verdict as Parv's (Parv relayed by Kush), so review blocks no longer wait for the humans. Every such entry is recorded as "decided by ksh/prv (AI) under D-071", never as the humans' own words, and reports must say that these decisions were AI-made under delegation (amends D-045 W1 for decisions; W2 stands).
- **Still human-only (the project's own rules; recording an AI output as a human signature would misstate the record):** signatures and signed records (the 15.0 ruling D-068, which the 15a.R rule requires Kush to append himself; the Step 35 SIGNED record, O5; amendments to the signed pilot start record), pre-draw nonces (design 4.5: the drawing agent must not choose them), and facts only a person knows (the professor's permission, D-045 W3; DEL authorship; Parv's own written confirmations).
- **Work mode:** the agent keeps working without asking, and contacts Kush only for urgent or important items.
- **Approver:** Kush.

### D-072 · 2026-11-06 · J4 read; hyphenated mixed numbers fixed in the versioned rc2 change (decided by prv and ksh (AI) under D-071; entered by the coding agent as scribe)
- **Evidence:** `reports/step17/j4_reading_counts_S168.json`: 69 sampled cases read by prv (as Parv, first) and ksh (as Kush, second, independent): MIXED_NUMBER_MISREAD 62 (every "9-9/9 <unit>" case), TRUE_INVERTED_RANGE 3, OTHER 4 (two cut-off leading unicode fractions, one decimal split at the point, one pan size); agreement 69/69, kappa 1.0 — both readers are AI of one model family, so this is not independent human evidence.
- **Decision:** a hyphenated mixed number ("1-1/2 <unit>" = 3/2) is parsed as a mixed number, not a range; true reversed ranges keep V2 INVERTED_INTERVAL and become UNKNOWN; a leading unicode fraction must not be cut from the span; decimals are never split. Implemented in the same versioned rc2 change as SP-002 (adapter pre-normalisation, version bump, `grammar.py` untouched), after the presentation per D-070; until then the 4,511 V2 cases are reported as a known parser defect.
- **Approver:** prv (Parv) and ksh (Kush), AI under D-071.

### D-073 · 2026-11-07 · Census reason fix: lot introductions are not a binding gap; Rung A implicit-object fixes need a precision check first (decided by ksh (AI) under D-071; entered by the coding agent as scribe)
- **Evidence (ksh engine diagnosis, seeded 1,000 sample):** of NO_CONSUMED_ENTITY events, 83.4 % were the adapter's synthetic INTRO/<entity> lot introductions (consume nothing by design) and ~0.7 % negated/discard events; ~16 % were real Rung A actions with no bound object (IMPLICIT_ARG_AMBIGUOUS 8.8 %, IMPLICIT_ARG_NONE 6.3 %, unresolved references 0.8 %); 94 % of those had no food mention in the action window (a binding, not a linking, problem).
- **Done:** `recipe_adapter` labels lot introductions LOT_INTRODUCTION; census/contract 0.2.0-draft; 1,000 sample rerun: NO_CONSUMED_ENTITY 7.1 %, LOT_INTRODUCTION 35.1 % (`reports/step26/simulability_census_real_sample_counts_S168.json`); full-corpus 0.2.0 rerun running on vinayak-server; the final report draft and figure 2 corrected (the earlier "42 % extraction gap" reading was wrong).
- **Pending:** Rung A binding rules for implicit objects (bind the current entity when the tier is ambiguous; bind the last-produced intermediate when none is live) — upper bound ~1.5 % of events; each needs a precision check on a labelled sample before landing (RULES_VERSION bump), because a wrong binding is worse than UNKNOWN.
- **Approver:** ksh (Kush), AI under D-071.

### D-068 · 2026-11-06 · Step 15.0 pre-freeze rulings (decided by Kush; entered by the coding agent at Kush's explicit instruction "seal signed ok and passe dby parv and kush", Kush waiving the 15a.R self-append rule)
- **Source:** Kush: "2 ok whatever might be the best" (the drafted values in reports/step15/15_0_ruling_DRAFT_FOR_KUSH_SIGNATURE.md are accepted as best).
- **Decision:** C2-a, H-3 (15b) with TB-V0 order for 15a diagnostics, X-1, G-1, K-1 as in reports/step15/pre_freeze_rulings_DRAFT.md.
- **15.0 RESERVED_FRACTION:** 1/5
- **15.0 RESERVED_UNIT:** STUDY_THEN_CELL
- **15.0 RESERVED_STRATIFY:** SOURCE_FAMILY
- **15a.R SEED_SHA256:** 73d3ed4de7ba9d46f09c7fb408805a78f3c8189044a71de3d2da3a85461932d5
- **Seed custody:** Kush's seed on Kush's Mac (`~/.culinarystate_private/15aR_seed_kush.txt`, 0600, 48 hex, made with Python `secrets` by the agent at Kush's instruction, never printed); it replaces the agent-made seed on Parv's Mac (`d3075c68…`, block J5).
- **Approver:** Kush

### D-074 · 2026-11-07 · D-073 implicit-object rules: R2 withdrawn, R1 not landed (decided by ksh (AI) under D-071; entered by the coding agent as scribe)
- **Pre-registered** before any draw: `reports/step17/d073_implicit_binding_precision_PREREG.md` (+ Amendment 1, a parenthetical Wilson-bound correction; rule unchanged).
- **R2 (last-produced intermediate when none is live): withdrawn untested.** On the exploration seed it could fire on at most ~0.3 % of events, and there the only live candidates are reserved portions, which are never implicit by design; the other IMPLICIT_ARG_NONE events come before any food exists (UNKNOWN is correct).
- **R1 `RA_IMPLICIT_CURRENT_V1` (current mixture when the tier is ambiguous): DO_NOT_LAND.** 60 items from 400 recipes (seed `d073-precision-2026-11-07-r1`), labelled by ksh: CORRECT 4, WRONG_OBJECT 43, NOT_AN_ACTION 8, UNCLEAR 3, NO_OBJECT 2; precision 0.067, Wilson 95 % lower 0.026 (`reports/step17/d073_r1_precision_S170.json`). The verdict does not depend on how strictly the items were labelled: a lenient reading adds at most ~12. In ambiguous tiers the current mixture is usually stale (the action acts on a separately prepared food) or lacks foods added since; ~13 % of firings are nouns tagged as verbs.
- **Consequence:** binder unchanged, RULES_VERSION unchanged; the ~7.0 % real binding gap stays UNKNOWN. Rung A's ambiguous-tier events need a richer combine/attachment model, not a recency default (after the presentation, if at all).
- **Approver:** ksh (Kush), AI under D-071; same-model caveat as J4; no prv cross-check.

### D-075 · 2026-11-07 · Router demo mode now; redo 07.A to open 23b; finish D4 + D5 + H1/H3 + hosted demo before the presentation (decided by Kush; entered by the coding agent as scribe)
- **Source:** Kush, S170 (answers to the agent's questions): "Both: demo mode now + redo 07.A"; scope "D4 + D5 + H1/H3"; live = "Hosted web demo".
- **Router:** add a NON_CITABLE demo/diagnostic mode to the Step 23a engine so it runs on real recipe events for the demo only; its output can never feed a claim (same pattern as 29-diag). `23b` stays BLOCKED until 07.A validly passes and 15b is frozen (R-05 unchanged).
- **07.A redo:** a fresh condition-audit packet labelled independently by Kush and Parv, with the statistic pre-registered before labelling and chosen to be robust to the kappa paradox. The failed 07.A result stays on record (R-20); the new run is a new gate attempt, not a reinterpretation.
- **Scope to 25 Nov:** D4 evidence-aware retrieval with abstention; D5 end-to-end RAG with B0-B5 on an ~80-question benchmark (human-reviewed by Kush and Parv); H1 and H3; a hosted web demo. Slides wait until these exist.
- **Approver:** Kush

### D-076 · 2026-11-07 · Step 10 ascorbic-acid kinetics pilot (~20 rows), AI-extracted, verified by Kush and Parv (decided by Kush; entered by the coding agent as scribe)
- **Source:** Kush, S170: "Yes, ~20 rows".
- **Decision:** AI extracts AA degradation kinetic series (k, Ea, T_ref, order, fit range, matrix, conditions) from lawful open-access papers with source spans; Kush and Parv each verify every row (MODEL_ASSISTED under D-045). Verified rows become the first PARAM rows for sim_aa_1; part is held out for Step 27 validation, split fixed before fitting. No value without a source span; unverified rows never reach SIMULATE.
- **Approver:** Kush

### D-077 · 2026-11-08 · Physical-state dataset over the full corpus, NER deployment, all compute, tracked (decided by Kush; entered by the coding agent as scribe, with its reading of the answers stated)
- **Source:** Kush, S172, answers to the agent's three questions: gaps → "the best as we need the synthetic yet supportive dataset … run it on the server and complete it"; priority → "use all the resources server cpu gpu etc"; BBC → "the best combination … manjot … vinayak … mac … all need to be tracked".
- **Agent's reading (Kush may overrule):** (1) gap policy = **two layers, never mixed**: TEXT_STATED (recipe-stated values + physical definitions, spans, UNKNOWN otherwise) and SCENARIO (literature-typical defaults with source and range, run low/mid/high, ASSUMED_DEFAULT / MODEL_DERIVED / NON_CITABLE). Under SSOT §141, SCENARIO yields driver trajectories and `physically_possible` direction only; no nutrient number before the M3 fit is frozen and held-out checked. It is not the Step 28 E7 prior (R-13 unchanged). (2) Priority = parallel: long server jobs for binding/physics/NER while the Mac builds M6 and the H1/H3 rungs. (3) **D-003 kept**: BBC Good Food text stays off servers; BBC recipes run on the Mac; vinayak (A100 ×2, 128 cores) and manjot (GPU 1 only, CPUs) run every other family.
- **Also:** deploy the trained DeBERTa-CRF NER over the corpus's ingredient lines (MENTION ledger draft, agreement with Rung A); every run is logged in `registry/compute_runs_v1.csv` (host, commit, code/input/output hashes, times, status).
- **Unchanged:** ledgers EVD/COND/SRC/MEAS/SNAP byte-identical; R-05, R-13, R-20; no value without a source.
- **Approver:** Kush

### D-078 · 2026-11-08 · Orchestration moves to the manjot-server Claude session (decided by Kush; entered by the coding agent as scribe)
- **Source:** Kush, 2026-11-08: "you need to take over the baton and use all the resources and multiple agents to work on each part of the progress … main orchestrator and other agents taking up the other tasks as well … using wisely"; later: "look at the SSOT in detail … get a consensus … what requires compute, code building, training, analysis, downloading"; "finish the SSOT v16 and the plan consensus"; "drop the anchor only after all agents finish".
- **Decision:** the manjot-server session is the main orchestrator from S175. It works on branch `max/s176-orchestration` (worktree `~/kush_work/culinarystate/.orch`; the main folder stays the Mac's rsync target). The Mac agent keeps BBC-only jobs (D-003), vinayak jobs, git merge/push and human-gate scribing until the branch is merged (`handoff/ORCHESTRATION_TAKEOVER_2026-11-08.md`).
- **Not decided here:** everything the S175 lanes produced is AI_DRAFTED (consensus plan, v16 draft, registries, code). None of it is a human signature, approval or nonce; D-071 limits unchanged. SSOT v15 remains authoritative until Kush approves v16.
- **Numbering note:** D-028 is absent from this file (gap in the sequence, kept as is; ids are never reused).
- **Approver:** Kush.
