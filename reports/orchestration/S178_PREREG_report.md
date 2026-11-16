# S178 PREREG lane report: pre-signature amendment drafts for the four preregistrations

Status: **AI_DRAFTED / PROPOSED.** Written 2026-11-09 by the S178 PREREG lane (an AI agent) on manjot-server,
worktree `~/kush_work/culinarystate/.orch` (branch `max/s176-orchestration`, HEAD 8577136 + uncommitted). Nothing in
this lane is a decision, signature, approval or ratification (D-071). The four prereg files, the freeze record and
every signed record are **unchanged** (base sha256 re-checked at the end of the lane). The Mac scribes the chosen
options into the prereg files after the 9-10 Nov sitting; the humans sign only the locked bytes.

## 1. What was built

| File | sha256 | Covers (ops pack / consensus) |
|---|---|---|
| `reports/step07/07A_R1_preregistration_AMENDMENT_S178_DRAFT.md` | `b3a95e127be6375a609e6c717b384e9a902d45a579ce00fbfa3be659e267d7fd` | #2 T2-C05-R5; C06 T2-C05-R7; REV-B Q24, F-01..F-07, G-01, G-17 |
| `reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_DRAFT.md` | `fd2c50321bd88f389e5309f1ebc96cfb73817cd92c81dee592a70df1582a15e3` | #4 T8-C06-R2, #5 T8-C12-R1, #6 T9-C12-R1 + T8-C04-R2, A1 (G-05..G-08, G-12, G-13), C07 |
| `reports/step29/29diag_preregistration_AMENDMENT_S178_DRAFT.md` | `ec598a83631c8ce8d34cb328f5f1daf6a28e42a8e854fc6eeb571c60aae74f96` | #7 T6-C03-R5, T6-C02-R1, REV-A Q18/Q19/N6, REV-B F-08 |
| `reports/step10/aa_pilot_preregistration_AMENDMENT_S178_DRAFT.md` | `4c1bc2139f75efff7d208acd727e1cb6e2b385c3545cf76b402f7d467d14a924` | A3 (REV-A V7/Q16, REV-B F-09/G-16/B2.3), T9-C26-R5 "AA wording" |
| `reports/orchestration/S178_PREREG_calc/` (3 scripts + 2 JSON) | listed in §5 | exact McNemar / sign-test / Clopper-Pearson tables; AC1 tolerance; R1 pool counts |

Each amendment file has: base-text sha256 it was written against; a decision table (option ids, type, pack
recommendation); a "why this is not post-hoc weakening" section; diff-style changes quoting the original lines with
OPTION blocks; the numbers behind the options; the code needed for computability; and a "hash after lock" block
(`git show <LOCK>:<file> | sha256sum`, `sha256sum <file>`, `git diff --exit-code <LOCK> -- <file>`).

## 2. Amendments and the decision each needs

| Prereg | Decisions (ids in the amendment) | Who | Lane recommendation |
|---|---|---|---|
| 07.A-R1 | D-07A-1 gate: A hardened AC1 (bootstrap lower bound >= 0.95, 7 critical fields, accuracy co-gate, planted rows) / A-keep / B kappa per R-06 + PABAK diagnostic / C accuracy-primary / D defer / E draft as written. D-07A-2 co-gate X (Clopper-Pearson: X_crit 0.95 = at most 1 critical defect of 100; X_any 0.90 = at most 4). D-07A-3 USDA floor U1/U2/U3. D-07A-4 planted rows P1/P2/P0. D-07A-5 deadline. **D-07A-R06: Kush's own DECISIONS entry (template only, §4 of the file)** | A, C, E and R-06: Kush (HUMAN); rest choice | A + U1 + P1 + T2 |
| D5 / H1 / H3 | D-D5-1 S pool 30/60. D-D5-2 S gold G-A blind human / G-B engine after blind pass. D-D5-3 B4 view K1/K2. D-D5-4 embedding. D-D5-5 H3 test H3-A/B/C. D-D5-6 sidedness. D-D5-7 VPN fallback F1/F2. D-D5-8 "uncalibrated" wording | choice (both sign) | S60 if >= 18 h each, else S30; G-A; K1; E5; H3-A; one-sided; F1 |
| 29-diag | D-29-2 contrast K-A (add TB-V0 B-2 ingredient mean) / K-B / K-C. D-29-3 splits S-A/S-B. D-29-4 cap sensitivity. D-29-5 duplicate control. D-29-1 and D-29-6 text fixes | choice (Kush signs) | K-A, S-A, add both |
| AA pilot | D-AA-1 add A3 lines. D-AA-2 pH gate pH-A/B/C. D-AA-3 firewall FW-A/FW-B. D-AA-4 sensitivities. D-AA-5 licence facts per paper | choice; D-AA-5 HUMAN fact (Kush) | add; pH-A falling back to pH-C; both; add |

