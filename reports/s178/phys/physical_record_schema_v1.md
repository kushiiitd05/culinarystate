# Physical record schema v1 (S178 PHYS2, T4-C02-R2)

Status: DRAFT / AI_DRAFTED (PROPOSED). Code: `src/culinarystate/simulation/physical_record_schema.py` (the validator and the constants
below), `tools/s178_phys_schema_validate.py` (counts-only report over a records directory), tests
`tests/unit/test_s178_phys2_schema.py`. Records are data-plane files (`data/derived/`, git-ignored); only counts are committed.

## 1. The field tuple

Every field of a physical-layer record is the SSOT tuple (value, unit, type, mask, provenance), stored flat. The unit is fixed by
the axis (heat inputs: `recipe_adapter.INPUT_SPECS`; deg C, minutes, fractions elsewhere); the type is the layer and the status
code; the mask is `status == UNKNOWN`; the provenance is the keys below.

### Layer 1 (TEXT_STATED, D-077): one entry per axis of `inputs`

| key | meaning |
|---|---|
| `value` | the stated or defined value (Fractions as strings; a range is a two-element list); `null` when UNKNOWN |
| `status` | `MEASURED`, `RANGE`, `BOUND_UPPER`, `BOUND_LOWER`, `QUALITATIVE`, `UNKNOWN` (= mask 0) |
| `basis` | how the value was fixed: `TEXT_STATED`, `CARRIED_SETPOINT`, `PHYSICAL_DEFINITION`, `PROCESS_DEFINITION`, `CUE`, `CUT_HISTORY`, `FOOD_GROUP`, and for the non-heat layer `TEXT_CUE`, `LINEAGE`, `ORDER_ADJACENT`, `LINEAGE_AND_STATED_DURATIONS`; `null` only when UNKNOWN |
| `span` | characters `[a, b)` of the joined step text, or `null` |
| `span_id` | evidence locator of a bound axis: `C:a-b` characters, `E:<event>` the event verb (a definition), `L:<event>` the lots the event consumes (food group) |
| `row` | the registry row or code rule that fixed the value: `process_medium_map_v1:<PROC>`, `RUNG_A:duration_min`, `CB_RULE:<rule>`, `ING_LEDGER:category`, `nonheat_binding:<...>` |
| `reason` | UNKNOWN only: why nothing is bound (`NO_DURATION_STATED`, `NO_TEMPERATURE_STATED`, `GAS_MARK_CODE_ONLY`, `MULTIPLE_FOOD_GROUPS`, ...) |

Heat axes (`condition_binding` 0.2.0): `duration`, `temperature_profile`, `medium`, `lid_state`, `start_mode`, `piece_size_class`,
`water_ratio`, `matrix_class`; conditional axes `matrix_groups` (food groups of all lot members), `ambient_temperature` (an oven,
grill or heat-level temperature stated for an aqueous step: kept, never used as the liquid temperature). Non-heat axes per family:
`nonheat_binding.INPUTS`. The `endpoint` block of a heat record (stopping criterion, QUALITATIVE, with spans) is NOT an axis and
never part of `inputs` (see section 3). `temperature_note` lists the events whose temperature differs from the 0.1.0 rule.

### Layer 2 (SCENARIO): per bracket record

- Every INPUT field (`bath_c`, `duration_min`, `initial_c`, `h`, `half_thickness_m`, `t_cap_c` for heat; the family inputs for non-heat) has an
  entry in `bases`: `L1:<basis>` taken from Layer 1; `SD-n` scenario default; `KGE-n` corpus duration quantile; `NH-n` non-heat
  default; `PC-n` phase-change row; `|` and `+` join a stated bound or stated liquid temperature with the row it overrides.
  `k` and `alpha` have a basis too (`SD-n`).
- Every OUTPUT field is MODEL_DERIVED (record `labels` = SCENARIO, MODEL_DERIVED, NON_CITABLE, ASSUMED_DEFAULT) and derives from named
  inputs (`HEAT_DERIVED_FROM`: for example `core_end_c` from `bath_c`, `duration_min`, `initial_c`, `h`, `half_thickness_m`, `k`, `alpha`).
- The record carries `l1_provenance`: `{axis: {basis, span_id, row}}` of the Layer 1 axes the run read, also when the status is
  SCENARIO_UNKNOWN or UNSUPPORTED_MEDIUM.

## 2. What the validator checks (100 % rules)

| rule | problem code when broken |
|---|---|
| every bound L1 axis has a `basis` from the vocabulary | `L1_BASIS_MISSING_OR_UNKNOWN_CODE` |
| every bound L1 axis has a `span_id` (`C:`, `E:` or `L:`), equal to `C:a-b` when `span` is set | `L1_SPAN_ID_MISSING_OR_INCONSISTENT` |
| every bound L1 axis has a `row` | `L1_ROW_MISSING` |
| every UNKNOWN L1 axis has null value, null basis and a `reason` | `L1_UNKNOWN_NEEDS_NULL_VALUE_NULL_BASIS_AND_REASON` |
| no endpoint field among the L1 `inputs`; every heat record has the `endpoint` block with valid cue classes and spans | `ENDPOINT_FIELD_IN_INPUTS`, `ENDPOINT_BLOCK_MISSING`, `ENDPOINT_CUE_BAD_CLASS_OR_SPAN` |
| every L2 input field has an entry in `bases`; every entry is a valid code | `L2_INPUT_FIELD_WITHOUT_BASIS`, `L2_BASIS_CODE_INVALID` |
| every L2 heat output field traces to input bases present in `bases` | `L2_OUTPUT_NOT_TRACEABLE_TO_INPUT_BASES` |
| no undeclared L2 field | `L2_UNDECLARED_FIELD` |
| the record has the four labels and `l1_provenance`; an `L1:` base has a Layer 1 span id | `L2_LABELS_MISSING`, `L2_L1_PROVENANCE_MISSING`, `L2_L1_INPUT_WITHOUT_L1_SPAN_ID` |

The validator reads records only and holds no scientific value. UNKNOWN is a valid, fully provenanced state (null value, reason); it is
never 0 and never imputed. Results on the S178 v04 records are in `reports/s178/phys/schema_validation_*_S178.json`.

## 3. Endpoint leakage (T4-C03, SSOT 199.8)

"until golden", "until tender", "until reduced by half" are observed endpoint information. They are stored in the `endpoint` block of
a heat record (`stopping_criterion` QUALITATIVE with its span and row, plus every cue; classes in `registry/endpoint_cue_lexicon_v1.csv`),
and a temperature that follows a food-probe cue ("until a thermometer reads 165 F") is a TARGET of the food stored there, not a medium
temperature. `endpoint_cues.physical_feature_row` flattens only `inputs` (and the L2 scenario inputs): a test asserts that two texts that
differ only in the endpoint phrase give identical feature rows and that `assert_no_endpoint_fields` rejects any endpoint column.

## 4. Not covered

Units are fixed per axis rather than stored per record. Strings such as `span_id` are locators, not text: no recipe text is stored
in any record. The schema does not validate the physical plausibility of a value.
