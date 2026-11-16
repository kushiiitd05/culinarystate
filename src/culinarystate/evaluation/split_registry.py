"""Split registry for the evaluations that will run (S178; consensus T9-C09-R1; REV-B G-06/G-10). DRAFT.

One CSV row per registered split or block: what the unit is, how many units, the seed and rule, the source artifact
with its sha256, a hash of the ids, and the checks that were run. Ids and hashes only; no recipe text and no ledger
text. The registry makes a later change to any evaluation set visible (the ids hash changes), it does not freeze
anything: ``status`` says whether the set is a draft, provisional (waiting for the 15a.R seal) or issued.

Pure helpers here; the tool ``tools/s178_build_split_registry.py`` reads the benchmark drafts, the EVD ledger and the
07.A-R1 inputs and calls them. ``verify_registry`` recomputes hashes from the unit listing so that an edited registry,
or an edited unit file, fails loudly.

S178 FIX-EVAL (SCI-B E5): each row is checked under ONE named hash convention (``hash_convention``: D5 and 07.A-R1 rows hash
the sorted unit ids, DIAG29 rows hash the unit-role assignment); ``unit_ids_sha256`` is recomputed from the listing (the
``recipe_id`` / ``cell`` attribute for RECIPE / CELL units, else the unit id), so a swapped recipe id is caught; a row with
units but no listing (DIAG29) is reported as NOT_VERIFIABLE_FROM_LISTING unless the caller passes the recomputed
assignment (``recomputed``), which is then checked like a listing.
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
HASH_CONVENTIONS = {"D5_BENCHMARK": "IDS_SORTED_NEWLINE", "07A_R1": "IDS_SORTED_NEWLINE", "DIAG29": "UNIT_ROLE_ASSIGNMENT"}
UNIT_ID_ATTRIBUTE = {"RECIPE": "recipe_id", "CELL": "cell"}   # other split units: the unit id itself


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


def hash_convention(row: Mapping[str, str]) -> str:
    """The one hash convention ``ids_sha256`` of this row is checked under."""
    return HASH_CONVENTIONS[row["evaluation"]]


def _attrs(text: str) -> dict[str, str]:
    out = {}
    for part in str(text or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v
    return out


def unit_ids_from_listing(row: Mapping[str, str], units: Sequence[Mapping[str, str]]) -> list[str] | None:
    """The ids ``unit_ids_sha256`` covers: the ``recipe_id`` / ``cell`` attribute for RECIPE / CELL units, else the unit id.
    None when a listed unit lacks the attribute (cannot be recomputed)."""
    key = UNIT_ID_ATTRIBUTE.get(row.get("split_unit", ""))
    if key is None:
        return [u["unit_id"] for u in units]
    vals = [_attrs(u.get("attributes", "")).get(key) for u in units]
    return None if any(v is None for v in vals) else [str(v) for v in vals]


def _check_row(r: Mapping[str, str], us: Sequence[Mapping[str, str]]) -> list[str]:
    out = []
    rid = r["registry_id"]
    if str(len(us)) != r["n_units"]:
        out.append(f"N_UNITS_MISMATCH: {rid} ({len(us)} listed, {r['n_units']} registered)")
    conv = hash_convention(r)
    got = (ids_sha256(u["unit_id"] for u in us) if conv == "IDS_SORTED_NEWLINE"
           else assignment_sha256((u["unit_id"], u["role"]) for u in us))
    if r["ids_sha256"] != got:
        out.append(f"IDS_SHA256_MISMATCH: {rid}")
    if r.get("unit_ids_sha256"):
        uids = unit_ids_from_listing(r, us)
        if uids is None:
            out.append(f"UNIT_IDS_NOT_RECOMPUTABLE: {rid}")
        elif r["unit_ids_sha256"] != ids_sha256(uids):
            out.append(f"UNIT_IDS_SHA256_MISMATCH: {rid}")
    return out


def verify_registry(registry_path: Path, units_path: Path | None = None, *,
                    recomputed: Mapping[str, Sequence[tuple[str, str]]] | None = None) -> list[str]:
    """Findings (empty = consistent and fully verified). Checks columns, required fields, statuses, unique ids and, for
    rows with a unit listing (or a ``recomputed`` list of (unit id, role) pairs), n_units, ids_sha256 under the row's one
    hash convention and unit_ids_sha256. A row with units and neither gives NOT_VERIFIABLE_FROM_LISTING (not silent)."""
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
        if r["evaluation"] not in EVALUATIONS:
            out.append(f"BAD_EVALUATION: {r['registry_id']}")
    by: dict[str, list[dict[str, str]]] = {}
    if units_path is not None:
        for u in read_csv(units_path):
            by.setdefault(u["registry_id"], []).append(u)
        out += [f"UNITS_WITHOUT_ROW: {k}" for k in sorted(set(by) - set(ids))]
    for rid, pairs in (recomputed or {}).items():
        if rid in by:
            out.append(f"RECOMPUTED_AND_LISTED: {rid}")
            continue
        by[rid] = [{"registry_id": rid, "unit_id": str(u), "role": str(role), "attributes": ""} for u, role in pairs]
    for r in rows:
        if r["evaluation"] not in EVALUATIONS:
            continue
        us = by.get(r["registry_id"])
        if us is None:
            if r["n_units"] not in ("", "0"):
                out.append(f"NOT_VERIFIABLE_FROM_LISTING: {r['registry_id']} ({r['n_units']} units, no listing)")
            elif r["ids_sha256"] != ids_sha256([]):
                out.append(f"IDS_SHA256_MISMATCH: {r['registry_id']}")
            continue
        out += _check_row(r, us)
    return out
