#!/usr/bin/env python
"""Score Step 07.A-R1 (reports/step07/07A_R1_preregistration_DRAFT.md §3). Run ONLY after both reviewers return.

Checks the issued packet still matches the manifest hash, records the SHA-256 of both returned files, then runs
``condition_agreement.score`` on the original independent labels and writes the result once (refuses overwrite).
Never edits a label. Labels from v1-v4 are never scored here.

    python tools/step07ar_agreement.py --kush <returned_Kush.csv> --parv <returned_Parv.csv>
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

from culinarystate.evidence import condition_agreement as CA  # noqa: E402

ISSUED = ROOT / "annotation/condition_audit/condition_audit_packet_100_R1_Kush.csv"
MANIFEST = ROOT / "reports/step07/07A_R1_packet_manifest.json"
OUT = ROOT / "reports/step07/07A_R1_gate_result.json"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _rows(p: Path) -> list[dict]:
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kush", required=True, type=Path)
    ap.add_argument("--parv", required=True, type=Path)
    ap.add_argument("--issued", default=ISSUED, type=Path)
    ap.add_argument("--manifest", default=MANIFEST, type=Path)
    ap.add_argument("--out", default=OUT, type=Path)
    a = ap.parse_args(argv)
    if a.out.exists():
        ap.error("refusing to overwrite an existing gate result")
    if _sha(a.issued) != json.loads(a.manifest.read_text())["sha256_packet_Kush"]:
        ap.error("issued packet does not match the manifest hash: refusing to score")
    returned = {"Kush": _sha(a.kush), "Parv": _sha(a.parv)}  # recorded before scoring (prereg §3.4)
    out = {**CA.score(_rows(a.issued), _rows(a.kush), _rows(a.parv)), "returned_sha256": returned,
           "issued_sha256": _sha(a.issued)}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "x", encoding="utf-8") as fh:
        fh.write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out.get(k) for k in ("gate", "pooled_ac1", "critical_field_flags", "n_problems")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
