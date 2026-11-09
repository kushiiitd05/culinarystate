"""Counts-only route census of the router demo over a seeded recipe sample (S171, D-075 M1). NON_CITABLE.

Per sampled recipe with steps: ``router_demo.route_text`` (Rung A -> unchanged 23a engine, EVD G0 pre-check for one
target state variable). The report holds integer counts, route/reason codes and registry codes (PROC-, SVAR-) only:
no recipe id, recipe text or seed. Sampling is the Step 17b rule (smallest sha256(seed || recipe_id)).
Not a gold score, not a human gate, not citable; EVD rows are tier E3 and unverified.

S176 (L-ROUTER): with ``gates`` (``evidence_gates.EvidenceGates``) the census also counts, in the SAME pass, what the
S171 engine would have said (``route_ungated``) next to the gated ``route``, the presence / lot-context codes, and the
fate of every ungated DIRECT (``direct_ungated_cross``: presence | lot context | final route). Counts and codes only.

S177: also ``prior_process_withheld`` (ungated DIRECT items withheld by the prior-process rule, by kind HEAT / LEACH),
``member_absent_items`` (items by the ING whose own member state is ABSENT, for the human review list) and
``member_presence`` (items by the member state of their own ING), ``member_blocker`` (why an UNKNOWN member is not ABSENT)
and ``category_blocked_items`` (items by ING that would be ABSENT if its category were confirmed).

S178 (FIX-ROUTER, SCI-B R2-R6): each recipe's ingredient lines are passed to ``route_text`` for their processed-state
cues (the lines are not routed as events: they describe foods, not process steps). New counters: ``event_role`` (items by
role), ``direct_ungated_by_role``, ``prior_process_withheld_by_basis`` (EVENT / EVENT_UNRESOLVED / TEXT_STATED_STATE /
INGREDIENT_LINE), ``prior_process_unresolved_withheld``, ``non_step_direct_withheld_only_by_role`` (attributive / serving items that every other
gate would have left DIRECT: the R3 share), ``prior_presupposed_would_release`` (ungated DIRECT items the
human-gated R6 exemption would release; the exemption itself is OFF), ``sr_not_analytical_items`` (items by ING whose
member is UNKNOWN only because a plausible SR value is not analytical, R4) and the ``ingredient_lines`` totals.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from typing import Iterable, Iterator, Mapping

from culinarystate.extraction.rung_a import RungA
from culinarystate.extraction.rung_a_measure import code, seeded_sample
from culinarystate.mechanism import applicability as AP
from culinarystate.mechanism import evidence_gates as EG
from culinarystate.mechanism import process_signatures as PS
from culinarystate.mechanism import router_demo as RD
from culinarystate.quantity import rc2_dryrun as D
from culinarystate.recipes.ledgers import LOCALE

CENSUS_VERSION = "router-demo-census-0.4.1-draft"


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
            "route_ungated": Counter(), "gate_cross": Counter(), "direct_ungated_cross": Counter(),
            "direct_ungated_proc": Counter(), "prior_withheld": Counter(), "member_absent": Counter(),
            "member_presence": Counter(), "member_blocker": Counter(), "category_blocked": Counter(), "pairs": set(), "ingredients": set(),
            "event_role": Counter(), "direct_ungated_role": Counter(), "prior_basis": Counter(), "prior_unresolved": Counter(),
            "presupposed": Counter(), "sr_not_analytical": Counter(), "lines": Counter(), "non_step_direct": Counter()}


def _route_chunk(recs: list[Mapping]) -> dict:
    c, part = _CTX, _empty()
    tot = part["tot"]
    for rec in recs:
        steps = _steps(rec)
        if not steps:
            continue
        tot["texts_with_steps"] += 1
        lines = rec.get("ingredient_lines") if c.get("gates") is not None else None
        lc: dict = {}
        try:
            out = RD.route_text("\n".join(steps), index=c["index"], target_svar=c["target_svar"],
                                locale=LOCALE.get(rec.get("source_family")), rung=c["rung"],
                                hierarchy=c["hierarchy"], schema=c["schema"], gates=c.get("gates"),
                                ingredient_lines=lines if isinstance(lines, list) else None, counts=lc)
        except Exception as e:  # noqa: BLE001 - counted by class name; the message may contain text
            part["exc"][code(type(e).__name__)] += 1
            continue
        part["lines"].update(lc)
        tot["events"] += len({i["event_id"] for i in out["items"]})
        any_direct = any_direct_ungated = False
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
            g = it.get("gates")
            ungated = it.get("route_ungated", it["route"])
            part["route_ungated"][code(ungated)] += 1
            if g is not None:
                part["gate_cross"][code(f"{g['presence']}|{g['lot_context']}")] += 1
                mp = it.get("member_presence")
                part["member_presence"][code(mp or "NONE")] += 1
                if mp == EG.ABSENT:
                    part["member_absent"][code(ing)] += 1
                mb = it.get("member_blocker")
                if mb:
                    part["member_blocker"][code(mb)] += 1
                    if mb in ("CATEGORY_EMPTY", "CATEGORY_MISMATCH"):
                        part["category_blocked"][code(ing)] += 1
                if EG.R_PRIOR_PROCESS in it["reasons"] or EG.R_PRIOR_UNRESOLVED in it["reasons"]:
                    part["prior_withheld"][code("_".join(it.get("prior_process") or ()) or "NONE")] += 1
                    part["prior_basis"][code("_".join(it.get("prior_basis") or ()) or "NONE")] += 1
                    if it.get("prior_presupposed"):
                        part["presupposed"]["ITEMS"] += 1
                if EG.R_PRIOR_UNRESOLVED in it["reasons"]:
                    part["prior_unresolved"]["ONLY" if EG.R_PRIOR_PROCESS not in it["reasons"] else "WITH_KNOWN_KIND"] += 1
                part["event_role"][code(it.get("event_role") or EG.PROCESS_STEP)] += 1
                if it.get("direct_if_process_step"):
                    part["non_step_direct"][code(it["event_role"])] += 1
                if mb == EG.B_NOT_ANALYTICAL:
                    part["sr_not_analytical"][code(ing)] += 1
            if ungated == "DIRECT":
                any_direct_ungated = True
                part["direct_ungated_proc"][code(proc)] += 1
                if g is not None:
                    part["direct_ungated_cross"][code(f"{g['presence']}|{g['lot_context']}|{it['route']}")] += 1
                    part["direct_ungated_role"][code(f"{it.get('event_role') or EG.PROCESS_STEP}|{it['route']}")] += 1
        tot["recipes_with_any_direct"] += any_direct
        tot["recipes_with_any_direct_ungated"] += any_direct_ungated
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
                        hierarchy: PS.ProcessHierarchy | None = None, workers: int = 1,
                        gates: EG.EvidenceGates | None = None) -> dict:
    """Counts-only router-demo census for ``target_svar`` over the seeded sample (``workers`` > 1: fork pool).

    ``gates`` (S176): evidence gates before G0; the report then also holds the ungated counts of the same pass."""
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
                hierarchy=hierarchy or PS.read_process_hierarchy(), gates=gates)
    try:
        acc = _run(sample, workers)
    finally:
        _CTX.clear()
    tot, route, reasons, direct_proc, exc = (acc[k] for k in ("tot", "route", "reasons", "direct_proc", "exc"))
    gated = gates is not None
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
        "gates": gates.describe() if gated else {"enabled": False},
        "route": dict(sorted(route.items())), "reason_counts": dict(sorted(reasons.items())),
        "direct_by_process": dict(sorted(direct_proc.items())), "exceptions_by_class": dict(sorted(exc.items())),
        "evidence_coverage": _coverage(index, target_svar, pairs, ingredients),
    }
    if gated:
        report.update(
            recipes_with_any_direct_ungated=tot["recipes_with_any_direct_ungated"],
            route_ungated=dict(sorted(acc["route_ungated"].items())),
            gate_cross=dict(sorted(acc["gate_cross"].items())),
            direct_ungated_cross=dict(sorted(acc["direct_ungated_cross"].items())),
            direct_ungated_by_process=dict(sorted(acc["direct_ungated_proc"].items())),
            prior_process_withheld=dict(sorted(acc["prior_withheld"].items())),
            member_presence=dict(sorted(acc["member_presence"].items())),
            member_absent_items=dict(sorted(acc["member_absent"].items())),
            member_blocker=dict(sorted(acc["member_blocker"].items())),
            category_blocked_items=dict(sorted(acc["category_blocked"].items())),
            event_role=dict(sorted(acc["event_role"].items())),
            direct_ungated_by_role=dict(sorted(acc["direct_ungated_role"].items())),
            prior_process_withheld_by_basis=dict(sorted(acc["prior_basis"].items())),
            prior_process_unresolved_withheld=dict(sorted(acc["prior_unresolved"].items())),
            prior_presupposed_would_release=int(acc["presupposed"]["ITEMS"]),
            non_step_direct_withheld_only_by_role=dict(sorted(acc["non_step_direct"].items())),
            sr_not_analytical_items=dict(sorted(acc["sr_not_analytical"].items())),
            ingredient_lines={k: int(acc["lines"][k]) for k in ("ingredient_lines_seen", "ingredient_lines_with_state_cue",
                                                                 "ingredient_line_ing_states")})
    D.assert_counts_only(report)
    return report
