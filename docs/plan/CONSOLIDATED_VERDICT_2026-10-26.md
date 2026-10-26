# CulinaryState: consolidated verdict (2026-10-26, WORKLOG S142)

Single reference for: what exists, which document wins, what the humans owe, the architecture, and what is realistic for 25-26 Nov 2026. Built from three independent read-only audits of the merged repo. Nothing here is a signature or a ruling; it records the state and the order of work.

## 1. Verdict in five lines
1. The 36-step spine (`registry/execution_spine_v2.csv`, 123 rows) has had **no new data work since Step 07I-R (22 Oct)**. About 6 rows done, 9 partial, 13 blocked, 69 not started.
2. Everything Max added (Plan v2, D-027, Step 04 v1.1 drafts, thresholds, Steps 21/19-D/35.0 drafts) is a **DRAFT**. Nothing is approved, signed or frozen. Step 08 is **not authorised**.
3. The bottleneck is **human hours** (signatures and blind labelling), not compute. No A100 work is planned in Plan v2.
4. The next scientific step is **Step 08a** (lineage on the 17,978 EVD rows, CPU, Mac). It needs only the Step 04 approvals, the 08a thresholds and Kush's written go-ahead. It does **not** need the two blind labelling passes (D-027 R-05 makes 07.A soft for Step 08).
5. For 25-26 Nov, show DEL-1..DEL-5 as finished silver/AI-assisted work and the new contracts as design. Cut Steps 26-28, 29-34 and 15b.

## 2. Who did what
| Who | Work | WORKLOG |
|---|---|---|
| Mac Claude sessions | Repo, ledgers, KG, DEL-2/4/5 code, NER and A100 runs, Gold pilots, Steps 05, 06, 07, 07H-R, 07I-R, D-026 intake | S001-S137 |
| Max (server) | Plan v2 and D-027, two-persona review, Step 04 v1.1 draft contracts, 9 schema drafts, 47 threshold rows, negative-results register, Step 21 / 19-D / 35.0 drafts and reviews | S138-S141 |
| Kush + Claude (operator/reviewer) | Merge of Max's branch, renumbering, D-028 rename, runbook ids, STATUS refresh, Step 21 round-3 fixes (contract test 22/22), repo clean-up | S142 |
| Humans (all open) | Signatures, blind labelling, licences, domain checks | none yet |

## 3. Which document wins
1. SSOT v15 laws and frozen contracts.
2. Signed human rulings in `DECISIONS.md`, including D-027 R-01..R-20.
3. `docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md` sections 0 and 7 (self-labelled PENDING HUMAN REVIEW).
4. Advisory: Final Master Plan v4.0, Detailed R&D Plan v2 (SSOT v14 base).
5. Proposals only: `reports/master_plan/master_plan_research_audit_v2.md`, `docs/SSOT/ssot_v16_change_set_DRAFT.md`.
6. Drafts with no force until signed: D-028, the runbook, the ADAPTED Master Plan draft.

