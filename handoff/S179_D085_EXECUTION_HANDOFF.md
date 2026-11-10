# S179 / D-085 execution handoff (Mac agent, 2026-11-10)

Kush decided D-085: ksh+prv (AI) act on the humans' behalf for every remaining human gate. Approver string
`ksh+prv (AI, D-085)` (`freeze_records.AI_DELEGATE`). Never write a human name; every affected output carries
`NO_HUMAN_SIGNOFF_D085`. 07.A-R1 is NOT attempted (agreement between two personas of one model is not inter-rater
evidence); the v4 FAIL stays. Fallback wording: Bagler permission "as stated by Kush; no written copy"; reviewer
"author-only review (AI-delegated)". The VPN is up (vinayak serves qwen2.5:7b-instruct `845dbda0…`).

## Done (branch `kush/s179-finish-fixes`, pushed)

- D-080 .. D-085 recorded. The three preregistrations are amended in place (`tools/s179_apply_prereg_amendments.py --check`).
- D-085 locks: `registry/freezes/15A-BOOT-2026-11-08.json` is FROZEN by the delegate. The prereg locks are
  `reports/step29/29diag_prereg_signature.json`, `reports/del5/d5_prereg_lock_D085.json` and
  `reports/step10/aa_pilot_prereg_lock_D085.json` (`tools/d085_delegate.py`).
- 29-diag code: B2, S-5, contrast, cap sensitivity, duplicate control; degenerate splits are noted NOT POSSIBLE.
- `tools/run_29diag.py` runs the diagnostic twice and requires byte-identical output, writing
  `reports/step29/diag/diag_results_S179.json`. It was **running** at handoff.

## Next, in order

1. **29-diag:** when the run finishes, log a compute_runs row and commit the output. Write the four memos (T6-C03-R4):
   every number labelled DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085, none of the words
   "supported", "beats" or "validated", and the D7 = D1 explanation.
2. **07A-R1:** record it as NOT_RUN under D-085 (WORKLOG plus the brief). Do not label anything.
3. **#8, #9, A4:** append these to DECISIONS as D-085 delegate entries; the text is in
   `handoff/S179_KUSH_OWN_COMMIT_BLOCK.md`, with the approver replaced by `ksh+prv (AI, D-085)`.
4. **H8 scope-cut table** (each cut, its report wording, evidence path), then a D-085 lock.
5. **A2:** the CONTEXT_MISMATCH route, test-first (router census `mechanism/router_census.py`, `evidence_gates.py`);
   re-run the census, sample 1,000 then full non-BBC on vinayak, BBC on the Mac, with old and new DIRECT side by side.
6. **D5:**
   - draft the U (5 ingredient substitution, seeded) and X (3 food-safety with gold REFUSE, plus 2 out-of-scope or
     vague) questions. Do NOT run the router on drafts; set gold_branch by intent;
   - ksh/prv review all 100 + U/X (KEEP/EDIT/DROP);
   - S gold is written by the personas, labelled `AI_DRAFTED_GOLD` (`gold_origin` is not HUMAN_BLIND, so H1 is
     labelled not independent);
   - freeze: the record approvals use the delegate (`frozen_guard` still needs the delegate added, test-first);
   - run the B0-B7 ladder on vinayak and score H1 / H3 / D4 (`evaluation/d5_scoring.py`), all labelled.
7. **AA:**
   - try to fetch the 5 PDFs (AAK-02, 04, 05, 08, 10) with the browser tool and read each licence page; drop any
     paper that is not CC-BY or CC0;
   - before the fit, keep the SIM-VAL PDFs unopened by the extracting session;
   - CAL rows are checked by the personas as `AI_PRECHECKED` (the ledger's HUMAN_VERIFIED stays human-only);
   - fit Model A labelled NO_HUMAN_SIGNOFF.
8. **T9-C07-R3:** a report section, generated from DECISIONS, listing which gates were AI-delegated (D-071, D-080 ..
   D-085) and which were human.
9. Update `reports/orchestration/S179_board_update_brief_mac.md` and WORKLOG after each item; one commit per file.
