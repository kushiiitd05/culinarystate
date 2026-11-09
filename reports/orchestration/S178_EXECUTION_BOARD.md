# S178 execution board: every MUST and SHOULD item of CulinaryState, 9-23 Nov 2026

Status: **AI_DRAFTED / PROPOSED** (S178 ROLE BOARD, written Mon 9 Nov 2026 about 15:30 IST on manjot-server, tree `~/kush_work/culinarystate/.orch`, branch `max/s176-orchestration`, HEAD `42c01bf` plus uncommitted S177 work). Nothing here is a decision, signature or approval (D-071). Hours are the ledger's estimates reduced for work already done and are **UNVERIFIED**; the humans' calendars are not in the repo and are unknown.

Companion file: `registry/execution_board_S178.csv` (one row per MUST/SHOULD ledger item, 252 rows: 84 MUST + 168 SHOULD). Inputs read: `registry/component_ledger_v1.csv`, `reports/orchestration/ssot_consensus/CONSENSUS_PLAN_2026-11-08.md` (sec 4, 6), `handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md`, the S176/S177/S178 lane reports, the two FINAL reviews, `handoff/MAC_TASKS_FROM_CONSOLIDATION_S177.md`, `git log 07fc0d2..HEAD` (62 commits) and the working tree.

## 0. How to read this board

| Term | Meaning |
|---|---|
| `status_now` | Item-level state on 9 Nov, judged from repo paths, not from the ledger's component `status` column (that column is per component: 19 MUST/SHOULD rows inherit `DONE` and 38 inherit `RUN` from their component while the item itself is open or partial). **DONE** = the ledger acceptance is met by an artifact on disk. **PARTIAL** = part of the acceptance exists (evidence named). **OPEN** = nothing yet, an agent can start. **BLOCKED_HUMAN** = the next step is a human decision, signature, label or fact (a draft usually exists; evidence is named in the CSV). **BLOCKED_DATA** = the input does not exist on the machine that would run it. |
| `wave` | Wave in which the item is planned to **close**: W1 Mon 9 - Thu 12, W2 Fri 13 - Mon 16, W3 Tue 17 - Fri 20, W4 Sat 21 - Mon 23 (code and result freeze Sat 21). **W0** = already done before 9 Nov 15:30. **POST** = cannot be finished by 23 Nov; the reason is in `post_reason` and `notes`. |
| `owner` | The actor who does the next step: `manjot-agent`, `mac-agent`, `kush`, `parv`, `kush+parv` (each does it separately where the item says 'each'), `expert`. Humans own every signature, label, freeze approval, nonce and fact (D-071); the item's agent part is in `notes`. |
| `agent_hours`, `human_hours` | **Remaining** estimate (midpoint of the ledger range, reduced for DONE/PARTIAL). Human hours are per person where the ledger says 'each'. The raw ledger text is in `ledger_agent_hours`, `ledger_human_hours`. |
| `review_needed` | GOV = governance/licence/law reviewer (R-GOV); SCI = food-process/chemistry/statistics reviewer (R-SCI); BOTH. Every reviewer is an AI persona unless the row says a human; an AI review is never a human verification. |
| `lane_group` | Items one agent lane can do together; the same label is used in the wave tables below. |

Owner split used throughout (S176 takeover, D-078): **mac-agent** owns `composition/`, BBC runs (D-003), vinayak jobs (GPU, VPN), git merge/push and the scribing of human gates; **manjot-agent** owns `simulation/`, `mechanism/`, `decision/`, `app/`, `evaluation/`, analyses, reviews, SSOT v16 and all non-BBC runs. The ledger's `where` column sometimes says otherwise; the board follows the split and lists the differences in sec 12.

## 1. Verdict

| Priority | DONE | PARTIAL | OPEN | BLOCKED_HUMAN | BLOCKED_DATA | Total |
|---|---|---|---|---|---|---|
| MUST | 4 | 15 | 23 | 42 | 0 | 84 |
| SHOULD | 6 | 27 | 85 | 48 | 2 | 168 |
| MUST + SHOULD | 10 | 42 | 108 | 90 | 2 | 252 |

**Planned closing wave** (MUST / SHOULD): W0 4 / 6; W1 33 / 13; W2 18 / 49; W3 22 / 46; W4 7 / 3; POST 0 / 51.

What the numbers say:

1. **Only 10 of 252 items are DONE and 42 are PARTIAL.** The work finished since 8 Nov (sec 2) mostly built tools, drafts and censuses; it did not close ledger items, because most MUST items end in a human act.
2. **42 of the 84 MUST items are BLOCKED_HUMAN** (decisions, signatures, blind labels, verification, freezes, edits). Agents can prepare all of them (the drafts exist for the 9-12 Nov decisions and the four preregs) but cannot close one. The two weeks are a human-throughput problem: Kush is planned at 19.5 h and Parv at 18.2 h for 9-16 Nov against a 16-20 h budget, which leaves Kush 0.5 h of slack and Thu 12 as the only buffer (sec 8).
3. **All 84 MUST items have a closing wave inside 9-23 Nov** (the rehearsal T9-C26-R3 ends Tue 24 by design; T9-C07-R2 needs a third party and has an allowed fallback wording). Whether they close depends on five gates: decisions #2-#7 (Mon 9 / Tue 10), the prereg lock (Tue 10), the signatures (Wed 11 noon), the three blind human tasks (07.A labels Fri 13, AA rows Sun 15, D5 review Mon 16) and VPN to vinayak. If a gate slips, the downstream MUST items flip to NOT_RUN, not to later waves (sec 11.2).
4. **51 SHOULD items (30 % of SHOULD, 20 % of all 252) are planned POST** and no MUST item is. They cannot finish by 23 Nov for stated reasons: decisions that gate work nobody will run (Step 35 code, lot-state schema; 23), human hours that do not fit (16), scope cut by the recommended decisions (4), capacity (3), human-only gates (3), paywalled sources (2). The 23 DECISION_CONDITIONAL items flip into W3 only if the humans choose option (b) of decision #3 or Q39(c), and then they break the human budget (sec 10).

## 2. Done since 8 Nov (what manjot and the Mac produced)

Times are from `git log` (IST). Items closed or advanced are in the last column.

| When | Commit | Who | What | Ledger items |
|---|---|---|---|---|
| 8 Nov 19:35-20:09 | 55d2574, 570e502, 88ef479, e137130, da263fa | manjot | Consensus plan (493 ledger rows, 0 contested), human operations pack, deployment plan; L-SRC source review of 97 scenario defaults + 149 mechanism windows (AI-opened, 0 human-verified); L-LOT lot-state layer (now SUPERSEDED by composition/); SSOT v16.0 DRAFT = v15 + PART XIV; Mac merge prompt | T9-C26-R1/R2/R4 (drafts), T0-C04-R1 and T4-C14-R3 (PARTIAL) |
| 8 Nov 21:11 | bbf5ee6 | manjot | L-NH: eight non-heat families (COOLING, SEPARATION, FERMENT_LEAVEN, PRESERVATION, MECHANICAL_CUT/MIX, RESTING, STORAGE), Layer 1 + Layer 2, full non-BBC runs: 600,148 recipes, 9,208,811 Rung A events, 3,027,750 non-heat events, 0 L1 exceptions | T4-C11-R2, T4-C12-R1, T4-C14-R1, T4-C06-R3 DONE; T4-C11-R1/R3, T4-C12-R2, T4-C14-R2 PARTIAL (BBC leg on the Mac) |
| 8 Nov 22:10 | b2ae1f2 | manjot | L-PHYS evaporation / phase-change cap: heat events with a core above 100 C 68.6 % -> 1.8 % (all dry-class); median core dose 341 -> 9.2 min; 153 tests | T4-C20-R2 DONE; T4-C07-R1 PARTIAL |
| 8 Nov 22:53-23:37 | b8d6f1c, 6485bbf, daae740, 618f424, bbff52b, 0a2295e, bdb0649 | manjot | L-ROUTER target-presence + lot-context gates (vitamin-C DIRECT 450 -> 73 on 1,000 non-BBC recipes; full non-BBC 267,933 -> 34,537), honest evidence labels, food-safety abstention, 120 tests; FINAL-GOV review applied (9 major); salt-unit bug and HIGH-only ABSENT fixed; D-078; worklog; resume anchor | T0-C06-R2/R3, T5-C05-R2 (PARTIAL) |
| 9 Nov 11:34-11:58 | 43 commits (e27ba54 ... 145fdfd) | Mac | S175 `composition/`: SR Legacy loader, ING->SR matcher + 490 curated terms, line-to-grams intervals with SSOT 235.3 q-levels, FDA pH registry (479 items), lot state with exact linear-fractional bounds, BBC line-mass census (11,934 recipes, 116,699 lines, 75.3 % with grams) and BBC lot census (15.9 % of lots with a bounded water fraction); Q41-Q44 added to the review packet | T3-C04-R1 DONE; T3-C08-R1/R2, T3-C13-R1, T3-C22-R1/R2 PARTIAL |
| 9 Nov 13:08-13:59 | a0a5b49, 0a5e272, 8577136 | manjot | Merge of the Mac's 43 commits (435 tests pass); consolidation: composition/ canonical, lotstate/ SUPERSEDED, 11 Mac tickets (A1-A11) + 11 ports; SCIFIX-PHYS: zone-resolved local doses (8-node accuracy max 0.34 %), boiling-point scope, F0 only for pressure canning, acid marinades qualitative, v16 text reworded, v03 non-BBC re-runs | T4-C07-R1, T4-C14-R3 (PARTIAL) |
| 9 Nov 14:52 | 3da963d | manjot | S178 PREREG: pre-signature AMENDMENT drafts for 07.A-R1, D5/H1/H3, 29-diag, AA pilot with option tables, exact McNemar power tables; 6 findings (sec 12) | T2-C05-R5, T6-C03-R5, T8-C06-R2, T8-C12-R1, T9-C12-R1 (drafts, BLOCKED_HUMAN); T9-C26-R5, T8-C04-R2 (PARTIAL) |
| 9 Nov 14:56 | d7cb55f | manjot | S178 ANALYSIS: EVD dataset card (17,978 ACTIVE rows, 0 human-verified), NEG-0031..0045 (83 figure checks, 0 mismatch), ING/ALIAS coverage census, 'what the corpus can say' + 3 SVG figures; 26 tests | T2-C15-R1, T3-C03-R2 DONE; T4-C04-R1, T4-C25-R1, T9-C08-R4 PARTIAL |
| 9 Nov 15:09 | 42c01bf | manjot | S178 EVAL: H1 gold-independence check (40 of 40 draft S gold are ENGINE_DRAFT, circular), independent H3 scorer, rung-blind claim-audit sheets, 25-row split registry, D5 leakage audit, exact power; 55 tests | T9-C09-R2 DONE; T9-C09-R1, T8-C16-R1, T8-C04-R2, T3-C20-R1 PARTIAL |
| 9 Nov, not committed | working tree | manjot | S177 FULLRUN (non-BBC line + lot census, 8 runs, report `S177_FULLRUN_report.md`, `reports/s177/*`); S177 SCIFIX-ROUTER (`decision/public_mode.py`, `mechanism/sr_identity.py`, edits to `evidence_gates.py`, `router_census.py`, `demo_context.py`, `app/server.py`, `app/static/index.html`, 3 new test files, `reports/step23/..._1000_S177.json`). No SCIFIX-ROUTER report exists yet | T3-C08-R2, T3-C13-R1, T8-C18-R2 (PARTIAL, evidence uncommitted) |

