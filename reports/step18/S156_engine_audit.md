# S156 Step 18 engine audit and event-sourcing contract draft (DRAFT_PENDING_16c)

2026-11-03. Branch `cloud/s156-step18-events`, stacked on `cloud/s155-step17ab`.
Status **DRAFT_PENDING_16c**: hard gate 16c (Step 16 schema pack v1) is open.

This is an **AI verdict** by worker "ksh" (an agent, not Kush), written under D-045.
Kush and Parv review it afterwards, and their review is final. Nothing here is human
review, adjudication, a signature or Gold. All fixtures are synthetic
(SYNTHETIC_NOT_GOLD). No EVT / ENTITY / STATE / ALLOC / REF / GRAPH ledger row was
read or written, and no existing engine file was edited.

Sources read: Plan Step 18 card (`docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`,
`### STEP 18`, substeps 18a–18g, method 1–8, negative controls); SSOT §240
(lines 26260–26319, validator stack V1–V6 and §240.2 canonical rules); the
`state_graph` package; `tests/unit/test_state_engine.py`; `tests/unit/test_transition.py`;
the S155 `extraction` interfaces, V4 invariants and the auditor; and the Step 16 drafts
`reports/step16/schema_drafts/{ALLOC,EVT,ENTITY}.draft_v1.schema.json`, which supply the
vocabularies used (ALLOC kind and basis, EVT trajectory, ENTITY lifecycle).

## 1. What exists (before S156)

| File | Lines | Content |
|---|---|---|
| `state_graph/engine.py` | 352 | Dataclass events (Add, Transform, Merge, Split, Reserve, Discard, Recombine, Transfer, Observe, Predict, OmittedStepCandidate, AcceptCandidate). `replay()` is a pure fold into versioned entities, edges, an audit trail and free-text issues. Three trajectories are tracked per field `Belief`, and observation outranks prediction with the prior kept. `Graph.sha256()` hashes `canonical_json`. |
| `state_graph/symqty.py` | 107 | Symbolic sums coef × Base (g / mL / count / qual). Different dimensions are never added numerically. Interval × fraction propagates. |
| `state_graph/rule_compiler.py` | 222 | Deterministic "B-rules" from recipe text to engine events. |
| `state_graph/source_class.py` | 57 | Simulator data contract: STRUCTURAL_RECIPE cannot carry a magnitude. |
| `state_graph/prefix_state.py` | 33 | Ancestry, processes and the reserved set along a prefix, for H_STATE tooling. |
| `tests/unit/test_state_engine.py` | 141 | 14 tests: symbolic algebra, merge/split/reserve/discard/recombine, observation override, consumed-entity flag, omitted-step candidates, determinism, no label overwrite. |
| `tests/unit/test_transition.py` | 76 | 7 tests of the **DEL-2 retention transition models** (`culinarystate.transition`: numpy, pandas, scikit-learn `HistGradientBoostingRegressor`, grouped bootstrap). It does not test the state graph. |

### Defects and silent behaviours in the existing engine (reproduced, not fixed)

Each item below was reproduced with a scratch script against the unmodified files. The task
did not require fixing them and they lie outside the hang fix, so the files are left unchanged.
They are listed for human decision. The new replay avoids all of them.

| ID | Behaviour (reproduced output) | Why it matters |
|---|---|---|
| L1 | `Reserve("w","r")` with neither `portion` nor `fraction` silently takes **0**: reserved `0`, remainder `100 g`, `issues=()`. `rule_compiler` can emit exactly this (in the drain + "reserving" branch, and in the reserve branch when there is no quantity and no "half"). | Silent default. The unknown amount becomes a known zero. |
| L2 | `SymQty.scale` applies `Fraction(k).limit_denominator(1000)`, so 1/1024 of 1024 g evaluates to **1.024 g**. | Silent approximation that produces an invented value. |
| L3 | `Discard("x", fraction=2)` gives `−100 g` with `issues=()`. `Reserve(..., fraction=3/2)` gives reserved `150 g` and remainder `−50 g` with `issues=()`. | No check that fractions are ≤ 1, outside `Split`. Negative quantities pass silently. |
| L4 | Merge sums the parents, and Transform keeps the quantity: `Merge(a 100 g, b 50 g, "fry")` followed by `Transform("boil")` evaluates to 150 g. | This assumes processes conserve mass. Whether they do is not stated in the sources (R-20: no chemistry from a verb). |
| L5 | `SymQty.evaluate` returns floats rounded to 6 decimals. | Exactness is lost in hashed output. |
| L6 | `engine.canonical_json` uses `json.dumps(..., default=str)`. | Unknown types are stringified instead of refused, which is not strict canonical JSON. |
| L7 | `prefix_state(ev, k, …)` builds its ancestry keys from every `Add` in `ev`, not `ev[:k]`. At k=1 the keys include a label added later (`['a', 'late']`). | The card's leakage control requires prefix packets to be computed from events ≤ t only. Only the keys leak (each value is `{label}`). |
| L8 | Issues are free-text strings, not codes. There is no transaction record, input snapshot hash, config hash or revisions, and no order check. A shuffle is caught only when it breaks consumption. | Required by the card's method 1–3. |

