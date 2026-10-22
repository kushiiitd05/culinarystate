#!/usr/bin/env python3
"""STEP 07I part 7: final recipe database statistics package + ledger/graph impact matrix. -> reports/step07i/final_recipe_database_statistics.{json,md}, reports/step07i/ledger_graph_impact_matrix.csv"""
import csv
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
R, ID, RS, RB = ROOT / "reports/step07i", ROOT / "ledgers/recipe_identity", ROOT / "ledgers/recipe_semantics", ROOT / "ledgers/recipe_base"
J = lambda p: json.loads(Path(p).read_text())
rows_of = lambda p: pq.ParquetFile(p).metadata.num_rows if Path(p).exists() else 0
jl = lambda p: sum(1 for _ in open(p, encoding="utf-8")) if Path(p).exists() else 0


def condition_stats():
    c = pq.read_table(RS / "recipe_condition_mentions_v1.parquet", columns=["source_family", "expression_family", "normalized_status", "raw_expression", "measurement_location"]).to_pandas()
    pat = lambda s: s.str.lower().str.replace(r"\d+(?:[.,]\d+)?", "#", regex=True).str.strip()
    out = {"condition_mentions": len(c), "by_family_status": {f: g.normalized_status.value_counts().to_dict() for f, g in c.groupby("expression_family")},
           "temperature_location": c[c.expression_family == "TEMPERATURE"].measurement_location.value_counts(dropna=False).to_dict(), "top_temporal_patterns": pat(c[c.expression_family == "TIME"].raw_expression).value_counts().head(15).to_dict(),
           "top_endpoint_openers": c[c.expression_family == "ENDPOINT"].raw_expression.str.lower().str.split().str[:3].str.join(" ").value_counts().head(15).to_dict(), "medium_values": c[c.expression_family == "MEDIUM"].raw_expression.str.lower().str.strip().value_counts().head(12).to_dict(),
           "by_source": {s: g.expression_family.value_counts().to_dict() for s, g in c.groupby("source_family")}}
    return out


