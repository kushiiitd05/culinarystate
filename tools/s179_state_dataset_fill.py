#!/usr/bin/env python3
"""D-110 / plan L2: state dataset fill. One row per recipe x step event with the State-contract columns; every cell is
{"v": value, "b": basis} or {"v": null, "u": UNKNOWN reason}. Rows go to a git-ignored directory; the committed output
is the per-column fill-rate table (VALUE_BY_BASIS vs UNKNOWN_BY_REASON) per family.

Sources: Rung A (event, D-102 v2 state type, process, inputs/outputs, step position); physics v06 L1 inputs (medium,
temperature, duration, matrix, lid, piece size) joined by (recipe_id, event_id); L2 TYPICAL scenario (food T =
min(bath, cap), duration, status); D-106 AA formula retention when in domain (FORMULA_RESEARCH_ONLY).

    python tools/s179_state_dataset_fill.py --families A1_BBC_GOOD_FOOD --l1 data/derived/physical_L1_full_S179v06 \
        --l2 data/derived/physical_L2_full_S179v06 --rows-dir data/derived/state_dataset_v1/BBC \
        --out reports/s179/state_dataset_fill_BBC_2026-11-13.json
"""
from __future__ import annotations

import argparse
import glob
import gzip
import importlib.util
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evaluation.runga_typed_vs_gold import map_event_v2  # noqa: E402

_fc_spec = importlib.util.spec_from_file_location("fc", ROOT / "tools" / "s179_formula_census.py")
FC = importlib.util.module_from_spec(_fc_spec)
_fc_spec.loader.exec_module(FC)

COLUMNS = ("state_type", "process_id", "process_family", "step_decile", "n_inputs", "n_outputs", "medium", "temperature_C",
           "duration_min", "matrix_class", "lid_state", "piece_size_class", "thermal_state", "food_T_typical_C",
           "moisture_cap_C", "aa_retention_typical")
L1_AXES = {"medium": "medium", "temperature_C": "temperature_profile", "duration_min": "duration",
           "matrix_class": "matrix_class", "lid_state": "lid_state", "piece_size_class": "piece_size_class"}
LABELS = ["DERIVED_VIEW_NOT_LEDGER", "SCENARIO_DEFAULT_WHERE_STATED", "FORMULA_RESEARCH_ONLY", "NO_HUMAN_SIGNOFF_D085"]


def V(v, b):
    return {"v": v, "b": b}


def U(reason):
    return {"v": None, "u": reason}


def _load(d: Path) -> dict:
    out = {}
    for f in sorted(glob.glob(str(d / "**" / "*.jsonl"), recursive=True)):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    out[(r["recipe_id"], r["event_id"])] = r
    return out


def l1_cell(r1, axis):
    if r1 is None:
        return U("NOT_A_HEAT_EVENT")
    x = (r1.get("inputs") or {}).get(axis) or {}
    if x.get("value") is None:
        return U(x.get("reason") or "UNKNOWN")
    return V(x["value"], x.get("basis") or x.get("status"))


def l2_cells(r1, r2, fit):
    if r2 is None:
        return {"thermal_state": U("NOT_A_HEAT_EVENT"), "food_T_typical_C": U("NOT_A_HEAT_EVENT"),
                "moisture_cap_C": U("NOT_A_HEAT_EVENT"), "aa_retention_typical": U("NOT_A_HEAT_EVENT")}
    st = r2.get("status")
    sc = (r2.get("scenarios") or {}).get("TYPICAL") or {}
    out = {"thermal_state": V(st, "PHYSICS_V06_L2")}
    if st == "SCENARIO_COMPUTED" and sc.get("bath_c") is not None:
        cap = sc.get("t_cap_c")
        out["food_T_typical_C"] = V(float(min(sc["bath_c"], cap)) if cap is not None else float(sc["bath_c"]), "SCENARIO_DEFAULT")
        out["moisture_cap_C"] = V(cap, "SCENARIO_DEFAULT") if cap is not None else U("NO_MOISTURE_CAP")
    else:
        out["food_T_typical_C"] = U(st or "SCENARIO_UNKNOWN")
        out["moisture_cap_C"] = U(st or "SCENARIO_UNKNOWN")
    ok, why, T, t = FC.gate(r1 or {}, r2, "TYPICAL", liquid_required=True)
    out["aa_retention_typical"] = V(round(FC.retention(fit, T, t)[0], 4), "FORMULA_RESEARCH_ONLY") if ok else U(why)
    return out