## 2. Card invariants mapped to code

"V4" means the S155 `extraction/invariants.py` checks on a candidate graph. "Replay" means
the new S156 modules.

| Card / SSOT §240.2 invariant | Existing engine | V4 (S155) | S156 replay / adapter | Status |
|---|---|---|---|---|
| Spans round-trip | — | V1 | Not repeated. `NOT_CHECKED: SPAN_ROUNDTRIP_SEE_V1` | Covered by V1 |
| Every ingredient-list lot accounted for | — | `LOT_UNACCOUNTED` / `LOT_STATUS_INVALID` | Final consistency: `LOT_STATUS_CONTRADICTS_REPLAY`, `LOT_NOT_IN_REPLAY`. Completeness is left to V4 (`NOT_CHECKED`). | Covered |
| Nothing consumed before it is produced | string "unknown entity" | `CONSUMED_BEFORE_PRODUCED` | `ENTITY_UNKNOWN`, `ORDER_REGRESSION`, `DEPENDENCY_NOT_APPLIED` | Covered |
| Nothing consumed after DISCARD | string "already consumed/discarded" | `CONSUMED_AFTER_DISCARD` | `ENTITY_REUSED_AFTER_DISCARD`, `ENTITY_ALREADY_CONSUMED` | Covered |
| Split fractions ≤ 1 per compatible basis | `Split` only, no basis (L3) | per (parent, event, basis) | `SPLIT_FRACTIONS_EXCEED_ONE` per (parent, basis). A known sum over 1 fails even when a sibling is unknown, because unknown shares are ≥ 0. UNSPECIFIED basis gives UNKNOWN, as in V4. | Covered |
| Mass balance only when every term is known, else UNKNOWN not FAIL | — | `check_mass_balance` on caller-selected terms | Per allocation parent. Mixed dimensions or any unknown term give UNKNOWN. FAIL only when outputs exceed the input. Exact and correlated. | Covered (partition scope only) |
| Inferred events never feed explicit-only queries | — | OPEN (`not_checked`) | `ReplayConfig(scope="EXPLICIT_ONLY")` skips non-EXPLICIT events (`SKIPPED_SCOPE`). An explicit event that needs their products or dependencies is rejected with `INFERRED_DEPENDENCY_IN_EXPLICIT_SCOPE`. | Implemented, as a replay scope rather than a query layer |
| Invented grams = 0 | by design, but L1 / L2 | auditor (S155) | The adapter runs `audit_outputs` on every call and excludes flagged values (`INVENTED_VALUE_EXCLUDED`), and it carries `invented_count`. The engine derives amounts by exact allocation algebra only. | Covered |
| Issue codes, never silent clamping | strings (L8) | issue / unknown lists | `ISSUE_CODES` / `UNKNOWN_CODES`. An event with any issue is REJECTED and changes nothing. | Covered |
| One transaction per event (input snapshot hash, event revision, output entity versions, quantity changes, issues, config hash) | — | — | `Transaction`: exactly those six, plus seq, event_id, event_sha256, status, unknown, mass_balance and output_snapshot_sha256 | Covered |
| Identical replay gives an identical snapshot hash; canonical JSON; no pandas in the core | `Graph.sha256` (L6) | — | Strict `canonical_json`. Hypothesis property: two replays are byte-identical. No pandas or numpy import (tested). | Covered |
| Interval propagation with correlated split children | symbolic, but L2 | — | `Quantity`: exact linear terms over traced bases, so two halves of 100–120 g close exactly (PASS where naive intervals give [−20, 20]) | Covered for exact fractions. Interval fractions are not propagated (UNKNOWN). |
| Planned / observed / predicted kept apart | per-field Belief | — | One trajectory per replay. Other events are rejected (`TRAJECTORY_MISMATCH`). | Covered (separation only) |
| Observation overrides prediction (prior kept) | implemented | — | Not implemented (`NOT_CHECKED`) | **Gap** |
| Every new intermediate has a producer; split/merge parent–child consistent | — | `INTERMEDIATE_WITHOUT_PRODUCER`, `ALLOC_PARENT_NOT_LISTED` | Adapter `ENTITY_WITHOUT_PRODUCER`. Replay `ALLOC_PARENT_NOT_CONSUMED`, `ALLOC_CHILD_NOT_PRODUCED`. | Covered |
| Ids never reused | "already exists" string | `DUPLICATE_ID` | `ENTITY_ID_REUSED`. Log revisions instead of rewrites. | Covered |
| Current state can be replayed from event history (§240.2) | `replay()` | OPEN | `replay_log(EventLog)` over the latest revisions | Covered |
| Negative control: shuffled order raises invariant issues | — | — | Hypothesis property. The adapter never re-sorts. | Covered |
| Negative control: reuse of a discarded entity fails | flagged (string) | `CONSUMED_AFTER_DISCARD` | Hypothesis property, plus a V4 cross-check on the same graph | Covered |
| 18a persist v1 ledgers | — | — | Not done: 16c is open, and no ledger writes were allowed | **Gap (gated)** |
| 18e `transition_tuples_v1`, `prefix_packets_v1` | — (L7) | — | Not implemented | **Gap** |
| Invalidation graph (method 8) | — | — | Not implemented | **Gap** |
| 18g session layer | — | — | Deferred by the card | Deferred |

