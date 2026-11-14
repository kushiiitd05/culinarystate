"""Draft MECH entries (MECH v1.1 schema) for the mechanism screen (S178 lane MECH, T5-C01-R1 / R2). AI_DRAFTED.

Builds ``registry/mech_entries_draft_v1.jsonl`` deterministically from ``registry/mechanism_seed_roster_draft_v1.csv``
(32 keys) plus the specifications below. One JSONL line per entry::

    {"record": "MECH_ENTRY_DRAFT", ..., "provenance_class": "AI_DRAFTED", "evidence_status": "UNSOURCED",
     "screen_subset": true, "screen_binding": {...}, "mech": {<a MECH v1.1 entry>}}

The ``mech`` object validates against ``registry/schemas/MECH.draft_v1_1.schema.json`` unchanged. The lane label
``AI_DRAFTED`` is not a value of the v1.1 ``provenance_class`` enum, so it is carried by the envelope and the entry says
``provenance_class: INFERRED_LLM`` + ``ai_drafted: true`` (the v1.1 spelling of the same fact; a human decides whether the
enum gains AI_DRAFTED). Ids are a DRAFT block ``MECH-9000nn`` that is NOT minted (minting and any ledger append are
orchestrator / human work after review; nothing here writes ``ledgers/``).

Evidence: this lane opened no source, so every entry has ``evidence_refs: []`` and ``evidence_status: UNSOURCED`` (not
counted toward G21.4). ``window_refs`` name rows of ``registry/mechanism_condition_windows_draft_v1.csv`` (QUALITATIVE_ONLY,
opened by the S176 L-SRC lane, not re-opened here); they are context for a reviewer, never evidence ids. No entry holds a
number other than the record ``version`` (G21.8; every interval bound is NOT_REPORTED).

Screen subset: 15 entries carry preconditions and a ``screen_binding`` (item key -> evaluator of
``mechanism.mech_inputs``) that ``mechanism.screen`` consumes. The other 17 roster keys are ``gates_unknown: true`` stubs
(authored structure only: kind, family, targets, links), so that G21.2 coverage can be checked; the screen does not run them.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[3]
ROSTER_PATH = ROOT / "registry" / "mechanism_seed_roster_draft_v1.csv"
WINDOWS_PATH = ROOT / "registry" / "mechanism_condition_windows_draft_v1.csv"
OUT_PATH = ROOT / "registry" / "mech_entries_draft_v1.jsonl"
DRAFT_REGISTRY = "mech-entries-draft-v1"
BUILDER_VERSION = "mech-entries-builder-0.1.0-draft"
SCHEMA_VERSION = "1.1.0-draft"
CREATED_AT = "2026-11-09T00:00:00+00:00"          # fixed: the file is reproducible byte for byte
CREATED_BY = "ai-agent-S178-lane-MECH"
ID_BLOCK = 900000
WINDOW_STATUS = "QUALITATIVE_ONLY_ROWS_OPENED_BY_S176_L-SRC_NOT_REOPENED_BY_THIS_LANE"
AF_NR = {"status": "NOT_REPORTED", "text": None, "token": None, "token_status": "NOT_APPLICABLE"}


# ----------------------------------------------------------------------------- small builders (structure only)
def state(key: str, label: str | None = None, *, svar: str | None = None) -> dict[str, Any]:
    if svar and svar.startswith("SVAR-FUT-"):
        return {"ref_status": "SVAR_FUTURE", "svar_id": svar, "state_key": None, "label_raw": label or svar}
    if svar:
        return {"ref_status": "SVAR_ACTIVE", "svar_id": svar, "state_key": None, "label_raw": label or svar}
    return {"ref_status": "PROPOSED_KEY", "svar_id": None, "state_key": key, "label_raw": label or key.replace("_", " ")}


def scope(kind: str = "UNKNOWN", inc: Iterable[str] = (), note: str | None = None) -> dict[str, Any]:
    return {"scope_kind": kind, "included": [{"ref_type": "CLASS_LABEL", "ref": r, "label_raw": r} for r in inc],
            "excluded": [], "unlisted_verdict": "UNKNOWN", "note_raw": note}


def bound_nr() -> dict[str, Any]:
    return {"status": "NOT_REPORTED", "value": None, "inclusive": None}


def precondition(key: str, state_key: str, op: str, values: Sequence[str], label: str | None = None,
                 svar: str | None = None) -> dict[str, Any]:
    return {"precondition_key": key, "state_ref": state(state_key, label, svar=svar), "subject_entity": None,
            "predicate": {"operator": op, "values": list(values)}, "missing_input_verdict": "UNKNOWN",
            "evidence_ids": [], "status": "CANDIDATE"}


def temp_gate(key: str, cv: str, gtype: str, rationale: str, matrix: dict[str, Any], modulates: str = "NOT_APPLICABLE"
              ) -> dict[str, Any]:
    """A temperature gate with both bounds NOT_REPORTED (no number in MECH)."""
    return {"gate_key": key, "gate_type": gtype, "cv_id": cv, "location": "NOT_APPLICABLE", "basis": "NOT_APPLICABLE",
            "clock": "NOT_APPLICABLE", "domain_kind": "NUMERIC_INTERVAL",
            "interval": {"unit": "K", "min": bound_nr(), "max": bound_nr()}, "categories": None,
            "modulates": modulates if gtype == "MODULATING" else "NOT_APPLICABLE", "independence_assumed": "UNKNOWN",
            "matrix_scope": matrix, "missing_input_verdict": "UNKNOWN", "evidence_ids": [], "status": "CANDIDATE",
            "rationale_raw": rationale}


def ph_gate_modulating(key: str, rationale: str, matrix: dict[str, Any], location: str = "TISSUE") -> dict[str, Any]:
    return {"gate_key": key, "gate_type": "MODULATING", "cv_id": "CV-013", "location": location, "basis": "NOT_APPLICABLE",
            "clock": "NOT_APPLICABLE", "domain_kind": "NUMERIC_INTERVAL",
            "interval": {"unit": "pH", "min": bound_nr(), "max": bound_nr()}, "categories": None, "modulates": "RATE",
            "independence_assumed": "UNKNOWN", "matrix_scope": matrix, "missing_input_verdict": "UNKNOWN",
            "evidence_ids": [], "status": "CANDIDATE", "rationale_raw": rationale}


def inhibitor_state(key: str, agent: str, state_key: str, label: str, role: str = "INHIBITOR") -> dict[str, Any]:
    return {"inhibitor_key": key, "role": role, "agent_or_condition_raw": agent,
            "sbo_role": "SBO:0000020" if role in ("INHIBITOR", "MITIGATOR") else "SBO:0000013",
            "extent": "UNKNOWN" if role in ("INHIBITOR", "MITIGATOR") else "NOT_APPLICABLE",
            "evaluated_via": {"mode": "STATE_PREDICATE", "gate_key": None, "state_ref": state(state_key, label),
                              "predicate": {"operator": "PRESENT", "values": []}},
            "missing_input_verdict": "UNKNOWN", "evidence_ids": [], "status": "CANDIDATE"}


def target(key: str, tstate: dict[str, Any], role: str, effect: str, dirs: Sequence[str], comp: str, shape: str,
           cls: str) -> dict[str, Any]:
    return {"target_key": key, "target": tstate, "target_role": role, "target_class": cls, "analyte_form": dict(AF_NR),
            "compartment": comp, "effect_type": effect, "allowed_directions": list(dirs), "trajectory_shape": shape,
            "evidence_ids": [], "status": "CANDIDATE"}


def participant(role: str, label: str, sbo: str) -> dict[str, Any]:
    return {"role_label": role, "entity": {"ref_type": "CLASS_LABEL", "ref": label, "label_raw": label}, "sbo_role": sbo}


def history(state_key: str, role: str, label: str | None = None) -> dict[str, Any]:
    return {"state_ref": state(state_key, label), "role": role, "evidence_ids": [], "status": "CANDIDATE"}


def enzyme(label: str, ec: str | None) -> dict[str, Any]:
    x = None if ec is None else {"curie": ec, "relation": "EXACT", "match_basis": "AI_PROPOSED", "xref_status": "PROPOSED",
                                 "verification_status": "UNVERIFIED", "verified_by": None, "collision_note": None}
    return {"label_raw": label, "ec": x, "go_mf": None, "rhea": None}


def competes(key: str, tstate: dict[str, Any], relation: str) -> dict[str, Any]:
    return {"mechanism_key": key, "shared_target": tstate, "relation": relation, "evidence_ids": [], "status": "CANDIDATE"}


def consecutive(key: str, order: str, shared: dict[str, Any] | None) -> dict[str, Any]:
    return {"mechanism_key": key, "order": order, "shared_species": shared, "evidence_ids": [], "status": "CANDIDATE"}


# ----------------------------------------------------------------------------- shared states
AA = state("", "Vitamin C, total ascorbic acid content", svar="SVAR-000009")
DHA = state("dehydroascorbic_acid_content", "dehydroascorbic acid (DHA) content")
CHL = state("chlorophyll_content", "chlorophyll a + b content")
BROWN = state("", "browning index", svar="SVAR-FUT-009")
MOIST = state("", "moisture content", svar="SVAR-FUT-001")
SULFENIC = state("propenyl_sulfenic_acid", "1-propenyl sulfenic acid (alliinase product in onion)")
GLUC = state("glucosinolate_content", "glucosinolate content")
STARCH_STATE = state("starch_state", "starch state (NATIVE / PARTIAL / GELATINISED / RETROGRADING)")
PROTEIN_STATE = state("protein_state", "protein state (NATIVE / DENATURED / AGGREGATED_GEL / ACID_DENATURED)")

CUT_STATES = ("CUT", "CRUSHED_PUREED")
TBOIL_RATIONALE = ("Onset window of a transition with no universal switch (SSOT 144.1); bounds are NOT reported in MECH "
                   "(QUALITATIVE_ONLY windows {w}). Screen witness (PROPOSED, needs H4): the food surface held at the "
                   "boiling point of water at 1 atm{water} lies above every onset those windows report, so the gate is "
                   "TRUE there; otherwise UNKNOWN. The gate is never FALSE (no bound is reported).")

# ----------------------------------------------------------------------------- the 15 screen entries
# Each spec: member_scope (taxon class whose raw-form members are evaluated one by one, or None), pre / gates / inh with
# their evaluator bindings, targets, links, history, entry matrix scope, window refs, verdict flags.
FRESH = "raw tissue (identity of record says raw / fresh)"

SCREEN_SPECS: dict[str, dict[str, Any]] = {
    "ALLIINASE_ALLIIN_CLEAVAGE": dict(
        member_scope="ALLIUM_FRESH",
        participants=[("substrate", "S-alk(en)yl-L-cysteine sulfoxides (alliin class)", "SBO:0000010"),
                      ("enzyme", "alliinase", "SBO:0000013"),
                      ("product", "alk(en)yl sulfenic acids -> thiosulfinates", "SBO:0000011")],
        enzyme=("alliinase (alliin lyase)", "EC:4.4.1.4"),
        pre=[("PRE01", "allium_tissue_presence", "IS", ["PRESENT"], "taxon_present", {"cls": "ALLIUM_FRESH"},
              "raw Allium tissue in the lot (holds substrate and enzyme in separate compartments)"),
             ("PRE02", "cell_integrity", "IN", list(CUT_STATES), "cell_disrupted", {},
              "cells disrupted (cut / crushed): substrate meets enzyme"),
             ("PRE03", "enzyme_state_alliinase", "IS", ["ACTIVE"], "enzyme_active", {},
              "enzyme not thermally inactivated before or at the start of the event")],
        gates=[ph_gate_modulating("CG01", "Low pH reduces alliinase activity (window MCW-0120 reports an inhibiting "
                                  "pH limit, QUALITATIVE_ONLY); encoded MODULATING because the lot pH is never a "
                                  "number here (SSOT v16 DRAFT 285.8: no mixture pH)", scope("FOOD_CLASS", ["garlic"]))],
        inh=[("INH01", "a member other than the Allium tissue or an inert fat (acidulant, salt, other food) may "
                       "inhibit or dilute the enzyme", "inhibiting_agent_member", "a non-reactant, non-inert member "
                       "is present", "inhibiting_agent_absent", {"cls": "ALLIUM_FRESH"})],
        targets=[target("TGT01", state("alliin_content", "S-alk(en)yl cysteine sulfoxide content"), "SUBSTRATE",
                        "CONSUMED", ["DECREASE"], "TISSUE", "MONOTONIC", "SPECIES"),
                 target("TGT02", state("thiosulfinate_content", "thiosulfinate content"), "PRODUCT", "FORMED",
                        ["INCREASE", "DECREASE"], "TISSUE", "PEAK_THEN_DECLINE", "SPECIES")],
        consecutive=[("ONION_LACHRYMATORY_FACTOR_SYNTHESIS", "THIS_PRECEDES_OTHER", SULFENIC)],
        history=[("cell_integrity", "INPUT_REQUIRED"), ("enzyme_state_alliinase", "ACTIVE_UNTIL_STATE_CHANGE"),
                 ("time_since_disruption", "MODULATES_DIRECTION_OR_SELECTIVITY")],
        matrix=("FOOD_CLASS", ["Allium vegetables, " + FRESH]),
        windows=["MCW-0117", "MCW-0118", "MCW-0120"], flags=[]),
    "ONION_LACHRYMATORY_FACTOR_SYNTHESIS": dict(
        member_scope="ONION_FRESH",
        participants=[("substrate", "1-propenyl sulfenic acid", "SBO:0000010"),
                      ("enzyme", "lachrymatory-factor synthase", "SBO:0000013"),
                      ("product", "propanethial S-oxide (lachrymatory factor)", "SBO:0000011")],
        enzyme=("lachrymatory-factor synthase", None),
        pre=[("PRE01", "onion_tissue_presence", "IS", ["PRESENT"], "taxon_present", {"cls": "ONION_FRESH"},
              "raw onion-type Allium tissue in the lot"),
             ("PRE02", "cell_integrity", "IN", list(CUT_STATES), "cell_disrupted", {}, "cells disrupted"),
             ("PRE03", "enzyme_state_lachrymatory_factor_synthase", "IS", ["ACTIVE"], "enzyme_active", {},
              "enzymes not thermally inactivated")],
        gates=[],
        inh=[("INH01", "a non-reactant, non-inert member may inhibit or dilute the enzyme system",
              "inhibiting_agent_member", "a non-reactant, non-inert member is present", "inhibiting_agent_absent",
              {"cls": "ONION_FRESH"})],
        targets=[target("TGT01", state("lachrymatory_factor_content", "propanethial S-oxide content"), "PRODUCT",
                        "FORMED", ["INCREASE", "DECREASE"], "TISSUE", "PEAK_THEN_DECLINE", "SPECIES")],
        consecutive=[("ALLIINASE_ALLIIN_CLEAVAGE", "OTHER_PRECEDES_THIS", SULFENIC)],
        history=[("cell_integrity", "INPUT_REQUIRED")],
        matrix=("FOOD_CLASS", ["onion-type Allium (onion, shallot, spring onion), " + FRESH]),
        windows=[], flags=[]),
    "MYROSINASE_GLUCOSINOLATE_HYDROLYSIS": dict(
        member_scope="BRASSICA_FRESH",
        participants=[("substrate", "glucosinolates", "SBO:0000010"), ("enzyme", "myrosinase", "SBO:0000013"),
                      ("product", "isothiocyanates / nitriles / thiocyanates", "SBO:0000011")],
        enzyme=("myrosinase (thioglucoside glucohydrolase)", "EC:3.2.1.147"),
        pre=[("PRE01", "brassicaceae_tissue_presence", "IS", ["PRESENT"], "taxon_present", {"cls": "BRASSICA_FRESH"},
              "raw Brassicaceae tissue in the lot (holds glucosinolates, myrosinase and tissue water)"),
             ("PRE02", "cell_integrity", "IN", list(CUT_STATES), "cell_disrupted", {}, "cells disrupted"),
             ("PRE03", "enzyme_state_myrosinase", "IS", ["ACTIVE"], "enzyme_active", {},
              "enzyme not thermally inactivated")],
        gates=[],
        inh=[("INH01", "a non-reactant, non-inert member may inhibit or redirect the hydrolysis",
              "inhibiting_agent_member", "a non-reactant, non-inert member is present", "inhibiting_agent_absent",
              {"cls": "BRASSICA_FRESH"})],
        targets=[target("TGT01", GLUC, "SUBSTRATE", "CONSUMED", ["DECREASE"], "TISSUE", "MONOTONIC", "SPECIES"),
                 target("TGT02", state("isothiocyanate_content", "isothiocyanate content"), "PRODUCT", "FORMED",
                        ["INCREASE", "DECREASE"], "TISSUE", "PEAK_THEN_DECLINE", "SPECIES")],
        history=[("cell_integrity", "INPUT_REQUIRED"), ("enzyme_state_myrosinase", "ACTIVE_UNTIL_STATE_CHANGE")],
        matrix=("FOOD_CLASS", ["Brassicaceae vegetables, " + FRESH]),
        windows=["MCW-0123", "MCW-0129"], flags=[]),
    "PPO_ENZYMATIC_BROWNING": dict(
        member_scope="PPO_FRESH",
        participants=[("substrate", "o-diphenols (phenolic substrates)", "SBO:0000010"),
                      ("co-substrate", "molecular oxygen", "SBO:0000010"),
                      ("enzyme", "polyphenol oxidase", "SBO:0000013"), ("product", "o-quinones -> melanins", "SBO:0000011")],
        enzyme=("polyphenol oxidase (catechol oxidase)", "EC:1.10.3.1"),
        pre=[("PRE01", "ppo_tissue_presence", "IS", ["PRESENT"], "taxon_present", {"cls": "PPO_FRESH"},
              "raw tissue of a food in the PPO-browning class"),
             ("PRE02", "cell_integrity", "IN", list(CUT_STATES), "cell_disrupted", {},
              "cells disrupted (window MCW-0115, UNVERIFIED)"),
             ("PRE03", "enzyme_state_ppo", "IS", ["ACTIVE"], "enzyme_active", {}, "enzyme not thermally inactivated"),
             ("PRE04", "oxygen_exposure", "IN", ["LID_OFF", "AGITATED"], "oxygen_contact", {},
              "oxygen reaches the disrupted surface (co-substrate; windows MCW-0107)")],
        gates=[],
        inh=[("INH01", "acidulant, reductant (ascorbate), salt or sulfite member may inhibit PPO or reduce quinones",
              "inhibiting_agent_member", "a non-reactant, non-inert member is present", "inhibiting_agent_absent",
              {"cls": "PPO_FRESH"})],
        targets=[target("TGT01", BROWN, "UNKNOWN", "UNKNOWN_TRANSFORMATION", ["UNKNOWN"], "TISSUE", "UNKNOWN",
                        "OBSERVABLE")],
        history=[("cell_integrity", "INPUT_REQUIRED"), ("enzyme_state_ppo", "ACTIVE_UNTIL_STATE_CHANGE"),
                 ("oxygen_exposure", "INPUT_REQUIRED")],
        matrix=("FOOD_CLASS", ["PPO-browning fruit, vegetables and mushrooms, " + FRESH]),
        windows=["MCW-0107", "MCW-0110", "MCW-0111", "MCW-0115"], flags=[]),
    "MAILLARD_STRECKER_LUMPED": dict(
        member_scope=None,
        participants=[("reactant", "reducing carbonyl (reducing sugars)", "SBO:0000010"),
                      ("reactant", "amino compound (amino acids, peptides, proteins)", "SBO:0000010")],
        enzyme=None,
        pre=[("PRE01", "amino_source_presence", "IS", ["PRESENT"], "nutrient_present", {"key": "protein"},
              "an amino-group source is present (SR protein as the stand-in; SR zero for every member = absent)"),
             ("PRE02", "carbonyl_source_presence", "IS", ["PRESENT"], "carbonyl_source", {},
              "a reducing-carbonyl source is present (SR total sugars as the stand-in; never absent from SR: "
              "trace sugars below SR reporting still react)")],
        gates=[temp_gate("CG01", "CV-007", "MODULATING", "Temperature changes rate and product spectrum; no switch "
                         "(SSOT 144.1; wet cooking can still support some Maillard chemistry)",
                         scope("GENERIC_MECHANISM"), "RATE")],
        inh=[],
        targets=[target("TGT01", BROWN, "UNKNOWN", "UNKNOWN_TRANSFORMATION", ["UNKNOWN"], "TISSUE", "UNKNOWN",
                        "OBSERVABLE")],
        competes=[("CARAMELISATION", BROWN, "LUMPED_OVERLAP"), ("ACRYLAMIDE_FORMATION", BROWN, "LUMPED_OVERLAP")],
        history=[], matrix=("GENERIC_MECHANISM", []),
        windows=[], flags=["DOSE_NOT_ASSESSED", "NO_SWITCH_REACTION"]),
    "CARAMELISATION": dict(
        member_scope=None,
        participants=[("reactant", "sugars", "SBO:0000010")], enzyme=None,
        pre=[("PRE01", "sugar_presence", "IS", ["PRESENT"], "nutrient_present",
              {"key": "sugars", "trace_exempt_class": "COLLAGEN_TISSUE"},
              "sugars present (SR total sugars; SR zero for every member = absent, except animal muscle tissue, whose "
              "glucose and glucose phosphates lie below SR reporting: UNKNOWN there)"),
             ("PRE02", "heat_applied", "IS", ["HEATED"], "heat_applied", {},
              "the food is being heated (caramelisation is by definition thermal degradation of sugars)")],
        gates=[temp_gate("CG01", "CV-007", "MODULATING", "Rate rises steeply with surface temperature; no switch",
                         scope("GENERIC_MECHANISM"), "RATE")],
        inh=[],
        targets=[target("TGT01", BROWN, "UNKNOWN", "UNKNOWN_TRANSFORMATION", ["UNKNOWN"], "TISSUE", "UNKNOWN",
                        "OBSERVABLE")],
        competes=[("MAILLARD_STRECKER_LUMPED", BROWN, "LUMPED_OVERLAP")],
        history=[], matrix=("GENERIC_MECHANISM", []), windows=[], flags=["DOSE_NOT_ASSESSED", "NO_SWITCH_REACTION"]),
    "STARCH_GELATINISATION": dict(
        member_scope=None,
        participants=[("reactant", "native starch granules", "SBO:0000010"), ("reactant", "water", "SBO:0000010")],
        enzyme=None,
        pre=[("PRE01", "starch_presence", "IS", ["PRESENT"], "nutrient_present", {"key": "starch"},
              "starch present (SR starch; SR zero for every member = absent)"),
             ("PRE02", "aqueous_phase_contact", "IS", ["EXCESS_WATER"], "excess_water", {},
              "water in excess at the starch (immersion in water or an aqueous liquid)")],
        gates=[temp_gate("CG01", "CV-007", "NECESSARY", TBOIL_RATIONALE.format(
            w="MCW-0043, MCW-0045, MCW-0046, MCW-0049, MCW-0052, MCW-0053", water=" in excess water"),
            scope("MODEL_SYSTEM", ["purified potato, maize, tapioca, wheat and rice starches in excess water"]))],
        gate_witness={"CG01": ("tboil_surface", {"excess_water": True})},
        inh=[],
        targets=[target("TGT01", STARCH_STATE, "UNKNOWN", "GELATINIZED", ["UNKNOWN"], "TISSUE", "UNKNOWN", "STATE")],
        consecutive=[("STARCH_RETROGRADATION", "THIS_PRECEDES_OTHER", STARCH_STATE)],
        history=[("starch_state", "INPUT_REQUIRED")],
        matrix=("FOOD_CLASS", ["starch-bearing foods (cereals, tubers, legumes, flours)"]),
        windows=["MCW-0043", "MCW-0045", "MCW-0046", "MCW-0049", "MCW-0052", "MCW-0053"],
        flags=["MATRIX_SCOPE_GENERALISED_FROM_MODEL_SYSTEMS", "SURFACE_ONLY_WITNESS"]),
    "PROTEIN_DENATURATION_AGGREGATION": dict(
        member_scope=None,
        participants=[("reactant", "native proteins", "SBO:0000010")], enzyme=None,
        pre=[("PRE01", "protein_presence", "IS", ["PRESENT"], "nutrient_present", {"key": "protein"},
              "protein present (SR protein; SR zero for every member = absent)"),
             ("PRE02", "denaturing_driver", "PRESENT", [], "denaturing_driver", {},
              "a denaturing driver acts (heat at the boiling point of water, or foaming / whipping): a disjunction")],
        gates=[temp_gate("CG01", "CV-007", "MODULATING", "Each protein has its own onset (myosin < actin; egg-white "
                         "proteins differ); evaluated only inside the denaturing-driver disjunction",
                         scope("FOOD_CLASS", ["muscle foods", "egg"]), "RATE")],
        inh=[],
        targets=[target("TGT01", PROTEIN_STATE, "UNKNOWN", "DENATURED", ["UNKNOWN"], "TISSUE", "UNKNOWN", "STATE")],
        history=[("protein_state", "INPUT_REQUIRED")],
        matrix=("FOOD_CLASS", ["protein-bearing foods (muscle, egg, dairy, legumes, cereals)"]),
        windows=["MCW-0059", "MCW-0060", "MCW-0061", "MCW-0062", "MCW-0066", "MCW-0067", "MCW-0070", "MCW-0076"],
        flags=["SURFACE_ONLY_WITNESS"]),
    "COLLAGEN_SOLUBILISATION": dict(
        member_scope=None,
        participants=[("reactant", "collagen (connective tissue)", "SBO:0000010"), ("product", "gelatin", "SBO:0000011")],
        enzyme=None,
        pre=[("PRE01", "collagen_tissue_presence", "IS", ["PRESENT"], "collagen_present", {},
              "animal connective tissue present (muscle foods; absent when SR protein is zero for every member)")],
        gates=[temp_gate("CG01", "CV-007", "NECESSARY", TBOIL_RATIONALE.format(
            w="MCW-0079, MCW-0086", water=" (moist heat)"),
            scope("FOOD_CLASS", ["bovine muscle", "fish skin collagen"]))],
        gate_witness={"CG01": ("tboil_surface", {"excess_water": False})},
        inh=[],
        targets=[target("TGT01", state("collagen_state", "collagen state (native / denatured / solubilised)"),
                        "UNKNOWN", "STRUCTURE_ALTERED", ["UNKNOWN"], "TISSUE", "UNKNOWN", "STATE")],
        history=[("thermal_history", "INPUT_REQUIRED")],
        matrix=("FOOD_CLASS", ["meat, poultry, fish and shellfish (animal connective tissue)"]),
        windows=["MCW-0079", "MCW-0086"], flags=["DOSE_NOT_ASSESSED", "SURFACE_ONLY_WITNESS"]),
    "ASCORBATE_TO_DHA_OXIDATION": dict(
        member_scope=None,
        participants=[("reactant", "L-ascorbic acid", "SBO:0000010"), ("co-substrate", "molecular oxygen", "SBO:0000010"),
                      ("product", "dehydroascorbic acid", "SBO:0000011"),
                      ("catalyst", "transition-metal ions (Cu, Fe)", "SBO:0000013")],
        enzyme=None,
        pre=[("PRE01", "vitamin_c_presence", "IS", ["PRESENT"], "nutrient_present", {"key": "vitamin_c"},
              "ascorbic acid present (SR vitamin C; SR zero for every member = absent)", "SVAR-000009"),
             ("PRE02", "oxygen_exposure", "IN", ["LID_OFF", "AGITATED"], "oxygen_contact", {},
              "an oxidant reaches the aqueous phase (aerobic pathway; windows MCW-0006, MCW-0007)")],
        gates=[temp_gate("CG01", "CV-006", "MODULATING", "Temperature changes the rate; no switch",
                         scope("MODEL_SYSTEM", ["aqueous ascorbic acid solutions"]), "RATE")],
        inh=[],
        targets=[target("TGT01", AA, "SUBSTRATE", "OXIDIZED", ["DECREASE"], "TISSUE", "MONOTONIC", "SPECIES"),
                 target("TGT02", DHA, "PRODUCT", "OXIDIZED", ["INCREASE", "DECREASE"], "TISSUE", "PEAK_THEN_DECLINE",
                        "SPECIES")],
        competes=[("ASCORBATE_OXIDASE_AA_OXIDATION", AA, "PARALLEL_PATHWAY"),
                  ("ASCORBIC_ACID_ANAEROBIC_DEGRADATION", AA, "PARALLEL_PATHWAY"),
                  ("ASCORBIC_ACID_APPARENT_LOSS_LUMPED", AA, "LUMPED_OVERLAP"), ("LEACHING", AA, "TRANSPORT_VS_REACTION")],
        consecutive=[("DHA_HYDROLYSIS_TO_DKG", "THIS_PRECEDES_OTHER", DHA)],
        history=[("oxygen_exposure", "INPUT_REQUIRED")],
        matrix=("GENERIC_MECHANISM", []),
        windows=["MCW-0001", "MCW-0002", "MCW-0003", "MCW-0004", "MCW-0005", "MCW-0006", "MCW-0007"],
        flags=["DOSE_NOT_ASSESSED", "NO_SWITCH_REACTION"]),
    "ASCORBATE_OXIDASE_AA_OXIDATION": dict(
        member_scope="AAO_FRESH",
        participants=[("substrate", "L-ascorbic acid", "SBO:0000010"), ("co-substrate", "molecular oxygen", "SBO:0000010"),
                      ("enzyme", "ascorbate oxidase", "SBO:0000013"),
                      ("product", "monodehydroascorbate -> dehydroascorbic acid", "SBO:0000011")],
        enzyme=("L-ascorbate oxidase", "EC:1.10.3.3"),
        pre=[("PRE01", "aao_tissue_presence", "IS", ["PRESENT"], "taxon_present", {"cls": "AAO_FRESH"},
              "raw tissue of a food for which an ascorbate-oxidase window exists (broccoli, carrot, cowpea leaves)"),
             ("PRE02", "vitamin_c_presence", "IS", ["PRESENT"], "nutrient_present", {"key": "vitamin_c"},
              "ascorbic acid present (SR vitamin C)", "SVAR-000009"),
             ("PRE03", "enzyme_state_ascorbate_oxidase", "IS", ["ACTIVE"], "enzyme_active", {},
              "enzyme not thermally inactivated (windows MCW-0021, MCW-0025, MCW-0027 report inactivation on heating)"),
             ("PRE04", "oxygen_exposure", "IN", ["LID_OFF", "AGITATED"], "oxygen_contact", {},
              "oxygen available (enzyme definition, MCW-0020)")],
        gates=[],
        inh=[("INH01", "a non-reactant, non-inert member may inhibit or dilute the enzyme", "inhibiting_agent_member",
              "a non-reactant, non-inert member is present", "inhibiting_agent_absent", {"cls": "AAO_FRESH"})],
        targets=[target("TGT01", AA, "SUBSTRATE", "OXIDIZED", ["DECREASE"], "TISSUE", "MONOTONIC", "SPECIES")],
        competes=[("ASCORBATE_TO_DHA_OXIDATION", AA, "PARALLEL_PATHWAY"),
                  ("ASCORBIC_ACID_APPARENT_LOSS_LUMPED", AA, "LUMPED_OVERLAP")],
        consecutive=[("DHA_HYDROLYSIS_TO_DKG", "THIS_PRECEDES_OTHER", DHA)],
        history=[("enzyme_state_ascorbate_oxidase", "ACTIVE_UNTIL_STATE_CHANGE"), ("cell_integrity", "UNKNOWN")],
        matrix=("FOOD_CLASS", ["broccoli, carrot, cowpea leaves, " + FRESH]),
        windows=["MCW-0020", "MCW-0021", "MCW-0025", "MCW-0027"], flags=[]),
    "CHLOROPHYLL_TO_PHEOPHYTIN": dict(
        member_scope=None,
        participants=[("reactant", "chlorophyll a / b", "SBO:0000010"), ("reactant", "H+", "SBO:0000010"),
                      ("product", "pheophytin a / b", "SBO:0000011")],
        enzyme=None,
        pre=[("PRE01", "chlorophyll_tissue_presence", "IS", ["PRESENT"], "taxon_present", {"cls": "CHLOROPHYLL_TISSUE"},
              "green plant tissue in the lot (raw or frozen identity of record)")],
        gates=[ph_gate_modulating("CG01", "Acid speeds Mg loss and alkaline conditions slow it; pH never gates "
                                  "possibility (rule M-1; OPEN_QUESTION 21-7 in the roster)",
                                  scope("FOOD_CLASS", ["green vegetables"]))],
        inh=[],
        targets=[target("TGT01", CHL, "SUBSTRATE", "CONSUMED", ["DECREASE"], "TISSUE", "MONOTONIC", "SPECIES"),
                 target("TGT02", state("pheophytin_content", "pheophytin a + b content"), "PRODUCT", "FORMED",
                        ["INCREASE", "DECREASE"], "TISSUE", "PEAK_THEN_DECLINE", "SPECIES")],
        competes=[("CHLOROPHYLLASE_DEPHYTYLATION", CHL, "PARALLEL_PATHWAY")],
        consecutive=[("CHLOROPHYLL_PYROPHEOPHYTIN_FORMATION", "THIS_PRECEDES_OTHER",
                      state("pheophytin_content", "pheophytin a + b content"))],
        history=[],
        matrix=("FOOD_CLASS", ["green leafy and green vegetables, green herbs"]),
        windows=["MCW-0031", "MCW-0032", "MCW-0033", "MCW-0034", "MCW-0035", "MCW-0036"],
        flags=["DOSE_NOT_ASSESSED", "NO_SWITCH_REACTION"]),
    "LEACHING": dict(
        member_scope=None,
        participants=[("solute", "water-soluble constituent (screened analyte: vitamin C)", "SBO:0000010")],
        enzyme=None,
        pre=[("PRE01", "vitamin_c_presence", "IS", ["PRESENT"], "nutrient_present", {"key": "vitamin_c"},
              "the screened solute (vitamin C) is present (SR vitamin C)", "SVAR-000009"),
             ("PRE02", "aqueous_phase_contact", "IN", ["EXCESS_WATER", "CONDENSATE"], "aqueous_contact", {},
              "the food is in contact with an aqueous liquid that can receive the solute (window MCW-0029)")],
        gates=[], inh=[],
        targets=[target("TGT01", AA, "UNKNOWN", "LEACHED", ["DECREASE"], "TISSUE", "MONOTONIC", "TRANSFERRED_AMOUNT"),
                 target("TGT02", AA, "UNKNOWN", "LEACHED", ["INCREASE"], "COOKING_MEDIUM", "UNKNOWN",
                        "TRANSFERRED_AMOUNT")],
        competes=[("ASCORBATE_TO_DHA_OXIDATION", AA, "TRANSPORT_VS_REACTION")],
        history=[("liquid_fate", "MODULATES_DIRECTION_OR_SELECTIVITY")],
        matrix=("GENERIC_MECHANISM", []), windows=["MCW-0029"], flags=["SCREENED_ANALYTE_VITAMIN_C"]),
    "MOISTURE_LOSS": dict(
        member_scope=None,
        participants=[("solute", "water", "SBO:0000010")], enzyme=None,
        pre=[("PRE01", "water_presence", "IS", ["PRESENT"], "nutrient_present", {"key": "water"},
              "water present in the lot (SR water; SR zero for every member = absent)")],
        gates=[temp_gate("CG01", "CV-007", "MODULATING", "Surface temperature and drying regime change the rate",
                         scope("GENERIC_MECHANISM"), "RATE")],
        inh=[],
        targets=[target("TGT01", MOIST, "UNKNOWN", "VOLATILIZED", ["DECREASE"], "TISSUE", "MONOTONIC",
                        "TRANSFERRED_AMOUNT")],
        history=[], matrix=("GENERIC_MECHANISM", []), windows=[], flags=["DOSE_NOT_ASSESSED"]),
    "LIPID_OXIDATION": dict(
        member_scope=None,
        participants=[("reactant", "unsaturated lipids", "SBO:0000010"), ("co-substrate", "molecular oxygen", "SBO:0000010")],
        enzyme=None,
        pre=[("PRE01", "lipid_presence", "IS", ["PRESENT"], "nutrient_present", {"key": "fat"},
              "lipid present (SR fat; SR zero for every member = absent)"),
             ("PRE02", "oxygen_exposure", "IN", ["LID_OFF", "AGITATED"], "oxygen_contact", {},
              "oxygen reaches the lipid")],
        gates=[temp_gate("CG01", "CV-007", "MODULATING", "Temperature, light and metals change the rate; no switch",
                         scope("GENERIC_MECHANISM"), "RATE")],
        inh=[],
        targets=[target("TGT01", state("", "oxidation markers", svar="SVAR-FUT-017"), "UNKNOWN",
                        "UNKNOWN_TRANSFORMATION", ["UNKNOWN"], "WHOLE_SYSTEM", "UNKNOWN", "OBSERVABLE")],
        history=[("oxygen_exposure", "INPUT_REQUIRED")],
        matrix=("GENERIC_MECHANISM", []), windows=[], flags=["DOSE_NOT_ASSESSED", "NO_SWITCH_REACTION"]),
}

# ----------------------------------------------------------------------------- the 17 GATES_UNKNOWN stubs
# (key -> targets, links). Structure only; preconditions are not authored, so gates_unknown is true.
STUB_SPECS: dict[str, dict[str, Any]] = {
    "LOX_HPL_OXIDATION": dict(targets=[target("TGT01", state("", "volatile abundance", svar="SVAR-FUT-016"), "UNKNOWN",
                                              "UNKNOWN_TRANSFORMATION", ["UNKNOWN"], "TISSUE", "UNKNOWN", "OBSERVABLE")],
                              enzyme=("lipoxygenase / hydroperoxide lyase", None)),
    "ACRYLAMIDE_FORMATION": dict(targets=[target("TGT01", state("acrylamide_content", "acrylamide content"), "PRODUCT",
                                                 "FORMED", ["INCREASE", "DECREASE"], "TISSUE", "PEAK_THEN_DECLINE",
                                                 "SPECIES")],
                                 competes=[("MAILLARD_STRECKER_LUMPED", BROWN, "LUMPED_OVERLAP")]),
    "STARCH_RETROGRADATION": dict(targets=[target("TGT01", STARCH_STATE, "UNKNOWN", "STRUCTURE_ALTERED", ["UNKNOWN"],
                                                  "TISSUE", "UNKNOWN", "STATE")],
                                  consecutive=[("STARCH_GELATINISATION", "OTHER_PRECEDES_THIS", STARCH_STATE)]),
    "DHA_HYDROLYSIS_TO_DKG": dict(targets=[target("TGT01", DHA, "SUBSTRATE", "CONSUMED", ["DECREASE"], "TISSUE",
                                                  "MONOTONIC", "SPECIES")],
                                  consecutive=[("ASCORBATE_TO_DHA_OXIDATION", "OTHER_PRECEDES_THIS", DHA),
                                               ("ASCORBATE_OXIDASE_AA_OXIDATION", "OTHER_PRECEDES_THIS", DHA)]),
    "ASCORBIC_ACID_ANAEROBIC_DEGRADATION": dict(
        targets=[target("TGT01", AA, "SUBSTRATE", "DEGRADED", ["DECREASE"], "TISSUE", "MONOTONIC", "SPECIES")],
        competes=[("ASCORBATE_TO_DHA_OXIDATION", AA, "PARALLEL_PATHWAY"),
                  ("ASCORBIC_ACID_APPARENT_LOSS_LUMPED", AA, "LUMPED_OVERLAP")]),
    "ASCORBIC_ACID_APPARENT_LOSS_LUMPED": dict(
        targets=[target("TGT01", AA, "SUBSTRATE", "DEGRADED", ["DECREASE"], "TISSUE", "MONOTONIC", "SPECIES")],
        competes=[("ASCORBATE_TO_DHA_OXIDATION", AA, "LUMPED_OVERLAP"), ("ASCORBATE_OXIDASE_AA_OXIDATION", AA, "LUMPED_OVERLAP"),
                  ("ASCORBIC_ACID_ANAEROBIC_DEGRADATION", AA, "LUMPED_OVERLAP")]),
    "CHLOROPHYLLASE_DEPHYTYLATION": dict(
        targets=[target("TGT01", CHL, "SUBSTRATE", "CONSUMED", ["DECREASE"], "TISSUE", "MONOTONIC", "SPECIES")],
        enzyme=("chlorophyllase", "EC:3.1.1.14"), competes=[("CHLOROPHYLL_TO_PHEOPHYTIN", CHL, "PARALLEL_PATHWAY")],
        consecutive=[("CHLOROPHYLLIDE_TO_PHEOPHORBIDE", "THIS_PRECEDES_OTHER",
                      state("chlorophyllide_content", "chlorophyllide content"))]),
    "CHLOROPHYLLIDE_TO_PHEOPHORBIDE": dict(
        targets=[target("TGT01", state("chlorophyllide_content", "chlorophyllide content"), "SUBSTRATE", "CONSUMED",
                        ["DECREASE"], "TISSUE", "MONOTONIC", "SPECIES")],
        consecutive=[("CHLOROPHYLLASE_DEPHYTYLATION", "OTHER_PRECEDES_THIS",
                      state("chlorophyllide_content", "chlorophyllide content"))]),
    "VOLATILISATION": dict(targets=[target("TGT01", state("", "volatile abundance", svar="SVAR-FUT-016"), "UNKNOWN",
                                           "VOLATILIZED", ["DECREASE"], "WHOLE_SYSTEM", "UNKNOWN", "TRANSFERRED_AMOUNT")]),
    "OIL_UPTAKE": dict(targets=[target("TGT01", state("fat_uptake", "fat taken up from the frying medium"), "UNKNOWN",
                                       "ABSORBED", ["INCREASE"], "TISSUE", "UNKNOWN", "TRANSFERRED_AMOUNT")]),
    "LACTIC_FERMENTATION": dict(targets=[target("TGT01", state("fermentable_sugar_content", "fermentable sugar content"),
                                                "SUBSTRATE", "FERMENTED", ["DECREASE"], "TISSUE", "UNKNOWN", "SPECIES")]),
    "UNRESOLVED_LOSS": dict(sink=True),
    "CELL_WALL_SOFTENING": dict(targets=[target("TGT01", state("", "texture / force / rheology", svar="SVAR-FUT-007"),
                                                "UNKNOWN", "STRUCTURE_ALTERED", ["UNKNOWN"], "TISSUE", "UNKNOWN",
                                                "OBSERVABLE")]),
    "CELL_DISRUPTION_DECOMPARTMENTALISATION": dict(
        targets=[target("TGT01", state("cell_integrity", "cell integrity"), "UNKNOWN", "STATE_SET", ["UNKNOWN"],
                        "TISSUE", "UNKNOWN", "STATE")]),
    "ENZYME_THERMAL_INACTIVATION": dict(
        targets=[target("TGT01", state("enzyme_state", "enzyme activity state"), "UNKNOWN", "STATE_SET", ["UNKNOWN"],
                        "TISSUE", "UNKNOWN", "STATE")]),
    "CHLOROPHYLL_PYROPHEOPHYTIN_FORMATION": dict(
        targets=[target("TGT01", state("pheophytin_content", "pheophytin a + b content"), "SUBSTRATE", "DEGRADED",
                        ["DECREASE"], "TISSUE", "UNKNOWN", "SPECIES")],
        consecutive=[("CHLOROPHYLL_TO_PHEOPHYTIN", "OTHER_PRECEDES_THIS",
                      state("pheophytin_content", "pheophytin a + b content"))]),
    "METALLO_CHLOROPHYLL_COMPLEX_FORMATION": dict(
        targets=[target("TGT01", state("metallo_chlorophyll_content", "Zn / Cu chlorophyll-derivative content"),
                        "PRODUCT", "FORMED", ["INCREASE"], "TISSUE", "UNKNOWN", "SPECIES")]),
}


# ----------------------------------------------------------------------------- roster and anchors
def read_roster(path: Path = ROSTER_PATH) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(Path(path).read_text(encoding="utf-8"))))


def window_ids(path: Path = WINDOWS_PATH) -> set[str]:
    return {r["window_id"] for r in csv.DictReader(io.StringIO(Path(path).read_text(encoding="utf-8")))}


def windows_by_key(path: Path = WINDOWS_PATH) -> dict[str, list[str]]:
    """mechanism_key -> every window id of the windows registry for that key (sorted)."""
    out: dict[str, list[str]] = {}
    for r in csv.DictReader(io.StringIO(Path(path).read_text(encoding="utf-8"))):
        out.setdefault(r["mechanism_key"], []).append(r["window_id"])
    return {k: sorted(v) for k, v in out.items()}


def _anchor_kind(text: str) -> str:
    t = text.strip()
    if t.startswith("SSOT"):
        return "SSOT_SECTION"
    if t.startswith("MP"):
        return "MASTER_PLAN"
    if t.startswith("ES-1.2"):
        return "ES_1_2_PRIORITY_CELL"
    if t.startswith("plan Step") or t.startswith("G21."):
        return "STEP_CARD"
    if t.startswith("PROC label"):
        return "PROC_LABEL"
    return "RESEARCH_NOTE"


def anchors(row: Mapping[str, str]) -> list[dict[str, str]]:
    out, seen = [], set()
    for part in (row.get("source_anchors") or "").split(";"):
        p = part.strip()
        if p and p not in seen:
            seen.add(p)
            out.append({"anchor_kind": _anchor_kind(p), "ref": p})
    out.append({"anchor_kind": "STEP_CARD", "ref": "registry/mechanism_seed_roster_draft_v1.csv (S158 seed roster)"})
    return out


# ----------------------------------------------------------------------------- entry assembly
def _base(row: Mapping[str, str], n: int) -> dict[str, Any]:
    return {"id": f"MECH-{ID_BLOCK + n:06d}", "record_type": "MECH", "schema_version": SCHEMA_VERSION, "version": 1,
            "status": "ACTIVE", "superseded_by": None, "created_at": CREATED_AT, "created_by": CREATED_BY,
            "provenance": {"method": "LLM", "source_ids": [], "agent": "S178 lane MECH (AI)", "locator": None,
                           "notes": "AI_DRAFTED from the S158 seed roster; no source opened by this lane"},
            "verification": {"status": "UNVERIFIED", "verifier": None, "verified_at": None, "ai_reviewer": None,
                             "notes": None},
            "external_refs": [], "notes": row.get("open_issue") or None,
            "mechanism_key": row["mechanism_key"], "label": row["label"], "synonyms": [],
            "family": row["family"], "kind": row["kind"], "edge_semantics": row["edge_semantics_proposed"],
            "is_evidence": False, "ai_drafted": True, "provenance_class": "INFERRED_LLM", "review_status": "CANDIDATE",
            "review": {"dual_blind_status": "NOT_STARTED", "reviewer_ids": [], "adjudication_ref": None,
                       "review_provenance_valid": "NOT_CHECKED", "review_packet_row_ids": []},
            "derivation_anchors": anchors(row), "participants": [], "enzyme": None, "gates_unknown": True,
            "preconditions": [], "condition_gates": [], "inhibitors_mitigators": [], "competes_with": [],
            "consecutive_with": [], "affected_targets": [], "markers": [], "history_dependence": [],
            "matrix_scope": scope(), "xrefs": [], "evidence_refs": [], "open_questions": []}


def _links(e: dict[str, Any], spec: Mapping[str, Any]) -> None:
    e["competes_with"] = [competes(k, s, r) for k, s, r in spec.get("competes", [])]
    e["consecutive_with"] = [consecutive(k, o, s) for k, o, s in spec.get("consecutive", [])]


def screen_entry(row: Mapping[str, str], n: int, spec: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    e = _base(row, n)
    e["participants"] = [participant(*p) for p in spec["participants"]]
    if spec.get("enzyme"):
        e["enzyme"] = enzyme(*spec["enzyme"])
    items: dict[str, Any] = {}
    for p in spec["pre"]:
        key, skey, op, vals, ev, args, label = p[:7]
        svar = p[7] if len(p) > 7 else None
        e["preconditions"].append(precondition(key, skey, op, vals, label, svar=svar))
        items[key] = {"role": "PRECONDITION", "evaluator": ev, "args": dict(args)}
    e["condition_gates"] = [dict(g) for g in spec["gates"]]
    for g in e["condition_gates"]:
        w = spec.get("gate_witness", {}).get(g["gate_key"])
        if g["gate_type"] == "NECESSARY":
            if w is None:
                raise ValueError(f"{row['mechanism_key']}: a NECESSARY gate needs a screen witness binding")
            items[g["gate_key"]] = {"role": "GATE", "evaluator": w[0], "args": dict(w[1])}
    for key, agent, skey, label, ev, args in spec["inh"]:
        e["inhibitors_mitigators"].append(inhibitor_state(key, agent, skey, label))
        items[key] = {"role": "INHIBITOR_ABSENT", "evaluator": ev, "args": dict(args)}
    e["affected_targets"] = [dict(t) for t in spec["targets"]]
    _links(e, spec)
    e["history_dependence"] = [history(*h) for h in spec.get("history", [])]
    kind, inc = spec["matrix"]
    e["matrix_scope"] = scope(kind, inc)
    e["gates_unknown"] = False
    binding = {"member_scope": spec["member_scope"], "items": items, "flags": list(spec.get("flags", [])),
               "evaluation_order": [p[0] for p in spec["pre"]]
               + [g["gate_key"] for g in e["condition_gates"] if g["gate_type"] == "NECESSARY"]
               + [i[0] for i in spec["inh"]],
               "modulating_gates_not_evaluated": [g["gate_key"] for g in e["condition_gates"]
                                                  if g["gate_type"] == "MODULATING"]}
    return e, binding


def stub_entry(row: Mapping[str, str], n: int, spec: Mapping[str, Any]) -> dict[str, Any]:
    e = _base(row, n)
    if spec.get("sink"):
        e["family"], e["edge_semantics"] = "UNRESOLVED", "NOT_APPLICABLE"
        return e
    if row["kind"] == "ENZYMATIC":
        e["enzyme"] = enzyme(*spec.get("enzyme", (row["label"], None)))
    e["affected_targets"] = [dict(t) for t in spec["targets"]]
    _links(e, spec)
    return e


def build(roster: Sequence[Mapping[str, str]] | None = None) -> list[dict[str, Any]]:
    rows = list(roster) if roster is not None else read_roster()
    keys = [r["mechanism_key"] for r in rows]
    missing = (set(SCREEN_SPECS) | set(STUB_SPECS)) - set(keys)
    if missing:
        raise ValueError(f"specs for keys not in the roster: {sorted(missing)}")
    wins = windows_by_key()
    out = []
    for n, row in enumerate(rows, 1):
        k = row["mechanism_key"]
        windows = wins.get(k, [])
        if k in SCREEN_SPECS:
            spec = SCREEN_SPECS[k]
            e, binding = screen_entry(row, n, spec)
            cited = list(spec.get("windows", []))
            if set(cited) - set(windows):
                raise ValueError(f"{k}: cited windows {sorted(set(cited) - set(windows))} are not windows of this key")
        elif k in STUB_SPECS:
            e, binding, cited = stub_entry(row, n, STUB_SPECS[k]), None, []
        else:
            raise ValueError(f"roster key {k} has no spec")
        out.append({"record": "MECH_ENTRY_DRAFT", "draft_registry": DRAFT_REGISTRY, "builder_version": BUILDER_VERSION,
                    "id_status": "DRAFT_BLOCK_NOT_MINTED", "provenance_class": "AI_DRAFTED",
                    "v1_1_provenance_class_used": "INFERRED_LLM", "evidence_status": "UNSOURCED",
                    "counts_toward_g21_4": False, "status": "DRAFT_PENDING_H4_AND_DUAL_REVIEW",
                    "window_refs": windows, "window_refs_cited_in_rationale": cited,
                    "window_refs_status": WINDOW_STATUS if windows else None,
                    "screen_subset": binding is not None, "screen_binding": binding, "mech": e})
    return out


def dumps(entries: Sequence[Mapping[str, Any]]) -> str:
    return "".join(json.dumps(x, sort_keys=True, ensure_ascii=True) + "\n" for x in entries)


def load(path: Path = OUT_PATH) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def screen_entries(entries: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [x for x in entries if x.get("screen_subset")]
