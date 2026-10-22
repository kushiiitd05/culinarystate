# STEP 07I-R -- MAX / master-plan consensus for recipe identity

Sources read: SSOT v15 (identity/leakage/duplicate sections), Master Plan v4.0 (Laws, E4 blocks B00-B17, Part H, R2/R4), Detailed R&D Plan v2 (7.7, F.3), Parv's repo `parv-origin/main` (DELTA/LANE/ACQUISITION/COVERAGE/STATUS/DECISIONS, `silver/pipeline.py`), local DECISIONS/WORKLOG, the 07I pre-registration and the code. Authority order: `plan_authority_inventory.md`. Conflict classes: IMPLEMENTATION_DETAIL, STALE_PLAN, SSOT_CONFLICT, SCOPE_CHANGE_REQUIRED, UNRESOLVED. "Prev. 07I" = the position of the stalled earlier attempt.

**Result: no SSOT_CONFLICT and no UNRESOLVED item affects recipe identity. Execution proceeded on the unambiguous intersection.** Items that need a human or a later step are listed in section B.

## A. Topic table

| Topic | SSOT position | MAX / master-plan position | Current implementation | Prev. 07I | CONSENSUS | CONFLICT | ACTION |
|---|---|---|---|---|---|---|---|
| Recipe-source acquisition | 257F acquisition protocol; B02 manifest | prefer APIs; no raw text beyond licence; H2 for unclear licences (R4) | 612,782 indexed records, 5 corpora; usage registry (342 rows) | census done, nothing scraped | no new acquisition in 07I | none | re-census (sec. C): 1 un-indexed ingredient-list corpus found, left un-indexed |
| Gold / Gold-Light / Silver / weak | 236 tiers; Gold protected from anchoring | Deep Gold ~750-1000, Gold-Light 3-5k, Silver 10k->100k gated (DELTA: Lane B/C) | tiers SOURCE_RAW 600,828 / SILVER_AUTO 11,914 / GOLD_PENDING 40; no Deep Gold | rep. selection prefers Gold; firewall table | Gold never demoted or merged away; identity never promotes a tier | our base is not "Silver" | keep; Gold firewall reports 50 indexed, 0 same-group non-Gold members, 2 with family relatives |
| Recipe canonicalisation | `Recipe.*` contract; raw text immutable, normalisation = new column | `REC-` immutable raw + content hash | `recipe_base` pointers + hashes; REC jsonl untouched | same | raw untouched | none | unchanged |
| Exact duplicates | 257A.15 step 2 (first); 192.5 `duplicate_group_id` | H1 content hash; B07 groups before splits | 4 deterministic keys (raw_hash, rec_content_sha256, A1 canonical_url, normalised-text hash); 1,039 groups / 2,107 records | done first, but inside the monolith | exact is its own phase, before any scoring | none | now `--phase exact`, hashed and resumable |
| Near duplicates | 264.8, E13E-05: **no universal threshold before calibration**; 247.13 duplicate detector "imperfect" | H1 "FAM- via MinHash>=0.8"; Detailed 7.7: >=0.8 is only an initial candidate rule, not proof | candidates only; nothing coalesced; 400-pair blind packet (unlabeled) | same | threshold stays unvalidated; shrinkage is a finding | H1 wording vs 264.8: **IMPLEMENTATION_DETAIL** (SSOT wins) | report instruction-MinHash >= 0.8 counts for comparability (5,885 stored pairs) but do not act on them |
| Recipe families | 257A.15 steps 4-5; 271.5 lineage is a network, not a tree | `FAM-`; derivative-family graph (F.3) with reviewed borderline matches and sampled precision | PROVISIONAL_STAR_V1 (direct edge to centre, no chaining), `calibrated=false`; 605,476 families, 5,803 multi-rep | same | families are provisional and non-destructive | none | added per-family consistency table (min/mean internal score, disagreement, source diversity, ingredient/process agreement) and `FAMILY_CANDIDATE_REVIEW` flag |
| Dish / cultural families | 264.9 identity != novelty != dish family; 160 never conflate | RS-14/15; L13E | dish-family *candidates* by centre title key, INFERRED_CANDIDATE, never collapsed | key from `groupby.first()` (file-order dependent) | candidates only | none | key now taken from the family **centre** (deterministic); 46,697 candidates |
| Historical variants | 270 date uncertainty, 264.10 novelty only vs earlier corpus | L13E parked post-course (DELTA) | era carried as provenance (author-born / published year) in consensus; no collapsing | same | keep era/culture as provenance, never as identity proof | none | unchanged |
| Ingredient ontology | 234/238 canonical vocabulary | B09 concept + facets, 3 identities | `ING` 2,048 / `ALIAS` 4,103; exact-alias link status only (frozen linker not re-run) | reused | reuse; no new concepts per raw phrase | NER/linker re-run needs GPU server | unchanged; coverage audited (`_audits.json`) |
| Quantity / portion | 235 CQPO | B10; no invented grams | v0 grammar, locale-aware, q-levels; mass-grounded only when evidenced | reused | unchanged | none | unchanged; quantity distance for identity uses mass-grounded shares only |
| Process ontology | 199, 107 | B05 >= 300 IDs target; PROC 156 now | PROC verb-form candidates, UNMAPPED stays unmapped | reused | unchanged | target 300 vs 156 existing -> **SCOPE** (later step) | audited; high-frequency unmapped verbs listed |
| Tool / utensil hierarchy | 203.2 process-event table | X1 `TOOL-` with `tool_family`, material, geometry...; DELTA T19: identity + process compatibility, **no physical/safety claims** | 119 TOOL; 14-class structural map (`recipe_tool_structural_class_map_v1.csv`) by deterministic keyword rules | created | no authoritative hierarchy exists beyond `tool_family`; broad classes kept, **every class marked DETERMINISTIC_RULE_UNVERIFIED / provisional** | none | do not classify nouns by guess: UNKNOWN/OTHER retained |
| Condition representation | W2 full condition profile, never one T and one t | frozen 07H-R normaliser | 3.9 M condition mentions; frozen fingerprint e7d58913 | not touched | frozen | human sub-gate pending | **not regenerated**; packet v4 stays valid |
| Recipe state graphs | 233 event-sourced graph | B11; EVT/STATE/ENTITY | **not built** (blocked future step) | not touched | stable foreign keys only | none | `recipe_identity_fk_v1.parquet` provides `recipe_id -> duplicate_group_id -> recipe_family_id` |
| Family consensus | 264 / 257 provenance | confidence vectors, never one truth score | support over duplicate-group representatives, UNANIMOUS...CONFLICTING; no invented recipe | same | non-destructive profiles | none | 182,743 field-support rows |
| Provenance | Law 15 append-only; every artifact hashed | Law 14 version everything | manifest with input/output hashes per partition | none | every table carries source_family/source_id; run manifest hashes inputs | none | done |
| Confidence | confidence vector | same | components separate; `calibrated=false` | same | never multiplied | none | done |
| Licence / use | 250 licensing | R4, H2 | `usage_class`, `training_allowed`, `raw_redistribution_allowed` | same | no licence invented; 523,217 records LICENCE_UNVERIFIED | none | carried unchanged through exact grouping (tested) |
| Split leakage | 257A.15, Duplicate-group-disjoint | Law 13, D 7.7/F.3 | groups/families are leakage-lock *candidates*; **no split frozen** | same | groups are the lock unit; families only after calibration | none | `split_lock_group_id` in Gold firewall |
| Level-13 representation | 264 multi-view `g(d_I,d_Q,d_role,d_P,d_G)`, probabilistic | B14 SX-14-03 | views implemented: d_I (id Jaccard, IDF Jaccard, multiset), d_P (set + LCS), d_Q (cosine of mass shares; SSOT baseline = log-ratio), title, condition; **d_role and d_G unavailable** (no roles/graph yet) | ranking score with fixed weights | weights are a ranking convenience, not `g` | 264.2 "no a-priori scalar weights": **IMPLEMENTATION_DETAIL** while score only ranks | components stored separately; revisit in E13E-05 |
| Level-13E cultural/historical | RQ13E-07, E13E-05 | B15 parked post-course | not started | not started | calibration set (400 pairs) is the seed | none | needs human labels |
| Level-14 process-conditioned | 197-205 | B12 | not started | n/a | out of scope | none | none |
| Level-15 transition/simulation | 208-227 | B13 | not started; SIM/RXN/KINETIC untouched | n/a | firewalled | none | scientific ledgers unchanged |
| Level-16 CulinaryState-RAG | 231-245 | B16 | identity layer provides `lineage/dedup` keys | n/a | dedup keys for RAG packets | none | none |
| FlavorTwin | 15-20 | B16 | n/a | n/a | unaffected | none | none |

