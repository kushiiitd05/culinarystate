# AI verdict — pending Kush/Parv review

**S157 AI cross-review of worker "ksh"'s parts A-C (Step 09 machinery, 12.0 registration, 12-local parsers and staging).**
Reviewer: worker "prv", an AI agent and not Parv. Under D-045 this is an AI verdict. It is not an
approval, a sign-off or a human verification; Kush and Parv review it and their review is final.
Every test cited here uses synthetic fixtures. The data bundle (`data/raw`, `data/external`,
`data/interim`) is not in this container, so nothing was run on the real Bognar text or the real R2
CSV.

Scope read: `src/culinarystate/evidence/{machinery,extraction_fields,registration,step12_local}.py`,
`src/culinarystate/ingest/{usda_yields_r2,bognar_remaining}.py`,
`tools/{step12_0_register_local_files,step12_local_stage}.py`, the four S157 test files,
`reports/step09/S157_09_audit.md`. These were compared with the formats encoded in
`tools/ingest_bognar.py` + `src/culinarystate/ingest/{bognar,bognar_build}.py`,
`tools/ingest_bognar_yields.py`, `tools/ingest_usda_r6.py`, `tools/infoods_transition_candidates.py`,
`reports/bognar_v1.md`, the acquisition manifest and the ledgers (read only).

## Findings

| id | severity | evidence | disposition |
|---|---|---|---|
| R1 | medium | `Proposal.family` was `extractor_id.split("@")[0]`, so the comparison was case-sensitive. One extractor written as `ai:synthetic-model-x@1` and `AI:Synthetic-Model-X@2` counted as two families, and a blind CONFIRM then gave `E4_ELIGIBLE_PENDING_ADJ`. Test: `test_s157_ai_review_regressions.py::test_r1_*`. | FIXED (`ef86e5d`): family is trimmed and casefolded. |
| R2 | medium | `_tier_candidate` did not compare the reviewer with the extractors. Kush as `HUMAN_EXTRACTOR` plus one AI proposal, then a blind CONFIRM by Kush, gave `E4_ELIGIBLE_PENDING_ADJ`. That is self-confirmation, not the card's independent blind adjudication. Test: `test_r2_*`. | FIXED (`0ec325b`): the result is E5 when the reviewer is one of the item's human extractors. A confirmation by Parv is still eligible. |
| R3 | medium | `map_licence_status` mapped every `VERIFIED_*` prefix to VERIFIED. This contradicted its docstring ("only literal VERIFIED / ASSUMED survive"). The manifest row DS-003 reads `VERIFIED_AT_INGESTION; re-check failed (TLS certificate mismatch on phenol-explorer.eu); search found no terms page` and was mapped to VERIFIED. DS-038 `RESTRICTIVE_AGREEMENT` was mapped to UNKNOWN. The default 12.0 entries (DS-002/006/007/014) were not affected, and DS-003 is LOCAL_ONLY anyway through H2 #5. Test: `test_r3_*`. | FIXED (`9ff786a`): VERIFIED only for the exact tokens VERIFIED / VERIFIED_AT_INGESTION; anything qualified becomes UNKNOWN; RESTRICTIVE becomes RESTRICTED. |
| R4 | medium | `_classify` kept only the last sub-variant mark line. `reports/bognar_v1.md` shows that table 35 really has stacked header lines (`'Constituentss boil', 'a)', 'boil', 'b)'`). On that layout the `a)` chunk was dropped from `sub_variant_raw` and `column_header_raw`, which breaks the raw-preserved law. Test: `test_r4_*`. | FIXED (`8f57296`): every mark line is kept per column. Parser version strings were not bumped because no staging output exists yet. |
| O-1 | medium | `HumanReview(...)` is a public constructor. HUMAN_VERIFIED can therefore be reached in memory without any review file. `write_queue_jsonl` only checks that a review matches the given file; code can write such a CSV naming Kush or Parv. The audit said this "blocks forged or upgraded reviews" and called the tests a "proof". | Audit and docstring wording FIXED (`a4fa341`, `9bbbfd0`). The underlying limit stays OPEN for humans: decide the provenance rule for review files (for example, accepted only from a Kush/Parv commit or a signed file). |
| O-2 | low | v1 (`bognar_build.py`) stores every value ≥ 1.0 as CENSORED GT_CAP. The remaining-tables parser treats only `"1.00"` as `CENSORED_GT_CAP_CANDIDATE` and marks values > 1.00 MEASURED. No value > 1.00 is known; `value_raw` is kept, so either reading can be recovered. | OPEN: harmonise at the G12 audit. |
| O-3 | low | v1 finds the first data row only on a line with a decimal value. `_is_data` also accepts a line whose only value token is `-`, so an alpha-led header or title-continuation line containing ` - ` would become the first data row and the header would be lost (`UNMAPPED_NO_METHOD_LINE`). This could not be checked without the text. | OPEN: on the real run, look at any remaining table reported `UNMAPPED_NO_METHOD_LINE`. |
| O-4 | low | With several method-label lines, only the last supplies labels; earlier ones become product sub-columns. On the T35-like synthetic layout, both columns read `EQUAL_GROUPS_AND_POSITION_AGREE` from a single label. The raw headers are now complete (R4). | OPEN: design decision for G12-3 (downgrade to UNCONFIRMED or not). |
| O-5 | low | The R2 parser skips short rows, which pandas (used by `tools/infoods_transition_candidates.py`) would pad. Expected cross-check: `reports/sources/infoods_transition_candidates.csv` holds 173 R2 rows, so the real run should report `rows_staged = 173`, `rows_skipped = 0`. The header normalisation maps all nine column names that the pandas tool uses (checked). | OPEN: needs the bundle. |
| O-6 | low | The R2 `_numeric` uses `Decimal()`, which also accepts `1_000` and `1e2` as MEASURED. No such cell is known. | OPEN. |
| O-7 | low | A family is the id string before `@`. Two model names from one vendor lineage count as different families, but the card asks for "a different model family". | OPEN: needs the human-maintained prompt/extractor registry (card output `registry/prompt_registry_v1.csv`). |
| O-8 | info | For DS-006/007/014 (`ledger_src_family = none`), the SRC re-registration check is the mint key `manifest:DS-xxx`, which no existing SRC uses. An SRC minted earlier under another key would not be detected. The ids ledger holds related lineage keys (`SRC-000493` `pe_yield_src:PECOT 1956_USDA-AH-102`, `SRC-000495` `pe_yield_src:USDA_2010_SR23`); these are not the R2 file. Placeholder numbers restart in every staging file. | OPEN: Kush checks this at the re-baseline review. |

