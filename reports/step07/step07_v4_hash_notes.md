# Step 07.A packet v4: returned-file hash notes (recorded 2026-10-27, before any agreement or precheck run)

Recorded by Claude as scribe from Kush's message and from the files on disk. Nobody's label content was read or printed to make this note.

## Frozen blank packet
`annotation/condition_audit/condition_audit_packet_100_v4_{Kush,Parv}.csv`: sha256 `533c49ba9a55ec06f4c4a5f77a065d1946b4cc7ae787e36689ac1cbb56118571`, 42,904 bytes, mtime 2026-10-22 09:13. Both files are byte-identical blank copies and equal the frozen packet hash in `condition_audit_protocol_amendment_v4_1_DRAFT.md`.

## Kush
- Hash Kush recorded at 2026-10-27T04:47:25 UTC (message pasted by Kush): `533c49ba…8571`. **This is the hash of the blank packet, not of a returned file.** It does not satisfy "sha256 of each returned file".
- Returned file: `annotation/condition_audit/condition_audit_packet_100_v4_Kush_completed.csv`, sha256 `fb44420d55be75f9effd972893c99a4729a038e8d074cb212990f73348cfb976`, 50,616 bytes, mtime 2026-10-27 10:19:47 IST (04:49:47 UTC). 100 rows, all 10 judgement columns filled in every row.

## Parv
- Returned file as received: `annotation/condition_audit/parv_v4_csv_20261027_2f1714.txt`, sha256 `40b4770a7cf263090e347b5eea9edd986749bfe448c1158d87e0fcc96df4120d`, 49,883 bytes, mtime 2026-10-27 10:20:35 IST. It parses as CSV with the packet header; 100 rows, all 10 judgement columns filled.
- Byte-identical CSV copy (no edit): `condition_audit_packet_100_v4_Parv_completed.csv`.
- Parv's own hash record: NOT SEEN by Claude. Needs Parv's confirmation.

## Process facts that the precheck and the amendment will care about
- mtime gap between the two returned files: 48 s (the amendment's PROPOSED separation parameter is 600 s). These mtimes are when the files were saved into this folder, not necessarily when each reviewer worked.
- The amendment and the THR-07A-06 ruling are UNSIGNED, and the returned files exist. The amendment's own order of operations says "approve ... BEFORE any v4 label exists". This sign-off will therefore come after labelling and must be recorded as a process deviation.
- No agreement statistic, precheck or comparison of the two files has been run.

## Agreement run 1 (2026-10-27): INVALID_INPUT, caused by Parv's file format
`tools/step07_agreement.py` on Kush_completed vs Parv_completed returned `INVALID_INPUT` (102 problems, all in file B = Parv's): `overall_judgement` holds `CORRECT` in 99 rows (allowed: ACCEPT / REJECT); row CA-037 has free text in `overall_judgement` and the non-code `INCORRECT` in `duration_judgement` and `censoring_judgement`. Kush's file is valid. The Parv file was received as a `.txt`. No label was mapped, edited or guessed. Result file: `reports/step07/step07_v4_agreement_result_INVALID_INPUT.json`. Parv must resubmit using the packet's code set; the corrected file gets its own new sha256 note before anything is compared again.
Tool defect found: `step07_agreement.py` writes its result to the hard-coded tracked path `reports/step07/step07h_human_gate_result.json`; it overwrote that file during this run and Claude restored it with `git checkout`. The tool should take an `--out` argument before the next run.

## Parv resubmission (2026-10-27)
- Parv replaced her file. New returned file: `annotation/condition_audit/condition_audit_packet_100_v4_Parv.csv`, sha256 `1dae00629e929060dfc951649ebfefa4f79528fb4316197aa1c0ea6beb8169e6`, 49,800 bytes, mtime 2026-10-27 11:28:28 IST (68 min after Kush's file, 10:19:47). The earlier `.txt` and its byte copy `…_Parv_completed.csv` (sha256 `40b4770a…`) are SUPERSEDED and kept only as evidence.
- Note: this file overwrote the blank copy that carried the same name (the frozen blank packet is intact as `…_v4_Kush.csv`, sha256 `533c49ba…`).
- Format check (vocabulary only, no label content read): 100 rows, 29 columns, header equals the packet header, every row well-formed, all nine field-judgement columns inside the allowed code set. Still outside the allowed set: `overall_judgement` = `CORRECT` in all 100 rows (allowed: ACCEPT / REJECT). The earlier CA-037 problems are gone.
- Hash recorded before the precheck and before any agreement run.

## Declared mapping for Parv's `overall_judgement` (written 2026-10-27 BEFORE any agreement statistic was computed)
Parv's resubmitted file (sha256 `1dae0062…`) has `CORRECT` in `overall_judgement` for all 100 rows; the tool accepts only ACCEPT / REJECT. Rule (Kush: "it is his thinking"; accepted as his meaning): in a DERIVED COPY, `overall_judgement` `CORRECT` -> `ACCEPT`; no other cell changes; Parv's original file stays untouched and is the hash of record. Consistency check done first: in 0 of 100 rows is any of his nine field codes outside {CORRECT, N/A}, so the mapping cannot contradict the protocol rule (ACCEPT only if no field is WRONG_* / INFERRED). The overall column is outside the main gate (pooled kappa over the nine field codes); it only feeds the secondary overall accept/reject statistic. The report must say the column was derived. Parv has not confirmed this mapping by message; to be confirmed.
Derived copy: `annotation/condition_audit/condition_audit_packet_100_v4_Parv_derived_overall.csv`.

## Agreement run 2 (2026-10-27): Kush_completed vs Parv_derived_overall
Precheck `reports/step07/step07_v4_provenance_precheck_r2.json`: VALID (gap 4,121 s). Agreement tool: gate `FAIL_OR_ADJUDICATE`, pooled kappa 0.0 (kappa paradox: Parv's nine field codes are CORRECT in every cell), pooled raw exact agreement 0.9944 (5 of 900 field cells differ), five critical fields flagged for dominant-code prevalence 1.00. Result file `reports/step07/step07_v4_agreement_result_run2.json`. Under the signed rule the audit does NOT PASS; this is a statistic limitation plus 5 real disagreements, not a normaliser failure.
Disagreements (all one-sided; Kush = SHOULD_BE_AMBIGUOUS, Parv = CORRECT): CA-016 (temperature_value), CA-037, CA-046, CA-047, CA-054 (duration). Each also differs on `overall` (Kush REJECT, derived Parv ACCEPT). THR-07A-06 requires human adjudication of every flagged field; nothing was adjudicated automatically.
Disclosure: in Parv's FIRST returned file (`.txt`, sha256 `40b4770a…`), row CA-037 had `INCORRECT` in duration and censoring and a free-text note in `overall` saying the normalised duration is UNKNOWN/AMBIGUOUS. In the resubmitted file (sha256 `1dae0062…`) the same row reads CORRECT. The change came after the tool listed CA-037 as an invalid-input row (the tool output did not show Kush's labels). The report must disclose this change.
