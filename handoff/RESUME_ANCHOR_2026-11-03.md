# Resume anchor — 2026-11-03 cloud run (S154 → S160)

Read this first when resuming. Then read `STATUS.md`, the WORKLOG tail (S154–S159),
`DECISIONS.md` D-045 to D-052 and `handoff/REVIEW_SHEET_AI_VERDICTS.md`.
The plan being executed is Kush's cloud-prompt sequence S154 → S163, with checkpoints H-A and H-B and the conditional sessions C1 and C2.

## Branches (stacked; merge in this order after checking locally against real data)

| # | Branch | Head at anchor | Content |
|---|---|---|---|
| 1 | `cloud/s154-step16-integration-2026-11-03` | a8314ff | Step 16 rc2 grounding, history check, rc2 dry-run, Step 19 pilot gate |
| 2 | `cloud/s155-step17ab` | d026b80 | Step 17a interfaces/validators/auditor, 17b Rung A; D-045, D-046, THR-19P signed |
| 3 | `cloud/s156-step18-events` | 0182967 | Step 18 event log/replay/adapter, 26g sim-input contract; D-047, D-048, signed pilot start record |
| 4 | `cloud/s157-evidence-machinery` | e1efc17 | Step 09 queue, 12.0 proposed rows, 12-local parsers, 13a-0 seed corpus |
| 5 | `cloud/s158-mechanism-stack` | e0b5702 | 04.3 KIN/KINPT v1.1, MECH v1.1, 22a signatures, 23a applicability |
| 6 | `cloud/s159-simulator-core` | 56d3cab | 24a FORM/PARAM/VAL, 26a fitting, 26b sim_aa_1/sim_chl_1, 26c verification |
| 7 | `cloud/s160-freeze-prep` | in progress | D-049..D-052 records, signed 26.0 selection (sim_aa_1); S160 work under way |

All branches start from main `2154406`. Each branch contains the one before it.

## Where S160 stands at this anchor

- **Done and committed:** D-049 (block F), D-050 (block G + scipy), D-051 (THR-04K signed), D-052 (block H; sim_aa_1 selected).
- **Running at anchor time** (AI worker "ksh"):
  - A. 15.0 pre-freeze rulings draft (options and recommendations only; no decision).
  - B. 15a.R RESERVED-group seal tool. It must refuse until a signed 15.0 decision exists, and is NOT run.
  - C. Step 35 v2 protocol package, hash-bound and unsigned, with a signature sheet. The baseline runner refuses until both sign.
- **Next:**
  - D (worker "prv"): harness scaffolds for 29-diag, 30, 34a and 34c, plus an AI review of A–C.
  - Then: the S160 build note, review-sheet block I, STATUS, WORKLOG and the push.
- **If the session was lost mid-S160:** check `git log cloud/s159-simulator-core..cloud/s160-freeze-prep` for what landed. Redo only the missing parts and keep test-first order.

## Working rules in force

- **D-045:** an AI verdict comes first; Kush and Parv review and their review is final. Agents "ksh" and "prv" are worker labels, never the humans.
- **Recording human input:** every human OK is recorded as a DECISIONS entry with the human's words; Parv's OK is relayed by Kush. Values (nonce, hours, coefficients) come from humans only.
- **Commits:** one commit per file, tests first, no Claude/Anthropic attribution, authored as Kush Tokas.
- **Push:** push each finished session (Kush, 2026-11-03).
- **Protected ledgers:** ledgers/data EVD, COND, SRC, MEAS and SNAP stay byte-identical (`verify_baseline` 7/7). The registry and DECISIONS are append-only, except for signing fields on threshold rows that humans approved.
- **Tests:** latest full suite is 2994 passed, 17 skipped and 1 deselected. The 1 failed + 11 errors are only the data-bundle files missing in the cloud.

## Human facts already supplied

- Pilot (D-048):
  - joint nonce `Houdini_loves_hustin_crepes_07|BlindedByTheRecipes_05`, committed 2026-11-03T15:01:16Z;
  - capacity 15 h/week each; budget 40 h each.
- Signed: THR-19P-01..35 (D-046) and THR-04K-01..04 (D-051).
- Selected: sim_aa_1 (D-052, before 11.D; one switch allowed after 11.D).

## Still needed from humans or the environment

1. **Checkpoint H-A** (after S160):
   - sign the Step 35 v2 package;
   - make the 15.0 rulings, including the RESERVED fraction;
   - decide whether to run the 15a.R seal;
   - review block I.
2. **Expert:** EQ21-01..14 (`reports/step21/S158_expert_questions.md`).
3. **26.0:**
   - exact "no-water-assay" design definition;
   - the pre-registration numbers;
   - Choi–Okos coefficients;
   - τ_h per size class;
   - M&S limits;
   - solver tolerances;
   - KiSAO id check.
4. **Open choices:**
   - FORM- vs MODEL- prefix;
   - the case set for 22c (to be authored, then sealed);
   - Bognar licence re-check;
   - re-baseline after a real 12.0 run (approved in principle, D-049).
5. **Environment:**
   - allow `drive.usercontent.google.com` (data bundle) and `www.enzyme-database.org` / `www.ebi.ac.uk` (source checks) under Network access;
   - the cloud container has no data, so every real-data run is pending.

## Real-data commands to run locally (counts-only outputs)

```bash
python tools/step16_rc2_grounding_dryrun.py --workers 8
python tools/step17b_rung_a_dryrun.py --seed <SEED>
python tools/step12_0_register_local_files.py
python tools/step12_local_stage.py --defaults
python tools/step13a0_seed_corpus.py
```

Pilot draw (C2), after rebuilding the frame and strata with data (both must be newer than the nonce commitment):

```bash
python tools/step19_real_pilot.py draw --record reports/step19/pilot_start_record.SIGNED.json --frame <frame.csv> --strata <strata.csv> --execute
```

## Remaining plan after S160

| Session | Content |
|---|---|
| H-A | Human checkpoint |
| C1 | Step 35 explicit baselines (needs the signed v2 package and data) |
| C2 | Pilot draw and packets (needs data; prerequisites met) |
| H-B | Model-assisted pilot labels reviewed by Kush and Parv (D-045 W2) |
| S161 | Pilot scoring and the 16c audit pack |
| S162 | Final report, figures and slide outline for 25–26 Nov |
| S163 | Consolidation and final handoff |

The final report states every gate outcome as it is, including G08-3 FAIL and 07.A FAIL, and makes no SOTA wording without measured comparisons.
