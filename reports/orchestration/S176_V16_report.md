# S176 lane V16 — SSOT v16.0 DRAFT (pending Kush's approval)

**Status: DRAFT · AI_DRAFTED · PROPOSED.** Written 2026-11-08 by the V16 lane (a coding agent) in the worktree `~/kush_work/culinarystate/.orch` (branch `max/s176-orchestration`, base `07fc0d2`, uncommitted). Nothing here is a decision, signature, approval or nonce (D-071). **SSOT v15.0 remains authoritative until Kush approves v16 in a `DECISIONS.md` entry.** No git write was run.

## 1. What was built

| File | What | sha256 | Size |
|---|---|---|---|
| `docs/SSOT/computational_gastronomy_master_ssot_v16_0_DRAFT.md` | v16.0 DRAFT = an exact `cp` of v15.0, with only the title/version/updated lines (1, 3, 4) edited, plus the appended **PART XIV, §280–§291** (lines 45698–46833) | `0c4d8409cd2cca55271f26b3f9400fd1aebe26ab75d0fe5276895ab5ad66b529` | 1,933,278 bytes; 46,833 lines |
| `docs/SSOT/ssot_v16_INDEX_ADDENDUM.md` | Line ranges of every new heading (same columns as `docs/SSOT_INDEX.md`: Start / End / Lvl / Heading), the two v15 index rows that differ, an inventory check and the boxed statements | `54329e48d537d455df1138e827cf37050fd83d3254958bbe73e8550d02b67f6e` | 138 lines |
| `reports/orchestration/S176_V16_report.md` | this report | — | — |

Reference hashes:
- v15.0 (unchanged, equal to `git show HEAD:`): `1c9262bfe51a9f97090b1c2874757de535866c9c8b428df6be67df95a3675644` (1,799,542 bytes; 45,697 lines).
- Lines 5–45697, identical in v15.0 and the v16 DRAFT: `4616a820a1ea3dbc9ef9cd8201c6d82b3dca7d0669b6ef6b9bb34d731dce2c98`.
- PART XIV alone (lines 45698–end): `91b735a5d6e09832411acabc788a932f40e8a564dfd76a4b97158c19feb3e382`.

Ownership note: the brief lists `docs/*` as orchestrator-only, but the lane assignment explicitly asked for the two new `docs/SSOT/` files above. They are **new files only**. No existing file under `docs/` was touched (`git status --porcelain -- docs/` shows only the two new files). `DECISIONS.md`, `STATUS.md`, `WORKLOG.md`, `handoff/*`, `registry/compute_runs_v1.csv` and all ledgers are untouched (`git diff --stat` empty). `tools/log_step.py` (repo CLAUDE.md) was not run, because it writes `WORKLOG.md`, which is orchestrator-only. The WORKLOG and compute-log entries are left to the orchestrator; the rows are in §4.

## 2. What changed

**Header (line-count neutral):**
- Line 1: the title gains "(v16.0 DRAFT — pending Kush's approval; v15.0 remains authoritative until approved)".
- Line 3: "**Version:** 16.0 DRAFT — pending Kush's approval; v15.0 remains authoritative until approved…", quoting the old v15.0 version line inside it.
- Line 4: "**Updated:** 8 November 2026 (v16.0 DRAFT; v15.0 was updated 6 October 2026)".
- Because the line count did not change, every range in `docs/SSOT_INDEX.md` still points at the same v15 text.

**PART XIV (appended after §279 and the v15 references, per §139 "append, don't rewrite"):**

