"""Prompts for the baseline ladder (SSOT §245.12): B0 LLM-only, B2 hybrid RAG, B5 packet + decision constrained.

The B5 prompt carries the decided mode, the precision cap (§242.7) and the packet's disallowed claims; the model may
only state numbers that appear in the rendered evidence, each with its [EVD-…] id.
"""
from __future__ import annotations

from culinarystate.generation.verbalize import facts
from culinarystate.retrieval.retriever import EvidencePacket


def _rf(row: dict) -> str:
    rf = (row.get("derived") or {}).get("retention_factor") or {}
    scale = 0.01 if rf.get("unit") == "%" else 1.0
    if rf.get("status") == "MEASURED":
        return f"retention {round(rf['value'] * scale, 4):g}"
    if rf.get("status") == "CENSORED":
        return f"retention ≥ {round(((rf.get('censor') or {}).get('limit') or 0) * scale, 4):g} (censored)"
    return f"direction {(row.get('derived') or {}).get('direction', 'UNKNOWN')}"


def render_evidence(p: EvidencePacket, k: int = 8) -> str:
    rows = [h.row for h in (p.direct + p.near)][:k]
    if not rows:
        return "(no evidence rows)"
    return "\n".join(f"[{r['id']}] {r['matrix'].get('raw_name', '')} | {r['process'].get('raw_name', '')} | "
                     f"{r['target'].get('raw_name', '')} | {_rf(r)} | tier {r.get('tier')} | "
                     f"{'DIRECT' if r in [h.row for h in p.direct] else 'NEAR'}" for r in rows)


def b0_prompt(q: str) -> str:
    return ("You are a cooking assistant. Answer the user's question in at most 3 sentences. "
            "If you are not sure, say so.\n\nQuestion: " + q)


def b2_prompt(q: str, p: EvidencePacket) -> str:
    return ("Answer the cooking question in at most 3 sentences using the retrieved rows below. Cite row ids like "
            "[EVD-000123] after any number you use.\n\nRows:\n" + render_evidence(p) + "\n\nQuestion: " + q)


def b5_prompt(q: str, p: EvidencePacket, decision: dict, disallowed: list[str]) -> str:
    mode, prec = decision.get("mode"), decision.get("precision") or "QUALITATIVE"
    rules = [f"Decision mode: {mode}. Output precision cap: {prec} (QUANTITATIVE = numbers allowed; INTERVAL = give "
             "a range from the rows; QUALITATIVE = no numbers; REPORT_CONFLICT = state that sources disagree).",
             "Use ONLY numbers that appear in the evidence rows and cite the row id in brackets after each number.",
             "If a row is NEAR (not the exact food/process), say it is from a similar food or process.",
             "Do not claim causes; describe what the evidence reports."] + [f"Not allowed: {d}." for d in disallowed]
    if mode == "ABSTAIN":
        rules = ["The evidence is insufficient. Say so in one sentence and do not give any number."]
    if mode == "ASK":
        rules = [f"Ask the user one short clarifying question about: {', '.join(decision.get('ask_for') or [])}"
                 + (f" (options: {', '.join(decision.get('ask_options') or [])})." if decision.get("ask_options") else ".")]
    return ("You are CulinaryState, an evidence-grounded cooking assistant. Follow the rules exactly.\nRules:\n- "
            + "\n- ".join(rules) + "\n\nEvidence rows:\n" + render_evidence(p) + "\n\nQuestion: " + q
            + "\nAnswer in at most 3 sentences.")


def b5f_prompt(q: str, decision: dict, packets: dict[str, EvidencePacket]) -> str:
    """Per-route C16 prompt: the LLM only rephrases the verbaliser's fact lines (no raw rows, no second analysis)."""
    lines = facts(decision, packets)["lines"]
    return ("You are CulinaryState, an evidence-grounded cooking assistant. Rewrite the facts below as a short, "
            "friendly answer (at most 3 sentences) to the question.\nRules:\n- Do not add numbers, foods, causes, "
            "steps or advice that are not in the facts.\n- Keep each [EVD-…] id right after the number or statement "
            "it supports.\n- Keep words like 'similar foods', 'may', 'not ranked' and 'unknown' when the facts use "
            "them.\n\nFacts:\n" + "\n".join(lines) + "\n\nQuestion: " + q)
