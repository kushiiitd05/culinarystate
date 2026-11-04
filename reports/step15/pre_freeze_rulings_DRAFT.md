# Step 15.0 pre-freeze rulings: options for Kush (AI DRAFT, NOT A DECISION)

**Status:** `DRAFT_FOR_HUMAN_RULING`. Written 2026-11-03 by AI worker "ksh" (an agent, not Kush) for spine row 15.0 (`registry/execution_spine_v2.csv` L49). Under D-045 W1 (`DECISIONS.md` L269) this is the AI verdict; Kush and Parv review it and their ruling is final. **No D-number is added, nothing is decided, no threshold row is written, no value is invented.** Every "AI recommendation" below is labelled as such and may be rejected.

Spine 15.0 gate (L49): "HUMAN: Kush rulings recorded in DECISIONS before 15a". 15a.R (L50) and 15a (L52) are HARD on 15.0. Plan Step 15 card, Substeps row (`docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md` L552) lists the six items: "C2 for bootstrap use only; headline-split rule (SSOT pair-holdout + study-disjoint L16896–16901 vs TB-V0 'min(S-2..S-5)'); E1–E6 vs E1–E7 crosswalk; giant-component threshold (proposal >40%); K (proposal 10); RESERVED fraction".

Context that bounds every option:
- 15a is diagnostic only: "Claims allowed: none headline; diagnostics only; negative results retained" (Plan L577). R-12 (Plan L29): Step 29 may move earlier only as a diagnostic on frozen bootstrap data.
- 15a is HARD on 08a (Plan L555). 08a's G08-3 is a recorded FAIL (D-034, `DECISIONS.md` L195); its lineage keys are provisional. 15a.R "needs no 08a" (spine L50) precisely because it uses only existing ES-1.1 fields.
- Feasibility (Plan L557; `reports/master_plan/working_notes/research/r_eval_splits.md` L97): a study-disjoint test with >= 10 independent clusters exists only for Phenol-Explorer polyphenol retention; USDA and Bognár are one cluster each.
- R-20 (Plan L37): no post-hoc gate weakening; R-08 (Plan L25): thresholds are never chosen to hit a corpus size.

---

## 1. C2: may unverified E3 rows enter evaluation (bootstrap use)?

**What exists.** Open conflict C2 (`reports/h_state/state_representation_contract_v1.md` L66): "Tiers E1-E4 may enter evaluation sets, but G14-3/G15-H require human-verified held-out labels. Proposal: E3 rows may train and form a *Bootstrap* benchmark labelled 'unverified'; nothing is called Gold until verified." Plan open item 6 (L638): "15a assumes C2 is ruled for bootstrap/diagnostic use only ... the ruling must be recorded in DECISIONS before 15a." CHG-15-6 (L617). SSOT §201.7: "Test labels should preferentially come from E1–E4 and be human verified" (SSOT L16664); §201.8: "All held-out test values should be human verified" (SSOT L16690). Tier map: E3 `primary_evaluation_eligible = YES (conditional: held-out test rows need human verification)` (`registry/evidence_tier_provenance_map_v1.csv` L4). Today 17,978 E3 rows and 0 E4 rows (same file, `current_rows`).

| Option | Meaning | Consequence |
|---|---|---|
| C2-a | E3 may train and form a Bootstrap benchmark, every result tagged `BOOTSTRAP_UNVERIFIED`, never "Gold", never headline; RESERVED groups are not read before 15b | 15a and 29-diag can run; matches the C2 proposal, R-12, G15-h (Plan L559) |
| C2-b | E3 may not enter any evaluation set until human-verified | Stricter; 15a/29-diag have no evaluation set (0 E4 rows), so they cannot run |
| C2-c | E3 counts as test-eligible like E1–E4 without verification | Contradicts SSOT L16690 and G14-3/G15-H; **not admissible** (would weaken a gate) |