| § | Content |
|---|---|
| 280 | Scope, authority order, the adoption rule, and the status of the change-set checks §E |
| 281 | Digest of D-026…D-077, one line each with its status (D-028 is absent and exists only as an unsigned draft), the proposed D-071 line "AI may tighten, defer or refuse; never loosen, close or sign", and proposed record repairs |
| 282 | Spine v2, rulings R-01…R-20, and the R-06 vs D-075 reconciliation, stated as PROPOSED for Kush |
| 283 | Evidence lineage and independence (04.1, 04.2-min, 04.6-min, 04.9-min ADOPTED by D-029) and the kinetic/trajectory contract (04.3, accepted for engineering by D-050 with thresholds signed by D-051; the contract as a whole is still a draft); the 15.0 rulings C2-a, H-3, X-1, K-1 (D-068) |
| 284 | Physical-state dataset (D-077 two layers, ADOPTED); verified full-corpus counts; the evaporation/phase-change rule (free-water zones capped at the local boiling point until dried, the DRY/FAT Layer-2 fields marked SUPERSEDED); surface/core/volume-average zones; geometry and shape factors; process-family coverage, including non-heat families, with validity domains (F₀ canning-only; thaw ≠ reverse; Fick only as a bound); what Layer 2 may and may not feed, with the Q1 ablation rule |
| 285 | Lot-state and mixture representation (REV-A §E): phases, members, composition intervals, solute load, a_w rules, pH member ranges with the bounding rule and violation flags, history variables and contact log, interaction edges (mechanism-mediated and physical), the weakest-provenance tier rule, computed vs learned, owner steps |
| 286 | Router v2: gate order G0–G9 plus a target-presence gate and a lot-context gate; three-valued applicability; INTERPOLATE bracketing rule; QUALITATIVE from unreviewed MECH entries labelled `AI_DRAFTED_MECH_UNREVIEWED`; ASK flip-sensitivity rule; mode → §141 crosswalk; demo vs scientific mode; census reporting |
| 287 | 07.A-R1 statistic package (stricter AC1 lower bound, accuracy co-gate, seeded errors); H1 circularity caveat and fix; H3 non-tautological scoring; power/MDE; reproducibility minimum; further claim rules |
| 288 | Step 35 representation firewall: task-view matrix, `depends_on` closure test, non-circular targets |
| 289 | Corrections register, C-01…C-17, each verified in the repo |
| 290 | Merge register: every change-set A/B/C/D item and CR-01…CR-65, with status and ids; V16-P01…P36 |
| 291 | Return point: status of every step and next actions |

**No v15 law or gate is weakened. No scientific value is added.** Every number in PART XIV is one of: a repo count; a value already signed in a registry; a plan-card PROPOSED_PILOT value; or a review proposal named as such and marked PROPOSED.

## 3. Verification performed

| Check | Result |
|---|---|
| `cp` v15 → v16, then `sha256sum` of both | identical (`1c9262bf…`) before editing |
| Header edit by script, with assertions on the old line contents and the line count | done; line count 45,697 kept |
| `diff <(sed -n '1,45697p' v15) <(sed -n '1,45697p' v16)` | only lines 1 and 3–4 differ |
| sha256 of lines 5–45697 and of line 2, v15 vs v16 | identical (`4616a820…`; line 2 `01ba4719…`) |
| sha256 of lines 1–45697 with lines 1, 3, 4 removed | identical (`e96200ef…`) |
| `git diff --stat` on `docs/`, `DECISIONS.md`, `STATUS.md`, `WORKLOG.md`, `handoff/`, `ledgers/`, `registry/compute_runs_v1.csv` | empty; v15.0 and `docs/SSOT_INDEX.md` equal their HEAD versions |
| Internal consistency of PART XIV (script) | 65/65 CR rows; status counts match the printed totals (12 APPLIED-BY-DECISION, 12 PARTLY, 4 HOLD, 37 PROPOSED); E.1 counts 55 MATCH / 10 PARTIAL; 36 V16-P ids, each listed and referenced; every §28x/§29x cross-reference resolves to a heading; every markdown table has consistent column counts |
| Change set §E.1: CR quoted "current text" vs the cited v15 lines | all 65 checked read-only (helper subagent, targeted `sed -n` / `grep -n` only): 55 MATCH, 10 PARTIAL (6 offset-only: CR-32, 45, 46, 48, 59, 63; 4 partly wrong in substance: CR-11, 31, 53, 57), 0 MISMATCH. A mechanical line-range check (script) agreed. |
| Corrections register figures | each re-derived from the files named in §289 (counts only) |

