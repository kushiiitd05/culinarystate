"""Step 19 P1 scoring after both commitments exist (S166; D-066). DRAFT_PENDING_H4.

Pairs annotator A's and B's packets through both sealed keys, refuses any label file whose bytes differ from its
committed sha256 (PV-6/PV-9), and summarises `pilot_agreement.recipe_metrics` / `disagreements` as numbers and
category counts only. The report never holds recipe ids, the packet-to-recipe keys, entity names or text (the
library's alignment map and disagreement rows carry free-text labels, so they are dropped). Under D-045 W2 the
labels are human-accepted AI drafts, so the report says so and is not a blind inter-annotator agreement.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Mapping

from culinarystate.annotation.gold import to_events
from culinarystate.annotation.pilot_agreement import CATEGORIES, disagreements, recipe_metrics
from culinarystate.scoring.state_metrics import final_fields
from culinarystate.state_graph.engine import replay
from culinarystate.quantity import rc2_dryrun as D

LABEL_BASIS = "HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND"
METRICS = ("spans_exact_f1", "spans_relaxed_f1", "concept_agreement", "unknown_disagreement_rate", "process_link_f1",
           "event_f1_strict", "event_f1_loose", "relation_f1", "structural_relation_f1", "coref_b_cubed_f1",
           "intermediate_entity_f1", "alive_entity_f1", "state_field_agreement")


GATE_RATE = 0.20  # THR-19P-16 / -31
# THR-19P-16 tool denominators, as tools/gold_pilot_agreement.py CAT_DENOM / denominators():
CAT_DENOM = {"boundary": "spans", "entity_type": "spans", "quantity": "spans", "canonical_identity": "lines",
             "event_type": "events", "event_argument": "events", "intermediate_identity": "events", "coref": "coref",
             "final_state": "state"}
SUMMED = ("spans", "events", "coref", "state")  # both annotators' units; "lines" counts annotator A only


def unit_counts(a: dict, b: dict) -> Counter:
    """Per-pair units exactly as the existing tool's denominators() (block M4; THR-19P-16)."""
    n = Counter()
    units = list(a["ingredient_lines"]) + list(a["steps"]) + list(b["ingredient_lines"]) + list(b["steps"])
    n["spans"] += sum(len(u["spans"]) for u in units)
    n["events"] += sum(len(s["events"]) for d in (a, b) for s in d["steps"])
    n["lines"] += len(a["ingredient_lines"])
    n["coref"] += sum(len(s.get("coref", [])) for d in (a, b) for s in d["steps"])
    n["state"] += len(final_fields(replay(to_events(a)))) + len(final_fields(replay(to_events(b))))
    return n


def handbook_gate(cats: Mapping[str, int], den: Mapping[str, int]) -> dict:
    """THR-19P-16 tool rate and THR-19P-31 per-pair rate (one annotator's units = summed / 2); gate on the max."""
    def rate(c, one):
        d = den.get(CAT_DENOM[c], 0)
        d = d / 2 if one and CAT_DENOM[c] in SUMMED else d
        return round(cats[c] / d, 4) if d else None
    tool = {c: rate(c, False) for c in CATEGORIES}
    pair = {c: rate(c, True) for c in CATEGORIES}
    flagged = sorted(c for c in CATEGORIES if max(tool[c] or 0, pair[c] or 0) > GATE_RATE)
    return {"threshold": GATE_RATE, "tool_rate": tool, "per_pair_rate": pair, "flagged_categories": flagged,
            "verdict": "HANDBOOK_REVISION_REQUIRED" if flagged else "NO_MECHANICAL_FLAG"}


class ScoreError(ValueError):
    pass


def pair_packets(key_a: Mapping[str, str], key_b: Mapping[str, str]) -> list[tuple[str, str]]:
    """(A packet, B packet) per recipe, in A packet order; the recipe sets must be identical."""
    by_rid = {rid: pid for pid, rid in key_b.items()}
    if set(key_a.values()) != set(by_rid) or len(by_rid) != len(key_b):
        raise ScoreError("KEYS_DIFFER: the two sealed keys do not cover the same recipes")
    return [(pa, by_rid[rid]) for pa, rid in sorted(key_a.items())]


def commitment_problems(commitment: Mapping, *, letter: str, label_dir: Path) -> list[str]:
    if commitment.get("annotator_letter") != letter:
        return [f"WRONG_LETTER: commitment is not annotator {letter}'s"]
    out = []
    for row in commitment.get("files", []):
        f = Path(label_dir) / f"{row['packet_id']}.json"
        if not f.is_file():
            out.append(f"MISSING_LABEL_FILE: {row['packet_id']}")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != row["sha256"]:
            out.append(f"CHANGED_SINCE_COMMITMENT: {row['packet_id']}")
    return out


