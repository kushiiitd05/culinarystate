# RESUME ANCHOR — server orchestrator, 2026-11-09 (S177–S178 rounds)

**Where:** manjot-server, worktree `~/kush_work/culinarystate/.orch`, branch `max/s176-orchestration`.
It contains GitHub `kush/s169-seal-p1b` @ `145fdfd`, i.e. the Mac's S175/S176 merged at `a0a5b49`, plus 15 server commits.
Not pushed: GitHub is public-read only from here.

**Delivery:** bundle `~/kush_work/culinarystate_s176_orchestration.bundle`, covering `github/kush/s169-seal-p1b..max/s176-orchestration` and verified, plus `handoff/MAC_CLAUDE_MERGE_PROMPT_2026-11-09.md`.

**Rules:**
- `~/kush_work/culinarystate` itself is the Mac's rsync target: never write there.
- Python: `.venv312` (no torch/lxml/sklearn/requests/hypothesis).
- Everything below is AI_DRAFTED. Nothing is signed or approved (D-071).
- Previous anchor: `RESUME_ANCHOR_2026-11-08_ORCH.md` (S175).

**Plan of record:**
- `registry/execution_board_S178.csv` and `reports/orchestration/S178_EXECUTION_BOARD.md`: all 84 MUST and 168 SHOULD items, waves W1 9–12 Nov, W2 13–16, W3 17–20, W4 21–23. Code/result freeze 21 Nov, rehearsal 24 Nov.
- Only the orchestrator edits the board CSV.

## Committed in S177–S178 (server, after the merge `a0a5b49`)
| Commit | Lane | Key result |
|---|---|---|
| `0a5e272` | CONSOLIDATION | Mac `composition/` is canonical; server `lotstate/` SUPERSEDED; FDA pH (L-PH) canonical; Mac tickets A1–A11 in `handoff/MAC_TASKS_FROM_CONSOLIDATION_S177.md` |
| `8577136` | SCIFIX-PHYS | FINAL-SCI physics rows 2–5, 9: zone-resolved doses (8 Gauss–Legendre nodes), boiling-point scope, F0 only for low-acid pressure canning, acid marinades qualitative; v03 non-BBC re-runs |
| `3da963d` | PREREG | Pre-signature AMENDMENT drafts (07.A-R1, D5/H1/H3, 29-diag, AA pilot) with option tables; exact power tables (originals untouched) |
| `d7cb55f` | ANALYSIS | EVD dataset card; NEG-0031..0045; ING/ALIAS coverage; "what the corpus can say" tables and figures |
| `42c01bf` | EVAL | H1 gold-independence check (40/40 S gold are ENGINE_DRAFT, so circular); independent H3 scorer; claim audit; split registry; D5 leakage audit; exact McNemar power |
| `7f586e4` | FULLRUN | Non-BBC composition census with the Mac tool, unmodified; bugs F1–F5 sent to the Mac list |
| `4a95380` | BOARD | Two-week MUST+SHOULD board (252 items) |
| `487b870` | RELWORK | 2023–2026 related work; calibrated novelty statement; 67-work bibliography |
| `b2ba3c0` | SCIFIX-ROUTER | Prior-process lot context; full ABSENT rule (ABSENT ING 185 → 52); SR identity adapter over the Mac registry; public mode `CS_DEMO_PUBLIC`; non-BBC vitamin-C DIRECT 267,933 → 40,308 (11,861 PRIOR_PROCESS withheld) |
| `4b8e5fc` | EVD | §203 conformance; export reproducibility (glibc log last-digit finding); SVAR 355 lines = 224 ids; coverage statement; D5 U/X drafts in `reports/s178/evd/`; 29-diag MNAR text |
| `e358307` | GOVDOC | STATUS refresh; remaining-compute ledger; §238 conformance; G16 gate table (0/14 pass); SSOT v15 status vs repo; coverage map; ladder crosswalk; prompt registry; D4 amendment draft |
| `2d45f68` | CORPUS | Opt-in SP-002 pre-normaliser; Food.com pairing-rule proposal; ING count reconcile; verb coverage; replay invariants over 14.2 M events; Food.com data card |
| `28321b4` | AASIM | AA FORM draft rows (no parameter values); kinetic-unit draft rows; SIMULATE branch wired behind a refusing guard. Finding F1: a validation pass threshold is needed, otherwise the answer stays QUALITATIVE |
| `e60b581` | INGCAT | Category proposals for the 1,417 uncategorised ACTIVE ING (193 HIGH / 914 MEDIUM / 310 LOW) plus a top-100 confirmation sheet; not consumed by any code |
| `32415c4` | PHYS2 | PROC→family registry (156 PROCs); 100% per-axis provenance; endpoint cues (30.3% of heat events); verification pack 15/15; sensitivity ("core reaches 70 C" fragile for 56.5%); Layer 1 temperature ownership (events lifted above 150 C: 197 → 21); v04 non-BBC re-runs (Layer 1 0.2.0, Layer 2 0.4.0) |