## 3. Plan 18f: the `test_transition` hang (investigation)

**Result: not reproduced in this container. No root cause was demonstrated and none is claimed.**
No guard test or fix was added, because there is nothing reproduced for one to guard.

Environment: Linux container, `/usr/local/bin/python` 3.13.18 (`/opt/anaconda3` does not exist
here), 4 CPUs, numpy 2.5.3, scikit-learn 1.9.1, pytest 9.2.0. `threadpoolctl` reports two OpenBLAS
runtimes (scipy 0.3.31.dev, numpy 0.3.34) and scikit-learn's bundled `libgomp`. torch, lightgbm and
xgboost are not installed. No `*_NUM_THREADS` variable was set in the environment.

| # | Command (from the repo root) | Observed |
|---|---|---|
| 1 | `timeout 120 python -m pytest tests/unit/test_transition.py -q -p no:cacheprovider` (no caps) | 7 passed in 1.31 s, exit 0 |
| 2 | `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 120 python -m pytest tests/unit/test_transition.py -q -p no:cacheprovider` | 7 passed in 1.26 s, exit 0 |
| 3 | Run 1 repeated 5 times | 5/5 passed (1.25–1.40 s) |
| 4 | `OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 timeout 120 …test_transition.py…` | 7 passed in 2.32 s |
| 5 | `OMP_NUM_THREADS=64 OPENBLAS_NUM_THREADS=64 timeout 120 …test_transition.py…` | 7 passed in 5.43 s |
| 6 | `timeout 900 python -m pytest tests/unit -q -p no:cacheprovider` (whole suite, no caps, so `test_transition` runs after the other modules) | 2000 passed, 17 skipped, 1 deselected, 1 failed + 11 errors (missing data-bundle files, the known baseline), 19.2 s. No hang. |
| 7 | Run 1 with `-o faulthandler_timeout=60` | 7 passed. The option is accepted by this pytest. |

