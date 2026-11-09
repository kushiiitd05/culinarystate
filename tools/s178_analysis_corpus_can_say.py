#!/usr/bin/env python3
"""S178 ANALYSIS lane, T4-C04-R1: "what the corpus can say" about stated time / temperature / size / medium.

Counts only. Two inputs, both read-only:

  1. committed census JSONs under reports/step26/ (heat L1, non-heat L1, heat L2 and non-heat L2, all S178 v04 since
     FIX-GOV; they were S176_v02 / S176 / S177_v03 before). Every headline number in the report is a value read from one
     of these files, and its path is printed beside it. Every input path is checked against
     registry/superseded_outputs_S176.csv first (culinarystate.governance_superseded): a superseded input stops the tool.
     The BBC heat L1 file (S173, binder 0.1.0) is superseded and has no v04 re-run on this server (D-003), so BBC is
     not in the tables;
  2. the per-event L1 / L2 records under data/derived/ (git-ignored). They are used ONLY to build the cross-tabs
     that the committed JSONs cannot give (the joint "stated time AND stated temperature", by process, and the
     UNKNOWN reasons of the heat L2 events). The aggregate is reconciled against the committed JSONs; any
     mismatch is reported as RECONCILIATION_FAILED and the tool exits non-zero.

No recipe text, id or span is read into the output: only integer counts keyed by source family, process family,
PROC id (a registry id) and fixed status / reason codes.

  python tools/s178_analysis_corpus_can_say.py --aggregate --workers 12          # writes data/derived/s178_analysis/*.json
  python tools/s178_analysis_corpus_can_say.py --build                           # writes reports/s178/analysis/*
  python tools/s178_analysis_corpus_can_say.py --aggregate --sample-parts 2 --out-agg /tmp/x   # smoke test

Everything is AI_DRAFTED / PROPOSED, NON_CITABLE, REAL_BASE_SAMPLE_COUNTS_NOT_GOLD. Not a gold score, not a human gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TOOL_VERSION = "s178-corpus-can-say-0.2.0-draft"
LAYER_TAG = "S178 v04"           # the census / record version every input belongs to (FIX-GOV repoint)
STEP26 = "reports/step26"
DERIVED = "data/derived"
OUT_DIR = "reports/s178/analysis"
AGG_DIR = "data/derived/s178_analysis"
SOURCES = ("FOODCOM", "WIKIBOOKS", "GUTENBERG_SEGMENT", "TASTESET")
HEAT_FAMILIES = ("DRY_HEAT", "FAT_HEAT", "HEAT_GENERAL", "WET_HEAT")
NH_FAMILIES = ("COOLING", "FERMENT_LEAVEN", "MECHANICAL_CUT", "MECHANICAL_MIX", "PRESERVATION", "RESTING",
               "SEPARATION", "STORAGE")
HEAT_L1_DIR = "physical_L1_full_S178v04"
HEAT_L2_DIR = "physical_L2_full_S178v04"
NH_L1_DIR = "physical_NH_L1_{src}_full_S178v04"
HEAT_INPUTS = ("duration", "temperature_profile", "medium", "lid_state", "start_mode", "piece_size_class",
               "water_ratio", "matrix_class")
NH_TEMP_INPUTS = ("medium_temperature", "target_food_temperature")
STATED_STATUS = ("MEASURED", "RANGE")
NH_DUR_STATED = ("MEASURED", "RANGE", "BOUND_LOWER", "BOUND_UPPER")


# ----------------------------------------------------------------------------- aggregation of derived records
def _key(*parts) -> str:
    return "|".join(str(p) for p in parts)


def heat_event_keys(l1: dict, l2: dict | None) -> list[str]:
    """Flat count keys for one heat L1 event (and its aligned L2 v03 record). Pure function, unit-tested."""
    src, fam, pid = l1["source_family"], l1["family"], l1["process_id"]
    inp = l1["inputs"]
    dur, tmp = inp["duration"], inp["temperature_profile"]
    t_stated = dur["status"] in STATED_STATUS
    tbasis = tmp["basis"] or "NONE"
    tclass = tbasis if tmp["status"] != "UNKNOWN" else "UNKNOWN"
    base = (src, fam, pid)
    out = [_key(*base, "n", "-")]
    out.append(_key(*base, "dur", dur["status"]))
    out.append(_key(*base, "temp", tmp["status"], tbasis))
    out.append(_key(*base, "joint", "t" + ("S" if t_stated else "U"), "T:" + tclass))
    if dur["status"] == "RANGE":
        out.append(_key(*base, "dur_range", "-"))
    if tmp["status"] == "RANGE":
        out.append(_key(*base, "temp_range", "-"))
    if l1.get("oven_setpoint_code"):
        out.append(_key(*base, "gas_mark", "T:" + tclass))
    for name in ("medium", "lid_state", "start_mode", "piece_size_class", "water_ratio", "matrix_class"):
        x = inp[name]
        out.append(_key(*base, "in:" + name, x["status"], x["basis"] or "NONE"))
    if l2 is not None:
        out.append(_key(*base, "l2status", l2["status"]))
        if l2["status"] == "SCENARIO_UNKNOWN":
            miss = sorted(l2.get("missing") or [])
            for m in miss:
                out.append(_key(*base, "l2missing", m))
            out.append(_key(*base, "l2missing_set", "+".join(miss) if miss else "NONE"))
    return out


def nh_event_keys(r: dict) -> list[str]:
    src, fam, role = r["source_family"], r["nh_family"], r["process_role"]
    base = (src, fam, role)
    inp = r["inputs"]
    out = [_key(*base, "n", "-")]
    dur = inp.get("duration")
    t_stated = bool(dur) and dur["status"] in NH_DUR_STATED
    if dur:
        out.append(_key(*base, "dur", dur["status"]))
    temps = [inp[k] for k in NH_TEMP_INPUTS if k in inp]
    has_temp_input = bool(temps)
    T_stated = any(x["status"] in STATED_STATUS for x in temps)
    if has_temp_input:
        out.append(_key(*base, "temp_applicable", "-"))
        out.append(_key(*base, "temp", "STATED" if T_stated else "UNKNOWN"))
        out.append(_key(*base, "joint", "t" + ("S" if t_stated else "U"), "T:" + ("S" if T_stated else "U")))
    for name, x in inp.items():
        if name in ("duration", *NH_TEMP_INPUTS):
            continue
        out.append(_key(*base, "in:" + name, x["status"]))
        if x["status"] == "UNKNOWN" and x.get("reason"):
            out.append(_key(*base, "reason:" + name, x["reason"]))
    for name in ("duration", *NH_TEMP_INPUTS):
        x = inp.get(name)
        if x and x["status"] == "UNKNOWN" and x.get("reason"):
            out.append(_key(*base, "reason:" + name, x["reason"]))
    return out


def _agg_heat_part(args):
    src, idx, root = args
    p1 = Path(root) / DERIVED / HEAT_L1_DIR / src / f"part-{idx:05d}.jsonl"
    p2 = Path(root) / DERIVED / HEAT_L2_DIR / src / f"part-{idx:05d}.jsonl"
    c, bad, n = Counter(), 0, 0
    if not p1.is_file():
        return src, idx, c, 0, 0
    f2 = open(p2, encoding="utf-8") if p2.is_file() else None
    try:
        for line in open(p1, encoding="utf-8"):
            if not line.strip():
                continue
            l1 = json.loads(line)
            l2 = None
            if f2 is not None:
                l2line = f2.readline()
                l2 = json.loads(l2line) if l2line.strip() else None
                if l2 is None or (l2["recipe_id"], l2["event_id"], l2["process_id"]) != (l1["recipe_id"], l1["event_id"], l1["process_id"]):
                    bad += 1
                    l2 = None
            n += 1
            c.update(heat_event_keys(l1, l2))
        if f2 is not None and f2.readline().strip():
            bad += 1
    finally:
        if f2 is not None:
            f2.close()
    return src, idx, c, n, bad


def _agg_nh_part(args):
    src, idx, root = args
    p1 = Path(root) / DERIVED / NH_L1_DIR.format(src=src) / f"part-{idx:05d}.jsonl"
    c, n = Counter(), 0
    if p1.is_file():
        for line in open(p1, encoding="utf-8"):
            if line.strip():
                n += 1
                c.update(nh_event_keys(json.loads(line)))
    return src, idx, c, n, 0


def _parts(root: Path, d: str, src: str, limit: int | None) -> list[int]:
    p = root / DERIVED / d / src
    if not p.is_dir():
        return []
    idx = sorted(int(f.name[5:10]) for f in p.glob("part-*.jsonl"))
    return idx[:limit] if limit else idx


def aggregate(root: Path, workers: int, sample_parts: int | None = None) -> dict:
    import multiprocessing as mp
    check_inputs_not_superseded(root)
    tasks_h = [(s, i, str(root)) for s in SOURCES for i in _parts(root, HEAT_L1_DIR, s, sample_parts)]
    tasks_n = [(s, i, str(root)) for s in SOURCES for i in _parts(root, NH_L1_DIR.format(src=s), "", None)] if False else []
    for s in SOURCES:
        d = root / DERIVED / NH_L1_DIR.format(src=s)
        if d.is_dir():
            idx = sorted(int(f.name[5:10]) for f in d.glob("part-*.jsonl"))
            tasks_n += [(s, i, str(root)) for i in (idx[:sample_parts] if sample_parts else idx)]
    # largest family first so the pool stays busy
    order = {s: k for k, s in enumerate(SOURCES)}
    tasks_h.sort(key=lambda t: (order[t[0]], t[1]))
    tasks_n.sort(key=lambda t: (order[t[0]], t[1]))
    res = {"heat": Counter(), "nh": Counter()}
    meta = {"heat_events": Counter(), "heat_alignment_errors": Counter(), "heat_parts": Counter(),
            "nh_events": Counter(), "nh_parts": Counter()}
    ctx = mp.get_context("fork")
    with ctx.Pool(max(1, workers)) as pool:
        for src, _idx, c, n, bad in pool.imap_unordered(_agg_heat_part, tasks_h, chunksize=1):
            res["heat"].update(c)
            meta["heat_events"][src] += n
            meta["heat_alignment_errors"][src] += bad
            meta["heat_parts"][src] += 1
        for src, _idx, c, n, _bad in pool.imap_unordered(_agg_nh_part, tasks_n, chunksize=1):
            res["nh"].update(c)
            meta["nh_events"][src] += n
            meta["nh_parts"][src] += 1
    out_meta = {k: dict(sorted(v.items())) for k, v in meta.items()}
    out_meta["layer_tag"] = LAYER_TAG
    out_meta["derived_dirs"] = derived_dirs()
    return {"heat": dict(sorted(res["heat"].items())), "nh": dict(sorted(res["nh"].items())), "meta": out_meta}


# ----------------------------------------------------------------------------- reading the aggregate
def split_keys(flat: dict[str, int]) -> dict:
    """{(src, fam, proc): {(metric, v1, v2...): count}}"""
    out: dict[tuple, dict] = defaultdict(dict)
    for k, v in flat.items():
        parts = k.split("|")
        out[tuple(parts[:3])][tuple(parts[3:])] = v
    return out


def rollup(flat: dict[str, int], by: str) -> dict:
    """Sum counts over process, keeping (src, fam) [by='fam'] or (src,) [by='src'] -> {group: {metric_tuple: n}}."""
    out: dict[tuple, Counter] = defaultdict(Counter)
    for k, v in flat.items():
        parts = k.split("|")
        grp = tuple(parts[:2]) if by == "fam" else tuple(parts[:1])
        out[grp][tuple(parts[3:])] += v
    return out


# ----------------------------------------------------------------------------- committed census readers
def read_json(root: Path, rel: str) -> dict:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def heat_census_paths(root: Path) -> dict[str, str]:
    # BBC (A1) has no v04 heat L1 census on this server (D-003); its S173 file is superseded, so it is not read.
    return {s: f"{STEP26}/binding_census_L1_{s}_full_S178_v04.json" for s in SOURCES}


def nh_l1_paths() -> dict[str, str]:
    return {s: f"{STEP26}/nonheat_L1_{s}_full_S178_v04.json" for s in SOURCES}


def heat_l2_paths() -> dict[str, str]:
    return {s: f"{STEP26}/scenario_L2_{s}_full_S178_v04.json" for s in SOURCES}


def nh_l2_paths() -> dict[str, str]:
    return {s: f"{STEP26}/nonheat_L2_{s}_full_S178_v04.json" for s in SOURCES}


def derived_dirs() -> list[str]:
    return [f"{DERIVED}/{HEAT_L1_DIR}", f"{DERIVED}/{HEAT_L2_DIR}", *[f"{DERIVED}/{NH_L1_DIR.format(src=s)}" for s in SOURCES]]


def all_input_paths(root: Path) -> list[str]:
    """Every committed census file and derived record directory this tool reads (checked against the superseded registry)."""
    return [*heat_census_paths(root).values(), *nh_l1_paths().values(), *heat_l2_paths().values(), *nh_l2_paths().values(), *derived_dirs()]


def check_inputs_not_superseded(root: Path) -> None:
    """Raise culinarystate.governance_superseded.SupersededInputError if any input is in registry/superseded_outputs_S176.csv."""
    from culinarystate.governance_superseded import assert_not_superseded
    assert_not_superseded(all_input_paths(root), root=root)


def pct(a: int, b: int) -> float:
    return round(100.0 * a / b, 2) if b else 0.0


def heat_source_row(src: str, d: dict, path: str) -> dict:
    """Source-level heat coverage straight from one committed census JSON (every value is a field of the file)."""
    n = int(d.get("heat_events") or 0)
    ist = d.get("input_status") or {}
    ib = d.get("input_basis") or {}
    dur = ist.get("duration", {})
    tmp = ist.get("temperature_profile", {})
    tb = ib.get("temperature_profile", {})
    row = {"source": src, "census_path": path, "census_version": d.get("census_version"),
           "binder_version": d.get("binder_version"), "recipes_seen": d.get("recipes_seen"),
           "texts_with_steps": d.get("texts_with_steps"), "events": d.get("events"), "heat_events": n,
           "heat_events_by_family": d.get("heat_events_by_family", {}),
           "duration_stated": dur.get("MEASURED", 0) + dur.get("RANGE", 0),
           "duration_measured": dur.get("MEASURED", 0), "duration_range": dur.get("RANGE", 0),
           "duration_unknown": dur.get("UNKNOWN", 0),
           "temperature_any": tmp.get("MEASURED", 0) + tmp.get("RANGE", 0),
           "temperature_range": tmp.get("RANGE", 0), "temperature_unknown": tmp.get("UNKNOWN", 0),
           "temperature_text_stated": tb.get("TEXT_STATED", 0),
           "temperature_carried_setpoint": tb.get("CARRIED_SETPOINT", 0),
           "temperature_physical_definition": tb.get("PHYSICAL_DEFINITION", 0),
           "gas_mark_only_events": d.get("gas_mark_only_events", 0),
           "driver_bounded_events": d.get("driver_bounded_events", 0),
           "driver_ready_events": d.get("driver_ready_events", 0),
           "medium_known": ist.get("medium", {}).get("MEASURED", 0),
           "piece_size_known": ist.get("piece_size_class", {}).get("MEASURED", 0),
           "lid_known": ist.get("lid_state", {}).get("MEASURED", 0),
           "start_mode_known": ist.get("start_mode", {}).get("MEASURED", 0),
           "matrix_class_known": ist.get("matrix_class", {}).get("MEASURED", 0),
           "water_ratio_known": ist.get("water_ratio", {}).get("MEASURED", 0)}
    return row


# ----------------------------------------------------------------------------- reconciliation
def reconcile_heat(src: str, flat_by_src: Counter, census: dict) -> list[str]:
    """Compare the derived-record aggregate with the committed census JSON of the same source. [] means equal."""
    errs: list[str] = []
    n = flat_by_src[("n", "-")]
    if n != census.get("heat_events", 0):
        errs.append(f"{src}: heat events {n} != census {census.get('heat_events', 0)}")
    ist = census.get("input_status") or {}
    for st, c in (ist.get("duration") or {}).items():
        if flat_by_src[("dur", st)] != c:
            errs.append(f"{src}: duration {st} {flat_by_src[('dur', st)]} != {c}")
    for st, c in (ist.get("temperature_profile") or {}).items():
        agg = sum(v for k, v in flat_by_src.items() if k[0] == "temp" and k[1] == st)
        if agg != c:
            errs.append(f"{src}: temperature_profile {st} {agg} != {c}")
    for name in ("medium", "lid_state", "start_mode", "piece_size_class", "water_ratio", "matrix_class"):
        for st, c in (ist.get(name) or {}).items():
            agg = sum(v for k, v in flat_by_src.items() if k[0] == "in:" + name and k[1] == st)
            if agg != c:
                errs.append(f"{src}: {name} {st} {agg} != {c}")
    gm = sum(v for k, v in flat_by_src.items() if k[0] == "gas_mark")
    if gm != census.get("gas_mark_only_events", 0):
        errs.append(f"{src}: gas_mark {gm} != {census.get('gas_mark_only_events', 0)}")
    bounded = sum(v for k, v in flat_by_src.items() if k[0] == "joint" and k[1] == "tS" and k[2] != "T:UNKNOWN")
    # driver_bounded = duration != UNKNOWN and temperature != UNKNOWN (same thing as tS and T known)
    if bounded != census.get("driver_bounded_events", 0):
        errs.append(f"{src}: driver_bounded {bounded} != {census.get('driver_bounded_events', 0)}")
    return errs


def reconcile_heat_l2(src: str, flat_by_src: Counter, l2: dict) -> list[str]:
    errs = []
    st = (l2.get("counts") or {}).get("status") or {}
    for k, c in st.items():
        if flat_by_src[("l2status", k)] != c:
            errs.append(f"{src}: L2 status {k} {flat_by_src[('l2status', k)]} != {c}")
    return errs


def reconcile_nh(src: str, flat_by_src: Counter, census: dict) -> list[str]:
    errs = []
    if flat_by_src[("n", "-")] != census.get("nonheat_events", 0):
        errs.append(f"{src}: non-heat events {flat_by_src[('n', '-')]} != census {census.get('nonheat_events', 0)}")
    return errs


# ----------------------------------------------------------------------------- build
def build(root: Path, agg_path: Path) -> dict:
    check_inputs_not_superseded(root)
    agg = json.loads(agg_path.read_text(encoding="utf-8"))
    if agg.get("meta", {}).get("layer_tag") != LAYER_TAG:
        raise SystemExit(f"aggregate {agg_path} was built from {agg.get('meta', {}).get('layer_tag', 'pre-v04 records')}, not {LAYER_TAG}: re-run --aggregate")
    heat_flat, nh_flat = agg["heat"], agg["nh"]
    errors: list[str] = []
    # per-source committed census
    hpaths = heat_census_paths(root)
    heat_rows, heat_census = {}, {}
    for s, p in hpaths.items():
        if (root / p).is_file():
            d = read_json(root, p)
            heat_census[s] = d
            heat_rows[s] = heat_source_row(s, d, p)
    nh_census = {s: read_json(root, p) for s, p in nh_l1_paths().items() if (root / p).is_file()}
    h2_census = {s: read_json(root, p) for s, p in heat_l2_paths().items() if (root / p).is_file()}
    n2_census = {s: read_json(root, p) for s, p in nh_l2_paths().items() if (root / p).is_file()}

    by_src_heat = rollup(heat_flat, "src")
    by_src_nh = rollup(nh_flat, "src")
    for s in SOURCES:
        if s in heat_census:
            errors += reconcile_heat(s, by_src_heat.get((s,), Counter()), heat_census[s])
        if s in h2_census and heat_census[s].get("heat_events"):
            errors += reconcile_heat_l2(s, by_src_heat.get((s,), Counter()), h2_census[s])
        if s in nh_census:
            errors += reconcile_nh(s, by_src_nh.get((s,), Counter()), nh_census[s])

    # PROC names (registry, not third-party text)
    proc_name: dict[str, tuple[str, str]] = {}
    latest: dict[str, dict] = {}
    for line in open(root / "ledgers/data/PROC.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            if r["id"] not in latest or r["version"] >= latest[r["id"]]["version"]:
                latest[r["id"]] = r
    for k, r in latest.items():
        proc_name[k.replace("-", "__") if False else k] = (r["canonical_name"], r.get("family", ""))

    out = {"record": "CORPUS_CAN_SAY_S178", "tool_version": TOOL_VERSION,
           "status": "AI_DRAFTED_PROPOSED_COUNTS_ONLY", "label": "REAL_BASE_SAMPLE_COUNTS_NOT_GOLD",
           "layer": f"TEXT_STATED (L1, {LAYER_TAG}) with SCENARIO (L2, {LAYER_TAG}) unknown reasons", "citable": False,
           "contains_text": False, "contains_ids": False, "counts_as_human_gate": False,
           "reconciliation": {"status": "PASS" if not errors else "FAILED", "errors": errors,
                              "alignment_errors_heat_l1_l2": agg["meta"]["heat_alignment_errors"],
                              "derived_heat_events": agg["meta"]["heat_events"],
                              "derived_nh_events": agg["meta"]["nh_events"]},
           "inputs": {"committed_census_files": {p: sha256_file(root / p) for p in sorted(
               [*hpaths.values(), *nh_l1_paths().values(), *heat_l2_paths().values(), *nh_l2_paths().values()])
               if (root / p).is_file()},
               "derived_aggregate_sha256": sha256_file(agg_path),
               "derived_dirs": derived_dirs(),
               "superseded_registry_check": "PASS (no input listed in registry/superseded_outputs_S176.csv)"}}
    return {"out": out, "heat_rows": heat_rows, "heat_census": heat_census, "nh_census": nh_census,
            "h2_census": h2_census, "n2_census": n2_census, "heat_flat": heat_flat, "nh_flat": nh_flat,
            "proc_name": proc_name, "errors": errors}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aggregate", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--sample-parts", type=int, default=None)
    ap.add_argument("--out-agg", default=str(ROOT / AGG_DIR))
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)
    if a.workers > 16:
        raise SystemExit("at most 16 workers (S178 lane rule)")
    agg_dir = Path(a.out_agg)
    if a.aggregate:
        agg_dir.mkdir(parents=True, exist_ok=True)
        res = aggregate(root, a.workers, a.sample_parts)
        p = agg_dir / ("can_say_agg_sample.json" if a.sample_parts else "can_say_agg.json")
        p.write_text(json.dumps(res, sort_keys=True), encoding="utf-8")
        print(json.dumps({"wrote": str(p), "sha256": sha256_file(p), "meta": res["meta"]}, sort_keys=True))
    if a.build:
        from s178_analysis_corpus_can_say_render import render  # noqa: E402  (second file, same lane)
        return render(root, agg_dir / "can_say_agg.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
