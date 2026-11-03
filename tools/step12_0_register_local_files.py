#!/usr/bin/env python
"""Step 12.0 (S157): PROPOSED SRC/SNAP registration rows for local structured-database files.

Status: PROVISIONAL_PENDING_H2_REBASELINE. Computes sha256 / size / locator of each local file and
writes PROPOSED rows (placeholder ids, no id minted, no ledger appended) to ONE new staging file for
Kush's review. SRC/SNAP stay byte-identical (the 08a baseline is checked before and after when the
repository root is used). Licence fields come from the acquisition manifest; open H2 => LOCAL_ONLY.

Run locally where the data bundle is present:
    python tools/step12_0_register_local_files.py
    python tools/step12_0_register_local_files.py --entry DS-006=data/external/usda_yields --out <new file>
Default entries: DS-006 R2 yields, DS-007 FNDDS, DS-014 INFOODS directories and the Bognar PDF (DS-002;
expected ALREADY_REGISTERED). Default output: registry/staging/step12_0_src_snap_proposed_v1.jsonl
(refuses overwrite). Exit 0 written, 1 no local file found (nothing written), 2 refused, 3 baseline mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evidence import registration as R  # noqa: E402
from culinarystate.lineage.guard import LedgerBaselineMismatch, verify_baseline  # noqa: E402

BASELINE = "registry/baseline_ledger_hashes_08a_v1.csv"
DEFAULT_OUT = "registry/staging/step12_0_src_snap_proposed_v1.jsonl"
DEFAULT_ENTRIES = (("DS-006", "data/external/usda_yields"), ("DS-007", "data/external/fndds"),
                   ("DS-014", "data/external/infoods"), ("DS-002", "data/raw/bognar/bognar_2002.pdf"))
FOUND = {"PROPOSED_SNAP", "ALREADY_REGISTERED_SNAP", "DUPLICATE_CONTENT_IN_RUN"}


def _fact(path: Path, root: Path) -> dict:
    data = path.read_bytes()
    try:
        loc = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        loc = str(path.resolve())
    return {"locator": loc, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _entry(text: str) -> tuple[str, str]:
    ds, sep, path = text.partition("=")
    if not sep or not ds.strip() or not path.strip():
        raise argparse.ArgumentTypeError("entry must be DS-###=path")
    return ds.strip(), path.strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--h2-queue", type=Path, default=None)
    ap.add_argument("--ids", type=Path, default=None)
    ap.add_argument("--src-ledger", type=Path, default=None)
    ap.add_argument("--entry", type=_entry, action="append", default=None)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    root = a.root.resolve()
    paths = {"manifest": a.manifest or root / "registry/data_source_acquisition_manifest.csv",
             "h2_queue": a.h2_queue or root / "reports/h_state/es_1_2_h2_approval_queue.md",
             "ids": a.ids or root / "ledgers/data/_ids.jsonl",
             "src_ledger": a.src_ledger or root / "ledgers/data/SRC.jsonl"}
    out = a.out or root / DEFAULT_OUT
    check_baseline = root == ROOT.resolve()
    try:
        if check_baseline:
            verify_baseline(root / BASELINE, root)
        rows = R.build_proposals(a.entry or DEFAULT_ENTRIES, manifest=R.load_manifest(paths["manifest"]),
                                 h2_open=R.load_h2_open(paths["h2_queue"]), id_index=R.IdIndex.from_file(paths["ids"]),
                                 existing_src=R.existing_src_by_family(paths["src_ledger"]), root=root)
        counts = Counter(r["record"] for r in rows)
        print(dict(sorted(counts.items())))
        if not FOUND & set(counts):
            print("no local file found: nothing written", file=sys.stderr)
            return 1
        inputs = {k: _fact(p, root) for k, p in paths.items()}
        target = R.write_staging(rows, out, root=root, inputs=inputs)
        if check_baseline:
            verify_baseline(root / BASELINE, root)
    except R.RegistrationError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    except LedgerBaselineMismatch as e:
        print(f"ledger baseline mismatch: {e}", file=sys.stderr)
        return 3
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
