#!/usr/bin/env python3
"""STEP 07H-R report writer: reports/step07/step07h_full_recipe_base_report.md from the audit/gate/stats/freeze artifacts (numbers are read, never typed)."""
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
J = lambda p: json.loads((ROOT / p).read_text())


def bbc_dialect():
    e = pq.read_table(ROOT / "ledgers/recipe_semantics/recipe_expression_probe_v1.parquet", columns=["source_family", "expression_family", "raw_expression", "normalized_status", "compound_group_id", "reason_codes", "measurement_location", "candidate_semantic_role"],
                      filters=[("source_family", "=", "A1_BBC_GOOD_FOOD")]).to_pandas()
    pat = lambda s: s.str.lower().str.replace(r"\d+(?:[.,]\d+)?", "#", regex=True).str.strip()
    out = {"a1_expressions": int(len(e)), "by_family": e.expression_family.value_counts().to_dict(), "gas_mark_expressions": int((e.expression_family == "GAS_MARK").sum()), "oven_compound_groups": int(e.compound_group_id.dropna().nunique()),
           "fan_marked_temperatures": int(e.candidate_semantic_role.fillna("").str.contains("FAN").sum()), "temperature_location": e[e.expression_family == "TEMPERATURE"].measurement_location.value_counts(dropna=False).to_dict(),
           "top_temperature_patterns": pat(e[e.expression_family == "TEMPERATURE"].raw_expression).value_counts().head(8).to_dict(), "top_time_patterns": pat(e[e.expression_family == "TIME"].raw_expression).value_counts().head(8).to_dict(),
           "top_gas_patterns": pat(e[e.expression_family == "GAS_MARK"].raw_expression).value_counts().head(5).to_dict(), "top_endpoint_openers": e[e.expression_family == "ENDPOINT"].raw_expression.str.lower().str.split().str[:3].str.join(" ").value_counts().head(8).to_dict(),
           "time_non_valid": e[(e.expression_family == "TIME") & (e.normalized_status != "VALID")].reason_codes.value_counts().head(4).to_dict()}
    return out


def table(d, cols=None):
    df = pd.DataFrame(d).T.fillna(0)
    return df.to_markdown() if hasattr(df, "to_markdown") else df.to_string()


