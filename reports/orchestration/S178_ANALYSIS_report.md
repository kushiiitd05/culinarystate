# S178 lane ANALYSIS: dataset card, negative-results rows, ING/ALIAS coverage census, "what the corpus can say"

Status: AI_DRAFTED / PROPOSED. Counts only; nothing here is a human review, signature or freeze. Role ANALYSIS, 2026-11-09, host manjot-server, tree `~/kush_work/culinarystate/.orch` (worktree `max/s176-orchestration`; HEAD was 8577136 when the lane started and 3da963d at the end, nothing this lane reads changed in between). Everything under `reports/s178/analysis/`, `tools/s178_analysis_*.py`, `tests/unit/test_s178_analysis_*.py`, plus 15 appended rows in `registry/negative_results_register_v1.csv`. Protected ledgers (EVD, COND, SRC, MEAS, SNAP) re-hashed before and after: byte-identical. No git write, no WORKLOG entry (orchestrator-only; CLAUDE.md asks for `tools/log_step.py`, which edits WORKLOG, so I did not run it).

## 0. Result in numbers

| Item | Deliverable | Headline |
|---|---|---|
| T2-C15-R1 | `reports/s178/analysis/evd_dataset_card_v1.{md,json}` + `tools/s178_analysis_evd_card.py` | 17,978 ACTIVE E3 rows (3 families, 127 independence groups, 165 ING concepts, 224 SVAR targets); **0 human-verified, 0/40**; all rows E3_UNVERIFIED + BOOTSTRAP_UNVERIFIED + COND_UNAUDITED; T and t both stated on 8.76 % (Phenol-Explorer only); 32.78 % censored; 17 conflict-candidate cells; double run byte-identical |
| T9-C08-R4 | 15 rows NEG-0031..NEG-0045 appended; `reports/s178/analysis/negative_results_s171_s177_verification_v1.{md,json}` | 83 figure checks: 74 recomputed from committed JSON/CSV/code, 9 matched in committed prose only, **0 mismatch, 0 unverified**; existing 30 rows untouched (git diff: +15 / -0) |
| T3-C03-R2 | `reports/s178/analysis/ing_alias_coverage_census_v1.{md,json}` + `_tables.csv` + `tools/s178_analysis_coverage_census.py` | Food.com mentions: 82.2 % exact ING/ALIAS, 16.7 % partial, 1.1 % miss; Wikibooks 63.7 / 33.7 / 2.6; TASTEset 58.5 / 37.7 / 3.9; TASTEset gold FOOD spans 81.5 % exact; 324 Food.com phrases hold 80 % of mentions |
| T4-C04-R1 | `reports/s178/analysis/corpus_can_say_v1.{md,json}`, `fig1..3 .svg/.csv`, `tools/s178_analysis_corpus_can_say{,_render}.py` | Food.com heat events (1,503,261): time stated 30.9 %, temperature stated in the text 3.7 %, both in the text 1.9 %, neither 60.1 %; reconciliation to the committed censuses PASS |
| Tests | 5 files, 26 tests | 26 passed (3.4 s) |

## 1. T2-C15-R1: dataset card for the 17,978 ACTIVE E3 EVD rows

`python tools/s178_analysis_evd_card.py --selfcheck` reads `ledgers/data/{EVD,COND,SRC,MEAS,SVAR,PROC,ING,STUDY}.jsonl` read-only (latest version per id, status ACTIVE), the SVAR registry and mapping, and the 15a.R seal commitment (counts only; the reserved list is outside git and was not read). No timestamp enters the card; `--selfcheck` runs it twice and compares; a separate run 14 minutes earlier produced the same sha256 (`d97d1af7...`).

Every SSOT 203.9 item has a section (`s203_9_1_total_rows` ... `s203_9_13_duplicate_conflict_audit`; the test `test_every_203_9_item_has_a_section` enforces it). Beyond 203.9: labels, censoring, units, licence status, lineage, seal check, computed limitations.

