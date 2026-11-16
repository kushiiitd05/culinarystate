# Run-log gap audit (S179, T9-C11-R2)

Status: **AI_DRAFTED, read-only**. `registry/compute_runs_v1.csv` is edited by the orchestrator, so nothing here
changes the CSV. Audit at 94e1014 on 2026-11-10: 282 rows.

## Acceptance check

- **Rows with an empty status:** 0.
- **Rows with an empty output_sha256:** 12. All of them declare why: no kept output, scratchpad, stdout, a test run, or the output was deleted.
  - RUN-S178-PHYS2-026..028 declare only `(deleted)`. The orchestrator may want a sentence on why.
- So the acceptance "0 rows with empty status/hash except declared" is **met**, if `(deleted)` counts as a declaration.

## Rows without a start or end time

27 rows. The start time cannot be recovered from the repository, so it stays blank: no time is invented. For each row,
the end time has an upper bound: the commit that first added the run row. The run row is written after the run, so
the run ended before that commit. The output file's commit is not used, because an output can predate its run
(RUN-S178-FIXGOV-012's output was first committed on 8 Nov; the run was on 9 Nov).

| run_id | host | start | end | end at or before (row's first commit) | commit |
|---|---|---|---|---|---|
| RUN-S171-001 | mac | — | — | 2026-11-08T12:38:27+05:30 | 926d081 |
| RUN-S171-002 | vinayak-server | — | — | 2026-11-08T12:38:27+05:30 | 926d081 |
| RUN-S171-003 | vinayak-server | — | — | 2026-11-08T12:38:27+05:30 | 926d081 |
| RUN-S172-001 | mac | — | — | 2026-11-08T12:38:27+05:30 | 926d081 |
| RUN-S172-002 | mac | — | — | 2026-11-08T12:43:08+05:30 | c522f28 |
| RUN-S172-003 | mac | — | — | 2026-11-08T12:43:08+05:30 | c522f28 |
| RUN-S173-001 | mac | 2026-11-08T13:04 | — | 2026-11-08T13:07:52+05:30 | 6790aa0 |
| RUN-S173-002 | mac | — | — | 2026-11-08T13:07:52+05:30 | 6790aa0 |
| RUN-S173-003 | mac | 2026-11-08T13:08 | — | 2026-11-08T13:35:02+05:30 | 946a557 |
| RUN-S173-004 | mac | 2026-11-08T13:08 | — | 2026-11-08T13:35:02+05:30 | 946a557 |
| RUN-S173-005 | mac | 2026-11-08T13:08 | — | 2026-11-08T13:35:02+05:30 | 946a557 |
| RUN-S174-001 | manjot-server | — | — | 2026-11-08T14:00:39+05:30 | 7fd02f9 |
| RUN-S174-002 | vinayak-server | — | — | 2026-11-08T14:21:57+05:30 | e003803 |
| RUN-S174-003 | vinayak-server | — | — | 2026-11-08T14:21:57+05:30 | e003803 |
| RUN-S175-001 | mac | — | — | 2026-11-09T11:48:20+05:30 | 39e8410 |
| RUN-S175-002 | mac | — | — | 2026-11-09T11:51:52+05:30 | 2a13103 |
| RUN-S175-003 | mac | — | — | 2026-11-09T11:57:38+05:30 | 9a40765 |
| RUN-S176-ROUTER-006 | manjot-server | — | — | 2026-11-08T23:24:02+05:30 | daae740 |
| RUN-S176-REVB-001 | manjot-server | — | — | 2026-11-08T23:24:02+05:30 | daae740 |
| RUN-S176-REVB-002 | manjot-server | — | — | 2026-11-08T23:24:02+05:30 | daae740 |
| RUN-S176-LSRC-001 | manjot-server | — | — | 2026-11-08T23:24:02+05:30 | daae740 |
| RUN-S177-ROUTER-001 | manjot-server | — | — | 2026-11-09T16:14:22+05:30 | b2ba3c0 |
| RUN-S178-CORP-009 | manjot-server | — | — | 2026-11-09T16:28:46+05:30 | 2d45f68 |
| RUN-S178-INGCAT-003 | manjot-server | — | — | 2026-11-09T19:10:08+05:30 | 3a71056 |
| RUN-S178-FIXGOV-010 | manjot-server | — | — | 2026-11-09T20:48:41+05:30 | 35b9220 |
| RUN-S178-FIXGOV-011 | manjot-server | — | — | 2026-11-09T20:48:41+05:30 | 35b9220 |
| RUN-S178-FIXGOV-012 | manjot-server | — | — | 2026-11-09T20:48:41+05:30 | 35b9220 |

Proposal for the orchestrator (not applied): write the bound into `notes` as `end<=<time> (row commit <hash>)`. Leave
`start` and `end` empty rather than filling estimates. S179 rows written by the Mac agent all carry start and end.
