# CulinaryState finish plan to the presentation (25–26 Nov 2026)

Set 2026-11-07 (S170) from D-075 and D-076. Supersedes the "Order for next session" lists in
`RESUME_ANCHOR_2026-11-03.md` (those items are folded in below). **Update the Status column every session.**
Step numbers are the 36-step plan (`docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`).

## Where the project stands (honest, 2026-11-07)

About 35–40 % of the 36-step plan. Done or run on the full corpus: Steps 01–07 (07.A FAILED, on record), 08a
(G08-3 FAILED), 15a.R seal, 16–18 (schema draft, Rung A extraction, event replay: 14.6 M events), 19 P1 pilot, 26g
census. Code only, never run on real data: 21–26 (mechanisms, router, formulas, simulators), 29–35 scaffolds.
Not started: 09–11 verified kinetics (0 PARAM rows: the root blocker of the physics chain), 20, D2, D4, D5, H1–H4.

## Progress snapshot (see `PROGRESS_AUDIT_2026-11-07.md`)

| Lens | 7 Nov | If M1–M6 land |
|---|---|---|
| 36-step plan | ≈ 35 % | ≈ 43 % |
| Proposal deliverables (D1–D5) | ≈ 25 %, H1–H4 untested | ≈ 60 %, H1 + H3 tested |
| SSOT §14 minimum publishable unit | ≈ 20 % | ≈ 65 % |

## Milestones

| # | Milestone | Plan steps | Owner | Target | Status |
|---|---|---|---|---|---|
| M0 | Anchor carry-over: census 0.2.0 full run, seal check, D-073 precision check, report refresh | 26g, 15a.R, 17 | agent | 7 Nov | ✅ DONE (S170) |
| M1 | Router demo mode on real recipes: 23a NON_CITABLE mode + G0 evidence pre-check from the 17,978 EVD rows (DIRECT / INTERPOLATE / ASK / UNKNOWN per event) | 23 | agent | 10 Nov | ✅ DONE (S171): demo + census on 1,000 recipes |
| M2 | 07.A redo: pre-registered statistic robust to the kappa paradox (e.g. Gwet AC1) + fresh 100-condition packet → Kush and Parv label independently (~3–4 h each) → score; a pass is the valid 07.A (23b also needs 15b frozen, R-05) | 07.A, 23b | agent packet; **Kush + Parv labels** | packet 9 Nov; labels 13 Nov | ⏳ packet + prereg + scorer READY (S171); **waiting: both sign prereg, then label** |
| M3 | Step 10 ascorbic-acid kinetics pilot: OA source list, AI extraction of ~20 rows with spans → **Kush + Parv verify** (~2–3 h each) → PARAM rows → fit sim_aa_1 on the calibration split → held-out check (Step 27) | 10, 24–27 | agent extract/fit; **Kush + Parv verify** | extract 12 Nov; verify 15 Nov; sim 17 Nov | ☐ TODO |
| M4 | D4 evidence-aware retrieval with abstention (router + EVD + retriever + claim enforcement) | 36 (D4) | agent | 14 Nov | ⏳ core DONE (S171): §39 router + front door + TRANSFORMATION/RELATIONSHIP handlers on real data; METADATA/SEMANTIC abstain |
| M5 | D5 benchmark (~80 questions, AI draft → **Kush + Parv review**) + B0–B5 runs → **H1** (state-aware vs text RAG) and **H3** (abstention lowers unsupported claims) | 36 (D5) | agent; **humans review questions** | questions 13 Nov; review 16 Nov; results 19 Nov | ⏳ prereg + 100 drafted questions READY (S171); **waiting: both sign prereg, review sheets** |
| M6 | Hosted web demo: recipe → state timeline → router decision → cited answer or abstention (FastAPI + UI on a free host; hosted LLM API key from Kush) | demo | agent; **Kush: host account + API key** | 21 Nov | ⏳ local app DONE (S173, stdlib server, no LLM key needed); hosting left |
| M7 | P1b pilot wave (needs the nonce) and Step 35 v2 signature | 19, 35 | **Kush** first, then agent | when supplied | ⏸ WAITING ON KUSH |
| M9 | Physical-state dataset (D-077): C binding (Layer 1 TEXT_STATED) → Layer 2 SCENARIO (cited defaults, ranged) → physics drivers θ(t); NER over the corpus; all runs in `registry/compute_runs_v1.csv` | 26g, 31, 35 | agent (servers + Mac) | L1 full run when VPN is up; L2/θ 18 Nov | ⏳ L1 binder + census DONE on 1,000 (S172) |
| M8 | Final report + slides from real M1–M6 results (deck started, paused at the cover) | — | agent draft; humans edit block Q | 22–24 Nov | ⏸ PAUSED |

## Human inputs needed (the critical path)

