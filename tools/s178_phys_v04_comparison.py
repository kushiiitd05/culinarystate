#!/usr/bin/env python
"""v03 -> v04 comparison of the non-BBC physical layers from the counts-only run reports (S178 PHYS2). DRAFT, AI_DRAFTED.

Reads the committed reports under reports/step26 (heat L1 S176_v02 -> S178_v04, heat L2 S177_v03 -> S178_v04, non-heat L1 S176 -> S178_v04,
non-heat L2 S177_v03 -> S178_v04) for FOODCOM, GUTENBERG_SEGMENT, WIKIBOOKS and TASTESET and writes one counts-only JSON and one table. The
Layer 1 heat layer was not re-run in S177, so its "v03" baseline is the S176 v02 census (L1 code 0.1.0). Nothing here is a new measurement:
every number is read from a run report; ``source_report_sha256`` names each input.

    python tools/s178_phys_v04_comparison.py --out reports/s178/phys/v03_to_v04_comparison_S178.json \
        --out-md reports/s178/phys/v03_to_v04_comparison_S178.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

FAMILIES = ("FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS", "TASTESET")
R = ROOT / "reports/step26"
SOURCES = {
    "heat_l1": ("binding_census_L1_{f}_full_S176_v02.json", "binding_census_L1_{f}_full_S178_v04.json"),
    "heat_l2": ("scenario_L2_{f}_full_S177_v03.json", "scenario_L2_{f}_full_S178_v04.json"),
    "nonheat_l1": ("nonheat_L1_{f}_full_S176.json", "nonheat_L1_{f}_full_S178_v04.json"),
    "nonheat_l2": ("nonheat_L2_{f}_full_S177_v03.json", "nonheat_L2_{f}_full_S178_v04.json")}
STATED_BUCKETS = ("100_TO_105", "105_TO_120", "120_TO_150", "ABOVE_150")


def _load(name: str) -> tuple[dict, str]:
    p = R / name
    return json.loads(p.read_text(encoding="utf-8")), hashlib.sha256(p.read_bytes()).hexdigest()


def _g(d, *path, default=0):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


def _pair(old, new) -> dict:
    return {"before": old, "after": new, "delta": (new - old) if isinstance(old, (int, float)) and isinstance(new, (int, float)) else None}


def heat_l1(a: dict, b: dict) -> dict:
    out = {k: _pair(a[k], b[k]) for k in ("recipes_sampled", "heat_events", "driver_ready_events", "driver_bounded_events", "contract_bindings",
                                          "gas_mark_only_events")}
    basis = {}
    for axis in ("temperature_profile", "duration", "medium", "lid_state", "start_mode", "piece_size_class", "matrix_class"):
        keys = sorted(set(_g(a, "input_basis", axis, default={})) | set(_g(b, "input_basis", axis, default={})))
        basis[axis] = {k: _pair(_g(a, "input_basis", axis, k), _g(b, "input_basis", axis, k)) for k in keys}
    out["input_basis"] = basis
    out["matrix_class_status"] = {k: _pair(_g(a, "input_status", "matrix_class", k), _g(b, "input_status", "matrix_class", k))
                                  for k in sorted(set(_g(a, "input_status", "matrix_class", default={})) | set(_g(b, "input_status", "matrix_class", default={})))}
    out["new_in_v04"] = {"matrix_groups_events_by_member_count": _g(b, "matrix_groups", "events_by_member_group_count", default={}),
                         "events_without_any_food_group": _g(b, "matrix_groups", "events_without_any_food_group"),
                         "temperature_differs_from_v01_by_reason_and_family": _g(b, "temperature_ownership",
                                                                                 "events_where_temperature_differs_from_v01_by_reason_and_family", default={}),
                         "events_with_ambient_temperature_by_family": _g(b, "temperature_ownership", "events_with_ambient_temperature_by_family", default={}),
                         "aqueous_events_with_stated_temperature_by_bucket_v04": _g(b, "temperature_ownership",
                                                                                     "aqueous_medium_events_with_stated_temperature_by_bucket", default={}),
                         "endpoint_heat_events_with_cue": _g(b, "endpoint_cues", "heat_events_with_cue"),
                         "endpoint_cues_per_event": _g(b, "endpoint_cues", "cues_per_event", default={}),
                         "provenance_axes": _g(b, "provenance_axes", default={}),
                         "exceptions_by_class": _g(b, "exceptions_by_class", default={})}
    return out


def heat_l2(a: dict, b: dict) -> dict:
    ca, cb = a["counts"], b["counts"]
    out = {"layer_version": {"before": a["layer_version"], "after": b["layer_version"]},
           "status": {k: _pair(_g(ca, "status", k), _g(cb, "status", k)) for k in sorted(set(ca.get("status", {})) | set(cb.get("status", {})))},
           "transition": {k: _pair(_g(ca, "transition", k), _g(cb, "transition", k))
                          for k in sorted(set(ca.get("transition", {})) | set(cb.get("transition", {})))},
           "typical_core_reaches_70": {k: _pair(_g(ca, "typical_core_reaches_70", k), _g(cb, "typical_core_reaches_70", k))
                                       for k in sorted(set(_g(ca, "typical_core_reaches_70", default={})) | set(_g(cb, "typical_core_reaches_70", default={})))},
           "core_known_typical": {k: _pair(_g(ca, "core_known", "TYPICAL", k), _g(cb, "core_known", "TYPICAL", k)) for k in ("True", "False")},
           "stated_liquid_lifted_typical": _pair(_g(ca, "stated_liquid_above_tboil", "TYPICAL"), _g(cb, "stated_liquid_above_tboil", "TYPICAL")),
           "stated_liquid_lifted_typical_by_stated_c": {k: _pair(_g(ca, "stated_liquid_above_tboil_by_stated_c", "TYPICAL", k),
                                                                _g(cb, "stated_liquid_above_tboil_by_stated_c", "TYPICAL", k)) for k in STATED_BUCKETS},
           "cap_flag_typical": {k: _pair(_g(ca, "cap_flag_typical", k), _g(cb, "cap_flag_typical", k))
                                for k in sorted(set(ca.get("cap_flag_typical", {})) | set(cb.get("cap_flag_typical", {})))},
           "surface_state_typical": {k: _pair(_g(ca, "surface_state", "TYPICAL", k), _g(cb, "surface_state", "TYPICAL", k))
                                     for k in sorted(set(_g(ca, "surface_state", "TYPICAL", default={})) | set(_g(cb, "surface_state", "TYPICAL", default={})))}}
    blk = b.get("v03_to_v04", {}).get("counts", {})
    out["v03_to_v04_event_comparison"] = {"events": blk.get("events"), "counts": {k: v for k, v in blk.items() if k not in ("flag_added", "flag_removed", "events")},
                                          "flag_added_typical": blk.get("flag_added", {}).get("TYPICAL", {}),
                                          "flag_removed_typical": blk.get("flag_removed", {}).get("TYPICAL", {})}
    out["new_in_v04"] = {"stated_liquid_typical_by_stated_c_and_member": _g(cb, "stated_liquid_typical_by_stated_c_and_member", default={}),
                         "stated_liquid_typical_core_computed_by_stated_c": _g(cb, "stated_liquid_typical_core_computed_by_stated_c", default={}),
                         "ambient_temperature_not_used_as_liquid_t_typical": _g(cb, "ambient_temperature_not_used_as_liquid_t_typical")}
    return out


def nonheat_l1(a: dict, b: dict) -> dict:
    fams = sorted(set(a.get("events_by_family", {})) | set(b.get("events_by_family", {})))
    return {"recipes_sampled": _pair(a["recipes_sampled"], b["recipes_sampled"]),
            "events_by_family": {f: _pair(_g(a, "events_by_family", f), _g(b, "events_by_family", f)) for f in fams},
            "driver_ready_events_by_family": {f: _pair(_g(a, "driver_ready_events_by_family", f), _g(b, "driver_ready_events_by_family", f)) for f in fams},
            "any_l1_value_by_family": {f: _pair(_g(a, "any_l1_value_by_family", f), _g(b, "any_l1_value_by_family", f)) for f in fams},
            "prior_heat_link_basis": {k: _pair(_g(a, "prior_heat_link_basis", k), _g(b, "prior_heat_link_basis", k))
                                      for k in sorted(set(a.get("prior_heat_link_basis", {})) | set(b.get("prior_heat_link_basis", {})))},
            "binder_version": {"before": a.get("binder_version"), "after": b.get("binder_version")}}


def nonheat_l2(a: dict, b: dict) -> dict:
    ca, cb = a["counts"], b["counts"]
    fams = sorted(set(ca["events_by_family"]) | set(cb["events_by_family"]))
    blk = b.get("v03_to_v04", {}).get("counts", {})
    changed = {}
    for fam, d in blk.get("status", {}).items():
        changed[fam] = sum(v for k, v in d.items() if k.split("__TO__")[0] != k.split("__TO__")[-1])
    return {"layer_version": {"before": a["layer_version"], "after": b["layer_version"]},
            "events_by_family": {f: _pair(_g(ca, "events_by_family", f), _g(cb, "events_by_family", f)) for f in fams},
            "computed_by_family": {f: _pair(_g(ca, "l2_driver_computed_by_family", f), _g(cb, "l2_driver_computed_by_family", f)) for f in fams},
            "qualitative_or_conditions_by_family": {f: _pair(_g(ca, "l2_qualitative_or_conditions_by_family", f),
                                                             _g(cb, "l2_qualitative_or_conditions_by_family", f)) for f in fams},
            "events_whose_status_changed_by_family": changed,
            "v03_to_v04_counts": {k: v for k, v in blk.items() if k != "status"},
            "errors_by_class": _g(cb, "errors_by_class", default={})}


FN = {"heat_l1": heat_l1, "heat_l2": heat_l2, "nonheat_l1": nonheat_l1, "nonheat_l2": nonheat_l2}


def superseded() -> list[dict]:
    rows = []
    for kind, (old, _) in SOURCES.items():
        for f in FAMILIES:
            p = R / old.format(f=f)
            if p.exists():
                rows.append({"output": f"reports/step26/{old.format(f=f)}", "kind": kind, "status": "SUPERSEDED_BY_S178_v04"})
    return rows


def markdown(rep: dict) -> str:
    L = ["# v03 -> v04 comparison, non-BBC physical layers (S178 PHYS2)", "",
         "Status: DRAFT / AI_DRAFTED, counts only, read from the run reports named in `source_report_sha256`. The heat Layer 1 was not re-run in S177, so its "
         "baseline is the S176 v02 census (Layer 1 0.1.0). Layer 2 heat 0.3.0 -> 0.4.0, non-heat Layer 2 0.3.0 -> 0.4.0, non-heat Layer 1 0.1.0 -> 0.2.0.", ""]
    for fam, d in rep["families"].items():
        h1, h2, n1, n2 = d["heat_l1"], d["heat_l2"], d["nonheat_l1"], d["nonheat_l2"]
        L += [f"## {fam}", ""]
        L += ["| quantity | before | after | delta |", "|---|---:|---:|---:|"]
        for k in ("heat_events", "driver_ready_events", "driver_bounded_events", "contract_bindings"):
            p = h1[k]
            L.append(f"| heat L1 {k} | {p['before']} | {p['after']} | {p['delta']} |")
        for k, p in h1["input_basis"]["temperature_profile"].items():
            L.append(f"| heat L1 temperature basis {k} | {p['before']} | {p['after']} | {p['delta']} |")
        for k, p in h2["status"].items():
            L.append(f"| heat L2 status {k} | {p['before']} | {p['after']} | {p['delta']} |")
        p = h2["stated_liquid_lifted_typical"]
        L.append(f"| heat L2 stated-liquid events lifted (TYPICAL) | {p['before']} | {p['after']} | {p['delta']} |")
        for k, p in h2["stated_liquid_lifted_typical_by_stated_c"].items():
            L.append(f"| heat L2 stated-liquid lifted, stated T {k} | {p['before']} | {p['after']} | {p['delta']} |")
        for k, p in h2["typical_core_reaches_70"].items():
            L.append(f"| heat L2 TYPICAL core reaches 70 C = {k} | {p['before']} | {p['after']} | {p['delta']} |")
        for k in ("TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER", "ALL_MEMBERS_DRY_CLASS", "MATRIX_UNKNOWN_MOIST_ASSUMED", "MATRIX_AMBIGUOUS_MOIST_ASSUMED",
                  "MATRIX_DRY_CLASS_UNCAPPED"):
            p = h2["cap_flag_typical"].get(k)
            if p:
                L.append(f"| heat L2 cap flag {k} (TYPICAL) | {p['before']} | {p['after']} | {p['delta']} |")
        for f, p in n1["events_by_family"].items():
            L.append(f"| non-heat L1 events {f} | {p['before']} | {p['after']} | {p['delta']} |")
        for f, p in n2["computed_by_family"].items():
            L.append(f"| non-heat L2 computed {f} | {p['before']} | {p['after']} | {p['delta']} |")
        L.append("")
        ev = h2["v03_to_v04_event_comparison"]
        L.append(f"Heat L2 per-event comparison over {ev['events']} events: bath temperature changed (TYPICAL) "
                 f"{ev['counts'].get('bath_c_changed', {}).get('TYPICAL', 0)}; core end temperature changed "
                 f"{ev['counts'].get('changed', {}).get('TYPICAL', {}).get('core_end_c', 0)}; non-heat events whose status changed {sum(n2['events_whose_status_changed_by_family'].values())}.")
        L.append("")
    L += ["## SUPERSEDED outputs", "", "The v04 files replace these reports for the non-BBC families; the old files are kept for the audit trail and are not read by any v04 tool.", ""]
    L += [f"- `{r['output']}` ({r['kind']})" for r in rep["superseded"]]
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    a = ap.parse_args(argv)
    for p in (a.out, a.out_md):
        if p.exists():
            ap.error(f"refusing to overwrite {p}")
    fams, shas = {}, {}
    for f in FAMILIES:
        fams[f] = {}
        for kind, (old, new) in SOURCES.items():
            ja, sa = _load(old.format(f=f))
            jb, sb = _load(new.format(f=f))
            shas[old.format(f=f)], shas[new.format(f=f)] = sa, sb
            fams[f][kind] = FN[kind](ja, jb)
    rep = {"record": "PHYSICAL_LAYERS_V03_TO_V04_COMPARISON", "status": "AI_DRAFTED_COUNTS_ONLY", "contains_ids": False, "contains_text": False,
           "citable": False, "counts_as_human_gate": False, "families": fams,
           "source_report_sha256": {re.sub(r"[^A-Za-z0-9_]", "_", k): v for k, v in sorted(shas.items())},
           "superseded": superseded(), "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    D.write_report(a.out, rep, root=ROOT)
    a.out_md.write_text(markdown(rep), encoding="utf-8")
    print(json.dumps({"families": list(fams), "report_sha256": hashlib.sha256(a.out.read_bytes()).hexdigest()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