Selected numbers (all from `evd_dataset_card_v1.json`):
- Rows: 17,978 ACTIVE of 18,156 ids (178 DEPRECATED excluded; 57,280 version lines). USDA-RETN-R6 7,018, BOGNAR-2002 7,090, PHENOL-EXPLORER-3.6 3,870. EVD sha256 equals the 15a.R commitment snapshot (`5b3b1939...`: True).
- Labels: E3_UNVERIFIED 17,978 (verification UNVERIFIED 14,108, AI_PRECHECKED 3,870, HUMAN_VERIFIED 0); BOOTSTRAP_UNVERIFIED 17,978; COND_UNAUDITED 17,978 (all 4,414 COND records UNVERIFIED).
- Foods: 619 distinct matrix names; 165 ING concepts linked on 64.35 % of rows (Bognar 36.64 %, USDA 72.97 %, Phenol-Explorer 99.48 %). Processes: 55 steps, 70 step sequences, 37 PROC ids on 99.13 % of rows. Pairs: 998 (matrix, step sequence) pairs, 40.7 % seen once; 13,448 cells.
- Targets: 224 SVAR (213 after the duplicate mapping); CHEMICAL 17,482 rows, PHYSICAL (food mass) 496 rows.
- Conditions (rows): temperature stated 6,015 (MEASURED 2,430, RANGE 3,585), duration 3,083, both **1,575 (8.76 %)**, all Phenol-Explorer; pH, moisture 0; a_w not in the COND schema; pressure on 129 rows; power on 60.
- Censoring: 5,894 rows (32.78 %): USDA 2,620 (37.33 %, GT_CAP 97.5), Bognar 3,274 (46.18 %, GT_CAP 0.995).
- Lineage: USDA and Bognar are one independence group each (study-disjoint evaluation impossible, NEG-0002); Phenol-Explorer 125 groups.
- Licence status (SRC ledger values): USDA SRC-000001 ASSUMED, Bognar SRC-000141 ASSUMED, Phenol-Explorer SRC-000012 VERIFIED with storage_rule DERIVED_ONLY and 126 SRC records in provenance whose licence status is UNKNOWN; every row touches a not-VERIFIED licence record. Not legal advice; H2 licence review still open.
- Analytical platform: no EVD row carries one (MEAS records describe the database calculation protocol); 3,870 Phenol-Explorer rows have no measurement_method_id.
- Duplicate/conflict audit: 4,474 replicate rows in the same group and cell; **17 conflict-candidate cells** (same count as the DEL-1 card, which did not include Bognar).

Third-party text: none. Foods appear only through ING canonical names and USDA/Phenol-Explorer food-group labels; the test `test_deterministic_and_counts_only` asserts that raw source food names never reach the card.

Acceptance gap: the ledger row asks for `reports/step15/dataset_card_15a_v1.md/.json`. My ownership is `reports/s178/analysis/`, so the card is there; the orchestrator can copy it (the generator takes `--out-dir`). G15-a ordering: no 29-diag output and no 15b freeze record exists in the tree (`reports/step29` holds the pre-registration draft only); the run times are in the compute_runs rows below.

## 2. T9-C08-R4: negative results S171-S177

`python tools/s178_analysis_negregister.py --append --full-scan` rebuilds every row from the committed sources, appends it (old bytes remain an exact prefix, sha256 `8a470764...` -> `bcb2dfd5...`, re-run is a no-op) and writes the verification table. Status column: RECORDED_AGENT_CHECKED when every headline number was recomputed from a machine-readable source, RECORDED_AGENT_CHECKED_PARTIAL_TEXT_ONLY when some supplementary numbers appear only in committed prose (tagged `[text-only]` inside the row). registry_status DRAFT_PENDING_H4 for all, as for the existing rows.