**AI recommendation (not a decision):** C2-a, scoped to 15a/29-diag only, with 15b still requiring human-verified held-out labels (G15-d, Plan L559). Reason: it is the only admissible option that lets the diagnostic lane run without weakening the 15b floor.

## 2. Headline-split rule

**What exists.** SSOT §202.3 (L16896–16901): "pair-holdout + source/study-disjoint as the strongest practical headline combination ... the default evaluation target when sample size permits." TB-V0 contract (`reports/h_state/transition_bootstrap_v0_contract.md` L20): "S-2 ingredient x process pair holdout; S-3 matrix-disjoint; S-4 process-disjoint; S-5 food-group-disjoint; S-6 study-disjoint (Phenol-Explorer only) ... Headline = S-2..S-5 min; S-1 not used for claims." Split 6 "is mandatory for literature-mined quantitative process data" (SSOT L16886–16891). Claim-first split registry (Plan L556; CHG-15-4 L615). 15a allows no headline claim (Plan L577), so this rule binds 15b; for 15a/29-diag it fixes which summary is reported first.

| Option | Rule | Notes |
|---|---|---|
| H-1 | SSOT: headline = pair holdout (S-2) AND study-disjoint (S-6), both required | S-6 exists only for PE (Plan L557); nutrient-retention families would have no headline |
| H-2 | TB-V0: headline = min over S-2..S-5 | Conservative (worst cold split); ignores study-disjointness, which SSOT L16890 makes mandatory for literature rows |
| H-3 | Claim-first: per claim family, headline = min over the applicable feasible cold splits (S-2..S-5) AND, for literature-mined rows, S-6 with >= K clusters; an infeasible required split makes the claim `DIAGNOSTIC_ONLY` | Combines both texts; nothing weaker than either |

**AI recommendation (not a decision):** H-3 for 15b; for 15a/29-diag keep the TB-V0 report order (min over S-2..S-5 first) as a diagnostic summary only, unchanged. Reason: H-3 is never weaker than H-1 or H-2 for any claim, and keeps the existing TB-V0 contract for the diagnostic.

## 3. Evidence-tier crosswalk (SSOT E1–E6 vs repo E1–E7)

**What exists.** SSOT §201.7 (L16651–16663): E1–E6, E6 = "heuristic / qualitative / weak inference", no simulator tier. Repo map (`registry/evidence_tier_provenance_map_v1.csv` L2–L8): E1–E7, E6 = "mechanism-family rule or heuristic (MODEL_ESTIMATED)" with allowed provenance `MODEL_ESTIMATED; IMPUTED`, E7 = "simulator output" (SIMULATED). SSOT change request CR-01 (`reports/master_plan/ssot_change_requests_v2.md` L7–L12, PROPOSED_ONLY) and audit finding (`reports/master_plan/master_plan_research_audit_v2.md` L271, L858: 04.4 crosswalk file proposed, never created; L3712: "Tier crosswalk ... HARD for 15"). No `registry/evidence_tier_crosswalk_v1.csv` exists. Plan R-13 (L30): Step 28 E7 prior deferred.

| Option | Rule | Notes |
|---|---|---|
| X-1 | Repo E1–E7 is canonical; record a one-to-one crosswalk E1–E5 = SSOT E1–E5, repo E6 ⊂ SSOT E6 (heuristic/model/imputed), repo E7 = repo extension SIMULATED with no SSOT tier; test/calibration eligibility = E1–E4 only, held-out values human-verified | Additive; keeps simulation != evidence (R-20) |
| X-2 | Collapse to SSOT E1–E6 (E7 folded into E6) | Loses the simulated/heuristic distinction that R-13/R-20 rely on |
| X-3 | Defer to a separate 04.4 crosswalk file before 15a | Blocks 15a on new work; the content would be X-1 or X-2 anyway |

**AI recommendation (not a decision):** X-1, recorded in the 15.0 DECISIONS entry (a separate registry file can follow). Reason: it changes no tier assignment of any existing row (all 17,978 are E3) and keeps E5/E6/E7 out of test and calibration (G15-b, Plan L559).

