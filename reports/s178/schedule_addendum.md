# Schedule addendum: consolidated day-by-day, 8-26 Nov 2026 (T9-C26-R1)

Status: **AI_DRAFTED / PROPOSED** (S178 GOVDOC lane, Mon 9 Nov 2026). Nothing here is a decision or a commitment by Kush or Parv; their availability is **not in the repo** and is unknown (D-071: the humans own every signature, label, freeze and fact). Hours are estimates (UNVERIFIED; P1 timing was never measured, D-061).

## 0. Does the human operations pack already cover the schedule? Verdict: PARTIAL, so this addendum

`handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md` (written Sun 8 Nov) covers most of what T9-C26-R1 asks:

| Acceptance part | Where it is | Covered? |
|---|---|---|
| Day-by-day schedule 9-16 Nov with named human hours per person per day | pack 1.2 (Kush 19.9 h, Parv 17.2 h) | yes, but pre-board (see section 3) |
| 17-25 Nov | pack 1.4 | partly: Tue 17 has **no hours** (blank cells), 25 and 26 Nov have no rows beyond "present", and the board's additions are missing |
| Human tasks front-loaded | pack 0, 1.1, 1.3 (decision sitting Mon 9; signatures by Wed 11 noon) | yes |
| Slip triggers with dates and pre-written fallback wording | pack 5.1 (levels L0-L3 with talk wording) and 5.2 (14 dated triggers incl. "no benchmark freeze by 17 Nov") | yes as text; **not yet adopted by a human** |
| "Fallback wording pre-agreed" | decision **A7** (pack 2, due Tue 10): "Adopt section 5 as the plan of record" | **no**: the wording is AI_DRAFTED until Kush and Parv adopt it at the sitting |

So the schedule exists; what was missing is (a) one table for the whole window that matches the S178 board's hours, (b) the days the pack leaves blank, and (c) the human adoption of the fallback wording. (a) and (b) are the table below. (c) cannot be done by an agent: item T9-C26-R1 stays **PARTIAL (BLOCKED_HUMAN for "pre-agreed")** until decision A7 is recorded.

## 1. Consolidated day by day (hours are the board's: `reports/orchestration/S178_EXECUTION_BOARD.md` sec 4-8)

K = Kush, P = Parv. A day's agent and compute work is in `reports/s178/compute_ledger_remaining.md` (job ids in brackets).

