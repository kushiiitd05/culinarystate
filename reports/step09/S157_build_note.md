# S157 build note — evidence machinery: Step 09, 12.0, 12-local, 13a-0

2026-11-03. Branch `cloud/s157-evidence-machinery`, stacked on `cloud/s156-step18-events` (merge S154 → S157 in order).
Every output is **PROVISIONAL**. There is no evidence freeze, no ledger write and no minted id. The ledger guard
passes 7/7 (EVD/COND/SRC/MEAS/SNAP are byte-identical).

Workflow (D-045): AI worker "ksh" built A–C, AI worker "prv" built D and cross-reviewed A–C, and the coordinator
verified both. Kush and Parv review afterwards, and their review is final. The data bundle is absent: every tool
is synthetic-tested, and real counts come from a local run.

## What was built

| Part | Files | Content |
|---|---|---|
| A — Step 09 | `src/culinarystate/evidence/{machinery,extraction_fields}.py`, `registry/schemas/evidence_verification_queue_item.provisional_v1.schema.json`, `reports/step09/S157_09_audit.md` | 15 field classes, locators, extractor proposals and validators that only flag. A queue item's status is derived **only** from a review file filled in by Kush or Parv. Worker labels and AI names are refused as reviewers. Code never assigns E4, and self-confirmation stays at E5. |
| B — 12.0 | `src/culinarystate/evidence/registration.py`, `tools/step12_0_register_local_files.py` | **Proposed** SRC/SNAP rows go to `registry/staging/` only. They carry placeholder ids checked against `_ids.jsonl` and licence fields from the manifest. An open H2 item makes a row LOCAL_ONLY; any other unrecognised status is UNKNOWN. |
| C — 12-local | `src/culinarystate/ingest/{usda_yields_r2,bognar_remaining}.py`, `src/culinarystate/evidence/step12_local.py`, `tools/step12_local_stage.py` | Parsers for the R2 cooking yields and the 11 remaining Bognar tables. Raw cells are kept; staging goes to the git-ignored `data/interim/`. A read-only EVD diff is labelled NOT_RESOLVED (G08-9 context), and a counts-only report is produced. All 6,594 real v1 Bognar Part 2 locators in EVD parse. |
| D — 13a-0 | `src/culinarystate/evidence/seed_corpus.py`, `tools/step13a0_seed_corpus.py`, `registry/evidence/seed_corpus_13a0_tracked_v0.jsonl`, `reports/step13/S157_13a0_*` | Offline seed corpus deduplicated on the exact normalised DOI (transforms listed in the file). No network access; abstracts are excluded by a field whitelist. From **tracked** artifacts: 1,254 records read, giving **713 seeds** (701 with a DOI, 12 without); licence UNKNOWN for all. |

## AI cross-review (`reports/step09/S157_ai_review.md`)

| ID | Fix |
|---|---|
| R1 | Extractor families are now compared case-insensitively; the false dual extraction could make an item E4-eligible |
| R2 | An extractor can no longer act as their own blind confirmer |
| R3 | The licence mapping no longer turns "VERIFIED…; re-check failed" into VERIFIED |
| R4 | Bognar's stacked sub-variant header lines were being lost |

The audit's over-claims were corrected. Open items O-1 to O-8 are in block F of the review sheet.

## Verification

| Check | Result |
|---|---|
| Full unit suite (thread caps) | **2341 passed**, 17 skipped, 1 deselected. The 1 failed + 11 errors are missing bundle files, unchanged. |
| Ledger guard | 7/7 |
| Pre-S157 files modified | 0 |
| Attribution lines | 0 |
| Raw third-party text in git | none: staging is in git-ignored `data/interim/`; the seed corpus is metadata only |

## Local runs (where the data bundle exists)

```bash
python tools/step12_0_register_local_files.py
python tools/step12_local_stage.py --defaults
python tools/step13a0_seed_corpus.py
```

For the second command, if only the PDF is present, first run
`pdftotext -layout data/raw/bognar/bognar_2002.pdf data/raw/bognar/bognar_2002.txt`.
Expected for R2: 173 rows staged, 0 skipped.

## Needs human

The decisions are listed as block F on the review sheet.
