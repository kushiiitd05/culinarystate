# RESUME ANCHOR — server orchestrator, 2026-11-09 ~21:00 IST (FINAL for 9 Nov; anchor dropped by Kush)

**Where:** manjot-server, worktree `~/kush_work/culinarystate/.orch`.
- **Branch `max/s176-orchestration`:** reviewed, tested, committed work. Its base is GitHub `kush/s169-seal-p1b` @ `145fdfd`, with the Mac's S175/S176 merged at `a0a5b49`.
- **Branch `max/s178-wip`:** a snapshot on top of it. It holds the unfinished fixer lanes and the finished-but-uncommitted MECH lane: UNREVIEWED, own tests green.
- **Delivery:** both branches are in `~/kush_work/culinarystate_s176_orchestration.bundle`, with `handoff/MAC_CLAUDE_MERGE_PROMPT_2026-11-09.md`.

**Status of the content:** everything is AI_DRAFTED; nothing is signed or approved (D-071). Lane briefs, cleaned of local paths, are in `handoff/orch_briefs_S178/`.

**Plan of record:** `registry/execution_board_S178.csv`, all 84 MUST and 168 SHOULD items, waves W1 9–12 Nov, W2 13–16, W3 17–20, W4 21–23. Freeze 21 Nov, rehearsal 24 Nov. Only the orchestrator edits the board.

## 1. Done on 9 Nov (committed on `max/s176-orchestration`)
| Commit | Lane | Result |
|---|---|---|
| `a0a5b49` | merge | Mac S175/S176 `composition/` (lot composition, FDA pH, BBC censuses) merged; 435 tests passing |
| `0a5e272` | CONSOLIDATION | Mac `composition/` canonical; server `lotstate/` SUPERSEDED; Mac tickets A1–A11 |
| `8577136` | SCIFIX-PHYS | Zone-resolved doses; boiling-point scope; F0 only for low-acid pressure canning; acid marinades qualitative; v03 re-runs |
| `3da963d` | PREREG | Pre-signature amendment drafts (07.A-R1, D5/H1/H3, 29-diag, AA) + exact power tables |
| `d7cb55f` | ANALYSIS | EVD dataset card; NEG rows; "what the corpus can say" tables and figures |
| `42c01bf` | EVAL | H1 circularity check (40/40 S gold are ENGINE_DRAFT); independent H3 scorer; split registry; D5 leakage audit |
| `7f586e4` | FULLRUN | Non-BBC composition census at full scale; Mac bugs F1–F5 |
| `4a95380` | BOARD | Two-week execution board, 252 items |
| `487b870` | RELWORK | 67-work related-work review; calibrated novelty statement |
| `b2ba3c0` | SCIFIX-ROUTER | Prior-process lot context; full ABSENT rule; SR identity adapter; public mode; non-BBC vitamin-C DIRECT 40,308 of 267,933 |
| `4b8e5fc` | EVD | §203 conformance; export reproducibility; SVAR 355 lines = 224 ids; D5 U/X drafts |
| `e358307` | GOVDOC | STATUS refresh; compute ledger; G16 table (0/14 gates pass); SSOT coverage map; ladder crosswalk; prompt registry |
| `2d45f68` | CORPUS | Opt-in SP-002 pre-normaliser; Food.com pairing rule; replay invariants over 14.2 M events; Food.com data card |
| `28321b4` | AASIM | AA FORM draft rows; SIMULATE branch behind a refusing guard |
| `e60b581` | INGCAT | Category proposals for 1,417 uncategorised ING + top-100 sheet (`human_decision` empty) |
| `32415c4` | PHYS2 | PROC→family registry (156); 100% per-axis provenance; endpoint cues; verification 15/15; sensitivity; Layer 1 0.2.0 / Layer 2 0.4.0; v04 non-BBC re-runs |
| `9f4cebb`, `fc4c004`, `3a71056` | REVIEWS | GOV 0 BLOCKER / 6 MAJOR; SCI-A 0 / 7; SCI-B 1 / 6. Orchestrator fixes: 34 run rows, errata, NEG-0046, board delta |
| `aea05bb` | H1H3H | D5/H1/H3/D4 scoring harness + frozen-input guard; synthetic fixture only |
| `fd93300` | PHYS3 | Cylinder/sphere/Heisler series 15/15 (not wired); shape map; 26g census on 1,000 sample (SIMULATE 0); 45 sourced diffusion rows |
| `35b9220`, `9961580` | FIX-GOV | SCI-B B1 blocker fixed (EVD card 0.2.0 + `reports/step15/` copies); superseded-input guard + 53-row registry; local server refuses tunnelled requests; transition firewall; NEG-0047..0049; deployment plan starts in `--public` |

**Board now (252 items):** DONE 34, PARTIAL 34, OPEN 73, BLOCKED_HUMAN 109, BLOCKED_DATA 2.
- MUST: DONE 4, PARTIAL 12, OPEN 16, BLOCKED_HUMAN 52.
- Most open MUST items end in a human act.

**Tests:**
- Full suite at `32415c4`: 4,485 passed. The 6 failures and the errors were the same on the base (missing lxml/requests/hypothesis/sklearn, Mac-only data).
- Lane suites at each commit: green. Protected ledgers byte-identical (GOV review).

