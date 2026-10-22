#!/usr/bin/env python3
"""Read-only statistics drop over every non-recipe ledger (latest version per id; append-only history counted separately).
  python tools/ledger_stats.py -> reports/h_state/ledger_stats.{md,json}"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L = ROOT / "ledgers/data"


def get(r, path):
    for k in path.split("."):
        r = r.get(k) if isinstance(r, dict) else None
    return r


def load(n):
    lat, lines = {}, 0
    for line in open(L / f"{n}.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            lines += 1
            lat[r["id"]] = r
    return lat, lines


def dist(recs, path, top=12):
    c = Counter()
    for r in recs:
        v = get(r, path)
        for x in (v if isinstance(v, list) else [v]):
            c[str(x) if not isinstance(x, (dict,)) else json.dumps(x, sort_keys=True)[:40]] += 1
    return dict(c.most_common(top))


def num(recs, path):
    xs = sorted(v for v in (get(r, path) for r in recs) if isinstance(v, (int, float)) and not isinstance(v, bool))
    return {"n": len(xs), "sum": sum(xs), "median": xs[len(xs) // 2] if xs else None, "max": xs[-1] if xs else None}


def top(recs, name, freq, k=10):
    return [[get(r, name), get(r, freq)] for r in sorted(recs, key=lambda r: -(get(r, freq) or 0))[:k]]


SPEC = {
    "ING": lambda R: {"canonical_names_unique": len({r["canonical_name"] for r in R}), "ambiguity": dist(R, "ambiguity"), "with_parent": sum(1 for r in R if r.get("parent_ids")), "corpus_frequency": num(R, "corpus_frequency"), "facet_keys": dist(R, "facets", 8),
            "crosswalk_fdc": dist(R, "crosswalks.fdc.status"), "crosswalk_foodon": dist(R, "crosswalks.foodon.status"), "top_by_frequency": top(R, "canonical_name", "corpus_frequency")},
    "ALIAS": lambda R: {"alias_type": dist(R, "alias_type"), "link_band": dist(R, "link_band"), "language": dist(R, "language"), "unique_normalized": len({r["normalized"] for r in R}), "unique_target_ingredients": len({r.get("ingredient_id") for r in R if r.get("ingredient_id")}),
                        "corpus_frequency": num(R, "corpus_frequency")},
    "PROC": lambda R: {"kind": dist(R, "kind"), "family": dist(R, "family", 20), "mechanism_families": dist(R, "mechanism_families", 20), "corpus_frequency": num(R, "corpus_frequency"), "evidence_coverage": num(R, "evidence_coverage"),
                       "with_evidence": sum(1 for r in R if (r.get("evidence_coverage") or 0) > 0), "top_by_frequency": top(R, "canonical_name", "corpus_frequency", 15)},
    "TOOL": lambda R: {"category": dist(R, "category", 20), "material": dist(R, "material"), "max_safe_temp_status": dist(R, "max_safe_temperature_c.status"), "unique_aliases": sum(len(r.get("aliases") or []) for r in R), "top_by_mentions": [[r["canonical_name"], (get(r, "provenance.notes") or "")] for r in R[:0]]},
    "UNIT": lambda R: {"dimension": dist(R, "dimension", 20), "aliases_total": sum(len(r.get("aliases") or []) for r in R), "with_ambiguity_note": sum(1 for r in R if r.get("ambiguity_notes")), "with_conventions": sum(1 for r in R if r.get("conventions")), "names": sorted(r["canonical_name"] for r in R)},
    "SVAR": lambda R: {"family": dist(R, "family"), "dimension": dist(R, "dimension", 15), "observable_in_session": dist(R, "observable_in_session"), "unique_names": len({r["canonical_name"] for r in R})},
    "MEAS": lambda R: {"family": dist(R, "family"), "basis": dist(R, "basis")},
    "EXP": lambda R: {"compute": dist(R, "compute"), "status": dist(R, "status")},
    "STUDY": lambda R: {"design": dist(R, "design"), "source_id": dist(R, "source_id")},
    "SRC": lambda R: {"kind": dist(R, "kind", 15), "licence_status": dist(R, "licence_status"), "primary_or_secondary": dist(R, "primary_or_secondary")},
    "SNAP": lambda R: {"http_status": dist(R, "http_status"), "bytes": num(R, "bytes")},
    "ALLERGEN": lambda R: {"names": sorted(r["allergen_name"] for r in R)},
    "MOL": lambda R: {"with_smiles": sum(1 for r in R if r.get("canonical_smiles")), "descriptor_keys": dist(R, "descriptors", 6), "unique_smiles": len({r.get("canonical_smiles") for r in R})},
    "IMAP": lambda R: {"basis": dist(R, "basis"), "concentration_status": dist(R, "concentration.status"), "unique_ingredients": len({r["ingredient_id"] for r in R}), "unique_molecules": len({r["molecule_id"] for r in R}), "unit": dist(R, "concentration.unit", 10)},
    "KGE": lambda R: {"predicate": dist(R, "predicate", 15), "method": dist(R, "method"), "confidence_band": dist(R, "confidence_band"), "corpus_ids": dist(R, "corpus_ids", 10), "unique_subjects": len({r.get("subject_id") for r in R}), "unique_objects": len({r.get("object_id") for r in R})},
    "COND": lambda R: {"mask_temperature": dist(R, "completeness_mask.temperature"), "mask_duration": dist(R, "completeness_mask.duration"), "mask_pressure": dist(R, "completeness_mask.pressure"), "mask_moisture": dist(R, "completeness_mask.moisture"), "mask_ph": dist(R, "completeness_mask.ph"),
                       "temperature_locations": dist([t for r in R for t in (r.get("temperatures") or [])], "location"), "temperature_entries": sum(len(r.get("temperatures") or []) for r in R), "medium": dist(R, "medium", 10),
                       "duration_raw_unique": len({get(r, "duration.raw") for r in R if get(r, "duration.raw")}), "duration_status": dist(R, "duration.status")},
    "EVD": lambda R: {"tier": dist(R, "tier"), "design": dist(R, "design"), "origin_type": dist(R, "origin_type"), "source_family": dist(R, "source_family_id"), "applicability": dist(R, "applicability"), "censored": dist(R, "censored"), "verification": dist(R, "verification.status"),
                      "unique_ingredients": len({get(r, "matrix.ingredient_id") for r in R}), "unique_matrix_raw_names": len({get(r, "matrix.raw_name") for r in R}), "unique_food_groups": dist(R, "matrix.food_group", 15), "unique_processes": len({get(r, "process.process_id") for r in R}),
                      "unique_conditions": len({get(r, "process.condition_id") for r in R}), "unique_target_svars": len({get(r, "target.state_variable_id") for r in R}), "unique_studies": len({s for r in R for s in (r.get("study_ids") or [])}), "target_basis": dist(R, "target.basis"),
                      "direction": dist(R, "derived.direction"), "retention_status": dist(R, "derived.retention_factor.status")},
}


def main():
    out, md = {}, ["# Ledger statistics drop (non-recipe ledgers; read-only)", "", "Latest version per id; `history_lines` counts the append-only lines. REC (recipes) excluded except its row count.", "",
                   "| ledger | latest ids | history lines | ACTIVE | other status | verification (top) | provenance method (top) |", "|---|---|---|---|---|---|---|"]
    for n in ["SRC", "SNAP", "STUDY", "ING", "ALIAS", "ALLERGEN", "PROC", "TOOL", "UNIT", "SVAR", "MEAS", "COND", "EVD", "MOL", "IMAP", "KGE", "EXP"]:
        lat, lines = load(n)
        R = list(lat.values())
        base = {"latest_ids": len(R), "history_lines": lines, "status": dist(R, "status"), "verification": dist(R, "verification.status"), "provenance_method": dist(R, "provenance.method"), "created_by": dist(R, "created_by")}
        base.update(SPEC[n](R))
        out[n] = base
        md.append(f"| {n} | {len(R)} | {lines} | {base['status'].get('ACTIVE', 0)} | {({k: v for k, v in base['status'].items() if k != 'ACTIVE'})} | {base['verification']} | {base['provenance_method']} |")
    out["REC"] = {"history_lines": sum(1 for _ in open(L / "REC.jsonl", encoding="utf-8")), "note": "recipes excluded from this drop"}
    md.append(f"| REC | (excluded) | {out['REC']['history_lines']} | | | | |")
    for n, d in out.items():
        if n == "REC":
            continue
        md += ["", f"## {n}", ""]
        for k, v in d.items():
            if k in ("latest_ids", "history_lines", "created_by"):
                continue
            s = json.dumps(v, ensure_ascii=False)
            md.append(f"- **{k}**: {s if len(s) < 700 else s[:700] + ' ...'}")
    (ROOT / "reports/h_state/ledger_stats.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    (ROOT / "reports/h_state/ledger_stats.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[:30]))


main()
