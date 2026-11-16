# Final state schema — `S_t = (G, C, Q, Y, P)`

**`AI_DRAFTED` · `NOT_HUMAN_REVIEWED` · 17 Nov 2026.** Read from the code, not from plans.
**The schema is broad; the observed state is sparse.** CulinaryState is **not** defined by the
salt / acid / lipid / water fields — those are a populated subset. `UNKNOWN` with a reason is a valid,
complete cell and is never zero.

Source keys: `[SF]` `src/culinarystate/composition/state_full.py` · `[S]` `src/culinarystate/composition/state.py` ·
`[CV]` `src/culinarystate/composition/context_v12.py` · `[FT]` `tools/s179_state_dataset_fill.py` ·
`[SV]` `src/culinarystate/composition/state_vector.py` ·
`[SI]` `reports/s179/state_inventory_FINAL_2026-11-15.md` (rates there are **heat-row** rates) ·
`[FILL]` `reports/s179/state_dataset_fill_full_2026-11-14.json` (612,782 recipes, 9,470,190 rows, 0 exceptions; **all-row** rates per source family) ·
`[FILLC]` `reports/s179/state_dataset_fill_full_D116v1_2026-11-14.json` (612,782 recipes, 9,194,463 rows; C_t **v1** column names) ·
`[D]` `DECISIONS.md`.

## 0. Wire format and unit of state

- One state record per **(food, step)**: for each event, for each non-medium ingredient in the consumed lots `[SF]`.
- Every cell is `{"v": value, "b": basis}` (`V`) or `{"v": None, "u": reason}` (`U`) `[S]`.
- **P (provenance) is not a separate block of fields**: it is the `b` / `u` carried by every cell, plus `_PARTIAL` suffixes on history sums `[SF]`. `[SI §3]` records P as 100% by construction.
- Record header (plain values, not cells): `step`, `event_id`, `action` (span text), `food_id`, `food` `[SF]`.
- All-row fill ranges below are min–max across the four families A1_BBC_GOOD_FOOD / FOODCOM / GUTENBERG_SEGMENT / WIKIBOOKS `[FILL]`. A cell with no rate recorded for its State v2 name is `NOT_EVIDENCED`.

## 1. Fields the engine actually emits

### G — lineage / structure

| Field | Value type | Basis vocabulary | UNKNOWN reason codes | Producer | Measured fill |
|---|---|---|---|---|---|
| `process` | str `"<PROC id> <name>"` | `RUNG_A` | none emitted (always `V`; may contain `None None` if no proc) | Rung A `proc_id` attribute + PROC ledger `[SF]` | `process_id` 99.08–99.82% all rows `[FILL]` |
| `family` | str | `PROC_LEDGER` | `NO_PROC` | PROC ledger `[SF]` | `process_family` 99.08–99.82% all rows `[FILL]` |
| `event_kind` | `MERGE` / `SPLIT` / `TRANSFORM` | `RUNG_A` | none | count of consumes/produces `[SF]` | "all events" `[SI §3]` |
| `lot_members` | list[str] ingredient names | `RUNG_A_LOT` | none (may be empty list) | `lot_members_v11` over entity parentage `[S]` | "all events" `[SI §3]` |
| `history` | list[str] prior process names for this food | `LINEAGE` | none | running history `[SF]` | NOT_EVIDENCED |
| `cell_integrity` | `NO_CUT_RECORDED` / `CUT` / `CRUSHED_PUREED` | `CUT_HISTORY` | none | family `MECHANICAL_CUT` + crush-word list `[SF]` | "per step" `[SI §3]` |
| `heat_steps_so_far` | int | `LINEAGE+PHYSICS_V06_HEAT_FLAG` | none | running count `[SF]` | NOT_EVIDENCED |
| `is_heat_step` | bool | `PHYSICS_V06_L1` | none | physics v06 heat flag `[SF]` | NOT_EVIDENCED |

### C — composition / contact context (C_t v1.2)

