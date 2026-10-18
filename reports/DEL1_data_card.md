# DEL-1 Process-Effect Evidence Ledger — data card (2026-10-18)

## Acceptance (proposal D1 / plan T1)

| Clause | Required | Achieved | |
|---|---|---|---|
| Public retention-database rows | ≥ 1,000 | 7,018 | ✅ |
| Hand-verified literature rows (human) | ≥ 40 | 0 | ❌ |
| Rows with source | 100% | 100.0% | ✅ |
| Rows with evidence tier | 100% | 100.0% | ✅ |
| Rows with condition status (completeness mask) | 100% | 100.0% | ✅ |
| Rows with censoring flag | 100% | 100.0% | ✅ |
| Names normalised to internal ING (AH2) | report | 0.0% | — |
| Process linked to PROC | report | 0.0% | — |
| Names normalised to RecipeDB/FlavorDB | proposal | UNRESOLVED_EXTERNAL (API pending, AH2) | ⏳ |

## Composition

- USDA-RETN-R6: 7,018 rows
- tiers: {'E3': 7018}; origin: {'DATABASE_AGGREGATE': 7018}
- study lineage: {'NOT_IDENTIFIABLE': 7018}; independent groups: 1
- censored rows: 2,620; RF status: {'CENSORED': 2620, 'MEASURED': 4374, 'UNKNOWN': 24}
- direction: {'UNKNOWN': 2644, 'DECREASE': 4374}; basis: {'RETENTION_TR_OR_AR': 7018}
- unique matrices 38, step sequences 42, targets 26, cells 7,018; matrix×process density 0.1071
- condition axes: {'duration': {'UNKNOWN': 6291, 'MEASURED': 259, 'RANGE': 468}, 'temperature': {'UNKNOWN': 7018}}
- conflict candidates (opposite directions across independent groups, same cell): 0

## Known limitations / bias

- USDA R6: factors largely imputed; mixed %TR/%AR; rounded to 5%; 37% capped at 100 (censored); placeholder date.
- Phenol-Explorer: RF includes a yield factor often borrowed from another food; per-publication design unknown.
- Sources skew to Western foods and polyphenols/vitamins/minerals; volatile/flavour compounds largely absent.
- 109 processes used in recipes have no state-change evidence at all (process registry v1).
- No row is human-verified yet: literature verification queue is the human task (E4 needs HUMAN_VERIFIED).

## Sources

- SRC-000001: USDA Table of Nutrient Retention Factors, Release 6 — licence: US federal government work (public domain, 17 U.S.C. §105) (COMMIT_OK)
