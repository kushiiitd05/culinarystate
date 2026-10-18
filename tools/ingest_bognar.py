#!/usr/bin/env python3
"""X5: Bognár (2002) Part 2 retention factors -> EVD (source family BOGNAR-2002).

  /opt/anaconda3/bin/python tools/ingest_bognar.py
PDF from the KIT repository (pinned by sha256 in SNAP); text via `pdftotext -layout` (poppler).
Tables with column-specific sub-variants are skipped and listed in reports/bognar_v1.md.
"""
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.acquire import fetch  # noqa: E402
from culinarystate.ingest.bognar import parse  # noqa: E402
from culinarystate.ingest.bognar_build import build  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

URL = "https://publikationen.bibliothek.kit.edu/9642002/1928"
PDF = ROOT / "data" / "raw" / "bognar" / "bognar_2002.pdf"
TXT = PDF.with_suffix(".txt")

snap = fetch(URL, PDF)
if not TXT.exists():
    subprocess.run(["pdftotext", "-layout", str(PDF), str(TXT)], check=True)
rows, problems = parse(TXT.read_text())
counts = build(LedgerStore(), rows, snap)
kept = [r for r in rows if r.value != "-"]
lines = ["# Bognár (2002) retention factors v1 (X5)", "",
         f"- PDF sha256 {snap.sha256[:16]}…, {snap.bytes:,} bytes; parsed value cells {len(rows):,}; EVD rows (non '-') {len(kept):,}",
         f"- tables parsed: {len({r.table for r in rows})} of 39; methods: {dict(Counter(r.method for r in kept))}",
         f"- values = 1.00 stored CENSORED (≥ cap / possible default): {sum(r.value == '1.00' for r in kept):,}; "
         f"constituents flagged estimated (preface list): {sum(r.estimated for r in kept):,}",
         f"- ledger writes: {dict(counts)}", "", "Skipped / problems:"] + [f"- {p}" for p in problems]
(ROOT / "reports" / "bognar_v1.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