| Field | Value type | Basis vocabulary | UNKNOWN reason codes | Producer | Measured fill |
|---|---|---|---|---|---|
| `salt_present` | `True` / not-detected sentinel | marker-table basis + SR basis, or the list of reasons why true `[CV]` | `MEMBER_UNLINKED` | `context_v12._axis` `[CV]` | v1 column `comp_salt_present` 85.95–90.22% all rows `[FILLC]`; v1.2 name: NOT_EVIDENCED |
| `acid_present` | same | marker-table basis (no SR for acid) `[CV]` | `MEMBER_UNLINKED` | same | v1 `comp_acid_present` 85.95–90.22% `[FILLC]` |
| `lipid_present` | same | marker + SR | `MEMBER_UNLINKED` | same | v1 `comp_lipid_present` 85.95–90.22% `[FILLC]` |
| `aqueous_present` | same | marker + SR | `MEMBER_UNLINKED` | same | NOT_EVIDENCED |
| `contact_phase` | `AQUEOUS` / `LIPID` / `AQUEOUS+LIPID` / `AIR` | `CONTEXT_AXES_V12` | `MEDIUM_UNKNOWN`, `NO_LINKED_MEMBERS` | `context_v12._phase` `[CV]` | v1 `comp_contact_phase` 39.69–49.40% `[FILLC]` |
| `member_composition` | dict ing_id → {nutrient: value} for co-members | USDA SR basis `[CV]` | none (may be empty dict) | `registry/ing_sr_composition_v1.csv` (793 ING `[SI §3]`) | NOT_EVIDENCED |
| `own_composition` | dict nutrient → value | `USDA_SR_LEGACY_2018_04` | `NO_SR_MATCH` | same registry `[SF]` | NOT_EVIDENCED |
| `nacl_equiv_fraction_as_added` | — | — | **always** `MASS_NOT_GROUNDED` | none (see table 2) | 0 by construction `[CV]` |
| `fat_fraction_as_added` | — | — | **always** `MASS_NOT_GROUNDED` | none | 0 by construction `[CV]` |
| `lot_acidity_band` | — | — | **always** `LOT_PH_NOT_COMPUTED` | none; not wired to FDA bands (D-136) | 0 by construction `[CV]`; "0%" `[SI §3]` |
| `salt_exposure_before` | bool | `LINEAGE_C_T` | none | running history `[SF]` | "derived" `[SI §3]`; rate NOT_EVIDENCED |
| `acid_exposure_before` | bool | `LINEAGE_C_T` | none | running history `[SF]` | same |

### Q — physical conditions

L1 cells: `V(value, basis)` where basis is the binder's own `basis` or `status` string for that
input, and the UNKNOWN reason is the binder's `reason` or the literal `UNKNOWN`; non-heat events give
`NOT_A_HEAT_EVENT` `[FT l1_cell]`. The full binder basis/reason vocabulary lives in
`src/culinarystate/simulation/condition_binding.py`, **not opened** → enumerations beyond those shown: NOT_EVIDENCED.

| Field | Value type | Basis vocabulary | UNKNOWN reason codes | Producer | Measured fill |
|---|---|---|---|---|---|
| `medium` | str medium type | binder basis (L1 PROC_DEF / TEXT `[SI]`) | `NOT_A_HEAT_EVENT`, binder reason, `UNKNOWN` | physics v06 L1 binder `[SF]`,`[FT]` | heat rows 53.8% `[SI §3]`; all rows 7.44–14.03% `[FILL]` |
| `temperature_C` | number / profile | binder basis | same | L1 axis `temperature_profile` `[FT]` | heat rows 16.5% stated `[SI]`; all rows 2.71–5.87% `[FILL]` |
| `duration_min` | number | binder basis (TEXT_STATED `[SI]`) | same | L1 axis `duration` | heat rows 28.2% `[SI]`; all rows 0.63–7.53% `[FILL]` |
| `matrix_class` | str | binder basis | same | L1 | all rows 5.94–7.15% `[FILL]`; heat-row: NOT_EVIDENCED |
| `lid_state` | str | binder basis | same | L1 | heat rows 8.8% `[SI]`; all rows 1.23–1.67% `[FILL]` |
| `piece_size_class` | str | binder basis (CUT_HISTORY `[SI]`) | same | L1 | heat rows 9.7% `[SI]`; all rows 1.57–2.63% `[FILL]` |
| `start_mode` | str | binder basis | same | L1 | "low" `[SI §3]`; number NOT_EVIDENCED |
| `thermal_state` | str L2 status | `PHYSICS_V06_L2` | `NOT_A_HEAT_EVENT` | L2 scenario layer `[FT l2_cells]` | all rows 18.30–19.48% `[FILL]` |
| `food_T_typical_C` | float | `SCENARIO_DEFAULT` | `NOT_A_HEAT_EVENT`, L2 status string, `SCENARIO_UNKNOWN` | L2 TYPICAL scenario `[FT]` | heat rows 46.4% scenario `[SI]`; all rows 6.69–12.94% `[FILL]` |
| `moisture_cap_C` | float | `SCENARIO_DEFAULT` | `NOT_A_HEAT_EVENT`, `NO_MOISTURE_CAP`, L2 status, `SCENARIO_UNKNOWN` | L2 `[FT]` | all rows 6.47–11.96% `[FILL]` |
| `thermal_dose_typical_min` | float | `SCENARIO_DEFAULT` | `NOT_A_HEAT_EVENT`, `DOSE_NOT_COMPUTED` | `volume_avg_dose` on TYPICAL `[SF]` | "where L2 runs" `[SI]`; number NOT_EVIDENCED |
| `oxygen_exposure_proxy` | `LIMITED_LID` / `OPEN` | `LID_STATE_PROXY` | `NO_LID_CUE` | derived from `lid_state` `[SF]` | "≈ lid rate" `[SI]` |
| `cumulative_thermal_dose_min` | float | `SUM_SCENARIO`, `SUM_SCENARIO_PARTIAL` | `NOT_HEATED_YET`, `DOSE_NOT_COMPUTED` | running sum `[SF]` | NOT_EVIDENCED |
| `hot_aqueous_minutes` | float | `SUM_TEXT_STATED`, `SUM_TEXT_STATED_PARTIAL` | none (0.0 with `_PARTIAL` when a duration is missing) | running sum `[SF]` | "duration-limited" `[SI]`; number NOT_EVIDENCED |
| `hot_fat_minutes` | float | same | none | running sum `[SF]` | same |

