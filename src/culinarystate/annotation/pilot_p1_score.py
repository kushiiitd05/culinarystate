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

from culinarystate.annotation.pilot_agreement import CATEGORIES, disagreements, recipe_metrics
from culinarystate.quantity import rc2_dryrun as D

LABEL_BASIS = "HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND"
METRICS = ("spans_exact_f1", "spans_relaxed_f1", "concept_agreement", "unknown_disagreement_rate", "process_link_f1",
           "event_f1_strict", "event_f1_loose", "relation_f1", "structural_relation_f1", "coref_b_cubed_f1",
           "intermediate_entity_f1", "alive_entity_f1", "state_field_agreement")


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


def score(key_a: Mapping[str, str], key_b: Mapping[str, str], *, labels_a: Path, labels_b: Path,
          commitment_a: Mapping, commitment_b: Mapping) -> dict:
    problems = (commitment_problems(commitment_a, letter="A", label_dir=labels_a)
                + commitment_problems(commitment_b, letter="B", label_dir=labels_b))
    if problems:
        raise ScoreError("; ".join(problems))
    per, cats = [], Counter({c: 0 for c in CATEGORIES})
    for n, (pa, pb) in enumerate(pair_packets(key_a, key_b), 1):
        doc_a = json.loads((Path(labels_a) / f"{pa}.json").read_text(encoding="utf-8"))
        doc_b = json.loads((Path(labels_b) / f"{pb}.json").read_text(encoding="utf-8"))
        m = recipe_metrics(doc_a, doc_b)
        rows = disagreements(doc_a, doc_b, m["alignment"])
        c = Counter(r["category"] for r in rows)
        cats.update(c)
        per.append({"pair": f"pair_{n:02d}", **_numbers(m), "disagreements": dict(sorted(c.items()))})
    mean = {k: (round(sum(p[k] for p in per if p[k] is not None) / max(1, sum(p[k] is not None for p in per)), 4)
                if any(p[k] is not None for p in per) else None) for k in METRICS}
    report = {"record": "STEP19_P1_AGREEMENT_COUNTS", "status": "AI_ENGINEERING_SCORE_COUNTS_ONLY",
              "label_basis": LABEL_BASIS, "counts_as_human_gate": False, "contains_ids": False, "contains_text": False,
              "pairs": len(per), "replay_ok_pairs": sum(p["replay_ok"] for p in per), "mean": mean,
              "disagreement_categories": dict(sorted(cats.items())), "per_pair": per}
    D.assert_counts_only(report)
    return report
