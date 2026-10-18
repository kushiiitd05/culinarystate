"""One minimal valid record per prefix. Doubles as documentation of the schemas."""
from __future__ import annotations

UNK = {"status": "UNKNOWN"}


def i(prefix: str, n: int = 1) -> str:
    return f"{prefix}-{n:06d}"


def base(prefix: str, n: int = 1, **kw) -> dict:
    rec = {
        "id": i(prefix, n), "record_type": prefix, "schema_version": "1.0.0", "version": 1, "status": "ACTIVE",
        "created_at": "2026-10-18T05:00:00+00:00", "created_by": "Kush+Claude",
        "provenance": {"method": "MANUAL", "source_ids": [i("SRC")]},
        "verification": {"status": "UNVERIFIED"},
    }
    rec.update(kw)
    return rec


def m(value, unit):
    return {"status": "MEASURED", "value": value, "unit": unit}


EXAMPLES: dict[str, dict] = {
    "SRC": base("SRC", kind="DATABASE", title="USDA Table of Nutrient Retention Factors, Release 6",
                licence="US public domain", licence_status="ASSUMED", storage_rule="COMMIT_OK"),
    "SNAP": base("SNAP", source_id=i("SRC"), retrieved_at="2026-10-18T05:00:00+00:00", sha256="a" * 64),
    "API": base("API", source_id=i("SRC"), base_url="https://api.nal.usda.gov/fdc/v1", auth="DEMO_KEY",
                api_status="AVAILABLE", last_checked_at="2026-10-18T05:00:00+00:00"),
    "STUDY": base("STUDY", source_id=i("SRC"), design="DATABASE_AGGREGATE"),
    "MEAS": base("MEAS", family="HPLC", basis="FRESH_WEIGHT"),
    "ING": base("ING", canonical_name="spinach", scientific_name="Spinacia oleracea",
                scientific_identity_status="JUSTIFIED",
                crosswalks={"recipedb": {"status": "UNRESOLVED_EXTERNAL"}}),
    "ALIAS": base("ALIAS", surface="palak", normalized="palak", ingredient_id=i("ING"), language="hi",
                  alias_type="REGIONAL", link_band="HIGH"),
    "ENTITY": base("ENTITY", recipe_id=i("REC"), label="the onions", kind="INGREDIENT_LOT", ordinal=0),
    "MOL": base("MOL", inchikey="MWOOGOJBHIARFG-UHFFFAOYSA-N", pubchem_cid=1183, preferred_name="vanillin",
                stereo_status="UNDEFINED"),
    "IMAP": base("IMAP", ingredient_id=i("ING"), molecule_id=i("MOL"), relation="PRESENCE"),
    "PROC": base("PROC", canonical_name="boil", family="WET_HEAT", kind="ACTION",
                 required_condition_axes=["duration", "temperature"]),
    "TOOL": base("TOOL", canonical_name="saucepan", category="COOKWARE"),
    "COND": base("COND", duration=m(10, "min"),
                 temperatures=[{"location": "MEDIUM", "value": m(100, "degC")}],
                 completeness_mask={"duration": "MEASURED", "temperature": "MEASURED", "ph": "UNKNOWN"}),
    "SVAR": base("SVAR", canonical_name="vitamin C concentration", family="CHEMICAL", value_type="SCALAR",
                 observable_in_session=False),
    "UNIT": base("UNIT", canonical_name="tablespoon", unit_type="CULINARY_VOLUME", dimension="VOLUME",
                 si_unit="mL", conventions=[{"locale": "US", "si_value": m(14.79, "mL")}]),
    "QNT": base("QNT", raw="1 cup flour", parsed={"kind": "NUMBER", "value": 1, "unit_raw": "cup"},
                normalized=UNK, q_level="Q0"),
    "POR": base("POR", ingredient_id=i("ING"), from_unit_id=i("UNIT"), grams_per_unit=m(125, "g"),
                basis="DATABASE"),
    "ALLOC": base("ALLOC", parent_entity_id=i("ENTITY"), child_entity_id=i("ENTITY", 2),
                  fraction={"status": "QUALITATIVE", "qualitative": "half"}, kind="RESERVE"),
    "REC": base("REC", title="Funky feta skewers", content_sha256="b" * 64),
    "INST": base("INST", recipe_id=i("REC"), step_index=0, raw_text="Boil the spinach for 2 min."),
    "EVT": base("EVT", recipe_id=i("REC"), step_index=0, ordinal=0, process_id=i("PROC"), trajectory="PLANNED"),
    "STATE": base("STATE", entity_id=i("ENTITY"), state_version=0, belief="PLANNED"),
    "REF": base("REF", recipe_id=i("REC"), mention_text="the mixture", step_index=2, kind="INTERMEDIATE_NAME"),
    "GRAPH": base("GRAPH", recipe_id=i("REC"),
                  edges=[{"src": i("STATE"), "dst": i("STATE", 2), "relation": "TRANSFORMS_INTO"}]),
    "EVD": base("EVD", provenance={"method": "IMPORT", "source_ids": [i("SRC")], "locator": "retn06 row 1234"},
                origin_type="DATABASE_AGGREGATE", source_id=i("SRC"), source_family_id="USDA-RETN",
                study_id_status="NOT_APPLICABLE", extraction_version="usda_r6@0.1",
                matrix={"ingredient_id": i("ING"), "raw_name": "Vegetables, leafy"},
                process={"process_id": i("PROC"), "raw_name": "boil, drain"},
                target={"state_variable_id": i("SVAR"), "raw_name": "Vitamin C", "basis": "TRUE_RETENTION"},
                derived={"retention_factor": m(0.5, "fraction")}, design="DATABASE_AGGREGATE", tier="E3",
                censored=False),
    "RXN": base("RXN", relation="DEGRADED", reactant_ids=[i("MOL")], confidence="LOW"),
    "WARN": base("WARN", warning_class="INGREDIENT_BEHAVIOUR", trigger={"process_ids": [i("PROC")]},
                 message="Cut apple browns (PPO).", severity="INFO", evidence_ids=[i("EVD")]),
    "ALLERGEN": base("ALLERGEN", allergen_name="peanut", jurisdiction="IN", authority_source_id=i("SRC", 2)),
    "DATASET": base("DATASET", name="DEL-1 evidence ledger", release="v0"),
    "SPLIT": base("SPLIT", dataset_id=i("DATASET"), strategy="STUDY_DISJOINT", seed=7),
    "MODEL": base("MODEL", name="RecipeDB3 DeBERTa v1", family="deberta", reproduction_status="SOURCE_REPORTED",
                  selected_on="UNKNOWN"),
    "EXP": base("EXP", title="D0 persistence baseline", card_path="experiments/EXP-000001/card.md",
                run_status="PLANNED"),
    "GATE": base("GATE", gate_code="G16-QTY", criterion="0 invented grams on fixture set", result="PENDING"),
    "RQ": base("RQ", question="Does process info beat identity-only on unseen pairs?", priority="P0",
               rq_status="OPEN", external_refs=["RQ16-07"]),
    "RS": base("RS", spawn_status="QUEUED"),
    "CLM": base("CLM", statement="State-aware retrieval improves Recall@5", experiment_ids=[i("EXP")],
                claim_type="COMPARATIVE", approval="DRAFT"),
    "KGE": base("KGE", predicate="PROC_USES_TOOL", subject_id=i("PROC"), object_id=i("TOOL"),
                support={"recipes": 120, "mentions": 150, "by_source_family": {"BBCGF-A1": 100, "WIKIBOOKS-COOKBOOK": 20}},
                association={"p_object_given_subject": 0.4, "lift": 6.2}, confidence=0.36, confidence_band="HIGH",
                method="CO_OCCURRENCE", corpus_ids=["BBCGF-A1", "WIKIBOOKS-COOKBOOK"]),
}
