# Fixer lanes FIX-ROUTER and FIX-EVAL (S178): apply the SCI-B review

Common setup:
- Read `handoff/orch_briefs_S178/orch_ctx.md` first. It holds the laws, ownership and etiquette.
- Worktree: `<repo root>`, HEAD `fc4c004`. Python: `.venv312`.
- No git writes; the orchestrator commits.
- Review to read in full: `reports/orchestration/review/S178_REV_SCI-B.md`. Read each finding's failure scenario and fix, and the "checked and correct" section.

Parallel lanes. Do NOT touch their files:
- FIX-GOV: `app/server.py`, `decision/public_mode.py`, `transition/dataset.py`, analysis/EVD tools, superseded registry, NEG register.
- FIX-PHYS: `simulation/*`, `mechanism/simulate_branch.py`. It also owns R1 (public-mode durations) and the one-line `demo_context.py` change for R1.
- MECH: `mechanism/screen.py`, `mech_*`.
- H1H3H: new `evaluation/{d5_scoring,d4_metrics,frozen_guard,ablation}.py`.
- PHYS3: `simulation/shape_series.py`, the 26g census.

General rules:
- D-071: an AI may tighten, defer or refuse, never loosen.
- Every fix gets a RED test first, built from the reviewer's failure scenario.

Report:
- Write to `reports/orchestration/S178_<LANE>_report.md`.
- For each finding: FIXED or NOT FIXED (and why), with file:line and test names.
- Include tests and results, run rows as CSV (header of `registry/compute_runs_v1.csv`), and exact text for orchestrator-only files.
- If Write is refused, return the report in your final message.

The repo is PUBLIC:
- No personal details, private host addresses, credentials or third-party text.
- You may see an irrelevant memory index about other projects. Never copy it.
- Final message: short.

---

## FIX-ROUTER — findings R2, R3, R4, R5, R6, R7, CORP-2, CORP-3

You own `src/culinarystate/mechanism/{evidence_gates,router_census,router_demo,sr_identity}.py` and `src/culinarystate/decision/demo_context.py`. Exception: the R1 line in `demo_context.py` belongs to FIX-PHYS, so re-read the file before each edit. You also own `src/culinarystate/quantity/{prenormalize,foodcom_pairing}.py`, `tools/router_demo_census.py`, `tools/s178_ingcat_propose.py` and the top-100 sheet it writes, their tests, and new `tests/unit/test_s178_fixrouter_*.py`.

