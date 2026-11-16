#!/usr/bin/env python3
"""New frozen-D5 unit registry and leakage audit; no source questions or ledger writes.

The old registry remains a historical draft. D5 is a frozen evaluation set, not
a newly created train/test split. Recorded DIAG29/R1 manifests are cited without
pretending to reconstruct unavailable private sealed assignments.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BLOCKS = ("S1", "S2", "P1", "P2", "P3", "C", "U", "X")
FILES = {"S": "benchmark/d5/d5_benchmark_v1_D085_S.csv",
         "PC": "benchmark/d5/d5_benchmark_v1_D085_PC.csv",
         "UX": "benchmark/d5/d5_benchmark_v1_D085_UX.csv"}
UNIT_COLUMNS = ["qid", "block", "unit_kind", "unit_id", "source_family", "component_ids_json",
                "gold_evd_ids", "gold_graph_ids", "role", "label"]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def ids_hash(ids):
    return hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()


def ids(value):
    return sorted({x for x in str(value or "").split("|") if x})


def write_new(path, text):
    with Path(path).open("x", encoding="utf-8", newline="") as handle:
        handle.write(text)


def csv_text(rows, columns):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def build_units(rows):
    seen, units = set(), []
    for row in sorted(rows, key=lambda x: (x["block"], x["qid"])):
        qid, block = row["qid"], row["block"]
        if qid in seen:
            raise ValueError("duplicate question ID")
        seen.add(qid)
        if block not in BLOCKS:
            raise ValueError("unknown block")
        if block in ("S1", "S2"):
            unit = str(row.get("recipe_id") or "")
            if not unit:
                raise ValueError("missing recipe identifier")
            kind, components = "RECIPE", [unit]
        elif block in ("P1", "P2", "P3", "C"):
            components = [row.get("ingredient_id", ""), row.get("process_id", ""),
                          row.get("process_id_2", ""), "|".join(ids(row.get("target_svars")))]
            if not components[0] or not components[1] or not components[3]:
                raise ValueError("missing cell identifiers")
            if block == "C" and not components[2]:
                raise ValueError("comparison missing second process")
            kind, unit = "CELL", json.dumps(components, separators=(",", ":"))
        else:
            kind, unit, components = "QUESTION", qid, [qid]
        units.append({"qid": qid, "block": block, "unit_kind": kind, "unit_id": unit,
                      "source_family": row.get("source_family", ""),
                      "component_ids_json": json.dumps(components, separators=(",", ":")),
                      "gold_evd_ids": "|".join(sorted(set(ids(row.get("gold_evd_ids"))) |
                                                          set(ids(row.get("gold_evd_ids_2"))))),
                      "gold_graph_ids": "|".join(ids(row.get("gold_graph_edge_ids"))),
                      "role": "FROZEN_EVALUATION", "label": "NO_HUMAN_SIGNOFF_D085"})
    return units


def overlaps(by_block):
    names = sorted(by_block)
    return {f"{a}&{b}": len(by_block[a] & by_block[b])
            for j, a in enumerate(names) for b in names[j + 1:] if by_block[a] & by_block[b]}


def summarize(units):
    recipes = {b: {u["unit_id"] for u in units if u["block"] == b} for b in ("S1", "S2")}
    gold = {b: {i for u in units if u["block"] == b for i in ids(u["gold_evd_ids"])} for b in BLOCKS}
    return {"questions": len(units), "by_block": dict(sorted(Counter(u["block"] for u in units).items())),
            "recipe_overlap_between_blocks": overlaps(recipes), "gold_evd_overlap_between_blocks": overlaps(gold),
            "distinct_gold_evd_ids": len(set().union(*gold.values())),
            "unit_assignment_sha256": ids_hash(json.dumps([u["qid"], u["block"], u["unit_id"]],
                                                          separators=(",", ":")) for u in units),
            "source_family_counts_S": dict(sorted(Counter(u["source_family"] for u in units
                                                          if u["block"] in ("S1", "S2")).items())),
            "near_duplicate_control": "NOT_ESTABLISHED", "source_family_disjoint": False,
            "gold_independence": "AI_DRAFTED_GOLD_NOT_INDEPENDENT_HUMAN_GOLD"}


def load_legacy():
    path = ROOT / "tools/s178_leakage_audit_d5.py"
    spec = importlib.util.spec_from_file_location("_d5_frozen_leakage_adapter", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.S_DRAFT, module.PC_DRAFT = ROOT / FILES["S"], ROOT / FILES["PC"]
    return module


def leakage_audit():
    legacy, result = load_legacy(), {}
    sections = [("s_blocks", legacy.s_audit), ("ner", legacy.ner_audit), ("pc_blocks", legacy.pc_audit)]
    selected = set()
    for name, function in sections:
        try:
            if name == "s_blocks":
                selected = function(result)
            elif name == "ner":
                if not selected:
                    raise ValueError("recipe-overlap prerequisite unavailable")
                function(result, selected)
            else:
                function(result)
        except Exception as exc:
            # Do not serialize exception bodies: they can include source strings.
            result.setdefault("incomplete_sections", {})[name] = {"status": "NOT_RECOMPUTED",
                                                                  "exception_class": type(exc).__name__}
    return result


def historical_manifest(path, fields):
    data = json.loads((ROOT / path).read_text())
    return {"path": path, "sha256": sha(ROOT / path), "status": "RECORDED_PROVENANCE_NOT_REDERIVED",
            "recorded_fields": {key: data[key] for key in fields if key in data},
            "warning": "A hash of a historical result is not a fresh derivation of private unit assignments."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--units", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    for path in (args.registry, args.units, args.report):
        if path.exists():
            parser.error("refusing existing output")
    from culinarystate.evaluation.frozen_guard import require_real_inputs
    freeze_path = "registry/freezes/D5-BENCH-2026-11-10b.json"
    freeze = json.loads((ROOT / freeze_path).read_text())
    require_real_inputs(ROOT, freeze_path, list(freeze["files"]))
    started = datetime.now(timezone.utc).isoformat()
    rows = []
    for relative in FILES.values():
        with (ROOT / relative).open(newline="") as handle:
            rows += list(csv.DictReader(handle))
    units, registry = build_units(rows), []
    for block in BLOCKS:
        subset = [u for u in units if u["block"] == block]
        source = FILES["S" if block in ("S1", "S2") else "PC" if block in ("P1", "P2", "P3", "C") else "UX"]
        registry.append({"registry_id": f"D5-V2-{block}", "block": block, "questions": len(subset),
                         "unit_kind": subset[0]["unit_kind"], "question_ids_sha256": ids_hash(u["qid"] for u in subset),
                         "unit_ids_sha256": ids_hash(u["unit_id"] for u in subset), "source_path": source,
                         "source_sha256": sha(ROOT / source), "freeze_id": freeze["freeze_id"],
                         "seed_rule": "D5 S/PC drafts: d5-bench-2026-11-08; KEEP/DROP/rank review D-090; UX authored controls, no stochastic draw",
                         "status": "FROZEN_EVALUATION_AI_DELEGATED_D085", "label": "NO_HUMAN_SIGNOFF_D085"})
    report = {"record": "FROZEN_D5_SPLIT_REGISTRY_V2", "labels": ["AI_PRECHECKED", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"],
              "started_at_utc": started, "frozen_summary": summarize(units), "leakage": leakage_audit(),
              "historical": {
                  "diag29": historical_manifest("reports/step29/diag/diag_results_S179.json",
                                                ("snapshot_id", "seal_payload_sha256", "exclusions", "signoff", "status")),
                  "07A_R1": historical_manifest("reports/step07/07A_R1_packet_manifest.json",
                                                ("attempt", "n", "seed", "excluded_count", "excluded_set_sha256",
                                                 "sha256_packet_Kush", "sha256_packet_Parv", "audited_by_humans")),
                  "old_registry": {"path": "registry/split_registry_v1.csv", "sha256": sha(ROOT / "registry/split_registry_v1.csv"),
                                   "status": "HISTORICAL_DRAFT_NOT_REPLACED"}},
              "limits": ["D5 is an evaluation question set, not a new model train/test split.",
                         "Source-family stratification is not source-family-heldout evaluation.",
                         "Provisional identity groups do not certify absence of near duplicates.",
                         "DIAG29 actual S-5 is food-group-disjoint and S-6 study-disjoint; old draft registry retained its earlier naming.",
                         "Historical private-seal and 07.A assignments are not freshly rederived here.",
                         "07A-R1 remains NOT_RUN under D-085; no inter-rater result is supplied."]}
    input_paths = [freeze_path, *freeze["files"], "ledgers/data/COND.jsonl", "ledgers/data/PROC.jsonl",
                   "ledgers/recipe_base/gold_recipe_index_v1.parquet", "ledgers/recipe_identity/duplicate_group_members_v1.parquet",
                   "ledgers/recipe_identity/recipe_family_members_v1.parquet", "reports/step17/j4_inverted_interval_sample_manifest_S166.csv",
                   "benchmark/ner/splits/recipedb3_split_v1.json", "data/external/recipedb3_ner/Ingredient_Annotated_Dataset.csv",
                   "data/interim/retrieval/bm25_top100.json", "reports/del5/ladder_v2_qwen7b.jsonl", "ledgers/data/REC.jsonl"]
    report["input_sha256"] = {p: sha(ROOT / p) for p in sorted(set(input_paths)) if (ROOT / p).is_file()}
    report["code_sha256"] = {p: sha(ROOT / p) for p in ("tools/s179_frozen_split_registry.py", "tools/s178_leakage_audit_d5.py",
        "src/culinarystate/evaluation/leakage_audit_d5.py", "src/culinarystate/evaluation/split_registry.py",
        "src/culinarystate/transition/splits.py", "tools/export_retrieval_set.py")}
    write_new(args.registry, csv_text(registry, list(registry[0])))
    write_new(args.units, csv_text(units, UNIT_COLUMNS))
    report["output_sha256"] = {str(p): sha(p) for p in (args.registry, args.units)}
    report["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_new(args.report, json.dumps(report, indent=1, sort_keys=True) + "\n")
    print("Frozen D5 registry written:", len(units), "questions; historical sets remain recorded, not rederived.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
