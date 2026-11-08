#!/usr/bin/env python
"""Non-heat process families: Layer 1 (TEXT_STATED) census + Layer 2 (SCENARIO) run (S176 L-NH, D-077 extension). DRAFT.

One command, two layers, same conventions as tools/binding_census.py and tools/scenario_layer_run.py: the shared
corpus reader and seeded sample, the protected-ledger baseline check, counts-only JSON reports (never overwritten) and
per-event records in a data-plane directory. Records hold ids, spans, classes and numbers but never recipe text.

    python tools/nonheat_layer_run.py --seed 20261104 --sample-size 1000 --workers 8 \
        --families FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET \
        --l1-records-dir <data-plane>/physical_NH_L1_1000_S176 --l2-records-dir <data-plane>/physical_NH_L2_1000_S176 \
        --l1-out reports/step26/nonheat_L1_1000_S176.json --l2-out reports/step26/nonheat_L2_1000_S176.json

Record directories must be under data/ (git-ignored) or outside the repository; they must be empty or new.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.lineage.guard import LedgerBaselineMismatch  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402
from culinarystate.simulation import nonheat_binding as NB  # noqa: E402
from culinarystate.simulation import nonheat_scenario as NS  # noqa: E402

_spec = importlib.util.spec_from_file_location("_step17b_rung_a_dryrun", ROOT / "tools/step17b_rung_a_dryrun.py")
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)
CODE_FILES = ("src/culinarystate/simulation/nonheat_binding.py", "src/culinarystate/simulation/nonheat_scenario.py",
              "src/culinarystate/simulation/nonheat_drivers.py", "src/culinarystate/simulation/physics_drivers.py",
              "src/culinarystate/simulation/condition_binding.py", "src/culinarystate/simulation/scenario_layer.py",
              "registry/scenario_defaults_nonheat_v1.csv", "registry/scenario_defaults_v1.csv",
              "registry/process_medium_map_v1.csv", "tools/nonheat_layer_run.py")
_LAYER: list = []


def provenance() -> dict:
    p = T17.code_provenance()
    return {**p, "code_sha256": p["code_sha256"] + [{"path": f, "sha256": hashlib.sha256((ROOT / f).read_bytes())
                                                       .hexdigest()} for f in CODE_FILES]}


def _ok(root: Path) -> bool:
    try:
        T17._baseline(root)
        return True
    except (LedgerBaselineMismatch, OSError, KeyError, ValueError):
        return False


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _check_dir(ap, p: Path, name: str) -> Path:
    r = p.resolve()
    try:
        inside = r.relative_to(ROOT.resolve()).parts
    except ValueError:
        inside = None
    if inside is not None and inside[:1] != ("data",):
        ap.error(f"{name} must be under data/ (git-ignored) or outside the repository")
    if r.exists() and any(r.iterdir()):
        ap.error(f"{name} must be empty or new")
    r.mkdir(parents=True, exist_ok=True)
    return r


def dir_manifest_sha256(d: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(d.glob("*.jsonl")):
        h.update(f"{f.name}\0{hashlib.sha256(f.read_bytes()).hexdigest()}\n".encode())
    return h.hexdigest()


def _l2_file(paths: tuple[str, str]) -> dict:
    src, dst = paths
    c: Counter = Counter()
    layer = _LAYER[0]
    with open(src, encoding="utf-8") as fi, open(dst, "x", encoding="utf-8") as fo:
        for line in fi:
            rec = json.loads(line)
            try:
                out = layer.run(rec)
            except Exception as e:  # noqa: BLE001 - class name only; a bad row must not lose the run
                out = {**layer._base(rec), "status": "SCENARIO_ERROR", "transition_status": "unsupported", "scenarios": {},
                       "error_class": type(e).__name__}
                c[("error", rec["nh_family"], type(e).__name__)] += 1
            fo.write(json.dumps(out, separators=(",", ":")) + "\n")
            NS.count_row(out, c)
    return dict(c)


def _nest(counts, prefix: str) -> dict:
    out: dict = {}
    for key, v in sorted(counts.items(), key=lambda kv: str(kv[0])):
        if key[0] != prefix:
            continue
        d = out
        for k in key[1:-1]:
            d = d.setdefault(str(k), {})
        d[str(key[-1])] = v
    return out


def run_l2(l1_dir: Path, l2_dir: Path, workers: int) -> dict:
    _LAYER.clear()
    _LAYER.append(NS.NonHeatScenario.load())
    jobs = [(str(f), str(l2_dir / f.name)) for f in sorted(l1_dir.glob("*.jsonl"))]
    if workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(workers) as pool:
            parts = pool.map(_l2_file, jobs)
    else:
        parts = [_l2_file(j) for j in jobs]
    tot: Counter = Counter()
    for p in parts:
        tot.update(p)
    fams = NB.NH_FAMILIES
    n = {f: tot[("n", f)] for f in fams}
    computed = {f: tot[("status", f, "SCENARIO_COMPUTED")] for f in fams}
    qual = {f: tot[("status", f, "QUALITATIVE_FLAGS_ONLY")] + tot[("status", f, "CONDITIONS_ONLY_KINETICS_UNKNOWN")]
            for f in fams}
    return {"l1_files": len(jobs), "events_by_family": n, "l2_driver_computed_by_family": computed,
            "l2_qualitative_or_conditions_by_family": qual, "status": _nest(tot, "status"),
            "transition": _nest(tot, "transition"), "missing_reasons": _nest(tot, "missing"),
            "basis_class_typical_bracket": _nest(tot, "basis"), "flags_typical_bracket": _nest(tot, "flag"),
            "bracket_order_check": _nest(tot, "order"), "cooling_target_reached": _nest(tot, "target_reached"),
            "errors_by_class": _nest(tot, "error")}


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--l1-out", required=True)
    ap.add_argument("--l2-out", required=True)
    ap.add_argument("--l1-records-dir", required=True)
    ap.add_argument("--l2-records-dir", required=True)
    ap.add_argument("--families", nargs="+", choices=T17.FAMILIES, default=list(T17.FAMILIES))
    ap.add_argument("--no-baseline-check", action="store_true")
    a = ap.parse_args(argv)
    root, o1, o2 = Path(a.root), Path(a.l1_out), Path(a.l2_out)
    if a.sample_size < 1 or a.workers < 1:
        ap.error("--sample-size and --workers must be positive")
    for o in (o1, o2):
        if o.exists():
            ap.error("refusing to overwrite an existing report")
    d1 = _check_dir(ap, Path(a.l1_records_dir), "--l1-records-dir")
    d2 = _check_dir(ap, Path(a.l2_records_dir), "--l2-records-dir")
    prov = provenance()
    if a.no_baseline_check:
        baseline = "SKIPPED_BY_FLAG"
    elif not _ok(root):
        print(json.dumps({"status": "REFUSED", "reason": "PROTECTED_LEDGER_BASELINE_CHECK_FAILED_BEFORE_RUN"}))
        return 2
    else:
        baseline = "PENDING_AFTER_RUN"
    t0, started = time.time(), _now()
    status: dict = {}
    rep1 = NB.census_from_records(T17._stream(a.families, root, record_source or T17.corpus_records, status),
                                  seed=a.seed, size=a.sample_size, workers=a.workers, records_dir=d1)
    t1 = time.time()
    rep2 = run_l2(d1, d2, a.workers)
    t2 = time.time()
    if baseline == "PENDING_AFTER_RUN":
        baseline = "PASS_BEFORE_AND_AFTER" if _ok(root) else "FAILED_AFTER_RUN"
    common = dict(family_status=dict(sorted(status.items())), baseline_check=baseline, families_requested=list(a.families),
                  code_provenance=prov, code_unchanged_during_run=provenance() == prov, started_at_utc=started,
                  ended_at_utc=_now())
    rep1.update(common, records_written=True, records_manifest_sha256=dir_manifest_sha256(d1),
                wall_seconds_l1=round(t1 - t0, 1), workers=a.workers)
    reg = {"scenario_registry_nonheat_sha256": hashlib.sha256((root / NS.REGISTRY).read_bytes()).hexdigest(),
           "scenario_registry_heat_sha256": hashlib.sha256((root / "registry/scenario_defaults_v1.csv").read_bytes())
           .hexdigest()}
    rep2 = {"record": "NONHEAT_SCENARIO_L2_SUMMARY", "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY",
            "layer_version": NS.VERSION, "labels": NS.LABELS, "contains_ids": False, "contains_text": False,
            "citable": False, "counts_as_human_gate": False, **reg, **common, "records_written": True,
            "records_manifest_sha256": dir_manifest_sha256(d2), "wall_seconds_l2": round(t2 - t1, 1),
            "workers": a.workers, "recipes_sampled": rep1["recipes_sampled"], "counts": rep2}
    try:
        D.write_report(o1, rep1, root=root)
        D.write_report(o2, rep2, root=root)
    except D.DryRunError as exc:
        ap.error(str(exc))
    print(json.dumps({"recipes_sampled": rep1["recipes_sampled"], "nonheat_events": rep1["nonheat_events"],
                      "wall_seconds_l1": rep1["wall_seconds_l1"], "wall_seconds_l2": rep2["wall_seconds_l2"],
                      "baseline_check": baseline, "l1_sha256": hashlib.sha256(o1.read_bytes()).hexdigest(),
                      "l2_sha256": hashlib.sha256(o2.read_bytes()).hexdigest()}))
    return 4 if baseline == "FAILED_AFTER_RUN" else (3 if any(v != "READ" for v in status.values()) else 0)


if __name__ == "__main__":
    sys.exit(main())