### Y — analyte / evidence state (two targets: `vitc` = SVAR-000009, `lycopene` = SVAR-000025 `[SF]`)

| Field (per target `t`) | Value type | Basis vocabulary | UNKNOWN reason codes | Producer | Measured fill |
|---|---|---|---|---|---|
| `{t}_route` | str route | joined `composition_reasons`, else `ROUTER_0.4.1` | `NO_ROUTER_ITEM` (then the three cells below are **absent**, not UNKNOWN) | frozen router + `router_v12.composition_route` `[SF]` | "all heat items" `[SI §3]`; number NOT_EVIDENCED |
| `{t}_compat` | dict axis → verdict | `D-122_AXIS_TABLE` | — | same | NOT_EVIDENCED |
| `{t}_frozen_reasons` | list[str] (≤ 4) | `ROUTER_0.4.1` | — | frozen router | NOT_EVIDENCED |
| `{t}_evidence` | list[str] `EVD-id=value unit` or list of EVD ids | `APPLIED`, `FOUND_NOT_APPLIED` | `NO_EVIDENCE_ROW` | EVD ledger via router | NOT_EVIDENCED |
| `vitc_formula_retention_typical` | float | `FORMULA_RESEARCH_ONLY` (NOT_VALIDATED) | `NOT_A_HEAT_EVENT`, gate-failure reason from the formula check (`why`, vocabulary not enumerated here) | Model A fit, `[FT l2_cells]` | 826 events `[SI §3]`; all rows 0.0–0.08% `[FILL]` (`aa_retention_typical`) |

### Legacy producers still in `state.py` (not emitted by State v2)

`composition()` (v1) emits `food_lot`, `salt_present`, `acid_present`, `lipid_present`,
`aqueous_solutes`, `contact_phase`, `salt_fraction`, `fat_fraction`, `acidity_band`; reasons
`NO_LINKED_MEMBERS`, `ONLY_MARKER_MEMBERS`, `MEDIUM_UNKNOWN`, `MASS_NOT_GROUNDED`,
`NO_SOURCED_PH_TABLE`; basis `MARKER_TABLE_V1`. `composition_v11()` emits `food_lot`,
`medium_members`, `{salt,acid,lipid}_marker_present` (`True` / `NOT_DETECTED` / `MEMBER_UNLINKED`),
`contact_phase`, `nacl_equiv_fraction_as_added`, `fat_fraction_as_added`, `lot_acidity_band`
(`LOT_PH_NOT_COMPUTED`); reasons add `ONLY_MEDIUM_MEMBERS`; basis `MARKER_TABLE_V2`
(+`PHYSICS_V06_L1`) `[S]`. These are the columns measured in `[FILLC]`
(`comp_food_lot` 76.73–82.91%; `comp_acidity_band`, `comp_salt_fraction`, `comp_fat_fraction` 0.0%).
`NO_SOURCED_PH_TABLE` is **knowingly stale** (a sourced table now exists) — correction recorded, not applied `[D] D-136`.

### Derived view (not the state definition)

`STATE_VECTOR_V0`: 51 named masked dims — G 24, C 13, Q 2, Y 12 `[SI §4]`. V1 appends 9 dims:
`log_heat_steps_so_far`, `thermal_dose_typical_min/60`, `cumulative_thermal_dose_min/60`,
`hot_aqueous_minutes/60`, `hot_fat_minutes/60`, `food_T_typical_C/100`, `moisture_cap_C/100`,
`lid_covered`, `oxygen_limited` `[SV]`. Status `DIAGNOSTIC_RETRIEVAL_ONLY_WEIGHTS_NOT_VALIDATED` `[SV]`.
Mask 0 = UNKNOWN, distinct from a known zero. Nothing is learned.

