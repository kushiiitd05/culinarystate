# Prompt for Parv's Claude session — 13 Nov 2026 (from Kush)

Paste this whole file as the first message of a fresh session on Parv's machine.

---

You are continuing CulinaryState on branch `kush/s179-finish-fixes` for Parv. Kush's session runs on Kush's Mac (holds the
15a seed/sealed list and P1-A Gold) and on vinayak (frozen NER checkpoint + qwen2.5:7b-instruct 845dbda0). **You have no
vinayak access and must not request the seed or sealed list.** Work only on what is listed for you below.

## 0. Start-up (do these first, in order)

1. `git pull --ff-only`. Expected HEAD includes `handoff/BRIEF_2026-11-13_KUSH_TO_PARV.md`, this file, and DECISIONS up to D-097a (D-098 is reserved for Kush's ablation pre-reg and may land after you start).
2. Read, in order: `STATUS.md` (top), tail of `WORKLOG.md` (S227 onward), `DECISIONS.md` D-085, D-094, D-097, D-097a (and D-098 once present),
   `handoff/BRIEF_2026-11-13_KUSH_TO_PARV.md`, `handoff/REVIEW_SHEET_AI_VERDICTS.md` block K13.
3. **Decision numbers:** Kush's session owns D-098 and D-100, D-102 … (even); **you own D-099, D-101, D-103 … (odd)**.
   Pull immediately before appending to `DECISIONS.md`, `WORKLOG.md`, `STATUS.md`, `registry/compute_runs_v1.csv`; push right after.
4. Laws unchanged: one commit per file; tests first; never overwrite a committed output (new dated path); no invented
   scientific values; UNKNOWN is valid; raw third-party text stays git-ignored; repo is PUBLIC (no host paths, IPs, ids, text).

## 1. Operating mode for "human" work (Kush's instruction, 13 Nov)

Kush has directed that **ksh+prv (AI, D-085) perform the remaining human-work items, and Kush and Parv review the AI
results afterwards** and record ok / not ok. You act as **prv**. Rules that still apply and must be stated on every output:

- An AI persona is not an independent human rater, judge or annotator. Every such output carries
  `AI_DELEGATED_D085`, `NOT_INDEPENDENT`, `NOT_HUMAN_VERIFIED_UNTIL_REVIEW`, and the item's own label set.
- Where an acceptance text allows a verdict such as `NOT_COUNTED` or `INVALID_INPUT`, use it honestly; never record PASS
  for a gate whose rule requires independent humans.
- Person-only facts (signatures, nonces, permissions, contributions, availability) are never written by AI. Draft
  placeholders `[[PARV TO CONFIRM: …]]` instead.
- Blinding: when an item says "blind to X", the session doing it must not open X. Record what was and was not opened.
- After each item: append a review row to `handoff/REVIEW_SHEET_AI_VERDICTS.md` (new block `P13-n`), status
  `AI_VERDICT_PENDING_HUMAN_REVIEW`.

## 2. Current status (252 items; 51 POST unchanged)

| | Done | Author edits | Open | Not run / independence | Calendar |
|---|---|---|---|---|---|
| MUST (84) | 52 | 12 | 10 | 7 | 3 |
| SHOULD (168) | 89 | 11 | 13 | 4 | — |

Closed 13 Nov by Kush's session (Kush review: ok all): T9-C09-R1, T3-C09-R1, T3-C11-R1, T6-C02-R3, T3-C17-R2
(figures `reports/s179/kush_figures_2026-11-13/`).

## 3. Every open item, how it can close, and who does it

### 3a. Kush's session (needs seal / P1-A Gold / vinayak) — do NOT touch

| Item | P | Action |
|---|---|---|
| T3-C20-R1 | S | duplicate + source control on the sealed 15a partition (row-content duplicates across RESERVED/DEV) |
| T8-C21-R2 | S | D-098 matched ablations on frozen D5 with frozen 7b (vinayak) |
| T9-C24-R2 | S | regenerate H1/B7 with frozen 7b; future-date part stays calendar |
| T8-C06-R1 | M | source-held-out retrieval diagnostic with CIs on frozen P/C questions |
| T0-C06-R2 | M | versioned strict-v3 re-emission of D5 answers (new path); original 30 flags retained |
| T2-C05-R1..R4 | M | **ksh** half of 07.A-R1 (Kush packet) — see 3b for the **prv** half |
| T2-C09-R4 | M | **ksh** CAL verification file — see 3b for the **prv** half |

### 3b. Your session (prv) — do these, in this order

1. **Records (no new analysis).**
   - `reports/s179/local_model_and_seal_dependencies_SUPERSEDED_2026-11-13.md`: states the four artifacts exist (paths/sha in
     the brief), that the original JSON is retained, and why it was wrong (searched Parv's machine only).
   - `reports/orchestration/S179_technical_scope_matrix_2026-11-13_v2.{csv,json,md}`: copy v1, update only the five closed
     items with evidence path + sha256, and every later item you or Kush close. Keep v1 untouched.
2. **T2-C05-R1..R4 (MUST ×4), prv half of 07.A-R1.**
   - Kush will send `annotation/condition_audit/condition_audit_packet_100_R1_Parv.csv` by private transfer if you lack it
     (git-ignored; verify sha256 on receipt and record it before labelling).
   - Label it as **prv** blind to the Kush packet, to any Kush labels, and to the v1–v4 results. Do not open
     `condition_audit_packet_100_R1_Kush.csv` or any `*_completed.csv`.
   - Non-judgement columns must stay byte-equal to the issued packet (acceptance R2). Hash the returned file on receipt.
   - Kush's session labels the Kush packet as **ksh**, then scores under the existing prereg
     `07A_R1_preregistration` with the recorded verdict vocabulary. Because both raters are AI personas, the scorer
     verdict must be **NOT_COUNTED** (not PASS/FAIL) with reason `AI_PERSONAS_NOT_INTER_RATER`; this closes R2–R4 as run
     and keeps the v4 FAIL as the only human result. R1 (human signature) stays `[[KUSH/PARV TO SIGN]]`.
3. **T2-C09-R4 (MUST), prv CAL verification.** Using your staged AA CAL rows (`annotation/aa_pilot/aa_pilot_verify_CAL_v1_Parv.csv`
   format), mark every row VERIFIED / CORRECTED / REJECTED against the source span, blind to the Kush/ksh file. Record
   source-page and span hash per row. Kush's session does ksh; disagreements go to an adjudication table; label both
   `AI_DELEGATED_D085 NOT_INDEPENDENT`.
4. **T8-C16-R1 (MUST), blind claim judge.** Pre-declare (commit first, as D-099) a random sample of ≥30 claims across D5
   rungs incl. the enforced rung, with a seed. Then judge each claim supported / unsupported / unclear from its cited
   evidence only, **blind to rung name and to checker output** (strip them in a pre-step committed before judging). Report
   manual-vs-checker agreement with a Wilson CI after unblinding. Label `AI_JUDGE_NOT_HUMAN`.
5. **T8-C04-R2 (MUST).** From item 4, write the caveat paragraph + agreement % into the D5 report draft section
   (draft file, not the author-final report).
6. **T8-C01-R1 (MUST), branch Gold.** Draft branch labels for the abstaining/decision branches on the frozen D5 benchmark
   in a session that has not opened the system's branch outputs; then compute accuracy + per-branch confusion matrix with
   the frozen-benchmark sha256. Label `AI_ASSISTED_GOLD_NOT_INDEPENDENT`. No code change to the frozen system.
7. **Licensed sources — Parv as a human, 10–20 min (T2-C09-R2/R3, T2-C07-R2, T2-C18-R1).** In a normal browser,
   download AAK-02/04/05/08/10 (scripts are refused by the sites; never work around that). Confirm CC-BY/CC0 from the
   publisher page or drop the paper and record why. Then (AI) verify every CAL span verbatim against the PDFs, write the
   CAL packet v2 manifest with new sha256. These PDFs may also raise SIM-VAL eligibility (T5-C10-R6) — run the existing
   separate-session SIM-VAL precheck on any new rows and report the count honestly (it may stay 0).
8. **Author work drafts (12 MUST + 11 SHOULD, D-094).** As prv, draft the final-edit text for every
   `*_FINAL_EDIT_EXCLUDED` item into a new file per section under `reports/final/drafts_2026-11-13/` (never the
   author-final report). Every number must trace to a committed JSON path; run the number-class lint (T9-C20-R1).
   Contributions, availability and personal statements are placeholders `[[PARV TO CONFIRM]]` / `[[KUSH TO CONFIRM]]`.
   Include the 13 Nov results with their labels; the Phenol-Explorer "rungs worse than D0" result is a negative result —
   keep it visible.
9. **Rehearsal pack.** Timed 13-slide run sheet with the `run_local_demo_v3.py` fallback, a Q&A sheet covering every
   limitation in 3c, and a PR #12 / #11 merge-readiness checklist (conflicts, tests, protected files). Do not merge.

### 3c. Cannot be driven to zero by running — present as limitations

| Item(s) | Why it stays open | What would actually close it |
|---|---|---|
| T2-C02-R1/R2, T4-C14-R3, T4-C21-R1, T5-C01-R1, T5-C05-R2, T5-C07-R2/R3, T5-C08-R1, T5-C11-R3/R4 | AA assay specificity, raw trajectories, basis/condition links and PARAM lineage do not exist in any source we hold; SIM-VAL eligible 0, G15 PASS 0 | new measured data or papers with raw trajectories; not achievable by 21 Nov |
| T5-C10-R6 | SIM-VAL needs assay-basis-compatible held-out observations | possibly partly by the AAK PDFs (3b-7); report the real count |
| T0-C17-R1 | endpoint permission is a person-only fact | Kush states it in writing |
| T3-C04-R3, T3-C08-R1, T6-C04-R1, T8-C08-R1 | deferred by recorded decision | only a new decision; not planned |
| T9-C23-R2, T9-C26-R3, T9-C26-R1 | real dates (post-19 Nov MPU, 24 Nov rehearsal) | happen on the day |
| 51 POST | outside scope | — |

## 4. Definition of done for your session

- Each item above has: committed output (new path), tests for any new code, a WORKLOG entry via `tools/log_step.py`,
  a compute_runs row for any run, a review-sheet row, and the scope matrix v2 updated.
- Full suite still green on your machine (record counts; missing-private-input skips must be named, not hidden).
- Push after every item. Tell Kush (in WORKLOG "Next") which files his session needs to pick up (e.g. returned prv
  packets for scoring).
- Do not: start new diagnostic lanes, touch the files in 3a, change frozen benchmarks/answers/scorers/prereg/ledgers,
  merge to main, or claim independence/human verification.
