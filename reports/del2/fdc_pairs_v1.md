# FDC SR Legacy raw/cooked pairs v1 (X15, SSOT §198.7)

Dry-basis ratio R = (N_c/(100-w_c)) / (N_r/(100-w_r)) equals true retention iff total solids are conserved;
descriptions are paired, samples are not matched (SSOT caveat), so rows are candidates, not EVD.
'analytical' = both values from source codes 1/6/13; imputed values (incl. retention-factor calculations) are
circular against R6.

- pairs: 867
- pairs_with_ratio: 867
- ratio_rows: 16365
- analytical_rows: 4984
- pairs_linked_to_ING: 830
- methods: {'roast': 211, 'braise': 168, 'boil': 127, 'grill': 112, 'broil': 82, 'cook': 73, 'fry': 30, 'simmer': 24, 'stew': 24, 'bake': 9, 'steam': 5, 'microwave': 2}

## L1 ingredient x step: R6 vs FDC dry-basis (all)
- overlap_cells: 347
- ingredients: 8
- steps: ['braise', 'broil', 'cook', 'fry', 'roast', 'simmer']
- nutrients: 17
- mae_same_cell: 0.1673
- median_ae: 0.0994
- share_within_0.10: 0.507
- spearman: 0.521
- mae_from_A_step_nutrient_mean: 0.1662
- mae_B_global_mean: 0.2769
- censored_share_a: 0.207
- censored_share_b: 0.0
  - ING-002106 / broil / folate: R6=0.75 FDC=3.733
  - ING-000374 / fry / vitamin_a: R6=0.75 FDC=2.319
  - ING-000374 / broil / folate: R6=0.85 FDC=2.387
  - ING-002106 / braise / carotenoids: R6=0.775 FDC=1.856
  - ING-000374 / fry / calcium: R6=0.75 FDC=1.667

## L2 group x step-family: R6 vs FDC dry-basis (all)
- overlap_cells: 246
- ingredients: 6
- steps: ['BOIL', 'DRY_HEAT', 'FRY', 'STEAM', 'STEW']
- nutrients: 17
- mae_same_cell: 0.1629
- median_ae: 0.0856
- share_within_0.10: 0.537
- spearman: 0.432
- mae_from_A_step_nutrient_mean: 0.1696
- mae_B_global_mean: 0.1861
- censored_share_a: 0.315
- censored_share_b: 0.0
  - FISH / FRY / sodium: R6=0.975 FDC=2.729
  - FRUIT / FRY / vitamin_b6: R6=0.9 FDC=2.295
  - FRUIT / DRY_HEAT / folate: R6=0.6 FDC=1.9
  - VEGETABLE / BOIL / vitamin_b12: R6=0.975 FDC=0.0
  - VEGETABLE / FRY / vitamin_b12: R6=0.975 FDC=0.0

## L1 ingredient x step: R6 vs FDC dry-basis (analytical)
- overlap_cells: 283
- ingredients: 7
- steps: ['braise', 'broil', 'cook', 'fry', 'roast', 'simmer']
- nutrients: 17
- mae_same_cell: 0.1408
- median_ae: 0.0974
- share_within_0.10: 0.53
- spearman: 0.494
- mae_from_A_step_nutrient_mean: 0.1292
- mae_B_global_mean: 0.1691
- censored_share_a: 0.226
- censored_share_b: 0.0
  - ING-002106 / fry / folate: R6=0.8 FDC=2.031
  - ING-002106 / braise / carotenoids: R6=0.775 FDC=1.856
  - ING-002106 / fry / carotenoids: R6=0.75 FDC=1.626
  - ING-000267 / simmer / vitamin_a: R6=0.775 FDC=0.0
  - ING-000080 / fry / vitamin_c: R6=0.8 FDC=0.102

## L2 group x step-family: R6 vs FDC dry-basis (analytical)
- overlap_cells: 190
- ingredients: 4
- steps: ['BOIL', 'DRY_HEAT', 'FRY', 'STEAM', 'STEW']
- nutrients: 17
- mae_same_cell: 0.1991
- median_ae: 0.1093
- share_within_0.10: 0.458
- spearman: 0.308
- mae_from_A_step_nutrient_mean: 0.1962
- mae_B_global_mean: 0.2145
- censored_share_a: 0.328
- censored_share_b: 0.0
  - VEGETABLE / FRY / vitamin_b1: R6=0.85 FDC=5.523
  - VEGETABLE / DRY_HEAT / carotenoids: R6=0.945 FDC=3.232
  - FRUIT / FRY / vitamin_b6: R6=0.9 FDC=2.295
  - FRUIT / DRY_HEAT / folate: R6=0.6 FDC=1.9
  - VEGETABLE / FRY / vitamin_c: R6=0.785 FDC=0.0
