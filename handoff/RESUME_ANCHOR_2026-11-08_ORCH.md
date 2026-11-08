# RESUME ANCHOR — server orchestrator, 2026-11-08 (PROVISIONAL; final version written when all agents finish)

**Where:** manjot-server, worktree `~/kush_work/culinarystate/.orch`, branch `max/s176-orchestration`
(from GitHub `kush/s169-seal-p1b` @ 07fc0d2). GitHub is public-read; pushing needs Kush's token or a bundle → Mac.
The folder `~/kush_work/culinarystate` itself is the Mac's rsync target — never write there.
Python for jobs: `~/kush_work/culinarystate/.venv312/bin/python` (no torch). Coordination: `handoff/ORCHESTRATION_TAKEOVER_2026-11-08.md`.

## Committed on the branch
- `3e9cb89` consensus plan (`reports/orchestration/ssot_consensus/CONSENSUS_PLAN_2026-11-08.md`), component ledger
  (`registry/component_ledger_v1.csv`, 217 components / 493 rows, all consensus 3/3), REV-A / REV-B answers to the
  review packet (`reports/orchestration/review/`), FDA pH registry draft (488 rows), takeover note.

## In flight when this was written (check `reports/orchestration/S176_*_report.md`; if a report is missing, that lane did not finish)
| Lane | Output paths | If unfinished |
|---|---|---|
| L-NH non-heat families L1/L2 | `src/culinarystate/simulation/nonheat_*`, `tools/nonheat_layer_run.py`, `reports/step26/nonheat_*_S176.json` | rerun lane from its brief; keep partial code only if tests pass |
| L-LOT lot-state [K] steps 1–3 | `src/culinarystate/lotstate/`, `registry/ing_sr_legacy_*`, `reports/lotstate/` | same |
| L-SRC defaults + mechanism windows sourcing | `registry/scenario_defaults_source_review_S176.csv`, `registry/mechanism_condition_windows_draft_v1.csv` | same |
| V16 SSOT v16 draft (appended) | `docs/SSOT/computational_gastronomy_master_ssot_v16_0_DRAFT.md`, `docs/SSOT/ssot_v16_INDEX_ADDENDUM.md` | same |
| OPS human operations pack | `handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md` | same |
| DEPLOY deployment + presentation plan | `handoff/DEPLOYMENT_AND_PRESENTATION_PLAN_2026-11-08.md` | same |

## Queued (not started at the time of writing)
1. **Physics bug fix (MUST, found by REV-A):** Layer-2 heat model has no evaporation term → moist cores reach
   160–220 °C in oven/oil/pan; cap free-water zones at the boiling point until dried, add surface vs core state;
   version the drivers; re-run L2 for non-BBC families on manjot; BBC re-run on the Mac.
2. **Router fix (MUST, REV-A):** vitamin-C DIRECT routes land mostly on foods with ~0 vitamin C (egg × bake 25 %);
   add a target-presence gate (needs the L-LOT SR match) and a lot-context gate; re-run the router census.
3. Two-persona review (governance + science) of all new code/docs → fixes → commit → bundle → final report.

## Human items (see the ops pack once written)
Decision sitting 9–10 Nov (Q39 lot-state scope, 07.A statistic ruling incl. accuracy co-gate + seeded errors,
SR_PORTION basis, Food.com no-unit policy, mode→§141 crosswalk …); signatures 10–11 Nov (07A-R1, AA, D5/H1/H3,
15a freeze, 29-diag); labels 13 Nov; AA verification 15 Nov; D5 review 16 Nov; merge `kush/s169-seal-p1b` → `main`
and this branch via the Mac.