| Date | K h | P h | Human tasks that day | Gate | Agent / compute | If it slips (pack 5.2, wording pre-written) |
|---|---|---|---|---|---|---|
| Sun 8 | 0 | 0 | none | | agents pre-draft the amendment texts, ops pack, board | |
| **Mon 9** | **2.1** | **2.0** | decision sitting 90 min (both); K: permission email to Prof. Bagler (#19, 0.3), ratify D-068 in own commit (A4, 0.3); P: own ratifications (A4, 0.5) | decisions #1 (lot state) and #2 (07.A statistic) due | commit the uncommitted S177 lanes (G1); correct pack decision #6 text (G4) before the sitting | lot state defers to stretch; without #2 the 07A-R1 prereg cannot be signed and 07.A stays FAILED on record |
| **Tue 10** | **1.55** | **1.1** | after the lock note: both sign the AA prereg (0.3 each); K downloads 5 PDFs and checks licences (1.0), ssh test to vinayak (0.25); P authorises the environment lock (0.3) and checks licence facts AAK-01/09/11 (0.5) | **prereg edit lock + hashes** (afternoon); decisions #3-#7, #20, #23, A1, A3, A6, A7; **K confirms calendar, talk day and VPN (#23)** | Mac merge/push (G3); M-01, M-03, M-04 | no edits after the lock; missing PDFs: fit on the 4 papers present; Step 35 becomes "designed, not run"; governance pack ships with "relays unratified" disclosed |
| **Wed 11** | **3.9** | **2.8** | sign 07A_R1 and D5 (0.8 each); K also signs 15A-BOOT, 29-diag, H8 (0.9) and asks an outside reviewer (0.2); **07.A labels, session 1 (2.0 each)** | **all signatures by noon**; decisions #8, #18 (sign), A5 | AA CAL extraction (Mac); tickets A4-A6 due (G2); M-02 starts | each unsigned prereg is reported NOT_RUN, never run on an AI signature; if one human is out: "signed by Kush; Parv pending" |
| Thu 12 | 0 (buffer) | 3.5 | P: 07.A labels session 2 (1.5), D5 blind S answers (1.5), own 07.A/07I-C confirmation (T9-C13-R4, 0.5) | all remaining decisions (#9-#17, #19, #22) due; AA verification packets issued; U/X drafts merged | J-01 + J-02 start | 29-diag not signed: drop it, keep the "D7 = D1" suspicion on the failure slide |
| **Fri 13** | **3.15** | **2.0** | K: 07.A labels session 2 (1.5), D5 blind S answers (1.5), confirm demo machine and slot (0.15); P: D5 review (2.0) | **07.A-R1 labels in**; VPN decision #21 | J-02 ends; J-03; J-04; report skeleton (Mac) | 07.A stays FAILED on record, 23b closed: "second attempt pre-registered; labels not returned" |
| Sat 14 | 4.0 | 3.0 | AA verification of every CAL row (3.0 each); K: D5 review (1.0) | 07.A-R1 scored (agent); 29-diag run twice; **D5 dry run on vinayak** (V-01) | M-05; V-01 | dry run fails: fix the route; plan the manjot-CPU fallback |
| **Sun 15** | **3.0** | **2.0** | K: D5 review (2.0), read 29-diag memos (0.5), 07.A joint adjudication with P (0.5); P: D5 review (1.0), read NEG register rows (0.5), 07.A adjudication (0.5) | **AA CAL rows dual-verified** | memos | no PARAM and no SIMULATE result; SIMULATE ships "code-tested only"; Model A NEED_DATA if below the prereg minimum |
| **Mon 16** | **1.8** | **1.8** | D5 finish with U and X (1.0 each), joint reconcile (0.5), confirm benchmark freeze (0.3) | **D5 reviewed and frozen; Model A fit frozen** (hash committed); hard stop for the freeze is **Tue 17** | J-05, J-10 | level L2: H1 and H3 NOT_RUN; SIM-VAL drops to SHOULD |
| **Tue 17** | **4.35** | **2.25** | review `corpus_can_say` report (1.0), skim EVD card (0.5), check the <=8 slide defaults (1.0 each), read H2 slide (0.5), read the fit-freeze hash and report (0.25), SHOULD decision batch (0.75 each), demo dry run (0.35); P: lineage statement (0.5) | vinayak reachable (else manjot-CPU fallback); **D5 hard stop** | V-02 starts; J-05, J-06, J-07 | LLM rungs NOT_RUN if vinayak is unreachable (written into the D5 prereg in the lock) |
| Wed 18 | 2.0 | 2.0 | verify SIM-VAL rows from 4 papers (2.0 each) | SIM-VAL verified | J-07 ends, J-08, J-10 | |
| Thu 19 | 0.6 | 0.6 | blind claim audit of 30 claims, part 1 | **results in** (H1, H3) | V-02 ends; M-06 (BBC router) | level L3: the report is the router census and gate table only |
| Fri 20 | 1.75 | 1.65 | claim audit part 2 (0.65 each); edit physical-layer slides (1.0 each); K optional cloudflared (0.1) | claim audit back; slides edited | J-08/J-09/J-10 census | L1 for H3 if the audit is missing |
| Sat 21 | 0.25 | 0 | K optional: choose the static-page host | **code and result freeze**; full report draft | M-07 leakage grep; J-04 reproduction | nothing new enters the talk; cached demo answers plus a screen recording |
| Sun 22 | 3.0 | 3.0 | edit report and deck | report draft delivered | | agent ships the draft with every number cited to a file |
| Mon 23 | 4.1 | 3.75 | edit (2.0 each), contributions section (1.0), number-class exceptions (0.5), read the Q&A sheet (0.25), K records the 4 demo queries (0.35) | "cannot claim" sheet delivered; **confirm talk day and slot (T9-C20-R3)** | | |
| **Tue 24** | 2.0 | 2.0 | timed rehearsal with the live-demo fallback and Q&A | rehearsal | | |
| Wed 25 / Thu 26 | present | present | the talk: **day, slot and length are not verified** (decision #23, T9-C20-R3) | | | |

Totals (check): 9-16 Nov K 19.5 h, P 18.2 h (budget 16-20 h each; Kush has 0.5 h of slack and Thu 12 as the only buffer); 17-20 Nov K 8.7, P 6.5; 21-23 Nov K 7.4 (7.35 rounded), P 6.8 (6.75); total 9-23 Nov K about 35.6, P about 31.5, plus Tue 24 (2.0 each).

## 2. Slip triggers: what the pack lacks and the board adds (all proposed, not adopted)

1. **If the Mon 9 sitting slides**, the lock slides from Tue 10 afternoon to Wed 11 noon at the latest; W2 then loses a labelling day and the 07.A labels move to Sat 14. 07.A is cut first (pack 1.1).
2. **Mac tickets A4-A6** (quantity-slash, size words, POINT only for stated mass) are due Wed 11. If late, the non-BBC census re-run moves from Thu 12-Fri 13 to Fri 13-Sat 14 and every slide number taken from the S177 census is quoted "before the fix" (board sec 12).
3. **Decision #6 text** in the ops pack (smallest significant results "8-0, 9-1, 10-2" at n = 30) is wrong: exact McNemar is already significant at 6-0 and 7-0 (PREREG finding 6). The pack file is orchestrator-owned and was **not edited by this lane**; correct it before the sitting reads it (board G4).
4. **Embeddings (decision #4).** B1/B2 need an embedding model; manjot has no torch, so the "deterministic rungs on manjot CPU" fallback fully works only for B0, B4 and B5T unless embeddings are pre-computed or served by the Mac or vinayak (`reports/s178/compute_ledger_remaining.md` sec 5).
5. **Over 20 h in 9-16 Nov** (Kush at 19.5 h): cut in this order, none touching a MUST gate: 07.A-R1 first (-3.5 h each), then 07.A late return to Fri 20, never the D5 review or the AA verification (board sec 8).
6. **W3 reading load** (Tue 17 K 4.35 h): the SHOULD decision batch, the slide-default checks and the card skim are not on a gate and fall back to their stated defaults if skipped (board sec 6).

## 3. Differences from the pack's day-by-day, so nobody is surprised

| Item | Pack | This addendum (board) | Effect |
|---|---|---|---|
| Tue 10, Parv | 0.6 h | 1.1 h | +0.5: licence facts AAK-01/09/11 moved from Kush to Parv |
| Thu 12, Parv | 3.0 h | 3.5 h | +0.5: own 07.A/07I-C confirmation (T9-C13-R4) |
| Sun 15, Kush | 3.35 h | 3.0 h | -0.35: demo dry run moved to Tue 17 |
| Tue 17 | no hours | K 4.35, P 2.25 | reviews and the SHOULD decision batch added by the board |
| Mon 16, Kush | 1.8 h and confirm the fit freeze live | 1.8 h; the fit-freeze hash is read Tue 17 | no extra hours |

## 4. Status for T9-C26-R1

**PARTIAL.** Done: schedule with named per-person hours for every day 9-24 Nov (this file plus the pack), slip triggers with dates and pre-written wording (pack 5, board sec 4-9). Not done and not doable by an agent: the humans' availability (Tue 10, #23), the adoption of the fallback wording (decision A7), and the talk day and slot. Evidence: `handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md` sec 1.2, 1.4, 5.1, 5.2; `reports/orchestration/S178_EXECUTION_BOARD.md` sec 4-8.