Not closed by any of the above (so still open): the signatures, the 07.A-R1 labels, the AA PDFs and verification, the D5 review and freeze, every H1/H3 run, the SIMULATE wiring, the report. The Mac must not merge or push until the two uncommitted S177 lanes are committed (orchestrator action, W1).

## 3. Lane split and capacity

Remaining agent-hours of the non-POST items by owner and closing wave (ledger midpoints reduced for PARTIAL; human-only rows count 0-1 agent-h):

| Owner | W1 | W2 | W3 | W4 | Total |
|---|---|---|---|---|---|
| manjot-agent | 8 | 91.8 | 133.5 | 11.5 | 244.8 |
| mac-agent | 10 | 49.6 | 45.5 | 24 | 129.2 |
| kush | 3.5 | 7.5 | 0.5 | 0 | 11.5 |
| parv | 0 | 0 | 0 | 0 | 0 |
| kush+parv | 9.4 | 1.5 | 12.2 | 0 | 23.2 |
| expert | 0 | 0 | 0.5 | 0 | 0.5 |
| **All** | 30.9 | 150.4 | 192.2 | 35.5 | 409.1 |

The agent-hours are not the constraint: each side can run several lane agents in parallel (S176 ran nine topic agents, three reviewers and eight build lanes). The constraints are (a) the human gates, (b) the shared server (at most 32 workers, `nice -n 10`, 95 % full disk, load average 67-410 on 128 cores in S176/S177), (c) one merge/push owner (the Mac) and (d) orchestrator-only files (WORKLOG, DECISIONS, STATUS, compute_runs, handoff/, SSOT), which only the orchestrator edits, so lane agents hand rows back and the orchestrator merges.

**Rules for the two sides (proposed)**

- `composition/`, `tools/s175_line_mass_census.py`, `reports/s175/*` are Mac-only. manjot reads them and sends tickets (the 11 in `handoff/MAC_TASKS_FROM_CONSOLIDATION_S177.md`). `lotstate/` is SUPERSEDED: no new feature on it.
- Anything that reads BBC text or the sealed 15a reserved list (29-diag, 07.A scoring, P1 gold, BBC censuses) runs on the Mac. Everything else, including the CPU jobs the ledger tags `vinayak`, runs on manjot to avoid the VPN dependency; only GPU/Ollama rungs (T8-C15-R1, T8-C21-R1) need vinayak.
- Report sections are drafted by the lane that owns the data; the Mac assembles, runs the leakage grep and pushes. No section is written from memory: every number cites a committed file.
- The prereg lock (Tue 10) is scribed by the Mac from manjot's S178 amendment drafts, because scribing human gates is the Mac's job; humans sign only the locked bytes.

## 4. Wave W1: Mon 9 - Thu 12 Nov (decisions, lock, signatures, AA start)

46 items close in W1 (33 MUST, 13 SHOULD); 34 are BLOCKED_HUMAN. This wave is a human wave: the agents' job is to make every human act a 5-minute act.

**Gates:** Mon 9 evening: decisions #1 (T3-C22-R7) and #2 (T2-C05-R5). Tue 10: prereg edit lock + hashes (afternoon), AA PDFs, decisions #3-#7, #20, #23, A1/A3/A6/A7. Wed 11 noon: all signatures. Thu 12: every other decision, Bagler permission copy. Slip fallbacks are the consensus sec 4.1 / ops pack sec 5.2.

