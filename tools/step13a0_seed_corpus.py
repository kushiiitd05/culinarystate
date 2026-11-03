#!/usr/bin/env python
"""Step 13a-0 (S157): offline seed corpus from existing local artifacts, exact-DOI dedup only.

Status: PROVISIONAL_PENDING_13A. No network call, no API key, no ledger write, no id minted. Reads the
verification queue, rejected candidates, Route A precheck, human review pack (DOIs only), the PE
``pe_pub:*`` PAPER records of SRC and the DOI-bearing DOC records (read only), counts the query
matrix (no record-level ids) and, when present locally, the git-ignored OpenAlex first-page caches
``data/raw/openalex/*.json``. Writes three NEW files (refuses overwrite): the seed corpus JSONL (ids,
DOIs, metadata, provenance; no abstract or free text), a counts-only JSON report and its Markdown
rendering. The 08a ledger baseline is checked before and after when the repository root is used.

    python tools/step13a0_seed_corpus.py --no-openalex     # tracked artifacts only (cloud container)
    python tools/step13a0_seed_corpus.py                   # full local run: adds data/raw/openalex/
    python tools/step13a0_seed_corpus.py --openalex-dir <dir> --out <jsonl> --report-json <json> --report-md <md>
Mode "full" is used when the OpenAlex directory exists and --no-openalex is not given, else "tracked".
Exit 0 written, 2 refused / missing input, 3 ledger baseline mismatch.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evidence import seed_corpus as S  # noqa: E402
from culinarystate.lineage.guard import LedgerBaselineMismatch, verify_baseline  # noqa: E402

BASELINE = "registry/baseline_ledger_hashes_08a_v1.csv"
DEFAULT_OUT = {"tracked": "registry/evidence/seed_corpus_13a0_tracked_v0.jsonl",
               "full": "registry/evidence/seed_corpus_13a0_full_v0.jsonl"}
DEFAULT_REPORT_JSON = {"tracked": "reports/step13/S157_13a0_seed_corpus_tracked_counts.json",
                       "full": "reports/step13/S157_13a0_seed_corpus_full_counts.json"}
DEFAULT_REPORT_MD = {"tracked": "reports/step13/S157_13a0_seed_corpus_tracked_report.md",
                     "full": "reports/step13/S157_13a0_seed_corpus_full_report.md"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--no-openalex", action="store_true", help="ignore data/raw/openalex even if present")
    ap.add_argument("--openalex-dir", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--report-json", type=Path, default=None)
    ap.add_argument("--report-md", type=Path, default=None)
    a = ap.parse_args(argv)
    root = a.root.resolve()
    oa_dir = a.openalex_dir or root / S.INPUT_PATHS["openalex_pages"]
    mode = "full" if not a.no_openalex and oa_dir.is_dir() else "tracked"
    out = a.out or root / DEFAULT_OUT[mode]
    rep_json = a.report_json or root / DEFAULT_REPORT_JSON[mode]
    rep_md = a.report_md or root / DEFAULT_REPORT_MD[mode]
    check_baseline = root == ROOT.resolve()
    try:
        if check_baseline:
            verify_baseline(root / BASELINE, root)
        for p in (out, rep_json, rep_md):
            S.guard_output_path(p, root=root)
        corpus = S.build_seed_corpus(S.default_inputs(root, openalex=mode == "full", openalex_dir=oa_dir),
                                     root=root)
        written = [S.write_seed_corpus(corpus, out, root=root), S.write_counts(corpus.counts, rep_json, root=root),
                   S.write_report_md(corpus.counts, rep_md, root=root)]
        if check_baseline:
            verify_baseline(root / BASELINE, root)
    except (S.SeedCorpusError, UnicodeDecodeError) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    except LedgerBaselineMismatch as e:
        print(f"ledger baseline mismatch: {e}", file=sys.stderr)
        return 3
    s = corpus.counts["seeds"]
    print(f"mode {mode}: {s['total']} seeds ({s['with_valid_doi']} with a valid DOI) from "
          f"{corpus.counts['records_read_total']} records")
    for p in written:
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
