"""Counts-only route census of the router demo over a seeded recipe sample (S171, D-075 M1). NON_CITABLE.

Per sampled recipe with steps: ``router_demo.route_text`` (Rung A -> unchanged 23a engine, EVD G0 pre-check for one
target state variable). The report holds integer counts, route/reason codes and registry codes (PROC-, SVAR-) only:
no recipe id, recipe text or seed. Sampling is the Step 17b rule (smallest sha256(seed || recipe_id)).
Not a gold score, not a human gate, not citable; EVD rows are tier E3 and unverified.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from typing import Iterable, Iterator, Mapping

from culinarystate.extraction.rung_a import RungA
from culinarystate.extraction.rung_a_measure import code, seeded_sample
from culinarystate.mechanism import applicability as AP
from culinarystate.mechanism import process_signatures as PS
from culinarystate.mechanism import router_demo as RD
from culinarystate.quantity import rc2_dryrun as D
from culinarystate.recipes.ledgers import LOCALE

CENSUS_VERSION = "router-demo-census-0.1.0-draft"


def _steps(rec: Mapping) -> list[str]:
    return [str(s) for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]


def _coverage(index: RD.EvidenceIndex, target_svar: str, pairs: set, ingredients: set) -> dict:
    evd_pairs, evd_ings = index.pairs(target_svar), index.ingredients(target_svar)
    return {"evd_pairs_for_target": len(evd_pairs), "evd_pairs_seen_in_sample": len(evd_pairs & pairs),
            "evd_ingredients_for_target": len(evd_ings),
            "sample_ingredients_with_target_evidence": len(evd_ings & ingredients),
            "sample_distinct_pairs": len(pairs), "sample_distinct_ingredients": len(ingredients)}


_CTX: dict = {}  # set before forking; workers read it (fork start method shares it copy-on-write)


def _empty() -> dict:
    return {"tot": Counter(), "route": Counter(), "reasons": Counter(), "direct_proc": Counter(), "exc": Counter(),
            "pairs": set(), "ingredients": set()}


def _route_chunk(recs: list[Mapping]) -> dict:
    c, part = _CTX, _empty()
    tot = part["tot"]
    for rec in recs:
        steps = _steps(rec)
        if not steps:
            continue
        tot["texts_with_steps"] += 1
        try:
            out = RD.route_text("\n".join(steps), index=c["index"], target_svar=c["target_svar"],
                                locale=LOCALE.get(rec.get("source_family")), rung=c["rung"],
                                hierarchy=c["hierarchy"], schema=c["schema"])
        except Exception as e:  # noqa: BLE001 - counted by class name; the message may contain text
            part["exc"][code(type(e).__name__)] += 1
            continue
        tot["events"] += len({i["event_id"] for i in out["items"]})
        any_direct = False
        for it in out["items"]:
            tot["items"] += 1
            part["route"][code(it["route"])] += 1
            part["reasons"].update(code(r) for r in it["reasons"])
            ing, proc = it["ingredient_id"], it["process_id"]
            tot["items_linked" if ing else "items_unlinked"] += 1
            tot["items_with_process" if proc else "items_without_process"] += 1
            if ing:
                part["ingredients"].add(ing)
            if ing and proc:
                part["pairs"].add((ing, proc))
            if it["route"] == "DIRECT":
                any_direct = True
                part["direct_proc"][code(proc)] += 1
        tot["recipes_with_any_direct"] += any_direct
    return part


def _merge(parts: Iterable[dict]) -> dict:
    acc = _empty()
    for p in parts:
        for k, v in p.items():
            acc[k].update(v)  # Counter.update adds; set.update unions
    return acc


def _run(sample: list[Mapping], workers: int) -> dict:
    if workers == 1:
        return _route_chunk(sample)
    import multiprocessing as mp
    chunks = [sample[i::workers * 8] for i in range(workers * 8)]
    with mp.get_context("fork").Pool(workers) as pool:
        return _merge(pool.map(_route_chunk, chunks))


def census_from_records(records: Iterable[Mapping], *, seed: str, size: int, index: RD.EvidenceIndex,
                        target_svar: str, rung: RungA | None = None, schema: Mapping | None = None,
                        hierarchy: PS.ProcessHierarchy | None = None, workers: int = 1) -> dict:
    """Counts-only router-demo census for ``target_svar`` over the seeded sample (``workers`` > 1: fork pool)."""
    if not isinstance(target_svar, str) or not target_svar.strip():
        raise ValueError("target_svar is required (e.g. SVAR-000009, vitamin C)")
    if not isinstance(workers, int) or workers < 1:
        raise ValueError("workers must be a positive integer")
    seen = 0

    def counted(it: Iterable[Mapping]) -> Iterator[Mapping]:
        nonlocal seen
        for rec in it:
            seen += 1
            yield rec

    sample = seeded_sample(counted(records), seed, size)
    _CTX.clear()
    _CTX.update(index=index, target_svar=target_svar, rung=rung or RungA(), schema=schema or D.load_schema(),
                hierarchy=hierarchy or PS.read_process_hierarchy())
    try:
        acc = _run(sample, workers)
    finally:
        _CTX.clear()
    tot, route, reasons, direct_proc, exc = (acc[k] for k in ("tot", "route", "reasons", "direct_proc", "exc"))
    pairs, ingredients = acc["pairs"], acc["ingredients"]
    report = {
        "record": "ROUTER_DEMO_CENSUS", "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY",
        "label": "REAL_BASE_SAMPLE_COUNTS_NOT_GOLD", "census_version": CENSUS_VERSION,
        "demo_version": RD.DEMO_VERSION, "labels": list(RD.LABELS), "citable": False,
        "engine_mode": AP.MODE_23A, "engine_version": AP.ENGINE_VERSION, "conditions_consumed": False,
        "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
        "target_svar": target_svar, "seed_sha256": hashlib.sha256(seed.encode("utf-8")).hexdigest(),
        "sample_rule": "SHA256_SEED_CONCAT_RECIPE_ID_ASC", "sample_size_requested": int(size),
        "recipes_seen": seen, "recipes_sampled": len(sample),
        **{k: tot[k] for k in ("texts_with_steps", "events", "items", "items_linked", "items_unlinked",
                               "items_with_process", "items_without_process", "recipes_with_any_direct")},
        "route": dict(sorted(route.items())), "reason_counts": dict(sorted(reasons.items())),
        "direct_by_process": dict(sorted(direct_proc.items())), "exceptions_by_class": dict(sorted(exc.items())),
        "evidence_coverage": _coverage(index, target_svar, pairs, ingredients),
    }
    D.assert_counts_only(report)
    return report
