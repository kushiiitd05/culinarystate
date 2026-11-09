# CulinaryState orchestration S176 — shared brief for every lane agent (read fully before starting)

## Where you work
- Worktree: `<repo root>` (git branch `max/s176-orchestration`, based on GitHub `kush/s169-seal-p1b` @ 07fc0d2 = the latest project state, S174 + S175 review packet). Work ONLY inside this worktree.
- NEVER edit anything in `~/kush_work/culinarystate/` outside `.orch/` — that folder is a sync target written by the Mac coding agent. Read data only through the worktree's symlinks: `data/` → main data dir; `ledgers/recipe_base/*.parquet`, `ledgers/recipe_identity/*.parquet` → main ledgers.
- Python: `python` (3.12; numpy, pandas 2.1, pyarrow 14, scipy 1.17, pytest 9.2; NO torch). Run from the worktree root. Tests: `<python> -m pytest -q <paths>`.
- Do NOT run `git add`, `git commit`, `git stash`, `git checkout`, `git reset` or any git write. The orchestrator commits your lane at the end. Read-only git (log/show/diff/status/grep) is fine.

## File ownership (parallel lanes — write ONLY your lane's paths)
- Orchestrator-only (never edit): `WORKLOG.md`, `DECISIONS.md`, `STATUS.md`, `registry/compute_runs_v1.csv`, `handoff/*`, `docs/*`, SSOT, the 36-step plan.
- Protected ledgers stay byte-identical: `ledgers/data/{EVD,COND,SRC,MEAS,SNAP}.jsonl` (and do not append to any `ledgers/data/*.jsonl`).
- Every lane writes a report `reports/orchestration/S176_<LANE>_report.md`: what was built, files, tests run + results, runs done (as CSV rows matching the header of `registry/compute_runs_v1.csv`, with host `manjot-server`, tree `~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)`, git_commit `07fc0d2+uncommitted`, output sha256), open questions, and anything a human must decide.

## Project laws you must keep (from SSOT v15 / DECISIONS; violations are blockers)
1. §141 output contract: a transition is `unsupported`, `physically_possible` or `evidence_supported`. A number about food chemistry/nutrition is emitted ONLY from a measurement (EVD) or a calibrated, held-out-validated model. There is none yet except EVD lookups. UNKNOWN is never 0, never imputed silently.
2. D-077 two physical layers, never mixed: Layer 1 TEXT_STATED (only what the recipe text says + physical definitions such as water boils at 100 °C at 1 atm, each value with its text span; missing = UNKNOWN). Layer 2 SCENARIO (literature-typical defaults with source + range, run at GENTLE/TYPICAL/INTENSE = low/mid/high; labelled ASSUMED_DEFAULT, MODEL_DERIVED, NON_CITABLE). Every derived value carries its basis/provenance.
3. Recipes are not chemistry truth; co-occurrence never trains chemistry targets; learned weights are not reactions.
4. Router: measured evidence first; similarity only finds candidates; UNKNOWN never routes to SIMULATE.
5. Defaults/constants: never present a recalled number as sourced. Mark `SOURCE_UNVERIFIED_AGENT_RECALLED` unless you have opened the source; give ranges, not points, where literature varies.
6. Licences: no BBC Good Food data exists on this server (D-003) — never try to fetch it. Food.com is uploader-declared CC0 (unverified); Gutenberg public domain; Wikibooks CC BY-SA; USDA SR Legacy/FNDDS/cooking yields public domain. Third-party text never goes into committed files; committed outputs are counts/aggregates/registries only. Large per-recipe outputs go to `data/derived/` (git-ignored).
7. Governance: AI output is never a human signature, approval or nonce. Under D-071 AI personas (ksh/prv) may decide review blocks, but YOU only propose; mark everything DRAFT / PROPOSED / AI_DRAFTED.
8. Negative results stay visible (07.A FAILED, G08-3 FAILED, D-074 R1 4/60, DEL-2 shortcut suspicion).

## Shared-server etiquette (this is manjot-server, shared with other users)
- At most 32 worker processes; prefix long runs with `nice -n 10`. No GPU use. Check `uptime` before big runs.
- Disk is 95% full (≈560 GB free): keep your lane's derived output under 15 GB; delete scratch you create; prefer counts-only summaries.
- Run a 1,000-recipe sample before any full-family run; full runs only for the non-BBC families present here (FOODCOM 522,517; GUTENBERG_SEGMENT 73,955; WIKIBOOKS 3,676; TASTESET 700). Use the same seed conventions as existing tools (`--seed 20261104`).
- Record start/end times and output sha256 for every run.

## Key repo pointers
- Plan: `docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`; finish plan `handoff/FINISH_PLAN_2026-11-07.md`; flow `handoff/PROJECT_FLOW_VERDICT_2026-11-08.md`; process coverage `handoff/PROCESS_COVERAGE_PLAN_2026-11-08.md`; review packet `handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md`.
- Physical layers code: `src/culinarystate/simulation/{condition_binding,binding_census,scenario_layer,physics_drivers,sim_core,choi_okos,recipe_adapter,census_chain}.py`, tools `tools/binding_census.py`, `tools/scenario_layer_run.py`, defaults `registry/` (grep for the scenario defaults registry), reports `reports/step26/`.
- SSOT: `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` — read by line ranges via `docs/SSOT_INDEX.md`, never whole.

## UPDATE 2026-11-09 (S177 round) — read this, it overrides older lines above where they differ
- The worktree branch `max/s176-orchestration` now also contains the Mac's 43 S175 commits (merged at a0a5b49, 435 tests pass).
- The Mac Claude is ACTIVELY developing `src/culinarystate/composition/` (lot composition layer: sr_legacy, ing_sr_match + `registry/ing_sr_defaults_v1.csv` (490 curated terms), line_mass, food_ph + `registry/food_ph_fda2003_v1.csv`, lot_state, lot_census, `tools/s175_line_mass_census.py`). NEVER edit those files or `reports/s175/*`; read and use them. If you find a bug there, report it (file:line + fix) — do not fix it.
- Our earlier `src/culinarystate/lotstate/` duplicates part of it; a consolidation review decides which is canonical. Do not build new features on `lotstate/` in this round.
- WORKLOG ids: S177 used (server); next free S178. DECISIONS next free D-079. Orchestrator-only files unchanged (WORKLOG, DECISIONS, STATUS, compute_runs, handoff/).
- The repo is PUBLIC: never write personal details, private host addresses or credentials into any file.

## UPDATE S178 waves — execution board
- `registry/execution_board_S178.csv` (252 MUST+SHOULD items, waves W1–W4) and `reports/orchestration/S178_EXECUTION_BOARD.md` define the work. Each lane: work only your listed item_ids; at the end list every item_id with its new status (DONE / PARTIAL + what is left) and the evidence path. Do NOT edit the board CSV (the orchestrator updates it).
- Acceptance = the board's `acceptance` column; quality over speed: tests first, counts-only outputs, honest statuses.