def rows_for(rec, rung, schema, proc_family, L1, L2, fit):
    from culinarystate.extraction.interfaces import SourceText
    raw = "\n".join(str(s) for s in (rec.get("steps") or []))
    if not raw.strip():
        return []
    events = list(rung.run(SourceText.from_raw("SDF", raw), rung.config(), schema=schema).graph.events)
    rid, out = rec["recipe_id"], []
    for i, e in enumerate(events):
        proc = next((a.value for a in e.attributes if a.field == "proc_id"), None)
        pf = proc_family.get(proc)
        r1, r2 = L1.get((rid, e.event_id)), L2.get((rid, e.event_id))
        row = {"recipe_id": rid, "event_id": e.event_id, "family": rec.get("source_family"),
               "state_type": V(map_event_v2(e, pf), "D-102_V2") if map_event_v2(e, pf) else U("UNMAPPED_STRUCTURE"),
               "process_id": V(proc, "RUNG_A") if proc else U("NO_PROC"),
               "process_family": V(pf, "PROC_LEDGER") if pf else U("NO_PROC"),
               "step_decile": V(min(9, 10 * i // max(len(events), 1)), "RUNG_A"),
               "n_inputs": V(len(e.consumes), "RUNG_A"), "n_outputs": V(len(e.produces), "RUNG_A")}
        for col, axis in L1_AXES.items():
            row[col] = l1_cell(r1, axis)
        row.update(l2_cells(r1, r2, fit))
        out.append(row)
    return out


def main(argv=None) -> int:
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.lotstate import corpus as C
    from culinarystate.quantity.rc2_dryrun import load_schema
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="+", required=True)
    ap.add_argument("--l1", required=True)
    ap.add_argument("--l2", required=True)
    ap.add_argument("--rows-dir", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out, rdir = Path(a.out), Path(a.rows_dir)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    if rdir.exists() and any(rdir.iterdir()):
        sys.exit("rows dir must be new or empty")
    rdir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    fit = json.loads((ROOT / FC.FIT).read_text())["fit"]
    proc_family = {}
    for line in (ROOT / "ledgers/data/PROC.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            proc_family[r["id"]] = r.get("family") or None
    L1, L2 = _load(Path(a.l1)), _load(Path(a.l2))
    rung, schema = RungA(), load_schema()
    fill = defaultdict(lambda: defaultdict(Counter))
    fill_heat = defaultdict(lambda: defaultdict(Counter))       # physics columns judged over heat-event rows only
    n_rec = n_rows = exc = 0
    joined = Counter()
    part, buf = 0, []

    def flush():
        nonlocal part, buf
        if buf:
            with gzip.open(rdir / f"part-{part:05d}.jsonl.gz", "wt", encoding="utf-8") as g:
                g.write("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in buf))
            part, buf = part + 1, []

    for k, rec in enumerate(C.stream(tuple(a.families), ROOT)):
        if a.limit and k >= a.limit:
            break
        n_rec += 1
        try:
            rows = rows_for(rec, rung, schema, proc_family, L1, L2, fit)
        except Exception:
            exc += 1
            continue
        for r in rows:
            fam = r["family"]
            joined[fam] += (r["recipe_id"], r["event_id"]) in L1
            heat = (r["recipe_id"], r["event_id"]) in L2
            for col in COLUMNS:
                c = r[col]
                for tgt in ((fill, fill_heat) if heat else (fill,)):
                    if c["v"] is not None:
                        tgt[fam][col]["VALUE:" + str(c.get("b"))] += 1
                    else:
                        tgt[fam][col]["UNKNOWN:" + str(c.get("u"))] += 1
        n_rows += len(rows)
        buf.extend(rows)
        if len(buf) >= 50000:
            flush()
    flush()
    def _rate(f):
        return {fam: {col: round(100 * sum(v for k, v in cnt.items() if k.startswith("VALUE:")) / max(1, sum(cnt.values())), 2)
                      for col, cnt in cols.items()} for fam, cols in f.items()}
    table = {fam: {col: {k: v for k, v in cnt.items() if v} for col, cnt in cols.items()} for fam, cols in fill.items()}
    rate = {fam: {col: round(100 * sum(v for k, v in cnt.items() if k.startswith("VALUE:")) / max(1, sum(
        v for k, v in cnt.items() if k.startswith(("VALUE:", "UNKNOWN:")))), 2) for col, cnt in cols.items()}
        for fam, cols in fill.items()}
    rec = {"record": "STATE_DATASET_FILL", "decision": "D-110", "labels": LABELS, "approver": "ksh+prv (AI, D-085)",
           "families_requested": a.families, "recipes": n_rec, "rows": n_rows, "exceptions": exc,
           "heat_rows_joined_to_physics": dict(joined), "columns": list(COLUMNS),
           "value_rate_pct": rate, "value_rate_pct_heat_rows": _rate(fill_heat), "fill_by_basis_or_reason": table, "rows_dir": rdir.name, "row_parts": part,
           "wall_seconds": round(time.time() - t0, 1), "contains_text": False, "contains_ids": False,
           "scientific_gate_pass": False}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x") as f:
        f.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"recipes": n_rec, "rows": n_rows, "exceptions": exc, "joined": dict(joined)}), round(time.time() - t0, 1), "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
