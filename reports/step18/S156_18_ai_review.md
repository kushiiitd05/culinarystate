# AI verdict — pending Kush/Parv review

S156 AI cross-review of the Step 18 engine drafts (DRAFT_PENDING_16c). 2026-11-03, branch
`cloud/s156-step18-events`.

This is an **AI verdict** by worker "prv" (an agent, not Parv), written under D-045. It is not
an approval, a human review, an adjudication or a signature. Kush and Parv review it afterwards,
and their review is final. All fixtures are synthetic (SYNTHETIC_NOT_GOLD). No ledger row was read
or written, and no pre-S156 file was edited.

## Scope

Reviewed: `src/culinarystate/state_graph/{event_log.py, replay.py, event_adapter.py}`,
`tests/unit/test_step18_{event_log,replay,adapter}.py` (119 tests) and
`reports/step18/S156_engine_audit.md`, by worker "ksh". I checked them against the Plan Step 18
card (method 1–8, negative controls, G18.1–G18.5) and the S155 auditor. I looked for correctness
bugs, determinism holes, append-only violations, invariant gaps and over-claims. Each defect was
first reproduced with a scratch script against the unmodified files. A failing test was then
committed (RED, `tests/unit/test_step18_review_fixes.py`, commit `2fd91f3`) before the fix.

## Findings

Severity: HIGH = breaks a project law or a stated invariant. MEDIUM = wrong verdict or a silent
acceptance of bad input. LOW = a robustness gap or an edge case.

| ID | Sev. | Evidence (reproduced before the fix) | Disposition |
|---|---|---|---|
| R1 | HIGH | `event_adapter`: a CATEGORICAL or IDENTIFIER claim traced `SPAN_LITERAL` has a value equal to its span text (the auditor checks this). The adapter copied `str(c.value)` into `EngineEvent.attributes`, so recipe text reached the event log JSONL: `"style":"secret sauce"` from a synthetic source. This breaks the module's own rule ("carry no raw text") and the third-party-text law. | **FIXED** `041e0b4`. Span-literal attribute values are never copied. They are reported as `LITERAL_TEXT_ATTRIBUTE_NOT_COPIED` (new adapter UNKNOWN code). Rule-, candidate- and registry-traced codes are copied as before. |
| R2 | MEDIUM | `EventLog.from_jsonl` rebuilt each event with `from_canonical`, which ignores unknown keys. It then compared hashes computed from the rebuilt event. A line with an injected field (inside `event` or at the top level) stayed canonical and kept a valid chain, so it was **accepted and the field was silently dropped**. The docstring says non-canonical or edited lines are refused. | **FIXED** `a4f884f`. After the chain check, the re-serialised entry must equal the line byte for byte. |
| R3 | MEDIUM | `replay_events` did not check event-id uniqueness. Two different events with id `E1` were both APPLIED, `Snapshot.applied == (("E1",0),("E1",0))`, status PASS. `depends_on` and any `recipe_event_id` link become ambiguous. The audit's "Ids never reused: Covered" holds for entity ids only. (`replay_log` was safe because `effective()` keeps one event per id. The adapter's `INTRO/<id>` events could collide with a graph event id.) | **FIXED** `c83959d`. New issue code `EVENT_ID_REUSED`. A later event with an id already seen in the replay (applied, rejected or skipped) is REJECTED. |
| R4 | LOW | `canonical_json(ensure_ascii=False)` leaves U+2028, U+2029 and U+0085 unescaped, but `from_jsonl` split with `str.splitlines()`, which also breaks on them. A valid log whose id held one of these characters failed to read back (`line 0: not JSON`). This was a determinism / round-trip hole. | **FIXED** `a4f884f`. Lines are split on `"\n"` only. |
| R5 | LOW | `guard_output_path` compared the protected prefixes case-sensitively. `Ledgers/x.jsonl`, `DATA/…`, `Exports/…` and `annotation/Gold/…` were accepted. On the Mac (case-insensitive APFS) these paths are the protected folders. | **FIXED** `a4f884f`. Path parts are case-folded before the comparison. |
| R6 | MEDIUM | `_balance` with an unknown sibling compared Σ low(known) with high(parent), which drops the correlation. In the probe, p ∈ [100, 120] g, a = 0.9 p, b = 25 g and c is unknown. a + b > p for every p (0.1 p ≤ 12 < 25), but the result was `UNKNOWN / TERM_UNKNOWN` and the split was APPLIED. | **FIXED** `c83959d`. The exact correlated residual is used: high(p − Σ known) < 0 ⇒ `MASS_BALANCE_FAIL`. This check is strictly stronger than the old one, so every earlier FAIL is still a FAIL. Unknown outputs are still assumed ≥ 0, as before. |
| O1 | LOW | `Quantity` has no dimension of its own. An exact zero (for example a remainder after a fraction-1 split) becomes `terms=[]`, `bounds.dim=None`. A later split of that entity then gives `BASIS_DIMENSION_MISMATCH` instead of 0 g. | OPEN. The fix changes the hashed snapshot form, so it is a contract choice for humans or 16c. |
| O2 | MEDIUM | `AdaptedGraph.replay()` returns the replay result only. Adapter issues such as `INVENTED_VALUE_EXCLUDED`, `EVENT_NOT_ADAPTABLE` and `ENTITY_WITHOUT_PRODUCER` are not part of `ReplayResult.status`, so a replay can report PASS while the adapter excluded values or dropped events. Callers must check `AdaptedGraph.issues` separately. | OPEN. API design choice: merge them into the status, or require callers to check both. |
| O3 | LOW–MED | Two lots that carry the same QNT `ref` are treated as one measurement base, and are fully correlated. With different bounds (`Q1` 100 g and `Q1` 50–60 g) they are treated as two bases. Neither case is flagged (status PASS). Reuse of a ref may double-count one grounded quantity. | OPEN. Should a QNT ref be unique per replay, and what code should reuse get? |
| O4 | LOW | `alloc_id` uniqueness is not checked, within an event or across events (two `A` allocations: PASS). Issue paths that use `alloc_id` become ambiguous. | OPEN. A suggested code is `ALLOC_ID_REUSED`. Not fixed, because it changes behaviour that V4 owns as `DUPLICATE_ID`. |
| O5 | LOW | In `_Adapter.events()`, `terms.pop(...)` runs before the `EngineEvent` constructor. When the constructor raises (`EVENT_NOT_ADAPTABLE`), the popped quantity terms are lost without their own `QUANTITY_NOT_ADAPTABLE` report. The event-level issue is still reported. | OPEN (informational). |
| O6 | LOW | Ids are hashed as given. NFC and NFD spellings of the same id give different hashes. | OPEN. Should ids be normalised in 16c? |
| O7 | INFO | Over-claims in `S156_engine_audit.md` (not edited by this review): "Ids never reused — Covered" (event ids were not covered, R3); "copies codes and ids only, never raw text" (R1); "`from_jsonl` refusing non-canonical lines" (lines with extra fields were accepted, R2). | OPEN for the author / coordinator: correct the audit text, or point to this review. |

