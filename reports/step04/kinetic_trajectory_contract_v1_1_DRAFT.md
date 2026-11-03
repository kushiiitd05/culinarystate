# Step 04.3 — Kinetic / trajectory contract v1.1 (KIN, KINPT): changes against v1

**Status: DRAFT_PENDING_H4.** Written 2026-11-03 in session S158 by the AI worker "ksh" (an agent, not Kush). This is an AI draft (D-045 W1). Kush and Parv review it, and the chemistry expert where asked. Nothing is approved, frozen, signed, minted or written to a ledger. D-029 approved 04.1, 04.2-min, 04.6-min and 04.9-min. It explicitly did **not** cover 04.3, so this contract still needs its own H4 approval before Step 09 freezes any KIN/KINPT schema and before Steps 10 and 11 (Plan v2 Step 04 card, pass gate (6)).

**Base, unchanged:** `reports/step04/kinetic_trajectory_contract_v1.md` (r1, 2026-10-26), `registry/schemas/KIN.draft_v1.schema.json`, `registry/schemas/KINPT.draft_v1.schema.json`. v1 still holds every rule, field table, crosswalk and open item. This file lists only what v1.1 changes and what the new validator enforces. Where it says nothing, v1 applies.

**New files (S158):**

| Path | What |
|---|---|
| `registry/schemas/KIN.draft_v1_1.schema.json` | KIN v1.1 draft, `schema_version 1.1.0-draft` |
| `registry/schemas/KINPT.draft_v1_1.schema.json` | KINPT v1.1 draft |
| `src/culinarystate/lineage/kinetic_contract.py` | pure cross-record validator: reads records, returns issues and verdicts, writes nothing |
| `tests/fixtures/kinetic_v1_1_fixtures.py` | SYNTHETIC SCHEMA FIXTURES: placeholder strings, dummy numbers, unit `u` |
| `tests/unit/test_step04_3_kinetic_v1_1_schema.py` | record-level tests: structure, v1 to v1.1 diff, 22 accepted variants, 31 negative controls |
| `tests/unit/test_step04_3_kinetic_contract.py` | cross-record tests of the validator (50 tests) |

The tests were written first and committed while they still failed (RED), before the schemas and the module existed.

## 1. Changes against v1 (complete list)

A test checks that the v1.1 JSON differs from v1 **only** at the paths below (`test_v1_1_differs_from_v1_only_at_the_declared_paths`). Every change adds structure. None adds a scientific value. The only numbers in the new rules are the constant 0 (seconds of a definitional zero) and list sizes.

### KIN

