# S176 lane L-PHYS: evaporation / phase-change cap in the physics drivers, and the non-BBC re-runs

Status: DRAFT / AI_DRAFTED. Nothing here is a human signature, approval or gate. Built 2026-11-08 in worktree `~/kush_work/culinarystate/.orch` (branch `max/s176-orchestration`, HEAD `bbf5ee6` at run time, files uncommitted). No git write, no ledger, no SSOT, no `registry/compute_runs_v1.csv`, no `docs/` edit. L1 code (`condition_binding.py`, `binding_census.py`, `tools/binding_census.py`) is untouched. Under SSOT §141 no nutrient, compound, yield or safety number is produced; the new outputs are temperatures, equivalent minutes and qualitative flags.

## 1. Verdict

The defect is fixed and default ON for new runs (heat layer 0.2.0, non-heat layer 0.2.0, cap model `evaporation-cap-0.1.0-draft`). Over the full FOODCOM + GUTENBERG_SEGMENT + WIKIBOOKS runs, **the share of heat events with a computed core above 100 °C falls from 47,198 of 68,783 (68.6 %) to 1,242 (1.8 %)**, and every one of the 1,242 is a dry-class matrix that the registry deliberately leaves uncapped. Moist-class cores above the cap: 0 of 55,146 + 13,186 + 451. Violations of cap + 0.5 °C: 0. Median core cook value (moist class, FOODCOM, TYPICAL) falls from 341 to 9.2 equivalent minutes (p99 37,422 to 116). Coverage is unchanged (status, transition and core-known counts identical to S173/S174).

The performance trap is gone: the very long thin RESTING case runs in 0.011 s (it needed about 1.7e8 Crank-Nicolson steps); FOODCOM non-heat L2 took 94 s on 8 workers instead of 23.9 min on 24, and the full FOODCOM heat L2 takes 78 s on 24 workers.

## 2. What was built

| file | change | sha256 (first 16) |
|---|---|---|
| `src/culinarystate/simulation/phase_change.py` | NEW: `PhaseChange`, `CapPolicy`, `Cap`, T_boil (1 atm, altitude, pressure process), matrix regimes, qualitative `surface_state` | a3b3fd82f194dc99 |
| `src/culinarystate/simulation/physics_drivers.py` | adds `slab_mean_theta` (volume average, closed-form semi-infinite branch below Fo 0.02, series above), `core_and_mean_temperature`, `zone_trajectory`; eigenvalues cached per (Bi, n). Old functions keep behaviour | cfc677f6d19e8d3f |
| `src/culinarystate/simulation/scenario_layer.py` | version 0.2.0; cap applied per bracket; new fields; `CapPolicy(enabled=False)` reproduces 0.1.0 byte for byte | 194bad77e098cb71 |
| `src/culinarystate/simulation/nonheat_drivers.py` | `slab_two_stage` exact in time (modal solution of the same finite-difference system), `caps=` per stage, volume average, `method="cn"` keeps the old stepper as reference | 615c93edc960e7e8 |
| `src/culinarystate/simulation/nonheat_scenario.py` | RESTING carries the cap in both stages; version 0.2.0; `_base` is now an instance method | 7ab795545061c599 |
| `registry/phase_change_v1.csv` | NEW: PC-001 (100 °C at 1 atm, PROCESS_DEFINITION), PC-002 (pressure bracket 108.4 / 115.2 / 121.0), PC-010..014 (altitude), PC-030..034 (gauge pressure table), PC-040/041 (tolerances) | d23eac29c5411799 |
| `registry/matrix_moisture_regime_v1.csv` | NEW: explicit class list (section 3.2) | c4736dbcf2d392b5 |
| `tools/scenario_layer_run.py` | `--compare-uncapped` (before/after counts), `--no-evaporation-cap`, `--altitude-m`, `--pressure-psig`, single-thread BLAS, timing and manifest | 74085da5acbdad32 |
| `tools/nonheat_layer_run.py` | `--l2-only` (re-run L2 over existing L1 records), same options, RESTING before/after block | 21505e07183578e6 |
| `tests/unit/test_s176_phys_cap.py` | NEW: 153 tests | 61f4affc731275ab |

## 3. Design

### 3.1 The cap
While a moist matrix holds free water, the boundary temperature of the conduction problem is `min(T_medium, T_cap)` (same h, same slab series). T_cap:

- Atmospheric process: 100 °C (PC-001, PROCESS_DEFINITION), flags `PRESSURE_ASSUMED_1ATM` and `ALTITUDE_ASSUMED_SEA_LEVEL`.
- Optional altitude (`CapPolicy(altitude_m=...)`, 0-3000 m): PC-010..014, linear between rows (99.97 / 96.65 / 94.98 / 93.31 / 89.97 °C at 0 / 1000 / 1500 / 2000 / 3000 m, the L-SRC derived values), flag `ALTITUDE_USER_SUPPLIED`. Outside the range: ValueError, no extrapolation.
- Pressure process (medium `WATER_PRESSURIZED`, PROC-000027): the saturation temperature of the bracket 108.4 / 115.2 / 121.0 °C (5 / 10 / 15 psig, PC-002, L-SRC proposal for SD-006), or a stated gauge pressure through the PC-030..034 table (0 to 15.552 psig). The registry's SD-006 bath (110 / 118 / 121) is cut to the same triple for the boundary. Altitude is not applied to pressure processes (flag `ALTITUDE_NOT_APPLIED_TO_PRESSURE_PROCESS`).
- Never lifted: no drying model exists, flag `CAP_NOT_LIFTED_NO_DRYING_MODEL`; the cap is an upper bound on temperature, not a validated model, flag `CAP_IS_UPPER_BOUND_NOT_VALIDATED`.
- Source status of every number: not human verified. The L-SRC lane opened the NIST saturation rows (19.736 psia 108.45 °C; 24.784 psia 115.31; 29.661 psia 120.92; 30.248 psia 121.54) and derived the altitude row. **This lane did not open NIST or any other source.** No Antoine or Clausius-Clapeyron constant is used (none is sourced here).

### 3.2 Which matrices are capped (explicit list, `registry/matrix_moisture_regime_v1.csv`)

| regime | classes | treatment |
|---|---|---|
| MOIST | VEGETABLE, FRUIT, MEAT, SEAFOOD, EGG, DAIRY, BEVERAGE | capped |
| MIXED_AMBIGUOUS | LEGUME, CEREAL, CONDIMENT, HERB_SPICE | capped, flag `MATRIX_AMBIGUOUS_MOIST_ASSUMED` |
| (no class: matrix unknown, the usual case) | UNKNOWN | capped, flag `MATRIX_UNKNOWN_MOIST_ASSUMED` (the layer already assumes high-moisture k and alpha for every matrix) |
| DRY_LOW_MOISTURE | NUT_SEED, SWEETENER, FAT_OIL | NOT capped, flags `MATRIX_DRY_CLASS_UNCAPPED`, `DRY_MATRIX_CONDUCTION_PROPERTIES_NOT_IN_REGISTRY` |

Every ING food group present in the ING ledger is classified (tested). The classification is an AI draft from recall (`SOURCE_UNVERIFIED_AGENT_RECALLED`); the ambiguous classes are capped because an uncapped moist piece is the 100-fold error.

### 3.3 Surface state (qualitative only)
Per bracket `surface_state`: `SURFACE_WET_AT_TBOIL` while the cap binds (medium hotter than T_cap) and the capped model's core is more than 1 °C (PC-040, an engineering tolerance) below T_cap; then `SURFACE_DRYING_POSSIBLE` (the piece no longer absorbs sensible heat, so further flux can only evaporate water or heat a dried surface). Other states: `SURFACE_IMMERSED_WET` (water-like immersion, cap not binding), `SURFACE_WET_BELOW_TBOIL_CAP_NOT_BINDING`, `SURFACE_STATE_NOT_APPLICABLE_DRY_MATRIX`, `SURFACE_STATE_UNKNOWN_CORE_NOT_COMPUTED` (no size or no h: never defaulted). Drying can start earlier than the criterion; the onset time is not modelled, so WET_AT_TBOIL means "not yet forced to dry by the energy balance". No crust temperature, no crust-onset time (tested: no key or flag mentions crust).

### 3.4 Doses
Per bracket: `core_cook_value_min` (core trajectory, now with capped boundary; the lower bound for quality loss), `quality_cook_value_min` (volume-average trajectory, REV-A: quality doses use the volume average), `volume_avg_end_c`, `surface_cook_value_min` for immersion media at the capped temperature (flag `SURFACE_DOSE_AT_TBOIL_WET_PERIOD_ONLY`: after crust onset the surface dose is higher, not modelled). Cook value convention unchanged (T_ref 100 °C, z 33 °C). Non-heat F0 (canning, at the medium temperature, flagged `F0_AT_MEDIUM_TEMPERATURE_NOT_COLD_SPOT`) and drying (wet-bulb based) do not use the slab boundary and are unchanged; COOLING uses a cold medium and a start at most 95 °C, so it is unchanged (counts identical, section 5.4).

### 3.5 Performance
`slab_two_stage` is exact in time: A is similar to a symmetric matrix (trapezoid weights), `eigh` gives the modes, any stage length costs one eigen-decomposition (cached per slab). The peak of the last stage is a 400-point geometric grid plus golden-section refinement. Eigenvalues of the series solution are cached per Bi, which also makes the whole heat L2 about 33 times faster (2,820 events: 57.8 s before, 1.75 s now, single process).

## 4. Tests

