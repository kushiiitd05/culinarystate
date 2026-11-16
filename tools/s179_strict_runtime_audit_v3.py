#!/usr/bin/env python3
"""Counts-only strict-demo engineering audit; never changes frozen scientific results."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def leaves(value, path):
    if isinstance(value, (list, tuple)):
        for i, child in enumerate(value):
            yield from leaves(child, f"{path}.{i}")
    elif value is not None:
        yield path


def inspect_payload(payload):
    detail = payload.get("detail") or {}
    physics = ((detail.get("recipe") or {}).get("physics") or {})
    result = Counter(numeric_fields=0, missing_numeric_provenance=0, unknown_numeric_fields=0,
                     handler_errors=int(payload["mode"] == "ABSTAIN_ERROR"),
                     unexpected_simulate=int("SIMULATE" in payload["mode"]),
                     citability_violations=int(payload.get("citable") is not False or "NON_CITABLE" not in payload.get("labels", [])),
                     table_numbers=len(detail.get("numeric_provenance") or []), physics_steps=len(physics.get("steps") or []))
    for step in physics.get("steps") or []:
        paths = []
        for prefix, fields in (("stated", ("duration_min", "temperature_c")),
                               ("scenario", ("typical_bath_c", "typical_duration_min", "typical_core_end_c", "range_core_end_c"))):
            for field in fields:
                paths.extend(leaves((step.get(prefix) or {}).get(field), f"{prefix}.{field}"))
        for path in paths:
            result["numeric_fields"] += 1
            metadata = (step.get("numeric_provenance") or {}).get(path)
            if not metadata:
                result["missing_numeric_provenance"] += 1
            elif metadata.get("basis") in (None, "UNKNOWN") or metadata.get("status") in (None, "UNKNOWN"):
                result["unknown_numeric_fields"] += 1
    result['display_numbers'] = 0
    result['display_provenance_violations'] = 0
    for step in (detail.get('recipe_display') or {}).get('steps') or []:
        for number in (step.get('physics') or {}).get('numbers') or []:
            result['display_numbers'] += 1
            value = number.get('value')
            good = (type(value) in (int, float) and math.isfinite(value)
                    and number.get('basis') not in (None, 'UNKNOWN')
                    and number.get('status') not in (None, 'UNKNOWN')
                    and bool(number.get('unit')))
            result['display_provenance_violations'] += not good
    return dict(result)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sessions", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=17912)
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error("refusing to overwrite an audit")
    from culinarystate.decision.demo_context_v3 import StrictDemoContext
    from culinarystate.ledgers.store import LedgerStore
    from s179_emission_audit import sample_cases
    started = datetime.now(timezone.utc).isoformat()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    paths = sorted(ROOT.glob("src/**/*.py")) + [ROOT / "src/culinarystate/app/static/strict_v3.html", Path(__file__).resolve()]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    rows = LedgerStore().all_latest("EVD")
    cases = sample_cases(rows, n=args.sessions, seed=args.seed, recipe_every=5)
    ctx = StrictDemoContext.load(public=True, host="127.0.0.1")
    totals, modes, branches, records = Counter(), Counter(), Counter(), []
    for i, case in enumerate(cases):
        payload = ctx.respond(case["query"], recipe_text=case["recipe_text"])
        counts = inspect_payload(payload)
        totals.update(counts)
        modes[payload["mode"]] += 1
        branches[payload["route"]["branch"]] += 1
        records.append({"case_id": case["case_id"], "source_evd_id": case["source_evd_id"],
                        "query_sha256": hashlib.sha256(case["query"].encode()).hexdigest(), **counts})
        if (i + 1) % 100 == 0:
            print(f"Strict-v3 audit {i + 1}/{len(cases)}", flush=True)
    if hashes != {p: sha(ROOT / p) for p in hashes}:
        raise RuntimeError("source changed during audit")
    report = {"record": "STRICT_V3_LOCAL_ENGINEERING_AUDIT", "labels": ["NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"],
              "started_at_utc": started, "completed_at_utc": datetime.now(timezone.utc).isoformat(), "base_commit": head,
              "code_sha256": hashes, "code_unchanged_during_run": True,
              "input_sha256": {p: sha(ROOT / p) for p in ("ledgers/data/EVD.jsonl", "ledgers/data/COND.jsonl")},
              "sampling": {"sessions": len(cases), "seed": args.seed, "synthetic_recipe_requests": sum(bool(c["recipe_text"]) for c in cases),
                           "rule": "ACTIVE_EVD_METADATA_WITH_REPLACEMENT", "modes": dict(modes), "branches": dict(branches)},
              "counts": dict(totals), "records": records, "scientific_gate_pass": False,
              "limitations": ["Post-hoc engineering diagnostic; not a rerun or repair of D5 H1/H3.",
                              "No explicit condition context is inferred; default numeric abstention reduces coverage.",
                              "Metadata queries and synthetic recipes are not natural-query or real-recipe validation.",
                              "Provenance is declared-source metadata, not source truth, applicability or scientific accuracy.",
                              "V3 recipe chips label source-row existence only; no applicability certificate. Display provenance is checked independently.",
                              "Only the listed numeric display fields are independently enumerated; registry IDs and counts are metadata."]}
    with args.out.open("x") as handle:
        handle.write(json.dumps(report, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"counts": dict(totals), "modes": dict(modes)}, sort_keys=True))


if __name__ == "__main__":
    main()