## 4. Giant-component threshold

**What exists (already signed).** `THR-08A-08` (`registry/preregistered_thresholds_v1.csv` L29, `PREREGISTERED_2026-10-26`, signed by Kush): "> 40%" share of a target family's rows in the largest split group, with the signer caution that USDA/Bognár hold 39.0% / 39.4% of all ACTIVE rows (knife-edge). `THR-08A-15` (L36): fallback naming "'publication-component CV' + leave-one-source-family-out; never 'study-disjoint'". `THR-08A-20` (L42): refinement on the evaluation-eligible pool with Kish n_eff >= K and largest share <= 0.40, "evaluated ONCE on the rule_version frozen at Step 15", the weaker label applies if either fails. Draft `T-08-01` (`registry/preregistered_thresholds_v1_DRAFT.csv` L8) is the unsigned earlier copy. Plan L564: "K=10 and the 40% giant-component threshold are PROPOSED_PILOT, pending pre-registration." (Plan L556 states the >40% rule itself.)

| Option | Rule |
|---|---|
| G-1 | Step 15 uses the signed THR-08A-08 + THR-08A-15 + THR-08A-20 unchanged (no new row) |
| G-2 | A new Step 15 row with a different value (any value must be justified without reference to observed shares, R-08) |
| G-3 | Only THR-08A-08 (drop the THR-08A-20 refinement) |

**AI recommendation (not a decision):** G-1. Reason: the rows are already signed; G-2 now would be chosen after the 39.0% / 39.4% shares were seen (the knife-edge note in THR-08A-08), and G-3 drops a stricter side-by-side check.

## 5. K (independent test clusters per headline split)

**What exists.** G15-c (Plan L559): "every HEADLINE split has ≥K=10 independent test clusters (PROPOSED), else it is registered DIAGNOSTIC_ONLY". `T-15-01` (`registry/preregistered_thresholds_v1_DRAFT.csv` L15, PROPOSED_UNSIGNED): "K = 10". `THR-08A-20` (signed, L42) already uses "K = 10, the same K as G15-c, PROPOSED". r_eval_splits L235: "PROPOSED_PILOT K = 10; not literature-derived"; L123: with fewer than about 20–30 clusters use a cluster sign-flip permutation test.

| Option | Rule |
|---|---|
| K-1 | Register K = 10 for G15-c as drafted (same K as signed THR-08A-20) |
| K-2 | Another single K (human value; must not be chosen from observed cluster counts, R-08) |
| K-3 | Family-specific K |

**AI recommendation (not a decision):** K-1, with the inference rule "Fewer than ~20–30 clusters → cluster sign-flip permutation, not cluster-robust SEs" (Plan L558) carried into the row. Reason: K = 10 is already inside a signed row; two different Ks for the same gate would be a forking path. K = 10 is a pilot convention, not a derived value, and the row must say so.

## 6. RESERVED fraction (and the parameters the 15a.R seal needs)

**What exists.** Spine 15a.R (L50): "seeded, group-level, hash-committed ... HUMAN: Kush signs RESERVED fraction and seed before sealing; DATA: existing 17,978 ES-1.1 rows; existing independence_group x (matrix, process)". Plan L552: "fraction pre-registered in 15.0, hash-committed, 0 reads before 15b ... If 08a later merges a RESERVED group with a DEV group, the merged component is burned and logged." CHG-15-3 (L614) and CHG-15-9 (L620): both "needs human approval". **No fraction value exists in any tracked file** (searched the plan, spine, threshold registries, audit and research notes): the value is UNKNOWN and this draft does not propose a number.

