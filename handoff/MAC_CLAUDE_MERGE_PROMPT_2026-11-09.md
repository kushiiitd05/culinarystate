# Prompt for the Mac Claude session — continue from the manjot anchor of 9 Nov 2026 (~21:00 IST)

Paste everything below the line into the Mac Claude session in `~/Desktop/CGAS/culinarystate`. It replaces the
08 Nov prompt and the earlier 09 Nov version.

---

You are taking back the baton from the manjot-server orchestrator (D-078) for the S177–S178 rounds. Read
`handoff/RESUME_ANCHOR_2026-11-09_ORCH.md` first: it lists what is done, what is half-done and who does what.
The bundle carries two branches:
- **`max/s176-orchestration`** — reviewed, tested, committed work. It contains your S175/S176 (GitHub
  `kush/s169-seal-p1b` @ `145fdfd`, merged at `a0a5b49`) plus about 25 server commits.
- **`max/s178-wip`** — one snapshot commit on top of it: three fixer lanes the server stopped mid-way (FIX-PHYS,
  FIX-ROUTER, FIX-EVAL) and the finished MECH lane. Their own tests pass (86 / 68 / 71 / 46), but the work is
  UNREVIEWED and not yet split into lane commits.

## 0. Notice / disclaimer (keep it in every report and slide)
- Everything the server added is AI_DRAFTED by agents. None of it is human-verified, signed or approved.
- No D-071 human-only act was done or simulated: no signatures, nonces, approvals, freeze records or human facts.
  The prereg amendments are drafts beside the untouched originals.
- SSOT v16 is a DRAFT pending Kush; v15 stays authoritative.
- Committed outputs are counts and aggregates only. No BBC data on manjot (D-003): BBC legs are yours.
- The GitHub repo is PUBLIC: no personal details, private host addresses or credentials in committed files.

## 1. Get both branches
```bash
cd ~/Desktop/CGAS/culinarystate
git status                                    # commit your own work first
scp <user>@<manjot-server>:~/kush_work/culinarystate_s176_orchestration.bundle ~/Desktop/CGAS/
git bundle verify ~/Desktop/CGAS/culinarystate_s176_orchestration.bundle
git fetch ~/Desktop/CGAS/culinarystate_s176_orchestration.bundle \
  max/s176-orchestration:max/s176-orchestration max/s178-wip:max/s178-wip
git log --oneline 145fdfd..max/s176-orchestration
```
- **Fast-forward** if your branch is still at `145fdfd`: `git merge --ff-only max/s176-orchestration`.
- **Otherwise merge**: keep both sides of `WORKLOG.md`, `registry/compute_runs_v1.csv` and `STATUS.md`; renumber the
  server's S177+ after yours (ids are never reused).
- Run the full suite: `python -m pytest -q --continue-on-collection-errors`.

## 2. Finish the WIP lanes (agent work; you or the next manjot session)
Work on a branch from `max/s178-wip`, e.g. `git switch -c kush/s179-finish-fixes max/s178-wip`.

**Inputs:**
- Briefs: `handoff/orch_briefs_S178/fixer_S178_phys.md`, `fixer_S178_router_eval.md`, `orch_ctx.md` (laws,
  ownership, etiquette).
- Reviews: `reports/orchestration/review/S178_REV_{GOV,SCI-A,SCI-B}.md`.

**What is left:**
1. **FIX-ROUTER + MECH**
   - Run the full non-BBC router census 0.4.0 (needs Food.com, on manjot) and the BBC leg (yours).
   - Write `reports/orchestration/S178_FIX-ROUTER_report.md`.
   - Commit FIX-ROUTER and MECH together, because MECH needs the analytical-zero ABSENT rule.
   - MECH's FOODCOM and v05 re-run commands are in `S178_MECH_report.md` §6.
