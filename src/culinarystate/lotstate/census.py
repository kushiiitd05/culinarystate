"""Counts-only lot-state census over a seeded recipe sample (+ optional per-lot / per-line records).

The report holds integer counts, percentages and codes only (``rc2_dryrun.assert_counts_only``). Per-lot and per-line
records (recipe ids, ING ids, numbers, no text) go to a data-plane directory (``data/derived/...``, git-ignored).
Fork pool for ``workers`` > 1; merged counts do not depend on the worker count.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from culinarystate.quantity import rc2_dryrun as D

from .composition import BAND_RANK, KINDS
from .lots import LotStateBuilder
from .ph import FLAGS
from .sr_legacy import NUTRIENT_KEYS

CENSUS_VERSION = "lotstate-census-0.1.0-draft"
_CTX: dict = {}


def _pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 3) if d else 0.0


def tally(out: Mapping, floor: str, t: Counter) -> None:
    """Add one recipe's counts to ``t`` (flat string keys; summarised later)."""
    st = out["stats"]
    t["graph_attempted"] += st["graph_attempted"]
    t["graph_failed"] += st["graph_failed"]
    t[f"replay_{st['replay_status']}"] += 1
    t["foodcom_qp_mismatch_recipes"] += st["foodcom_qp_mismatch"]
    for ln in out["lines"]:
        fam = ln["source_family"]
        t["lines"] += 1
        t[f"lines|{fam}"] += 1
        t[f"line_link|{ln['link']}"] += 1
        t[f"line_link|{fam}|{ln['link']}"] += 1
        if ln["link"] == "LINKED":
            t[f"line_band|{ln['sr_band']}"] += 1
        t[f"line_basis|{ln['basis']}"] += 1
        t[f"line_basis|{fam}|{ln['basis']}"] += 1
        t[f"line_reason|{ln['reason']}"] += 1
        t[f"line_reason|{fam}|{ln['reason']}"] += 1
        has = "grams_low" in ln
        usable = has and (ln["basis"] == "STATED_MASS" or BAND_RANK.get(ln["sr_band"], 0) >= BAND_RANK[floor])
        if has:
            t["lines_with_grams_any_band"] += 1
            t[f"lines_with_grams_any_band|{ln['basis']}"] += 1
        if has and (ln["basis"] == "STATED_MASS" or BAND_RANK.get(ln["sr_band"], 0) >= BAND_RANK["HIGH"]):
            t["lines_with_grams_high_band_only"] += 1
        if usable:
            t["lines_with_usable_grams"] += 1
            t[f"lines_with_usable_grams|{ln['basis']}"] += 1
            t[f"lines_with_usable_grams|{fam}"] += 1
            if ln["ambiguous"]:
                t[f"lines_usable_interval|{ln['basis']}"] += 1
    for lot in out["lots"]:
        fam, kind = lot["source_family"], lot["kind"]
        comp, ck = lot["composition"], lot["composition"]["kind"]
        t["lots"] += 1
        t[f"lot_replay|{lot.get('replay_status', 'NONE')}"] += 1
        t[f"lotkind|{kind}"] += 1
        t[f"lotfam|{fam}"] += 1
        t[f"comp|{ck}"] += 1
        t[f"compkind|{kind}|{ck}"] += 1
        t[f"compfam|{fam}|{ck}"] += 1
        t[f"match_floor|{comp['match_floor']}"] += 1
        t[f"compfloor|{comp['match_floor']}|{ck}"] += 1
        masses_known = all("mass_g" in m for m in lot["members"]) and bool(lot["members"])
        if masses_known:
            t[f"all_member_masses_known|floor_{comp['match_floor']}"] += 1
        if lot["is_leaf"]:
            t["leaf_lots"] += 1
            t[f"leaf_comp|{ck}"] += 1
            t[f"leaf_ph_contains_acid|{lot['ph']['flags']['CONTAINS_ACID_MEMBER']}"] += 1
        if kind == "INGREDIENT_LOT" and lot["members"]:
            m0 = lot["members"][0]
            t[f"ingredient_lot_member|{'LINKED' if m0.get('ing_id') else 'UNLINKED'}"] += 1
            if m0.get("ing_id"):
                t[f"ingredient_lot_band|{m0['sr_band']}"] += 1
        if ck in ("SINGLE_MEMBER_POINT", "INTERVAL_EXACT_BOUNDS"):
            for k, v in comp["nutrients"].items():
                t[f"nutrient|{k}|{v['type']}"] += 1
        for k, v in lot["solute_load"].items():
            t[f"solute|{k}|{v['type']}"] += 1
            if v["type"] == "UNKNOWN":
                t[f"solute_reason|{k}|{v.get('reason')}"] += 1
        t[f"water_activity|{lot['water_activity']['type']}"] += 1
        for f in FLAGS:
            t[f"ph|{f}|{lot['ph']['flags'][f]}"] += 1
        t[f"ph_mask|{lot['ph']['mask']}"] += 1


