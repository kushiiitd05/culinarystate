# Prompt for the Mac Claude session — take the manjot S177–S178 rounds (2026-11-09)

Paste everything below the line into the Mac Claude session in `~/Desktop/CGAS/culinarystate`.
It replaces `MAC_CLAUDE_MERGE_PROMPT_2026-11-08.md`, which covered S175 only.

---

The manjot-server orchestrator (D-078) continued on branch `max/s176-orchestration`. That branch already contains
your S175/S176 work: GitHub `kush/s169-seal-p1b` @ `145fdfd`, merged at `a0a5b49`, with 435 tests passing then.
On top of it are the server's S177–S178 commits, 15 or more. Do the steps below in order. Stop to ask Kush only where a
step says so.

## 0. Notice / disclaimer (keep it in every report and slide)
- **AI-drafted.** Everything the server added is AI_DRAFTED by agents. None of it is human-verified, signed or
  approved.
- **No human-only acts.** No D-071 human-only item was done or simulated: signatures, nonces, approvals, freeze
  records, human facts. The preregistration amendments are drafts beside the untouched originals.
- **SSOT.** SSOT v16 is a DRAFT pending Kush; v15 stays authoritative.
- **Data.** Committed outputs are counts and aggregates only. No BBC data exists on manjot (D-003), so every
  BBC-dependent re-run below is yours.
- **Public repo.** It is PUBLIC. Do not add personal calendar details, private host addresses or credentials to any
  committed file.

## 1. Get the branch
```bash
cd ~/Desktop/CGAS/culinarystate
git status                                   # commit your own work first
scp <user>@<manjot-server>:~/kush_work/culinarystate_s176_orchestration.bundle ~/Desktop/CGAS/
git bundle verify ~/Desktop/CGAS/culinarystate_s176_orchestration.bundle
git fetch ~/Desktop/CGAS/culinarystate_s176_orchestration.bundle max/s176-orchestration:max/s176-orchestration
git log --oneline 145fdfd..max/s176-orchestration
```
- **Clean fast-forward:** if your branch is still `kush/s169-seal-p1b` at `145fdfd`, run
  `git merge --ff-only max/s176-orchestration`.
- **If you committed after `145fdfd`:** merge normally. Expect conflicts only in `WORKLOG.md`,
  `registry/compute_runs_v1.csv` and `STATUS.md`.
  - Keep both sides.
  - Renumber the server's WORKLOG ids (S177+) after yours. Ids are never reused.
  - The run log is a union of rows.
- **Tests:** run the full suite, `python -m pytest -q --continue-on-collection-errors`. Fix only merge breakage and
  report anything else.

## 2. Your code: `composition/` (the server never edits it)
Work through `handoff/MAC_TASKS_FROM_CONSOLIDATION_S177.md`:
- **Tickets A1–A11.** A1 and A2 matter most.
- **Ports from `lotstate/`.** `lotstate/` is SUPERSEDED. Port its parts only if you agree.
- **FULLRUN bugs F1–F5.** Found on the non-BBC full-scale census; the report is
  `reports/orchestration/S177_FULLRUN_report.md`.

Write tests first, then fix, then reply in the task file with the fixing commit for each id.

## 3. BBC re-runs (D-003: Mac only)
Log every run in `registry/compute_runs_v1.csv` with its sha256. Mark the old outputs SUPERSEDED: keep them on record,
and no tool may read them.
1. **Heat physical layers.** Run Layer 1 0.2.0 (temperature ownership, `matrix_groups`, endpoint block) and Layer 2
   0.4.0 for the BBC family. Use the same tools and seed as the server's v04 runs: `tools/binding_census.py`, then
   `tools/scenario_layer_run.py`, `--seed 20261104`. Tag them `S178_v04`.
   - Run the schema validator `tools/s178_phys_schema_validate.py` on the BBC records. Expect 100%.
   - Rows `RUN-S178-PHYS2-*` show the server's commands.
2. **Non-heat layers.** Run v04 for BBC with `tools/nonheat_layer_run.py`.
3. **Router census.** Run CENSUS_VERSION 0.3.0, with prior-process context, the full ABSENT rule and the SR identity
   adapter, for BBC:
   - command: `tools/router_demo_census.py --gates on`, the same as rows `RUN-S177-ROUTER-*`;
   - publish full corpus = non-BBC (manjot S177: vitamin-C DIRECT 40,308) + BBC (yours).
4. **Public mode.** Before any public hosting, check `CS_DEMO_PUBLIC=1` on the Mac demo. BBC-derived KGE edges and
   carbon figures must be absent from every page and API answer.

## 4. Push, PR, merge
```bash
git push origin max/s176-orchestration
gh pr create --base main --head max/s176-orchestration \
  --title "Gather the stack: s169-seal-p1b + manjot orchestration (S175-S178)" \
  --body "Merges kush/s169-seal-p1b, the Mac S175/S176 lot composition work and the manjot orchestration rounds S175-S178. All server content is AI_DRAFTED; see handoff/RESUME_ANCHOR_2026-11-09_ORCH.md."
```
**Ask Kush before merging into `main`.** After the merge, log a WORKLOG step.

## 5. Humans: scribe only, in their own words
Open `handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md` with Kush and Parv. Add the new questions listed in
`handoff/RESUME_ANCHOR_2026-11-09_ORCH.md` ("Next — humans"):
- the AA validation pass threshold;
- the ING category top-100 confirmation;
- the stated-liquid residual;
- PROC 93 vs 156;
- endpoint-lexicon scope.

Record each decision in `DECISIONS.md` as the human's words; you are the scribe. The prereg lock is scribed from the
server's S178 amendment drafts. Humans sign only the locked bytes.

## 6. Key files
- **Board:** `registry/execution_board_S178.csv` and `reports/orchestration/S178_EXECUTION_BOARD.md`.
- **Anchor:** `handoff/RESUME_ANCHOR_2026-11-09_ORCH.md`.
- **Lane reports:** `reports/orchestration/S177_*`, `S178_*`.
- **Reviews:** `reports/orchestration/review/S178_REV_*`.
- **Prereg amendments:** `reports/{step07,del5,step29,step10}/*AMENDMENT_S178_DRAFT*.md`.
