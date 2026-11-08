# Human operations pack: Kush and Parv, 9 to 25 Nov 2026

Status: **AI_DRAFTED / PROPOSED**. Written Sunday 8 Nov 2026 by the S176 OPS lane (an AI agent). Nothing here is a decision, a signature or an approval (D-071). Every "recommendation" is the agent's, built from the two reviews and the consensus plan. You choose.

Hours are ledger estimates and are **UNVERIFIED** (P1 timing was never measured, D-061). Dates are the consensus plan's (section 4.1) unless a line says otherwise. The talk is Wed 25 / Thu 26 Nov.

Sources: `reports/orchestration/ssot_consensus/CONSENSUS_PLAN_2026-11-08.md` (called "consensus"), `registry/component_ledger_v1.csv`, `reports/orchestration/review/S176_REV-A_science.md` ("REV-A"), `reports/orchestration/review/S176_REV-B_eval_governance.md` ("REV-B"), `handoff/FINISH_PLAN_2026-11-07.md`, `DECISIONS.md` (D-045, D-071).

## 0. Read this first

**The five things to do first** (details in sections 1 to 3):

1. **Mon 9 Nov, evening: hold the 90-minute decision sitting** (section 2). Decisions #1 and #2 are due that day. Everything else hangs on them.
2. **Do not sign anything dated 8 Nov.** The prereg files in the tree today are drafts. The agent edits them, then locks and hashes them (target: Tue 10 Nov afternoon). You sign only the locked bytes.
3. **Tue 10 Nov: Kush signs the AA prereg, then downloads 5 PDFs** (AAK-02, 04, 05, 08, 10) in a browser. About 1.3 h.
4. **Wed 11 Nov by noon: all signatures done** (07.A-R1, D5, AA for both of you; 15A-BOOT, 29-diag and H8 for Kush). Then start the blind work the same day.
5. **Label and verify alone.** 07.A-R1 labels by Fri 13 Nov. AA rows by Sun 15. D5 review by Mon 16. No talking about items until both files are back.

**Marks used in this pack**

| Mark | Meaning |
|---|---|
| SIGN | A signature, freeze approval or ratification. Human only. An AI persona (ksh, prv) can never do it (D-071). |
| HUMAN | Not a signature, but a human-only act: it amends a ruling, loosens a gate, or states a fact only a person knows (D-071 list; REV-B rule in section 2.2). |
| choice | An ordinary design choice. D-071 would let ksh/prv decide, but we recommend you decide all of them this week because each one changes text you sign. |
| Mac | The task runs on Kush's Mac (authoritative ledgers, git-ignored packets, BBC data). Packets and review sheets are **not** in the server worktree. |

---

## 1. This week on one page

### 1.1 Rules of the week

- **Sign first, then open.** No packet, review sheet or verification sheet is opened before both of you have signed its prereg. Opening first voids the attempt.
- **Alone means alone.** No chat, no calls, no hints about items until both returned files exist and the agent has recorded their hashes.
- **Own hand.** Each of you types your own signature file and commits it from your own session. Nobody types for the other (the D-046 relay problem, REV-B B2.2).
- **One tree for ledgers.** Do not append to `ledgers/data/{EVD,COND,SRC,MEAS,SNAP,STUDY,PROC,ING,SVAR}.jsonl` after Kush approves the 15A-BOOT freeze. Any change voids it (`SNAPSHOT_HASH_MISMATCH`).
- **Budget.** Target 16 to 20 h each for 9 to 16 Nov (T9-C26-R4). The plan below uses 19.9 h (Kush) and 17.2 h (Parv).
- **If a day slips, cut in this order:** 07.A-R1 first (it opens nothing before 25 Nov), then the 29-diag, then P1b. Never cut the D5 review or the AA verification.

### 1.2 Day by day, 9 to 16 Nov (hours in brackets)

