"""H1 gold-independence checks (S178; REV-B F-13, G-05/G-06; consensus T8-C04-R2; SSOT v16 draft 287.2). DRAFT.

The S173 benchmark draft has two circularities the H1 evaluation must be able to show or exclude:

1. The S1 gold ("ingredients heated so far") and the S2 gold (next action) are the Rung A engine's own replay. The
   legacy B4 context prints "Heated so far", the S1 gold computed by the same function, and every rung retrieves from
   steps after the cut (the next action sits in one of them). H1 on such rows measures engine self-consistency.
2. A reviewer who sees the engine gold and keeps it has not produced independent gold.

What this module provides (pure functions; the corpus is read only by the tool that calls them):
- ``gold_origin`` / ``gold_origin_detail`` / ``gold_independence_report``: provenance gate over the S rows (ENGINE_DRAFT,
  HUMAN_AFTER_SEEING_ENGINE, HUMAN_BLIND). Only HUMAN_BLIND rows are independent of the engine run. Since S178 FIX-EVAL
  (SCI-B E1) HUMAN_BLIND needs evidence: the scored gold comes from a filled blind-answer column (``gold_source`` =
  BLIND_HUMAN, a non-empty ``blind_answer*`` column) with ``seen_system_output`` false. A KEEP or EDIT of an engine draft is
  HUMAN_AFTER_SEEING_ENGINE (reason ENGINE_DRAFT_KEPT / ENGINE_DRAFT_EDITED) whatever the seen flag says, and an explicit
  HUMAN_BLIND that contradicts the row (AI drafter or kept draft without a blind answer, or seen true) is refused
  (``GoldOriginRefused``; the report label becomes REFUSED_GOLD_PROVENANCE_CONFLICT).
- ``engine_outputs`` / ``shared_engine_outputs`` / ``context_leaks`` / ``assert_independent``: the gold-vs-context test.
  It fails when an engine output (heated ingredient set, next process) appears both in the gold and in the context of
  a rung, or when a context carries an aggregate answer field or a step after the cut.
- ``primitive_events`` / ``heated_from_primitives``: how far the engine events that the independent B4 context still
  prints determine the S1 gold (the residual circularity that only blind-first human gold removes).
- ``heat_presence_agreement``: a text-only cross-check (plain heat-verb scan, no engine) used as a plausibility figure.
- ``gold_agreement``: engine draft vs final (human-edited) gold, the figure T8-C04-R2 asks to report with the caveat.

None of this makes the gold independent; it shows which rows are not, and blocks the claim label accordingly.
"""
from __future__ import annotations

import re
from typing import Any, Iterable, Mapping, Sequence

from culinarystate.evaluation import d5_state as DS
from culinarystate.evaluation import h1_rungs as H
from culinarystate.evaluation.paired_stats import wilson

VERSION = "h1_independence@0.3"
GOLD_ORIGINS = ("ENGINE_DRAFT", "HUMAN_AFTER_SEEING_ENGINE", "HUMAN_BLIND", "AI_DRAFTED_GOLD")   # S179: D-085 AI gold
LABELS = ("INDEPENDENT_GOLD", "PARTLY_INDEPENDENT", "CIRCULAR_SELF_CONSISTENCY_ONLY", "REFUSED_GOLD_PROVENANCE_CONFLICT")
BLIND_GOLD_SOURCE = "BLIND_HUMAN"
BLIND_ANSWER_PREFIX = "blind_answer"          # e.g. blind_answer_r1 / blind_answer_r2 on the blind-first sheet (amendment C4)
# A drafter that is an AI agent, a model or the engine (whole tokens; "_", "-" and digits are separators).
AI_DRAFTER = re.compile(r"(?<![a-z])(ai|agent|claude|anthropic|engine|llm|gpt|model|bot|assistant|qwen|rung)(?![a-z])", re.I)
HEATED_LINE = re.compile(r"^Heated so far:[ \t]*(.*)$", re.M | re.I)
STEP_LINE = re.compile(r"^Step (\d+):", re.M)
_FALSE = {"false", "0", "no", "n"}
_TRUE = {"true", "1", "yes", "y"}
HEAT_VERBS = re.compile(
    r"\b(boil\w*|simmer\w*|fry\w*|fri(?:ed|es)|bak(?:e|ed|es|ing)|roast\w*|saut[eé]\w*|steam\w*|grill\w*|stew\w*|poach\w*|"
    r"toast\w*|brown\w*|sear\w*|braise\w*|braising|blanch\w*|scald\w*|cook\w*|heat\w*|warm\w*|melt\w*|"
    r"parboil\w*|broil\w*|caramel\w*|reduc\w*)\b", re.I)


