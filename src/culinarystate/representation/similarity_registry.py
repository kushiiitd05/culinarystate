"""35e typed similarity registry v2: row schema, the nine notions and the registry lint, as pure functions.

Pre-registration draft 35.0 v1, sections 8.1, 8.2, 8.2b, 8.4 and Appendix B (UNSIGNED). Nothing here
reads or writes files and no registry row is defined here (sim_id scheme is H4, D35-12): callers pass
rows in memory. Tested on synthetic rows only.
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import asdict, dataclass, fields
from itertools import pairwise
from typing import Iterable, Mapping, Sequence

NOTIONS = (  # draft 8.2, pinned (R-16)
    "STRUCTURAL", "CHEMICAL", "COMPOSITIONAL", "SENSORY", "FUNCTIONAL",
    "NUTRITIONAL", "CULTURAL", "PROCEDURAL", "PROCESS-RESPONSE",
)
NOTION_ALIASES = {"PROCESS-CONDITIONED": "PROCESS-RESPONSE"}  # draft 8.2: the audit's name; rejected, not mapped
OUTSIDE_NINE = "OUTSIDE_NINE"  # chosen here (flagged): SIM-13 reaction-center similarity, RESEARCH_ONLY only (D35-11)
STATUSES = ("BASELINE", "HYPOTHESIS", "PROMOTED", "RESEARCH_ONLY", "NEED_DATA", "UNSUPPORTED")  # draft 8.1

CORE_FIELDS = (  # draft 8.1; every value non-blank, UNKNOWN allowed
    "sim_id", "notion", "level", "formula", "aggregator", "null_model", "eval_set", "split_family",
    "valid_domain", "evidence_class_required", "licence_scope", "status",
)
OPTIONAL_FIELDS = (  # draft 8.1 "proposed" fields, plus decision_ref (added here, flagged) for the 8.4 PROMOTED rule
    "coverage_fields", "fp_definition_ref", "ssot_sim_ref", "rung", "decision_ref",
)

# Draft 8.2b: a split family may be shared only where the leakage unit is identical, and every share is listed.
SHARED_SPLIT_FAMILIES = {
    "S-rec-grp": frozenset({"COMPOSITIONAL", "PROCEDURAL", "FUNCTIONAL", "CULTURAL"}),  # SPLITGRP-REC- group
    "S-mol-cc": frozenset({"STRUCTURAL", "SENSORY"}),  # S-mol-cc component
    "S-ing-clu": frozenset({"CHEMICAL", "STRUCTURAL", "NUTRITIONAL"}),  # ingredient cluster
    "S-ing-cold": frozenset({"CHEMICAL", "STRUCTURAL", "NUTRITIONAL"}),  # cold-start entity
    "S-cui-src": frozenset({"CULTURAL"}),  # source (cuisine level only)
    "S-cui-hold": frozenset({"CULTURAL"}),  # cuisine (cuisine level only)
    "study-disjoint": frozenset({"PROCESS-RESPONSE"}),  # study
}

# Conventions chosen here (flagged for sign-off): ";" separates several values in eval_set / split_family;
# "assoc:<target>" marks a cross-notion association test (8.2b), never a notion's own target;
# "none" and "UNKNOWN" are not targets or families.
LIST_SEP = ";"
ASSOC_PREFIX = "assoc:"
NOT_A_VALUE = frozenset({"", "none", "unknown"})
SIM_TOKENS = frozenset({"sim", "sims", "similarity", "similarities", "score", "scores"})  # draft 8.4
FUSION_TOKENS = frozenset({"fusion", "fused", "fuse", "fusing"})
BLANK_DECISION = frozenset({"", "unknown", "none", "tbd"})
SIM06 = re.compile(r"\bSIM-0*6(?!\d)")


class RegistryError(ValueError):
    """A registry row or output column breaks the 35e schema or lint."""


@dataclass(frozen=True)
class SimRow:
    sim_id: str
    notion: str
    level: str
    formula: str
    aggregator: str
    null_model: str
    eval_set: str
    split_family: str
    valid_domain: str
    evidence_class_required: str
    licence_scope: str
    status: str
    coverage_fields: str = ""
    fp_definition_ref: str = ""
    ssot_sim_ref: str = ""
    rung: str = ""
    decision_ref: str = ""

    @classmethod
    def from_mapping(cls, m: Mapping[str, str]) -> SimRow:
        unknown = sorted(set(m) - set(CORE_FIELDS) - set(OPTIONAL_FIELDS))
        if unknown:
            raise RegistryError(f"unknown column(s): {', '.join(unknown)}")
        missing = [f for f in CORE_FIELDS if f not in m]
        if missing:
            raise RegistryError(f"missing core field(s): {', '.join(missing)}")
        vals = {k: ("" if v is None else str(v).strip()) for k, v in m.items()}
        for f in CORE_FIELDS:
            if not vals[f]:
                raise RegistryError(f"blank core field '{f}' in row {vals['sim_id']!r} (UNKNOWN is allowed, blank is not)")
        _check_notion(vals["notion"], vals["status"])
        if vals["status"] not in STATUSES:
            raise RegistryError(f"status {vals['status']!r} not in {STATUSES}")
        return cls(**vals)


def _check_notion(notion: str, status: str) -> None:
    if notion in NOTIONS:
        return
    if notion == OUTSIDE_NINE:
        if status != "RESEARCH_ONLY":
            raise RegistryError(f"{OUTSIDE_NINE} rows must have status RESEARCH_ONLY (D35-11), got {status!r}")
        return
    if notion.upper() in NOTION_ALIASES:
        raise RegistryError(f"notion {notion!r} is not canonical; use {NOTION_ALIASES[notion.upper()]!r} (draft 8.2)")
    raise RegistryError(f"notion {notion!r} is not one of the nine notions {NOTIONS} or {OUTSIDE_NINE}")


def _tokens(text: str) -> list:
    """Lower-case word tokens; camelCase and any non-alphanumeric character split words."""
    return [t for t in re.split(r"[^a-z0-9]+", re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text).lower()) if t]


def _notions_in(tokens: Sequence[str]) -> set:
    found = {n for n in NOTIONS if "-" not in n and n.lower() in tokens}
    if any(a == "process" and b == "response" for a, b in pairwise(tokens)) or "processresponse" in tokens:
        found.add("PROCESS-RESPONSE")
    return found


def _items(value: str) -> list:
    return [v.strip() for v in value.split(LIST_SEP) if v.strip().lower() not in NOT_A_VALUE]


def own_targets(r: SimRow) -> list:
    """The row's own evaluation targets (association tests, none and UNKNOWN excluded)."""
    return [t for t in _items(r.eval_set) if not t.lower().startswith(ASSOC_PREFIX)]