## 2. Unfinished — on branch `max/s178-wip` (the session restarted twice; these agents stopped mid-lane)
| Lane | Done in code (own tests) | Left |
|---|---|---|
| FIX-PHYS (SCI-A M1–M7, m1–m11 + SCI-B R1) | Layer 1 0.3.0, Layer 2 0.5.0, non-heat Layer 1 0.3.0 / Layer 2 0.5.0. Food-target / setter / clause-window fixes; stricter cap lift (owned temperature + solute/syrup/pressure cue; never inside moist pieces); G7 = UNKNOWN on ASSUMED_DEFAULT inputs; public mode drops the 39 BBC-derived durations; verification v05. **86 tests pass.** | v05 re-runs: sample, then full non-BBC; schema validator; v04→v05 comparison; sensitivity / endpoint / stated-liquid reports; superseded rows; lane report `S178_FIX-PHYS_report.md` |
| FIX-ROUTER (SCI-B R2–R7, CORP-2/3) | Prior process from participles and ingredient lines; serving-suggestion gate; ABSENT only with analytical SR zeros; fail-closed ancestors; class fixes; neutral top-100 sheet; census 0.4.0; 1,000-sample census `reports/step23/router_demo_census_vitc_nonBBC_1000_S178.json`. **68 tests pass.** | Full non-BBC census 0.4.0; before/after counts; superseded rows; lane report |
| FIX-EVAL (SCI-B E1–E8, P1, P2, CORP-4/5/6, B5) | Fixes + `_v2` outputs; the 07.A-R1 amendment now recommends the non-loosening option (P1). **71 tests pass.** | Replay-invariants re-run (killed at 21:00, ABORTED); regenerate 2 committed outputs that now fail: `test_s178_d5_fixture_run` (fixture output) and `test_s178_prompt_registry` (PR-H1-CONTEXT hash); lane report |
| MECH (T5-C01-R1/R2, T5-C02-R2/R3) | **Finished:** 32 MECH draft entries (all UNSOURCED); strong-Kleene screen per layer; GUTENBERG/WIKIBOOKS/TASTESET full runs on v04; report `S178_MECH_report.md`. **46 tests pass.** | Commit together with FIX-ROUTER (it needs the analytical-zero ABSENT rule); FOODCOM run and re-run on v05 (commands in report §6) |

Touched existing suites on the WIP state: 843 passed, 2 failed (the two regenerations above).

## 3. Next — whoever resumes (Mac Claude or the next manjot session)
1. **Check out the WIP state and review it.** Finish the three fixer lanes per their briefs (`handoff/orch_briefs_S178/fixer_*.md`), using the review files `reports/orchestration/review/S178_REV_{GOV,SCI-A,SCI-B}.md`.
   - Commit each lane separately: FIX-PHYS; FIX-ROUTER + MECH together; FIX-EVAL incl. the shared `S178_EVD_report.md` correction sections.
   - Re-run the full suite.
2. **Heavy runs.** The v05 physical re-runs and the full router census 0.4.0 need the non-BBC corpus. Food.com (522,517 recipes) is on manjot. Run them on manjot, or on the Mac if the data is there.
   - BBC legs on the Mac only (D-003): v05 heat + non-heat, router 0.4.0.
   - Then the full 26g census and the FOODCOM mechanism screen on v05.
3. **A short re-review of the fixes**, one GOV + one SCI pass (Sonnet, Opus only for physics).
4. **W2/W3 agent work after that:**
   - ROUTER-V2: targets beyond vitamin C (T5-C05-R3); conflicting evidence (T8-C07-R1); contract audit (T0-C06-R2); 50-recipe regression (T0-C09-R2); ~100-query gate set (T0-C07-R1); demo chips (T0-C06-R3).
   - Report sections: D1 (T2-C21-R1); G15 T5 scorecard (T5-C21-R1); 15b readiness (T2-C16-R1); DoD scorecard (T9-C30-R1).
   - Binder audit, n=100 AI_CHECKED (T4-C26-R1).
   - H1/H3 real runs only after the D5 freeze.

## 4. Humans (Kush, Parv) — see `handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md`
**From the plan:**
- Decision sitting (lot-state scope; 07.A statistic; SR_PORTION; Food.com no-unit policy; mode→§141 crosswalk; presence floor/margin; physics class list).
- Signatures; 07.A labels; AA verification + 5 PDFs; D5 review (16 Nov) incl. the missing gold columns `gold_branch` / `gold_compare` / `gold_origin`.
- Benchmark freeze record (both humans, after final code edits; format in `evaluation/frozen_guard.py`).
- SSOT v16 approval.

**New on 9 Nov:**
- AA validation pass threshold (AASIM F1).
- ING top-100 confirmation; ABSENT top-50 review.
- Stated-liquid lift rule: FIX-PHYS applied the stricter one as PROPOSED.
- May a scenario default ever feed SIMULATE? FIX-PHYS: no, as PROPOSED.
- Sensitivity caveat.
- Shapes into Layer 2?
- Diffusion merge rows + human check.
- PROC 93 vs 156.
- Endpoint lexicon scope.
- MECH H1–H7: presence floor; Maillard at non-heat events; boiling-point rule; who opens sources for G21.4; taxon lists; oxygen default; `INFERRED_LLM` label.
- 07.A-R1: Option A loosens the signed R-06 and is only Kush's explicit choice.
- Per-person hour budgets in the public repo OK?
- Food.com counts on slides before the licence review?
- Public talk route (tunnel only in `--public`).