- New: `tests/unit/test_s176_phys_cap.py`, 153 tests: the invariant (6 media x 4 sizes x 5 durations, core and volume average at most T_boil + 0.5 °C, whole trajectory under the cap); REV-A numbers reproduced (163.73 / 601.88 become 91.87 / 6.26; deep fry 163.4 / 101.7 become 94.0 / 1.2); water bath, steam, sous-vide and scald unchanged against the old version (7 processes); pressure cooking above 100 °C only with a pressure process, stated psig, out-of-range refused; dry classes uncapped and the class list explicit; every ING group classified; altitude lowers the cap and the default is flagged; surface state qualitative; quality dose equals the volume-average trajectory dose; volume-average series against a 400-node finite-difference reference; limits and continuity at Fo 0.02; exact scheme against Crank-Nicolson; non-heat RESTING capped, after a water bath unchanged, after a dry class uncapped, after pressure cooking clipped to the atmospheric boil on release; performance cases under 1 s; the scenario tool end to end (counts only, no overwrite).
- Existing: `pytest -q tests/unit/test_s172_*.py tests/unit/test_nonheat_*.py tests/unit/test_s171_demo_context.py` with the new file: **252 passed** (1 deselected by the repo config). Nine more simulation-related modules (step23a, step26b, step26c, s166, s171 aa pilot): 174 passed. `test_s168_lot_introduction_reason.py` and `test_step26g_recipe_adapter.py` cannot be collected in `.venv312` (`hypothesis` missing), and `tests/unit/test_calibration.py` needs `sklearn`: both pre-existing, unrelated.
- **Existing tests updated: none.** No existing test encoded the bug: `bath_c` still reports the medium temperature, the capped fields are new, and the non-heat tests do not assert the `NO_EVAPORATION_CAP_AT_100C` flag (it is now emitted only by the superseded `enabled=False` model). The existing finite-difference tests call `slab_two_stage` without `caps`, so they exercise the uncapped driver, which is correct.

## 5. Equality and regression proofs

1. **Cap disabled equals 0.1.0, byte for byte:** `ScenarioLayer.load(policy=CapPolicy(enabled=False))` over all 2,820 L1 heat events of the 1,000-recipe sample equals the output of the pre-change code (saved before editing), `sha256` of the sorted-JSON stream identical (58be43c79ae2b1fb).
2. **Exact two-stage scheme against the old Crank-Nicolson, synthetic grid** (960 cases, L 1.5-20 mm, h 15-1500, stages 3-90 + 5-120 min): max difference centre 0.0058 °C, last-stage peak 0.0057 °C. The surface node differs up to 1.11 °C in the stiffest case (L 2 cm, h 1500, Bi 60, Fo 0.063), where the **old stepper is the one that is wrong**: analytic series 174.02, exact 174.03, Crank-Nicolson 172.92 (test `..._surface_agrees_with_the_analytic_series_...`).
3. **Exact scheme against the stored 0.1.0 RESTING outputs on real data:** all 642 computed RESTING events (3 brackets each) of WIKIBOOKS, GUTENBERG_SEGMENT and FOODCOM, the uncapped exact scheme against the stored Crank-Nicolson records (including the very long ones): max difference core end of heat 0.004 °C, peak 0.002, core end 0.002, surface 0.002, carry-over rise 0.005 (outputs are rounded to 0.001).
4. **Non-heat counts:** for all four families the v02 non-heat counts equal the S176 counts for status, transition, missing reasons, bracket-order checks, cooling-target counts, errors, and every flag and basis of every family except RESTING; the RESTING differences are exactly the new cap flags and the `t_cap_c` basis (`NO_EVAPORATION_CAP_AT_100C` replaced).
5. **L1 unchanged:** the regenerated L1 censuses equal the S173 / S174 reports on every counted field (FOODCOM 522,517 recipes, 1,503,261 heat events, 56,214 driver-ready, 2,102,847 contract bindings; GUTENBERG 182,049; WIKIBOOKS 11,433; TASTESET 0). Only `sample_size_requested` differs (600,000 against 612,782).
6. **Heat L2 coverage:** status, transition, core-known and basis counts equal S174 (FOODCOM) and S173 (GUTENBERG, WIKIBOOKS, TASTESET) except the new `t_cap_c` basis and the cap flags; one count moves by design, `typical_core_reaches_70` (section 6.2).

## 6. Before / after (counts only; before = the SUPERSEDED 0.1.0 model run on the same regenerated L1 records in the same pass)

### 6.1 Share of heat events whose core exceeds 100 °C (any of the three brackets)
Columns: heat events; events with a computed core (TYPICAL bracket); before; after; moist-class events above the cap after; dry-class events with a computed core.

