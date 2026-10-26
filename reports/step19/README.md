# Step 19-D / 19-pilot — Deep Gold PILOT design: index and human-decision checklist

**Status: DRAFT_PENDING_H4 / H5.** Written 2026-10-26 under D-027 ruling R-17 (Plan section 4.2 lane L7), with R-08, R-19 and R-20; revised the same day after the round-3 reviews (governance Review A, science Review B). Design only. No recipe was drawn, no packet built, no annotation exists, no tool was run or edited, nothing is signed, and **Step 08 is not started**. All numbers are PROPOSED_PILOT. Local ids in this lane: decisions `D19-n`, checks `PV-n`, packets `DGP-` (none is a ledger id or a DECISIONS id; the `D-0nn` ids below are DECISIONS entries).

## 1. Index

| Path | Bytes | What it is |
|---|---|---|
| `reports/step19/deep_gold_pilot_design_v1_draft.md` | 98,402 | The 19-D design: goal and questions, verified facts, sample (frame, exclusions, 07I-S grouping, strata and quotas, seeded draw, reserves, locks), independence protocol (packets, hash commitments, provenance-validity check with a planted-pair test, handbook freeze and Addendum B), timing sheet, IAA plan with CIs and what n supports, adjudication, schema-problem log, stop/scale decision rule for H5/H8, hours cap; Appendix A = 35 proposed 01.6 rows `THR-19P-01..35` (CSV block, **not** written to the registry; rows 31-35 are new in the round-3 revision); Appendix B arithmetic; Appendix C templates |
| `reports/step19/README.md` | (this file) | index and checklist |

Planned but **not created** (Plan Step 19 outputs, produced only after approval): `reports/step19/{pilot_iaa_report.md, pilot_timing_v1.csv, pilot_representability_v1.csv, pilot_schema_problem_log.md, pilot_provenance_check.json}`; **git-ignored, local only:** `annotation/gold/deep_gold_pilot_v1/{A,B,adjudicated}/` (labels and recipe text); **tracked, text-free:** `registry/recipe_semantics/deep_gold_pilot_v1/{manifest_<wave>.csv, commitments_<letter>_<wave>.json, sealed_key_<wave>.sha256}` and `registry/recipe_semantics/deep_gold_pilot_{frame,tag_rules}_v1.csv`; and **six scripts**: (1) frame builder + seeded draw, (2) packet maker + sealed key, (3) commit step, (4) provenance checker + planted-pair test, (5) agreement wrapper, (6) pilot report script.

## 2. What was and was not touched

- Created: `reports/step19/` with the two files above; both were revised in place on 2026-10-26 (round-3 fixes). No tracked file was modified, `.gitignore` was **not** edited, and `registry/preregistered_thresholds_v1.csv` was not touched (the 35 proposed rows are an appendix). The only repo commands run for the revision were read-only `git check-ignore -v` probes of candidate paths.
- Not touched: every existing file, including `registry/preregistered_thresholds_v1.csv` (read for format only; the proposed rows are an appendix), `tools/gold_cli.py`, `tools/gold_pilot_agreement.py`, `tools/bundle_gold_packs.py`, `tools/make_independent_gold_packs.py`, `annotation/*`, `ledgers/*`, `registry/*`, `reports/{gold,del3,step04,step07,step07i}`, the plan, `DECISIONS.md`, `WORKLOG.md`, `STATUS.md`.
- Read-only facts used (ids, counts, hashes, structure only): `ledgers/recipe_base/{recipe_base_v1,gold_recipe_index_v1}.parquet`, `ledgers/recipe_identity/*.parquet`, the annotation manifests and the S116 screening log. **No ingredient or instruction text of any recipe was opened and no title was read from the recipe base.** (Committed manifests such as `annotation/batches/pilot_20.csv` carry titles/URL slugs of the already-excluded BBC pilot recipes; a few were incidentally visible in command output and are not used.) No git write command, no pipeline, no model.

