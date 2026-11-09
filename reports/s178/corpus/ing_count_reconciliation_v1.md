# ING count reconciliation and vocab status (S178, T3-C03-R1)

Status: AI_DRAFTED / PROPOSED. Counts only; no ingredient names, no recipe text. Tool `s178-corpus-ing-reconcile-0.1.0-draft`.

## What each number counts

| number | what it counts | where it is quoted |
|---:|---|---|
| 1,951 | ACTIVE ids first written by the A1 (BBC) registry build (a1_ner+registry_build@0.1): 1951 in the ledger now; the report's own ledger-write tally (4 created + 1,867 unchanged + 80 revised = 1,951) is that build's output. STALE as a description of the current ledger: it omits the Wikibooks-link ids added by a later step (and does not track later status changes). | `reports/ingredient_registry_v1.md` L4, `reports/fdc_crosswalk_v0.md` L3 |
| 5,387 | ledger VERSION LINES of ING.jsonl (append-only), not concepts: 2110 ids + 3277 later versions (enrichment and merge revisions; git history shows the X1 FoodOn, X2 Open Food Facts, X2b merge and X3 Wikibooks commits touching this file). The review packet's 'ING rows' means these lines. | review packet Q7, `reports/master_plan/master_plan_research_audit_v2.md`, SSOT working notes |
| 2,110 | distinct ING ids of every status (2048 ACTIVE + 49 SUPERSEDED + 13 DEPRECATED). | `reports/orchestration/S176_L-LOT_report.md`, plan 'x of 2,110' |
| 2,048 | distinct ING ids whose latest version is ACTIVE; this is the ING set the Rung A lexicon and every S175-S178 census use (`rung_a_lexicon._latest_active`). | S176 L-LOT / L-PH reports, Rung A lexicon |

## Verdict

- Current concept count: **2,048 ACTIVE ING concepts** (2,110 ids ever, 5,387 ledger lines).
- Stale report: reports/ingredient_registry_v1.md (and reports/fdc_crosswalk_v0.md): '1,951 ING concepts' is the first BBC-only build, not the current vocabulary. Quote 2,048 ACTIVE concepts (1,951 BBC-derived + 97 Wikibooks-linked) with the ledger lines (5,387) named as lines.
- Mislabelled wording: '5,387 ING rows' (review packet Q7, master-plan audit, SSOT working notes) counts ledger lines; say '2,048 ACTIVE ING concepts (5,387 ledger lines)'. The statement 'crosswalked 0 %' in packet Q7 refers to USDA/FDC: {'UNRESOLVED_EXTERNAL': 2048}; FoodOn LINKED is 27.0 %.
- File that produced 5,387: ledgers/data/ING.jsonl (wc -l); not a separate Food.com-extended registry: the consensus R-SSOT guess 'suspected Food.com-extended ING' is NOT supported (no ING line has a Food.com provenance agent).
- BBC-only claim: the A1-derived ids are 1,951 of 2,048 ACTIVE (95.3 %); Wikibooks links add 97; no Food.com or Gutenberg ING ids exist in the ledger.

## Ledger counts per type (read-only)

