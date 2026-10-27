# Step 16a batch 1: DRAFT vocabulary registries

Status: DRAFT_PENDING_H4. Nothing frozen, nothing approved. Source: Step 16 card + blocks 16-A/16-B in `docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`.

## Produced
- `registry/recipe_semantics/*_registry_v1_DRAFT.csv` (10 files; columns code,label,definition,source_ref,status). Members: event_kind 6, modality 5, temporal_relation 5, transformation_mode 6, tool_role 4, entity_type 6, lifecycle 6, field_status 5, claim_route 5, annotation_mode 0 + 1 `OPEN` row.
- `registry/processes/process_hierarchy_v1_DRAFT.csv`: 1112 rows = 17 family nodes (level 1, `FAM:<PROC.family>`), 147 latest-version ACTION canonicals (level 2, parent = family node), 939 level-3 rows (PROC.aliases + CANDIDATE surface-form mappings, parent = PROC id), 9 ENDPOINT rows (endpoint_flag=true, no parent, no level).
- `registry/processes/endpoint_vocabulary_v1_DRAFT.csv`: 9 ENDPOINT PROC ids (latest versions) with name and raw surface forms (PROC.aliases + mapped surface forms).
- `registry/tools/tool_hierarchy_v1_DRAFT.csv`: 329 rows = 6 category nodes, 119 tools, 204 aliases; extra column structural_class (from the UNVERIFIED rule map, informational only).

## NEEDS_HUMAN counts
- process hierarchy: 0 rows with a missing family. BUT the family-to-canonical parent is only the existing `PROC.family` field; any finer grouping inside a family (e.g. MECHANICAL_CUT has 69 canonicals) is not derivable and was not attempted. 13,103 UNMAPPED surface forms in `recipe_process_surface_forms_v1.csv` are NOT in the hierarchy (no parent derivable; not enumerated here).
- tool hierarchy: 8 tools with category OTHER (no usable parent, parent empty).
- endpoint vocabulary: 0.

## Plan silent / ambiguous
- No definitions for any enum member (all say "definition not given in plan; needs H4"); only a few plan rules quoted.
- `annotation_mode`: only named in Outputs, no members anywhere in the card -> single OPEN row. The other nine enums are fully enumerated in the card, so no OPEN row was added (they may still be open to H4 additions).
- Plan says PROC flat 156 with ENDPOINT mixed in: 156 ids, 9 are ENDPOINT (the 18 ENDPOINT lines in PROC.jsonl are versions). 66 surface forms map to ENDPOINT ids and are listed under endpoint raw forms.
- Whether families count as hierarchy level 1 or sit above it is not stated; here family=1, canonical=2, alias/surface=3 (3 levels).
- Surface-form mappings are CANDIDATE_VERB_FORM_MATCH_POS_UNCHECKED; treated as proposed aliases only.
- Latest version per id = highest `version` (ledgers are append-only).

## Regenerate
`/opt/anaconda3/bin/python tools/step16a_build_registries.py` (deterministic, sorted, byte-identical; reads ledgers/data/{PROC,TOOL}.jsonl and two registry CSVs read-only). Tests: `/opt/anaconda3/bin/python -m pytest tests/unit -k step16a -q`.

## Pre-existing issue (not caused by this batch)
`tests/unit/test_lineage_guard.py::test_real_repo_matches_real_csv` fails: STUDY.jsonl grew (128347 B) past the 08a baseline (47500 B). STUDY is append-only; baseline CSV is stale for it.
