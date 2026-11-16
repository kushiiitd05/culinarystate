#!/usr/bin/env python
"""Layer 1 (TEXT_STATED) condition-binding census, counts only, + optional per-event dataset (S172, D-077). DRAFT.

Same corpus reader, seeded sample and protected-ledger check as tools/step26g_census.py. Writes ONE counts-only JSON
(refuses overwrite or protected places). ``--records-dir`` writes the per-event Layer 1 dataset (recipe and event ids,
values, spans); it must be under data/ (git-ignored) or outside the repository.

    python tools/binding_census.py --seed 20261104 --sample-size 1000 --out reports/step26/<new>.json
    python tools/binding_census.py --seed 20261104 --sample-size 612782 --workers 64 --families WIKIBOOKS ... \
        --records-dir data/derived/physical_L1/ --out ...                      (server; BBC on the Mac, D-003)
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
from culinarystate.simulation import binding_census as BC  # noqa: E402

_spec = importlib.util.spec_from_file_location("_step17b_rung_a_dryrun", ROOT / "tools/step17b_rung_a_dryrun.py")
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)
CODE_FILES = ("src/culinarystate/simulation/condition_binding.py", "src/culinarystate/simulation/binding_census.py",
              "src/culinarystate/simulation/endpoint_cues.py", "registry/endpoint_cue_lexicon_v1.csv",
              "registry/process_medium_map_v1.csv", "tools/binding_census.py")


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


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", required=True)
    ap.add_argument("--records-dir", default=None)
    ap.add_argument("--families", nargs="+", choices=T17.FAMILIES, default=list(T17.FAMILIES))
    ap.add_argument("--no-baseline-check", action="store_true")
    a = ap.parse_args(argv)
    root, out = Path(a.root), Path(a.out)
    if a.sample_size < 1 or a.workers < 1:
        ap.error("--sample-size and --workers must be positive")
    if out.exists():
        ap.error("refusing to overwrite an existing report")
    rdir = None
    if a.records_dir:
        rdir = Path(a.records_dir).resolve()
        try:
            inside = rdir.relative_to(ROOT.resolve()).parts
        except ValueError:
            inside = None
        if inside is not None and inside[:1] != ("data",):
            ap.error("--records-dir must be under data/ (git-ignored) or outside the repository")
        if rdir.exists() and any(rdir.iterdir()):
            ap.error("--records-dir must be empty or new")
        rdir.mkdir(parents=True, exist_ok=True)
    prov = provenance()
    if a.no_baseline_check:
        baseline = "SKIPPED_BY_FLAG"
    elif not _ok(root):
        print(json.dumps({"status": "REFUSED", "reason": "PROTECTED_LEDGER_BASELINE_CHECK_FAILED_BEFORE_RUN"}))
        return 2
    else:
        baseline = "PENDING_AFTER_RUN"
    status: dict = {}
    rep = BC.census_from_records(T17._stream(a.families, root, record_source or T17.corpus_records, status),
                                 seed=a.seed, size=a.sample_size, workers=a.workers, records_dir=rdir)
    if baseline == "PENDING_AFTER_RUN":
        baseline = "PASS_BEFORE_AND_AFTER" if _ok(root) else "FAILED_AFTER_RUN"
    rep.update(family_status=dict(sorted(status.items())), baseline_check=baseline, families_requested=list(a.families),
               code_provenance=prov, code_unchanged_during_run=provenance() == prov,
               records_written=rdir is not None)
    try:
        D.write_report(out, rep, root=root)
    except D.DryRunError as exc:
        ap.error(str(exc))
    print(json.dumps({k: rep[k] for k in ("recipes_sampled", "heat_events", "driver_ready_events", "contract_bindings",
                                           "baseline_check")}))
    return 4 if baseline == "FAILED_AFTER_RUN" else (3 if any(v != "READ" for v in status.values()) else 0)


if __name__ == "__main__":
    sys.exit(main())