| family | heat events | core computed | before (all heat events / computed) | after (all heat events / computed) | moist class above cap, after | dry-class computed |
|---|---|---|---|---|---|---|
| FOODCOM | 1,503,261 | 55,146 (3.7 %) | 39,825 (2.65 % / 72.2 %) | 1,043 (0.07 % / 1.9 %) | 0 | 1,199 |
| GUTENBERG_SEGMENT | 182,049 | 13,186 (7.2 %) | 7,111 (3.91 % / 53.9 %) | 194 (0.11 % / 1.5 %) | 0 | 357 |
| WIKIBOOKS | 11,433 | 451 (3.9 %) | 262 (2.29 % / 58.1 %) | 5 (0.04 % / 1.1 %) | 0 | 8 |
| TASTESET | 0 | 0 | 0 | 0 | 0 | 0 |
| total | 1,696,743 | 68,783 | 47,198 (2.78 % / 68.6 %) | 1,242 (0.07 % / 1.8 %) | 0 | 1,564 |

Per bracket, FOODCOM, core above 100 °C (of 55,146): GENTLE 15,851 (28.7 %) to 241 (0.4 %); TYPICAL 38,603 (70.0 %) to 935 (1.7 %); INTENSE 39,825 (72.2 %) to 1,043 (1.9 %). The remaining "after" events are all dry-class (NUT_SEED, SWEETENER, FAT_OIL), uncapped on purpose (their conduction properties are still the high-moisture ones: flagged). Pressure events: FOODCOM has 9 pressure-cook events, none with a size class, so the pressure path is exercised by unit tests only.

### 6.2 Other counts that move
`typical_core_reaches_70` (events with a computed core, TYPICAL): not reaching 70 °C rises from 713 to 2,678 of 55,146 in FOODCOM (1.3 % to 4.9 %), 11 to 38 in GUTENBERG, 5 to 14 in WIKIBOOKS: with the boundary held at 100 °C the pieces heat more slowly than with a 170-220 °C boundary. Surface states, TYPICAL, FOODCOM: DRYING_POSSIBLE 22,155; WET_AT_TBOIL 16,650; IMMERSED_WET 204,923; WET_BELOW_TBOIL_CAP_NOT_BINDING 1,881; dry-class not applicable 27,409; unknown (core not computed) 394,616.

### 6.3 Dose distribution, `core_cook_value_min` (equivalent minutes, T_ref 100 °C, z 33 °C), moist-class events with a computed core, TYPICAL bracket

| family (n) | version | p10 | p50 | p90 | p99 | max |
|---|---|---|---|---|---|---|
| FOODCOM (53,947) | before | 4.79 | 341.0 | 5,690 | 37,422 | 9,297,094 |
| | after | 0.69 | 9.17 | 25.1 | 116.0 | 2,634 |
| | after, `quality_cook_value_min` (volume average) | 0.96 | 9.38 | 25.7 | 116.2 | 2,634 |
| GUTENBERG_SEGMENT (12,829) | before | 9.35 | 117.2 | 5,370 | 7,358 | 3,551,507 |
| | after | 3.35 | 12.06 | 24.4 | 117.2 | 2,810 |
| | after, quality | 3.61 | 12.19 | 24.4 | 117.2 | 2,810 |
| WIKIBOOKS (443) | before | 3.57 | 58.3 | 5,042 | 26,780 | 89,328 |
| | after | 0.69 | 8.08 | 27.7 | 117.0 | 117.2 |
| | after, quality | 1.06 | 8.37 | 28.0 | 117.0 | 117.2 |

The same quantiles for GENTLE and INTENSE, the dry-class split and the surface cook value of immersion media are in the `before_after.dose_quantiles` block of each `scenario_L2_<FAMILY>_full_S176_v02.json`. Example, FOODCOM INTENSE p50: 13,970 before, 34.7 after. Dry-class events are identical before and after (FOODCOM p50 195.0). Surface cook value of immersion media (FOODCOM max): 558,595 before (oil immersion at the oil temperature), 480 after.

### 6.4 Non-heat RESTING (events with a computed result; core peak above 100 °C, any bracket)
| family | RESTING computed | before | after | moist class above 100 after | note |
|---|---|---|---|---|---|
| FOODCOM | 552 (535 moist, 17 dry) | 382 | 8 (all dry class) | 0 | TYPICAL moist core peak p50 169.4 to 99.3, max 231.4 to 100.0 |
| GUTENBERG_SEGMENT | 87 | 31 | 2 (dry class) | 0 | |
| WIKIBOOKS | 3 | 3 | 0 | 0 | |
| TASTESET | 0 | 0 | 0 | 0 | no step lists |

RESTING coverage is unchanged (same computed counts). Rest after pressure cooking can show a core end of heat above 100 °C (pressure process) but the core on release is clipped to the atmospheric boil (flag `PRESSURE_RELEASE_PROFILE_CLIPPED_TO_ATMOSPHERIC_TBOIL`).

## 7. Runs on manjot-server (nice -n 10, seed 20261104, at most 32 workers: 24 + 8; BBC not touched, D-003; single-thread BLAS in the new runs)

