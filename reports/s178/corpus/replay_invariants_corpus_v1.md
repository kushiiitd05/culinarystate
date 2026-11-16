# Replay-invariant property tests at corpus scale (S178, T3-C12-R1)

Status: AI_DRAFTED / PROPOSED. Counts only; no text, id or value. Engineering check, not a gold score. Tool `s178-corpus-replay-invariants-0.1.0-draft`; Rung A `STEP17B_RUNG_A_RULES_V1_DRAFT`, lexicon `9678937f6a9a0ff6`, adapter `step18-extraction-adapter-0.1.0-draft`, engine `step18-replay-0.1.0-draft`.
Sample: full families. Pipeline per text: Rung A -> adapter -> engine replay (which rejects an event violating an invariant) + an independent re-implementation of the seven invariants, compared event by event.

## Violations per invariant (events), engine vs independent checker

| invariant | FOODCOM engine / independent / disagree | GUTENBERG_SEGMENT engine / independent / disagree | WIKIBOOKS engine / independent / disagree |
|---|---:|---:|---:|
| ORDER_REGRESSION | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| ENTITY_UNKNOWN | 79,206 / 79,206 / 0 | 4,957 / 4,957 / 0 | 779 / 779 / 0 |
| ENTITY_ALREADY_CONSUMED | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| ENTITY_REUSED_AFTER_DISCARD | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| ENTITY_ID_REUSED | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| EVENT_ID_REUSED | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| SPLIT_FRACTIONS_EXCEED_ONE | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

## Per family

| family | texts | with events | Rung A graph events | engine events (incl. lot intros) | replay PASS | UNKNOWN | FAIL | unexplained (untraced + disagreements) | determinism identical |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| FOODCOM | 522,517 | 522,390 | 8,214,960 | 12,543,466 | 455,613 | 55,180 | 11,721 | **0** | 10416/10416 |
| GUTENBERG_SEGMENT | 73,778 | 73,777 | 934,494 | 1,563,210 | 66,392 | 6,431 | 955 | **0** | 1550/1550 |
| WIKIBOOKS | 3,676 | 3,674 | 59,357 | 90,224 | 3,123 | 455 | 98 | **0** | 80/80 |

### FOODCOM

- Transactions: {'APPLIED': 12464260, 'REJECTED': 79206}.
- All engine issue codes (events): {'DEPENDENCY_NOT_APPLIED': 67627, 'ENTITY_UNKNOWN': 80142}.
- Traced causes of every engine issue: {'DEPENDENCY_NOT_APPLIED__CASCADE_DEPENDENCY_REJECTED': 67627, 'ENTITY_UNKNOWN__ADAPTER_ENTITY_WITHOUT_PRODUCER': 11864, 'ENTITY_UNKNOWN__CASCADE_PRODUCER_REJECTED': 68278}; untraced: 0; engine-vs-independent disagreements: 0.
- Engine unknown codes: {'FRACTION_BASIS_UNSPECIFIED': 79220, 'MASS_BALANCE_UNKNOWN': 77778}.
- Adapter issue codes: {'ENTITY_WITHOUT_PRODUCER': 11874}; adapter unknown codes: {'EVENT_QUANTITY_NOT_BOUND_TO_ENTITY': 18529}.
- Lot-accounting issues (final): {'LOT_STATUS_CONTRADICTS_REPLAY': 22687}; invented values excluded by the adapter: 0.
- Final entity lifecycles: {'ACTIVE': 1834586, 'DISCARDED': 20646, 'INCORPORATED': 10343530, 'RESERVED': 25039}. Exceptions: none.
- Split-sum invariant coverage (what it had to check): {'partition_groups': 79220, 'partition_groups_basis_unspecified': 79220, 'partition_groups_with_two_or_more_allocations': 7543, 'partition_groups_with_any_known_fraction': 664, 'partition_groups_checkable_basis_and_fraction': 0}.
- Power check (planted violations on the sampled texts):

| mutation | expected code | applicable | engine detected | independent detected | both | same violating events |
|---|---|---:|---:|---:|---:|---:|
| M_ORDER_SWAP | ORDER_REGRESSION | 26,120 | 26,120 (100.0 %) | 26,120 (100.0 %) | 26,120 | 26,120 |
| M_DOUBLE_CONSUME | ENTITY_ALREADY_CONSUMED | 25,133 | 25,133 (100.0 %) | 25,133 (100.0 %) | 25,133 | 25,133 |
| M_RESURRECT_DISCARDED | ENTITY_REUSED_AFTER_DISCARD | 896 | 896 (100.0 %) | 896 (100.0 %) | 896 | 896 |
| M_SPLIT_OVER_ONE | SPLIT_FRACTIONS_EXCEED_ONE | 365 | 365 (100.0 %) | 365 (100.0 %) | 365 | 365 |

### GUTENBERG_SEGMENT

