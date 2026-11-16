#!/usr/bin/env python
"""Validate physical-layer records against the S178 schema (T4-C02-R2): counts-only JSON, never overwritten. DRAFT.

    python tools/s178_phys_schema_validate.py --kind L1_HEAT data/derived/physical_L1_full_S178v04/WIKIBOOKS \
        --out reports/s178/phys/schema_validation_L1_WIKIBOOKS_S178.json [--max-files N]

``--kind`` is one of L1_HEAT, L1_NONHEAT, L2_HEAT, L2_NONHEAT. Input directories hold .jsonl records (under data/ or outside the
repository). Exit code 0 when no problem was found, 1 otherwise. The report holds counts and problem codes only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.quantity import rc2_dryrun as D  # noqa: E402
from culinarystate.simulation import physical_record_schema as PS  # noqa: E402


def validate_dir(kind: str, d: Path, max_files: int | None = None) -> tuple[PS.Tally, int]:
    t = PS.Tally()
    files = sorted(d.glob("*.jsonl"))[:max_files]
    for f in files:
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    PS.check(kind, json.loads(line), t)
    return t, len(files)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kind", required=True, choices=PS.KINDS)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--max-files", type=int, default=None)
    ap.add_argument("dirs", nargs="+", type=Path)
    a = ap.parse_args(argv)
    if a.out.exists():
        ap.error("refusing to overwrite an existing report")
    tot = PS.Tally()
    n_files = 0
    for d in a.dirs:
        try:
            parts = d.resolve().relative_to(ROOT.resolve()).parts
        except ValueError:
            parts = ("data",)
        if parts[:1] != ("data",):
            ap.error("input directories must be under data/ or outside the repository")
        t, n = validate_dir(a.kind, d, a.max_files)
        tot.update(t)
        n_files += n
    rep = {"record": "PHYSICAL_RECORD_SCHEMA_VALIDATION", "status": "AI_ENGINEERING_COUNTS_ONLY", "kind": a.kind,
           "contains_ids": False, "contains_text": False, "counts_as_human_gate": False, "files": n_files,
           "inputs_dirs": len(a.dirs), "max_files": a.max_files, **PS.summary(tot),
           "code_sha256": hashlib.sha256((ROOT / "src/culinarystate/simulation/physical_record_schema.py").read_bytes()).hexdigest()}
    D.write_report(a.out, rep, root=ROOT)
    print(json.dumps({"kind": a.kind, "files": n_files, "problems": rep["problems"], "ratios": rep["ratios"]}))
    return 1 if rep["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
