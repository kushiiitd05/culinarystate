# KGE concept edges v1 (X3c, D-011)

Recipes scanned: {'BBCGF-A1': 11934, 'WIKIBOOKS-COOKBOOK': 3676}

| predicate                |   edges |   high |   medium |   median_support |
|:-------------------------|--------:|-------:|---------:|-----------------:|
| COMPONENT_CONTAINS_ING   |      49 |      0 |       12 |              7   |
| ING_CO_OCCURS            |    3683 |   2077 |     1606 |             33   |
| ING_HAS_CATEGORY         |     631 |    485 |      146 |             18   |
| ING_MEASURED_IN_UNIT     |    1137 |    109 |      229 |             27   |
| ING_PARENT               |     315 |      0 |      315 |             13   |
| ING_PROCESSED_BY         |     776 |     95 |      470 |             19   |
| ING_USED_IN_CUISINE      |    1564 |    173 |      659 |             10   |
| PROC_FOLLOWED_BY         |      30 |      9 |        9 |             59.5 |
| PROC_IN_FAMILY           |     156 |      0 |      156 |            439   |
| PROC_TYPICAL_DURATION    |      28 |     12 |       10 |             67.5 |
| PROC_TYPICAL_TEMPERATURE |       5 |      1 |        3 |             61   |
| PROC_USES_TOOL           |     334 |    142 |      192 |             53.5 |
| TOOL_HAS_CATEGORY        |     116 |      0 |      116 |              0   |

Ledger writes: {'unchanged': 8824}

Examples:
- PROC_USES_TOOL: preheat→oven (n=5519, lift=2.504); bake→oven (n=3576, lift=1.587); fry→frying pan (n=2995, lift=3.052); bake→baking tray (n=2696, lift=2.496); bake→baking parchment (n=1874, lift=2.493); line→baking parchment (n=1555, lift=4.743)
- PROC_FOLLOWED_BY: line→bake (n=1142, lift=1.21); insert→rinse (n=353, lift=1.814); thread→insert (n=350, lift=4.605); whip→beat (n=263, lift=2.559); knead→spread (n=253, lift=1.256); melt→microwave (n=144, lift=1.242)
- ING_PROCESSED_BY: butter→brush (n=1638, lift=1.36); butter→melt (n=1513, lift=2.268); egg→beat (n=1361, lift=1.643); onion→fry (n=1283, lift=1.445); egg→whisk (n=950, lift=1.709); baking powder→bake (n=732, lift=2.201)
- ING_CO_OCCURS: onion→garlic (n=1681, lift=2.005); garlic→onion (n=1681, lift=2.005); plain flour→butter (n=1320, lift=2.33); butter→plain flour (n=1320, lift=2.33); egg→plain flour (n=1139, lift=2.405); plain flour→egg (n=1139, lift=2.405)
- ING_USED_IN_CUISINE: olive oil→Italian (n=437, lift=1.98); golden caster sugar→British (n=415, lift=1.753); icing sugar→British (n=327, lift=1.698); self-raising flour→British (n=321, lift=2.143); coriander→Indian (n=263, lift=4.449); parmesan→Italian (n=256, lift=5.825)
- typical durations (median min, n): bake 25.0 (n=847), cook 9.0 (n=769), chill 60.0 (n=296), boil 8.0 (n=269), simmer 15.0 (n=246), cool 10.0 (n=157), heat 8.75 (n=136), stir 5.5 (n=126), mix 13.75 (n=124), rest 15.0 (n=118)

Statistical edges are corpus associations (recipe text), not chemistry; confidence = 95% Wilson lower bound of P(object|subject); durations/temperatures are as written in steps (setpoint vs core unknown).