## 3. Things in this draft that differ from, or sharpen, the brief and the plan

1. **Exclusion list is a superset.** The brief said "exclude the 20 AI-assisted Food.com ids". The plan card excludes 40 AI-assisted recipes (20 BBC + 20 Food.com, the BBC set including the 7 calibration recipes), the S116 20 Food.com recipes and title twins. `gold_recipe_index_v1` holds 50 ids (those 40 + 10 screened Food.com reserves) and the S116 screening log touches 120 Food.com recipes. The draft excludes all 50 + the 90 further screened ids + their groups + title twins (`THR-19P-03`). The 20 Food.com ids are a subset.
2. **Gutenberg and TASTEset cannot be sampled**: Gutenberg segments have 0 ingredient lines and TASTEset has 0 steps, so the gold-1.0 template cannot hold them. This is logged as a representability gap, not sampled.
3. **BBC text is not on this server** (the old batch tool reads the Mac path `../a1/A1 3/...`); the frame/packet steps must run where the text is.
4. **The existing agreement tool's independence label is a default**: it prints `INDEPENDENT_HUMAN_VS_HUMAN` whenever no file carries the notes marker `AI_DRAFT_HUMAN_REVIEWED`. The draft makes the provenance check, not the tool, decide whether "independent" may be printed.
5. **Its category rate is deflated** for matched pairs (denominators sum both annotators' units). The 20% rule is kept verbatim for comparability (`THR-19P-16`) and the review gate now fires on max(tool rate, per-pair-normalised rate) > 0.20 (`THR-19P-31`, supersedes `-16` for gating only; nothing is weakened).
6. **n = 20 supports little** (Section 7.4 of the design): pooled F1 near 0.85 to about +/-0.06-0.10, kappa at high prevalence not at all, "0 unrepresentable phenomena" only to an upper bound of 13.9% of recipes, minutes per recipe to about multiply-or-divide by 1.26-1.39. The pilot is feasibility and falsification, not certification.
7. **The 40 h cap binds at about 93 min per recipe** (with 6 h adjudication); a capacity check sits between P1 and P2.
8. **Independence artefacts live on a tracked path (round 3, review A #5).** `.gitignore:9` (`annotation/gold/*`) ignores everything under `annotation/gold/deep_gold_pilot_v1/` (checked with `git check-ignore -v`), so commitments and manifests left there would be skipped by a plain `git add` and the commitment-before-key-opening control could not be timestamped. Manifests, commitments and the sealed-key hash (ids, hashes, sizes, times; no recipe text) therefore go to `registry/recipe_semantics/deep_gold_pilot_v1/` (not ignored); labels and recipe text stay in the ignored folder; new check PV-9 requires `git ls-files --error-unmatch` to succeed before the sealed key is opened. The plan card's output layout names the ignored path, so the integrating session has to reconcile it (D19-18).
9. **Routing and stop rules are split and tightened (round 3, review B).** Alpha cut-offs apply to categorical families (`THR-19P-18`); the same numbers on F1 are only a routing convention (`THR-19P-35`). STOP-SCHEMA also fires on >= 2 recipes with an adjudicated BLOCKING SCHEMA_GAP / HANDBOOK_GAP item on one family, whoever logged it (`THR-19P-32`); the old both-annotators rule stays as a supplementary trigger; a per-recipe representability checklist makes silent schema debt visible (`THR-19P-33`). Bound-reading rules use the most conservative of three intervals (`THR-19P-34`). The question log is write-only during a wave; provenance values are recorded at commitment time (PV-3, PV-10).

## 4. Human-decision checklist

Tick when decided; the design's default is given. Hours are the plan's estimates (UNVERIFIED): design approval and 01.6 signature Kush ~2-3 h, Parv ~2-3 h (Plan section 4.5).

**Numbering.** All local decision ids were renamed `D-n` -> `D19-n` in round 3 (review A #9: `D-n` collided with the DECISIONS family and the README had both `D-16` and `D-016`); `D19-1..D19-16` are the earlier items with their old numbers, `D19-17..D19-25` are new. Count: **25 items** (16 renamed, 9 new) plus the signature item. `D-016`, `D-017`, `D-024`, `D-027` below are DECISIONS entries and keep their ids.

**Approvals before anything runs (H4 / H5)**
- [ ] **D19-1** (was D-1) Approve the frame: sources (BBC, Food.com under the S116 Gate-1 local-research decision, Wikibooks), caps (4-20 ingredient lines, 2-15 steps), quotas BBC 6 / Food.com 10 / Wikibooks 4, tiers LOW 5 / MID 9 / HIGH 6 (`THR-19P-02,05,06`). *Open sub-question: is Food.com acceptable at all while its source is unregistered and the S116 eligibility screen is unconfirmed?*
- [ ] **D19-2** (was D-2) Confirm the exclusion list is the superset (`THR-19P-03`).
- [ ] **D19-3** (was D-3) Kush supplies the seed nonce **before** the frame is inspected; decide who runs the draw (`THR-19P-08`).
- [ ] **D19-5** (was D-5) Core vs secondary fields and the 0.80 / 0.667 routing; the falsification rule (`THR-19P-17..19`, `-35`).
- [ ] **D19-19** (new) Split the routing cut-offs: alpha on categorical families (`THR-19P-18`), F1 on span / event / edge families as a routing convention only (`THR-19P-35`); unitizing alpha as an optional diagnostic.
- [ ] **D19-20** (new) STOP-SCHEMA: add the any-logger adjudicated rule (`THR-19P-32`), keep `THR-19P-26` as a supplementary trigger, add the per-recipe representability checklist and the silent-schema-debt count (`THR-19P-33`).
- [ ] **D19-22** (new) Interval rule for decisions that read a bound: the more conservative of percentile, BCa and cluster-level t (`THR-19P-34`); all intervals are conditional on annotators A and B.
- [ ] **D19-7** (was D-7) 120-minute time-box with right-censoring (`THR-19P-13`).
- [ ] **D19-14** (was D-14, reworded) Keep the tool's 20% rule (`THR-19P-16`, unchanged, kept for comparability) and gate on max(tool rate, per-pair-normalised rate) > 0.20 via the new row `THR-19P-31`, or choose differently (a different gate needs a new row, never an edit of the old one).
- [ ] **D19-15** (was D-15) Run on the CURRENT contract (v0 schemas + handbook v1 + Addendum A), no pre-pilot edits.
- [ ] **D19-17** (new) The `S_max = 500` sub-blocking clause of `THR-19P-04` (Plan 'Reading conventions' conflict #4, R-08 versus the giant-component guard; the value was fixed after the largest component, 261, was seen): confirm or drop. Default: dropped if not confirmed (whole component excluded; no effect today).
- [ ] **Sign the 35 rows** `THR-19P-01..35` in `registry/preregistered_thresholds_v1.csv` (Step 01.6) with `data_seen_before_registration` as proposed (Appendix A; row 03 is now `DESCRIPTIVE_COUNTS_SEEN`). Nothing is drawn before this.

**Independence and exposure**
- [ ] **D19-4** (was D-4) Accept the exposure limitation (Kush reviewed 40 AI-drafted recipes; Parv's approval was relayed) or attest otherwise for specific recipes. The adjudicated set's name records the exposure (D19-13).
- [ ] **D19-12** (was D-12) Confirm the exposed S116 blank bundle is **not** reused.
- [ ] **D19-11** (was D-11) Confirm pilot content stays local-only (BBC local-only; Food.com text never committed; Gold text release blocked until H2, SSOT section 250.7).
- [ ] **D19-18** (new) Tracked location of the independence artefacts (`registry/recipe_semantics/deep_gold_pilot_v1/`; `.gitignore` not edited) and check PV-9; the integrating session reconciles the plan card's output path.
- [ ] **D19-21** (new) Commitment-time provenance values (packet id, sha256, size, mtime) and >= 2 interim snapshots per file (PV-3 on recorded values, PV-10); accept the annotators' extra step (`snapshot` at the first `validate` and at `DONE`).
- [ ] **D19-23** (new) The question log is write-only during a wave; answers only after both commitments; no convention change inside a wave (anchoring control).
- [ ] **D19-25** (new) PV-7 restricted to fields with dominant-class share < 0.95; chance-corrected identity (p_o - p_e) / (1 - p_e) >= 0.98 for the others.

**Design choices**
- [ ] **D19-10** (was D-10) P2: coverage-greedy (default) or pure stratified random.
- [ ] **D19-6** (was D-6) Third reviewer / expert for cultural cases (0-4 h) or not.
- [ ] **D19-16** (was D-16) Timing by phase (READ_PLAN / LABEL / VALIDATE_FIX) or one total per sitting.
- [ ] **D19-13** (was D-13, reworded) Name and status for the adjudicated pilot set in tier registry v2 (19-R, H4) - proposal only: `pilot development Gold, blind two-annotator (independent only if pilot provenance check PASS), prior AI exposure of annotators recorded, design pilot`.

**Capacity and scheduling**
- [ ] **D19-8** (was D-8) Kush sets weekly hour capacity for Kush and Parv; P1 inside the next 30 days, P2 after 07I-C labelling closes; never interleave 07.A / 07I-C packets with pilot sittings.
- [ ] Per-annotator budget **B_h** for the later GO-40 test (`THR-19P-27`); no default exists.

**Build authorisation and ids**
- [ ] **D19-9** (was D-9, reworded) Authorise the agent to write the **six scripts** for human review: (1) frame builder + seeded draw, (2) packet maker + sealed key, (3) commit step, (4) provenance checker + planted-pair test, (5) agreement wrapper, (6) pilot report script; none exists today. The existing tools are reused, not edited.
- [ ] **D19-24** (new) Register `DGP-` as a local packet label (not a ledger id) in the 04.9-min section 4 table, or rename it to a file-name token, and re-run the section 5 collision scan.

## 5. After the decisions (order of work)

1. Sign the 01.6 rows (Kush; Parv co-signs) -> 2. build the frame on the machine that holds the text, hash it, apply the nonce, draw P1, freeze the manifest -> 3. issue P1 packets (separate ids, own machines) -> 4. P1 annotation with timing and private schema-problem logs -> 5. commitments tracked in git (PV-9), provenance check (FAIL => NOT_COUNTED), agreement run, joint adjudication (incl. the schema-problem items), Addendum B decision -> 6. capacity check -> 7. after 07I-C closes, draw and run P2 -> 8. pilot report and go / no-go memo to 16c and 19-S. The pilot never authorises 19-M or N > 40; those need a separate H5 / H8 decision.

## 6. Cross-references

**Logging (review A #36).** CLAUDE.md asks that each step is logged with `tools/log_step.py`; this lane did not log (a WORKLOG entry would modify an existing file). The integrating session should log it with `--files` the two Step-19 paths and `--verify` 'git diff --stat on tracked files empty; Appendix A row check (35 rows, 16 fields, unique ids)'.

Plan v2 Step 19 and Step 16 cards (16b shares the sampling frame; 16c consumes the pilot outputs); Phase D facts 1-2; `reports/del3/gold_pilot_7_calibration.md`, `gold_pilot_20_v1.md`; D-016, D-017; `reports/step04/README.md` (for the 07I-S / `SPLITGRP-REC-` plane rule and the 01.6 row format); Audit v2 section M.8 and `r_recipe_semantics_gold.md` (anchoring evidence, sample-size arithmetic).
