# Replay-invariant property tests at corpus scale (S178, T3-C12-R1)

Status: AI_DRAFTED / PROPOSED. Counts only; no text, id or value. Engineering check, not a gold score. Tool `s178-corpus-replay-invariants-0.2.0-draft`; Rung A `STEP17B_RUNG_A_RULES_V1_DRAFT`, lexicon `9678937f6a9a0ff6`, adapter `step18-extraction-adapter-0.1.0-draft`, engine `step18-replay-0.1.0-draft`.
Sample: 1000. Pipeline per text: Rung A -> adapter -> engine replay (which rejects an event violating an invariant) + an independent replay that re-derives the seven invariants, every other structural rejection rule and its own apply/reject vector (only MASS_BALANCE_FAIL positions come from the engine), compared event by event.

## Violations per invariant (events), engine vs independent checker

ORDER_REGRESSION and EVENT_ID_REUSED are marked BY CONSTRUCTION: Rung A and the adapter cannot produce them (ids `E{n}` and order keys in loop order, `extraction/rung_a_binding.py:211-226`; introductions first, `state_graph/event_adapter.py:180-213`). Their zeros are not validation.

| invariant | FOODCOM engine / independent / disagree | GUTENBERG_SEGMENT engine / independent / disagree | WIKIBOOKS engine / independent / disagree |
|---|---:|---:|---:|
| ORDER_REGRESSION (BY CONSTRUCTION) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| ENTITY_UNKNOWN | 196 / 196 / 0 | 88 / 88 / 0 | 313 / 313 / 0 |
| ENTITY_ALREADY_CONSUMED | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| ENTITY_REUSED_AFTER_DISCARD | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| ENTITY_ID_REUSED | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| EVENT_ID_REUSED (BY CONSTRUCTION) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| SPLIT_FRACTIONS_EXCEED_ONE | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

## Per family

| family | texts | with events | Rung A graph events | engine events (incl. lot intros) | replay PASS | UNKNOWN | FAIL | unexplained (untraced + disagreements) | apply-decision disagreements | determinism same worker | determinism other pool (hash seed differs) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| FOODCOM | 1,000 | 1,000 | 15,370 | 23,524 | 853 | 118 | 29 | **0** | 0 | 14/14 | 14/14 (True) |
| GUTENBERG_SEGMENT | 1,000 | 1,000 | 13,408 | 22,218 | 878 | 104 | 18 | **0** | 0 | 26/26 | 26/26 (True) |
| WIKIBOOKS | 1,000 | 999 | 15,681 | 23,905 | 861 | 108 | 31 | **0** | 0 | 29/29 | 29/29 (True) |

### FOODCOM

- Transactions: {'APPLIED': 23328, 'REJECTED': 196}.
- All engine issue codes (events): {'DEPENDENCY_NOT_APPLIED': 168, 'ENTITY_UNKNOWN': 226}.
- Traced causes of every engine issue: {'DEPENDENCY_NOT_APPLIED__CASCADE_DEPENDENCY_REJECTED': 168, 'ENTITY_UNKNOWN__ADAPTER_ENTITY_WITHOUT_PRODUCER': 29, 'ENTITY_UNKNOWN__CASCADE_PRODUCER_REJECTED': 197}; untraced: 0; engine-vs-independent disagreements: 0.
- Engine unknown codes: {'FRACTION_BASIS_UNSPECIFIED': 181, 'MASS_BALANCE_UNKNOWN': 173}.
- Adapter issue codes: {'ENTITY_WITHOUT_PRODUCER': 29}; adapter unknown codes: {'EVENT_QUANTITY_NOT_BOUND_TO_ENTITY': 35}.
- Lot-accounting issues (final): {'LOT_STATUS_CONTRADICTS_REPLAY': 60}; invented values excluded by the adapter: 0.
- Final entity lifecycles: {'ACTIVE': 3419, 'DISCARDED': 36, 'INCORPORATED': 19468, 'RESERVED': 49}. Exceptions: none.
- Split-sum invariant coverage (what it had to check): {'partition_groups': 181, 'partition_groups_basis_unspecified': 181, 'partition_groups_with_two_or_more_allocations': 22, 'partition_groups_with_any_known_fraction': 1, 'partition_groups_checkable_basis_and_fraction': 0}.
- Independent replay: {'apply_decision_disagreements': 0, 'issue_code_set_disagreements': 0, 'issue_codes_in_disagreement': {}, 'engine_rejected_events': 196, 'independent_rejected_events': 196, 'mass_balance_fail_events_taken_from_engine': 0}.
- Power check (planted violations on the sampled texts, at a hash-drawn position):

