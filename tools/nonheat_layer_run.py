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

S176 L-PHYS (layer 0.2.0): RESTING carries the evaporation cap of ``phase_change`` (default ON). ``--l2-only`` re-runs only
Layer 2 over existing Layer 1 records (``--l1-records-dir`` then names the existing directory, nothing is written there);
``--compare-uncapped`` also runs the SUPERSEDED 0.1.0 model on RESTING events and reports a counts-only before/after block;
``--no-evaporation-cap`` reproduces 0.1.0; ``--altitude-m`` / ``--pressure-psig`` are the optional cap parameters.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")  # many fork workers: no BLAS oversubscription

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.lineage.guard import LedgerBaselineMismatch  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402
from culinarystate.simulation import nonheat_binding as NB  # noqa: E402
from culinarystate.simulation import nonheat_scenario as NS  # noqa: E402
from culinarystate.simulation import phase_change as PC  # noqa: E402

_spec = importlib.util.spec_from_file_location("_step17b_rung_a_dryrun", ROOT / "tools/step17b_rung_a_dryrun.py")
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)
CODE_FILES = ("src/culinarystate/simulation/nonheat_binding.py", "src/culinarystate/simulation/nonheat_scenario.py",
              "src/culinarystate/simulation/nonheat_drivers.py", "src/culinarystate/simulation/physics_drivers.py",
              "src/culinarystate/simulation/phase_change.py", "registry/phase_change_v1.csv",
              "registry/matrix_moisture_regime_v1.csv",
              "src/culinarystate/simulation/condition_binding.py", "src/culinarystate/simulation/scenario_layer.py",
              "registry/scenario_defaults_nonheat_v1.csv", "registry/scenario_defaults_v1.csv",
              "registry/process_medium_map_v1.csv", "tools/nonheat_layer_run.py")
_LAYER: list = []  # [main layer, SUPERSEDED uncapped layer or None]
BR = ("GENTLE", "TYPICAL", "INTENSE")


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


def _rest_compare(c: Counter, vals: dict, tag: str, out: dict, capped: bool, dry: bool) -> None:
    """RESTING counts and temperatures of one variant; ``dry`` is the matrix regime (DRY_LOW_MOISTURE: never capped) as
    classified by the capped model, so both variants are split the same way (tags ``<tag>_moist`` / ``<tag>_dry``)."""
    c[("cmp", tag, "rest_events")] += 1
    c[("cmp", tag, "status", out["status"])] += 1
    over = viol = over_moist = False
    sub = f"{tag}_dry" if dry else f"{tag}_moist"
    for b in BR:
        s = out["scenarios"].get(b)
        if not s:
            continue
        c[("cmp", tag, "rest_computed", b)] += 1
        c[("cmp", tag, "rest_computed_dry_class" if dry else "rest_computed_moist_class", b)] += 1
        for f in ("core_end_of_heat_c", "core_peak_c", "core_end_c"):
            vals.setdefault((tag, f, b), []).append(s[f])
            vals.setdefault((sub, f, b), []).append(s[f])
        if s["core_peak_c"] > 100.0:
            c[("cmp", tag, "core_peak_gt_100", b)] += 1
            c[("cmp", tag, "core_peak_gt_100_dry_class" if dry else "core_peak_gt_100_moist_class", b)] += 1
            over = True
            over_moist = over_moist or not dry
        if capped and s.get("t_cap_c") is not None and (s["core_peak_c"] > s["t_cap_c"] + _TOL or
                                                         s["volume_avg_end_c"] > s["t_cap_c"] + _TOL):
            c[("cmp", tag, "violations_above_cap_plus_tol", b)] += 1
            viol = True
    if over:
        c[("cmp", tag, "events_core_peak_gt_100_any_bracket")] += 1
    if over_moist:
        c[("cmp", tag, "events_core_peak_gt_100_moist_class_any_bracket")] += 1
    if viol:
        c[("cmp", tag, "events_violating_cap_any_bracket")] += 1


_TOL = 0.5


def _l2_file(paths: tuple[str, str]) -> dict:
    src, dst = paths
    c: Counter = Counter()
    vals: dict = {}
    layer, old = _LAYER
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
            if old is not None and rec["nh_family"] == "RESTING":
                dry = out["status"] == "SCENARIO_COMPUTED" and out["scenarios"]["TYPICAL"].get("t_cap_c", 1) is None
                if out["status"] == "SCENARIO_COMPUTED":
                    _rest_compare(c, vals, "after", out, layer.capped, dry)
                try:
                    o = old.run(rec)
                    if o["status"] == "SCENARIO_COMPUTED":
                        _rest_compare(c, vals, "before", o, False, dry)
                except Exception:  # noqa: BLE001 - counted below
                    c[("cmp", "before", "error")] += 1
    return {"c": dict(c), "vals": vals}


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


