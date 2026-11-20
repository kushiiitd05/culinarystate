# CulinaryState — remaining tasks, for a coding agent (written 20 Nov 2026, evening)

You are a careful coding agent working in Parv Goyal's checkout of the CulinaryState repository on his Mac.
The technical freeze is done and pushed. Your job is to finish the remaining deliverables for submission
on **21 Nov 2026**, without breaking anything that is frozen, and to report honestly what you could not do.

Work slowly and verify everything. A wrong number in the report is worse than a missing one. When a step
says "ask Parv", stop and ask; do not guess.

---

## 0. Where things are (verified 20 Nov, 18:00 IST)

| Fact | Value |
|---|---|
| Repo | Parv's local checkout (GitHub `kushiiitd05/culinarystate`, **public**); paths below are relative to its root |
| Branch | `kush/s181-explorer-build`, in sync with `origin` |
| Freeze tag | `freeze-2026-11-20` → commit `0a41d62` (pushed) |
| Tests at the freeze | 8,578 passed, 5 skipped, 0 failed, 44 deselected (~4 min) |
| Preflight at the freeze | `tools/preflight.sh` 28/28 |
| Snapshot | `web/public/snapshot/`, manifest sha256 `bf0f80611429552b1a8264bdedf56b03fef1323630e41b896b1e3cfd81a24025`, signature verified |
| Decisions | through **D-141**; next free id **D-142** (ids are never reused) |
| Worklog | last step **S264**; `tools/log_step.py` assigns the next id itself |
| Deliverables D1–D5 | all **PARTIAL** (`reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md`) |
| Human-only gaps | D1 **0 of 40** literature rows verified · D5 chef/peer review not done · 9-row proposal packet not done · D3 spot-audit not done |
| Uncommitted at freeze | `reports/final/deck/build_deck.py`, `reports/final/deck/slides.py` (large edit, not from the freeze session) |

**Read before acting, in this order:** `STATUS.md` (top entry) → `handoff/PARV_LATEST_PROMPT_2026-11-19.md`
(governs where documents differ) → `handoff/PARV_HANDOVER_2026-11-17.md` → `handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md`
→ tail of `WORKLOG.md` → `DECISIONS.md` D-134…D-141 → `reports/s181/human_audit/README.md` and `REPORT_WORDING.md`.

**Already done — do not redo:** B1 (D-140 range-bug decision), B2 (`/live` hidden unless server-side
`CS_LIVE_ENABLED=1`), B4 except the `--live` run, B5 (freeze, tag, STATUS hashes), the snapshot re-signature (D-141).

## 1. Environment on this Mac (the handover documents assume Kush's machine)

- **Python:** `../.venvs/s179-py311/bin/python` (3.11.9, next to the repo root). `/opt/anaconda3` does
  **not exist** here, even though `CLAUDE.md` and the handovers name it. Do not create a new venv.
  Tests: `<that python> -m pytest -q`.
