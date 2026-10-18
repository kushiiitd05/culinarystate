# DEL-1 Process-Effect Evidence Ledger — data card (2026-10-18)

## Acceptance (proposal D1 / plan T1)

| Clause | Required | Achieved | |
|---|---|---|---|
| Public retention-database rows | ≥ 1,000 | 10,888 | ✅ |
| Hand-verified literature rows (human) | ≥ 40 | 0 | ❌ |
| Rows with source | 100% | 100.0% | ✅ |
| Rows with evidence tier | 100% | 100.0% | ✅ |
| Rows with condition status (completeness mask) | 100% | 100.0% | ✅ |
| Rows with censoring flag | 100% | 100.0% | ✅ |
| Names normalised to internal ING (AH2) | report | 53.2% | — |
| Process linked to PROC | report | 98.8% | — |
| Names normalised to RecipeDB/FlavorDB | proposal | UNRESOLVED_EXTERNAL (API pending, AH2) | ⏳ |

## Composition

- USDA-RETN-R6: 7,018 rows
- PHENOL-EXPLORER-3.6: 3,870 rows
- tiers: {'E3': 10888}; origin: {'DATABASE_AGGREGATE': 7018, 'PRIMARY_STUDY': 3870}
- study lineage: {'NOT_IDENTIFIABLE': 7018, 'PRESENT': 3870}; independent groups: 126
- censored rows: 2,620; RF status: {'CENSORED': 2620, 'MEASURED': 8244, 'UNKNOWN': 24}
- direction: {'UNKNOWN': 2644, 'DECREASE': 7146, 'NO_CHANGE': 80, 'INCREASE': 1018}; basis: {'RETENTION_TR_OR_AR': 7018, 'FRESH_WEIGHT': 2906, 'PER_VOLUME': 960, 'DRY': 4}
- unique matrices 184, step sequences 67, targets 187, cells 8,651; matrix×process density 0.0372
- condition axes: {'duration': {'UNKNOWN': 7805, 'MEASURED': 2607, 'RANGE': 476}, 'temperature': {'UNKNOWN': 8660, 'MEASURED': 2047, 'RANGE': 181}}
- conflict candidates (opposite directions across independent groups, same cell): 17

## Known limitations / bias

- USDA R6: factors largely imputed; mixed %TR/%AR; rounded to 5%; 37% capped at 100 (censored); placeholder date.
- Phenol-Explorer: RF includes a yield factor often borrowed from another food; per-publication design unknown.
- Sources skew to Western foods and polyphenols/vitamins/minerals; volatile/flavour compounds largely absent.
- 109 processes used in recipes have no state-change evidence at all (process registry v1).
- No row is human-verified yet: literature verification queue is the human task (E4 needs HUMAN_VERIFIED).

## Sources

- SRC-000001: USDA Table of Nutrient Retention Factors, Release 6 — licence: US federal government work (public domain, 17 U.S.C. §105) (COMMIT_OK)
- SRC-000012: Phenol-Explorer 3.6 — polyphenol retention factors (food processing) — licence: Free public resource; commercial use/redistribution requires authors' permission; cite Phenol-Explorer and original publications (DERIVED_ONLY)
