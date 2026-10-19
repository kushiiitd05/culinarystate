#!/usr/bin/env python3
"""API-RECON-01: recover Foodoscope/CoSyLab API contracts from PUBLIC client code (GitHub search + file reads only).

  /opt/anaconda3/bin/python tools/recon_foodoscope_public.py
Never calls the Foodoscope API. Every committed credential-looking string is replaced by <REDACTED> before anything is stored
or printed; credentials are treated as compromised and never used. Writes registry/sources/foodoscope_public_usage_registry.csv.
Host, path, auth-header pattern and query-parameter names are extracted from string literals; 'reported working' is NOT inferred.
"""
import base64
import csv
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMS = ["api.foodoscope.com", "recipe2-api", "recipeByTitle", "foodoscope_client", "molecules_data", "flavordb entities"]
TOKEN = re.compile(r"(?<![A-Za-z0-9_\-])[A-Za-z0-9_\-]{32,}(?![A-Za-z0-9_\-])")
URL = re.compile(r"https?://(?:api\.foodoscope\.com|cosylab\.iiitd\.edu\.in)[^\s\"'`)>,]*", re.I)
PATH = re.compile(r"[\"'`](/(?:recipe|recipes|search-recipe|instructions|entities|food|molecules_data|properties|search_plants|recipe-bytitle|recipes_cuisine|[A-Za-z_\-]+)[A-Za-z0-9_\-/{}$.]*)[\"'`]")
PARAM = re.compile(r"params\s*[=:]\s*\{([^}]{0,200})\}")


def gh(args):
    r = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=60)
    return r.stdout if r.returncode == 0 else ""


def redact(s):
    return TOKEN.sub("<REDACTED>", s)


def main():
    seen = {}
    for t in TERMS:
        out = gh(["search", "code", t, "--limit", "12", "--json", "repository,path"])
        for x in json.loads(out or "[]"):
            seen[(x["repository"]["nameWithOwner"], x["path"])] = None
        time.sleep(2)
    rows, auth_hits = [], 0
    for (repo, path) in sorted(seen):
        if not path.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".txt", ".json", ".ipynb")):
            continue
        content = gh(["api", f"repos/{repo}/contents/{path}", "--jq", ".content"])
        try:
            text = base64.b64decode(content).decode("utf-8", "ignore")
        except Exception:
            continue
        if "foodoscope" not in text.lower() and "cosylab" not in text.lower():
            continue
        hosts = sorted({re.match(r"https?://[^/]+(?:/recipe2-api|/recipedb|/flavordb|/spicerx)?", u).group(0) for u in URL.findall(text)})
        paths = sorted({p for p in PATH.findall(text) if len(p) > 3})[:25]
        auth = []
        if re.search(r"authorization[\"']?\s*[:=]\s*f?[\"']Bearer", text, re.I):
            auth.append("Authorization: Bearer")
        if re.search(r"x-api-key", text, re.I):
            auth.append("x-api-key")
        params = sorted({redact(m)[:120] for m in PARAM.findall(text)})[:6]
        committed_secret = bool(re.search(r"(api_?key|token|bearer)[\"'\s:=]+[\"'][A-Za-z0-9_\-]{32,}[\"']", text, re.I))
        auth_hits += committed_secret
        rows.append({"repository": repo, "file": path, "hosts": ";".join(hosts), "endpoint_paths": ";".join(paths),
                     "auth_pattern": ";".join(auth) or "none seen", "param_literals": " | ".join(params),
                     "committed_credential_seen": "YES (redacted, compromised, not used)" if committed_secret else "no",
                     "observed_on": time.strftime("%Y-%m-%d"), "works_reported": "NOT_INFERRED", "licence_of_repo": "check before reuse"})
        time.sleep(1)
    out = ROOT / "registry" / "sources" / "foodoscope_public_usage_registry.csv"
    cols = list(rows[0]) if rows else ["repository"]
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    hosts = sorted({h for r in rows for h in r["hosts"].split(";") if h})
    print(len(rows), "files in", len({r["repository"] for r in rows}), "repos; files with a committed credential:", auth_hits)
    print("hosts:", hosts)
    print("auth patterns:", sorted({r["auth_pattern"] for r in rows}))
    print("distinct endpoint paths:", len({p for r in rows for p in r["endpoint_paths"].split(";") if p}))


if __name__ == "__main__":
    main()
