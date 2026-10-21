#!/usr/bin/env python3
"""ES-1.2: read-only reconciliation of sources already represented in the repo (SRC ledger, ledgers by provenance, local data dirs, ingest code). Changes nothing.
  python tools/es12_local_source_audit.py -> reports/h_state/_es_1_2_local_source_audit.json"""
import glob
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L = ROOT / "ledgers/data"


def latest(name):
    d = {}
    for line in open(L / f"{name}.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            d[r["id"]] = r
    return d


src = latest("SRC")
fam_of = {k: v.get("source_family_id") for k, v in src.items()}
fams = defaultdict(lambda: {"src_ids": [], "titles": set(), "licences": Counter(), "licence_status": Counter(), "storage_rule": Counter(), "year": set(), "url": set(), "kind": Counter()})
for k, v in src.items():
    if v["status"] != "ACTIVE":
        continue
    f = fams[v.get("source_family_id")]
    f["src_ids"].append(k)
    f["titles"].add(v["title"][:110])
    f["licences"][v.get("licence")] += 1
    f["licence_status"][v.get("licence_status")] += 1
    f["storage_rule"][v.get("storage_rule")] += 1
    f["year"].add(str(v.get("year")))
    if v.get("url"):
        f["url"].add(v["url"][:100])
    f["kind"][v.get("kind")] += 1
use = defaultdict(lambda: defaultdict(int))
for led in ("ING", "ALIAS", "MOL", "IMAP", "PROC", "TOOL", "UNIT", "EVD", "REC", "KGE", "ALLERGEN", "COND", "SVAR", "STUDY", "MEAS"):
    for r in latest(led).values():
        if r.get("status") != "ACTIVE":
            continue
        ids = set((r.get("provenance") or {}).get("source_ids") or [])
        if r.get("source_id"):
            ids.add(r["source_id"])
        for i in ids:
            use[fam_of.get(i, "UNKNOWN_SRC")][led] += 1
out = {}
for f, d in fams.items():
    out[f] = {"n_src_records": len(d["src_ids"]), "src_id_range": [min(d["src_ids"]), max(d["src_ids"])], "titles_sample": sorted(d["titles"])[:2], "licences": dict(d["licences"]), "licence_status": dict(d["licence_status"]),
              "storage_rule": dict(d["storage_rule"]), "years": sorted(d["year"]), "kinds": dict(d["kind"]), "records_by_ledger": dict(use.get(f, {})), "url_sample": sorted(d["url"])[:1]}
dirs = {}
for base in ("data/raw", "data/external", "data/interim"):
    for p in sorted(glob.glob(str(ROOT / base / "*"))):
        n = sum(1 for q in Path(p).rglob("*") if q.is_file()) if Path(p).is_dir() else 1
        sz = sum(q.stat().st_size for q in Path(p).rglob("*") if q.is_file()) if Path(p).is_dir() else os.path.getsize(p)
        dirs[f"{base}/{Path(p).name}"] = {"files": n, "MB": round(sz / 1e6, 1)}
scripts = sorted(str(p.relative_to(ROOT)) for p in list((ROOT / "src/culinarystate/ingest").glob("*.py")) + list((ROOT / "src/culinarystate/sources").glob("*.py")) + list((ROOT / "src/culinarystate/evidence").glob("*.py")) + list((ROOT / "src/culinarystate/vocab").glob("*.py")) + list((ROOT / "tools").glob("*ingest*.py")) + list((ROOT / "tools").glob("*download*")) if p.is_file())
(ROOT / "reports/h_state/_es_1_2_local_source_audit.json").write_text(json.dumps({"families": out, "local_dirs": dirs, "ingest_scripts": scripts}, indent=1, default=str))
for f, v in sorted(out.items(), key=lambda kv: -sum(kv[1]["records_by_ledger"].values())):
    print(f"{f:34s} src={v['n_src_records']:3d} lic={list(v['licences'])[:1]} st={list(v['licence_status'])} store={list(v['storage_rule'])} ledgers={v['records_by_ledger']}")
print(len(dirs), "local dirs;", len(scripts), "scripts")
