# S178 lane FIX-PHYS: report (v05 re-runs finished S179)

Status: AI_DRAFTED (D-071). Nothing here is a decision, signature or approval. Code: branch `kush/s179-finish-fixes`
(snapshot `max/s178-wip` 6f8d1bc, which holds the fixer's code: heat and non-heat Layer 1 0.3.0, Layer 2 0.5.0; plus the
Mac composition merge 1c21191, which does not touch `simulation/`). The fixer agent wrote the code and tests (86 pass); it
stopped before the v05 re-runs. They were run in S179: non-BBC on manjot (same seed 20261104, same commands and worker
counts as RUN-S178-PHYS2-*), BBC on the Mac (D-003).

## 1. Runs

| what | where | rows |
|---|---|---|
| 1,000 sample: heat L1, heat L2, non-heat L1 + L2 | manjot | RUN-S179-PHYSNB-001..003 |
| full heat L1 + L2 per family (WIKIBOOKS, TASTESET, GUTENBERG_SEGMENT, FOODCOM) | manjot | RUN-S179-PHYSNB-004..011 |
| full non-heat per family | manjot | RUN-S179-PHYSNB-012..015 |
| schema validator x4, endpoint cues, sensitivity, stated liquid, record audit, v04 -> v05 comparison | manjot | RUN-S179-PHYSREP-016..024 |
| BBC heat L1, heat L2, non-heat; schema validator | Mac | RUN-S179-PHYS-001..004 |

Every report has `code_unchanged_during_run` true, `contains_text` false and the ledger baseline PASS_BEFORE_AND_AFTER.
Layer 1 binding census exit code 3 = A1_BBC INPUT_MISSING on manjot (D-003), as in every non-BBC run.

## 2. Results

- **Schema validator: 100 %.** Non-BBC: 384 heat L1, 384 heat L2, 768 non-heat L1, 768 non-heat L2 record files,
  0 problems, every ratio 1.0. BBC: 16 files per kind, 0 problems.
- **Same events, same statuses.** Heat events 1,696,743 in v04 and v05; heat L2 SCENARIO_COMPUTED / UNKNOWN /
  UNSUPPORTED_MEDIUM unchanged per family (Food.com 667,634 / 768,753 / 66,874). The fixes change bindings and flags,
  not which events are computed.
- **SCI-A targets (record audit, all non-BBC families, v04 -> v05):**
  - moist-piece core above T_boil 12 -> 0; lifted TYPICAL core above 100 °C 12 -> 0; lifted TYPICAL above 150 °C 21 -> 5;
  - lifts without a solute-rich member 123 -> 2 (the stricter cap lift: owned temperature + solute / syrup / pressure cue);
  - fat-heat temperature taken from a setter step 460 -> 190; aqueous above 100 °C from a setter 10 -> 3;
  - until-clause temperatures bound by the reviewer method 869 -> 438, now carried as clause spans (475);
  - oven temperatures stated below 77 °C 318 -> 189.
- **Flag renaming, not new physics:** TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER (162,378 TYPICAL) is replaced by
  SUGAR_PHASE_TBOIL_LOWER_ESTIMATE (112,352) and SALT_MEMBER_BPE_SMALL (68,558). New cues: syrup stage 50,733 records,
  pressure 1,102, water bath 493 (WATER_BATH_IN_OVEN, bounded by the T_boil upper bound).
- **Food.com Layer 1:** driver-ready events 55,662 -> 57,417; driver-bounded 87,139 -> 89,882 (more temperatures bound
  from the food's own clause; CARRIED_SETPOINT basis 70,835 -> 73,761).
- **BBC v05 (first BBC run since S173):** 11,934 recipes, 49,662 heat events, 1,167 driver-ready. No BBC v04 exists and
  none was made (SCI-A found v04 Layer 1 errors).

Full tables: `reports/s178/phys/v04_to_v05_comparison_S178.{json,md}`, `fixphys_audit_S178_v05.json`,
`sensitivity_S178_v05.*` (joint-corner caveat kept), `endpoint_cue_counts_S178_v05.*`,
`stated_liquid_t_before_after_S178_v05.*`.

## 3. Superseded

v04 reports `reports/step26/*_S178_v04.json` -> `*_S178_v05.json`; the v04 schema, endpoint, sensitivity and
stated-liquid reports -> their `_v05` versions. Recorded in `registry/superseded_outputs_S176.csv` (S179 rows); older rows
that pointed at v04 now point at the live v05 file, with the old target kept in the reason.

## 4. Not done / for the next session

- **v04 per-record files under `data/derived/` on manjot are NOT deleted.** The brief allows it after v05 validates; it is
  irreversible and left for Kush to approve. Directories: `physical_*_S178v04*`, `physical_NH_*_S178v04*`.
- `tools/s178_analysis_corpus_can_say.py` and `tools/s178_evd_coverage.py` still name v04 / S177 inputs, which are now
  registered as superseded; re-point them to v05 / S179 before their next run (the guard refuses superseded inputs).
- MECH on v05: run in S179 (see `S178_FIX-ROUTER_report.md` §5).
- Short re-review (one GOV, one SCI pass) of the fixer code is still owed (`MAC_CLAUDE_MERGE_PROMPT_2026-11-09.md` §2.5).