The first versions of the heat L2 and non-heat L2 reports for GUTENBERG_SEGMENT, WIKIBOOKS, TASTESET and the 1,000 sample were produced before the dry-class split was added to the comparison block; I deleted those first outputs (my own scratch, not a prior deliverable; 8 workers, under two minutes in total) and re-ran them with the final tools. All rows below are from final code: every `code_sha256` entry in the v02 reports matches the files listed in section 2. `code_unchanged_during_run` is False for the two long L1 reports (FOODCOM, GUTENBERG) because `code_provenance()` hashes all of `src/`, which other lanes and this lane edited during the runs; the L1 module hashes are unchanged and the counts equal S173/S174 (section 5.5).

```
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S176-PHYS-001,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,8,"tools/binding_census.py --seed 20261104 --sample-size 1000 --records-dir data/derived/physical_L1_1000_S176v02",reports/step26/binding_census_L1_1000_S176_v02.json,03e36ba36a8bf5fbc7e8de59d1716ac3294a42437e42c77c6c5943d5b9c6591a,2026-11-08T15:46:53Z,2026-11-08T15:50:58Z,DONE,"2,820 heat events, driver_ready 89, bindings 3,885 (equal to the L-NH baseline run); baseline PASS"
RUN-S176-PHYS-002,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,FOODCOM,24,"tools/binding_census.py --seed 20261104 --sample-size 600000 --families FOODCOM --records-dir data/derived/physical_L1_full_S176v02/FOODCOM",reports/step26/binding_census_L1_FOODCOM_full_S176_v02.json,3cdef451c0f88d51fbc81a93778efacdd594afe9f07844bb86e666137ef6c366,2026-11-08T15:52:15Z,2026-11-08T16:26:12Z,DONE,"522,517 recipes; 1,503,261 heat events; counts equal S174 on every counted field; FOODCOM heat L1 records regenerated (1.5 GB incl. the other families); baseline PASS; code_unchanged_during_run False (src edited by other lanes)"
RUN-S176-PHYS-003,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,GUTENBERG_SEGMENT,8,"tools/binding_census.py --seed 20261104 --sample-size 600000 --families GUTENBERG_SEGMENT --records-dir data/derived/physical_L1_full_S176v02/GUTENBERG_SEGMENT",reports/step26/binding_census_L1_GUTENBERG_SEGMENT_full_S176_v02.json,8a1f74bf35a555bc86ade973bc00283f824466bd9ae67d0299651d202077cd3b,2026-11-08T15:53:25Z,2026-11-08T16:05:55Z,DONE,"73,955 recipes; 182,049 heat events; equal to S173; code_unchanged_during_run False (src edited during the run)"
RUN-S176-PHYS-004,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,WIKIBOOKS,8,"tools/binding_census.py --seed 20261104 --sample-size 600000 --families WIKIBOOKS --records-dir data/derived/physical_L1_full_S176v02/WIKIBOOKS",reports/step26/binding_census_L1_WIKIBOOKS_full_S176_v02.json,774b7ac5a2c8493f250d9d8b07cfac3aa76fb12279f8d623246d8b52dcb255c0,2026-11-08T15:52:15Z,2026-11-08T15:53:18Z,DONE,"3,676 recipes; 11,433 heat events; equal to S173"
RUN-S176-PHYS-005,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,TASTESET,8,"tools/binding_census.py --seed 20261104 --sample-size 600000 --families TASTESET --records-dir data/derived/physical_L1_full_S176v02/TASTESET",reports/step26/binding_census_L1_TASTESET_full_S176_v02.json,cd79d64245ecba31d66b4a27bed57dfa65a9e5171efd4e05cbc72c4b00b91b53,2026-11-08T15:53:18Z,2026-11-08T15:53:25Z,DONE,"700 recipes; 0 heat events (no step lists); equal to S173"
RUN-S176-PHYS-006,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,4,"tools/scenario_layer_run.py --l1 data/derived/physical_L1_1000_S176v02 --l2 data/derived/physical_L2_1000_S176v02 --workers 4 --compare-uncapped",reports/step26/scenario_L2_1000_S176_v02.json,ce04cd2044191fb79603aea1ef91e8ce0b16879309638d0b87393000fe9e8968,2026-11-08T16:18:03Z,2026-11-08T16:18:05Z,DONE,"2,820 heat events; 1,333 SCENARIO_COMPUTED; sample before any full run"
RUN-S176-PHYS-007,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,FOODCOM,24,"tools/scenario_layer_run.py --l1 data/derived/physical_L1_full_S176v02/FOODCOM --l2 data/derived/physical_L2_full_S176v02/FOODCOM --workers 24 --compare-uncapped",reports/step26/scenario_L2_FOODCOM_full_S176_v02.json,75d33a6793a28b50ffe3effbc3cb5d9227c8f5b523ac0625df3e291828ef308c,2026-11-08T16:26:26Z,2026-11-08T16:27:44Z,DONE,"1,503,261 heat events; 667,634 SCENARIO_COMPUTED; 55,146 with a core; 78 s; records manifest 0d77c189fc445cae... (data/derived/physical_L2_full_S176v02, 2.4 GB for the three families)"
RUN-S176-PHYS-008,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,GUTENBERG_SEGMENT,8,"tools/scenario_layer_run.py --l1 data/derived/physical_L1_full_S176v02/GUTENBERG_SEGMENT --l2 data/derived/physical_L2_full_S176v02/GUTENBERG_SEGMENT --workers 8 --compare-uncapped",reports/step26/scenario_L2_GUTENBERG_SEGMENT_full_S176_v02.json,0b9cedd7e7060e199ef0805c92db72957027f647197356082c301e40a197a65d,2026-11-08T16:14:07Z,2026-11-08T16:14:57Z,DONE,"182,049 heat events; 120,951 SCENARIO_COMPUTED; 13,186 with a core"
RUN-S176-PHYS-009,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,WIKIBOOKS,8,"tools/scenario_layer_run.py --l1 data/derived/physical_L1_full_S176v02/WIKIBOOKS --l2 data/derived/physical_L2_full_S176v02/WIKIBOOKS --workers 8 --compare-uncapped",reports/step26/scenario_L2_WIKIBOOKS_full_S176_v02.json,499a34cca680f15a105307ffd0ea95e319b6437110de576e70f92864e8f666c4,2026-11-08T16:14:00Z,2026-11-08T16:14:03Z,DONE,"11,433 heat events; 4,871 SCENARIO_COMPUTED; 451 with a core"
RUN-S176-PHYS-010,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,TASTESET,8,"tools/scenario_layer_run.py --l1 data/derived/physical_L1_full_S176v02/TASTESET --l2 data/derived/physical_L2_full_S176v02/TASTESET --workers 8 --compare-uncapped",reports/step26/scenario_L2_TASTESET_full_S176_v02.json,fc19f3ed42bfc5e57363f41561eafea1e1e4163cd97a6e8352110c6abe664e24,2026-11-08T16:14:04Z,2026-11-08T16:14:05Z,DONE,"0 heat events (no step lists)"
RUN-S176-PHYS-011,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,4,"tools/nonheat_layer_run.py --l2-only --seed 20261104 --workers 4 --compare-uncapped --l1-records-dir data/derived/physical_NH_L1_1000_S176 --l2-records-dir data/derived/physical_NH_L2_1000_S176v02",reports/step26/nonheat_L2_1000_S176_v02.json,b2c1e98f16eef7a0d1d49e883428cc9556403ad0500876761a411afabb95a4f6,2026-11-08T16:18:09Z,2026-11-08T16:18:10Z,DONE,"4,927 non-heat events; counts equal to nonheat_L2_1000_S176 (no computed RESTING in the sample)"
RUN-S176-PHYS-012,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,FOODCOM,8,"tools/nonheat_layer_run.py --l2-only --seed 20261104 --workers 8 --compare-uncapped --families FOODCOM --l1-records-dir data/derived/physical_NH_L1_FOODCOM_full_S176 --l2-records-dir data/derived/physical_NH_L2_FOODCOM_full_S176v02",reports/step26/nonheat_L2_FOODCOM_full_S176_v02.json,1883ad6285642e2f4f58c28cb1967ff382cb6ef04cf6ec26fe27614587148740,2026-11-08T16:16:34Z,2026-11-08T16:18:09Z,DONE,"2,711,429 non-heat events over 522,517 recipes; 552 RESTING computed; L2 94 s (23.9 min before the step-rule fix)"
RUN-S176-PHYS-013,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,GUTENBERG_SEGMENT,8,"tools/nonheat_layer_run.py --l2-only --seed 20261104 --workers 8 --compare-uncapped --families GUTENBERG_SEGMENT --l1-records-dir data/derived/physical_NH_L1_GUTENBERG_SEGMENT_full_S176 --l2-records-dir data/derived/physical_NH_L2_GUTENBERG_SEGMENT_full_S176v02",reports/step26/nonheat_L2_GUTENBERG_SEGMENT_full_S176_v02.json,835089e9783c9a92b5458850e2b2173b2da6ebc68773a5be6f82368ea564aabf,2026-11-08T16:18:46Z,2026-11-08T16:18:54Z,DONE,"297,421 non-heat events; 87 RESTING computed; L2 8 s (11.3 min before)"
RUN-S176-PHYS-014,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,WIKIBOOKS,8,"tools/nonheat_layer_run.py --l2-only --seed 20261104 --workers 8 --compare-uncapped --families WIKIBOOKS --l1-records-dir data/derived/physical_NH_L1_WIKIBOOKS_full_S176 --l2-records-dir data/derived/physical_NH_L2_WIKIBOOKS_full_S176v02",reports/step26/nonheat_L2_WIKIBOOKS_full_S176_v02.json,961f53f996f2044875a7ce8bbfa22edbd07b77bdc678a54125ab75084aa55fcc,2026-11-08T16:18:38Z,2026-11-08T16:18:39Z,DONE,"18,900 non-heat events; 3 RESTING computed"
RUN-S176-PHYS-015,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",bbf5ee6+uncommitted,TASTESET,8,"tools/nonheat_layer_run.py --l2-only --seed 20261104 --workers 8 --compare-uncapped --families TASTESET --l1-records-dir data/derived/physical_NH_L1_TASTESET_full_S176 --l2-records-dir data/derived/physical_NH_L2_TASTESET_full_S176v02",reports/step26/nonheat_L2_TASTESET_full_S176_v02.json,e0122533a6bf5d65c570021ccbaa1d975dd93080f71ce01e0438151b571c043e,2026-11-08T16:18:42Z,2026-11-08T16:18:43Z,DONE,"0 non-heat events (no step lists)"
```

