#!/usr/bin/env python
"""15a.R RESERVED-group seal on the ES-1.1 snapshot. Refuses until 15.0 is signed.

  check  [--decision D-NNN] [--seed-file F] [--sealed-out P]
         Lists every blocker as JSON; exit 0 only when a seal could run.
  seal   --decision D-NNN --seed-file F --sealed-out P [--commitment-out C] --execute
         Seals per the signed 15.0 decision (fraction, unit, stratify, seed commitment).
         Writes the commitment file (hashes and counts only) and the sealed list, which
         must lie outside git. Without --execute, or with any blocker, nothing is written.

The tool never chooses a fraction or seed, never writes DECISIONS.md and never
overwrites an existing seal. Rules: src/culinarystate/lineage/reserved_seal.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.lineage.reserved_seal import (  # noqa: E402
    COMMITMENT_PATH, SealRefused, collect_blockers, run_seal,
)


def _path(value: Optional[str]) -> Optional[Path]:
    return Path(value) if value else None


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("check", "seal"))
    ap.add_argument("--root", default=str(ROOT), help="repository root (default: this checkout)")
    ap.add_argument("--decision", help="signed 15.0 decision id, e.g. D-0NN")
    ap.add_argument("--seed-file", help="file holding the seed text, outside git")
    ap.add_argument("--sealed-out", help="sealed list path, outside git or in a git-ignored path")
    ap.add_argument("--commitment-out", help=f"commitment JSON (default {COMMITMENT_PATH})")
    ap.add_argument("--execute", action="store_true", help="required to seal")
    args = ap.parse_args(argv)
    root = Path(args.root)
    commitment = _path(args.commitment_out) or root / COMMITMENT_PATH
    if args.command == "check":
        blockers, _, _ = collect_blockers(root=root, decision_id=args.decision, seed_file=_path(args.seed_file),
                                          sealed_out=_path(args.sealed_out), commitment_out=commitment,
                                          require_execute=False, execute=False)
        print(json.dumps({"ready": not blockers, "blockers": blockers}, indent=2))
        return 0 if not blockers else 1
    try:
        out = run_seal(root=root, decision_id=args.decision, seed_file=_path(args.seed_file),
                       sealed_out=_path(args.sealed_out), commitment_out=commitment, execute=args.execute)
    except SealRefused as exc:
        print(json.dumps({"sealed": False, "blockers": exc.blockers}, indent=2))
        return 2
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
