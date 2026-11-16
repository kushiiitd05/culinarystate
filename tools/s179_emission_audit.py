#!/usr/bin/env python3
"""Read-only audit of saved D5 answers plus sampled public demo calls. No rescoring.

Questions use EVD metadata, not private recipe text. Every fifth call includes an
explicitly synthetic recipe to exercise physics. Findings are counts/IDs/hashes;
the tool never stores answers, queries, recipe text or private source excerpts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evaluation.emission_audit import audit_text, audit_payload  # noqa: E402

CODE = ("tools/s179_emission_audit.py", "src/culinarystate/evaluation/emission_audit.py")
NO_NUMBERS = {"QUALITATIVE", "REPORT_CONFLICT", "ABSTAIN"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sample_cases(rows, *, n, seed, recipe_every):
    if n <= 0 or recipe_every <= 0:
        raise ValueError("positive session count and recipe cadence required")
    pool = [r for r in sorted(rows, key=lambda r: r["id"]) if r.get("status") == "ACTIVE"
            and all(r.get(k, {}).get("raw_name") for k in ("matrix", "process", "target"))]
    if not pool:
        raise ValueError("no metadata-bearing ACTIVE EVD rows")
    rng, cases = random.Random(seed), []
    for i in range(n):
        row = rng.choice(pool)
        food, process, target = (row[k]["raw_name"] for k in ("matrix", "process", "target"))
        recipe = f"Boil {food} in water at 90 C for 5 minutes." if i % recipe_every == 0 else None
        cases.append({"case_id": f"AUDIT-{seed}-{i:04d}", "source_evd_id": row["id"],
                      "query": f"How much {target} remains in {food} after {process}?",
                      "recipe_text": recipe,
                      "recipe_origin": "SYNTHETIC_CALLER_INPUT" if recipe else "NONE"})
    return cases


def cap(decision):
    if str(decision.get("mode", "")).startswith("ABSTAIN") or decision.get("mode") == "ASK":
        return True
    if decision.get("precision") in NO_NUMBERS:
        return True
    per = list((decision.get("per_option") or {}).values())
    return bool(per) and all((p or {}).get("precision") in NO_NUMBERS for p in per)


def audit_record(record, evd, *, demo=False):
    detail = record.get("detail") or {}
    decision = {"mode": record.get("mode"), "precision": detail.get("precision")} if demo else record.get("decision", {})
    packet = record.get("packet_ids")
    if demo and detail.get("evidence"):
        evidence = detail["evidence"]
        packet = evidence.get("evd_ids_asked_food", []) + evidence.get("evd_ids_other", [])
    audit = audit_text(record.get("answer", ""), evd,
                       packet_ids=set(packet) if packet is not None else None, no_numbers=cap(decision))
    audit["structural_issues"] = audit_payload(record)
    if demo and (record.get("citable") is not False or "NON_CITABLE" not in record.get("labels", [])):
        audit["structural_issues"]["DEMO_CITABILITY_LABEL_ABSENT"] = 1
    return audit


def aggregate(audits):
    out = {k: Counter() for k in ("issues", "gaps", "counts", "structural_issues")}
    for audit in audits:
        for key in out:
            out[key].update(audit[key])
    return {"n_records": len(audits), "records_with_issues": sum(bool(a["issues"] or a["structural_issues"]) for a in audits),
            "records_with_gaps": sum(bool(a["gaps"]) for a in audits),
            "aligned_retention_numbers": sum(a["aligned_retention_numbers"] for a in audits),
            **{k: dict(sorted(v.items())) for k, v in out.items()}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--recipe-every", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error("refusing to overwrite an audit")
    from culinarystate.evaluation.frozen_guard import require_real_inputs
    from culinarystate.ledgers.store import LedgerStore
    from culinarystate.decision.demo_context import DemoContext
    freeze = "registry/freezes/D5-BENCH-2026-11-10b.json"
    frozen = json.loads((ROOT / freeze).read_text())
    require_real_inputs(ROOT, freeze, list(frozen["files"]))
    started = datetime.now(timezone.utc).isoformat()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    code_files = sorted(set(CODE) | {p.as_posix() for p in Path("src").rglob("*.py")})
    code_hashes = {p: sha(ROOT / p) for p in code_files}
    rows = [r for r in LedgerStore().all_latest("EVD") if r["status"] == "ACTIVE"]
    evd = {r["id"]: r for r in rows}
    runs_path = ROOT / "reports/del5/d5_runs_v1_D085.jsonl"
    runs = [json.loads(line) for line in runs_path.read_text().splitlines() if line.strip()]
    saved, by_rung = [], defaultdict(list)
    for record in runs:
        audit = audit_record(record, evd)
        saved.append({"qid": record["qid"], "rung": record["rung"], **audit})
        by_rung[record["rung"]].append(audit)
    cases = sample_cases(rows, n=args.sessions, seed=args.seed, recipe_every=args.recipe_every)
    ctx, demo, modes, branches = DemoContext.load(public=True), [], Counter(), Counter()
    physics_steps = recipe_responses = 0
    for i, case in enumerate(cases):
        answer = ctx.respond(case["query"], recipe_text=case["recipe_text"])
        audit = audit_record(answer, evd, demo=True)
        recipe = (answer.get("detail") or {}).get("recipe") or {}
        physics = (recipe.get("physics") or {}).get("steps") or []
        physics_steps += len(physics)
        recipe_responses += bool(recipe)
        modes[answer["mode"]] += 1
        branches[answer.get("route", {}).get("branch", "UNKNOWN")] += 1
        demo.append({"case_id": case["case_id"], "source_evd_id": case["source_evd_id"],
                     "query_sha256": hashlib.sha256(case["query"].encode()).hexdigest(),
                     "recipe_origin": case["recipe_origin"], "physics_steps": len(physics), **audit})
        if (i + 1) % 100 == 0:
            print(f"Audited {i + 1}/{len(cases)} demo calls", flush=True)
    stable = code_hashes == {p: sha(ROOT / p) for p in code_files}
    stable = stable and head == subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if not stable:
        raise RuntimeError("code changed during audit; output refused")
    if sha(ROOT / "ledgers/data/EVD.jsonl") != frozen["files"]["ledgers/data/EVD.jsonl"]:
        raise RuntimeError("EVD changed during audit; output refused")
    report = {"record": "READ_ONLY_EMISSION_AUDIT", "labels": ["ENGINEERING_DIAGNOSTIC", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"],
              "base_commit": head, "started_at_utc": started, "completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "code_sha256": code_hashes, "code_unchanged_during_run": stable,
              "input_sha256": {"reports/del5/d5_runs_v1_D085.jsonl": sha(runs_path), "ledgers/data/EVD.jsonl": sha(ROOT / "ledgers/data/EVD.jsonl")},
              "sampling": {"seed": args.seed, "sessions": len(cases), "rule": "ACTIVE_EVD_METADATA_WITH_REPLACEMENT",
                           "recipe_every": args.recipe_every, "synthetic_recipe_requests": sum(c["recipe_text"] is not None for c in cases),
                           "recipe_responses": recipe_responses, "physics_steps": physics_steps,
                           "unique_query_hashes": len({r["query_sha256"] for r in demo}), "modes": dict(modes), "branches": dict(branches)},
              "saved_D5": aggregate(saved), "saved_D5_by_rung": {k: aggregate(v) for k, v in sorted(by_rung.items())},
              "demo": aggregate(demo), "saved_records": saved, "demo_records": demo,
              "acceptance": "PARTIAL_LEXICAL_AND_STRUCTURAL_AUDIT_ONLY", "scientific_gate_pass": False,
              "limitations": ["Not a source-entailment, food/process/target/condition applicability or scientific-validity audit.",
                              "Numeric types not covered remain review gaps; count and corpus scores classified separately.",
                              "EVD point matching does not establish conditional applicability; censor limits are not measured points.",
                              "Metadata-template calls are not a sample of natural user queries or real recipes.",
                              "Synthetic recipe inputs exercise code only and supply no scientific measurements.",
                              "Structural scans only see serialized fields; omitted basis/model provenance cannot be certified.",
                              "No rescoring, retuning, model call, threshold amendment or frozen-output change."]}
    with args.out.open("x") as handle:
        handle.write(json.dumps(report, sort_keys=True, allow_nan=False) + "\n")
    print("Audit written; acceptance remains PARTIAL; no scientific gate pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
