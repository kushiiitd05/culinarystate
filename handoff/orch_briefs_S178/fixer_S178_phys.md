# Fixer lane FIX-PHYS (S178): apply the SCI-A review to the physical layers and the AA SIMULATE branch, then v05 re-runs

## Setup
- Read `handoff/orch_briefs_S178/orch_ctx.md` first. It has the laws, ownership rules and server etiquette.
- Worktree: `<repo root>`, HEAD `5742fc1`. Python: `.venv312`. No git writes; the orchestrator commits.
- The review is `reports/orchestration/review/S178_REV_SCI-A.md` (findings M1–M7, m1–m11). Read it fully, including its "checked and correct" section. Read `reports/orchestration/S178_PHYS2_report.md` as well.

## Ownership this round
You own:
- `src/culinarystate/simulation/{condition_binding,endpoint_cues,scenario_layer,phase_change,nonheat_scenario,nonheat_binding,phys_verification,binding_census}.py`
- `src/culinarystate/mechanism/simulate_branch.py`
- `tools/{binding_census,scenario_layer_run,nonheat_layer_run,s178_phys_*}.py`
- `registry/matrix_moisture_regime_v1.csv`, `registry/endpoint_cue_lexicon_v1.csv`
- their tests, and new `tests/unit/test_s178_fixphys_*.py`

Do NOT touch the files other lanes own:
- PHYS3: `simulation/shape_series.py`, `phys_verification_shapes.py`, the 26g census.
- MECH: `mechanism/screen.py`, `mech_*`.
- H1H3H: the new evaluation modules.
- FIX-GOV: `app/server.py`, `decision/public_mode.py`, `transition/dataset.py`, the analysis/EVD tools.

## Rulings for the reviewer's three questions
These are tightenings, which D-071 allows an AI to apply. Implement them as the PROPOSED default and mark them for Kush:
- **Q1 (M4/M5).** The stated-liquid cap is lifted only when all three hold:
  1. the temperature is OWNED by the liquid step;
  2. there is a solute-rich member, a syrup/candy/stage cue, or a pressure cue (pressure lifts only up to 121 °C + ε);
  3. the value is never used inside a moist solid piece. For a cut piece, the conduction boundary is min(bath, T_boil); the lifted value applies only to the liquid itself.

  Otherwise keep the cap and flag it. Treat appliance and heat-level words (electric skillet, slow cooker, "over medium heat", "reduce heat to") as ambient cues.
- **Q2 (M7).** A Layer 2 scenario default never counts as observed. G7 = UNKNOWN when any SIMULATE input has basis ASSUMED_DEFAULT or another non-TEXT_STATED/non-PHYSICAL_DEFINITION scenario basis. Such events are at most QUALITATIVE. Extend the property test to cover the `with_scenario` path, and reword the AASIM report claim in a dated correction section appended to your report (do not edit the AASIM report).
- **Q3 (M6).** Add the caveat paragraph to the sensitivity report output, through its generator `tools/s178_phys_sensitivity.py`. The caveat: the bracket is within one boundary-condition model; GENTLE/INTENSE are joint corners; pan geometry is not bracketed. Add the boundary-model bracket axis only if it is cheap and tested. Otherwise list it as open.

## What to fix
- **M1–M3:** the Layer 1 binder and endpoint cues. Use the reviewer's failing inputs as RED tests first, then fix. Add a corpus check: the count of bound temperatures inside until-clauses, before and after.
- **M4/M5:** per the Q1 ruling. Add an invariant test: no moist-piece core above T_boil unless a pressure cue is present.
- **M6, M7:** per the rulings above.
- **Minors:** fix m1–m11 where they are reasonable in scope, each with a test:
  - m1: ranges, spelled-out units, "c." meaning cups.
  - m2: UK fan strings become a RANGE plus a flag.
  - m3: water bath in an oven.
  - m4: the cooling `target_food_temperature` is an endpoint.
  - m5: refuse SIMULATE when the piece size is known (until zone doses are wired), or wire `zone_mean_survival` if it is simple.
  - m6: no `query_overrides` in REAL mode; test-only fixtures require a test marker.
  - m7: give each verification check an independence class; gate V14 on monotonicity; add short-time FD checks; reword the "thaw mirror".
  - m8: split the basis kinds in the sensitivity report.
  - m9: state the numerical biases.
  - m10: split the solute-rich flag into sugar phase vs salt; keep row 3(c) open.
  - m11: canner temperature above 121 °C + ε becomes QUALITATIVE `STATED_CANNER_T_IMPLAUSIBLE`.

  A minor you cannot do well goes in the report as NOT FIXED with the reason.
- **Version bumps:** Layer 1 heat and non-heat 0.2.0 → 0.3.0; Layer 2 heat and non-heat 0.4.0 → 0.5.0. Update the version-pinning tests honestly.

## v05 re-runs
- Order: the 1,000-recipe sample first (heat L1, L2, non-heat L1 + L2). Then the full non-BBC families with the same commands and worker counts as the PHYS2 rows `RUN-S178-PHYS2-*` in `registry/compute_runs_v1.csv`. Use seed 20261104, `nice -n 10`, and check `uptime` first.
- Outputs:
  - per-record files under `data/derived/physical_*_S178v05*`;
  - reports as `reports/step26/*_S178_v05.json`;
  - a v04 → v05 comparison (reuse `tools/s178_phys_v04_comparison.py` or a new `tools/s178_fixphys_v05_comparison.py`);
  - the schema validator on all v05 records (expect 100%);
  - regenerate the sensitivity, endpoint-cue and stated-liquid reports as `*_S178_v05.*` under `reports/s178/phys/`.
- List every v04 output that v05 supersedes, as CSV rows in the column format of `registry/superseded_outputs_S176.csv`. FIX-GOV is editing that file now, so put the rows in your report and the orchestrator appends them.
- Disk: delete the v04 per-record files under `data/derived/` only AFTER v05 validates, and list what you deleted. Keep the committed v04 JSON reports.
- Log every run as a CSV row (header of `registry/compute_runs_v1.csv`), including failed and aborted runs.

## Tests
Run all PHYS2, S177 physics, AASIM and non-heat suites plus your new tests:
`tests/unit/test_s178_phys2_*.py test_s177_phys_*.py test_s178_aasim_*.py test_nonheat_*.py test_s176_*.py test_s172_*.py test_step26b_*.py test_step26c_*.py test_s166_step26g_census.py`, plus yours. Report the results.

## Report
- Path: `reports/orchestration/S178_FIX-PHYS_report.md`.
- Contents:
  - each finding as FIXED or NOT FIXED, with file:line and test names;
  - before/after counts, including the corpus counts the reviewer cited: 869 until-clause bindings, 318 L2 ovens below 77 °C, the 241 lifts, the 12 moist-piece cores above 100 °C;
  - the runs;
  - the superseded rows;
  - the proposed SSOT v16 wording changes (`docs/` is not yours);
  - the PROPOSED rulings, flagged for Kush.
- If Write is refused, return the report in your final message.

## Rules
- The repo is PUBLIC: no personal details, private host addresses, credentials or third-party text. You may see an irrelevant memory index about other projects; never copy it.
- No corpus sentence is quoted in committed files; use synthetic examples.
- Final message: short.