## 3. Could any proposal be read as post-hoc weakening?

The rule applied: nothing may relabel or rescore a failed gate, loosen a threshold after seeing an outcome, or drop
a criterion. **07.A v4 stays FAILED on record (kappa 0.0, raw 0.9944, 900 cells, 5 disagreements); the R1 attempt is
a new attempt on a fresh packet, fixed before any R1 label exists.**

| Item | Reading risk | How the draft handles it |
|---|---|---|
| 07.A Option A (AC1) | "gate changed after a failed gate" | Disclosed in the prereg text ("gate redefined after a failed gate"); needs Kush's R-06 entry before any signature; stricter than the draft's 0.80 (tolerates <= 35 / 26 disagreeing cells of 900 on the bootstrap bound vs 174), adds a correctness co-gate and planted rows. The pooled-AC1 part alone would still pass the v4 pattern (lower bound 0.9889) and the file says so; with the duration critical-field rule, the co-gate and the planted rows the v4 pattern would not pass (illustration, not a rescoring). |
| 07.A Option A, provenance | **One element relaxes a rule:** `IDENTICAL_JUDGEMENTS` (identical files -> NOT_COUNTED) is removed (REV-B F-05) | Flagged in the file; replaced by three copy checks; **A-keep** offered for a zero-relaxation choice. |
| 07.A Option E (draft as written) | Looser than R-06 at high prevalence (would have passed v4) | Listed for completeness; not recommended. |
| 07.A Option C (accuracy-primary) | Removes every agreement statistic from the gate after an agreement gate failed: the reading most open to "metric shopping" | Not recommended; needs the strongest R-06 wording if chosen. |
| 07.A Option B (R-06 unchanged) | none (no deviation) | Accepted in advance that it may FAIL again by the kappa paradox. |
| D5 H3 | Replacing the bootstrap with a sign test | Stricter (the sign test needs >= 5 one-way questions; the bootstrap could pass with 3). The near-automatic P3 abstention condition is **kept** in the rule so no criterion is dropped. |
| D5 H1 | none | Decision rule unchanged (both McNemar tests); gold made independent; power note added before signature. |
| D5 embedding | Choice informed by a silver dev study | No D5 output exists; the evidence and its limits are cited. |
| 29-diag | none (no gate) | Additions are diagnostics fixed before signature; label fixes only describe the code. |
| AA pilot | The agent has seen the 16 CAL values (§6 already says so) | Primary Model A unchanged; new analyses are pre-declared sensitivities beside it; the §4 target becomes a hard minimum (stricter); RESEARCH_ONLY pre-announced. |

## 4. Findings (bugs, mismatches, corrections) for the orchestrator

1. **29-diag rung text does not match the code.** `transition/baselines.D3Hierarchical` (L60-L91) is a target x
   process mean shrunk to the process mean; it never reads matrix or food group. No TB-V0 B-2 (ingredient mean)
   exists in the code. So the consensus "D2 process-mean vs D3 ingredient-mean" contrast (T6-C03-R5) is not
   computable as worded, and the T6-C02-R1 crosswalk row "B-2 = D3 matrix arm" points at nothing. Option K-A adds a
   ~20-line B-2 mean. Whoever writes `registry/transition_ladder_crosswalk_v1.csv` should not map D3 to B-2.
2. **29-diag split list:** the prereg names S-5 food-group-disjoint; `transition/splits.all_splits` (L100-L111) has
   no food-group split (it has random, pair_holdout, matrix_disjoint, process_disjoint, study_disjoint). "All grouped
   by `independence_group`" is also not what the runner does.
3. **The 29-diag contrast is lopsided by construction** (S-3: B-2 sees no test matrix; S-4: D2 sees no test process);
   only S-6 (Phenol-Explorer) compares the arms on equal terms. Stated in the amendment before any run.
4. **`tools/step07_agreement.py` writes to the hard-coded path of the retained v3 result**
   (`reports/step07/step07h_human_gate_result.json`, L54/L90). If the sitting picks the kappa route (Option B), the
   scorer must be a mode of `condition_agreement.score`, not this tool, or it overwrites an R-19 record.
5. **PABAK as printed** by `condition_agreement.score` is the binary form 2·p_o − 1 although the codebook has q = 7;
   the q-category form (q·p_o − 1)/(q − 1) differs (v4 pattern: 0.9889 vs 0.9935). Diagnostic only; both labelled.
6. **Ops pack #6 text is slightly wrong:** it says the smallest significant results at n = 30 are "8-0, 9-1, 10-2 ...
   gap 0.23 to 0.27". Exact McNemar: 6-0 (p 0.031, gap 0.20) and 7-0 (0.016, 0.233) are also significant (REV-B's own
   table agrees). The D5 amendment carries the corrected table.