| # | Path | Change | Why |
|---|---|---|---|
| KC-1 | `$id`, `title`, `description`, `$comment` | v1.1 id and title. The description now reads `schema_version 1.1.0-draft. STATUS DRAFT_PENDING_H4`. The comment points to this file and the validator, and says the thresholds are referenced, not signed. | versioned file next to v1; never edit v1 in place |
| KC-2 | `properties.digitisation_summary` (new, required) | `{any_digitised YES/NO/UNKNOWN, two_read_status NOT_APPLICABLE / ALL_DIGITISED_POINTS_TWO_INDEPENDENT_READS / SOME_DIGITISED_POINTS_FEWER_READS / NOT_ASSESSED, rule_ref const "THR-04K-03"}`. NO forces NOT_APPLICABLE. YES and UNKNOWN forbid NOT_APPLICABLE. UNKNOWN forces NOT_ASSESSED. | R04-7 and THR-04K-03 (two independent reads for TEST / SIM-VAL) existed only as prose on `OBS.digitization`. Without a series-level field, a reader cannot tell a digitised series from its header. The pattern is the same as `censoring_summary`: a summary whose agreement with the points is checked by the validator. The field never makes a series eligible on its own. |
| KC-3 | `allOf` (one new root rule) | `series_origin_form` FIGURE_DIGITIZED or MIXED_TABLE_AND_FIGURE requires `digitisation_summary.any_digitised = YES` | v1 let a figure series claim "not digitised" |
| KC-4 | `$defs.analyte_form`: `required`, `properties.token`, `properties.token_status`, `allOf`, `description` | New keys `token` (pattern `^[A-Z][A-Z0-9_]{1,63}$`, never `UNKNOWN`, or null) and `token_status` (NO_APPROVED_REGISTRY / REGISTRY_TOKEN / NOT_APPLICABLE). A STATED form takes NO_APPROVED_REGISTRY or REGISTRY_TOKEN. NOT_REPORTED and UNKNOWN take NOT_APPLICABLE. The token is non-null only for REGISTRY_TOKEN. | Round-3 Review B 21-12 / D21-22: the analyte basis (for example a reduced form against reduced plus oxidised forms) must be machine-comparable for the Step-10 ranking confounder and the Step-27 basis checks. **No token list is defined.** No registry is approved, so every real record today is `NO_APPROVED_REGISTRY` with a null token. The list is expert question EQ21-06. MECH v1.1 carries the same slot, so the KIN and MECH conventions stay identical. |
| KC-5 | `properties.censoring_summary.allOf`, `.description` | `any_censored = YES` must list at least one **censoring** kind: ND, LT_LOD, LT_LOQ, GT_ULOQ, GT_CAP, GT_STATED, LT_STATED, CENSORED_UNKNOWN, ROUNDED_INTERVAL, RANGE_ONLY or TRACE_BETWEEN_LOD_LOQ | v1 accepted YES with only DETECTED or TRUE_ZERO, which are uncensored kinds (CS-001, CS-010 in 04.2-min) |
| KC-6 | `required` | `digitisation_summary` added | KC-2 |

### KINPT

| # | Path | Change | Why |
|---|---|---|---|
| PC-1 | `$id`, `title`, `description`, `$comment` | as KC-1 | versioned file |
| PC-2 | `properties.digitized`: `required`, `properties.read_independence`, `allOf`, `description` | New required `read_independence`: INDEPENDENT_READERS / SAME_READER_REPEATED / SINGLE_READ / NOT_REPORTED / NOT_APPLICABLE / UNKNOWN. Status NO forces NOT_APPLICABLE, UNKNOWN forces UNKNOWN, and YES forbids NOT_APPLICABLE. | THR-04K-03 asks for **independent** reads. OBS holds the read count (`n_reads`) and the inter-read SD (`read_sd`) but nothing about independence. Whether a same-reader repeat counts as independent is an H4 question (§4 H-1): it is recorded and never upgraded. |
| PC-3 | `allOf` (one new root rule) | `tau.derivation = DIGITIZED` requires `digitized.status = YES` | v1's mirror rule ran one way only. A digitised tau on a point flagged NO validated. |
| PC-4 | `properties.tau.allOf` | `NOT_APPLICABLE_REFERENCE` forbids conversion to seconds (NOT_CONVERTED / NOT_CONVERTIBLE / UNKNOWN only) | v1 let a reference with no defined tau carry a seconds value, which amounts to a fabricated time |
| PC-5 | `properties.tau.allOf` | a `RANGE` tau is never converted to one seconds value | `normalised_seconds` holds one number, so converting "10–12 min" means inventing a midpoint (law: no invented values). The interval stays in `low` / `high`. |
| PC-6 | `properties.tau.allOf` | a `DEFINITIONAL_ZERO` that is CONVERTED_EXACT has value 0 | consistency: the definition fixes the value |

Not changed: every v1 field, enum value and rule, the mint keys, the K-level vocabulary, the fit record, lineage and lab-group keys (UNKNOWN stays valid), raw time units (week / month / year / OTHER), and the clock rule (PROCESS_TAU only until 03.3).

## 2. Validator `culinarystate.lineage.kinetic_contract`

