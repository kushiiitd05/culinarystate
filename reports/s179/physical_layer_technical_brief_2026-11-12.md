# Physical-layer technical brief — 12 November 2026

**AI_ENGINEERING_COUNTS_ONLY / SCENARIO / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.** This is a technical artifact for later expert checking (T4-C25-R1), not an author-facing final edit, a scientific validation or a new physical run.

## Declared provenance, not observed truth

Layer1 preserves the Binder-declared TEXT_STATED, cue, physical-definition and process-definition basis; other/missing bases stay UNKNOWN. Layer2 computes scenario brackets using defaults/corpus quantiles, never primary measurements. A source/registry reference proves a recorded dependency, not the scientific correctness of that dependency. Scenario output cannot grant evidence-supported status or real SIMULATE permission.

| Recorded v06 validation subset | Files | Heat-event records | Bound/input fields with basis | Source |
|---|---:|---:|---:|---|
| non-BBC L1 | 384 | 1,696,743 | 3,847,976 | `reports/s178/phys/schema_validation_L1_HEAT_S179_v06.json` |
| non-BBC L2 | 384 | 1,696,743 | 9,817,488 | `reports/s178/phys/schema_validation_L2_HEAT_S179_v06.json` |
| BBC L1 local | 16 | 49,662 | 104,932 | `reports/s179/schema_validation_L1_HEAT_A1_S179_v06.json` |
| BBC L2 local | 16 | 49,662 | 215,481 | `reports/s179/schema_validation_L2_HEAT_A1_S179_v06.json` |

The L1 and L2 rows cover the same events and must not be added as independent observations. Non-BBC and BBC totals are 1,746,405 heat events. Schema conformance validates structure and declared provenance fields; it is not evidence that temperatures, durations, mass or model estimates are correct. BBC raw records remain local; this brief publishes aggregate counts only.

## Engineering changes and persistent limits

- v06 separates food-target temperature cues from medium-driver temperatures; original v04/v05 output reports remain preserved as superseded lineage. Source: `reports/orchestration/S178_FIX-PHYS_report.md` §5.
- Evaporation caps and matrix regimes are modelling assumptions. The diffuse-liquid lift and analytical-zero interpretation require their explicit existing rulings; a new technical brief does not settle them.
- The separate strict physical display now supplies per-number metadata and source/default refs. The prior runtime sample found 141 numeric fields across 53 physical steps with no omitted/UNKNOWN metadata in that limited sample; it did not test source truth or population accuracy. Source: `reports/s179/strict_runtime_audit_2026-11-12.json`.
- Two-zone surface/crust modelling is not supplied; oven/bath temperature is not a food-core measurement. Source: D-080 #15.
- No Layer2 feature enters Step31 first arm; EVD-row boundary card is `reports/step31/31_effect_card_EVD_boundary_amendment_2026-11-12.md`.
- No human review is invented. The separate AI source review and synthetic controls do not substitute for primary measurements or independent human verification.

The companion JSON binds every displayed census count to the exact original source hash. Later expert review should inspect raw record basis/status/unit/spans and scientific model assumptions independently before claiming applicability.