## B. Conflicts and items needing a decision

| # | Item | Class | Resolution |
|---|---|---|---|
| 1 | Master Plan H1 "`FAM-` via MinHash >= 0.8" vs SSOT 264.8 / Detailed 7.7 (0.8 = candidate rule only) | IMPLEMENTATION_DETAIL | SSOT wins; `FAM-`-style grouping stays provisional and uncalibrated |
| 2 | Parv repo `silver/pipeline.py::duplicate_families` (O(n^2), chaining, auto-coalesce at Jaccard 0.8) | STALE_PLAN | not used; documented as an anti-pattern for the pipeline's no-chaining rule |
| 3 | Fixed ranking-score weights vs SSOT 264.2 | IMPLEMENTATION_DETAIL | allowed only because the score *ranks* candidates; no decision uses it. A future threshold needs E13E-05 calibration |
| 4 | Previous consensus tool rewrote the frozen `recipe_base_v1.parquet` in place | IMPLEMENTATION_DETAIL (defect) | fixed: identity foreign keys now live in `recipe_identity_fk_v1.parquet`; base bytes verified unchanged (84,553,667 B, matches the 07H-R freeze manifest) |
| 5 | `STATUS.md` stale | STALE_PLAN | WORKLOG is authoritative |
| 6 | Local assets: `data/external/sustainablefooddb/Recipe_cfp.csv` = 118,083 ingredient-name lists + region (no steps, no quantities) is **not indexed** | SCOPE_CHANGE_REQUIRED | adding records to the frozen 612,782 base needs a decision; recorded below, not done |
| 7 | Process target (>= 300 PROC) vs 156 | SCOPE (later step) | untouched |
| 8 | SSOT 264.4 quantity baseline (log-ratio) vs cosine used | IMPLEMENTATION_DETAIL | revisit with E13E-05 |

