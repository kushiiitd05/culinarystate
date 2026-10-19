# API and dataset survey (S115, 2026-10-20) — what helps CulinaryState, under what terms
Read terms pages only; no key was used, nothing ledgered. Keys pasted in chat are NOT stored anywhere in the repo; load
from env var only and rotate (they appeared in a transcript).

| Source | What | Terms found | Verdict |
|---|---|---|---|
| Spoonacular | 365k+ recipes, nutrition, parse | ToS: may store only recipe id/title/image URL; cache <=1h; no derived/transformed datasets; delete on stop | NO ledger ingestion. Optional live baseline only, no stored output |
| TheMealDB | ~300 meals, ingredients, steps | test key 1 = dev/educational; public app needs paid; licence not stated | Tiny; manual spot-check only, DERIVED_ONLY if at all |
| TheCocktailDB | cocktails, ingredients | same model; premium $10 for app release | Off-scope for retention/state; flavour pairing demo at most |
| Zestful | POST /parseIngredients -> qty/unit/product/prep + FDC id | sandbox quota unstated; ToS unread | Useful as external baseline for our ingredient parser/linker on a text-free sample; never send BBC text (D-003) |
| ReceptAPI (SE) | Swedish recipes, rewritten text, allergens | 50/day anon; mass download needs data licence | Not useful (Swedish, rate-limited, no mass use) |
| TinyPlate | key given, docs not provided | UNKNOWN | Not assessed; send docs |
| Kaggle Food.com Recipes+Reviews (irkaal/shuyangli94) | 522k recipes, steps, nutrition, 1.4M reviews | check page licence; Food.com scrape | Candidate for REC corpus (steps) after licence check |
| Kaggle Recipe Ingredients (cuisine) | ingredient lists only | check | low value |
| USDA retention/yield (Ag Data Commons) | already in EVD (R6) | public domain | done |
| Open Food Facts | packaged foods | ODbL, share-alike | already used for aliases; products not needed |
| Other open leads to verify (not yet checked) | RecipeNLG, Recipe1M+ (access form), FoodKG, FoodOn, FNDDS, EuroFIR (paid) | per source | verify licence before download |

Priority for the thesis: evidence (retention/yield by ingredient+process) is the bottleneck for H_STATE-R, not recipes.
So the best next sources are nutrient-retention/yield tables, not recipe APIs.
