# Food.com tag -> cuisine -> continent derivation (D-036) — DRAFT, UNSIGNED

Status: `DRAFT_PENDING_SIGN`. For review by Kush and Parv. No cuisine statistic may be computed from this until signed (35.0, 35d). Food.com raw is LOCAL research use only; only aggregate tag counts are written. No per-recipe label file exists. Reproduce: `/opt/anaconda3/bin/python tools/step35_foodcom_tag_census.py`.

Files (all in `registry/cuisine/`): `foodcom_tag_census_v1.csv` (tag, n_recipes, source_column; cut n_recipes >= 20 is a privacy/noise cut, not a science claim), `explicit_cuisine_labels_v1.csv`, `cuisine_lookup_v1_DRAFT.csv` (the editable fixed lookup, 211 terms, with `label_level`), `foodcom_tag_cuisine_map_v1_DRAFT.csv` (columns: tag, n_recipes, n_recipes_keywords, n_recipes_category, proposed_cuisine, proposed_continent, label_level, match_basis, status).

Method: tags = `Keywords` (list) and `RecipeCategory` (scalar), stripped, counted once per recipe. Match is exact on casefolded tag against the lookup; no fuzzy matching or automatic judgement. Continent = UN M49 continent (Africa, Americas, Asia, Europe, Oceania); `MIXED` gives no continent label. Unmatched tags and explicitly reviewed ambiguous terms can be `UNKNOWN`. Lookup terms are an editable proposal; terms absent from the data are harmless. The mapping remains unsigned.

## Label levels (D-037 item 1)
`label_level` in lookup and map: `CUISINE` (country / cuisine / nationality term: cuisine + continent), `REGION` (multi-country or below-country region: `proposed_cuisine=UNKNOWN`, continent kept only if the interpretation lies in one UN M49 continent, else `MIXED`), `NEEDS_HUMAN` (unreviewed ambiguity), `UNKNOWN` (unmatched tag or explicit ambiguous-term ruling, with cuisine and continent both UNKNOWN). All generated map rows stay `DRAFT_PENDING_SIGN`. Cuisine analysis uses CUISINE terms only; continent analysis uses CUISINE or REGION terms with a real continent. D-040 extends REGION to below-country terms following D-037's Southwestern U.S. precedent; this is Parv's single-reviewer choice, awaiting Kush/expert review, not a signed ontology.

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
Parv accepted the existing regional continents above without exceptions in D-040.
The historical uncertainty notes explain their origin; acceptance is single-reviewer,
not expert verification.

### Parv's lookup rulings (2026-10-28, D-040; single reviewer)

| Terms | level | cuisine | continent |
|---|---|---|---|
| Tex Mex, Cajun, Pennsylvania Dutch, Native American | REGION | UNKNOWN | Americas |
| Cantonese, Szechuan, Hunan | REGION | UNKNOWN | Asia |
| Creole, Hawaiian, Jewish | REGION | UNKNOWN | MIXED |
| American | CUISINE | American | Americas |
| Georgian, Southern, Roman, Oriental | UNKNOWN | UNKNOWN | UNKNOWN |

Creole retains the Louisiana/Caribbean/Indian Ocean ambiguity; Hawaiian retains
the US-state/Polynesia ambiguity. American is Parv's explicit cuisine ruling;
the other ambiguous terms are not guessed. `basis=PARV_REVIEW_D040_*` records the
source of each changed lookup row. Expert cuisine reviewer remains pending.

## Counts (522,517 recipes)
- Tags in census (>= 20 recipes): 507 tag-column rows (625 distinct before cut); 286 distinct tags in the map.
- Map tags after D-040: 57 CUISINE, 18 REGION, 0 NEEDS_HUMAN, rest UNKNOWN (unmatched or explicitly ruled ambiguous).
- Cuisine analysis (CUISINE terms only): recipes with a CUISINE-level mapping 67,216 (12.9%); with > 1 distinct cuisine 2,643 (flag `CONFLICTING`, not resolved); UNKNOWN 455,301 (87.1%), of which 59,286 carry lookup terms but no CUISINE-level label. 67,216 + 455,301 = 522,517 (tested).
- Continent review counts (CUISINE or REGION terms): recipes with a continent-level label 123,812 (23.7%); with conflicting continents 3,386 (flag, not resolved); UNKNOWN 398,705 (76.3%), of which 2,690 carry lookup terms without a usable continent (including explicit UNKNOWN terms). 123,812 + 398,705 = 522,517 (tested). These are draft mapping-coverage counts, not scored cuisine results.

Parv accepts the 20-recipe reporting cut and 12.9% cuisine coverage with this
limitation disclosed. Country-cuisine coverage and its 2,643 conflicts did not
change after his rulings. Conflicting cuisine recipes are to be excluded from
single-cuisine scoring, with their CONFLICTING flag and count retained; CONFLICTING
is not a scored class. The census writes aggregate counts only and implements no
scoring or per-recipe label export.

## Count discrepancy census vs map (fixed)
The census counts per (tag, source_column); the map counts a tag once per recipe over Keywords OR RecipeCategory. Example: Easy = 276,838 (Keywords) + 727 (RecipeCategory) = 277,565 (no recipe has it in both). Map `n_recipes` is now defined as that union, and the map carries `n_recipes_keywords` and `n_recipes_category`, which equal the census rows (tested; max(k,c) <= n <= k+c).

## Explicit-vs-derived overlap check
Not possible. `cuisine_if_explicit` is non-null for BBC 6,977, Gutenberg 51,492, Wikibooks 1,675, and 0 for Food.com and TasteSet; the sources with explicit labels have no Food.com-style tags and Food.com has no explicit labels. No source has both, so agreement of derived with explicit cannot be measured and is not imputed.

## Confound warning
Food.com is 522,517 of 612,782 recipes (85.3%). Derived cuisine would exist almost only for Food.com, while explicit labels come almost only from Gutenberg/BBC/Wikibooks. Derived cuisine and source are therefore tied (cuisine = source, THR-35P-26), and derived labels (`DERIVED_FROM_TAG`) must never be pooled with explicit ones in one claim. Only 12.9% of Food.com recipes get a label and the tags are author-chosen, so label coverage is itself selective.

## Remaining review gates
1. Kush/expert review of Parv's lookup choices, including the expanded REGION definition; cuisine expert not yet appointed (plan estimates 4-6 h).
2. Both humans sign the final mapping/protocol, or Kush records an authorised single-signer reason. No such signatures or override exist.
3. No scored cuisine result until G35-PRE; derived-only Food.com classes still cannot meet the two-source-family headline requirement alone. The pending expert review is not waived by zero NEEDS_HUMAN map rows.