7. **C07 fallback sentence is internally inconsistent:** it calls B0/B1/B2/B4 "deterministic", but each is an LLM
   answer (`h1_rungs.prompt`). Without the LLM, H1 and H3 cannot run; only B5T, retrieval rankings and router
   accuracy can. Option F1 says so; F2 runs the same model digest on the Mac.
8. **Extra S1 circularity beyond REV-B F-13:** `tools/d5_draft_s.py` L66-L67 keeps an S1 recipe only when the engine
   found a heated ingredient (selection on engine output; all 20 S1 drafts have non-empty engine gold). The D5
   amendment drops that filter.
9. **H3 is likely underpowered:** at the silver-ladder rate of B2 unsupported claims (about 1-2 of 20 answers),
   the exact sign test at n = 40 has power 0.05-0.37 (one-sided); a "cannot be shown at this n" outcome is the most
   likely one and is pre-stated.
10. **`freeze_records.prereg_signed` binds only `reports/step29/29diag_preregistration_DRAFT.md`**, so amendments
    must be merged into that file before Kush signs (a side-by-side amendment cannot be signed for 29-diag).
11. **AA pilot:** no pH field is extracted (§2), so a pH domain gate needs a new verified field or falls back to
    matrix class only; AAK-09 (mango blanching, a water-contact process) is in CAL while the domain gate excludes
    water contact (handled as a pre-declared sensitivity); AAK-01 and AAK-11 rows were extracted with licence
    UNKNOWN; SIM-VAL PDFs AAK-03/07/12 already sit in `data/raw/aa_pilot/` within the agent's reach (FW-A).