Future change request (not filed, for the humans): register an ingredient-list-only recipe tier (`INGREDIENT_LIST_ONLY`) if the sustainability corpus is to be indexed, with H2 licence review.

## C. Local asset census, re-run after the plan review (no scraping)

| Class | Assets |
|---|---|
| INDEXED (LOCAL_RAW, in the 612,782 base) | A1/BBC 11,934 (LOCAL_RESEARCH_ONLY), Wikibooks 3,676 (REDISTRIBUTABLE_WITH_ATTRIBUTION), Gutenberg segments 73,955 (PUBLIC_OPEN), Food.com 522,517 (LICENCE_UNVERIFIED, CC0 declared by uploader, authority not verified), TASTEset 700 (LICENCE_UNVERIFIED) |
| NOT_INDEXED (recipe-like) | `sustainablefooddb/Recipe_cfp.csv` 118,083 ingredient lists + region (LICENCE_UNVERIFIED, local only); CoSyLab `gk_ingredient_phrases.csv` 258,170 phrases of ~23,201 AllRecipes/Food.com recipes (fragment); RecipeDB3 instruction NER sample 10,000 sentences (fragment) |
| NOT_INDEXED (not recipes) | phrase-level NER sets (RecipeDB3 ingredient 26,444; recipe_ner_dl 8,798), RecipeDB2 category labels 19,019, FlavorGraph edges, OpenPI procedures |
| MISSING_RAW | 177 Gutenberg REC ids have no local segment (kept as members, flagged RAW_SEGMENT_MISSING_LOCALLY); 48 A1 raw rows have no REC id (23 have >= 3 ingredients and steps) |
| LICENCE_BLOCKED | none stored beyond the use class; Food.com/TASTEset need an H2 registration; A1/BBC raw text never leaves `data/raw` |
| LOCAL_RESEARCH_ONLY | A1/BBC 11,934 |
| DUPLICATE_SOURCE_ARTIFACT | A1 raw copy `Q1a_raw_recipes.jsonl`; SSOT v15 copies (3); A3/A1 incidence matrices (derivatives) |
| Recipe1M+ / RecipeNLG | **not present locally** (FlavorGraph is a derived graph only) |