No tests were run: no code was changed. This lane is documentation only.

## 4. Runs (rows matching the `registry/compute_runs_v1.csv` header; for the orchestrator to log)

`<S>` = `/tmp/claude-1035/-home-manjot23309-kush-work/1d912ff7-13d4-43e2-ac29-84a2419065b4/scratchpad`. All runs are read-only on repo data and counts-only. The shared server's load average was ≈ 150–160, so only single processes were run.

```
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S176-V16-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,NONE (CR anchors vs docs/SSOT_INDEX.md),1,"python -I <S>/v16/cr_linecheck.py . <S>/v16/cr_linecheck.json",<S>/v16/cr_linecheck.json,91ad71a9c76bf113ed1705ef728163b9b61cca635e42a37bf83ecb976108bb2b,2026-11-08T13:59Z (approx),2026-11-08T13:59:50Z,DONE,"mechanical CR line-range check; <1 s"
RUN-S176-V16-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,NONE (SSOT v15 line ranges),1,"helper subagent: targeted sed -n / grep -n reads of docs/SSOT/computational_gastronomy_master_ssot_v15_0.md for CR-01..CR-65 (read-only)",<S>/v16/cr_textcheck.md,b03e713578d8419aeb3860ee5ff20fccf9cd1f0f4968fbd790c07e727495dba9,2026-11-08T14:00Z (approx),2026-11-08T14:20:21Z,DONE,"change set E.1 text check; 55 MATCH / 10 PARTIAL / 0 MISMATCH"
RUN-S176-V16-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,NONE (ledgers + report JSONs; counts only),1,"inline python -I reads of ledgers/data/{SVAR,EVD,COND,KGE}.jsonl and reports/step17/rung_a_dryrun_counts_full_corpus_final.json, reports/step26/{simulability_census_full_corpus_S169,binding_census_L1_*_full_S17*,scenario_L2_*_full_S17*}.json, reports/step23/router_demo_census_vitc_full_corpus_S171.json, registry/{scenario_defaults_v1,state_variable_registry_v1,mechanism_seed_roster_draft_v1,compute_runs_v1,negative_results_register_v1}.csv",stdout (values quoted in v16 §284.2 and §289),n/a,2026-11-08T13:10Z (approx),2026-11-08T13:50Z (approx),DONE,"verification counts for the corrections register; no file written"
RUN-S176-V16-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,NONE (document build),1,"cp v15 -> v16; python -I <S>/v16/edit_header.py v16; cat <S>/v16/part14_{a,b,c,d,e}.md >> v16",docs/SSOT/computational_gastronomy_master_ssot_v16_0_DRAFT.md,0c4d8409cd2cca55271f26b3f9400fd1aebe26ab75d0fe5276895ab5ad66b529,2026-11-08T14:33Z (approx),2026-11-08T14:34:10Z,DONE,"v15 portion verified identical except lines 1,3,4"
RUN-S176-V16-005,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,NONE (document index),1,"python -I <S>/v16/build_addendum_rows.py v15 v16 <S>/v16/addendum_rows.json; python -I <S>/v16/write_addendum.py <S>/v16/addendum_rows.json docs/SSOT/ssot_v16_INDEX_ADDENDUM.md",docs/SSOT/ssot_v16_INDEX_ADDENDUM.md,54329e48d537d455df1138e827cf37050fd83d3254958bbe73e8550d02b67f6e,2026-11-08T14:35Z (approx),2026-11-08T14:35:56Z,DONE,"same heading rule as tools/build_ssot_index.py"
```

## 5. PROPOSED items Kush must approve (nothing below has force)

