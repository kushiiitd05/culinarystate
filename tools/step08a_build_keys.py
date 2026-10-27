#!/usr/bin/env python3
"""Step 08a.5: study / lineage-root / split-group keys and independence_resolution per ACTIVE EVD row.

  python tools/step08a_build_keys.py --ledgers-root <scratch root with data/{EVD,STUDY,DOC,SRC}.jsonl> \
      --edges <edge_candidates.jsonl> --out-dir <dir under ALLOWED_OUT_ROOT>

--ledgers-root is REQUIRED; any root inside (or containing) this repo, including the real ledgers/, is refused.
Writes keys.jsonl (one record per EVD row) and counts.json (gates, counts, level sensitivity). Deterministic.
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
from culinarystate.lineage import keys  # noqa: E402
from culinarystate.lineage.guard import assert_safe_write_target  # noqa: E402

ALLOWED_OUT_ROOT = Path("/private/tmp/claude-501/-Users-bournesmartasfuck-kush-Desktop/"
                        "775421c5-2d3e-4fef-b4e7-eac43c97b253/scratchpad/keys")


class RefusedPathError(RuntimeError):
    """Input or output path not allowed."""


def _inside(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def _check_paths(root: Path, out: Path, repo: Path, allowed: Path) -> tuple[Path, Path]:
    root, out, repo, allowed = (Path(p).resolve() for p in (root, out, repo, allowed))
    if _inside(root, repo) or _inside(repo, root):
        raise RefusedPathError(f"refusing ledgers root inside (or containing) the repo: {root}")
    if _inside(out, repo) or not _inside(out, allowed):
        raise RefusedPathError(f"output must be under {allowed} and outside the repo: {out}")
    assert_safe_write_target(out)
    for n in ("EVD", "STUDY", "DOC", "SRC"):
        if not (root / "data" / f"{n}.jsonl").is_file():
            raise RefusedPathError(f"no data/{n}.jsonl under {root}")
    return root, out


def load_latest(path: Path, active_only: bool = True) -> dict[str, dict]:
    last: dict[str, dict] = {}
    with Path(path).open() as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                cur = last.get(r["id"])
                if cur is None or r["version"] > cur["version"]:
                    last[r["id"]] = r
    return {k: v for k, v in sorted(last.items()) if not active_only or v.get("status") == "ACTIVE"}


def _sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(ledgers_root: Path, edges_path: Path, out_dir: Path, *, repo_root: Path = REPO,
        allowed_out_root: Path = ALLOWED_OUT_ROOT) -> dict:
    root, out = _check_paths(ledgers_root, out_dir, repo_root, allowed_out_root)
    d = root / "data"
    rows = list(load_latest(d / "EVD.jsonl").values())
    studies, docs, srcs = (load_latest(d / f"{n}.jsonl") for n in ("STUDY", "DOC", "SRC"))
    edges = [json.loads(l) for l in Path(edges_path).read_text().splitlines() if l.strip()]
    res = keys.assign_keys(rows, studies, docs, srcs, edges)
    recs, st = res["records"], res["stats"]
    gates = keys.check_gates(recs, len(rows), studies, docs)
    drv_parents = {r["id"]: r["parent_ids"] for r in rows if r.get("parent_ids")}
    gates["G08-2"] = {**keys.check_drv_gate(recs, drv_parents),
                      "note": "no DRV rows in the ledgers; rule tested on synthetic data" if not drv_parents else "applied"}
    sizes = Counter(r["split_group_id"] for r in recs)
    counts = {
        "rule_version": keys.RULE_VERSION, "rows_total": len(recs), "gates": gates,
        "inputs_sha256": {"EVD": _sha(d / "EVD.jsonl"), "edges": _sha(edges_path)},
        "study_ids_distinct": len({r["study_id"] for r in recs if r["study_id"]}),
        "lineage_roots": st["lineage_roots"], "split_groups": st["split_groups"],
        "largest_split_group_rows": st["largest_group_rows"], "largest_split_group_share": st["largest_group_share"],
        "top5_split_groups": [{"id": k, "rows": v, "share": v / len(recs)} for k, v in sizes.most_common(5)],
        "exceeds_40pct_rule": st["largest_group_share"] > 0.40,
        "independence_resolution": dict(sorted(Counter(r["independence_resolution"] for r in recs).items())),
        "study_id_status": dict(sorted(Counter(r["study_id_status"] for r in recs).items())),
        "lab_group_status": dict(sorted(Counter(r["lab_group_status"] for r in recs).items())),
        "stats": st,
        "level_sensitivity": keys.level_sensitivity(rows, studies, docs, srcs, edges),
        "edges_input": len(edges),
        "edges_input_by_level": dict(sorted(Counter(e.get("detector_level") for e in edges).items())),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "keys.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in recs))
    (out / "counts.json").write_text(json.dumps(counts, indent=2, sort_keys=True) + "\n")
    return counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledgers-root", required=True, type=Path)
    ap.add_argument("--edges", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    a = ap.parse_args(argv)
    t0 = time.perf_counter()
    try:
        counts = run(a.ledgers_root, a.edges, a.out_dir)
    except RefusedPathError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    print(json.dumps(counts, indent=2, sort_keys=True))
    print(f"runtime_seconds={time.perf_counter() - t0:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