| ID | Negative result | Recomputed from | Status |
|---|---|---|---|
| NEG-0031 | Router DIRECT 274,058 of 36,359,902 = **0.754 %** (S171 full corpus); 103 of 130,886 distinct pairs hit | `router_demo_census_vitc_full_corpus_S171.json` | CHECKED |
| NEG-0032 | Gated revision (S176 non-BBC full): DIRECT **267,933 (0.760 %) -> 34,537 (0.098 %)**, 87.1 % withheld | `router_demo_census_vitc_nonBBC_full_S176.json` | CHECKED |
| NEG-0033 | D-074 R1: CORRECT **4 of 60**, Wilson [0.0262, 0.1593], DO_NOT_LAND, one AI labeller | `d073_r1_precision_S170.json` | CHECKED |
| NEG-0034 | Food.com has no units: 0 unit tokens in 7,950 quantity strings; 0 of 4,129,433 lines with grams | `foodcom_units_check_S176.json`, `s177/line_mass_census_FOODCOM` | CHECKED |
| NEG-0035 | Food.com quantity/parts misalignment: sample **683 of 859 (79.5 %)**; **full corpus 407,536 of 522,517 (78.0 %)** (my scan) | units check JSON, parquet list lengths | PARTIAL (5,237/6,682 text-only) |
| NEG-0036 | NER UNIT << QUANTITY on Food.com: 171,812 vs 3,937,650 (4.4 %); Wikibooks 82.2 %, TASTEset 83.7 % | `ner_corpus_counts_S174.json` | CHECKED |
| NEG-0037 | SP-002: **1,275,782 of 4,281,956 lines (29.8 %)** carry U+2044; recounted here: Food.com 1,275,153, TASTEset 441, Wikibooks 0, denominator reconciles; parser still lacks U+2044 handling at HEAD | coverage census JSON, S175/S177 line censuses, grep of `grammar.py` | PARTIAL (BBC 188 and shapes text-only) |
| NEG-0038 | P1 **HANDBOOK_REVISION_REQUIRED**: 5 of 9 categories above 0.20 (coref 0.9558, final_state 0.8169, event_type 0.7629, entity_type 0.2361, event_argument 0.2268); 7 pairs | `p1_agreement_counts_S166.json` | CHECKED |
| NEG-0039 | 07.A v4 kappa paradox: pooled kappa 0.0 vs >= 0.80, raw agreement 0.9944, 5 disagreements in 900 cells, prevalence 1.00 in all 5 critical fields | `step07_v4_agreement_result_run2.json` | CHECKED |
| NEG-0040 | Layer-2 evaporation bug: cores above 100 C 47,198 of 68,783 (**68.6 %**, INTENSE) -> 1,242 (1.8 %, all dry-class); median dose 341 -> 9.2 min, p99 37,422 -> 116 | `scenario_L2_*_full_S176_v02.json` | CHECKED |
| NEG-0041 | Salt-unit bug: salt load 100x too high; 13,391 POINT values in the 1,000-recipe census wrong (lotstate, superseded) | `lotstate_census_1000_S176.json`, FINAL-SCI review | PARTIAL (butter inputs from the review) |
| NEG-0042 | lotstate pH crosswalk bug: BAND_RANK lacks EXACT; **147 EXACT rank-1 rows dropped, 123 ING left with no entry** | `food_ph_fda_ing_crosswalk_draft_v1.csv`, `lotstate/ph.py` | PARTIAL (apricot/carrot/tomato ranges text-only) |
| NEG-0043 | Scenario defaults all unverified: heat 27/27, non-heat 38/40 (2 retired) SOURCE_UNVERIFIED_AGENT_RECALLED; review 97 rows, 0 human-verified; 149 windows all QUALITATIVE_ONLY | four registry CSVs | CHECKED |
| NEG-0044 | BBC gram coverage does not carry over: lines with grams BBC 75.3 % -> Wikibooks 59.0, TASTEset 56.7, Food.com 0.0, Gutenberg 0 lines; recipes with every line in grams 10.0-17.3 % | S175 and S177 line censuses | PARTIAL (284 TASTESET lines text-only) |
| NEG-0045 | Stated liquid T above T_boil: 520 events lifted, **197 state more than 150 C** (probable L1 mis-association); open for a human | `scenario_L2_*_S177_v03.json` | PARTIAL (core up to 204 C text-only) |

Things the verification changed or pinned down:
- **Numbering.** The ledger acceptance says "NEG-0032+", but the register ends at NEG-0030 and NEG-0031 is unused anywhere in the tree, so the rows start at NEG-0031 (contiguous). Say so if NEG-0031 was meant to be reserved.
- **Bracket.** The plan's "68.6 % -> 1.8 %" is the INTENSE bracket (47,198/68,783); TYPICAL is 66.8 % -> 1,130 and GENTLE 26.6 % -> 300. The row names the bracket.
- **Food.com 79.5 %** is a sample figure (859 recipes); the full-corpus scan gives 78.0 %. Both are in the row.
- **123 ING** (pH) recomputes exactly: 145 ING have an EXACT rank-1 row, 22 also have a HIGH row, 123 have none.
- **S171 vs S176** are different corpora (all five families vs four non-BBC); the like-for-like pair is ungated vs gated inside NEG-0032, which says so.
- Not added (outside S171-S177 or no source in this tree): G08-3 FAIL (D-034) and DEL-2 shortcut suspicion are not in the register; the 195-of-380 false-ABSENT figure of FINAL-SCI #6 (fixed by the router lane, content table under edit by another lane). The register rows still need the H4 human review.

## 3. T3-C03-R2: ING / ALIAS coverage census

Method (`MENTION_RULE_V1`, in the tool header): mention = Food.com ingredient *name* field (never the quantity field), or for Wikibooks and TASTEset the text after the quantity with every (...) / [...] group removed, cut at the first comma. Lookup = the Rung A food lexicon (ACTIVE ING canonical names and ALIAS surfaces; fingerprint `9678937f6a9a0ff6`). Classes: EXACT_ING, EXACT_ALIAS (whole phrase), PARTIAL (a sub-span matches), MISS. Deciles by mention mass and by phrase rank, coverage curve, hapax share, non-exact queue size. A bug found on the way and fixed before the final run: a leading "(3/4 cup)" swallowed the food on 1,115 Wikibooks lines (now 70 lines without a food phrase, mostly quantity-only lines such as a bare amount and unit).

