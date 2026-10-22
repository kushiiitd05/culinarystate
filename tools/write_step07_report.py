#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
a = json.loads((ROOT / "reports/step07/step07_condition_coverage_audit.json").read_text())
m = json.loads((ROOT / "reports/step07/condition_audit_sampling_manifest.json").read_text())
v, s = a["value_type_counts"], a["status_counts"]
f = lambda d: "; ".join(f"{k} {n:,}" for k, n in d.items())
txt = f"""# STEP 07 -- Condition and measurement normalization (report)

**Gate result: PASS for the automated gate; human sub-gate PENDING (100-condition audit, kappa >= 0.8).** Read-only over the current data; no source row was modified (EVD, COND, MEAS, SVAR sha256 unchanged: {a['ledger_sha256_unchanged']}). No acquisition, no E5 rows, no verification, no mechanism/simulation work, no NER/linker/span experiments.

## Artifacts
Registries (stable ids authoritative, raw strings kept): `registry/condition_variable_registry_v1.csv` (40 variables: time 4, temperature 8 incl. setpoint/medium/surface/core/unspecified/trajectory/rate/preheat, chemical 11, physical 13, biological 4), `value_type_registry_v1.csv` (POINT, INTERVAL, TRAJECTORY, QUALITATIVE, UNKNOWN), `measurement_basis_registry_v1.csv`, `quantity_form_registry_v1.csv`, `retention_type_registry_v1.csv`, `censoring_registry_v1.csv`, `value_origin_registry_v1.csv`, `measurement_location_registry_v1.csv`, `measurement_method_registry_v1.csv`, `heat_transfer_mode_registry_v1.csv`. Schema: `registry/schemas/condition_value_v1.schema.json`. Normalizer: `src/culinarystate/evidence/condition_normalizer.py`. Tests: `tests/unit/test_condition_normalizer.py` (11). Audit: `tools/step07_condition_audit.py`. Human audit: `reports/step07/condition_audit_protocol.md`, `condition_audit_sampling_manifest.json`, local packets `annotation/condition_audit/` (git-ignored).

## Behaviour (all tested)
POINT / INTERVAL (either end may be open) / TRAJECTORY / QUALITATIVE / UNKNOWN. Qualitative never becomes a number without an explicit sourced mapping; "boiling" is never 100 C (reason BOILING_POINT_NOT_ASSUMED); absent pH/aw/moisture/pressure/O2 stay UNKNOWN (never 7 or 0); mixture pH is never averaged (no such function exists). Setpoint, medium, surface, core and unspecified temperatures are separate variables; absolute vs difference temperatures are handled separately (degF difference scales by 5/9, no offset). Pressure: unit table, gauge vs absolute from the unit text, bare psi/bar = AMBIGUOUS (PRESSURE_REFERENCE_UNSPECIFIED). Percent vs fraction: bare numbers AMBIGUOUS; fraction > 1 INVALID; moisture requires WET/DRY basis (wet <= 100%, dry may exceed). pH 0-14, aw 0-1, reversed intervals INVALID (never swapped), trajectory times strictly increasing, trajectory temperature needs a stated location. Measurement fields: basis (incompatible bases cannot be combined), retention type (true / apparent / yield-adjusted / undisclosed / unknown kept distinct and not combinable), censoring (DETECTED, NON_DETECT, BELOW_LOD, BELOW_LOQ, ABOVE_CAP, CENSORED_UNKNOWN, NOT_REPORTED; UNKNOWN is not NON_DETECT, NON_DETECT is not zero), analytical method (raw text preserved), value origin (incl. USDA SOURCE_IMPUTATION_POSSIBLE).
Retention contract: reported retention factor, concentration ratio, log-fold-change and yield factor stay separate fields; the 278 Phenol-Explorer rows where retention differs from after/before x yield by > 0.02 remain an audit signal (no correction). Phenol-Explorer retention type is recorded as RT-003 yield-adjusted with status AMBIGUOUS (the description comes from a secondary snippet; primary-source check pending).

## Current-data coverage ({a['conditions_audited']:,} conditions referenced by {a['evd_rows']:,} active EVD rows)
| Field | Value-type counts | Status counts |
|---|---|---|
| duration | {f(v['duration'])} | {f(s['duration'])} |
| temperature (one entry per stated temperature) | {f(v['temperature'])} | {f(s['temperature'])} |
| pressure | {f(v['pressure'])} | {f(s['pressure'])} |
| microwave power | {f(v['power'])} | {f(s['power'])} |
| medium | {f(v['medium'])} | {f(s['medium'])} |
| pH / moisture / aw | UNKNOWN {v['ph']['UNKNOWN']:,} each (the COND ledger has no such fields) | UNKNOWN |
Temperature location: {f(a['temperature_location_counts'])}. Temperatures with a stated location: {a['temperature_location_counts'].get('CORE',0)+a['temperature_location_counts'].get('SETPOINT',0)+a['temperature_location_counts'].get('MEDIUM',0)}; the {a['temperature_location_counts'].get('UNSPECIFIED',0):,} UNSPECIFIED ones are AMBIGUOUS (MEASUREMENT_LOCATION_MISSING) by design. Pressure: all {s['pressure'].get('AMBIGUOUS',0)} stated pressures lack a gauge/absolute statement -> AMBIGUOUS (PRESSURE_REFERENCE_UNSPECIFIED). INVALID: 0 in all fields. No trajectories exist in the current data.
Measurement: basis ids {f(a['measurement_basis_counts'])} (MB-007 = ratio, MB-001 fresh weight, MB-005 per volume, MB-002 dry); retention types {f(a['retention_type_counts'])}; censoring {f(a['censoring_counts'])}; analytical method {f(a['method_counts'])} (no platform is recorded in any current row); value origin {f(a['value_origin_counts'])}. LOD/LOQ remain UNKNOWN everywhere.
Top reason codes: {', '.join(list(a['reason_counts'])[:6])}.

## Human sub-gate (pending)
100 conditions sampled deterministically (strata: {f(m['selected_by_stratum'])}; sources {f(m['source_family_counts'])}). Reviewers Kush + Parv, blind, per-field codes; gate kappa >= 0.8 before condition annotations are promoted for scientific use. Not conducted in this run.

## Source-access notes carried into the manifest (Step-06 corrections)
Europe PMC: OA/bulk automated routes documented, production route and per-article licence to verify before capture. NCBI E-utilities: usable at low rate without a key; key raises the default rate; tool/email policy applies. Unpaywall: search endpoint retired 2026-09-18 (stated in the instruction, not independently re-verified here); use OpenAlex for discovery; DOI lookup may remain useful.

## Status correction
NER v1, linker D3 and span CSD-C are CLOSED/FROZEN; no backbone, CRF, knowledge-fusion, linker or span-reranker work will restart. Steps 16-17 later reuse the frozen components for instruction/event semantics only.

## Next
STEP 08 -- source lineage. Not started.
"""
(ROOT / "reports/step07/step07_report.md").write_text(txt)
print(len(txt))
