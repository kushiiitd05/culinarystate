# DEL-2 cross-source agreement v1 (source-disjoint, SSOT split 6)

Harmonisation: nutrient keys, Bognár portion A only, aligned on (ingredient, first step, nutrient); censored at lower bound.
Phenol-Explorer targets are polyphenols, so it has no nutrient overlap with USDA/Bognár (expected).

## L1 ingredient-level: USDA-RETN-R6 vs BOGNAR-2002
- overlap_cells: 67
- ingredients: 4
- steps: ['roast']
- nutrients: 17
- mae_same_cell: 0.0751
- median_ae: 0.05
- share_within_0.10: 0.687
- spearman: 0.611
- mae_from_A_step_nutrient_mean: 0.0681
- mae_B_global_mean: 0.1165
- censored_share_a: 0.134
- censored_share_b: 0.284
  - chicken / roast / copper: A=0.95 B=0.6
  - turkey / roast / vitamin_b12: A=0.65 B=0.9
  - turkey / roast / sodium: A=0.75 B=0.995
  - turkey / roast / potassium: A=0.75 B=0.98
  - chicken / roast / potassium: A=0.8 B=0.6
  - chicken / roast / vitamin_b6: A=0.8 B=0.6

## L1 ingredient-level: USDA-RETN-R6 vs PHENOL-EXPLORER-3.6
- overlap_cells: 0

## L1 ingredient-level: BOGNAR-2002 vs PHENOL-EXPLORER-3.6
- overlap_cells: 0

## L2 food-group x step-family: USDA-RETN-R6 vs BOGNAR-2002
- overlap_cells: 249
- ingredients: 4
- steps: ['BOIL', 'DRY_HEAT', 'FRY', 'STEAM', 'STEW']
- nutrients: 17
- mae_same_cell: 0.0831
- median_ae: 0.0556
- share_within_0.10: 0.695
- spearman: 0.693
- mae_from_A_step_nutrient_mean: 0.0966
- mae_B_global_mean: 0.116
- censored_share_a: 0.322
- censored_share_b: 0.148
  - POULTRY / BOIL / copper: A=0.95 B=0.5
  - POULTRY / BOIL / sodium: A=0.838 B=0.4
  - VEGETABLE / BOIL / potassium: A=0.922 B=0.488
  - VEGETABLE / BOIL / magnesium: A=0.958 B=0.6
  - VEGETABLE / BOIL / vitamin_b12: A=0.975 B=0.633
  - VEGETABLE / STEAM / vitamin_b12: A=0.975 B=0.633

Caveats: some aligned cells are table defaults for nutrients absent in the food (e.g. vitamin B12 in vegetables);
USDA %TR/%AR vs Bognár true retention are close but not identical definitions; Bognár "estimated" values are not
separable (grey shading lost in text). Largest systematic disagreement: mineral leaching in boiled vegetables/poultry.
