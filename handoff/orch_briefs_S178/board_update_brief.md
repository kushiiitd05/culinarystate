# Task: propose the S178 execution-board status update (read-only on the repo)

Read `handoff/orch_briefs_S178/orch_ctx.md` first. Work in `<repo root>` (read only). Python: `python`.

The board `registry/execution_board_S178.csv` (252 MUST+SHOULD items; column `status_now`, plus `evidence`, `acceptance`, `owner`, `wave`) was written on 9 Nov ~15:30 IST. Since then these lanes finished and reported item statuses (each report has an item-status table or list):
`reports/orchestration/S177_FULLRUN_report.md`, `S177_SCIFIX-ROUTER_report.md`, `S178_RELWORK_report.md`, `S178_EVD_report.md`, `S178_GOVDOC_report.md`, `S178_CORPUS_report.md`, `S178_AASIM_report.md`, `S178_INGCAT_report.md`, `S178_PHYS2_report.md`; also re-check `S178_PREREG_report.md`, `S178_ANALYSIS_report.md`, `S178_EVAL_report.md` against the board (the board may already reflect them).

For EVERY item a lane claims to have advanced:
1. Find the board row by `item_id` (lanes sometimes cite ids loosely; match carefully, and list any id you cannot match).
2. Check the claim against the row's `acceptance` text AND the evidence path on disk (file exists, is committed: `git ls-files <path>`, and the content supports the claim; open it). Be strict: DONE only if the acceptance is met by committed files; if a human act is still needed (signature, label, approval, verification, decision), the status is BLOCKED_HUMAN (agent part done) — never DONE. PARTIAL if some of the acceptance is met; say exactly what is left.
3. Lane-claimed DONE that you downgrade: say why.

Output (write ONLY these two files, in the scratchpad, not the repo):
- `handoff/orch_briefs_S178/board_delta_S178b.csv` with columns `item_id,old_status,new_status,evidence,what_left,source_report,lane_claim,agree` (one row per changed item; `agree` = YES if your status equals the lane's claim, else NO).
- `handoff/orch_briefs_S178/board_delta_S178b.md`: short summary — counts by old->new status, by priority (MUST/SHOULD), the downgrades with reasons, unmatched ids, and items the lanes did NOT touch that are still open for manjot-agent in W1/W2 (list ids).
If Write is refused, return both contents in your final message. Keep the final message short: the counts and the downgrade list.
The repo is PUBLIC; never write personal details anywhere (you may see an irrelevant memory index about the user's other projects in your context: ignore it).