def run_l2(l1_dir: Path, l2_dir: Path, workers: int, policy: PC.CapPolicy, compare: bool) -> tuple[dict, dict]:
    global _TOL
    _LAYER.clear()
    main_layer = NS.NonHeatScenario.load(policy=policy)
    _TOL = main_layer.heat.pc.invariant_tol_c if main_layer.capped else 0.5
    _LAYER.extend([main_layer, NS.NonHeatScenario.load(policy=PC.CapPolicy(enabled=False)) if compare else None])
    jobs = [(str(f), str(l2_dir / f.name)) for f in sorted(l1_dir.glob("*.jsonl"))]
    if workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(workers) as pool:
            parts = pool.map(_l2_file, jobs, chunksize=1)
    else:
        parts = [_l2_file(j) for j in jobs]
    tot: Counter = Counter()
    vals: dict = {}
    for p in parts:
        tot.update(p["c"])
        for k, v in p["vals"].items():
            vals.setdefault(k, []).extend(v)
    fams = NB.NH_FAMILIES
    n = {f: tot[("n", f)] for f in fams}
    computed = {f: tot[("status", f, "SCENARIO_COMPUTED")] for f in fams}
    qual = {f: tot[("status", f, "QUALITATIVE_FLAGS_ONLY")] + tot[("status", f, "CONDITIONS_ONLY_KINETICS_UNKNOWN")]
            for f in fams}
    rep = {"l1_files": len(jobs), "events_by_family": n, "l2_driver_computed_by_family": computed,
           "l2_qualitative_or_conditions_by_family": qual, "status": _nest(tot, "status"),
           "transition": _nest(tot, "transition"), "missing_reasons": _nest(tot, "missing"),
           "basis_class_typical_bracket": _nest(tot, "basis"), "flags_typical_bracket": _nest(tot, "flag"),
           "bracket_order_check": _nest(tot, "order"), "cooling_target_reached": _nest(tot, "target_reached"),
           "errors_by_class": _nest(tot, "error")}
    extra: dict = {}
    if compare:
        q: dict = {}
        for (tag, f, b), xs in sorted(vals.items()):
            a = np.asarray(xs, dtype=float)
            qq = np.quantile(a, QUANTILES)
            q.setdefault(tag, {}).setdefault(f, {})[b] = {
                "n": int(a.size), **{("max" if p == 1.0 else f"p{int(round(p * 100)):02d}"): round(float(x), 3)
                                     for p, x in zip(QUANTILES, qq)}}
        extra = {"before_after": {"before_layer_version": NS.VERSION_UNCAPPED, "after_layer_version": NS.VERSION,
                                  "counts": _nest(tot, "cmp"), "temperature_quantiles_resting": q}}
    return rep, extra


QUANTILES = (0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0)


