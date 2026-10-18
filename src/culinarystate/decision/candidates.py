"""C10 candidate action generator (SSOT §257B.10): state + goal + ontology → structured action candidates.

Three candidate families:
1. **Process candidates** (RECOMMEND): alternative cooking methods for an ingredient, ranked by
   ING_PROCESSED_BY confidence and evidence support (how many EVD rows exist for each).
2. **Substitution candidates**: ING_ALTERNATIVE_TO edges for ingredient substitutions.
3. **Sequence candidates** (RECOVER/COMPARE): PROC_FOLLOWED_BY edges suggesting what comes next.

Nothing is invented: all candidates come from the KGE or EVD ledgers. Unsupported candidates
are returned with support=0 so downstream can filter or rank.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

VERSION = "candidates@0.1"

CandidateType = Literal["PROCESS", "SUBSTITUTION", "SEQUENCE"]


@dataclass(frozen=True)
class Candidate:
    type: CandidateType
    id: str                         # PROC or ING id
    name: str
    confidence: float               # KGE edge confidence
    evidence_count: int             # EVD rows supporting this (process, ingredient)
    source_predicate: str           # which KGE predicate this came from
    reason: str                     # human-readable one-liner


@dataclass(frozen=True)
class CandidateSet:
    ingredient_id: str | None
    process_id: str | None
    target: str | None
    candidates: tuple[Candidate, ...]
    version: str = VERSION


def process_candidates(
    ingredient_id: str | None,
    processed_by: dict,             # ING id -> [PROC id, ...] sorted by confidence
    heat_procs: frozenset,
    proc_names: dict,               # PROC id -> canonical name
    kge_confidence: dict,           # (subject_id, predicate, object_id) -> confidence
    evd_support: dict,              # (ING id, PROC id) -> count of EVD rows
    max_k: int = 6,
) -> list[Candidate]:
    """Process candidates for RECOMMEND: heat methods the ingredient is processed by."""
    if not ingredient_id:
        return []
    procs = processed_by.get(ingredient_id, [])
    out = []
    for pid in procs:
        if pid not in heat_procs:
            continue
        conf = kge_confidence.get((ingredient_id, "ING_PROCESSED_BY", pid), 0.0)
        count = evd_support.get((ingredient_id, pid), 0)
        name = proc_names.get(pid, pid)
        out.append(Candidate(
            type="PROCESS", id=pid, name=name, confidence=conf,
            evidence_count=count, source_predicate="ING_PROCESSED_BY",
            reason=f"corpus: ingredient is {name}d in {int(conf * 100) if conf else '?'}% of recipes",
        ))
        if len(out) >= max_k:
            break
    # sort: evidence support first, then confidence
    out.sort(key=lambda c: (-c.evidence_count, -c.confidence))
    return out


def substitution_candidates(
    ingredient_id: str | None,
    alternatives: dict,             # ING id -> [(ING id, confidence), ...]
    ing_names: dict,                # ING id -> canonical name
    max_k: int = 4,
) -> list[Candidate]:
    """Substitution candidates: ING_ALTERNATIVE_TO edges."""
    if not ingredient_id:
        return []
    alts = alternatives.get(ingredient_id, [])
    out = []
    for alt_id, conf in alts:
        name = ing_names.get(alt_id, alt_id)
        out.append(Candidate(
            type="SUBSTITUTION", id=alt_id, name=name, confidence=conf,
            evidence_count=0, source_predicate="ING_ALTERNATIVE_TO",
            reason=f"corpus: used as substitute ({int(conf * 100)}% support)",
        ))
        if len(out) >= max_k:
            break
    return out


def sequence_candidates(
    process_id: str | None,
    followed_by: dict,              # PROC id -> [(PROC id, confidence), ...]
    proc_names: dict,
    max_k: int = 3,
) -> list[Candidate]:
    """Sequence candidates: PROC_FOLLOWED_BY edges (what typically comes next)."""
    if not process_id:
        return []
    nexts = followed_by.get(process_id, [])
    out = []
    for next_pid, conf in nexts:
        name = proc_names.get(next_pid, next_pid)
        out.append(Candidate(
            type="SEQUENCE", id=next_pid, name=name, confidence=conf,
            evidence_count=0, source_predicate="PROC_FOLLOWED_BY",
            reason=f"corpus: typically followed by {name}",
        ))
        if len(out) >= max_k:
            break
    return out


def generate_candidates(
    ingredient_id: str | None,
    process_id: str | None,
    target: str | None,
    processed_by: dict,
    heat_procs: frozenset,
    proc_names: dict,
    kge_confidence: dict,
    evd_support: dict,
    alternatives: dict,
    ing_names: dict,
    followed_by: dict,
) -> CandidateSet:
    """Full candidate generation: process + substitution + sequence."""
    procs = process_candidates(ingredient_id, processed_by, heat_procs, proc_names,
                               kge_confidence, evd_support)
    subs = substitution_candidates(ingredient_id, alternatives, ing_names)
    seqs = sequence_candidates(process_id, followed_by, proc_names)
    return CandidateSet(
        ingredient_id=ingredient_id,
        process_id=process_id,
        target=target,
        candidates=tuple(procs + subs + seqs),
    )