def main():
    a, g = J("reports/step07/step07h_full_recipe_base_audit.json"), J("reports/step07/step07hr_gate_result.json")
    p1, p2 = J("reports/step07/_recipe_build_stats_pass1.json"), J("reports/step07/_recipe_build_stats.json")
    pre = J("reports/step07/recipe_corpus_preflight_inventory.json")
    fm = J("reports/step07/step07hr_freeze_manifest.json") if (ROOT / "reports/step07/step07hr_freeze_manifest.json").exists() else {}
    dia = bbc_dialect()
    (ROOT / "reports/step07/step07h_bbc_a1_dialect.json").write_text(json.dumps(dia, indent=1, ensure_ascii=False))

    def cov(stats):
        rows = {}
        for k, n in stats["coverage"].items():
            s, f, st = k.split("|")
            rows.setdefault(f, {}).setdefault(st, 0)
            rows[f][st] += n
        return {f: {"total": sum(v.values()), "VALID%": round(100 * v.get("VALID", 0) / sum(v.values()), 1), **{k: v for k, v in v.items() if k != "VALID"}} for f, v in rows.items()}
    c1, c2 = cov(p1), cov(p2)
    L = ["# STEP 07H-R -- full recipe-base consolidation, ledger synchronisation, parser freeze", "", "**STEP 08 NOT STARTED.** Recipe text is a procedural observation (`source_plane=RECIPE`, `observation_class=TEXT_STATED`), never a measurement.", "",
         "## A. Canonical base", "", f"- **recipe_base_v1**: {a['totals']['recipe_base']:,} recipes (`ledgers/recipe_base/recipe_base_v1.parquet`; REC stays immutable, base holds pointers + hashes)",
         f"- REC history lines {pre['rec_ledger']['history_lines']:,} = {pre['rec_ledger']['unique_recipe_ids_latest']:,} unique ids + {pre['rec_ledger']['extra_version_lines']:,} version-2 lines (**the earlier '107,760 recipes' counted history lines**)",
         "- by source family: " + ", ".join(f"{k} {v:,}" for k, v in a["totals"]["by_source_family"].items()), f"- recipe families: {a['totals']['unique_recipe_families']:,} (REC family_id kept; Food.com/TASTEset singleton identity families -- no algorithm invented)",
         "- tier totals: " + ", ".join(f"{k} {v:,}" for k, v in a["totals"]["tier_totals"].items()), f"- Gold index rows: {a['totals']['gold_index_rows']} -> {a['totals']['gold_index_status']}",
         "- tiers by source: `" + json.dumps(a["totals"]["tiers_by_source_family"]) + "`", "- **bulk recipes were NOT promoted to Gold**: no DEEP_GOLD / GOLD_LIGHT assigned; all existing Gold is AI-drafted + human-reviewed (D-016/D-017) -> GOLD_PENDING_INDEPENDENT_IAA",
         "", "## B. Ledger synchronisation", "", "Full matrix: `reports/step07/step07h_ledger_sync_matrix.csv` (every designed ledger/registry: before, after, action, reason, plane, owner).", "", "| object | before | after | action |", "|---|---|---|---|"]
    import csv
    for r in csv.DictReader(open(ROOT / "reports/step07/step07h_ledger_sync_matrix.csv", encoding="utf-8")):
        L.append(f"| {r['object']} | {r['row_count_before']} | {r['row_count_after']} | {r['action']} |")
    L += ["", "## C. Parser / normalizer", "", f"- expressions (final): {p2['counts']['expr']:,}; condition mentions {p2['counts']['cond']:,}; ingredient mentions {p2['counts']['ing']:,}; quantity mentions {p2['counts']['qty']:,}; process mentions {p2['counts']['proc']:,}",
          "- first pass vs second pass VALID% by expression family (pass 2 after deterministic-syntax fixes):", "", "| family | pass1 total | pass1 VALID% | pass2 total | pass2 VALID% | pass2 other statuses |", "|---|---|---|---|---|---|"]
    for f in sorted(c2):
        o = c1.get(f, {})
        L.append(f"| {f} | {o.get('total', 0):,} | {o.get('VALID%', '-')} | {c2[f]['total']:,} | {c2[f]['VALID%']} | {({k: v for k, v in c2[f].items() if k not in ('total', 'VALID%')})} |")
    L += ["", "- pass-1 fixes (deterministic syntax only): bare `350°` and `350 degrees` -> `TEMPERATURE_SCALE_NOT_STATED` (was UNIT_MISSING / unparsed); `degrees Fahrenheit/Celsius`; `8″` inch mark; `W/watts`; false temperature `1/2 c.` (a cup) removed; compound `1 hr 30 mins`; `2 1/2`, `1-1/2`, `1/2`, vulgar fractions; calendar-at-ingest guard; U+2044 fraction slash.",
          "- remaining ambiguity is by design: tsp/tbsp/cup etc. (recognised, not converted in the expression ledger; the quantity ledger uses the existing locale-aware grammar), multi-dimension sizes, calendar months/years, temperatures with no stated location/scale, bare psi.",
          "", "### BBC / A1 dialect findings", "", "```json", json.dumps(dia, indent=1, ensure_ascii=False)[:3500], "```", "- gas marks are kept as `GAS_MARK` QUALITATIVE with `UNSUPPORTED_NO_SOURCED_MAPPING`; `180C/160C fan/gas 4` components share a `compound_group_id` and are NOT merged or converted.",
          "- USDA/other unresolved abbreviations (CKD, BKD, BLD, DRND, BKD/SIMMRD, +) remain UNVERIFIED; nothing was learned from recipe co-occurrence.", "",
          "## D. Gold safety", "", f"- Gold links: {a['totals']['gold_index_status']}", f"- leakage proxy (exact normalised title, no splits frozen): {a['family_leakage']['gold_with_bulk_title_twin']} of {a['family_leakage']['gold_checked']} Gold recipes have a bulk-corpus title twin",
          f"- cross-source same-title groups: {a['family_leakage']['cross_source_title_groups']:,}; A1/BBC cross-source groups {a['family_leakage']['a1_bbc_cross_source_title_groups']:,}; singleton families {a['family_leakage']['singleton_family_count']:,}; largest {a['family_leakage']['largest_families'][:3]}",
          "- sealed linker sets (441 / 850) were not read or used; protected Gold labels were not used to tune any rule (parser rules derive from recipe TEXT only).", "", "## E. Simulation readiness (TEXT availability only -- NOT simulation eligibility)", "", "| source | status counts |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in a["readiness"].items()]
    L += [f"| **ALL** | {a['readiness_total']} |", "", "## F. Tests / gate", "", "```json", json.dumps(g, indent=1)[:2600], "```", "", "## G. Freeze", ""]
    L += ["```json", json.dumps(fm, indent=1)[:3500], "```"] if fm else ["(freeze manifest pending)"]
    (ROOT / "reports/step07/step07h_full_recipe_base_report.md").write_text("\n".join(L) + "\n")
    print("report written", len(L), "lines")


if __name__ == "__main__":
    main()
