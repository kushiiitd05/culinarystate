#!/usr/bin/env python3
"""DEL-1: fetch (pinned) + parse + ingest USDA Retention Factors R6 into the ledgers.

  /opt/anaconda3/bin/python tools/ingest_usda_r6.py [--root ledgers/data]
Idempotent: unchanged records are skipped; changed parses append a new version.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.acquire import fetch  # noqa: E402
from culinarystate.ingest.usda_r6 import read_rows  # noqa: E402
from culinarystate.ingest.usda_r6_build import build  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

BASE = "https://www.ars.usda.gov/ARSUserFiles/80400525/Data/retn/"

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=str(ROOT / "ledgers" / "data"))
a = ap.parse_args()
raw = ROOT / "data" / "raw" / "usda_r6"
snaps = [fetch(BASE + f, raw / f) for f in ("retn06.txt", "retn06.pdf")]
rows = read_rows(raw / "retn06.txt")
counts = build(LedgerStore(Path(a.root)), rows, snaps)
for (rt, action), n in sorted(counts.items()):
    print(f"{rt:6s} {action:9s} {n}")