The validator is pure: no file writes, no ledger reads, no network. It loads only the two v1.1 schema files. Everything it returns is an AI-side engineering check, not human verification.

| Function | Returns | Rules |
|---|---|---|
| `schema_errors(record, "KIN" \| "KINPT")` | sorted error strings | v1.1 schema; the relative `$id` is stripped, as in the Step 04 README |
| `validate_series(kin, kinpts, obs_by_id, *, companions=None, analyte_form_tokens=None)` | `list[Issue(code, severity, record_id, detail)]` | all checks below |
| `validate_series_set(kins)` | issues | `LAB_GROUP_NESTING_VIOLATED` (split group ⊆ one lab group, L-10); `GRID_FIT_INPUTS_INCOMPLETE` (grid-level fit names every grid member, R04-16, K-16) |
| `distinct_numeric_tau(kinpts)` | int | numeric times only; a range or a reference without tau is not one |
| `two_read_status(kinpts, obs_by_id)` | the KC-2 vocabulary | from `OBS.digitization.n_reads` and `KINPT.digitized.read_independence` |
| `split_eligibility(kin, kinpts, obs_by_id)` | `Eligibility(verdict, reasons, rule_refs)` | TEST / SIM-VAL under draft rules |
| `arrhenius_eligibility(kin)` | `Eligibility` | R04-15 |
| `fitting_selection(kin, kinpts, obs_by_id)` | `FittingSelection(included, excluded{id: reason}, censored)` | R04-2, R04-5, R04-9, R04-13 |
| `series_storage_required(n)` | bool | R04-1 under THR-04K-01 (draft value 2) |
| `DRAFT_THRESHOLDS` | `ThresholdRef` for THR-04K-01..04, status DRAFT_PENDING_H4 | a test fails if the registry row status changes or a `signed_by` appears, so a signature cannot slip in silently |

**Issue codes (ERROR unless marked WARN).**

| Area | Codes | Contract rule |
|---|---|---|
| Times, raw units | `N_TIMEPOINTS_MISMATCH`, `TAU_CLOCK_MISMATCH`, `TAU_UNIT_DIFFERS_FROM_TIME_BASE` (WARN), `SECONDS_CONVERSION_MISMATCH` (KINPT and temperature-profile points: exact seconds must equal raw value × s/min/h/d/week factor), `TAU_RANGE_INVERTED`, `KIN_ID_MISMATCH`, `KINPT_MINT_KEY_DUPLICATE` | R04-5, §2, §4 mint key |
| Temperature profiles | `PROFILE_CLOCK_MISMATCH`, `DUPLICATE_PROFILE_LOCATION` (WARN) | R04-5, R04-6 |
| OBS mirror | `OBS_MISSING`, `OBS_SERIES_LINK_MISMATCH`, `OBS_SHARED_BY_KINPTS` | §4 (1 KINPT ↔ 1 OBS), §5 |
| Digitisation | `DIGITIZED_FLAG_MISMATCH`, `ORIGIN_FORM_DIGITISATION_MISMATCH`, `DIGITISATION_SUMMARY_MISMATCH` | R04-7, KC-2 |
| C0 and value scale | `C0_VALUE_MISMATCH`, `C0_NOT_A_T0_POINT`, `C0_OBS_MISSING` (WARN), `RELATIVE_T0_NOT_DEFINITIONAL`, `DEFINITIONAL_NORMALISATION_MISPLACED`, `DEFINITIONAL_NORMALISATION_SCALE_UNSTATED` (WARN), `RELATIVE_SCALE_C0_UNKNOWN` (WARN: UNKNOWN is a valid answer, so this is not an error) | R04-13, §3 `initial_conditions` |
| Censoring | `CENSORING_SUMMARY_MISMATCH`: YES must list exactly the censoring kinds of the points; NO is wrong if any point is censored or has censoring NOT_REPORTED | R04-9 |
| Replicates | `UNIT_LABEL_REQUIRED` (repeated-measures design) | R04-10 |
| Companions (only when `companions` is supplied) | `COMPANION_MISSING` (WARN), `COMPANION_MASS_BALANCE_SET_MISMATCH`, `COMPANION_MASS_BALANCE_SET_ABSENT` (WARN), `COMPANION_POINT_UNPAIRED` (WARN): at the same tau and run, the two points share an SMP or name each other in `paired_kinpt_ids` | R04-14 |
| Analyte-form token | `ANALYTE_TOKEN_WITHOUT_APPROVED_REGISTRY`, `ANALYTE_TOKEN_NOT_IN_REGISTRY` | KC-4 |