| family | mentions | distinct phrases | EXACT ING / ALIAS | PARTIAL | MISS | any hit | phrases for 80 % of mentions |
|---|---:|---:|---:|---:|---:|---:|---:|
| Food.com | 4,129,433 | 7,198 | 62.55 / 19.64 % | 16.69 % | 1.11 % | 98.89 % | 324 |
| Wikibooks | 31,966 | 8,255 | 51.86 / 11.85 % | 33.70 % | 2.59 % | 97.41 % | 1,972 |
| TASTEset (lines) | 3,779 | 1,665 | 48.95 / 9.53 % | 37.66 % | 3.86 % | 96.14 % | 910 |
| TASTEset gold FOOD spans | 4,020 | 1,096 | 73.68 / 7.84 % | 13.21 % | 5.27 % | 94.73 % | 353 |
| Gutenberg | NOT_AVAILABLE | | | | | | no ingredient lines (S177 F6); NER spans not persisted |

By mention-mass decile (Food.com, % exact): deciles 1-5 100 %, then 86.2, 79.2, 70.6, 57.4, 28.1. The head is fully mapped; coverage falls off in the tail (Wikibooks deciles 9-10: 7.3 and 6.5 %). Top 10 Food.com phrases hold 23.4 % of mentions, top 300 hold 78.9 %, top 1,000 93.5 %. The non-exact queue: 6,086 Food.com phrases, of which the top 633 hold 80 % of the non-exact mentions (T3-C03-R3 sizing: "top ~300 covering ~80 %" holds for all mentions, not for the non-exact ones).

Reconciliation: lines with no lexicon food match equal the S177 Mac-tool `NO_FOOD_MENTION` counts exactly (45,825 / 538 / 129, delta 0), so the Rung A reading and the S175 line census agree. NER context (`ner_corpus_counts_S174.json`, counts only, torch absent so no per-span hit rate): FOOD spans 4,133,781 over 4,098,353 of 4,129,433 Food.com lines; 35,411 over 31,543 of 32,036 Wikibooks lines; 4,032 over 3,756 of 3,788 TASTEset lines.

Law 6 deviation to approve: the unmapped top-500 lists are short food phrases with counts. The ledger acceptance asks for "unmapped top-500 list by frequency (counts, no recipe text)", but law 6 says third-party text never enters committed files, so the three CSVs are in `data/derived/s178_analysis/unmapped_top500_{FOODCOM,WIKIBOOKS,TASTESET}.csv` (git-ignored; sha256 in the JSON). I wrote there, which is outside my four ownership patterns; it is the law-6 location for derived lists. Move or delete as you see fit.

Reading caveat: EXACT is strict (a modifier such as "fresh" or a brand word keeps a phrase from matching); PARTIAL means the lexicon found a food inside the phrase (the Rung A and S175 notion of a food mention). ING/ALIAS are UNVERIFIED registries, so a hit is "the registry has this surface", not a verified identity.

## 4. T4-C04-R1: what the corpus can say

Inputs: committed `reports/step26/` censuses (heat L1 `binding_census_L1_*_S176_v02` and the S173 BBC file; non-heat L1 `nonheat_L1_*_S176`; heat L2 `scenario_L2_*_S177_v03`; non-heat L2 `nonheat_L2_*_S177_v03`). The committed JSONs have no joint "time and temperature", no per-process rows and no heat UNKNOWN reasons, so the tool aggregates the per-event records behind them (`data/derived/physical_L1_full_S176v02`, `physical_L2_full_S177v03`, `physical_NH_L1_*`) into counts. **Reconciliation: PASS** for every source (heat events, duration, temperature, medium, size, lid, start mode, water ratio, matrix class, gas mark, driver-bounded, L2 status, non-heat events; 0 L1/L2 alignment errors). The aggregate sha256 is identical across two runs.

Food.com heat events (1,503,261; % of events), `corpus_can_say_v1.md` tables 1-6 and figures 1-3:

| measure | Food.com | Wikibooks (11,433) | Gutenberg (182,049) |
|---|---:|---:|---:|
| time stated (value or range) | 30.87 | 24.31 | 3.21 |
| temperature stated in the text | 3.68 | 6.37 | 0.57 |
| temperature bound (text + carried setpoint + boil = 100 C) | 14.95 | 20.77 | 30.17 |
| time and temperature both in the text | 1.88 | 3.18 | 0.18 |
| time stated and temperature bound | 5.86 | 8.23 | 1.09 |
| ranges (time / temperature) | 9.94 / 0.04 | 8.28 / 0.31 | 0.55 / 0.0 |
| gas mark only (events) | 237 | 1 | 0 |
| medium known (mostly by process definition) | 52.12 | 50.41 | 72.00 |
| piece size class known (from cut history) | 9.27 | 11.10 | 13.49 |

