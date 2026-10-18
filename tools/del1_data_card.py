#!/usr/bin/env python3
"""DEL-1 data card + acceptance check against the submitted proposal contract (plan T1 / AH7).

  /opt/anaconda3/bin/python tools/del1_data_card.py
Writes reports/DEL1_data_card.md. Every acceptance line is computed from the ledgers; nothing is asserted.
"""
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.eda.report import evidence_section  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

st = LedgerStore()
evd = [e for e in st.all_latest("EVD") if e["status"] == "ACTIVE"]
cond = {c["id"]: c for c in st.all_latest("COND")}
src = {s["id"]: s for s in st.all_latest("SRC")}
db_rows = [e for e in evd if e["tier"] == "E3"]
human_lit = [e for e in evd if e["tier"] in ("E1", "E2", "E4") and e["verification"]["status"] == "HUMAN_VERIFIED"]
has_src = sum(bool(e["source_id"]) for e in evd)
has_tier = sum(bool(e["tier"]) for e in evd)
has_cond = sum(bool(cond.get(e["process"].get("condition_id") or "", {}).get("completeness_mask")) for e in evd)
has_cens = sum(isinstance(e.get("censored"), bool) for e in evd)
ing_linked = sum(bool(e["matrix"].get("ingredient_id")) for e in evd)
proc_linked = sum(bool(e["process"].get("process_id")) for e in evd)
n = len(evd)
ev = evidence_section(st)


def ok(b):
    return "✅" if b else "❌"


fams = Counter(e["source_family_id"] for e in evd)
lines = [
    f"# DEL-1 Process-Effect Evidence Ledger — data card ({date.today().isoformat()})", "",
    "## Acceptance (proposal D1 / plan T1)", "", "| Clause | Required | Achieved | |", "|---|---|---|---|",
    f"| Public retention-database rows | ≥ 1,000 | {len(db_rows):,} | {ok(len(db_rows) >= 1000)} |",
    f"| Hand-verified literature rows (human) | ≥ 40 | {len(human_lit)} | {ok(len(human_lit) >= 40)} |",
    f"| Rows with source | 100% | {has_src / n:.1%} | {ok(has_src == n)} |",
    f"| Rows with evidence tier | 100% | {has_tier / n:.1%} | {ok(has_tier == n)} |",
    f"| Rows with condition status (completeness mask) | 100% | {has_cond / n:.1%} | {ok(has_cond == n)} |",
    f"| Rows with censoring flag | 100% | {has_cens / n:.1%} | {ok(has_cens == n)} |",
    f"| Names normalised to internal ING (AH2) | report | {ing_linked / n:.1%} | — |",
    f"| Process linked to PROC | report | {proc_linked / n:.1%} | — |",
    "| Names normalised to RecipeDB/FlavorDB | proposal | UNRESOLVED_EXTERNAL (API pending, AH2) | ⏳ |", "",
    "## Composition", "",
    *[f"- {f}: {c:,} rows" for f, c in fams.most_common()],
    f"- tiers: {ev.get('tier')}; origin: {ev.get('origin_type')}",
    f"- study lineage: {ev.get('study_lineage')}; independent groups: {ev.get('independent_groups')}",
    f"- censored rows: {ev.get('censored_rows'):,}; RF status: {ev.get('retention_factor_status')}",
    f"- direction: {ev.get('direction')}; basis: {ev.get('target_basis')}",
    f"- unique matrices {ev.get('unique_matrices')}, step sequences {ev.get('unique_step_sequences')}, "
    f"targets {ev.get('unique_targets')}, cells {ev.get('unique_cells'):,}; matrix×process density "
    f"{ev.get('matrix_process_density')}",
    f"- condition axes: { {k: v for k, v in (ev.get('condition_axes') or {}).items() if k in ('duration', 'temperature')} }",
    f"- conflict candidates (opposite directions across independent groups, same cell): {ev.get('conflict_candidates')}",
    "", "## Known limitations / bias", "",
    "- USDA R6: factors largely imputed; mixed %TR/%AR; rounded to 5%; 37% capped at 100 (censored); placeholder date.",
    "- Phenol-Explorer: RF includes a yield factor often borrowed from another food; per-publication design unknown.",
    "- Sources skew to Western foods and polyphenols/vitamins/minerals; volatile/flavour compounds largely absent.",
    "- 109 processes used in recipes have no state-change evidence at all (process registry v1).",
    "- No row is human-verified yet: literature verification queue is the human task (E4 needs HUMAN_VERIFIED).",
    "", "## Sources", "", *[f"- {s['id']}: {s['title']} — licence: {s['licence']} ({s['storage_rule']})"
                            for s in src.values() if s["id"] in {e['source_id'] for e in evd}],
]
(ROOT / "reports" / "DEL1_data_card.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines[:16]))
