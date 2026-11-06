#!/usr/bin/env python
"""Step 19 real-pilot gate (S154). Refuses to draw until every human prerequisite exists.

  check  --record reports/step19/pilot_start_record.UNSIGNED.json
         Lists every missing human fact with its owner. Exit 0 only when ready.
  draw   --record R --frame FRAME.csv --strata STRATA.csv --execute
         P1 draw per the bound specification; writes a text-free manifest to
         registry/recipe_semantics/deep_gold_pilot_v1/ and refuses overwrite.
         Without --execute, or with any blocker, nothing is drawn or written.
This tool never edits the start record and never supplies a nonce, signature,
capacity, budget or H5 decision. P2 is not supported (D19-10 / tag rules open).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.annotation.pilot_real import (  # noqa: E402
    DRAW_ALGORITHM_ID, TOOL_VERSION, PilotGateError, blockers_as_json, check_prerequisites, draw_p1, draw_wave,
)

OUT_DIR = "registry/recipe_semantics/deep_gold_pilot_v1"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "draw"):
        p = sub.add_parser(name)
        p.add_argument("--root", default=str(ROOT))
        p.add_argument("--record", required=True)
        p.add_argument("--wave", default="P1", choices=["P1", "P1b", "P2"])
        if name == "draw":
            p.add_argument("--frame", required=True)
            p.add_argument("--strata", required=True)
            p.add_argument("--out-dir", default=None)
            p.add_argument("--execute", action="store_true", help="actually draw (only if every prerequisite holds)")
            p.add_argument("--cells", default="", help="P1b only: comma-separated P1 cell ids chosen by a human")
            p.add_argument("--exclude", action="append", default=[], help="P1b only: earlier manifest(s) to exclude")
    a = ap.parse_args(argv)
    root = Path(a.root)
    blockers = check_prerequisites(Path(a.record), root=root, wave=a.wave)
    report = {"tool_version": TOOL_VERSION, "draw_algorithm": DRAW_ALGORITHM_ID, "wave": a.wave,
              "ready": not blockers, "blockers": blockers_as_json(blockers), "counts_as_human_gate": False}
    if a.cmd == "check" or blockers:
        if a.cmd == "draw":
            report["draw"] = "REFUSED"
        print(json.dumps(report, indent=2))
        return 0 if not blockers else 1
    if not a.execute:
        report["draw"] = "REFUSED"
        report["reason"] = "EXECUTE_FLAG_REQUIRED"
        print(json.dumps(report, indent=2))
        return 1
    try:
        out = Path(a.out_dir) if a.out_dir else root / OUT_DIR
        if a.wave == "P1":
            result = draw_p1(Path(a.record), Path(a.frame), Path(a.strata), out_dir=out, root=root)
        else:  # S168: P1b (P1b amendment); refused unless the signed record authorises the wave
            result = draw_wave(Path(a.record), Path(a.frame), Path(a.strata), out_dir=out, root=root, wave=a.wave,
                               cells=[c for c in a.cells.split(",") if c], exclude_manifests=[Path(x) for x in a.exclude])
    except PilotGateError as exc:
        report.update(draw="REFUSED", reason=str(exc))
        print(json.dumps(report, indent=2))
        return 1
    report.update(draw="DONE", manifest=result["manifest"], frame_sha256=result["frame_sha256"],
                  seed_hex=result["seed_hex"], rows=len(result["rows"]))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