class GoldOriginRefused(ValueError):
    """The row's provenance fields contradict each other (e.g. an explicit HUMAN_BLIND on an AI draft with no blind answer)."""

    def __init__(self, qid: str, reason: str):
        self.qid, self.reason = qid, reason
        super().__init__(f"{qid}: {reason}")


class GoldContextOverlap(AssertionError):
    """Gold and a rung context share engine outputs, or the context leaks an answer field / post-cut step."""

    def __init__(self, findings: Iterable[str]):
        self.findings = list(findings)
        super().__init__("; ".join(self.findings))


# ------------------------------------------------------------------ provenance gate

def is_ai_drafted(row: Mapping[str, Any]) -> bool:
    """The draft (and so any gold kept from it) was written by an AI agent, a model or the engine."""
    return bool(AI_DRAFTER.search(str(row.get("drafted_by") or "")))


def _blind_answer_filled(row: Mapping[str, Any]) -> bool:
    return any(str(k).lower().startswith(BLIND_ANSWER_PREFIX) and str(v or "").strip() for k, v in row.items())


def gold_origin_detail(row: Mapping[str, Any]) -> tuple[str, str]:
    """(origin, reason) of the gold of one S row; raises ``GoldOriginRefused`` on contradictory provenance.

    HUMAN_BLIND only with evidence: ``gold_source`` BLIND_HUMAN, a filled ``blind_answer*`` column and ``seen_system_output``
    false (reason BLIND_ANSWER_COLUMN). An explicit ENGINE_DRAFT or HUMAN_AFTER_SEEING_ENGINE always wins (a downgrade). An
    explicit HUMAN_BLIND without that evidence is accepted only from a non-AI drafter with no KEEP / EDIT verdict and no seen
    flag set to true (EXPLICIT_DECLARED_NON_AI_DRAFTER, e.g. the synthetic fixture); otherwise it is refused. A KEEP or EDIT
    verdict means the gold is the kept engine draft: HUMAN_AFTER_SEEING_ENGINE (ENGINE_DRAFT_KEPT / ENGINE_DRAFT_EDITED)."""
    qid = str(row.get("qid") or "?")
    explicit = str(row.get("gold_origin") or "").strip().upper()
    verdict = str(row.get("verdict") or row.get("human_verdict") or "").strip().upper()
    seen = str(row.get("seen_system_output", "") or "").strip().lower()
    source = str(row.get("gold_source") or "").strip().upper()
    filled = _blind_answer_filled(row)
    blind_evidence = source == BLIND_GOLD_SOURCE and filled and seen in _FALSE
    if explicit in ("ENGINE_DRAFT", "HUMAN_AFTER_SEEING_ENGINE"):
        return explicit, "EXPLICIT_DOWNGRADE"
    if explicit == "AI_DRAFTED_GOLD":                 # S179 D-085: written by the AI personas; never HUMAN_BLIND
        if source == BLIND_GOLD_SOURCE:
            raise GoldOriginRefused(qid, "AI_DRAFTED_GOLD_WITH_GOLD_SOURCE_BLIND_HUMAN")
        return "AI_DRAFTED_GOLD", "EXPLICIT_AI_DELEGATE_D085"
    if source == BLIND_GOLD_SOURCE and not filled:
        raise GoldOriginRefused(qid, "GOLD_SOURCE_BLIND_HUMAN_WITHOUT_A_FILLED_BLIND_ANSWER")
    if explicit == "HUMAN_BLIND":
        if seen in _TRUE:
            raise GoldOriginRefused(qid, "EXPLICIT_HUMAN_BLIND_BUT_SEEN_SYSTEM_OUTPUT_TRUE")
        if blind_evidence:
            return "HUMAN_BLIND", "BLIND_ANSWER_COLUMN"
        if is_ai_drafted(row):
            raise GoldOriginRefused(qid, "EXPLICIT_HUMAN_BLIND_ON_AN_AI_DRAFTED_ROW_WITH_EMPTY_BLIND_COLUMNS")
        if verdict in ("KEEP", "EDIT"):
            raise GoldOriginRefused(qid, "EXPLICIT_HUMAN_BLIND_ON_A_KEPT_DRAFT_WITH_EMPTY_BLIND_COLUMNS")
        return "HUMAN_BLIND", "EXPLICIT_DECLARED_NON_AI_DRAFTER"
    if blind_evidence:
        return "HUMAN_BLIND", "BLIND_ANSWER_COLUMN"
    if source == BLIND_GOLD_SOURCE:
        return "HUMAN_AFTER_SEEING_ENGINE", "BLIND_ANSWER_BUT_SEEN_FLAG_NOT_FALSE"
    if verdict == "KEEP":
        return "HUMAN_AFTER_SEEING_ENGINE", "ENGINE_DRAFT_KEPT"
    if verdict == "EDIT":
        return "HUMAN_AFTER_SEEING_ENGINE", "ENGINE_DRAFT_EDITED"
    return "ENGINE_DRAFT", "NO_HUMAN_VERDICT"


