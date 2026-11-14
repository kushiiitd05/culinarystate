#!/usr/bin/env python
"""D-097 (T3-C11-R1, T3-C17-R2): Rung A structural types vs the P1-A and 40 dev gold recipes, per-type count match,
Wilson + recipe-cluster bootstrap. Mac only (gold folders are git-ignored; P1 is BBC, D-003). One counts-only JSON,
refuses to overwrite. Mapping/method/seed/sets are those fixed in DECISIONS D-097.

    /opt/anaconda3/bin/python tools/s179_d097_runga_type_table.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from culinarystate.evaluation import runga_typed_vs_gold as R  # noqa: E402

TOOL_VERSION = "s179-d097-runga-type-table-0.1.0"
OUT = ROOT / "reports" / "s179" / "d097_runga_type_table_2026-11-13.json"
OUT_V2 = ROOT / "reports" / "s179" / "d102_runga_type_table_v2_2026-11-13.json"
LABELS = ["DIAGNOSTIC", "NOT_INDEPENDENT", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--mapping", choices=("d097", "v2"), default="d097")
    a = ap.parse_args(argv)
    out = Path(a.out) if a.out else (OUT if a.mapping == "d097" else OUT_V2)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    import s179_compiler_vs_gold_pooled as pooled
    from culinarystate.annotation.gold import to_events
    from culinarystate.extraction.interfaces import SourceText
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.quantity.rc2_dryrun import load_schema
    from culinarystate.state_graph.engine import Add
    rung, schema = RungA(), load_schema()
    fam = None
    if a.mapping == "v2":
        fam = {}
        for line in (ROOT / "ledgers/data/PROC.jsonl").read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                fam[r["id"]] = r.get("family") or ""
    sets = {}
    for name, folder, pattern, basis in pooled.SETS:
        paths = sorted(folder.glob(pattern))
        if not paths:
            sys.exit(f"INPUT_MISSING: {name}")
        docs = pooled.load_docs(paths)
        per, unmapped = [], 0
        for i, d in enumerate(docs):
            g, p, u = R.recipe_counts(d, rung, schema, to_events=to_events, Add=Add, SourceText=SourceText, idx=i,
                                       proc_family=fam)
            per.append((g, p))
            unmapped += u
        t = R.type_table_from_counts(per, unmapped=unmapped)
        t |= {"label_basis": basis, "independent": False, "input_set_sha256": pooled.set_digest(paths)}
        sets[name] = t
        print(name, t["n_recipes"], "pooled P", t["pooled"]["precision"], "R", t["pooled"]["recall"],
              "unmapped", unmapped)
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    labels = LABELS if fam is None else [*LABELS, "POST_HOC_AMENDMENT"]
    rec = {"record": "D097_RUNGA_TYPED_VS_GOLD" if fam is None else "D102_RUNGA_TYPED_VS_GOLD_V2",
           "decision": "D-097" if fam is None else "D-102 (POST_HOC_AMENDMENT of D-097)", "items": ["T3-C11-R1", "T3-C17-R2"],
           "tool_version": TOOL_VERSION, "labels": labels, "approver": "ksh+prv (AI, D-085)", "git_commit": head,
           "run_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
           "mapping": ("D-097 structural (discards/consumes/produces arity); Transfer/Reserve/Recombine never predicted"
                       if fam is None else "D-102 v2: discards; PROC family TRANSFER->Transfer, RESERVATION->Reserve; else D-097"),
           "sets": sets,
           "limitations": ["No gold set is independent (D-017, D-060); P1-A is HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND.",
                           "Count match per type per recipe, not event alignment; a matched count is not a matched event.",
                           "Structural arity is a declared proxy for gold semantics, not Rung A accuracy.",
                           "First scored output under D-097; any change is a dated amendment with a new path."],
           "contains_ids": False, "contains_text": False, "scientific_gate_pass": False}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x") as f:
        f.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print("wrote", out.relative_to(ROOT), hashlib.sha256(out.read_bytes()).hexdigest()[:16])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
