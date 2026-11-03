#!/usr/bin/env python
"""Step 17b (S155): counts-only Rung A report on SYNTHETIC inputs only. DRAFT_PENDING_16c.

Runs Rung A, validators V1-V4 and the invented-value auditor over the synthetic
fixtures in culinarystate.extraction.rung_a_measure and the 17 synthetic hard-case
prompts (annotation/hard_case_catalog_v2_DRAFT.jsonl, read-only; outcomes stay
blank) and writes integer counts by code. Labelled SYNTHETIC_NOT_GOLD: not a gold
score, not a quality estimate, not a human gate.

    python tools/step17b_rung_a_synthetic_report.py
Default output: reports/step17/rung_a_synthetic_counts.json (refuses overwrite).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.extraction import rung_a_measure as M  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

OUT = "reports/step17/rung_a_synthetic_counts.json"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / OUT), help=f"new counts-only JSON (default {OUT})")
    a = ap.parse_args(argv)
    report = M.synthetic_report(ROOT)
    try:
        D.write_report(Path(a.out), report, root=ROOT)
    except D.DryRunError as exc:
        ap.error(str(exc))
    print(json.dumps({"label": report["label"], "output": a.out,
                      "fixtures_invented": report["fixtures"]["invented_count"],
                      "hard_cases_invented": report["hard_cases"]["invented_count"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
