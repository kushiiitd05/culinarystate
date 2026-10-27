#!/usr/bin/env python3
"""Step 08a.3: LIN edge candidates from EVD rows, written ONLY under the scratch edges directory.

  python tools/step08a_detect_edges.py --ledgers-root <scratch root containing data/EVD.jsonl> --out-dir <dir under ALLOWED_OUT_ROOT>

--ledgers-root is REQUIRED (no default). Any root inside this repo (including the repo's real ledgers/) is refused.
Outputs: edge_candidates.jsonl and edge_counts.json (deterministic; runtime is printed, never stored).
Never writes to a ledger; edge candidates carry no LIN ids.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from culinarystate.lineage import detectors  # noqa: E402
from culinarystate.lineage.guard import assert_safe_write_target  # noqa: E402

ALLOWED_OUT_ROOT = Path("/private/tmp/claude-501/-Users-bournesmartasfuck-kush-Desktop/"
                        "775421c5-2d3e-4fef-b4e7-eac43c97b253/scratchpad/edges")


class RefusedPathError(RuntimeError):
    """Input or output path not allowed."""


def _inside(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def _check_paths(ledgers_root: Path, out_dir: Path, repo_root: Path, allowed_out_root: Path) -> tuple[Path, Path]:
    root, out = Path(ledgers_root).resolve(), Path(out_dir).resolve()
    repo, allowed = Path(repo_root).resolve(), Path(allowed_out_root).resolve()
    if _inside(root, repo) or _inside(repo, root):
        raise RefusedPathError(f"refusing ledgers root inside (or containing) the repo: {root}")
    if _inside(out, repo) or not _inside(out, allowed):
        raise RefusedPathError(f"output must be under {allowed} and outside the repo: {out}")
    assert_safe_write_target(out)
    if not (root / "data" / "EVD.jsonl").is_file():
        raise RefusedPathError(f"no data/EVD.jsonl under {root}")
    return root, out


def load_latest_active(evd_path: Path) -> list[dict]:
    latest: dict[str, dict] = {}
    with Path(evd_path).open() as f:
        for line in f:
            r = json.loads(line)
            cur = latest.get(r["id"])
            if cur is None or r["version"] > cur["version"]:
                latest[r["id"]] = r
    return [r for _, r in sorted(latest.items()) if r.get("status") == "ACTIVE"]


def run(ledgers_root: Path, out_dir: Path, *, repo_root: Path = REPO, allowed_out_root: Path = ALLOWED_OUT_ROOT) -> dict:
    root, out = _check_paths(ledgers_root, out_dir, repo_root, allowed_out_root)
    evd = root / "data" / "EVD.jsonl"
    rows = load_latest_active(evd)
    edges, stats = detectors.detect_edges(detectors.item_from_evd(r) for r in rows)
    counts = {
        "rule_version": detectors.RULE_VERSION, "b3_cut": detectors.B3_CUT,
        "input_evd_sha256": hashlib.sha256(evd.read_bytes()).hexdigest(), "rows_total": len(rows),
        "rows_without_numeric_value": stats["rows_without_numeric_value"], "edges_total": len(edges),
        "by_level": dict(sorted(Counter(e["detector_level"] for e in edges).items())),
        "by_edge_type": dict(sorted(Counter(e["edge_type"] for e in edges).items())),
        "by_level_and_type": dict(sorted(Counter(f"{e['detector_level']}|{e['edge_type']}" for e in edges).items())),
        "detector_stats": stats,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "edge_candidates.jsonl").write_text(detectors.edges_to_jsonl(edges))
    (out / "edge_counts.json").write_text(json.dumps(counts, indent=2, sort_keys=True) + "\n")
    return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledgers-root", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    a = ap.parse_args(argv)
    t0 = time.perf_counter()
    try:
        counts = run(a.ledgers_root, a.out_dir)
    except RefusedPathError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    print(json.dumps(counts, indent=2, sort_keys=True))
    print(f"runtime_seconds={time.perf_counter() - t0:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
