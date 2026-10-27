# Food.com tag -> cuisine -> continent derivation (D-036) — DRAFT, UNSIGNED

Status: `DRAFT_PENDING_SIGN`. For review by Kush and Parv. No cuisine statistic may be computed from this until signed (35.0, 35d). Food.com raw is LOCAL research use only; only aggregate tag counts are written. No per-recipe label file exists. Reproduce: `/opt/anaconda3/bin/python tools/step35_foodcom_tag_census.py`.

Files (all in `registry/cuisine/`): `foodcom_tag_census_v1.csv` (tag, n_recipes, source_column; cut n_recipes >= 20 is a privacy/noise cut, not a science claim), `explicit_cuisine_labels_v1.csv`, `cuisine_lookup_v1_DRAFT.csv` (the editable fixed lookup, 211 terms), `foodcom_tag_cuisine_map_v1_DRAFT.csv`.

Method: tags = `Keywords` (list) and `RecipeCategory` (scalar), stripped, counted once per recipe. Match is exact on casefolded tag against the lookup (country name, nationality adjective / cuisine name); no fuzzy matching, no judgement. Continent = UN M49 continent (Africa, Americas, Asia, Europe, Oceania); `MIXED` / `NEEDS_HUMAN` for pan-regional or ambiguous terms (those carry cuisine `NEEDS_HUMAN` and never count as a mapped cuisine). Unmatched tags = `UNKNOWN`. Lookup terms are an editable proposal; terms absent from the data are harmless.

## Counts (522,517 recipes)
- Tags in census (>= 20 recipes): 507 tag-column rows (625 distinct before cut); 286 distinct tags in the map.
- Tags mapped to a real cuisine: 57. Tags NEEDS_HUMAN/MIXED: 19.
- Recipes with >= 1 mapped tag: 67,216 (12.9%).
- Recipes with > 1 distinct mapped cuisine: 2,643 -> to be flagged `CONFLICTING`, not resolved.
- Recipes UNKNOWN (no mapped tag): 455,301 (87.1%); of these 59,286 carry only a NEEDS_HUMAN/MIXED term (e.g. European, Asian), so they stay UNKNOWN.
- Mapped + UNKNOWN = 522,517 (reconciles; tested).

## Explicit-vs-derived overlap check
Not possible. `cuisine_if_explicit` is non-null for BBC 6,977, Gutenberg 51,492, Wikibooks 1,675, and 0 for Food.com and TasteSet; the sources with explicit labels have no Food.com-style tags and Food.com has no explicit labels. No source has both, so agreement of derived with explicit cannot be measured and is not imputed.

## Confound warning
Food.com is 522,517 of 612,782 recipes (85.3%). Derived cuisine would exist almost only for Food.com, while explicit labels come almost only from Gutenberg/BBC/Wikibooks. Derived cuisine and source are therefore tied (cuisine = source, THR-35P-26), and derived labels (`DERIVED_FROM_TAG`) must never be pooled with explicit ones in one claim. Only 12.9% of Food.com recipes get a label and the tags are author-chosen, so label coverage is itself selective.

## Top 15 NEEDS_HUMAN terms (recipes)
European 50,811 (MIXED) · Asian 27,620 (MIXED) · Southwestern U.S. 6,730 · African 4,741 · Southwest Asia (middle East) 3,752 · Caribbean 3,013 · Tex Mex 2,831 · Cajun 2,486 · South American 2,482 · Scandinavian 2,383 · Creole 1,851 (MIXED) · Hawaiian 875 · Polynesian 376 · Pennsylvania Dutch 366 · Native American 355.

## Open questions (max 4)
1. Should pan-regional terms (European, Asian, African, South American) get a continent-level label, or stay out of the cuisine classes?
2. Subnational and US-regional terms (Cantonese, Szechuan, Cajun, Tex Mex, Southwestern U.S., Hawaiian, Creole): fold into a country cuisine, keep separate, or leave UNKNOWN?
3. Conflicting recipes (2,643): drop from cuisine work, keep as a `CONFLICTING` class, or multi-label?
4. Is the 20-recipe tag cut and the "mapped at all" coverage (12.9%) acceptable given THR-35P-22 (>= 100 recipes and >= 2 source families, which derived-only Food.com labels cannot satisfy alone)?
