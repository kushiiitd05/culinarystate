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
