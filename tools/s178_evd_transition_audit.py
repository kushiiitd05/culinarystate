#!/usr/bin/env python3
"""S178 EVD lane, T6-C09-R2 (evidence): counts-only audit that the real transition cell tables hold no imputed value.

Reads ledgers/data/{EVD,COND}.jsonl READ-ONLY, builds the DEL-2 cell table per source family with the unmodified
``culinarystate.transition.dataset.cells_from_rows`` and reports, per family: rows in scope, how many are MEASURED / CENSORED,
how many cells carry y = 0, y_lower = 0, a missing y without the censored flag (must be 0), the censor kinds and whether any
censored row lacks a limit, the evidence tiers present, and the share of the training target that is the stated bound
(``y_train`` substitutes the bound for a censored row; that is the only substitution). Deterministic, no timestamp.

  python tools/s178_evd_transition_audit.py [--out-dir reports/s178/evd] [--selfcheck]
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s178_evd_common import (DEFAULT_OUT, ROOT, counter_dict, dumps, pct, protected_hashes, read_ledger, write_new_or_same)  # noqa: E402

TOOL_VERSION = "s178-evd-transition-audit-0.1.0-draft"


def build(root: Path) -> dict:
    import pandas as pd
    from culinarystate.transition.dataset import cells_from_rows, y_train
    led = root / "ledgers" / "data"
    evd, _ = read_ledger(led / "EVD.jsonl")
    cond, _ = read_ledger(led / "COND.jsonl")
    rows = [e for e in evd.values() if e["status"] == "ACTIVE"]
    fams = sorted({e["source_family_id"] for e in rows})
    out: dict = {}
    for fam in fams:
        fam_rows = [e for e in rows if e["source_family_id"] == fam]
        df = cells_from_rows(fam_rows, cond, fam).df
        rf = [(e.get("derived") or {}).get("retention_factor") or {} for e in fam_rows]
        status = Counter(r.get("status", "ABSENT") for r in rf)
        cens = [r for r in rf if r.get("status") == "CENSORED"]
        y = pd.to_numeric(df["y"], errors="coerce")
        yl = pd.to_numeric(df["y_lower"], errors="coerce")
        yt = y_train(df)
        out[fam] = {
            "active_rows": len(fam_rows), "retention_status_rows": counter_dict(status), "cells": int(len(df)),
            "cells_equal_measured_plus_censored": int(len(df)) == status.get("MEASURED", 0) + status.get("CENSORED", 0),
            "rows_without_cell_are_unknown_or_absent": sum(v for k, v in status.items() if k not in ("MEASURED", "CENSORED")),
            "cells_censored": int(df["censored"].sum()), "censored_share_of_cells_pct": pct(int(df["censored"].sum()), int(len(df))),
            "cells_y_equal_0": int((y == 0).sum()),
            "source_measured_zero_rows": sum(1 for r in rf if r.get("status") == "MEASURED" and r.get("value") == 0),
            "cells_y_equal_0_equal_source_measured_zero": int((y == 0).sum()) == sum(1 for r in rf if r.get("status") == "MEASURED" and r.get("value") == 0),
            "cells_y_lower_equal_0": int((yl == 0).sum()),
            "cells_missing_y_and_not_censored": int((y.isna() & ~df["censored"]).sum()),
            "cells_censored_with_y_filled": int((df["censored"] & y.notna()).sum()),
            "censor_kinds": counter_dict(Counter((r.get("censor") or {}).get("kind", "NO_CENSOR_OBJECT") for r in cens)),
            "censor_limits": counter_dict(Counter(str((r.get("censor") or {}).get("limit", "NO_LIMIT")) for r in cens)),
            "censored_rows_without_limit": sum(1 for r in cens if (r.get("censor") or {}).get("limit") is None),
            "tiers": counter_dict(Counter(e["tier"] for e in fam_rows)),
            "y_train_rows_equal_stated_bound": int(df["censored"].sum()), "y_train_nan": int(yt.isna().sum()),
            "y_train_equals_y_or_y_lower_everywhere": bool(((yt == y.where(~df["censored"], yl)) | (yt.isna() & y.where(~df["censored"], yl).isna())).all()),
        }
    tot = {k: sum(v[k] for v in out.values()) for k in ("active_rows", "cells", "cells_censored", "cells_y_equal_0", "source_measured_zero_rows", "cells_y_lower_equal_0",
                                                        "cells_missing_y_and_not_censored", "cells_censored_with_y_filled", "censored_rows_without_limit", "y_train_nan")}
    return {"record": "TRANSITION_NO_IMPUTATION_AUDIT_S178", "tool_version": TOOL_VERSION, "status": "AI_DRAFTED_PROPOSED", "contains_text": False,
            "contains_ids": False, "counts_as_human_gate": False, "by_source_family": out, "totals": tot,
            "violations": {"y_equal_0_cells_not_a_source_measured_zero": tot["cells_y_equal_0"] - tot["source_measured_zero_rows"], "y_lower_equal_0_cells": tot["cells_y_lower_equal_0"],
                           "missing_y_not_censored": tot["cells_missing_y_and_not_censored"], "censored_with_y_filled": tot["cells_censored_with_y_filled"],
                           "censored_rows_without_limit": tot["censored_rows_without_limit"], "y_train_nan": tot["y_train_nan"]},
            "reading": "0 in every violation field = no zero / mean / half-minimum value reached a real cell (a cell with y = 0 is counted as a violation unless the ledger row itself states MEASURED 0). Source-side imputation inside USDA R6 (SOURCE_SIDE_IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE) cannot be seen from the ledger. The only substitution is y_train: a censored cell (GT_CAP) enters training at its stated bound; "
                       "its share of each family's cells is censored_share_of_cells_pct and is the quantity the 29-diag cap-stratified rerun exists to expose."}


def run(out_dir: Path, root: Path = ROOT) -> dict:
    before = protected_hashes(root)
    d = build(root)
    assert before == protected_hashes(root)
    return {"json_sha256": write_new_or_same(out_dir / "transition_no_imputation_audit_v1.json", dumps(d)), "violations": d["violations"], "totals": d["totals"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)
    if a.selfcheck:
        with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
            r1, r2 = run(Path(t1)), run(Path(t2))
        print(dumps({"selfcheck": "IDENTICAL" if r1 == r2 else "DIFFERENT", "run1": r1}))
        return 0 if r1 == r2 else 1
    print(dumps(run(ROOT / a.out_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
