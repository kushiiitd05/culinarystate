#!/usr/bin/env python
"""Run Layer 2 SCENARIO over Layer 1 records (S172, D-077). Data-plane in, data-plane out, counts-only summary.

    python tools/scenario_layer_run.py --l1 data/derived/physical_L1/ --l2 data/derived/physical_L2/ \
        --out reports/step26/<new>.json [--workers 64]
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

from culinarystate.extraction.rung_a_measure import code  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402
from culinarystate.simulation import scenario_layer as SL  # noqa: E402

_LAYER: list = []


def _one(paths: tuple[str, str]) -> dict:
    src, dst = paths
    layer = _LAYER[0]
    c = Counter()
    with open(src, encoding="utf-8") as fi, open(dst, "x", encoding="utf-8") as fo:
        for line in fi:
            out = layer.run(json.loads(line))
            fo.write(json.dumps(out) + "\n")
            c[("status", code(out["status"]))] += 1
            c[("transition", code(out["transition_status"]))] += 1
            for b, s in out["scenarios"].items():
                c[("core_known", b, s["core_end_c"] is not None)] += 1
                for k, v in s["bases"].items():
                    c[("basis", k, code(str(v).split(":")[0] if str(v).startswith("L1:") else
                                        ("SD" if str(v).startswith("SD-") else
                                         "KGE" if str(v).startswith("KGE-") else str(v))))] += 1
                if b == "TYPICAL" and s["core_end_c"] is not None:
                    c[("typical_core_reaches_70", s["core_minutes_above_70"] > 0)] += 1
    return dict(c)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--l1", required=True, type=Path)
    ap.add_argument("--l2", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if a.out.exists():
        ap.error("refusing to overwrite an existing report")
    for p in (a.l1, a.l2):
        try:
            parts = p.resolve().relative_to(ROOT.resolve()).parts
        except ValueError:
            parts = ("data",)
        if parts[:1] != ("data",):
            ap.error("--l1/--l2 must be under data/ (git-ignored) or outside the repository")
    a.l2.mkdir(parents=True, exist_ok=True)
    if any(a.l2.iterdir()):
        ap.error("--l2 must be empty or new")
    _LAYER.append(SL.ScenarioLayer.load())
    jobs = [(str(f), str(a.l2 / f.name)) for f in sorted(a.l1.glob("*.jsonl"))]
    if a.workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(a.workers) as pool:
            parts = pool.map(_one, jobs)
    else:
        parts = [_one(j) for j in jobs]
    tot = Counter()
    for p in parts:
        tot.update(p)
    nest: dict = {}
    for key, v in sorted(tot.items(), key=lambda kv: str(kv[0])):
        d = nest
        for k in key[:-1]:
            d = d.setdefault(str(k), {})
        d[str(key[-1])] = v
    reg = (ROOT / "registry/scenario_defaults_v1.csv").read_bytes()
    rep = {"record": "SCENARIO_L2_SUMMARY", "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY", "layer_version": SL.VERSION,
           "labels": SL.LABELS, "contains_ids": False, "contains_text": False, "citable": False,
           "scenario_registry_sha256": hashlib.sha256(reg).hexdigest(), "l1_files": len(jobs), "counts": nest}
    D.write_report(a.out, rep, root=ROOT)
    print(json.dumps({"files": len(jobs), "status": nest.get("status")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
