# S179 board update brief from the Mac agent (for the orchestrator)

The board (`registry/execution_board_S178.csv`) is edited only by the orchestrator. This brief lists items the Mac
agent moved on 2026-11-10 (`kush/s179-finish-fixes`, PR #12), with evidence, for the orchestrator to apply.

Every status below is an **agent proposal**. Items whose acceptance needs a human read stay PARTIAL until that read.

| Item | Proposed status | Evidence | Still needed |
|---|---|---|---|
| T4-C11-R1 (MUST) | DONE | BBC non-heat census `reports/step26/nonheat_L1_A1_full_S179_v06.json` (RUN-S179-BBC6-003); non-BBC v06 RUN-S179-PHYS6-012..015 | none |
| T0-C07-R2 (MUST) | DONE (draft in report) | `reports/final/sections/S179_hypothesis_and_task_crosswalk_DRAFT.md` §1 (80a8cdc) | moves into the report at assembly |
| T0-C11-R3 (MUST) | DONE (draft in report) | same file, §2: D5 covers SSOT Tasks 1, 2, 8 and part of 9; 4 and 6 only through one 5-question block; 3, 5 and 7 not at all | D-008 merge decision (human) |
| T9-C28-R1 (MUST) | PARTIAL | `reports/final/sections/S179_licence_and_split_labels_DRAFT.md` §1 (50314ff) | human read of the paragraph; T9-C28-R2 grep once the slides exist |
| T9-C09-R3 (MUST) | DONE (draft) | same file, §2: split label per recipe-level result; none is source-family-disjoint | re-run the D5 rows after the freeze |
| T3-C15-R1 (SHOULD) | DONE (draft) | `reports/step19/pilot_iaa_report.md` (35dca96): HANDBOOK_REVISION_REQUIRED, label_basis visible | none |
| T3-C11-R1 (SHOULD) | DONE | `reports/del3/compiler_vs_gold_pooled_S179.{json,md}` (RUN-S179-GOLD-001; code 763eca6, d56f4a0, 483efe0) | none (see the note below) |
| T3-C17-R2 (SHOULD) | DONE (table; figure pending slides) | `reports/del3/event_type_table_S179.json` (RUN-S179-GOLD-002; code 7177b9e) | figure belongs to the slides (paused) |
| T9-C16-R1 (MUST) | DONE (draft) | `reports/final/sections/S179_D3_state_tracking_DRAFT.md` (0c93a21) | none |
| T9-C08-R4 (MUST) | still PARTIAL | NEG-0050 added (a2bad19): DEL-2 D7 equals D1 on raw-scale Phenol-Explorer in 5 of 5 splits. G08-3 was already NEG-0047 | Parv and Kush read; report cross-reference |
| T2-C14-R1 (SHOULD) | DONE | `reports/s179/seal_integrity_check_S179.json` (RUN-S179-SEAL-001; code 887a4df): 6/6 PASS, including byte-identical re-derivation of the reserved list; a private access log was started beside the sealed list | none |
| T8-C15-R3 (SHOULD) | DONE | RUN-S179-PIN-001: run-host digest `845dbda0…` for qwen2.5:7b-instruct on vinayak (Ollama 0.30.8) plus prompt registry sha `bc5766b7…` (`--check` clean), in the run CSV | re-check the digest at D5 run time |
| T7-C01-R5 (SHOULD) | DONE (table); Route B host open | `reports/s179/env_inputs_three_hosts_S179.md` + Mac / vinayak JSONs (RUN-S179-ENV-001/002) | human: Route B host (Mac is the only host with every input and package) |
| T9-C11-R1 (SHOULD) | DONE | `registry/experiments_S171_S175.csv` (288ae11) and `tests/unit/test_s179_experiments_registry.py`; EXP ids left NOT_ASSIGNED | orchestrator assigns the EXP ids |

Notes:
- **Two findings that change the board's wording.**
  - The "40 AI-assisted dev-Gold recipes" are pilot_20 v1.1 (BBC) plus Food.com AI-assisted v1.1. The
    `evidence_first_expansion` drafts hold 0 step events, so they cannot score events.
  - `tools/eval_compiler_vs_gold.py` scores the rule compiler, not the Step 17b Rung A EventGraph. Scoring Rung A
    itself needs an adapter that does not exist.
- **Next agent items with no blocking dependency.** T9-C30-R1 (DoD scorecard) and
  T9-C11-R2 (run-log gaps). Slides and the dry run stay paused under "core before demo".