Disk used by this lane: 1.5 GB (L1 full) + 2.4 GB (heat L2 full) + 1.9 GB (non-heat L2 full) + small samples, about 5.8 GB, all under `data/derived/` (git-ignored through the main repo exclude, like L-NH). The old L2 directories are kept; each non-heat one received a one-line `SUPERSEDED_S176_L-PHYS.txt` marker (the `*.jsonl` manifests are unchanged).

## 8. SUPERSEDED outputs (kept, never deleted)

Superseded fields: for every oven, oil, pan, air-fryer and pressure heat event with a computed core: `core_end_c`, `core_minutes_above_70`, `core_cook_value_min`, `surface_cook_value_min` (immersion media at the oil temperature) and `typical_core_reaches_70`; for RESTING: `core_end_of_heat_c`, `core_peak_c`, `carryover_rise_c`, `core_end_c`, `surface_end_c`. Water-bath, steam and sous-vide events are numerically unchanged (proved), COOLING, SEPARATION, FERMENT_LEAVEN, PRESERVATION, MECHANICAL_*, STORAGE are unchanged. Dry-class events are unchanged by design. Coverage and basis counts of every report below remain valid.

| superseded output | where | replaced by |
|---|---|---|
| `reports/step26/scenario_L2_1000_S172.json` (0.1.0) | repo | `scenario_L2_1000_S176_v02.json` |
| `reports/step26/scenario_L2_FOODCOM_full_S174.json` | repo; records on vinayak `~/Kush/cs_runs/physical_L2_full_S174/FOODCOM` | `scenario_L2_FOODCOM_full_S176_v02.json` |
| `reports/step26/scenario_L2_GUTENBERG_SEGMENT_full_S173.json`, `scenario_L2_WIKIBOOKS_full_S173.json`, `scenario_L2_TASTESET_full_S173.json` | repo; records on the Mac `data/derived/physical_L2_full_S173/*` | the three `_full_S176_v02.json` files |
| `reports/step26/scenario_L2_A1_full_S173.json` (BBC) | repo; records on the Mac | **Mac re-run, section 9** |
| `reports/step26/nonheat_L2_1000_S176.json`, `nonheat_L2_{FOODCOM,GUTENBERG_SEGMENT,WIKIBOOKS,TASTESET}_full_S176.json` (RESTING fields only) | repo; records `data/derived/physical_NH_L2_*_S176` on manjot (marker file added) | the five `nonheat_L2_*_S176_v02.json` files |
| any feature, screen or slide that read these core, dose or RESTING fields (SSOT v16 §284.3: none until the invariant passes) | | the invariant now passes on every non-BBC record |