**Full suite at `32415c4`:** 4,485 passed. The 6 failures and the errors are the pre-existing environment ones (missing modules) and Mac-only data, the same as on the base. Protected ledgers are untouched.

## In flight at this anchor (round S178c, launched 18:52 IST)
- **Reviews of the round** (`a0a5b49..32415c4`):
  - GOV (Sonnet) → `reports/orchestration/review/S178_REV_GOV.md`
  - SCI-A physics (Opus) → `S178_REV_SCI-A.md`
  - SCI-B router/eval/corpus (Opus) → `S178_REV_SCI-B.md`
  - Then fixer lanes apply the BLOCKER/MAJOR findings.
- **Board delta:** proposal in the scratchpad (`board_delta_S178b.csv`). The orchestrator applies it to `registry/execution_board_S178.csv`.
- **Build lanes:**
  - MECH: mechanism entries and the Kleene screen, T5-C01-R1/R2, T5-C02-R2/R3.
  - H1H3H: D5/H1/H3/D4 scoring harness on synthetic fixtures only, with a frozen-input guard; never run on the D5 questions before the freeze.
  - PHYS3: cylinder/sphere series, 26g census with Layer 1 bindings, sourced diffusion ranges.
- If the session dies before these finish, re-launch them with the briefs in the session scratchpad: `orch_ctx.md`, `review_S178_brief.md`, `board_update_brief.md`, `lanes_S178c.md`. Their content is summarised here; the scratchpad is not in the repo.

## Next — agent (after round c)
1. Apply the review fixes. Commit each lane by explicit path, with a privacy grep before every commit.
2. Apply the board delta. Re-plan W2/W3.
3. **ROUTER-V2 lane:**
   - targets beyond vitamin C for DIRECT/INTERPOLATE (T5-C05-R3);
   - conflicting-evidence packets (T8-C07-R1);
   - contract audit (T0-C06-R2);
   - 50-recipe end-to-end regression (T0-C09-R2);
   - ~100-query annotated gate set (T0-C07-R1);
   - demo chips (T0-C06-R3).
4. **W3:**
   - report sections: D1 (T2-C21-R1), G15 T5 scorecard (T5-C21-R1), 15b readiness (T2-C16-R1), DoD scorecard (T9-C30-R1);
   - binder precision audit n=100, AI_CHECKED (T4-C26-R1);
   - H1/H3 real runs only after the D5 freeze.

## Next — Mac Claude
See `handoff/MAC_CLAUDE_MERGE_PROMPT_2026-11-09.md`:
- fast-forward to the bundle;
- BBC re-runs: Layer 1 0.2.0 + Layer 2 0.4.0 heat, non-heat v04, router census;
- `composition/` tickets A1–A11 and F1–F5;
- push, then a PR to `main` (ask Kush before merging).

## Next — humans
See `handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md`:
- Decision sitting: lot-state scope; 07.A statistic; SR_PORTION; Food.com no-unit policy; mode→§141 crosswalk; presence floor and margin; physics class list. Also the new questions below.
- Signatures, 07.A labels, AA verification and 5 PDFs, D5 review, SSOT v16 approval.

New questions from this round:
- AA validation pass threshold (AASIM F1).
- Confirm the ING category top-100 sheet (INGCAT) and the ABSENT top-50 review.
- Stated-liquid residual (PHYS2 §2.4). Agent lean: keep as is.
- PROC count: 93 vs 156 (PHYS2 §13.1).
- Endpoint-lexicon scope (PHYS2 §13.4).
- One memory-class list for the report.
- E1: human audit of 100 gate decisions.
