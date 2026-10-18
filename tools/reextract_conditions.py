#!/usr/bin/env python3
"""Re-run temperature extraction on Phenol-Explorer COND records after an extractor fix (new versions only).

  /opt/anaconda3/bin/python tools/reextract_conditions.py
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence.conditions import extract_conditions  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

PREFIX = "food after processing: "
st = LedgerStore()
w = Counter()
for c in st.all_latest("COND"):
    loc = c["provenance"].get("locator") or ""
    if not loc.startswith(PREFIX):
        continue
    temps = extract_conditions(loc[len(PREFIX):])["temperatures"]
    if temps == (c.get("temperatures") or []):
        continue
    mask = {**c["completeness_mask"], "temperature": temps[0]["value"]["status"] if temps else "UNKNOWN"}
    new = {**c, "completeness_mask": mask}
    new.pop("temperatures", None)
    if temps:
        new["temperatures"] = temps
    w[st.upsert(new)[0]] += 1
print("COND writes:", dict(w))
