#!/usr/bin/env python
"""Sensitivity of the evidence gates to the presence floor and the identity margin, counts only (S176, L-ROUTER).

One pass over the seeded sample's recipes is streamed once; the router census (gates on) then runs per variant on the
in-memory sample. Each variant reports the gated and ungated routes of the same items and the fate of every ungated
DIRECT. NON_CITABLE, DRAFT; the floor and the margin are PROPOSED_PILOT values and a human decides them.

    python tools/router_gate_sensitivity.py --seed 20261104 --sample-size 1000 --workers 8 \\
        --families WIKIBOOKS GUTENBERG_SEGMENT FOODCOM TASTESET --out reports/step23/<new>.json

Variants default to ``0.5:0.15 1.0:0.15 2.0:0.15 5.0:0.15 1.0:0 1.0:0.10 1.0:0.20`` (floor:margin, SVAR-000009).
Refuses to overwrite and to write in ledgers/, data/, exports/ or annotation/gold/.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.extraction.rung_a_measure import seeded_sample  # noqa: E402
from culinarystate.mechanism import evidence_gates as EG  # noqa: E402
from culinarystate.mechanism import router_census as RC  # noqa: E402
from culinarystate.mechanism import router_demo as RD  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

_spec = importlib.util.spec_from_file_location("_router_demo_census", ROOT / "tools/router_demo_census.py")
CENSUS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CENSUS)
T17 = CENSUS.T17
SVAR = "SVAR-000009"
DEFAULT_VARIANTS = ("0.5:0.15", "1.0:0.15", "2.0:0.15", "5.0:0.15", "1.0:0", "1.0:0.10", "1.0:0.20")
KEEP = ("items", "route", "route_ungated", "direct_ungated_cross", "gate_cross", "recipes_with_any_direct",
        "recipes_with_any_direct_ungated", "direct_by_process")


def variant_name(floor: str, margin: str) -> str:
    return "FLOOR_" + floor.replace(".", "_") + "_MARGIN_" + margin.replace(".", "_")


def run_variants(sample, variants, *, seed: str, index, gates, workers: int = 1) -> dict:
    out = {}
    for v in variants:
        floor, _, margin = v.partition(":")
        if not floor or not margin:
            raise ValueError(f"variant {v!r} must be FLOOR:MARGIN")
        g = EG.EvidenceGates(gates.screen.with_floor(SVAR, floor).with_margin(SVAR, margin),
                             provenance=gates.provenance)
        rep = RC.census_from_records(sample, seed=seed, size=len(sample), index=index, target_svar=SVAR, gates=g,
                                     workers=workers)
        out[variant_name(floor, margin)] = {"floor_mg_per_100g": float(floor), "identity_score_margin": float(margin),
                                            **{k: rep[k] for k in KEEP}}
    return out


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--families", nargs="+", choices=T17.FAMILIES, default=list(T17.FAMILIES))
    ap.add_argument("--variants", nargs="+", default=list(DEFAULT_VARIANTS), metavar="FLOOR:MARGIN")
    ap.add_argument("--evd", default=str(RD.EVD_PATH))
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    root, out = Path(a.root), Path(a.out)
    if out.exists():
        ap.error("refusing to overwrite an existing report")
    status: dict = {}
    sample = seeded_sample(T17._stream(a.families, root, record_source or T17.corpus_records, status), a.seed,
                           a.sample_size)
    report = {"record": "ROUTER_DEMO_CENSUS_GATE_SENSITIVITY", "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY",
              "citable": False, "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
              "target_svar": SVAR, "sample_size": len(sample),
              "seed_sha256": hashlib.sha256(a.seed.encode("utf-8")).hexdigest(),
              "families_in_sample": dict(sorted(Counter(r["source_family"] for r in sample).items())),
              "family_status": dict(sorted(status.items())), "gates_version": EG.VERSION,
              "by_variant": run_variants(sample, a.variants, seed=a.seed, index=RD.EvidenceIndex.from_ledger(Path(a.evd)),
                                         gates=EG.EvidenceGates.load(), workers=a.workers)}
    try:
        D.write_report(out, report, root=root)
    except D.DryRunError as exc:
        ap.error(str(exc))
    print(json.dumps({"output": str(out), "variants": {k: v["route"] for k, v in report["by_variant"].items()}}))
    return 3 if any(v != "READ" for v in status.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
