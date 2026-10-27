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
