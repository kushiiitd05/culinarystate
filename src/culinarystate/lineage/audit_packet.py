"""Blind two-reviewer packets for the 08a.8 edge audit and the natural-duplicate miss review.

THR-08A-16: stratified by detector level (B2, B3, STRONG), n >= 50 per stratum or a 100% audit when fewer exist.
THR-08A-18: >= 200 random blocked-together pairs that have NO edge, reported only (no pass/fail).
THR-08A-13 / G08-H: both reviewers get the same rows in a different order; detector name, score and stratum
are kept out of the reviewer files (sealed key file only); returned files are provenance-validated.
Pure and deterministic: the same seed gives byte-identical files.
"""
from __future__ import annotations

import csv
import hashlib
import os
import random
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from culinarystate.lineage.wilson import wilson_interval

STRATA = ("B2", "B3", "STRONG")
N_PER_STRATUM = 50  # THR-08A-16
N_UNLINKED_PAIRS = 200  # THR-08A-18
REVIEWERS = ("Kush", "Parv")
# CONTRACT-AMBIGUITY: neither the plan, the contract nor THR-08A-13/16 fixes the judgement codes; the three
# codes below are the set named by the 08a.8 work order (D-032) and must be confirmed by the signer.
EDGE_JUDGEMENT_CODES = ("CORRECT_EDGE", "WRONG_EDGE", "UNCERTAIN")
# CONTRACT-AMBIGUITY: codes for the THR-08A-18 pair review are not specified anywhere; proposed here.
MISSED_PAIR_JUDGEMENT_CODES = ("TRUE_DUPLICATE", "NOT_DUPLICATE", "UNCERTAIN")

EDGE_JUDGEMENT_COL = "edge_judgement"
PAIR_JUDGEMENT_COL = "pair_judgement"
REASON_COL = "reason_if_not_correct"
_EDGE_HEADER = ("audit_id", "edge_type", "from_id", "to_id", "from_summary", "to_summary", EDGE_JUDGEMENT_COL, REASON_COL)
_PAIR_HEADER = ("audit_id", "from_id", "to_id", "from_summary", "to_summary", PAIR_JUDGEMENT_COL, REASON_COL)

_EDGE_INSTRUCTIONS = """# Edge audit packet (blind)
For each row, judge whether the two records really are linked as the edge_type says. Use exactly one of: {codes}.
Fill the `{col}` column only; optionally explain in `{reason}`. Do not edit any other cell.
Judge only the texts shown. Do not look up the detector, do not look at the other reviewer's file, do not open the sealed key file.
A false merge is worse than a missed duplicate: when unsure choose UNCERTAIN. Detector, score and stratum are hidden on purpose.
"""
_PAIR_INSTRUCTIONS = """# Missed-duplicate review packet (blind)
These pairs were compared by the detector and NOT linked. Judge whether each pair is a true duplicate / re-use of the same data.
Use exactly one of: {codes}. Fill the `{col}` column only; optionally explain in `{reason}`. Do not edit any other cell.
Do not look at the other reviewer's file or the sealed key file. When unsure choose UNCERTAIN.
"""


