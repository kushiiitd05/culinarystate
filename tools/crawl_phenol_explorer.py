#!/usr/bin/env python3
"""Polite, resumable crawl of Phenol-Explorer retention-factor pages into the local HTML cache.

  /opt/anaconda3/bin/python tools/crawl_phenol_explorer.py
~1,900 requests at 1.5 s. Cached pages are never re-fetched. Progress -> logs/crawl_phenol_explorer.log
"""
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.phenol_explorer import CachedFetcher, parse_food_processing, parse_list_page  # noqa

LOG = ROOT / "logs" / "crawl_phenol_explorer.log"


def log(msg):
    line = f"{datetime.now():%H:%M:%S} {msg}"
    print(line, flush=True)
    with LOG.open("a") as fh:
        fh.write(line + "\n")


f = CachedFetcher(ROOT / "data" / "raw" / "phenol_explorer" / "html")
rows, last = parse_list_page(f.get("/retention-factors/polyphenols"))
for p in range(2, last + 1):
    rows += parse_list_page(f.get(f"/retention-factors/polyphenols?page={p}"))[0]
fps = sorted({r.fp_path for r in rows})
log(f"list rows={len(rows)} fp_pages={len(fps)}")
details = set()
failures = []


def safe_get(path):
    try:
        return f.get(path)
    except Exception as e:  # noqa: BLE001 — log, skip, re-run later picks it up
        failures.append(path)
        log(f"FAILED {path}: {type(e).__name__}: {str(e)[:120]}")
        return ""


for i, fp in enumerate(fps, 1):
    details |= {x.details_path for x in parse_food_processing(safe_get(fp))}
    if i % 50 == 0:
        log(f"fp {i}/{len(fps)} details_so_far={len(details)} fetched={f.fetched}")
log(f"fp done; details pages={len(details)}")
for i, d in enumerate(sorted(details), 1):
    safe_get(d)
    if i % 100 == 0:
        log(f"details {i}/{len(details)} fetched={f.fetched}")
log(f"DONE fetched_this_run={f.fetched} details={len(details)} failures={len(failures)}")
if failures:
    sys.exit(2)
