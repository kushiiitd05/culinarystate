#!/usr/bin/env python
"""Step 17b (S155): read-only, counts-only dry-run of Rung A over a seeded recipe sample. DRAFT_PENDING_16c.

Streams the local recipe corpora through culinarystate.recipes.corpus (the iterators
used to build recipe_base_v1), keeps the --sample-size recipes (default 1,000) with
the smallest sha256(seed || recipe_id), runs Rung A + validators V1-V4 + the
invented-value auditor in memory and writes ONE JSON file of integer counts by code.
No recipe text, recipe id, seed or exception message is ever written or printed.
Protected ledgers are hash-checked before and after the run (as in the Step 16 rc2
dry-run); refuses to write in ledgers/, data/, exports/, annotation/gold/ or over an
existing file. Not a gold score and not a human gate.

Run locally where the data bundle is present (not in git):
    python tools/step17b_rung_a_dryrun.py --seed <SEED>
Default output: reports/step17/rung_a_dryrun_counts.json (refuses overwrite).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.extraction import rung_a_measure as M  # noqa: E402
from culinarystate.lineage.guard import LedgerBaselineMismatch, verify_baseline  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

FAMILIES = ("A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT", "FOODCOM", "TASTESET")
BASELINE = "registry/baseline_ledger_hashes_08a_v1.csv"
OUT = "reports/step17/rung_a_dryrun_counts.json"


def corpus_records(families, root):
    """Default read-only source: the existing corpus iterators (repository root only; as the S154 dry-run)."""
    if Path(root).resolve() != ROOT.resolve():
        raise FileNotFoundError("corpus iterators read the repository root only")
    from culinarystate.recipes import corpus
    rec_families = tuple(f for f in families if f in ("A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT"))
    if rec_families:
        yield from corpus.iter_rec_corpora(families=rec_families)
    if "FOODCOM" in families:
        yield from corpus.iter_foodcom()
    if "TASTESET" in families:
        yield from corpus.iter_tasteset()


def _stream(families, root, record_source, status):
    for fam in families:
        n = 0
        try:
            for rec in record_source((fam,), root):
                if rec.get("source_family") != fam:
                    continue
                n += 1
                yield rec
        except (FileNotFoundError, OSError, ImportError):
            status[fam] = "INPUT_ERROR_PARTIAL" if n else "INPUT_MISSING"
            continue
        status[fam] = "READ"


def _baseline(root):
    verify_baseline(Path(root) / BASELINE, Path(root))


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", required=True, help="sampling seed (only its SHA-256 is reported)")
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", default=None, help=f"new counts-only JSON (default {OUT})")
    ap.add_argument("--families", nargs="+", choices=FAMILIES, default=list(FAMILIES))
    ap.add_argument("--no-baseline-check", action="store_true",
                    help="skip the protected-ledger hash check (recorded in the report; tests only)")
    a = ap.parse_args(argv)
    if a.sample_size < 1:
        ap.error("--sample-size must be positive")
    root = Path(a.root)
    out = Path(a.out) if a.out else root / OUT
    if a.no_baseline_check:
        baseline = "SKIPPED_BY_FLAG"
    else:
        try:
            _baseline(root)
        except (LedgerBaselineMismatch, OSError, KeyError, ValueError):
            print(json.dumps({"status": "REFUSED", "reason": "PROTECTED_LEDGER_BASELINE_CHECK_FAILED_BEFORE_RUN"}))
            return 2
        baseline = "PENDING_AFTER_RUN"
    status = {}
    report = M.summarise_records(_stream(a.families, root, record_source or corpus_records, status), seed=a.seed,
                                 size=a.sample_size, schema=D.load_schema(ROOT))
    if baseline == "PENDING_AFTER_RUN":
        try:
            _baseline(root)
            baseline = "PASS_BEFORE_AND_AFTER"
        except (LedgerBaselineMismatch, OSError, KeyError, ValueError):
            baseline = "FAILED_AFTER_RUN"
    report.update(family_status=dict(sorted(status.items())), baseline_check=baseline,
                  families_requested=list(a.families))
    try:
        D.write_report(out, report, root=root)
    except D.DryRunError as exc:
        ap.error(str(exc))
    t = report["totals"]
    print(json.dumps({"status": report["status"], "output": str(out), "recipes_seen": t["recipes_seen"],
                      "recipes_sampled": t["recipes_sampled"], "invented_count": t["invented_count"],
                      "exceptions": sum(t["exceptions"].values()), "baseline_check": baseline,
                      "family_status": report["family_status"]}))
    if baseline == "FAILED_AFTER_RUN":
        return 4
    return 3 if any(v != "READ" for v in status.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