By family (Food.com): DRY_HEAT time 53.7 %, temperature in the text 9.5 %, both 6.9 %; WET_HEAT 29.0 / 1.1 / 0.1 (36.3 % temperature bound only through boil/steam = 100 C); FAT_HEAT 22.6 / 0.9 / 0.15; HEAT_GENERAL (cook, heat, melt) 21.5 / 2.4 / 0.35. By process (top 15 in the report, all in the JSON): bake time 62.0 %, temperature in the text 11.2 %, both 8.5 %; simmer time 55.0 %, temperature 0.2 %; boil 17.8 % / 0.6 %.

Non-heat families (Food.com): a duration (value, range or bound) is stated on 0.0 % (MECHANICAL_CUT) to 40.7 % (RESTING) of events; where a family has a medium or target temperature input (COOLING, FERMENT_LEAVEN, PRESERVATION, STORAGE) it is stated on at most 0.21 % of events.

Top UNKNOWN reasons per family (Food.com): heat L2 v03: HEAT_GENERAL 97.8 % missing `medium` (95.4 % `bath_c`), 0 reach SCENARIO_COMPUTED; FAT_HEAT 23.6 % missing `duration_min`; WET_HEAT 24.5 % missing `medium`; DRY_HEAT at most 2.2 %. Non-heat L1: COOLING `medium_temperature` NO_TEMPERATURE_STATED 99.96 %, MECHANICAL_MIX emulsified NO_FLAG_CUE 99.2 %, PRESERVATION duration 97.5 %, STORAGE `medium_temperature` 99.98 %. Non-heat L2 v03 reasons are quoted from the committed JSON.

Figures: no matplotlib in the venv, so three dependency-free SVGs (light surface, direct labels, `<title>`/`<desc>`) with the numbers in sibling CSVs: `fig1_heat_time_temperature_joint`, `fig2_foodcom_heat_inputs_by_family`, `fig3_foodcom_top_unknown_reasons`. I checked well-formedness and text extents programmatically but could not rasterise them here (no renderer on the server); a quick visual check before they go on a slide is advised. TASTEset has 0 heat events (no step lists); the BBC row is only the committed S173 totals (same L1 binder 0.1.0; BBC records are not on this server).

## 5. Tests

`tests/unit/test_s178_analysis_{evd_card,negregister,coverage_census,corpus_can_say}.py` (+ `test_s178_analysis_helpers.py`, a loader with no tests): 26 passed. Synthetic ledgers and lexicon (invented rows, test only) for the generators; append-only behaviour on a temp register; Wilson interval equals the committed 0.0262; svg well-formedness; plus structural checks that read the committed outputs (card sha equals the current EVD ledger, census reconciles with S177, every quoted negative-result figure recomputes).

## 6. compute_runs rows (proposed; the orchestrator owns `registry/compute_runs_v1.csv`)

All: host manjot-server, tree `~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)`, git_commit `3da963d+uncommitted`, nice -n 10, `.venv312`, load average about 91 on 128 cores throughout.