def _check_existing_dir(ap, p: Path, name: str) -> Path:
    r = p.resolve()
    try:
        inside = r.relative_to(ROOT.resolve()).parts
    except ValueError:
        inside = None
    if inside is not None and inside[:1] != ("data",):
        ap.error(f"{name} must be under data/ (git-ignored) or outside the repository")
    if not r.is_dir() or not any(r.glob("*.jsonl")):
        ap.error(f"{name} must be an existing directory of Layer 1 .jsonl records with --l2-only")
    return r


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--l1-out", default=None, help="Layer 1 counts report (not used with --l2-only)")
    ap.add_argument("--l2-out", required=True)
    ap.add_argument("--l1-records-dir", required=True)
    ap.add_argument("--l2-records-dir", required=True)
    ap.add_argument("--families", nargs="+", choices=T17.FAMILIES, default=list(T17.FAMILIES))
    ap.add_argument("--no-baseline-check", action="store_true")
    ap.add_argument("--l2-only", action="store_true", help="re-run Layer 2 over the existing Layer 1 records")
    ap.add_argument("--l1-report", default=None, help="existing Layer 1 report: only recipes_sampled is read (--l2-only)")
    ap.add_argument("--compare-uncapped", action="store_true",
                    help="also run the SUPERSEDED 0.1.0 model on RESTING events and report a before/after block")
    ap.add_argument("--no-evaporation-cap", action="store_true", help="run the SUPERSEDED 0.1.0 model (regression only)")
    ap.add_argument("--altitude-m", type=float, default=None, help="optional altitude (default sea level, flagged)")
    ap.add_argument("--pressure-psig", type=float, default=None, help="optional gauge pressure of a pressure process")
    a = ap.parse_args(argv)
    root, o2 = Path(a.root), Path(a.l2_out)
    o1 = Path(a.l1_out) if a.l1_out else None
    if a.sample_size < 1 or a.workers < 1:
        ap.error("--sample-size and --workers must be positive")
    if a.no_evaporation_cap and a.compare_uncapped:
        ap.error("--compare-uncapped needs the capped model as the main model")
    if not a.l2_only and o1 is None:
        ap.error("--l1-out is required unless --l2-only")
    for o in (o1, o2):
        if o is not None and o.exists():
            ap.error("refusing to overwrite an existing report")
    d1 = _check_existing_dir(ap, Path(a.l1_records_dir), "--l1-records-dir") if a.l2_only \
        else _check_dir(ap, Path(a.l1_records_dir), "--l1-records-dir")
    d2 = _check_dir(ap, Path(a.l2_records_dir), "--l2-records-dir")
    policy = PC.CapPolicy(enabled=not a.no_evaporation_cap, altitude_m=a.altitude_m, pressure_psig=a.pressure_psig)
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
    rep1 = None
    if a.l2_only:
        sampled = None
        if a.l1_report:
            sampled = json.loads(Path(a.l1_report).read_text(encoding="utf-8")).get("recipes_sampled")
    else:
        rep1 = NB.census_from_records(T17._stream(a.families, root, record_source or T17.corpus_records, status),
                                      seed=a.seed, size=a.sample_size, workers=a.workers, records_dir=d1)
        sampled = rep1["recipes_sampled"]
    t1 = time.time()
    rep2c, extra = run_l2(d1, d2, a.workers, policy, a.compare_uncapped)
    t2 = time.time()
    if baseline == "PENDING_AFTER_RUN":
        baseline = "PASS_BEFORE_AND_AFTER" if _ok(root) else "FAILED_AFTER_RUN"
    common = dict(family_status=dict(sorted(status.items())), baseline_check=baseline, families_requested=list(a.families),
                  code_provenance=prov, code_unchanged_during_run=provenance() == prov, started_at_utc=started,
                  ended_at_utc=_now())
    reg = {"scenario_registry_nonheat_sha256": hashlib.sha256((root / NS.REGISTRY).read_bytes()).hexdigest(),
           "scenario_registry_heat_sha256": hashlib.sha256((root / "registry/scenario_defaults_v1.csv").read_bytes())
           .hexdigest()}
    if policy.enabled:
        reg.update(phase_change_registry_sha256=hashlib.sha256((root / PC.REGISTRY).read_bytes()).hexdigest(),
                   matrix_regime_registry_sha256=hashlib.sha256((root / PC.REGIME_REGISTRY).read_bytes()).hexdigest(),
                   cap_model=PC.VERSION, cap_policy={"enabled": True, "altitude_m": a.altitude_m,
                                                    "pressure_psig": a.pressure_psig},
                   supersedes="NONHEAT_SCENARIO_L2_0_1_0_RESTING_CORE_FIELDS")
    else:
        reg.update(superseded_model=True)
    if rep1 is not None:
        rep1.update(common, records_written=True, records_manifest_sha256=dir_manifest_sha256(d1),
                    wall_seconds_l1=round(t1 - t0, 1), workers=a.workers)
    rep2 = {"record": "NONHEAT_SCENARIO_L2_SUMMARY", "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY",
            "layer_version": NS.VERSION if policy.enabled else NS.VERSION_UNCAPPED, "labels": NS.LABELS,
            "contains_ids": False, "contains_text": False, "citable": False, "counts_as_human_gate": False, **reg, **common,
            "records_written": True, "records_manifest_sha256": dir_manifest_sha256(d2),
            **({"l1_records_manifest_sha256": dir_manifest_sha256(d1)} if a.l2_only else {}), "l2_only": bool(a.l2_only),
            "wall_seconds_l2": round(t2 - t1, 1), "workers": a.workers, "recipes_sampled": sampled, "counts": rep2c, **extra}
    try:
        if rep1 is not None:
            D.write_report(o1, rep1, root=root)
        D.write_report(o2, rep2, root=root)
    except D.DryRunError as exc:
        ap.error(str(exc))
    print(json.dumps({"recipes_sampled": sampled, "events": sum(rep2c["events_by_family"].values()),
                      "wall_seconds_l2": rep2["wall_seconds_l2"], "baseline_check": baseline,
                      "l2_sha256": hashlib.sha256(o2.read_bytes()).hexdigest(),
                      **({"l1_sha256": hashlib.sha256(o1.read_bytes()).hexdigest()} if o1 else {})}))
    return 4 if baseline == "FAILED_AFTER_RUN" else (3 if any(v != "READ" for v in status.values()) else 0)


if __name__ == "__main__":
    sys.exit(main())
