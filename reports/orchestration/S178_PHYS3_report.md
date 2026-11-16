# S178 lane PHYS3 report: shapes, 26g census with Layer 1 bindings, diffusion sourcing

Status: AI_DRAFTED / PROPOSED. Nothing here is a human signature or approval. Worktree `.orch` (branch `max/s176-orchestration`), HEAD at
run time `aea05bb` (the lane brief named 32415c4; other lanes committed before my runs). No existing file was edited. No git write was run.

Session restart (about 19:50 IST): no PHYS3 run was in progress at the restart. Only smoke tests had run, so nothing is logged
`ABORTED_SESSION_RESTART`. Every run below started after the restart.

## Item statuses

| item | status | evidence |
|---|---|---|
| T4-C08-R1 finite cylinder and sphere eigen-series, Heisler products, shape map, slab kept as the bound | **DONE** (not wired into Layer 2, as the brief says) | `src/culinarystate/simulation/shape_series.py`, `src/culinarystate/simulation/phys_verification_shapes.py`, `registry/shape_map_v1.csv`, `reports/s178/phys3/shape_verification_S178.{json,md}` (15/15 checks pass), `reports/s178/phys3/shape_census_*_S178v04.json` (counts-only diagnostic) |
| T4-C21-R1 26g census with Layer 1 bindings (T, t, medium, size), SIMULATE 0 asserted, baseline PASS | **PARTIAL**. Done: tool, tests, 1,000-recipe sample on v04. Left: the full non-BBC family runs, which the orchestrator will do on the v05 records (command below), per the orchestrator note. | `tools/s178_phys3_census_l1.py`, `tests/unit/test_s178_phys3_census_l1.py`, `reports/step26/simulability_census_L1_1000_S178_26g.json` |
| T4-C14-R3 diffusion coefficients (salt, acid, sugar in meat / vegetable) as ranges with page / locator cites | **PARTIAL**, at BLOCKED_HUMAN for the part only a human can do. Done: 45 AI-opened rows with locators, plus proposed merge rows. Left: a human check of the figures that reach a slide, and the merge decision. The defaults registry was not edited, as the brief says. | `registry/diffusion_coefficients_sourced_S178.csv` |

## T4-C08-R1: shapes

**Built.**
- `shape_series.py` (`shape-series-0.1.0-draft`) evaluates eigen-series for the SLAB, INFINITE_CYLINDER and SPHERE:
  - The roots are bracketed exactly: slab ((n-1)π, (n-½)π); cylinder [j₁,ₙ₋₁, j₀,ₙ] from scipy `jn_zeros`; sphere ((n-1)π, nπ). They are found with brentq, and Bi = ∞ gives the exact Dirichlet roots.
  - It returns C_n, the local θ and the volume-mean θ.
  - The term count is chosen from Fo, with every dropped term below 1e-14. There is no front switch, and Fo below 2.1e-7 is refused.
- Heisler product shapes:
  - FINITE_CYLINDER = cylinder × slab.
  - BRICK = slab³ with separate half-sides; CUBE = equal sides.
- A `Geometry` wrapper takes half-dimensions in metres, with `bound_half_thickness_m` and V/A.
- `core_and_mean_temperature` has the same signature as `physics_drivers.core_and_mean_temperature`, plus a geometry argument.
- Shape-map loader and lookup with precedence: exact (cut, class) > (cut, \*) > (NONE, class), the last only when no cut class is bound > (NONE, \*).

**Verification pack.** `phys_verification_shapes.py` extends the slab pack in a new file; `phys_verification.py` is unchanged. Run:
`python tools/s178_phys3_shape_verification.py --out-json reports/s178/phys3/shape_verification_S178.json --out-md reports/s178/phys3/shape_verification_S178.md`
gives **15 of 15 checks pass**, `results_sha256` = `ab3b285d112e5524078338f425ad1a249cfeec6c210c4193e3721cbbdf996949`.