def gold_origin(row: Mapping[str, Any]) -> str:
    """Origin of the gold of one S row (see ``gold_origin_detail``; raises ``GoldOriginRefused`` on contradictions)."""
    return gold_origin_detail(row)[0]


def gold_independence_report(rows: Sequence[Mapping[str, Any]], *, blocks: Sequence[str] = ("S1", "S2")) -> dict:
    """Counts of S rows by gold origin and the label H1 may carry. Only HUMAN_BLIND rows are independent; any refused
    row makes the label REFUSED_GOLD_PROVENANCE_CONFLICT (the provenance must be repaired before H1 is labelled)."""
    sel = [r for r in rows if str(r.get("block")) in blocks]
    per_block: dict[str, dict[str, int]] = {b: {o: 0 for o in GOLD_ORIGINS} for b in blocks}
    reasons: dict[str, int] = {}
    circular, refused = [], {}
    for r in sel:
        try:
            o, why = gold_origin_detail(r)
        except GoldOriginRefused as e:
            refused[str(r.get("qid"))] = e.reason
            circular.append(str(r.get("qid")))
            continue
        per_block[str(r["block"])][o] += 1
        reasons[why] = reasons.get(why, 0) + 1
        if o != "HUMAN_BLIND":
            circular.append(str(r.get("qid")))
    n, n_ind = len(sel), len(sel) - len(circular)
    label = ("REFUSED_GOLD_PROVENANCE_CONFLICT" if refused else
             "CIRCULAR_SELF_CONSISTENCY_ONLY" if n_ind == 0 else "INDEPENDENT_GOLD" if n_ind == n else "PARTLY_INDEPENDENT")
    return {"version": VERSION, "n_rows": n, "n_independent": n_ind, "n_not_independent": len(circular),
            "n_refused": len(refused), "refused": dict(sorted(refused.items())),
            "by_block": per_block, "by_reason": dict(sorted(reasons.items())), "label": label,
            "not_independent_qids": sorted(circular),
            "rule": "only gold_origin HUMAN_BLIND is independent of the engine run: the scored gold comes from a filled "
                    "blind-answer column (gold_source BLIND_HUMAN) answered from the recipe text with seen_system_output "
                    "false; a KEEP / EDIT of an engine draft is HUMAN_AFTER_SEEING_ENGINE"}