Not superseded: the three L1 reports `binding_census_L1_*` (the `_S176_v02` L1 reports repeat them with equal counts and regenerate the FOODCOM heat L1 records on manjot). `src/culinarystate/decision/demo_context.py` (L-ROUTER) builds `ScenarioLayer.load()`, so it now serves the capped values (`typical_core_end_c`); its tests pass, the file was not touched.

## 9. BBC re-run for the Mac (D-003: BBC data is not on this server)

L1 code and L1 records are unchanged, so existing BBC L1 records stay valid. On the Mac, from a checkout that has this lane's files (`phase_change.py`, both registries, the three modified modules, both tools):

```
# heat L2 over the existing BBC L1 records (family A1_BBC_GOOD_FOOD), with the before/after block
python tools/scenario_layer_run.py --l1 data/derived/physical_L1_full_S173/A1_BBC_GOOD_FOOD \
    --l2 data/derived/physical_L2_full_S176v02/A1_BBC_GOOD_FOOD \
    --out reports/step26/scenario_L2_A1_full_S176_v02.json --workers 2 --compare-uncapped
# non-heat L1 + L2 for BBC (never run yet: L-NH ran the four non-BBC families only)
python tools/nonheat_layer_run.py --seed 20261104 --sample-size 612782 --workers 2 --families A1_BBC_GOOD_FOOD --compare-uncapped \
    --l1-out reports/step26/nonheat_L1_A1_full_S176.json --l2-out reports/step26/nonheat_L2_A1_full_S176_v02.json \
    --l1-records-dir data/derived/physical_NH_L1_A1_full_S176 --l2-records-dir data/derived/physical_NH_L2_A1_full_S176v02
```

