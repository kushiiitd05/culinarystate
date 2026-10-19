# Foodoscope / CoSyLab API audit v1 (S111) — read-only discovery, no key

Method: one unauthenticated request per endpoint (1 req/s, no crawling, nothing downloaded beyond error bodies), plus reading public client code on GitHub for the host and auth pattern. `FOODOSCOPE_API_KEY` is **not set**, so nothing authenticated was tried. Registry: `registry/sources/foodoscope_api_registry.csv` (19 rows).

## Findings
1. **The base URLs in the integration sheet are wrong for the API.** `https://cosylab.iiitd.edu.in/recipedb/...` and `/flavordb/...` are the web UIs: every API path there returns an nginx HTML 404 (12 endpoints, status `WRONG_HOST`). `https://cosylab.iiitd.edu.in/spicerx/search_plants` is a public HTML page, not JSON (`WEB_PAGE_NOT_API`).
2. **The real RecipeDB API host is `https://api.foodoscope.com/recipe2-api/`** (seen in public client code from several student projects). Unauthenticated calls to `/recipe/recipeofday`, `/recipe/recipesinfo` and `/recipe-bytitle/recipeByTitle` return HTTP 400 with `{"error":"ApiKey is not provided"}`: **AUTH_REQUIRED**. That confirms the host exists and that a key is mandatory.
3. **Auth header not verified.** Public code shows two patterns, `Authorization: Bearer <key>` and `x-api-key: <key>`. The client should make the header configurable and try one request each once we have our own key.
4. **FlavorDB, SpiceRx, SustainableFoodDB, DietRxDB and CocktailDB API hosts are unknown.** The code seen only gives the RecipeDB prefix `recipe2-api`; I did not guess other prefixes. They need the Foodoscope API Playground (request URL copied once per endpoint) or the professor's documentation.
5. **Security note.** At least one public repository hard-codes a live-looking Foodoscope key in its client file. It belongs to another project; it was **not** used, not stored in any file here, and should not be. We need our own key (H1 email, item 1). Keys must stay in the environment, never in code (`FOODOSCOPE_API_KEY`, server side only).
6. The integration sheet's claim that FlavorDB needs no authentication cannot be checked until the FlavorDB API host is known.

## Status table
| source | endpoints probed | result |
|---|---|---|
| RecipeDB (api.foodoscope.com/recipe2-api) | 3 | AUTH_REQUIRED (no key) |
| RecipeDB (cosylab web host) | 3 | WRONG_HOST |
| FlavorDB (cosylab web host) | 9 | WRONG_HOST; real host unknown |
| SpiceRx | 1 | web page, not an API |
| RecipeDB id-parameter routes (`/search-recipe/{id}`, `/instructions/{recipe_id}`, `/recipes_cuisine/cuisine/{region}`) | 0 (3 rows, not called) | PARAMETER_UNKNOWN: need a real id from an authenticated call; not invented |

## Next (needs a human)
- Get our own Foodoscope key (H1 email) and put it in `FOODOSCOPE_API_KEY`.
- Then run `tools/probe_foodoscope.py` again (it prints no key), verify the header, record id/region parameters, and capture the other databases' request URLs from the Playground.
- Do not ingest anything into the ledgers until provenance, licence (still UNVERIFIED; D-015) and identifier mappings are understood.
