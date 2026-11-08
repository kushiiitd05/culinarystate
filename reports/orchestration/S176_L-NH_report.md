# S176 lane L-NH: non-heat process families for the physical-state dataset (D-077 extension)

Status: DRAFT / AI_DRAFTED. Nothing here is a human signature, approval or gate. Built 2026-11-08 in worktree `~/kush_work/culinarystate/.orch` (branch `max/s176-orchestration`, base `07fc0d2`, uncommitted). No ledger, no existing module and no 23a engine file was edited (new files only). Under SSOT §141 no nutrient, compound, yield or safety number is produced. Every L2 output is a temperature, a time, a geometry value or a dimensionless transport fraction with transition status `physically_possible`, or an explicit UNKNOWN.

## 1. What was built

Layer 1 TEXT_STATED: only what the step text states, each value with its character span, missing = UNKNOWN with a reason code. Layer 2 SCENARIO: GENTLE / TYPICAL / INTENSE = low / mid / high brackets from a new defaults registry, labelled SCENARIO, MODEL_DERIVED, NON_CITABLE, ASSUMED_DEFAULT. Each record names its FORM candidate class (coverage-plan table) for 23a to map later.

| file | sha256 (first 16) |
|---|---|
| `registry/scenario_defaults_nonheat_v1.csv` | 047732f446633cf0 |
| `src/culinarystate/simulation/nonheat_binding.py` | 1453fe36b43200df |
| `src/culinarystate/simulation/nonheat_drivers.py` | 3af066b92f4cafc8 |
| `src/culinarystate/simulation/nonheat_scenario.py` | 4df2af113eda452d |
| `tools/nonheat_layer_run.py` | a74647a7a4d9a5a9 |
| `tests/unit/test_nonheat_binding.py` | fa43d95fff6ab1ec |
| `tests/unit/test_nonheat_drivers.py` | df4143ab74375306 |
| `tests/unit/test_nonheat_scenario.py` | b649a4fd2d01c559 |
| `tests/unit/test_nonheat_cli.py` | 8612d4a772e11d7d |

- `nonheat_binding.py`: L1 binder (reuses the heat `Binder` for the Rung A graph and the prior heat step, does not modify it), readiness (`missing_core`), census with workers and records.
- `nonheat_drivers.py`: new drivers only (finite-difference two-stage slab, thaw as reverse Plank, two-stage drying, F0, A/V). Slab series, Fickian uptake and Plank freezing from a0b669c (`physics_drivers.py`) are reused unchanged.
- `nonheat_scenario.py`: L2 per family and `count_row` for the counts-only summary.
- `tools/nonheat_layer_run.py`: both layers in one command, with the same corpus reader, seeded sample, protected-ledger check and counts-only reports as the heat tools.
- The registry has 40 rows (NH-001 ... NH-080). I opened no source for any row. Shared properties (k, alpha, cut half-thickness, ambient start, corpus durations) are read from the heat registry (SD ids) and the KGE quantiles (KGE ids), never copied.

## 2. Design

### 2.1 Families, inputs, drivers

