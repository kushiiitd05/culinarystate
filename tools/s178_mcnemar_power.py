#!/usr/bin/env python
"""S178: exact McNemar power / MDE table for H1 at n = 30 and n = 60 (and the per-block n = 15 descriptive case).

Reuses paired_stats.mcnemar_exact and newcombe_paired through evaluation/mcnemar_power.py. Planning grid only (alpha,
target power, discordance rates are arguments, not decisions). Writes reports/s178/mcnemar_power_n30_n60.json and
refuses to overwrite it.

    python tools/s178_mcnemar_power.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evaluation import mcnemar_power as MP  # noqa: E402

OUT = ROOT / "reports/s178/mcnemar_power_n30_n60.json"


def main() -> int:
    table = MP.planning_table(ns=(15, 30, 60))
    design = {f"n{n}_baseline0.5_delta{g}_d{d}": MP.design_interval(n, 0.5, g, d)
              for n, g, d in ((30, 0.3, 0.4), (60, 0.2, 0.4), (60, 0.15, 0.3)) if abs(g) <= d}
    rep = {"tool": "tools/s178_mcnemar_power.py", "module": MP.VERSION, "status": "PLANNING_NON_CITABLE",
           "table": table, "newcombe_at_design_points": design,
           "min_realised_discordant_pairs_for_p05": MP.min_discordant_for_significance(),
           "rejection_rule_n30": {str(m): k for m, k in MP.rejection_table(30).items() if m >= 6},
           "rejection_rule_n60": {str(m): k for m, k in MP.rejection_table(60).items() if m >= 6 and m % 2 == 0},
           "reading": ("MDE = smallest accuracy gap from which exact two-sided McNemar keeps >= target power for every "
                       "larger gap, given a discordance rate d. REV-B (reports/orchestration/review/S176_REV-B_eval_governance.md "
                       "Q26) reported about 0.28-0.33 at n = 30 and 0.16-0.24 at n = 60 for 80 % power under its own "
                       "discordance grid; compare the 'mde' columns. H1 needs two such tests (B4 > B1 and B4 > B2): the "
                       "joint power is only bounded (Frechet) because both share B4's answers."),
           "rule_287_4": ["state the MDE next to every H1 result", "if discordant < min_realised_discordant_pairs_for_p05 say "
                          "'cannot be significant at this n'", "exact test decides, Newcombe interval is descriptive"]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(rep, indent=1, sort_keys=True) + "\n").encode()
    with open(OUT, "xb") as fh:
        fh.write(data)
    print(json.dumps({"out": str(OUT.relative_to(ROOT)), "sha256": hashlib.sha256(data).hexdigest()}))
    for r in table["rows"]:
        print(r["n"], r["discordance"], "MDE", r["mde"], "power@MDE", r.get("power_at_mde"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
