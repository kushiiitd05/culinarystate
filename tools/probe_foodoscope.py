#!/usr/bin/env python3
"""Read-only Foodoscope/CoSyLab API discovery (S111): ONE request per endpoint, 1 req/s, no crawling, no bulk download.

  FOODOSCOPE_API_KEY=... /opt/anaconda3/bin/python tools/probe_foodoscope.py
Key (if set) is sent as `Authorization: Bearer`, never printed or stored. Without a key only unauthenticated requests are made;
401/403 is recorded as AUTH_REQUIRED and not retried or worked around. Host note: api.foodoscope.com/recipe2-api is the API host seen in public client code; cosylab.iiitd.edu.in/<db>/ are the web UIs (404 for API paths).
Only endpoints observed working by other projects
(class A) are probed; parameter names are NOT guessed, so those endpoints are called without parameters and the status/shape is
recorded (400/422 = PARAMETER_UNKNOWN). Writes registry/sources/foodoscope_api_registry.csv and small redacted fixtures.
"""
import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
BASES = {"RecipeDB(api)": "https://api.foodoscope.com/recipe2-api", "RecipeDB": "https://cosylab.iiitd.edu.in/recipedb", "FlavorDB": "https://cosylab.iiitd.edu.in/flavordb",
         "SpiceRx": "https://cosylab.iiitd.edu.in/spicerx"}
EP = [("RecipeDB(api)", "/recipe-bytitle/recipeByTitle", {"title": "Chicken Curry"}), ("RecipeDB(api)", "/recipe/recipeofday", None),
      ("RecipeDB(api)", "/recipe/recipesinfo", None),
      ("RecipeDB", "/recipe-bytitle/recipeByTitle", {"title": "Chicken Curry"}), ("RecipeDB", "/search-recipe/{id}", None),
      ("RecipeDB", "/instructions/{recipe_id}", None), ("RecipeDB", "/recipe/recipeofday", None),
      ("RecipeDB", "/recipe/recipesinfo", None), ("RecipeDB", "/recipes_cuisine/cuisine/{region}", None),
      ("FlavorDB", "/entities/by-entity-alias-readable", None), ("FlavorDB", "/entities/by-name-and-category", None),
      ("FlavorDB", "/entities/by-natural-source", None), ("FlavorDB", "/food/by-alias", None),
      ("FlavorDB", "/molecules_data/by-flavorProfile", None), ("FlavorDB", "/molecules_data/by-commonName", None),
      ("FlavorDB", "/molecules_data/filter-by-type", None), ("FlavorDB", "/properties/by-description", None),
      ("FlavorDB", "/properties/taste-threshold", None), ("SpiceRx", "/search_plants", {"id": "4045", "page": "1"})]
COLS = ["source", "base_url", "resolved_path", "http_method", "query_parameters", "requires_auth", "auth_header", "status_code",
        "content_type", "response_top_level_keys", "pagination", "rate_limit_observed", "license", "test_timestamp", "provenance", "status"]


def main():
    key = os.getenv("FOODOSCOPE_API_KEY")          # only OUR key from the environment; keys found in public code are never used
    s = requests.Session()
    s.headers.update({"Accept": "application/json", "User-Agent": "CulinaryState-Research/0.1 (IIIT Delhi course project)"})
    auth_used = bool(key)
    if key:
        s.headers["Authorization"] = f"Bearer {key}"
    rows = []
    for src, path, params in EP:
        url = BASES[src] + path
        row = {"source": src, "base_url": BASES[src], "resolved_path": path, "http_method": "GET",
               "query_parameters": json.dumps(params or {}), "auth_header": "Bearer (env)" if auth_used else "none",
               "license": "UNVERIFIED (no licence statement found; use per D-015)", "provenance": "tools/probe_foodoscope.py, 1 request",
               "test_timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "pagination": "", "rate_limit_observed": ""}
        if "{" in path:                                       # needs an id we do not have yet: do not invent one
            row.update(status_code="", content_type="", response_top_level_keys="", requires_auth="UNKNOWN",
                       status="PARAMETER_UNKNOWN", provenance="not called: needs a real id from a previous call")
            rows.append(row)
            continue
        try:
            r = s.get(url, params=params, timeout=20)
            ct = r.headers.get("content-type", "")
            row.update(status_code=r.status_code, content_type=ct.split(";")[0])
            rl = {k: v for k, v in r.headers.items() if k.lower().startswith(("x-ratelimit", "retry-after"))}
            row["rate_limit_observed"] = json.dumps(rl) if rl else ""
            body = None
            if "json" in ct:
                try:
                    body = r.json()
                except ValueError:
                    pass
            if isinstance(body, dict):
                row["response_top_level_keys"] = ",".join(list(body)[:12])
            elif isinstance(body, list):
                row["response_top_level_keys"] = f"list[{len(body)}]"
            err = str(body.get("error", "")) if isinstance(body, dict) else ""
            if r.status_code in (401, 403) or "apikey" in err.lower().replace(" ", ""):
                row.update(requires_auth="YES", status="AUTH_REQUIRED")
            elif r.status_code == 404 and "html" in ct:
                row.update(requires_auth="UNKNOWN", status="WRONG_HOST")        # web UI host, path does not exist
            elif r.status_code in (400, 404, 422):
                row.update(requires_auth="NO" if not auth_used else "UNKNOWN", status="PARAMETER_UNKNOWN")
            elif r.ok:
                row.update(requires_auth="NO" if not auth_used else "UNKNOWN",
                           status="WEB_PAGE_NOT_API" if body is None else "VERIFIED_WORKING" if body not in ([], {}) else "VERIFIED_EMPTY")
                if body is not None:
                    (ROOT / "data" / "interim" / "foodoscope_probe" / f"{src}_{path.strip('/').replace('/', '_')}.json").write_text(
                        json.dumps(body)[:4000])
            else:
                row.update(requires_auth="UNKNOWN", status="BROKEN")
        except requests.RequestException as e:
            row.update(status_code="", content_type="", response_top_level_keys=type(e).__name__, requires_auth="UNKNOWN", status="BROKEN")
        rows.append(row)
        print(src, path, row["status_code"], row["status"], flush=True)
        time.sleep(1.0)
    with (ROOT / "registry" / "sources" / "foodoscope_api_registry.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