| family | L1 inputs (span or UNKNOWN + reason) | L2 driver | FORM candidate class |
|---|---|---|---|
| COOLING: cool, chill (incl. refrigerate), freeze, defrost | duration; stated medium T (signed, F exact); stated food target ("to 40C"); environment class FRIDGE / FREEZER / ICE_BATH / COLD_WATER / ROOM / MICROWAVE (words stay classes); target and start state (POST_HEAT from graph or preceding step); cut-class size | cool / chill: slab-centre trajectory in a cold medium (core end T, minutes above 60 and 5 C as reporting thresholds, time to a stated target); freeze: Plank time; defrost: Plank thaw time | `TRANSIENT_CONDUCTION_COLD_BATH\|PLANK_FREEZING_THAW_REVERSE` |
| SEPARATION: drain, strain, rinse, squeeze, discard, skim, sift, separate, pick, pat-dry, degorge | removed phase (verb-defined, refined by "discard the liquid / solids"); liquid fate DISCARDED / RETAINED; rinse medium and T class; follows soak or brine | leaching hand-off code plus a liquid-removed fraction bracket for drain and strain | `LEACHING_COMPARTMENT_HANDOFF` |
| FERMENT_LEAVEN: soak, marinate, prove, ferment, germinate | duration (overnight, ranges, "up to"); medium BRINE / VINEGAR / CITRUS_JUICE / MARINADE_OTHER / WATER; salt and acid % when written; T class; size | soak / marinate: Fickian slab uptake fraction; prove / ferment / germinate: qualitative flags only (VOLUME_RISES, PH_FALLS) | `FICKIAN_SLAB_UPTAKE\|PH_STATE_FLAG` |
| PRESERVATION: dry, pickle, brine, pasteurise, sterilise, can | duration; stated T ("boiling water bath" = 100 C by PHYSICAL_DEFINITION, phrase as span); environment; medium; concentrations; size; equipment cue | dry: two-stage drying; pickle / brine: Fickian uptake; can / sterilise / pasteurise: F0 minutes (z 10 C, T_ref 121.1 C) where a T and t exist | `DRYING_CONSTANT_PLUS_FALLING_RATE\|F_VALUE_Z10_TREF121_1\|FICKIAN_SLAB_UPTAKE` |
| MECHANICAL_CUT: 22 verbs | cut class and disruption level (verb-defined); enzyme-system candidate (food word in the clause, flag only); time until next heat (lower bound; `NEXT_HEAT_NO_TIMED_STEP_BETWEEN`, never 0) | half-thickness, slab A/V (1/L), cube A/V (3/L), flags | `GEOMETRY_SIZE_CLASS_AND_ENZYME_ACTIVATION_FLAG` |
| MECHANICAL_MIX: stir, mix, beat, whisk, knead, blend ... | duration; tool; AERATED / EMULSIFIED / DEVELOPED (text cue, else verb capability) | qualitative flags only | `QUALITATIVE_STATE_FLAGS` |
| RESTING: rest | duration; environment; cover; prior heat step (LINEAGE or ORDER_ADJACENT, with its heat-layer L1 inputs); size | carry-over: finite-difference slab, heat stage then still air | `CARRYOVER_CONDUCTION_STILL_AIR` |
| STORAGE: store | stated T; environment; duration bound (months as 30 d with `unit_convention`); container | storage T bracket and the time bound only; kinetics `UNKNOWN_PENDING_PARAM`; transition `unsupported` | `ARRHENIUS_AT_STORAGE_T_PARAM_PENDING` |

### 2.2 Rules enforced and tested

