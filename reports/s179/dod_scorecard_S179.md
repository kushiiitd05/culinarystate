# Definition-of-Done scorecard: SSOT §257 (17 items) and §257A.25 (21 items) (S179, T9-C30-R1)

Status: **AI_DRAFTED / PROPOSED, for the report appendix.** This is the agent's reading of committed files, not a
gate verdict (D-071). It is checked against `kush/s179-finish-fixes` at 6f7b5e7 on 2026-11-10. Every row cites a
path or gives a reason.

Statuses:
- **MET:** the demonstration exists and can be re-run.
- **PARTIAL:** built or run, but the SSOT condition is not fully shown.
- **NOT_MET:** missing, or shown to fail.
- **NOT_STARTED:** nothing built.

Companion table for the 14 G16 gates: `reports/s178/g16_gate_status.md` (0 of 14 pass).

## A. SSOT §257 Definition of Done (17)

| # | Item | Status | Evidence / reason |
|---|---|---|---|
| 1 | Raw recipe parsed into versioned ingredient / quantity / event / state objects without inventing science | PARTIAL | Rung A + adapter ran on 599,971 texts, invented values excluded by the adapter (`reports/s178/corpus/replay_invariants_corpus_v2.json`); quantity grounding is low and Food.com lines lack units (NEG-0034) |
| 2 | State replayable from events | MET | Determinism 12,046 / 12,046 same-worker and cross-process; 0 engine vs independent disagreements; planted errors 60,091 / 60,091 caught (same file; `reports/final/sections/S179_D3_state_tracking_DRAFT.md`) |
| 3 | Quantity conversions show evidence class and uncertainty | PARTIAL | `src/culinarystate/quantity/rc2_grounding.py`, `units.py`; U+2044 defect on 29.8 % of lines unfixed until after the talk (D-070 O1, NEG-0037) |
| 4 | Aliases resolve to canonical foods; modifiers separate | PARTIAL | Linker held-out alias Acc@1 0.704 (`reports/ner_v2/fresh_linker_final_report.md`); ALIAS ledger; modifiers kept separate in the gold schema; no corpus-level resolution accuracy |
| 5 | Deep-Gold benchmark independent of Silver | NOT_MET | P1 gold is HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND; handbook gate failed (`reports/step19/pilot_iaa_report.md`, NEG-0038) |
| 6 | Source / duplicate-safe splits frozen | NOT_MET | Split registry exists (`registry/split_registry_v1.csv`), but G08-3 failed (NEG-0047) and the identity ledger is provisional; no split is source-family-disjoint (`reports/final/sections/S179_licence_and_split_labels_DRAFT.md`) |
| 7 | Retriever finds state / process / condition-compatible evidence with exact provenance | PARTIAL | Router with gates (`src/culinarystate/decision/query_router.py`; census `reports/step23/router_demo_census_vitc_nonBBC_full_S179b.json`: DIRECT 30,220 of 35.3 M items); not evaluated on a frozen benchmark |
| 8 | Context compiled into direct / near / conflict / model / unknown / disallowed sections | PARTIAL | `src/culinarystate/decision/evidence_label.py`, `pipeline.py`; no held-out check |
| 9 | Confidence / abstention calibrated on held-out gold | NOT_MET | `decision/confidence.py` says its values are "not probabilities"; the S178 amendment draft would call B7 "uncalibrated" (D-D5-8) |
| 10 | Level-15 fallback only in validated domains | NOT_MET | No validated transition model; DEL-2 learned models do not clearly beat baselines, and D7 = D1 on raw Phenol-Explorer (NEG-0050) |
| 11 | Candidate actions feasibility-checked before recommendation | PARTIAL | `src/culinarystate/decision/feasibility.py` (tool / time / allergen, unknown when unstated); proposal H4 not tested |
| 12 | Diagnosis / recovery separates cause from recovery evidence | PARTIAL | `src/culinarystate/decision/diagnosis.py` (separate recovery index, never an inverted cause); no evaluation |
| 13 | Every factual response claim has traceable provenance | PARTIAL | C17 claim checker and enforcer; D5CLM schema draft (`registry/schemas/D5CLM.draft_v1.schema.json`); not run on the benchmark |
| 14 | Strong RAG baselines beaten, or the simpler baseline retained | NOT_MET | B0-B7 ladder not run on the frozen D5 benchmark (M5); digest pinned (RUN-S179-PIN-001) |
| 15 | FlavorTwin static baselines before process-conditioned claims | NOT_STARTED | Research note only (`reports/master_plan/working_notes/research/r_representation_flavortwin.md`); scope cut candidate (T9-C07-R4) |
| 16 | Negative / null results retained | MET | `registry/negative_results_register_v1.csv` NEG-0001..0050; failed gates kept (07.A, G08-3) |
| 17 | All results rerunnable from dataset / split / code / model / prompt versions | PARTIAL | `registry/compute_runs_v1.csv` (282 rows), prompt registry `--check` clean; 27 old rows lack start / end (`reports/s179/run_log_gap_audit_S179.md`); EXP ids not assigned (`registry/experiments_S171_S175.csv`) |