def lint_registry(rows: Iterable[SimRow]) -> list:
    """All 35e lint problems for a set of rows (empty list = clean). Never fixes anything."""
    rows = list(rows)
    problems = []
    seen = set()
    for r in rows:
        if r.sim_id in seen:
            problems.append(f"duplicate sim_id {r.sim_id!r}")
        seen.add(r.sim_id)
        other = _notions_in(_tokens(r.formula)) - {r.notion}
        if other:
            problems.append(f"{r.sim_id}: formula mixes notions ({r.notion} with {', '.join(sorted(other))}; draft 8.4)")
        if FUSION_TOKENS & set(_tokens(r.formula) + _tokens(r.aggregator)):
            problems.append(f"{r.sim_id}: fusion is a task-conditioned reranker, never a registry similarity (SSOT 246.2)")
        if r.status == "PROMOTED" and (r.decision_ref.lower() in BLANK_DECISION or r.decision_ref.startswith("<")):
            problems.append(f"{r.sim_id}: status PROMOTED without a decision-record reference (draft 8.4)")
        fp = _tokens(r.fp_definition_ref)
        open_babel = "openbabel" in fp or "obabel" in fp or any(a == "open" and b == "babel" for a, b in pairwise(fp))
        if open_babel and SIM06.search(r.ssot_sim_ref):
            problems.append(f"{r.sim_id}: Open Babel ECFP may not be labelled SIM-06 (D35-3)")

    targets: dict = {}
    for r in rows:
        for t in own_targets(r):
            targets.setdefault(t.casefold(), (t, set()))[1].add(r.notion)
    for shown, notions in targets.values():
        if len(notions) > 1:
            problems.append(f"evaluation target {shown!r} listed as own by several notions: {', '.join(sorted(notions))} (draft 8.2b)")

    families: dict = {}
    for r in rows:
        for fam in _items(r.split_family):
            families.setdefault(fam, set()).add(r.notion)
    for fam, notions in families.items():
        allowed = SHARED_SPLIT_FAMILIES.get(fam)
        if allowed is not None:
            bad = notions - allowed
            if bad:
                problems.append(f"split family {fam!r} used by {', '.join(sorted(bad))}; the 8.2b table allows only {', '.join(sorted(allowed))}")
        elif len(notions) > 1:
            problems.append(f"split family {fam!r} shared by {', '.join(sorted(notions))} but not listed in the 8.2b table")
    return problems