- **Node:** `web/node_modules` is installed (Next 16.4.6). Build with `cd web && ./node_modules/.bin/next build`.
- **Chrome:** `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (headless works; minimum headless
  viewport width is 500 px). **Keynote** is installed; LibreOffice and pandoc are not.
- **Not installed:** `python-pptx`, a Markdown converter, Playwright. Install only what a task needs, pin exact
  versions published at least two weeks ago, and record each install in the WORKLOG step:
  - `pip install "python-pptx==1.0.2"` into the venv above (deck);
  - `pip install "Markdown==3.4.1"` (the version in `reports/s179/env_lock/mac_S179.txt`) for report HTML;
  - for screenshots, put `playwright-core` (exact version, check it with `npm view playwright-core versions`)
    in its own folder `tools/screens/` with its own `package.json`, and launch the installed Chrome via
    `executablePath`. **Do not add anything to `web/package.json` or `web/package-lock.json`.**
- **GitHub CLI:** `gh` is logged in as Parv. **Vercel CLI** is not installed; use `npx vercel@66.2.0`.
- **NVIDIA key:** `~/.config/culinarystate/nvidia.env` exists, mode 600. **Never open, print, copy, log or commit
  it**, never echo environment variables, and never put a key in a screenshot.

## 2. Laws (break none; they come from the project, not from you)

1. No invented scientific values. UNKNOWN is a valid answer. Every number you write must come from a frozen
   artifact you opened in this session; cite its path.
2. AI review is not human verification (D-071/D-085). **Never fill a human column** (`human_locator`, `human_note`,
   reviewer blocks, sign-offs) and never write that a human did something unless Parv tells you he did.
3. `src/`, `registry/` and `ledgers/` are frozen. Changing them needs a decision record first, and on submission
   eve the answer is almost always "don't".
4. BBC Good Food and Food.com recipe text never leaves the machine (D-003): not in screenshots, the report, the
   deck, the zip, a hosted model or Vercel. Only self-written or public (Wikibooks, Gutenberg) recipe text may go
   to the hosted model.
5. Commits: **one file per commit**, authored by Parv (git is already configured), **no AI attribution or
   co-author lines**. Commit by explicit path (`git commit -- <path>`) so you never sweep up unrelated edits.
   Push only after Parv says so; then push every session.
6. Log each step with `tools/log_step.py --who "Parv+GPT" --block <DEL-n> --title … --did … --files … --verify … --next …`.
7. If you add a decision to `DECISIONS.md`, regenerate the provenance section
   (`<python> tools/s179_gate_provenance_report.py`) or the test `test_s179_gate_provenance_report` fails.
8. Language in the report, deck and talk. **Never write:** "SOTA", "beats state of the art", "more accurate",
   "completed" for any deliverable, "validated/verified/clean" about lineage vNext, "tomato sauce is acidic", or
   any accuracy number from the Layer-1 comparison. **Say instead:** same model, different context; the system
   cites evidence or says UNKNOWN with the reason; simulated values are labelled simulated; there is no gold.

## 3. Stop and ask Parv (do not improvise) when

- a step needs a login, a credential, money, or sending anything outside this Mac for the first time;
- a science or governance decision is needed (resolution rule: `ksh` governs AI-delegated reviews, D-139; a human
  decision outranks it);
- a number in a handover document disagrees with the artifact it cites (use the artifact, and tell Parv);
- anything would put BBC/Food.com text, a key, or a private path (`/Users/...`) into a shared file.

Ask in this form: **QUESTION · RECOMMENDED · ALTERNATIVES · CONSEQUENCE · DEADLINE IMPACT.**

## 4. Raise with Kush through Parv first: tracked BBC-derived ledger rows in a public repo

`ledgers/data/KGE.jsonl` (80,607 rows) is tracked in git and the GitHub repo is **public**. 39,473 of its rows
carry the BBC markers `BBCGF` / `SRC-000002` (association records — no recipe text was found, but
`deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md` §1 treats shipping these rows to a third party as a D-003
problem). This predates the handover. **Do not rewrite history, delete files, or change visibility.**
Consequences for you: keep `ledgers/` out of the submission zip and out of Vercel, and give Parv one paragraph
he can send Kush.

---

## 5. Tasks, in order

Each task ends with a **Done when** check. Tick it only when the check passes, and record the evidence.

### T1 · Decide the uncommitted deck edits (5 min, ask Parv)

`git diff reports/final/deck/` shows ~245 added / 273 removed lines in `slides.py` and an output-path change in
`build_deck.py` (`CS_DECK_OUTPUT`, default `reports/final/CulinaryState_final.pptx`). Summarise the diff for Parv
in five lines and ask: keep and build on it, or discard? **Never discard without his yes**
(`git stash` is safer than `checkout` if he says discard).
**Done when:** Parv has answered and you have either committed the edits as his or stashed them.

### T2 · Live presets through the model (B4 remainder, ~10 min)

Confirm once with Parv that the ten self-written demo recipes may be sent to NVIDIA with his key. Then, in one
terminal, `./tools/live_demo.sh` (starts the engine on `127.0.0.1:8770` and the web app on `localhost:3000/live`).
In another terminal, `tools/preflight.sh --live`.
**Done when:** the script prints `10/10 presets reached Verify without error` and `PREFLIGHT PASS`. Save the
console output to `reports/final/screens/runs/preflight_live_<date>.txt`. If a preset fails, report which one and
why; do not change the presets or the engine to make it pass.

### T3 · Screenshots (N1)

From the frozen build, light mode, 1600×1000, into `reports/final/screens/`, with `MANIFEST.json` listing file,
route, commit, timestamp (UTC) and sha256 for every image. The list (from the 19 Nov prompt §6):
`01_landing` · `02_lab_tomato_state` · `03_lab_unknown_axis` · `04_compare_A-D` · `05_method_pipeline` ·
`06_live_pipeline_ticking` · `07_live_answer_carrots` · `08_live_compare_plain_carrots` · `09_live_vitc_compare` ·
`10_live_similar_recipes` · `11_live_safety_refusal` · `12_snapshot_signature_badge`.
Snapshot pages (01–05, 12) from `next start` **without** `CS_LIVE_ENABLED`; live pages (06–11) from
`live_demo.sh`. The prompt also lists `04_compare_A-D?vision=deut` as a colour-blind check, but **no `?vision=`
mode exists in `web/src`** (checked 20 Nov). Do not build it now and do not simulate it; record it in STATUS as
not implemented.
Open every PNG and look at it: no key, no `/Users/...` path, no BBC/Food.com recipe title or text, no "offline"
chip in a live shot, badge says "signature verified" in snapshot shots.
**Done when:** all files exist, MANIFEST hashes recompute, and you have viewed each image.

### T4 · Story panels (N3)

Four stories, one panel each: QUESTION · PLAIN MODEL · CULINARYSTATE · WHY (format and limits in the 19 Nov
prompt §5). Stories: Tomato A–D (`/compare`, from the snapshot), Carrots mushy, Tomatoes · vitamin C, Chicken ·
is it safe? (`/live`). Save each live run's full JSON response in `reports/final/screens/runs/` and **paste answers
verbatim from that JSON**; never retype or tidy them. Mark invented values in the plain answer as `[no source]`
only where the verifier or the packet shows no source. State the run date and model id.
Verified reference points: the tomato vitamin C system answer is DIRECT, `EVD-002765=95.0%`; the similar search
covers 612,903 recipe titles. Do **not** assume the plain model will say "40–60 %" — quote whatever it said.
**Done when:** `reports/final/screens/STORIES.md` holds four panels, each traceable to a saved JSON file.

### T5 · Vercel, snapshot only (B3; needs Parv)

Ask Parv to run `npx vercel@66.2.0 login` himself. Then deploy **only the `web/` folder** (never the repo root,
never a GitHub import: the public repo includes `ledgers/`): `npx vercel@66.2.0 deploy --cwd web` (preview). Do not
set `CS_LIVE_ENABLED` or any `NEXT_PUBLIC_` variable. Check the preview URL with curl and headless Chrome: `/`,
`/lab`, `/compare`, `/method` return 200 and show "signature verified"; `/live`, `/api/live` return 404;
`/snapshot/public_key.pem` is served. Show Parv the URL; run `deploy --prod` only after he says yes.
**Done when:** the production URL passes the same checks and is recorded in `STATUS.md`.

### T6 · Final report → PDF (B6)

Update the existing drafts, do not start a new one: `reports/final/FINAL_REPORT_DRAFT_S179_2026-11-11.md` and
`reports/final/sections/S180_freeze_results_DRAFT.md`. Order (19 Nov prompt §8): problem → data → D1…D5 (each:
what, number, limit) → models and comparisons → stories (T4 panels) → negative results → what is left → demo
links → reproducibility index. Required content:
- the freeze facts in §0 (tag, test count, preflight, snapshot hash);
- what `/live` is and is not (17 Nov handover §4), including its known issues;
- **recipe counts reconciled:** 612,782 (recipe base v1), 611,902 (compiler corpus run) and 612,903
  (similar-search titles) are three populations — define each or use one;
- D1–D5 honest status from the compliance matrix, and for every human gap the exact sentence from
  `reports/s181/human_audit/REPORT_WORDING.md` that matches its real state on 21 Nov;
- all negative results (H1/H3 not met, NER no win, lineage vNext diagnostic only, pH/salt/fat fractions UNKNOWN).
Export: Markdown → HTML (Markdown 3.4.1, a small print stylesheet) → Chrome headless `--print-to-pdf` →
`reports/final/CulinaryState_final_report.pdf`.
**Done when:** every number in the PDF is traceable to a cited artifact (list them in an appendix), no forbidden
phrase appears (`grep -i` for each), and you have read the PDF page by page.

### T7 · Deck → PPTX + PDF (B7)

After T1. Extend `reports/final/deck/slides.py` with the four slides in the 19 Nov prompt §4 (data, models,
live, business only if T8 says yes), keep the honest-limits slide second to last, and follow the design rules in
§2 of that prompt (title = claim, one idea per slide, a source line on every slide, light background, system fonts).
Build with the venv Python. PDF: export the PPTX with Keynote (`osascript` driving Keynote's export to PDF); if
that fails, ask Parv to use File → Export in Keynote.
**Done when:** `CulinaryState_final.pptx` and its PDF exist, every slide renders (view the PDF), and the numbers
match the report.

### T8 · Business proposal (N2) — only if Kush confirms

Ask Parv whether Kush wants it. If not confirmed by the time T6/T7 are done, skip it and say so. If yes: one slide
plus one page, no market-size numbers unless cited, no accuracy claims (19 Nov prompt §7).

### T9 · Rehearsal script and fallback video (B9)

Write `handoff/REHEARSAL_SCRIPT_2026-11-24.md`: the ≈6-minute demo from the 17 Nov handover §6, with exact
clicks, what to say, and what to do if live is down (switch to the snapshot pages and the video). Parv records the
fallback screen video himself (macOS screen recording) following your shot list; you do not record his screen.
**Done when:** the script exists and Parv has the shot list.

### T10 · Submission package (B8, 21 Nov)

Build `submission/CulinaryState_Group17_<date>.zip` from an allow-list, not by zipping the repo:
`git archive freeze-2026-11-20` limited to `src/ tools/ tests/ registry/ web/ docs/ design/ deployment/ handoff/
reports/ DECISIONS.md STATUS.md WORKLOG.md pyproject.toml CLAUDE.md`, **excluding `ledgers/` and `data/`**,
plus the report PDF, deck PPTX + PDF, screenshots, `reports/final/RELEASE_CARD.md`, the compliance matrix, and a
`README_SUBMISSION.md` with demo links (Vercel URL, `./tools/live_demo.sh`, the fallback video) and a `SHA256SUMS`.
Checks: `unzip -t` clean; extract to a fresh folder and verify every hash; `grep -r` the extract for `nvapi-`,
`PRIVATE KEY`, `BBCGF`, `SRC-000002` — any hit stops the build; list the zip size.
**Private paths:** 21 committed files in those folders already contain `/Users/…` paths (e.g.
`registry/compute_runs_v1.csv`, several `reports/s179/*.json`). Grep the extract for `/Users/`, list every hit,
and ask Parv whether to leave those files out of the zip or keep them. Do not edit frozen files to scrub them.
**Done when:** all checks pass, Parv has decided on the `/Users/` hits, and the checks' output is saved next to the zip.

### T11 · Close out

- `STATUS.md`: tick each line of the 19 Nov prompt §10 with the commit that closed it, or state why it is open.
- `WORKLOG.md`: one step per task.
- Ask Parv before opening the PR `kush/s181-explorer-build` → `main` with `gh pr create`.
- Draft the one-line WhatsApp to Kush (DONE / PARTIAL and why) for Parv to send.

## 6. Human-only work you support but never perform

D1 (40 literature rows), D5 (chef/peer review), the 9-row proposal packet, D3 (10-recipe spot-audit and the P1-A
label question to Kush). You may open the source for a row, show the precheck columns, and time-box the session.
You may not fill a human column, paraphrase a verdict as if a human gave it, or mark any of these done. If they are
not done on 21 Nov, the report and deck use the "not done" sentence from `REPORT_WORDING.md`.

## 7. How to report back after each task

Five lines: **what you did · the check you ran and its output · files changed (with commits) · anything you
could not do and why · what you need from Parv.** If a check fails, say so first. Never summarise a failure
as "mostly done".