### 5.1 Urgent: they change what gets signed or shown this week

| Id | Item (v16 §) | Due (consensus §6.2) |
|---|---|---|
| V16-P05 | **R-06 vs D-075:** amend R-06 for attempt 07.A-R1 only (named pre-registered deviation; AC1 + accuracy co-gate), or keep the κ gate (§282.3) | 9 Nov, before the prereg lock |
| V16-P06 | 07.A-R1 package: a stricter threshold on the AC1 lower bound, an accuracy co-gate, seeded errors (REV-B wants them to decide whether a file counts; consensus C06 wants diagnostic-only, so choose one), and `duration_judgement` / `temperature_value_judgement` added to the critical fields (§287.1) | 10 Nov edit lock |
| V16-P15…P22 | Lot-state schema scope (Q39; consensus lean: defer, or a minimal slice) (§285) | 9 Nov |
| V16-P30, P31, P32 | H1 circularity fix (blind-first S gold, no gold in B4, pre-cut retrieval); H3 independent claim audit and sign test; MDE statement (§287.2–§287.4) | 10 Nov, before the D5 prereg is signed |
| V16-P35 | Step 35 firewall and naming (§288) | 10 Nov (T7-C01-R2) |
| V16-P27 | Mode → §141 crosswalk, including the editor's mappings of TARGET_ABSENT/CONTEXT_MISMATCH → `unsupported` (§286.7) | 11 Nov |
| V16-P08, P09 | Evaporation cap (DRY/FAT Layer-2 core fields SUPERSEDED; invariant test); surface/core zones (§284.3–§284.4) | 12 Nov (T4-C09-R1) |
| V16-P24, P25, P26 | INTERPOLATE bracketing; QUALITATIVE from unreviewed MECH entries; ASK flip-sensitivity (§286.4–§286.6) | 12 Nov (T5-C05-R4) |
| V16-P13 | What Layer 2 may feed, plus the Q1 ablation rule with a permuted-registry control (§284.8) | 12 Nov (T4-C22-R1) |
| V16-P01 | Adoption rule and timing: recommended "v15 governs through 26 Nov; v16 not applied" (§280.4) | 12 Nov (T0-C01-R1) |

### 5.2 Governance

| Id | Item |
|---|---|
| V16-P02 | Authority order: PART XIV may only add or tighten; on conflict, v15 wins (§280.3) |
| V16-P03 | The D-071 line and the human-only classes H1–H5 (§281.3) |
| V16-P04 | Record repairs (Parv's own ratification of D-071 and D-046; Kush's signed ratification of D-068); `ksh-AI`/`prv-AI` approvers; a `closer_type` column; signatures verified by signed commits; renaming the 15A-BOOT freeze record (§281.4, §287.8) |

### 5.3 Science and engineering design (after the talk unless pulled in)

| Id | Item |
|---|---|
| V16-P07 | REFERENCE class for food reference properties beside the two D-077 layers (§284.1) |
| V16-P10 | Geometry and shape factors (§284.5) |
| V16-P11 | Process-family coverage with validity domains (§284.6) |
| V16-P12 | Defaults/corpus-statistic rules, including a D-003 ruling for the BBC-derived KGE duration aggregates (§284.7) |
| V16-P14 | D-VAL physics validation (§284.9) |
| V16-P23 | Target-presence and lot-context gates; basis and liquid-fate checks; route enum v2 (§286.2–§286.3) |
| V16-P28 | AA SIMULATE domain gate; scientific-mode prerequisites beyond R-05 (§286.3, §286.8) |
| V16-P29 | Router census reporting as a funnel, with no coverage headline (§286.9) |
| V16-P33 | Reproducibility minimum (§287.5) |
| V16-P34 | Further evaluation and claim rules (§287.6) |
| V16-P36 | KGE duration loader selects the maximum `version` explicitly (§289 C-08) |

### 5.4 CR-level items (§290.4)

