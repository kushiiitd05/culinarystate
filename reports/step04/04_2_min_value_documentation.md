# Step 04.2-min — minimal OBS value documentation

**Status: DRAFT_PENDING_H4.** Written 2026-10-26 (D-027 / Plan v2 §7: contract and documentation only). Nothing is approved, frozen or applied; the registry blocks below are draft content, **not** files under `registry/`.

**Revision r1 (2026-10-26, still DRAFT_PENDING_H4):** reviews A and B applied. Main changes: an unknown digitisation uncertainty is spelled UNKNOWN (status field + nullable number); a MEASURED 0 is admitted only with kind TRUE_ZERO; `basis_raw` is a required key; censor limits are strictly positive; TRACE_BETWEEN_LOD_LOQ added; dispersion gains n-basis, CV, pooled SE, LSD and scope; the retention definition is split with a basis and an evidence field; value origin VO-009 DEFINITIONAL_NORMALISATION; `series_link` and `measurement_dedup` on OBS; three measurement bases proposed.

What the Step 04 card defines for 04.2-min (implemented here, nothing more): *minimal OBS value documentation* — `dispersion_type`, `n_biological` / `n_technical` or NOT_REPORTED, `statistic`, `basis`, `retention_definition ∈ {TRUE, APPARENT, YIELD_ADJUSTED, TR_OR_AR_UNDISCLOSED, UNKNOWN}` (the card's list; this revision splits it, see §1 and decision 3), `method_indicator`, `method_id` per OBS, per-row `licence_status`; censor kinds = CS-001..007 + ROUNDED_INTERVAL, RANGE_ONLY, TRUE_ZERO (GT_CAP an alias of ABOVE_CAP) in `registry/censoring_registry_v1_1.csv`; value origins + DIGITIZED, ESTIMATED_FROM_SUMMARY in `registry/value_origin_registry_v1_1.csv`. 04.2-min is the **single owner** of the censor-kind / value-origin additions that the audit repeated in 03.2, 04.2, 05.4 and 07.D (Plan conflict 5). It is a listed precondition of Step 08 (H4 approval required). Rulings: R-03, R-04, R-02 (additive: `censoring_registry_v1.csv` and `value_origin_registry_v1.csv` stay untouched; the v1.1 files are new).

Where it lands: `OBS` (and the same value block on `AGG`) in `registry/schemas/OBS.draft_v1_1.schema.json` / `AGG.draft_v1_1.schema.json`. Companion: `lineage_contract_v1_1.md`.

Research basis (`r_evidence_model.md` §Q2, Q4): effect-size variance (Hedges et al. 1999; Lajeunesse 2011) needs mean, dispersion **and its type**, and n; Cochrane ch. 6 conversions require knowing *which* dispersion statistic was reported; Wan et al. 2014 estimates from median / range are allowed only as flagged ESTIMATED derivations; censoring: SSOT L19291–19317, L23992–24001 (no zero imputation; censored likelihood), EFSA 2010 and Hwang et al. 2023 (RE Q4); basis: FAO / INFOODS unit and denominator conversion guideline (conversion needs its inputs, e.g. moisture, and is a DERIVED record); EuroFIR Method Indicator / Value Type thesauri (analysis vs calculation vs imputation; numeric vs qualitative). None of the 17,978 EVD rows has SD or n (RE §0), so inverse-variance weighting is impossible for the current corpus: that is a structural NOT_REPORTED, not a value to impute.

---

## 1. Field set

All fields are **required keys** in the draft schema with an explicit status where the value may be unknown. A missing key is a validation error; "unknown" is spelled `UNKNOWN`, "source silent" is spelled `NOT_REPORTED`, never 0, "", or a default.

| Field | Values (draft) | Notes / rule |
|---|---|---|
| `value` | `{status, value, low, high, unit, unit_id, unit_id_status, qualitative, raw}`; status ∈ MEASURED, RANGE, QUALITATIVE, CENSORED, UNKNOWN, NOT_APPLICABLE | Same status vocabulary as the ledger `QVALUE`. A number only where the status says so; MEASURED needs `value` + non-empty `unit`; RANGE needs `low`, `high`, `unit`; CENSORED carries **no** number (the limit lives in `censoring`) but needs `unit`; `raw` keeps the verbatim string; `unit` stays the raw printed unit, `unit_id` (UNIT-) is an optional normalised pointer with `unit_id_status` MAPPED / NOT_MAPPED / UNKNOWN (null unless MAPPED). **A MEASURED value of exactly 0 is admitted only with `censoring.kind = TRUE_ZERO`** (a stated real zero with a basis note); it is never produced from a non-detect, an unreported or an unknown value |
| `statistic` | MEAN, MEDIAN, SINGLE, GEOMETRIC_MEAN, MODE, MIN, MAX, OTHER, UNKNOWN | what the reported number is |
| `n_biological`, `n_technical` | `{status ∈ REPORTED, NOT_REPORTED, NOT_APPLICABLE, UNKNOWN, value}` | REPORTED needs an integer ≥ 1. Never 0, never a default 1. Counts are separate (RE Q4) |
| `dispersion` | `type` ∈ SD, SE, VARIANCE, CI (+`ci_level`), RANGE, IQR, INSTRUMENT, REPORTED_UNSPECIFIED, **CV_PERCENT, POOLED_SE, LSD**, NONE_REPORTED, UNKNOWN; `value` / `low` / `high`; `unit` (null = same as the value; CV_PERCENT must say "%"); **`n_basis`** ∈ BIOLOGICAL, TECHNICAL, NOT_REPORTED, UNKNOWN, NOT_APPLICABLE (which n the SD / SE refers to: needed for Cochrane SE→SD conversion); **`scope`** ∈ PER_VALUE, POOLED_TABLE, NOT_APPLICABLE, UNKNOWN (one pooled SEM / LSD for a whole table is common in food science); **`significance_raw`** (letters / p text verbatim); `derivation` ∈ AS_REPORTED, ESTIMATED_FROM_SUMMARY, DIGITIZED, NOT_APPLICABLE | SD / SE / VARIANCE / INSTRUMENT / REPORTED_UNSPECIFIED / CV_PERCENT / POOLED_SE / LSD need a value ≥ 0; SE and POOLED_SE cannot have n_basis NOT_APPLICABLE; POOLED_SE and LSD have scope POOLED_TABLE or UNKNOWN; NONE_REPORTED / UNKNOWN force n_basis and scope NOT_APPLICABLE; CV is stored as printed, never converted to an SD; CI needs low, high and a level in (0,1); RANGE / IQR need low, high; NONE_REPORTED / UNKNOWN carry no number. The type tokens are a superset-compatible echo of `registry/schemas/condition_value_v1.schema.json` (`SD, SE, CI, INSTRUMENT, REPORTED_UNSPECIFIED, UNKNOWN`) |
| `censoring` | `kind` ∈ DETECTED, TRUE_ZERO, ND, LT_LOD, LT_LOQ, GT_ULOQ, GT_CAP, GT_STATED, LT_STATED, CENSORED_UNKNOWN, ROUNDED_INTERVAL, RANGE_ONLY, **TRACE_BETWEEN_LOD_LOQ**, NOT_REPORTED; `registry_id` (CS-), `limit_low`, `limit_high`, `limit_unit`, `limit_origin`, `resolution`, `basis_note` | §2 |
| `lod`, `loq` | `{status ∈ REPORTED, NOT_REPORTED, NOT_APPLICABLE, UNKNOWN, value, unit}` | method limits as stated for this observation. Today **null everywhere** in the ledger (`lod` / `loq` are null; the sources record only GT_CAP caps, D-018); legacy mapping: NOT_REPORTED only where the source row is known to carry none, otherwise UNKNOWN (§4). A censor limit is not a LOD |
| `basis_id`, `basis_raw` | `MB-001..008` (`measurement_basis_registry_v1.csv`) + proposed MB-009..011 (§1a); **both keys are required** (`basis_raw` is the source wording, null only when the source states none: the normalised column never exists without the raw it came from) | no silent cross-basis pooling; MB-004 and MB-008 are non-combinable; MB-007 (dimensionless ratio) forces a stated retention definition |
| `retention_definition`, `retention_definition_evidence`, `retention_type_id` | `retention_definition` ∈ **TRUE_MURPHY, APPARENT_FRESH_BASIS, APPARENT_DRY_BASIS, APPARENT_BASIS_UNSTATED**, TR_OR_AR_UNDISCLOSED, UNKNOWN, NOT_APPLICABLE; `retention_definition_evidence` ∈ STATED_IN_PRIMARY, STATED_IN_SECONDARY, INFERRED_FROM_FORMULA, ASSUMED, NOT_APPLICABLE, UNKNOWN; `retention_type_id` (RT-001..006, optional) keeps the registry id and is checked for consistency: RT-001 / RT-003 ⇒ TRUE_MURPHY, RT-002 ⇒ APPARENT_*, RT-004 ⇒ TR_OR_AR_UNDISCLOSED, RT-005 ⇒ UNKNOWN, RT-006 ⇒ NOT_APPLICABLE | **Deviation from the card's five tokens (decision 3).** Review B #21: the card's TRUE and YIELD_ADJUSTED are the SAME quantity (Murphy et al. 1975 true retention, weight change accounted for) and differ only in who states it, which belongs in an evidence field, not in the definition; APPARENT carried no basis although apparent retention on fresh vs dry weight differs by the water loss (often 10–50%) and MB-007 delegates the basis to the retention type. Mapping of the card tokens: TRUE → TRUE_MURPHY; YIELD_ADJUSTED → TRUE_MURPHY (+ evidence); APPARENT → APPARENT_FRESH_BASIS / APPARENT_DRY_BASIS / APPARENT_BASIS_UNSTATED (no default); TR_OR_AR_UNDISCLOSED, UNKNOWN unchanged; NOT_APPLICABLE added for values that are not retentions. Phenol-Explorer: TRUE_MURPHY + STATED_IN_SECONDARY (RT-003 rests on a secondary snippet and stays AMBIGUOUS pending a primary-source check, D-020). DRV adds `derived_quantity` APPARENT_RETENTION_FW / APPARENT_RETENTION_DW |
| `method_indicator` | ANALYSIS, CALCULATION, IMPUTATION, IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE, COMPILED, UNKNOWN | EuroFIR Method Indicator idea (analysis / calculation / imputation) plus two project tokens. **The EuroFIR term list was not opened** (RE §6); this enumeration is an agent draft to be reconciled with the thesaurus before freezing |
| `method` | `{status ∈ REFERENCED, NOT_REPORTED, NOT_APPLICABLE, UNKNOWN, method_id (MEAS-), platform_family, platform_raw}` | `method_id` **per OBS**, not only per study (one paper can use HPLC for one analyte and GC-MS for another, RE Q4). `platform_family` reuses the MEAS `family` enum; `platform_raw` keeps the source wording. Finer platform vocabulary (07.C) is not adopted |
| `condition_ref` | `{status ∈ LINKED, INHERITED_FROM_SAMPLE, NOT_REPORTED, NOT_APPLICABLE, UNKNOWN, condition_id (COND-)}` | |
| `value_origin` | VO-001..006 names + DIGITIZED, ESTIMATED_FROM_SUMMARY, DEFINITIONAL_NORMALISATION (VO-009) | §3. DIGITIZED requires `digitization{tool, tool_version, uncertainty (> 0 or null), uncertainty_unit (or null), uncertainty_status ∈ READ_FROM_TOOL / ESTIMATED_BY_READER / UNKNOWN, uncertainty_type ∈ HALF_WIDTH / SD / AXIS_RESOLUTION / UNKNOWN, axis_scale_x / axis_scale_y ∈ LINEAR / LOG10 / LN / UNKNOWN, calibration_points_raw, digitizer, n_reads, read_sd, figure_locator}`; an unknown read uncertainty is `uncertainty_status = UNKNOWN` with the number null, never a number and never 0; other origins require `digitization = null`. Two independent reads for TEST / SIM-VAL eligibility (THR-04K-03) |
| `licence_status`, `storage_rule` | SRC vocabulary: VERIFIED / ASSUMED / UNKNOWN / RESTRICTED; COMMIT_OK / DERIVED_ONLY / LOCAL_ONLY / DO_NOT_STORE | per-row, inherited from the source and never weaker. Phenol-Explorer redistribution needs permission; USDA / Bognár licence ASSUMED / DERIVED_ONLY |
| `locator` | `{doc_id, locator_type, page, table_id, row_label, column_label, figure_id, char_span, raw_text}` | exact place in a DOC; `raw_text` is a required key (null only when the source has no text form). A locator DOC is never a lineage edge (lineage contract §4.2 step 2a) |
| `series_link` | `{status ∈ LINKED_KINPT, ENDPOINT_ONLY_SOURCE, SERIES_NOT_EXTRACTED, UNKNOWN; kinpt_id}` | record-level R-04 guard (kinetic contract §5): this OBS is the value behind a KINPT, or the source reports one time per cell (checked by the second extractor, not self-certified), or a series exists but was not extracted, or not assessed. UNKNOWN is treated like SERIES_NOT_EXTRACTED for exclusions |
| `measurement_dedup` | `{status ∈ UNIQUE_MEASUREMENT, CANONICAL, DUPLICATE_OF_CANONICAL, UNKNOWN; canonical_obs_id; report_priority}` | the same measurement read from the journal paper and from the thesis gives two OBS with different locators; only UNIQUE_MEASUREMENT and CANONICAL enter pooled or meta-analytic estimates and row counts (Cochrane: collate the reports, extract each result once). The same value reaching us from two reports is never counted twice |
| `extraction_version`, `extraction_record_ids` | string; `XTR-` ids | Step 09 links |

### 1a. Measurement bases: proposed additions (draft content of `registry/measurement_basis_registry_v1_1.csv`, not created)

`measurement_basis_registry_v1.csv` (MB-001..008) stays untouched. True retention and compositional calculation need three bases the registry lacks (review B #22). Proposed rows (all `PROPOSED_H4`):

```csv
measurement_basis_id,name,definition,ledger_target_basis_aliases,combinable_with,added_in
MB-009,PER_RAW_EQUIVALENT_MASS,"nutrient in the cooked portion per 100 g of the raw food it came from (needs a yield / moisture parent)",,MB-009 only,v1.1-PROPOSED
MB-010,PER_EDIBLE_PORTION,"per mass of the edible portion (refuse removed); as purchased is MB-001/003 with the refuse stated",,MB-010 only,v1.1-PROPOSED
MB-011,PER_UNIT_ITEM,"per item / piece (egg, fruit, slice)",,MB-011 only,v1.1-PROPOSED
```

Proposed ledger-alias settlements (the card does not decide them; H4): `WET` → MB-001, `AS_CONSUMED` → MB-003, `PER_SERVING` → MB-006, `APPARENT_RETENTION` → MB-007 **plus** `retention_definition` APPARENT_* (the fresh / dry basis then lives in the definition), `HEADSPACE` → no MB entry (stays MB-008 with `basis_raw` until H4 decides on a new row). Validator rule (not expressible in JSON Schema): a `BASIS_CONVERSION` DRV needs a moisture / yield / refuse / conversion-factor parent with a matching `parent_roles` role (schema-enforced) **on the same SMP** or a stated AGG (semantic check).

---

## 2. Censoring: rules and the draft registry

Laws: a non-detect is **not zero** (left-censored; limit may be unknown); UNKNOWN is **not** NON_DETECT (CS-007); a cap is a right-censored bound, not a value; a rounded value is an interval, not a point; a true zero is allowed only when the source states a real zero.

Draft content of `registry/censoring_registry_v1_1.csv` (CS-001..007 copied verbatim from `registry/censoring_registry_v1.csv` — `name`, `definition` and `numeric_use` unchanged; ids are never reused; new rows appended; three helper columns added; CS-005's `GT_CAP` alias is carried by the helper column `ledger_censor_kind`, not by editing `numeric_use`):

```csv
censoring_id,name,definition,numeric_use,ledger_censor_kind,side,added_in
CS-001,DETECTED,a quantified value is reported,value usable,DETECTED,NONE,v1
CS-002,NON_DETECT,analyte reported as not detected (limit may be unknown),NOT zero; left-censored,ND,LEFT,v1
CS-003,BELOW_LOD,below the stated limit of detection,left-censored at LOD (LOD must be stated),LT_LOD,LEFT,v1
CS-004,BELOW_LOQ,below the stated limit of quantification,left-censored at LOQ (LOQ must be stated),LT_LOQ,LEFT,v1
CS-005,ABOVE_CAP,reported value is a cap/upper bound (e.g. >100% retention capped),right-censored at the cap,GT_CAP,RIGHT,v1
CS-006,CENSORED_UNKNOWN,censored but type/limit unknown,no numeric use,CENSORED_UNKNOWN,UNKNOWN,v1
CS-007,NOT_REPORTED,no value or censoring information (UNKNOWN is not NON_DETECT),none,NOT_REPORTED,UNKNOWN,v1
CS-008,ROUNDED_INTERVAL,value reported rounded to a stated resolution (e.g. nearest 5%): the true value lies within half the resolution of the reported number,interval-censored; resolution required; reported number kept as MEASURED,ROUNDED_INTERVAL,INTERVAL,v1.1
CS-009,RANGE_ONLY,only an interval (low-high) is reported and no point value,interval-censored; both ends required; value status RANGE,RANGE_ONLY,INTERVAL,v1.1
CS-010,TRUE_ZERO,the source states a real zero (analyte absent by definition; not below a detection limit),value 0 allowed ONLY with a basis note; never inferred from ND or NOT_REPORTED,TRUE_ZERO,NONE,v1.1
CS-011,TRACE_BETWEEN_LOD_LOQ,"detected but below the LOQ: interval-censored between the stated LOD and LOQ (INFOODS 'tr')",interval-censored [LOD LOQ); both limits required; value status CENSORED; no number,TRACE_BETWEEN_LOD_LOQ,INTERVAL,v1.1
CS-012,ABOVE_ULOQ,reported value is above the upper limit of quantification,right-censored at the stated ULOQ,GT_ULOQ,RIGHT,v1.1-PROPOSED-H4
CS-013,ABOVE_STATED,"reported as greater than a stated bound",right-censored at the stated bound,GT_STATED,RIGHT,v1.1-PROPOSED-H4
CS-014,BELOW_STATED,"reported as less than a stated bound",left-censored at the stated bound,LT_STATED,LEFT,v1.1-PROPOSED-H4
```

CS-012..014 close the gap for the three ledger tokens that have no CS id (decision 2); they are proposals and the alternative is to declare the tokens ledger-only aliases.

Cross-field laws enforced by the draft OBS / AGG schemas (JSON Schema `if/then`):

| If … | then … |
|---|---|
| `censoring.kind` ∈ ND, LT_LOD, LT_LOQ, GT_ULOQ, GT_CAP, GT_STATED, LT_STATED, CENSORED_UNKNOWN | `value.status = CENSORED` (and conversely a CENSORED value needs one of these kinds) |
| kind ∈ LT_LOD, LT_LOQ, LT_STATED | `limit_high` (number) and `limit_unit` required |
| kind ∈ GT_ULOQ, GT_CAP, GT_STATED | `limit_low` (number) and `limit_unit` required |
| kind = ROUNDED_INTERVAL | `resolution` > 0 required; `value.status = MEASURED` |
| kind = RANGE_ONLY | `value.status = RANGE` |
| kind = TRUE_ZERO | non-empty `basis_note`; `value.status = MEASURED` and `value.value = 0` |
| `value.status = MEASURED` and `value.value = 0` (the converse) | `censoring.kind = TRUE_ZERO`; with NOT_REPORTED, DETECTED, ROUNDED_INTERVAL … the record is rejected (no 0 from an unknown or non-detect) |
| kind = TRACE_BETWEEN_LOD_LOQ | `limit_low` (LOD), `limit_high` (LOQ), `limit_unit` required; `value.status = CENSORED` |
| any stated limit (`limit_low`, `limit_high`) | strictly positive (> 0): a limit of 0 is not a limit and is never a stand-in for a non-detect |
| kind = GT_CAP together with `resolution` (USDA "> 100 reported as 100", rounded to the nearest 5%) | the cap stays AS PRINTED in `limit_low` (raw preserved); the effective bound `limit_low - resolution/2` is a NEW derived quantity (a reported 100 means true ≥ 97.5), never an overwrite |
| kind ∈ DETECTED, NOT_REPORTED, CENSORED_UNKNOWN | `limit_low` and `limit_high` null |
| `value_origin = ESTIMATED_FROM_SUMMARY` | `dispersion.derivation ∈ {ESTIMATED_FROM_SUMMARY, NOT_APPLICABLE}` |
| `basis_id = MB-007` | `retention_definition ≠ NOT_APPLICABLE` |

**Gap the crosswalk exposes (not in the card):** three ledger censor tokens have no CS id: `GT_ULOQ` (right-censored at the upper limit of quantification), `GT_STATED` and `LT_STATED` (D-013, stated bounds). The drafts keep them in the OBS enum so the ledger mapping is lossless and leave `registry_id` null for them. Decision for H4: adopt CS-012..014 as proposed above, or declare them ledger-only aliases. One `censoring.kind` cannot express the USDA combination of capping and rounding; the rule in the table above (cap as printed + `resolution`) is the proposed handling, the alternative being a `kinds[]` list (decision 2).

## 3. Value origins

Draft content of `registry/value_origin_registry_v1_1.csv` (VO-001..006 verbatim from v1; VO-006 has an empty definition in v1 and is kept as is):

```csv
value_origin_id,name,definition,added_in
VO-001,MEASURED,measured by the source authors (primary study),v1
VO-002,REPORTED,reported by a database/compilation without per-row measurement detail,v1
VO-003,DERIVED_DETERMINISTIC,computed by a documented deterministic rule from stated values,v1
VO-004,SOURCE_IMPUTED,imputed by the source (stated),v1
VO-005,SOURCE_IMPUTATION_POSSIBLE,source says imputation occurs but does not mark rows (USDA R6),v1
VO-006,UNKNOWN,,v1
VO-007,DIGITIZED,read from a figure with a digitising tool; tool + version mandatory; read uncertainty stated or explicitly UNKNOWN (never a forced number); never silently merged with tabular values,v1.1
VO-008,ESTIMATED_FROM_SUMMARY,mean/SD (or similar) estimated from median / range / IQR by a documented method (Wan et al. 2014 type); a flagged estimate and never recorded as MEASURED,v1.1
VO-009,DEFINITIONAL_NORMALISATION,a point that equals its reference by construction (t0 = 1 or 100% of a relative-scale series); not an observation; fitting code excludes it,v1.1
```

A DRV may carry only `DERIVED_DETERMINISTIC` or `ESTIMATED_FROM_SUMMARY`. `MODEL_ESTIMATED`, `IMPUTED` (model side) and `SIMULATED` are **provenance classes of other planes**, not value origins of evidence-plane records (FW-09, FW-03).

---

## 4. Legacy population (dry-run design, not run)

Pass criterion from the Step 04 card: **100% of the 17,978 ACTIVE rows get a value or an explicit status for each new field, 0 value changes** (hash of the original value fields before and after is identical), ledgers byte-identical, on a scratch copy. Proposed default status per legacy population (assigned by rule at export-v2 time; `UNKNOWN` when no rule applies):

| New field | Legacy rule |
|---|---|
| `dispersion` | `NONE_REPORTED` for all rows only where the source file's column list shows no SD / SE (RE §0 found none in the corpus; this was not re-read for this draft); a ledger-null alone maps to `UNKNOWN`; `REPORTED_UNSPECIFIED` if the old `uncertainty` number is non-null; `n_basis` and `scope` NOT_APPLICABLE |
| `n_biological`, `n_technical` | `NOT_REPORTED` only where the source file's column list shows no n (no ledger row has n); a ledger-null alone maps to `UNKNOWN` |
| `lod`, `loq` | `NOT_REPORTED` (matches the existing token `NOT_REPORTED_BY_SOURCE_ROW`) where the source row is known to carry none; otherwise `UNKNOWN` |
| `censoring` | from the old `censor{kind, limit}` (same tokens); USDA "nearest 5%" with the "> 100 reported as 100" cap → GT_CAP with the printed cap in `limit_low` and `resolution` 5; uncensored rows → DETECTED only if the source states an exact value, else NOT_REPORTED. **A legacy value of exactly 0 is mapped to TRUE_ZERO only when the source states a real zero; otherwise the row cannot be exported as MEASURED 0 and stays value UNKNOWN** (no 0 from an unreported or non-detect value) |
| `method_indicator` | USDA R6: IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE (SRC / MEAS note "imputed from similar foods"); others UNKNOWN until read |
| `value_origin` | USDA R6: VO-005; Bognár and PE: assigned in 08a by rule (VO-001 / VO-002 / VO-003) or UNKNOWN |
| `retention_definition` | USDA R6: TR_OR_AR_UNDISCLOSED (RT-004); Bognár: TRUE_MURPHY (RT-001; evidence set when the text is read, UNKNOWN until then); PE: TRUE_MURPHY + `STATED_IN_SECONDARY` (RT-003, AMBIGUOUS pending a primary check) |
| `series_link`, `measurement_dedup` | `ENDPOINT_ONLY_SOURCE` for USDA R6 / Bognár (K0 aggregates are AGG, no OBS); Phenol-Explorer OBS: `UNKNOWN` (the papers may contain series; not knowable without them); `measurement_dedup` UNKNOWN until reports are linked |
| `licence_status` | from the SRC row (Phenol-Explorer: VERIFIED, DERIVED_ONLY; the 125 PE papers: UNKNOWN, DERIVED_ONLY) |

## 5. What is and is not enforced by the schema drafts

Enforced at record level: required keys, enums, the status ↔ number laws, the table in §2 (including the converse zero rule and the positive limits), DIGITIZED ↔ `digitization` (with an UNKNOWN-able uncertainty), retention definition ↔ `retention_type_id`, dispersion type ↔ n-basis / scope, `series_link` / `measurement_dedup` shapes, id patterns. **Not** expressible in JSON Schema and left to the semantic validators (Mac): `low ≤ high`, unit consistency between `value.unit` and `censoring.limit_unit`, `lod` / `loq` vs `limit_*` agreement, the n ≥ replicates sanity checks, `digitization` ↔ `KINPT.digitized` mirror, and any cross-record rule.

## 6. Open decisions for H4

1. Approve the field set and the enumerations (the EuroFIR-derived `method_indicator` list and the dispersion token list are agent drafts).
2. The three unmapped ledger censor tokens (§2): add CS ids, or keep ledger-only.
3. `retention_definition` split (TRUE_MURPHY / APPARENT_FRESH_BASIS / APPARENT_DRY_BASIS / APPARENT_BASIS_UNSTATED + evidence field) replacing the card's TRUE / APPARENT / YIELD_ADJUSTED, and `NOT_APPLICABLE` added (D-16).
4. Whether `lod` / `loq` live on OBS (draft) or only on MEAS (method level; per-observation values then reference it).
5. Registry file names `censoring_registry_v1_1.csv` / `value_origin_registry_v1_1.csv` / `measurement_basis_registry_v1_1.csv` are to be created **after** approval; the blocks above are their proposed content.
6. New bases MB-009..011 and the alias settlements of §1a.
7. CS-011 TRACE_BETWEEN_LOD_LOQ and the ids CS-012..014 for the three unmapped ledger tokens; cap + resolution handling vs a `kinds[]` list.
8. Digitisation record (axis scale, calibration points, digitizer, repeat reads) and the two-read rule (THR-04K-03); `measurement_dedup` and `series_link` on OBS.
