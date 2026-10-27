# STATUS — CulinaryState (Group 17 · Kush Tokas + Parv Goyal)

**As of:** WORKLOG S145 (2026-10-27 20:50 IST). Old body (as of S083) archived at `docs/archive/STATUS_as_of_S083.md`.
**Repo:** `~/Desktop/CGAS/culinarystate` (local; GitHub push only after H7 approval)
**Logs:** `WORKLOG.md` (append-only) · `DECISIONS.md` (D-001..D-034; D-028 draft unsigned) · SSOT index `docs/SSOT_INDEX.md` (bible `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md`)
**Plan:** `docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md` (D-027: original 36-step spine governs; only R-01..R-20 adopted)
**Resume file:** `reports/master_plan/RESUME_ANCHOR_2026-10-26.md`

## Current stage
ES-1 data and evidence factory. Step 07H-R (612,782 recipes) and 07I-R done. 2026-10-27: H4 walk-through signed (D-029..D-032); Step 08a built (08a.1-08a.9) and the real run applied (new `DOC.jsonl`, `SRC_08A_YIELD.jsonl`, STUDY append, `_ids` append; EVD/COND/SRC/MEAS byte-identical). Edge audit returned by Kush and Parv: **G08-3 FAIL** (B3 weak; D-034 keeps the B3 cut 0.75, no gate loosened). 07.A statistic FAIL; 07I-C original kappa 0.571/0.588, D-033 records Kush's stated 0.88 on adjudicated labels. Step 16a draft registries and v1-rc schemas written (DRAFT_PENDING_H4). Step 08b NOT authorised; 08b draft authorisation package in preparation. A100 servers unreachable (VPN down at last check).

## Steps 01-08
| Step | Title | State | Source |
|---|---|---|---|
| 01 | Freeze project authority | DONE (historical); v1.1 registries PENDING HUMAN (H4) | `registry/execution_spine_v2.csv` |
| 02 | Audit implementation state | DONE (historical, stale); 02.4 register drafted, 02.R-min drafted, PENDING HUMAN | spine; S140 |
| 03 | Freeze state semantics | DONE (historical); 03.3/03.9 addenda NOT STARTED; MP-1 label DRAFT vs FROZEN UNKNOWN | spine |
| 04 | Evidence / provenance / similarity contracts | DONE (historical); v1.1 addenda DRAFT, PENDING HUMAN (H4) | `reports/step04/`, S140 |
| 05 | Normalize EVD | DONE (ES-1.1 PASS, 17,978 rows); export v2 NOT STARTED (inside 08a.7) | S129; spine |
| 06 | Source acquisition manifest | DONE (automated); 21 H2 items PENDING HUMAN | S130; `reports/h_state/es_1_2_h2_approval_queue.md` |
| 07 | Condition and measurement normalization | Automated gate PASS (07H, 07H-R frozen); human condition audit PENDING HUMAN | S131-S133; `reports/step07/step07h_human_gate_result.json` |
| 08 | Scientific source lineage (08a/08b) | 08a DONE on the machine side, G08-3 FAIL (B3/B2 edges PROVISIONAL), G08-9 expert reading pending; 08b NOT authorised | D-032, D-034; `reports/step08/step08a_audit_result_v2.json`, `exports/lineage/step08a_v1/` |

Step 07 note: the returned v3 audit is `NOT_COUNTED_PROVENANCE_INVALID` (archived in `reports/step07/v3_not_counted_archive/`); v4 packet is frozen and unlabelled. Gate = pooled kappa >= 0.80 and no systematic critical-field failure (D-027).

## Human gates
| Gate | Location | Owner |
|---|---|---|
| H4 review of Step 04 checklist; sign/change threshold rows | `reports/step04/README.md`, `registry/preregistered_thresholds_v1.csv` (47 rows, unsigned); residual rulings draft `docs/plan/D-028_DRAFT_residual_rulings.md` (items 4, 5 open); 07.A amendment `reports/step07/condition_audit_protocol_amendment_v4_1_DRAFT.md` | Kush |
| Pre-label decision on prevalence-only critical flags (THR-07A-06) | thresholds CSV | Kush |
| Step 07.A condition audit, frozen packet v4 (~2-3 h each, blind) | `annotation/condition_audit/condition_audit_packet_100_v4_Kush.csv` and `_v4_Parv.csv`; protocol `reports/step07/condition_audit_protocol.md` | Kush + Parv |
| Pre-register 07I-C label mapping/operating point, then label 400-pair identity packet (~4-10 h each) | `annotation/duplicate_calibration/duplicate_pairs_v1_Kush.csv` and `_Parv.csv` (key `_KEY_SEALED.csv`: do not open); manifest `reports/step07i/duplicate_calibration_packet_manifest.json` | Kush + Parv |
| H2 licence decisions (Food.com, TASTEset) and 21-item queue | `reports/h_state/es_1_2_h2_approval_queue.md` | Kush |
| Written authorisation of Step 08a (after 04.1, 04.2-min, 04.6-min, 04.9-min approval and 08a.0 sign-off) | DECISIONS.md | Kush |
| Older manual items (DEL-1 literature rows, Gold pilot, allergen sign-off, benchmark questions, FSIS/FooDB/FoodAtlas downloads, professor email). Current completion UNKNOWN; list is not dated after S083 | `handoff/MANUAL_NEXT_STEPS.md` | Kush / Parv per row |

## Deadlines
Presentation 25-26 Nov 2026 (`handoff/MANUAL_NEXT_STEPS.md`). Source-dated weekly plan: archived S083 file section 4; whether it still holds is UNKNOWN.

## Merged from server branch plan/v2-reconciliation
S138-S141 and D-027 were written on server branch `plan/v2-reconciliation` (commits bc343ee, f398a44, round 3) and merged here; WORKLOG ids renumbered from S135-S138 (WORKLOG S138 header). D-027 follows Mac D-026 (recipe-usage decision) unchanged (`DECISIONS.md`).

## Known open defects
- Round-3 review fixes incomplete: `reports/step21/*`, `registry/schemas/MECH.draft_v1.schema.json` and K-1 jsonschema corrections (`reports/step04/README.md`, `lineage_contract_v1_1.md`, `reports/step02/r_min_08a_input_classification.md`) not changed; another agent is fixing Step 21 now (do not edit step21 or registry/schemas). Reviews: `reports/master_plan/review_queue/round3_review_{A_governance,B_science}.md` (39 and 43 findings).
- `reports/step19/*` and `reports/step35/*`: audit of 2026-10-26 checked 18 round-3 items and found most already fixed (independence artefacts, ID counts, split alpha/F1 thresholds); B 35-3, 35-4, 35-9, 19-5 and minors not re-checked. No fix log from Max.
- STUDY ledger: 125 rows `design=UNKNOWN`; EVD is endpoint-only (D-027 evidence).
- D-026 open: TASTEset MIT-vs-unverified licence inconsistency; CoSyLab and Phenol-Explorer permissions untouched; redistribution of BBC/Food.com raw = NO.
- One pre-existing unrelated hang in `test_transition` (deselected in S134 runs).
- Current DEL-1 verified-row count, Gold pilot status and ledger file sizes (D-012): UNKNOWN after S083.
