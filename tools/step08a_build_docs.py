#!/usr/bin/env python3
"""Step 08a.1 + 08a.2: DOC records and STUDY versions, written ONLY to a scratch ledgers root.

  python tools/step08a_build_docs.py --ledgers-root <scratch root containing data/> --out counts.json

The root must hold `data/` (a copy of ledgers/data). The repo's own ledgers are refused; so is any
path the lineage guard protects. Nothing is downloaded: files under data/raw are only hashed.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.lineage import docs, studies  # noqa: E402
from culinarystate.lineage.guard import ProtectedPathError, assert_safe_write_target  # noqa: E402

SRCMAP = {"usda_r6": "SRC-000001", "bognar": "SRC-000141", "phenol_explorer": "SRC-000012"}
PE_SRC = "SRC-000012"
EXACT = ("EVD", "COND", "SRC", "MEAS", "SNAP")       # must stay byte-identical
PREFIX = ("STUDY", "_ids")                            # append-only: first baseline bytes unchanged


def _baseline(csv_path: Path) -> dict[str, dict]:
    with Path(csv_path).open(newline="") as f:
        return {Path(r["path"]).stem: r for r in csv.DictReader(f)}


def _check_baseline(data: Path, base: dict[str, dict], *, exact: tuple[str, ...]) -> dict[str, str]:
    out = {}
    for name in exact:
        r = base[name]
        sha, size = docs.sha256_file(data / f"{name}.jsonl")
        ok = sha == r["sha256"] and size == int(r["bytes"])
        out[name] = "IDENTICAL" if ok else "DIFFERS"
        if not ok:
            raise SystemExit(f"baseline mismatch: {name}.jsonl")
    for name in PREFIX:
        studies.check_prefix_unchanged(data / f"{name}.jsonl", int(base[name]["bytes"]), base[name]["sha256"])
        out[name] = "PREFIX_IDENTICAL"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledgers-root", required=True, type=Path)
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    ap.add_argument("--baseline-csv", type=Path, default=ROOT / "registry" / "baseline_ledger_hashes_08a_v1.csv")
    ap.add_argument("--out", type=Path, required=True, help="counts JSON (must be outside protected paths)")
    ap.add_argument("--created-at", default=docs.FIXED_CREATED_AT)
    a = ap.parse_args()

    root = a.ledgers_root.resolve()
    if root == (ROOT / "ledgers").resolve() or root == (ROOT / "ledgers" / "data").resolve():
        raise SystemExit("refusing the repo's real ledgers; pass a scratch copy")
    data = root / "data"
    try:
        for p in (data / "DOC.jsonl", data / "STUDY.jsonl", data / "_ids.jsonl", a.out):
            assert_safe_write_target(p)
    except ProtectedPathError as e:
        raise SystemExit(f"refused: {e}")

    base = _baseline(a.baseline_csv)
    ids_before = (data / "_ids.jsonl").stat().st_size
    pre = _check_baseline(data, base, exact=EXACT)

    files = docs.build_file_docs(data, a.repo_root, SRCMAP, created_at=a.created_at)
    pe = docs.build_pe_metadata_docs(data, a.repo_root, PE_SRC, a.repo_root / "data/raw/doi_resolve",
                                     created_at=a.created_at)
    st = studies.run_08a2(data, PE_SRC, pe["doc_ids_by_src"], data / "EVD.jsonl", created_at=a.created_at,
                          expect_prefix=(int(base["STUDY"]["bytes"]), base["STUDY"]["sha256"]))

    post = _check_baseline(data, base, exact=EXACT)
    ids_after = (data / "_ids.jsonl").stat().st_size
    n_ids = sum(1 for _ in (data / "_ids.jsonl").open())
    summary = {
        "ledgers_root": str(root), "created_at": a.created_at,
        "doc_records_from_files": files, "pe_metadata": {k: v for k, v in pe.items() if k != "doc_ids_by_src"},
        "pe_publications": pe["pe_publications"], "pe_publications_with_docs": len(pe["doc_ids_by_src"]),
        "doc_total_ledger_lines": sum(1 for _ in (data / "DOC.jsonl").open()),
        "study": st, "ids_minted_note": "see ids_growth", "ids_growth": {
            "bytes_before": ids_before, "bytes_after": ids_after, "growth_bytes": ids_after - ids_before,
            "lines_after": n_ids},
        "baseline_before": pre, "baseline_after": post,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
