# Foodoscope public implementations audit (API-RECON-01, S113)

Method: GitHub code search plus reading public client files (`tools/recon_foodoscope_public.py`); **no call to the Foodoscope API was made with anyone else's credential**. 30 files in 19 public repositories mention the API. Registry: `registry/sources/foodoscope_public_usage_registry.csv` (hosts, paths, auth pattern, parameter literals; no credential survives: 0 token-like strings, every committed secret replaced by `<REDACTED>`). Licences of the repositories were not checked; reuse of their *code* needs a licence check, reuse of the *contract facts* (host, path, parameter names) does not.

## Credentials
3 of the 30 files contain a committed key. They are treated as compromised and were not used, copied or stored. We need our own key (H1 email item 1; Foodoscope also advertises a free Starter plan with 25 requests/minute per its site, as reported by Kush's reviewer; not verified here). Key: environment `FOODOSCOPE_API_KEY` only.

## Hosts (current vs legacy; do not assume identical schemas)
| family | host | evidence |
|---|---|---|
| CURRENT RecipeDB | `https://api.foodoscope.com/recipe2-api` | public clients; our unauthenticated probe: 400 `{"error":"ApiKey is not provided"}` |
| CURRENT FlavorDB | `https://api.foodoscope.com/flavordb` | public clients; our unauthenticated probe: same body, so **FlavorDB also needs a key on the current host** (the "no auth" report applies to an older deployment) |
| LEGACY | `https://cosylab.iiitd.edu.in/recipedb`, `/flavordb` (web UIs: API paths 404) and `http://cosylab.iiitd.edu.in:6969/...` (old dev port, not probed) | public clients |
| SpiceRx, CocktailDB | API host not found in public client code | needs the Playground |
| SustainableFoodDB, DietRxDB | marked "coming soon" on the Foodoscope site per the reviewer's note; no public client usage found | do not assume availability |

## Contract facts recovered (all UNVERIFIED until we hold a key)
- Auth header: two patterns in public code, `Authorization: Bearer <key>` (most) and `x-api-key: <key>` (some). The client makes it configurable.
- RecipeDB (current): `/recipe-bytitle/recipeByTitle?title=`, `/recipe/recipebyid`, `/recipe/recipebytitle`, `/recipe/recipebycuisine`, `/recipe/recipebycalories`, `/recipe/recipebyrecipediet`, `/recipe/recipebyreciperange`, `/recipe/mealplan`, `/recipe-nutri/nutritioninfo`; also `/search-recipe/{id}` and `/instructions/{id}` from the two-call pattern (title -> id -> details).
- FlavorDB (current): `/entities/by-entity-alias-readable?entity_alias_readable=<name>&page=0&size=1` (Spring paging: `page`, `size`; response `content`, `pageable`, `totalPages`), `/entities/by-nameAndCategory`, `/entities/by-naturalSource`, `/molecules_data/by-commonName`, `/molecules_data/by-flavorProfile` (a public issue note records a parameter-name mismatch: the service expects `flavor_profile`), `/molecules_data/filter-by-type`, `/properties/by-description`, `/properties/by-aromaThresholdValues`, and ~15 numeric range filters (`/more_properties/by-*-range`).
- 55 distinct endpoint paths appear across the files, including some from other APIs (`/recipes/complexSearch` is Spoonacular, not Foodoscope): the registry is a candidate list, not a contract.

## Client
`src/culinarystate/sources/foodoscope_client.py` (+5 mocked tests): credentials from `FOODOSCOPE_API_KEY` only; configurable header mode; configurable base URLs; timeout; retries for safe GETs (5xx/timeouts); explicit `FoodoscopeAuthError` on 401/403 and on a 400 that says the key is missing; bounded Spring-style pagination; rate limit 2.5 s between calls (25/min); optional response snapshots with provenance (URL, params, status, UTC time, sha256) that never contain the key. Convenience wrappers are marked UNVERIFIED.

## Not done / next
No authenticated call, no bulk ingestion, nothing in a ledger. With our own key: run `tools/probe_foodoscope.py`, verify the header and every parameter name against live responses (one request each), record id routes, then decide ledger mappings (licence is still UNVERIFIED, D-015).