| check | max abs error (tolerance) |
|---|---|
| Bi = ∞ against independent Dirichlet series (slab, cylinder, sphere; centre and mean) | 3.3e-16 (1e-12) |
| Bi = 1e8 → Dirichlet | 2.1e-8 (1e-6) |
| Bi → 0 lumped exp(-(hA/kV)αt) for cylinder, sphere, finite cylinder, cube | 5.8e-4 (1e-3; the O(Bi) error of the lumped model; error / Bi = 0.58) |
| long-cylinder limit: finite-cylinder centre → infinite cylinder at Lz ≥ 10R (and thin disk → slab) | 1.2e-13 (1e-9); mean rel error 0.11 / 0.037 / 0.011 at Lz/R = 10 / 30 / 100 (∝ R/Lz, monotone) |
| short time: slab surface = semi-infinite solid; Dirichlet sphere uptake = 6√(Fo/π) − 3Fo; sphere surface → semi-infinite with order 1 in Fo while Bi√Fo ≪ 1 | 4.4e-16 (1e-10) |
| 1-D finite-volume reference (200 cells, exact in time) | 2.1e-5 (2e-3) |
| 2-D Crank-Nicolson finite-volume solve of finite cylinder (Lz = 0.5, 1, 2R) and square bar (tests the product rule) | 1.3e-4 (3e-3) |
| roots: scaled eigen-condition residual (200 roots, Bi 1e-6 to 1e6); exact roots / C_n at Bi = 1 (sphere) and Bi = ∞ | 1.1e-13 (1e-12) |
| first-term ζ₁, C₁ table, cylinder and sphere (recalled textbook values, `SOURCE_UNVERIFIED_AGENT_RECALLED`) | 6.2e-5 (6e-4) |
| closed-form mean coefficients 2Bi²/(ζ²(ζ²+Bi²+Bi)), 4Bi²/(ζ²(ζ²+Bi²)), 6Bi²/(ζ²(ζ²+Bi²−Bi)); completeness Σ = 1 over 4000 terms plus the analytic tail | 1.0e-11 (1e-10) |
| **slab bound**: cylinder, sphere, finite cylinder, cube and brick θ ≤ slab of the smallest half-dimension; sphere ≤ cylinder ≤ slab | 0 violations in 1,512 comparisons (Bi 0.01–100, Fo 1e-3–5). Numerical evidence on that grid, not a proof. |
| shape_series slab against the Layer 2 slab driver (Fo ≥ 0.02) | 3.3e-16 (1e-10); Fo < 0.02 differs by ≤ 8.5e-7 (the driver's front bound) |
| one-term (Heisler chart) centre against the full series at Fo ≥ 0.2 | 1.2 % rel (2 %) |
| truncation rule against 2N terms (Fo 1e-5–1) | 3.1e-15 (1e-12) |
| dimensional wrapper against `physics_drivers` (°C); cube = slab³; V/A | 1.4e-14 (1e-8) |

**Shape map.** `registry/shape_map_v1.csv` has 13 rows, all basis `ASSUMED_DEFAULT` and status `AI_DRAFTED_PROPOSED`. The assignment of a shape to a class is an agent convention (`SHAPE_ASSIGNMENT_AGENT_CONVENTION`). The only number in the map is the coin aspect ratio R/Lz = 2/4/8, which is `SOURCE_UNVERIFIED_AGENT_RECALLED`.
- Cut-class rows:
  - SLICED → SLAB, except SLICED + VEGETABLE/FRUIT → FINITE_CYLINDER (coins).
  - DICED, CHOPPED, MINCED → CUBE.
  - GRATED → INFINITE_CYLINDER.
  - SHREDDED → SLAB.
  - HALVED, CRUSHED → SLAB_BOUND_UNRESOLVED.
- Ingredient-class rows (only when no cut class is bound): EGG → SPHERE, LEGUME → SPHERE, MEAT|SEAFOOD → SLAB.
- Default: SLAB_BOUND_UNRESOLVED.
- The slab stays the stated bound in Layer 2. Nothing is wired.

**Counts-only diagnostic: how many events would change shape class.** Computed by `tools/s178_phys3_shape_census.py` from the v04 L1 and L2 records. For events with a computed Layer 2 core, it also gives the change in the end-of-step centre temperature if the mapped shape replaced the slab. That change is recomputed from each record's own h, L, T₀, boundary T and duration, with k and α at the SD-040 / SD-041 mid values.

| records | L1 heat events | shape class would change | L2 events with a computed core | … of which shape would change | TYPICAL ΔT_core,end ≤0.1 / 0.1–1 / 1–5 / 5–20 / >20 °C |
|---|---:|---:|---:|---:|---|
| 1,000 sample v04 | 2,820 | 150 | 101 | 62 | 24 / 17 / 4 / 15 / 2 |
| FOODCOM full v04 | 1,503,261 | 77,976 | 55,146 | 31,481 | 13,657 / 4,776 / 2,349 / 7,433 / 3,266 |
| GUTENBERG_SEGMENT full v04 | 182,049 | 14,510 | 13,186 | 8,930 | 5,126 / 1,773 / 120 / 1,766 / 145 |
| WIKIBOOKS full v04 | 11,433 | 960 | 451 | 308 | 170 / 53 / 16 / 52 / 17 |
| TASTESET full v04 | 0 (no step text in the corpus) | 0 | 0 | 0 | — |
| **non-BBC total** | **1,696,743** | **93,446 (5.5 %)** | **68,783** | **40,719 (59 %)** | 18,953 / 6,602 / 2,485 / 9,251 / 3,428 |

Reading:
- The shape changes come from CHOPPED → CUBE (20,171 of the 40,719 core events), DICED → CUBE (6,157), GRATED → cylinder (7,103), SLICED vegetable / fruit → coin (3,849) and MINCED → CUBE (3,439).
- At TYPICAL, **12,679 of the 40,719 events (31 %) move by more than 5 °C**. Each would get a hotter core, since the slab is the slow side.
- At GENTLE (thick piece, low h) the effect is larger: 13,935 events move by more than 20 °C.
- At INTENSE it is mostly ≤ 0.1 °C (35,563), because the core already reaches the bath.
- Consistency checks: in every core event and bracket, the recomputed slab centre equals the record's `core_end_c` within 0.01 °C, and the slab bound held, with 0 violations.
- So wiring shapes into Layer 2 is a material change. It is a human decision for a later round.

## T4-C21-R1: 26g census with Layer 1 bindings

**Hook.** The S166 census tool (`tools/step26g_census.py` + `simulation/census_chain.py`) has no hook for Layer 1 inputs. I did not edit it; instead a new tool reuses its parts:
- `tools/s178_phys3_census_l1.py` reuses the corpus reader, seeded sample, ledger baseline check and counts-only writer, and takes the Layer 1 records directory as a parameter (`--layer1-records DIR ...`).
- Per sampled recipe it runs the same chain once (Rung A → event adapter → replay) and builds the contract records twice:
  - `baseline_no_bindings`: no bindings. This equals the S166 census.
  - `with_layer1_bindings`: the Layer 1 records of that recipe, joined on recipe id + event id and decoded back to exact Fractions, then turned into `ConditionBinding`s by the Layer 1 binder's own rule (`condition_binding.Binder._bindings`). The rule covers duration, medium, lid, start mode, size class and matrix class, and a temperature profile only with a point duration. Source class is STRUCTURAL_RECIPE.
- No applicability record is supplied.
- SIMULATE gate:
  - Both arms are asserted SIMULATE = 0.
  - `ledgers/data/PARAM.jsonl` is read (it is absent here: 0 human-verified rows).
  - If any SIMULATE appeared, the tool writes nothing and exits 5 (tested).
- Fork pool of at most 24 workers. Records are folded into the census every 256 recipes, so memory stays bounded.

**Old mode byte-identical (tested).**
- `tests/unit/test_s178_phys3_census_l1.py`:
  - The baseline arm's census and `census_sha256` equal `census_chain.census_from_records` on the same records.
  - That holds with block flushing and with 2 workers too.
  - `tools/step26g_census.py`, `census_chain.py` and `recipe_adapter.py` are hash-identical to `git show HEAD:…`.
- On real data, the unchanged S166 tool was run on the same seed and sample size (system sim_aa_1; output to the scratchpad, not committed; census_sha256 `84057660e3c98cc144114ed3c33e32a3c021468ec8f12003dd2ddd18eb58d785`).
  - Its `systems.sim_aa_1` block, `binding_counts` and every other census key are **identical** to the new tool's baseline arm.
  - The same holds for `recipes_seen` (600,848), `engine_events` (23,580), the adapter issue codes and the exceptions.
  - The two census hashes differ only because my run carries both systems (`sets` 1,994 = 2 × 997, and a sim_chl_1 block).
- Provenance caveats:
  - `code_unchanged_during_run` is **False** in all three census runs, the S166 one included. Other lanes edited unrelated `src/` files during the runs (`nonheat_binding.py` 20:23:25, `nonheat_scenario.py` 20:16:02, both FIX-PHYS), so `src_tree_sha256` moved.
  - Every file whose hash the tool records (`census_chain`, `recipe_adapter`, `condition_binding`, `step26g_census`, this tool) still matches its recorded hash after the run.
  - `condition_binding.py` in the working tree is FIX-PHYS's uncommitted 0.3.0 edit (made at 20:07, before my runs), but its `_bindings` rule is byte-identical to HEAD. So the bound arm applied the committed rule to the v04 (0.2.0) records.

**1,000-recipe sample (v04 Layer 1 records), seed 20261104, systems sim_aa_1 and sim_chl_1.**
- Output: `reports/step26/simulability_census_L1_1000_S178_26g.json`.
- Families: BBC is INPUT_MISSING by design (D-003), as in the L1 v04 sample that produced the records. So the sample is the same 1,000 non-BBC recipes, and the exit code is 3 for that reason only.
- Baseline check PASS_BEFORE_AND_AFTER; exceptions 0; recipes 1,000, of which 997 have steps; 23,580 engine events.
- Layer 1 join:
  - 2,820 records for 837 recipes; all 2,820 matched a replay event (0 not in replay, 0 duplicates, 0 decode errors).
  - 160 recipes with steps have no heat event, so they have no record.
- 3,882 contract bindings supplied.
- **SIMULATE = 0 in both arms, both systems**; `all_inputs_present` = 0, because Layer 1 v0 binds neither the water ratio nor the pH.

Event reasons, sim_aa_1, over 23,580 events (2,820 with a Layer 1 record):

| reason | before | after | dropped |
|---|---:|---:|---:|
| MISSING_MEDIUM | 23,580 | 22,002 | 1,578 |
| MISSING_MATRIX_CLASS | 23,580 | 22,637 | 943 |
| MISSING_DURATION | 23,580 | 22,829 | 751 |
| MISSING_LID_STATE | 23,580 | 23,336 | 244 |
| MISSING_PIECE_SIZE_CLASS | 23,580 | 23,342 | 238 |
| MISSING_TEMPERATURE_PROFILE | 23,580 | 23,494 | 86 |
| MISSING_START_MODE | 23,580 | 23,538 | 42 |
| MISSING_WATER_RATIO | 23,580 | 23,580 | 0 (not bound in L1 v0) |

- 2,288 of the 2,820 bound events lose at least one MISSING_* reason.
- The reasons per event fall from 9–11 to as few as 3.
- On sim_chl_1, 1 event is blocked only by MISSING_MEDIUM_PH (plus applicability).
- **404 events have a Layer 1 temperature but no contract temperature profile.** The binder rule builds a profile segment only with a point duration, so a stated temperature with a duration range or no duration stays MISSING. This is the main loss and an open question (below).
- Reasons by event family and the full reason-set distribution of the bound events are in the JSON (`paired_by_event`).

**Full non-BBC runs (for the orchestrator, on v05 once it exists).** Same seed. The per-family Layer 1 directories must be the v05 ones; `uptime` first.
```
for F in FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET; do
  uptime
  nice -n 10 .venv312/bin/python tools/s178_phys3_census_l1.py \
    --seed 20261104 --sample-size 612782 --families $F --systems sim_aa_1 sim_chl_1 \
    --layer1-records data/derived/physical_L1_full_S178v05/$F --workers 24 \
    --out reports/step26/simulability_census_L1_${F}_full_S178v05_26g.json
done
```
- Run first the v05 1,000 sample: the same command with `--sample-size 1000`, no `--families`, `--layer1-records data/derived/physical_L1_1000_S178v05`, `--workers 8` and `--out reports/step26/simulability_census_L1_1000_S178v05_26g.json`.
- Check `layer1.records_event_not_in_replay` = 0 and `layer1.record_versions` = L1 0.3.0. If v05 changes the record layout, the decode errors appear in `layer1.decode_exceptions_by_class`, and the round-trip test (`test_decoded_records_give_the_live_binder_bindings`) will fail first.
- Expected cost: the sample took about 2.5 min in total, most of it the single-process corpus read. FOODCOM full is about 0.1 to 0.2 s of chain per recipe, so roughly 30 to 70 min at 24 workers (an estimate). The parent holds the full seeded sample, about 3 GB, as the S166 tool does.
- TASTESET has no step text (0 events), so its run is a formality.
- The full shape diagnostic on v05 is `tools/s178_phys3_shape_census.py --l1 data/derived/physical_L1_full_S178v05/$F --l2 data/derived/physical_L2_full_S178v05/$F --workers 12 --out reports/s178/phys3/shape_census_${F}_full_S178v05.json` (under a minute per family).

## T4-C14-R3: diffusion coefficients

`registry/diffusion_coefficients_sourced_S178.csv` has 45 rows. A sourcing sub-agent opened each source through the Europe PMC REST full text or abstracts, SciELO HTML, repository PDFs, an ARS/USDA PDF or the CORE API, and read the numbers from the raw text.
- Every row has `opened_by_agent=YES`, `human_verified=NO`, a locator (table / section / page / abstract) and notes starting `[AI_DRAFTED]`.
- 20 rows are FULL_TEXT and 25 ABSTRACT_ONLY; 39 are PRIMARY_MEASURED and 6 AS_CITED_SECONDARY, each naming the original.
- I re-opened three rows myself, and all three matched the source:
  - DCS-002: Visy 2021, static brining 1.8e-10 m²/s.
  - DCS-036: mango Table 5, 6.79 / 7.16 / 8.43e-10.
  - DCS-023: Casales 2009, 3.39 / 3.49e-6 cm²/s.
- No defaults registry was edited.

| solute × matrix | rows | span (m²/s) | T (°C) |
|---|---:|---|---|
| NaCl × MEAT | 11 | 4.7e-11 – 2.58e-9 | 4–21 |
| NaCl × FISH | 10 | 2.39e-11 – 6.53e-9 | 2–33 |
| NaCl × VEGETABLE (flesh) | 4 | 3.5e-10 – 4.05e-9 | 30–60 where stated |
| NaCl × FRUIT | 1 | 4.32e-10 – 5.42e-10 | 25–55 |
| acetic acid × FISH / MEAT / VEGETABLE | 1 / 1 / 1 | 3.4e-10 / 2e-10–8.6e-9 (tumbled) / 6.3e-10–4.0e-9 | 20 / – / – |
| lactic acid × FISH (cytosol extract) | 1 | 7.9e-11 – 2.26e-10 | 5–25 |
| sucrose × FRUIT | 8 | 2.07e-11 – 1.79e-9 | 25–75 |
| sucrose × VEGETABLE / × MEAT (cat myocardium, physiology) | 1 / 1 | 5.41e-10 / 1.51e-10 | 40 / 23 |
| glucose × FRUIT; reducing sugars × VEGETABLE; unspecified sugar × apple; deoxyglucose × fish cytosol | 1; 2; 1; 1 | 5.6e-10–1.88e-9; 1.57e-10–9.18e-9; 4.4e-10; 1.2–2.9e-10 | 45–75; –; 50; 5–25 |

**Proposed merge rows** (PROPOSED, for a human; not applied):
- `NH-040:MEAT` (NaCl, static brine, fridge temperature): 1.2e-10 / 2.5e-10 / 9.6e-10 m²/s.
  - The low and mid come from Fick slab fits on pork at 4–8 °C (DCS-001 to 004, 009); the high is the beef / chicken abstracts (DCS-007/008).
  - Method-dependent values above 1e-9 (DCS-005, one-way and power-function fits) stay as context.
  - The current 1e-10 / 2.5e-10 / 6e-10 is consistent except the high.
- `NH-040:FISH`: 1.1e-10 / 2.4e-10 / 1.45e-9.
  - From post-rigor salmon at 10 °C, herring at 10 °C, and swordfish / cod at 23–33 °C (as cited).
  - In-rigor salmon (2.9e-11) and pre-salted anchovy (2.4e-11) are excluded as process-specific.
- `NH-040:VEGETABLE` (internal flesh only): 3.5e-10 / 1.4e-9 / 4.05e-9.
  - All at 30–60 °C, above kitchen brining.
  - Add a flag `SKIN_LIMITED_UPTAKE_WHOLE_PRODUCE`: olive skin is 1.1–2.2e-13 (DCS-027), and the cucumber Bi is 2.6–5.5 (DCS-032).
  - The S176 Chinese-cabbage 1.7e-11 was not re-opened.
- `NH-041` (acid) stays RETIRED. The new values are apparent D (buffering, reaction-diffusion) and are kept as context only.
- `NEW_SUGAR` (sucrose infusion into fruit / vegetable tissue, osmotic dehydration): 6e-11 / 5e-10 / 1.8e-9.
  - The low is whole skin-on berries (DCS-038, 041); the mid is the banana / carrot / apple / pomegranate cluster at about 4–6e-10; the high is carambola at 75 °C and cherry at 60 °C.
  - Label it SOLUTE_GAIN_APPARENT_D, mostly measured at 25–75 °C.
  - Sugar in meat: no food-tissue source exists (only a physiology tracer), so it stays **UNKNOWN**.

**Gaps:**
- NaCl in ham.
- NaCl inside cucumber or cabbage (only rate constants).
- Citric acid in any matrix.
- Lactic acid in vegetables or meat.
- Acetic acid in cucumber, onion or carrot.
- Static acid marinating of beef or chicken.
- Sucrose in pear, papaya, pumpkin or potato.
- Glucose infusing into vegetables.

**Seen only in search snippets (`SOURCE_UNVERIFIED_SEARCH_SNIPPET`, not rows):**
- Acetic acid in water, 1.21e-5 cm²/s at 20 °C (a homework document).
- A cut-vegetable / gel acid-diffusion Ea of 16.8 kJ/mol over 20–70 °C (a repository snippet).
- Cheese salting D* 0.31 cm²/day (not a target matrix).

**Doubts flagged in the rows:**
- DCS-020: herring 2.31e-9 has the same digits as the cited 2.31e-10, so it may be a 10× slip.
- DCS-035 / DCS-036: the cherry and mango abstracts disagree with their own tables; the table values are used.
- DCS-005: an internal 2.20 / 2.35 inconsistency.
- Mojibake in two Europe PMC records; the exponents were read as -9 and -10.

## Files (all new)

- `src/culinarystate/simulation/shape_series.py`, `src/culinarystate/simulation/phys_verification_shapes.py`
- `registry/shape_map_v1.csv` (sha256 `ce5b313f10d3cbd17d1a30e268153774f4f96227fd63165f31a2f4781d6f84c2`), `registry/diffusion_coefficients_sourced_S178.csv` (sha256 `f2ba255161872f4a238ac3d8596c7a3d6237617d979d8b00e793627004a18730`)
- `tools/s178_phys3_census_l1.py`, `tools/s178_phys3_shape_census.py`, `tools/s178_phys3_shape_verification.py`
- `tests/unit/test_s178_phys3_census_l1.py` (15 tests), `tests/unit/test_s178_phys3_shapes.py` (11 tests)
- `reports/s178/phys3/shape_verification_S178.{json,md}`, `reports/s178/phys3/shape_census_{1000,FOODCOM_full,GUTENBERG_SEGMENT_full,WIKIBOOKS_full,TASTESET_full}_S178v04.json`
- `reports/step26/simulability_census_L1_1000_S178_26g.json`
- `data/derived/`: nothing written (both tools are counts-only).

## Tests

`.venv312/bin/python -m pytest -q tests/unit/test_s178_phys3_census_l1.py tests/unit/test_s178_phys3_shapes.py` → **26 passed**; together with `test_s166_step26g_census.py` and `test_s172_binding_census.py`, 40 passed (66 s).
- Existing suites rerun alongside: `test_s166_step26g_census.py`, `test_s172_binding_census.py`, `test_s178_phys2_verification.py` and `test_s172_physics_drivers.py` all pass.
- `test_step26g_recipe_adapter.py` cannot be collected in this venv, because `hypothesis` is not installed. That predates this lane.

## compute_runs rows (CSV, header of `registry/compute_runs_v1.csv`)

```
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S178-PHYS3-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),aea05bb+uncommitted,none (analytic / numerical only),1,nice -n 10 .venv312/bin/python tools/s178_phys3_shape_verification.py --out-json reports/s178/phys3/shape_verification_S178.json --out-md reports/s178/phys3/shape_verification_S178.md,reports/s178/phys3/shape_verification_S178.json,0e2ee7656478d1ccf36067b932c23b0aea6d8481a9b0c57e45aa304d4489d731,2026-11-09T14:45:25Z,2026-11-09T14:47:09Z,DONE,"15/15 checks pass; results_sha256 ab3b285d112e5524078338f425ad1a249cfeec6c210c4193e3721cbbdf996949; md sha256 53c7fae8e49eba022bf60461f8ccd25b36788c3f86ec957d39fd6e7de6302d02; 102.6 s"
RUN-S178-PHYS3-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),aea05bb+uncommitted,1000-sample L1/L2 v04 records (FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET),4,nice -n 10 .venv312/bin/python tools/s178_phys3_shape_census.py --l1 data/derived/physical_L1_1000_S178v04 --l2 data/derived/physical_L2_1000_S178v04 --workers 4 --out reports/s178/phys3/shape_census_1000_S178v04.json,reports/s178/phys3/shape_census_1000_S178v04.json,c2b8c894112130745c4dbb9efc0cdbc785e8861e95b251ae9f807659a001b198,2026-11-09T14:47:09Z,2026-11-09T14:47:13Z,DONE,"counts only; 2,820 heat events, 150 shape change, 62 of 101 core events change; slab recompute matches record 62/62 per bracket"
RUN-S178-PHYS3-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),aea05bb+uncommitted,FOODCOM (full v04 L1/L2 records),12,nice -n 10 .venv312/bin/python tools/s178_phys3_shape_census.py --l1 data/derived/physical_L1_full_S178v04/FOODCOM --l2 data/derived/physical_L2_full_S178v04/FOODCOM --workers 12 --out reports/s178/phys3/shape_census_FOODCOM_full_S178v04.json,reports/s178/phys3/shape_census_FOODCOM_full_S178v04.json,19db54f13f5d7dfafa45159791c458ae883aa6d6e4bd23852a05ceaffa4062e2,2026-11-09T14:47:13Z,2026-11-09T14:47:58Z,DONE,"read-only over existing v04 records; 1,503,261 heat events; 31,481 of 55,146 core events change shape"
RUN-S178-PHYS3-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),aea05bb+uncommitted,GUTENBERG_SEGMENT (full v04 L1/L2 records),12,nice -n 10 .venv312/bin/python tools/s178_phys3_shape_census.py --l1 data/derived/physical_L1_full_S178v04/GUTENBERG_SEGMENT --l2 data/derived/physical_L2_full_S178v04/GUTENBERG_SEGMENT --workers 12 --out reports/s178/phys3/shape_census_GUTENBERG_SEGMENT_full_S178v04.json,reports/s178/phys3/shape_census_GUTENBERG_SEGMENT_full_S178v04.json,fcf54174b35e39d00ef6efbc3457649499fe2be2b973191cef994454b3fb8a32,2026-11-09T14:47:58Z,2026-11-09T14:48:08Z,DONE,"182,049 heat events; 8,930 of 13,186 core events change shape"
RUN-S178-PHYS3-005,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),aea05bb+uncommitted,WIKIBOOKS (full v04 L1/L2 records),12,nice -n 10 .venv312/bin/python tools/s178_phys3_shape_census.py --l1 data/derived/physical_L1_full_S178v04/WIKIBOOKS --l2 data/derived/physical_L2_full_S178v04/WIKIBOOKS --workers 12 --out reports/s178/phys3/shape_census_WIKIBOOKS_full_S178v04.json,reports/s178/phys3/shape_census_WIKIBOOKS_full_S178v04.json,d5cfd3d03c61a11a51347904b2fab2aef45b5a59e9f462bdcff33f819627b935,2026-11-09T14:48:08Z,2026-11-09T14:48:12Z,DONE,"11,433 heat events; 308 of 451 core events change shape"
RUN-S178-PHYS3-006,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),aea05bb+uncommitted,TASTESET (full v04 L1/L2 records),12,nice -n 10 .venv312/bin/python tools/s178_phys3_shape_census.py --l1 data/derived/physical_L1_full_S178v04/TASTESET --l2 data/derived/physical_L2_full_S178v04/TASTESET --workers 12 --out reports/s178/phys3/shape_census_TASTESET_full_S178v04.json,reports/s178/phys3/shape_census_TASTESET_full_S178v04.json,aaa132e46a69467cf90019b57e853d1abb12d2536afefb0122e669381a34c587,2026-11-09T14:48:12Z,2026-11-09T14:48:16Z,DONE,"0 heat events (TASTESET has no step text)"
RUN-S178-PHYS3-007,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),aea05bb+uncommitted,WIKIBOOKS FOODCOM GUTENBERG_SEGMENT TASTESET (A1_BBC_GOOD_FOOD INPUT_MISSING by design),8,nice -n 10 .venv312/bin/python tools/s178_phys3_census_l1.py --seed 20261104 --sample-size 1000 --systems sim_aa_1 sim_chl_1 --layer1-records data/derived/physical_L1_1000_S178v04 --workers 8 --out reports/step26/simulability_census_L1_1000_S178_26g.json,reports/step26/simulability_census_L1_1000_S178_26g.json (deleted),b28f7172d9fa77b739de2e00b88d71ed9cac8eaef217fbf17cb06837d79d8708,2026-11-09T14:45:25Z,2026-11-09T14:47:49Z,SUPERSEDED,"tool edited after this run (block flush every 256 recipes + duplicate-id check); output deleted and re-run as RUN-S178-PHYS3-008; all counts identical to 008 (only code_provenance differs); exit 3 = BBC INPUT_MISSING"
RUN-S178-PHYS3-008,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),aea05bb+uncommitted,WIKIBOOKS FOODCOM GUTENBERG_SEGMENT TASTESET (A1_BBC_GOOD_FOOD INPUT_MISSING by design),8,nice -n 10 .venv312/bin/python tools/s178_phys3_census_l1.py --seed 20261104 --sample-size 1000 --systems sim_aa_1 sim_chl_1 --layer1-records data/derived/physical_L1_1000_S178v04 --workers 8 --out reports/step26/simulability_census_L1_1000_S178_26g.json,reports/step26/simulability_census_L1_1000_S178_26g.json,2a9f7c8d09b4668a38976cfd2a1c5d2a0b8f40d6632bd069b40c2cec84fce874,2026-11-09T14:50:09Z,2026-11-09T14:53:30Z,DONE,"T4-C21-R1 sample; baseline PASS_BEFORE_AND_AFTER; SIMULATE gate PASS (0 both arms, both systems); 3,882 L1 bindings; 2,288 of 2,820 bound events lose a MISSING reason; baseline census_sha256 6289a8cd2bd19c96429a38eed964ca81dc447c782255151b08b0ac0aeefc7bbf; bound census_sha256 2ba51cf060e1077820bc4e628f205741398cc361108573e6461d83c62ee592fc; code_unchanged_during_run False (other lanes edited unrelated src files; recorded files unchanged); exit 3 = BBC INPUT_MISSING"
RUN-S178-PHYS3-009,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),aea05bb+uncommitted,WIKIBOOKS FOODCOM GUTENBERG_SEGMENT TASTESET (A1_BBC_GOOD_FOOD INPUT_MISSING by design),1,nice -n 10 .venv312/bin/python tools/step26g_census.py --seed 20261104 --sample-size 1000 --out <session scratchpad>/old_step26g_census_1000_seed20261104.json,session scratchpad (not committed),5188a1421888cf532d199fca69e27d8983f1141965a82391c621c6e179ad3be1,2026-11-09T14:45:25Z,2026-11-09T14:52:56Z,DONE,"unchanged S166 tool on the same sample, for the old-mode comparison: census_sha256 84057660e3c98cc144114ed3c33e32a3c021468ec8f12003dd2ddd18eb58d785; sim_aa_1 block identical to RUN-008 baseline arm; exit 3 = BBC INPUT_MISSING
```

## Open questions

1. **Temperature without a point duration (T4-C21).** 404 bound events in the sample have a stated temperature that never reaches the contract, because `Binder._bindings` builds a profile segment only from a MEASURED duration.
   - Option: allow a RANGE duration to give one segment [0, d_hi) with the temperature interval, marked as a range.
   - Option: add a duration-free "setpoint only" input.
   - This is a contract change (recipe_adapter / condition_binding, now owned by FIX-PHYS), not done here.
2. **Shape wiring (T4-C08).** At TYPICAL, 12,679 non-BBC core events would get an end centre temperature at least 5 °C hotter with the mapped shape. Should Layer 2 carry a second core, `core_end_c_shape` (MODEL_DERIVED, ASSUMED_DEFAULT shape), next to the slab bound, or keep the slab only? The CHOPPED → CUBE row drives half the change and is the least certain.
3. **Diffusion merge (T4-C14).** Accept, narrow or reject the four proposed rows. A human should check the figures before any reaches a slide; the human-verify list is DCS-001, 002, 013, 036 and 042 (the mid values).
4. The sourcing sub-agent's own summary miscounted the access types (it said 19 FULL_TEXT / 38 primary). The file holds 20 / 39; the report uses the file.

## Human decisions needed

- T4-C14-R3: approve or modify the proposed `NH-040:{MEAT,FISH,VEGETABLE}` and `NEW_SUGAR` rows, and human-check the cited figures (`human_verified` stays NO until then).
- T4-C08-R1: decide whether and how shapes enter Layer 2 (later round), and review `registry/shape_map_v1.csv` (ASSUMED_DEFAULT rows).
- T4-C21-R1: the orchestrator runs the full v05 families with the command above; SIMULATE stays 0 until a human-verified PARAM row and a 23a applicability record exist (M3 gate).
