#!/usr/bin/env python
"""Step 26g simulability census over a seeded recipe sample, counts only (S166; review block J8). DRAFT.

Chain: Rung A -> event adapter -> replay -> 26g simulation inputs (sim_aa_1 by default) -> census.
Same corpus reader, seeded sample and protected-ledger check as tools/step17b_rung_a_dryrun.py; writes ONE
JSON of integer counts, codes and hashes (no recipe text, id or seed) and refuses to overwrite or to write
in ledgers/, data/, exports/ or annotation/gold/. Not a gold score and not a human gate.

    python tools/step26g_census.py --seed dryrun-2026-11-04 --out reports/step26/<new>.json
    python tools/step26g_census.py --seed 20261104 --sample-size 612782 --out ...   (server only: ~3 GB RAM)
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
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402
from culinarystate.simulation import census_chain as C  # noqa: E402
from culinarystate.simulation.recipe_adapter import SYSTEM_REQUIREMENTS  # noqa: E402

_spec = importlib.util.spec_from_file_location("_step17b_rung_a_dryrun", ROOT / "tools/step17b_rung_a_dryrun.py")
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)


def provenance() -> dict:
    p = T17.code_provenance()
    me = Path(__file__).resolve()
    rows = p["code_sha256"] + [{"path": me.relative_to(ROOT).as_posix(),
                                "sha256": hashlib.sha256(me.read_bytes()).hexdigest()}]
    return {**p, "code_sha256": rows}


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", required=True, help="sampling seed (only its SHA-256 is reported)")
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--system", default="sim_aa_1", choices=sorted(SYSTEM_REQUIREMENTS))
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", required=True, help="new counts-only JSON (refuses overwrite)")
    ap.add_argument("--families", nargs="+", choices=T17.FAMILIES, default=list(T17.FAMILIES))
    ap.add_argument("--no-baseline-check", action="store_true",
                    help="skip the protected-ledger hash check (recorded in the report; tests only)")
    a = ap.parse_args(argv)
    if a.sample_size < 1:
        ap.error("--sample-size must be positive")
    root, out = Path(a.root), Path(a.out)
    prov = provenance()
    try:
        D.assert_counts_only({"code_provenance": prov})
    except D.DryRunError as exc:
        ap.error(f"code provenance would fail the counts-only guard: {exc}")
    if a.no_baseline_check:
        baseline = "SKIPPED_BY_FLAG"
    else:
        try:
            T17._baseline(root)
        except (LedgerBaselineMismatch, OSError, KeyError, ValueError):
            print(json.dumps({"status": "REFUSED", "reason": "PROTECTED_LEDGER_BASELINE_CHECK_FAILED_BEFORE_RUN"}))
            return 2
        baseline = "PENDING_AFTER_RUN"
    status: dict = {}
    report = C.census_from_records(T17._stream(a.families, root, record_source or T17.corpus_records, status),
                                   seed=a.seed, size=a.sample_size, system_id=a.system, schema=D.load_schema(ROOT))
    if baseline == "PENDING_AFTER_RUN":
        try:
            T17._baseline(root)
            baseline = "PASS_BEFORE_AND_AFTER"
        except (LedgerBaselineMismatch, OSError, KeyError, ValueError):
            baseline = "FAILED_AFTER_RUN"
    report.update(family_status=dict(sorted(status.items())), baseline_check=baseline,
                  families_requested=list(a.families), code_provenance=prov,
                  code_unchanged_during_run=provenance() == prov)  # prv P8: re-checked after the run
    try:
        D.write_report(out, report, root=root)
    except D.DryRunError as exc:
        ap.error(str(exc))
    sys_ = report["census"]["systems"].get(a.system, {})
    print(json.dumps({"output": str(out), "recipes_seen": report["recipes_seen"],
                      "recipes_sampled": report["recipes_sampled"], "engine_events": report["engine_events"],
                      "simulate": sys_.get("route", {}).get("SIMULATE", 0),
                      "exceptions": sum(report["exceptions_by_class"].values()), "baseline_check": baseline,
                      "family_status": report["family_status"]}))
    if baseline == "FAILED_AFTER_RUN":
        return 4
    return 3 if any(v != "READ" for v in status.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