2. **FIX-EVAL**
   - Regenerate the two committed outputs that now fail: `tests/unit/test_s178_d5_fixture_run.py` (run
     `tools/s178_d5_fixture.py`) and `tests/unit/test_s178_prompt_registry.py` (regenerate the prompt registry
     after the `h1_rungs.py` change).
   - Re-run `tools/s178_corpus_replay_invariants.py`. The server run was killed and is logged ABORTED.
   - Write the report and commit, including the shared `S178_EVD_report.md` correction sections.
3. **FIX-PHYS**
   - Run v05: Layer 1 0.3.0, Layer 2 0.5.0, heat and non-heat. Do the 1,000 sample first, then full families,
     with the same commands as rows `RUN-S178-PHYS2-*`, `--seed 20261104`.
   - Run the schema validator, the v04→v05 comparison, and the regenerated sensitivity/endpoint/stated-liquid
     reports.
   - Write the report and commit.
   - Non-BBC full runs need Food.com: run them on manjot if it is not on the Mac.
4. Log every run in `registry/compute_runs_v1.csv` and add the superseded rows to `registry/superseded_outputs_S176.csv`.
5. Do a short re-review (one GOV pass, one SCI pass), then re-run the full suite.

## 3. Your own code: `composition/` (the server never edits it)
`handoff/MAC_TASKS_FROM_CONSOLIDATION_S177.md`:
- tickets A1–A11 (A1 drops a pH row; A2 matters most);
- FULLRUN bugs F1–F5;
- optional ports from the SUPERSEDED `lotstate/`;
- consider porting `registry/food_ph_fda_draft_v1.csv` (488 rows; D-079 PROPOSED).

Tests first; reply in the task file with the fixing commit per id.

## 4. BBC re-runs (D-003, Mac only), AFTER step 2 lands
- Physical layers v05 (heat + non-heat) for BBC, with the same tools and seed; schema validator expected at 100%.
- Router census 0.4.0 for BBC. Full corpus = non-BBC (manjot) + BBC (yours).
- Public mode check with `CS_DEMO_PUBLIC=1` / `--public`: no BBC-derived KGE edges, typical durations or carbon
  figures on any page or API answer. A local-mode server must answer 503 to tunnelled requests.
- Do NOT run BBC physics on v04: SCI-A found Layer 1 errors that v05 fixes.

## 5. Push, PR, merge
```bash
git push origin max/s176-orchestration        # the reviewed branch; push the finished fixes branch when step 2 is done
gh pr create --base main --head max/s176-orchestration \
  --title "Gather the stack: s169-seal-p1b + Mac S175/S176 + manjot orchestration (S175-S178)" \
  --body "All server content is AI_DRAFTED; see handoff/RESUME_ANCHOR_2026-11-09_ORCH.md. Unfinished fixer lanes are on max/s178-wip."
```
- Do not merge `max/s178-wip` unreviewed.
- **Ask Kush before merging into `main`.**
- Log a WORKLOG step.

## 6. Humans: you are the scribe
Open `handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md` and the list in the anchor §4 with Kush and Parv. Record each
decision in `DECISIONS.md` in the human's own words. The prereg lock is scribed from the S178 amendment drafts;
the 07.A-R1 draft now recommends the non-loosening option, and Option A needs Kush's explicit signed choice.
The benchmark freeze record is written by both humans, in the format of `src/culinarystate/evaluation/frozen_guard.py`.

## 7. Key files
- Board: `registry/execution_board_S178.csv`, `reports/orchestration/S178_EXECUTION_BOARD.md`
- Anchor: `handoff/RESUME_ANCHOR_2026-11-09_ORCH.md`
- Briefs: `handoff/orch_briefs_S178/`
- Lane reports: `reports/orchestration/S177_*`, `S178_*`
- Reviews: `reports/orchestration/review/S178_REV_*`
- Deployment: `handoff/DEPLOYMENT_AND_PRESENTATION_PLAN_2026-11-08.md` (starts in `--public` before any tunnel)
