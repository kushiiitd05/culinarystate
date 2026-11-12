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

## Round 5 (2026-11-10): agent items after D-083

**Proposed DONE:**
- **T6-C19-R1 (MUST):** an environment lock, smoke import and transition tests on the Mac, manjot and vinayak, all at
  `440dbeb` (`reports/s179/env_lock/`, RUN-S179-ENV-003..005).
  - Mac 56 / 56 and vinayak 56 / 56 pass.
  - manjot: 53 pass and 3 fail, because sklearn is not installed and no installs are allowed (D-080 #20).
- **T6-C02-R2:** the "test_transition hang" is not reproduced. The file takes 3 s on the Mac and at most 41 s on any
  host.
- **T9-C24-R1:** `reports/final/RELEASE_CARD.md` (SSOT 257A.16, 5 artefacts, UNKNOWN where unknown).
- **T7-C22-R1 and T7-C20-R1:** `reports/step35/35h_decision_record_level{12,13}_v1.md`. Every SSOT box has a status
  and evidence; "learned rungs deferred; entry rule LR-1..LR-5" is stated in both.
- **T4-C11-R3:** already met by the v06 non-heat runs (RUN-S179-PHYS6-012..015, BBC6-003).

**Infrastructure:**
- `tools/human_sign.py` is for the signers only; the agent never runs it.
- The KGE schema JSON was regenerated from the registry, and `test_s179_schemas_match_registry` prevents future drift.
- manjot and vinayak copies were updated by bundle to `440dbeb`.

**Open design item, not built:** scoring the Rung A EventGraph against the gold-1.0 sets needs a documented mapping
from EngineEvent kinds to gold event types. That is a design choice, so it was not invented here.

**Signatures:** Kush reported "all signed and passed ok by Parv". No signature file exists in any branch, and the
15A-BOOT freeze is still PROPOSED. Each signer runs `tools/human_sign.py` in their own session and commits the
result. The Parv files must come from Parv.


## Round 6 (2026-11-11): Parv local continuation, acceptance audit and report assembly

Anchor: `65298da`, `kush/s179-finish-fixes`. Every status is an AI proposal; no new human act is inferred.
The complete acceptance table is `S179_round6_acceptance_audit.csv` and its Markdown companion, with original
acceptance text, gaps, next actions and evidence hashes. **252 unique rows: 84 MUST, 168 SHOULD; 51 POST retained.**
The supplied takeover list repeats T8-C20-R3 once; expanded ranges cover every MUST. VERIFY choices are resolved
from existing D-080/D-084 decisions; no new decision or frozen-science edit was needed.

MUST statuses: 24 DONE, 8 DONE_AI_DELEGATED, 8 DONE_DRAFT, 4 DONE_WITH_DEVIATION, 25 PARTIAL, 5 OPEN,
4 NOT_RUN_BY_DECISION, 2 BLOCKED_DATA, 2 BLOCKED_HUMAN, 1 DEFERRED, 1 ONGOING. These categories are not interchangeable;
there is no claim of 44 fully satisfied independent-human or scientific gates.

Completed local artifacts:
- D1, D4, H2/lineage sections; current hypothesis/task crosswalk; seven preregistered 29-diag memos.
- AA identifiability diagnostic from frozen OLS summaries, with 10 new tests and separate small-sample t intervals.
  No refit, SIM-VAL access or practical precision gate pass. Model A remains NOT_VALIDATED/RESEARCH_ONLY.
- Integrated report `reports/final/FINAL_REPORT_DRAFT_S179_2026-11-11.md`, Markdown slide draft and updated release
  card. Final author edits, contributions, deck export, final leakage checks and timed rehearsal remain pending.
- D5 P3 evidence-boundary amendment PROPOSAL only; original H3 failure retained, no amended experiment executed.
- Proposed schedule through 24 Nov; availability and presentation facts remain unconfirmed.

Verification: baseline 7,906 passed / 8 failed / 13 errors; fixed three stale test assumptions (version provenance,
PROPOSED fixture versus live FROZEN record, and explicit D-085 delegate lock).44 targeted tests pass;83 socket tests
pass with localhost permission. Final complete rerun: **7,926 passed, 1 failed, 11 errors, 14 skipped, 44 deselected**.
Every remaining failure/error is missing local `recipe_identity_features_v1.parquet` or Food.com recipes input.
No missing-input test was skipped or removed. Counts/hashes: `reports/s179/parv_verification_2026-11-11.json`;
actual Python 3.11.9 package lock in `reports/s179/env_lock/parv_S179_2026-11-11.*`.

Important report corrections: frozen raw H1 is NOT_COMPUTED; the separate rung-blind supplement/D-092 records
RULE_NOT_MET. Compatible-recall values contradict their frozen note; no compatible-recall claim is made.
Router accuracy covers only 10 gold-branch questions. The family-stratified retrieval diagnostic is not a
train-source-heldout experiment. Original results and protected ledgers remain unchanged.

Next: restore private/local inputs, then CAL/Model B and separate-session SIM-VAL; PARAM/calibration provenance and
T5 G15 scorecard; full emission-contract scan; new frozen split registry; final report/deck leakage comparison.
Post-19-Nov MPU and actual 24 Nov rehearsal cannot truthfully be completed on 11 Nov. No SSH until current VPN/host/path
confirmation. Parv asked to defer private-file questions until this local batch is complete.


## Round 7 (2026-11-11): private sources restored; AA closeout evidence

See `reports/orchestration/S179_round7_private_transfer_update.md` for the item-by-item supplement.
All 15 transferred files match the manifest and remain local-only. Model B and CAL sensitivity dispositions are
complete with explicit licence and assay exclusions. Separate-context SIM-VAL extraction plus second AI source
precheck found zero computationally eligible rows; no primary prediction/error result is manufactured.
The 13-gate T5 scorecard has zero PASS. PARAM/calibration and real SIMULATE retain their existing requirements.
Report/deck updates and draft model card disclose these outcomes. No decision or scientific freeze was changed.

Final full verification: 7,975 passed, 1 failed, 11 errors, 13 skipped, 44 deselected; all remaining failure/errors missing
identity-features/Food.com inputs. 48 new tests plus 21 independent provenance/CLI tests pass. The expanded local
source-window scan finds zero 12-word matches in seven artifacts against five supplied source files, with
release_clearance=false. Final exports, absent corpora, short excerpts/paraphrases/images remain outside that scan.


## Round 8 (2026-11-12): answer provenance engineering audit

T0-C06-R2 remains PARTIAL. All 346 frozen answers were scanned, including raw baselines; 1,000 metadata-template
public-demo calls include 200 synthetic recipe requests. After correcting source-name false positives in the
instrument, v2 flags 30 saved records (B0:4, B2:8, B5:18) and no demo calls; B5T/B7 have no lexical flags.
Only 173 calls reach TRANSFORMATION, 36 return recipe payloads and 51 physical steps are serialized. This is
neither an accuracy result nor a semantic/applicability certificate or representative user/recipe sample.

The path inventory, original audit, corrected v2, limitations and runtime-hardening proposal are under
reports/s179/emission*. NEG-0052 records the engineering finding without changing D-092. Full suite: 7,996 passed,
1 failed, 11 errors, 13 skipped, 44 deselected; remaining failures/errors are missing local data. All 21 new tests pass.
No original frozen answer, score, preregistration, prompt, protected ledger or production generation code changed.
The source-path agent supplied a draft before a service limit; root completed the instrument and checks without
claiming independent expert verification. Private source material remains local-only.
