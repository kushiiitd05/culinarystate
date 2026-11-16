#!/usr/bin/env python
"""S178: exact McNemar power / MDE table for H1 at n = 30 and n = 60 (and the per-block n = 15 descriptive case).

Reuses paired_stats.mcnemar_exact and newcombe_paired through evaluation/mcnemar_power.py. Planning grid only (alpha,
target power, discordance rates are arguments, not decisions). Writes reports/s178/mcnemar_power_n30_n60.json and
refuses to overwrite it.

    python tools/s178_mcnemar_power.py [--out reports/s178/mcnemar_power_n30_n60_v2.json]

S178 FIX-EVAL (SCI-B E7): the reading no longer calls the MDE a conservative reading of a sawtooth in delta (power is
monotone in delta; the discrete sawtooth is in the discordant count m); the table states its grid step and, per n, the
discordance range its MDE range covers, plus the MDE ranges over the common discordance range.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evaluation import mcnemar_power as MP  # noqa: E402

OUT = ROOT / "reports/s178/mcnemar_power_n30_n60.json"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    out_path = Path(ap.parse_args(argv).out)
    table = MP.planning_table(ns=(15, 30, 60))
    table_common = MP.planning_table(ns=(30, 60))["common_discordance_range"]
    design = {f"n{n}_baseline0.5_delta{g}_d{d}": MP.design_interval(n, 0.5, g, d)
              for n, g, d in ((30, 0.3, 0.4), (60, 0.2, 0.4), (60, 0.15, 0.3)) if abs(g) <= d}
    rep = {"tool": "tools/s178_mcnemar_power.py", "module": MP.VERSION, "status": "PLANNING_NON_CITABLE",
           "table": table, "newcombe_at_design_points": design,
           "min_realised_discordant_pairs_for_p05": MP.min_discordant_for_significance(),
           "rejection_rule_n30": {str(m): k for m, k in MP.rejection_table(30).items() if m >= 6},
           "rejection_rule_n60": {str(m): k for m, k in MP.rejection_table(60).items() if m >= 6 and m % 2 == 0},
           "common_discordance_range_n30_n60": table_common,
           "reading": ("MDE = smallest accuracy gap on a 0.005 grid whose exact two-sided McNemar power reaches the target, "
                       "given a discordance rate d; power is monotone in the gap at fixed n and d, so this is the first "
                       "crossing (the discrete sawtooth is in the number of discordant pairs, not in the gap). Each n's "
                       "MDE range covers a different d range (table.headline_by_n): n = 30 has no MDE at d 0.2, so compare "
                       "n = 30 and n = 60 over d 0.3-0.5 (common_discordance_range_n30_n60). REV-B "
                       "(reports/orchestration/review/S176_REV-B_eval_governance.md Q26) reported about 0.28-0.33 at n = 30 "
                       "and 0.16-0.24 at n = 60 for 80 % power under its own discordance grid. H1 needs two such tests "
                       "(B4 > B1 and B4 > B2): the joint power is only bounded (Frechet) because both share B4's answers."),
           "rule_287_4": ["state the MDE next to every H1 result", "if discordant < min_realised_discordant_pairs_for_p05 say "
                          "'cannot be significant at this n'", "exact test decides, Newcombe interval is descriptive"]}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(rep, indent=1, sort_keys=True) + "\n").encode()
    with open(out_path, "xb") as fh:
        fh.write(data)
    print(json.dumps({"out": str(out_path), "sha256": hashlib.sha256(data).hexdigest()}))
    for r in table["rows"]:
        print(r["n"], r["discordance"], "MDE", r["mde"], "power@MDE", r.get("power_at_mde"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