**Totals:** MET 2, PARTIAL 9, NOT_MET 5, NOT_STARTED 1.

## B. SSOT §257A.25 sanity checklist (21)

| # | Item | Status | Evidence / reason |
|---|---|---|---|
| 1 | Raw sources immutable / versioned | PARTIAL | Raw text git-ignored and local (D-003); acquisition manifest `registry/data_source_acquisition_manifest.csv`; frozen ledger hashes match on 3 hosts (`reports/s179/env_inputs_three_hosts_S179.md`); not every raw source has a hash |
| 2 | Schemas frozen / versioned | PARTIAL | `ledgers/schemas/*.schema.json` versioned; several are DRAFT (D5CLM, kinetic units need a UNIT schema change, T5-C07-R5) |
| 3 | Provenance enum enforced | PARTIAL | Enum in `ledgers/schemas/EVD.schema.json` (provenance block); enforced on EVD writes; not shown for every ledger |
| 4 | Gold independently annotated | NOT_MET | As §257 item 5 |
| 5 | Duplicate / source leakage controlled | NOT_MET | As §257 item 6; D5 leakage audit `reports/s178/leakage_audit_d5_findings.md` |
| 6 | Vocabulary coverage and long-tail errors reported | PARTIAL | Can-say v2 and Food.com card v2 (`reports/s178/analysis/corpus_can_say_v2.md`, `reports/s178/corpus/foodcom_data_card_v2.md`); G16-VOCAB PARTIAL |
| 7 | Quantity conversions expose evidence class | PARTIAL | As §257 item 3 |
| 8 | Unknown chemistry stays unknown | MET | Router answers UNKNOWN on 35,151,784 of 35,256,601 items rather than guessing (S179b census); scenario defaults labelled AI-recalled and unverified (NEG-0043) |
| 9 | Evidence atoms keep exact proof / source spans | PARTIAL | EVD rows carry source and DOC links; 0 of 40 literature rows hand-verified (DEL-1) |
| 10 | Retrieval uses condition / state compatibility | PARTIAL | Prior-process and lot-context gates in the router census 0.4.1; no held-out retrieval evaluation |
| 11 | Conflict explicit | PARTIAL | CONFLICT regime in `decision/evidence_label.py`; not exercised on a benchmark |
| 12 | Confidence calibrated, not self-reported | NOT_MET | As §257 item 9 |
| 13 | Transition model gated by Level-15 results | NOT_MET | As §257 item 10 |
| 14 | Actions pass feasibility constraints | PARTIAL | As §257 item 11 |
| 15 | Diagnosis and recovery evidence distinct | PARTIAL | As §257 item 12 |
| 16 | Final claims have a claim ledger | PARTIAL | CLM schema `ledgers/schemas/CLM.schema.json`; D5CLM draft; no claims recorded from a benchmark run |
| 17 | Strong baseline / ablation results exist | NOT_MET | As §257 item 14 (the DEL-2 baselines exist, but the D5 ladder does not) |
| 18 | Negative results recorded | MET | As §257 item 16 |
| 19 | FlavorTwin does not overclaim sensory equivalence | MET (vacuous) | No FlavorTwin claim is made anywhere; nothing is built (§257 item 15) |
| 20 | Reproducibility metadata complete | PARTIAL | As §257 item 17 |
| 21 | Level 17 optional, not blocking | MET | Nothing in the 25 Nov plan depends on Level 17 (`registry/execution_board_S178.csv`: no MUST item names it) |

**Totals:** MET 4 (one of them vacuous), PARTIAL 12, NOT_MET 5, NOT_STARTED 0.

## Reading for the report

- **The system is not complete in the SSOT sense.** 6 of 38 rows are MET. Every NOT_MET row traces to the same three
  gaps: no independent gold, no frozen source-safe split, and the D5 ladder not run.
- **What is finished is the plumbing that keeps claims honest.** Replay, UNKNOWN by default, negative results kept,
  and provenance on runs.
- **"Complete" must not appear in the report.**