## Checks with no defect found

- **Ledger writes:** every S157 writer resolves symlinks, calls `assert_safe_write_target`, refuses
  `ledgers/`, `exports/` and `annotation/gold/` relative to the root and refuses ledger-like file
  names. Each writer opens its file in `"x"` mode. Both tools verify the 08a baseline before and
  after on the repository root. No path writes `ledgers/data`. `verify_baseline` gives 7/7 after
  this review.
- **Raw third-party text:** Bognar and R2 staging can only go under `data/interim/` (git-ignored) or
  outside the repo. The 12-local report passes `assert_counts_only`. The 12.0 staging rows carry
  manifest metadata and hashes only. The machinery stores span sha256s and never span text.
- **VERIFIED / E4 by code:** no code assigns tier E4. HUMAN_* comes only from `_derive_status` on a
  `HumanReview` (limit O-1). Registration proposes `verification = UNVERIFIED` and never COMMIT_OK.
- **Id reuse:** no id is minted. `PROPOSED-*` placeholders and SNAP `sha256:` keys are checked
  against `_ids.jsonl`. Queue ids are content hashes, not ledger ids.
- **Formats:** the Bognar parser reuses the v1 vocabularies (TABLE, letters_of, methods_of, CANON,
  SKIP_TARGETS, ESTIMATED, PORTION, FAMILY). Its table list equals the 11 tables that
  `reports/bognar_v1.md` lists as skipped. v1 EVD locators (`Part 2 table N, method, basis`) are read
  correctly, including methods that contain a comma (ksh `bdadd71`). Part 1 yields
  (`ingest_bognar_yields.py`) and R6 (`ingest_usda_r6.py`) are not re-parsed; the diff reads them
  from EVD only.
- **Audit numbers:** reproduced read-only. There are 17,978 latest-ACTIVE EVD rows: 14,108
  UNVERIFIED, 3,870 AI_PRECHECKED, 0 HUMAN_VERIFIED, all E3. `test_step09_machinery.py` has 55 cases.

## OPEN for Kush and Parv

O-1 (review-file provenance rule), O-2 and O-4 (Bognar encoding choices at G12), O-3 and O-5 (check
on the real run), O-6, O-7 (extractor-family registry), O-8 (SRC re-registration check). The ksh
audit's own O-1 to O-6 remain as written.