| Date | Kush | Parv | Gate that day (agent unless stated) |
|---|---|---|---|
| **Mon 9** | Sitting (1.5). Send the permission email, section 2 #19 (0.3). Ratify D-068 in own commit (decision A4, 0.3). **2.1 h** | Sitting (1.5). Write own ratifications (decision A4, 0.5). **2.0 h** | **Due: decisions #1 and #2.** Agent pre-drafts all amended prereg texts under the recommended options (proposed prep, Sun night). |
| **Tue 10** | (Confirm availability.) After the lock note arrives: sign AA prereg (0.3). Download 5 PDFs and check licences (1.0). Test ssh to vinayak (0.25). **1.55 h** | After the lock note: sign AA prereg (0.3). Authorise the learning-environment lock (0.3). **0.6 h** | **Prereg edit lock + hashes** (target afternoon). Due: decisions #3 to #7, #20, #23. 07.A packet and D5 sheets re-issued if the sitting chose the REV-B options. |
| **Wed 11** | Sign 07.A-R1, D5 (0.8). Sign 15A-BOOT freeze, 29-diag, H8 (0.9). Ask an outside reviewer (0.2). **07.A labels, session 1 (2.0).** **3.9 h** | Sign 07.A-R1, D5 (0.8). **07.A labels, session 1 (2.0).** **2.8 h** | **Signatures complete by noon.** AA CAL extraction of the new PDFs starts (11 to 12 Nov). Due: decision #8. |
| **Thu 12** | **Buffer day.** **0 h** | 07.A labels, session 2: finish and return (1.5). D5 review, blind S answers (1.5). **3.0 h** | Due: decisions #9 to #19, #22 (all taken at the sitting). H8 register due (signed Wed). AA extraction complete; verification sheets issued. |
| **Fri 13** | 07.A labels, session 2: finish and return (1.5). D5 blind S answers (1.5). Confirm the demo machine and the talk slot (0.15; DEPLOY H-4, H-7). **3.15 h** | D5 review (2.0). **2.0 h** | **07.A-R1 labels due.** VPN confirmed (#21) or manjot-CPU fallback in force. |
| **Sat 14** | AA verification of every CAL row (3.0). D5 review (1.0). **4.0 h** | AA verification of every CAL row (3.0). **3.0 h** | 07.A-R1 scored (agent). 29-diag run twice; memos written. D5 dry run on vinayak. |
| **Sun 15** | D5 review (2.0). Read 29-diag memos (0.5). 07.A joint adjudication, with Parv (0.5). Demo bundle dry run on the Mac (0.35; DEPLOY). **3.35 h** | D5 review (1.0). Review NEG register rows (0.5). 07.A joint adjudication (0.5). **2.0 h** | **AA CAL rows dual-verified (return both files).** |
| **Mon 16** | D5 finish, U and X blocks (1.0). Joint reconcile (0.5). Confirm benchmark freeze (0.3). **1.8 h** | D5 finish, U and X blocks (1.0). Joint reconcile (0.5). Confirm benchmark freeze (0.3). **1.8 h** | **D5 reviewed and frozen. Model A fit frozen** (agent, hash committed). Hard stop for the benchmark freeze is Tue 17. |
| **Total 9 to 16 Nov** | **19.9 h** | **17.2 h** | |

If you pick the larger S pool (section 2, A1 option B), add about 1.5 h each to D5. Kush then reaches about 21.4 h. Move the Sun 15 memo reading to Tue 17 to ease it.

### 1.3 Hours by task, 9 to 16 Nov

| Task | Kush (h) | Parv (h) | Notes |
|---|---|---|---|
| Decision sitting | 1.5 | 1.5 | One joint sitting |
| Signatures (prereg and freeze files) | 2.0 | 1.1 | Kush also signs 15A-BOOT, 29-diag, H8 |
| Own ratifications and governance repairs | 0.3 | 0.5 | REV-B G-03; not in the consensus list |
| Admin: email, ssh test, outside reviewer, env lock, demo machine and slot, demo dry run | 1.25 | 0.3 | Kush: 0.3 + 0.25 + 0.2 + 0.15 + 0.35. Parv: env lock. The last two Kush items come from `handoff/DEPLOYMENT_AND_PRESENTATION_PLAN_2026-11-08.md` (DEPLOY lane, proposed) |
| 5 PDF downloads and licence checks | 1.0 | 0 | Kush only (browser, Mac) |
| 07.A-R1 labels | 3.5 | 3.5 | 3 to 4 h each |
| 07.A joint adjudication | 0.5 | 0.5 | After scoring on 14 Nov |
| AA CAL verification | 3.0 | 3.0 | 3 h each |
| D5 review (incl. blind S answers, U and X) | 6.3 | 6.3 | 6.0 plus 0.3 freeze confirm |
| Memo and NEG register reading | 0.5 | 0.5 | Split so each reads one |
| **Total** | **19.9** | **17.2** | Consensus ledger sum is 26 to 35 h; the decision sitting is the saving |

### 1.4 After 16 Nov

| Date | Kush | Parv | Gate (agent unless stated) |
|---|---|---|---|
| Tue 17 | | | vinayak reachable (else manjot-CPU fallback). AA SIM-VAL extraction. D5 hard-stop for the freeze. |
| Wed 18 | Verify SIM-VAL rows from 4 papers (2.0). | Same (2.0). | Model A already frozen on 16 Nov. SIM-VAL stays closed until then. |
| Thu 19 | Blind audit of 30 claims, part 1 (0.6). | Same (0.6). | H1 and H3 runs done; results in. Claim-audit sheets issued. |
| Fri 20 | Claim audit, part 2 (0.65). Edit physical-layer slides (1.0). Optional: install `cloudflared` if you want the tunnel (0.1; DEPLOY H-6). | Same, without the tunnel. | Edits to slides by 20 Nov. 07.A-R1 absolute latest return (REV-B only; consensus trigger was 13 Nov). |
| Sat 21 | Optional: choose a place for the static demo page (0.25; DEPLOY H-5). | Nothing. | **Code and result freeze.** Full report draft. Nothing new enters the talk after this. |
| Sun 22 | Edit report and deck (3.0). | Same. | |
| Mon 23 | Edit (2.0). Contributions section (1.0). Number-class exceptions list (0.5). Read the Q&A sheet (0.25). Screen-record the 4 demo queries (0.35; DEPLOY H-8). | Same, without the recording. | "Cannot claim" sheet delivered. |
| **Tue 24** | **Timed rehearsal with the live-demo fallback and Q&A (2.0).** | Same. | |
| Wed 25 / Thu 26 | Present. | Present. | |
| Total 17 to 25 Nov | about 13.7 h | about 13.0 h | |

### 1.5 Calendar facts to confirm at the sitting (decision #23)

| Fact | Source | Confirm |
|---|---|---|
| Kush: any blocked days 9 to 16 Nov | **Not known. Not in the repo.** | Kush |
| Parv: any blocked days 9 to 16 Nov | **Not known. Not in the repo.** | Parv |
| Presentation: day (25 or 26 Nov), slot, talk length, projector connector, shared Q&A (STATUS says the dates were never independently verified) | `STATUS.md`; DEPLOY H-7 | Both |
| Parv's machine for blind work: is Parv's laptop back? (D-064 used Kush's Mac in a separate clone while it was down) | `reports/step19/P1b_design_amendment_PROPOSED.md` | Parv |

---

## 2. The decision sitting

**Target: one 90-minute sitting, Mon 9 Nov, evening, both of you, this file open.** Reason: #1 and #2 are due that day and the prereg lock (Tue 10 Nov) needs #2 to #7. If it must move to Tue 10 Nov, take only #1 and #2 on Mon by message (20 min), hold the full sitting Tue evening, and the lock slides to Wed 11 noon. That costs one day of the labelling window.

**Pre-read (15 min each, before the sitting):** the summary table below, then #2, #6 with A1, and A3. They change the text you sign.

### 2.1 Run of show (90 min)

| Min | Block | Items |
|---|---|---|
| 0 to 4 | Open | Scribe named. Calendar and machines (#23). |
| 4 to 16 | 1. Due Mon 9 | #1 lot state (4). #2 07.A gate (8). |
| 16 to 41 | 2. Lock-critical, due Tue 10 | #3 (3), #4 (3), #5 (2), #6 with A1 (8), #7 (3), A3 (3), #20 (3). |
| 41 to 69 | 3. Due 11 to 13 Nov | #8 (2), #9 (1), #10 (3), #11 (2), #12 (4), #13 (1), #14 (1), #15 with A2 (4), #16 (1), #17 (1), #18 (3), #19 (3), #21 (1), #22 (1). |
| 69 to 85 | 4. Review add-ons | A4 governance (7), A5 outside reviewer (2), A6 demo hosting and licence calls (5), A7 fallback levels (2). |
| 85 to 90 | Wrap | Read back every choice. Name who commits each HUMAN or SIGN entry. |

If time runs out, take #9, #14, #16, #17, #22 by message. Their defaults are safe.

### 2.2 How to record a decision

- Proposals on this branch start at **D-078** (`handoff/ORCHESTRATION_TAKEOVER_2026-11-08.md`). The scribe numbers them in order.
- Header to use for every entry:
  `### D-0NN · 2026-11-09 · <title> (decided by Kush and Parv in the 9 Nov sitting, in their own words; text drafted by AI_AGENT and adopted by them; entered by <scribe>)`
- **HUMAN and SIGN entries are committed by the human named, from their own session.** The scribe may prepare the text but does not commit it. (D-068 was appended by the agent on a verbal waiver; REV-B B2.2 calls that a breach. Do not repeat it.)
- The blocks below are written for the **recommended option**. If you choose another, change the first line and use the "if you pick it" text.
- REV-B proposes this rule, which this pack follows: **an AI persona may tighten, defer, withdraw or refuse. It may never loosen, close or sign.** It is not yet a DECISIONS entry (see A4).

### 2.3 Summary table (all 30)

| # | Id | Question (one line) | Type | Rec. | Due |
|---|---|---|---|---|---|
| 1 | T3-C22-R7 | Lot-state layer before 25 Nov? | choice (Kush's item) | A defer | Mon 9 |
| 2 | T2-C05-R5 | 07.A gate: kappa or AC1? | HUMAN (amends R-06) | B2 AC1, hardened | Mon 9 |
| 3 | T7-C01-R2 | Step 35: run descriptive rungs or only design? | choice | A design only | Tue 10 |
| 4 | T8-C06-R2 | B1/B2 embedding: bge or e5-large-v2? | choice | B e5-large-v2 | Tue 10 |
| 5 | T8-C12-R1 | H3/B7 wording | choice | A "uncalibrated" | Tue 10 |
| 6 | T9-C12-R1, T8-C04-R2 | Add power note and circularity caveat before signing? | choice | A add both | Tue 10 |
| 7 | T6-C03-R5 | Add D2-vs-D3 contrast to 29-diag before signing? | choice | A add | Tue 10 |
| 8 | T0-C06-R1 | Freeze the mode-to-§141 crosswalk | HUMAN (freeze) | A approve | Wed 11 |
| 9 | T5-C07-R1 | FORM- or MODEL- prefix; freeze schemas | HUMAN (freeze) | A FORM- | Thu 12 |
| 10 | T5-C13-R3 | Accept descriptive pilot validation (D-076) | HUMAN (loosens a gate) | A accept, label fixed | Thu 12 |
| 11 | T3-C17-R1 | D3 claim at the talk | choice | B no accuracy claim | Thu 12 |
| 12 | T5-C05-R4 | Q20, Q22, Q23 rules | choice | yes, taxonomy, flip rule | Thu 12 |
| 13 | T3-C07-R3 | Food.com lines with no units | choice | A presence-only | Thu 12 |
| 14 | T3-C04-R3 | SR Legacy as portion authority | HUMAN (basis code) | A, not used before 26 Nov | Thu 12 |
| 15 | T4-C09-R1 | Two-zone surface model | choice | B limitation (plus A2 cap fix) | Thu 12 |
| 16 | T4-C22-R1 | Layer 1 and 2 in Step 31 | choice | A EVD-row arm only | Thu 12 |
| 17 | T8-C02-R2 | SEMANTIC branch | choice | A abstain | Thu 12 |
| 18 | T9-C07-R4 | Sign the H8 scope-cut register | SIGN | A sign | Thu 12 |
| 19 | T9-C07-R2 | Written permission from Prof. Bagler | HUMAN (fact) | A get it in writing | Thu 12 |
| 20 | T9-C25-R5 | Install authorisation | choice | A Mac only, pinned | Tue 10 |
| 21 | T9-C25-R3 | VPN to vinayak | choice | test Tue 10, else fallback | Fri 13 |
| 22 | T0-C01-R1 | Apply SSOT v16 before the talk? | HUMAN (Kush's line) | A do not apply | Thu 12 |
| 23 | T9-C26-R1 | Calendar and machines | HUMAN (fact) | confirm | Tue 10 |
| A1 | T8-C20 (REV-B G-05, 06, 07, 12, 13) | D5 prereg design fixes | choice | A all fixes | Tue 10 |
| A2 | REV-A V2, V5 | Cap Layer 2 heat at 100 C; add TARGET_ABSENT and CONTEXT_MISMATCH | HUMAN (H4 enum) | A yes | Thu 12 |
| A3 | REV-A V7, REV-B F-09 | AA prereg: domain gate and RESEARCH_ONLY | choice | A add | Tue 10 |
| A4 | REV-B G-03 | Governance repairs and the AI-persona line | SIGN | A all four | Mon 9 (REV-B) |
| A5 | REV-B G-20, T9-C17-R3 | Name an outside reviewer | HUMAN (fact) | A ask now | Wed 11 |
| A6 | T8-C18-R1, DEPLOY H-1, H-2 | Demo hosting, what may leave the Mac, LLM path | choice (Kush) | A local live, static page, no key | Tue 10 |
| A7 | T9-C26-R2 | Adopt fallback levels L0 to L3 | choice | A adopt | Tue 10 |
| (23 rows are from consensus 6.2; A1 to A7 come from REV-A and REV-B and are not in that table.) | | | | | |

---

### Block 1. Due Monday 9 Nov

#### #1 · T3-C22-R7 (Q39) · Lot-state layer before 25 Nov? · choice (Kush's own item) · due Mon 9

| Option | If you pick it |
|---|---|
| **A. Defer to stretch (recommended)** | No human hours. No lot-state number in the talk. At most one design slide, labelled NON_CITABLE. The lane code (`src/culinarystate/lotstate/`) stays DRAFT. |
| B. Minimal slice only (lot members, presence-only composition) if an agent is idle | No human hours for the slice. It is design only, never a result. Any real use needs 4 to 8 h of human ING-to-SR match checks, which you do not have. |
| C. Full layer [K] | Agent time leaves H1/H3 and the first SIMULATE. Needs hundreds of human-verified ING-to-SR matches in the same two weeks. Cannot be evaluated (no gold). |

**Why A.** REV-B Q39 says cut it, with seven reasons. Food.com has no units, so composition is presence-only for about 85 % of the corpus. The ING-to-SR crosswalk is 0 % resolved. Every output would be MODEL_DERIVED with no gold. No hypothesis H1 to H3 depends on it. The router stays DIRECT or UNKNOWN, so the headline does not move. No DECISIONS entry authorises it. R-FEAS (consensus 6.2 #1) agrees. REV-A calls the design "sound in spirit" but wants four changes first (phases, a provenance lattice, physical edges, a pH bound). That is post-talk work.

```
Q39 (lot-state layer): DEFERRED past the 25 Nov talk (option A). No lot-state result, figure or number appears in the talk or report; at most one design slide labelled NON_CITABLE. The lane code stays DRAFT. Reason: no hypothesis H1-H3 depends on it, it needs human verification of ING->SR matches that competes with the H1/H3 and AA tasks, and it cannot be evaluated (no gold). Source: REV-B Q39, R-FEAS.
```

#### #2 · T2-C05-R5 · 07.A gate: kappa or AC1? · HUMAN (amends R-06) · due Mon 9

This is the most important decision of the week. It must be taken **before** anyone signs the 07.A-R1 prereg, and it must be in **Kush's own hand** (it amends a ruling).

| Option | If you pick it |
|---|---|
| A. Keep kappa as the gate (R-06). AC1 diagnostic only | No deviation to record. The agent rewrites prereg section 3 back to kappa. High chance of repeating the v4 paradox: v4 had raw agreement 0.9944 and kappa 0.0. A FAIL would then say nothing about the normaliser. You still spend 3 to 4 h each. |
| B1. AC1 as drafted: pooled AC1 at or above 0.80, agreement only | Fastest. But REV-B shows it **would have passed v4** (AC1 0.994) and tolerates about 179 of 900 disagreeing cells (19.9 %). Reads as shopping for a metric until the gate passes. Not recommended. |
| **B2. AC1 with REV-B's hardening (recommended)** | Defensible. Agent work about 2 h: re-issue the packet, extend the scorer. About 0.3 h extra per rater for planted rows. List below. |

**B2 contents (REV-B Q24 and G-01; numbers are PROPOSED, you set them):**

1. Pooled AC1 at or above **0.95** (at most about 45 disagreeing cells of 900), judged on the lower 95 % condition-bootstrap bound.
2. **Accuracy co-gate** after joint adjudication: at most 1 of 100 conditions with a WRONG_*, INFERRED or SHOULD_BE_AMBIGUOUS code in a critical field, and at most 4 of 100 in any field. AC1 measures agreement, not correctness: two raters who both code every cell wrong would score AC1 = 1.
3. **10 planted-defect rows** (known-wrong values made by a fixed edit of real conditions outside the 100). Each reviewer must flag at least 8 of 10 or that reviewer's file is NOT_COUNTED. This is the only design that catches a constant-code reviewer in advance (v4: Parv's 900 of 900 codes were CORRECT).
4. Add `duration_judgement` and `temperature_value_judgement` to the critical fields. All 5 v4 disagreements sat in those two fields.
5. Floor of 20 USDA-dialect conditions (R1 packet today: Phenol-Explorer 78, Bognar 18, USDA 4).
6. Replace the `IDENTICAL_JUDGEMENTS` rule (it makes a perfectly agreeing pair NOT_COUNTED) with file timestamps, free-text overlap and the planted-row result.
7. Print AC1 and agreement on informative cells only (VALID or AMBIGUOUS), and positive specific agreement on flagged cells, as diagnostics.

**Why B2.** REV-B Q24: "statistic yes; 0.80 and agreement-only logic no". R-SCI: AC1 only as a recorded deviation. Consensus 6.2 #2 says either route is valid if decided before signing.

**Four conditions that go with B (all of them):** a DECISIONS entry written by Kush that amends R-06 for attempt 07.A-R1 only; both of you sign before the packet opens; the report says "gate redefined after a failed gate"; the v4 FAIL (kappa 0.0, raw agreement 0.9944, 900 cells, 5 disagreements) is never relabelled or rescored.

**What a valid 07.A unlocks.** Nothing before 25 Nov. 23b also needs 15b frozen, and 15b needs 08b, Steps 11, 12, 14 verdicts and a human-verified test subset. State it in the ruling.

```
07.A gate for attempt 07.A-R1 ONLY (amends R-06 / D-027 for this attempt): pooled Gwet AC1 replaces kappa as the gate statistic on the fresh packet, with these conditions fixed before any label exists: pooled AC1 >= 0.95 on the lower 95% bound; accuracy co-gate (<= 1/100 critical-field defects, <= 4/100 any-field defects after adjudication); 10 planted-defect rows (a reviewer must flag >= 8 or the file is NOT_COUNTED); duration and temperature value added to the critical fields; USDA floor of 20 conditions. The v4 FAIL (kappa 0.0, raw agreement 0.9944, 900 cells, 5 disagreements) stays on record and is never rescored. The report will say "gate redefined after a failed gate". A PASS opens nothing before 25 Nov: 23b stays BLOCKED until 15b is frozen. Source: D-075, REV-B Q24/G-01, R-SCI. Committed by Kush from his own session.
```

---

### Block 2. Lock-critical, due Tuesday 10 Nov

#### #3 · T7-C01-R2 · Step 35 for the course · choice · due Tue 10

| Option | If you pick it |
|---|---|
| **A. DESIGNED, pre-registered, NOT RUN (recommended)** | You do not sign Step 35 (saves about 3 h each). The runner refuses every Step 35 run (tested). The talk carries one limitation slide. |
| B. Sign and run descriptive explicit rungs (35a-lite, 35b PRESENCE, 35c R0/R2, 35d, 35e) | Both sign the v2 package (about 3 h each per `reports/step35/35_0_v2_signature_sheet.md`). The chemistry-reviewer condition S-1 and the 204 deprecated-edge condition S-2 are still open. |

**Why A.** R-FEAS (consensus 6.2 #3). REV-B D.4 puts the Step 35 rungs on the CUT list: the plan card defaults learned rungs to DEFER, and Step 35 is a chemistry ladder, not a lot-state encoder.

```
Step 35 for the course: DESIGNED, pre-registered, NOT RUN (option A). The v2 package stays UNSIGNED; no Step 35 run is authorised before 26 Nov. The talk carries one limitation slide ("learned rungs deferred; entry rule LR-1..LR-5"). Source: R-FEAS, REV-B D.4.
```

#### #4 · T8-C06-R2 · Embedding for rungs B1 and B2 · choice · due Tue 10

| Option | If you pick it |
|---|---|
| A. bge | Matches the draft wording, but the draft names no size or revision. The repo's own study ranks bge-small below e5-large-v2. |
| **B. e5-large-v2 (recommended)** | One model named in the signed prereg, with its revision and the query/passage prefix convention. |

**Why B.** `reports/del4/retrieval_silver_v2_analysis.md`: e5-large-v2 was best of 6 (MRR@10 0.700 alone); RRF of BM25 and e5-large gave 0.762 against 0.704 for bge-small, a gain of +0.057 [+0.035, +0.082]. That study decided "e5-large-v2 replaces bge-small". **Limits:** the queries were templated, silver, dev only, over EVD text. B1 and B2 on the S blocks retrieve recipe steps, which that study did not measure. Whatever you pick is fixed at signing. No switching after.

```
B1/B2 dense embedding: e5-large-v2 (option B), named in the signed D5 prereg with model revision and prefix convention; no change after signing. Evidence: reports/del4/retrieval_silver_v2_analysis.md (silver, dev only; not measured on recipe-step chunks).
```

#### #5 · T8-C12-R1 · H3/B7 wording · choice · due Tue 10

| Option | If you pick it |
|---|---|
| **A. "Rule-based evidence-sufficiency abstention (uncalibrated)", no calibration claim (recommended)** | Wording goes into the prereg and the deck. No calibration claim is made anywhere. |
| B. Keep the current wording and add a calibration study | Not feasible before 25 Nov. The word "calibrated" would stay unearned. |

**Why A.** R-FEAS (consensus 6.2 #5). B7 is a hard rule over an evidence lookup, not a calibrated score.

```
H3/B7 is described everywhere (prereg, report, deck) as "rule-based evidence-sufficiency abstention (uncalibrated)". No calibration claim. A calibration study is not feasible before 25 Nov. Source: consensus 6.2 #5, R-FEAS.
```

#### #6 · T9-C12-R1 and T8-C04-R2 · Power note and circularity caveat in the D5 prereg · choice · due Tue 10

| Option | If you pick it |
|---|---|
| **A. Add both before signing (recommended)** | Prereg says at n = 30 a null result is uninformative and that S gold is engine output. A null then reads as "cannot show", not "no effect". |
| B. Sign without them | A null result reads as "H1 untested". Adding them later voids the signature. |

**Why A.** Consensus 6.2 #6. REV-B Q26 (exact McNemar): the smallest result that reaches p at or below 0.05 at n = 30 is 8-0, 9-1, 10-2 and so on, a gap of 0.23 to 0.27. At n = 30, true gap 0.20 gives power 0.40. Only gaps of about 0.25 or more can show.

```
D5 prereg gets, before signature: (1) a power/MDE note for H1 and H3 (exact McNemar; at n=30 only accuracy gaps of about 0.25 or more can reach significance; a null result is uninformative); (2) an H1 circularity caveat (S gold is engine output, reviewed by its authors). Source: consensus 6.2 #6, REV-B Q26.
```

(A1 below goes further than #6. Take them together.)

#### A1 · REV-B G-05, G-06, G-07, G-12, G-13 · D5 prereg design fixes · choice · due Tue 10

REV-B found that three of the five evaluation instruments cannot show what they claim:

- **H1 on S1 is circular.** The S1 gold ("ingredients heated so far") comes from `d5_state.heated_ingredient_ids`. B4's context prints "Heated so far:" from the same function on the same graph. B4 is handed the gold. Also, B1/B2/B4 retrieve from all steps, including steps after the cut.
- **H3 is close to tautological.** B7 is built by `enforce()`, which deletes sentences that `check_claims` flags. H3 then scores unsupported-claim rate with the same `check_claims`. UCR(B7) is zero by construction (already 0.0 in both smoke ladders).
- **P3 abstention is guaranteed** for B7 and B5T, because gold ABSTAIN means "the ledger is silent" and the route is also a ledger lookup.

| Option | If you pick it |
|---|---|
| **A. Agent applies all eight fixes before the lock (recommended)** | Agent about 3 to 5 h. Your D5 review changes shape: blind-first for S rows. S pool size is the open point, below. |
| B. Add only the caveat (#6) | H1 on S1 then measures engine self-consistency and must be reported as exactly that. H3 "supported" means almost nothing. |

**The eight fixes (A):**

1. **Blind-first S gold.** For every S question you write the answer from the recipe text **before** you see the engine's answer. The sheet hides the `gold_*` columns for S rows. (REV-B Q25; Step 36 G36-B needs `seen_system_output = false`.)
2. B4 is not given the S1 gold field.
3. B1, B2, B4 retrieve only from `steps[:cut]`.
4. One question per recipe. S recipes excluded from any Rung A tuning pool.
5. H3 decision test becomes an **exact sign test** on questions where B2 has an unsupported claim and B7 has none (needs at least 5 such questions; p = 0.5^5 = 0.031). The bootstrap becomes a descriptive interval. B5T is compared too.
6. "Supported" needs the cited row to match the question's ingredient, process and target, not only the number within 0.03.
7. The X block gets 3 safety items with gold REFUSE.
8. A manual audit of 30 random claims, blind to rung (in section 4).

**S pool size (decide here):**

| Option | Power (REV-B Q26) | Cost to you |
|---|---|---|
| A. Keep 30 S questions (15 + 15) | 0.71 at true gap 0.30. 0.40 at 0.20. Needs gap of 0.28 to 0.33 for 80 % power. | 6.3 h each (plan above) |
| **B. Enlarge to 60 (30 + 30) (REV-B)** | 0.97 at 0.30. 0.80 at gap 0.16 to 0.24. | about +1.5 h each (planning figure) |

Recommend B **if both of you can confirm at least 18 h of free time for 9 to 16 Nov**. Otherwise A, with the MDE stated on the slide.

```
D5 prereg amended before signature (REV-B G-05/06/07/12/13): (1) S gold is blind-first (reviewers answer from the recipe text before seeing engine output); (2) B4 is not given the S1 gold field; (3) B1/B2/B4 retrieve only from steps up to the cut; (4) S pool = [30 | 60] questions, one per recipe; (5) H3 decision test = exact sign test on questions where B2 has an unsupported claim and B7 has none (>= 5 needed), bootstrap descriptive, B5T also compared; (6) "supported" requires the cited row to match the question's ingredient, process and target; (7) the X block includes 3 safety items with gold REFUSE; (8) a 30-claim manual audit blind to rung. The benchmark is labelled MODEL_ASSISTED_GOLD, PILOT, authors-as-reviewers. Source: REV-B Q25/Q26/G-05..G-13.
```

#### #7 · T6-C03-R5 · D2-vs-D3 contrast in the 29-diag prereg · choice · due Tue 10

| Option | If you pick it |
|---|---|
| **A. Add it before signing (recommended)** | One paired contrast (process-mean vs ingredient-mean) on S-3, S-4, S-6, DIAGNOSTIC only. |
| B. Leave it out | Any later contrast is EXPLORATORY_POST_HOC and cut. |

**Why A.** R-FEAS and R-SCI (consensus 6.2 #7). REV-A also asks for two more controls in the same edit: a cap sensitivity (0.95, 0.975, 1.0) because R6 values are rounded to the nearest 5 % and capped, and an imputation-duplicate control because R6 values are "many imputed from similar foods" (a process-only model reproduces copies; DEL-2's "D7a matched D1 to four decimals" may be this). Both are REV-A Q18 and Q19.

```
29-diag prereg gets, before signature: the paired D2-process-mean vs D3-ingredient-mean contrast on S-3/S-4/S-6 (DIAGNOSTIC only); a cap sensitivity (0.95/0.975/1.0); the R6 imputation-duplicate control (duplicate groups kept in one fold); the rung-label fix (T6-C02-R1). Anything added after signature is EXPLORATORY_POST_HOC and cut. Source: consensus 6.2 #7, REV-A Q18/Q19.
```

#### A3 · REV-A V7 and Q16, REV-B F-09 and G-16 · AA prereg: domain gate and RESEARCH_ONLY · choice · due Tue 10

| Option | If you pick it |
|---|---|
| **A. Add four lines before signing (recommended)** | The signed text says where SIMULATE may fire, and that the pilot is RESEARCH_ONLY from the start. |
| B. Sign the draft as is | The domain is only in words at the talk. A SIMULATE number for boiled broccoli from a juice fit becomes possible to claim. |

**The four lines:** (1) domain gate: liquid acidic fruit matrices, a stated pH range, 60 to 100 C, no water contact (leaching stays UNKNOWN). The CAL papers are juices and nectars; the target SVAR is total vitamin C but the model is reduced AA. (2) Analyte-basis check (reduced AA against total vitamin C). (3) Step 27 is pre-announced RESEARCH_ONLY: SIM-VAL has 4 papers (3 if AAK-05 is missing), the plan needs at least 5. (4) The agent does not open SIM-VAL full text before the fit hash is committed; a separate session extracts SIM-VAL rows (REV-B B2.3).

```
AA prereg amended before signature: SIMULATE domain gate (liquid acidic fruit matrices, stated pH range, 60-100 C, no water contact; leaching UNKNOWN); analyte-basis check (reduced AA vs total vitamin C); Step 27 pre-announced RESEARCH_ONLY (SIM-VAL 4 papers, 3 if AAK-05 is missing; minimum 5); SIM-VAL full texts are not opened by the agent before the fit hash is committed. Source: REV-A V7/Q16, REV-B F-09/G-16.
```

#### #20 · T9-C25-R5 · Install authorisation · choice · due Tue 10

| Option | If you pick it |
|---|---|
| **A. Pinned installs, Mac only (recommended)** | Unblocks the 10^4-case property test (T5-C05-R1) and the 29-diag on the Mac. |
| B. Also on manjot | More hosts to log. Not needed for any MUST item. |
| C. No installs | T5-C05-R1 and the hypothesis tests are reported NOT_RUN. |

**Check before you choose:** the repo `CLAUDE.md` says "No new venvs" (Python is `/opt/anaconda3/bin/python`). Option A as the consensus words it says "a Mac venv". So the decision text must say either "install `hypothesis` into the existing env" or "one venv, as a named exception to CLAUDE.md". The agent may not install anything until you write it. DEPLOY also found that `lxml` is missing in `.venv312` and that the demo imports it at module top; its task T-D4 makes the import lazy, so no install is needed for that.

```
Install authorisation: pinned install of hypothesis [and any package the 29-diag run proves it needs, named in the per-step host/package table] into [the existing /opt/anaconda3 env | one Mac venv, as a named exception to the CLAUDE.md "No new venvs" rule], Mac only. No installs on manjot or vinayak. Agents install nothing else without a new entry. If not authorised, T5-C05-R1 and the hypothesis property tests are reported NOT_RUN. Source: T9-C25-R5.
```

#### #23 · T9-C26-R1 · Calendar and machines · HUMAN (fact) · due Tue 10

Confirm section 1.5. Record nothing in DECISIONS. The schedule in section 1 changes if any date is wrong.

---

### Block 3. Due Wed 11 to Fri 13 Nov (take them all at the sitting)

#### #8 · T0-C06-R1 · Freeze the mode-to-§141 crosswalk · HUMAN (freeze) · due Wed 11

| Option | If you pick it |
|---|---|
| **A. Approve as written (recommended)** | DIRECT and INTERPOLATE map to `evidence_supported`, tagged E3_UNVERIFIED and COND_UNAUDITED_07A, with an EVD id. SIMULATE, SCENARIO, QUALITATIVE map to `physically_possible`. UNKNOWN, ASK, ABSTAIN map to `unsupported`. |
| B. Amend | Say what changes. The contract audit (T0-C06-R2) is built on the crosswalk, so every amendment costs agent hours. |

**Why A, with a caveat.** Consensus 6.2 #8. REV-A V5: DIRECT fires on the (ingredient, process) pair alone. In a 1,000-recipe non-BBC sample, 364 of 451 DIRECT (80.7 %) were for foods with about 0 mg vitamin C, and 372 (82.5 %) reached the ingredient through a merged lot. So the crosswalk must say what DIRECT means until A2 lands.

```
Mode-to-§141 crosswalk frozen as written: DIRECT/INTERPOLATE -> evidence_supported (tagged E3_UNVERIFIED + COND_UNAUDITED_07A, with an EVD id); SIMULATE/SCENARIO/QUALITATIVE -> physically_possible; UNKNOWN/ASK/ABSTAIN -> unsupported. Caveat in force until the TARGET_ABSENT and CONTEXT_MISMATCH gates land (A2): DIRECT means "a table row exists for this pair", not "the value applies to this food in this context". Source: consensus 6.2 #8, REV-A V5/N5.
```

#### #9 · T5-C07-R1 · Formula id prefix and schema freeze · HUMAN (freeze) · due Thu 12

| Option | If you pick it |
|---|---|
| **A. FORM- and freeze FORM, PARAM, VAL (recommended)** | Formula records have their own namespace. Must be done before PARAM minting on Mon 16 Nov. |
| B. MODEL- | Formula records share the MODEL namespace with the ML model cards (`ledgers/schemas/MODEL`) and each FORM must carry `model_discriminator = FORMULA_MODEL` to stay apart from them. |

**Why A.** Neither review addresses this one. The agent's reasoning is from the code: `src/culinarystate/mechanism/form_param_val.py` says the prefix is "not decided", the schemas accept both, and every function takes a required `form_id_prefix` with no default. So either choice costs little code. FORM- avoids a namespace clash with the ML model cards and needs no discriminator. The draft schemas are `registry/schemas/{FORM,PARAM,VAL}.draft_v1.schema.json`.

```
Formula ids use the prefix FORM- (not MODEL-); the FORM, PARAM and VAL schemas are frozen. Decided before PARAM minting on 16 Nov. Reason: keeps formula records out of the ML model-card namespace. Source: consensus 6.2 #9; form_param_val.py header.
```

#### #10 · T5-C13-R3 · Accept descriptive pilot validation (D-076) · HUMAN (loosens a gate) · due Thu 12

| Option | If you pick it |
|---|---|
| **A. Accept, record the deviation, label never moves (recommended)** | One SIMULATE pilot may appear in the talk, as RESEARCH_ONLY. `sim_aa_1` stays NOT_VALIDATED. VAL-5 stays NOT_MET. |
| B. No SIMULATE result in the talk | The AA verification (3 h each) still feeds PARAM rows, but nothing is shown. |

**Why A.** R-SCI: "the label never moves". REV-B F-09: SIM-VAL has 4 papers, the plan's own G15-f needs at least 5, so Step 27 is RESEARCH_ONLY anyway. REV-A Q16: one calibrated system shows the SIMULATE **pathway**, not that SIMULATE works for recipes.

```
The talk accepts descriptive pilot validation (D-076) in place of the plan's formal Step 27 gate. Recorded deviation. sim_aa_1 stays NOT_VALIDATED / RESEARCH_ONLY; VAL-5 NOT_MET; SIM-VAL has 4 papers (3 if AAK-05 is missing) against a plan minimum of 5. Domain: acidic fruit liquids only; leaching UNKNOWN. The label never moves. Source: consensus 6.2 #10, R-SCI, REV-B F-09, REV-A Q16. Committed by Kush or Parv from their own session.
```

#### #11 · T3-C17-R1 · D3 claim at the talk · choice · due Thu 12

| Option | If you pick it |
|---|---|
| A. Diagnostic on P1 (7 recipes) plus P1b if signed, with intervals | Needs Kush's P1b nonce (section 4.6) and 6 to 12 more human hours. REV-B says cut P1b. |
| **B. No D3 accuracy claim. "Built and run" only, plus one engineering line on P1 (recommended)** | No extra hours. |

**Why B.** REV-B Q28: every P1 label is an AI draft that a human accepted, not blind (`label_basis` is `HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND`; handbook verdict `HANDBOOK_REVISION_REQUIRED`). Agreement with it measures shared bias. A real claim needs at least 30 blind recipes and at least 2 annotators. The consensus lean is "(a) with explicit n, or (b) if P1b is not signed". With P1b off the table, that is B.

```
D3 at the talk: built and run (612,782 recipes; 14,594,812 engine events). The only comparison is the P1 pilot (7 recipes; human-accepted AI drafts, not blind; handbook verdict HANDBOOK_REVISION_REQUIRED), reported as an engineering score with n stated. No accuracy claim. P1b not run. Source: REV-B Q28, consensus 6.2 #11.
```

#### #12 · T5-C05-R4 · Q20, Q22, Q23 rules · choice · due Thu 12

| Question | Recommended rule | Source |
|---|---|---|
| Q20: is "mostly UNKNOWN" a result? | **Yes**, shown as a funnel with reason codes, not one percentage, and only with the target-presence and context gates (A2). Check on a labelled sample that the UNKNOWNs were right. | consensus lean; REV-B Q20; REV-A N5 |
| Q22: what counts as bracketing? | Taxonomy donors (not embedding distance). Output the donor interval, never a point. At least 2 donors independent under 08a lineage (USDA is one cluster, Bognar one). A cold-food coverage table decides each group; coverage under the plan's 0.85 floor means QUALITATIVE. | REV-B Q22 |
| Q23: ASK rule | Ask only if some admissible value of the missing input flips the route or the sign. Call it "flip-sensitivity", not value of information. Report ASK precision on the 5 X items, descriptively. | REV-B Q23 |

If you answer "no" to Q20, the router slide has to show DIRECT 0.754 % without the funnel, and REV-B expects a reviewer to ask for the false-activation rate. There is none.

```
Q20: yes, "mostly UNKNOWN" is a reported result, shown as a funnel with reason codes and with the target-presence and context gates; no single coverage percentage is presented. Q22: INTERPOLATE uses taxonomy donors, returns the donor interval, needs >= 2 donors independent under 08a lineage, else it is not emitted as INTERPOLATE; a cold-food coverage table decides each group (coverage below 0.85 -> QUALITATIVE). Q23: ASK fires only if some admissible value of the missing input changes the route or the direction's sign (flip-sensitivity); ASK quality is not claimed. Source: REV-B Q20/Q22/Q23.
```

#### #13 · T3-C07-R3 · Food.com lines with no units · choice · due Thu 12

| Option | If you pick it |
|---|---|
| **A. Presence-only composition (recommended)** | Mass-based ratios (salt per water, sugar per water, pH bound) are UNKNOWN for Food.com. |
| B. Find the original data with units | A new download under the H2 licence gate. REV-A: scraping food.com is a new acquisition with unclear terms. |
| C. Flagged imputation | REV-A: do not. Teaspoon against cup is a factor of 48, and a learned unit model silently becomes a composition source. |

**Why A.** REV-A Q8 (agree) and REV-B Q30 and Q34. Also, 29.8 % of corpus ingredient lines (1,275,782 of 4,281,956, almost all Food.com) carry a Unicode fraction slash that the legacy parser misreads (SP-002); the fix is after the talk.

```
Food.com ingredient lines without units: composition is presence-only (option A); no unit imputation; mass-based ratios (salt per water, pH bound) are UNKNOWN for Food.com. No new acquisition. Source: REV-A Q8, REV-B Q30/Q34.
```

#### #14 · T3-C04-R3 · SR Legacy as portion and composition authority · HUMAN (basis code) · due Thu 12

| Option | If you pick it |
|---|---|
| **A. Yes, new basis code SR_PORTION, intervals only, not used before 26 Nov (recommended)** | The rule is recorded now. rc2's strict HUMAN_VERIFIED rule stays unchanged for every 25 Nov output. |
| B. Keep the strict rc2 rule | A later lot-state task needs a new decision first. |

**Why A.** REV-A Q9 agrees, "via a decision record" (rc2 is a frozen rule, so do not relax it silently), with grams as intervals spanning the plausible portion records and the AI link kept `AI_MATCHED` until verified. Consensus: moot if #1 = defer. REV-A side finding: the crosswalk's top candidate for the ING "milk" is "Milk, human, mature, fluid".

```
SR Legacy portion weights may be used under the new basis code SR_PORTION, as intervals only, with AI-matched links labelled AI_MATCHED until human-verified. The rc2 rule is unchanged for every output before 26 Nov; nothing uses SR_PORTION while Q39 is deferred. Source: REV-A Q9, consensus 6.2 #14. Committed by Kush or Parv.
```

#### #15 · T4-C09-R1 · Two-zone surface model · choice · due Thu 12 (take with A2)

| Option | If you pick it |
|---|---|
| A. QUALITATIVE two-zone model (surface near 100 C until dry) | Agent 8 to 14 h. Not needed for the talk. |
| **B. Stated limitation for 25 Nov (recommended), plus the A2 cap fix** | The full crust model is future work. |

**Why B plus A2.** Consensus lean is B. But REV-A Q3 says the evaporative cap is "a correctness fix, not only a browning add-on" and wants it now (see A2). B alone would leave wrong numbers in the committed outputs.

```
Two-zone surface/crust model: stated limitation for 25 Nov (option B). Separately (A2): Layer 2 caps moist zones at the evaporation temperature. Source: consensus 6.2 #15, REV-A Q3.
```

#### A2 · REV-A V2, V5, N2, N5 · Physics cap and the two DIRECT gates · HUMAN (route enum is an H4 change) · due Thu 12

| Option | If you pick it |
|---|---|
| **A. Yes to both (recommended)** | Agent code, registry and wording only; no new data. Old and new numbers are shown side by side. |
| B. No | The deck must show no DRY or FAT core temperature or dose, and the router slide must carry the caveat. |

**What REV-A found (reviewer-reproduced, not yet fixed in the tree):**

- **Evaporation bug.** Layer 2 uses the oven, oil or pan temperature as the boundary for every medium, with no evaporation term. Moist pieces reach 163.7 C (diced, bake, 30 min, TYPICAL), 163.4 C (diced, deep-fry, 5 min), 170 C (sliced, saute, 8 min) and 220 C (roast, INTENSE). Capping the boundary at 100 C gives 91.9 C (bake) and 94.0 C (deep-fry), and cook values of 6.3 instead of 601.9 and 1.2 instead of 101.7. Every DRY or FAT driver with a size class is affected.
- **Headline rewording (V1).** "810,951 heat events (46 %) get drivers" is true for a bath temperature and duration. Only **69,995** (4.0 % of 1,746,405) get a core trajectory. Of the computed scenarios, 67.7 % of bath temperatures are defaults and 60.5 % of durations are corpus quantiles.
- **DIRECT is not applicability.** See #8. Fix: a target-presence gate (TARGET_ABSENT when the reference content is about 0) and a context gate (CONTEXT_MISMATCH). Re-run the vitamin-C census and print both counts. The old figure stays on record (R-20).

```
(1) Layer-2 heating boundary is capped at the evaporation temperature (100 C at 1 atm) while a moist zone remains; the DRY/FAT core fields in reports/step26/scenario_L2_* are marked SUPERSEDED (kept on file, R-20). (2) Route values TARGET_ABSENT and CONTEXT_MISMATCH are added (H4 enum change); the vitamin-C router census is re-run and the old and new DIRECT counts are reported side by side. Source: REV-A V2/V5/N2/N5.
```

#### #16 · T4-C22-R1 · How Layer 1 and 2 enter Step 31 · choice · due Thu 12

| Option | If you pick it |
|---|---|
| **A. EVD-row arm only, as planned (recommended)** | Layer 2 never enters a claim-bearing model. |
| B. Add a recipe-event arm with Layer 2 masked | Needs masks and a permuted-registry control. Step 31 is after 25 Nov anyway. |

**Why A.** REV-A Q1 disagrees with the packet's option (b) as a default. On USDA R6 and Bognar rows (no stated T or t), Layer 2 values are a deterministic function of (process, cut class, registry): a hand-written embedding of the process label. A gain would come from the registry's ordering. Allow Layer 2 only later, as a pre-registered ablation that must beat a permuted-registry control.

```
Step 31: EVD-row arm only; no recipe-event arm with Layer 2 features. Layer 2 may enter later only as a pre-registered ablation with a permuted-registry control and an equal-capacity comparator. Step 31 is after 25 Nov. Source: REV-A Q1, consensus 6.2 #16.
```

#### #17 · T8-C02-R2 · SEMANTIC branch · choice · due Thu 12

| Option | If you pick it |
|---|---|
| **A. Explicit abstention, said in the demo and the report (recommended)** | Honest and already built. |
| B. Build it | No time. |

```
SEMANTIC branch: explicit abstention for 25 Nov, stated in the demo and report (option A). Source: consensus 6.2 #17.
```

#### #18 · T9-C07-R4 · Sign the H8 scope-cut register · SIGN · due Thu 12 (sign Wed 11)

| Option | If you pick it |
|---|---|
| **A. Sign (recommended)** | The report can say each cut was decided, with a report line and evidence path. |
| B. Sign with edits | Say which. |
| C. Do not sign | Unannounced descoping reads as failure (consensus). |

**What it lists:** D2, the full H2 test, H4, Steps 20, 28, 33, 34, FlavorTwin. The ledger acceptance row also lists the D3 gold of 40 recipes, the 8-scenario demo and SSOT Levels 10 to 11 as proposal promises. Ask the agent to include them with a status (delivered, diagnostic, declared-not-run). Kush is away Thu 12, so sign on Wed 11.

```
H8 scope-cut register signed: D2, the full H2 test, H4, Steps 20/28/33/34 and FlavorTwin are dropped or deferred before the talk; the D3 gold of 40 recipes and the 8-scenario demo are reported as "not delivered at this scale". Each cut has a report wording and a repo evidence path in [table file]. Source: consensus 6.2 #18, T9-C07-R4. Committed by Kush (and Parv) from their own session.
```

#### #19 · T9-C07-R2 · Prof. Bagler's permission, in writing · HUMAN (fact only a person knows) · due Thu 12

| Option | If you pick it |
|---|---|
| **A. Ask in writing now, store a copy (recommended)** | The report can show the permission. |
| B. Keep "as stated by Kush" (D-045 W3) | The report asserts a permission nobody can show (consensus calls this an integrity risk). |

**Why A.** One 15-minute email covers five things (REV-B G-02, D.5; DEPLOY H-3): the AI-first workflow (D-045), the AI-persona delegation (D-071), Food.com use (uploader-declared CC0, unverified), course use of the BBC Good Food data (D-003), and what we may show from Phenol-Explorer (redistribution is not cleared in writing). A draft is in section 4.8. Send it Monday 9 Nov. Kush sends it. The agent does not. **Store the reply privately** (it is a person's email): keep the file outside git and commit only its sha256, date and a one-line statement. Until a reply exists, the report says "as stated by Kush; no written copy".

```
Permission: Kush emailed Prof. Bagler on [date] covering the D-045 AI-first workflow, the D-071 AI-persona delegation, Food.com use, BBC course use and Phenol-Explorer redistribution. Reply: [received on <date>, stored privately, sha256 <hash> | not yet received]. Until a reply exists the report states "permission as stated by Kush; no written copy" (D-045 W3). Source: consensus 6.2 #19, REV-B G-02. Committed by Kush.
```

#### #21 · T9-C25-R3 · VPN to vinayak · choice · due Fri 13

| Option | If you pick it |
|---|---|
| **A. Kush runs the ssh test on Tue 10; if it fails, accept the manjot-CPU fallback in writing that day (recommended)** | A fail on Tue costs nothing: the fallback is already written (C07). |
| B. Wait until 13 Nov | If vinayak is down on 17 Nov the fallback starts late. |

**Fallback text (C07):** if vinayak is unreachable by Tue 17 Nov, the rungs that need no LLM run on manjot CPU and the LLM rungs are NOT_RUN. The consensus names "B0/B1/B2/B4/B5T"; B0 is "LLM only" in the prereg, so the agent will confirm which of them truly run without an LLM.

```
VPN to vinayak: ssh test on [date] [worked | failed]. If failed: the manjot-CPU fallback applies from now (rungs that need no LLM run on manjot; LLM rungs NOT_RUN, C07). Source: consensus 6.2 #21.
```

#### #22 · T0-C01-R1 (Q40) · Apply the SSOT v16 change set before the talk? · HUMAN (Kush's own line) · due Thu 12

| Option | If you pick it |
|---|---|
| **A. Do not apply. v15 governs through 26 Nov (recommended)** | Every prereg cites v15. A one-page "SSOT v15 vs current state" delta goes in the report. |
| B. Apply v16 | Moves the authority under live preregs. Every one needs a re-sign. |

**Why A.** REV-B Q40.

```
SSOT v15 governs through 26 Nov; the v16 change set is not applied before the talk. A one-page "SSOT v15 vs current state" delta goes in the report. Source: REV-B Q40, consensus 6.2 #22. Committed by Kush.
```

---

### Block 4. Review add-ons (not in the consensus list)

#### A4 · REV-B G-03 · Governance repairs and the AI-persona line · SIGN · REV-B asks for Mon 9

REV-B B2.2 found that no D-071 decision (D-072 to D-074) closed a human gate, but two earlier records need written repair and D-071's second half is unratified.

| Part | What | Who | Time |
|---|---|---|---|
| (1) The line | AI personas may tighten, defer, withdraw or refuse. They may not loosen, close or sign. Independent-labelling gates are human-only. Agreement between ksh and prv is not inter-rater evidence. | Kush enters it (T0-C18-R2, SHOULD) | 0.3 h at the sitting |
| (2) Parv's own ratification | D-071 says "prv is Parv" and Parv's consent is not on record. D-046 and D-070 record Parv's OK as relayed by Kush. Parv writes, in Parv's own words, whether Parv ratifies them. | Parv, own hand | 0.5 h |
| (3) D-068 | The agent appended the 15.0 ruling on a verbal waiver. Kush ratifies it in his own commit before 15b relies on it. | Kush, own hand | 0.3 h |
| (4) Wording | A file an AI wrote and no human signed is a "dated AI draft", not "pre-registered" (D-074 used the loose word). | Both | 0 |

| Option | If you pick it |
|---|---|
| **A. All four (recommended)** | The report's method section states what was AI-delegated and what was human-signed (T9-C07-R3 can be generated from DECISIONS). |
| B. Skip | Ship with "relays unratified" disclosed (REV-B D.3). |

Parv must write part (2) in Parv's own words. The agent drafts nothing for it. Suggested place: a dated first-person section in `handoff/PARV_SESSION_NOTES.md` (proposed), in Parv's own commit.

```
D-071 addendum (adds a limit; does not remove delegation): AI personas (ksh, prv) may tighten, defer, withdraw or refuse. They may not loosen, close or sign. Human-only: signatures, freeze approvals, seals, nonces, amendments to signed records and to rulings, independent-labelling gates (07.A labels, 07I-C, G08-H, G21.6, G23 case labels, Step 10/11 row verification, Step 19 annotation, D5 review) and facts only a person knows. Agreement between ksh and prv is not inter-rater evidence. A file written by an AI and not signed by a human is called a "dated AI draft". Source: REV-B B2.1/B2.3/G-03. Committed by Kush.
```

#### A5 · REV-B G-20, Q25 and T9-C17-R3; REV-A C-sci 11 · Name an outside reviewer · HUMAN (fact) · due Wed 11

Kush asks one person (a TA, a senior student, a food-science acquaintance). They review 20 D5 items: all P3, 5 S1, 5 S2, 5 P1 (about 1 h). If they will also read REV-A's physics notes N1 to N4 and the mechanisms that fire in the demo, better. REV-A: "the physics corrections, 20 to 30 mechanism windows, 20 to 30 benchmark answers".

| Option | If you pick it |
|---|---|
| **A. Ask now (recommended)** | The slide can say "outside check on 20 items". |
| B. No one | The report says "author-only review" as a limitation (T9-C17-R3). |

```
Outside reviewer: [name or role] will review 20 D5 items (all P3, 5 S1, 5 S2, 5 P1) by [date]. | No outside reviewer found; the report states "author-only review". Source: REV-B G-20, T9-C17-R3.
```

#### A6 · T8-C18-R1, DEPLOY H-1 and H-2 · Demo hosting, what may leave the Mac, LLM path · choice (Kush) · due Tue 10

The DEPLOY lane (`handoff/DEPLOYMENT_AND_PRESENTATION_PLAN_2026-11-08.md`, AI_DRAFTED, proposed) did the hosting research. This pack uses its default. I did not re-check its pricing and limits (it marks them UNVERIFIED and dated 8 Nov).

| Option | If you pick it |
|---|---|
| **A. Local live demo on Kush's Mac, template-only (B5T, no LLM, no key). A static cached page (about 20 precomputed answers) on a free static host or inside the report archive. Optional Cloudflare quick tunnel only during the talk window (recommended, DEPLOY default)** | No paid account, no key, no VPN. Your time: H-4 machine check (5 min, Fri 13), demo dry run (20 min, Sat 14 or Sun 15), optional H-5 static place (15 min, by Sat 21), optional H-6 `cloudflared` install (5 min, Fri 20), H-8 screen recording (20 min, Mon 23). Offline fallback: single-file `demo_offline.html`, recording, backup slides. |
| B. A live hosted demo | DEPLOY says Hugging Face Docker and Gradio Spaces now need a paid plan (only Static Spaces are free) and free Render is too small (1.2 GB RAM and about 60 CPU-seconds to load). Needs a payment method and a budget cap (H-9). |
| C. Add an LLM paraphrase layer with an API key | The key lives in an environment variable on the Mac, never in the tree, with a spend cap. DEPLOY and the silver ladder show no LLM variant beat B5T, so this adds risk without a measured gain. |

**Licence calls that go with A (DEPLOY H-2, 10 min; recommended: accept).** Nothing that leaves the Mac contains: Phenol-Explorer rows, SU-EATABLE carbon data, the OFF taxonomy, third-party recipe text. Bare BBC-derived aggregates (counts and scores, no ids) are accepted for the **local** demo only. **No BBC-derived example on any slide or on the static page.** DEPLOY found one in the demo today (the "Swap buttermilk" button, an edge supported only by BBC recipes). It is removed before the static page is built. Also (REV-B G-13 and G-14): the demo holds no key in the tree, logs no user input without notice, and refuses food-safety questions. **The refusal rule does not exist yet** (DEPLOY T-D7, agent task, due Fri 13).

```
Demo plan: local live demo on Kush's Mac, template-only (B5T, no LLM, no API key); a static cached page of about 20 precomputed answers on a free static host or in the report archive; an optional Cloudflare quick tunnel during the talk window only (option A). Licence calls: nothing leaving the Mac contains Phenol-Explorer rows, SU-EATABLE carbon data, the OFF taxonomy or third-party recipe text; bare BBC-derived aggregates only in the local demo; no BBC-derived example on slides or the static page. The demo holds no key in the tree, logs no user input without notice, and refuses food-safety questions. Source: T8-C18-R1, DEPLOY H-1/H-2, REV-B G-13/G-14. Committed by Kush.
```

#### A7 · T9-C26-R2 · Adopt the fallback levels · choice · due Tue 10

Adopt section 5 (L0 to L3, slip triggers and wording) as the plan of record. **Note:** the consensus names the four levels but gives no trigger for L1. The L1 trigger in section 5 is this pack's proposal.

```
Fallback levels L0-L3, the slip triggers and their wording (handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md section 5) are adopted as the plan of record. Source: T9-C26-R2.
```

### 2.4 Not this week: the agent's default holds

These SHOULD or COULD decisions (consensus 6.4) are not on the sitting. If you say nothing, the agent's default in its report holds: T0-C17-R1 professor endpoint terms; T0-C18-R2 (handled in A4); T2-C02-R1 storage form for AA rows; T2-C03-R1 SVAR v1.1 set; T2-C04-R1 07.B/07.C axes; T2-C11-R2 R2 and Bognar ingestion order; T2-C18-R1 H2-queue licence rulings; T3-C16-R1 P1b size and nonce (section 4.6); T3-C25-R1 belief-field design note; T4-C05-R3 Layer 2 circularity control; T5-C01-R4 MECH schema decisions; T5-C02-R4 Q21 QUALITATIVE from unreviewed MECH; T5-C11-R1 G26 numbers prereg; T6-C04-R1 H2 operational test; T7-C01-R3, T7-C04-R1, T7-C16-R1 open Step 35 items; T7-C08-R1 sensory UNSUPPORTED wording; T7-C20-R1 "learned rungs deferred" statement; T7-C24-R1 park L13E; T8-C07-R1 conflicting-evidence display; T8-C08-R1 B6 SIMULATE rung; T9-C06-R2 claim ledger; T9-C07-R1 H3 compute threshold; T9-C07-R5 repo visibility.

REV-A also asks for decisions that are moot while #1 is "defer": a REFERENCE class beside Layer 1 and 2 for SR and FDA values (REV-A P1), the weakest-link provenance rule, and the SVAR v1.1 list in REV-A section E.6. **Default: parked, DRAFT, after 26 Nov.** One rule applies even if parked: **no SR or FDA value is ever labelled Layer 2.** On Q21 (QUALITATIVE direction from unreviewed mechanisms) REV-B says demo only, as `physically_possible` with an `AI_DRAFTED_MECH_UNREVIEWED` flag, never in H1, H3 or any slide number.

---

## 3. Signature checklist

### 3.1 Rules for every signature

1. **Wait for the lock note.** The agent edits the four prereg texts, then posts one lock record with: the sha256 of each file, the issued packet and sheet hashes, and the lock time. Target: Tue 10 Nov afternoon. Proposed path `reports/orchestration/PREREG_LOCK_2026-11-10.json` (the agent confirms the real path in its note). **Do not sign the 8 Nov drafts.** They will change.
2. **Hash it yourself.** Before you sign, hash the file and compare with the lock record. If the numbers differ, stop and tell the agent.
3. **Do not type your name into the `.md` file.** That changes its hash and voids the signature. The "Signatures" block at the end of each draft (`Kush Tokas: ______`) will be replaced in the lock by a pointer to the signature files (REV-B F-07).
4. **Own hand.** Type your own JSON and commit it from your own session (D-049 F5). Write the day you actually sign. Never before the lock time. Never typed by the other person.
5. **Signed commits (REV-B G-04, recommended).** If your git signing key is set up, use `git commit -S`. The agent will run `git log --format=%G? -1 <file>`. If your commit is unsigned, the hash-bound file still counts and the report says so.
6. **Names are exact:** `Kush Tokas` and `Parv Goyal`. The checker refuses anything else, including `ksh`, `prv`, `(Kush)` or `(Parv)`.
7. **File names for 07A_R1, D5 and AA are PROPOSED.** Only the 29-diag and freeze checkers exist today (`src/culinarystate/evaluation/freeze_records.py`). The agent wires the same check for the other three (about 2 agent hours, REV-B G-04) on 9 to 10 Nov and gives the final names in the lock note. The lock note wins.
8. **A file keeps its `_DRAFT` name after signing.** The signature file is what makes it signed (the 29-diag precedent).

### 3.2 What the locked text will contain

| File | Edits already agreed (consensus) | Edits that need your yes at the sitting (REV-A, REV-B) |
|---|---|---|
| `reports/step07/07A_R1_preregistration_DRAFT.md` | The #2 ruling text. Optional planted-error design (C06; only allowed inside the lock). Signature block replaced by a pointer. | B2 contents: AC1 at 0.95, accuracy co-gate, 10 planted rows, critical set, USDA floor, new provenance rule. Packet re-issued (new hashes). |
| `reports/del5/d5_benchmark_preregistration_DRAFT.md` | H3/B7 reword (#5). Power note and circularity caveat (#6). One embedding named (#4). VPN-fallback sentence (C07). | A1 eight fixes. S pool size. U and X blocks drafted (none exist yet). X safety items. |
| `reports/step10/aa_pilot_preregistration_DRAFT.md` | Wording only (consensus lock list). | A3 four lines. Licence status per paper (see 4.3). |
| `reports/step29/29diag_preregistration_DRAFT.md` | D2-vs-D3 contrast (#7). Rung-label fix T6-C02-R1 (the draft says D2 = B-3 process mean and D3 = B-2 ingredient mean; the crosswalk row says B-2 = D3 matrix arm). | Cap sensitivity. Duplicate control. A note on the freeze record that **approving it does not satisfy Step 15a** while 08a G08-3 is FAILED (REV-B F-08). |

### 3.3 The checklist

| # | File | Exact action | Who | Deadline | Unlocks | Agent check afterwards |
|---|---|---|---|---|---|---|
| S1 | `reports/step10/aa_pilot_preregistration_DRAFT.md` | Create `reports/step10/aa_pilot_prereg_signature_Kush.json` and `..._Parv.json` (3.4). Commit. | Kush and Parv, each | **Tue 10**, after the lock | PDF downloads, CAL extraction (11 to 12), verification (12 to 15), fit freeze (16). | Recompute the sha256; both files present; exact names; ISO dates; time after the lock. Final command in the lock note. |
| S2 | `reports/step07/07A_R1_preregistration_DRAFT.md` | Create `reports/step07/07A_R1_prereg_signature_Kush.json` and `..._Parv.json`. Include `"confirms_no_R1_label_exists": true`. **Sign before you open the packet.** | Kush and Parv, each | **Wed 11 noon** | Opening the 07.A-R1 packet and labelling. A PASS is the valid 07.A, but 23b stays closed (needs 15b). | Same check. Also the packet hash equals the lock record. |
| S3 | `reports/del5/d5_benchmark_preregistration_DRAFT.md` | Create `reports/del5/d5_prereg_signature_Kush.json` and `..._Parv.json`. **Sign before you open the review sheet.** | Kush and Parv, each | **Wed 11 noon** | D5 review, benchmark freeze, rung runs (17 to 19 Nov), H1 and H3. | Same check. |
| S4 | `registry/freezes/15A-BOOT-2026-11-08.json` | Edit three fields only: `"status": "FROZEN"`, `"approved_by": "Kush Tokas"`, `"approved_date": "2026-11-1X"`. Touch nothing else (the hashes bind the nine ledgers and the seal). Do it on the **Mac**. | **Kush only** | **Wed 11** | 29-diag runs. It is a snapshot for the diagnostic only. | `freeze_problems('.', '15A-BOOT-2026-11-08')` must print `[]`. Today it prints `['NOT_APPROVED', 'NO_HUMAN_APPROVAL']` (checked on manjot, 8 Nov). |
| S5 | `reports/step29/29diag_preregistration_DRAFT.md` | Create `reports/step29/29diag_prereg_signature.json` (3.4). Only after S4 and the text fix. | **Kush only** | **Wed 11**. REV-B: drop it if not signed by Thu 12. | Run 29-diag twice on the Mac (11 to 14 Nov), memos 14 Nov, the H2 diagnostic slide 15 Nov. | `prereg_signed('.')` must print `True`. Today `False`. |
| S6 | DECISIONS entry for #2 (07.A gate) | Kush types and commits the entry himself (block in #2). | **Kush only** | **Mon 9 or Tue 10**, before S2 | The R1 prereg may be signed. | Entry exists, cites R-06, R-20 and names the 23b dependency. Dated before any signature file. |
| S7 | H8 scope-cut register (#18) | Kush commits the DECISIONS entry. Parv co-signs if both agree. | Kush (and Parv) | **Wed 11** (due Thu 12) | The report's scope-cut table. | Entry lists each cut with a report wording and evidence path. |
| S8 | A4 repairs | Parv writes own ratification (D-071 second half, D-046, D-070, 07.A and 07I-C statements). Kush ratifies D-068 in his own commit. Kush enters the D-071 addendum. | Each their own | **Mon 9** (REV-B) | The method section can say what was AI-delegated. | Entries exist; authors match. Report section T9-C07-R3 is generated from DECISIONS. |
| S9 | Prof. Bagler permission (#19) | Kush emails, stores the reply privately, commits sha256 and date. | Kush | Email Mon 9; entry Thu 12 | The report can show the permission. | Hash recorded, or the "as stated by Kush" sentence kept. |
| S10 | 07.A-R1 joint adjudication entry (T2-C05-R4) | Both enter it together. The statistic is **never** recomputed after adjudication. | Kush and Parv | 14 to 15 Nov | Closes 07.A-R1. | Entry exists; result JSON untouched. |
| S11 | D5 benchmark freeze confirmation (T8-C20-R3) | After the joint reconcile, each confirms the sha256 the agent posts. The agent has not built the freeze tool yet; it will give the exact command. | Kush and Parv | **Mon 16** (hard stop Tue 17) | Rung runs. No question changes after a rung runs. | Freeze check passes; hash in the run log. |
| S12 | Step 35 v2 package | **Do not sign** if #3 = A. | | | | `authorise_explicit_run('35e', root='.')` refuses (tested). |
| S13 | P1b start-record amendment | **Optional, recommended skip** (4.6). | Kush | only if you choose it | | `python tools/step19_real_pilot.py check --record reports/step19/pilot_start_record.SIGNED.json --wave P1b`. Today it prints 1 blocker: `H5_WAVE_NOT_AUTHORISED`. |

### 3.4 Copy and paste

```bash
# 1. From the repo root on the Mac: hash the file the lock note names
shasum -a 256 reports/step07/07A_R1_preregistration_DRAFT.md      # Linux: sha256sum
# 2. Compare with the lock record. If different, STOP.

# 3. Type your own signature file (this example is Kush, 07.A-R1)
cat > reports/step07/07A_R1_prereg_signature_Kush.json <<'JSON'
{"prereg_sha256": "<paste the 64-character hash>",
 "signed_by": "Kush Tokas",
 "signed_date": "2026-11-11",
 "confirms_no_R1_label_exists": true}
JSON

# 4. Commit from your own session (add -S if your signing key is set up)
git add reports/step07/07A_R1_prereg_signature_Kush.json
git commit -m "sign: 07A_R1 prereg (Kush Tokas)"
```

The 29-diag file has exactly three keys, no others:
`{"prereg_sha256": "<hash>", "signed_by": "Kush Tokas", "signed_date": "YYYY-MM-DD"}`

Check commands that exist today (the agent runs them; you can too):

```bash
PYTHONPATH=src python -c "from culinarystate.evaluation.freeze_records import prereg_signed, freeze_problems; print(prereg_signed('.'), freeze_problems('.', '15A-BOOT-2026-11-08'))"
# expected after S4 and S5:   True []
python tools/step07hr_freeze.py --verify          # Mac only; must say FREEZE INTACT (needs a ledger that is not on manjot)
```

### 3.5 What voids a signature

- Any edit to the signed `.md` file, even a typo. Any change needs a new lock and a new signature.
- Any change to the nine frozen ledgers or the seal commitment after S4 (`SNAPSHOT_HASH_MISMATCH`). The agent must hold orchestrator appends such as SVAR v1.1 rows until after the 29-diag runs (about 14 Nov), or record them as 15a.1.
- Re-issuing the 07.A packet or the D5 sheet after the signature. After signing, any change must be a dated amendment committed before labelling, or the attempt is void (07A prereg header).
- Opening the packet, sheet or verification file before signing (07A, D5, AA).
- A signature typed by someone else, or a relayed one. If one of you is unavailable, record "signed by Kush; Parv pending" (REV-B D.3). The talk then says "pre-registered by one author; second signature pending".

---

## 4. Labelling and verification tasks

### 4.1 Independence rules (all tasks)

| Rule | 07.A-R1 | AA CAL rows | D5 review | Claim audit | SIM-VAL rows |
|---|---|---|---|---|---|
| Sign the prereg first | Yes. Opening first voids the attempt. | Yes. | Yes. | n/a | n/a |
| Work alone, different session from the other | Yes | Yes | Yes | Yes | Yes |
| No external source | Yes. Judge only the raw string shown. | The paper only. | Recipe text and the cited EVD rows only. | The cited rows only. | The paper only. |
| Do not see the other's file or answers | Yes | Yes | Yes | Yes | Yes |
| Do not discuss any item before | both files are back and hashed | both files are back | both sheets are back | both are back | both are back |
| Fill every cell | Blank cell makes the file invalid | Every row gets a verdict | KEEP, EDIT or DROP with a reason for every row | Every sampled claim | Every row |
| Return how | The file as issued, to the Mac agent, not to each other | Same | Same | Same | Same |
| Agent action on receipt | Record the sha256 **before** scoring | Record the sha256 | Record the sha256 | Record the sha256 | Record the sha256 |
| Log your time | Start and end per session | Same | Same | Same | Same |

Keep a one-line time log: date, start, end, items done. The plan wants minutes per item and the ledger hours are unmeasured guesses (REV-B G-18).

**Where you work.** If Parv's laptop is still down, work in a separate clone and a separate OS user or session on the Mac, and say so in the report (the D-064 deviation repeated). The two files must never be in a folder both of you can open during the work.

### 4.2 07.A-R1 packet (3 to 4 h each, due Fri 13 Nov)

**Open:** `annotation/condition_audit/condition_audit_packet_100_R1_Kush.csv` or `..._R1_Parv.csv` (Mac; git-ignored; raw third-party strings). The two files hold identical content. Packet hash today (manifest `reports/step07/07A_R1_packet_manifest.json`): `f086975a2eac8531633299ff4f089da007ecc19c46c77619977ba96b925ca27d`. If the sitting chooses B2, the packet is re-issued and the lock note gives the new hashes.

**What is in it.** 100 conditions, 6 strata (S1 20, S2 25, S3 15, S4 15, S5 10, S6 15), disjoint from v1 to v4, same frozen normaliser (`e7d589136275`), same codes as v4. 9 fields plus an overall judgement per condition (900 field cells plus 100 overall).

**Fields:** duration, temperature value, temperature location, pressure, power, medium, basis, retention type, censoring. **Critical fields today:** temperature location, pressure, basis, retention type, censoring. (B2 adds duration and temperature value.)

**Codes (exactly one per field):**

| Code | Use when |
|---|---|
| CORRECT | The normalised value type and status match what the raw text says. |
| WRONG_TYPE | It should be POINT, INTERVAL, QUALITATIVE or UNKNOWN (say which in the reason column). |
| WRONG_VALUE | The type is right but the number or unit is wrong. |
| WRONG_LOCATION | The temperature is assigned to a place the text does not support, or should be UNSPECIFIED. |
| INFERRED | The output has information that is not in the raw text. Any assumption. |
| SHOULD_BE_AMBIGUOUS | The raw text is genuinely ambiguous and the normaliser should have flagged it. |
| N/A | The field is not in the raw text or the output. |

`overall_judgement` is ACCEPT only if no field is WRONG_* or INFERRED. Otherwise REJECT. Rows such as `POINT/AMBIGUOUS calendar:6.0 month` are **correct** behaviour (calendar durations are deliberately not converted).

**Rules.**
1. Judge only against the raw string shown. No external source. Do not edit the normalised columns.
2. Do not skim. If the sitting adopts B2, 10 rows have planted errors. You must flag at least 8 of 10 or your file is NOT_COUNTED.
3. **Do not copy and do not match on purpose.** Under the scorer as it stands, two files that are identical in all 10 judgement columns are NOT_COUNTED (`IDENTICAL_JUDGEMENTS`). REV-B F-05 calls that rule perverse and B2 replaces it with timestamps and free-text overlap. The lock note states the rule in force.
4. Fill every cell. A blank cell makes the file INVALID_INPUT.
5. Optional (REV-B G-17): about 20 minutes together on **10 separate practice items** (not the 100) before you start, if the agent supplies them by Tue 10. Calibration happens only on those. Never on the packet.
6. v4 needed three file replays (invalid codes such as `INCORRECT`, non-codebook values). If the agent supplies a validator or dropdown sheet, run it before you return the file.

**After you return it.** The agent records each file's sha256, then scores with `python tools/step07ar_agreement.py --kush <returned_Kush.csv> --parv <returned_Parv.csv>`. The result is written once to `reports/step07/07A_R1_gate_result.json` (it refuses to overwrite). Joint adjudication follows (14 to 15 Nov, 0.5 h each). The statistic is never recomputed after adjudication.

### 4.3 AA pilot: the 5 PDFs, then the CAL rows

#### 4.3a The 5 PDFs (Kush, browser on the Mac, about 1.0 h, Tue 10 Nov, right after S1)

These 5 papers refuse scripted download. The agent does not work around the sites.

| Id | DOI | Role | Matrix |
|---|---|---|---|
| AAK-02 | 10.33899/magrj.2017.161257 | SIM-CAL | orange juice |
| AAK-04 | 10.1155/ijfo/2464512 | SIM-CAL | strawberry nectar and surrogate |
| AAK-05 | 10.7455/ijfs.v8i1.571 | **SIM-VAL** | broccoli |
| AAK-08 | 10.9734/bbj/2014/9837 | SIM-CAL | baobab pulp |
| AAK-10 | 10.3390/foods10010046 | SIM-CAL | canned mango and pineapple |

Steps for each: open `https://doi.org/<DOI>` in a browser; read the **licence line on the publisher page** (it must say CC BY or CC0); download the PDF; save it into `data/raw/aa_pilot/` (git-ignored); tell the Mac agent the file name. The agent records the sha256. If a paper is not CC BY or CC0, do not save it. Tell the agent. The paper is dropped and recorded, never stored.

**AAK-05 is SIM-VAL. Save it. Do not read it.** SIM-VAL stays closed until the fit is frozen on Mon 16 Nov.

**More licences to confirm than the ledger says.** In `registry/evidence/aa_kinetics_source_candidates_v1.csv` only AAK-06 and AAK-09 have a licence stated in the PDF. For the others the column reads UNKNOWN. That includes **AAK-01 and AAK-11, which the agent already extracted rows from.** AAK-09's repository copy is labelled CC-BY-NC-ND while the publisher version is CC-BY. While you have the publisher pages open, check AAK-01, AAK-09 and AAK-11 too (about 10 min each). If AAK-01 or AAK-11 is not CC BY or CC0, its rows are dropped and the report says so. The SIM-VAL papers (03, 07, 12) can wait until after the freeze (read the licence badge on the landing page, not the paper).

**If you cannot do it on Tue 10:** do it Wed 11 morning. The agent extracts whichever PDFs are present at noon Wed 11. That grace is this pack's suggestion; the consensus trigger is Tue 10 (fit on the papers already present, the rest dropped and recorded).

#### 4.3b Verify the CAL rows (3 h each, Sat 14 and Sun 15, due Sun 15 Nov)

**Open:** your verification packet from the Mac agent (git-ignored; one row per extracted value, with a verbatim span and locator). Today it holds **16 rows from 4 papers** (AAK-01, 06, 09, 11): 13 `K_AT_T` rows and 3 `AUTHOR_FIT_EA` rows. Rows from the newly downloaded CAL papers are added by 12 Nov. Open the **paper PDF** (`data/raw/aa_pilot/`) next to it.

**For every row, check against the paper, not against the agent's quote:** the quote is really at the locator; analyte basis (AA only, or AA + DHA); matrix; heating medium; temperature and where it was measured; time range; order; k and its unit; dispersion; n; assay; whether the cooking water or syrup was assayed.

**Give one verdict:** `VERIFIED`, `CORRECTED` (write the corrected value and its span) or `REJECTED`.

**What counts.** A row becomes a PARAM row only if **both** of you mark it VERIFIED, or both CORRECT it to the same value. Anything else stays out. Unverified rows never reach SIMULATE. Target: about 20 verified rows, at least 3 temperatures in at least 2 SIM-CAL matrices. Below the minimum, Model A is recorded NEED_DATA and is not fitted on fewer rows.

**Watch for anchoring.** The agent flagged three things: AAK-11's k is nearly temperature-independent (30 to 90 C); AAK-06 used iodine titration, which is not AA-specific; AAK-01 gives k to 1 or 2 significant figures. These are hints, not verdicts. Judge from the paper. The ledger names "AI LIKELY_CONFIRM anchoring" as a risk.

**After you return it.** `python tools/aa_pilot_fit.py --kush <returned_Kush.csv> --parv <returned_Parv.csv>` writes `reports/step10/aa_pilot_model_a_fit_FROZEN.json` once. Its sha256 is the freeze point. Only then are SIM-VAL full texts opened.

### 4.4 D5 benchmark review (about 6.3 h each, Wed 11 to Mon 16 Nov)

**Open:** `annotation/d5_review/d5_review_v1_Kush.csv` or `..._Parv.csv` (Mac; git-ignored because it holds recipe text). Today it has **100 drafted questions**: S1 20, S2 20 (from Wikibooks and Gutenberg only), P1, P2, P3 and C 15 each. The committed drafts are `benchmark/d5/d5_draft_S_v1.csv` (40 rows) and `benchmark/d5/d5_draft_PC_v1.csv` (60 rows). **U (substitution) and X (control) blocks, 5 each, have no drafts yet.** The agent drafts them; you review them (0.5 h).

**Blocks and what each tests:** S1 current state and S2 next action test H1. P1 (DIRECT evidence exists), P2 (only similar-food evidence), P3 (no evidence, gold ABSTAIN) and C (compare two processes) test H3. U and X are descriptive.

**Order of work (REV-B Q25, if A1 is adopted):**

| Phase | What you do | About |
|---|---|---|
| 1. S rows, blind | For each S question, write your own answer from the recipe text. The sheet hides `gold_*` for S rows. Write the answer before you look at anything the engine produced. | 2.0 h (30 S questions) |
| 2. S rows, gold | Open the engine gold. KEEP, EDIT (write the edited question or gold) or DROP, with a reason. Your blind answer and the engine gold are compared later; that comparison is itself a D3 datapoint. | 0.5 h |
| 3. P and C rows | Check each gold against the cited EVD rows: right ingredient, process and target; the retention range matches the cited rows (fractions, USDA % divided by 100); the stratum is right (P1 DIRECT, P2 similar-only, P3 none so gold ABSTAIN); the wording is a fair question. | 2.5 h (60 questions) |
| 4. U and X | Review the new drafts. X should include 3 safety questions with gold REFUSE. | 0.5 h |
| 5. Reconcile (joint) | After both sheets are back. A question enters only if both KEEP, or both KEEP after the same edit. | 0.5 h |

**P and C blocks are over-drafted** (15 per block, ranked by a seeded hash; the first 10 by rank that survive form the block). So drops do not shrink a block and you cannot choose replacements. Do not try to.

**Rules.** Sign first. Alone. Do not discuss until both sheets are back. Do not edit a question after the benchmark is frozen. If you enlarged the S pool (A1 option B), add about 1.5 h.

**Label on every slide:** `MODEL_ASSISTED_GOLD, PILOT, authors-as-reviewers`.

### 4.5 Later tasks

| Task | When | Time each | What you do |
|---|---|---|---|
| SIM-VAL row verification (T5-C10-R6) | Wed 18 | 2.0 h | Same rules as 4.3b, for the 4 SIM-VAL papers, after the Model A fit is frozen. Descriptive only. |
| Blind claim audit (T8-C16-R1) | Thu 19 to Fri 20 | 1.25 h | Sheet of 30 randomly drawn numeric or directional claims across rungs, **blind to rung and to the checker's verdict.** Judge: is the claim supported by the cited row, and is the row relevant (right ingredient, process, target)? REV-B G-08 would take 40 to 60 claims; the consensus MUST is 30. |
| 07.A joint adjudication (T2-C05-R4) | Sun 15 | 0.5 h | Joint session on the disagreements. Record in DECISIONS. Never recompute the statistic. |

### 4.6 P1b nonce (optional; recommended skip)

**What it is.** A small second Step 19 annotation wave (3 or 4 new recipes) to check Addendum B. It needs three things only Kush can supply (`reports/step19/P1b_design_amendment_PROPOSED.md`): the size (3 or 4); a **new nonce, written by Kush before the frame is rebuilt**, with only its sha256 committed (the drawing agent never chooses it; `pilot_real.check_prerequisites` refuses `NONCE_SUPPLIER_NOT_KUSH`); and a signed amendment to the start record covering wave P1b, its budget against THR-19P-14/15 (40 h cap) and the reserve rule. The tool may also ask which P1 cells to use (`--cells`, "chosen by a human").

**Why skip.** REV-B Q28: it buys little (3 to 4 more recipes), costs 6 to 12 more human hours (UNVERIFIED), and the labels are again human-accepted AI drafts. Decision #11 recommends no D3 accuracy claim, so nothing needs it. Consensus makes it SHOULD (nonce) and COULD (annotation).

**If you do it anyway:** Kush types the nonce himself, from his own head or dice, never from an AI. He keeps it private. He commits only `printf '%s' "<nonce>" | shasum -a 256` before the agent rebuilds the frame. Time: 0.5 to 1 h.

### 4.7 Not scheduled this week (and what that costs)

| Task | Hours | If it stays unscheduled |
|---|---|---|
| Verify the 40 MAIN EVD rows against papers (T2-C10-R1, Kush 6 to 12 h, Parv audits a sample) | 9 to 18 | D1's hand-verified literature rows stay at 0 of 40 (if still 0 on the day). Say so (section 6). |
| Random transcription audit of 50 to 100 of the 17,978 EVD rows (REV-A Q17) | about 1 | **Cheap and worth it if there is slack.** It turns "unverified" into a measured error rate with a Wilson interval. |
| 200 to 300 Food.com lines labelled for the NER sample (T3-C09-R4, REV-B Q33) | 3 to 5 | NER accuracy on Food.com stays unmeasured. Say so. |
| Parv's audit of the 50 ING to FlavorGraph crosswalks (T7-C05-R2) | 2 | Step 35 is not run anyway (#3). |
| Blind dual review of the 32 MECH entries (T5-C01-R3) | 12 to 20 | All 32 stay AI-drafted and unreviewed. Never in a claim. |

### 4.8 Draft email for decision #19 (Kush edits and sends; AI_DRAFTED, the agent sends nothing)

> **To:** bagler@iiitd.ac.in  **Cc:** Parv Goyal
> **Subject:** CGAS Group 17: written confirmation of our AI-assisted workflow and three data-use questions
>
> Dear Prof. Bagler,
>
> For our CulinaryState project we work in this order: an AI agent drafts every label, extraction and gate verdict first; Kush and Parv then review it and decide; every result is labelled model-assisted. Two AI "persona" workers may also decide engineering choices, but never signatures, nonces or independent labels. We understood from [Kush: when and how the permission was given] that this is acceptable. Could you confirm it by email so we can cite it in the report?
>
> Three data questions. (1) We use the Food.com recipe dump from Kaggle (the uploader declares CC0, which we cannot verify) for analysis and internal diagnostics only. May we report results from it in the report and slides? (2) We hold the BBC Good Food dataset on one machine only and publish only counts, never recipe text. May we report such counts? (3) Our evidence ledger includes Phenol-Explorer 3.6 values. We have not cleared their redistribution terms in writing. We will show no Phenol-Explorer rows outside our own machines. Is it acceptable to show derived aggregates in slides?
>
> Thank you,
> Kush Tokas (2023296) and Parv Goyal

---

## 5. Fallback levels and slip triggers

### 5.1 The four levels (decision A7)

The consensus names the levels (T9-C26-R2) but gives only some triggers. Triggers marked **proposed** are this pack's. Wording is AI_DRAFTED. Fill the brackets from committed files only.

| Level | What runs | Trigger | What the talk says (pre-written) |
|---|---|---|---|
| **L0 Full plan** | H1 and H3 piloted on the frozen benchmark. One SIMULATE pilot, RESEARCH_ONLY. 29-diag H2 diagnostic. Router census with gates. | Everything below is green by Thu 19 Nov. | "We piloted H1 and H3 on a [N]-question benchmark that the two of us reviewed (MODEL_ASSISTED_GOLD). Result: [from file], with intervals. At this n only gaps of about 0.25 or more can show. 0 of 4 hypotheses are confirmed." |
| **L1 H1 only** | H1 runs. H3 is NOT_RUN. | **Proposed:** S1 and S2 reviewed and frozen by Tue 17, but a P or C block has fewer than 10 reviewed questions, or the 30-claim blind audit is not back by Fri 20. | "We piloted H1 only. H3 was not run: the evidence blocks were not fully reviewed in time. H3 stays untested." |
| **L2 Benchmark frozen or drafted, not run** | Nothing is run on the benchmark. | D5 not reviewed and frozen on Mon 16, or the reviewed count is below 40 (REV-B). Freeze whatever both of you kept by the hard stop. SIM-VAL drops to SHOULD. | "A [N]-question benchmark was drafted and [N reviewed]. H1 and H3 were NOT_RUN. We do not present runs on unreviewed AI gold." |
| **L3 Router census and gates only** | No new results after the census. | Results are not in by Thu 19 Nov. | "Our result is the audited pipeline up to the router and its census: most checks are UNKNOWN. No hypothesis was tested." |

Minimum rule (REV-B D.3): fewer than 40 reviewed items means no H1 or H3 numbers at all.

### 5.2 Slip triggers with dates

| Date | Gate | If it slips (pre-written fallback) | Source |
|---|---|---|---|
| Mon 9 | #1 lot state ruling. #2 07.A ruling. | Lot state defers to stretch. Without the 07.A ruling the R1 prereg cannot be signed, so 07.A stays FAILED on record. | consensus 4.1 |
| Tue 10 | Prereg edit lock and hashes. AA PDFs. Step 35 decision (#3). Governance pack. | No edits after the lock. Missing PDFs: fit on the 4 papers already present, the missing paper dropped and recorded. Step 35 becomes DESIGNED, NOT RUN. Governance pack: ship with "relays unratified" disclosed in the method section. | consensus 4.1; REV-B D.3 |
| Tue 10 to Wed 11 | Signatures: 07A_R1, AA, D5, 15A-BOOT, 29-diag. | Each unsigned prereg means its result is reported **NOT_RUN**, never run on an AI signature. One human unavailable: record "signed by Kush; Parv pending". | consensus 4.1; REV-B D.3 |
| Thu 12 | 29-diag signed. | Drop it. Keep the DEL-2 "D7 = D1" suspicion on the failure slide: "diagnostic not run". | REV-B D.3 |
| **Fri 13** | 07.A-R1 labels in. | 07.A stays FAILED on record (v4). 23b stays closed. Say: "second attempt pre-registered; labels not returned". It changes nothing the talk shows. REV-B would allow a late return to Fri 20 for credibility only. | consensus 4.1; REV-B D.3 |
| Sat 14 | D5 runner dry run on vinayak. | Fix the route. Plan the manjot-CPU fallback. | consensus 4.1 |
| **Sun 15** | AA CAL rows dual-verified. | No PARAM and no SIMULATE result. SIMULATE wiring ships "code-tested only". Model A is NEED_DATA if below the prereg minimum. REV-B: verify only the 16 CAL rows from the 7 PDFs already fetched and skip the 5 browser PDFs (SIM-VAL then has 3 papers or fewer, say so). | consensus 4.1; REV-B D.3 |
| **Mon 16** | D5 reviewed and frozen. Model A fit frozen. | Level L2: H1 and H3 NOT_RUN. SIM-VAL drops to SHOULD. Hard stop for the benchmark freeze is **Tue 17**; REV-B's "Wed 18 latest" is not adopted (runs would have one day). | consensus 4.1; T9-C26-R1 |
| Tue 17 | vinayak reachable. | Run the rungs that need no LLM on manjot CPU. LLM rungs NOT_RUN (C07, written into the D5 prereg in the lock). | consensus 4.1 |
| Thu 19 | Results in. | Level L3: report is the router census and gate table only. | consensus 4.1 |
| Fri 20 | Claim audit back. Slides edited. | L1 for H3 if the audit is missing. | proposed |
| Sat 21 | **Code and result freeze.** Hosted demo or cached fallback. | Nothing new enters the talk after this. Demo: cached answers for 15 to 20 queries plus a screen recording. | consensus 4.1; REV-B D.3 |
| Sun 22 to Mon 23 | Human edit of report and deck. | Agent ships the draft with every number cited to a file. | consensus 4.1 |
| Tue 24 | Timed rehearsal and Q&A sheet. | none | consensus 4.1 |

### 5.3 Three rules that never bend

1. **NOT_RUN is a valid, honest outcome.** Say it on the slide. Do not fill a gap with an AI-signed or unreviewed result.
2. **No edits to a signed prereg.** A change is a dated amendment before labelling, or the attempt is void.
3. **No claim word without a gate** (section 6.1).

---

## 6. We cannot claim: the Q&A sheet

Drafted for the 24 Nov rehearsal (T9-C26-R3). Numbers come from the files named. Wording marked **[if]** depends on whether a fix landed. Refresh the numbers on 21 Nov.

### 6.1 Words we do not use

| Word | Why | Say instead |
|---|---|---|
| validated, calibrated | No calibrated or held-out-validated model exists. `sim_aa_1` is NOT_VALIDATED. B7 is uncalibrated. | "pilot", "descriptive", "RESEARCH_ONLY" |
| supported, confirmed, beats, proved | H1 and H3 are pilots at small n with authors as reviewers. 0 of 4 hypotheses are confirmed. | "met the pre-registered pilot rule at n = [N]" only if the file says so; else "not shown at this n" |
| accuracy (for D3 or the router) | No blind gold. Router accuracy is unmeasured. | "engineering score on 7 recipes" |
| coverage (for DIRECT 0.754 %) | The denominator includes pairs such as flour x vitamin C. | "funnel" |
| safe, safe to eat | No safety layer is evaluated. | "not evaluated" |
| pre-registered (for an unsigned file) | D-074 used it loosely. | "dated AI draft" until a human signs |
| physics-based prediction (for Layer 2) | Layer 2 is defaults and brackets. | "scenario envelope" |
| measured (for USDA R6 or EVD values) | They are reference-table values, partly calculated or imputed. | "unverified table values" |

### 6.2 Limitations that must be said

| # | Topic | Limitation | Honest wording (say this) | Where it is recorded |
|---|---|---|---|---|
| 1 | Overall | 0 of 4 hypotheses confirmed. H1 and H3 piloted. H2 diagnostic on data we had already read. H4 not started. | "We piloted H1 and H3 at small n, ran H2 as a diagnostic on data we had already looked at, and did not start H4." | REV-B Q27 |
| 2 | Pipeline | Real and full-scale up to the router. No calibrated or validated model. No PARAM rows unless the AA pilot verifies. | "Our main finding is how little the data supports: most checks end in UNKNOWN." | consensus section 1 |
| 3 | 07.A | FAILED on packet v4: kappa 0.0 (gate 0.80), raw agreement 0.9944, 900 cells, 5 disagreements. The cause is the kappa paradox, not proven error. | "Our first human audit of the condition normaliser failed its gate. We kept that on record." | `reports/step07/step07_v4_agreement_result_run2.json` |
| 4 | 07.A-R1 | **[if]** Second attempt on a fresh packet with a statistic chosen after the failure. | "We changed the statistic after a failed gate, pre-registered the change, and kept the first failure. Status: [PASS or FAIL or labels pending]." A PASS opens nothing before 25 Nov. | #2 DECISIONS entry |
| 5 | Evidence plane | 17,978 ACTIVE EVD rows, all tier E3, unverified. USDA R6 values are partly calculated or imputed. COND is not human-audited (07.A not passed). D1 hand-verified literature rows: 0 of 40 **[if still 0]**. | "These are reference-table values, not our measurements. We have verified [N] rows by hand." | consensus section 1; MANUAL_NEXT_STEPS |
| 6 | Lineage | G08-3 FAILED (the two reviewers' audits disagreed: B3 13 of 50 against 0 of 50). USDA R6 and Bognar are one lineage cluster each. | "We cannot make study-disjoint claims on USDA or Bognar. Their agreement is not independent validation." | NEG-0002, NEG-0008; D-034 |
| 7 | Router DIRECT | DIRECT is an evidence-table lookup, not router skill. 274,058 DIRECT of 36,359,902 checks (0.754 %) has a meaningless denominator. In a 1,000-recipe non-BBC sample, 364 of 451 DIRECT (80.7 %) were for foods with about 0 mg vitamin C and 372 (82.5 %) came through merged lots. | **[if A2 landed]** "We added target-presence and context gates; DIRECT fell from [old] to [new]." **[else]** "This is a known flaw; most DIRECT hits are not applicable." | REV-A V5, N5 |
| 8 | Router accuracy | Unmeasured. No false-activation rate. An all-UNKNOWN router passes any safety test trivially. G23.1 and G23.3 are not evaluated. | "We report what the router does, not how well. A labelled case set is future work." | REV-B Q20 |
| 9 | SIMULATE | One system (vitamin C). Calibrated on about [N] verified rows from at most 8 papers, acidic fruit juices and nectars. SIM-VAL has 4 papers (3 if AAK-05 is missing), under the plan's 5. Leaching unidentified, so vegetables in water stay UNKNOWN. The agent extracted and fitted (the SIM-VAL firewall is behavioural). | "One pilot, RESEARCH_ONLY, NOT_VALIDATED. It shows the pathway from verified rows to a held-out check. It does not show that simulation works for recipes." | D-076; REV-A V7, Q16; REV-B F-09 |
| 10 | Layer 2 | The 27 defaults are `SOURCE_UNVERIFIED_AGENT_RECALLED`. Of computed scenarios, 67.7 % of bath temperatures are defaults and 60.5 % of durations are corpus quantiles (BBC and Wikibooks). TYPICAL is a middle, not an estimate. | "Scenario drivers are an envelope under assumed defaults. They are never a measurement." | REV-A V1, V3, V4 |
| 11 | Heat model | **[if A2 not landed]** The committed DRY and FAT core temperatures are wrong (163 to 220 C for moist pieces) and doses are inflated by about 100 times. Only 69,995 of 1,746,405 heat events (4.0 %) have a core trajectory. | "We found a physics error in our own outputs: the heat model has no evaporation term. We marked those fields SUPERSEDED **[if landed]**." | REV-A V1, V2 |
| 12 | Layer 1 | Only 3.4 % of heat events are driver-ready from the text alone (5.3 % with ranges). Recipes rarely state both time and temperature. UK "fan or gas" strings are not resolved. | "Recipes rarely say how long and how hot. That is why we added a labelled scenario layer." | consensus section 1; REV-A V14 |
| 13 | Food safety | Not evaluated. F0 is a canning reference, not a cooking rule. | "We do not answer 'is it safe'. The demo refuses." | REV-A N4; REV-B G-13 |
| 14 | D3 state tracker | No accuracy claim. P1 gold is human-accepted AI drafts, not blind; handbook verdict HANDBOOK_REVISION_REQUIRED. | "Built and run on 612,782 recipes. Compared with 7 recipes as an engineering score, not an accuracy claim." | REV-B Q28; `p1_agreement_counts_S166.json` |
| 15 | H1 | Pilot. n = [30 or 60]. **[if A1 B not adopted]** S1 gold is engine output and B4 saw it; H1 on S1 measures engine self-consistency. At n = 30 a null result is uninformative. | "We cannot show small effects at this n. The S1 gold came from the engine, so S1 is a consistency check." | REV-B F-13, Q26 |
| 16 | H3 | UCR for B7 is zero by construction (the same checker removes and scores claims). It measures evidence-conditional faithfulness, not truth. B7 is rule-based and uncalibrated. | "H3 shows the enforcement works as designed. A human audit of 30 claims is our independent check: [result]." | REV-B Q27, F-12, G-07; #5 |
| 17 | Benchmark gold | MODEL_ASSISTED_GOLD, PILOT, authors-as-reviewers. [Outside check on 20 items: yes or no.] | "The two of us reviewed AI-drafted questions. Outside check: [N items by whom, or none]." | REV-B Q25; A5 |
| 18 | P3 abstention | Gold ABSTAIN means "our ledger is silent". B7's route is also a ledger lookup, so P3 abstention is guaranteed. | "On P3, abstention follows from the design. It does not show the system knows what it does not know." | REV-B F-12 |
| 19 | H2 | PRIOR_EXPOSURE_REANALYSIS. No pass gate. Cold-split collapse: learned models do not beat persistence under study, matrix or process splits. D7 matched D1 to four decimals on Phenol-Explorer (cause not investigated). Conformal 90 % intervals under-cover on cold splits (0.72 to 0.89). USDA and Bognar are single clusters. R6 values are capped at 0.975 and imputed from similar foods. | "H2 is a diagnostic. We looked at these rows before. We cannot conclude that process information beats food identity." | NEG-0001, 0003, 0004, 0006, 0007; REV-A Q18, Q19 |
| 20 | 29-diag | **[if signed and run]** Memo numbers carry DIAGNOSTIC, BOOTSTRAP_UNVERIFIED, NON_CITABLE. **[if not]** Not run. | "Diagnostic: [run, not a result] or [not run]." | REV-B D.3 |
| 21 | Step 35 | **[if #3 = A]** DESIGNED, NOT RUN. Learned rungs deferred. | "Designed and pre-registered, not run." | #3 |
| 22 | NER | The tagger scores about 0.93 to 0.94 exact entity F1 on TASTEset, which is in-domain. Food.com has no units, so UNIT tags fall far below QUANTITY. Corpus accuracy is unmeasured. NER outputs are diagnostics, never gold. | "The F1 is on the tagger's home dataset. On Food.com we have not measured it." | `reports/ner/culinaryner_kf_final_report.md`; `reports/ner_v2/ner_corpus_counts_S174.json`; REV-B Q33, Q34 |
| 23 | Quantity parser | 29.8 % of corpus ingredient lines (1,275,782 of 4,281,956) carry a Unicode fraction slash the legacy parser misreads (SP-002). 4,511 inverted-interval cases. Fix is after the talk. | "Known parser defect. Quantity figures carry this caveat." | DECISIONS D-070, D-072 |
| 24 | Linker agreement | Two humans agreed only moderately on linker gold: kappa 0.500 (441 items) and 0.317 (850 items). | "Human agreement on ingredient linking was moderate to low." | NEG-0025, NEG-0026 |
| 25 | Mechanisms | All 32 MECH entries are AI-drafted and unreviewed. They appear in no claim. | "The mechanism screen is a demo aid, not evidence." | REV-A V9; REV-B Q21 |
| 26 | Lot state | Not built for the talk. Design only. | "Lot state is future work." | #1 |
| 27 | Non-heat families | Drafted on 1,000-recipe samples only. NON_CITABLE. | "Sketched, not evaluated." | `reports/step26/nonheat_*` |
| 28 | Demo | NON_CITABLE. Template-only. SEMANTIC and MULTIMODAL abstain. ASK untested. The demo does not replay a state (DEPLOY finding 4): "current state" and "next action" questions, the H1 task types, end as ASK, so the demo cannot show H1. **[if not fixed]** the green "Answered from data" badge also appears on broad qualitative answers built from unrelated foods; one shipped example was BBC-derived; there is no food-safety refusal yet. Router recall gaps seen in real output ("fried okra" and "what is the next instruction" end as ASK). Examples from Gutenberg. | "A demo of the abstain-first design, not a product. It does not show state tracking." | #17; A6; DEPLOY section 0.3 |
| 29 | Licences | BBC Good Food data never leaves the Mac (D-003); only counts are shown. Food.com is uploader-declared CC0, unverified. Wikibooks is CC BY-SA. Gutenberg is public domain. USDA is public domain. Phenol-Explorer redistribution is not cleared in writing. | "BBC numbers are counts only. Food.com's licence is declared by the uploader and unverified." | `orch_ctx` law 6; REV-B Q30, Q36 |
| 30 | AA licences | Licences were UNKNOWN for AAK-01 and AAK-11 when rows were extracted. Rows from any paper that is not CC BY or CC0 are dropped. | "Rows from [N] papers; [N] dropped for licence." | `aa_kinetics_source_candidates_v1.csv` |
| 31 | Reproducibility | Run log has 14 rows: start blank in 10, end blank in 14, output hash blank in 3. No input, code or environment hash column. No lockfile. LLM digest not logged. **[if G-11 landed]** fixed. | "Counts can be re-derived from committed JSON. Full re-runs are not yet reproducible." The BBC part cannot be reproduced by anyone without BBC. | REV-B F-10, Q35 |
| 32 | AI use | AI drafted every label and verdict first. Humans reviewed (D-045 W2). ksh and prv decisions under D-071 are AI-made under delegation. Permission is "as stated by Kush" unless a written copy exists. | "Which gates were AI-delegated and which were human-signed is in [report section]." | DECISIONS D-045, D-071; #19 |
| 33 | Governance | D-046 and D-070 record Parv's agreement as relayed. D-068 was appended by the agent on a waiver. **[if A4 done]** ratified on [date]. | "Two records were relayed; we repaired them on [date]." | REV-B B2.2 |
| 34 | Scope cuts | D2, full H2, H4, Steps 20, 28, 33, 34, FlavorTwin were cut. D3 gold of 40 recipes and the 8-scenario demo were not delivered at that scale. | "These were in the proposal. We cut them on [date], in writing." | #18 |
| 35 | Sensory | Ingredient-level SENSORY is UNSUPPORTED. Structure is not sensory. No flavour claim. | "We do not predict taste." | T7-C08-R1 |
| 36 | Time | Two authors; reviewers are the authors. Hours are estimates. | | |

### 6.3 If asked

| Question | Short answer |
|---|---|
| Does it work? | "The pipeline runs on 612,782 recipes. What it shows is how little the evidence supports. The pilots are small and say so." (rows 1, 2) |
| Why is the router almost always UNKNOWN? | "Because the evidence ledger has 115 vitamin-C pairs over 25 ingredients. UNKNOWN is the honest answer." (row 7) |
| Was H1 a fair test? | "It is a pilot. We found S1 was circular and [fixed it / kept it and said so]. A null is uninformative at this n." (rows 15, 17) |
| Who wrote the gold? | "AI drafted, the two of us reviewed. Not independent." (rows 17, 32) |
| Is the vitamin C simulation validated? | "No. One pilot on fruit juices, RESEARCH_ONLY." (row 9) |
| You changed the 07.A statistic. Isn't that gate shopping? | "We pre-registered the change after the failure, added an accuracy check and planted errors, and kept the failure on record." (rows 3, 4) |
| Can I use it to decide if food is safe? | "No. It refuses." (row 13) |
| Is the data licensed for this? | "BBC: counts only. Food.com: declared CC0, unverified. We asked our supervisor in writing on [date]." (rows 29, 32) |

---

## 7. Lane record (for the orchestrator; not for the humans)

**Deliverable:** this file. No code, no tests, no compute runs, no ledger edits. Nothing signed or decided. No separate `S176_OPS_report.md` was written; this section is the lane record.

**Files read:** consensus plan (sections 1, 3.7 to 3.11, 4, 6), `registry/component_ledger_v1.csv` (human-owned rows), REV-A, REV-B, `handoff/FINISH_PLAN_2026-11-07.md`, `handoff/ORCHESTRATION_TAKEOVER_2026-11-08.md`, `handoff/MANUAL_NEXT_STEPS.md`, `DECISIONS.md` (D-045, D-046, D-068, D-070 to D-077), the four prereg drafts, `registry/freezes/15A-BOOT-2026-11-08.json`, `src/culinarystate/evaluation/freeze_records.py`, `tools/step07ar_agreement.py`, `tools/aa_pilot_fit.py`, `reports/step07/07A_R1_packet_manifest.json`, `reports/step10/aa_pilot_CAL_packet_manifest_v1.json`, `registry/evidence/aa_kinetics_source_candidates_v1.csv`, `reports/step35/35_0_v2_signature_sheet.md`, `reports/step19/P1b_design_amendment_PROPOSED.md`, `reports/del4/retrieval_silver_v2_analysis.md`, `registry/negative_results_register_v1.csv`, and the sibling lane's `handoff/DEPLOYMENT_AND_PRESENTATION_PLAN_2026-11-08.md` (read for the demo asks H-1 to H-9 and its findings; I did not re-verify its hosting prices).

**Checks run (read-only, on manjot):** `prereg_signed('.')` printed `False`; `freeze_problems('.', '15A-BOOT-2026-11-08')` printed `['NOT_APPROVED', 'NO_HUMAN_APPROVAL']` (so the ledger hashes match in this tree). `python tools/step19_real_pilot.py check --record reports/step19/pilot_start_record.SIGNED.json --wave P1b` returned 1 blocker, `H5_WAVE_NOT_AUTHORISED`. `tools/step07hr_freeze.py --verify` **fails on manjot** (missing `ledgers/recipe_semantics/recipe_expression_probe_v1.parquet`), so it is marked Mac-only.

**Where the two source plans differ, and what the pack chose:**

| Point | Consensus | REV-B | Pack |
|---|---|---|---|
| Benchmark freeze | Mon 16 | review Mon 16 or Tue 17, freeze by Wed 18 | Mon 16 planned; Tue 17 hard stop (T9-C26-R1) |
| 07.A-R1 labels | Fri 13 (trigger) | soft Fri 13, hard Fri 20 | Fri 13; Fri 20 noted as REV-B grace |
| Signatures | Tue 10 to Wed 11 after the lock | Mon 9 and Wed 11 | After the lock, finishing by Wed 11 noon |
| 5 PDFs | Tue 10 | Wed 11 | Tue 10, Wed 11 morning as suggested grace |
| Claim audit | 30 claims, 1 to 1.5 h | 40 to 60 claims, 1 h | 30 claims, 1.25 h |
| S pool | 30 (15 + 15) | 60 (30 + 30) | Option, recommended if both have at least 18 h free |
| 07.A gate | AC1 at 0.80 as drafted, or kappa | AC1 at 0.95 plus co-gate, planted rows | B2 recommended |

**Open questions for the orchestrator:**

1. The lock record path and the signature file names for 07A_R1, D5 and AA are proposals. The checker for them is not built (REV-B G-04). The agent must wire it before Tue 10 afternoon.
2. U and X blocks of the D5 benchmark have no drafts (consensus T8-C20-R4, SHOULD). The pack assumes they are drafted before the sheets are issued.
3. The `annotation/d5_review/` sheets and the 07.A, AA packets are Mac-only. Their exact current file names were not checked in this tree. The packet names come from `tools/step07ar_build_packet.py` and the prereg; the AA verification packet name is not recorded anywhere in the tree.
4. The consensus T9-C26-R2 text lists B0 among "deterministic rungs" for the manjot fallback, but B0 is "LLM only" in the D5 prereg. The pack asks the agent to confirm.
5. Decision #20 option A as the consensus words it ("a Mac venv") conflicts with the repo `CLAUDE.md` rule "No new venvs".
6. AAK-01 and AAK-11 were extracted with licence UNKNOWN (prereg section 1 says the licence is confirmed before use). Disclosed in row 30 and 4.3a.
7. No personal calendar information is recorded here; Kush and Parv state their own availability at the sitting.
8. Hours are the ledger's estimates (UNVERIFIED). The plan totals 19.9 h (Kush) and 17.2 h (Parv) for 9 to 16 Nov. Kush's total includes 0.5 h from the DEPLOY plan (demo machine and slot check 0.15 h, demo dry run 0.35 h); its other asks (H-5, H-6, H-8) fall after 16 Nov.
9. REV-B governance repairs (D-046, D-068, D-071 half) are not in the consensus decision list. They are A4 here.
10. The DEPLOY lane's plan and this pack agree on dates (21 Nov freeze, 24 Nov rehearsal) and on "no BBC-derived example". They differ on one point: DEPLOY asks Kush to approve the demo plan by Tue 10 Nov; REV-B and T8-C18-R1 had it later (Fri 13). The pack takes Tue 10 (in A6). DEPLOY's own findings (stateless demo, no safety refusal, a BBC-derived example, a misleading badge) are carried into section 6.2 row 28 so the Q&A sheet stays honest if they are not fixed by 21 Nov.
11. Two items in section 4 depend on tooling that does not exist yet: the D5 freeze command and the signature checkers for 07A_R1, D5 and AA. Without them the agent can only verify by hand-run `sha256` compares.