| ledger | lines | ids | ACTIVE ids | latest-status other than ACTIVE | lines beyond first version | verification of ACTIVE |
|---|---:|---:|---:|---|---:|---|
| ALIAS | 4,183 | 4,116 | 4,103 | {'DEPRECATED': 13} | 67 | {'UNVERIFIED': 4103} |
| ALLERGEN | 11 | 8 | 8 | - | 3 | {'UNVERIFIED': 8} |
| COND | 4,746 | 4,414 | 4,414 | - | 332 | {'UNVERIFIED': 4414} |
| DATASET | 5 | 5 | 5 | - | 0 | {'UNVERIFIED': 5} |
| DOC | 1,967 | 1,967 | 1,967 | - | 0 | {'UNVERIFIED': 1967} |
| EVD | 57,280 | 18,156 | 17,978 | {'DEPRECATED': 178} | 39,124 | {'AI_PRECHECKED': 3870, 'UNVERIFIED': 14108} |
| EXP | 8 | 7 | 7 | - | 1 | {'UNVERIFIED': 7} |
| IMAP | 31,972 | 30,294 | 30,294 | - | 1,678 | {'UNVERIFIED': 30294} |
| ING | 5,387 | 2,110 | 2,048 | {'DEPRECATED': 13, 'SUPERSEDED': 49} | 3,277 | {'UNVERIFIED': 2048} |
| KGE | 80,607 | 48,181 | 45,201 | {'DEPRECATED': 2980} | 32,426 | {'UNVERIFIED': 45201} |
| MEAS | 3 | 3 | 3 | - | 0 | {'UNVERIFIED': 3} |
| MOL | 1,726 | 1,726 | 1,726 | - | 0 | {'UNVERIFIED': 1726} |
| PROC | 552 | 156 | 156 | - | 396 | {'UNVERIFIED': 156} |
| REC | 107,760 | 89,565 | 89,565 | - | 18,195 | {'UNVERIFIED': 89565} |
| SNAP | 347 | 346 | 346 | - | 1 | {'UNVERIFIED': 346} |
| SRC | 609 | 488 | 488 | - | 121 | {'AI_PRECHECKED': 5, 'NEEDS_SOURCE': 4, 'UNVERIFIED': 479} |
| SRC_08A_YIELD | 7 | 7 | 7 | - | 0 | {'UNVERIFIED': 7} |
| STUDY | 257 | 132 | 132 | - | 125 | {'UNVERIFIED': 132} |
| SVAR | 355 | 224 | 224 | - | 131 | {'UNVERIFIED': 224} |
| TOOL | 297 | 119 | 119 | - | 178 | {'UNVERIFIED': 119} |
| UNIT | 74 | 74 | 74 | - | 0 | {'NEEDS_SOURCE': 4, 'UNVERIFIED': 70} |

## ING vocabulary status (ACTIVE concepts)

| measure | count | % of ACTIVE |
|---|---:|---:|
| ACTIVE concepts | 2,048 | 100 |
| FoodOn crosswalk LINKED | 553 | 27.0 |
| FoodOn CANDIDATE | 296 | 14.45 |
| FoodOn NO_MATCH | 1,199 | 58.54 |
| USDA FDC LINKED | 0 | 0.0 |
| with parent ids | 315 | 15.38 |
| with facets | 235 | 11.47 |
| scientific identity | {'UNKNOWN': 2048} | |

## Origin of the ING ids

| first-version agent | ids | of which ACTIVE |
|---|---:|---:|
| `a1_ner+registry_build@0.1` | 2,013 | 1,951 |
| `wikibooks_links@0.1` | 97 | 97 |

## ALIAS

4,103 ACTIVE aliases; 4,103 have an ACTIVE ING target, 0 do not (the Rung A lexicon drops those). The registry report's '2,052 ALIAS rows' is likewise the first build only.

## Claims checked against their files

| claim | number | file | found in file | line |
|---|---:|---|---|---:|
| ING_CONCEPTS_1951 | 1,951 | `reports/ingredient_registry_v1.md` | True | 4 |
| ING_CONCEPTS_1951_FDC | 1,951 | `reports/fdc_crosswalk_v0.md` | True | 3 |
| ING_ROWS_5387_PACKET | 5,387 | `handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md` | True | 292 |
| ING_LINES_5387_MP_AUDIT | 5,387 | `reports/master_plan/master_plan_research_audit_v2.md` | True | 639 |
| ING_ACTIVE_2048_L_LOT | 2,048 | `reports/orchestration/S176_L-LOT_report.md` | True | 27 |
| ING_IDS_2110_L_LOT | 2,110 | `reports/orchestration/S176_L-LOT_report.md` | True | 27 |

## Notes

- Latest version per id = highest `version` (later line wins a tie), as rung_a_lexicon._latest_active.
- SUPERSEDED / DEPRECATED ids (49 + 13) are no longer ACTIVE; their lines stay in the append-only ledger.
- All vocabulary records are UNVERIFIED (AI-drafted); 'ACTIVE' is a lifecycle status, not a verification status.
- Protected ledgers (EVD, COND, SRC, MEAS, SNAP) were read only; their sha256 are recorded in ledger_file_sha256 for before/after comparison.
