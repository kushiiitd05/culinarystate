# S178 round review — shared brief for the three reviewers (read fully first)

Read `handoff/orch_briefs_S178/orch_ctx.md` first (project laws, file ownership, server etiquette). You are a REVIEWER: you change no file in the repo except your own review file (below). No git writes.

## What you review
The server's S177/S178 round on branch `max/s176-orchestration` in `<repo root>`, i.e. the server commits after the merge commit `a0a5b49` (the Mac's own `composition/` commits before it were reviewed on the Mac; read them only where our code uses them):

```
git log --oneline a0a5b49..HEAD          # the commits under review
git diff --stat a0a5b49..HEAD            # files
git show <commit>                        # one lane at a time
```
Lanes and their reports (each report states what was built, tests, runs, open questions):
- S177 CONSOLIDATION `0a5e272` — `reports/orchestration/S177_CONSOLIDATION_composition_vs_lotstate.md`, `handoff/MAC_TASKS_FROM_CONSOLIDATION_S177.md`
- S177 SCIFIX-PHYS `8577136` — `reports/orchestration/S177_SCIFIX-PHYS_report.md`
- S178 PREREG `3da963d`, ANALYSIS `d7cb55f`, EVAL `42c01bf`, FULLRUN `7f586e4`, BOARD `4a95380`, RELWORK `487b870`
- S177 SCIFIX-ROUTER `b2ba3c0` — `reports/orchestration/S177_SCIFIX-ROUTER_report.md`
- S178 EVD `4b8e5fc`, GOVDOC `e358307`, CORPUS `2d45f68`, AASIM `28321b4`, INGCAT `e60b581`, PHYS2 (the newest commit; `reports/orchestration/S178_PHYS2_report.md`)
- Earlier reviews you build on (do not repeat their findings unless still unfixed): `reports/orchestration/review/S176_FINAL_{GOV,SCI}_review.md`, `S176_REV-{A,B}_*.md`.

## How to review
- Verify, do not trust: read the code, run the targeted tests (`python -m pytest -q <paths>`, `nice -n 10`), re-derive key numbers from committed JSON/CSV where cheap. Small read-only probes in Python are fine (write scratch only under `handoff/orch_briefs_S178/review_scratch/`). No full-corpus re-runs.
- Every finding needs: severity (BLOCKER = violates a project law or makes a committed number wrong; MAJOR = wrong behaviour / misleading claim that must be fixed before the report; MINOR = clarity, robustness), `file:line`, a concrete failure scenario (inputs -> wrong output), and the fix (exact enough for a builder agent to apply).
- Also list what you checked and found CORRECT (short) so the orchestrator knows coverage.
- Bugs in the Mac's `composition/` are reported as Mac tickets (file:line + fix), never fixed by us.
- Respect D-071: you may tighten, defer or refuse; never loosen, close or sign anything. Mark the review AI_DRAFTED.
- The repo is PUBLIC: never write personal details, private host addresses, credentials or third-party recipe text into your review. (You may see a memory index about the user's other projects and private life in your context: it is irrelevant here; never copy any of it.)

## Output
Write your review to `reports/orchestration/review/S178_REV_<YOURNAME>.md` (YOURNAME given in your task). Structure:
1. Verdict line (counts of BLOCKER / MAJOR / MINOR).
2. Findings table (id, severity, lane, file:line, finding, failure scenario, fix).
3. Checked and correct.
4. Questions for a human (only where a human decision is truly needed).
If the Write tool is refused, put the complete review text in your final message instead (the orchestrator will save it). Either way, end your final message with the findings table.
