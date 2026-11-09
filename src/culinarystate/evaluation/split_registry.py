"""Split registry for the evaluations that will run (S178; consensus T9-C09-R1; REV-B G-06/G-10). DRAFT.

One CSV row per registered split or block: what the unit is, how many units, the seed and rule, the source artifact
with its sha256, a hash of the ids, and the checks that were run. Ids and hashes only; no recipe text and no ledger
text. The registry makes a later change to any evaluation set visible (the ids hash changes), it does not freeze
anything: ``status`` says whether the set is a draft, provisional (waiting for the 15a.R seal) or issued.

Pure helpers here; the tool ``tools/s178_build_split_registry.py`` reads the benchmark drafts, the EVD ledger and the
07.A-R1 inputs and calls them. ``verify_registry`` recomputes hashes from the unit listing so that an edited registry,
or an edited unit file, fails loudly.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Iterable, Mapping, Sequence

VERSION = "split_registry@0.1"
COLUMNS = ["registry_id", "evaluation", "block_or_split", "source_family", "split_unit", "n_units", "roles",
           "ids_sha256", "unit_ids_sha256", "seed", "seed_rule", "source_artifact", "source_sha256", "code_artifact",
           "code_sha256", "snapshot_id", "status", "checks", "notes"]
UNIT_COLUMNS = ["registry_id", "unit_id", "role", "attributes"]
REQUIRED = ["registry_id", "evaluation", "block_or_split", "split_unit", "n_units", "ids_sha256", "seed_rule",
            "source_artifact", "status"]
STATUSES = ("DRAFT_UNFROZEN", "PROVISIONAL_PRE_SEAL", "PACKET_ISSUED_DRAFT", "NOT_DRAFTED")
EVALUATIONS = ("D5_BENCHMARK", "DIAG29", "07A_R1")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def ids_sha256(ids: Iterable[str]) -> str:
    """sha256 over the sorted ids joined by newline (the convention of the 07.A-R1 manifest's excluded_set_sha256)."""
    return sha256_bytes("\n".join(sorted(str(i) for i in ids)).encode("utf-8"))


def assignment_sha256(pairs: Iterable[tuple[str, str]]) -> str:
    """sha256 over sorted ``unit<TAB>role`` lines: pins which unit sits in which role."""
    return sha256_bytes("\n".join(f"{u}\t{r}" for u, r in sorted((str(u), str(r)) for u, r in pairs)).encode("utf-8"))


def make_row(**kw: object) -> dict[str, str]:
    """A registry row with every column present (empty string when not given); unknown keys are refused."""
    unknown = sorted(set(kw) - set(COLUMNS))
    if unknown:
        raise ValueError(f"unknown registry column(s): {unknown}")
    row = {c: "" if kw.get(c) is None else str(kw[c]) for c in COLUMNS}
    missing = [c for c in REQUIRED if not row[c]]
    if missing:
        raise ValueError(f"registry row missing required field(s): {missing}")
    if row["status"] not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    if row["evaluation"] not in EVALUATIONS:
        raise ValueError(f"evaluation must be one of {EVALUATIONS}")
    return row


def disjoint_report(groups: Mapping[str, Iterable[str]]) -> dict[str, int]:
    """Pairwise overlap counts between named id groups (empty dict = all disjoint)."""
    names = sorted(groups)
    sets = {n: set(map(str, groups[n])) for n in names}
    out = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            k = len(sets[a] & sets[b])
            if k:
                out[f"{a}&{b}"] = k
    return out


def write_registry(rows: Sequence[Mapping[str, str]], units: Sequence[Mapping[str, str]], registry_path: Path,
                   units_path: Path) -> dict[str, str]:
    """Write the registry and its unit listing; refuses to overwrite either (a new version is a new file)."""
    seen = set()
    for r in rows:
        if r["registry_id"] in seen:
            raise ValueError(f"duplicate registry_id {r['registry_id']}")
        seen.add(r["registry_id"])
    with open(registry_path, "x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with open(units_path, "x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=UNIT_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(units)
    return {"registry_sha256": sha256_file(registry_path), "units_sha256": sha256_file(units_path)}


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def verify_registry(registry_path: Path, units_path: Path | None = None) -> list[str]:
    """Findings (empty = consistent). Checks columns, required fields, statuses, unique ids and, for rows with a unit
    listing, that n_units and ids_sha256 match the listed units."""
    out: list[str] = []
    rows = read_csv(registry_path)
    if not rows:
        return ["EMPTY_REGISTRY"]
    if list(rows[0]) != COLUMNS:
        out.append("COLUMNS_MISMATCH")
    ids = [r["registry_id"] for r in rows]
    out += [f"DUPLICATE_ID: {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for r in rows:
        out += [f"MISSING_{c.upper()}: {r['registry_id']}" for c in REQUIRED if not r.get(c)]
        if r["status"] not in STATUSES:
            out.append(f"BAD_STATUS: {r['registry_id']}")
    if units_path is not None:
        by: dict[str, list[dict[str, str]]] = {}
        for u in read_csv(units_path):
            by.setdefault(u["registry_id"], []).append(u)
        for r in rows:
            us = by.get(r["registry_id"])
            if us is None:
                continue
            if str(len(us)) != r["n_units"]:
                out.append(f"N_UNITS_MISMATCH: {r['registry_id']} ({len(us)} listed, {r['n_units']} registered)")
            if r["ids_sha256"] != ids_sha256(u["unit_id"] for u in us) and \
                    r["ids_sha256"] != assignment_sha256((u["unit_id"], u["role"]) for u in us):
                out.append(f"IDS_SHA256_MISMATCH: {r['registry_id']}")
        out += [f"UNITS_WITHOUT_ROW: {k}" for k in sorted(set(by) - set(ids))]
    return out
