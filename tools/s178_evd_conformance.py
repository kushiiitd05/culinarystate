#!/usr/bin/env python3
"""S178 EVD lane, T2-C01-R1: field-by-field conformance of the EVD rows against the SSOT section 203.2 process-event schema.

One table row per field (or sub-field) of the 203.2 minimum schema. For every ACTIVE EVD row (17,978 = the export v1 row
count) each field gets exactly one status:

  PRESENT              the row carries a stated value for the field
  CENSORED_BOUND_ONLY  only a one-sided bound is stated (target value / temperature given as "at least ...")
  UNKNOWN              the field has a home in the ledger / export, the row carries explicit UNKNOWN or null (never 0, never imputed)
  NOT_APPLICABLE       the field does not apply to this row by form (a point value makes lo/hi moot; USDA rows have no pressure)
  ABSENT               no field of that meaning exists in the EVD / COND ledger schemas or in the export (the gap is structural)

so PRESENT + CENSORED_BOUND_ONLY + UNKNOWN + NOT_APPLICABLE + ABSENT = 17,978 for every field (asserted). "UNKNOWN" is the
board's "UNKNOWN-by-source". Condition fields (T, t, medium, pH, ...) live in the COND record joined through
process.condition_id (export v1 carries only their completeness mask); this is stated in the `carrier` column.

Inputs read-only: ledgers/data/{EVD,COND,SRC,SVAR,PROC}.jsonl, registry/svar_duplicate_mapping_v1.csv, the committed
exports/lineage/step08a_v1/keys.jsonl (v2 lineage columns). The v1 export rows are rebuilt in memory with
``culinarystate.evidence.evd_export.build_export`` (the same code that wrote the export). Counts only; no recipe or paper text.

  python tools/s178_evd_conformance.py [--out-dir reports/s178/evd] [--selfcheck]

Status: AI_DRAFTED / PROPOSED (reviewed by nobody). Deterministic, no timestamp.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s178_evd_common import (DEFAULT_OUT, ROOT, counter_dict, dumps, md_table, protected_hashes,  # noqa: E402
                             read_ledger, sha256_file, write_new_or_same)

TOOL_VERSION = "s178-evd-conformance-0.1.0-draft"
STATUSES = ("PRESENT", "CENSORED_BOUND_ONLY", "UNKNOWN", "NOT_APPLICABLE", "ABSENT")
P, C, U, N, A = STATUSES
KEYS = "exports/lineage/step08a_v1/keys.jsonl"
CARRIERS = {"X": "export v1 column", "XC": "export v1 + COND join", "C": "COND record via condition_id (v1: mask only)", "L": "EVD ledger only (not in export v1)",
            "J": "joined ledger (SVAR / SRC / PROC) via an export id", "V2": "export v2 added column", "-": "none"}


class Row:
    """Everything a rule may look at for one ACTIVE EVD row."""
    __slots__ = ("x", "e", "c", "src", "svar", "key")

    def __init__(self, x, e, c, src, svar, key):
        self.x, self.e, self.c, self.src, self.svar, self.key = x, e, c, src, svar, key

    @property
    def temps(self):
        return self.c.get("temperatures", [])

    def temp_status(self, st):
        return [t for t in self.temps if t["value"]["status"] == st]


def _t_value(r):
    if r.temp_status("MEASURED"):
        return P, "measured"
    if r.temp_status("CENSORED"):
        return C, "one_sided_bound"
    if r.temp_status("RANGE"):
        return N, "stated_as_range"
    return U, "no_temperature_stated"


def _t_range(side):
    def f(r):
        if r.temp_status("RANGE"):
            return P, "range"
        if r.temps:
            return N, "stated_as_point_or_bound"
        return U, "no_temperature_stated"
    return f


def _t_type(r):
    if any(t["location"] != "UNSPECIFIED" for t in r.temps):
        return P, "location_given"
    return U, "location_unspecified" if r.temps else "no_temperature_stated"


def _dur(kind):
    def f(r):
        st = r.c["duration"]["status"]
        if kind == "value":
            return (P, "measured") if st == "MEASURED" else ((N, "stated_as_range") if st == "RANGE" else (U, "no_duration_stated"))
        return (P, "range") if st == "RANGE" else ((N, "stated_as_point") if st == "MEASURED" else (U, "no_duration_stated"))
    return f


def _cond_obj(field, kind, mask_key=None):
    """COND object field (status/value/low/high): kind = value | range."""
    def f(r):
        o = r.c.get(field)
        if o is None:
            if mask_key and r.c["completeness_mask"].get(mask_key) == "NOT_APPLICABLE":
                return N, "mask_not_applicable"
            return U, "not_populated"
        st = o["status"]
        if kind == "value":
            return (P, "measured") if st == "MEASURED" else ((N, "stated_as_range") if st == "RANGE" else (U, st.lower()))
        return (P, "range") if st == "RANGE" else ((N, "stated_as_point") if st == "MEASURED" else (U, st.lower()))
    return f


def _target_value(r):
    d = r.e["derived"]
    rf, yf = d.get("retention_factor") or {}, d.get("yield_factor") or {}
    if r.e.get("before") and r.e.get("after") and r.e["before"]["status"] == "MEASURED" and r.e["after"]["status"] == "MEASURED":
        return P, "before_after_measured"
    if rf.get("status") == "MEASURED":
        return P, "retention_measured"
    if r.e["target"]["state_variable_id"] and not rf and yf.get("status") == "MEASURED":
        return P, "yield_measured"
    if rf.get("status") == "CENSORED":
        return C, "retention_censored_at_cap"
    return U, "retention_unknown"


def _target_lo(r):
    s, why = _target_value(r)
    rf = (r.e["derived"].get("retention_factor") or {})
    if s == C:
        return C, "lower_bound_is_censor_limit"
    if s == P:
        return (P, "low_stated") if rf.get("low") is not None else (N, "point_value")
    return U, why


def _target_hi(r):
    s, why = _target_value(r)
    rf = (r.e["derived"].get("retention_factor") or {})
    if s == C:
        return N, "one_sided_lower_bound"
    if s == P:
        return (P, "high_stated") if rf.get("high") is not None else (N, "point_value")
    return U, why


def _unit(r):
    s, why = _target_value(r)
    d = r.e["derived"]
    if s == U:
        return U, "no_value"
    rf, yf = d.get("retention_factor") or {}, d.get("yield_factor") or {}
    u = rf.get("unit") or (r.e.get("before") or {}).get("unit") or yf.get("unit")
    return (P, "unit_stated") if u else (U, "value_without_unit_in_export")


def _direction(r):
    d = r.e["derived"].get("direction")
    return (P, "increase_decrease_or_no_change") if d in ("INCREASE", "DECREASE", "NO_CHANGE") else (U, "direction_unknown_derived")


def _doi(r):
    if any(r.src.get(s, {}).get("doi") for s in r.e["provenance"]["source_ids"]):
        return P, "doi_on_publication_record"
    return U, "database_level_citation_only_or_no_doi"


def _state_in(r):
    m = r.e["matrix"]
    return (P, "free_text_state") if (m.get("initial_state") or m.get("prior_processing")) else (U, "no_state_text")


def _process_leaf(r):
    return (P, "process_id") if r.e["process"].get("process_id") else (U, "process_id_null_raw_name_kept")


def _process_family(r):
    return (P, "family") if r.x.get("process_family") else (U, "no_family")


def _medium(r):
    return (P, "medium_recorded") if (r.e["process"].get("medium") or r.c.get("medium")) else (U, "medium_not_recorded")


def _simple(fn: Callable) -> Callable:
    return lambda r: (P, "") if fn(r) else (U, "")


def _fixed(status, why=""):
    return lambda r: (status, why)


# (ssot_line, field, group, carrier, match, rule, note)
FIELDS: list[tuple] = [
    ("event_id", "event_id", "identity", "X", "EXACT", lambda r: (P, "evd_id"), "an EVD row is an evidence atom (food x process x target), not a recipe process event"),
    ("ingredient_id", "ingredient_id", "identity", "X", "EXACT", lambda r: (P, "ING_linked") if r.e["matrix"].get("ingredient_id") else (U, "ING_unresolved_raw_name_kept"), "unlinked rows keep matrix.raw_name"),
    ("ingredient_state_in", "ingredient_state_in", "state", "XC", "PARTIAL", _state_in, "free text matrix.initial_state / prior_processing; no controlled vocabulary (prior_state_id is a hash of the raw descriptor)"),
    ("ingredient_state_out", "ingredient_state_out", "state", "-", "NONE", _fixed(A, "no output-state field"), "the process raw name may imply it; nothing structured"),
    ("process_leaf", "process_leaf", "process", "X", "EXACT", _process_leaf, "process.process_id (PROC ledger); multi-step rows also list step_process_ids"),
    ("process_family", "process_family", "process", "XC", "EXACT", _process_family, "PROC.family of the process id"),
    ("T_value", "T_value", "condition", "C", "EXACT", _t_value, "COND.temperatures[]; v1 export keeps only completeness_mask.temperature"),
    ("T_lo", "T_lo", "condition", "C", "EXACT", _t_range("lo"), "COND.temperatures[] RANGE low"),
    ("T_hi", "T_hi", "condition", "C", "EXACT", _t_range("hi"), "COND.temperatures[] RANGE high"),
    ("T_type", "T_type", "condition", "C", "EXACT", _t_type, "COND.temperatures[].location (SETPOINT / MEDIUM / CORE ...)"),
    ("t_value", "t_value", "condition", "C", "EXACT", _dur("value"), "COND.duration (unit min)"),
    ("t_lo", "t_lo", "condition", "C", "EXACT", _dur("lo"), "COND.duration RANGE low"),
    ("t_hi", "t_hi", "condition", "C", "EXACT", _dur("hi"), "COND.duration RANGE high"),
    ("t_type", "t_type", "condition", "-", "NONE", _fixed(A, "COND.duration has value/unit/raw only"), "no total-vs-hold-vs-ramp type"),
    ("medium", "medium", "condition", "XC", "EXACT", _medium, "process.medium or COND.medium"),
    ("tool", "tool", "condition", "C", "EXACT", lambda r: (P, "tool_ids") if (r.c.get("tool_ids") or r.e["process"].get("tool_ids")) else (U, "tool_ids_never_populated"), "COND.tool_ids / process.tool_ids exist in the schema; no row fills them"),
    ("geometry", "geometry", "condition", "C", "PARTIAL", lambda r: (P, "geometry") if (r.c.get("geometry") or r.c.get("particle_size") or r.e["matrix"].get("geometry")) else (U, "geometry_never_populated"), "COND.geometry / particle_size / matrix.geometry exist; matrix.form (sliced, diced ...) is not counted as geometry"),
    ("moisture_value / range / type", "moisture_value", "condition", "C", "EXACT", _cond_obj("moisture", "value", "moisture"), "COND.moisture"),
    ("moisture_value / range / type", "moisture_range", "condition", "C", "EXACT", _cond_obj("moisture", "range", "moisture"), "COND.moisture RANGE"),
    ("moisture_value / range / type", "moisture_type", "condition", "-", "NONE", _fixed(A, "no moisture basis/type field"), "wet vs dry basis is carried only by the unit string, when a value exists"),
    ("water_activity_value / range / type", "water_activity_value", "condition", "C", "EXACT", _cond_obj("water_activity", "value", "water_activity"), "COND.water_activity exists in the schema (the completeness_mask has no a_w key; the card's NOT_IN_COND_SCHEMA is about the mask)"),
    ("water_activity_value / range / type", "water_activity_range", "condition", "C", "EXACT", _cond_obj("water_activity", "range", "water_activity"), "COND.water_activity RANGE"),
    ("water_activity_value / range / type", "water_activity_type", "condition", "-", "NONE", _fixed(A, "no a_w type field"), ""),
    ("pH_value / range / type", "pH_value", "condition", "C", "EXACT", _cond_obj("ph_initial", "value", "ph"), "COND.ph_initial / ph_final (mask key `ph` is UNKNOWN on every row)"),
    ("pH_value / range / type", "pH_range", "condition", "C", "EXACT", _cond_obj("ph_initial", "range", "ph"), "COND.ph_initial RANGE"),
    ("pH_value / range / type", "pH_type", "condition", "C", "PARTIAL", lambda r: (P, "initial_or_final") if ("ph_initial" in r.c or "ph_final" in r.c) else (U, "not_populated"), "initial vs final is the only type the schema has (no medium / tissue distinction)"),
    ("pressure_value / range / type", "pressure_value", "condition", "C", "EXACT", _cond_obj("pressure", "value", "pressure"), "COND.pressure; mask NOT_APPLICABLE for USDA retention rows"),
    ("pressure_value / range / type", "pressure_range", "condition", "C", "EXACT", _cond_obj("pressure", "range", "pressure"), "COND.pressure RANGE"),
    ("pressure_value / range / type", "pressure_type", "condition", "-", "NONE", _fixed(A, "no absolute / gauge / vacuum type field"), "unit strings only (psi, MPa, Mpa: three spellings in COND)"),
    ("oxygen_value / category", "oxygen_value", "condition", "C", "EXACT", _cond_obj("oxygen", "value"), "COND.oxygen"),
    ("oxygen_value / category", "oxygen_category", "condition", "C", "PARTIAL", lambda r: (P, "qualitative") if (r.c.get("oxygen") or {}).get("qualitative") else (U, "not_populated"), "COND.oxygen.qualitative"),
    ("mixing", "mixing", "condition", "C", "EXACT", lambda r: (P, "agitation") if r.c.get("agitation") else (U, "agitation_never_populated"), "COND.agitation"),
    ("target_type", "target_type", "target", "J", "EXACT", lambda r: (P, r.svar[r.e["target"]["state_variable_id"]]["family"]) if r.e["target"].get("state_variable_id") else (U, "no_svar"), "SVAR.family (CHEMICAL / PHYSICAL) through target_state_variable_id; the registry adds a subfamily"),
    ("target_variable / target_compound", "target_variable", "target", "X", "EXACT", lambda r: (P, "svar_id") if r.e["target"].get("state_variable_id") else (U, "no_svar"), "target_state_variable_id + canonical_variable_id (duplicate mapping)"),
    ("target_variable / target_compound", "target_compound", "target", "L", "EXACT", lambda r: (P, "molecule_id") if r.e["target"].get("molecule_id") else (U, "molecule_id_never_populated"), "target.molecule_id; no PubChem / ChEBI / InChIKey link on any row"),
    ("target_value", "target_value", "target", "X", "EXACT", _target_value, "retention fraction, before/after pair, or yield fraction; a GT_CAP value is a bound, not a measurement"),
    ("target_lo", "target_lo", "target", "X", "PARTIAL", _target_lo, "retention low; for censored rows the censor limit is the lower bound"),
    ("target_hi", "target_hi", "target", "X", "PARTIAL", _target_hi, "retention high"),
    ("unit", "unit", "target", "X", "EXACT", _unit, "retention_unit / before_unit; the 496 yield rows have no unit column in v1"),
    ("direction_label", "direction_label", "target", "X", "EXACT", _direction, "derived.direction; UNKNOWN is derived, not source-stated (censored rows)"),
    ("ordinal_band", "ordinal_band", "target", "-", "NONE", _fixed(A, "no ordinal band field"), ""),
    ("censor_flag", "censor_flag", "quality", "X", "EXACT", lambda r: (P, "flag_true" if r.e["censored"] else "flag_false"), "censoring_flag is a boolean on every row; true on 5,894"),
    ("LOD", "LOD", "quality", "X", "PARTIAL", lambda r: (U, "NOT_REPORTED_BY_SOURCE_ROW"), "export columns lod / loq exist, null on all rows; GT_CAP limits are upper caps, not detection limits"),
    ("platform", "platform", "provenance", "-", "NONE", _fixed(A, "no analytical-platform field"), "MEAS records give the method family of the database, not HPLC / GC of the primary measurement"),
    ("study_id", "study_id", "provenance", "X", "EXACT", lambda r: (P, "study_id") if r.e["study_ids"] else (U, "NOT_IDENTIFIABLE"), "export v1 study_ids; v2 adds study_id from the lineage keys"),
    ("source_id", "source_id", "provenance", "X", "EXACT", lambda r: (P, "source_id"), ""),
    ("doi_or_citation", "doi_or_citation", "provenance", "J", "PARTIAL", _doi, "SRC.doi on 3,678 publication records; USDA and Bognar rows cite the database SRC (authors / year / title) but no primary study"),
    ("evidence_tier", "evidence_tier", "quality", "X", "EXACT", lambda r: (P, r.e["tier"]), "all E3"),
    ("verified_by", "verified_by", "quality", "L", "EXACT", lambda r: (P, "verifier") if r.e["verification"].get("verifier") else (U, "no_human_verifier"), "verification.verifier; AI_PRECHECKED rows carry ai_reviewer only"),
    ("verification_status", "verification_status", "quality", "X", "EXACT", lambda r: (P, r.e["verification"]["status"]), "UNVERIFIED or AI_PRECHECKED; 0 HUMAN_VERIFIED"),
    ("extraction_method", "extraction_method", "provenance", "L", "EXACT", lambda r: (P, r.e["extraction_version"]), "extraction_version + provenance.method (IMPORT); the export keeps only provenance_class"),
    ("explicit_or_inferred", "explicit_or_inferred", "provenance", "X", "EXACT", lambda r: (P, r.x["provenance_class"]), "provenance_class; EXPLICIT_SOURCE for all rows; USDA rows flagged SOURCE_SIDE_IMPUTATION_POSSIBLE"),
    ("notes", "notes", "provenance", "L", "EXACT", lambda r: (P, "notes") if r.e.get("notes") else (U, "empty"), "EVD.notes is empty on every ACTIVE row"),
    ("dataset_version", "dataset_version", "provenance", "X", "PROXY", lambda r: (P, "export_version_only"), "export_version evd_export@1.0.0 is a schema version; no dataset has been frozen (15a not frozen), so this is a proxy"),
    ("split_id", "split_id", "provenance", "V2", "PROXY", _fixed(A, "not in export v1"), "export v2 adds split_group_id (SCRATCH_PROVISIONAL assignment, keys-v1) on every row"),
]


def classify(rows: list[Row]) -> list[dict]:
    out = []
    for ssot, field, group, carrier, match, rule, note in FIELDS:
        tot = Counter()
        by_fam: dict[str, Counter] = defaultdict(Counter)
        detail = Counter()
        for r in rows:
            s, why = rule(r)
            tot[s] += 1
            by_fam[r.x["source_family_id"]][s] += 1
            if why:
                detail[f"{s}:{why}"] += 1
        n = sum(tot.values())
        assert n == len(rows), (field, n, len(rows))
        out.append({"ssot_line": ssot, "field": field, "group": group, "carrier": carrier, "carrier_text": CARRIERS[carrier], "match": match,
                    "counts": {s: tot.get(s, 0) for s in STATUSES}, "total": n,
                    "by_source_family": {f: {s: c.get(s, 0) for s in STATUSES} for f, c in sorted(by_fam.items())},
                    "detail": counter_dict(detail), "note": note})
    return out


def load_rows(root: Path) -> tuple[list[Row], dict]:
    from culinarystate.evidence.evd_export import build_export
    led = root / "ledgers" / "data"
    x_rows, _, _, meta = build_export(led)
    evd, _ = read_ledger(led / "EVD.jsonl")
    cond, _ = read_ledger(led / "COND.jsonl")
    src, _ = read_ledger(led / "SRC.jsonl")
    svar, _ = read_ledger(led / "SVAR.jsonl")
    keys = {}
    with open(root / KEYS, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                k = json.loads(line)
                keys[k["evd_id"]] = k
    rows = [Row(x, evd[x["evd_id"]], cond[evd[x["evd_id"]]["process"]["condition_id"]], src, svar, keys.get(x["evd_id"])) for x in x_rows]
    return rows, meta


def v2_lineage_counts(rows: list[Row]) -> dict:
    return {"rows_with_v2_key_record": sum(1 for r in rows if r.key is not None),
            "split_group_id_present": sum(1 for r in rows if r.key and r.key.get("split_group_id")),
            "distinct_split_group_ids": len({r.key["split_group_id"] for r in rows if r.key and r.key.get("split_group_id")}),
            "assignment_status": counter_dict(Counter(r.key.get("assignment_status") for r in rows if r.key)),
            "study_id_present_v2": sum(1 for r in rows if r.key and r.key.get("study_id")),
            "lineage_study_id_status": counter_dict(Counter(r.key.get("study_id_status") for r in rows if r.key)),
            "independence_resolution": counter_dict(Counter(r.key.get("independence_resolution") for r in rows if r.key))}


def build(root: Path) -> dict:
    rows, meta = load_rows(root)
    table = classify(rows)
    fams = Counter(r.x["source_family_id"] for r in rows)
    full = [t["field"] for t in table if t["counts"][P] == t["total"]]
    part = [t["field"] for t in table if 0 < t["counts"][P] < t["total"] or (t["counts"][P] == 0 and t["counts"][C] > 0)]
    never = [t["field"] for t in table if t["counts"][P] == 0 and t["counts"][C] == 0 and t["counts"][A] < t["total"]]
    absent = [t["field"] for t in table if t["counts"][A] == t["total"]]
    other0 = [t["field"] for t in table if t["field"] not in full + part + never + absent]
    summary = {"fields_total": len(table), "ssot_203_2_lines": len({t["ssot_line"] for t in table}),
               "carried_on_every_row": len(full), "populated_on_some_rows": len(part), "in_schema_but_never_populated": len(never),
               "no_field_exists": len(absent), "other": len(other0),
               "lists": {"carried_on_every_row": full, "populated_on_some_rows": part, "in_schema_but_never_populated": never, "no_field_exists": absent, "other": other0}}
    return {"record": "EVD_FIELD_CONFORMANCE_203_2_S178", "tool_version": TOOL_VERSION, "status": "AI_DRAFTED_PROPOSED_UNREVIEWED",
            "contains_text": False, "contains_ids": False, "counts_as_human_gate": False,
            "scope": {"ssot_section": "203.2 canonical process-event table (minimum schema)", "rows": len(rows), "export_version": "evd_export@1.0.0",
                      "rows_by_source_family": dict(sorted(fams.items())), "ledger_sha256_evd": meta["ledger_sha256"],
                      "expected_rows": 17978, "rows_equal_export_v1_count": len(rows) == 17978},
            "status_legend": {"PRESENT": "row carries a stated value", "CENSORED_BOUND_ONLY": "only a one-sided bound is stated",
                              "UNKNOWN": "field has a home; row carries explicit UNKNOWN / null (never 0, never imputed)",
                              "NOT_APPLICABLE": "field does not apply to this row by form", "ABSENT": "no field of that meaning exists in the ledger schemas or the export"},
            "carrier_legend": CARRIERS, "table": table, "summary": summary, "export_v2_lineage": v2_lineage_counts(rows),
            "inputs": {f"ledgers/data/{n}.jsonl": sha256_file(root / "ledgers" / "data" / f"{n}.jsonl") for n in ("EVD", "COND", "SRC", "SVAR", "PROC")} | {KEYS: sha256_file(root / KEYS)}}


def render_csv(d: dict) -> str:
    import io
    fams = sorted(d["scope"]["rows_by_source_family"])
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["ssot_203_2_line", "field", "group", "carrier", "match", *STATUSES, "total", *[f"PRESENT_{f}" for f in fams], "note"])
    for t in d["table"]:
        w.writerow([t["ssot_line"], t["field"], t["group"], t["carrier"], t["match"], *[t["counts"][s] for s in STATUSES], t["total"],
                    *[t["by_source_family"].get(f, {}).get(P, 0) for f in fams], t["note"]])
    return buf.getvalue()


def render_md(d: dict) -> str:
    s, sc = d["summary"], d["scope"]
    rows = [[t["field"], t["carrier"], t["match"], *[t["counts"][x] for x in STATUSES]] for t in d["table"]]
    v2 = d["export_v2_lineage"]
    out = ["# EVD rows vs the SSOT 203.2 process-event schema: field-by-field conformance (S178, T2-C01-R1)", "",
           "Status: AI_DRAFTED / PROPOSED, **not reviewed** (the board asks Kush to review). Counts only, no recipe or paper text. "
           f"`tools/s178_evd_conformance.py` ({TOOL_VERSION}); deterministic. Every row of this table sums to **{sc['rows']:,}** = the export v1 row count (asserted).", "",
           f"Source families: {sc['rows_by_source_family']}. All rows are tier E3, UNVERIFIED or AI_PRECHECKED, COND_UNAUDITED (07.A condition-audit gate not passed).", "",
           "## What the D1 claim can say", "",
           f"- The 203.2 minimum schema has {s['ssot_203_2_lines']} lines, {s['fields_total']} fields once the value / range / type lines are split.",
           f"- **Carried with a value on every row ({s['carried_on_every_row']}):** " + ", ".join(s["lists"]["carried_on_every_row"]) + ".",
           f"- **Populated on some rows only ({s['populated_on_some_rows']}):** " + ", ".join(s["lists"]["populated_on_some_rows"]) + ".",
           f"- **In the schema but never populated ({s['in_schema_but_never_populated']}):** " + ", ".join(s["lists"]["in_schema_but_never_populated"]) + ". No row carries a value for these (UNKNOWN, or NOT_APPLICABLE where the form makes it moot).",
           f"- **No field exists ({s['no_field_exists']}):** " + ", ".join(s["lists"]["no_field_exists"]) + ". (split_id is absent from export v1 only; export v2 adds split_group_id on every row, a SCRATCH_PROVISIONAL assignment, see below.)",
           (f"- Other ({s['other']}): " + ", ".join(s["lists"]["other"]) + ".") if s["other"] else "- Other: none.", "",
           "## Table", "",
           "Statuses: PRESENT = value stated; CENSORED_BOUND_ONLY = only a one-sided bound; UNKNOWN = explicit UNKNOWN/null (never 0, never imputed); NOT_APPLICABLE = does not apply by form; ABSENT = no such field in the schemas or export. "
           "Carrier: X export v1 column, XC export v1 plus COND join, C COND record only (v1 keeps the completeness mask), L EVD ledger only, J joined ledger, V2 export v2 column, - none.", "",
           md_table(["field", "carrier", "match", *STATUSES], rows, align_right=tuple(range(3, 3 + len(STATUSES)))), "",
           "Notes per field, per-source-family PRESENT counts and the detail codes are in the CSV and JSON next to this file.", "",
           "## Export v2 (not part of v1; for the split_id and study_id lines)", "",
           f"- split_group_id on {v2['split_group_id_present']:,} of {v2['rows_with_v2_key_record']:,} rows ({v2['distinct_split_group_ids']:,} distinct groups); assignment status {v2['assignment_status']}.",
           f"- study_id: v1 `study_ids` is filled on 3,870 rows, v2 `study_id` on {v2['study_id_present_v2']:,} rows (the other {3870 - v2['study_id_present_v2']} Phenol-Explorer rows have no resolvable publication); lineage study_id status {v2['lineage_study_id_status']}; independence resolution {v2['independence_resolution']}.", "",
           "## Findings that change other documents", "",
           "1. COND has a `water_activity` field (and `ph_initial`, `ph_final`, `moisture`, `oxygen`, `agitation`, `tool_ids`, `geometry`); none is populated on any ACTIVE row. "
           "The dataset card's wording `NOT_IN_COND_SCHEMA` for water activity is true only of the completeness mask, not of the COND schema.",
           "2. The completeness mask labels a one-sided stated temperature (for example \"above 75 C\", GT_STATED) as RANGE, so the card's temperature `RANGE 3,585` mixes true two-sided ranges with one-sided bounds. "
           "In the COND temperature entries the split is shown by the T_value row (CENSORED_BOUND_ONLY) against T_lo / T_hi (PRESENT).",
           "3. `doi_or_citation` is exact only for the Phenol-Explorer publications (DOI); USDA and Bognar rows cite one database record each.", ""]
    return "\n".join(out)


def run(out_dir: Path, root: Path = ROOT) -> dict:
    before = protected_hashes(root)
    d = build(root)
    assert before == protected_hashes(root), "protected ledger changed during run"
    d["protected_ledgers_unchanged_during_run"] = True
    h = {"json": write_new_or_same(out_dir / "evd_field_conformance_203_2_v1.json", dumps(d)),
         "csv": write_new_or_same(out_dir / "evd_field_conformance_203_2_v1.csv", render_csv(d)),
         "md": write_new_or_same(out_dir / "evd_field_conformance_203_2_v1.md", render_md(d))}
    return {"sha256": h, "rows": d["scope"]["rows"], "fields": d["summary"]["fields_total"], "summary": {k: v for k, v in d["summary"].items() if k != "lists"}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--selfcheck", action="store_true", help="run twice into scratch dirs and compare hashes")
    a = ap.parse_args(argv)
    if a.selfcheck:
        with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
            r1, r2 = run(Path(t1)), run(Path(t2))
        print(dumps({"selfcheck": "IDENTICAL" if r1 == r2 else "DIFFERENT", "run1": r1, "run2": r2}))
        return 0 if r1 == r2 else 1
    print(dumps(run(ROOT / a.out_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
