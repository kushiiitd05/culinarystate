# S163 AI cross-review: ksh (Kush persona) and prv (Parv persona), 2026-11-05

Status: **AI_VERDICT_PENDING_HUMAN_REVIEW**. Two read-only AI reviewers each checked the other person's work, as in review blocks C/D.
- **ksh** reviewed Parv's 2026-11-04 local work (merged in PR #5).
- **prv** reviewed the S163 coding-agent work (PRs #4–#6).

Neither reviewer edited, committed or ssh'd anything. Both printed counts, hashes, code and synthetic strings only. AI review is not human verification: Kush and Parv decide in review-sheet block J.

## prv: S163 auditor fixes and full-corpus results

| ID | Verdict | Reason |
|---|---|---|
| P1 | ACCEPT_WITH_CHANGES | The fix is narrow and consistent with `TEMP_RE`. Each test fails against the code before its fix: prv re-ran test commit N against fix commit N−1 (2, 1 and 1 failures). The risky case was untested: a unit whose case or letter does not match the text. |
| P2 | ACCEPT_WITH_CHANGES | **The three full-corpus JSONs agree on every non-auditor key**: seed, sample size, events, entities, failures, validators and values_checked. Only the invented counts differ: 626/226 → 4/2 → 0/0. Every number in 3.2b, WORKLOG S163, STATUS and the anchor matches. But the JSONs do not record which commit produced them, and the root-cause wording claimed more mask evidence than exists. |
| P3 | ACCEPT_WITH_CHANGES | The PR #5 conflict resolution is correct: Parv's pre-fix file is byte-identical to `_prefix_S161.json` (sha256 `d3e642fb…`). STATUS credited the 1/5 fraction to Parv, but an agent chose it. One STATUS line was stale. |
| P4 | Recommendation | V2 `INVERTED_INTERVAL` affects 1.9 % of Gutenberg texts and 0.47 % of Food.com texts. Step 16, which runs the same grounding code on ingredient lines, found only 2. Suspect the step-text quantity spans. Plan: an agent-built counts-only census by family and shape mask, then a human-read stratified sample. Decide afterwards whether an inverted quantity should become UNKNOWN (as `RANGE_INVERTED_UNKNOWN` already does on the rule path). No threshold change. |

Robustness probes by prv (synthetic):
- Refused, correctly: `C`/`350degF`, `f`/`350degF`, `F`/`350degf`, `F`/`350degreessF`, `F`/`350degFahrenheit`, `5degmin`, `5degs`.
- Accepted but harmless: `F`/`350_degF` and `F`/`350degF2`. Rung A cannot produce either, because its temperature spans are full `TEMP_RE` matches.

**Applied in this branch (AI remit):**
- refusal regression tests for case mismatch and wrong unit (`test_deg_prefix_refuses_case_mismatch_and_wrong_unit`; they pass on the current code, as regression guards);
- per-file provenance and an evidence-scope note in report 3.2b;
- STATUS: "agent-drafted" wording for 1/5 and the stale repo line fixed;
- WORKLOG S164.

**Not applied (follow-ups):**
- the tool does not record the code commit or auditor hash in its JSON;
- the scratch diagnostic scripts are not committed.

## ksh: Parv's local work (PR #5)

| ID | Verdict | Reason |
|---|---|---|
| K1 | ACCEPT_WITH_CHANGES | The draft block parses in the seal: `find_ruling` returns `(1/5, STUDY_THEN_CELL, SOURCE_FAMILY, d3075c68…)` once a D-number is filled in. 1/5 is defensible: Phenol-Explorer has 125 groups, so 25 are reserved, which is above K = 10. The K-1 sign-flip rule applies below 20–30 clusters. 1/4 would give 31. **But one agent, on one machine, made the seed, and nothing proves only one seed was drawn.** Parv's session had also evaluated all Phenol-Explorer publications before the seal (K4). |
| K2 | **ACCEPT** | Independent re-draw gives the **same 21 rows**, 7 strata × 3, 21 distinct groups, ≥ 57 eligible per cell. The `step19_real_pilot.py check` reports ready, 0 blockers. `seed_hex` recomputes. The frame hash matches Kush's local frame. The draw (2026-11-04T13:53Z) came after the nonce commitment (2026-11-03T15:01Z), done by Parv, who is authorised under D-048. Accept as C2; "on Kush's go" becomes a ratification. Notes: the frame bytes predate the nonce, which is stronger in substance; the frame-age gate uses mtime only; the run record wrongly calls the git-ignored frame files "tracked". |
| K3 | ACCEPT_WITH_CHANGES | The packets are blank, text-free and git-ignored. 7 tests pass. **But the "sealed" key is not sealed:** packet order is sha256(public seed \| letter \| recipe_id), and the ids are in the tracked manifest. ksh rebuilt B's key hash (`3d92d0ce…` = committed), and A's is predictable. Nothing stops one machine building both letters. The output folder is not checked to be git-ignored. The commit/snapshot step (design script 3, PV-10) is not built, so annotation started now cannot pass provenance. |
| K4 | ACCEPT_WITH_CHANGES | The labels are honest and the files hold counts only. But the Step 30 bake-off ran before the seal and ahead of Step 30's HARD dependencies (29, 15, 07). It used an agent-chosen seed and margin 0.0, and writes "verdict" fields. Its test set was 25 Phenol-Explorer publications with a heavy tail (max 102.49), so "global median wins" is fragile. The 26g census used Rung A before the auditor fixes and is now stale. The Step 34a record is clean. |

**Recommended by ksh, for human decision (block J):**
- K1:
  - Kush generates the 15a.R seed, or it is joined from two hash-committed parts as in D-048;
  - the seal runs on Kush's Mac (EVD.jsonl is present; `~/.culinarystate_private` does not exist yet);
  - D-054 records the pre-seal bake-off exposure and a reveal-or-escrow rule for the seed at 15b;
  - D-054 is committed from Kush's own session.
- K3:
  - add a secret per-annotator salt committed by hash, or reword the design to say the key is public;
  - build the commit/snapshot step before annotation;
  - then build A on Kush's Mac.
- K4: mark the bake-off non-citable and not for choosing Step 30 rungs (done in STATUS); rerun the 26g census on the fixed Rung A when convenient.
