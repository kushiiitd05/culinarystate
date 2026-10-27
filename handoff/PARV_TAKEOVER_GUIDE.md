# CulinaryState: guide for Parv to take over for a few days

Written 2026-10-27 (after WORKLOG S145). Kush hands the day-to-day work to Parv for a few days. Plain words; every task has a file path. If something here disagrees with `STATUS.md` or the tail of `WORKLOG.md`, those win. Refresh this guide at the anchor (see the end).

## 0. What Kush must do BEFORE Parv starts (Kush's checklist)
1. **Push to GitHub** (`kushiiitd05/culinarystate`). The GitHub copy is far behind: it stops at commit `4c2c829`, the local copy is about 113 commits ahead. Nothing is pushed until Kush says so (law H7). Parv cannot see the new work until this happens.
2. **Check no Claude attribution** in the new commits: `declaude kushiiitd05/culinarystate --dry-run` after the push.
3. **Tell Parv to re-clone** (do not pull): the history was rewritten earlier, so an old clone will not merge.
4. **Give Parv the data that is NOT in git** (about 3 GB; `data/`, parts of `ledgers/`, EVD export v1 and the BBC files in `../a1`). It is packed by `tools/make_parv_data_bundle.sh` into `~/Desktop/PARV_DATA_BUNDLE/` (required 1.0 GB, recommended 10 MB, optional 2.0 GB, plus `SHA256SUMS.txt`). Upload that folder to Google Drive, share it with Parv only (it holds Food.com data: LOCAL research use only, never public), and paste the link into `~/Desktop/PARV_CLAUDE_PROMPT.md`. Extraction commands are in that prompt.
5. **Write the missing line**: Parv's own written confirmation of the 07.A and 07I-C adjudication ("I reviewed the disagreements and agree with Kush's labels") is still only relayed by Kush. Parv should put it in his own words in `docs/plan/H4_ANSWERS_LOG.md` (or a new file under `docs/plan/`), then commit it.
6. If Parv needs the GPU servers, give him access details yourself. This guide holds no passwords or usernames.

## 1. Set up (Parv, about 20 minutes)
```
git clone https://github.com/kushiiitd05/culinarystate.git
cd culinarystate
/opt/anaconda3/bin/python -m pytest tests/unit -q      # expect about 1,500 passed; test_transition has one old hang, deselect it
```
If Python lives elsewhere on Parv's machine, use any base conda environment with pandas, pyarrow, jsonschema 4.19 and pytest. Do not create new virtual environments (project rule). Read, in this order: `CLAUDE.md` -> `STATUS.md` -> the last 3 entries of `WORKLOG.md` -> `DECISIONS.md` from D-027 to the end (D-038 as of today).

## 2. The laws (never break these)
- Never fill in, guess or "fix" a human label. Never sign or approve for another person. AI review is not human verification.
- UNKNOWN is a valid answer. Never invent a scientific value.
- Ledgers are append-only; ids are never reused. `ledgers/data/EVD, COND, SRC, MEAS, SNAP` stay byte-identical (the guard `src/culinarystate/lineage/guard.py` checks this).
- No push to GitHub without Kush's explicit yes. No "state of the art" wording before gate H6.
- Recipe text from Food.com, BBC and the books never goes to an outside AI service and never into git.
- One commit per file, authored by the human whose session did the work. No Claude/Anthropic line in commits or files.
- Log each finished step with `python tools/log_step.py --block ... --title ... --did ... --files ... --verify ... --next ...`.

## 3. Where the project stands (short)
| Step | State |
|---|---|
| 07H-R / 07I-R | done (612,782 recipes parsed; identity layer) |
| 07.A (condition audit) | statistic FAILED (kappa paradox); steps that need it stay closed |
| 07I-C (duplicate calibration) | blind kappa 0.571 / 0.588; Kush states 0.88 on adjudicated labels (D-033). Operating points chosen on Kush's labels; recipe split groups exist in `ledgers/recipe_identity_v2/` (single-reviewer caveat) |
| 08a (source lineage) | built and run (D-032). Machine gates pass. **G08-3 (edge precision) FAILED** in the audit (D-034), so edges B2/B3 stay provisional. G08-9 (USDA vs Bognar overlap) waits for an expert reading |
| 08b-v0 (reusable library) | built (D-035). 08b v1 NOT authorised |
| 16a / 16b | draft vocabularies, draft schemas v1-rc, draft Deep-Gold frame and strata. Nothing frozen. 16c waits for Step 19 |
| 35 (representations) | pre-registration 35.0 drafted; code for the guard, cuisine rungs and recipe rungs built on fake data only. **Nothing runs on real data until 35.0 is signed** |
| Cuisine for Food.com | decided: derive from tags (D-036), pan-regional tags only at region level (D-037). Mapping is a draft, unsigned |
| 17 (instruction extraction) | not started; needs 16c; will need the A100 server |

