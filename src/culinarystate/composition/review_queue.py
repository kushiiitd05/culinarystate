"""Mention-weighted human verification queue over the ING -> SR defaults registry (S179, port P9, packet Q44).

One row per registry term, ordered by corpus mentions (desc, then term), with the share of all food mentions and the
cumulative share, so a reviewer can verify the rows that carry most of the grams first and see how much of the corpus
a top-N sample audit covers. Kinds whose mapping changes composition (UK_US, DEFAULT_FORM, APPROX, AMBIGUOUS) are
marked for a check whatever their rank. The human columns start empty and every row stays UNVERIFIED: an AI-built
queue is not verification (D-071).
"""
from __future__ import annotations

from typing import Iterable, Mapping

KIND_CHECK = {"UK_US": "UK_US_DEFAULT_FORM_CHECK", "DEFAULT_FORM": "DEFAULT_FORM_CHECK", "APPROX": "APPROX_CHECK",
              "AMBIGUOUS": "AMBIGUOUS_CHECK"}
COLUMNS = ("rank", "term", "sr_description", "fdc_id", "kind", "mentions", "mention_share", "cumulative_share",
           "in_top_n", "review_reason", "verification", "human_decision", "human_corrected_fdc_id", "human_reviewer",
           "human_note")


def review_rows(registry: Iterable[Mapping[str, str]], mentions: Mapping[str, int], *, total_mentions: int,
                top_n: int = 100) -> list[dict]:
    """Queue rows; ``total_mentions`` counts every food mention in the corpus (registry terms or not)."""
    if total_mentions <= 0:
        raise ValueError("total_mentions must be positive")
    reg = sorted(registry, key=lambda r: (-mentions.get(r["term"], 0), r["term"]))
    out, cum = [], 0
    for rank, r in enumerate(reg, start=1):
        n = int(mentions.get(r["term"], 0))
        cum += n
        top = rank <= top_n
        reason = KIND_CHECK.get(r["kind"]) or ("TOP_MENTION" if top and n > 0 else "")
        out.append({"rank": rank, "term": r["term"], "sr_description": r["sr_description"], "fdc_id": r["fdc_id"],
                    "kind": r["kind"], "mentions": n, "mention_share": n / total_mentions,
                    "cumulative_share": cum / total_mentions, "in_top_n": top, "review_reason": reason,
                    "verification": "UNVERIFIED", "human_decision": "", "human_corrected_fdc_id": "",
                    "human_reviewer": "", "human_note": ""})
    return out