**Eligibility verdicts.** There are three: `ELIGIBLE_UNDER_DRAFT_RULES`, `NOT_ELIGIBLE` and `UNKNOWN`. NOT_ELIGIBLE wins over UNKNOWN. Anything other than ELIGIBLE means "keep out of TEST / SIM-VAL". UNKNOWN never becomes eligible.

- **NOT_ELIGIBLE:** independence UNKNOWN (D-029 D-5); lab group UNKNOWN (contract §10); evidence tier E5 (FW-09); a digitised point with fewer than 2 reads, read count not reported, or SINGLE_READ.
- **UNKNOWN:** lineage or lab group PENDING; a same-reader repeat (H-1); read independence not reported; inter-read SD not stored.

The positive verdict is named "under draft rules" because THR-04K-03 is unsigned.

**Arrhenius eligibility (R04-15).** ELIGIBLE needs one of: a MEDIUM, CORE or SURFACE profile; PRODUCT_ISOTHERMAL_STATED; or come-up time EXCLUDED_FROM_TIME. UNKNOWN results when temperature status, isothermality or come-up is UNKNOWN, or when a profile is UNSPECIFIED (never promoted to a location). NOT_ELIGIBLE covers everything else, such as a setpoint only with the come-up included.

## 3. Conformance tests K-1..K-16 of v1 §12: where they now run

The following are covered by the new tests on synthetic fixtures: K-2 (figure-only series, two-read rule), K-5, K-6, K-7 (censored points stay censored; no substituted bound; summary consistent), K-9, K-10, K-11, K-12 (C0 / relative scale, excluded from fitting), K-13, K-14 (companions and pairing), K-15, K-16. Still needing Step 09 data paths or the export layer: K-1 (export round-trip and DRV parent check), K-3 (R04-1 endpoint-only rejection needs a source-structure assertion checked by the second extractor, THR-04K-04), K-4 (Step 24 PARAM) and K-8 (Step 09 promotion path).

## 4. Open for humans (H4; none decided here)

- **H-1** Do repeated reads by the same reader count as "independent" under THR-04K-03? Draft: recorded as `SAME_READER_REPEATED`; eligibility UNKNOWN.
- **H-2** Approve, change or reject THR-04K-01..04 (all DRAFT_PENDING_H4, PROPOSED_PILOT, unsigned). The module holds the draft values 2 and 2 as constants, and its tests fail if the registry rows change status.
- **H-3** Should a missing inter-read SD block TEST / SIM-VAL (draft: UNKNOWN) or be a hard NOT_ELIGIBLE?
- **H-4** Analyte-form token registry: content (expert question EQ21-06), file location and approval. Until then the token stays null.
- **H-5** KC-5 reads `kinds_present` as "censoring kinds present". If the humans intend it to also list uncensored kinds, the rule still holds, because YES needs at least one censoring kind.
- **H-6** All of v1 §14 (A-1..A-14) stays open as written there. That includes A-12 (absent context key = UNKNOWN versus the card's NOT_REPORTED) and the 03.3 clock vocabulary.
- **H-7** Approval of 04.3 (v1 + v1.1) as a whole. Step 09 must not freeze KIN/KINPT before it.
