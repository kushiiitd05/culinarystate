#!/usr/bin/env python
"""Build / validate registry/proc_family_registry_v1.csv (S178 PHYS2, T4-C01-R1). DRAFT, AI_DRAFTED.

    python tools/s178_phys_proc_registry.py --build     # writes registry/proc_family_registry_v1.csv (refuses to overwrite)
    python tools/s178_phys_proc_registry.py --validate  # checks the committed file against the PROC ledger and the binders
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.simulation import proc_family_registry as PR  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--path", default=str(ROOT / PR.REGISTRY))
    a = ap.parse_args(argv)
    path = Path(a.path)
    if a.build:
        if path.exists():
            ap.error("refusing to overwrite an existing registry")
        PR.write_registry(path, PR.build_rows(ROOT))
    if a.validate or a.build:
        rows = PR.read_registry(path)
        probs = PR.validate(rows, ROOT)
        print(json.dumps({"rows": len(rows), "problems": probs, "by_primary_family": dict(sorted(Counter(
            r["primary_family"] for r in rows).items())), "ambiguous": sum(r["ambiguity_flag"] == "YES" for r in rows),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}, indent=1))
        return 1 if probs else 0
    ap.error("nothing to do: pass --build or --validate")


if __name__ == "__main__":
    sys.exit(main())
