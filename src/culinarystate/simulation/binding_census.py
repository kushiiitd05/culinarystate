"""Layer 1 binding census over a seeded recipe sample (S172, D-077): counts only, plus optional dataset records.

Per sampled recipe: ``condition_binding.Binder.bind_text``; counts per heat event and input (status, basis). With
``records_dir`` it also writes one JSONL row per heat event (recipe id, event id, process, inputs with values as
strings, layer TEXT_STATED) into that directory, which must be a data-plane location (the caller checks). The report
holds counts and codes only. Fork pool for ``workers`` > 1, merged counts identical to one worker.
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

CENSUS_VERSION = "binding-census-L1-0.1.0-draft"
_CTX: dict = {}


def _steps(rec: Mapping) -> list[str]:
    return [str(s) for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]


def _s(v):
    if isinstance(v, Fraction):
        return str(v)
    if isinstance(v, tuple):
        return [_s(x) for x in v]
    return v


def _chunk(args: tuple[int, list[Mapping]]) -> dict:
    idx, recs = args
    binder, out_dir = _CTX["binder"], _CTX["records_dir"]
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
                if ev["oven_setpoint_code"]:
                    tot["gas_mark_only_events"] += 1
                if fh:
                    fh.write(json.dumps({"recipe_id": rec["recipe_id"], "source_family": rec.get("source_family"),
                                         "event_id": ev["event_id"], "process_id": ev["process_id"],
                                         "family": ev["family"], "layer": "TEXT_STATED", "version": CB.VERSION,
                                         "oven_setpoint_code": ev["oven_setpoint_code"],
                                         "inputs": {k: {"value": _s(v["value"]), "status": v["status"],
                                                        "basis": v["basis"], "span": v["span"]}
                                                    for k, v in inp.items()}}) + "\n")
    finally:
        if fh:
            fh.close()
    return {"tot": tot, "st": st, "ba": ba, "fam": fam, "exc": exc}


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
    acc = {k: Counter() for k in ("tot", "st", "ba", "fam", "exc")}
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
              **{k: tot[k] for k in ("texts_with_steps", "events", "heat_events", "driver_ready_events",
                                     "gas_mark_only_events", "contract_bindings")},
              "heat_events_by_family": dict(sorted(acc["fam"].items())),
              "input_status": {k: dict(sorted(v.items())) for k, v in sorted(st.items())},
              "input_basis": {k: dict(sorted(v.items())) for k, v in sorted(ba.items())},
              "exceptions_by_class": dict(sorted(acc["exc"].items()))}
    D.assert_counts_only(report)
    return report
