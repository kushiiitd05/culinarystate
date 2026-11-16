# ksh and prv verdicts on the human-only items, for Kush and Parv to OK or not (S179)

Status: **AI verdicts under D-071, review role only.** ksh (as Kush) and prv (as Parv) are AI personas of one model,
so their agreement is not inter-rater evidence. A verdict decides nothing.
- **Decisions:** an item becomes a decision only when Kush (and Parv where named) answers OK. The scribe then records
  it in DECISIONS with the humans' own words.
- **Signatures and freeze approvals:** "ready" means the text or record checks out. The human still runs
  `tools/human_sign.py` and commits the file.

Written 2026-11-10 against `kush/s179-finish-fixes`.

## A. Decisions: verdict, then your OK

| # | Item | ksh | prv | Why (short) | If you OK |
|---|---|---|---|---|---|
| 1 | **#2 / D-07A-1, 07.A-R1 gate statistic** | **B**: keep the signed R-06 kappa >= 0.80, PABAK as a diagnostic | **B** | Options A, C and E loosen the signed R-06. In the kappa-paradox region a pattern R-06 fails passes them (synthetic counterexample in `07A_R1_preregistration_AMENDMENT_S178_DRAFT.md` §1). B and D are the only options that do not loosen. **Risk stated honestly:** with near-perfect agreement and rare non-CORRECT codes, kappa can collapse again, so B may FAIL again. That would be an honest result. | The agent applies the 07A-R1 amendment with option B; no R-06 amendment entry is needed |
| 1a | D-07A-2, co-gate thresholds | not used under B | not used | — | — |
| 1b | D-07A-3, USDA floor | **U1** (fixed USDA sub-quotas, 100 kept) | U1 | pack and AI recommendation | applied |
| 1c | D-07A-4, planted defect rows | **P1** (10 rows, >= 8 found or NOT_COUNTED) | P1 | only adds a NOT_COUNTED condition | applied |
| 1d | D-07A-5, return deadline | **T2** (13 Nov soft, 20 Nov hard) | T2 | REV-B | applied |
| 2 | **#8, freeze the mode-to-§141 crosswalk** | OK as written | OK | Wording is honest: DIRECT means "a table row exists for this pair", until the context gate lands (item 7) | Kush commits the freeze |
| 3 | **#9, FORM- prefix; freeze the FORM / PARAM / VAL schemas** | OK | OK | Avoids a clash with the ML model-card namespace; drafts exist (`registry/schemas/{FORM,PARAM,VAL}.draft_v1.schema.json`) | Kush commits the freeze before PARAM minting |
| 4 | **#10, accept descriptive pilot validation (D-076)** | OK, with the label fixed at NOT_VALIDATED / RESEARCH_ONLY | OK, same condition | It loosens the formal Step 27 gate, so it must be your call. SIM-VAL has 4 papers against a minimum of 5, so Step 27 cannot pass anyway. | Kush or Parv commits it |
| 5 | **#14, SR Legacy portions under basis code SR_PORTION** | **DEFER** | **DEFER** | No consumer before 26 Nov (lot state deferred, D-080 #1); deferring is within the persona line | nothing changes; revisit after the talk |
| 6 | **#18, sign the H8 scope-cut register** | OK in principle, **not ready** | not ready | The text points at a table file that does not exist yet. The agent writes it (each cut, its report wording, evidence path) before you sign. | sign after the table lands |
| 7 | **A2: physics cap plus the TARGET_ABSENT / CONTEXT_MISMATCH routes (H4)** | OK | OK | (1) The evaporation cap is already in code (S176) and the old DRY/FAT fields are on the superseded register. (2) TARGET_ABSENT exists (`decision/demo_context.py`, `mechanism/evidence_gates.py`); **CONTEXT_MISMATCH is not yet a route value**. | the agent adds CONTEXT_MISMATCH, test-first, and re-runs the router census with old and new counts side by side |
| 8 | **#22, SSOT v16 not applied before the talk** | OK | OK | v15 governs; a one-page delta goes in the report | Kush commits it |
| 9 | **A4, D-071 addendum (the persona line)** | OK | OK | It is the rule followed since D-080; writing it down closes REV-B G-03 | Kush commits it |
| 10 | **A6, demo hosting** | **DEFER** | DEFER | Your "core before demo" rule; decide after H1/H3 | nothing changes now |

## B. Signatures and the freeze: readiness

| What | ksh | prv | Check done | You do |
|---|---|---|---|---|
| D5 pre-registration (`reports/del5/d5_benchmark_preregistration_DRAFT.md`, sha256 `1c174553…`) | READY | READY | `--check` reproduces it from v1 + amendment; no open option (D-083); model digest and e5 revision filled | Kush and Parv each: `human_sign.py sign --doc D5` |
| AA pre-registration (`reports/step10/aa_pilot_preregistration_DRAFT.md`, `6f12e617…`) | READY | READY | amendment applied; firewall and domain gate present | Kush and Parv: `--doc AA`. Before verification, Kush also confirms each licence on the publisher page (D-AA-5). |
| 29-diag pre-registration (`reports/step29/29diag_preregistration_DRAFT.md`, `ce7f0e1f…`) | READY, after the freeze | READY | amendment applied; the B2, S-5, contrast, cap and duplicate code exists and is tested (410 passed) | Kush: approve the freeze, then `--doc D29` |
| 15A-BOOT freeze record | READY to approve | READY | `freeze_problems` shows only NOT_APPROVED and NO_HUMAN_APPROVAL; every ledger hash still matches | Kush: `human_sign.py approve-freeze --snapshot 15A-BOOT-2026-11-08 --approver "Kush Tokas"` |
| 07A-R1 pre-registration | **NOT READY** | NOT READY | waits on item 1 | after your OK on item 1, the agent applies it; then you sign |

## C. Facts only you know (no verdict possible)

| # | Item | Fallback wording if nothing arrives |
|---|---|---|
| #19 | Prof. Bagler's written permission | "permission as stated by Kush; no written copy" (D-045 W3) |
| #23 | calendar and machines, 9-25 Nov | fallback levels L0-L3 (D-080 A7) apply on the slip triggers |
| A5 | outside reviewer for 20 D5 items | "author-only review" |

## D. Human work: no persona may do it as yours

These are the 07A-R1 labels, the five PDFs and the licence pages, the CAL and SIM-VAL verification, the D5
blind-first review, and the 30-claim audit.
- **Offer:** ksh and prv can make an AI pre-pass of any of them, labelled a "dated AI draft", to speed you up.
- **Limit:** a pre-pass never counts as the gate. For the D5 S gold it would also make those rows ENGINE- or
  AI-anchored, not HUMAN_BLIND, so do not ask for a pre-pass on the S answers.
