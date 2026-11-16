"""Layer 1 binding census over a seeded recipe sample (S172, D-077): counts only, plus optional dataset records.

S178 PHYS2 (census 0.2.0): also counts of the endpoint cues per heat event (``endpoint_cues``), of the temperature-ownership
decisions (``temperature_note``: events whose temperature differs from the 0.1.0 nearest-temperature rule), of the aqueous-medium
events whose stated temperature is above 100 C (by bucket: the S177 "stated liquid" population) and of the per-axis provenance
(bound axes with a basis, a span id and a row; unknown axes with a reason).

Per sampled recipe: ``condition_binding.Binder.bind_text``; counts per heat event and input (status, basis). With
``records_dir`` it also writes one JSONL row per heat event (recipe id, event id, process, inputs with values as
strings, layer TEXT_STATED) into that directory, which must be a data-plane location (the caller checks). The report
holds counts and codes only. Fork pool for ``workers`` > 1, merged counts identical to one worker.

S178 FIX-PHYS (census 0.3.0, Layer 1 0.3.0): ``fixphys_layer1`` block: the corpus check of SCI-A M1 (bound temperatures inside an
until-clause span, by the role of that temperature: 0 is expected outside the exempt roles), temperature roles in until-clauses, the
new CUE axes (syrup / stage, pressure, water bath), ambient temperatures by rule, the Layer 1 temperature flags (fan / conventional,
heat level at or below T_boil) and RANGE temperatures.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from culinarystate.extraction.rung_a_measure import code, seeded_sample
from culinarystate.quantity import rc2_dryrun as D
from culinarystate.recipes.ledgers import LOCALE
from culinarystate.simulation import condition_binding as CB
from culinarystate.simulation import endpoint_cues as EC

CENSUS_VERSION = "binding-census-L1-0.3.0-draft"
_CTX: dict = {}


def _steps(rec: Mapping) -> list[str]:
    return [str(s) for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]


def _s(v):
    if isinstance(v, Fraction):
        return str(v)
    if isinstance(v, tuple):
        return [_s(x) for x in v]
    return v


LIQUID_MEDIA = CB.LIQUID_MEDIA
BUCKETS = ((100, "T_100_OR_BELOW"), (105, "T_100_105"), (120, "T_105_120"), (150, "T_120_150"))


def _bucket(hi: float) -> str:
    return next((name for lim, name in BUCKETS if hi <= lim), "T_ABOVE_150")


def _as_float(v) -> float:
    return float(Fraction(v)) if not isinstance(v, (list, tuple)) else float(Fraction(str(v[-1])))


def _count_event(ev: Mapping, rec_inputs: Mapping, extra: Counter, ep: Counter) -> None:
    """Endpoint, ownership, stated-liquid and provenance counters of one heat event (all counts, no ids)."""
    f = code(ev["family"])
    blk = ev.get(EC.BLOCK_KEY) or {"cues": []}
    cues = blk["cues"]
    ep[("cue_events_hist", min(len(cues), 3))] += 1
    if cues:
        ep[("events_with_cue", f)] += 1
        ep[("stopping_class", code(blk["stopping_criterion"]["value"]))] += 1
        dur = rec_inputs["duration"]["status"] != "UNKNOWN"
        ep[("cue_and_duration" if dur else "cue_without_duration", f)] += 1
        for c in cues:
            ep[("cue_class", code(c["class"]))] += 1
            ep[("cue_trigger", code(c["trigger"]))] += 1
            ep[("cue_class_by_family", f, code(c["class"]))] += 1
        if rec_inputs["temperature_profile"]["status"] == "UNKNOWN":
            ep[("cue_without_temperature", f)] += 1
    for n in ev.get("temperature_note") or []:
        extra[("temperature_note", code(n["now"]), f)] += 1
    if "ambient_temperature" in rec_inputs:
        extra[("ambient_temperature_events", f)] += 1
    mg = rec_inputs.get("matrix_groups")
    if mg:
        extra[("matrix_groups_events", min(len(mg["value"]), 4))] += 1
    elif rec_inputs["matrix_class"]["status"] == "UNKNOWN":
        extra[("no_food_group_events",)] += 1
    t = rec_inputs["temperature_profile"]
    medium = rec_inputs["medium"]["value"]
    if t["status"] != "UNKNOWN" and t["basis"] in ("TEXT_STATED", "CARRIED_SETPOINT") and medium in LIQUID_MEDIA:
        v = t["value"]
        hi = max(float(Fraction(str(x))) for x in v) if isinstance(v, (list, tuple)) else float(Fraction(str(v)))
        extra[("stated_aqueous_temperature", _bucket(hi), code(ev["process_id"]) if hi > 150 else "ALL")] += 1
    # S178 FIX-PHYS: until-clause check (M1), cue axes (M4 / m3), ambient rules (M2), temperature flags (m1 / m2)
    sp = t.get("span") if t["status"] != "UNKNOWN" and t["basis"] == "TEXT_STATED" else None
    for cl in blk.get("until_clauses") or []:
        extra[("fx", "until_clauses")] += 1
        for tt in cl.get("temperatures") or []:
            extra[("fx_until_role", code(tt["role"]))] += 1
        if sp and cl["span"][0] <= sp[0] and sp[1] <= cl["span"][1]:
            role = next((tt["role"] for tt in cl.get("temperatures") or [] if tt["span"] == list(sp)), "NOT_CLASSIFIED")
            extra[("fx_bound_in_until_clause", code(role))] += 1
    for ax in ("syrup_stage_cue", "pressure_cue", "water_bath_cue"):
        if ax in rec_inputs:
            extra[("fx_cue_axis", ax, f)] += 1
    amb = rec_inputs.get("ambient_temperature")
    if amb:
        extra[("fx_ambient_row", code(str(amb.get("row")).replace("CB_RULE:", "")))] += 1
    for flag in t.get("flags") or []:
        extra[("fx_temperature_flag", code(flag))] += 1
    if t["status"] == "RANGE":
        extra[("fx", "temperature_range_events")] += 1
    for axis, x in rec_inputs.items():
        if x["status"] == "UNKNOWN":
            extra[("prov", "unknown_axes")] += 1
            extra[("prov", "unknown_with_reason")] += 1 if x.get("reason") else 0
        else:
            extra[("prov", "bound_axes")] += 1
            extra[("prov", "bound_with_basis")] += 1 if x.get("basis") else 0
            extra[("prov", "bound_with_span_id")] += 1 if x.get("span_id") else 0
            extra[("prov", "bound_with_row")] += 1 if x.get("row") else 0


def _chunk(args: tuple[int, list[Mapping]]) -> dict:
    idx, recs = args
    binder, out_dir = _CTX["binder"], _CTX["records_dir"]
    extra, ep = Counter(), Counter()
    tot, st, ba, fam, exc = Counter(), Counter(), Counter(), Counter(), Counter()
    fh = open(Path(out_dir) / f"part-{idx:05d}.jsonl", "w", encoding="utf-8") if out_dir else None
    try:
        for rec in recs:
            steps = _steps(rec)
            if not steps:
                continue
            tot["texts_with_steps"] += 1
            try:
                res = binder.bind_text("\n".join(steps), LOCALE.get(rec.get("source_family")))
            except Exception as e:  # noqa: BLE001 - class name only
                exc[code(type(e).__name__)] += 1
                continue
            tot["events"] += len(res["events"])
            tot["contract_bindings"] += len(res["bindings"])
            for ev in res["events"]:
                if not ev["heat"]:
                    continue
                tot["heat_events"] += 1
                fam[code(ev["family"])] += 1
                inp = ev["inputs"]
                for name, x in inp.items():
                    st[(name, x["status"])] += 1
                    if x["basis"]:
                        ba[(name, x["basis"])] += 1
                if inp["duration"]["status"] == "MEASURED" and inp["temperature_profile"]["status"] != "UNKNOWN":
                    tot["driver_ready_events"] += 1
                if inp["duration"]["status"] != "UNKNOWN" and inp["temperature_profile"]["status"] != "UNKNOWN":
                    tot["driver_bounded_events"] += 1
                if ev["oven_setpoint_code"]:
                    tot["gas_mark_only_events"] += 1
                _count_event(ev, inp, extra, ep)
                if fh:
                    fh.write(json.dumps({"recipe_id": rec["recipe_id"], "source_family": rec.get("source_family"),
                                         "event_id": ev["event_id"], "process_id": ev["process_id"],
                                         "family": ev["family"], "layer": "TEXT_STATED", "version": CB.VERSION,
                                         "oven_setpoint_code": ev["oven_setpoint_code"],
                                         "inputs": {k: {kk: (_s(vv) if kk == "value" else vv) for kk, vv in v.items()}
                                                    for k, v in inp.items()},
                                         EC.BLOCK_KEY: ev.get(EC.BLOCK_KEY),
                                         **({"temperature_note": ev["temperature_note"]} if ev.get("temperature_note") else {})})
                             + "\n")
    finally:
        if fh:
            fh.close()
    return {"tot": tot, "st": st, "ba": ba, "fam": fam, "exc": exc, "extra": extra, "ep": ep}


def census_from_records(records: Iterable[Mapping], *, seed: str, size: int, workers: int = 1,
                        binder: CB.Binder | None = None, records_dir: Path | None = None) -> dict:
    if workers < 1:
        raise ValueError("workers must be positive")
    seen = 0

    def counted(it: Iterable[Mapping]) -> Iterator[Mapping]:
        nonlocal seen
        for rec in it:
            seen += 1
            yield rec

    sample = seeded_sample(counted(records), seed, size)
    _CTX.clear()
    _CTX.update(binder=binder or CB.Binder.load(), records_dir=str(records_dir) if records_dir else None)
    n = workers * 8 if workers > 1 else 1
    chunks = [(i, sample[i::n]) for i in range(n)]
    try:
        if workers == 1:
            parts = [_chunk(c) for c in chunks]
        else:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(workers) as pool:
                parts = pool.map(_chunk, chunks)
    finally:
        _CTX.clear()
    acc = {k: Counter() for k in ("tot", "st", "ba", "fam", "exc", "extra", "ep")}
    for p in parts:
        for k, v in p.items():
            acc[k].update(v)
    st = {}
    for (name, s), c in acc["st"].items():
        st.setdefault(name, {})[s] = c
    ba = {}
    for (name, b), c in acc["ba"].items():
        ba.setdefault(name, {})[b] = c
    tot = acc["tot"]
    report = {"record": "BINDING_CENSUS_L1", "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY",
              "label": "REAL_BASE_SAMPLE_COUNTS_NOT_GOLD", "census_version": CENSUS_VERSION, "binder_version": CB.VERSION,
              "layer": "TEXT_STATED", "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
              "seed_sha256": hashlib.sha256(seed.encode()).hexdigest(), "sample_rule": "SHA256_SEED_CONCAT_RECIPE_ID_ASC",
              "sample_size_requested": int(size), "recipes_seen": seen, "recipes_sampled": len(sample),
              **{k: tot[k] for k in ("texts_with_steps", "events", "heat_events", "driver_ready_events", "driver_bounded_events",
                                     "gas_mark_only_events", "contract_bindings")},
              "heat_events_by_family": dict(sorted(acc["fam"].items())),
              "input_status": {k: dict(sorted(v.items())) for k, v in sorted(st.items())},
              "input_basis": {k: dict(sorted(v.items())) for k, v in sorted(ba.items())},
              "exceptions_by_class": dict(sorted(acc["exc"].items())),
              **_s178_blocks(acc["extra"], acc["ep"], tot["heat_events"])}
    D.assert_counts_only(report)
    return report


def _nest_counter(c: Counter, name: str) -> dict:
    out: dict = {}
    for k, v in c.items():
        if k[0] != name:
            continue
        d = out
        for part in k[1:-1]:
            d = d.setdefault(str(part), {})
        d[str(k[-1])] = d.get(str(k[-1]), 0) + v
    return out


def _s178_blocks(extra: Counter, ep: Counter, heat_events: int) -> dict:
    """Counts-only blocks added in S178 PHYS2: endpoint cues, temperature ownership, stated aqueous temperatures, provenance."""
    prov = {k[1]: v for k, v in extra.items() if k[0] == "prov"}
    ev_with_cue = sum(v for k, v in ep.items() if k[0] == "events_with_cue")
    return {
        "endpoint_cues": {
            "extractor_version": EC.VERSION, "heat_events": heat_events, "heat_events_with_cue": ev_with_cue,
            "cues_per_event": {str(k[1]): v for k, v in sorted(ep.items(), key=lambda kv: str(kv[0])) if k[0] == "cue_events_hist"},
            "events_with_cue_by_family": _nest_counter(ep, "events_with_cue"),
            "stopping_criterion_class": _nest_counter(ep, "stopping_class"),
            "cue_class": _nest_counter(ep, "cue_class"), "cue_trigger": _nest_counter(ep, "cue_trigger"),
            "cue_class_by_family": _nest_counter(ep, "cue_class_by_family"),
            "cue_and_duration_by_family": _nest_counter(ep, "cue_and_duration"),
            "cue_without_duration_by_family": _nest_counter(ep, "cue_without_duration"),
            "cue_without_temperature_by_family": _nest_counter(ep, "cue_without_temperature"),
            "stored_outside_inputs": True},
        "temperature_ownership": {
            "rule": "OWN_CLAUSE_OR_EARLIER_SETTER_NOT_NEAREST_IN_SENTENCE",
            "events_where_temperature_differs_from_v01_by_reason_and_family": _nest_counter(extra, "temperature_note"),
            "events_with_ambient_temperature_by_family": _nest_counter(extra, "ambient_temperature_events"),
            "aqueous_medium_events_with_stated_temperature_by_bucket": _nest_counter(extra, "stated_aqueous_temperature")},
        "matrix_groups": {"events_by_member_group_count": _nest_counter(extra, "matrix_groups_events"),
                          "events_without_any_food_group": extra[("no_food_group_events",)]},
        "fixphys_layer1": {
            "until_clauses": extra[("fx", "until_clauses")],
            "temperatures_in_until_clauses_by_role": _nest_counter(extra, "fx_until_role"),
            "bound_text_stated_temperature_inside_an_until_clause_by_role": _nest_counter(extra, "fx_bound_in_until_clause"),
            "cue_axis_events_by_family": _nest_counter(extra, "fx_cue_axis"),
            "ambient_temperature_by_rule": _nest_counter(extra, "fx_ambient_row"),
            "temperature_flags": _nest_counter(extra, "fx_temperature_flag"),
            "temperature_range_events": extra[("fx", "temperature_range_events")]},
        "provenance_axes": prov}
