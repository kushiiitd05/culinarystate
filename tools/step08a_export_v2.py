#!/usr/bin/env python3
"""08a.7: build EVD export v2 (additive) from SCRATCH ledgers + keys; verify against v1. Never writes inside the repo's exports/.
  python tools/step08a_export_v2.py --ledgers DIR --keys keys.jsonl --out DIR [--committed-v1 exports/evd/evd_export_v1.jsonl]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence.evd_export import build_export, canon_json  # noqa: E402
from culinarystate.lineage.export_v2 import build_v2_rows, check_v1_identical, load_keys, write_export_v2  # noqa: E402


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _tree_sha(d: Path) -> dict:
    return {p.name: _sha(p) for p in sorted(d.iterdir()) if p.is_file()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledgers", type=Path, required=True)
    ap.add_argument("--keys", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--committed-v1", type=Path, default=ROOT / "exports" / "evd" / "evd_export_v1.jsonl")
    a = ap.parse_args()
    evd_dir = ROOT / "exports" / "evd"
    before = _tree_sha(evd_dir) if evd_dir.is_dir() else {}
    v1_rows, _, _, meta = build_export(a.ledgers / "data" if (a.ledgers / "data").is_dir() else a.ledgers)
    v1_lines = [canon_json(r) for r in v1_rows]
    v1_regen_sha = hashlib.sha256("".join(l + "\n" for l in v1_lines).encode()).hexdigest()
    rows = build_v2_rows(v1_rows, load_keys(a.keys))
    n = check_v1_identical(rows, v1_lines)
    committed = {"file": str(a.committed_v1), "present": a.committed_v1.is_file()}
    if committed["present"]:
        committed["sha256"] = _sha(a.committed_v1)
        committed["identical_to_regenerated_v1"] = committed["sha256"] == v1_regen_sha
        committed["v1_columns_identical_to_committed_v1"] = check_v1_identical(rows, a.committed_v1.read_text(encoding="utf-8").splitlines()) == n
    man = write_export_v2(rows, a.out, {"v1_regenerated_sha256": v1_regen_sha, "v1_rows_checked_identical": n, "committed_v1": committed,
                                        "ledger_sha256_evd": meta["ledger_sha256"], "keys_file_sha256": _sha(a.keys),
                                        "schema_version_bump": "evd_export@1.0.0 -> evd_export@2.0.0 (additive columns only)"})
    after = _tree_sha(evd_dir) if evd_dir.is_dir() else {}
    if before != after:
        raise SystemExit("exports/evd changed during build")
    print(json.dumps({"rows": man["export_rows"], "sha256": man["export_sha256"], "v1_regen_sha256": v1_regen_sha, "committed_v1": committed,
                      "exports_evd_untouched": True}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
