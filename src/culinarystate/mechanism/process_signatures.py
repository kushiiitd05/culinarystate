"""Step 22a process-level signatures over PROC x modifiers x MECH (S158, DRAFT_PENDING_21b_H4).

Status DRAFT_PENDING_21b_H4: Step 21b (reviewed MECH seed entries, PROC crosswalk) is NOT STARTED and the
EFFSIG contract is not H4-approved. This module is the data structure, validator and builder only. It holds no
rule: every (process, modifiers) -> mechanism link is a caller-supplied ``SignatureRule`` authored and reviewed
by humans, and no rule is shipped here. The shared case set (22c) must be sealed before rules are coded (spine
human gate); see ``case_seal``.

Contract (Plan Step 22 card; R-15, R-20, R-05)
- Trigger: a PROC family node (``FAM:*``) or PROC leaf of registry/processes/process_hierarchy_v1_DRAFT.csv,
  optionally its descendants, plus modifier predicates over INTENSITY / GEOMETRY / GRANULARITY / MEDIUM (SSOT
  257A.3) and optional heat-transfer-mode ids. ENDPOINT is refused: an endpoint cue is an observed outcome /
  stop criterion, never a trigger or condition input (SSOT 199.8). Alias and endpoint rows are not triggers.
- Output per (rule, mechanism): the MECH read API projections, unchanged (required_state_inputs,
  required_condition_axes including modifier gates, candidate_effects with sign sets only), Step-18
  deterministic change refs (``ALLOC_KINDS`` only; referenced, never recomputed), requires_gate_eval = true,
  provenance_class = MODEL_ESTIMATED, label CANDIDATE, is_evidence = false. Never a magnitude, rate or extent.
- Recall-oriented: an entry that Step 23 may not consume (``consumable_for_applicability`` false) still yields
  a signature, carrying ``mech_consumable = false`` and the reasons; Step 23 refuses it (UNKNOWN).
- No COND value is read (R-05 soft): signatures name condition axes and locations only.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from culinarystate.mechanism import mech_contract as MC
from culinarystate.state_graph.event_log import ALLOC_KINDS

STATUS = "DRAFT_PENDING_21b_H4"
CONTRACT_VERSION = "step22a-procsig-0.1.0-draft"
MODIFIER_AXES = ("INTENSITY", "GEOMETRY", "GRANULARITY", "MEDIUM")
REFUSED_MODIFIER_AXES = ("ENDPOINT",)
PREDICATE_OPERATORS = ("IS", "IS_NOT", "IN", "NOT_IN")
DETERMINISTIC_CHANGE_TYPES = tuple(ALLOC_KINDS)
PROVENANCE_CLASS = "MODEL_ESTIMATED"
CANDIDATE_LABEL = "CANDIDATE"
MATCHED, MODIFIER_UNKNOWN = "MATCHED", "MODIFIER_UNKNOWN"
MAGNITUDE_KEYS = frozenset({"value", "magnitude", "rate", "rate_constant", "extent", "amount", "k", "ea",
                            "half_life", "d_value", "z_value", "q10", "estimate", "fraction", "percent"})

_ROOT = Path(__file__).resolve().parents[3]
HIERARCHY_PATH = _ROOT / "registry" / "processes" / "process_hierarchy_v1_DRAFT.csv"
HEAT_TRANSFER_PATH = _ROOT / "registry" / "heat_transfer_mode_registry_v1.csv"
_KEY = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")
_TOKEN = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


class SignatureError(ValueError):
    """Structural contract violation (programming or input-shape error, not a data finding)."""


# ----------------------------------------------------------------------------- PROC hierarchy
@dataclass(frozen=True)
class ProcessNode:
    node_id: str
    name: str
    parent_id: str | None
    level: int | None
    endpoint_flag: bool


def _read_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


def read_hierarchy_rows(path: Path = HIERARCHY_PATH) -> list[dict[str, str]]:
    return _read_rows(path)


def read_heat_transfer_mode_ids(path: Path = HEAT_TRANSFER_PATH) -> frozenset[str]:
    return frozenset(r["heat_transfer_mode_id"] for r in _read_rows(path))


def hierarchy_problems(rows: Sequence[Mapping[str, str]]) -> list[str]:
    """Duplicate ids, unresolved parents, cycles and endpoint rows placed inside the hierarchy."""
    out: list[str] = []
    ids = [r["id"] for r in rows]
    dup = sorted(k for k, n in Counter(ids).items() if n > 1)
    if dup:
        out.append(f"duplicate node id: {dup}")
    parent = {r["id"]: (r["proposed_parent_id"] or None) for r in rows}
    for r in rows:
        p = r["proposed_parent_id"] or None
        if p is not None and p not in parent:
            out.append(f"{r['id']}: parent {p} not in hierarchy")
        if r["endpoint_flag"].strip().lower() == "true" and p is not None:
            out.append(f"{r['id']}: endpoint row has a parent (endpoints sit outside the hierarchy)")
    for start in parent:
        seen, cur = set(), start
        while cur is not None and cur in parent:
            if cur in seen:
                out.append(f"{start}: parent cycle")
                break
            seen.add(cur)
            cur = parent[cur]
    return out


class ProcessHierarchy:
    """Read-only view of the PROC hierarchy draft (family -> leaf -> alias; endpoints outside)."""

    def __init__(self, nodes: Mapping[str, ProcessNode]) -> None:
        self._nodes = dict(nodes)
        kids: dict[str, list[str]] = {}
        for n in self._nodes.values():
            if n.parent_id is not None:
                kids.setdefault(n.parent_id, []).append(n.node_id)
        self._children = {k: tuple(sorted(v)) for k, v in kids.items()}

    @property
    def node_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._nodes))

    def contains(self, node_id: str) -> bool:
        return node_id in self._nodes

    def node(self, node_id: str) -> ProcessNode:
        return self._nodes[node_id]

    def is_endpoint(self, node_id: str) -> bool:
        return node_id in self._nodes and self._nodes[node_id].endpoint_flag

    def ancestors(self, node_id: str) -> tuple[str, ...]:
        out, cur = [], self._nodes[node_id].parent_id
        while cur is not None:
            out.append(cur)
            cur = self._nodes[cur].parent_id
        return tuple(out)

    def descendants(self, node_id: str) -> tuple[str, ...]:
        out, stack = [], [node_id]
        while stack:
            cur = stack.pop()
            out.append(cur)
            stack.extend(self._children.get(cur, ()))
        return tuple(sorted(out))

    def process_ids_under(self, node_id: str, *, include_descendants: bool = True) -> tuple[str, ...]:
        """PROC-* ids at or below node_id (family and alias nodes are not event process ids)."""
        ids = self.descendants(node_id) if include_descendants else (node_id,)
        return tuple(i for i in ids if i.startswith("PROC-") and not self.is_endpoint(i))


def hierarchy_from_rows(rows: Sequence[Mapping[str, str]]) -> ProcessHierarchy:
    probs = hierarchy_problems(rows)
    if probs:
        raise SignatureError("; ".join(probs))
    return ProcessHierarchy({r["id"]: ProcessNode(r["id"], r["name"], r["proposed_parent_id"] or None,
                                                  int(r["level"]) if r["level"] else None,
                                                  r["endpoint_flag"].strip().lower() == "true") for r in rows})


def read_process_hierarchy(path: Path = HIERARCHY_PATH) -> ProcessHierarchy:
    return hierarchy_from_rows(read_hierarchy_rows(path))


# ----------------------------------------------------------------------------- rules and signatures
@dataclass(frozen=True)
class ModifierPredicate:
    axis: str
    operator: str
    values: tuple[str, ...]

    def to_canonical(self) -> dict[str, Any]:
        return {"axis": self.axis, "operator": self.operator, "values": list(self.values)}

    def holds(self, value: str) -> bool:
        inside = value in self.values
        return inside if self.operator in ("IS", "IN") else not inside


def predicate_problems(p: Mapping[str, Any] | ModifierPredicate) -> list[str]:
    d = p.to_canonical() if isinstance(p, ModifierPredicate) else dict(p)
    axis, op, vals = d.get("axis"), d.get("operator"), list(d.get("values") or [])
    out: list[str] = []
    if axis in REFUSED_MODIFIER_AXES:
        out.append(f"modifier axis {axis} refused: an endpoint cue is never a trigger or condition input")
    elif axis not in MODIFIER_AXES:
        out.append(f"unknown modifier axis {axis}")
    if op not in PREDICATE_OPERATORS:
        out.append(f"unknown predicate operator {op}")
    elif op in ("IS", "IS_NOT") and len(vals) != 1 or op in ("IN", "NOT_IN") and len(vals) < 2:
        out.append(f"{op} needs {'one value' if op in ('IS', 'IS_NOT') else 'two or more values'}")
    if len(set(vals)) != len(vals):
        out.append("duplicate predicate values")
    for v in vals:
        if not isinstance(v, str) or not _TOKEN.match(v) or v.upper() == "UNKNOWN":
            out.append(f"predicate value {v!r} is not an upper-case code (UNKNOWN is never a value)")
    return out


@dataclass(frozen=True)
class SignatureRule:
    """A human-authored trigger -> mechanism-key rule. This module ships none."""

    rule_key: str
    process_ref: str
    include_descendants: bool
    modifier_predicates: tuple[ModifierPredicate, ...]
    mechanism_keys: tuple[str, ...]
    heat_transfer_mode_ids: tuple[str, ...]
    deterministic_change_refs: tuple[str, ...]
    rationale_raw: str
    authored_by: str


@dataclass(frozen=True)
class ProcessSignature:
    signature_key: str
    rule_key: str
    process_ref: str
    include_descendants: bool
    process_ids_covered: tuple[str, ...]
    modifier_predicates: tuple[ModifierPredicate, ...]
    heat_transfer_mode_ids: tuple[str, ...]
    mechanism_key: str
    mechanism_id: str
    mech_review_status: str
    mech_consumable: bool
    mech_refusal_reasons: tuple[str, ...]
    required_state_inputs: tuple[MC.StateInput, ...]
    required_condition_axes: tuple[MC.AxisRequirement, ...]
    candidate_effects: tuple[MC.CandidateEffect, ...]
    deterministic_change_refs: tuple[str, ...]
    rationale_raw: str
    authored_by: str
    requires_gate_eval: bool = True
    provenance_class: str = PROVENANCE_CLASS
    label: str = CANDIDATE_LABEL
    is_evidence: bool = False
    status: str = STATUS
    contract_version: str = CONTRACT_VERSION

    def to_canonical(self) -> dict[str, Any]:
        return {
            "signature_key": self.signature_key, "status": self.status, "contract_version": self.contract_version,
            "rule_key": self.rule_key,
            "trigger": {"process_ref": self.process_ref, "include_descendants": self.include_descendants,
                        "process_ids_covered": list(self.process_ids_covered),
                        "modifier_predicates": [p.to_canonical() for p in self.modifier_predicates],
                        "heat_transfer_mode_ids": list(self.heat_transfer_mode_ids)},
            "mechanism": {"mechanism_key": self.mechanism_key, "mechanism_id": self.mechanism_id,
                          "review_status": self.mech_review_status, "consumable": self.mech_consumable,
                          "refusal_reasons": list(self.mech_refusal_reasons)},
            "required_state_inputs": [_dc(x) for x in self.required_state_inputs],
            "required_condition_axes": [_dc(x) for x in self.required_condition_axes],
            "candidate_effects": [_dc(x) for x in self.candidate_effects],
            "deterministic_change_refs": list(self.deterministic_change_refs),
            "requires_gate_eval": self.requires_gate_eval, "provenance_class": self.provenance_class,
            "label": self.label, "is_evidence": self.is_evidence,
            "rationale_raw": self.rationale_raw, "authored_by": self.authored_by,
        }

    def sha256(self) -> str:
        return hashlib.sha256(_canonical_bytes(self.to_canonical())).hexdigest()


@dataclass(frozen=True)
class SignatureBuild:
    signatures: tuple[ProcessSignature, ...]
    problems: tuple[str, ...]


def _dc(x: Any) -> dict[str, Any]:
    return {k: (list(v) if isinstance(v, tuple) else v) for k, v in vars(x).items()}


def _canonical_bytes(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _entry_problems(entries: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    out: list[str] = []
    dup = sorted(k for k, n in Counter(e.get("mechanism_key") for e in entries).items() if n > 1)
    if dup:
        out.append(f"duplicate mechanism_key in MECH set: {dup}")
    by: dict[str, Mapping[str, Any]] = {}
    for e in entries:
        errs = MC.schema_errors(e)
        if errs:
            out.append(f"{e.get('mechanism_key')}: MECH v1.1 schema errors ({len(errs)}): {errs[0]}")
        else:
            by[e["mechanism_key"]] = e
    return by, out


def rule_problems(r: SignatureRule, by_key: Mapping[str, Mapping[str, Any]], hierarchy: ProcessHierarchy,
                  heat_transfer_mode_ids: frozenset[str]) -> list[str]:
    k = r.rule_key
    out: list[str] = []
    if not isinstance(k, str) or not _KEY.match(k):
        out.append(f"{k!r}: rule_key must be an upper-case key")
    ref = r.process_ref
    if not hierarchy.contains(ref):
        out.append(f"{k}: process_ref {ref} not in the PROC hierarchy")
    elif hierarchy.is_endpoint(ref):
        out.append(f"{k}: process_ref {ref} is an endpoint (outcome, never a trigger)")
    elif not (ref.startswith("FAM:") or ref.startswith("PROC-")):
        out.append(f"{k}: process_ref {ref} is not a family or PROC node (aliases are surface forms)")
    elif not hierarchy.process_ids_under(ref, include_descendants=r.include_descendants):
        out.append(f"{k}: process_ref {ref} covers no PROC id")
    if not r.mechanism_keys:
        out.append(f"{k}: no mechanism key")
    if len(set(r.mechanism_keys)) != len(r.mechanism_keys):
        out.append(f"{k}: duplicate mechanism key")
    out += [f"{k}: mechanism key {m} not in the MECH set (a rule never invents a mechanism)"
            for m in r.mechanism_keys if m not in by_key]
    axes = [p.axis for p in r.modifier_predicates]
    if len(set(axes)) != len(axes):
        out.append(f"{k}: one predicate per modifier axis")
    for p in r.modifier_predicates:
        if not isinstance(p, ModifierPredicate):
            out.append(f"{k}: modifier predicates must be ModifierPredicate instances")
            continue
        out += [f"{k}: {x}" for x in predicate_problems(p)]
    out += [f"{k}: heat-transfer-mode id {h} not in the registry" for h in r.heat_transfer_mode_ids
            if h not in heat_transfer_mode_ids]
    out += [f"{k}: deterministic change ref {d} is not a Step-18 operator type {DETERMINISTIC_CHANGE_TYPES}"
            for d in r.deterministic_change_refs if d not in DETERMINISTIC_CHANGE_TYPES]
    if not (r.rationale_raw or "").strip() or not (r.authored_by or "").strip():
        out.append(f"{k}: rationale_raw and authored_by are required")
    return out


def _signature(r: SignatureRule, e: Mapping[str, Any], hierarchy: ProcessHierarchy) -> ProcessSignature:
    ok, why = MC.consumable_for_applicability(e)
    return ProcessSignature(
        signature_key=f"{r.rule_key}:{e['mechanism_key']}", rule_key=r.rule_key, process_ref=r.process_ref,
        include_descendants=r.include_descendants,
        process_ids_covered=hierarchy.process_ids_under(r.process_ref, include_descendants=r.include_descendants),
        modifier_predicates=tuple(sorted(r.modifier_predicates, key=lambda p: p.axis)),
        heat_transfer_mode_ids=tuple(sorted(r.heat_transfer_mode_ids)), mechanism_key=e["mechanism_key"],
        mechanism_id=e["id"], mech_review_status=e["review_status"], mech_consumable=ok, mech_refusal_reasons=why,
        required_state_inputs=MC.required_state_inputs(e), required_condition_axes=MC.required_condition_axes(e),
        candidate_effects=MC.candidate_effects(e),
        deterministic_change_refs=tuple(sorted(r.deterministic_change_refs)), rationale_raw=r.rationale_raw,
        authored_by=r.authored_by)


def build_signatures(rules: Iterable[SignatureRule], entries: Sequence[Mapping[str, Any]],
                     hierarchy: ProcessHierarchy, *,
                     heat_transfer_mode_ids: frozenset[str] | None = None) -> SignatureBuild:
    """One ProcessSignature per (valid rule, mechanism key). A rule with any problem yields no signature."""
    rules = list(rules)
    ht = read_heat_transfer_mode_ids() if heat_transfer_mode_ids is None else heat_transfer_mode_ids
    by_key, probs = _entry_problems(entries)
    dup = sorted(k for k, n in Counter(r.rule_key for r in rules).items() if n > 1)
    if dup:
        probs.append(f"duplicate rule_key: {dup}")
    sigs: list[ProcessSignature] = []
    for r in rules:
        if not isinstance(r, SignatureRule):
            raise SignatureError("rules must be SignatureRule instances")
        rp = rule_problems(r, by_key, hierarchy, ht)
        probs += rp
        if not rp and r.rule_key not in dup:
            sigs += [_signature(r, by_key[m], hierarchy) for m in r.mechanism_keys]
    return SignatureBuild(tuple(sorted(sigs, key=lambda s: s.signature_key)), tuple(probs))


# ----------------------------------------------------------------------------- validator over canonical records
def _magnitude_keys(x: Any) -> int:
    if isinstance(x, dict):
        return sum(1 for k in x if str(k).lower() in MAGNITUDE_KEYS) + sum(_magnitude_keys(v) for v in x.values())
    if isinstance(x, list):
        return sum(_magnitude_keys(v) for v in x)
    return 0


def signature_problems(sig: Mapping[str, Any], entries: Sequence[Mapping[str, Any]],
                       hierarchy: ProcessHierarchy) -> list[str]:
    """Check a canonical signature against the contract and recompute every MECH projection from the entry."""
    out: list[str] = []
    k = sig.get("signature_key")
    fixed = {"status": STATUS, "contract_version": CONTRACT_VERSION, "requires_gate_eval": True,
             "provenance_class": PROVENANCE_CLASS, "label": CANDIDATE_LABEL, "is_evidence": False}
    out += [f"{k}: {f} must be {v!r}" for f, v in fixed.items() if sig.get(f) != v]
    if _magnitude_keys(dict(sig)):
        out.append(f"{k}: a magnitude-like key is present (signs only)")
    trig, m = sig.get("trigger") or {}, sig.get("mechanism") or {}
    for p in trig.get("modifier_predicates", []):
        out += [f"{k}: {x}" for x in predicate_problems(p)]
    by = {e["mechanism_key"]: e for e in entries}
    e = by.get(m.get("mechanism_key"))
    if e is None:
        return out + [f"{k}: mechanism key {m.get('mechanism_key')} not in the MECH set"]
    ref = trig.get("process_ref", "")
    if not hierarchy.contains(ref) or hierarchy.is_endpoint(ref):
        return out + [f"{k}: process_ref {ref} is not a hierarchy trigger"]
    want = _signature(SignatureRule(sig.get("rule_key", ""), ref, bool(trig.get("include_descendants")), (),
                                    (e["mechanism_key"],), (), (), "", ""), e, hierarchy).to_canonical()
    if trig.get("process_ids_covered") != want["trigger"]["process_ids_covered"]:
        out.append(f"{k}: process_ids_covered differs from the hierarchy")
    for f in ("mechanism_id", "review_status", "consumable", "refusal_reasons"):
        if m.get(f) != want["mechanism"][f]:
            out.append(f"{k}: mechanism.{f} differs from the MECH entry")
    for f in ("required_state_inputs", "required_condition_axes", "candidate_effects"):
        if sig.get(f) != want[f]:
            out.append(f"{k}: {f} differs from the MECH read API (nothing may be dropped, added or widened)")
    if sig.get("signature_key") != f"{sig.get('rule_key')}:{e['mechanism_key']}":
        out.append(f"{k}: signature_key must be rule_key:mechanism_key")
    out += [f"{k}: deterministic change ref {d} is not a Step-18 operator type"
            for d in sig.get("deterministic_change_refs", []) if d not in DETERMINISTIC_CHANGE_TYPES]
    return out


def firewall_counters(signatures: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    """Plan G22.4 counters over canonical signatures (all must be 0)."""
    c = {"magnitudes_emitted": 0, "is_evidence_true": 0, "endpoint_as_condition": 0, "gate_eval_skipped": 0}
    for s in signatures:
        c["magnitudes_emitted"] += _magnitude_keys(dict(s))
        c["is_evidence_true"] += s.get("is_evidence") is not False
        c["endpoint_as_condition"] += sum(p.get("axis") in REFUSED_MODIFIER_AXES
                                          for p in (s.get("trigger") or {}).get("modifier_predicates", []))
        c["gate_eval_skipped"] += s.get("requires_gate_eval") is not True
    return c


# ----------------------------------------------------------------------------- matching an event
@dataclass(frozen=True)
class SignatureMatch:
    signature: ProcessSignature
    modifier_status: str                  # MATCHED or MODIFIER_UNKNOWN
    missing_modifiers: tuple[str, ...]


def match_signatures(signatures: Iterable[ProcessSignature], process_id: str,
                     modifiers: Mapping[str, str | None]) -> tuple[SignatureMatch, ...]:
    """Signatures whose trigger covers process_id. A predicate on a missing modifier keeps the signature as
    MODIFIER_UNKNOWN (recall-oriented); a predicate that fails on a stated modifier excludes it."""
    refused = sorted(set(modifiers) & set(REFUSED_MODIFIER_AXES))
    if refused:
        raise SignatureError(f"{refused}: an ENDPOINT cue is an observed outcome, never a modifier input")
    unknown = sorted(set(modifiers) - set(MODIFIER_AXES))
    if unknown:
        raise SignatureError(f"unknown modifier axes {unknown}")
    out: list[SignatureMatch] = []
    for s in signatures:
        if process_id not in s.process_ids_covered:
            continue
        missing = tuple(p.axis for p in s.modifier_predicates if modifiers.get(p.axis) is None)
        if any(not p.holds(str(modifiers[p.axis])) for p in s.modifier_predicates if p.axis not in missing):
            continue
        out.append(SignatureMatch(s, MODIFIER_UNKNOWN if missing else MATCHED, missing))
    return tuple(sorted(out, key=lambda x: x.signature.signature_key))