```csv
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S178-ANA-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),3da963d+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,12,tools/s178_analysis_corpus_can_say.py --aggregate --workers 12,data/derived/s178_analysis/can_say_agg.json,a91fb1deb9bcd6d3d132349ea560e9be2744e5df94d7e9a8754a5934630b7ae7,2026-11-09T09:17:58Z,2026-11-09T09:19:19Z,DONE,"git-ignored counts file; 1,696,743 heat + 3,027,750 non-heat events; same sha256 as an earlier run from 2026-11-09T08:58:37Z (smoke run on 2 parts per family before that); alignment errors 0"
RUN-S178-ANA-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),3da963d+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,1,tools/s178_analysis_corpus_can_say.py --build,reports/s178/analysis/corpus_can_say_v1.json,a6c07064f21d2eabaaa7194adf325323c14503955e8076ba22d236345962b7e5,2026-11-09T09:19:29Z,2026-11-09T09:19:31Z,DONE,"reconciliation PASS; md b8e20f63...; figures fig1 6ecddb5c..., fig2 f4b98870..., fig3 d47232d9...; a first build 09:19:19-09:19:21Z was superseded by a wording fix (BBC binder note) and re-run"
RUN-S178-ANA-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),3da963d+uncommitted,FOODCOM WIKIBOOKS TASTESET,1,tools/s178_analysis_coverage_census.py,reports/s178/analysis/ing_alias_coverage_census_v1.json,f6f09bafca54f536320953ada17fa453e6ba7283990017296f7c79d2ec39e2fc,2026-11-09T09:19:21Z,2026-11-09T09:22:14Z,DONE,"4,129,433 + 32,036 + 3,788 lines; lines without a lexicon match equal S177 NO_FOOD_MENTION (delta 0); unmapped lists in data/derived/s178_analysis (git-ignored): FOODCOM cc5d38cd..., WIKIBOOKS 0063126a..., TASTESET 8663400f...; an earlier run (09:01Z, before the parenthesis fix) is superseded"
RUN-S178-ANA-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),3da963d+uncommitted,BOGNAR-2002 PHENOL-EXPLORER-3.6 USDA-RETN-R6,1,tools/s178_analysis_evd_card.py --selfcheck,reports/s178/analysis/evd_dataset_card_v1.json,d97d1af7804df874af8d24976998feddb44f9850cf1c8f7c38299ee7fc6540fc,2026-11-09T09:22:14Z,2026-11-09T09:22:58Z,DONE,"two runs inside the command byte-identical (json and md e4e33bc0...); same sha256 as a separate run at about 09:08Z; EVD/COND/SRC/MEAS/SNAP sha256 unchanged before and after; EVD sha 5b3b1939... equals the 15a.R commitment"
RUN-S178-ANA-005,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),3da963d+uncommitted,—,1,tools/s178_analysis_negregister.py --append --full-scan,registry/negative_results_register_v1.csv,bcb2dfd5d797d8106d3e806ce199a0bcb67e3aad9b58abf33fd133d851c6d84f,2026-11-09T09:14:04Z,2026-11-09T09:14:18Z,DONE,"appended NEG-0031..NEG-0045 (15 rows); old file sha256 8a4707641c2694ac... is an exact byte prefix; git diff +15/-0; includes a full Food.com list-length scan (522,517 recipes)"
RUN-S178-ANA-006,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),3da963d+uncommitted,—,1,tools/s178_analysis_negregister.py --append --full-scan,reports/s178/analysis/negative_results_s171_s177_verification_v1.json,f9cf031b49e3768df8a91fd27deef87226ddbc3f034b36edbad08f15fe4f0f83,2026-11-09T09:22:58Z,2026-11-09T09:23:04Z,DONE,"idempotent re-run: 0 rows appended, register sha256 unchanged (bcb2dfd5...); 83 checks (74 VERIFIED_COMPUTED, 9 VERIFIED_TEXT_ONLY), 0 mismatch; md 525d43d2..."
RUN-S178-ANA-007,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),3da963d+uncommitted,—,1,python -m pytest -q tests/unit/test_s178_analysis_*.py,—,,2026-11-09T09:23:04Z,2026-11-09T09:23:09Z,DONE,"26 passed in 3.4 s"
```

Tool sha256: corpus_can_say `647b8504...`, corpus_can_say_render `ad8b7059...`, coverage_census `aa8f8a27...`, evd_card `83ec5ae2...`, negregister `1f8bb3e2...`.

## 7. Bugs, hazards and gaps found (none fixed; outside this lane or by rule)