If the BBC L1 directory is missing, regenerate it first with `tools/binding_census.py --families A1_BBC_GOOD_FOOD --records-dir ... --sample-size 612782`; its counts must equal `binding_census_L1_A1_full_S173.json`. Expected pattern: moist-class events above the cap = 0, `events_violating_cap_any_bracket` absent, coverage counts equal to `scenario_L2_A1_full_S173.json`. Then add the Mac rows to `registry/compute_runs_v1.csv` and mark `scenario_L2_A1_full_S173.json` SUPERSEDED.

## 10. Open questions and limits (for a human; nothing here is decided)

1. **Cap boundary form.** The capped boundary is a Robin condition with the same h and T = T_boil, as specified. It guarantees the temperature invariant but is not a flux-limited bound and not a Dirichlet bound (surface held at T_boil with h to infinity), which would heat faster. The effect shows in section 6.2 (more pieces fail to reach 70 °C). REV-A N2 item 2 (flux-limited lower bound against a humidity bracket) is not implemented; the SSOT marks it optional. A physics owner should decide whether to add the Dirichlet bracket as the other end.
2. **Class list** (section 3.2) is an AI draft from recall. Dry-class events are about 2 % of core-computed events and stay uncapped with high-moisture k and alpha (flagged `DRY_MATRIX_CONDUCTION_PROPERTIES_NOT_IN_REGISTRY`); they are the only events still above 100 °C. Ambiguous classes (CEREAL, LEGUME, CONDIMENT, HERB_SPICE) are capped; a dry-roasted spice or flour would be under-heated by the cap.
3. **Surface-state criterion** (core within 1 °C of the cap) and the 1 °C tolerance are an AI proposal. It reports a late bound; earlier onset of drying is possible and not modelled. No crust temperature or onset time exists (no sourced model). Maillard and crust gates may read the flag only qualitatively.
4. **Sources.** The saturation and altitude rows are from the L-SRC review (AI_DRAFTED, VERIFIED_OPENED by that lane, not human verified); this lane opened no source. Pressure at altitude is not modelled. SD-006 itself (110 / 118 / 121 °C) is unchanged in `registry/scenario_defaults_v1.csv`: the proposed 108 / 115 / 121 is applied to the boundary through PC-002 only. Adopting it in SD-006 (and the altitude rows as scenario options) is a registry decision.
5. **Pressure path on real data** is untested: FOODCOM has 9 pressure-cook events and none has a size class.
6. **Old-model scheme error.** The Crank-Nicolson stepper of 0.1.0 RESTING was up to 1.1 °C low at the surface node in stiff cases; all RESTING numbers in the superseded files carry that small error besides the missing cap. The "before" RESTING numbers in the comparison block use the exact scheme (the stored 0.1.0 files agree to 0.005 °C where checked).
7. Quality doses at the volume average are computed for the slab only; cube, cylinder and sphere shapes (REV-A N3, SSOT §284.5) are not implemented.
8. **Environment.** `.venv312` has no `hypothesis`, `sklearn`: three test modules cannot be collected here (pre-existing).
9. Heat L2 records are in `data/derived/physical_L2_full_S176v02/<FAMILY>`; the heat L1 records (including FOODCOM) are in `data/derived/physical_L1_full_S176v02/<FAMILY>`. Per-event files hold recipe and event ids but no recipe text; reports are counts only.

## 11. Reproduce

```
cd ~/kush_work/culinarystate/.orch
~/kush_work/culinarystate/.venv312/bin/python -m pytest -q tests/unit/test_s176_phys_cap.py tests/unit/test_s172_*.py tests/unit/test_nonheat_*.py
nice -n 10 ~/kush_work/culinarystate/.venv312/bin/python tools/scenario_layer_run.py --l1 data/derived/physical_L1_full_S176v02/FOODCOM \
   --l2 <new dir under data/derived> --out reports/step26/<new>.json --workers 24 --compare-uncapped
nice -n 10 ~/kush_work/culinarystate/.venv312/bin/python tools/nonheat_layer_run.py --l2-only --seed 20261104 --workers 8 --compare-uncapped \
   --families FOODCOM --l1-records-dir data/derived/physical_NH_L1_FOODCOM_full_S176 --l2-records-dir <new dir> --l2-out reports/step26/<new>.json
```
Options: `--altitude-m 2000` (optional, flagged), `--pressure-psig 15`, `--no-evaporation-cap` (reproduces the SUPERSEDED 0.1.0 model, regression only).