| mutation | expected code | applicable | engine detected | independent detected | independent at the planted position | same violating events | planted first / interior / last |
|---|---|---:|---:|---:|---:|---:|---|
| M_ORDER_SWAP | ORDER_REGRESSION | 48 | 48 (100.0 %) | 48 (100.0 %) | 48 | 48 | 0 / 45 / 3 |
| M_DOUBLE_CONSUME | ENTITY_ALREADY_CONSUMED | 48 | 48 (100.0 %) | 48 (100.0 %) | 48 | 48 | 0 / 32 / 16 |
| M_RESURRECT_DISCARDED | ENTITY_REUSED_AFTER_DISCARD | 1 | 1 (100.0 %) | 1 (100.0 %) | 1 | 1 | 0 / 1 / 0 |
| M_SPLIT_OVER_ONE | SPLIT_FRACTIONS_EXCEED_ONE | 1 | 1 (100.0 %) | 1 (100.0 %) | 1 | 1 | 0 / 1 / 0 |

### GUTENBERG_SEGMENT

- Transactions: {'APPLIED': 22130, 'REJECTED': 88}.
- All engine issue codes (events): {'DEPENDENCY_NOT_APPLIED': 70, 'ENTITY_UNKNOWN': 89}.
- Traced causes of every engine issue: {'DEPENDENCY_NOT_APPLIED__CASCADE_DEPENDENCY_REJECTED': 70, 'ENTITY_UNKNOWN__ADAPTER_ENTITY_WITHOUT_PRODUCER': 18, 'ENTITY_UNKNOWN__CASCADE_PRODUCER_REJECTED': 71}; untraced: 0; engine-vs-independent disagreements: 0.
- Engine unknown codes: {'FRACTION_BASIS_UNSPECIFIED': 137, 'MASS_BALANCE_UNKNOWN': 137}.
- Adapter issue codes: {'ENTITY_WITHOUT_PRODUCER': 18}; adapter unknown codes: {'EVENT_QUANTITY_NOT_BOUND_TO_ENTITY': 85}.
- Lot-accounting issues (final): {'LOT_STATUS_CONTRADICTS_REPLAY': 36}; invented values excluded by the adapter: 0.
- Final entity lifecycles: {'ACTIVE': 5898, 'INCORPORATED': 16707, 'RESERVED': 63}. Exceptions: none.
- Split-sum invariant coverage (what it had to check): {'partition_groups': 137, 'partition_groups_basis_unspecified': 137, 'partition_groups_with_two_or_more_allocations': 11, 'partition_groups_with_any_known_fraction': 0, 'partition_groups_checkable_basis_and_fraction': 0}.
- Independent replay: {'apply_decision_disagreements': 0, 'issue_code_set_disagreements': 0, 'issue_codes_in_disagreement': {}, 'engine_rejected_events': 88, 'independent_rejected_events': 88, 'mass_balance_fail_events_taken_from_engine': 0}.
- Power check (planted violations on the sampled texts, at a hash-drawn position):

| mutation | expected code | applicable | engine detected | independent detected | independent at the planted position | same violating events | planted first / interior / last |
|---|---|---:|---:|---:|---:|---:|---|
| M_ORDER_SWAP | ORDER_REGRESSION | 47 | 47 (100.0 %) | 47 (100.0 %) | 47 | 47 | 0 / 44 / 3 |
| M_DOUBLE_CONSUME | ENTITY_ALREADY_CONSUMED | 46 | 46 (100.0 %) | 46 (100.0 %) | 46 | 46 | 0 / 37 / 9 |
| M_RESURRECT_DISCARDED | ENTITY_REUSED_AFTER_DISCARD | 0 | 0 (None %) | 0 (None %) | 0 | 0 | 0 / 0 / 0 |
| M_SPLIT_OVER_ONE | SPLIT_FRACTIONS_EXCEED_ONE | 2 | 2 (100.0 %) | 2 (100.0 %) | 2 | 2 | 0 / 2 / 0 |

