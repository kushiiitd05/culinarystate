# Resume anchor — 2026-11-03 cloud run (S154 → S160), STOPPED AT CHECKPOINT H-A

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
| 7 | `cloud/s160-freeze-prep` | see the update below | D-049..D-052, signed 26.0 selection (sim_aa_1), 15.0 draft, 15a.R seal tool, Step 35 v2 package, evaluation scaffolds |

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

## Update — S160 complete, run stopped (2026-11-03)

- **S160 is done and pushed.** Build note: `reports/step15/S160_build_note.md`. Full suite: 3185 passed, 17 skipped, 1 deselected; the 1 failed + 11 errors are the missing bundle files. Ledger guard 7/7.
- **The cloud run stopped here at Kush's request.** Nothing is running; no agent is active.
- **Checkpoint H-A is block I of the review sheet:**
  - 15.0 rulings, including the RESERVED fraction and the seed policy;
  - the Step 35 v2 signature: protocol `009c9047ce78da21dd7d7061a64bc9fbb86d38d3eada5b3d8c9769ce5dd60145`, UNSIGNED record `8885a63a0dc0181d4aec5d05fea124776d6a0afbbe5a1e162da7cbb9a4b582e5`, with P-1..P-5, S-1/S-2 and Route A/B;
  - the scaffold values (δ_30, ρ, c_floor, 34c thresholds).
- **To resume:**
  1. Record the H-A answers as new DECISIONS entries (D-053 onward), quoting the humans' own words.
  2. The 15.0 entry must use the seal's marker lines: `RESERVED_FRACTION`, `RESERVED_UNIT`, `RESERVED_STRATIFY`, `SEED_SHA256`, and an Approver line naming Kush.
  3. Signing Step 35 means creating `reports/step35/preregistration_35_0_v2_package.sha256.SIGNED.json`, committed from the signer's own session (O5).
  4. Then run C1 and C2 where the data bundle exists, then H-B and S161–S163.

## Update — 2026-11-04 (fix for Parv's Mac test failure)

- **Problem:** two Step 35 v2 package tests failed on the Mac because they assumed the three Mac-only recipe files were absent. The fix is in `1276cae`; the tests now pass on both the cloud and the Mac. No data, record, signature or threshold changed.
- **Branch to resume from:** `cloud/s160-freeze-prep` (the latest; it contains S154–S160 plus this fix).
- **Next step for whoever starts:** checkpoint H-A, which is block I of `handoff/REVIEW_SHEET_AI_VERDICTS.md`. Nothing else is in progress.
- **First commands when resuming:**

```bash
git fetch origin && git checkout cloud/s160-freeze-prep && git pull
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest tests/unit -q
```

On the Mac with the data bundle, the 12 cloud-only data failures should also pass. Report any other failing test.

## Update — 2026-11-04 evening: real-data runs done (branch `cloud/s161-real-data-runs`, WORKLOG S162)

