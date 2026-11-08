# Orchestration takeover — manjot-server, 2026-11-08 (S175 onward)

Kush asked the Claude session on manjot-server to take over as the main orchestrator ("take over the baton … main
orchestrator and other agents taking up the other tasks"). This note keeps the Mac coding agent and the server
orchestrator from writing the same files.

## Single source of truth
- GitHub `kushiiitd05/culinarystate`: every branch is already contained in `kush/s169-seal-p1b` (checked
  2026-11-08 18:19 IST: 0 commits outside it). `main` is 165 commits behind that branch → **one PR merge
  `kush/s169-seal-p1b` → `main` gathers the whole stack.**
- Orchestrator branch: `max/s176-orchestration`, created from `kush/s169-seal-p1b` @ `07fc0d2`, in the worktree
  `~/kush_work/culinarystate/.orch` on manjot (the `~/kush_work/culinarystate` folder itself stays the Mac's
  rsync target and is not written by the orchestrator).
- Delivery: git bundle (and a push if Kush supplies a write token); the Mac merges and pushes.

## Who does what until the branch is merged
| Owner | Work |
|---|---|
| Server orchestrator (manjot) | non-heat process families L1/L2 (lane L-NH); lot-state layer [K] steps 1–3 (L-LOT); FDA pH registry (L-PH); sourcing of Layer-2 defaults and mechanism condition windows (L-SRC); answers to the review packet (REV-A science, REV-B evaluation/governance); SSOT-vs-repo component consensus (9 topic agents + 3 reviewers); SSOT v16 draft; deployment/presentation plan |
| Mac coding agent | BBC Good Food jobs only (D-003); vinayak jobs; git merge/push of the orchestrator bundle; scribe for human gates (M2, M3, M5, M7 signatures and labels); nothing in the paths below until the bundle is merged |
| Kush + Parv | M2 07.A-R1 prereg signature + labels; M3 ascorbic-acid row verification + 5 PDF downloads; M5 benchmark prereg + review; P1b nonce; Step 35 signature; 15a freeze approval; 29-diag prereg signature; M6 host account + LLM key; approval of SSOT v16 |

Paths owned by the orchestrator branch (please do not edit on the Mac until merged): `src/culinarystate/lotstate/`,
`src/culinarystate/simulation/nonheat_*`, `tools/nonheat_*`, `tools/lotstate_*`, `tests/unit/test_nonheat_*`,
`tests/unit/test_lotstate_*`, `registry/scenario_defaults_nonheat_v1.csv`, `registry/scenario_defaults_source_review_S176.csv`,
`registry/mechanism_condition_windows_draft_v1.csv`, `registry/food_ph_fda_*`, `registry/ing_sr_legacy_*`,
`registry/component_ledger_v1.csv`, `reports/orchestration/`, `reports/lotstate/`, `reports/step26/nonheat_*`,
`docs/SSOT/computational_gastronomy_master_ssot_v16_0*.md`, this file.

## Numbering
- WORKLOG: the branch logs from **S175**. If the Mac logs more sessions before merging, renumber on merge (ids are
  never reused; keep both entries).
- DECISIONS: proposals on this branch start at **D-078**; same rule on merge.

## Rules kept
§141 output contract; UNKNOWN ≠ 0; Layer 1 / Layer 2 never mixed (D-077); protected ledgers byte-identical;
R-05, R-13, R-20; D-003 (no BBC on servers); D-071 limits (no AI signatures, nonces or human-only facts);
counts-only committed outputs; every run logged in `registry/compute_runs_v1.csv`.
