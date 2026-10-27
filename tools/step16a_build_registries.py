#!/opt/anaconda3/bin/python
"""Step 16a batch 1: build DRAFT vocabulary registries (deterministic, read-only on ledgers)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = "docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md"
STATUS = "DRAFT_PENDING_H4"
NO_DEF = "named in plan; definition not given in plan; needs H4"
OPEN_DEF = "members not enumerated in the plan; needs H4"
M = f"{PLAN} STEP 16 Method/architecture"
A = f"{PLAN} 16-A"

# registry -> (source_ref, [(code, definition)]); members exactly as named in the Step 16 card.
ENUMS: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "event_kind": (M + " (EVT v1)", [(c, NO_DEF) for c in
        ["ACTION", "ENDPOINT_CHECK", "OBSERVATION", "CONDITIONAL", "WAIT_REST", "CONTROL"]]),
    "modality": (M + " (EVT v1)", [(c, NO_DEF) for c in
        ["REQUIRED", "OPTIONAL", "NEGATED", "CONDITIONAL", "HYPOTHETICAL"]]),
    "temporal_relation": (M + " (EVT v1)", [
        ("SEQUENTIAL", NO_DEF), ("PARALLEL", NO_DEF), ("OVERLAPS", NO_DEF), ("UNTIL", NO_DEF),
        ("REPEAT_UNTIL", 'plan note: "repeat until smooth" never invents a count; otherwise ' + NO_DEF)]),
    "transformation_mode": (M + " (EVT v1)", [(c, NO_DEF) for c in
        ["MECHANICAL", "THERMAL", "CHEMICAL_CURING", "BIOCHEMICAL_FERMENTATION", "TRANSFER", "TEMPORAL_REST"]]),
    "tool_role": (M + " (EVT v1 tool_roles)", [(c, NO_DEF) for c in
        ["INSTRUMENT", "CONTAINER", "HEAT_SOURCE", "MEASURE"]]),
    "entity_type": (A + " layer 3 (ENTITY v1)", [
        ("INGREDIENT_LOT", "one lot (16-A layer 3)"), ("INTERMEDIATE", NO_DEF), ("MIXTURE", NO_DEF),
        ("RESERVED_PORTION", NO_DEF), ("DISCARDED_PORTION", NO_DEF), ("TOOL_CONTENTS", NO_DEF)]),
    "lifecycle": (A + " layer 3 (ENTITY v1)", [
        ("ACTIVE", NO_DEF), ("RESERVED", NO_DEF),
        ("INCORPORATED", "plan rule: incorporated is not vanished"), ("DISCARDED", NO_DEF),
        ("SERVED", NO_DEF), ("UNRESOLVED", "plan rule: unresolved references keep their candidate set; never forced")]),
    "field_status": (M + " (per-field metadata triple)", [
        ("KNOWN", NO_DEF), ("UNKNOWN", "plan rule: UNKNOWN is not 0"), ("NOT_APPLICABLE", NO_DEF),
        ("CONFLICTING", NO_DEF), ("CENSORED", NO_DEF)]),
    "claim_route": (M + " (per-field metadata triple)", [(c, NO_DEF) for c in
        ["EXPLICIT", "INFERRED_RULE", "INFERRED_LLM", "MODEL", "SIMULATED"]]),
    "annotation_mode": (PLAN + " STEP 16 (name appears in Outputs only; no members listed)", []),
}

REG_DIR = ROOT / "registry" / "recipe_semantics"
PROC_DIR = ROOT / "registry" / "processes"
TOOL_DIR = ROOT / "registry" / "tools"


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def enum_rows(name: str) -> list[list[str]]:
    ref, members = ENUMS[name]
    members = list(members) or [("OPEN", OPEN_DEF)]
    return [[c, c.replace("_", " ").title(), d, ref, STATUS] for c, d in sorted(members)]


def latest(path: Path) -> list[dict]:
    best: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r["id"] not in best or r["version"] > best[r["id"]]["version"]:
            best[r["id"]] = r
    return [best[k] for k in sorted(best)]


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def build_process() -> tuple[list[list[str]], list[list[str]]]:
    procs = latest(ROOT / "ledgers/data/PROC.jsonl")
    by_id = {p["id"]: p for p in procs}
    forms = read_csv(ROOT / "registry/recipe_process_surface_forms_v1.csv")
    hier: list[list[str]] = []
    ep: list[list[str]] = []
    fams = sorted({p["family"] for p in procs if p["kind"] != "ENDPOINT" and p.get("family")})
    for f in fams:
        hier.append([f"FAM:{f}", f, "", "1", "false", "PROC.family value (family node; root)"])
    for p in procs:
        raw = sorted(set(p.get("aliases") or []))
        mapped = sorted({r["surface_form"] for r in forms if r["canonical_mapping"] == p["id"]})
        if p["kind"] == "ENDPOINT":
            hier.append([p["id"], p["canonical_name"], "", "", "true",
                         "PROC.kind=ENDPOINT; moved to V_ENDPOINT, outside hierarchy"])
            ep.append([p["id"], p["canonical_name"], ";".join(sorted(set(raw) | set(mapped)))])
            continue
        if p.get("family"):
            hier.append([p["id"], p["canonical_name"], f"FAM:{p['family']}", "2", "false",
                         "PROC.family (parent=family node, proposal only)"])
        else:
            hier.append([p["id"], p["canonical_name"], "", "2", "false", "NEEDS_HUMAN: PROC.family missing"])
        seen = {p["canonical_name"]}
        for s, src in [(a, "PROC.aliases") for a in raw] + \
                      [(m, "recipe_process_surface_forms_v1.canonical_mapping (CANDIDATE, POS unchecked)") for m in mapped]:
            if s in seen:
                continue
            seen.add(s)
            hier.append([f"ALIAS:{p['id']}:{s}", s, p["id"], "3", "false", src])
    hier.sort(key=lambda r: (r[3] or "9", r[0]))
    ep.sort()
    return hier, ep


def build_tool() -> list[list[str]]:
    tools = latest(ROOT / "ledgers/data/TOOL.jsonl")
    smap = {r["tool_id"]: r for r in read_csv(ROOT / "registry/recipe_tool_structural_class_map_v1.csv")}
    rows: list[list[str]] = []
    cats = sorted({t["category"] for t in tools if t.get("category") and t["category"] != "OTHER"})
    for c in cats:
        rows.append([f"CAT:{c}", c, "", "1", "category", "", "TOOL.category value (root)"])
    for t in tools:
        sc = smap.get(t["id"], {}).get("structural_class", "")
        cat = t.get("category") or ""
        if cat and cat != "OTHER":
            parent, ev = f"CAT:{cat}", "TOOL.category (proposal only)"
        else:
            parent, ev = "", f"NEEDS_HUMAN: TOOL.category={cat or 'missing'} gives no parent"
        rows.append([t["id"], t["canonical_name"], parent, "2", "tool", sc, ev])
        seen = {t["canonical_name"]}
        for a in sorted(set(t.get("aliases") or [])):
            if a in seen:
                continue
            seen.add(a)
            rows.append([f"ALIAS:{t['id']}:{a}", a, t["id"], "3", "alias", "", "TOOL.aliases"])
    rows.sort(key=lambda r: (r[3], r[0]))
    return rows


def main() -> None:
    hdr = ["code", "label", "definition", "source_ref", "status"]
    for name in ENUMS:
        write_csv(REG_DIR / f"{name}_registry_v1_DRAFT.csv", hdr, enum_rows(name))
    hier, ep = build_process()
    write_csv(PROC_DIR / "process_hierarchy_v1_DRAFT.csv",
              ["id", "name", "proposed_parent_id", "level", "endpoint_flag", "evidence"], hier)
    write_csv(PROC_DIR / "endpoint_vocabulary_v1_DRAFT.csv", ["id", "name", "raw_surface_forms"], ep)
    write_csv(TOOL_DIR / "tool_hierarchy_v1_DRAFT.csv",
              ["id", "name", "proposed_parent_id", "level", "node_type", "structural_class", "evidence"],
              build_tool())


if __name__ == "__main__":
    main()