Findings the ruling should see (read from code, no data counted):
- PE rows carry `independence_group` = the publication's source family (`src/culinarystate/ingest/phenol_explorer_build.py` L161); USDA and Bognár rows carry one family each (`usda_r6_build.py` L115, `bognar_build.py` L101). The plan's literal unit, independence_group × (matrix, process), therefore lets **one PE publication have cells on both sides** (RESERVED and DEV), which SSOT Split 6 forbids for literature rows ("Keep all rows from a paper/study/experimental campaign together", L16886–16891). r_eval_splits L89–L92 gives the units: lineage component for literature rows, (matrix × process × source) cell for database rows.
- USDA/Bognár cells are not independent clusters (one database each); reserving them protects against adaptive reuse but adds no independent test cluster.

Parameters to rule (the 15a.R tool, `tools/step15a_R_seal.py`, reads exactly these):

| Parameter | Options | AI recommendation (not a decision) |
|---|---|---|
| fraction | a group-level fraction in (0, 1), value chosen by Kush; or a row-level fraction | group-level (the plan says "group-level"); value: **UNKNOWN, Kush supplies it** |
| unit | `CELL` = independence_group × (matrix, process) for every row (plan literal); `STUDY_THEN_CELL` = rows with a present study id grouped by independence_group (whole publication), all other rows by cell | `STUDY_THEN_CELL` (Split 6 for literature rows; the plan's cell rule for database rows) |
| stratify | `SOURCE_FAMILY` (fraction applied within each source family) or `NONE` | `SOURCE_FAMILY`, so each family keeps DEV groups for diagnostics |
| seed | public seed written in DECISIONS (as D-048 did for the pilot nonce), or a secret seed committed by sha256 | committed seed (`SEED_SHA256` in DECISIONS; seed file kept outside git): the sealed list must never be in git, and a public seed plus the tracked ledger would let anyone recompute it |
| rounding | per stratum, floor(fraction × n_groups) (tool rule `15aR-sha256-rank-v1`) | as built; a stratum with fewer than 1/fraction groups reserves none, which the commitment file reports |

### Lines the 15a.R tool requires in the signed 15.0 entry

The tool refuses unless a `### D-NNN` heading containing `15.0` exists in `DECISIONS.md`, is not marked DRAFT/PROPOSED/UNSIGNED, names Kush on its `**Approver:**` line and carries each line below exactly once. Placeholders in angle brackets are for Kush; the tool rejects them as written.

```text
- **15.0 RESERVED_FRACTION:** <fraction in (0,1), e.g. written as a/b or a decimal>
- **15.0 RESERVED_UNIT:** <CELL | STUDY_THEN_CELL>
- **15.0 RESERVED_STRATIFY:** <SOURCE_FAMILY | NONE>
- **15a.R SEED_SHA256:** <sha256 hex of the UTF-8 seed text, one trailing newline removed>
- **Approver:** Kush ...
```

No such entry exists today, so the tool refuses (tested).

---

## 7. Summary for the ruling

| Item | Options | AI recommendation (labelled, not adopted) | Value supplied by AI |
|---|---|---|---|
| C2 | C2-a / C2-b / (C2-c inadmissible) | C2-a, bootstrap/diagnostic only | none |
| Headline split | H-1 / H-2 / H-3 | H-3 for 15b; TB-V0 order for 15a diagnostics | none |
| Tier crosswalk | X-1 / X-2 / X-3 | X-1 | none |
| Giant component | G-1 / G-2 / G-3 | G-1 (signed THR-08A-08/15/20 unchanged) | none (existing signed rows) |
| K | K-1 / K-2 / K-3 | K-1 (K = 10 as in signed THR-08A-20) | none (existing proposed value) |
| RESERVED | fraction, unit, stratify, seed handling | group-level, STUDY_THEN_CELL, SOURCE_FAMILY, committed seed | **fraction and seed: UNKNOWN until Kush supplies them** |

Not covered by 15.0 and unchanged here: 08a's G08-3 FAIL, the Step-07 gate (HARD for 15b, R-05), 15b sealing and the licence matrix (Plan L561).