# ------------------------------------------------------------------ engine outputs and the overlap test

def engine_outputs(steps: Sequence[str], cut: int, *, locale: str | None = None,
                   family: Mapping[str, str] | None = None) -> dict:
    """What the Rung A engine says about the recipe at the cut (the fields an S gold is drafted from)."""
    fam = H._family() if family is None else family
    g = DS.graph("\n".join(steps[:cut]), locale)
    names: dict[str, str] = {}
    for e in g.entities:
        ing = H._attr(e.attributes, "ingredient_id")
        if ing and e.span is not None:
            names.setdefault(ing, e.span.surface.lower())
    heated = DS.heated_ingredient_ids(g, fam)
    nxt = DS.next_action(steps, cut, locale)
    return {"heated_ids": sorted(heated), "heated_names": sorted(names.get(i, i) for i in heated),
            "used_ids": sorted(DS.linked_ingredient_ids(g)),
            "next_process_id": (nxt or {}).get("process_id"),
            "next_step_index": None if not nxt else nxt["step_index"] + 1}      # 1-based step holding the next action


def gold_engine_outputs(row: Mapping[str, Any], engine: Mapping[str, Any]) -> list[str]:
    """Engine output fields that the gold of ``row`` equals (the gold was drafted from them)."""
    out = []
    if str(row.get("block")) == "S1":
        gold = {x for x in str(row.get("gold_ingredient_ids") or "").split("|") if x}
        if gold and gold == set(engine.get("heated_ids") or ()):
            out.append("heated_ids")
    if str(row.get("block")) == "S2":
        pid = str(row.get("gold_next_process_id") or "")
        if pid and pid == (engine.get("next_process_id") or ""):
            out.append("next_process_id")
    return out


def context_engine_outputs(row: Mapping[str, Any], context: str, engine: Mapping[str, Any]) -> list[str]:
    """Engine output fields the rung context carries (as an aggregate line or as the step that holds the answer)."""
    out = []
    if str(row.get("block")) == "S1":
        for m in HEATED_LINE.finditer(context or ""):
            printed = {x.strip().lower() for x in m.group(1).split(",") if x.strip() and x.strip() != "none"}
            if printed and printed == set(engine.get("heated_names") or ()):
                out.append("heated_ids")
                break
    if str(row.get("block")) == "S2" and engine.get("next_step_index"):
        if int(engine["next_step_index"]) in {int(x) for x in STEP_LINE.findall(context or "")}:
            out.append("next_process_id")
    return out


def shared_engine_outputs(row: Mapping[str, Any], context: str, engine: Mapping[str, Any]) -> list[str]:
    """Engine outputs present in BOTH the gold and the context (empty = the rung is not handed the gold)."""
    return sorted(set(gold_engine_outputs(row, engine)) & set(context_engine_outputs(row, context, engine)))


def context_leaks(row: Mapping[str, Any], context: str, *, cut: int) -> list[str]:
    """Findings that hold whatever the gold is: an aggregate answer field, or a step after the question point."""
    out = []
    if str(row.get("block")) == "S1" and HEATED_LINE.search(context or ""):
        out.append("AGGREGATE_ANSWER_FIELD: context prints a 'Heated so far' line (the S1 answer field)")
    late = sorted({int(x) for x in STEP_LINE.findall(context or "") if int(x) > cut})
    if late:
        out.append(f"POST_CUT_STEP: context retrieves step(s) {late} after the cut at step {cut}")
    return out


def assert_independent(row: Mapping[str, Any], context: str, engine: Mapping[str, Any], *, cut: int) -> None:
    """Raise ``GoldContextOverlap`` when gold and context share engine outputs or the context leaks."""
    findings = [f"SHARED_ENGINE_OUTPUT: {x}" for x in shared_engine_outputs(row, context, engine)]
    findings += context_leaks(row, context, cut=cut)
    if findings:
        raise GoldContextOverlap(findings)