def _chunk(args: tuple[int, list[Mapping]]) -> Counter:
    idx, recs = args
    b: LotStateBuilder = _CTX["builder"]
    out_dir, floor = _CTX["records_dir"], b.cfg.min_band
    t: Counter = Counter()
    lots_fh = open(Path(out_dir) / f"lots-part-{idx:05d}.jsonl", "w", encoding="utf-8") if out_dir else None
    lines_fh = open(Path(out_dir) / f"lines-part-{idx:05d}.jsonl", "w", encoding="utf-8") if out_dir else None
    try:
        for rec in recs:
            t["recipes"] += 1
            t[f"recipes|{rec.get('source_family')}"] += 1
            if rec.get("steps"):
                t["recipes_with_steps"] += 1
            try:
                out = b.build_recipe(rec)
            except Exception as exc:  # noqa: BLE001 - class name only
                t[f"exception|{type(exc).__name__}"] += 1
                continue
            tally(out, floor, t)
            if lots_fh:
                for lot in out["lots"]:
                    lots_fh.write(json.dumps(lot, separators=(",", ":")) + "\n")
                for ln in out["lines"]:
                    lines_fh.write(json.dumps(ln, separators=(",", ":")) + "\n")
    finally:
        for fh in (lots_fh, lines_fh):
            if fh:
                fh.close()
    return t


def census(records: Sequence[Mapping], builder: LotStateBuilder, *, workers: int = 1, records_dir: Path | None = None) -> Counter:
    _CTX.clear()
    _CTX.update(builder=builder, records_dir=str(records_dir) if records_dir else None)
    n = workers * 4 if workers > 1 else 1
    chunks = [(i, list(records[i::n])) for i in range(n)]
    try:
        if workers == 1:
            parts = [_chunk(c) for c in chunks]
        else:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(workers) as pool:
                parts = pool.map(_chunk, chunks)
    finally:
        _CTX.clear()
    total: Counter = Counter()
    for p in parts:
        total.update(p)
    return total