| lane_group | Items | Owner | Agent h | Human h | Depends on | Acceptance |
|---|---|---|---|---|---|---|
| `decision-sitting` | T0-C01-R1, T0-C06-R1, T0-C18-R2, T2-C05-R5, T2-C11-R2, T3-C04-R3, T3-C07-R3, T3-C17-R1, T3-C22-R7, T4-C09-R1, T4-C22-R1, T5-C05-R4, T5-C07-R1, T5-C13-R3, T6-C04-R1, T7-C01-R2, T8-C02-R2, T8-C06-R2, T8-C12-R1, T8-C18-R1, T9-C07-R2, T9-C12-R1, T9-C13-R4, T9-C25-R5, T9-C26-R2 | kush+parv decide; manjot drafts (ops pack); mac-agent scribes | 11.7 | 14.3 | handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md sec 2; Kush and Parv in the same sitting (Mon 9 evening, 90 min). | Each decision is a D-079+ entry in the humans' own words (HUMAN/SIGN entries committed by the named human from his or her own session); read-back at the end; decisions #1 and #2 on Mon 9, #3-#7 + #20 + #23 + A1/A3/A6/A7 on Tue 10, the rest by Thu 12. |
| `07a-r1` | T2-C05-R1 | kush+parv | 0.2 | 0.8 | T2-C05-R5 ruling; prereg-lock. Wed 11 noon. | Both sign the locked 07A_R1 prereg before opening the packet (sha-bound signature files). |
| `aa-extract-verify` | T2-C09-R1, T2-C09-R2, T2-C09-R3 | kush (PDFs, browser on the Mac); parv (licence facts AAK-01/09/11); kush+parv (sign); mac-agent (extraction) | 4.1 | 1.4 | prereg-lock; AA signature before any PDF is opened for extraction. Tue 10 (grace Wed 11 noon). | AA prereg signed; 5 PDFs in data/raw/aa_pilot/ with licence line checked (CC BY/CC0 only, AAK-05 saved but unread); CAL rows for the new SIM-CAL papers extracted with spans and a verification packet issued for each person by Thu 12; rows from papers with an unconfirmed licence dropped and recorded. |
| `physical-layer-closeout` | T4-C11-R1, T4-C11-R3, T4-C12-R2, T4-C14-R2 | mac-agent (BBC leg, D-003) | 1.5 | 0 | Branch merged on the Mac (git merge/push is the Mac's). Est. 2-3 h wall (UNVERIFIED). | BBC non-heat L1/L2 census and heat L2 v03 re-run on the Mac with the commands in S176_L-PHYS_report sec 9; counts-only JSON + run rows; baseline PASS; nothing BBC copied to the server. |
| `router-v2` | T5-C05-R1 | mac-agent | 0.5 | 0 | Decision #20 (A: pinned installs in a Mac venv), due Tue 10. | hypothesis installed in a pinned Mac venv; >=10^4 randomised property test 'UNKNOWN/NOT_APPLICABLE never reaches SIMULATE' passes (G23.2); else the report says NOT_RUN. |
| `prereg-lock` | T6-C02-R1, T9-C12-R2, T9-C26-R5 | mac-agent (scribe: apply options, commit, hash); manjot-agent (text, T6-C02-R1, T9-C12-R2) | 7 | 0.5 | Decisions #2-#7, A1, A3 (Mon 9 / Tue 10 morning). Lock target Tue 10 afternoon; slides to Wed 11 noon if the sitting slips. | The four prereg files (07.A-R1, D5/H1/H3, 29-diag, AA) carry the chosen options; one lock note with sha256 per file and a commit hash; D4 descriptive metrics and the VPN/CPU fallback sentence are inside the lock; crosswalk csv written with no D3 -> B-2 mapping. |
| `signatures` | T6-C03-R1, T6-C03-R2, T8-C20-R1, T9-C07-R4 | kush (15A-BOOT, 29-diag, H8); kush+parv (D5/H1/H3) | 1 | 1.8 | prereg-lock; T6-C02-R1 (before the 29-diag signature). Wed 11 noon. | Signature files committed from each person's own session after the lock timestamp; `shasum` of the locked file equals the lock note; 15A-BOOT record set to FROZEN by Kush only; no ledger touched afterwards. |
| `transition-29diag` | T6-C19-R1 | mac-agent; parv authorises | 1.5 | 0.3 | Decision #20. | Lock file per host (Mac pinned versions, vinayak, manjot CPU) + smoke import + transition suite; Parv writes the authorisation in his own words. |
| `d5-benchmark` | T8-C20-R4 | manjot-agent | 1.5 | 0.5 | Decision A1; Mac regenerates the git-ignored review sheets. | 5 U + 5 X questions drafted (X includes 3 safety questions with gold REFUSE) and merged into the Mac review sheets by Thu 12; sheets re-issued with the amended S-pool/gold order (A1). |
| `governance-ledgers` | T9-C01-R3, T9-C25-R1, T9-C26-R1 | manjot-agent (orchestrator) | 2 | 0.5 | Kush's calendar (not in the repo). | STATUS.md refreshed to S178; compute plan + day-by-day schedule + human-time ledger exist (this board and the ops pack) and Kush confirms calendar/VPN on Tue 10. |

**Non-ledger gating tasks in W1** (not rows of the ledger, but the MUST items wait on them):

| # | Task | Owner | Due | Why |
|---|---|---|---|---|
| G1 | Commit the uncommitted S177 lanes (FULLRUN report + `reports/s177/*`; SCIFIX-ROUTER code, tests, `public_mode.py`, `sr_identity.py`, app edits) and write the missing SCIFIX-ROUTER report | manjot-agent (orchestrator) | Mon 9 night | Mac merge/push and FINAL-GOV findings 1-2 (demo wording, BBC-derived edges in public mode) depend on it |
| G2 | Mac: fix tickets A4, A5, A6 (U+2044, extra-large/jumbo sizes, POINT only for stated mass) test-first, then A1-A3 (pH registry), A7, A10; tell manjot when done so the non-BBC census can be re-run | mac-agent | A4-A6 by Wed 11 | Changes the S177 FULLRUN numbers (58 TASTEset lines wrong, non-conservative intervals); T3-C08-R2/T3-C13-R1 cannot close before the re-run |
| G3 | Mac: merge `max/s176-orchestration`, push, open PR; confirm `.gitignore` covers `data/derived/` and no LAN address is in `handoff/` (FINAL-GOV 3, 9 were fixed in daae740) | mac-agent | Tue 10 | One merge owner; Kush's write token |
| G4 | Correct ops-pack decision #6 text (6-0 and 7-0 are already significant at n=30; PREREG finding 6) before the sitting reads it | manjot-agent | Mon 9 before the sitting | Decisions are taken on that text |
| G5 | Apply decisions the same night: manjot drafts the DECISIONS entries; the scribe numbers them from D-079 (D-078 is used) | mac-agent scribe | Mon 9 - Thu 12 | HUMAN/SIGN entries are committed by the named human, not the scribe (REV-B B2.2) |

**Human tasks, W1 (hours in brackets)**

| Day | Kush | Parv | Gate that day |
|---|---|---|---|
| Mon 9 | Sitting (1.5); permission email to Prof. Bagler, decision #19 (0.3); ratify D-068 in own commit, A4 (0.3) = **2.1** | Sitting (1.5); own ratifications, A4 (0.5) = **2.0** | Decisions #1 and #2 due. |
| Tue 10 | After the lock note: sign AA prereg (0.3); download 5 PDFs + licence checks (1.0); ssh test to vinayak (0.25) = **1.55** | After the lock note: sign AA prereg (0.3); authorise the learning-environment lock (0.3); + licence facts of AAK-01/09/11 on the publisher pages (0.5, moved from Kush) = **1.1** | Prereg edit lock + hashes. Decisions #3-#7, #20, #23, A1, A3, A6, A7 (taken at the Mon sitting or by message). |
| Wed 11 | Sign 07A_R1 and D5 (0.8); sign 15A-BOOT, 29-diag, H8 (0.9); ask an outside reviewer (0.2); 07.A labels session 1 (2.0) = **3.9** | Sign 07A_R1 and D5 (0.8); 07.A labels session 1 (2.0) = **2.8** | Signatures complete by noon. Decisions #8, #18 (sign), A5. |
| Thu 12 | Buffer day = **0** | 07.A labels session 2 (1.5); D5 blind S answers (1.5); own 07.A/07I-C/Step 16 confirmation, T9-C13-R4 (0.5) = **3.5** | All remaining decisions (#9-#17, #19, #22) due; AA verification packets issued; U/X drafts merged. |

**Exit criteria W1:** lock note + hashes committed; 5 signatures sets committed from own sessions; all 23 consensus decisions + A1-A7 recorded (or default stated); AA CAL packet issued; S177 lanes committed. If the lock slides to Wed 11 noon, W2 loses one labelling day and the 07.A labels move to Sat 14 (07.A is the first thing cut, ops pack 1.1).

## 5. Wave W2: Fri 13 - Mon 16 Nov (labelling, verification, review, freezes)

67 items close in W2 (18 MUST, 49 SHOULD). The human work is concentrated here: 07.A labels (Fri 13), AA verification (Sat 14 - Sun 15), D5 review (to Mon 16). The agents build everything the W3 runs need.

**Gates:** Fri 13 07.A-R1 labels in (else 07.A stays FAILED on record, 23b closed); VPN confirmed (#21) or manjot-CPU fallback; Sat 14 D5 dry run on vinayak, 29-diag run twice; Sun 15 AA CAL rows dual-verified (else NEED_DATA, no PARAM, SIMULATE 'code-tested only'); Mon 16 D5 reviewed and frozen, Model A fit frozen (hard stop for the freeze Tue 17).

| lane_group | Items | Owner | Agent h | Human h | Depends on | Acceptance |
|---|---|---|---|---|---|---|
| `ssot-delta` | T0-C01-R2, T0-C19-R1 | manjot-agent | 5.5 | 0.5 | Decision #22. | One-page v15-status-block-vs-repo delta (report appendix) and the SSOT coverage map for the 87 unanchored sections. |
| `related-work` | T0-C02-R1 | manjot-agent | 8 | 1.5 | Web/OpenAlex access from manjot (else the Mac). | Targeted related-work re-search with every citation opened; table of 10-15 works. |
| `report-sections` | T0-C07-R2, T0-C11-R3, T6-C04-R3, T7-C20-R1, T9-C28-R1 | mac-agent (assembly) / data owners draft | 5 | 1.8 | T6-C03-R4 memos (Sat 14) for the H2 slide. | H1-H5 to H1-H4 map; SSOT Task <-> D5 <-> D-008 crosswalk; licence paragraph; H2 slide (after memos); 'learned rungs deferred' statement. |
| `decision-sitting` | T0-C17-R1, T9-C25-R3 | kush | 0.5 | 1 | Tue 10 ssh test. | VPN/ssh to vinayak confirmed or manjot-CPU fallback accepted (Fri 13); Bagler reply recorded or fallback wording used. |
| `evd-card-d1` | T2-C01-R1, T2-C01-R2, T2-C03-R3, T2-C13-R1, T2-C14-R1, T2-C15-R4 | manjot-agent; mac-agent (full seal check on the Mac) | 14.7 | 0.5 | d7cb55f dataset-card generator. | sec 203.2 conformance table; export v2 byte-reproducible; SVAR count reconciliation; EVD coverage vs corpus demand per process family; reproducibility record; full 15a seal check on the Mac before the 29-diag run. |
| `aa-extract-verify` | T2-C02-R1, T2-C07-R2, T2-C09-R4 | kush+parv (blind verification); mac-agent (register PDFs); manjot-agent (schema, default staged CSV) | 7.5 | 3.8 | T2-C09-R3 packet by Thu 12; Sat 14 - Sun 15 (3 h each). | Every CAL row has two blind verdicts by Sun 15 (VERIFIED / CORRECTED / REJECTED); PDFs registered through register_document; storage form decided (default staged CSV). |
| `07a-r1` | T2-C05-R2, T2-C05-R3, T2-C05-R4 | kush+parv (labels, adjudication); mac-agent (scoring) | 1.2 | 4.2 | T2-C05-R1 signatures (Wed 11 noon). | Both label files returned by Fri 13 (hash recorded before scoring); scorer run once on Sat 14 (result JSON write-once, freeze verified); joint adjudication Sun 15; statistic never recomputed. Fallback: 07.A stays FAILED on record. |
| `corpus-grounding` | T3-C03-R1, T3-C05-R1, T3-C07-R1, T3-C07-R4, T3-C12-R1, T3-C23-R1 | manjot-agent | 15.5 | 0.5 | Mac ticket A4/P1 (same fix in composition/); decision #13. | ING count reconciliation JSON; per-family verb-coverage table; U+2044/U+2215 normalisation in quantity/grammar.py with glued '11/2' still REFUSE and non-BBC grounding re-run; bare-count share; Food.com data card; replay-invariant property tests at corpus scale. |
| `lot-composition` | T3-C08-R1, T3-C08-R2, T3-C13-R1, T3-C22-R1, T3-C22-R2 | mac-agent (owns composition/); manjot-agent re-runs the 4 non-BBC census after the fixes | 13 | 0.5 | handoff/MAC_TASKS_FROM_CONSOLIDATION_S177.md; decisions #1, #14. | Mac tickets A4-A6 (+A1-A3 pH, A7, A10) fixed test-first; POR records exported; non-BBC census re-run (Food.com ~46 min line, ~2.9 h lots) and the Q-level / bounded-mass tables rebuilt; FDA pH on the L-PH registry. |
| `gold-d3` | T3-C11-R1, T3-C15-R1, T3-C17-R2 | mac-agent | 10 | 1 | BBC recipes only on the Mac; decision #11. | Rung A vs P1 gold diagnostic with Wilson intervals labelled NOT INDEPENDENT; confusion matrix; P1 closeout report with the negative gate verdict visible. |
| `physical-layer-closeout` | T4-C01-R1, T4-C02-R2, T4-C03-R1, T4-C07-R1, T4-C14-R3 | manjot-agent | 12.5 | 1 | none (all manjot paths). | PROC->family registry CSV; per-axis provenance schema doc + validator; endpoint-cue extractor + leakage test; slab verification report (FD + textbook values + N_TERMS); diffusion-range sources checked. |
| `physical-layer-reports` | T4-C05-R1 | manjot-agent | 3 | 0 | reports/step26 v03 JSONs. | Bracket-width table and robust/fragile flag per conclusion, counts-only. |
| `aa-fit-sim` | T5-C07-R2, T5-C07-R3, T5-C07-R5, T5-C10-R5, T5-C11-R4 | manjot-agent | 18.5 | 2 | T2-C09-R4 (Sun 15), decision #9 (FORM- prefix), #10. | Router SIMULATE branch wired end to end (code-tested only if no PARAM); FORM rows minted; Model A fit frozen with sha256 + code hash on Mon 16 BEFORE any SIM-VAL text is opened; PARAM minted only from rows both humans VERIFIED (0 from K0 aggregates); NEED_DATA if below the prereg minimum. |
| `transition-29diag` | T6-C01-R1, T6-C02-R2, T6-C03-R3, T6-C03-R4, T6-C03-R5, T6-C07-R1, T6-C08-R3, T6-C09-R2 | mac-agent (runs, memos); manjot-agent (property tests) | 19.8 | 1.8 | 15A-BOOT approval + 29-diag signature (Wed 11); scikit-learn in the Mac venv (decision #20). | 29-diag run twice, byte-identical outputs (G15-R); four memos with DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE labels and no 'supported', 'beats', 'validated'; D2-vs-B-2 contrast on S-3/S-4/S-6 (diagnostic only); D7a == D1 diagnosis; no-imputation property tests; canonical cell definition recounted on the frozen snapshot. |
| `step35-design` | T7-C01-R5 | manjot-agent | 0.5 | 0 | none. | Which Step 35 bound inputs are visible on manjot/vinayak (counts only). |
| `h1h3-runs` | T8-C15-R3, T8-C17-R1 | manjot-agent | 3 | 0 | Before the dry run on vinayak. | Ollama digest + prompt sha pinned in the run record; prompt_registry and claim_ledger schema committed; dry-run plan ready for Sat 14. |
| `d5-human-review` | T8-C20-R2, T9-C17-R3 | kush+parv (about 6.3 h each); an outside reviewer (named by Kush) | 2 | 7.5 | Signatures (Wed 11); U/X drafts (Thu 12). Fewer than 40 reviewed items = no H1/H3 numbers. | Blind S answers first, then KEEP/EDIT/DROP of 100 questions plus the U/X blocks, reconciled Mon 16 (a question enters only if both KEEP, or both KEEP after the same edit). Outside reviewer checks 20 items or the limitation is stated. |
| `d5-benchmark` | T8-C20-R3, T9-C09-R1 | manjot-agent | 2 | 0.3 | T8-C20-R2 (both sheets back, reconciled). | Benchmark frozen Mon 16 (sha256 + freeze check); split registry rebuilt with U/X and recorded; leakage audit re-run on the frozen set. Hard stop Tue 17. |
| `governance-ledgers` | T9-C06-R1, T9-C08-R4, T9-C11-R1, T9-C11-R2, T9-C29-R1 | manjot-agent (orchestrator); parv/kush read the NEG rows (0.5 h) | 8.2 | 1 | Orchestrator-only files. | SSOT sec 238 conformance table; G16 gate table; run-log blanks filled; experiment back-fill; NEG register read by a human and cross-referenced. |

**Milestone inside another wave's item:** T9-C20-R1 report skeleton with placeholders by Fri 13 (mac-agent; the item itself closes in W4).

**Human tasks, W2**

| Day | Kush | Parv | Gate that day |
|---|---|---|---|
| Fri 13 | 07.A labels session 2 (1.5); D5 blind S answers (1.5); confirm demo machine and slot (0.15) = **3.15** | D5 review (2.0) = **2.0** | 07.A-R1 labels due. VPN decision #21. 07.A packet hashes recorded. |
| Sat 14 | AA verification of every CAL row (3.0); D5 review (1.0) = **4.0** | AA verification of every CAL row (3.0) = **3.0** | 07.A scored (agent). 29-diag run twice, memos. D5 dry run on vinayak. |
| Sun 15 | D5 review (2.0); read the 29-diag memos (0.5); 07.A joint adjudication with Parv (0.5) = **3.0** (demo dry run, 0.35 in the ops pack, moved to Tue 17) | D5 review (1.0); read the NEG register rows, T9-C08-R4 (0.5); 07.A joint adjudication (0.5) = **2.0** | AA CAL rows dual-verified (return both files). |
| Mon 16 | D5 finish with U and X (1.0); joint reconcile (0.5); confirm benchmark freeze (0.3) = **1.8** (the Model A fit-freeze hash is read on Tue 17, not confirmed live) | D5 finish with U and X (1.0); joint reconcile (0.5); confirm benchmark freeze (0.3) = **1.8** | D5 reviewed and frozen. Model A fit frozen. PARAM minted from doubly-verified rows. |

**Exit criteria W2:** D5 frozen with sha256 (or level L2 declared); both 07.A files scored once; AA fit frozen with its hash committed before SIM-VAL is opened; 29-diag memos written; report skeleton exists; run-log rows merged.

## 6. Wave W3: Tue 17 - Fri 20 Nov (runs, results, sections)

68 items close in W3 (22 MUST, 46 SHOULD). The H1/H3 chain runs Tue 17 - Thu 19; everything that needs results waits for it; everything that does not is already done in W2.

**Gates:** Tue 17 vinayak reachable (else deterministic rungs on manjot CPU, LLM rungs NOT_RUN); Wed 18 SIM-VAL verified; Thu 19 results in (else level L3: report = router census + gate table only); Fri 20 claim audit back and slides edited (else L1 for H3).

| lane_group | Items | Owner | Agent h | Human h | Depends on | Acceptance |
|---|---|---|---|---|---|---|
| `scenario-defaults-sourcing` | T0-C04-R1 | kush+parv (1 h each, Tue 17); manjot-agent preps | 1.5 | 1 | Library access for paywalled handbooks. | The <=8 defaults shown on slides are SOURCE_VERIFIED with page+range, or stay labelled unverified. |
| `router-v2` | T0-C06-R2, T0-C06-R3, T0-C07-R1, T0-C09-R2, T5-C05-R2, T5-C05-R3, T8-C07-R1 | manjot-agent (mac-agent for the BBC leg and hypothesis) | 26 | 0.5 | T0-C06-R1 crosswalk (Wed 11); SCIFIX-ROUTER committed. | Contract audit (property tests + corpus scan: no food-chemistry number without an EVD id or frozen-model id); evidence label on every chip; golden regression of 50 recipes byte-identical; conflicting-evidence display; AI-labelled gate set with FN/FP and Wilson CIs; full non-BBC router re-run after fixes + PARAM; extra targets (stretch). |
| `aa-extract-verify` | T2-C02-R2, T2-C09-R7 | manjot-agent (orchestrator append), kush+parv none | 4.5 | 0.5 | T2-C09-R4. | Verified rows appended to NEW KIN/KINPT ledgers with hashes; the 'what the pilot is not' statement and availability table. |
| `decision-batch` | T2-C04-R1, T2-C18-R1, T5-C01-R4, T5-C02-R4, T7-C08-R1, T7-C24-R1, T9-C06-R2, T9-C07-R1, T9-C07-R5 | kush+parv (45 min Tue 17); defaults hold if skipped | 6.8 | 5.8 | Not on the critical path; moved from Fri 13 to Tue 17 to keep Kush under 20 h in 9-16 Nov. | All nine recorded as D-numbers or their stated default applied and written into the report (T2-C04-R1 raw-text axes, T2-C18-R1 no new source, T5-C01-R4 agent defaults, T5-C02-R4 demo-only, T7-C08-R1 sensory UNSUPPORTED, T7-C24-R1 L13E parked, T9-C06-R2 claim ledger runtime-only, T9-C07-R1 node-hour threshold, T9-C07-R5 repo already public). |
| `evd-card-d1` | T2-C06-R1, T2-C16-R1, T2-C21-R1, T3-C20-R1 | manjot-agent; kush (card skim 0.5 h, Tue 17); expert/Kush for the USDA-Bognar reading | 10.5 | 3 | T2-C05-R3 result (Sat 14). | Dataset card copied to reports/step15/; D1 section + figures with verified rows stated as 0/40 and the G08-3 FAIL; 15b readiness checklist with NOT_FROZEN/BLOCKED_BY list; T3 gold partition union-grouping check. |
| `report-sections` | T2-C06-R2, T6-C11-R1, T6-C20-R1, T7-C22-R1, T7-C22-R2, T7-C27-R1, T9-C07-R3, T9-C09-R3, T9-C20-R2, T9-C32-R1 | data owner drafts; mac-agent assembles | 22.5 | 5.8 | Results of 14-19 Nov as they land; sections sent to Kush/Parv as they land. | Lineage statement, D2-lite page, learning claim-boundary page, Level 12/13 decision records + slides, FlavorTwin boundary, D-071 delegation table (script from DECISIONS), source-disjoint line, architecture/provenance/router figures, number-class lint script. |
| `corpus-grounding` | T3-C09-R1 | manjot-agent; mac-agent supplies NER spans | 5 | 0 | VPN/Mac copy of vinayak NER spans (T9-C25-R3); else POST. | NER vs Rung A mention agreement (labelled DIAGNOSTIC) if the span files reach manjot; ING/ALIAS coverage already DONE (d7cb55f). |
| `physical-layer-reports` | T4-C04-R1, T4-C25-R1, T4-C26-R1 | manjot-agent (analysis), mac-agent (slides); kush review 1 h (Tue 17) | 7 | 2 | D5 freeze for the audit sample; T4-C05-R1. | Kush has reviewed the 'what the corpus can say' report; physical-layer slides/figures with section-141 wording audit, edits by Fri 20; binder precision audit n=100 AI-only (AI_CHECKED). |
| `physical-layer-closeout` | T4-C08-R1, T4-C21-R1 | manjot-agent | 11.5 | 0 | T4-C04-R1. | 26g census re-run with L1 bindings (SIMULATE 0 asserted); finite cylinder/sphere series (stretch); items already built in L-NH close with their evidence. |
| `mech-screen` | T5-C01-R1, T5-C01-R2, T5-C02-R2, T5-C02-R3 | manjot-agent (stretch lane) | 22.5 | 0 | Decision T5-C01-R4 (Fri 13 batch); composition/ API (read only). | 20-32 MECH entries authored (AI_DRAFTED, never in a claim), 32-entry subset, Kleene three-valued screen over composition/ lots, non-BBC run. First lane to be cut if H1/H3 slip. |
| `aa-fit-sim` | T5-C08-R1, T5-C10-R6, T5-C11-R3, T5-C11-R6, T5-C12-R2, T5-C21-R1, T8-C08-R1 | manjot-agent; kush+parv (SIM-VAL verification Wed 18, 2 h each) | 29 | 5.2 | Fit freeze Mon 16; decision #10 (a). | SIM-VAL rows (AAK-12/07/03/05) extracted and dual-verified Wed 18; descriptive error + interval coverage; sim_aa_1 calibrated on frozen Model A with identifiability report; SIMM-AA-1 card with validation_status NOT_VALIDATED; B6 rung RESEARCH_ONLY or NOT_RUN; G15 T5 gate scorecard with file evidence. |
| `transition-29diag` | T6-C02-R3 | mac-agent | 4 | 0 | T6-C03-R3. | Paired-CI DEL-2 re-run (cut if the memos slip). |
| `h1h3-scoring` | T8-C01-R1, T8-C03-R1, T8-C04-R2, T8-C06-R1, T8-C10-R1, T8-C13-R1, T8-C16-R1, T8-C16-R2, T8-C21-R2, T8-C22-R1, T9-C18-R1 | manjot-agent; kush+parv (30-claim blind audit, 1.25 h each, Thu 19-Fri 20) | 22.5 | 1.2 | Frozen benchmark; H1/H3 raw outputs (19 Nov); EVAL tooling (42c01bf). | H3 on frozen P/C (decision-mode F1, zero-claim denominators, exact sign test), D4 retrieval metrics, router branch accuracy with confusion matrix, slot accuracy, C-block 'cannot separate' rate, OOD abstain recall/false-abstain, enforcement cost, citation precision/recall + the human audit, engine-vs-human gold agreement; ablations if time. |
| `h1h3-runs` | T8-C15-R1, T8-C21-R1 | mac-agent (vinayak via VPN); manjot-agent runs the CPU fallback | 6.5 | 0 | Benchmark freeze (Mon 16, hard stop Tue 17); VPN (decision #21). | B0/B1/B2/B4/B5/B7/B5T on the frozen benchmark with qwen2.5:7b (temp 0, fixed seed), digest pinned, run rows logged; H1 (B0,B1,B2,B4 + B5/B7) McNemar/Newcombe computed. Dry run Sat 14. Fallback: deterministic rungs on manjot CPU, LLM rungs NOT_RUN. |
| `demo-hosting` | T8-C18-R2, T9-C22-R2 | manjot-agent (app/, public mode); mac-agent (host, scenario script) | 6.5 | 1 | Decision A6 (Tue 10); SCIFIX-ROUTER committed; D5 frozen for the X controls. | Local live demo bundle plus a static page of ~20 cached answers; BBC-derived edges filtered in public mode; evidence label on every chip; >=5 of the 8 SSOT scenarios scripted with evidence class. |
| `gold-d3` | T9-C16-R1 | mac-agent | 2.5 | 0 | T3-C11-R1; T3-C17-R2. | D3 reported as 'built + run, gold comparison limited to P1 (7 pairs, AI-drafted, human-accepted)' with intervals and replay/merge-split property tests. |
| `governance-ledgers` | T9-C24-R1 | mac-agent | 3.5 | 0.5 | Licence paragraph (T9-C28-R1). | RELEASE_CARD.md, counts only, for recipe base, EVD export, benchmark, physical layers, NER outputs. |

**Human tasks, W3** (items marked + are additions to the ops pack, see sec 8)

| Day | Kush | Parv | Gate that day |
|---|---|---|---|
| Tue 17 | + Review `corpus_can_say` report, T4-C04-R1 (1.0); + skim the EVD card, T2-C15-R1 (0.5); + check the <=8 slide defaults, T0-C04-R1 (1.0); + read the H2 slide, T6-C04-R3 (0.5); + read the Model A fit-freeze hash and report (0.25); + SHOULD decision batch (0.75); demo dry run, moved from Sun 15 (0.35) = **4.35** | + Check the <=8 slide defaults (1.0); + read the lineage statement, T2-C06-R2 (0.5); + SHOULD decision batch (0.75) = **2.25** | vinayak reachable. D5 hard stop. Agent runs begin. |
| Wed 18 | Verify SIM-VAL rows from 4 papers (2.0) = **2.0** | Same (2.0) = **2.0** | Model A already frozen. |
| Thu 19 | Blind audit of 30 claims, part 1 (0.6) = **0.6** | Same (0.6) = **0.6** | H1/H3 results in. Claim-audit sheets issued. |
| Fri 20 | Claim audit part 2 (0.65); edit physical-layer slides (1.0); optional cloudflared install (0.1) = **1.75** | Claim audit part 2 (0.65); edit physical-layer slides (1.0) = **1.65** | Slides edited by Fri 20. |

**Exit criteria W3:** every number the talk will use exists in a committed JSON; H1, H3, D4, router accuracy, OOD, SIMULATE pilot (or NEED_DATA) all reported with intervals; G15 T5 scorecard; D1, D3, physical, lineage, licence sections drafted. Nothing new starts after Fri 20 except the report.

## 7. Wave W4: Sat 21 - Mon 23 Nov (freeze and polish)

10 items close in W4 (7 MUST, 3 SHOULD). The wave has few agent items on purpose.

**Gates:** Sat 21 **code and result freeze**, full report draft, leakage grep; Sun 22 - Mon 23 human edit; Mon 23 'cannot claim' sheet delivered; Tue 24 timed rehearsal (outside the 23 Nov line).

| lane_group | Items | Owner | Agent h | Human h | Depends on | Acceptance |
|---|---|---|---|---|---|---|
| `report-sections` | T8-C19-R1, T9-C23-R2 | manjot-agent drafts; mac-agent assembles | 4.5 | 1 | H1/H3 results (19 Nov). | D4 section from the frozen-benchmark results (silver study labelled); MPU table re-scored with true H1/H3 numbers. |
| `report-assembly` | T9-C20-R1 | mac-agent (assembles, commits); data owners supply tables | 18.5 | 5 | All W3 outputs; freeze Sat 21. | Skeleton with placeholders by Fri 13; tables filled from committed JSON as results land; full draft Sat 21; human edit Sun 22 - Mon 23 (~5 h each); number-class check passes; every number cites a file. |
| `human-report-edit` | T9-C20-R3 | kush+parv | 0 | 1 | Report draft (Sat 21). | Contributions section corrected; presentation day and slot confirmed. |
| `demo-hosting` | T9-C21-R2 | mac-agent; kush records 0.35 h Mon 23 | 1.5 | 0.3 | Code freeze Sat 21. | Screen recording of the 4 demo queries and offline fallback page. |
| `governance-ledgers` | T9-C24-R2, T9-C25-R4, T9-C28-R2, T9-C30-R1 | manjot-agent; mac-agent (leakage grep) | 9.5 | 0.2 | Report draft; H1/H3 outputs. | 3 run ids reproduced on manjot with matching sha256; every run logged; slides/report/screenshots grepped against git-ignored text hashes (Sat 21); DoD scorecard MET/PARTIAL/NOT_MET with paths. |
| `qa-rehearsal` | T9-C26-R3 | mac-agent drafts; kush+parv rehearse (Tue 24) | 1.5 | 1.8 | Report draft. | 'We cannot claim' sheet refreshed with real numbers by Mon 23; timed rehearsal incl. live-demo fallback on Tue 24 (outside the 23 Nov line). |

**Human tasks, W4**

| Day | Kush | Parv | Gate that day |
|---|---|---|---|
| Sat 21 | Optional: choose the static-page host (0.25) = **0.25** | Nothing = **0** | Code and result freeze. |
| Sun 22 | Edit report and deck (3.0) = **3.0** | Same (3.0) = **3.0** | Report draft delivered. |
| Mon 23 | Edit (2.0); contributions section (1.0); number-class exceptions list (0.5); read the Q&A sheet (0.25); record the 4 demo queries (0.35) = **4.1** | Edit (2.0); contributions section (1.0); number-class exceptions (0.5); Q&A sheet (0.25) = **3.75** | 'Cannot claim' sheet delivered. |
| Tue 24 | Timed rehearsal with the live-demo fallback (2.0) = **2.0** | Same (2.0) = **2.0** | Rehearsal (outside the 23 Nov line). |

**Flag (W4 overload):** the ledger asks the two authors to read about 12 h of report sections in 'the 22-23 Nov edit' (D1 1.5, D4 1, Level 12/13 records and slides 3, related work 1.5, learning pages 1.25, H1-H5 map, D-071 table, licence paragraph, lineage, number-class lint 0.5 each or less), against the 5 h each the ops pack plans for Sun-Mon. Lever: sections go to the humans as they land in W3 (15 min each, Thu/Fri), and the four lowest-value SHOULD sections (T7-C22-R2, T7-C27-R1, T6-C20-R1, T0-C02-R1) drop to an appendix if the freeze day is tight.

## 8. Human load, 9-23 Nov, and where it overloads

| Window | Kush (h) | Parv (h) | Ops pack plan (K / P) | Comment |
|---|---|---|---|---|
| 9-16 Nov (W1+W2) | **19.5** | **18.2** | 19.9 / 17.2 | Inside the 16-20 h budget, but Kush has 0.5 h of slack. Differences from the pack: Parv takes the AAK-01/09/11 licence facts (+0.5 Parv), Parv's own 07.A/07I-C confirmation T9-C13-R4 (+0.5 Parv), the 9-item SHOULD decision batch moves from the sitting week to Tue 17 (0 here), the demo dry run moves to Tue 17 (-0.35 Kush), the Model A fit-freeze is read Tue 17 not confirmed live (0) |
| 17-20 Nov (W3) | 8.7 | 6.5 | 4.4 / 4.3 | Additions the pack does not schedule: Tue 17 reviews (Kush 3.0, Parv 1.5: T4-C04-R1, T2-C15-R1, T0-C04-R1, T6-C04-R3, T2-C06-R2), the SHOULD decision batch (0.75 each), the fit-freeze read (0.25 Kush) and the demo dry run moved from Sun 15 (0.35 Kush) |
| 21-23 Nov (W4) | 7.4 | 6.8 | 7.4 / 6.8 | Same as the pack; add ~1 h each for section reading unless sections are sent in W3 (flagged in sec 7) |
| 9-23 Nov total | about 35.6 | about 31.5 | 31.6 / 28.2 | Tue 24 rehearsal (2.0 each) is on top |

**Overload flags.** (1) Kush's heavy days are Wed 11 (3.9 h: three signature sets plus 2 h of blind labels) and Sat 14 (4.0 h); Thu 12 is an empty buffer on purpose and is the only place a slip can land. (2) Any change that adds to 9-16 Nov puts Kush over 20 h: the larger D5 S pool (A1 option B, +1.5 h each, Kush 21.0 h), a human item promoted from POST, a re-labelled 07.A packet. (3) W3 is heavier in this board than in the pack by about 4 h (Kush) and 2 h (Parv) because the board adds reviews the ledger requires (T4-C04-R1 review, T0-C04-R1 verification, the SHOULD decision batch); they are not on a gate and can be cut to defaults. (4) W4: see the section-reading flag in sec 7.

**Levers if a person is over 20 h in 9-16 Nov** (in this order; none touches a MUST gate): (1) cut 07.A-R1 first, as the ops pack says (-3.5 each; 07.A stays FAILED on record); (2) 07.A late return to Fri 20 (REV-B) instead of Fri 13 (moves 3.5 h each out of the week); (3) never cut the D5 review or the AA verification. The ledger sum of MUST human hours is 26-35 h per person (T9-C26-R4); the decision sitting is what brings it to 16-20 h, so the 90-minute sitting is the single most important meeting of the two weeks.

## 9. Compute plan (T9-C25-R1, draft)

Run times are from the lane reports (measured at load average 67-410, UNVERIFIED for the next runs). Every run follows the rules: seed 20261104, 1,000-recipe sample first, `nice -n 10`, at most 32 workers, counts-only outputs, sha256, one row in `registry/compute_runs_v1.csv` merged by the orchestrator. Disk: 532 GB free on manjot at S177; each lane stays under 15 GB and removes scratch.

| Host | Run | When | Est. wall | Items |
|---|---|---|---|---|
| Mac | BBC non-heat L1/L2 census; BBC heat L2 v03 re-run (commands in `S176_L-PHYS_report.md` sec 9) | Tue 10 - Wed 11 | 1-3 h | T4-C11-R1/R3, T4-C12-R2, T4-C14-R2 |
| Mac | BBC line + lot census re-run after tickets A4-A6 | Wed 11 - Thu 12 | about 1 h (UNVERIFIED) | T3-C08-R2, T3-C13-R1 |
| Mac | 29-diag twice (CPU minutes); 07.A-R1 scoring; AA extraction; seal check | Sat 14 | < 1 h | T6-C03-R3, T2-C05-R3, T2-C09-R3, T2-C14-R1 |
| Mac | BBC router census with gates (BBC leg) | Thu 19 | about 1-2 h | T5-C05-R2 |
| manjot | Non-BBC line census re-run (Food.com about 46 min, lots about 2.9 h single process); small families minutes | Thu 12 - Fri 13 | about 4 h total, 1 process each | T3-C08-R2, T3-C13-R1 |
| manjot | Quantity-grammar fix re-run on non-BBC grounding (rc2 took 50 min on 4 workers) | Fri 13 - Sat 14 | about 1-2 h | T3-C07-R1 |
| manjot | Retrieval metrics, router accuracy, OOD, slot accuracy, H3 analysis, claim audit merge, deterministic rungs B0/B1/B2/B4/B5T (fallback) | Tue 17 - Thu 19 | minutes to 1 h each | T8-C06-R1, T8-C01-R1, T8-C13-R1, T8-C03-R1, T8-C22-R1, T8-C16-R1 |
| manjot | 26g census re-run with L1 bindings (full corpus 14.6 M engine events; sample first) | Tue 17 - Wed 18 | several h (UNVERIFIED) | T4-C21-R1 |
| manjot | Router census non-BBC full re-run after fixes + PARAM; mechanism screen non-BBC run; simulability census with calibrated sim_aa_1 | Wed 18 - Fri 20 | 1-3 h each | T5-C05-R2, T5-C02-R3, T5-C11-R6 |
| vinayak (via Mac) | D5 dry run; B0/B1/B2/B4/B5/B7/B5T on the frozen benchmark with qwen2.5:7b (GPU 1 only); H1 McNemar/Newcombe | Sat 14 (dry); Tue 17 - Thu 19 | a few GPU-hours (UNVERIFIED) | T8-C15-R1, T8-C21-R1 |

VPN risk is the one external dependency: confirm ssh Tue 10 (Kush) and again Fri 13 (decision #21). If it is down, only the LLM rungs are lost; the deterministic rungs, all scoring and all analysis run on manjot CPU.

## 10. Items that cannot finish by 23 Nov (POST), and why

51 items, all SHOULD. Agent-hours avoided: 240.2; human hours avoided: 100.5 (ledger basis, per person where 'each').

**DECISION_CONDITIONAL (23)**: Decision-conditional: the recommended option means nobody will run the work (flips to W3 only if the humans choose the other option, and then breaks the hours budget).

| Item | What | Why it cannot finish |
|---|---|---|
| T2-C03-R1 | Decide the physical/history SVAR v1.1 set and definitions (shared with the lot-state topic) | SVAR v1.1 is shared with lot-state (Q39 lean: defer) and any SVAR.jsonl append after 15A-BOOT approval voids the freeze. Default holds; parked after 26 Nov. |
| T3-C01-R1 | Fold SP-001 and SP-004 plus lot-state fields into STATE/ENTITY v1.1 drafts under new ids (R-18: new versions ... | STATE/ENTITY v1.1 only matters for the lot-state slice and the 16c freeze (both deferred under Q39 lean). |
| T3-C12-R3 | Add §233.2 belief fields (timestamp, provenance class, unknown flag) to replay output records per lot-step | belief fields belong to the lot-step record (Q39 lean: defer event-level lots, Mac P8). |
| T3-C21-R1 | Draft SVAR v1.1 physical/history registry (definitions, units, allowed types, UNKNOWN semantics) as additive ... | additive SVAR v1.1 registry only serves the deferred lot-state work; REV-A E.6 list stays parked. |
| T3-C25-R1 | Write a short design note fixing belief fields and class tags (source/semantic/episode/evidence/model) for ... | belief-field design note only matters if lot-step records are built (deferred). |
| T4-C05-R3 | Q1 circularity control: basis masks on every Layer 2 feature plus an ablation that removes Layer 2 before any ... | no Layer 2 feature enters learning before 25 Nov (Step 31 is AFTER; decision #16 lean (a)). |
| T7-C01-R1 | Kush and Parv each sign the v2 package (Route B on the Mac: regenerate template, confirm sha256 009c9047..., ... | only if decision #3 = (b). Lean (a): Step 35 DESIGNED, NOT RUN (no v2 signature). |
| T7-C01-R3 | Kush answers the open D35 checklist items not covered by Parv: D35-1 (sign THR rows), -2 (rdkit as project ... | D35 checklist only if (b). |
| T7-C01-R4 | After signature, copy THR-35P-01..43 into registry/preregistered_thresholds_v1.csv (Step 01.6) and freeze ... | orchestrator copy of THR-35P rows after a signature that is not planned. |
| T7-C02-R1 | Write molecule split auditor: InChIKey full + 14-char connectivity overlap check, tau881 cluster splits with ... | molecule split auditor has no consumer under (a). ~100 agent-h of Step 35 code (C02-R1, C03-R1, C05-R1/R3, C06-R1, C12-R2, C14-R1, C16-R2, C19-R1, C23-R1) would compete with H1/H3. |
| T7-C02-R3 | Run splits on real data and write sha256 manifests (registry/splits/step35_split_hash_manifest_v1.json, ... | Step 35 DESIGNED, NOT RUN under the recommended decision #3 (a); same reason as T7-C02-R1; revisit only if the humans choose (b). |
| T7-C03-R1 | Write 35a scoring (no-rdkit arm): CACTVS-881 decode unit test (222 hex = 881 bits MSB-first + 7 pad), E0 ... | Step 35 DESIGNED, NOT RUN under the recommended decision #3 (a); same reason as T7-C02-R1; revisit only if the humans choose (b). |
| T7-C04-R1 | Kush confirms (or reverses) the RDKit dependency decision D35-2 and the Open Babel stance D35-3. | RDKit / Open Babel stance (D35-2/3); default holds. |
| T7-C05-R1 | Write x_ij builder producing ingredient_profile_xij_v1 and ingredient_profile_coverage_v1 (git-ignored ... | Step 35 DESIGNED, NOT RUN under the recommended decision #3 (a); same reason as T7-C02-R1; revisit only if the humans choose (b). |
| T7-C05-R3 | BAN-35-1 enforcement: static check that no arm, comparator or tie-breaker reads KGE ING_CO_OCCURS or any ... | Step 35 DESIGNED, NOT RUN under the recommended decision #3 (a); same reason as T7-C02-R1; revisit only if the humans choose (b). |
| T7-C06-R1 | Implement ingredient E0/E1 metrics, null percentile with B >= max(1000, ceil(20m/q)) (THR-35P-37), ... | Step 35 DESIGNED, NOT RUN under the recommended decision #3 (a); same reason as T7-C02-R1; revisit only if the humans choose (b). |
| T7-C12-R2 | Build 35c task harness: masked-ingredient recovery (Recall@K, MRR, nDCG), partial-recipe completion, ... | Step 35 DESIGNED, NOT RUN under the recommended decision #3 (a); same reason as T7-C02-R1; revisit only if the humans choose (b). |
| T7-C12-R3 | After signature only: run R0/R2 descriptive and primary PE-35c on real recipes incl. link-coverage floor ... | Step 35 DESIGNED, NOT RUN under the recommended decision #3 (a); same reason as T7-C02-R1; revisit only if the humans choose (b). |
| T7-C14-R1 | Implement remaining cuisine pieces: Curveball-calibrated Z / MX null path, E (era/source) null, macro-F1 ... | Step 35 DESIGNED, NOT RUN under the recommended decision #3 (a); same reason as T7-C02-R1; revisit only if the humans choose (b). |
| T7-C16-R1 | Kush decides sim_id scheme and status mapping (D35-12), SIM-13 home (D35-11), and which statuses count as ... | sim_id scheme (D35-12). |
| T7-C16-R2 | Generate registry/similarity_registry_v2.csv and registry/representation_registry_v1.csv from the 21 v1 rows ... | Step 35 DESIGNED, NOT RUN under the recommended decision #3 (a); same reason as T7-C02-R1; revisit only if the humans choose (b). |
| T7-C19-R1 | Build one audit module producing G35-0/COV/CIRC/NULL/SEP verdict JSON per run with negative results kept ... | Step 35 DESIGNED, NOT RUN under the recommended decision #3 (a); same reason as T7-C02-R1; revisit only if the humans choose (b). |
| T7-C23-R1 | Create representation registry files and the output manifest writer (dataset/preprocessing/split versions, ... | output manifest writer has no Step 35 run to serve. |

**HUMAN_HOURS (16)**: Human hours that do not fit the 16-20 h per person budget.

| Item | What | Why it cannot finish |
|---|---|---|
| T2-C08-R3 | Pre-register the Step 10/11 accuracy gate (precision/recall LB thresholds, human-first fallback) before any ... | a second signature set (0.5-1 h each) for an extraction gate that is not used before 25 Nov. |
| T2-C10-R1 | Strip the AI suggestion columns and have Kush verify the 40 MAIN rows against the cited papers (Parv audits a ... | Kush 6-12 h + Parv 3-6 h cannot fit the 16-20 h/person budget. D1 hand-verified rows stay 0/40 and the report says so. |
| T2-C17-R1 | Kush resolves the 129 HELD and 23 CONCEPT_MISSING ingredient links (HV-008) | 129 HELD + 23 CONCEPT_MISSING links (2-4 h). Stays open; report states it. |
| T3-C01-R2 | Step 16c freeze: Kush and Parv review contract v1, vocabulary hierarchy, handbook v2, hard-case keys and sign | 16c freeze review 4-8 h each is not schedulable before 25 Nov. |
| T3-C03-R3 | Human review queue for the top-frequency unmapped / polysemous ingredients (top ~300 covering ~80 % of ... | 6-10 h of human review. Agent builds the mention-weighted queue (Mac P9) in W2 so it is ready. |
| T3-C04-R2 | Human verification of matches for the top ingredients by corpus frequency | 4-8 h verification of top ING->SR matches. 60 % of BBC grams still rest on unverified links (S175). |
| T3-C09-R4 | Small human-labelled Food.com line sample (200-300 lines) to measure NER and Rung A accuracy under no-unit ... | 200-300 hand-labelled Food.com lines (3-5 h each). |
| T3-C11-R2 | Per-rule precision audit on a seeded sample for the 5 highest-volume rules (COMBINE_WITH_CURRENT, ... | per-rule precision audit needs 4-6 h of labelling. |
| T3-C20-R2 | 07I-C family threshold calibration on a human-labelled pair sample | 07I-C threshold calibration needs 3-5 h of pair labelling; threshold stays provisional and is stated. |
| T4-C01-R2 | Human review of the 27 process_medium_map rows and PROC mechanism_families for the physical families ... | 2-3 h review of 27 process_medium_map rows; rows stay AI_DRAFTED. |
| T5-C01-R3 | Blind dual review of every entry (Kush, Parv) plus adjudication log with technical independence safeguards ... | blind dual review 6-10 h each; entries stay AI_DRAFTED and are never in a claim. |
| T5-C01-R6 | PROC->MECH crosswalk for 156 PROC (HV-010): AI-draft all, humans verify the PROC used by the AA pilot and ... | PROC->MECH crosswalk verification 3-6 h (Parv). Agent drafts only; humans verify the AA pilot PROC set if time. |
| T5-C13-R2 | Write and co-sign Step 27 pre-registration before opening SIM-VAL rows; run single confirmatory analysis; ... | co-signed Step 27 pre-registration (3-5 h each plus audit) is not schedulable; SIM-VAL is descriptive only. |
| T7-C03-R3 | Chemistry-aware reviewer approves taste-label normalisation map (THR-35P-04) and the scored-class support ... | chemistry expert (4-6 h) not named; Step 35 not run. |
| T7-C05-R2 | Parv audits the 50 ING<->FlavorGraph crosswalks / profile joins (D35-7). | Parv audit of 50 ING-FlavorGraph crosswalks. |
| T7-C13-R1 | Parv writes his own 07I-C confirmation; Kush/Parv label or adjudicate any remaining calibration pairs; record ... | Parv's own 07I-C confirmation plus pair labelling (2-3 h + 1 h). T9-C13-R4 (0.5 h) is the cheap part and stays scheduled. |

**SCOPE_CUT (4)**: Cut by the recommended decisions (descriptive validation, G26 formal gates, Step 27).

| Item | What | Why it cannot finish |
|---|---|---|
| T2-C03-R2 | Append additive SVAR v1.1 rows (physical/history) via orchestrator, before the 15a freeze is approved or as ... | appending to SVAR.jsonl after Kush approves the 15A-BOOT freeze voids it (SNAPSHOT_HASH_MISMATCH); do as 15a.1 after the talk. |
| T5-C11-R1 | Pre-register G26-VER/G26-CAL numbers and the exact no-water-assay design (O6); sign (separate files). | formal G26 prereg replaced by descriptive validation if decision #10 = (a); sim_aa_1 stays NOT_VALIDATED / RESEARCH_ONLY. |
| T5-C12-R1 | Run the pre-registered G26-VER suite and the >=200-dataset recovery grid; write verification_report_v1.md ... | formal G26-VER suite needs the unsigned G26 prereg. Replaced by the identifiability report (T5-C12-R2). |
| T5-C13-R1 | Implement baselines (S27-B1 persistence/mean-retention, S27-B3) and negative controls NC-1..4 and cluster ... | Step 27 baselines/negative controls/sign-flip inference belong to the formal Step 27 that decision #10 (a) replaces by a descriptive report. |

**CAPACITY (3)**: Agent capacity with no consumer before 25 Nov.

| Item | What | Why it cannot finish |
|---|---|---|
| T2-C08-R1 | Build golden fixtures (synthetic tables with seeded fabricated values, unit/basis traps, censoring footnotes, ... | no new extraction beyond the AA pilot before 25 Nov; ~12 agent-h with no consumer. Stretch only if an agent is idle in W3. |
| T3-C24-R1 | Extract the Q and V cases into a machine-readable fixture file (text only from SSOT; no third-party text) and ... | Q/V conformance fixture (8-14 agent-h) has no consumer in the 25 Nov deliverables. |
| T6-C08-R1 | Build propensity model with available covariates (food frequency in recipe corpus as popularity proxy, ... | propensity sensitivity has no consumer in the 25 Nov report; the MNAR claim boundary (T6-C08-R3) carries the message. |

**HUMAN_GATE (3)**: Human-only gate nobody has scheduled (P1b nonce, 15b freeze).

| Item | What | Why it cannot finish |
|---|---|---|
| T3-C14-R1 | Frame update for P1b: exclude all 21 P1 manifest rows and groups; wave-scoped files and --wave P1b support in ... | P1b needs Kush's nonce and a signed amendment; ops pack recommends skip. |
| T3-C16-R1 | Kush supplies size (3 or 4), writes the new nonce, signs the start-record amendment for P1b | Kush-only nonce; ops pack sec 4.6 recommends skip (decision #11 = no D3 accuracy claim). |
| T5-C06-R2 | If 07.A PASS and 15b frozen: run 23b on real COND rows and report. | needs 07.A PASS and a frozen 15b; 15b stays NOT_FROZEN (40-row verification is POST, T2-C10-R1). |

**LICENCE (2)**: Paywalled or institutional-access source the agent may not and cannot open.

| Item | What | Why it cannot finish |
|---|---|---|
| T2-C10-R2 | Library/proxy access for the 110 non-OA Phenol-Explorer papers (human permission or institutional login) | 110 non-OA Phenol-Explorer papers need institutional access (human) and have no use without T2-C10-R1. |
| T4-C10-R1 | Verify Choi-Okos coefficients against the 1986 paper or Rahman handbook, record page cites | Choi-Okos 1986 / Rahman handbook are paywalled; agent cannot open them. Coefficients stay SOURCE_UNVERIFIED and the slide says so. Same library ask as T2-C10-R2. |

**Missing data (BLOCKED_DATA, 2):** T3-C09-R1 (NER span files exist only on vinayak and Gutenberg spans were never persisted; closes in W3 only if the VPN works or the Mac copies them) and T4-C10-R1 (Choi-Okos 1986 / Rahman handbook are paywalled; POST). A third data risk is a MUST chain: the AA fit needs about 20 doubly-verified CAL rows with at least 3 temperatures in at least 2 SIM-CAL matrices; today there are 16 rows from 4 papers, 3 of which are `AUTHOR_FIT_EA`, and papers AAK-01 and AAK-11 have an UNKNOWN licence (rows are dropped if it is not CC BY/CC0). Below the prereg minimum Model A is NEED_DATA and the SIMULATE result does not exist (T5-C10-R5, T5-C07-R3, T5-C12-R2, T5-C10-R6, T5-C11-R3, T5-C21-R1, T8-C08-R1, T5-C11-R6).

**Things this board will not promise:** a verified-literature D1 (T2-C10-R1, 0 of 40 rows stay hand-verified); a validated or calibrated model (the label stays NOT_VALIDATED / RESEARCH_ONLY); any claim from Step 35; a Prof. Bagler reply (T9-C07-R2 closes with fallback wording if none arrives); 07.A PASS (it may fail again by the kappa paradox, which the prereg accepts in advance, or the labels may not come back, in which case 07.A stays FAILED on record).

## 11. Burndown

Projected counts at the **end** of each wave. 'Closed' = DONE now + items whose closing wave is that wave or earlier. It assumes every human gate lands on its date; sec 11.2 shows what happens when one does not. 'Not closed' items are shown by their status today.

**All 252 items**

| Point in time | Closed (DONE) | Not closed: PARTIAL | OPEN | BLOCKED_HUMAN | BLOCKED_DATA | POST | Total |
|---|---|---|---|---|---|---|---|
| Today, Mon 9 (status_now) | 10 | 42 | 108 | 90 | 2 | - | 252 |
| End of W1 (Thu 12) | 56 | 34 | 79 | 31 | 1 | 51 | 252 |
| End of W2 (Mon 16) | 123 | 15 | 47 | 15 | 1 | 51 | 252 |
| End of W3 (Fri 20) | 191 | 3 | 6 | 1 | 0 | 51 | 252 |
| End of W4 (Mon 23) | 201 | 0 | 0 | 0 | 0 | 51 | 252 |

**MUST (84)**

| Point in time | Closed (DONE) | Not closed: PARTIAL | OPEN | BLOCKED_HUMAN | BLOCKED_DATA | POST | Total |
|---|---|---|---|---|---|---|---|
| Today, Mon 9 (status_now) | 4 | 15 | 23 | 42 | 0 | - | 84 |
| End of W1 (Thu 12) | 37 | 11 | 21 | 15 | 0 | 0 | 84 |
| End of W2 (Mon 16) | 55 | 8 | 17 | 4 | 0 | 0 | 84 |
| End of W3 (Fri 20) | 77 | 3 | 3 | 1 | 0 | 0 | 84 |
| End of W4 (Mon 23) | 84 | 0 | 0 | 0 | 0 | 0 | 84 |

**SHOULD (168)**

| Point in time | Closed (DONE) | Not closed: PARTIAL | OPEN | BLOCKED_HUMAN | BLOCKED_DATA | POST | Total |
|---|---|---|---|---|---|---|---|
| Today, Mon 9 (status_now) | 6 | 27 | 85 | 48 | 2 | - | 168 |
| End of W1 (Thu 12) | 19 | 23 | 58 | 16 | 1 | 51 | 168 |
| End of W2 (Mon 16) | 68 | 7 | 30 | 11 | 1 | 51 | 168 |
| End of W3 (Fri 20) | 114 | 0 | 3 | 0 | 0 | 51 | 168 |
| End of W4 (Mon 23) | 117 | 0 | 0 | 0 | 0 | 51 | 168 |

Reading the last row: at the end of Mon 23, 201 of 252 items are closed (MUST 84 of 84, SHOULD 117 of 168) and the 51 POST items are the only ones left. T9-C26-R3 (rehearsal) is counted closed on 23 Nov although the rehearsal itself is Tue 24.

### 11.1 Per-wave closing counts

| Wave | Items closing | MUST | SHOULD | manjot-agent | mac-agent | kush / parv / kush+parv / expert | Agent h | Human h (ledger basis) |
|---|---|---|---|---|---|---|---|---|
| W0 | 10 | 4 | 6 | 9 | 1 | 0 | 0 | 0 |
| W1 | 46 | 33 | 13 | 6 | 8 | 32 | 31 | 20 |
| W2 | 67 | 18 | 49 | 36 | 23 | 8 | 150.4 | 28.9 |
| W3 | 68 | 22 | 46 | 38 | 17 | 13 | 192.2 | 26.5 |
| W4 | 10 | 7 | 3 | 4 | 5 | 1 | 35.5 | 9.3 |
| POST | 51 | 0 | 51 | 20 | 5 | 26 | 240.2 | 100.5 |

### 11.2 What flips if a gate slips (non-POST items downstream of each gate, from `depends_on`)

| Gate (date) | MUST items at risk | SHOULD items at risk | Fallback (consensus 4.1 / ops pack 5.2) |
|---|---|---|---|
| D5 frozen (T8-C20-R3) | 12 | 8 | Level L2: benchmark frozen or drafted but NOT run; H1/H3 NOT_RUN; SIM-VAL drops to SHOULD. Hard stop Tue 17; fewer than 40 reviewed items means no H1/H3 numbers. |
| AA verified rows (T2-C09-R4) | 7 | 7 | No PARAM, no SIMULATE result; wiring shipped code-tested only; Model A NEED_DATA below the prereg minimum. |
| 07.A-R1 labels (T2-C05-R2) | 2 | 1 | 07.A stays FAILED on record, 23b stays closed; changes nothing the talk shows. |
| 29-diag signature (T6-C03-R2) | 4 | 4 | Drop the 29-diag; keep the DEL-2 D7 = D1 suspicion on the failure slide as not run. |
| 15A-BOOT approval (T6-C03-R1) | 4 | 5 | 29-diag and the cell-definition recount cannot run; same fallback as above. |

The closure is computed over the dependencies recorded in the CSV (ledger text plus the board's additions); it undercounts where the ledger names no item id.

## 12. Findings for the orchestrator (inconsistencies and corrections found while building the board)

- **Ledger status is per component, not per item.** 19 MUST/SHOULD rows carry the component status `DONE` (for example the T9-C07 rows) and 38 carry `RUN` although the item itself is open or partial. The board's `status_now` is item-level; `ledger_component_status` keeps the original.
- **29-diag ladder.** `transition/baselines.D3Hierarchical` never reads matrix or food group, so the ledger row T6-C02-R1 ('B-2 = D3 matrix arm') and the contrast in T6-C03-R5 ('D3 ingredient mean') point at nothing; `transition/splits.all_splits` has no food-group split although the prereg names S-5 (PREREG findings 1-2). Option K-A adds about 20 lines for a real B-2 mean; the contrast is lopsided by construction and only S-6 compares on equal terms (finding 3). Write the crosswalk after decision #7 and do not map D3 to B-2.
- **`tools/step07_agreement.py` overwrites the retained v3 result path** (`reports/step07/step07h_human_gate_result.json`). If the sitting picks the kappa route, scoring must be a mode of `condition_agreement.score` (PREREG finding 4). T2-C05-R3 names `tools/step07ar_agreement.py`; check that tool's output path before Sat 14.
- **The D5 amendment draft does not contain the D4 descriptive metrics** (T9-C12-R2: condition-compatible Recall@K, risk-coverage of B7 abstention). They must be added inside the Tue 10 lock or cannot be pre-registered; the board puts T9-C12-R2 in W1.
- **D5 S block is 38 of 40 Gutenberg segments and 2 Wikibooks, 40 of 40 gold are ENGINE_DRAFT** (EVAL): H1 can only be stated for that text type and only as self-consistency unless the humans answer blind first (A1 option G-A). P/C: all 101 gold EVD rows sit in the DEL-2/29-diag pool, so no DEL-2 or 29-diag number may be offered as validation of those cells.
- **Two ledger rows would void the 15A-BOOT freeze if done as written:** T2-C03-R2 (append SVAR v1.1 to `SVAR.jsonl`) and T2-C11-R2 option 'ingest R2 + Bognar before the freeze'. The board sets T2-C03-R2 POST and T2-C11-R2 default 'defer to 15a.1'.
- **Ledger `where` vs the owner split.** Differences followed here: T0-C06-R3, T9-C12-R2, T9-C18-R1 (ledger: Mac; `app/` and `evaluation/` are manjot's), the CPU jobs tagged `vinayak` (T4-C03-R1, T4-C21-R1, T5-C02-R3, T5-C05-R2, T5-C11-R6; run on manjot CPU), and T9-C26-R5 (ledger: manjot + Kush; the Mac scribes the lock). Only T8-C15-R1 and T8-C21-R1 truly need vinayak.
- **Acceptance paths differ from where the work landed:** T2-C15-R1 asks for `reports/step15/dataset_card_15a_v1.*`, the card is in `reports/s178/analysis/` (copy it); T9-C08-R4 asks for NEG-0032+, the register ends at NEG-0030 so rows start at NEG-0031 (ANALYSIS); T3-C15-R1 names `reports/step19/pilot_iaa_report.md`, which is not in the tree.
- **Mac tickets change published numbers.** A4 (U+2044), A5 (size words), A6 (POINT only for stated mass) alter the S177 FULLRUN counts and the BBC line census; the NEG-0044 figures and any slide number from them must be re-derived after the Mac fixes (T3-C08-R2, T3-C13-R1).
- **Compute log.** `registry/compute_runs_v1.csv` holds 46 RUN-S176 and 8 RUN-S177/S178 rows; the FULLRUN (8 runs), ANALYSIS and PREREG runs have rows in their reports that are not all merged, and RUN-S176-NH-006 has blank start/end (T9-C11-R2, T9-C25-R4).
- **Ops pack decision #6** states the smallest significant results at n = 30 as 8-0, 9-1, 10-2; exact McNemar already gives significance at 6-0 (p 0.031) and 7-0 (PREREG finding 6). Fix before the sitting.
- **Presentation date.** The consensus plan says the talk is 25-26 Nov; STATUS says the dates were never independently verified; T9-C20-R3 confirms them only on Mon 23, which is too late for the slot, the projector and the rehearsal. Ask Kush to confirm day, slot and talk length on Tue 10 together with the calendar (decision #23)

## 13. Sources and limits

Status calls rest on repo paths, commits and the lane reports named in each CSV `evidence` cell. I did not run any test or tool for this board (read-only), so the test counts above are the lane reports' claims (435 pass at the S177 merge; EVAL 55 new; ANALYSIS 26 new). I did not open REV-A/REV-B in full; their add-on decisions A1-A7 enter through the ops pack. Hours are estimates; no wall-clock was measured for runs not yet made. Nothing here is a human decision, signature, freeze approval or nonce.

