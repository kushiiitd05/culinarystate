# Step 16a batch 2: DRAFT JSON Schemas v1-rc

Status: DRAFT_PENDING_H4. Nothing frozen or approved. Source: Step 16 card + blocks 16-A / 16-B in `docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`.
Drafts: `reports/step16/schema_drafts/<NAME>.draft_v1.schema.json` (Draft 2020-12, description says `schema_version 1.0.0-rc`). `ledgers/schemas/*` untouched (sha256 pinned in the test). No `default` keyword anywhere, so UNKNOWN never becomes 0. Tests: `tests/unit/test_step16a_schema_drafts.py`.

## Changes vs v0 (all additive: v0 required list identical, no property removed, v0 fixtures in `tests/fixtures/ledger_examples.py` still validate; 0 rows exist in ledgers/data for these ten)
- **EVT** (+14 properties, +1 rule): event_kind, process_family_id, process_modifiers (9 slots, each {status, value, raw}, UNKNOWN-capable), transformation_mode, tool_roles, implicit_args, alternative_group_id, modality, temporal_relation, depends_on, condition_profile_id, endpoint_state_refs, endpoint_leakage_flag, clock. Rule: event_kind ACTION with process_id null requires non-empty `action_raw` (raw verb kept when UNMAPPED, G16.2). v0 `action_raw`, `process_id`, `omitted_step_candidate`, `condition_id` kept.
- **ENTITY** (+6): entity_type, parent_entity_ids, created_by_event_id, consumed_by_event_id, lifecycle, facets (10 V_* facets + size_class; value OTHER requires raw). v0 `kind` kept.
- **STATE** (+2, triple on 2 containers, +5 rules): existence and container layers; optional `meta` {origin, status, claim_route} on variables[*] and quantity; meta.status UNKNOWN/NOT_APPLICABLE forces value/low/high null. Five history keys (cell_integrity, enzyme_activity_state, time_since_disruption, thermal_dose, oxygen_exposure): any non-UNKNOWN value requires meta.claim_route MODEL or SIMULATED (never filled from recipe text, 16-A).
- **QNT** (+12, `$defs.ast_node`, triple on normalized/mass_g/volume_ml/count, +2 rules): normalized_mass_low_g/high_g, intervals[] (SOURCE_RANGE / CONVERSION_UNCERTAINTY / EMPIRICAL_QUANTILES), ast (11 node types; QUALITATIVE/OPEN_AMOUNT/UNKNOWN nodes carry null numbers), quantity_scope, measured_state, as_purchased_vs_edible, multiplier, dual_expression_check, unit_variant, locale_evidence, unit_system_era. Rules: Q6 forces UNKNOWN mass; a MEASURED/RANGE gram at Q1-Q4 requires `portion_id`. `q_level` Q0..Q6 and `locale` already existed in v0 (q_level already required); unchanged.
- **POR** (+8): state, size_class, mass_low_g, mass_high_g, sample_count, source_diversity, source_record, licence. `verification` already in v0 (required) so unchanged; `basis` untouched (open ruling).
- **SPLIT** (+1 enum value): `split-group-disjoint`.
- **INST, ALLOC, REF, GRAPH**: copied forward unchanged except the description string. The card gives no concrete additions ("ALLOC/REF/GRAPH: Part M section M.6" is a pointer to text not in the card).

## Migration note
v0 1.0.0 records validate unchanged against the drafts. New fields are all optional; no backfill needed. `schema_version` stays a free string so 1.0.0 and 1.0.0-rc records both pass; a freeze (16c) should pin it. Two tightenings are rules on new data only (QNT Q6 and Q1-Q4 portion_id; EVT unmapped ACTION raw verb); they would reject a hypothetical v0 record that violated them (none exist). Install = replace `ledgers/schemas/*` only after H4 (R-18: new schema versions only).

## Ambiguities / judgement calls
1. Card says ENTITY "created_by / consumed_by event" but v0 `created_by` is the record author, required. Used `created_by_event_id` / `consumed_by_event_id`. Needs a ruling.
2. Card's `split-group-disjoint` is lower-case hyphenated while sibling values are UPPER_SNAKE. Copied verbatim.
3. Two distinct "status" axes: v0 value-shape status (MEASURED/RANGE/...) vs the card's KNOWN/UNKNOWN/... Kept both; triple lives in `meta`.
4. `origin` enum = the 8 classes in registry/provenance_class_registry_v1.csv (card says "8-class provenance, 239.1"); not otherwise listed in the card.
5. process_family_id typed as a PROC id (hierarchy via PROC parent_id); the card does not say.
6. Q1-Q4 portion_id rule is my reading of "must trace to Q0 arithmetic or a SELECTED human-verified POR record". Q5 left unconstrained ("only if the task permits"). Human-verified status of the POR is not checkable inside a QNT record.
7. History-key claim_route rule (MODEL/SIMULATED only) is my encoding of "never filled from recipe text"; history SVARs are PROPOSED (CHG-16-7).

## Not sourced by the card (nothing written, or written permissively)
- Value vocabularies for: process_modifiers values, POR.state, POR.size_class, STATE existence/container values, measured_state, as_purchased_vs_edible, unit_variant, locale_evidence, unit_system_era, facet values (all free strings, null/UNKNOWN allowed; closed vocab lives in batch-1 registries).
- AST node payloads per type (RATIONAL numerator/denominator, PACKAGE_CONTENT, FRACTION_OF operands): only generic value/low/high/raw/children offered. The ALTERNATIVE "never multiplied" rule is semantic, not schema-enforced.
- Quantile levels for EMPIRICAL_QUANTILES; dual_expression_check shape (only `conflict`, `notes`); implicit_args item payload (only `resolution_ref`); source_diversity type (int or string or null); tool_roles shape (array of {tool_id, role}).
- ALLOC / REF / GRAPH additions (M.6), INST additions, STATE "SVAR attribute" layer beyond v0 `variables`.
- Q-level for "other approved national table" and POR.basis CONVENTION mapping (open rulings, not adopted).