Checked and found sound (no finding): the hash chain covers seq, prev and the event. `EventLog`
has no rewrite path. `effective()` takes the latest revision at the first position. Floats cannot
enter `EngineEvent`s, `Quantity` uses exact `Fraction`s only, and key ordering is canonical. There
is one transaction per event with the card's six fields. Rejected events change no state.
`EXPLICIT_ONLY` handles skipped dependencies and products. The fraction-sum logic per (parent,
basis) is correct. The auditor's path format (`<owner_id>/<field>`) matches the adapter's exclusion
paths, so invented-value exclusion does work. The 119 existing tests still pass unchanged.

Card items already listed as open in the audit (§5) are not repeated here as findings. They
are: observation override (method 6), `transition_tuples_v1` / `prefix_packets_v1` (18e), the
invalidation graph (method 8), lot statuses OPTIONAL / ALTERNATIVE / GARNISH / UNRESOLVED, 18a
persistence, the 18f hang, the cascade when a rejected event still advances the order key, and
G18.1–G18.5 (not evaluated: no adjudicated Gold).

## Verification

- `tests/unit/test_step18_review_fixes.py`: 11 tests, all RED before the fixes and all green
  after them.
- Full unit suite with thread caps (`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
  python -m pytest tests/unit -q -p no:cacheprovider`): 2166 passed, 17 skipped, 1 deselected,
  1 failed + 11 errors. The failure and errors are the same missing data-bundle files as the
  2119-pass baseline. Nothing new fails. The 2166 passes include the 36 Step 26g tests added in
  the same session.
- `git diff --check` is clean.

## For Kush / Parv

1. Accept or reject R1–R6 and their fixes. R1 adds the adapter UNKNOWN code
   `LITERAL_TEXT_ATTRIBUTE_NOT_COPIED`. R3 adds the replay issue code `EVENT_ID_REUSED`.
2. Decide O1–O6.
3. Decide whether the S156 audit text is corrected for O7.
