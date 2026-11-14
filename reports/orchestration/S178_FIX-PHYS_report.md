# S178 lane FIX-PHYS: report (v05 re-runs finished S179; v06 after the re-review, §5)

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
- `tools/s178_analysis_corpus_can_say.py` and `tools/s178_evd_coverage.py` named v04 / S177 inputs: re-pointed to v06 /
  router 0.4.1 and re-run in S179 (v2 outputs; `S178_ANALYSIS_report.md` and `S178_EVD_report.md`, S179 corrections).
- MECH on v05: run in S179 (see `S178_FIX-ROUTER_report.md` §5).
- Short re-review (one GOV, one SCI pass): done S179, `reports/orchestration/review/S179_REV_{GOV,SCI}.md`; it led to v06 (§5).

## 5. v06 re-run (S179b, after the SCI re-review)

Code: `endpoint_cues` 0.3.0 / condition-binding L1 0.3.1 (SCI #1, M1 residual: food targets such as "165 F inside" or
"N F for medium" were bound as the medium temperature). Layer 2 code unchanged (0.5.0). Commit bf2e635.

| what | where | rows |
|---|---|---|
| 1,000 sample, full heat L1 + L2 and non-heat per family (same seed and commands as v05) | manjot | RUN-S179-PHYS6-001..015 |
| schema x4, endpoint cues, sensitivity, stated liquid, record audit v06, role-aware re-audit of v05 | manjot | RUN-S179-PHYSREP6-016..024 |
| BBC heat L1, heat L2, non-heat, schema | Mac (D-003) | RUN-S179-BBC6-001..004 |

- **Schema validator: 100 %.** Non-BBC 384 / 384 / 768 / 768 files, BBC 16 per kind; 0 problems, every ratio 1.0.
- **Same events.** Heat events 1,696,743; Layer 2 computed 793,456 (v05 and v06). Non-heat Layer 1 identical in every family;
  non-heat Layer 2 one count differs (Food.com RESTING prior-heat bath missing 3,053 -> 3,054).
- **Record audit, v05 (re-audited with the SCI #3 tool) -> v06, all non-BBC families:**

| counter | v05 | v06 |
|---|---:|---:|
| text-stated temperatures bound to the medium (DRY / HEAT_GENERAL / WET / FAT) | 51,121 | 51,001 |
| food-target cues, Food.com / Wikibooks / Gutenberg | 3,326 / 154 / 21 | 3,457 / 168 / 26 |
| oven temperature stated below 77 °C (core computed) | 189 (14) | 171 (12) |
| until-clause temperatures, reviewer method | 438 | 427 |
| clause-span temperatures: syrup / candy exempt; other roles | 475; 0 | 513; 0 |
| lifted TYPICAL (solute member yes / no); above 150 °C | 166 (164 / 2); 5 | 163 (161 / 2); 5 |
| aqueous above 100 °C (from a setter) | 330 (3) | 326 (3) |
| fat-heat temperature from a setter | 190 | 190 |

  Food.com Layer 2: bath temperature from Layer 1 610,770 -> 610,719 (51 events moved to the scenario default).
- **BBC v06:** TEXT_STATED temperatures 5,669 -> 5,664; food-target cues 80 -> 90.
- The v05 audit file `fixphys_audit_S178_v05.json` used a key that never existed (exempt count always 0); it is superseded by
  `fixphys_audit_S178_v05_rerun_S179.json` (same v05 records, fixed tool). `tools/s178_fixphys_v05_comparison.py` is
  fixed to v04 -> v05 names, so the v05 -> v06 table is here, not in a new comparison file.
- The 2 lifts without a solute-rich member remain: SCI #2 (lift gate fires on dilute liquids) needs Kush's ruling (Q1).
- `verification_pack_S178_v05` checks the drivers only (unchanged since v05) and stays current.
- Superseded: every `*_S178_v05` report above and the BBC `*_S179_v05` reports -> their v06 files
  (`registry/superseded_outputs_S176.csv`, S179 rows; older rows re-pointed to the live v06 file).
- v05 and v04 per-record dirs on manjot are kept (deleting needs Kush's OK).