def lint_columns(columns: Iterable[str], exempt: Iterable[str] = ()) -> list:
    """Draft 8.4: a column named like similarity / score / sim needs exactly one notion qualifier.

    Two or more notions in one such column = a fused scalar (draft 8.3). `exempt` lists columns the
    caller deliberately excludes (for example a metric table's f1_score); nothing is exempt by default.
    """
    exempt = set(exempt)
    problems = []
    for col in columns:
        if col in exempt:
            continue
        tok = _tokens(col)
        if not SIM_TOKENS & set(tok):
            continue
        found = _notions_in(tok)
        if not found:
            problems.append(f"column {col!r}: names a similarity/score without a notion qualifier (draft 8.4)")
        elif len(found) > 1:
            problems.append(f"column {col!r}: more than one notion in one similarity/score column ({', '.join(sorted(found))}; fused scalar)")
    return problems


def assert_lint_clean(rows: Iterable[SimRow] | None = None, columns: Iterable[str] | None = None,
                      exempt: Iterable[str] = ()) -> None:
    """Raise RegistryError listing every problem; return None when clean."""
    problems = (lint_registry(rows) if rows is not None else []) + (lint_columns(columns, exempt) if columns is not None else [])
    if problems:
        raise RegistryError("35e lint failed:\n" + "\n".join(problems))


def parse_registry_csv(text: str) -> list:
    """Rows from CSV text (the caller reads the file). Header must hold every core column and nothing unknown."""
    reader = csv.DictReader(io.StringIO(text))
    header = reader.fieldnames or []
    missing = [f for f in CORE_FIELDS if f not in header]
    if missing:
        raise RegistryError(f"missing core column(s): {', '.join(missing)}")
    unknown = [f for f in header if f not in CORE_FIELDS and f not in OPTIONAL_FIELDS]
    if unknown:
        raise RegistryError(f"unknown column(s): {', '.join(unknown)}")
    out = []
    for rec in reader:
        if None in rec:
            raise RegistryError(f"row {reader.line_num} has more values than the header")
        out.append(SimRow.from_mapping(rec))
    return out


def to_csv(rows: Iterable[SimRow]) -> str:
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=[f.name for f in fields(SimRow)], lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(asdict(r))
    return out.getvalue()


def notion_coverage(rows: Iterable[SimRow]) -> dict:
    """Descriptive: per notion, how many rows, which statuses, own targets and null models. No pass/fail."""
    cov = {n: {"rows": 0, "statuses": set(), "own_targets": set(), "null_models": set()} for n in NOTIONS}
    for r in rows:
        c = cov.setdefault(r.notion, {"rows": 0, "statuses": set(), "own_targets": set(), "null_models": set()})
        c["rows"] += 1
        c["statuses"].add(r.status)
        c["own_targets"].update(own_targets(r))
        c["null_models"].add(r.null_model)
    return cov


def unlisted_notions(rows: Iterable[SimRow]) -> tuple:
    """Notions with no row at all (draft 8.3 wants every notion explicit, even as UNSUPPORTED/NEED_DATA)."""
    present = {r.notion for r in rows}
    return tuple(n for n in NOTIONS if n not in present)