- Every non-UNKNOWN input has a span, a basis (TEXT_STATED, TEXT_CUE, PROCESS_DEFINITION, PHYSICAL_DEFINITION, CUT_HISTORY, LINEAGE, ORDER_ADJACENT, LINEAGE_AND_STATED_DURATIONS) and a status (MEASURED, RANGE, BOUND_UPPER, BOUND_LOWER, QUALITATIVE). Every UNKNOWN has value None, no span and a reason. Audited over the 4,927 sample rows: 0 violations.
- An event reads only its own clause. A decimal point does not split a sentence (the heat layer's splitter does).
- Durations come from Rung A claims with spans:
  - "1 hour 30 minutes" is summed and "30 seconds to 1 minute" is a range.
  - A lower bound written "6&ndash;12 hours" or "4 or 5 hours" is recovered from the text.
  - "up to" and "at least" give bounds; "overnight" is a class, not a number.
- L2 never writes into L1: the record is copied on entry and L1 values stay in every bracket with basis `L1:<basis>`. A gap is filled only with an NH, SD or KGE id. A size is never invented, and UNKNOWN stays UNKNOWN.
- Noun and adjective surfaces (marinade, canned, can, cans, pickles, grates) get the cue `NON_VERB_SURFACE` and L2 status `UNSUPPORTED_NON_VERB_SURFACE`. "Sterilise the jars" is `UNSUPPORTED_TARGET_EQUIPMENT`. A microwave medium is `UNSUPPORTED_MEDIUM`.

### 2.3 Brackets

GENTLE / TYPICAL / INTENSE are low / mid / high of the process effect. Each parameter is read from its registry row in the direction that raises the effect. They are coherent extremes of ranges, not confidence intervals. RESTING brackets are ordered by heat dose as in the heat layer. The carry-over rise itself is not monotone in the bracket by physics, so it is reported but not order-checked.

## 3. Tests

Run with venv312 after the last code edit: `pytest -q tests/unit/test_nonheat_*.py` gives 66 passed (drivers 19, binding 19, scenario 24, CLI 4). The heat regression `pytest -q tests/unit/test_s172_*.py` gives 28 passed.

- **Drivers (analytic):**
  - Finite-difference slab against the eigenvalue series, four Bi regimes plus a cold-bath case.
  - Plank conduction limit (h to infinity) and convection limit (k to infinity), inverse and quadratic scaling, thaw as the mirror image.
  - Fickian uptake against the exact series at five Fourier numbers, the hand value 0.9313 at Dt/L^2 = 1, and the short-time law.
  - Drying linearity, continuity at the break, exponential falling rate and equilibrium limit.
  - F0 convention and A/V.
- **Binding:** the span / UNKNOWN invariant over a 14-text corpus touching all eight families, plus fridge classes, signed and Fahrenheit temperatures, duration forms, soak-discard chain, never-0 next-heat time, and prior-heat inputs equal to the heat binder's own.
- **Scenario:** registry rules, L1 untouched, stated values kept, gaps never labelled L1, UNKNOWN and size never invented, drivers equal the formulas with registry values, bracket order, JSON round-trip, no nutrient words in any output.
- **CLI:** end to end on synthetic records, with worker invariance and overwrite refusal.

## 4. Runs

Server `manjot-server`, shared and heavily loaded throughout (load average about 110 to 410 on 128 cores), so wall times are pessimistic. All runs: `nice -n 10`, at most 32 workers in total (sample 8 + chain 24), seed 20261104, protected-ledger baseline PASS before and after, no BBC (D-003). Each full run streams only its own family, so L1 wall includes the corpus read. Records are git-ignored and 4.5 GB in total: FOODCOM L1 2.4 GB and L2 1.7 GB, GUTENBERG 257 MB and 222 MB, WIKIBOOKS 17 MB and 13 MB, sample 4.5 MB and 3.2 MB.

### 4.1 Heat baseline proof
`tools/binding_census.py --seed 20261104 --sample-size 1000 --families FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET` was run before any L-NH code existed (18:28 IST) and again after. 29 of 29 non-provenance fields are identical (heat_events 2,820; driver_ready 89; contract_bindings 3,885; all per-input counts). No existing file was modified.

### 4.2 Combined over WIKIBOOKS + GUTENBERG_SEGMENT + FOODCOM

600,148 recipes with steps; 9,208,811 Rung A events, of which 3,027,750 are non-heat events in the eight families.

"any L1 value" counts verb-defined classes, so it is 100% for some families by construction. "any text-stated" is the honest coverage figure. "full L1 driver inputs" means every input the family's driver needs is bound from text alone. "L2 qual" means `QUALITATIVE_FLAGS_ONLY` or `CONDITIONS_ONLY_KINETICS_UNKNOWN`.

| family | events | any L1 value | any text-stated | full L1 driver inputs | L2 drivers computed | L2 qual | top UNKNOWN reasons (core inputs) |
|---|---:|---:|---:|---:|---:|---:|---|
| COOLING | 310,762 | 100% | 38.3% | 1.2% | 8.1% | 0 | no temperature stated 100%; no cut history (size) 90%; no duration 66% |
| SEPARATION | 325,389 | 100% | 8.1% | 60.1% | 41.3% | 58.7% | no fate cue 40% |
| FERMENT_LEAVEN | 58,613 | 93.9% | 71.8% | 1.6% | 4.1% | 8.4% | no cut history 84%; no duration 70% |
| PRESERVATION | 81,813 | 19.3% | 12.6% | 0.0% | 0.2% | 0 | no duration 98%; no temperature 94%; no cut history 80% |
| MECHANICAL_CUT | 656,204 | 100% | 16.9% | 43.2% | 43.2% | 31.5% | none (verb-defined) |
| MECHANICAL_MIX | 1,552,674 | 26.5% | 13.0% | 18.4% | 0 | 18.4% | no emulsified cue 99%; no developed cue 99%; no aerated cue 83% |
| RESTING | 16,898 | 74.4% | 46.8% | 2.4% | 3.8% | 0 | no cut history 87%; no duration 63%; no prior heat link 50% |
| STORAGE | 25,397 | 82.3% | 82.3% | 9.8% | 0 | 48.3% | no temperature 100%; no duration 85%; no environment 52% |

### 4.3 Per run

| run | recipes (with steps) | Rung A events | non-heat events | L1 wall | L2 wall | /usr/bin/time total, max RSS | start to end (UTC) |
|---|---:|---:|---:|---|---|---|---|
| sample 1,000 (8 workers) | 1,000 (997) | 15,326 | 4,927 | 2.5 min | 5 s | 2:38, 0.43 GB | 14:03:11 to 14:05:47 |
| TASTESET | 700 (0) | 0 | 0 | 4 s | 1 s | 0:08 | 14:03:11 to 14:03:17 |
| WIKIBOOKS | 3,676 (3,676) | 59,357 | 18,900 | 22 s | 11 s | 0:37, 0.39 GB | 14:03:20 to 14:03:54 |
| GUTENBERG_SEGMENT | 73,955 (73,778) | 934,494 | 297,421 | 5.1 min | 11.3 min | 16:37, 0.68 GB | 14:03:58 to 14:20:24 |
| FOODCOM | 522,517 (522,514) | 8,214,960 | 2,711,429 | 52.4 min | 23.9 min | 1:16:24, 2.47 GB | 14:20:39 to 15:36:53 |

Every run had 0 L1 exceptions and 0 L2 errors, and baseline PASS before and after.

FOODCOM (full), per family:

| family | events | any text-stated | full L1 inputs | L2 drivers | L2 qual | top UNKNOWN reasons |
|---|---:|---:|---:|---:|---:|---|
| COOLING | 297,413 | 39.6% | 1.2% | 7.9% | 0 | no temperature 100%; no size 90%; no duration 65% |
| SEPARATION | 269,657 | 9.2% | 59.4% | 42.1% | 57.9% | no fate cue 41% |
| FERMENT_LEAVEN | 50,942 | 74.6% | 1.7% | 3.9% | 7.5% | no size 85%; no duration 67% |
| PRESERVATION | 66,675 | 12.7% | 0.0% | 0.1% | 0 | no duration 97%; no temperature 96%; no environment 83% |
| MECHANICAL_CUT | 541,273 | 17.4% | 43.3% | 43.3% | 32.1% | none |
| MECHANICAL_MIX | 1,447,067 | 13.6% | 17.8% | 0 | 17.8% | no flag cue |
| RESTING | 14,232 | 52.2% | 2.8% | 3.9% | 0 | no size 86%; no duration 57%; no prior heat link 48% |
| STORAGE | 24,170 | 84.6% | 10.2% | 0 | 50.0% | no temperature 100%; no duration 85% |

GUTENBERG_SEGMENT (full), per family:

| family | events | any text-stated | full L1 inputs | L2 drivers | L2 qual |
|---|---:|---:|---:|---:|---:|
| COOLING | 11,785 | 6.0% | 1.9% | 11.6% | 0 |
| SEPARATION | 53,329 | 2.7% | 63.5% | 36.8% | 63.2% |
| FERMENT_LEAVEN | 7,100 | 52.4% | 0.3% | 5.6% | 15.0% |
| PRESERVATION | 14,653 | 12.4% | 0.0% | 0.3% | 0 |
| MECHANICAL_CUT | 110,806 | 14.2% | 43.2% | 43.2% | 28.3% |
| MECHANICAL_MIX | 96,148 | 4.3% | 27.5% | 0 | 27.5% |
| RESTING | 2,525 | 15.2% | 0.1% | 3.4% | 0 |
| STORAGE | 1,075 | 28.4% | 0.6% | 0 | 11.6% |

WIKIBOOKS (full), per family:

| family | events | any text-stated | full L1 inputs | L2 drivers | L2 qual |
|---|---:|---:|---:|---:|---:|
| COOLING | 1,564 | 35.7% | 0.2% | 6.6% | 0 |
| SEPARATION | 2,403 | 8.4% | 59.8% | 41.5% | 58.5% |
| FERMENT_LEAVEN | 571 | 69.4% | 3.9% | 3.3% | 10.2% |
| PRESERVATION | 485 | 16.3% | 0.0% | 0.2% | 0 |
| MECHANICAL_CUT | 4,125 | 20.0% | 43.5% | 43.5% | 34.6% |
| MECHANICAL_MIX | 9,459 | 11.0% | 15.5% | 0 | 15.5% |
| RESTING | 141 | 60.3% | 2.1% | 2.1% | 0 |
| STORAGE | 152 | 84.9% | 6.6% | 0 | 48.7% |

Sample (1,000 recipes), per family:

| family | events | any text-stated | full L1 inputs | L2 drivers | L2 qual |
|---|---:|---:|---:|---:|---:|
| COOLING | 505 | 35.6% | 1.4% | 6.9% | 0 |
| SEPARATION | 520 | 6.9% | 60.8% | 40.4% | 59.6% |
| FERMENT_LEAVEN | 96 | 81.2% | 1.0% | 1.0% | 7.3% |
| PRESERVATION | 131 | 9.9% | 0.0% | 0.0% | 0 |
| MECHANICAL_CUT | 1,060 | 16.2% | 40.8% | 40.8% | 34.3% |
| MECHANICAL_MIX | 2,555 | 14.0% | 18.9% | 0 | 18.9% |
| RESTING | 25 | 32.0% | 0.0% | 0.0% | 0 |
| STORAGE | 35 | 91.4% | 14.3% | 0 | 62.9% |

Bracket-order self-check (GENTLE <= TYPICAL <= INTENSE on each family's main output):
- FOODCOM: 2 violations in 21,370 COOLING `core_end_c`.
- GUTENBERG_SEGMENT: 1 violation in 1,148 COOLING `core_end_c`.
- All other computed outputs are in order. The violations are "cool" steps with a stated medium of about 40 C, warmer than the assumed ambient start. They are left in, not filtered.

Report sha256 (L1 / L2):

| run | L1 report | L2 report |
|---|---|---|
| sample | c0f947d8543ea04315ae09a5cf3a52a129aaf1bf5c79d51ed5ca136265876946 | dea868e5962dbbeeab012ded2383579a4ce328456e9352cff8d02e018f40fa18 |
| TASTESET | d913edc39ffbe22e0cefad646a90df18029fa4ce669c63d6990c15d4c04d07e1 | 3fb02ce3c72d1da12a30ec4edb0cb7f79b00dbffbbf9ccbd77da833e37a295d5 |
| WIKIBOOKS | deb79260ee9639bcf76d7d32297ccff69b8a3d877483962ead7c5a5c42a973ce | 52deaac4254e203fa74084836b01299e4c076b931c0a27f0fc6ece1686def2b7 |
| GUTENBERG_SEGMENT | e2980b384647e0e03595c62603922c51f1ee1139a161d54ec79a05cafd15759a | 6824a64b86752a750d93b76de21dac19f313db0e348c21af6b4b2574141b8252 |
| FOODCOM | 343ff502fa6b8a1f657100231bff1f39a5d4353b1abf5a6881459e8f426d5791 | 07b60a607e61a903797cef17a8faee2839c9f37da450a6be93721dc470844188 |

## 5. Findings and negative results

- TASTESET has no step lists (ingredient lines only): 700 recipes, 0 events, as in the heat census.
- L2 driver coverage is low wherever text rarely gives a size class or duration. COOLING, FERMENT_LEAVEN, RESTING and PRESERVATION compute for a few percent of events, and `half_thickness` (no cut verb upstream of the lot) is the first missing input. The heat layer has the same bottleneck (102 of 2,850 heat events). MECHANICAL_CUT (about 43% have a class with geometry) and SEPARATION compute for many events.
- PRESERVATION is mostly not preservation: many events are the lexicon's noun or adjective surfaces (`canned`, `can`, `pickles`) or `dry` as an adjective ("dry mustard", "too dry"). In FOODCOM, 18,064 of 50,942 FERMENT_LEAVEN events (35%) are the noun "marinade" (`NON_VERB_SURFACE`), plus 5,369 PRESERVATION surfaces and 1,739 `EQUIPMENT_LIKELY` ("sterilise the jars").
- Rung A artefacts the layer only counts:
  - "process" (canning) mapped to blend (cue `BLEND_VERB_PROCESS_WITH_CANNING_CUE`, 732 in FOODCOM).
  - `crack` ("hard crack stage") and `grates` (grill grates).
  - Generic `cut` (L2 UNKNOWN).
  - HTML entities in ranges (repaired for durations only).
  - A duration attached to the preceding verb ("mince the garlic and let stand 10 minutes"; cue `HOLD_TIME_ATTACHED_TO_CUT`, used only as a lower bound).
- Carry-over cores can exceed 100 C (no evaporation cap), inherited from the heat layer's conduction model; flagged `NO_EVAPORATION_CAP_AT_100C`.
- **Performance trap, not fixed:** one FOODCOM L2 part file stalled the pool for about 24 minutes. A RESTING event whose prior heat lasts 10,080 to 20,160 minutes on a 0.5 to 1.5 mm piece needs about 1.3e8 finite-difference steps at the fixed Fourier step 0.004. Results are correct, only slow. I left it so every run comes from one code state (decision 8).
- `code_unchanged_during_run` is False for the sample, GUTENBERG and FOODCOM L1 reports. The shared `code_provenance()` hashes all of `src/`, and other lanes edited tracked files under `src/` (decision/*, mechanism/router_*, lotstate) during the runs. I checked that every L-NH file, the heat modules and both registries match the recorded hashes in all five L1 reports.
- ORDER_ADJACENT prior-heat links (preceding physical step is a heat step in the same or previous recipe step, no lot link) are weaker than LINEAGE. They are marked in the L1 `basis` and in `bases.prior_heat_link`. In FOODCOM: COOLING 161,446 LINEAGE vs 16,226 ORDER_ADJACENT; RESTING 6,504 vs 853.

## 6. Compute-run rows (`registry/compute_runs_v1.csv` header)

```
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S176-NH-001,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",07fc0d2+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,8,"tools/nonheat_layer_run.py --seed 20261104 --sample-size 1000 --workers 8 --families FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET",reports/step26/nonheat_L1_1000_S176.json,c0f947d8543ea04315ae09a5cf3a52a129aaf1bf5c79d51ed5ca136265876946,2026-11-08T14:03:11Z,2026-11-08T14:05:47Z,DONE,"1,000 recipes; 4,927 non-heat events; L1 2.5 min + L2 5 s; L2 report sha256 dea868e5962dbbeeab012ded2383579a4ce328456e9352cff8d02e018f40fa18; records data/derived/physical_NH_L1|L2_1000_S176 (git-ignored via the worktree data symlink)"
RUN-S176-NH-002,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",07fc0d2+uncommitted,TASTESET,24,"tools/nonheat_layer_run.py --seed 20261104 --sample-size 600000 --workers 24 --families TASTESET",reports/step26/nonheat_L1_TASTESET_full_S176.json,d913edc39ffbe22e0cefad646a90df18029fa4ce669c63d6990c15d4c04d07e1,2026-11-08T14:03:11Z,2026-11-08T14:03:17Z,DONE,"700 recipes; 0 non-heat events (no step lists); L2 report sha256 3fb02ce3c72d1da12a30ec4edb0cb7f79b00dbffbbf9ccbd77da833e37a295d5"
RUN-S176-NH-003,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",07fc0d2+uncommitted,WIKIBOOKS,24,"tools/nonheat_layer_run.py --seed 20261104 --sample-size 600000 --workers 24 --families WIKIBOOKS",reports/step26/nonheat_L1_WIKIBOOKS_full_S176.json,deb79260ee9639bcf76d7d32297ccff69b8a3d877483962ead7c5a5c42a973ce,2026-11-08T14:03:20Z,2026-11-08T14:03:54Z,DONE,"3,676 recipes; 18,900 non-heat events; L1 22 s + L2 11 s; L2 report sha256 52deaac4254e203fa74084836b01299e4c076b931c0a27f0fc6ece1686def2b7"
RUN-S176-NH-004,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",07fc0d2+uncommitted,GUTENBERG_SEGMENT,24,"tools/nonheat_layer_run.py --seed 20261104 --sample-size 600000 --workers 24 --families GUTENBERG_SEGMENT",reports/step26/nonheat_L1_GUTENBERG_SEGMENT_full_S176.json,e2980b384647e0e03595c62603922c51f1ee1139a161d54ec79a05cafd15759a,2026-11-08T14:03:58Z,2026-11-08T14:20:24Z,DONE,"73,955 recipes; 297,421 non-heat events; L1 5.1 min + L2 11.3 min; L2 report sha256 6824a64b86752a750d93b76de21dac19f313db0e348c21af6b4b2574141b8252"
RUN-S176-NH-005,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",07fc0d2+uncommitted,FOODCOM,24,"tools/nonheat_layer_run.py --seed 20261104 --sample-size 600000 --workers 24 --families FOODCOM",reports/step26/nonheat_L1_FOODCOM_full_S176.json,343ff502fa6b8a1f657100231bff1f39a5d4353b1abf5a6881459e8f426d5791,2026-11-08T14:20:39Z,2026-11-08T15:36:53Z,DONE,"522,517 recipes; 2,711,429 non-heat events; L1 52.4 min + L2 23.9 min; L2 report sha256 07b60a607e61a903797cef17a8faee2839c9f37da450a6be93721dc470844188"
RUN-S176-NH-006,manjot-server,"~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)",07fc0d2+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET,8,"tools/binding_census.py --seed 20261104 --sample-size 1000 (heat census re-run after L-NH code existed)",,cdb29f4fe08b40c1aced741374758b46acdd4c47d9e6d2300d9d16253ab72f62,,,DONE,"baseline proof: 29 count fields identical to the run before (sha256 0e0215103aa9cdfff42c23ab950e009871090566746116b86a327a528a14693d); heat_events 2820, driver_ready 89, contract_bindings 3885; output kept in the session scratchpad, not committed"
```

## 7. Open questions and decisions for a human

1. **Size fallback.** L2 drivers that need a size (cooling, soak / marinate / pickle, drying, rest) stay UNKNOWN when no cut verb sits upstream of the lot, so coverage is a few percent. Option: a documented generic piece-size bracket (one registry row per food group, or a wide "piece" range) labelled ASSUMED_DEFAULT. It would multiply L2 coverage but widens the brackets and invents a size where the text gives none; the heat layer chose the other way. Needs a D-077 owner decision.
2. **Where per-event records live.** The brief names `data/derived/physical_NH_*_S176/`. In the worktree `data` is a symlink to the main checkout's `data/`, so the records physically sit in `~/kush_work/culinarystate/data/derived/` (new subdirectories only).
   - `.gitignore` does not list `data/derived`. The main repo's `.git/info/exclude` contains `/data`, and `git check-ignore` confirms the new directories are ignored there.
   - This is the same route L-PH used for its raw download. Please confirm or move them.
3. `needs_source` is a prefix of `source_hint`, not a column. A column can be added with no code change.
4. FORM candidate class labels are plain strings from the coverage-plan table (`nonheat_binding.FORM_CANDIDATE`); 23a maps them to FORM ids later. Confirm the vocabulary.
5. Rung A lexicon (not this lane): noun and adjective surfaces, `dry`, `process`, `crack`, `grates`, a duration attached to the preceding verb, HTML entities. A lexicon pass would raise PRESERVATION and FERMENT_LEAVEN precision.
6. Conventions to confirm:
   - Months as 30 days and years as 365 days (flagged `unit_convention`).
   - GENTLE = least process effect, so GENTLE cooling is the slowest cooling.
   - STORAGE L2 status `CONDITIONS_ONLY_KINETICS_UNKNOWN` with transition `unsupported`.
   - `time_until_next_heat` is a lower bound from stated durations only.
7. All 40 NH registry rows are agent recall and need the sourcing lane. The drivers are engineering verification only (NOT_VALIDATED), never evidence. SIMULATE stays unreachable for any compound until PARAM rows are human verified.
8. **Performance fix** for very long, very thin RESTING stages (see Findings). Change the step rule in `slab_two_stage` (cap the step count, backward Euler on a geometric grid) and re-run L2 only, since L1 is unaffected. Otherwise accept the slow tail on vinayak. The rest of L2 cost is the series evaluation in `physics_drivers.core_trajectory`, which is reused as is.

## 8. Reproduce

```
cd ~/kush_work/culinarystate/.orch
~/kush_work/culinarystate/.venv312/bin/python -m pytest -q tests/unit/test_nonheat_*.py tests/unit/test_s172_*.py
nice -n 10 ~/kush_work/culinarystate/.venv312/bin/python tools/nonheat_layer_run.py --seed 20261104 --sample-size 1000 --workers 8 \
  --families FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET \
  --l1-records-dir data/derived/physical_NH_L1_1000_S176 --l2-records-dir data/derived/physical_NH_L2_1000_S176 \
  --l1-out reports/step26/nonheat_L1_1000_S176.json --l2-out reports/step26/nonheat_L2_1000_S176.json
```

---
*Saved by the orchestrator from the L-NH agent handback (the agent could not write report files).*
