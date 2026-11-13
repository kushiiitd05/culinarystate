# 36-step pass-gate audit — 13 Nov 2026

AI audit (ksh+prv, D-085; four parallel read-only agents), every pre-registered pass-gate clause in
 checked against an existing artifact. Clause rows:
. AI_PRECHECKED · NON_CITABLE · AI_VERDICT_PENDING_HUMAN_REVIEW.

**Steps:** 0 COMPLETE · 2 COMPLETE_WITH_RECORDED_FAILURE (07, 08) · 18 PARTIAL · 7 NOT_STARTED · 5 BLOCKED · 4 CUT.
**Clauses (269):** 67 MET · 12 MET_AI_DELEGATED · 9 FAILED_RECORDED · 116 NOT_MET · 36 NOT_EVIDENCED · 29 NOT_APPLICABLE.

Most declared plan output paths do not exist; work was done under other paths, so verdicts follow the gate conditions, not file names.

| Step | Title | Verdict | To close |
|---|---|---|---|
| 01 | Freeze project authority | PARTIAL | To close: create plan_authority_map_v1_1.csv (+ABSENT rows) and namespace_registry_v1.csv; register 07I-S and 09 THR rows (data_seen=N); move signed THR-08B rows into v1 registry |
| 02 | Audit implementation state | PARTIAL | To close: write reports/step02/count_definitions_v1.md reconciling all listed counts in one place (families and similarity included) |
| 03 | Freeze state semantics | NOT_STARTED | To close: write clock_registry_v1.csv + state_representation_contract_v1_1.md (03.3/03.9), run 3 scratch negative controls, record approval (AI_DELEGATED under D-085) |
| 04 | Freeze evidence / provenance / similarity contracts | PARTIAL | To close: run 04.2-min dry-run on scratch copy; add EXTERNAL_VERIFIED-on-aggregate control to export-v2 validator; materialise the 7 declared registry CSVs (README says not created) |
| 05 | Normalize EVD | PARTIAL | To close: add 05.1 card fields (explicit statuses) as v2.1 export; write evd_export_v2.schema.json + independent v2 validator and run it |
| 06 | Freeze source acquisition manifest | NOT_STARTED | To close: record H2 #1/#3/#4 decisions (AI_DELEGATED under D-085 if accepted); build manifest v1_1 with two new columns, UNKNOWN where not documented |
| 07 | Condition & measurement normalization | COMPLETE_WITH_RECORDED_FAILURE | To close: none possible under D-085 for 07.A/07I-C (needs new independent human labelling); write v4 gate-result JSON with counts_as_human_gate; register 07I-S reference |
| 08 | Scientific source lineage | COMPLETE_WITH_RECORDED_FAILURE | To close: G08-3 stays FAIL (needs new human edge audit); copy gate_report/freeze manifest into reports/step08; G08-7 cell verdicts need a new pre-registered THR-08A-09 cut-off |
| 09 | Evidence extraction & verification machinery | PARTIAL | To close: board marks T2-C08-R1/R3 POST; needs golden fixtures + seeded-error suite + KIN/KINPT/XTR/ADJ schemas + signed accuracy prereg + step09_gate_result.json |
| 10 | 20-row mechanism pilot | PARTIAL | To close: independent (human) dual extraction and verification of AA rows into KIN/LIN with schema validation; >=100-abstract double-labelled triage for AA and CHL; publish kinetic_series_availability_v1.csv (AA+CHL, Wilson CIs) and field_reporting_rates_v1.csv; PROVISIONAL 10a DECISIONS entry; step10_gate_result.json. |
| 11 | Wave-1 verified mechanism evidence | NOT_STARTED | To close: acquire licensed full texts (e.g. AAK-02/04/05/08/10), run dual independent verified Wave-1 extraction to >=40 rows in >=6 families with acquisition log and hashed partition lock, then record 11.D. |
| 12 | Structured database evidence | PARTIAL | To close: in 15a.1, ingest R2/Bognar remainder with full field set, run >=75-row/source transcription audit with 0 errors, publish aggregate_bibliography_edges_v1.csv, structured_wave_a_report.md, step12_gate_result.json. |
| 13 | Large literature discovery corpus | PARTIAL | To close: run 13a discovery with query log and licence table, score known-item recall on the evaluation half of the 713 seeds, pre-register triage precision, publish discovery_corpus_report.md and step13_gate_result.json. |
| 14 | Coverage-driven evidence growth | NOT_STARTED | To close: publish consumer_readiness_v1.json (NEED_DATA is a valid verdict), coverage_cells_v1.csv in lineage units and declared_gaps_v1.csv; cheap, no new data needed. |
| 15 | Freeze DATA-EVIDENCE v1 | BLOCKED | To close: a valid 07.A-R1 pass by two independent humans, a human-verified held-out subset, and a Step-11 partition lock; then freeze 15b with evd_export_v2, split_feasibility_v1.md, 257I.6 checks and a manifest. |
| 16 | Instruction semantic schema | PARTIAL | To close: run P1b, re-encode 20 pilot recipes in v1 with a representability audit, add 3 corrupted-text controls to the hard-case catalog, then the 16c H4 freeze and step16_gate_result.json. |
| 17 | Instruction-level extraction | PARTIAL | To close: stratified invented-value audit >=300, per-field error table on a declared dev partition (DESCRIPTIVE), oracle cascade, source-disjoint report, step17_gate_result.json. |
| 18 | Event-sourcing engine | PARTIAL | To close: persist v1 Gold-scope ledgers (18a), implement transition_tuples/prefix exports, run the oracle-vs-predicted state report on adjudicated Gold, step18_gate_result.json. |
| 19 | Gold state-trajectory pilot | PARTIAL | To close: run P1b (needs Kush's human-only nonce + signed start-record amendment, D-071) with timing and a real-packet provenance check, then write the 19-S go/no-go memo; or record a formal no-go/scope cut for 19-M. |
| 20 | Scale procedural semantic corpus | CUT | To close: none; keep the H8-04 wording in the report (scope cut signed AI_DELEGATED, not human). |
| 21 | Effect / mechanism ontology | PARTIAL | To close: source every entry (G21.4), build PROC->MECH crosswalk 156/156, xref table + collision audit, independent dual-blind human review (G21.6 cannot be AI-delegated, D-088), then mint ledgers/data/MECH.jsonl. |
| 22 | Event → effect signatures | NOT_STARTED | To close: build a sealed locked case set labelled by named humans (case_seal requires them; personas cannot, D-088), then run B0/B1, permutation control, firewall counters and two replays. |
| 23 | Mechanism applicability engine | PARTIAL | To close: human-labelled locked cases (not MECH authors) for G23.1/23.3/23.4, freeze DATA-EVIDENCE v1 and deliver the UNKNOWN census to Step 14, byte-identical APPDEC replay twice. |
| 24 | Formula / model registry | PARTIAL | To close: reproduce >=1 source figure per FORM (REPRODUCED), mint human-verified PARAM rows with fitted_on, record calibration domains, write VAL plan hashed to Step-15 partitions and the PARAM coverage-vs-quota report. |
| 25 | Parameter-compatibility retrieval | NOT_STARTED | To close: needs PARAM rows (Step 24) first; then build param_compat.py, sealed query set and controls. |
| 26 | Implement one focused deterministic simulator | PARTIAL | To close: freeze preregistration_v1.md, run the >=200-dataset recovery grid, obtain >=5 obs/param human-verified CAL data incl. water assay for k_L, mint PARAM, two clean rebuilds, expert sign-off. |
| 27 | Validate simulator on real held-out evidence | BLOCKED | To close: >=5 independent lab-group held-out series with resolved assay basis, frozen 27a prereg, then run VAL-1..6; until then report NOT_VALIDATED / RESEARCH_ONLY (Step 28 not entered, H8-05). |
| 28 | Generate controlled E7 synthetic prior | CUT | To close: pass Step 27 (>=5 SIM-VAL papers, VALIDATED_HELD_OUT sim) then build prior_generator + DATA-SIM_v1 + reports/step28/*; otherwise keep as cut in report |
| 29 | TRANSITION_BOOTSTRAP_V0 | PARTIAL | To close: re-pass Step 07.A (or new pre-registered gate), freeze phase_g_preregistration_v1 + SPLIT.jsonl, run TB-V0 with cold-split shortcut re-run and T1/T2 separation, write v0_results + decision_record_v0 |
| 30 | Strong tabular / sparsity bake-off | BLOCKED | To close: valid 07.A (or new gate), sign 30.0 prereg (phase_g_preregistration_v1.csv with δ_30, c_floor), run D0-D7 on all headline splits, decide G30-B/C, report G30-D |
| 31 | Physics / condition features | BLOCKED | To close: new valid Step-07 gate, build physics_feature_registry_v1, freeze EVD-row arm per 12 Nov card, run A3/A4/A5 on condition-OOD/process-disjoint cooking stratum |
| 32 | Focused kinetics | BLOCKED | To close: acquire/verify >=1 focused kinetic system (multi-study K-at-T series), run KA0-KA6 with profile CIs + LOSO, write g15_4_record |
| 33 | Mechanistic vs ML vs hybrid | CUT | To close: requires Steps 27, 30, 32 first; otherwise keep cut |
| 34 | Short rollout | CUT | To close: keep 34a/34b cut; optionally freeze 34c spec (thresholds + actions, AI_DELEGATED) so the Step-36 abstention path cites it |
| 35 | Molecule → ingredient → recipe / cuisine representation ladder | NOT_STARTED | To close: sign 35.0 v2 (AI_DELEGATED under D-085 if accepted), freeze molecule/recipe splits, run 35a-35e, then mark every 35h box PROMOTED/FAILED/DATA-BLOCKED |
| 36 | Evidence compiler → selective CulinaryState-RAG → later FlavorTwin | PARTIAL | To close: write 36.0 design specs + prototype replay audit, empty L15 whitelist (B6≡B5), OOD strata table, §257P checklist; G36-B/ABST need >=240 locked items + real double labels (cannot be met by personas) |
