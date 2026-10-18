#!/usr/bin/env python3
"""Ledger EDA report: reports/eda/ledger_eda.{html,md,json}.

  /opt/anaconda3/bin/python tools/eda_report.py [--prefixes EVD,ING,PROC,COND]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.eda.report import build_report, to_html, to_markdown  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--prefixes", default="")
ap.add_argument("--out", default=str(ROOT / "reports" / "eda"))
a = ap.parse_args()
rep = build_report(LedgerStore(), tuple(a.prefixes.split(",")) if a.prefixes else None)
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
(out / "ledger_eda.json").write_text(json.dumps(rep, indent=1, default=str))
(out / "ledger_eda.html").write_text(to_html(rep))
(out / "ledger_eda.md").write_text(to_markdown(rep))
print(to_markdown(rep))
