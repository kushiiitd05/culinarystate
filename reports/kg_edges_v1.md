# KGE concept edges v1 (X3c, D-011)

Recipes scanned: {'BBCGF-A1': 11934, 'WIKIBOOKS-COOKBOOK': 3676, 'GUTENBERG-PD': 73778}

| predicate                |   edges |   high |   medium |   median_support |
|:-------------------------|--------:|-------:|---------:|-----------------:|
| COMPONENT_CONTAINS_ING   |      49 |      0 |       12 |              7   |
| ING_ALTERNATIVE_TO       |     220 |      6 |       88 |              7.5 |
| ING_CO_OCCURS            |    6864 |   5019 |     1845 |             59   |
| ING_HAS_CATEGORY         |     631 |    485 |      146 |             18   |
| ING_MEASURED_IN_UNIT     |    1150 |    485 |      583 |             27   |
| ING_OFTEN_OPTIONAL       |      40 |     11 |       29 |             23   |
| ING_PARENT               |     315 |      0 |      315 |             13   |
| ING_PREP_FORM            |     596 |    262 |      334 |             25   |
| ING_PROCESSED_BY         |    2132 |    447 |     1244 |             26   |
| ING_USED_IN_CUISINE      |    2330 |    522 |      971 |             14   |
| PROC_ENDPOINT_STATE      |      47 |     15 |       26 |             58   |
| PROC_FOLLOWED_BY         |      63 |     23 |       18 |             70   |
| PROC_IN_FAMILY           |     156 |      0 |      156 |            439   |
| PROC_TYPICAL_DURATION    |      39 |     21 |        9 |            124   |
| PROC_TYPICAL_TEMPERATURE |      10 |      3 |        4 |             46   |
| PROC_USES_MEDIUM         |      35 |     16 |       15 |             96   |
| PROC_USES_TOOL           |     543 |    291 |      252 |             88   |
| TOOL_HAS_CATEGORY        |     119 |      0 |      119 |              0   |

Ledger writes: {'unchanged': 15339}

Examples:
- PROC_USES_TOOL: bake→oven (n=11734, lift=2.235); preheat→oven (n=5671, lift=4.523); fry→frying pan (n=3986, lift=4.878); strain→sieve (n=3224, lift=6.413); bake→baking tray (n=3090, lift=2.97); heat→frying pan (n=2870, lift=2.37)
- PROC_FOLLOWED_BY: heat→preheat (n=3982, lift=3.098); whip→beat (n=2124, lift=1.953); cut→dice (n=1609, lift=1.796); rub-in→strain (n=1264, lift=1.258); preheat→line (n=477, lift=1.407); pick→rinse (n=460, lift=1.333)
- ING_PROCESSED_BY: salt→season (n=20293, lift=1.51); cream→beat (n=14019, lift=3.272); pepper→season (n=11497, lift=1.799); butter→melt (n=7293, lift=1.782); onion→chop (n=4077, lift=1.669); baking powder→bake (n=3935, lift=3.144)
- ING_CO_OCCURS: pepper→salt (n=15289, lift=2.344); salt→pepper (n=15289, lift=2.344); flour→milk (n=9439, lift=2.026); milk→flour (n=9439, lift=2.026); yolk→egg (n=7530, lift=2.942); egg→yolk (n=7530, lift=2.942)
- ING_USED_IN_CUISINE: sauce→English (n=1780, lift=1.563); lemon→English (n=1398, lift=1.555); molasses→American (n=1388, lift=1.575); gravy→English (n=1317, lift=2.764); cracker→American (n=1292, lift=1.591); mace→English (n=1037, lift=3.32)
- ING_ALTERNATIVE_TO: chicken stock→vegetable stock (n=106, lift=11.34); vegetable stock→chicken stock (n=106, lift=11.34); sunflower oil→vegetable oil (n=98, lift=6.907); vegetable oil→sunflower oil (n=98, lift=6.907); parmesan→vegetarian alternative (n=81, lift=44.007); vegetarian alternative→parmesan (n=81, lift=44.007)
- ING_PREP_FORM: garlic→crushed (n=1375, lift=15.711); egg→beaten (n=1099, lift=20.547); onion→finely chopped (n=844, lift=7.65); onion→chopped (n=801, lift=4.618); butter→softened (n=770, lift=18.306); tomato→chopped (n=714, lift=8.744)
- PROC_USES_MEDIUM: boil→water (n=5951, lift=1.577); beat→cream (n=2485, lift=3.296); fry→butter (n=1435, lift=1.79); heat→oil (n=864, lift=1.572); soak→water (n=812, lift=1.392); fry→fat (n=708, lift=3.278)
- PROC_ENDPOINT_STATE: blend→smooth (n=539, lift=4.577); beat→stiff (n=388, lift=1.83); stir→dissolved (n=267, lift=2.551); fry→golden brown (n=231, lift=2.019); fry→softened (n=226, lift=1.847); whisk→smooth (n=219, lift=2.437); fry→brown (n=211, lift=1.756); beat→creamy (n=198, lift=1.829); knead→smooth (n=192, lift=3.682); chill→firm (n=185, lift=6.108)
- ING_OFTEN_OPTIONAL: salt→OPTIONAL (n=770, lift=5.628); pepper→OPTIONAL (n=288, lift=6.096); sugar→OPTIONAL (n=139, lift=1.813); parsley→OPTIONAL (n=99, lift=1.709); black pepper→OPTIONAL (n=87, lift=3.266); coriander leaf→OPTIONAL (n=80, lift=2.745)
- typical durations (median min, n): bake 27.5 (n=3030), boil 15.0 (n=1799), cook 12.0 (n=1420), simmer 20.0 (n=847), chill 60.0 (n=355), stir 5.0 (n=259), fry 5.0 (n=245), heat 13.75 (n=218), cool 15.0 (n=205), soak 60.0 (n=205)

Statistical edges are corpus associations (recipe text), not chemistry; confidence = 95% Wilson lower bound of P(object|subject); durations/temperatures are as written in steps (setpoint vs core unknown).