### WIKIBOOKS

- Transactions: {'APPLIED': 23592, 'REJECTED': 313}.
- All engine issue codes (events): {'DEPENDENCY_NOT_APPLIED': 282, 'ENTITY_UNKNOWN': 314}.
- Traced causes of every engine issue: {'DEPENDENCY_NOT_APPLIED__CASCADE_DEPENDENCY_REJECTED': 282, 'ENTITY_UNKNOWN__ADAPTER_ENTITY_WITHOUT_PRODUCER': 32, 'ENTITY_UNKNOWN__CASCADE_PRODUCER_REJECTED': 282}; untraced: 0; engine-vs-independent disagreements: 0.
- Engine unknown codes: {'FRACTION_BASIS_UNSPECIFIED': 150, 'MASS_BALANCE_UNKNOWN': 145}.
- Adapter issue codes: {'ENTITY_WITHOUT_PRODUCER': 32}; adapter unknown codes: {'EVENT_QUANTITY_NOT_BOUND_TO_ENTITY': 37}.
- Lot-accounting issues (final): {'LOT_STATUS_CONTRADICTS_REPLAY': 84}; invented values excluded by the adapter: 0.
- Final entity lifecycles: {'ACTIVE': 3575, 'DISCARDED': 40, 'INCORPORATED': 19847, 'RESERVED': 46}. Exceptions: none.
- Split-sum invariant coverage (what it had to check): {'partition_groups': 150, 'partition_groups_basis_unspecified': 150, 'partition_groups_with_two_or_more_allocations': 20, 'partition_groups_with_any_known_fraction': 0, 'partition_groups_checkable_basis_and_fraction': 0}.
- Independent replay: {'apply_decision_disagreements': 0, 'issue_code_set_disagreements': 0, 'issue_codes_in_disagreement': {}, 'engine_rejected_events': 313, 'independent_rejected_events': 313, 'mass_balance_fail_events_taken_from_engine': 0}.
- Power check (planted violations on the sampled texts, at a hash-drawn position):

| mutation | expected code | applicable | engine detected | independent detected | independent at the planted position | same violating events | planted first / interior / last |
|---|---|---:|---:|---:|---:|---:|---|
| M_ORDER_SWAP | ORDER_REGRESSION | 50 | 50 (100.0 %) | 50 (100.0 %) | 50 | 50 | 0 / 48 / 2 |
| M_DOUBLE_CONSUME | ENTITY_ALREADY_CONSUMED | 49 | 49 (100.0 %) | 49 (100.0 %) | 49 | 49 | 0 / 34 / 15 |
| M_RESURRECT_DISCARDED | ENTITY_REUSED_AFTER_DISCARD | 0 | 0 (None %) | 0 (None %) | 0 | 0 | 0 / 0 / 0 |
| M_SPLIT_OVER_ONE | SPLIT_FRACTIONS_EXCEED_ONE | 0 | 0 (None %) | 0 (None %) | 0 | 0 | 0 / 0 / 0 |

## Reading and limits

- A violation is a structural breach (order, consumption, resurrection, id reuse, split sum). Zero says the rule-based extraction respects the replay's structural invariants; it does not say the events are right.
- The independent replay shares the engine's SEMANTICS (what counts as a violation) but not its code or constants; it derives its own apply/reject vector. The only engine input is the MASS_BALANCE_FAIL positions (quantity arithmetic is not re-implemented).
- Determinism: same-worker double replay, and a second worker pool started with a different PYTHONHASHSEED over the same sample.
- Not checked by the replay at all: SPAN_ROUNDTRIP_SEE_V1, LOT_ACCOUNTING_COMPLETENESS_SEE_V4, INVENTED_VALUES_SEE_ADAPTER_AUDIT, MERGE_AND_TRANSFORM_QUANTITIES_NOT_PROPAGATED, OBSERVATION_OVERRIDE_NOT_IMPLEMENTED, TRANSITION_TUPLES_AND_PREFIX_PACKETS_NOT_IMPLEMENTED.
- TASTEset has no instruction text; BBC is not on this server (D-003).
