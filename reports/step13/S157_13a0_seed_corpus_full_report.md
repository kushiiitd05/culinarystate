# S157 13a-0 offline seed corpus: counts

**Status: PROVISIONAL_PENDING_13A.** AI-built (worker prv) and counts only; Kush and Parv review it (D-045). No network call, no ledger row, no id minted, no abstract or full text.

Dedup rule: `EXACT_NORMALISED_DOI_ONLY`. DOI transforms applied in order: `STRIP_WHITESPACE`, `STRIP_RESOLVER_URL`, `STRIP_DOI_SCHEME`, `PERCENT_DECODE_URL_FORM`, `CASE_FOLD_ASCII`. Not applied: `TRAILING_PUNCTUATION_TRIM`, `INTERNAL_WHITESPACE_REMOVAL`, `UNICODE_CASE_MAPPING`, `UNICODE_NORMALISATION`, `PREFIX_REPAIR`, `NETWORK_LOOKUP`, `FUZZY_TITLE_MERGE` (see `src/culinarystate/evidence/seed_corpus.py`).

## Inputs

| artifact | present | records | DOI valid | invalid | absent |
|---|---|---|---|---|---|
| queue_v1 | True | 634 | 630 | 0 | 4 |
| rejected_v1 | True | 73 | 73 | 0 | 0 |
| route_a_precheck_v1 | True | 125 | 121 | 0 | 4 |
| human_review_pack_v1 | True | 55 | 55 | 0 | 0 |
| src_ledger_pe_pub | True | 125 | 121 | 0 | 4 |
| doc_ledger_doi | True | 242 | 242 | 0 | 0 |
| query_matrix_v1 | True | 0 | 0 | 0 | 0 |
| openalex_pages | True | 614 | 614 | 0 | 0 |

## Seeds

| key | count |
|---|---|
| total | 715 |
| with_valid_doi | 703 |
| without_valid_doi | 12 |
| invalid_syntax | 0 |
| absent | 12 |
| doi_records_merged_into_an_earlier_record | 1153 |
| doi_seeds_multi_source_record | 701 |
| doi_seeds_multi_artifact | 701 |
| doi_seeds_with_several_raw_forms | 582 |
| doi_seeds_with_conflicting_years | 0 |

Seeds by number of source records: n_1 = 14, n_2 = 556, n_3 = 19, n_4 = 4, n_5_plus = 122.

## DOI transforms applied (records)

| key | count |
|---|---|
| STRIP_WHITESPACE | 0 |
| STRIP_RESOLVER_URL | 614 |
| STRIP_DOI_SCHEME | 0 |
| PERCENT_DECODE_URL_FORM | 0 |
| CASE_FOLD_ASCII | 0 |

## DOI seeds per artifact and pairwise overlap

| key | count |
|---|---|
| doc_ledger_doi | 121 |
| human_review_pack_v1 | 15 |
| openalex_pages | 584 |
| queue_v1 | 630 |
| rejected_v1 | 73 |
| route_a_precheck_v1 | 121 |
| src_ledger_pe_pub | 121 |

| key | count |
|---|---|
| doc_ledger_doi__human_review_pack_v1 | 15 |
| doc_ledger_doi__openalex_pages | 2 |
| doc_ledger_doi__queue_v1 | 121 |
| doc_ledger_doi__rejected_v1 | 2 |
| doc_ledger_doi__route_a_precheck_v1 | 121 |
| doc_ledger_doi__src_ledger_pe_pub | 121 |
| human_review_pack_v1__openalex_pages | 2 |
| human_review_pack_v1__queue_v1 | 15 |
| human_review_pack_v1__rejected_v1 | 2 |
| human_review_pack_v1__route_a_precheck_v1 | 15 |
| human_review_pack_v1__src_ledger_pe_pub | 15 |
| openalex_pages__queue_v1 | 511 |
| openalex_pages__rejected_v1 | 73 |
| openalex_pages__route_a_precheck_v1 | 2 |
| openalex_pages__src_ledger_pe_pub | 2 |
| queue_v1__rejected_v1 | 2 |
| queue_v1__route_a_precheck_v1 | 121 |
| queue_v1__src_ledger_pe_pub | 121 |
| rejected_v1__route_a_precheck_v1 | 2 |
| rejected_v1__src_ledger_pe_pub | 2 |
| route_a_precheck_v1__src_ledger_pe_pub | 121 |

## Access and licence (as stated by the inputs; nothing verified)

| key | count |
|---|---|
| oa_flag FALSE | 190 |
| oa_flag TRUE | 517 |
| oa_flag UNKNOWN | 8 |

| key | count |
|---|---|
| licence_status STATED_BY_INPUT_UNVERIFIED | 327 |
| licence_status UNKNOWN | 388 |

An OA flag is not a reuse licence; `tdm_status` is UNKNOWN for every seed.

## Fuzzy duplicates (report only, not applied)

| key | count |
|---|---|
| applied_to_dedup | False |
| doi_seed_groups_sharing_normalised_title | 2 |
| doi_seeds_in_those_groups | 4 |
| no_doi_seeds_sharing_normalised_title_with_another_seed | 12 |

Method: exact equality of casefolded, punctuation-collapsed titles. Route A titles are full citations, so this under-counts; the 08b detector does real linkage later.
