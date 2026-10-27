#!/usr/bin/env python3
"""Step 08a.6: component-feasibility report (G08-7). Scratch outputs only.

  python tools/step08a_feasibility.py --ledgers-root <scratch root> --keys <keys.jsonl> --out-dir <dir>

Reads EVD (source family, analyte, matrix, process) and SVAR from a scratch ledgers root; refuses any root inside
the repo and any output outside ALLOWED_OUT_ROOT. Writes feasibility.json and feasibility_report.txt. Deterministic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from culinarystate.lineage import feasibility as fz  # noqa: E402
from culinarystate.lineage.guard import assert_safe_write_target  # noqa: E402

ALLOWED_OUT_ROOT = Path("/private/tmp/claude-501/-Users-bournesmartasfuck-kush-Desktop/"
                        "775421c5-2d3e-4fef-b4e7-eac43c97b253/scratchpad/feasibility")


class RefusedPathError(RuntimeError):
    """Input or output path not allowed."""


def _inside(p: Path, parent: Path) -> bool:
    return p == parent or parent in p.parents


def _check_out(out: Path, repo: Path, allowed: Path) -> Path:
    out, repo, allowed = (Path(p).resolve() for p in (out, repo, allowed))
    if _inside(out, repo) or not _inside(out, allowed):
        raise RefusedPathError(f"output must be under {allowed} and outside the repo: {out}")
    assert_safe_write_target(out)
    return out


def _load_latest(path: Path) -> dict:
    last: dict = {}
    for line in Path(path).read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r["id"] not in last or r["version"] > last[r["id"]]["version"]:
                last[r["id"]] = r
    return last


def _pct(x) -> str:
    return "n/a" if x is None else f"{100 * x:.2f}%"


def _fmt(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def render(rep: dict) -> str:
    L = ["08a.6 component-feasibility report (G08-7; THR-08A-08, 09, 15, 20)", "SCRATCH / PROVISIONAL: built on keys-v1 scratch assignments.", ""]
    L += ["Formulas:"] + [f"  {k}: {v}" for k, v in rep["formulas"].items()] + [""]
    o = rep["overall"]
    L += [f"Rows {rep['rows']}; split groups {o['all_rows']['groups']}; largest group {o['all_rows']['largest_group_rows']} rows "
          f"= {_pct(o['all_rows']['largest_share'])} of all rows; card rule (>40%) exceeded: {o['card_exceeds']}.", ""]
    for name in ("A_tier_only", "B_tier_and_human_verified"):
        a = o[name]
        L.append(f"Overall, reading {name}: pool rows {a['pool_rows']}, groups {a['pool_groups']}, largest share {_pct(a['pool_largest_share'])}, "
                 f"n_eff {_fmt(a['n_eff'])}, share<=40% {a['share_pass']}, n_eff>=10 {a['neff_pass']}, label: {a['label']}")
    L += ["", "By target family (SVAR.family):"]
    for t, v in rep["by_target_family"].items():
        a = v["A_tier_only"]
        L.append(f"  {t}: rows {v['all_rows']['rows']}, largest share {_pct(v['all_rows']['largest_share'])}, card_exceeds {v['card_exceeds']}; "
                 f"pool {a['pool_rows']} rows / {a['pool_groups']} groups, n_eff {_fmt(a['n_eff'])}, label A: {a['label']}, label B: {v['B_tier_and_human_verified']['label']}")
    s = rep["by_analyte_summary"]
    L += ["", f"By analyte: {s['analytes']} analytes, card rule exceeded in {s['card_exceeds']}, non-empty pool {s['pool_nonempty']}, refined pass (A) {s['refined_pass_A']}, labels {s['labels_A']}", "", "By source family:"]
    for f, v in rep["by_source_family"].items():
        L.append(f"  {f}: rows {v['rows']}, groups {v['groups']}, largest group {v['largest_group_rows']} ({_pct(v['largest_share'])}), n_eff {_fmt(v['n_eff'])}, resolution {v['resolution']}")
    lo = rep["losfo"]
    L += ["", f"Leave-one-source-family-out: structurally feasible {lo['structurally_feasible']}; split groups spanning families {lo['groups_spanning_families']}"]
    for f, v in lo["per_family"].items():
        L.append(f"  hold out {f}: {v['heldout_rows']} rows ({_pct(v['heldout_share'])}); train keeps {v['remaining_rows']} rows / {v['remaining_groups']} groups (>=5 groups: {v['remaining_has_ge_k_groups']})")
    for t, v in rep["losfo_by_target_family"].items():
        L.append(f"  target family {t}: structurally feasible {v['structurally_feasible']} (source families {v['families']})")
    for k, c in rep["cells_k5"].items():
        L.append(f"Cells (analyte x matrix-family x process-family), {k}: {c['cells']} cells, {c['cells_with_ge_k_groups']} with >= {c['k']} groups "
                 f"({c['surviving_rows']} rows); {c['cells_with_ge_2_source_families']} cells span >= 2 source families")
    v = rep["label_verdict"]
    L += ["", f"Lab-disjoint: {rep['lab_disjoint']}", f"LABEL VERDICT: headline (overall, reading A) = {v['headline_overall_A']}; "
          f"weakest across target families (A) = {v['weakest_across_target_families_A']}; weakest across all readings = {v['weakest_across_all_readings']}",
          "", "UNKNOWN / ambiguity register:"] + [f"  - {u}" for u in rep["unknowns"]]
    return "\n".join(L) + "\n"


def run(ledgers_root: Path, keys_path: Path, out_dir: Path, *, repo_root: Path = REPO, allowed: Path = ALLOWED_OUT_ROOT) -> dict:
    root = Path(ledgers_root).resolve()
    if _inside(root, repo_root.resolve()) or _inside(repo_root.resolve(), root):
        raise RefusedPathError(f"refusing ledgers root inside (or containing) the repo: {root}")
    out = _check_out(out_dir, repo_root, allowed)
    evd = [v for v in _load_latest(root / "data" / "EVD.jsonl").values() if v.get("status") == "ACTIVE"]
    svar = _load_latest(root / "data" / "SVAR.jsonl")
    keys = [json.loads(l) for l in Path(keys_path).read_text().splitlines() if l.strip()]
    rows = fz.join_rows(sorted(evd, key=lambda e: e["id"]), keys, svar)
    rep = fz.build_report(rows)
    rep["inputs_sha256"] = {"EVD": hashlib.sha256((root / "data" / "EVD.jsonl").read_bytes()).hexdigest(),
                            "keys": hashlib.sha256(Path(keys_path).read_bytes()).hexdigest()}
    out.mkdir(parents=True, exist_ok=True)
    (out / "feasibility.json").write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n")
    (out / "feasibility_report.txt").write_text(render(rep))
    return rep


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledgers-root", required=True, type=Path)
    ap.add_argument("--keys", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--scratch-root", type=Path, default=ALLOWED_OUT_ROOT,
                    help="output must be under this directory (default: legacy scratch dir)")
    a = ap.parse_args()
    rep = run(a.ledgers_root, a.keys, a.out_dir, allowed=a.scratch_root)
    print(json.dumps(rep["label_verdict"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
