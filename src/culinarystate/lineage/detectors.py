"""08a.3 LIN edge detectors B0, B1, B2, B3 and STRONG (pure, deterministic, ledger-free).

Contract: reports/step04/lineage_contract_v1_1.md sections 3.1, 3.3, 3.4, 4.2. Nothing here reads or writes a
ledger: functions take EVD-row-like dicts ("items", see `item_from_evd`) and return edge-candidate dicts.

Levels (each pair is emitted ONCE, at the strongest level that fires: STRONG > B0 > B1 > B2 > B3):
  B0      same source_id + same normalised table/row locator.
  B1      exact normalised key: analyte + matrix + process + value tuple (10 significant figures).
  B2      looser key: analyte + matrix token set + process steps (order-free) + value tuple at 3 s.f.
  B3      fuzzy numeric fingerprint inside a block (analyte, matrix head token): per-value match after unit /
          percent<->fraction / fresh<->dry (only when moisture is known) canonicalisation, or 1-2 s.f.
          rounding; pair score = matched values / values of the smaller side; edge iff score >= B3_CUT.
  STRONG  same explicit document reference (DOI, else document / study id) AND the B1 key.
Key-group levels (B0, B1, B2, STRONG) emit a star (member -> smallest id of the group): same union-find
connectivity as all pairs, linear edge count. B3 emits every passing pair not already joined by a stronger group.

B3_CUT = 0.75   FROZEN before any real EVD row was screened (THR-08A-19). Derivation: sweep of cut-points
0.05..1.00 (step 0.05) on scratch seeded pairs only (`seeding.generate_seeded_pairs(20261027, 100)`, 700 pairs);
B3_CUT is the highest cut-point at which every one of the seven perturbation classes has point recall >= 0.95
(`sweep_cut_for_recall`). Reason it is not higher: a one-cell transcription error in a 4-row record scores 3/4,
so any cut above 0.75 loses ONE_CELL_ERROR recall. No real row was used. Seeded recall at B3_CUT is 1.00 in all seven
classes (tests/unit/test_lineage_detectors.py).
# CONTRACT-AMBIGUITY: THR-08A-19 says "the loosest B3 score at which seeded recall >= 0.95". Lowest cut-point is
# trivially 0, so "loosest" is read as the most permissive cut that is still the highest meeting recall; flagged.
# CONTRACT-AMBIGUITY: the separate (stricter) B3 EDGE threshold is not registered: UNKNOWN. B3 edges here are emitted
# at B3_CUT and carry their score, so a later edge threshold can only filter them.

Edge status: every candidate is PROVISIONAL (the only non-human value the LIN schema allows); `audit_required`
is False for STRONG and B0, True otherwise.
# CONTRACT-AMBIGUITY: the contract does not define a non-PROVISIONAL machine status for STRONG / B0.
# CONTRACT-AMBIGUITY: the contract's B1 is identifier based (DOI/PMID/title/hash); the work order defines B1 as an exact
#   analyte+matrix+process+value key. The work-order definition is implemented; identifier B1 is not (EVD rows carry none).
# CONTRACT-AMBIGUITY: the contract gives no machine definition of the B2 / B3 keys; those above are proposals.
# CONTRACT-AMBIGUITY: STRONG in the contract is B3 + bibliography listing (PRIMARY_SOURCE); the work order defines it as
#   same DOI / document locator + identical value. Work-order definition implemented; no bibliography data used (UNKNOWN).
# CONTRACT-AMBIGUITY: LIN node types do not include EVD. Edges carry the EVD id plus AGG/OBS per Appendix B
#   (DATABASE_AGGREGATE / REVIEW_AGGREGATE -> AGG, else OBS); AGG/OBS ids are not minted (UNKNOWN).
# CONTRACT-AMBIGUITY: QUOTES_VALUES_FROM is directed (from = quoting/newer); creation order is unknown, so from = the
#   larger EVD id, to = the smaller (deterministic convention only).
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from itertools import combinations
from typing import Any, Iterable, Mapping, Sequence

from culinarystate.lineage.seeding import PERTURBATION_CLASSES, POINT_FLOOR, refuse_if_seeded

B3_CUT = 0.75
CUT_DETERMINATION_SEED = 20261027
CUT_DETERMINATION_N = 100
B1_SF = 10
B2_SF = 3
_RULE_TEXT = f"detectors-v1;B3_CUT={B3_CUT};B1_SF={B1_SF};B2_SF={B2_SF};rounding_sf=1,2"
RULE_VERSION = "detectors-v1-" + hashlib.sha256(_RULE_TEXT.encode()).hexdigest()[:12]
LEVEL_ORDER = ("STRONG", "B0", "B1", "B2", "B3")
_ROUND_SFS = (1, 2)  # THR-08A-17 perturbation class ROUNDING_1_2_SF
_MASS = {"ug": 1e-6, "mg": 1e-3, "g": 1.0}
_AGG_ORIGINS = ("DATABASE_AGGREGATE", "REVIEW_AGGREGATE")
_RATIONALE = {"STRONG": "SAME_DOC_REF_IDENTICAL_VALUE", "B0": "SAME_SRC_SAME_LOCATOR", "B1": "EXACT_KEY_MATCH",
              "B2": "LOOSE_KEY_MATCH", "B3": "NUMERIC_FINGERPRINT_SCORE_GE_CUT"}


# ------------------------------------------------------------------ normalisation
def normalise_text(s: Any) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-z']+", " ", str(s or "").lower())).strip()


def _stem(tok: str) -> str:
    return tok[:-1] if len(tok) > 3 and tok.endswith("s") and not tok.endswith("ss") else tok


def _matrix_tokens(s: Any) -> tuple[str, ...]:
    return tuple(_stem(t) for t in normalise_text(s).split())


def _norm_locator(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def _norm_doc_ref(s: Any) -> str:
    t = re.sub(r"\s+", "", str(s or "").strip().lower())
    return t


def _sf(x: float, n: int) -> float:
    return float(f"{x:.{n}g}")


def canonical_value(value: float, unit: str, basis: str | None = None,
                    moisture_fraction: float | None = None) -> tuple[str, float]:
    d, x, _k = _canon3(value, unit, basis, moisture_fraction)
    return d, x


def _canon3(value: float, unit: str, basis: str | None, moisture_fraction: float | None) -> tuple[str, float, float]:
    """Return (dimension, value) in canonical units: mass/100g in g/100g, fractions as fractions, fresh basis.

    Dry basis is converted to fresh only when moisture is known; otherwise the dimension keeps a '|dry' tag
    (UNKNOWN is never guessed). Unrecognised units keep their own dimension and are not converted.
    Third element k is the basis multiplier already applied (1.0 if none), so rounding done in the source
    basis can be compared after conversion."""
    u = str(unit or "").lower().replace("µ", "u").replace("mcg", "ug")
    u_ns = re.sub(r"\s+", "", u)
    if basis is None:
        basis = "dry" if "dryweight" in u_ns else ("fresh" if "freshweight" in u_ns else None)
    m = re.match(r"^(ug|mg|g)/100g", u_ns)
    if m:
        x = float(value) * _MASS[m.group(1)]
        dim, k = "mass/100g", 1.0
        if str(basis or "").lower().startswith("dry"):
            if moisture_fraction is not None:
                k = 1.0 - moisture_fraction
                x *= k
            else:
                dim += "|dry"
        return dim, x, k
    if u_ns == "%":
        return "fraction", float(value) / 100.0, 1.0
    if u_ns == "fraction":
        return "fraction", float(value), 1.0
    return "raw:" + u_ns, float(value), 1.0


def _values_match(a: float, b: float, ka: float = 1.0, kb: float = 1.0) -> bool:
    if math.isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
        return True
    return any(math.isclose(_sf(a / ka, s) * ka, b, rel_tol=1e-9, abs_tol=0.0)
               or math.isclose(_sf(b / kb, s) * kb, a, rel_tol=1e-9, abs_tol=0.0) for s in _ROUND_SFS)


# ------------------------------------------------------------------ items
def item_from_evd(row: Mapping[str, Any]) -> dict[str, Any]:
    """Normalised detector item from one EVD row (latest ACTIVE version). Only MEASURED numeric values are used."""
    vals = []
    for role in ("before", "after"):
        q = row.get(role)
        if isinstance(q, Mapping) and q.get("status") == "MEASURED" and isinstance(q.get("value"), (int, float)):
            vals.append({"role": role, "value": float(q["value"]), "unit": q.get("unit"), "basis": None})
    rf = (row.get("derived") or {}).get("retention_factor")
    if isinstance(rf, Mapping) and rf.get("status") == "MEASURED" and isinstance(rf.get("value"), (int, float)):
        vals.append({"role": "retention", "value": float(rf["value"]), "unit": rf.get("unit"), "basis": None})
    ident = row.get("identifiers") or {}
    studies = row.get("study_ids") or []
    doc_ref = (f"doi:{ident['doi']}" if ident.get("doi") else (f"study:{studies[0]}" if studies else None))
    process = row.get("process") or {}
    return {
        "id": row["id"], "source_id": row.get("source_id"), "family": row.get("source_family_id"),
        "locator": (row.get("provenance") or {}).get("locator"),
        "analyte": (row.get("target") or {}).get("raw_name"),
        "matrix": (row.get("matrix") or {}).get("raw_name"),
        "process": process.get("raw_name"), "steps": list(process.get("steps") or []),
        "values": vals, "doc_ref": doc_ref, "origin_type": row.get("origin_type"), "moisture_fraction": None,
    }


def _canon_values(it: Mapping[str, Any]) -> list[tuple[str, str, float, float]]:
    out = []
    for v in it.get("values") or []:
        dim, x, k = _canon3(v["value"], v.get("unit"), v.get("basis"), it.get("moisture_fraction"))
        out.append((v["role"], dim, x, k))
    return sorted(out)


def _tuple_score(a: Sequence[tuple], b: Sequence[tuple]) -> float:
    small, large = (a, b) if len(a) <= len(b) else (b, a)
    if not small:
        return 0.0
    hit = sum(1 for (r, d, x, k) in small
              if any(r == r2 and d == d2 and _values_match(x, x2, k, k2) for (r2, d2, x2, k2) in large))
    return hit / len(small)


# ------------------------------------------------------------------ record-level B3 (seeded test)
def _record_rows(rec: Mapping[str, Any]) -> list[tuple]:
    w = rec.get("moisture_fraction")
    return [(normalise_text(r["analyte"]),) + _canon3(r["value"], r.get("unit"), r.get("basis"), w)
            for r in rec["rows"]]


def record_b3_score(a: Mapping[str, Any], b: Mapping[str, Any]) -> float:
    """B3 score of two multi-row records (seeding.make_synthetic_record shape): matched rows / rows of the smaller."""
    ra, rb = _record_rows(a), _record_rows(b)
    return _tuple_score(ra, rb)


def record_b3_detects(a: Mapping[str, Any], b: Mapping[str, Any], cut: float = B3_CUT) -> bool:
    return record_b3_score(a, b) >= cut


def sweep_cut_for_recall(pairs: Sequence[Mapping[str, Any]], floor: float = POINT_FLOOR) -> float | None:
    """Highest cut in 0.05..1.00 (step 0.05) at which EVERY class has point recall >= floor; None if none."""
    scores: dict[str, list[float]] = {c: [] for c in PERTURBATION_CLASSES}
    for p in pairs:
        scores[p["seeded_class"]].append(record_b3_score(p["original"], p["copy"]))
    for i in range(20, 0, -1):
        cut = round(i * 0.05, 2)
        if all(s and sum(1 for v in s if v >= cut - 1e-12) / len(s) >= floor for s in scores.values()):
            return cut
    return None


# ------------------------------------------------------------------ edge detection
def _node_type(it: Mapping[str, Any]) -> str:
    return "AGG" if it.get("origin_type") in _AGG_ORIGINS else "OBS"


def _edge(level: str, a: Mapping[str, Any], b: Mapping[str, Any], *, method: str, score: float | None,
          basis: str, fields: list[str]) -> dict[str, Any]:
    frm, to = (a, b) if a["id"] > b["id"] else (b, a)
    return {
        "edge_key": f"QUOTES_VALUES_FROM|{frm['id']}|{to['id']}", "edge_type": "QUOTES_VALUES_FROM",
        "from_id": frm["id"], "to_id": to["id"], "from_node_type": _node_type(frm), "to_node_type": _node_type(to),
        "detector_level": level, "detection_method": method, "score": score, "score_basis": basis,
        "matched_fields": fields, "rationale_code": _RATIONALE[level], "edge_status": "PROVISIONAL",
        "audit_required": level not in ("STRONG", "B0"), "rule_version": RULE_VERSION, "seeded": False,
    }


def _group_keys(items: Sequence[Mapping[str, Any]], cv: dict[str, list]) -> dict[str, dict[str, Any]]:
    """level -> item id -> group key (items lacking a key are absent)."""
    out: dict[str, dict[str, Any]] = {lv: {} for lv in LEVEL_ORDER[:-1]}
    for it in items:
        i = it["id"]
        loc = _norm_locator(it.get("locator"))
        if it.get("source_id") and loc:
            out["B0"][i] = (it["source_id"], loc)
        if not cv[i]:
            continue
        an, mx, pr = normalise_text(it["analyte"]), normalise_text(it["matrix"]), normalise_text(it["process"])
        v10 = tuple((r, d, _sf(x, B1_SF)) for r, d, x, _k in cv[i])
        out["B1"][i] = (an, mx, pr, v10)
        steps = tuple(sorted(normalise_text(s) for s in it.get("steps") or [])) or (pr,)
        out["B2"][i] = (an, tuple(sorted(set(_matrix_tokens(it["matrix"])))), steps,
                        tuple((r, d, _sf(x, B2_SF)) for r, d, x, _k in cv[i]))
        ref = _norm_doc_ref(it.get("doc_ref"))
        if ref:
            out["STRONG"][i] = (ref, out["B1"][i])
    return out


def detect_edges(items: Iterable[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return (edge candidates, stats). Order independent; refuses seeded items; never writes anything."""
    its = sorted(items, key=lambda x: x["id"])
    for it in its:
        refuse_if_seeded(it)
    by_id = {it["id"]: it for it in its}
    cv = {it["id"]: _canon_values(it) for it in its}
    keys = _group_keys(its, cv)
    edges: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    group_of: dict[str, dict[str, Any]] = {}
    stats: dict[str, Any] = {"n_items": len(its), "rows_without_numeric_value": sum(1 for i in cv if not cv[i])}

    for lv in LEVEL_ORDER[:-1]:
        groups: dict[Any, list[str]] = defaultdict(list)
        for i, k in keys[lv].items():
            groups[k].append(i)
        group_of[lv] = {i: (lv, k) for i, k in keys[lv].items() if len(groups[k]) > 1}
        stats[f"{lv.lower()}_groups_ge2"] = sum(1 for g in groups.values() if len(g) > 1)
        stats[f"{lv.lower()}_largest_group"] = max((len(g) for g in groups.values()), default=0)
        for k in sorted(groups, key=repr):
            g = sorted(groups[k])
            for m in g[1:]:
                if (g[0], m) in seen:
                    continue
                seen.add((g[0], m))
                a, b = by_id[g[0]], by_id[m]
                if lv == "B0":
                    edges.append(_edge(lv, a, b, method="OTHER", score=None, basis="same SRC and locator",
                                       fields=["source_id", "locator"]))
                elif lv == "STRONG":
                    method = "DOI_MATCH" if k[0].startswith("doi:") else "OTHER"
                    edges.append(_edge(lv, a, b, method=method, score=1.0, basis="same document ref + exact key",
                                       fields=["doc_ref", "analyte", "matrix", "process", "values"]))
                else:
                    sc = _tuple_score(cv[g[0]], cv[m])
                    edges.append(_edge(lv, a, b, method="NUMERIC_FINGERPRINT", score=sc,
                                       basis=f"{lv} key group", fields=["analyte", "matrix", "process", "values"]))

    blocks: dict[tuple[str, str], list[str]] = defaultdict(list)
    for it in its:
        if cv[it["id"]]:
            toks = normalise_text(it["matrix"]).split()
            blocks[(normalise_text(it["analyte"]), _stem(toks[0]) if toks else "")].append(it["id"])
    stats["n_blocks"] = len(blocks)
    stats["largest_block"] = max((len(b) for b in blocks.values()), default=0)
    big = max(blocks, key=lambda k: (len(blocks[k]), k), default=None)
    stats["largest_block_key"] = list(big) if big else None
    stats["b3_pairs_compared"] = sum(len(b) * (len(b) - 1) // 2 for b in blocks.values())
    for k in sorted(blocks):
        for ia, ib in combinations(sorted(blocks[k]), 2):
            if (ia, ib) in seen or any(group_of[lv].get(ia) is not None and group_of[lv].get(ia) == group_of[lv].get(ib)
                                       for lv in LEVEL_ORDER[:-1]):
                continue
            sc = _tuple_score(cv[ia], cv[ib])
            if sc >= B3_CUT:
                seen.add((ia, ib))
                edges.append(_edge("B3", by_id[ia], by_id[ib], method="NUMERIC_FINGERPRINT", score=sc,
                                   basis="matched values / values of smaller side",
                                   fields=["analyte", "matrix_head", "values"]))
    order = {lv: n for n, lv in enumerate(LEVEL_ORDER)}
    edges.sort(key=lambda e: (order[e["detector_level"]], e["from_id"], e["to_id"]))
    return edges, stats


def edges_to_jsonl(edges: Sequence[Mapping[str, Any]]) -> str:
    return "".join(json.dumps(e, sort_keys=True, separators=(",", ":")) + "\n" for e in edges)
