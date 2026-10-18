# R4 graph expansion — leave-cell-out retention interpolation v1 (1500 cells, seed 7)

Prediction of a hidden (ingredient, process, target) cell median from the remaining evidence; fraction scale. Silver dev analysis.

| system | coverage | MAE (own covered) | MAE (common subset, n=104) |
|---|---|---|---|
| B0 | 0.873 | 0.1854 | 0.0722 |
| RP | 0.071 | 0.0792 | 0.0769 |
| RG | 0.386 | 0.1302 | 0.0699 |
| RGN | 0.203 | 0.0494 | 0.0772 |
| RGU | 0.671 | 0.1079 | 0.0956 |

Paired |error| differences on the common subset (negative = first system better):

| pair | Δ MAE [95% CI] |
|---|---|
| RG − B0 | -0.0023 [-0.0170, +0.0118] |
| RGN − B0 | +0.0050 [-0.0110, +0.0204] |
| RP − B0 | +0.0047 [-0.0114, +0.0202] |
| RG − RP | -0.0070 [-0.0128, -0.0014] |
| RGN − RG | +0.0073 [+0.0016, +0.0137] |

Cells newly covered by RG (RP had nothing, B0 available): 467; MAE RG 0.1398 vs B0 0.1218; paired Δ +0.0180 [-0.0029, +0.0420].
Cells newly covered by RGN (RP had nothing, B0 available): 198; MAE RGN 0.032 vs B0 0.0584; paired Δ -0.0264 [-0.0351, -0.0173].
Cells newly covered by RGU (RP had nothing, B0 available): 895; MAE RGU 0.1059 vs B0 0.0879; paired Δ +0.0179 [+0.0120, +0.0235].

| relation | cells | MAE of that relation's median | B0 MAE on the same cells | paired Δ [95% CI] |
|---|---|---|---|---|
| PARENT | 118 | 0.0482 | 0.0564 | -0.0081 [-0.0219, +0.0053] |
| CHILD | 122 | 0.0356 | 0.0634 | -0.0278 [-0.0398, -0.0160] |
| SIBLING | 343 | 0.1828 | 0.1464 | +0.0364 [+0.0072, +0.0699] |
| ANCESTOR | 18 | 0.0194 | 0.0667 | -0.0472 [-0.0653, -0.0292] |
| GROUP_ROW | 51 | 0.0873 | 0.075 | +0.0123 [-0.0049, +0.0289] |
