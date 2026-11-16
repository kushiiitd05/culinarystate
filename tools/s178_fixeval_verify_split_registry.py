#!/usr/bin/env python
"""S178 FIX-EVAL (SCI-B E5): verify registry/split_registry_v1.csv, including the DIAG29 rows that have no unit listing.

The D5 and 07.A-R1 rows are checked against reports/s178/split_registry_units_v1.csv (ids_sha256 under the row's one hash
convention, unit_ids_sha256 from the listed recipe / cell / unit ids). The DIAG29 rows are checked against an assignment
recomputed here from the ledgers with the same code path as tools/s178_build_split_registry.py (ACTIVE EVD rows,
``transition.dataset.cells_from_rows`` per source family, ``transition.splits.all_splits(df, 7)``). Ids and hashes stay in
memory; the output holds counts, findings and hashes only. Refuses to overwrite.

    python tools/s178_fixeval_verify_split_registry.py [--out reports/s178/split_registry_verify_S178fix.json]
AI_DRAFTED. A consistency check, not a freeze and not a human gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evaluation import split_registry as SR  # noqa: E402

REGISTRY = ROOT / "registry/split_registry_v1.csv"
UNITS = ROOT / "reports/s178/split_registry_units_v1.csv"
OUT = ROOT / "reports/s178/split_registry_verify_S178fix.json"
DIAG_SEED = 7
PREREG_SPLITS = {"random": "S-1", "pair_holdout": "S-2", "matrix_disjoint": "S-3", "process_disjoint": "S-4",
                 "study_disjoint": "S-5"}


def latest(name: str) -> dict:
    out = {}
    with open(ROOT / f"ledgers/data/{name}.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out[r["id"]] = r
    return out


def diag29_assignments() -> tuple[dict[str, list[tuple[str, str]]], dict]:
    from culinarystate.transition.dataset import cells_from_rows
    from culinarystate.transition.splits import all_splits
    evd, cond = latest("EVD"), latest("COND")
    active = [r for r in evd.values() if r["status"] == "ACTIVE"]
    out: dict[str, list[tuple[str, str]]] = {}
    info: dict = {"families": {}}
    for fam in sorted({r["source_family_id"] for r in active}):
        table = cells_from_rows(active, cond, fam)
        df = table.df
        info["families"][fam] = {"cells": int(len(df)), "excluded_by_reason": dict(sorted(getattr(table, "excluded", {}).items()))
                                 if isinstance(getattr(table, "excluded", None), dict) else str(getattr(table, "excluded", ""))}
        if not len(df):
            continue
        splits, _ = all_splits(df, DIAG_SEED)
        ids = df["evd_id"].to_numpy()
        for s in splits:
            sx = PREREG_SPLITS.get(s.name)
            if sx is None:
                continue
            out[f"SPL-29D-{fam}-{sx}-{s.name}"] = [(str(ids[i]), role) for role, idx in
                                                    (("train", s.train), ("cal", s.cal), ("test", s.test)) for i in idx]
    return out, info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    listing_only = SR.verify_registry(REGISTRY, UNITS)
    rec, info = diag29_assignments()
    rows = SR.read_csv(REGISTRY)
    registered = {r["registry_id"] for r in rows if r["evaluation"] == "DIAG29" and r["n_units"] not in ("", "0")}
    rec = {k: v for k, v in rec.items() if k in registered}
    full = SR.verify_registry(REGISTRY, UNITS, recomputed=rec)
    rep = {"tool": "tools/s178_fixeval_verify_split_registry.py", "module": SR.VERSION, "status": "AI_DRAFTED_COUNTS_ONLY",
           "registry_sha256": SR.sha256_file(REGISTRY), "units_sha256": SR.sha256_file(UNITS),
           "evd_sha256": SR.sha256_file(ROOT / "ledgers/data/EVD.jsonl"), "cond_sha256": SR.sha256_file(ROOT / "ledgers/data/COND.jsonl"),
           "dataset_code_sha256": SR.sha256_file(ROOT / "src/culinarystate/transition/dataset.py"),
           "splits_code_sha256": SR.sha256_file(ROOT / "src/culinarystate/transition/splits.py"),
           "n_rows": len(rows), "n_rows_by_evaluation": {e: sum(r["evaluation"] == e for r in rows) for e in SR.EVALUATIONS},
           "listing_only": {"findings": listing_only,
                            "n_not_verifiable_from_listing": sum(f.startswith("NOT_VERIFIABLE_FROM_LISTING") for f in listing_only)},
           "with_recomputed_diag29": {"n_diag29_rows_with_units": len(registered), "n_recomputed": len(rec),
                                      "findings": full, "n_errors": len(full)},
           "diag29_recompute_inputs": info,
           "reading": "listing_only names every DIAG29 row as NOT_VERIFIABLE_FROM_LISTING (no unit listing is committed for "
                      "them); with_recomputed_diag29 checks them against the split recomputed from the ledgers. An empty "
                      "findings list there means every registered id hash re-derives."}
    out.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(rep, indent=1, sort_keys=True) + "\n").encode()
    with open(out, "xb") as fh:
        fh.write(data)
    print(json.dumps({"out": str(out), "sha256": hashlib.sha256(data).hexdigest(), "n_errors": len(full),
                      "listing_only_not_verifiable": rep["listing_only"]["n_not_verifiable_from_listing"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
