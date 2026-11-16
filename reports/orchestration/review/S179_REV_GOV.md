# S179 re-review, GOV pass (fixer snapshot 6f8d1bc + S179 follow-ups, vs 3d97196)

AI review (Sonnet subagent), read-only. AI review is not human verification (D-071).

**Verdict: no blockers.** No agent-made signature, approval, nonce or freeze; prereg originals untouched; the 07.A-R1
amendment draft recommends B (R-06 unchanged); ledgers and `quantity/grammar.py` byte-identical; `compute_runs_v1.csv`
13 columns, unique ids, failed / aborted rows kept, append-only vs 3d97196; committed BBC outputs counts-only; superseded
registry test 9 passed.

| # | Severity | Finding | Disposition (S179) |
|---|---|---|---|
| 1 | MINOR | `superseded_outputs_S176.csv`: 48 rows re-pointed (chain collapse), not appended | Intentional: the integrity rule forbids a replacement that is itself superseded. Every re-pointed row keeps its old target in `reason` ("re-pointed S179 ... (was X)"); pre-collapse rows also recoverable at 3d97196 |
| 2 | MINOR | `ing_sr_defaults_v1.csv`: `bay leaf` row deleted without stated reason | Ticket A10 (4 non-ACTIVE ING terms; successors `bay`, `feta` already mapped); reason in `handoff/MAC_TASKS_FROM_CONSOLIDATION_S177.md` Mac reply and commit 9c7ad84 |
| 3 | MINOR | host labels and `~/Kush/` paths in public run rows | Existing practice (170 such rows before S179); no IPs, usernames or credentials. Open: generic host labels in a later cleanup if Kush wants |
| 4 | MINOR | uncommitted MECH v05 outputs at review time | Committed with run rows RUN-S179-MECH-001..005 |
