"""End-to-end question -> slots -> evidence packets -> feasibility -> decision (DEL-5 rule baseline, B5 rung).

Slots: ingredient = first lexicon mention (LineLinker); processes = action verbs in the question, in order
(step_processes, inflection-aware); target = first nutrient phrase (cross_source NUTRIENT patterns).
RECOMMEND questions without a process get candidates from the corpus (SSOT §243.2): the ingredient's
ING_PROCESSED_BY edges restricted to heat processes, in edge-confidence order. Nothing is invented: unlinked
slots stay None and the policy asks or abstains.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from pathlib import Path

from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.food_graph import FoodGraph
from culinarystate.retrieval.retriever import EvidenceRetriever
from culinarystate.state_graph.rule_compiler import step_processes
from culinarystate.transition.cross_source import NUTRIENT
from culinarystate.vocab.line_link import LineLinker

from .diagnosis import TroubleshootIndex, diagnose
from .session_state import SessionState
from .state_conditioning import condition_slots
from .targets import TargetLexicon
from .feasibility import Action, Constraints, Requirements, check
from .ood import SupportIndex
from .policy import decide
from .relevance import intent
from .candidates import CandidateSet, substitution_candidates, sequence_candidates
from .selector import Option, Selection, select

HEAT_FAMILIES = ("WET_HEAT", "DRY_HEAT", "FAT_HEAT")          # cooking-method candidates (+ microwave below)
EXTRA_METHODS = ("microwave",)                                   # in HEAT_GENERAL with cook/heat/melt
MAX_CANDIDATES = 4
# verbs whose question reading is not a cooking action: "keep vitamin C" (-> reserve), "sauce split" (state, -> divide),
# modal "can" (-> canning), generic "cook"
QUESTION_NOT_PROCESS = {"cook", "reserve", "divide", "can", "serve", "set", "rest"}
NEGATION = re.compile(r"\b(?:not|never|without|no)\s+(?:\w+\s+)?$")
# non-numeric targets (SSOT §242.7: quantitative output only if the target definition supports it)
QUALITATIVE_TARGET = re.compile(r"\b(texture|colou?r|flavou?r|taste|aroma|smell|crisp(?:ness)?|tender(?:ness)?|"
                                r"moisture|juic(?:y|iness)|softness|firmness)\b")


@dataclass(frozen=True)
class Lexicon:
    linker: LineLinker
    proc_ids: dict                  # canonical process name -> PROC id
    parents: dict                   # ING id -> tuple of parent ING ids
    processed_by: dict              # ING id -> PROC ids by ING_PROCESSED_BY confidence
    heat_procs: frozenset
    relations: dict = field(default_factory=dict)   # ING id -> ((ING id, relation), ...) from the R4 food graph
    targets: TargetLexicon | None = None             # ledger target names (closed world); regex list is the fallback
    alternatives: dict = field(default_factory=dict)  # ING id -> ((ING id, confidence), ...) ING_ALTERNATIVE_TO (C10)
    followed_by: dict = field(default_factory=dict)   # PROC id -> ((PROC id, confidence), ...) PROC_FOLLOWED_BY (C10)
    ing_names: dict = field(default_factory=dict)     # ING id -> canonical name
    carbon: dict = field(default_factory=dict)        # ING id -> typical kgCO2e/kg (p50 of ING_CARBON_FOOTPRINT)
    durations: dict = field(default_factory=dict)     # PROC id -> typical minutes (p50 of PROC_TYPICAL_DURATION)


@dataclass(frozen=True)
class Slots:
    ingredient_id: str | None
    ingredient_name: str | None
    parents: tuple
    processes: tuple                # ((name, PROC id), ...)
    target: str | None
    candidates: tuple               # PROC ids generated for RECOMMEND
    contradictions: tuple = ()      # PROC ids both affirmed and negated ("boiled and not boiled")
    numeric_target: bool = True


def parse_query(q: str, lex: Lexicon) -> Slots:
    ments = lex.linker.mentions(q)
    ing = ments[0] if ments else None
    seen, procs, negated = set(), [], set()
    for pos, name in step_processes(q):          # one hit per process: the affirmed reading
        pid = lex.proc_ids.get(name)
        if pid and name not in QUESTION_NOT_PROCESS and pid not in seen and \
                not NEGATION.search(q[max(0, pos - 24):pos].lower()):
            seen.add(pid)
            procs.append((name, pid))
    for m in re.finditer(r"[A-Za-z]+(?:-[A-Za-z]+)?", q):     # every mention, for negations ("not boiled")
        if NEGATION.search(q[max(0, m.start() - 24):m.start()].lower()):
            negated |= {lex.proc_ids[n] for _, n in step_processes(m.group(0)) if n in lex.proc_ids}
    lt = lex.targets.find(q) if lex.targets else None
    tm = None if lt else next((m for pat, _ in NUTRIENT if (m := re.search(pat, q.lower()))), None)
    qual = QUALITATIVE_TARGET.search(q.lower()) if not (lt or tm) else None
    cands = ()
    if not procs and ing and intent(q) == "RECOMMEND":
        cands = tuple(p for p in lex.processed_by.get(ing, ()) if p in lex.heat_procs)[:MAX_CANDIDATES]
    name = next((n for n, i in lex.linker.names.items() if i == ing), None) if ing else None
    target = lt or (tm.group(0) if tm else qual.group(0) if qual else None)
    return Slots(ing, name, tuple(lex.parents.get(ing, ())), tuple(procs), target, cands,
                 tuple(sorted(seen & negated)), numeric_target=not qual)

FEAS_MAP = {"ALLOW": "ALLOWED", "REJECT": "REJECTED", "UNKNOWN": "UNKNOWN"}


def pareto_view(packets: dict, feas: dict, proc_ids: dict, durations: dict | None = None) -> Selection | None:
    """C15: Pareto trade-off over the compared/recommended options. Retention = median MEASURED retention_factor
    in the packet's evidence pool (None when unmeasured); time = typical minutes of the process when a duration profile exists (None = neutral). Needs >=2 options."""
    if len(packets) < 2:
        return None
    opts = []
    for n, pk in packets.items():
        pool = pk.direct or pk.near
        vals = sorted(rf["value"] for h in pool
                      if (rf := h.row["derived"].get("retention_factor") or {}).get("status") == "MEASURED"
                      and isinstance(rf.get("value"), (int, float)))
        ret = vals[len(vals) // 2] if vals else None
        opts.append(Option(n, retention=ret, feasibility=FEAS_MAP.get(feas.get(n, {}).get("decision"), "UNKNOWN"),
                           process_id=proc_ids.get(n), evidence_count=len(pool),
                           time_minutes=(durations or {}).get(proc_ids.get(n))))
    return select(opts)


def extra_candidates(q: str, s: Slots, lex: Lexicon) -> CandidateSet | None:
    """C10: substitution (RECOMMEND/COMPARE/RECOVER) and next-step (RECOVER/COMPARE with a process) candidates.
    Corpus edges only; None when the intent or slots give nothing to generate from."""
    it = intent(q)
    if it not in ("RECOMMEND", "COMPARE", "RECOVER"):
        return None
    pid = s.processes[0][1] if s.processes else None
    name_of = {v: n for n, v in lex.proc_ids.items()}
    subs = substitution_candidates(s.ingredient_id, lex.alternatives, lex.ing_names)
    base = lex.carbon.get(s.ingredient_id)
    if base is not None:                       # C15 sustainability context, only where both footprints are evidenced
        subs = [replace(c, reason=f"{c.reason}; carbon {lex.carbon[c.id]:.1f} vs {base:.1f} kgCO2e/kg (literature median)")
                if c.id in lex.carbon else c for c in subs]
    seqs = sequence_candidates(pid, lex.followed_by, name_of) if it in ("RECOVER", "COMPARE") else []
    if not (subs or seqs):
        return None
    return CandidateSet(s.ingredient_id, pid, s.target, tuple(subs + seqs))


def answer(q: str, lex: Lexicon, retriever: EvidenceRetriever, req: Requirements, proc_family: dict,
           constraints: Constraints | None = None, k: int = 10, support_index: SupportIndex | None = None,
           troubleshoot: TroubleshootIndex | None = None, session: SessionState | None = None,
           use_state: bool = False) -> dict:
    """use_state=False is rung B3 (question slots only); True is B4 (empty slots filled from the reconstructed session state)."""
    s = parse_query(q, lex)
    state_trace: dict = {}
    if use_state and session:
        s, state_trace = condition_slots(q, s, session, lex)
    t_opts = None
    if not s.target and s.processes and support_index and intent(q) in ("ANSWER", "COMPARE"):
        t_opts = [t for t, _ in support_index.targets_for(s.ingredient_id, s.parents, s.ingredient_name, s.processes[0][1])]
        if len(t_opts) == 1:                      # VOI: a single evidenced target -> asking changes nothing
            s = Slots(s.ingredient_id, s.ingredient_name, s.parents, s.processes, t_opts[0], s.candidates,
                      s.contradictions, s.numeric_target)
    name_of = {v: n for n, v in lex.proc_ids.items()}
    options = [(n, p) for n, p in s.processes] or [(name_of.get(p, p), p) for p in s.candidates]
    if intent(q) not in ("COMPARE", "RECOMMEND", "RECOVER"):
        options = options[:1]

    def query(pid: str) -> Query:
        return Query(ingredient_id=s.ingredient_id, ingredient_name=s.ingredient_name,
                     ingredient_parents=frozenset(s.parents), process_id=pid,
                     process_family=proc_family.get(pid), target=s.target,
                     ingredient_relations=lex.relations.get(s.ingredient_id, ()))

    # B4: the retrieval text carries the state-filled slots too, so BM25 candidates are state-conditioned, not only the compat axes
    qr = f"{q} {s.ingredient_name or ''} {' '.join(n for n, _ in s.processes)}".strip() if state_trace else q
    packets = {n: retriever.packet(qr, query(p), k) for n, p in options}
    feas = {n: check(Action(p, (s.ingredient_id,) if s.ingredient_id else ()), constraints or Constraints(), req)
            for n, p in options}
    slots = {"ingredient": s.ingredient_id, "process": options[0][1] if options else None, "target": s.target,
             "needs_target": intent(q) in ("ANSWER", "COMPARE"), "contradictions": list(s.contradictions),
             "target_options": t_opts}
    # C18: diagnosis uses session process history when available, falls back to question processes
    history = list(session.process_history()) if session else [n for n, _ in s.processes]
    dg = diagnose(q, history, troubleshoot) \
        if troubleshoot and intent(q) in ("DIAGNOSE", "RECOVER") else None
    support = {n: support_index.support(s.ingredient_id, s.parents, s.ingredient_name, p) for n, p in options} \
        if support_index else None
    return {"slots": s, "decision": decide(q, packets, slots, feasibility=feas, support=support, numeric_target=s.numeric_target,
                              diagnosis=dg), "packets": packets,
            "feasibility": feas, "support": support, "session": session, "state_trace": state_trace,
            "candidates": extra_candidates(q, s, lex),
            "pareto": pareto_view(packets, feas, dict(options), lex.durations) if intent(q) in ("COMPARE", "RECOMMEND") else None}


OFF_TAXONOMY = Path(__file__).resolve().parents[3] / "data" / "raw" / "off" / "ingredients_a1ce1d36.txt"


def load_lexicon(store, off_path: Path | None = OFF_TAXONOMY) -> tuple[Lexicon, dict]:
    """off_path: OFF taxonomy for R4 relations (parents/children/ancestors); None or missing file -> ING parents only."""
    from culinarystate.vocab.foodon import norm
    from culinarystate.vocab.off import parse as parse_off
    names = {norm(i["canonical_name"]): i["id"] for i in store.all_latest("ING") if i["status"] == "ACTIVE"}
    for a in store.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en":
            names.setdefault(norm(a["normalized"]), a["ingredient_id"])
    procs = [p for p in store.all_latest("PROC") if p["status"] == "ACTIVE"]
    family = {p["id"]: p["family"] for p in procs}
    by: dict = {}
    alts: dict = {}
    fol: dict = {}
    dur: dict = {}
    carb: dict = {}
    for e in store.all_latest("KGE"):
        if e["status"] != "ACTIVE":
            continue
        if e["predicate"] == "ING_PROCESSED_BY":
            by.setdefault(e["subject_id"], []).append((-e["confidence"], e["object_id"]))
        elif e["predicate"] == "ING_ALTERNATIVE_TO":
            alts.setdefault(e["subject_id"], []).append((e["object_id"], e["confidence"]))
        elif e["predicate"] == "ING_CARBON_FOOTPRINT" and (e.get("quantiles") or {}).get("p50") is not None:
            carb[e["subject_id"]] = e["quantiles"]["p50"]
        elif e["predicate"] == "PROC_TYPICAL_DURATION" and (e.get("quantiles") or {}).get("p50") is not None:
            dur[e["subject_id"]] = e["quantiles"]["p50"]
        elif e["predicate"] == "PROC_FOLLOWED_BY":
            fol.setdefault(e["subject_id"], []).append((e["object_id"], e["confidence"]))
    ings = [i for i in store.all_latest("ING") if i["status"] == "ACTIVE"]
    off = {k: e.parents for k, e in parse_off(off_path).items()} if off_path and off_path.exists() else {}
    graph = FoodGraph(ings, off)
    relations = {i["id"]: r for i in ings if (r := tuple(graph.related(i["id"]).items()))}
    targets = TargetLexicon(sorted({e["target"]["raw_name"] for e in store.all_latest("EVD") if e["status"] == "ACTIVE"}))
    lex = Lexicon(LineLinker(names, set()), {p["canonical_name"]: p["id"] for p in procs},
                  {i["id"]: tuple(i.get("parent_ids") or ()) for i in store.all_latest("ING")},
                  {k: tuple(p for _, p in sorted(v)) for k, v in by.items()},
                  frozenset(p["id"] for p in procs if p["family"] in HEAT_FAMILIES or p["canonical_name"] in EXTRA_METHODS),
                  relations, targets,
                  {k: tuple(sorted(v, key=lambda x: -x[1])) for k, v in alts.items()},
                  {k: tuple(sorted(v, key=lambda x: -x[1])) for k, v in fol.items()},
                  {i["id"]: i["canonical_name"] for i in ings}, carb, dur)
    return lex, family
