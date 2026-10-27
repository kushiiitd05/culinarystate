# Step 08a.0: preregistration (v1, written 2026-10-27, before any lineage edge, key or label is computed)

Authority: D-027 (R-03, R-09), D-029 (04.1 approved), D-030 (THR-08A-01..23 signed), D-031 (Mac, manifest v1, baseline hashes), D-032 and its addendum (08a authorised; `registry.py` port allowed; `_ids.jsonl` may grow after a scratch dry run shown to Kush). Nothing below changes a signed threshold. Where this text and `registry/preregistered_thresholds_v1.csv` differ, the CSV wins.

## 1. Scope
Lineage resolution for the existing 17,978 ACTIVE EVD rows. New files only, plus the allowed `registry.py` port and one append to `STUDY.jsonl`. EVD, COND, SRC, MEAS stay byte-identical (THR-08A-06; baseline `registry/baseline_ledger_hashes_08a_v1.csv`). Not authorised: 08b, 07.A or 07I-C use, any push. 07.A is a soft dependency (R-05) and is currently `FAIL_REVIEWER_DISAGREEMENT` on its registered statistic (`reports/step07/step07_v4_adjudication_result.md`); 08a does not use it.

## 2. Gates (all signed 2026-10-27 or 2026-10-26 by Kush; values in the CSV)
| Gate | Rule in one line | Row(s) |
|---|---|---|
| G08-1 coverage | 100% of 17,978 rows get study_id_status, independence_resolution, lineage_root_id, split_group_id | THR-08A-01 |
| G08-2 | 0 DRV rows whose parents sit in different split groups (hard stop) | THR-08A-02 |
| G08-3 edge precision | audited-edge 95% Wilson lower bound >= 0.90; about 150 edges, at most 7 errors in 150; per stratum n >= 50 (B2, B3, STRONG) | THR-08A-03, 04, 16 |
| G08-4 recall | seeded-copy recall >= 0.95 per perturbation class (scratch only); natural-duplicate recall estimate from a blind 200-pair review, report only | THR-08A-05, 17, 18 |
| G08-5 | 0 byte differences in EVD/COND/SRC/MEAS; STUDY append-only; export v1 untouched | THR-08A-06 |
| G08-6 | two independent rebuilds identical | THR-08A-07 |
| G08-7 giant component | largest split-group share > 40% forces the label "publication-component CV" and leave-one-source-family-out, never "study-disjoint"; refinement: eligible pool, Kish n_eff >= 10, weaker label wins | THR-08A-08, 09, 15, 20 |
| G08-8 | 0 fabricated study_id (every non-NOT_IDENTIFIABLE study_id has a DOC locator) | THR-08A-10 |
| G08-9 | USDA-Bognar overlap verdict recorded before cross_source_v1 agreement is reused | THR-08A-11, 23 |
| G08-10 | 0 nesting violations (study within lineage_root within split_group) and no key aliasing | THR-08A-12 |
| G08-H | human edge audit: two reviewers, files not identical, counts_as_human_gate = true | THR-08A-13 |
Other signed rules: PROVISIONAL edges merge conservatively (THR-08A-14); UNKNOWN-independence screen at the loosest B3 score with seeded recall >= 0.95, frozen before real rows are screened (THR-08A-19); hub rule (THR-08A-21); same-lab window N = 3 years (THR-08A-22).

## 3. Run policy
1. `lineage.guard.verify_baseline` before every run; abort on any mismatch. Writes only to scratch or to the named new files (`assert_safe_write_target`).
2. A full dry run on a scratch copy of `ledgers/data` first; its counts are shown to Kush before the real run (D-032 addendum). `_ids.jsonl` is re-hashed after the dry run.
3. Seeded copies live in scratch only. A failed gate stops the run and is reported; no gate is loosened (R-20).
4. Environment: the Mac; vinayak only if a run is heavy (D-031).

## 4. Work packages (from the Plan v2 card)
08a.0 this document and the guard (done: `src/culinarystate/lineage/guard.py`); 08a.1 DOC records; 08a.2 STUDY versions; 08a.3 detectors B0-B3 and STRONG and LIN edges; 08a.4 USDA-Bognar overlap verdict; 08a.5 keys by union-find, DRV parent union, independence registry; 08a.6 component-feasibility report; 08a.7 EVD export v2 (additive); 08a.8 audit packets and the recall tests; 08a.9 gate JSON and freeze manifest. Plus the `registry.py` schema port (D-029 D-6).

## 5. Contract ambiguities decided conservatively in the first work package (flagged for Kush)
1. Hub rule: a hub's links are dropped only when they would join two or more distinct primary-bearing components; hub-to-hub links are always dropped. Independent of edge order.
2. Key aliasing is checked only as string equality across the three key levels; the contract gives no machine definition of "aliasing by naming convention".

## 6. What needs people
Two reviewers (Kush and Parv, separate files) for the roughly 150-edge audit (2-4 h each) and the 200-pair natural-duplicate recall review; an expert reading of the USDA-Bognar overlap before Step 15. Without them 08a ends at "G08-3 pending", never PASS.

## 7. Sign-off
Kush: signed through D-030/D-032 (2026-10-26, 2026-10-27). Parv: the Plan v2 card asks for both; Parv's sign-off is NOT recorded here.
