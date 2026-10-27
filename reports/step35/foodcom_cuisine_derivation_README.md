# Food.com tag -> cuisine -> continent derivation (D-036) — DRAFT, UNSIGNED

Status: `DRAFT_PENDING_SIGN`. For review by Kush and Parv. No cuisine statistic may be computed from this until signed (35.0, 35d). Food.com raw is LOCAL research use only; only aggregate tag counts are written. No per-recipe label file exists. Reproduce: `/opt/anaconda3/bin/python tools/step35_foodcom_tag_census.py`.

Files (all in `registry/cuisine/`): `foodcom_tag_census_v1.csv` (tag, n_recipes, source_column; cut n_recipes >= 20 is a privacy/noise cut, not a science claim), `explicit_cuisine_labels_v1.csv`, `cuisine_lookup_v1_DRAFT.csv` (the editable fixed lookup, 211 terms, with `label_level`), `foodcom_tag_cuisine_map_v1_DRAFT.csv` (columns: tag, n_recipes, n_recipes_keywords, n_recipes_category, proposed_cuisine, proposed_continent, label_level, match_basis, status).

Method: tags = `Keywords` (list) and `RecipeCategory` (scalar), stripped, counted once per recipe. Match is exact on casefolded tag against the lookup (country name, nationality adjective / cuisine name); no fuzzy matching, no judgement. Continent = UN M49 continent (Africa, Americas, Asia, Europe, Oceania); `MIXED` / `NEEDS_HUMAN` for pan-regional or ambiguous terms (those carry cuisine `NEEDS_HUMAN` and never count as a mapped cuisine). Unmatched tags = `UNKNOWN`. Lookup terms are an editable proposal; terms absent from the data are harmless.

## Label levels (D-037 item 1)
`label_level` in lookup and map: `CUISINE` (country / cuisine / nationality term: cuisine + continent), `REGION` (term names more than one country: `proposed_cuisine=UNKNOWN`, continent kept only if the whole region lies in one UN M49 continent, else `MIXED`), `NEEDS_HUMAN` (not decidable from the "more than one country" rule alone), `UNKNOWN` (tag not in lookup). All `DRAFT_PENDING_SIGN`. Cuisine analysis uses CUISINE terms only; continent analysis uses CUISINE or REGION terms with a real continent (MIXED / NEEDS_HUMAN give no continent).

### Pan-regional classification for human review (decided only by "names more than one country")
| Term | Recipes (union) | level | continent | Note |
|---|---|---|---|---|
| European | 50,811 | REGION | Europe | |
| Asian | 27,620 | REGION | Asia | |
| African | 4,741 | REGION | Africa | |
| Caribbean | 3,013 | REGION | Americas | M49: all Caribbean states are in Americas |
| South American | 2,482 | REGION | Americas | |
| Latin American | (<20, in lookup only) | REGION | Americas | |
| Scandinavian | 2,383 | REGION | Europe | |
| Southwestern U.S. | 6,730 | REGION | Americas | several US states; single country, listed as pan-regional by D-037 |
| Southwest Asia (middle East) | 3,752 | REGION | MIXED | UNCERTAIN: M49 Western Asia is Asia, but "middle East" is usually read to include Egypt (Africa); MIXED chosen to avoid inventing |
| Middle Eastern | (<20) | REGION | MIXED | same reason |
| Mediterranean | (<20) | REGION | MIXED | Europe, Asia, Africa |
| Polynesian | 376 | REGION | Oceania | UNCERTAIN: Easter Island (Chile) is Polynesian; M49 puts Polynesia in Oceania |
| Southwest Pacific | (<20) | REGION | MIXED | boundary undefined |
| Oriental | (<20) | NEEDS_HUMAN | NEEDS_HUMAN | dated term; East Asia vs Asia unclear |
Not pan-regional, kept NEEDS_HUMAN (single country or ambiguous sense, cuisine-fold question 2 still open): Tex Mex 2,831, Cajun 2,486, Creole 1,851 (continent MIXED), Hawaiian 875, Pennsylvania Dutch 366, Native American 355, Cantonese 307, Szechuan 231, Hunan 54, Georgian 41; in lookup only: American, Southern, Jewish, Roman.

## Counts (522,517 recipes)
- Tags in census (>= 20 recipes): 507 tag-column rows (625 distinct before cut); 286 distinct tags in the map.
- Map tags: 57 CUISINE, 9 REGION, 10 NEEDS_HUMAN, rest UNKNOWN (no lookup match).
- Cuisine analysis (CUISINE terms only): recipes with a CUISINE-level mapping 67,216 (12.9%); with > 1 distinct cuisine 2,643 (flag `CONFLICTING`, not resolved); UNKNOWN 455,301 (87.1%), of which 59,286 carry only a REGION / NEEDS_HUMAN term. 67,216 + 455,301 = 522,517 (tested).
- Continent analysis (CUISINE or REGION terms): recipes with a continent-level label 120,870 (23.1%); with conflicting continents 3,265 (flag, not resolved); UNKNOWN 401,647 (76.9%), of which 5,632 carry only MIXED / NEEDS_HUMAN terms. 120,870 + 401,647 = 522,517 (tested).

## Count discrepancy census vs map (fixed)
The census counts per (tag, source_column); the map counts a tag once per recipe over Keywords OR RecipeCategory. Example: Easy = 276,838 (Keywords) + 727 (RecipeCategory) = 277,565 (no recipe has it in both). Map `n_recipes` is now defined as that union, and the map carries `n_recipes_keywords` and `n_recipes_category`, which equal the census rows (tested; max(k,c) <= n <= k+c).

## Explicit-vs-derived overlap check
Not possible. `cuisine_if_explicit` is non-null for BBC 6,977, Gutenberg 51,492, Wikibooks 1,675, and 0 for Food.com and TasteSet; the sources with explicit labels have no Food.com-style tags and Food.com has no explicit labels. No source has both, so agreement of derived with explicit cannot be measured and is not imputed.

## Confound warning
Food.com is 522,517 of 612,782 recipes (85.3%). Derived cuisine would exist almost only for Food.com, while explicit labels come almost only from Gutenberg/BBC/Wikibooks. Derived cuisine and source are therefore tied (cuisine = source, THR-35P-26), and derived labels (`DERIVED_FROM_TAG`) must never be pooled with explicit ones in one claim. Only 12.9% of Food.com recipes get a label and the tags are author-chosen, so label coverage is itself selective.

## Top NEEDS_HUMAN terms
See the classification tables above (superseded the earlier all-in-one list).

## Open questions (max 4)
1. (Answered by D-037 item 1: REGION labels, continent analysis only.) Review the REGION list above, esp. Southwest Asia and Polynesian.
2. Subnational and US-regional terms (Cantonese, Szechuan, Cajun, Tex Mex, Southwestern U.S., Hawaiian, Creole): fold into a country cuisine, keep separate, or leave UNKNOWN?
3. Conflicting recipes (2,643): drop from cuisine work, keep as a `CONFLICTING` class, or multi-label?
4. Is the 20-recipe tag cut and the "mapped at all" coverage (12.9%) acceptable given THR-35P-22 (>= 100 recipes and >= 2 source families, which derived-only Food.com labels cannot satisfy alone)?