Resolved contradictions (winner first):
- 08a go-ahead: Plan v2 section 7 (four preconditions plus Kush's written go-ahead) beats D-028 line 15.
- Step-07 gate: pooled kappa >= 0.80 (R-06) beats the audit's per-field kappa.
- Thresholds: `registry/preregistered_thresholds_v1.csv` (47 rows, THR-*) beats `_v1_DRAFT.csv` (14 rows).
- Deep Gold pilot size: 20 (Plan v2 X6) beats "20-50" in the runbook and ADAPTED draft, pending Kush.
- SSOT v16 "adopt now" items: Plan v2 section 6 (D-027 approves none of them) wins.
- D-026 / D-027 numbering caveats in Plan v2 and the v16 draft are obsolete: both ids exist in `DECISIONS.md`.
- Still unresolved (needs a human line): the original 36 step cards are not in the repo, only titles.

## 4. Architecture (spine layers)
| Layer | Steps | State |
|---|---|---|
| 0 Authority and contracts | 01-04 | historical DONE; v1.1 additions (01.6, 04.1, 04.2/04.6/04.9-min, 04.3) DRAFT, waiting for H4 |
| 1 Data and evidence factory | 05, 06, 07, 07H-R, 07I-R, 09, 12, 13 | 05, 06 automated, 07 automated PASS; 09, 12, 13 prototypes only |
| 2 Lineage | 08a, 08b | NOT STARTED, NOT AUTHORISED |
| 3 Conditions and identity | 07.A, 07I-C, 07I-S | BLOCKED by blind labelling (0 judgements; `labels_filled` = 0) |
| 3b Evidence growth | 10, 11, 14, 15x | NOT STARTED; 15b hard-gated on a valid 07.A |
| 4 Procedural state | 16-20 | 16, 18 partial; 19-D design draft; 19-pilot blocked |
| 5 Mechanisms | 21-25 | 21 draft (fixed, 22/22); rest not started |
| 6 Simulation | 26-28 | not started / blocked / deferred |
| 7 Transition science | 29-34 | 29, 30 partial; 31-34 blocked |
| 8 Representation | 35 | 35.0 pre-registration draft |
| 9 Retrieval and answer | 36 | prototype partial (DEL-4/5) |

Deliverables: DEL-1 ledger 17,978 rows, 0/40 verified literature rows. DEL-2 done as a negative result (gains vanish on cold splits). DEL-3 engine plus Gold v1.1 (batch-reviewed only; 0/30 sessions reviewed). DEL-4 retrieval and NER done on silver data. DEL-5 prototype done; the 80-question human benchmark, allergen sign-off and the demo are missing.

## 5. What the humans owe, in order
### 5a. Minimum to unblock Step 08a (about 10-12 Kush hours, 2-3 Parv hours; Parv's part is the Step 04 approvals only)
1. Read the H4 checklist: `reports/step04/README.md` section 4.
2. Approve 04.1, 04.2-min, 04.6-min, 04.9-min (same file).
3. Sign D-028 item 4 and the 23 rows `THR-08A-01..23` in `registry/preregistered_thresholds_v1.csv`.
4. Decide whether the planned manifest v1.1 (06.3-min, file does not exist) is a hidden precondition of 08a.
5. Record where 08a runs (Mac or server CPU) and the baseline sha256 of the 7 ledger files.
6. Assign real DECISIONS ids for the rulings and registries.
7. Write the 08a authorisation in `DECISIONS.md`.

### 5b. Needs two people (blind; waits for Parv or a decision on how to run it)
- 07.A condition audit: `annotation/condition_audit/condition_audit_packet_100_v4_Kush.csv` and `_v4_Parv.csv` (2-3 h each). Soft for 08; hard for Steps 15, 23, 29-33.
- 07I-C identity pairs: `annotation/duplicate_calibration/duplicate_pairs_v1_Kush.csv` and `_Parv.csv` (4-10 h each). Do not open `_KEY_SEALED.csv`.
- Before either: sign the 07.A amendment (`reports/step07/condition_audit_protocol_amendment_v4_1_DRAFT.md`, D-028 item 5), rule on THR-07A-06, pre-register 07I-C (THR-07IC-01..12).

### 5c. Later or optional
- Licence decisions (21 items, `reports/h_state/es_1_2_h2_approval_queue.md`; Food.com and TASTEset first).
- Step 21 chemistry OPEN_QUESTIONs (`reports/step21/FIX_LOG_round3.md`): needs a domain expert, 8-16 h.
- Older DEL items (`handoff/MANUAL_NEXT_STEPS.md`): 40 literature rows, 30 sessions, 80 benchmark questions, allergen sign-off, FSIS/FooDB/FoodAtlas downloads, professor email.

## 6. Scope for 25-26 Nov (4 weeks)
- **Show as finished (label silver / AI-assisted honestly):** DEL-1 ledger and data card, DEL-2 negative result, DEL-3 engine with Gold v1.1, DEL-4 retrieval and NER, DEL-5 prototype, the 07H-R and 07I-R automated gates.
- **Show as design only:** Step 04 v1.1 contracts, Step 21 mechanism ontology, 19-D pilot design, 35.0 pre-registration, 36A evidence compiler; simulator candidates (ascorbic acid leading, chlorophyll fallback).
- **Cut:** Steps 26-28, 29-34, 35g, 36D, 15b, any paper-grade claim.
- Realistic Kush load: about 25-35 h (H4 chain, labelling, possibly 08a). 19-pilot (16-38 h) does not fit.

## 7. Next ten actions
1. [Kush] H4 review and signatures (5a, items 1-6).
2. [Kush] Written 08a go-ahead (5a, item 7).
3. [Mac, CPU] Run 08a on the 17,978 EVD rows; Kush reviews the output.
4. [Kush] Sign the 07.A amendment, rule on THR-07A-06, pre-register 07I-C.
5. [Kush + Parv] 07.A and 07I-C blind labelling (decision needed on Parv's availability).
6. [Mac] Run `tools/step07_agreement.py` after both files return.
7. [Mac] Re-check Step 19/35 items B 35-3, 35-4, 35-9, 19-5 (not yet re-checked).
8. [Kush] Licence decisions and the professor email.
9. [Kush + Parv] 40 literature rows, 30 sessions, 80 benchmark questions.
10. [A100, optional] only if spare time; confirm VPN first.

## 8. Unknown (not stated in the repo)
Current DEL-1 verified-row count; Gold pilot status after S083; whether the Streamlit demo exists; whether the S083-era weekly plan still holds; Parv's availability; who approved the Detailed R&D Plan; the original 36 step cards.

## 9. Housekeeping still to apply (docs only)
Add "superseded by" status banners to: `CulinaryState_Claude_Max_Master_Prompt_v2_0.md`, the Detailed R&D Plan and the audit; mark `registry/plan_authority_map_v1.csv` as older than D-027 (no rows for Plan v2, the audit or D-027).
