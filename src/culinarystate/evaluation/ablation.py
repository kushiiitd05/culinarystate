"""One-at-a-time ablation driver for the D5 benchmark (S178 lane H1H3H; board T8-C21-R2). AI_DRAFTED, DRAFT.

SSOT §245.13 lists nine modules to remove one at a time. The board asks for the cheap subset on the frozen set:
state conditioning, evidence compatibility, claim enforcement and the OOD gate; every other row is NOT_RUN with its
reason (acceptance: "ablation table (SSOT §245.13 subset, rest NOT_RUN)"). The ablation table is EXPLORATORY: the
prereg names no ablation, there is no alpha and no decision rule, and no ablation result may change a module or a
threshold (it is computed after the freeze, once).

The driver is generic. ``system(row, disabled)`` returns a run record (``d5_scoring.RUN_RECORD_FIELDS``) for one
benchmark row with the named components switched off; the D5 runner (T8-C15-R1) supplies the real one, wiring the
toggles to the pipeline (state conditioning -> ``pipeline.answer(use_state=False)``, OOD gate -> no support index,
claim enforcement -> the un-enforced B5F text, evidence compatibility -> retrieval without the compatibility term).
A precomputed set of records per configuration can be scored instead (``table_from_records``).
"""
from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

from culinarystate.evaluation import d5_scoring as DS
from culinarystate.evaluation import h3_independent as H3
from culinarystate.evaluation.d4_metrics import cp, question_error
from culinarystate.evaluation.paired_stats import mcnemar_exact

VERSION = "ablation@0.1"
FULL = "FULL"
CHEAP = ("state_conditioning", "evidence_compatibility", "claim_enforcement", "ood_gate")
COMPONENTS_245_13: tuple[dict[str, str], ...] = (
    {"ssot": "state reconstruction", "toggle": "state_conditioning", "status": "CHEAP_RUN"},
    {"ssot": "quantity grounding", "toggle": "", "status": "NOT_RUN",
     "reason": "no quantity-grounding switch in the D5 answer path"},
    {"ssot": "structured retrieval", "toggle": "", "status": "NOT_RUN", "reason": "B3 (structured metadata RAG) is not built"},
    {"ssot": "evidence compatibility", "toggle": "evidence_compatibility", "status": "CHEAP_RUN"},
    {"ssot": "conflict/lineage processing", "toggle": "", "status": "NOT_RUN",
     "reason": "no switch separates conflict / lineage handling from the packet builder"},
    {"ssot": "transition fallback", "toggle": "", "status": "NOT_RUN", "reason": "B6 (Level-15 transition fallback) is not built"},
    {"ssot": "uncertainty/OOD gate", "toggle": "ood_gate", "status": "CHEAP_RUN"},
    {"ssot": "feasibility filtering", "toggle": "", "status": "NOT_RUN", "reason": "not in the board's cheap subset"},
    {"ssot": "provenance/claim ledger", "toggle": "claim_enforcement", "status": "CHEAP_RUN"},
)


def configs(components: Sequence[str] = CHEAP) -> list[tuple[str, frozenset[str]]]:
    unknown = sorted(set(components) - set(CHEAP))
    if unknown:
        raise ValueError(f"unknown ablation component(s): {unknown}")
    return [(FULL, frozenset())] + [(c, frozenset({c})) for c in components]


def run_ablations(rows: Sequence[Mapping[str, Any]], system: Callable[[Mapping[str, Any], frozenset[str]], Mapping[str, Any]],
                  *, components: Sequence[str] = CHEAP) -> dict[str, dict[str, dict]]:
    """``config -> qid -> record`` for the P and C questions (one call per question and configuration)."""
    sel = DS.by_block(rows, DS.H3_BLOCKS)
    out: dict[str, dict[str, dict]] = {}
    for name, off in configs(components):
        out[name] = {}
        for r in sel:
            rec = dict(system(r, off))
            rec.setdefault("qid", r["qid"])
            rec["config"] = name
            out[name][r["qid"]] = rec
    return out


def _metrics(rows, recs: Mapping[str, Mapping[str, Any]], evd, relatives) -> tuple[dict, dict[str, int]]:
    sel = DS.by_block(rows, DS.H3_BLOCKS)
    scored = DS.score_rung(sel, recs, evd, relatives, blocks=DS.H3_BLOCKS)
    modes = {r["qid"]: str(r.get("gold_mode")) for r in sel}
    s = H3.summarize_rung(scored, modes)
    err = {r["qid"]: question_error(r, scored[r["qid"]]) for r in sel if r["qid"] in scored}
    return ({"n_questions": s["n_questions"], "n_numeric_claims": s["n_numeric_claims"], "ucr": s["ucr"],
             "coverage_answerable": s["coverage_answerable"], "false_abstention_answerable": s["false_abstention_answerable"],
             "abstention_on_abstain_gold": s["abstention_on_abstain_gold"], "selective_risk": s["selective_risk"],
             "error_rate_E1": cp(sum(err.values()), len(err))}, err)


def table_from_records(rows: Sequence[Mapping[str, Any]], by_config: Mapping[str, Mapping[str, Mapping[str, Any]]],
                       evd: Mapping[str, Mapping], relatives: Mapping[str, Sequence[str]] | None = None) -> dict:
    """Ablation table: the §245.13 rows (CHEAP_RUN rows scored, the others NOT_RUN), each scored like FULL, with the
    paired per-question E1 error discordance against FULL and its exact two-sided McNemar p (descriptive only)."""
    if FULL not in by_config:
        raise ValueError("the FULL configuration is required")
    full, full_err = _metrics(rows, by_config[FULL], evd, relatives)
    table = []
    for comp in COMPONENTS_245_13:
        row: dict[str, Any] = {"ssot_245_13": comp["ssot"], "toggle": comp["toggle"] or None}
        if comp["status"] != "CHEAP_RUN":
            row.update({"status": "NOT_RUN", "reason": comp["reason"]})
        elif comp["toggle"] not in by_config:
            row.update({"status": "NOT_RUN", "reason": "no records for this configuration"})
        else:
            m, err = _metrics(rows, by_config[comp["toggle"]], evd, relatives)
            q = sorted(set(err) & set(full_err))
            b = sum(full_err[x] == 0 and err[x] == 1 for x in q)          # removing the module adds an error
            c = sum(full_err[x] == 1 and err[x] == 0 for x in q)          # removing it removes an error
            row.update({"status": "RUN", "metrics": m,
                        "delta_vs_full": {"ucr": None if m["ucr"] is None or full["ucr"] is None else round(m["ucr"] - full["ucr"], 4),
                                          "error_rate_E1": None if m["error_rate_E1"]["rate"] is None or full["error_rate_E1"]["rate"] is None
                                          else round(m["error_rate_E1"]["rate"] - full["error_rate_E1"]["rate"], 4)},
                        "paired_E1": {"n": len(q), "errors_added": b, "errors_removed": c,
                                      "p_exact_two_sided_descriptive": mcnemar_exact(b, c)}})
        table.append(row)
    return {"version": VERSION, **DS.tag("ablation_table"), "full": full, "table": table,
            "reading": "descriptive; no alpha, no decision rule, no multiplicity control; no module is kept or "
                       "dropped on this table without a dated amendment"}