Facts that narrow it down (not a diagnosis): the hanging module tests the DEL-2 retention models,
not the state engine. It is the only state-graph-adjacent test that fits
`HistGradientBoostingRegressor` (OpenMP through scikit-learn's `libgomp`) and runs grouped bootstraps
on numpy. The thread-cap workaround that unblocks it on the Mac fits an OpenMP / BLAS threading
interaction in that environment. That is a **hypothesis only**, not demonstrated here, because the
Mac anaconda environment (its BLAS / OpenMP runtimes and their versions) is not available.

Suggested diagnostic for Kush on the Mac (no code change; it records evidence):
`timeout 300 /opt/anaconda3/bin/python -m pytest tests/unit/test_transition.py -q -p no:cacheprovider -o faulthandler_timeout=60`
without caps. If it hangs, pytest dumps every thread's stack after 60 s. Also save the output of
`python -c "import sklearn, threadpoolctl, json; from sklearn.ensemble import HistGradientBoostingRegressor; print(json.dumps(threadpoolctl.threadpool_info(), indent=1))"`,
and narrow the run with `-k test_baselines_run_and_beat_persistence_on_toy`. Until then the
thread caps stay as the documented workaround (STATUS), and 18f stays OPEN.

## 4. S156 contract draft (part B)

All modules are new and their headers say DRAFT_PENDING_16c. None imports pandas or numpy.

| Module | Lines | Content |
|---|---|---|
| `state_graph/event_log.py` | 411 | Strict `canonical_json` and `sha256_canonical`. `EngineEvent`, `Allocation` and `QuantityTerm` use the Step 16 draft vocabularies. A quantity term needs a QNT `ref` and exact bounds in g, mL or count. `EventLog` is append-only and hash-chained: a revision n+1 is appended and never rewrites, and `effective()` gives the latest revision of each event. JSONL writers refuse `ledgers/`, `data/`, `exports/`, `annotation/gold/`, any ledger file name and any overwrite. `extend_log_jsonl` appends only when the file is a byte prefix of the log. |
| `state_graph/replay.py` | 601 | `replay_events` / `replay_log` give a `ReplayResult` with one `Transaction` per event, a `Snapshot` (append-only entity versions using the ENTITY lifecycle enum), snapshot and config hashes and byte-identical JSONL. Hard invariants with codes. Exact correlated `Quantity` algebra. `EXPLICIT_ONLY` scope. Final lot consistency. `write_replay_jsonl`. |
| `state_graph/event_adapter.py` | 218 | `adapt_event_graph(source, graph, groundings=…, recomputers=…)` maps an S155 `EventGraph` to engine events, with INTRO events for producer-less lots. It runs the existing auditor first and excludes invented values. It copies codes and ids only, never raw text. Structural gaps become adapter issues. |

Tests: `test_step18_event_log.py` 59, `test_step18_replay.py` 43, `test_step18_adapter.py` 17,
119 in total including hypothesis properties. Each test file was committed RED before its module.
The properties cover byte-identical double replay with no false issues on valid generated sequences,
shuffled order giving `ORDER_REGRESSION`, reuse of any discarded entity being REJECTED, prefix replay
being a prefix of the full replay, and appends never changing earlier log bytes.

Full unit suite with thread caps: **2119 passed**, 17 skipped, 1 deselected. The 1 failed + 11 errors
are the same missing data-bundle files as the 2000-pass baseline. Nothing new fails.

## 5. Open for humans (H4 / 16c and Step 18 owners)

1. **Shapes.** Do the engine event, snapshot and transaction shapes map onto the 16c
   EVT / ENTITY / STATE / ALLOC / REF / GRAPH v1 schemas? 18a persistence is not done.
2. **Quantity policy.** Transforms and merges propagate no amount (this differs from L4). Should a
   pure combine conserve mass, and which processes do? Interval fractions are not propagated.
3. **Basis.** Rung A always emits basis `UNSPECIFIED`, so no Rung A split or reserve quantity is ever
   derived and those fraction sums are UNKNOWN. Who assigns the basis, and from what evidence?
4. **REMAINDER without a fraction** is treated as "the rest" (= parent − known siblings). V4 instead
   reports it as `FRACTION_UNKNOWN`. Choose one reading for both.
5. **COUNT amounts** are not mapped until count-unit identity (item / package / regional) is decided.
   Event-level amounts (Rung A `amount_g_k`) are not bound to an entity.
6. **Rejection policy.** An event with any issue is rejected whole, and later events then cascade
   (`ENTITY_UNKNOWN`). Equal order keys are allowed; only a regression is an issue. Text order versus
   execution order is the caller's choice, as in V4.
7. **Negative fractions and quantities** are refused (QuantityTerm) or undecided
   (`NEGATIVE_FRACTION_RULE_OPEN`). The rule is OPEN.
8. **Lot statuses** OPTIONAL / ALTERNATIVE / GARNISH / UNRESOLVED are not checked against the replay.
9. **Legacy engine L1–L8.** Fix `engine.py` / `symqty.py` / `prefix_state.py`, or migrate callers to the
   new replay. Not changed here.
10. **Not implemented:** observation override (method 6), `transition_tuples_v1` / `prefix_packets_v1`
    (18e), invalidation graph (method 8), session layer (18g, deferred by the card).
11. **18f hang:** run the Mac diagnostic in §3 and record the stacks.
12. **G18.1–G18.5 not evaluated.** There are no adjudicated Gold events. Human adjudication of
    invariant violations is the card's human gate.
