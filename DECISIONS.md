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
