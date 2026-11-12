#!/usr/bin/env python3
"""Fixed 50-recipe source/replay/router/packet/strict-display regression, not gold accuracy."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from fractions import Fraction
import hashlib
from itertools import chain
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
FAMILIES = ("A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT", "FOODCOM")
QUOTAS = {"A1_BBC_GOOD_FOOD": 13, "WIKIBOOKS": 13, "GUTENBERG_SEGMENT": 12, "FOODCOM": 12}
SEED = "s179-local-pipeline-regression-2026-11-12"
LABELS = ["ENGINEERING_REGRESSION_NOT_SCIENTIFIC_GOLD", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value):
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, Fraction):
        return {"rational": [value.numerator, value.denominator]}
    if isinstance(value, Enum):
        return canonical(value.value)
    if isinstance(value, dict):
        return {str(k): canonical(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [canonical(child) for child in value]
    if isinstance(value, (set, frozenset)):
        return sorted((canonical(child) for child in value), key=lambda v: json.dumps(v, sort_keys=True))
    return value


def digest(value):
    return hashlib.sha256(json.dumps(canonical(value), sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def source_hash(recipe):
    return digest({key: recipe.get(key) for key in ("recipe_id", "source_family", "title", "ingredient_lines", "steps")})


def rank(recipe, seed):
    return hashlib.sha256(f"{seed}|{recipe['source_family']}|{recipe['recipe_id']}".encode()).hexdigest()


def select_recipes(recipes, *, families=FAMILIES, per_family=QUOTAS, seed=SEED):
    quotas = {family: per_family[family] if isinstance(per_family, dict) else per_family for family in families}
    if any(quota < 1 for quota in quotas.values()):
        raise ValueError("positive per-family quota required")
    selected = {family: [] for family in families}
    for recipe in recipes:
        family = recipe["source_family"]
        if family not in selected or not any(str(step).strip() for step in recipe.get("steps", [])):
            continue
        key = rank(recipe, seed)
        bucket = selected[family]
        existing = next((row for _, row in bucket if row["recipe_id"] == recipe["recipe_id"]), None)
        if existing is not None:
            if source_hash(existing) != source_hash(recipe):
                raise ValueError("duplicate recipe identity has conflicting source fields")
            continue
        if len(bucket) < quotas[family] or key < bucket[-1][0]:
            bucket.append((key, recipe))
            bucket.sort(key=lambda pair: (pair[0], pair[1]["recipe_id"]))
            del bucket[quotas[family]:]
    if any(len(bucket) != quotas[family] for family, bucket in selected.items()):
        raise ValueError("not enough instruction-bearing recipes in every declared source family")
    return [recipe for family in families for _, recipe in selected[family]]


def all_recipes():
    from culinarystate.recipes import corpus
    return chain(corpus.iter_rec_corpora(), corpus.iter_foodcom(), corpus.iter_tasteset())


def corpus_paths():
    from culinarystate.recipes import corpus
    return [corpus.A1_DIR / "recipes_processed.jsonl", ROOT / "data/interim/wikibooks/recipes.jsonl",
            ROOT / "data/interim/gutenberg/recipes.jsonl", corpus.FOODCOM, corpus.TASTESET,
            ROOT / "ledgers/data/REC.jsonl"]


def run_case(recipe, context):
    from culinarystate.extraction.interfaces import SourceText
    from culinarystate.state_graph.event_adapter import adapt_event_graph
    from culinarystate.mechanism import router_demo
    from culinarystate.decision.pipeline import answer
    raw = "\n".join(recipe.get("steps") or [])
    source = SourceText.from_raw(recipe["recipe_id"], raw)
    parsed = context.rung.run(source, context.rung.config(), schema=context.schema)
    adapted = adapt_event_graph(source, parsed.graph, groundings=parsed.quantities,
                                recomputers=context.rung.recomputers())
    replay = adapted.replay()
    routed = router_demo.route_text(raw, index=context.index, target_svar="SVAR-000009", rung=context.rung,
                                    hierarchy=context.hierarchy, schema=context.schema, gates=context.gates,
                                    ingredient_lines=recipe.get("ingredient_lines"))
    linked = next((item for item in routed["items"] if item["ingredient_id"] and item["process_id"]), None)
    if linked:
        food = context.lex.ing_names.get(linked["ingredient_id"], "food")
        names = [name for name, pid in context.lex.proc_ids.items() if pid == linked["process_id"]]
        process = min(names, key=lambda name: (len(name), name)) if names else "cooking"
        query = f"How much vitamin C remains in {food} after {process}?"
    else:
        query = "How much vitamin C remains in food after cooking?"
    pipeline = answer(query, context.lex, context.retriever, context.req, context.family,
                      support_index=context.sup, troubleshoot=context.ts)
    valid = {row["id"] for row in context.retriever.evd}
    hits = [hit for packet in pipeline["packets"].values() for hit in [*packet.direct, *packet.near]]
    invalid = sum(hit.evd_id not in valid or hit.row.get("id") != hit.evd_id for hit in hits)
    final = context.respond(query, recipe_text=raw)
    detail = final.get("detail") or {}
    physics = ((detail.get("recipe") or {}).get("physics") or {})
    return {"recipe_id": recipe["recipe_id"], "source_family": recipe["source_family"],
            "adapter_source_fields_sha256": source_hash(recipe), "instruction_text_sha256": source.sha256,
            "query_sha256": hashlib.sha256(query.encode()).hexdigest(),
            "query_origin": "FIRST_LINKED_ROUTED_PAIR" if linked else "UNLINKED_FALLBACK_NO_RECIPE_CLAIM",
            "parse_events": len(parsed.graph.events), "parse_mentions": len(parsed.mentions.mentions),
            "parse_sha256": digest(parsed), "engine_events": len(adapted.events),
            "adapter_invented_count": adapted.invented_count,
            "adapter_issue_codes": dict(Counter(issue.code for issue in adapted.issues)),
            "engine_log_sha256": hashlib.sha256(adapted.log().to_jsonl().encode()).hexdigest(),
            "replay_sha256": hashlib.sha256(replay.to_jsonl().encode()).hexdigest(),
            "replay_snapshot_sha256": replay.snapshot_sha256, "replay_status": replay.status,
            "replay_issue_codes": dict(Counter(issue.code for issue in replay.issues)),
            "replay_unknown_codes": dict(Counter(issue.code for issue in replay.unknown)),
            "route_items": len(routed["items"]), "route_sha256": digest(routed),
            "routes": dict(Counter(item["route"] for item in routed["items"])),
            "packet_count": len(pipeline["packets"]), "packet_hits": len(hits), "invalid_packet_refs": invalid,
            "packet_sha256": digest({name: packet.summary() for name, packet in pipeline["packets"].items()}),
            "final_mode": final["mode"], "display_sha256": digest(final),
            "table_retention_numbers": len(detail.get("numeric_provenance") or []),
            "physics_steps": len(physics.get("steps") or []),
            "physical_provenance_complete": physics.get("numeric_provenance_complete"),
            "handler_errors": int(final["mode"] == "ABSTAIN_ERROR"), "citable": final.get("citable"),
            "emission_policy": final.get("emission_policy")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["select", "run"])
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args(argv)
    started = datetime.now(timezone.utc).isoformat()
    if args.action == "select":
        if args.manifest.exists():
            parser.error("refusing to replace preregistered engineering selection")
        selected = select_recipes(all_recipes())
        manifest = {"record": "FIXED_50_PIPELINE_ENGINEERING_SELECTION", "labels": LABELS,
                    "seed": SEED, "per_family": QUOTAS, "target_svar": "SVAR-000009", "n_recipes": 50,
                    "excluded_family_channels": {"TASTESET": "INGREDIENT_ONLY_ADAPTER_HAS_NO_INSTRUCTIONS"},
                    "preselection_design_note": "Initial five-family quota check refused before outcomes; TASTEset exposes no instruction channel. Four instruction-bearing families allocated13/13/12/12 before pipeline execution.",
                    "selection_rule": "SMALLEST_SHA256_SEED_FAMILY_RECIPE_ID;NONEMPTY_INSTRUCTIONS;NO_OUTCOME_FILTER",
                    "selection_tool_sha256": sha(__file__),
                    "hash_scope": "ADAPTER_IDENTITY_TITLE_INGREDIENT_LINE_AND_STEP_FIELDS_NOT_ORIGINAL_FILE_BYTES",
                    "input_sha256": {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p) for p in corpus_paths()},
                    "units": [{"recipe_id": row["recipe_id"], "source_family": row["source_family"],
                               "selection_rank_sha256": rank(row, SEED), "adapter_source_fields_sha256": source_hash(row)} for row in selected],
                    "started_at_utc": started, "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                    "scientific_gate_pass": False}
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        with args.manifest.open("x") as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print("Selected 50 recipes before pipeline outcomes; source IDs/hashes only")
        return 0
    if args.out is None or args.out.exists():
        parser.error("new --out required")
    manifest = json.loads(args.manifest.read_text())
    if manifest["seed"] != SEED or manifest["n_recipes"] != 50 or len(manifest["units"]) != 50:
        parser.error("unexpected selection manifest")
    for path, expected in manifest["input_sha256"].items():
        if sha(ROOT / path) != expected:
            parser.error("corpus input changed since selection")
    wanted = {(row["source_family"], row["recipe_id"]): row for row in manifest["units"]}
    if len(wanted) != 50 or Counter(row["source_family"] for row in manifest["units"]) != Counter(QUOTAS):
        parser.error("manifest must have 50 unique identities and the declared balanced family quotas")
    recipes = {(row["source_family"], row["recipe_id"]): row for row in all_recipes()
               if (row["source_family"], row["recipe_id"]) in wanted}
    if recipes.keys() != wanted.keys():
        parser.error("selected source records missing")
    for key, row in recipes.items():
        if source_hash(row) != wanted[key]["adapter_source_fields_sha256"]:
            parser.error("selected source fields changed")
    from culinarystate.decision.demo_context_v3 import StrictDemoContext
    context = StrictDemoContext.load(public=False, host="127.0.0.1")
    code = sorted(ROOT.glob("src/**/*.py")) + [Path(__file__).resolve()]
    hashes = {str(path.relative_to(ROOT)): sha(path) for path in code}
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    cases = [run_case(recipes[key], context) for key in wanted]
    core_hash = digest(cases)
    stable = hashes == {path: sha(ROOT / path) for path in hashes}
    stable = stable and head == subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if not stable:
        raise RuntimeError("code/commit changed during pipeline regression")
    baseline = json.loads(args.baseline.read_text()) if args.baseline else None
    if baseline and (baseline["core_sha256"] != core_hash or baseline["manifest_sha256"] != sha(args.manifest)):
        raise RuntimeError("fixed engineering golden-output hashes differ; inspect without rewriting baseline")
    report = {"record": "FIXED_50_END_TO_END_ENGINEERING_REGRESSION", "labels": LABELS,
              "base_commit": head, "started_at_utc": started, "completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "manifest_path": str(args.manifest), "manifest_sha256": sha(args.manifest), "code_sha256": hashes,
              "code_unchanged_during_run": stable, "cases": cases, "n_recipes": len(cases), "core_sha256": core_hash,
              "second_run_matches_baseline": True if baseline else None,
              "baseline_sha256": sha(args.baseline) if baseline else None,
              "totals": {field: sum(row[field] for row in cases) for field in ["parse_events", "engine_events", "adapter_invented_count",
                         "route_items", "packet_count", "packet_hits", "invalid_packet_refs", "handler_errors", "table_retention_numbers", "physics_steps"]},
              "families": dict(Counter(row["source_family"] for row in cases)),
              "final_modes": dict(Counter(row["final_mode"] for row in cases)),
              "replay_statuses": dict(Counter(row["replay_status"] for row in cases)), "scientific_gate_pass": False,
              "limitations": ["Engineering golden outputs only; not human annotations, accuracy, independent validation or scientific gold.",
                              "Selection fixed before pipeline outcomes; no recipe dropped for failures or unknowns.",
                              "Parser feeds adapter/replay; router reparses the same source with RungA. Replay snapshot is not a retriever input API.",
                              "Query uses first linked route pair; packet and strict response run on that metadata query with the original instruction text.",
                              "Exact condition context not inferred; zero numeric retention output is conservative coverage, not answer quality.",
                              "Known source/rule/replay unknowns and issues retained; hashes do not prove scientific correctness."]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"core_sha256": core_hash, "totals": report["totals"], "final_modes": report["final_modes"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