- Transactions: {'APPLIED': 1558253, 'REJECTED': 4957}.
- All engine issue codes (events): {'DEPENDENCY_NOT_APPLIED': 4088, 'ENTITY_UNKNOWN': 5167}.
- Traced causes of every engine issue: {'DEPENDENCY_NOT_APPLIED__CASCADE_DEPENDENCY_REJECTED': 4088, 'ENTITY_UNKNOWN__ADAPTER_ENTITY_WITHOUT_PRODUCER': 956, 'ENTITY_UNKNOWN__CASCADE_PRODUCER_REJECTED': 4211}; untraced: 0; engine-vs-independent disagreements: 0.
- Engine unknown codes: {'FRACTION_BASIS_UNSPECIFIED': 8952, 'MASS_BALANCE_UNKNOWN': 8874}.
- Adapter issue codes: {'ENTITY_WITHOUT_PRODUCER': 956}; adapter unknown codes: {'EVENT_QUANTITY_NOT_BOUND_TO_ENTITY': 6325}.
- Lot-accounting issues (final): {'LOT_STATUS_CONTRADICTS_REPLAY': 2642}; invented values excluded by the adapter: 0.
- Final entity lifecycles: {'ACTIVE': 426651, 'DISCARDED': 153, 'INCORPORATED': 1167098, 'RESERVED': 4503}. Exceptions: none.
- Split-sum invariant coverage (what it had to check): {'partition_groups': 8952, 'partition_groups_basis_unspecified': 8952, 'partition_groups_with_two_or_more_allocations': 573, 'partition_groups_with_any_known_fraction': 126, 'partition_groups_checkable_basis_and_fraction': 0}.
- Power check (planted violations on the sampled texts):

| mutation | expected code | applicable | engine detected | independent detected | both | same violating events |
|---|---|---:|---:|---:|---:|---:|
| M_ORDER_SWAP | ORDER_REGRESSION | 3,645 | 3,645 (100.0 %) | 3,645 (100.0 %) | 3,645 | 3,645 |
| M_DOUBLE_CONSUME | ENTITY_ALREADY_CONSUMED | 3,548 | 3,548 (100.0 %) | 3,548 (100.0 %) | 3,548 | 3,548 |
| M_RESURRECT_DISCARDED | ENTITY_REUSED_AFTER_DISCARD | 4 | 4 (100.0 %) | 4 (100.0 %) | 4 | 4 |
| M_SPLIT_OVER_ONE | SPLIT_FRACTIONS_EXCEED_ONE | 23 | 23 (100.0 %) | 23 (100.0 %) | 23 | 23 |

### WIKIBOOKS

- Transactions: {'APPLIED': 89445, 'REJECTED': 779}.
- All engine issue codes (events): {'DEPENDENCY_NOT_APPLIED': 683, 'ENTITY_UNKNOWN': 785}.
- Traced causes of every engine issue: {'DEPENDENCY_NOT_APPLIED__CASCADE_DEPENDENCY_REJECTED': 683, 'ENTITY_UNKNOWN__ADAPTER_ENTITY_WITHOUT_PRODUCER': 99, 'ENTITY_UNKNOWN__CASCADE_PRODUCER_REJECTED': 686}; untraced: 0; engine-vs-independent disagreements: 0.
- Engine unknown codes: {'FRACTION_BASIS_UNSPECIFIED': 645, 'MASS_BALANCE_UNKNOWN': 631}.
- Adapter issue codes: {'ENTITY_WITHOUT_PRODUCER': 99}; adapter unknown codes: {'EVENT_QUANTITY_NOT_BOUND_TO_ENTITY': 140}.
- Lot-accounting issues (final): {'LOT_STATUS_CONTRADICTS_REPLAY': 213}; invented values excluded by the adapter: 0.
- Final entity lifecycles: {'ACTIVE': 13176, 'DISCARDED': 161, 'INCORPORATED': 75940, 'RESERVED': 194}. Exceptions: none.
- Split-sum invariant coverage (what it had to check): {'partition_groups': 645, 'partition_groups_basis_unspecified': 645, 'partition_groups_with_two_or_more_allocations': 62, 'partition_groups_with_any_known_fraction': 4, 'partition_groups_checkable_basis_and_fraction': 0}.
- Power check (planted violations on the sampled texts):

| mutation | expected code | applicable | engine detected | independent detected | both | same violating events |
|---|---|---:|---:|---:|---:|---:|
| M_ORDER_SWAP | ORDER_REGRESSION | 180 | 180 (100.0 %) | 180 (100.0 %) | 180 | 180 |
| M_DOUBLE_CONSUME | ENTITY_ALREADY_CONSUMED | 173 | 173 (100.0 %) | 173 (100.0 %) | 173 | 173 |
| M_RESURRECT_DISCARDED | ENTITY_REUSED_AFTER_DISCARD | 2 | 2 (100.0 %) | 2 (100.0 %) | 2 | 2 |
| M_SPLIT_OVER_ONE | SPLIT_FRACTIONS_EXCEED_ONE | 2 | 2 (100.0 %) | 2 (100.0 %) | 2 | 2 |

## Reading and limits

- A violation is a structural breach (order, consumption, resurrection, id reuse, split sum). Zero says the rule-based extraction respects the replay's structural invariants; it does not say the events are right.
- The independent checker shares the engine's SEMANTICS (what counts as a violation) but not its code; it is conditioned on the engine's apply/reject decisions because the state before an event depends on them.
- Not checked by the replay at all: SPAN_ROUNDTRIP_SEE_V1, LOT_ACCOUNTING_COMPLETENESS_SEE_V4, INVENTED_VALUES_SEE_ADAPTER_AUDIT, MERGE_AND_TRANSFORM_QUANTITIES_NOT_PROPAGATED, OBSERVATION_OVERRIDE_NOT_IMPLEMENTED, TRANSITION_TUPLES_AND_PREFIX_PACKETS_NOT_IMPLEMENTED.
- TASTEset has no instruction text; BBC is not on this server (D-003).
