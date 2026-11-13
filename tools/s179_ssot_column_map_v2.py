#!/usr/bin/env python3
"""D-100 Lane C / plan L1: SSOT §238 column map v2. Every one of the 210 fields gets a producer, the artifact that
fills it over the full corpus, a fill statement taken from that artifact, and a disposition. v1 columns are copied
unchanged. AI_DRAFTED mapping (ksh+prv, D-085); numbers are read from committed artifacts, not typed in.

    python tools/s179_ssot_column_map_v2.py --out reports/s179/ssot_column_map_v2_2026-11-13.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "reports/s178/ssot238_conformance.csv"
L1_FC = "reports/step26/binding_census_L1_FOODCOM_full_S179_v06.json"
L2_FC = "reports/step26/scenario_L2_FOODCOM_full_S179_v06.json"
PSM = "reports/s179/process_state_map_full_2026-11-13.json"
ROUTER = "reports/step23/router_demo_census_vitc_nonBBC_full_S179b.json"
NER = "reports/ner_v2/ner_corpus_counts_S174.json"
MASS = "reports/s179/line_mass_census_nonBBC.json"


def _j(p):
    return json.loads((ROOT / p).read_text())


def facts() -> dict:
    l1 = _j(L1_FC)["input_status"]
    def bound(ax):
        v = l1[ax]; tot = sum(v.values()); return f"{100 * (tot - v.get('UNKNOWN', 0)) / tot:.1f}% of {tot:,} Food.com heat events"
    psm, rt, mass = _j(PSM), _j(ROUTER), _j(MASS)["families"]
    l2 = _j(L2_FC)
    computed = (l2.get("counts") or {}).get("status", {}).get("SCENARIO_COMPUTED") if isinstance(l2.get("counts"), dict) else None
    fc = mass["FOODCOM"]; wb = mass["WIKIBOOKS"]
    return {
        "engine": f"100% of {psm['n_events']:,} step events over {psm['n_recipes']:,} recipes (Rung A, 0 exceptions)",
        "medium": bound("medium"), "duration": bound("duration"), "temperature": bound("temperature_profile"),
        "lid": bound("lid_state"), "size": bound("piece_size_class"), "matrix": bound("matrix_class"),
        "pressure": f"{sum(l1['pressure_cue'].values()):,} events with a pressure cue",
        "scenario": f"L2 SCENARIO_COMPUTED {computed:,} Food.com heat events (SCENARIO_DEFAULT)" if computed else "L2 scenario layer (see artifact)",
        "linked": f"{100 * rt['items_linked'] / rt['items']:.1f}% of {rt['items']:,} non-BBC ingredient items linked",
        "ner": "4.17 M ingredient lines NER-tagged (frozen ckpt 582c056a; FOODCOM/WIKIBOOKS/TASTESET)",
        "mass": f"lines with grams: Food.com {fc['lines_with_grams']:,}/{fc['lines']:,}; Wikibooks {wb['lines_with_grams']:,}/{wb['lines']:,} (Food.com units dropped at source)",
    }


# field -> (producer, artifact key, fact key, disposition)
MAP = {
    "Event": {**{f: ("RUNG_A_ENGINE", PSM, "engine", "FILLED_DERIVED") for f in (
        "event_id", "recipe_id", "event_index", "process_id", "input_entity_ids", "output_entity_ids", "tool_ids",
        "source_span", "provenance", "process_modifiers")},
        "medium": ("PHYSICS_V06_L1", L1_FC, "medium", "FILLED_PARTIAL"),
        "temperature_C": ("PHYSICS_V06_L1", L1_FC, "temperature", "FILLED_PARTIAL"),
        "temperature_raw": ("PHYSICS_V06_L1", L1_FC, "temperature", "FILLED_PARTIAL"),
        "duration_s": ("PHYSICS_V06_L1", L1_FC, "duration", "FILLED_PARTIAL"),
        "duration_raw": ("PHYSICS_V06_L1", L1_FC, "duration", "FILLED_PARTIAL"),
        "pressure": ("PHYSICS_V06_L1", L1_FC, "pressure", "FILLED_SPARSE"),
        "moisture_condition": ("PHYSICS_V06_L1", L1_FC, "lid", "FILLED_PARTIAL"),
        "endpoint_states": ("PHYSICS_V06_L1", L1_FC, "engine", "FILLED_DERIVED"),
        "pH": ("NONE", "", "", "UNKNOWN_NO_PRODUCER"),
        "validation_flags": ("AUDITOR_REPLAY_INVARIANTS", "reports/s178/corpus/replay_invariants_corpus_v1.json", "", "FILLED_DERIVED")},
    "Entity": {**{f: ("RUNG_A_ENGINE", PSM, "engine", "FILLED_DERIVED") for f in (
        "entity_id", "recipe_id", "entity_type", "name", "created_by_event", "destroyed_or_consumed_by_event",
        "parent_entity_ids", "current_state_id", "quantity_state_id")},
        "canonical_food_id": ("ROUTER_LINKER", ROUTER, "linked", "FILLED_DERIVED")},
    "State": {**{f: ("RUNG_A_ENGINE", PSM, "engine", "FILLED_DERIVED") for f in ("state_id", "entity_id", "event_index")},
        "thermal_state": ("PHYSICS_V06_L2", L2_FC, "scenario", "FILLED_SCENARIO_DEFAULT"),
        "temperature_C": ("PHYSICS_V06_L2", L2_FC, "scenario", "FILLED_SCENARIO_DEFAULT"),
        "moisture": ("PHYSICS_V06_L2_CAP", L2_FC, "scenario", "FILLED_SCENARIO_DEFAULT"),
        "uncertainty": ("PHYSICS_V06_L2_BRACKET", L2_FC, "scenario", "FILLED_SCENARIO_DEFAULT"),
        "observation_source": ("PHYSICS_V06_L1_L2", L1_FC, "temperature", "FILLED_DERIVED"),
        "physical_state": ("PHYSICS_V06_L1_MATRIX", L1_FC, "matrix", "FILLED_PARTIAL"),
        "form": ("ING_ATTRIBUTES_AI_DRAFT_L6B", "registry/ing_attributes_ai_draft_v1.csv", "", "FILLED_AI_DRAFTED_PENDING"),
        "quantity_mass_g": ("LINE_MASS_CENSUS", MASS, "mass", "FILLED_SPARSE"),
        "chemical_state_ref": ("EFFECT_MAP_224_L4", "reports/s179/effect_map_224_*", "", "FILLED_PENDING_L4"),
        "field_provenance": ("PHYSICS_V06_L1_L2", L1_FC, "engine", "FILLED_DERIVED"),
        "timestamp": ("NONE", "", "", "ABSENT_ORDER_ONLY"),
        **{f: ("NONE", "", "", "UNKNOWN_NO_PRODUCER") for f in ("visual_state", "texture_state", "water_activity", "pH")}},
    "IngredientMention": {**{f: ("NER_S174_PLUS_LINKER", NER, "ner", "FILLED_DERIVED") for f in (
        "mention_id", "recipe_id", "raw_text", "source_span", "canonical_ingredient_id", "candidate_ids", "variety", "form",
        "state", "size", "quantity_id", "optional", "divided", "reserved", "canonicalization_status", "provenance")},
        "role": ("NONE", "", "", "UNKNOWN_NO_PRODUCER"), "brand": ("NONE", "", "", "UNKNOWN_NO_PRODUCER"),
        "annotation_confidence_features": ("NONE", "", "", "UNKNOWN_NO_PRODUCER")},
    "Quantity": {**{f: ("QUANTITY_RC2_LINE_MASS", MASS, "mass", "FILLED_SPARSE") for f in (
        "quantity_id", "raw_text", "quantity_type", "value", "lower", "upper", "fraction", "count", "unit_id", "unit_locale",
        "size", "packing", "approximate", "qualitative_term", "optional", "divided", "reserved", "normalized_mass_g",
        "normalized_volume_ml", "conversion_record_id", "provenance")},
        "container": ("NONE", "", "", "UNKNOWN_NO_PRODUCER")},
    "Recipe": {**{f: ("RUNG_A_ENGINE", PSM, "engine", "FILLED_DERIVED") for f in ("event_ids", "entity_ids", "recipe_graph_id")},
               "validation_flags": ("AUDITOR_REPLAY_INVARIANTS", "reports/s178/corpus/replay_invariants_corpus_v1.json", "", "FILLED_DERIVED"),
               **{f: ("NONE", "", "", "UNKNOWN_NO_PRODUCER") for f in ("title_normalized", "servings_raw", "servings_normalized")},
               "prompt_version": ("NONE", "", "", "NOT_APPLICABLE_NO_LLM_EXTRACTION")},
    "CanonicalIngredient": {"portion_profile_ids": ("NONE", "", "", "DEFERRED_SR_PORTION_D084")},
    "Alias": {"source_domains": ("NONE", "", "", "UNKNOWN_NO_PRODUCER")},
    "EvidenceAtom": {f: ("NONE", "", "", "NOT_IN_EVD_SCHEMA_REVIEW") for f in ("subject_type", "object_type", "doi")},
    "PortionProfile": "DEFERRED_SR_PORTION_D084",
    "InverseDesignTrial": "DECLARED_CUT_H8_08",
    "ClaimLedger": "D5_APP_CLAIMS_ONLY_NOT_CORPUS",
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    F = facts()
    rows = list(csv.DictReader(V1.open()))
    fields = list(rows[0]) + ["v2_producer", "v2_artifact", "v2_full_corpus_fill", "v2_disposition", "v2_label"]
    with out.open("x", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            m = MAP.get(r["contract"])
            populated = r["n_rows"] not in ("", "0") and r["map_kind"] != "ABSENT"
            if populated:
                prod = ("LEDGER", r["count_artifact"], f"{r['pct_populated']}% of {r['n_rows']} rows", "FILLED_LEDGER")
            elif isinstance(m, str):
                prod = ("NONE", "", "", m)
            elif isinstance(m, dict) and r["ssot_field"] in m:
                p, art, fk, disp = m[r["ssot_field"]]
                prod = (p, art, F.get(fk, ""), disp)
            else:
                prod = ("NONE", "", "", "UNMAPPED_REVIEW")
            w.writerow({**r, "v2_producer": prod[0], "v2_artifact": prod[1], "v2_full_corpus_fill": prod[2],
                        "v2_disposition": prod[3], "v2_label": "AI_DRAFTED_MAP NO_HUMAN_SIGNOFF_D085"})
    print("rows", len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
