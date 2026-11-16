# Typed Event IR — contract between producers and the state engine

**Status: FINAL for the 21 Nov submission.** Freeze step 2, 15 Nov 2026. Owner: Step 17a validator V4 (`VALIDATOR_ID = "V4_STEP18_INVARIANTS"`, module status `DRAFT_PENDING_16c`).

This document states the contract that already exists in code and names the one gap that was closed on 15 Nov. It creates **no second graph implementation** — `EventGraph` in `src/culinarystate/extraction/interfaces.py` is the only event graph, and everything below points at it.

## 1. Why this document exists

The Event IR was real but undocumented: its fields lived in `interfaces.py`, its controlled vocabularies in `validators.py`, its rule producers in `rung_a_binding.py` / `rung_a_rules.py`, and its invariants in `invariants.py`. Nothing said in one place what a producer must emit, or which invariant catches which error. A parser rule and an LLM proposal are held to the same contract, so that contract has to be writable down.

## 2. The IR

Every type is a frozen dataclass. Ids are local and never minted by a producer.

### `EventCandidate`

| Field | Type | Meaning |
|---|---|---|
| `event_id` | str | local id, non-blank |
| `order` | (int, int) | text order (step_index, ordinal) — **not** execution order |
| `span` | Span \| None | source grounding; round-trip checked by V1 |
| `consumes` | tuple[str, ...] | entity ids consumed |
| `produces` | tuple[str, ...] | entity ids produced |
| `discards` | tuple[str, ...] | entity ids discarded |
| `depends_on` | tuple[str, ...] | execution dependencies; must form a DAG |
| `attributes` | tuple[ValueClaim, ...] | typed, vocabulary-checked claims (see §3) |
| `claim_route` | str \| None | how the event was arrived at |
| `alternative_group` | str \| None | **added 15 Nov** — binds mutually exclusive events (CR-25) |
| `condition_profile_id` | str \| None | **added 15 Nov** — shared condition profile the event was read under (CR-25) |

Both new fields default to `None` and are never inferred. A non-`None` value must be non-blank. Adding them is backward compatible: 160 existing tests over the 17a/17b/18 surface pass unchanged.

### `EntityCandidate`

`entity_id`, `entity_type`, `lifecycle`, `parent_entity_ids`, `created_by_event_id`, `span`, `attributes`. This is CR-25/26 entity parentage and lifecycle, already in place.

### `AllocationCandidate`

`alloc_id`, `kind`, **`basis`**, `parent_entity_id`, `child_entity_id`, `event_id`, `fraction`. The CR-26 allocation basis is this `basis` field — it already existed and needed no change.

### `EventGraph`

`source_text_id`, `raw_sha256`, `events`, `entities`, `allocations`, `lot_accounting`, `provenance`, `failure`, `diagnostics`. `claims()` yields every `ValueClaim` qualified by its owner id.

## 3. Typed attributes, not free-form keys

`event_kind`, `modality`, `temporal_relation`, `transformation_mode`, `tool_role`, `entity_type` and `lifecycle` are emitted as `ValueClaim` attributes whose vocabulary is checked by validator V3 against registries under `registry/recipe_semantics/*_registry_v1_DRAFT.csv` (`VOCAB_FILES` / `CLAIM_FIELD_VOCAB` in `validators.py`). A value outside its registry is an issue, not a silent pass. Other categorical fields are explicitly **not** vocabulary-checked, and `validators.py` says so rather than implying coverage.

Each `ValueClaim` carries `field`, `kind`, `value` (which may be a `(low, high)` interval), `status`, `origin`, `claim_route`, `span`, `trace`, `unit`. `origin` / `status` / `claim_route` are the three orthogonal fields of **CR-02**, so the "every state value carries basis and provenance" invariant is a property of the type, not a check that can be forgotten.

## 4. Invariants, and the code that enforces each

The freeze names six invariants. Five were already enforced; one was not.