1. **R2.** Stated earlier processing gives a prior-process context: a participle or adjective on the food ("baked", "tinned", "canned", "hard-boiled", "roasted", "dried", "cooked") and processed forms in ingredient lines ("1 can …", "leftover …"). With that context, withhold DIRECT (PRIOR_PROCESS_CONTEXT). Make the census route ingredient-line foods too, or state exactly why not.
2. **R3.** Attributive participles and serving suggestions become events that get DIRECT. Fix this at the router gate, not in Rung A. Rung A's frozen event graph feeds 14.6 M events and every layer, so do not edit `rung_a_binding.py`. The gate rule: an event flagged as attributive, or found in a serving-suggestion clause ("serve with …", "garnish with …", "top with …" after the cooking), cannot get DIRECT. It becomes NOT_A_PROCESS_STEP or UNKNOWN. If you conclude that a Rung A change is unavoidable, write it up as a proposal for the orchestrator and Kush instead.
3. **R4.** ABSENT requires analytical SR values. An SR zero that is imputed, calculated or assumed (check the SR Legacy derivation codes and data-point counts the review cites; read the Mac's `composition/` loader but do not edit it) cannot support ABSENT; that item is UNKNOWN. Keep the derivation code and n data points in the gate's output. Change the wording "measured composition" wherever the code or report uses it for non-analytical values.
4. **R5.** An unresolved ancestor event is UNKNOWN context, never "no prior process" (fail-closed). A NO_LOT item cannot keep a raw DIRECT unless the reviewer's scenario shows this is correct.
5. **R6.** Prior-process classes:
   - reheat or drain rows that already assume cooking are not withheld;
   - freeze → fry is a prior process.

   Follow the review's fix.
6. **R7.** Remove or neutralise the "unlocks ABSENT" tag in the top-100 confirmation sheet. Show the SR-zero basis (analytical or not) next to each row so the human confirms the category without steering. Regenerate the sheet and keep `human_decision` empty.
7. **CORP-2.** Inverted ranges ("1-½", en dash) must not survive pre-normalisation. Decide what the review asks: flag them and leave the value UNKNOWN.
8. **CORP-3.** `pair_lines` must keep and return the length-mismatch status.
9. **Re-run** the non-BBC router census with CENSUS_VERSION 0.4.0:
   - the 1,000-recipe sample first, then the full families;
   - same command as rows `RUN-S177-ROUTER-006/007`: `nice -n 10`, ≤ 24 workers, `uptime` first;
   - outputs `reports/step23/router_demo_census_vitc_nonBBC_{1000,full}_S178.json`;
   - report before/after DIRECT, ABSENT, PRIOR_PROCESS and NOT_APPLICABLE counts, and the 52 ABSENT ING split by analytical vs not;
   - list the S177 census files as SUPERSEDED rows in your report (the orchestrator appends them).

   Keep the census code-hash list in the output up to date.

## FIX-EVAL — findings E1–E8, P1, P2, CORP-4, CORP-5, CORP-6, B5

You own:
- `src/culinarystate/evaluation/{h1_independence,h3_independent,claim_audit,leakage_audit_d5,mcnemar_power,split_registry,h1_rungs}.py`. `h1_rungs.py` is the Mac's S174 file; fix only E6, minimally.
- `tools/s178_{leakage_audit_d5,corpus_replay_invariants,corpus_verb_census,evd_transition_audit}.py` and their outputs.
- The S178 prereg AMENDMENT drafts `reports/{step07,del5,step29,step10}/*AMENDMENT_S178_DRAFT*.md`. Never the originals.
- `reports/orchestration/S178_EVAL_report.md`, `S178_PREREG_report.md`, `S178_CORPUS_report.md`, `S178_EVD_report.md`. Append dated "S178 correction (FIX-EVAL)" sections only; never rewrite history.
- Tests, plus new `tests/unit/test_s178_fixeval_*.py`.

1. **E1.** A KEEP verdict with seen=false on an engine-draft gold is NOT HUMAN_BLIND. Label it ENGINE_DRAFT_KEPT or similar, per the review. Re-run the H1 independence check and correct the reported counts.
2. **E2–E8.** Fix each as the review states:
   - E2: one-sided floor.
   - E3: token-boundary matching ("pea" ≠ "peanut").
   - E4: a claim with cell=None is NOT_CHECKED and never counted as SUPPORTED.
   - E5: detect swapped recipe ids; verify DIAG29 rows.
   - E6: fix the docstring; `context()` defaults must not leak gold.
   - E7: correct the "sawtooth / conservative MDE" claim and separate the discordance ranges in the MDE tables (regenerate them).
   - E8: the id scan covers `reports/s178/`, with an explicit allow-list for files that legitimately name ids.
3. **P1 (D-071).** In the 07.A-R1 amendment draft:
   - (i) Withdraw the false claim that the three new copy checks are "stronger". Either restore IDENTICAL_JUDGEMENTS as a check or add a check that catches a judgement-only copy, with a test or a synthetic demonstration.
   - (ii) State plainly that Option A is a LOOSENING relative to the signed R-06 in the kappa-paradox region, with the reviewer's counterexample.
   - (iii) The AI recommendation must be the non-loosening option ("A-keep", or whichever the review shows does not loosen R-06). Present Option A only as a human choice that requires Kush's explicit, signed amendment.
   - Keep the option table and record the change in a "Revision S178-FIX-EVAL" note at the top.
4. **P2.** State the ≤1 and ≤4 counts per n, or define the co-gate by the Clopper–Pearson bound alone, as the review suggests.
5. **CORP-4/5/6, B5.**
   - Make the replay check independent of the engine where feasible, with non-trivial planted mutations.
   - Label the two by-construction invariants as such in a correction section.
   - Check determinism across two processes.
   - Fix the verb-census denominator and do not call a sample exhaustive.
   - Complete the transition-audit violations block, comparing per row, not totals.
   - Re-run whatever changes its outputs and log the runs.

Tests: run every touched lane's tests and report before and after, especially the EVAL, PREREG and CORPUS suites.
