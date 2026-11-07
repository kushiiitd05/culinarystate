#!/usr/bin/env python
"""Freeze the AA pilot Model A fit (reports/step10/aa_pilot_preregistration_DRAFT.md §6). Run after BOTH return.

Reads the two returned CAL verification files, applies the verdict rule (§4) and the inclusion rule (§6), fits
Model A, and writes the fit JSON once (refuses overwrite). Its SHA-256 is the freeze point: no SIM-VAL full text is
opened before this file is committed. Writes no ledger row.

    python tools/aa_pilot_fit.py --kush <returned_Kush.csv> --parv <returned_Parv.csv>
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.simulation import aa_pilot_fit as F  # noqa: E402

OUT = ROOT / "reports/step10/aa_pilot_model_a_fit_FROZEN.json"


def _rows(p: Path) -> list[dict]:
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kush", required=True, type=Path)
    ap.add_argument("--parv", required=True, type=Path)
    ap.add_argument("--out", default=OUT, type=Path)
    a = ap.parse_args(argv)
    if a.out.exists():
        ap.error("refusing to overwrite a frozen fit")
    returned = {who: hashlib.sha256(p.read_bytes()).hexdigest() for who, p in (("Kush", a.kush), ("Parv", a.parv))}
    try:
        agreed, why_v = F.agreed_rows(_rows(a.kush), _rows(a.parv))
        inc, why_i = F.include(agreed)
        fit = F.fit_model_a(inc)
    except F.FitRefused as exc:
        ap.error(str(exc))
    code = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest()
            for f in ("src/culinarystate/simulation/aa_pilot_fit.py", "tools/aa_pilot_fit.py")}
    rep = {"record": "AA_PILOT_MODEL_A_FIT", "status": "FROZEN_BEFORE_SIM_VAL", "sim_val_opened": False,
           "returned_sha256": returned, "excluded_by_verdict": why_v, "excluded_by_inclusion": why_i,
           "fit": fit, "code_sha256": code}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "x", encoding="utf-8") as fh:
        fh.write(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"out": str(a.out), "sha256": hashlib.sha256(a.out.read_bytes()).hexdigest(),
                      "Ea_kJ_per_mol": round(fit["Ea_J_per_mol"] / 1000, 2), "n_rows": fit["n_rows"],
                      "n_papers": fit["n_papers"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