| Freeze invariant | Enforced by | Status |
|---|---|---|
| **lineage conservation** | V4: referenced ids exist; nothing consumed before produced; nothing consumed after DISCARD; every new intermediate has a producing event; split/merge parent-child consistency; split fractions sum ≤ 1 per compatible basis; every ingredient-list lot accounted for; `depends_on` forms a DAG | ✅ existing |
| **UNKNOWN ≠ zero** | V4 `check_mass_balance` — balance is checked only where every term is known, otherwise **UNKNOWN, not FAIL**. `ValueClaim.status` keeps UNKNOWN distinct from a known zero. CR-07 / CR-51 | ✅ existing |
| **no unsupported numeric values** | `auditor` (invented grams), reported by V4 as the open scope `INVENTED_GRAMS_SEE_AUDITOR`; CR-25/26 interval semantics — an interval is never collapsed to a fake gram value | ✅ existing, split across two modules |
| **alternatives are not conjunctions** | **`_alternatives` in `invariants.py`, new 15 Nov** → `ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION` | ✅ **closed 15 Nov** |
| **every state value carries basis / provenance** | `ValueClaim.origin` / `.status` / `.claim_route` (CR-02); State v2 P block, 100% corpus fill | ✅ existing |
| **evidence-context UNKNOWN ≠ MATCH** | `retrieval/compatibility.py`: `VALUE = {MATCH 1.0, NEAR 0.5, UNKNOWN 0.25, MISMATCH 0.0}` — UNKNOWN scores distinctly and is never read as MATCH; UNKNOWN on either side is also never a mismatch | ✅ existing |

### The alternatives invariant, precisely

At most one member of an `alternative_group` may **commit state**, where committing means a non-empty `consumes`, `produces` or `discards`. "A or B" is a labelled choice, not two facts.

- A member that declares the group but commits nothing is legal.
- Reported once per group, naming every committed member, with the group id as the issue path.
- V4 never repairs a graph, so a violation is reported and the graph is left alone.

Before 15 Nov this error was invisible to V4. Lineage vNext raised the parse-time diagnostic `VNEXT_ALTERNATIVE_SKIPPED` (48,520 recipes), which binds the first-named alternative only — a heuristic at parse time, not an invariant on the graph. The two are complementary: vNext decides what to bind, V4 now checks the binding was not a conjunction.

## 5. Still open — say this in the report, do not imply coverage

`OPEN_INVARIANTS` in `invariants.py` lists scopes V4 reports as **not checked** rather than silently passing:

| Open scope | Why | What would close it |
|---|---|---|
| `STATE_REPLAY_FROM_EVENT_HISTORY` | needs a replay check: that applying the event history reproduces `S_t`. State v2 now exists, so this is newly reachable, but it is **not** closed and must not be described as such | a replay harness over State v2 plus a gold or self-consistency criterion |
| `INFERRED_EVENTS_NOT_IN_EXPLICIT_ONLY_QUERIES` | query-layer property, not a graph property | query layer |
| `MASS_BALANCE_SCOPE` | which terms belong in a balance is caller-selected, unstated in the sources | H4 / 16c review |
| `INVENTED_GRAMS_SEE_AUDITOR` | enforced in `auditor`, outside V4 | wiring, or keep as a documented split |
| `SPAN_ROUNDTRIP_SEE_V1` | enforced in V1, outside V4 | wiring, or keep as a documented split |

Module status is `DRAFT_PENDING_16c`. Promoting V4 out of DRAFT needs a 16c decision with a `DECISIONS.md` entry; nothing here does that.

## 6. What this means for the LLM Layer-1 proposer (freeze step 6)

The contract is already sufficient for it, which is the point of formalizing it:

- a proposal is an `EventCandidate` / `EntityCandidate` / `AllocationCandidate`, nothing else;
- **source-span grounding is already mandatory** in the sense that V1 round-trips `Span.texts` against the raw bytes, so a proposal with an invented span fails;
- `claim_route` records that the value came from a model rather than a rule;
- categorical values must hit the existing registries, so a proposal cannot invent an `event_kind`;
- V4 decides acceptance. The proposer never writes state directly.

Per CR-30 / CR-32 the MODEL rung additionally requires an applicability PASS, all inputs observed and an in-domain check. Those are 36C gates, not IR properties.

## 7. Files

| Path | Role |
|---|---|
| `src/culinarystate/extraction/interfaces.py` | the IR types |
| `src/culinarystate/extraction/validators.py` | V1 span round-trip, V2 quantity records, V3 vocabulary |
| `src/culinarystate/extraction/invariants.py` | V4 Step-18 invariants, incl. `_alternatives` |
| `src/culinarystate/extraction/rung_a_binding.py`, `rung_a_rules.py` | rule producers |
| `registry/recipe_semantics/*_registry_v1_DRAFT.csv` | controlled vocabularies |
| `tests/unit/test_s180_event_ir_alternatives.py` | 12 tests for the new fields and invariant |
| `tests/unit/test_step17a_invariants.py`, `test_step17a_interfaces.py` | existing V4 / IR coverage |
