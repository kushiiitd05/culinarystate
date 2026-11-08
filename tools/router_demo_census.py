#!/usr/bin/env python
"""Router demo route census over a seeded recipe sample, counts only (S171, D-075 M1). NON_CITABLE, DRAFT.

Chain per recipe: Rung A -> unchanged Step 23a engine with the EVD G0 pre-check for one target state variable.
Same corpus reader, seeded sample and protected-ledger check as tools/step26g_census.py; writes ONE JSON of
integer counts and codes (no recipe text, id or seed) and refuses to overwrite or to write in ledgers/, data/,
exports/ or annotation/gold/. Not a gold score, not a human gate, never citable.

    python tools/router_demo_census.py --seed router-demo-2026-11-08 --out reports/step23/<new>.json
    python tools/router_demo_census.py --seed 20261104 --sample-size 612782 --workers 32 --out ...  (server)

S176: ``--gates on`` (default) applies the target-presence screen and the lot-context gate before G0 and also counts the
ungated routes of the same pass; ``--gates off`` is the S171 behaviour. ``--presence-floor SVAR=VALUE`` overrides one
floor for a sensitivity run (the report records it).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.lineage.guard import LedgerBaselineMismatch  # noqa: E402
from culinarystate.mechanism import evidence_gates as EG  # noqa: E402
from culinarystate.mechanism import router_census as RC  # noqa: E402
from culinarystate.mechanism import router_demo as RD  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

_spec = importlib.util.spec_from_file_location("_step17b_rung_a_dryrun", ROOT / "tools/step17b_rung_a_dryrun.py")
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)

CODE_FILES = ("src/culinarystate/mechanism/router_demo.py", "src/culinarystate/mechanism/router_census.py",
              "src/culinarystate/mechanism/applicability.py", "src/culinarystate/mechanism/evidence_gates.py",
              "tools/router_demo_census.py")


def provenance() -> dict:
    p = T17.code_provenance()
    rows = p["code_sha256"] + [{"path": f, "sha256": hashlib.sha256((ROOT / f).read_bytes()).hexdigest()}
                               for f in CODE_FILES]
    return {**p, "code_sha256": rows}


def _baseline_ok(root: Path) -> bool:
    try:
        T17._baseline(root)
        return True
    except (LedgerBaselineMismatch, OSError, KeyError, ValueError):
        return False


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", required=True, help="sampling seed (only its SHA-256 is reported)")
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--target", default="SVAR-000009", help="target state variable (default: vitamin C)")
    ap.add_argument("--workers", type=int, default=1, help="fork-pool workers (server: e.g. 32)")
    ap.add_argument("--evd", default=str(RD.EVD_PATH), help="EVD ledger (read only)")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", required=True, help="new counts-only JSON (refuses overwrite)")
    ap.add_argument("--families", nargs="+", choices=T17.FAMILIES, default=list(T17.FAMILIES))
    ap.add_argument("--gates", choices=("on", "off"), default="on",
                    help="evidence gates before G0 (target presence + lot context); off = S171 behaviour")
    ap.add_argument("--presence-floor", action="append", default=[], metavar="SVAR=VALUE",
                    help="override one presence floor (sensitivity run only; recorded in the report)")
    ap.add_argument("--no-baseline-check", action="store_true",
                    help="skip the protected-ledger hash check (recorded in the report; tests only)")
    a = ap.parse_args(argv)
    if a.sample_size < 1 or a.workers < 1:
        ap.error("--sample-size and --workers must be positive")
    root, out = Path(a.root), Path(a.out)
    if out.exists():
        ap.error("refusing to overwrite an existing report")
    prov = provenance()
    if a.no_baseline_check:
        baseline = "SKIPPED_BY_FLAG"
    elif not _baseline_ok(root):
        print(json.dumps({"status": "REFUSED", "reason": "PROTECTED_LEDGER_BASELINE_CHECK_FAILED_BEFORE_RUN"}))
        return 2
    else:
        baseline = "PENDING_AFTER_RUN"
    index = RD.EvidenceIndex.from_ledger(Path(a.evd))
    gates = None
    if a.gates == "on":
        gates = EG.EvidenceGates.load()
        for item in a.presence_floor:
            svar, _, val = item.partition("=")
            if svar not in gates.screen.floors or not val:
                ap.error(f"--presence-floor expects SVAR=VALUE for a screened target, got {item!r}")
            ck = EG.code_key(svar)
            gates = EG.EvidenceGates(gates.screen.with_floor(svar, val), provenance={
                **gates.provenance, "floors": {**gates.provenance["floors"], ck: {
                    **gates.provenance["floors"][ck], "value": float(val), "status": "OVERRIDE_SENSITIVITY_RUN"}}})
    status: dict = {}
    report = RC.census_from_records(T17._stream(a.families, root, record_source or T17.corpus_records, status),
                                    seed=a.seed, size=a.sample_size, index=index, target_svar=a.target,
                                    workers=a.workers, gates=gates)
    if baseline == "PENDING_AFTER_RUN":
        baseline = "PASS_BEFORE_AND_AFTER" if _baseline_ok(root) else "FAILED_AFTER_RUN"
    report.update(family_status=dict(sorted(status.items())), baseline_check=baseline,
                  families_requested=list(a.families), code_provenance=prov,
                  code_unchanged_during_run=provenance() == prov)
    try:
        D.write_report(out, report, root=root)
    except D.DryRunError as exc:
        ap.error(str(exc))
    print(json.dumps({"output": str(out), "recipes_sampled": report["recipes_sampled"], "items": report["items"],
                      "route": report["route"], "route_ungated": report.get("route_ungated"),
                      "coverage": report["evidence_coverage"],
                      "exceptions": sum(report["exceptions_by_class"].values()), "baseline_check": baseline}))
    if baseline == "FAILED_AFTER_RUN":
        return 4
    return 3 if any(v != "READ" for v in status.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