def summarise(t: Counter, floor: str) -> dict:
    """Group the flat tally into a nested, counts-only report body."""
    def grp(prefix: str) -> dict:
        n = len(prefix)
        return {k[n:]: v for k, v in sorted(t.items()) if k.startswith(prefix)}

    def nest(prefix: str) -> dict:
        out: dict = {}
        for k, v in sorted(t.items()):
            if k.startswith(prefix):
                parts = k[len(prefix):].split("|")
                d = out
                for p in parts[:-1]:
                    d = d.setdefault(p, {})
                d[parts[-1]] = v
        return out

    lines, lots = t["lines"], t["lots"]
    linked = t["line_link|LINKED"]
    pct_basis = {b: _pct(t[f"lines_with_usable_grams|{b}"], lines) for b in ("STATED_MASS", "SR_PORTION")}
    comp_kinds = {k: t[f"comp|{k}"] for k in KINDS}
    return {
        "recipes_sampled": t["recipes"], "recipes_by_family": grp("recipes|"), "recipes_with_steps": t["recipes_with_steps"],
        "graph_attempted": t["graph_attempted"], "graph_failed": t["graph_failed"],
        "replay_status": {k: t[f"replay_{k}"] for k in ("PASS", "UNKNOWN", "FAIL", "NONE") if t[f"replay_{k}"]},
        "foodcom_recipes_q_len_ne_p_len": t["foodcom_qp_mismatch_recipes"],
        "lines": {
            "total": lines, "by_family": grp("lines|"), "linked_to_ing": linked, "unlinked": t["line_link|UNLINKED"],
            "pct_linked": _pct(linked, lines), "sr_top1_band_of_linked": grp("line_band|"),
            "pct_linked_band": {k: _pct(v, linked) for k, v in grp("line_band|").items()},
            "basis_counts": grp("line_basis|") and {k: v for k, v in grp("line_basis|").items() if "|" not in k},
            "basis_by_family": nest("line_basis|") and {k: v for k, v in nest("line_basis|").items()
                                                          if isinstance(v, dict)},
            "pct_basis_all_lines": {b: _pct(t[f"line_basis|{b}"], lines) for b in ("STATED_MASS", "SR_PORTION", "UNKNOWN")},
            "grams_any_band": t["lines_with_grams_any_band"], "grams_high_band_only": t["lines_with_grams_high_band_only"],
            "pct_grams_high_band_only": _pct(t["lines_with_grams_high_band_only"], lines),
            "usable_grams_at_band_floor": t["lines_with_usable_grams"], "band_floor": floor,
            "pct_usable_grams": _pct(t["lines_with_usable_grams"], lines), "pct_usable_by_basis": pct_basis,
            "usable_interval_lines_by_basis": grp("lines_usable_interval|"),
            "reason_counts": {k: v for k, v in grp("line_reason|").items() if "|" not in k},
            "reason_by_family": {k: v for k, v in nest("line_reason|").items() if isinstance(v, dict)},
            "link_by_family": {k: v for k, v in nest("line_link|").items() if isinstance(v, dict)},
        },
        "lots": {
            "total": lots, "by_kind": grp("lotkind|"), "by_family": grp("lotfam|"),
            "leaf_lots": t["leaf_lots"], "lots_by_replay_status": grp("lot_replay|"),
            "composition_kind_counts": comp_kinds,
            "pct_composition_kind": {k: _pct(v, lots) for k, v in comp_kinds.items()},
            "pct_interval_composition": _pct(comp_kinds["INTERVAL_EXACT_BOUNDS"], lots),
            "pct_single_member_point": _pct(comp_kinds["SINGLE_MEMBER_POINT"], lots),
            "pct_presence_only": _pct(comp_kinds["PRESENCE_ONLY"], lots),
            "composition_kind_by_lot_kind": nest("compkind|"), "composition_kind_by_family": nest("compfam|"),
            "leaf_composition_kind": grp("leaf_comp|"),
            "member_match_floor_counts": grp("match_floor|"),
            "composition_kind_by_match_floor": nest("compfloor|"),
            "lots_with_all_member_masses_known_by_match_floor": grp("all_member_masses_known|"),
            "ingredient_lot_member_link": grp("ingredient_lot_member|"),
            "ingredient_lot_member_band": grp("ingredient_lot_band|"),
            "pct_ingredient_lot_band": {k: _pct(v, sum(grp("ingredient_lot_band|").values()))
                                        for k, v in grp("ingredient_lot_band|").items()},
            "nutrient_value_types_in_point_or_interval_lots": nest("nutrient|"),
            "solute_load_types": nest("solute|"), "solute_unknown_reasons": nest("solute_reason|"),
            "water_activity_types": grp("water_activity|"),
            "ph_flags": nest("ph|"), "pct_ph_flag_unknown": {f: _pct(t[f"ph|{f}|UNKNOWN"], lots) for f in FLAGS},
            "pct_ph_flag_true": {f: _pct(t[f"ph|{f}|TRUE"], lots) for f in FLAGS},
            "ph_mask_counts": grp("ph_mask|"), "leaf_ph_contains_acid": grp("leaf_ph_contains_acid|"),
        },
        "exceptions_by_class": grp("exception|"),
    }