## 2. Declared but no producer — stays UNKNOWN

| Field / variable | Block | Where declared | Current cell | Why no producer | What would unblock |
|---|---|---|---|---|---|
| `nacl_equiv_fraction_as_added` (v1: `salt_fraction`) | C | `[CV]`, `[S]` | `U(MASS_NOT_GROUNDED)` | masses 0.6% groundable `[SI §3]` | quantity grounding — DEFER |
| `fat_fraction_as_added` (v1: `fat_fraction`) | C | `[CV]`, `[S]` | `U(MASS_NOT_GROUNDED)` | same | same |
| `lot_acidity_band` (v1: `acidity_band`) | C | `[CV]`, `[S]` | `U(LOT_PH_NOT_COMPUTED)` / `U(NO_SOURCED_PH_TABLE)` | lot pH is not a computable function of member pH; D-136 | a measured pH **for the mixture** `[D] D-136` |
| `member_ph_band` | C | shape settled in `[D] D-136`, **not in code** | absent | crosswalk `UNVERIFIED_CROSSWALK_AI_DRAFTED` | human verification of crosswalk rows |
| quantity / mass | G/C | `[SI §3]` | absent ("—") | 0.6% groundable | DEFER (census) |
| water activity / moisture | C/Q | `[SI §3]`; axis 8 `SCHEMA_ONLY` | absent, 0% | no producer | post-submission |
| water:food ratio | Q | L1 slot `water_ratio`, `NOT_BOUND_V0` `[SI §3]` | not emitted by State v2 | slot unbound | binding |
| core vs surface temperature | Q | `[SI §3]` | volume-average dose only | L2 zones not exposed | — |
| molecule set (aroma/taste) | C | `[SI §3]` (IMAP, 313 ING) | not wired | wiring; CAN, cut if late | — |
| enzyme activity state | Y | `[SI §3]` | absent, 0% | needs mechanism sources | post-submission |
| browning / gelatinisation / texture / colour | Y | `[SI §3]` | absent, 0% | no producer | — |
| bioaccessibility (≠ content) | Y | `[SI §3]` | absent | unverified literature | verification |
| analyte routes for any target other than vitamin C / lycopene | Y | `TARGETS` has two entries `[SF]` | absent | not built | — |
| measurement method / platform (axis 12) | compat. | registry `SCHEMA_ONLY` | UNKNOWN with reason | MEAS has 3 rows `[SI §5]` | data |
| `condition_profile_id` (Event IR, not S_t) | IR | `docs/EVENT_IR_CONTRACT.md` | `None` | reference with no referent, no consumer `[D] D-135` | COND records on the recipe side |

## 3. Contradictions / NOT_EVIDENCED

- **Heat-row fill rates are not reproducible from the cited JSON.** `[SI §1]` cites `[FILL]` for
  "heat-row rates" (medium 53.8%, duration 28.2%, lid 8.8%, piece size 9.7%, temperature 16.5%), but
  `[FILL]` as opened has **no** `value_rate_pct_heat_rows` key — only all-row `value_rate_pct` per
  family (e.g. medium 7.44–14.03%). The tool does write that key `[FT]`; this JSON appears to be a
  shard merge without it. The heat-row numbers above are therefore copied from `[SI]` only.
- `[SI §3]` lists `lot_acidity_band = UNKNOWN`; the reason code differs by version
  (`LOT_PH_NOT_COMPUTED` in v1.1/v1.2 code, `NO_SOURCED_PH_TABLE` in v1 and in D-136's text
  "state.py continues to write `acidity_band = UNKNOWN:NO_SOURCED_PH_TABLE`"; D-136 also names a
  future `MIXTURE_PH_NOT_COMPUTED`). State v2 emits `LOT_PH_NOT_COMPUTED`.
- Fill rates for State v2 **v1.2** field names (C block, history sums, Y block) were not found in any
  file opened: NOT_EVIDENCED. `[FILLC]` measures the **v1** composition columns over a different row
  count (9,194,463 vs 9,470,190).
- The not-detected sentinel literal (`NO_MARK`) and the exact marker/SR basis strings in `[CV]` were
  not printed in this pass: NOT_EVIDENCED as literals.
- Both fill runs predate D-134's `lineage_vnext=True` default for State v2 or not: NOT_EVIDENCED.
