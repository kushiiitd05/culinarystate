"""Reusable EDA / data-quality report over the ledgers (plan P14, Part M/AA).

`build_report(store)` returns a dict of sections; `to_html` / `to_markdown` render it. Generic per-ledger
profiling (counts, versions, status, verification, provenance, field missingness incl. UNKNOWN) plus
specialised sections for evidence (tiers, censoring, conditions, sparsity, duplicates, conflicts, lineage),
ingredients (crosswalks, ambiguity, long tail) and processes (evidence coverage).
"""
from __future__ import annotations

import html
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone

from culinarystate.ledgers.store import LedgerStore


def _flatten(d: dict, prefix: str = "", depth: int = 2) -> dict:
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict) and depth > 0 and "status" not in v:
            out.update(_flatten(v, key + ".", depth - 1))
        else:
            out[key] = v
    return out


def _missing(v) -> str | None:
    if v is None or v == [] or v == "":
        return "empty"
    if isinstance(v, dict) and v.get("status") in ("UNKNOWN", "NOT_APPLICABLE"):
        return v["status"].lower()
    return None


def profile_ledger(store: LedgerStore, prefix: str) -> dict:
    rows = store._rows(prefix)
    latest = store.all_latest(prefix)
    if not latest:
        return {"prefix": prefix, "records": 0}
    fields = Counter()
    miss = defaultdict(Counter)
    for r in latest:
        flat = _flatten({k: v for k, v in r.items() if k not in ("provenance", "verification")})
        for k, v in flat.items():
            fields[k] += 1
            m = _missing(v)
            if m:
                miss[k][m] += 1
    n = len(latest)
    missingness = sorted(((k, round(sum(miss[k].values()) / n, 4), dict(miss[k])) for k in fields
                          if miss[k]), key=lambda t: -t[1])
    return {
        "prefix": prefix, "records": n, "versions": len(rows),
        "status": dict(Counter(r["status"] for r in latest)),
        "verification": dict(Counter(r["verification"]["status"] for r in latest)),
        "provenance_method": dict(Counter(r["provenance"]["method"] for r in latest)),
        "top_sources": Counter(s for r in latest for s in r["provenance"].get("source_ids", [])).most_common(8),
        "missingness": missingness[:25],
    }