## 4. What Parv can do alone (in this order)
1. **Review and, if he agrees, co-sign Step 35.0.** Read `reports/step35/35_0_signoff_sheet_DRAFT.md` (8 decisions). Signing is a record with both names and today's date, made with the guard described in `reports/step35/g35_pre_guard_README.md`. Both Kush and Parv sign, or Kush records a written reason for one signature.
2. **Review the cuisine lookup** (`registry/cuisine/cuisine_lookup_v1_DRAFT.csv`, about 200 terms): fix wrong countries or continents; rule on the NEEDS_HUMAN terms (Tex Mex, Cajun, Creole, Hawaiian, Jewish, Roman and the others in `reports/step35/foodcom_cuisine_derivation_README.md`). Edit the lookup, rerun `tools/step35_foodcom_tag_census.py`, run its tests, commit.
3. **Edge audit follow-up (08a):** he already returned a rechecked file. If he wants to revisit B2 ("same report, different value"), write down what he needed to see. Scoring tool: `tools/step08a_score_audit.py`.
4. **Choose the pilot column:** `reserve_split` v1 or the corrected `reserve_split_v2` in `registry/recipe_semantics/deep_gold_text_strata_v1_DRAFT.csv` (D-038). Recommended: v2 for the pilot, v1 reported for comparison. Record it with Kush.
5. **Build 35e** (the typed similarity registry, nine notions) as code with fake-data tests, in `src/culinarystate/representation/`. Follow the pattern of `cuisine_rungs.py` and `recipe_rungs.py`: pure functions, tests first, no real data.
6. **Step 16 reading:** review `registry/recipe_semantics/*_DRAFT.csv`, `registry/processes/*`, `registry/tools/*` and the schemas in `reports/step16/schema_drafts/`. Write comments in `reports/step16/` for H4. These are drafts, so correct them, do not freeze them.

## 5. What needs Kush (Parv should not decide alone)
- Push, history, anything on GitHub.
- Step 08b v1 authorisation; changing any signed threshold (`registry/preregistered_thresholds_v1.csv`).
- The rdkit decision for Step 35b; the H2 licence decisions (Food.com, TASTEset); Step 19 start and seal (H5); the FortiClient VPN.
- ThyroGenUS: `docs/paper/PAPER_A_FINAL_ANATOMY_COMPLETENESS_LEDGER.md` lines 4 and 190 should read `e48688fdd5f69cb0bd04139e8cdecaf57cc7278b` instead of `1d454319...` (separate repo).

## 6. GPU server (only when a task needs it)
Step 17 extraction, Step 20 scale-up and big embedding jobs are the heavy ones. Everything else runs on a laptop. Rules: confirm the IIITD FortiClient VPN is connected (it was OFF on 2026-10-27, so the A100 servers were unreachable), run the project in its own folder on the server, copy scripts over, pull results back, leave nothing running. Ask Kush for the host and folder details.

## 7. Working with an AI assistant (if Parv uses one)
Point it at `CLAUDE.md` first. Keep the same rules: one decision at a time, plain words, tests before code, commit per file, log with `log_step.py`, never let it sign or label for a human. Subagents are fine for drafting and building; always run the tests yourself before committing.

## 8. Key places
| What | Where |
|---|---|
| Current state | `STATUS.md`, `WORKLOG.md` (append-only), `DECISIONS.md` |
| The plan | `docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`, `registry/execution_spine_v2.csv` |
| Signed thresholds | `registry/preregistered_thresholds_v1.csv` |
| 08a results | `reports/step08/`, `exports/lineage/step08a_v1/`, `annotation/lineage_audit/` |
| 07I-C results | `reports/step07i/step07ic_*`, `ledgers/recipe_identity_v2/` |
| Step 16 drafts | `reports/step16/`, `registry/recipe_semantics/`, `registry/processes/`, `registry/tools/` |
| Step 35 drafts | `reports/step35/`, `registry/cuisine/`, `src/culinarystate/representation/` |
| NER (finished, frozen) | `reports/ner/culinaryner_kf_final_report.md` |
| Human to-do list | `handoff/MANUAL_NEXT_STEPS.md` |

## 9. Large files that are regenerated, not stored in git
`exports/lineage/step08a_v1/{edge_candidates,keys,evd_export_v2}.jsonl`, `registry/recipe_semantics/deep_gold_sampling_frame_v1_DRAFT.csv` (78 MB) and `deep_gold_text_strata_v1_DRAFT.csv` (7 MB). They are also in the Drive bundle (`culinarystate_regenerable_outputs_...tar.gz`). To rebuild: `tools/step08a_gate.py`, `tools/step16b_build_frame.py`, `tools/step16b_text_strata.py`; hashes are in the matching README or freeze manifest. The three are listed in `.gitignore` so they are never committed by accident.

## 10. Refresh at the anchor
Before the handover, update section 3, run the unit tests, append a WORKLOG entry, and tick the section-0 list.