# ------------------------------------------------------------------ what the independent B4 context still hands over

def primitive_events(steps: Sequence[str], cut: int, *, locale: str | None = None) -> list[dict]:
    """The engine events behind the PRIMITIVES state view: action word and bound ingredient ids, in text order."""
    g = DS.graph("\n".join(steps[:cut]), locale)
    return [{"surface": ev.span.surface.lower(), "ing_ids": sorted(H._lot_ingredients(g, ev.consumes))}
            for ev in sorted(g.events, key=lambda e: e.span.char_start)]


def heated_from_primitives(events: Sequence[Mapping[str, Any]]) -> set[str]:
    """Ingredients bound to an event whose action word matches a plain heat-verb pattern (a rule a reader can apply to
    the printed "Actions so far" line without the engine's heat families or parent-lot walk)."""
    out: set[str] = set()
    for e in events:
        if HEAT_VERBS.search(str(e.get("surface", ""))):
            out.update(e.get("ing_ids") or ())
    return out


# ------------------------------------------------------------------ text-only plausibility and agreement

def heat_presence_agreement(steps: Sequence[str], cut: int, gold_ids: set[str]) -> str:
    """Plain heat-verb scan of ``steps[:cut]`` (no engine, no lexicon) against a non-empty/empty S1 gold.

    AGREE: verb found and gold non-empty, or none found and gold empty. GOLD_WITHOUT_HEAT_WORD: gold lists heated
    ingredients but the prefix has no heat verb (suspicious gold). HEAT_WORD_WITHOUT_GOLD: the reverse (the engine
    may have missed it). A coarse plausibility figure only; it cannot confirm which ingredients were heated.
    """
    has_verb = bool(HEAT_VERBS.search(" ".join(steps[:cut])))
    if has_verb == bool(gold_ids):
        return "AGREE"
    return "HEAT_WORD_WITHOUT_GOLD" if has_verb else "GOLD_WITHOUT_HEAT_WORD"


def gold_agreement(draft_rows: Sequence[Mapping[str, Any]], final_rows: Sequence[Mapping[str, Any]]) -> dict:
    """Engine-draft gold vs final (human-edited) gold per S block, by qid. T8-C04-R2 'agreement figure'.

    S1: exact set equality of ``gold_ingredient_ids`` (and mean Jaccard). S2: equal ``gold_next_process_id``.
    DROPPED questions are counted, not scored. Wilson 95 % intervals on the exact-agreement rate.
    """
    final = {str(r["qid"]): r for r in final_rows}
    out: dict[str, Any] = {"version": VERSION}
    for block, field in (("S1", "gold_ingredient_ids"), ("S2", "gold_next_process_id")):
        n = agree = dropped = missing = 0
        jac = []
        for d in draft_rows:
            if str(d.get("block")) != block:
                continue
            f = final.get(str(d["qid"]))
            if f is None:
                missing += 1
                continue
            if str(f.get("verdict") or "").upper() == "DROP":
                dropped += 1
                continue
            a = {x for x in str(d.get(field) or "").split("|") if x}
            b = {x for x in str(f.get(field) or "").split("|") if x}
            n += 1
            agree += a == b
            if block == "S1":
                jac.append(1.0 if not a and not b else len(a & b) / len(a | b))
        lo, hi = wilson(agree, n)
        out[block] = {"n_scored": n, "n_exact_agree": agree, "n_dropped": dropped, "n_missing_final": missing,
                      "exact_agreement": round(agree / n, 4) if n else None,
                      "wilson95": [round(lo, 4), round(hi, 4)] if n else None,
                      **({"mean_jaccard": round(sum(jac) / len(jac), 4) if jac else None} if block == "S1" else {})}
    out["caveat"] = ("Engine draft vs human-edited gold: an anchored reviewer inflates agreement; blind-first gold "
                     "(gold_origin HUMAN_BLIND) is the non-circular figure.")
    return out