def evidence_section(store: LedgerStore) -> dict:
    evd = store.all_latest("EVD")
    if not evd:
        return {}
    cond = {c["id"]: c for c in store.all_latest("COND")}
    n = len(evd)
    axes = Counter()
    complete_any_temp = 0
    for e in evd:
        c = cond.get(e["process"].get("condition_id") or "")
        mask = (c or {}).get("completeness_mask", {})
        for ax, st in mask.items():
            axes[(ax, st)] += 1
        complete_any_temp += mask.get("temperature") in ("MEASURED", "RANGE")
    axis_table = defaultdict(dict)
    for (ax, st), k in axes.items():
        axis_table[ax][st] = k
    cells = Counter((e["matrix"]["raw_name"].lower(), tuple(e["process"].get("steps", [])), e["target"]["raw_name"].lower())
                    for e in evd)
    pairs = Counter((e["matrix"]["raw_name"].lower(), tuple(e["process"].get("steps", []))) for e in evd)
    matrices = Counter(e["matrix"]["raw_name"].lower() for e in evd)
    procs = Counter(s for e in evd for s in e["process"].get("steps", []))
    targets = Counter(e["target"]["raw_name"].lower() for e in evd)
    density = len(pairs) / (len(matrices) * max(1, len({p for _, p in pairs})))
    # duplicates: identical cell from same source family; conflicts: same cell, opposite direction, independent groups
    dup = sum(c - 1 for c in Counter((k, e["source_family_id"]) for e in evd
                                     for k in [(e["matrix"]["raw_name"].lower(), tuple(e["process"].get("steps", [])),
                                                e["target"]["raw_name"].lower())]).values() if c > 1)
    by_cell = defaultdict(list)
    for e in evd:
        k = (e["matrix"]["raw_name"].lower(), tuple(e["process"].get("steps", [])), e["target"]["raw_name"].lower())
        by_cell[k].append(e)
    conflicts = []
    for k, es in by_cell.items():
        dirs = {(x["derived"].get("direction"), x.get("independence_group")) for x in es}
        d_only = {d for d, _ in dirs if d in ("INCREASE", "DECREASE")}
        groups = {g for _, g in dirs}
        if len(d_only) == 2 and len(groups) > 1:
            conflicts.append({"cell": " | ".join([k[0], ">".join(k[1]), k[2]]), "rows": len(es),
                              "groups": len(groups)})
    return {
        "rows": n,
        "tier": dict(Counter(e["tier"] for e in evd)),
        "origin_type": dict(Counter(e["origin_type"] for e in evd)),
        "source_family": dict(Counter(e["source_family_id"] for e in evd)),
        "study_lineage": dict(Counter(e["study_id_status"] for e in evd)),
        "independent_groups": len({e.get("independence_group") for e in evd}),
        "censored_rows": sum(e["censored"] for e in evd),
        "retention_factor_status": dict(Counter(e["derived"].get("retention_factor", {}).get("status", "ABSENT")
                                                for e in evd)),
        "direction": dict(Counter(e["derived"].get("direction", "ABSENT") for e in evd)),
        "target_basis": dict(Counter(e["target"]["basis"] for e in evd)),
        "ingredient_id_linked": round(sum(bool(e["matrix"]["ingredient_id"]) for e in evd) / n, 4),
        "process_id_linked": round(sum(bool(e["process"].get("process_id") or e["process"].get("step_process_ids"))
                                       for e in evd) / n, 4),
        "condition_axes": dict(axis_table),
        "rows_with_temperature": complete_any_temp,
        "unique_matrices": len(matrices), "unique_step_sequences": len({p for _, p in pairs}),
        "unique_targets": len(targets), "unique_cells": len(cells),
        "matrix_process_density": round(density, 4),
        "rows_per_matrix_top": matrices.most_common(10),
        "matrix_long_tail": {"matrices_with_1_row": sum(1 for c in matrices.values() if c == 1),
                             "median_rows_per_matrix": sorted(matrices.values())[len(matrices) // 2]},
        "process_steps_top": procs.most_common(15),
        "duplicate_rows_same_family": dup,
        "conflict_candidates": len(conflicts), "conflict_examples": conflicts[:15],
    }


def ingredient_section(store: LedgerStore) -> dict:
    ing = store.all_latest("ING")
    if not ing:
        return {}
    xw = defaultdict(Counter)
    for r in ing:
        for k, v in (r.get("crosswalks") or {}).items():
            xw[k][v["status"]] += 1
    freqs = sorted((r.get("corpus_frequency") or 0 for r in ing), reverse=True)
    top10 = sum(freqs[: max(1, len(freqs) // 10)]) / max(1, sum(freqs))
    return {"concepts": len(ing), "active": sum(r["status"] == "ACTIVE" for r in ing),
            "ambiguity": dict(Counter(r.get("ambiguity") for r in ing)),
            "with_parent": sum(bool(r.get("parent_ids")) for r in ing),
            "scientific_identity": dict(Counter(r["scientific_identity_status"] for r in ing)),
            "crosswalks": {k: dict(v) for k, v in xw.items()},
            "frequency_share_top10pct": round(top10, 4),
            "aliases": len(store.all_latest("ALIAS"))}


def process_section(store: LedgerStore) -> dict:
    pr = store.all_latest("PROC")
    if not pr:
        return {}
    zero = [p["canonical_name"] for p in sorted(pr, key=lambda p: -(p.get("corpus_frequency") or 0))
            if not p.get("evidence_coverage") and p["kind"] == "ACTION" and (p.get("corpus_frequency") or 0) > 0]
    return {"processes": len(pr), "family": dict(Counter(p["family"] for p in pr)),
            "kind": dict(Counter(p["kind"] for p in pr)),
            "with_evidence": sum(bool(p.get("evidence_coverage")) for p in pr),
            "corpus_actions_without_evidence": len(zero), "top_unevidenced_by_corpus_freq": zero[:25]}


def build_report(store: LedgerStore, prefixes: tuple[str, ...] | None = None) -> dict:
    prefixes = prefixes or tuple(sorted(p.name[:-6] for p in store.root.glob("*.jsonl") if not p.name.startswith("_")))
    return {"generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "ledgers": {p: profile_ledger(store, p) for p in prefixes},
            "evidence": evidence_section(store), "ingredients": ingredient_section(store),
            "processes": process_section(store)}


# ------------------------------------------------------------------ rendering
def _bar(k: float, total: float) -> str:
    w = 0 if not total else max(1, int(160 * k / total))
    return f'<span class="bar" style="width:{w}px"></span>'


def _dict_table(d: dict) -> str:
    if not d:
        return "<p class='muted'>none</p>"
    total = sum(v for v in d.values() if isinstance(v, (int, float)))
    rows = "".join(f"<tr><td>{html.escape(str(k))}</td><td class='num'>{v:,}</td><td>{_bar(v, total)}</td></tr>"
                   if isinstance(v, (int, float)) else
                   f"<tr><td>{html.escape(str(k))}</td><td colspan=2>{html.escape(str(v))}</td></tr>"
                   for k, v in sorted(d.items(), key=lambda kv: -kv[1] if isinstance(kv[1], (int, float)) else 0))
    return f"<table>{rows}</table>"


def _kv(section: dict) -> str:
    parts = []
    for k, v in section.items():
        if isinstance(v, dict) and v and all(isinstance(x, (int, float)) for x in v.values()):
            parts.append(f"<h4>{html.escape(k)}</h4>{_dict_table(v)}")
        elif isinstance(v, dict):
            inner = "".join(f"<h5>{html.escape(str(a))}</h5>{_dict_table(b) if isinstance(b, dict) else html.escape(str(b))}"
                            for a, b in v.items())
            parts.append(f"<h4>{html.escape(k)}</h4>{inner}")
        elif isinstance(v, list):
            items = "".join(f"<li>{html.escape(str(x))}</li>" for x in v[:25])
            parts.append(f"<h4>{html.escape(k)}</h4><ul>{items}</ul>")
        else:
            parts.append(f"<p><b>{html.escape(k)}</b>: {html.escape(str(v))}</p>")
    return "".join(parts)


CSS = """body{font:14px/1.45 -apple-system,system-ui,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;
color:#1f2328;background:#fff}h1{font-size:22px}h2{border-bottom:1px solid #d0d7de;padding-bottom:4px;margin-top:32px}
table{border-collapse:collapse;margin:6px 0 12px}td{padding:2px 10px 2px 0;vertical-align:top}.num{text-align:right;
font-variant-numeric:tabular-nums}.bar{display:inline-block;height:9px;background:#4c78a8;border-radius:2px}
.muted{color:#656d76}@media (prefers-color-scheme:dark){body{background:#0d1117;color:#e6edf3}.bar{background:#79a6d8}}"""


def to_html(rep: dict, title: str = "CulinaryState ledger EDA") -> str:
    secs = [f"<h1>{html.escape(title)}</h1><p class='muted'>generated {rep['generated_at']}</p>"]
    for name in ("evidence", "ingredients", "processes"):
        if rep.get(name):
            secs.append(f"<h2>{name.title()}</h2>{_kv(rep[name])}")
    secs.append("<h2>Per-ledger profiles</h2>")
    for p, prof in rep["ledgers"].items():
        if not prof.get("records"):
            continue
        miss = "".join(f"<tr><td>{html.escape(k)}</td><td class='num'>{f:.1%}</td><td>{html.escape(str(d))}</td></tr>"
                       for k, f, d in prof["missingness"])
        secs.append(f"<h3>{p} — {prof['records']:,} records / {prof['versions']:,} versions</h3>"
                    f"{_kv({k: prof[k] for k in ('status', 'verification', 'provenance_method')})}"
                    f"<h4>missingness (empty / UNKNOWN)</h4><table>{miss}</table>")
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Ledger EDA</title><style>{CSS}</style></head>" \
           f"<body>{''.join(secs)}</body></html>"


def to_markdown(rep: dict) -> str:
    lines = [f"# Ledger EDA summary ({rep['generated_at']})", "", "| Ledger | records | versions | verification |",
             "|---|---|---|---|"]
    for p, prof in rep["ledgers"].items():
        if prof.get("records"):
            lines.append(f"| {p} | {prof['records']:,} | {prof['versions']:,} | {prof['verification']} |")
    ev = rep.get("evidence") or {}
    if ev:
        lines += ["", "## Evidence", ""] + [f"- **{k}**: {v}" for k, v in ev.items()
                                            if k not in ("condition_axes", "conflict_examples", "rows_per_matrix_top")]
    for name in ("ingredients", "processes"):
        if rep.get(name):
            lines += ["", f"## {name.title()}", ""] + [f"- **{k}**: {v}" for k, v in rep[name].items()]
    return "\n".join(lines) + "\n"