def _write_csv(path: Path, header: Sequence[str], rows: Iterable[Mapping[str, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(header), lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _orders(ids: list[str], seed: int, reviewers: Sequence[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for name in reviewers:
        salt = 0
        while True:
            order = list(ids)
            random.Random(f"{seed}:order:{name}:{salt}").shuffle(order)
            if len(ids) < 2 or all(order != o for o in out.values()):
                break
            salt += 1
        out[name] = order
    return out


def _emit(
    items: list[dict[str, Any]], key_rows: list[dict[str, Any]], key_cols: Sequence[str], header: Sequence[str],
    instructions: str, seed: int, out_dir: Path, prefix: str, reviewers: Sequence[str], prefix_id: str,
) -> dict[str, Any]:
    """items: reviewer-visible dicts (without audit_id) aligned with key_rows."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    perm = list(range(len(items)))
    random.Random(f"{seed}:ids").shuffle(perm)
    rows: dict[str, dict[str, Any]] = {}
    keys: list[dict[str, Any]] = []
    for n, i in enumerate(perm, start=1):
        aid = f"{prefix_id}-{n:04d}"
        rows[aid] = {**items[i], "audit_id": aid}
        keys.append({**key_rows[i], "audit_id": aid})
    ids = sorted(rows)
    files: dict[str, Path] = {}
    for name, order in _orders(ids, seed, reviewers).items():
        p = out_dir / f"{prefix}_{name}.csv"
        _write_csv(p, header, ({**rows[a], header[-2]: "", REASON_COL: ""} for a in order))
        files[name] = p
    key_path = out_dir / f"{prefix}_KEY_SEALED.csv"
    _write_csv(key_path, ["audit_id", *key_cols], sorted(keys, key=lambda k: k["audit_id"]))
    ins_path = out_dir / f"{prefix}_INSTRUCTIONS.md"
    ins_path.write_text(instructions, encoding="utf-8")
    return {"reviewer_files": files, "key_file": key_path, "instructions_file": ins_path, "n_rows": len(rows)}


def build_edge_audit_packets(
    edges: Sequence[Mapping[str, Any]], seed: int, out_dir: str | os.PathLike, prefix: str,
    n_per_stratum: int = N_PER_STRATUM, reviewers: Sequence[str] = REVIEWERS,
) -> dict[str, Any]:
    """Stratified (B2, B3, STRONG) blind edge-audit packets. Edge dicts need: edge_id, from_id, to_id, edge_type,
    detector_level, detection_method, score; optional from_summary / to_summary (reviewer-visible text)."""
    if n_per_stratum < N_PER_STRATUM:
        raise ValueError(f"n_per_stratum must be >= {N_PER_STRATUM} (THR-08A-16), got {n_per_stratum}")
    items: list[dict[str, Any]] = []
    keys: list[dict[str, Any]] = []
    counts: dict[str, dict[str, int]] = {}
    for lvl in STRATA:
        pool = sorted((e for e in edges if e["detector_level"] == lvl), key=lambda e: str(e["edge_id"]))
        if len(pool) <= n_per_stratum:
            chosen = pool
        else:
            chosen = sorted(random.Random(f"{seed}:stratum:{lvl}").sample(pool, n_per_stratum), key=lambda e: str(e["edge_id"]))
        counts[lvl] = {"available": len(pool), "audited": len(chosen)}
        for e in chosen:
            items.append({"edge_type": e["edge_type"], "from_id": e["from_id"], "to_id": e["to_id"],
                          "from_summary": e.get("from_summary", ""), "to_summary": e.get("to_summary", "")})
            keys.append({"edge_id": e["edge_id"], "stratum": lvl, "detector_level": e["detector_level"],
                         "detection_method": e.get("detection_method", ""), "score": e.get("score", "")})
    res = _emit(items, keys, ["edge_id", "stratum", "detector_level", "detection_method", "score"], _EDGE_HEADER,
                _EDGE_INSTRUCTIONS.format(codes=", ".join(EDGE_JUDGEMENT_CODES), col=EDGE_JUDGEMENT_COL, reason=REASON_COL),
                seed, Path(out_dir), prefix, reviewers, "EA")
    res["strata_counts"] = counts
    return res


def draw_unlinked_pairs(
    blocked_pairs: Iterable[Sequence[str]], edge_pairs: Iterable[Iterable[str]], seed: int, n: int = N_UNLINKED_PAIRS,
) -> list[tuple[str, str]]:
    """Random candidate pairs that were blocked together but have NO edge (THR-08A-18). Returns all of them if fewer than n."""
    if n < N_UNLINKED_PAIRS:
        raise ValueError(f"n must be >= {N_UNLINKED_PAIRS} (THR-08A-18), got {n}")
    linked = {frozenset(p) for p in edge_pairs}
    seen: dict[frozenset, tuple[str, str]] = {}
    for a, b in blocked_pairs:
        k = frozenset((a, b))
        if len(k) == 2 and k not in linked and k not in seen:
            seen[k] = (min(a, b), max(a, b))
    pool = sorted(seen.values())
    if len(pool) <= n:
        return pool
    return sorted(random.Random(f"{seed}:unlinked").sample(pool, n))


def build_missed_pair_packets(
    pairs: Sequence[Mapping[str, Any]], seed: int, out_dir: str | os.PathLike, prefix: str, reviewers: Sequence[str] = REVIEWERS,
) -> dict[str, Any]:
    """Blind packets for the unlinked-pair review. Pair dicts: pair_id, from_id, to_id, optional from_summary / to_summary."""
    items = [{"from_id": p["from_id"], "to_id": p["to_id"], "from_summary": p.get("from_summary", ""), "to_summary": p.get("to_summary", "")}
             for p in pairs]
    keys = [{"pair_id": p["pair_id"]} for p in pairs]
    return _emit(items, keys, ["pair_id"], _PAIR_HEADER,
                 _PAIR_INSTRUCTIONS.format(codes=", ".join(MISSED_PAIR_JUDGEMENT_CODES), col=PAIR_JUDGEMENT_COL, reason=REASON_COL),
                 seed, Path(out_dir), prefix, reviewers, "MP")


def miss_rate_report(duplicates_found: int, n_reviewed: int) -> dict[str, Any]:
    """THR-08A-18: duplicates found among unlinked pairs and the Wilson 95% upper bound of the miss rate. Report only."""
    lo, hi = wilson_interval(duplicates_found, n_reviewed)
    return {"duplicates_found": duplicates_found, "n_reviewed": n_reviewed, "miss_rate": (duplicates_found / n_reviewed) if n_reviewed else None,
            "wilson_lower_miss_rate": lo, "wilson_upper_miss_rate": hi, "gate": "REPORT_ONLY"}


def _load(path: str | os.PathLike) -> tuple[list[str], dict[str, dict[str, str]]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        rows = list(r)
        return list(r.fieldnames or []), {row["audit_id"]: row for row in rows}


def _sha(path: str | os.PathLike) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_returned_packets(
    blank: str | os.PathLike, a_path: str | os.PathLike, b_path: str | os.PathLike, judgement_col: str, allowed: Sequence[str],
) -> dict[str, Any]:
    """Provenance precheck of two returned files (mirrors tools/step07_provenance_precheck.py). Never edits or reports labels."""
    problems: list[str] = []
    hb, B = _load(blank)
    loaded = {}
    for name, p in (("A", a_path), ("B", b_path)):
        h, rows = _load(p)
        loaded[name] = rows
        if h != hb:
            problems.append(f"{name}: header differs from the blank packet")
        if set(rows) != set(B):
            problems.append(f"{name}: audit_id set differs from the blank packet")
        fixed = [c for c in hb if c not in (judgement_col, REASON_COL)]
        bad = sum(1 for i in set(rows) & set(B) for c in fixed if (rows[i].get(c) or "") != (B[i].get(c) or ""))
        if bad:
            problems.append(f"{name}: {bad} non-judgement cells differ from the blank packet")
        vals = [(r.get(judgement_col) or "").strip() for r in rows.values()]
        empty = sum(1 for v in vals if not v)
        if empty:
            problems.append(f"{name}: {empty} judgement cells are empty")
        outside = sum(1 for v in vals if v and v not in allowed)
        if outside:
            problems.append(f"{name}: {outside} judgement cells are not in the allowed code set")
    if _sha(a_path) == _sha(b_path):
        problems.append("the two returned files are byte-identical")
    return {"status": "INVALID_PROVENANCE" if problems else "VALID", "problems": problems,
            "sha256": {"blank": _sha(blank), "A": _sha(a_path), "B": _sha(b_path)},
            "note": "Process-integrity precheck only. Does not compute agreement or precision."}


def validate_returned_edge_packets(blank: str | os.PathLike, a_path: str | os.PathLike, b_path: str | os.PathLike) -> dict[str, Any]:
    return validate_returned_packets(blank, a_path, b_path, EDGE_JUDGEMENT_COL, EDGE_JUDGEMENT_CODES)


def validate_returned_pair_packets(blank: str | os.PathLike, a_path: str | os.PathLike, b_path: str | os.PathLike) -> dict[str, Any]:
    return validate_returned_packets(blank, a_path, b_path, PAIR_JUDGEMENT_COL, MISSED_PAIR_JUDGEMENT_CODES)
