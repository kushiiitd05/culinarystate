# D1: evidence resource and its limits (S179 report draft, 2026-11-11)

Status: AI_DRAFTED. All counts below describe imported records: E3_UNVERIFIED, COND_UNAUDITED,
BOOTSTRAP_UNVERIFIED, NON_CITABLE. This is a resource description, not a performance or evidence-quality claim.
New report assembly is AI_PRECHECKED; no human review of this new section is recorded.

## Sources, targets and tiers

The evidence resource contains **17,978 ACTIVE rows**, with **178 deprecated ids excluded**. Its sources are
Bognár (7,090 rows), USDA retention factors R6 (7,018), and Phenol-Explorer 3.6 (3,870). Every ACTIVE row is E3;
14,108 are UNVERIFIED and 3,870 AI_PRECHECKED. **Human-verified D1 rows: 0/40.** These are counts of database
imports, not independent primary experiments. Source: `reports/s178/analysis/evd_dataset_card_v1.json`,
`s203_9_1_total_rows`, `s203_9_6_evidence_tiers` and `labels`.

There are 224 SVAR target ids (213 canonical variables after duplicate mapping). By target subfamily, the row
counts are NUTRIENT_CONTENT 12,116; PHENOLIC_COMPOUND_CONTENT 3,870; GROUP_AGGREGATE 1,496; MASS_YIELD 496.
These categories sum to the ACTIVE total. Source: same JSON, `s203_9_5_target_types`.

## Conditions: preserve missingness

Every figure in this table is an E3_UNVERIFIED / COND_UNAUDITED diagnostic count. No UNKNOWN is filled with zero.

| Axis | MEASURED | Two-sided RANGE | One-sided censored | UNKNOWN | Not recorded | NOT_APPLICABLE |
|---|---:|---:|---:|---:|---:|---:|
| Temperature | 2,430 | 216 | 3,369 | 11,963 | 0 | 0 |
| Duration | 2,607 | 476 | 0 | 14,895 | 0 | 0 |
| pH | 0 | 0 | 0 | 17,978 | 0 | 0 |
| Moisture | 0 | 0 | 0 | 17,978 | 0 | 0 |
| Pressure | 129 | 0 | 0 | 0 | 10,831 | 7,018 |

Source: same JSON, `s203_9_9_condition_coverage.<axis>.rows_by_status`. Water activity is in the schema but
never populated (0/17,978). Temperature and duration are both stated on 1,575 rows (8.76%), all from
Phenol-Explorer. A stated condition does not imply it has been checked against the primary paper.

## Supply against recipe demand

The paired coverage analysis is distinct from condition completeness. EVD has 338 routable (ING, PROC) pairs.
A seeded 1,000-recipe non-BBC sample has 12,501 distinct pairs, of which 111 (0.89%) have an EVD pair.
At process level, 63.47% of 4,724,493 non-BBC process events use a process with some EVD row; this is an upper
bound that ignores the ingredient. For vitamin C, 102 of 125,172 full-corpus distinct pairs have an EVD pair
(0.08%). Source: `reports/s178/evd/evd_coverage_vs_corpus_demand_v2.json` and its companion Markdown table.
These are different denominators and must not be collapsed into one coverage percentage.

Figure for report/deck: `reports/s178/evd/fig_evd_coverage_by_family_v2.svg`, whose adjacent JSON/CSV carry the
numbers. Its caption must retain NON_CITABLE / E3_UNVERIFIED / COND_UNAUDITED and distinguish full-corpus
process counts from sampled pair counts. Tables above are the source/target and condition panels; no new
scientific run was performed for this section.

## Lineage and permitted interpretation

There are 127 provisional independence groups: Bognár 1, USDA 1 and Phenol-Explorer 125. The feasibility report's
headline under reading A is **publication-component CV**, not confirmed study-disjoint evaluation. Reading B,
which also requires human verification, has zero eligible rows and uses leave-one-source-family-out.
Source: dataset-card JSON `s203_9_7_study_source_counts` and
`exports/lineage/step08a_v1/feasibility.json` / `feasibility_report.txt`.
The human edge audit G08-3 is FAIL; exact audit counts and slide wording are in
`S179_H2_and_lineage_statements_DRAFT.md`. Imported row count cannot be read as independent study count.

No claim is made about comprehensive chemistry coverage, primary-paper correctness, study-independent
prediction, or human-verified evidence. Phenol-Explorer raw-table redistribution remains restricted; only
counts and ids enter this section. See `S179_licence_and_split_labels_DRAFT.md` and D-079.

Acceptance remaining: human review of this new section/figure captions and incorporation into the final report
and slides. D-079 accepted earlier drafts; it is not a review of this newly written section.
