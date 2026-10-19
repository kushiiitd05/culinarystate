# API_BLOCKERS — what is blocked, impact, workaround, who unblocks

| # | Blocker | Impact | Workaround in place | Unblock action (owner) |
|---|---|---|---|---|
| 1 | RecipeDB / RecipeDB3 API key + licence | RecipeDB3 NER reproduction; RecipeDB name crosswalk; DEL-1 "names normalised to RecipeDB" clause | A1 BBC corpus + TASTEset; ING crosswalk `UNRESOLVED_EXTERNAL` (AH2) | Send H1 email to Prof. Bagler (Kush) — draft `handoff/H1_email_bagler.md` (2026-10-19). Found: RecipeDB 3.0 API docs on Postman (33 endpoints, base URL not public); RecipeDB3 NER code+data public on GitHub but **no licence** -> not downloaded until permission |
| 2 | FlavorDB bulk access | ingredient↔molecule presence for flavour compounds | PubChem identities + Phenol-Explorer measured contents (IMAP) | Same email; ask for FlavorDB2 dump/terms (Kush) |
| 3 | FSIS / FoodSafety.gov charts return 403 to scripts | food-safety WARN rules (temperatures) | none — no safety warning without authority text | Open in a browser, save HTML/PDF to `data/raw/fsis/` (Parv), then run WARN builder |
| 4 | Router DNS SERVFAIL for *.usda.gov | downloads fail | `curl --resolve` with public-DNS IP | optional: set Mac DNS to 1.1.1.1 |
| 5 | FDC API DEMO_KEY rate limit | live FDC lookups | bulk SR Legacy CSV used instead | free api.data.gov key if live lookups are needed |
| 6 | rdkit not installed in any conda env | ECFP/Morgan fingerprints, RDKit descriptors | PubChem CACTVS 881-bit fingerprint + PubChem descriptors | `conda install -n recsys_env -c conda-forge rdkit` (approve first) |
| 7 | TabPFN not installed / GPU | DEL-2 D6 | recorded SKIPPED | install on A100 server only if a card justifies it |
| 8 | Human verification | DEL-1 ≥40 verified literature rows; DEL-3 ≥40 Gold recipes; allergen + FDC link sign-off | queues prepared, tools ready | Kush + Parv: work the queues (see MANUAL_NEXT_STEPS.md) |

| 9 | Foodoscope API key (RecipeDB2/3 API at api.foodoscope.com/recipe2-api) | live RecipeDB/FlavorDB/SpiceRx calls; name crosswalk | web UIs cannot serve API paths (404); unauthenticated API answers `ApiKey is not provided` | request our own key (H1 email item 1); never use keys found in public repos; hosts for FlavorDB/SpiceRx/SustainableFoodDB/DietRxDB/CocktailDB still unknown (S111, `reports/sources/foodoscope_api_audit_v1.md`) |