- **Numbering:** the branch and report are named S161 as Kush asked; the WORKLOG entry is S162, because S161 was already used by the Mac test fix earlier the same day.
- **Data bundle:** downloaded in the cloud after Kush allowed `drive.usercontent.google.com`; checksums OK; 3,814 macOS `._*` files removed; baseline 7/7.
- **Done on real data** (details in `reports/step16/S161_real_data_runs.md`):
  - Step 16 rc2 grounding: 612,782 recipes, 4,281,956 lines, 0 exceptions, invented grams 0;
  - Step 17b, seed 20261104, 1,000 sample: invented_count 0 after the test-first `ºF`/`ºC` auditor fix (23 before);
  - 12.0 proposed rows, 12-local staging, 13a-0 seed corpus.
  - Not finished: the extra full-corpus Rung A run (stopped at the cloud's 2 h limit); rerun it on the Mac if wanted.
- **Tests with data:** 3215 passed, 2 skipped, 1 deselected, 0 failed.
- **D-053:** Kush and Parv accepted the block I AI recommendations. Still open: the RESERVED fraction and seed; δ_30, ρ, c_floor and the 34c values; P-1..P-5, S-1 and S-2; the Step 35 signature (Route B, committed from the signer's own session).
- **Branches:** s154–s160 are contained in `main` (PR #2). Kush chose to delete the nine old branches; the git proxy refused the delete from the cloud, so Kush deletes them on GitHub.
- **Resume point:** checkpoint H-A remainder, then C2 (rebuild the P1 frame and strata with data, then the draw, on Kush's go) and C1 (after the Step 35 signature).

## Update — 2026-11-05: full-corpus Rung A done; Parv's local runs merged (PRs #4, #5; WORKLOG S163)

- **Full-corpus Step 17b Rung A** ran on vinayak-server (CPU only, no GPU). The data went there as a 14-part Drive bundle, because the VPN dropped rsync and scp.
  - Result: 612,782 recipes, 0 exceptions, baseline check PASS.
  - invented_count **626 → 4 → 0** after two test-first auditor fixes: the `deg`/`degree` prefix before C/F, and lowercase c/f. These were false positives.
  - V2 `INVERTED_INTERVAL` 4,511 in 3,848 texts. Report section 3.2b.
  - The tool's own full rerun on `a567a92` gives invented_count 0, exceptions 0 (`reports/step17/rung_a_dryrun_counts_full_corpus_final.json`).
- **Parv's branch `parv/local-real-runs-2026-11-04` is merged (PR #5).** Parv started from `8759550`, in parallel with S162.
  - 6 of Parv's files were byte-identical to PR #3.
  - The 17b conflict was resolved to main's post-fix file; Parv's pre-fix copy has the same totals as `_prefix_S161`.
  - New from Parv:
    - **Step 19 P1 frame rebuilt and drawn under D-048** (21 rows, 7 strata), so **C2 is done**;
    - the packet maker and annotator B's packets;
    - the **15.0 draft** for Kush's signature (1/5, STUDY_THEN_CELL, SOURCE_FAMILY, seed hash `d3075c68…`, seed on Parv's Mac);
    - the 26g census on a real 1,000 sample;
    - the Step 30 exploratory bake-off (DIAGNOSTIC_ONLY, not citable);
    - the Step 34a attempt (refused: 34a.0, ρ, c_floor).
- **Resume point, in unblocking order:**
  1. Kush signs 15.0 as a D-054 entry (Approver Kush).
  2. Run the 15a.R check and seal on Parv's Mac.
  3. Build annotator A's P1 packets on Kush's Mac.
  4. P1 annotation (both).
  5. δ_30, ρ, c_floor, the 34a.0 circularity check and the 34c values.
  6. Step 35: P-1..P-5, S-1, S-2, then the signature from the signer's own session (unlocks C1).
  7. Reviews: 12.0 rows / D-049 re-baseline, G12 audit, V2 intervals.
  8. Expert: EQ21-01..14 and the 26.0 inputs.
- **Lessons:**
  - The 8 GB Mac cannot run the full test suite or a full-corpus run (it swaps). Use the server.
  - Large Mac→server transfers: minimal bundle → 50 MB parts → Drive folder → `gdown`.

## Update — 2026-11-06 00:55 IST: day closed after S165; sequence for the next session

- **Branch to resume from:** `kush/s164-step19-salt-commit` (head `b74eb51` before this anchor commit), pushed, **PR #8 open** (S165: Step 19 packet salt, guards and commit step; V2 census). Main is at PR #7. Nothing is running on the Mac or on vinayak-server.
- **Stray file:** `tests/unit/.probe` (empty, untracked, from 2026-10-27). Not part of any session; delete or ignore.
- **Mac note:** after a macOS update the terminal lost Desktop access (TCC, `Operation not permitted`); fixed under Privacy & Security → Files and Folders. Check this first if git fails with that error.

### Order for tomorrow (each step unblocks the next; A = agent, K = Kush, P = Parv)

| # | Who | Task | Unblocks | Done when |
|---|---|---|---|---|
| 1 | A → K | Review PR #8 against main; run the step19/pilot/gold/annotation/s163/s164 subset on the Mac and the full suite on vinayak-server; Kush merges | everything below builds on main | PR #8 merged, suite green apart from the known server-only failures |
| 2 | K | Generate the 15a.R seed in Kush's own session (seed custody, block J5; Parv's agent-made seed `d3075c68…` is not used unless Kush says so) | 3 | seed file private, only its sha256 known |
| 3 | K (A records) | D-054: sign 15.0 with the seal's marker lines `RESERVED_FRACTION`, `RESERVED_UNIT`, `RESERVED_STRATIFY`, `SEED_SHA256`, Approver Kush; record the Step 30 bake-off as a pre-seal deviation (J8) | 4 | D-054 in DECISIONS with Kush's own words |
| 4 | K | `tools/step15a_R_seal.py` check, then seal, on Kush's Mac | 29-diag, Step 30 | seal record committed, check reports 0 blockers |
| 5 | K + P (parallel with 2–4) | P1 salts (private 0600 file outside the repo; commit only `salt_P1_<letter>.sha256`); Kush builds annotator A packets; Parv re-issues B with his salt | 6 | both packet sets issued, packet maker refusals clean |
| 6 | K + P | P1 annotation, then `tools/step19_commit_step.py` snapshots/commitments per wave | H-B, pilot scoring | commitments_<letter>_<wave>.json for both |
| 7 | A | Write the auditor code commit (`a567a92`) into the Step 17b reports (JSONs + 3.2b) | traceability | reports name the exact code commit |
| 8 | A | Build a committed, test-first Step 26g census tool; run it on vinayak-server on the fixed Rung A output (counts only) | J8 closed, block E | tool + tests + counts JSON committed |
| 9 | K + P (A drafts the sample) | J4 human sample of V2 `INVERTED_INTERVAL`, focused on the `9-9/9 <unit>` shape (~94 %); then decide the rc2 quantity-grammar change (versioned, test-first) | Step 16/17 quality | decision recorded as a DECISIONS entry |
| 10 | K + P | Block I values: δ_30, ρ, c_floor, 34a.0 circularity check, 34c thresholds | Step 30/34 | values recorded with the humans' words |
| 11 | K + P | Step 35: P-1..P-5, S-1/S-2, then Route B signature from the signer's own session | C1 (explicit baselines) | `preregistration_35_0_v2_package.sha256.SIGNED.json` committed |
| 12 | A | After 6 and 11: H-B review pack, pilot scoring/16c audit, C1 runs on the server | final report | — |

- **Optional, low priority:** a sharded Step 17b tool (the current one is single-process, ~3.5 h, ~3.3 GB in memory).
- **Still open, outside this order:** expert EQ21-01..14 and the 26.0 inputs; 12.0 review / D-049 re-baseline; G12 audit; old branches s154–s158 to delete on GitHub.
- **Deadline:** presentation 25–26 Nov. Aim for annotation (6) to finish by ~Nov 15 and C1 (12) by ~Nov 19, leaving ~Nov 20–24 for the report, figures and slides. The report states every gate as it is (G08-3 FAIL, 07.A FAIL stay).

### First commands next session

```bash
cd ~/Desktop/CGAS/culinarystate && git fetch origin && git checkout kush/s164-step19-salt-commit && git pull
gh pr view 8
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest tests/unit -q -k "step19 or pilot or gold or annotation or s163 or s164"
```

Run the full suite on vinayak-server only (VPN first); the 8 GB Mac swaps.