1. VPN up for vinayak / manjot (full runs, GPU, manjot pipeline review).
2. M2: Kush and Parv sign `reports/step07/07A_R1_preregistration_DRAFT.md`, then label
   `annotation/condition_audit/condition_audit_packet_100_R1_{Kush,Parv}.csv` independently (~3–4 h each) by 13 Nov.
3. M3 verification: Kush and Parv, ~2–3 h each, by 15 Nov.
4. M5: sign `reports/del5/d5_benchmark_preregistration_DRAFT.md`; review `annotation/d5_review/d5_review_v1_{Kush,Parv}.csv` (100 rows, KEEP/EDIT/DROP) independently by 16 Nov.
5. M6: a hosting account and an LLM API key (or approve the A100 + tunnel route).
6. M7: P1b nonce; Step 35 signature.

## Progress log

- 2026-11-08 S173: **M6 local demo** (`python -m culinarystate.app.server`): cited answers, per-step router chips and
  heat strip, refusals; phone layout checked. **Bug found via the demo and fixed test-first:** the template answer
  cited boil/stew rows as steaming evidence without saying so (verbalize@0.2 now names other-process rows). The
  October silver-ladder B5T results used @0.1. M9: BBC (11,934) + Wikibooks (3,676) L1/L2 done on the Mac;
  servers unreachable (VPN route missing), Food.com waits for vinayak.
- 2026-11-08 S172: **M9 started (D-077).** Verdict doc `PROJECT_FLOW_VERDICT_2026-11-08.md`. Layer 1 binder
  (`simulation/condition_binding.py`, no Rung A change) + census: 1,000 recipes → 2,850 heat events; duration 27 %,
  bath T 18 % (definition 310, text 107, carried setpoint 99), medium 56 %, matrix class 33 %, lid 9 %, size 8 %;
  both time and T for 3.3 % (4.8 % with ranges): recipes rarely state both, which is why Layer 2 exists. Bug found
  and fixed test-first (ING food group is `category`). VPN dropped mid-session: full run pending.
- 2026-11-08 S171: **M5 drafts.** D5/H1/H3 prereg (McNemar for H1 B4 vs B1/B2; question-bootstrap UCR test for H3);
  100 AI-drafted questions (P1/P2/P3/C 15 each from EVD strata; S1/S2 20 each from Wikibooks/Gutenberg with Rung A
  gold), ranked overdraft so drops don't shrink blocks. Review sheets for Kush and Parv (git-ignored).
- 2026-11-08 S171: **M4 core.** `decision/query_router.py` (SSOT §39), `front_door.py` (explicit abstention),
  `demo_context.py` (load once; DEL-5 pipeline + B5T template + router demo per recipe step; corpus substitution
  patterns labelled as patterns). Real-ledger test passes (38 s load). Router accuracy is unmeasured: it is scored on
  the M5 questions, never tuned on them.
- 2026-11-08 S171: **M1 full corpus** (vinayak, 32 workers, ~25 min): 612,782 recipes, 36,359,902 checks, DIRECT
  274,058 (0.754 %), 0 exceptions, baseline PASS; 172,350 recipes have at least one DIRECT check; 103/115 EVD vit-C pairs
  used, among 130,886 distinct pairs.
- 2026-11-08 S171: **M1 done.** Router demo census, 1,000 seeded recipes, vitamin C: 60,882 route checks, DIRECT 421
  (0.69 %), UNKNOWN 60,461, exceptions 0, baseline PASS. EVD has 115 vitamin-C (ingredient, process) pairs over 25
  ingredients; the sample used 53 of them, but those are 53 of its 13,652 distinct pairs (0.39 %). Every UNKNOWN names
  NO_FORM / PARAM_UNCONFIRMABLE / NO_CANDIDATE_MECHANISM: M3 is what moves it.
- 2026-11-08 S171: **M2 agent part done.** 07.A-R1 pre-registration (Gwet AC1 ≥ 0.80 pooled + critical-field rule;
  kappa diagnostic only), fresh packet of 100 conditions disjoint from v1–v4 (same strata, same frozen normalizer,
  v4 rows reproduce 100/100), scorer + CLI. Waiting on both signatures, then labels.
- 2026-11-08 S171: manjot-server reviewed (read-only): stale 26 Oct snapshot, 0 server-only files; M4 reuses the local
  retrieval stack (EVD texts, 6 encoder embeddings, BM25, bge rerankers). Continuing M1 census.
- 2026-11-07 S170: M1 core landed (`mechanism/router_demo.py`, 6 tests): real recipe events through the unchanged 23a engine, EVD G0 pre-check, DIRECT / UNKNOWN with reasons. Next in M1: CLI + full-corpus route census + EVD ingredient/process coverage. Progress audit written.
- 2026-11-07 S170: M0 done (census 0.2.0 full run committed; D-074 R1 rejected 4/60; report refreshed). D-075 / D-076 recorded. M1 started. VPN dropped mid-session (manjot review pending).
