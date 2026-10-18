"""End-to-end question -> slots -> evidence packets -> feasibility -> decision (DEL-5 rule baseline, B5 rung).

Slots: ingredient = first lexicon mention (LineLinker); processes = action verbs in the question, in order
(step_processes, inflection-aware); target = first nutrient phrase (cross_source NUTRIENT patterns).
RECOMMEND questions without a process get candidates from the corpus (SSOT §243.2): the ingredient's
ING_PROCESSED_BY edges restricted to heat processes, in edge-confidence order. Nothing is invented: unlinked
slots stay None and the policy asks or abstains.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.retriever import EvidenceRetriever
from culinarystate.state_graph.rule_compiler import step_processes
from culinarystate.transition.cross_source import NUTRIENT
from culinarystate.vocab.line_link import LineLinker

from .feasibility import Action, Constraints, Requirements, check
from .policy import decide
from .relevance import intent

HEAT_FAMILIES = ("WET_HEAT", "DRY_HEAT", "FAT_HEAT")          # cooking-method candidates (+ microwave below)
EXTRA_METHODS = ("microwave",)                                   # in HEAT_GENERAL with cook/heat/melt
MAX_CANDIDATES = 4
# verbs whose question reading is not a cooking action: "keep vitamin C" (-> reserve), "sauce split" (state, -> divide),
# modal "can" (-> canning), generic "cook"
QUESTION_NOT_PROCESS = {"cook", "reserve", "divide", "can", "serve", "set", "rest"}


@dataclass(frozen=True)
class Lexicon:
    linker: LineLinker
    proc_ids: dict                  # canonical process name -> PROC id
    parents: dict                   # ING id -> tuple of parent ING ids
    processed_by: dict              # ING id -> PROC ids by ING_PROCESSED_BY confidence
    heat_procs: frozenset


@dataclass(frozen=True)
class Slots:
    ingredient_id: str | None
    ingredient_name: str | None
    parents: tuple
    processes: tuple                # ((name, PROC id), ...)
    target: str | None
    candidates: tuple               # PROC ids generated for RECOMMEND/RECOVER


def parse_query(q: str, lex: Lexicon) -> Slots:
    ments = lex.linker.mentions(q)
    ing = ments[0] if ments else None
    seen, procs = set(), []
    for _, name in step_processes(q):
        pid = lex.proc_ids.get(name)
        if pid and pid not in seen and name not in QUESTION_NOT_PROCESS:
            seen.add(pid)
            procs.append((name, pid))
    tm = next((m for pat, _ in NUTRIENT if (m := re.search(pat, q.lower()))), None)
    cands = ()
    if not procs and ing and intent(q) == "RECOMMEND":
        cands = tuple(p for p in lex.processed_by.get(ing, ()) if p in lex.heat_procs)[:MAX_CANDIDATES]
    name = next((n for n, i in lex.linker.names.items() if i == ing), None) if ing else None
    return Slots(ing, name, tuple(lex.parents.get(ing, ())), tuple(procs), tm.group(0) if tm else None, cands)


def answer(q: str, lex: Lexicon, retriever: EvidenceRetriever, req: Requirements, proc_family: dict,
           constraints: Constraints | None = None, k: int = 10) -> dict:
    s = parse_query(q, lex)
    name_of = {v: n for n, v in lex.proc_ids.items()}
    options = [(n, p) for n, p in s.processes] or [(name_of.get(p, p), p) for p in s.candidates]
    if intent(q) not in ("COMPARE", "RECOMMEND", "RECOVER"):
        options = options[:1]

    def query(pid: str) -> Query:
        return Query(ingredient_id=s.ingredient_id, ingredient_name=s.ingredient_name,
                     ingredient_parents=frozenset(s.parents), process_id=pid,
                     process_family=proc_family.get(pid), target=s.target)

    packets = {n: retriever.packet(q, query(p), k) for n, p in options}
    feas = {n: check(Action(p, (s.ingredient_id,) if s.ingredient_id else ()), constraints or Constraints(), req)
            for n, p in options}
    slots = {"ingredient": s.ingredient_id, "process": options[0][1] if options else None}
    return {"slots": s, "decision": decide(q, packets, slots, feasibility=feas), "packets": packets, "feasibility": feas}


def load_lexicon(store) -> tuple[Lexicon, dict]:
    from culinarystate.vocab.foodon import norm
    names = {norm(i["canonical_name"]): i["id"] for i in store.all_latest("ING") if i["status"] == "ACTIVE"}
    for a in store.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en":
            names.setdefault(norm(a["normalized"]), a["ingredient_id"])
    procs = [p for p in store.all_latest("PROC") if p["status"] == "ACTIVE"]
    family = {p["id"]: p["family"] for p in procs}
    by: dict = {}
    for e in store.all_latest("KGE"):
        if e["status"] == "ACTIVE" and e["predicate"] == "ING_PROCESSED_BY":
            by.setdefault(e["subject_id"], []).append((-e["confidence"], e["object_id"]))
    lex = Lexicon(LineLinker(names, set()), {p["canonical_name"]: p["id"] for p in procs},
                  {i["id"]: tuple(i.get("parent_ids") or ()) for i in store.all_latest("ING")},
                  {k: tuple(p for _, p in sorted(v)) for k, v in by.items()},
                  frozenset(p["id"] for p in procs if p["family"] in HEAT_FAMILIES or p["canonical_name"] in EXTRA_METHODS))
    return lex, family