12. **29-diag needs scikit-learn** (`baselines.py` L142, D5Boosting); `.venv312` on manjot has none, so 29-diag stays
    on the Mac (install decision #20).
13. **Concurrent lane overlap:** a parallel S178 lane has uncommitted changes in `evaluation/h1_rungs.py`
    (`pre_cut_only`, `state_view`) and new `evaluation/{h1_independence,h3_independent,claim_audit,leakage_audit_d5}.py`.
    The D5 amendment names these as the computing functions, but this lane **did not review or run them**. Their
    defaults keep the S173 behaviour, so the D5 runner must pass the new arguments explicitly.
14. R1 condition pool by source (counts only, before the v1-v4 exclusion): USDA 270 (S3 18, S5 15, S6 237), Bognar
    274, Phenol-Explorer 3,870; matches the manifest's stratum pool sizes. A USDA floor of 20 is feasible only
    through S3, S5, S6.

## 5. Runs (rows for `registry/compute_runs_v1.csv`; the orchestrator merges)

```csv
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S178-PREREG-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),8577136+uncommitted,—,1,.venv312/bin/python -I reports/orchestration/S178_PREREG_calc/r1_pool_counts_s178.py,stdout only (counts quoted in reports/step07/07A_R1_preregistration_AMENDMENT_S178_DRAFT.md C3),—,2026-11-09,2026-11-09,DONE,read-only count of the 07.A-R1 condition pool by stratum x source family from ledgers/data/COND+EVD (no ids or text printed); script sha256 087ad078512acacd4b39a644e776e752cbc9ec43b7a6bde6004c031dfe246383; clock times not captured (< 1 min)
RUN-S178-PREREG-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),8577136+uncommitted,—,1,.venv312/bin/python -I reports/orchestration/S178_PREREG_calc/power_s178.py <out.json>,reports/orchestration/S178_PREREG_calc/power_s178.json,1da525daf3ac1425cb16be5b72f2cc36586c86911a1c70792950c7ad3353f8c8,2026-11-09,2026-11-09,DONE,exact McNemar min splits + power (n 30/45/60) via paired_stats.mcnemar_exact; sign test; Clopper-Pearson; planted-row pass probabilities; second run byte-identical (34.8 s); script sha256 6b0fc2f3b665fc9eb1cf5716735930aef7d258c8b89d70e1427fe61f45ed8ff4
RUN-S178-PREREG-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),8577136+uncommitted,—,1,.venv312/bin/python reports/orchestration/S178_PREREG_calc/ac1_s178.py <out.json>,reports/orchestration/S178_PREREG_calc/ac1_s178.json,c818ddea7ed58686e242e0d584e4065cbf97f2476603cb115877d1f7ecbcd25e,2026-11-09,2026-11-09,DONE,AC1/kappa/PABAK tolerance on SYNTHETIC label vectors with condition_agreement (2000-resample bootstrap) + v4 reconstruction from committed counts; a first version was stopped after 180 s (too many bootstraps) and replaced by a binary search; script sha256 6695334f0776ccac25cf8bec82570d143d01e4362e316091c8b2532821a44d80
```

Tests: none run; this lane changed no code. Disk: < 1 MB.

## 6. What a human must decide or do (in addition to the decision tables)

- **Kush, own hand:** the R-06 amendment entry if 07.A takes Option A, A-keep, C or E (template in the 07.A file §4;
  the agent must not write or commit it); the licence facts per AA paper (D-AA-5); FW-A (moving the SIM-VAL PDFs).
- **Both:** choose options at the sitting; confirm >= 18 h free 9-16 Nov before choosing S60.
- **Mac scribe (agent, after the sitting):** apply the chosen blocks to the four prereg files in one lock commit; fill
  the placeholders the D5 text requires (e5 revision hash, Ollama digest, seed, `num_predict`); write the lock
  record (proposed `reports/orchestration/PREREG_LOCK_2026-11-10.json`) with each prereg sha256, each base sha256,
  each amendment-draft sha256, the packet / sheet / key hashes and the lock time; then the code items in each
  file's computability table, before the packets and sheets are re-issued.
- **Orchestrator:** WORKLOG was not touched (`tools/log_step.py` writes WORKLOG, which is orchestrator-only in this
  round); log this lane as S178. DECISIONS ids for the sitting start at D-079.

## 7. Not done / limits

- The four prereg files, `registry/freezes/15A-BOOT-2026-11-08.json`, DECISIONS, WORKLOG, STATUS, handoff and the
  compute log were not edited.
- The concurrent S178 evaluation modules were read only for their interfaces, not reviewed or tested.
- U and X block drafts, the blind review sheet and the planted-row builder do not exist yet (named in the
  computability tables).
- Every numeric threshold proposed (0.95 bootstrap bound, X_crit, X_any, 8 of 10, USDA sub-quotas, K_min 10,
  k = 5 for B-2, claim-audit size) is a PROPOSED design value for the humans to set, not a literature constant.

## S178 correction (FIX-EVAL), 2026-11-09

AI_DRAFTED (D-071: this correction only tightens or withdraws). Appended by lane FIX-EVAL after the SCI-B review
(`reports/orchestration/review/S178_REV_SCI-B.md`, P1, P2, E7); the sections above are kept as written. The amendment
drafts carry a "Revision S178-FIX-EVAL" note at the top.

- **P1 (i), §3 row "07.A Option A, provenance".** "replaced by three copy checks" was presented in the 07.A draft as
  "three stronger copy checks". Withdrawn: they are different and do not catch a judgement-only copy (reviewer 2 copies
  reviewer 1's 10 judgement columns and blanks the reasons: the old rule gives NOT_COUNTED, all three new checks pass).
  Synthetic demonstration with the project's scorer code: `tests/unit/test_s178_fixeval_prereg.py`. No check on the
  judgement columns can separate that copy from an honest perfect agreement.
- **P1 (ii), §3 row "07.A Option A (AC1)" and the "post-hoc weakening" framing.** Option A is a **LOOSENING relative to
  the signed R-06** in the kappa-paradox region. Counterexample (same test file): reviewer 1 all CORRECT, reviewer 2
  SHOULD_BE_AMBIGUOUS on 5 conditions in 5 fields, adjudicated to 0 defects: R-06 pooled kappa 0.0, FAIL; Option A
  bootstrap AC1 lower bound 0.990, every critical field passes, co-gate 0 defects, PASS. **A-keep also passes it** (the
  files differ in 5 cells, so the kept IDENTICAL_JUDGEMENTS rule does not fire), and so do C and E.
- **P1 (iii), §2 table "Lane recommendation: A + U1 + P1 + T2".** Replaced by **B + U1 + P1 + T2**: B (R-06 unchanged)
  is the only attempt option that does not loosen R-06 (D is a deferral). The review suggested "A-keep"; A-keep loosens
  R-06 in the same region, so an AI may not recommend it. A, A-keep, C and E remain human choices; each needs Kush's own
  signed D-0NN that names the loosening (the §4 template now asks for that sentence). Under B, planted rows P1 as an
  added NOT_COUNTED condition only tighten.
- **P2, §2 table "X_crit 0.95 = at most 1 critical defect of 100; X_any 0.90 = at most 4".** The counts hold for n = 100
  only. The co-gate is the Clopper-Pearson bound; implied counts: n = 100 (U1, U3) at most 1 / at most 4; n = 120 (U2)
  at most 1 / at most 6.
- **E7, D5 amendment C5 and §3.** The C5 power sentence set an n = 30 range over discordance 0.3-0.5 next to an n = 60
  range over 0.2-0.5. Now: over 0.3-0.5, n = 30 needs a gap of 0.28-0.36 and n = 60 0.20-0.26 (n = 60 at 0.2: 0.16;
  n = 30 at 0.2: none). Power is monotone in the gap, so the first grid gap reaching 80 % is the MDE; no number changed.
