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
| M1 | Router demo mode on real recipes: 23a NON_CITABLE mode + G0 evidence pre-check from the 17,978 EVD rows (DIRECT / INTERPOLATE / ASK / UNKNOWN per event) | 23 | agent | 10 Nov | ⏳ IN PROGRESS |
| M2 | 07.A redo: pre-registered statistic robust to the kappa paradox (e.g. Gwet AC1) + fresh 100-condition packet → Kush and Parv label independently (~3–4 h each) → score; pass opens 23b | 07.A, 23b | agent packet; **Kush + Parv labels** | packet 9 Nov; labels 13 Nov | ☐ TODO |
| M3 | Step 10 ascorbic-acid kinetics pilot: OA source list, AI extraction of ~20 rows with spans → **Kush + Parv verify** (~2–3 h each) → PARAM rows → fit sim_aa_1 on the calibration split → held-out check (Step 27) | 10, 24–27 | agent extract/fit; **Kush + Parv verify** | extract 12 Nov; verify 15 Nov; sim 17 Nov | ☐ TODO |
| M4 | D4 evidence-aware retrieval with abstention (router + EVD + retriever + claim enforcement) | 36 (D4) | agent | 14 Nov | ☐ TODO |
| M5 | D5 benchmark (~80 questions, AI draft → **Kush + Parv review**) + B0–B5 runs → **H1** (state-aware vs text RAG) and **H3** (abstention lowers unsupported claims) | 36 (D5) | agent; **humans review questions** | questions 13 Nov; review 16 Nov; results 19 Nov | ☐ TODO |
| M6 | Hosted web demo: recipe → state timeline → router decision → cited answer or abstention (FastAPI + UI on a free host; hosted LLM API key from Kush) | demo | agent; **Kush: host account + API key** | 21 Nov | ☐ TODO |
| M7 | P1b pilot wave (needs the nonce) and Step 35 v2 signature | 19, 35 | **Kush** first, then agent | when supplied | ⏸ WAITING ON KUSH |
| M8 | Final report + slides from real M1–M6 results (deck started, paused at the cover) | — | agent draft; humans edit block Q | 22–24 Nov | ⏸ PAUSED |

## Human inputs needed (the critical path)

1. VPN up for vinayak / manjot (full runs, GPU, manjot pipeline review).
2. M2 labels: Kush and Parv, independently, ~3–4 h each, by 13 Nov.
3. M3 verification: Kush and Parv, ~2–3 h each, by 15 Nov.
4. M5 question review: by 16 Nov.
5. M6: a hosting account and an LLM API key (or approve the A100 + tunnel route).
6. M7: P1b nonce; Step 35 signature.

## Progress log

- 2026-11-07 S170: M1 core landed (`mechanism/router_demo.py`, 6 tests): real recipe events through the unchanged 23a engine, EVD G0 pre-check, DIRECT / UNKNOWN with reasons. Next in M1: CLI + full-corpus route census + EVD ingredient/process coverage. Progress audit written.
- 2026-11-07 S170: M0 done (census 0.2.0 full run committed; D-074 R1 rejected 4/60; report refreshed). D-075 / D-076 recorded. M1 started. VPN dropped mid-session (manjot review pending).
