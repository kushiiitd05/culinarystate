# Step 07 archive — v3 agreement output (NOT_COUNTED)

Status: DRAFT_PENDING_H4 (record; not a gate result). Written 2026-10-26 under D-027 / Execution Plan v2 §7 ("archive of the v3 agreement output with sha256 before any 07.A run"). Nothing here is a gate result; nothing was edited.

Location note (2026-10-26, review fix F4): this record first sat in `reports/step07/archive/`, which is git-ignored (`.gitignore:35`, pattern `archive/`), so it could never have been committed. It was moved (rename, no content change) to `reports/step07/v3_not_counted_archive/`, which is not ignored; the JSON stayed a byte copy (mode 0444, mtime 2026-10-22 19:47 preserved) and its sha256 was re-verified after the move. `.gitignore` was not touched. The plan's own output path (`reports/step07/step07h_human_gate_result_v3_NOT_COUNTED.json`, no folder) remains an alternative that Kush may prefer; the choice is a human decision (see `reports/step04/README.md` §4 D).

## Files and hashes

| File | Bytes | sha256 |
|---|---|---|
| `reports/step07/step07h_human_gate_result.json` (original, left in place, untouched) | 4238 | `b1c856ba35e7390f5f305a1d3a9a0e4a9998655efe3da926d21da49dc6dad2ff` |
| `reports/step07/v3_not_counted_archive/step07h_human_gate_result_v3_NOT_COUNTED.json` (immutable byte copy, mode 0444, mtime preserved) | 4238 | `b1c856ba35e7390f5f305a1d3a9a0e4a9998655efe3da926d21da49dc6dad2ff` |

The copy was made with `cp --preserve=timestamps` and checked with `cmp` (byte-identical) and `sha256sum` (equal hashes) on 2026-10-26; after the folder move both checks were repeated and still hold. Re-verify at any time with `sha256sum reports/step07/v3_not_counted_archive/step07h_human_gate_result_v3_NOT_COUNTED.json`.

Content in one line: gate `NOT_COUNTED_PROVENANCE_INVALID`; pooled κ 0.9978 over 100 conditions (retained as a record, not as a pass); the two returned v3 files were written 11 s apart (07:53:11 / 07:53:22), judgement columns identical on 899/900 cells; critical-field flags on basis / retention_type / censoring at dominant-code prevalence 1.00; `counts_as_human_gate: false`; the `provenance_check` block was written by hand, not by the tool. It is also negative-results register row NEG-0029 (`registry/negative_results_register_v1.csv`, R-19).

## Why this archive exists (plan conflict X3)

`tools/step07_agreement.py` hard-codes its output path. The string `reports/step07/step07h_human_gate_result.json` appears at:

- L3 (docstring: `... -> reports/step07/step07h_human_gate_result.json`),
- L54 (the `INVALID_INPUT` branch writes the file),
- L90 (the normal branch writes the file).

So the first run on packet v4 (with either outcome, valid or `INVALID_INPUT`) would overwrite the retained v3 NOT_COUNTED result, which R-19 requires to be preserved. The tool was **not edited** (it is a frozen, preregistered gate computation; R-06). Its sha256 at the time of writing: `5cd53dc30d0eb1628f8045a7477e93de15e870f40c391bde14d6852b0d2674b3`. The protocol it implements (`reports/step07/condition_audit_protocol.md`) has sha256 `ed4d1824a3b4aff3d188e1b8a2b2e0a3a358cca44a1b12455a936c79e204a0af`.

## Handling rule for 07.A (proposed; the plan's Step 07 card item (4))

1. Before the run: verify the archive hash above; verify the packet freeze (`python tools/step07hr_freeze.py --verify`); make sure the 01.6 row for 07.A exists, **is signed** (`signed_by` and `signed_at` set in `registry/preregistered_thresholds_v1.csv`, THR-07A-01..08; the draft rows are `PROPOSED_VERBATIM_UNSIGNED` / `PROPOSED_PILOT` and do not satisfy this) and has `data_seen_before_registration = N`.
2. Run the unchanged tool on the two v4 packets (Mac).
3. Immediately move the tool's output out of the hard-coded path to a versioned v4 file (`reports/step07/step07_human_gate_result_v4.json`) and restore the v3 original from this archive to the hard-coded path **or** leave the hard-coded path to hold only the latest raw tool output and never cite it; humans decide which, before the run. Either way the archive copy stays the immutable v3 record.
4. Provenance validity (`counts_as_human_gate`) and the diagnostics annex are produced by separate scripts, never by editing the tool.

Open point for humans: whether to leave the original at the hard-coded path (done here, because the plan says "archive", not "move") or to remove it after the archive is accepted.