1. **SP-002 still open at HEAD.** `src/culinarystate/quantity/grammar.py:56-62` (`normalize_text`) handles the vulgar fractions in `UNICODE_FRAC` (line 16) but not U+2044. Recount here: 1,275,153 Food.com lines and 441 TASTEset lines contain it. Proposed fix (as S177 F1): `s = s.replace("⁄", "/")` after `html.unescape`, with tests for "1⁄2 cup" and "1 1⁄4 teaspoons". Re-run the Food.com-dependent counts after.
2. **`src/culinarystate/recipes/corpus.py` `iter_foodcom` (about lines 94-95)** pairs quantity and part by index and pads or truncates; 78.0 % of Food.com recipes (407,536 of 522,517) have lists of different length. Proposed fix: pair only when the lengths are equal, otherwise emit the parts with no quantity (the lot-state reader's FOODCOM_QP_LENGTH_MISMATCH rule). Anything built on its `ingredient_lines` inherits the mispairing; my census uses the parts field only, so it is unaffected.
3. `reports/lotstate/lotstate_census_1000_S176_ph_provisional.json` is not relabelled INVALID in-file (consolidation B1 asked for it; the file is not mine). `registry/superseded_outputs_S176.csv` lists the S176 supersessions but has no rows yet for v02 -> v03 (S177_SCIFIX-PHYS section 7 lists them).
4. USDA SRC-000001 carries `licence_status` ASSUMED although the DEL-1 card calls it a US federal work in the public domain; the card reports the ledger value. A human licence review (H2) should settle it.
5. Unit spelling in the ledger: "mg/100 ml" (678 rows) and "mg/100 mL" (282) are separate strings, and pressure units "Mpa" (27) and "MPa" (17); not merged (raw preserved).
6. Duration is 100 % UNKNOWN for Bognar and temperature 100 % UNKNOWN for USDA; every model that conditions on T and t can use only the 1,575 Phenol-Explorer rows (8.76 %).
7. Observation, not a bug: L1 temperature values like "530/3" are exact Fractions of a degree C (350 F), not mis-reads.

## 8. Needs a human or the orchestrator

1. Copy the card to `reports/step15/dataset_card_15a_v1.{md,json}` if that path is the acceptance path; decide who reviews it (Kush and Parv) and whether 15a freezes on it.
2. Approve or reject keeping the unmapped top-500 name lists out of git (law 6); T3-C03-R3 needs them (the files exist locally).
3. NEG numbering (NEG-0031 start) and the H4 human review of NEG-0031..0045 (all DRAFT_PENDING_H4).
4. Decide the open physics question in NEG-0045 (197 stated liquid temperatures above 150 C).
5. Add the compute_runs rows above and the superseded-registry rows (item 3 of section 7).
6. Whether "EXACT" (whole-phrase) or "EXACT + PARTIAL" (a food is found) is the number the T3 report quotes; both are in the census.

## 9. Files

- `tools/s178_analysis_evd_card.py`, `tools/s178_analysis_negregister.py`, `tools/s178_analysis_coverage_census.py`, `tools/s178_analysis_corpus_can_say.py`, `tools/s178_analysis_corpus_can_say_render.py`
- `tests/unit/test_s178_analysis_{evd_card,negregister,coverage_census,corpus_can_say,helpers}.py`
- `reports/s178/analysis/`: `evd_dataset_card_v1.{md,json}`, `negative_results_s171_s177_verification_v1.{md,json}`, `ing_alias_coverage_census_v1.{md,json}`, `ing_alias_coverage_census_v1_tables.csv`, `corpus_can_say_v1.{md,json}`, `fig1_heat_time_temperature_joint.{svg,csv}`, `fig2_foodcom_heat_inputs_by_family.{svg,csv}`, `fig3_foodcom_top_unknown_reasons.{svg,csv}`
- `registry/negative_results_register_v1.csv` (rows NEG-0031..NEG-0045 appended)
- `data/derived/s178_analysis/` (git-ignored: `can_say_agg.json`, `unmapped_top500_*.csv`, run logs; about 1 MB)

## S178 correction (FIX-GOV, 2026-11-09)

Appended by the S178 FIX-GOV lane (GOV review findings GOV-1, GOV-2, GOV-6; SCI-B review findings B1, B2, CORP-1). Nothing above was rewritten. The values above are the first build's values and are kept as history; the values below replace them. Status: AI_DRAFTED / PROPOSED, counts only.

**1. What the corpus can say (T4-C04-R1, GOV-1).** The first build read superseded inputs: heat L1 `binding_census_L1_*_S176_v02` plus the S173 BBC file, non-heat L1 `nonheat_L1_*_S176`, and L2 `*_S177_v03`. The tool now reads the S178 v04 censuses and records (`*_S178_v04.json`, `data/derived/physical_*_S178v04`). It refuses any input listed in `registry/superseded_outputs_S176.csv` (`culinarystate.governance_superseded`). Reconciliation is still PASS with 0 alignment errors. The BBC row is gone: its only heat L1 census (S173, binder 0.1.0) is superseded, and the v04 re-run can only be done on the Mac (D-003). Heat event counts are unchanged (Food.com 1,503,261; Wikibooks 11,433; Gutenberg 182,049).

| Food.com / Wikibooks / Gutenberg, % of heat events | old (v02 / v03 inputs) | new (v04) |
|---|---|---|
| time stated | 30.87 / 24.31 / 3.21 | 30.87 / 24.31 / 3.21 (unchanged) |
| temperature stated in the text | **3.68 / 6.37 / 0.57** (55,364 / 728 / 1,042 events) | **3.26 / 5.55 / 0.51** (48,952 / 634 / 932) |
| temperature bound (text + carried setpoint + boil = 100 C) | 14.95 / 20.77 / 30.17 | 14.6 / 20.02 / 30.14 |
| time and temperature both in the text | 1.88 / 3.18 / 0.18 | 1.77 / 3.07 / 0.18 |
| time stated and temperature bound | 5.86 / 8.23 / 1.09 | 5.8 / 8.13 / 1.09 |
| neither | 60.05 / 63.15 / 67.7 | 60.33 / 63.81 / 67.73 |

- Headline (table row T4-C04-R1): the temperature stated in the text goes from 3.7 % to **3.3 %**, both in the text from 1.9 % to **1.8 %**, and neither from 60.1 % to **60.3 %**.
- Food.com by family (time / temperature in the text / both): DRY_HEAT 53.7 / 9.5 → **8.9** / 6.9 → **6.7**. WET_HEAT 29.0 / 1.1 → **0.35** / 0.1 → **0.06**; its temperature bound goes from 36.3 % to **35.6 %**. FAT_HEAT 22.6 / 0.9 → **0.5** / 0.15 → **0.1**. HEAT_GENERAL 21.5 / 2.4 → **2.2** / 0.35 → **0.3**.
- Heat L2 HEAT_GENERAL: missing `bath_c` goes from 95.4 % to **95.6 %**. Missing `medium` stays 97.8 %, and 0 events reach SCENARIO_COMPUTED.
- Files (sha256 prefix): `corpus_can_say_v1.json` `32cbed9f2ce6c522`, `.md` `d3fb2d78d9363558`. The figures `fig1..3` were regenerated, and every SVG `<desc>` now says AI_DRAFTED (GOV-8).

**2. EVD dataset card (T2-C15-R1; SCI-B B1, BLOCKER; EVD lane request).** The card is now version 0.2.0. Its json and md hashes are `1e7af6e2…` and `2cca6ed8…`; `--selfcheck` gave identical output twice. Corrections to the Conditions bullet:
- temperature "RANGE 3,585" → **216 two-sided ranges + 3,369 one-sided censored bounds** (Bognar core "> 75 C").
- "a_w not in the COND schema" → **a_w is a COND schema field (`water_activity`) that no row fills (0 of 17,978)**.
- pressure: MEASURED 129, NOT_APPLICABLE 7,018 (USDA), and **10,831 rows where pressure is not in the completeness mask**, now shown as "not recorded". Every axis row sums to 17,978.
- missingness now counts "not recorded" as missing: pressure is missing on **100 % of Bognar rows (was 0 %)** and **96.67 % of Phenol-Explorer rows (was 0 %)**.
- The card was copied byte-identical to `reports/step15/dataset_card_15a_v1.{md,json}`, listed in `reports/step15/README_S178_copies.md`. RUN-S178-EVD-007 was re-run and reproduces the new card hash.

**3. ING/ALIAS coverage census (CORP-1).** The bare "79.5 %" note now reads "78.0 % of recipes, 407,536 / 522,517, full corpus; the S176 seeded sample gave 79.5 %, 683 / 859". The census was re-run, and only that note line changed: json `2652fa09…`, md `ecebc5ba…`.

**4. Negative-results register (B2, T9-C08-R4).** Rows NEG-0047 to NEG-0049 were appended; NEG-0032 and NEG-0045 are unchanged:
- NEG-0048 supersedes NEG-0032's gated figures. As of router census 0.3.0 (S177), gated DIRECT is **40,308 (0.114 %)**, recipes with any DIRECT are 37,773, and NOT_APPLICABLE is 813,547.
- NEG-0049 supersedes NEG-0045's counts. As of v04, 241 events are lifted and **21 are above 150 C** (v03: 520 and 197).
- NEG-0047 records G08-3 FAIL, which was missing.
- The DEL-2 shortcut suspicion (D7 identical to D1 on Phenol-Explorer) is already NEG-0004, so no new row was added.
- The corrected row NEG-0032 in table 4 above should be read with NEG-0048.

**5. Open item 3 above.** `reports/lotstate/lotstate_census_1000_S176_ph_provisional.json` is now registered as INVALID_SUPERSEDED_KEPT_ON_RECORD in `registry/superseded_outputs_S176.csv`. The v02 → v03 → v04 rows were added, and each `superseded_by` now ends at a live file.

## S179 correction (physics v06, 2026-11-10)

**What the corpus can say (T4-C04-R1).** The tool (0.3.0) now reads the S179 v06 censuses and records
(`*_S179_v06.json`, `data/derived/physical_*_S179v06`). The S178 v04 inputs are superseded (FIX-PHYS v05, then v06
after the S179 SCI re-review). No v05 build was made, so the change below is v04 -> v06. New files
`corpus_can_say_v2.{json,md}` and `fig1..3_*_v2.{svg,csv}`; the v1 files stay on record (registered as superseded).
Run rows RUN-S179-ANA6-001..002. Reconciliation PASS, 0 heat L1/L2 alignment errors; heat events unchanged
(Food.com 1,503,261; Wikibooks 11,433; Gutenberg 182,049).

| % of heat events | Food.com v04 | v06 | Wikibooks v04 | v06 | Gutenberg v04 | v06 |
|---|---:|---:|---:|---:|---:|---:|
| temperature stated in the text | 3.26 | 3.29 | 5.55 | 5.32 | 0.51 | 0.52 |
| temperature bound | 14.60 | 14.84 | 20.02 | 19.81 | 30.14 | 30.15 |
| time and temperature both in the text | 1.77 | 1.83 | 3.07 | 3.04 | 0.18 | 0.18 |
| time stated and temperature bound | 5.80 | 5.98 | 8.13 | 8.10 | 1.09 | 1.09 |
| temperature ranges | 0.03 | 0.08 | 0.31 | 0.31 | 0.00 | 0.02 |
| gas mark only (events) | 246 | 218 | 1 | 1 | 0 | 0 |

Food.com by family, temperature in the text: DRY_HEAT 8.89 -> 9.22 %, FAT_HEAT 0.50 -> 0.30 %, WET_HEAT 0.35 -> 0.20 %
(food targets and setter temperatures no longer counted as the medium temperature). Time-stated shares are unchanged.
BBC v06 censuses exist only on the Mac (D-003) and are not in these tables.
