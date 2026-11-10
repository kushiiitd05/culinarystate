# S179 board update brief from the Mac agent (for the orchestrator)

The board (`registry/execution_board_S178.csv`) is edited only by the orchestrator. This brief lists items the Mac
agent moved on 2026-11-10 (`kush/s179-finish-fixes`, PR #12), with evidence, for the orchestrator to apply.

Every status below is an **agent proposal**. Items whose acceptance needs a human read stay PARTIAL until that read.

| Item | Proposed status | Evidence | Still needed |
|---|---|---|---|
| T4-C11-R1 (MUST) | DONE | BBC non-heat census `reports/step26/nonheat_L1_A1_full_S179_v06.json` (RUN-S179-BBC6-003); non-BBC v06 RUN-S179-PHYS6-012..015 | none |
| T0-C07-R2 (MUST) | DONE (draft in report) | `reports/final/sections/S179_hypothesis_and_task_crosswalk_DRAFT.md` §1 (80a8cdc) | moves into the report at assembly |
| T0-C11-R3 (MUST) | DONE (draft in report) | same file, §2: D5 covers SSOT Tasks 1, 2, 8 and part of 9; 4 and 6 only through one 5-question block; 3, 5 and 7 not at all | D-008 merge decision (human) |
| T9-C28-R1 (MUST) | DONE (D-079: Kush read and accepted) | `reports/final/sections/S179_licence_and_split_labels_DRAFT.md` §1 (50314ff) | T9-C28-R2 grep once slides exist |
| T9-C09-R3 (MUST) | DONE (draft) | same file, §2: split label per recipe-level result; none is source-family-disjoint | re-run the D5 rows after the freeze |
| T3-C15-R1 (SHOULD) | DONE (draft) | `reports/step19/pilot_iaa_report.md` (35dca96): HANDBOOK_REVISION_REQUIRED, label_basis visible | none |
| T3-C11-R1 (SHOULD) | DONE | `reports/del3/compiler_vs_gold_pooled_S179.{json,md}` (RUN-S179-GOLD-001; code 763eca6, d56f4a0, 483efe0) | none (see the note below) |
| T3-C17-R2 (SHOULD) | DONE (table; figure pending slides) | `reports/del3/event_type_table_S179.json` (RUN-S179-GOLD-002; code 7177b9e) | figure belongs to the slides (paused) |
| T9-C16-R1 (MUST) | DONE (draft) | `reports/final/sections/S179_D3_state_tracking_DRAFT.md` (0c93a21) | none |
| T9-C08-R4 (MUST) | DONE (D-079: Kush read and accepted; Parv not recorded) | NEG-0050 added (a2bad19); G08-3 already NEG-0047 | report cross-reference at assembly |
| T2-C14-R1 (SHOULD) | DONE | `reports/s179/seal_integrity_check_S179.json` (RUN-S179-SEAL-001; code 887a4df): 6/6 PASS, including byte-identical re-derivation of the reserved list; a private access log was started beside the sealed list | none |
| T8-C15-R3 (SHOULD) | DONE | RUN-S179-PIN-001: run-host digest `845dbda0…` for qwen2.5:7b-instruct on vinayak (Ollama 0.30.8) plus prompt registry sha `bc5766b7…` (`--check` clean), in the run CSV | re-check the digest at D5 run time |
| T7-C01-R5 (SHOULD) | DONE (table); Route B host open | `reports/s179/env_inputs_three_hosts_S179.md` + Mac / vinayak JSONs (RUN-S179-ENV-001/002) | human: Route B host (Mac is the only host with every input and package) |
| T9-C11-R1 (SHOULD) | DONE | `registry/experiments_S171_S175.csv` (288ae11) and `tests/unit/test_s179_experiments_registry.py`; EXP ids left NOT_ASSIGNED | orchestrator assigns the EXP ids |
| T9-C11-R2 (SHOULD) | DONE (audit); CSV edit is yours | `reports/s179/run_log_gap_audit_S179.md` (6f7b5e7): 0 empty status; 12 empty hashes, all declared (3 say only "(deleted)"); 27 rows lack start / end, each with an end upper bound from the row's first commit | orchestrator: put the bounds in `notes`, or leave them |
| T9-C30-R1 (SHOULD) | DONE (D-079 accepted) | `reports/s179/dod_scorecard_S179.md` (96a58df): 38 rows; 6 MET, 21 PARTIAL, 10 NOT_MET, 1 NOT_STARTED | none |
| T5-C07-R5 (SHOULD) | DONE (D-079, H4) | UNIT schema additive enum (KINETIC; RATE_PER_TIME, ENERGY_PER_AMOUNT); UNIT-000075..085 minted (RUN-S179-UNIT-001); `tests/unit/test_s179_unit_kinetic_ledger.py`; full Mac suite 5,405 passed | kcal/mol stays UNKNOWN until a calorie convention is declared; calorie rows NEEDS_SOURCE |

Notes:
- **Two findings that change the board's wording.**
  - The "40 AI-assisted dev-Gold recipes" are pilot_20 v1.1 (BBC) plus Food.com AI-assisted v1.1. The
    `evidence_first_expansion` drafts hold 0 step events, so they cannot score events.
  - `tools/eval_compiler_vs_gold.py` scores the rule compiler, not the Step 17b Rung A EventGraph. Scoring Rung A
    itself needs an adapter that does not exist.
- **Hash changes to note.**
  - `ledgers/data/UNIT.jsonl` sha256 is now `2073074d…` (was `c7b317ae…`). The table in
    `handoff/DEPLOYMENT_AND_PRESENTATION_PLAN_2026-11-08.md` needs that row refreshed. The Rung A lexicon fingerprint
    is unchanged, because it reads only MASS / VOLUME / COUNT units.
  - Pre-existing drift, not fixed: `src/culinarystate/ledgers/registry.py` has three KGE predicates
    (ING_HEALTH_ASSOCIATION, ING_COSYLAB_CATEGORY, ING_CARBON_FOOTPRINT) that the committed `KGE.schema.json` lacks.
- **No agent item with all dependencies met is left open.** Slides, the report skeleton and the dry run stay paused
  under "core before demo". Everything else waits on a human act: signatures, the D5 freeze, H4/H8 decisions, reads.

## Round 3 (2026-11-10): D-080 to D-082, the 52 human-blocked MUST items

Kush wrote "all 52 human prv and ksh approvdd". Under D-071 and the persona line, ksh and prv may decide items of type
**choice** (tighten, defer, withdraw or refuse) but may not loosen, close or sign.

**Proposed DONE (13 MUST).** These choice items are recorded in D-080 and D-081 with the pack's recommended text:
- T3-C22-R7 (Q39 deferred);
- T7-C01-R2 (Step 35 designed, not run);
- T8-C06-R2 (e5-large-v2, revision `f169b11e…`);
- T8-C12-R1 ("uncalibrated");
- T9-C12-R1 (power note);
- T3-C17-R1 (no D3 accuracy claim);
- T5-C05-R4 (Q20 / Q22 / Q23);
- T3-C07-R3 (presence-only);
- T4-C09-R1 (limitation);
- T4-C22-R1 (EVD-row arm only);
- T8-C02-R2 (SEMANTIC abstains);
- T9-C26-R2 (fallback levels L0-L3);
- T5-C05-R1, the G23.2 property test: 10,500 randomised queries, 0 failing (RUN-S179-PROP-001; hypothesis was already in the Mac env, D-080 #20).

**Proposed DONE (SHOULD and other items).** T9-C25-R5 (install: nothing to install), T9-C25-R3 (VPN worked), the
D-008 merge, the Route B host (the Mac), A1, A3, #7, and the 29-diag / AA options (D-082).

**Prereg edit lock, T9-C26-R5 (MUST): still PARTIAL.** The S178 amendments are applied in place to the D5, 29-diag and
AA DRAFT files (`tools/s179_apply_prereg_amendments.py --check` reproduces them). Two things remain open:
- the 07.A-R1 ruling (#2, HUMAN);
- D5 sidedness D-D5-6. One-sided would loosen the test, so it is a human choice.

**Still BLOCKED_HUMAN (39 MUST).** These cannot move on any persona approval:
- 7 signatures: 07A-R1, AA, 29-diag, D5 (Kush and Parv), H8 register;
- 2 freezes: 15A-BOOT, §141 crosswalk;
- human labour: the 07A-R1 labels and adjudication, the 5 PDFs and licence checks, the CAL and SIM-VAL verification, the 100-question review, the 30-claim blind audit;
- facts: Prof. Bagler's permission, calendar, contributions and date;
- gate-loosening decisions: #10, #14;
- every agent run downstream of these (29-diag run, PARAM, fit, H1 / H3 / D4 scoring).

**Process flag.** The pack's proposed rule (§2.2, not yet in force; A4) says HUMAN-type entries are committed by the
human from their own session. D-079 decision 2 (the H4 UNIT enum, pack type HUMAN) was entered by the agent as scribe
on Kush's chat instruction, as D-069 / D-070 were. If A4 is adopted, Kush should re-confirm D-079 in his own commit.

## Round 4 (2026-11-10): D-083, the 29-diag code

- **D-083.** ksh and prv chose the two-sided D5 H3 sign test, the stricter option. The D5 prereg now has no open
  option. T9-C26-R5 is still PARTIAL, waiting only on #2, the 07.A-R1 ruling, which is HUMAN.
- **T6-C02-R1: proposed DONE.** The ladder crosswalk, the prereg text and the runner now use the same rung names.
  XW-04 (B-2) is now EXACT and implemented; XW-05 (D3) is labelled OK.
- **29-diag code promised by the amended prereg**: B2 ingredient mean, S-5
  food-group-disjoint split, D2-vs-B2 contrast, cap sensitivity, and the imputation-duplicate control.
  - Where it lives: `evaluation/diag29_additions.py`, wired into `diag29_runner`; DEL-2's `all_models` is unchanged.
  - Tests: 8 new; 410 passed across the transition, diag, bakeoff and crosswalk tests.
  - The run itself (T6-C03-R3) still needs Kush's 15A-BOOT freeze approval and his 29-diag signature.
- **No MUST item is now open to agents alone.** Every remaining one waits on a signature, a freeze, human labelling,
  review or verification, the 5 PDFs, or a human fact.
- **Kush asked for all of it to be completed through ksh and prv. That was refused for those acts (D-071).**