- **PROPOSED (37):** CR-02, 05, 08, 20, 22, 23, 24 (narrowed: D-045 W2 / D-060 ran the P1 pilot model-assisted), 25, 26, 27, 29, 35, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 52, 53, 54, 55, 56, 58, 59, 60, 61, 63, 64, 65.
- **PARTLY (12; the remainder is PROPOSED):** CR-01, 06, 07, 17, 18, 21, 30, 31, 36, 51, 57, 62.
- **APPLIED-BY-DECISION (12; become SSOT text only on adoption):** CR-03, 04, 09, 10, 11, 12, 13, 14, 16, 28, 32, 49.
- **HOLD (4):** CR-15, 33, 34 (the first-simulator anchor; D-052 made the plan-level selection, but the calibration set is acidic fruit liquids with leaching unidentified, so the CR's "vegetables in water" domain is unsupported); CR-19 (needs the H8 decision first).
- When a CR is applied, use the corrected line numbers of §289 C-16 (CR-32, 45, 46, 48, 59, 63). Rewrite the substance of CR-11, 31, 53 and 57 per §290.4 before applying.

## 6. Findings the humans should know (verified)

- **Rung A vs census:** Rung A = **9,470,190** events. 14,594,812 is the 26g census `engine_events`. The review packet conflates the two (C-01).
- **SVAR:** 355 version records = **224 distinct ids** (223 chemical, 1 physical). The registry also reserves 30 FUTURE ids, which the lot state should promote rather than duplicate (C-02, §285.10).
- **Defaults registry:** **27** data rows, not 28, all `SOURCE_UNVERIFIED_AGENT_RECALLED` (C-03).
- **COND:** 4,746 version lines = **4,414 distinct conditions**. Step 07 itself counts 4,414 (C-06).
- **Layer 2:** of the 810,951 computed scenarios only **69,995** have a core trajectory. Bath temperatures are 67.7 % defaults and durations 60.5 % corpus quantiles (C-04).
- **KGE durations:** 93 ACTIVE lines = **39 ids**, all versions of one row per process. The loader is correct today only because of file order (C-08).
- **D-028** is not in `DECISIONS.md`; only an unsigned draft exists. Its item 2 (MP-1 rulings C2–C8) is still open (C-12).
- **v15 invariant 16** (§230.3, L25162: "Gold labels should not be produced by showing annotators the model answer first") stays in force. So the model-assisted P1 labels must never be called Gold, and a D3 accuracy claim needs blind annotation (§287.6).

## 7. Open questions and human decisions

1. Adopt v16 now, partly, or after 26 Nov? (V16-P01; recommended after 26 Nov.)
2. R-06 vs D-075 (V16-P05): option (a) or (b), and who signs.
3. Should food reference properties (SR composition, SR portions, FDA pH) be a third class, REFERENCE (V16-P07), or sit inside Layer 2 as lane L-PH did?
4. `ph_interval`: promote SVAR-FUT-013 "pH / acidity" (editor's note) or mint a new id?
5. The TARGET_ABSENT / CONTEXT_MISMATCH → §141 mappings are the editor's proposals (REV-A gave no mapping).
6. Should inline `[superseded by §N]` markers be inserted into the v15 text when v16 is adopted? This draft keeps the v15 bytes intact and uses §290 as the marker list.

## 8. Limits

- PART XIV reproduces AI reviews (REV-A, REV-B) and an AI consensus plan. Their findings are AI_DRAFTED and NON_CITABLE until a human checks them.
- REV-A's 1,000-recipe DIRECT breakdown and the evaporation reproductions were not re-run by this lane; they are cited as REV-A results.
- The S176 lane drafts (`src/culinarystate/lotstate/`, the non-heat modules, `registry/*_draft_v1.csv`) are uncommitted and still changing. PART XIV cites them as drafts and does not depend on their content.
- The repo state described is `07fc0d2+uncommitted` as of 2026-11-08 ~14:30 UTC.