def main():
    base = pq.read_table(RB / "recipe_base_v1.parquet").to_pandas()
    base = base.merge(pd.read_parquet(ID / "recipe_identity_fk_v1.parquet"), on="recipe_id", how="left", validate="1:1")  # frozen base + identity FK join table
    cn, idn, cs, au = J(R / "census_notes.json"), J(R / "_identity_summary.json"), J(R / "_consensus_summary.json"), J(R / "_audits.json")
    dg = pd.read_parquet(ID / "duplicate_group_members_v1.parquet", columns=["duplicate_group_id", "duplicate_relation", "group_size", "group_cross_source"])
    multi = dg[dg.group_size > 1].drop_duplicates("duplicate_group_id")
    rel = dg[dg.duplicate_relation.isin(["EXACT_BINARY_COPY", "EXACT_NORMALIZED_COPY", "MIRRORED_COPY"])].duplicate_relation.value_counts().to_dict()
    pairs = pd.read_parquet(ID / "candidate_pairs_v1.parquet", columns=["relation_status", "score", "family_edge", "cross_source_family"])
    reg = pd.read_parquet(ID / "recipe_family_registry_v1.parquet")
    usage = pd.read_csv(ROOT / "registry/recipe_source_usage_registry_v1.csv")
    v = cs["views"]
    counts = {"RAW_SOURCE_RECIPES": len(base), "LOCAL_ANALYSIS_ELIGIBLE": v["in_LOCAL_ANALYSIS"], "RELEASE_ELIGIBLE_strict(raw_redistribution=YES)": v["in_RELEASE_ELIGIBLE"], "RELEASE_CONDITIONAL(attribution/share-alike, needs H2)": v["in_RELEASE_CONDITIONAL"],
              "EXACT_DUPLICATE_GROUPS(>=2 members)": int(len(multi)), "RECORDS_IN_EXACT_DUPLICATE_GROUPS": int((dg.group_size > 1).sum()), "EXACT_DEDUP_LOGICAL_RECIPES": v["in_EXACT_DEDUP"], "HIGH_CONFIDENCE_NEAR_DUPLICATE_GROUPS": 0,
              "NEAR_DUPLICATE_CANDIDATE_PAIRS_STORED": int((pairs.relation_status == "CANDIDATE_NEAR_DUPLICATE").sum()), "RECIPE_FAMILIES_PROVISIONAL": int(len(reg)), "MULTI_GROUP_FAMILIES": cs["multi_group_families"], "DISH_FAMILY_CANDIDATES": idn["dish_family_candidates"],
              "MODEL_ELIGIBLE(training_allowed=YES)": v["in_MODEL_ELIGIBLE"], "GOLD_PENDING": v["in_GOLD"], "GOLD_CANDIDATES_NOT_ANNOTATED": 10}
    out = {"counts": counts, "SOURCE": base.source_family.value_counts().to_dict(), "LICENCE_USAGE": {"registry_rows": len(usage), "recipes_by_usage_class": base.usage_class.value_counts().to_dict(), "training_allowed": base.training_allowed.value_counts().to_dict(),
                                                                                               "raw_redistribution_allowed": base.raw_redistribution_allowed.value_counts().to_dict(), "h2_items": ["Food.com SRC registration + licence", "TASTEset SRC registration + licence", "A1/BBC training/redistribution", "Wikibooks share-alike training/release"]},
           "DUPLICATION": {"exact_relation_member_counts": rel, "exact_group_stats": idn["exact_stats"], "cross_source_exact_groups": int(multi.group_cross_source.sum()), "candidate_retrieval_diagnostics": idn["diagnostics"],
                           "human_benchmark": "none exists; blind ~400-pair calibration packet created UNLABELED; near-duplicates are NOT auto-coalesced", "legacy_signal": "REC family_id + 7 A1 near-duplicate pairs (word-5-shingle Jaccard>=0.8)"},
           "RECIPE_FAMILY": {"method": "PROVISIONAL_STAR_V1 (pre-registered, uncalibrated)", "families": len(reg), "multi_recipe_families": cs["multi_member_families_over_recipes"], "multi_group_families": cs["multi_group_families"], "heterogeneous": cs["heterogeneous_families"], "families_with_conflicts": cs["families_with_conflicts"],
                             "family_size_distribution_recipes": reg.n_recipes.value_counts().sort_index().head(12).to_dict(), "largest": reg.sort_values("n_recipes", ascending=False).head(5)[["recipe_family_id", "n_recipes"]].values.tolist()},
           "CULTURE_REGION_HISTORY": au["bias"], "INGREDIENTS_ALIASES": au["ingredients"], "QUANTITIES_UNITS": au["quantities"], "PROCESSES_HIERARCHY": au["processes"], "TOOLS_UTENSILS_MACHINES": au["tools"], "TOOL_REVIEW_ESTIMATE": au["tool_review_queue_estimate"],
           "CONDITIONS_TEMPORAL_ENDPOINTS": {"recipe_level_pct": au["conditions_recipe_level_pct"], "family_level_pct": au["conditions_family_level_pct"], "mentions": condition_stats()}, "SIMULATION_READINESS": {"recipe": au["readiness_recipe_level"], "family": au["readiness_family_level"], "extras": au["family_readiness_extras"]},
           "GOLD_SILVER_RAW": base.quality_tier.value_counts().to_dict(), "GOLD_FIREWALL": cs["gold_firewall"], "MISSINGNESS": {s: {c: round(1 - float(g[c].mean()), 4) for c in ("has_ingredients", "has_quantities", "has_instructions", "has_conditions")} for s, g in base.groupby("source_family")},
           "UNMAPPED_TERMS": {"ingredients": "reports/step07i/high_priority_unmapped_ingredients.csv", "processes": "reports/step07i/high_frequency_unmapped_processes.csv", "tools": "reports/step07i/tool_review_queue.csv"},
           "CONFLICTS": {"families_with_conflicting_condition_fields": cs["families_with_conflicts"]}, "DATA_QUALITY": "validators + deterministic rebuild reported in reports/step07i/step07i_gate_result.json", "VIEWS": v}
    (R / "final_recipe_database_statistics.json").write_text(json.dumps(out, indent=1, default=str))
    L = ["# Final recipe database statistics (STEP 07I)", "", "Provisional, uncalibrated identity layer. Source memory is untouched; counts below are FINDINGS, not targets.", "", "## Counts", "", "| measure | value |", "|---|---|"]
    L += [f"| {k} | {val:,} |" for k, val in counts.items()]
    for sec in ("SOURCE", "LICENCE_USAGE", "DUPLICATION", "RECIPE_FAMILY", "GOLD_SILVER_RAW", "GOLD_FIREWALL", "SIMULATION_READINESS", "MISSINGNESS", "CONFLICTS"):
        L += ["", f"## {sec}", "", "```json", json.dumps(out[sec], indent=1, default=str)[:2500], "```"]
    for sec in ("CULTURE_REGION_HISTORY", "INGREDIENTS_ALIASES", "QUANTITIES_UNITS", "PROCESSES_HIERARCHY", "TOOLS_UTENSILS_MACHINES", "CONDITIONS_TEMPORAL_ENDPOINTS"):
        L += ["", f"## {sec}", "", "```json", json.dumps(out[sec], indent=1, default=str)[:3500], "```"]
    L += ["", "## UNMAPPED TERMS / DATA QUALITY", "", "See the three review-queue CSVs in this folder and the gate result."]
    (R / "final_recipe_database_statistics.md").write_text("\n".join(L) + "\n")
    # ledger/graph impact matrix
    M = [("REC", "ledgers/data/REC.jsonl", "UNCHANGED_CANONICAL", "immutable source memory"), ("SRC", "ledgers/data/SRC.jsonl", "UNCHANGED_CANONICAL", "Food.com/TASTEset remain UNREGISTERED:* (H2); usage classes in recipe_source_usage_registry_v1"), ("DATASET", "ledgers/data/DATASET.jsonl", "UNCHANGED_CANONICAL", "5 rows from 07H-R"),
         ("FAM", "ledgers/recipe_identity/recipe_family_members_v1.parquet", "FAMILY_AGGREGATE_CREATED", "recipe_family_registry/members/consensus/field_support built; legacy family ids kept as legacy_family_id"),
         ("recipe_base", "ledgers/recipe_base/recipe_base_v1.parquet", "FOREIGN_KEY_UPDATE", "duplicate_group_id, recipe_family_id, dish_family_candidate_id, representative_recipe_id, family_role, duplicate_relation, usage columns added"),
         ("ING", "ledgers/data/ING.jsonl", "VALIDATED_ONLY", "no ING auto-created from unmapped strings; queue CSV only"), ("ALIAS", "ledgers/data/ALIAS.jsonl", "VALIDATED_ONLY", "used read-only"), ("PROC", "ledgers/data/PROC.jsonl", "VALIDATED_ONLY", "used read-only; unmapped queue CSV"),
         ("TOOL", "ledgers/data/TOOL.jsonl", "VALIDATED_ONLY", "structural class map registry + recipe_tool_mentions_v1 (derived)"), ("UNIT", "ledgers/data/UNIT.jsonl", "VALIDATED_ONLY", "unit coverage audited"), ("QTY", "ledgers/data/QNT.jsonl", "BLOCKED_FUTURE_STEP", "CQPO programme; recipe_quantity_mentions_v1 is the syntax-level derived layer"),
         ("POR", "ledgers/data/POR.jsonl", "BLOCKED_FUTURE_STEP", "no portion/density evidence created"), ("COND", "ledgers/data/COND.jsonl", "UNCHANGED_CANONICAL", "scientific conditions byte-identical"), ("EVT", "ledgers/data/EVT.jsonl", "BLOCKED_FUTURE_STEP", "will use stable recipe/duplicate/family ids"),
         ("STATE", "ledgers/data/STATE.jsonl", "BLOCKED_FUTURE_STEP", "not built"), ("ENTITY", "ledgers/data/ENTITY.jsonl", "BLOCKED_FUTURE_STEP", "not built"), ("EVD", "ledgers/data/EVD.jsonl", "UNCHANGED_CANONICAL", "recipes create no evidence rows"), ("MEAS", "ledgers/data/MEAS.jsonl", "UNCHANGED_CANONICAL", ""),
         ("SVAR", "ledgers/data/SVAR.jsonl", "UNCHANGED_CANONICAL", ""), ("RXN", "ledgers/data/RXN.jsonl", "BLOCKED_FUTURE_STEP", ""), ("WARN", "ledgers/data/WARN.jsonl", "BLOCKED_FUTURE_STEP", ""), ("HYP", "ledgers/data/HYP.jsonl", "BLOCKED_FUTURE_STEP", ""), ("SIM", "ledgers/data/SIM.jsonl", "BLOCKED_FUTURE_STEP", ""),
         ("KINETIC", "ledgers/data/KINETIC.jsonl", "BLOCKED_FUTURE_STEP", ""), ("KGE", "ledgers/data/KGE.jsonl", "BLOCKED_FUTURE_STEP", "graph rebuild from the consolidated base is a later step"), ("Gold index", "ledgers/recipe_base/gold_recipe_index_v1.parquet", "FOREIGN_KEY_UPDATE", "gold_firewall_v1 attaches duplicate_group_id/recipe_family_id; no annotation propagated"),
         ("recipe expressions", "ledgers/recipe_semantics/recipe_expression_probe_v1.parquet", "UNCHANGED_CANONICAL", "recipe-level observations; joined via recipe_id -> duplicate_group_id -> recipe_family_id (no rewrite)"), ("ingredient mentions", "ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet", "UNCHANGED_CANONICAL", "audited"),
         ("quantity mentions", "ledgers/recipe_semantics/recipe_quantity_mentions_v1.parquet", "UNCHANGED_CANONICAL", "audited"), ("process mentions", "ledgers/recipe_semantics/recipe_process_mentions_v1.parquet", "UNCHANGED_CANONICAL", "audited"),
         ("tool mentions", "ledgers/recipe_semantics/recipe_tool_mentions_v1.parquet", "FAMILY_AGGREGATE_CREATED", "new derived recipe-level layer (required for the tool audit)")]
    with open(R / "ledger_graph_impact_matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["object", "path", "action", "reason", "rows_now"])
        for o, p, a_, r_ in M:
            P = ROOT / p
            w.writerow([o, p, a_, r_, rows_of(P) if p.endswith(".parquet") else jl(P)])
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