def key_problems(key: Mapping[str, str], *, salt_hex: str, tracked_line: str, letter: str) -> list[str]:
    """The sealed key must match its tracked salted commitment (ksh review KS2b; checkable once salts are revealed)."""
    from culinarystate.annotation import pilot_packets as pp
    want = (tracked_line.split() or [""])[0]
    return [] if pp.key_commitment(key, salt_hex=salt_hex) == want else [f"KEY_COMMITMENT_MISMATCH: {letter}"]


def _coverage_problems(key: Mapping[str, str], commitment: Mapping, letter: str) -> list[str]:
    files = {row["packet_id"] for row in commitment.get("files", [])}
    return [] if set(key) == files else [f"KEY_VS_COMMITMENT: annotator {letter}'s key and commitment list different packets"]


def _f1(x) -> float | None:
    if isinstance(x, Mapping):
        if "f1" in x:
            return x["f1"]
        if "micro" in x:
            return x["micro"].get("f1")
        if "overall" in x:
            return x["overall"].get("f1")
    return x


def _numbers(m: Mapping) -> dict:
    return {"spans_exact_f1": _f1(m["spans_exact"]), "spans_relaxed_f1": _f1(m["spans_relaxed"]),
            "concept_agreement": m["concept_agreement"], "unknown_disagreement_rate": m["unknown_disagreement_rate"],
            "process_link_f1": _f1(m["process_link_f1"]), "event_f1_strict": _f1(m["event_f1_strict"]),
            "event_f1_loose": _f1(m["event_f1_loose"]), "relation_f1": _f1(m["relation"]),
            "structural_relation_f1": _f1(m["structural_relation_f1"]), "coref_b_cubed_f1": _f1(m["coref_b_cubed"]),
            "intermediate_entity_f1": _f1(m["intermediate_entity_f1"]), "alive_entity_f1": _f1(m["alive_entity_f1"]),
            "state_field_agreement": m["state_field_agreement"]["agree"],
            "replay_ok": bool(m["replay_consistent"]["ok"])}


def sp002_normalised(doc: Mapping) -> dict:
    """Copy of a label doc with U+2044 FRACTION SLASH -> "/" in ingredient-line text (same length, offsets kept)."""
    out = json.loads(json.dumps(doc))
    for line in out["ingredient_lines"]:
        line["text"] = line["text"].replace("\u2044", "/")
    return out


def _summarise(pairs):
    per, cats, den = [], Counter({c: 0 for c in CATEGORIES}), Counter()
    for n, (doc_a, doc_b) in enumerate(pairs, 1):
        m = recipe_metrics(doc_a, doc_b)
        den.update(unit_counts(doc_a, doc_b))
        c = Counter(r["category"] for r in disagreements(doc_a, doc_b, m["alignment"]))
        cats.update(c)
        per.append({"pair": f"pair_{n:02d}", **_numbers(m), "disagreements": dict(sorted(c.items()))})
    mean = {k: (round(sum(p[k] for p in per if p[k] is not None) / max(1, sum(p[k] is not None for p in per)), 4)
                if any(p[k] is not None for p in per) else None) for k in METRICS}
    return per, cats, den, mean


def score(key_a: Mapping[str, str], key_b: Mapping[str, str], *, labels_a: Path, labels_b: Path,
          commitment_a: Mapping, commitment_b: Mapping) -> dict:
    problems = (commitment_problems(commitment_a, letter="A", label_dir=labels_a)
                + commitment_problems(commitment_b, letter="B", label_dir=labels_b)
                + _coverage_problems(key_a, commitment_a, "A") + _coverage_problems(key_b, commitment_b, "B"))
    if problems:
        raise ScoreError("; ".join(problems))
    pairs = []
    for pa, pb in pair_packets(key_a, key_b):
        pairs.append((json.loads((Path(labels_a) / f"{pa}.json").read_text(encoding="utf-8")),
                      json.loads((Path(labels_b) / f"{pb}.json").read_text(encoding="utf-8"))))
    per, cats, den, mean = _summarise(pairs)
    s_per, s_cats, s_den, s_mean = _summarise([(sp002_normalised(a), sp002_normalised(b)) for a, b in pairs])
    report = {"record": "STEP19_P1_AGREEMENT_COUNTS", "status": "AI_ENGINEERING_SCORE_COUNTS_ONLY",
              "label_basis": LABEL_BASIS, "counts_as_human_gate": False, "contains_ids": False, "contains_text": False,
              "pairs": len(per), "replay_ok_pairs": sum(p["replay_ok"] for p in per), "mean": mean,
              "disagreement_categories": dict(sorted(cats.items())), "denominators": dict(sorted(den.items())),
              "handbook_gate": handbook_gate(cats, den), "per_pair": per,
              # block N7 (D-069): SP-002 sensitivity, never replacing the headline numbers above
              "sensitivity_sp002": {"basis": "U2044_NORMALISED_AT_SCORING_LABELS_UNCHANGED", "mean": s_mean,
                                    "disagreement_categories": dict(sorted(s_cats.items())),
                                    "handbook_gate": handbook_gate(s_cats, s_den)}}
    D.assert_counts_only(report)
    return report
