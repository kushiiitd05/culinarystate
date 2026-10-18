"""All ledger record types: prefix -> JSON Schema.

Sources: master plan v4.0 Parts H, W2–W6, X, AH1–AH3, AY; SSOT §235 (quantity), §257 annexes.
Fields not listed in `required` may be absent; scientific values use QVALUE so UNKNOWN is explicit.
"""
from __future__ import annotations

from .common import (
    BOOL, DATETIME, ENVELOPE_REQUIRED, INT0, NUM, OPT_NUM, OPT_STR, QVALUE, SCHEMA_VERSION, STR, STR_LIST,
    enum, envelope, nullable, ref, ref_or_null, refs,
)

EVIDENCE_TIERS = ["E1", "E2", "E3", "E4", "E5", "E6", "E7"]
ORIGIN_TYPES = ["PRIMARY_STUDY", "DATABASE_AGGREGATE", "REVIEW_AGGREGATE", "AUTHORITY_STANDARD",
                "PROJECT_MEASUREMENT"]
RXN_RELATIONS = ["FORMED", "DEGRADED", "RETAINED", "LEACHED", "VOLATILIZED", "OXIDIZED", "REDUCED",
                 "ISOMERIZED", "DENATURED", "AGGREGATED", "GELATINIZED", "FERMENTED", "CONSUMED",
                 "UNKNOWN_TRANSFORMATION"]
GRAPH_RELATIONS = ["TRANSFORMS_INTO", "MERGES_INTO", "SPLITS_INTO", "RESERVED_AS", "DISCARDED_FROM",
                   "RECOMBINED_WITH", "TRANSFERRED_TO", "PART_OF", "LOCATED_IN", "OBSERVED_AS"]
SVAR_FAMILIES = ["PHYSICAL", "CHEMICAL", "SENSORY", "PROCEDURAL", "SAFETY"]
TEMP_LOCATIONS = ["SETPOINT", "MEDIUM", "SURFACE", "CORE", "AMBIENT", "UNSPECIFIED"]
QLEVELS = ["Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]

COND_AXES = [
    "duration", "temperature", "ph", "moisture", "water_activity", "pressure", "oxygen", "salt", "sugar",
    "fat", "particle_size", "geometry", "agitation", "power", "humidity", "heating_rate", "batch_size",
]

TEMPERATURE = {
    "type": "object",
    "required": ["location", "value"],
    "additionalProperties": False,
    "properties": {"location": enum(*TEMP_LOCATIONS), "value": QVALUE,
                   "measurement_method_id": ref_or_null("MEAS")},
}
TRAJECTORY = {
    "type": "array",
    "items": {"type": "object", "required": ["t", "value"], "additionalProperties": False,
              "properties": {"t": NUM, "t_unit": OPT_STR, "value": NUM, "unit": OPT_STR, "axis": OPT_STR}},
}


def _schema(prefix: str, title: str, props: dict, required: list[str] | None = None,
            extra: list[dict] | None = None) -> dict:
    s = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"culinarystate/{prefix}.schema.json",
        "title": f"{prefix}- {title}",
        "description": f"schema_version {SCHEMA_VERSION}",
        "type": "object",
        "additionalProperties": False,
        "properties": {**envelope(prefix), **props},
        "required": ENVELOPE_REQUIRED + (required or []),
    }
    if extra:
        s["allOf"] = extra
    return s


R: dict[str, dict] = {}


def _add(prefix: str, title: str, props: dict, required: list[str] | None = None,
         extra: list[dict] | None = None) -> None:
    R[prefix] = _schema(prefix, title, props, required, extra)


# ---------------- source / provenance (AY1) ----------------
_add("SRC", "source / dataset / paper / API identity", {
    "kind": enum("PAPER", "DATABASE", "DATASET", "API", "WEBSITE", "BOOK", "AUTHORITY_STANDARD", "REPO",
                 "PROJECT"),
    "title": STR, "authors": STR_LIST, "year": nullable({"type": "integer"}),
    "doi": OPT_STR, "url": OPT_STR, "publisher": OPT_STR,
    "licence": STR, "licence_status": enum("VERIFIED", "ASSUMED", "UNKNOWN", "RESTRICTED"),
    "storage_rule": enum("COMMIT_OK", "DERIVED_ONLY", "LOCAL_ONLY", "DO_NOT_STORE"),
    "primary_or_secondary": enum("PRIMARY", "SECONDARY", "TERTIARY", "UNKNOWN"),
    "source_family_id": nullable({"type": "string"}),   # lineage group for duplicate-safe evaluation
    "robots_terms_notes": OPT_STR,
}, ["kind", "title", "licence", "licence_status", "storage_rule"])

_add("SNAP", "exact source snapshot", {
    "source_id": ref("SRC"), "retrieved_at": DATETIME, "retrieval_url": OPT_STR,
    "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}, "bytes": INT0,
    "local_path": OPT_STR, "source_version": OPT_STR, "http_status": nullable({"type": "integer"}),
}, ["source_id", "retrieved_at", "sha256"])

_add("API", "API endpoint / auth / rate limit / terms", {
    "source_id": ref("SRC"), "base_url": STR, "auth": enum("NONE", "API_KEY", "OAUTH", "DEMO_KEY", "UNKNOWN"),
    "rate_limit": OPT_STR, "terms_url": OPT_STR,
    "api_status": enum("AVAILABLE", "BLOCKED", "PENDING_ACCESS", "DEPRECATED", "UNKNOWN"),
    "last_checked_at": DATETIME, "check_result": OPT_STR,
}, ["source_id", "base_url", "auth", "api_status", "last_checked_at"])

_add("STUDY", "study design / experiment family", {
    "source_id": ref("SRC"),
    "design": enum("CONTROLLED_EXPERIMENT", "OBSERVATIONAL", "DATABASE_AGGREGATE", "REVIEW", "AUTHORITY",
                   "PROJECT_MEASUREMENT", "UNKNOWN"),
    "matrix_description": OPT_STR, "controls": OPT_STR, "replicates": nullable(INT0),
    "analytical_platform_ids": refs("MEAS"), "equipment": OPT_STR,
    "condition_completeness": nullable({"type": "number", "minimum": 0, "maximum": 1}),
    "quality_flags": STR_LIST,
}, ["source_id", "design"])

_add("MEAS", "measurement method / platform", {
    "family": enum("HPLC", "LC_MS", "GC_MS", "GC_IMS", "GC_O", "SPECTROPHOTOMETRY", "GRAVIMETRY",
                   "TEXTURE_ANALYZER", "COLORIMETER", "PH_METER", "AW_METER", "THERMOCOUPLE",
                   "SENSORY_PANEL", "TITRATION", "NMR", "CALCULATION", "OTHER", "UNKNOWN"),
    "protocol": OPT_STR, "extraction": OPT_STR, "calibration": OPT_STR,
    "basis": enum("WET", "DRY", "FRESH_WEIGHT", "PER_SERVING", "HEADSPACE", "AS_CONSUMED", "UNKNOWN"),
    "lod": QVALUE, "loq": QVALUE, "comparability_notes": OPT_STR,
}, ["family", "basis"])

# ---------------- ingredient / molecule (AY2) ----------------
_add("ING", "canonical food / ingredient concept", {
    "canonical_name": STR,
    "category": OPT_STR,
    "scientific_name": OPT_STR,
    "scientific_identity_status": enum("JUSTIFIED", "AMBIGUOUS", "NOT_APPLICABLE", "UNKNOWN"),
    "facets": {"type": "object", "additionalProperties": False, "properties": {
        "variety": OPT_STR, "part": OPT_STR, "form": OPT_STR, "prep_state": OPT_STR,
        "fresh_dry": enum("FRESH", "DRY", "FROZEN", "CANNED", "UNKNOWN"), "packing": OPT_STR}},
    "parent_ids": refs("ING"),              # IS_VARIANT_OF / DERIVED_FROM hierarchy
    "is_composite_product": BOOL,           # e.g. "pesto", "garam masala"
    "crosswalks": {"type": "object", "additionalProperties": False, "properties": {
        k: {"type": "object", "required": ["status"], "additionalProperties": False, "properties": {
            "status": enum("LINKED", "CANDIDATE", "UNRESOLVED_EXTERNAL", "NO_MATCH"),
            "external_id": OPT_STR, "score": OPT_NUM}}
        for k in ("foodon", "fdc", "flavordb", "recipedb", "foodb")}},
    "corpus_frequency": nullable(INT0),
    "ambiguity": enum("LOW", "MEDIUM", "HIGH", "UNKNOWN"),
}, ["canonical_name", "scientific_identity_status"])

_add("ALIAS", "surface / regional / language alias", {
    "surface": STR, "normalized": STR, "ingredient_id": ref_or_null("ING"),
    "candidate_ingredient_ids": refs("ING"),
    "language": STR, "region": OPT_STR,
    "alias_type": enum("SYNONYM", "REGIONAL", "TRANSLATION", "SPELLING", "PLURAL", "BRAND", "ABBREVIATION",
                       "AMBIGUOUS"),
    "link_band": enum("EXACT", "HIGH", "MEDIUM", "LOW", "UNRESOLVED"),
    "corpus_frequency": nullable(INT0),
}, ["surface", "normalized", "language", "alias_type", "link_band"])

_add("ENTITY", "physical recipe/session entity (not the concept)", {
    "recipe_id": ref("REC"), "ingredient_id": ref_or_null("ING"), "label": STR,
    "kind": enum("INGREDIENT_LOT", "INTERMEDIATE", "TOOL_CONTENTS", "FINAL_DISH", "DISCARD", "UNKNOWN"),
    "ordinal": INT0,
}, ["recipe_id", "label", "kind"])

_add("MOL", "canonical molecule", {
    "inchikey": {"type": "string", "pattern": "^[A-Z]{14}-[A-Z]{10}-[A-Z]$"},
    "pubchem_cid": nullable({"type": "integer", "minimum": 1}),
    "preferred_name": STR, "synonyms": STR_LIST,
    "canonical_smiles": OPT_STR, "isomeric_smiles": OPT_STR, "formula": OPT_STR,
    "molecular_weight": OPT_NUM,
    "stereo_status": enum("DEFINED", "PARTIAL", "UNDEFINED", "RACEMIC", "UNKNOWN"),
    "descriptors": {"type": "object", "additionalProperties": NUM},
    "fingerprints": {"type": "object", "additionalProperties": {"type": "string"}},  # name -> hex/bitstring
}, ["inchikey", "preferred_name", "stereo_status"])

_add("IMAP", "ingredient <-> molecule evidence mapping", {
    "ingredient_id": ref("ING"), "molecule_id": ref("MOL"),
    "relation": enum("PRESENCE", "MEASURED_CONCENTRATION", "SENSORY_ASSOCIATION", "PROCESS_CHANGE"),
    "concentration": QVALUE, "basis": OPT_STR, "measurement_method_id": ref_or_null("MEAS"),
    "state_id_or_form": OPT_STR, "evidence_ids": refs("EVD"),
}, ["ingredient_id", "molecule_id", "relation"])

# ---------------- process / tool / condition / state variable (AY4) ----------------
_add("PROC", "canonical process / action family", {
    "canonical_name": STR, "aliases": STR_LIST, "family": STR,
    "kind": enum("ACTION", "ENDPOINT", "STATE_DESCRIPTOR", "COMPOSITE"),
    "parent_id": ref_or_null("PROC"),
    "media": STR_LIST, "tool_ids": refs("TOOL"), "prerequisite_ids": refs("PROC"),
    "required_condition_axes": {"type": "array", "items": enum(*COND_AXES), "uniqueItems": True},
    "likely_state_variable_ids": refs("SVAR"),
    "mechanism_families": STR_LIST,
    "corpus_frequency": nullable(INT0),
    "evidence_coverage": nullable(INT0),   # number of EVD rows referencing it
}, ["canonical_name", "family", "kind"])

_add("TOOL", "utensil / tool / material", {
    "canonical_name": STR, "aliases": STR_LIST,
    "category": enum("COOKWARE", "APPLIANCE", "UTENSIL", "VESSEL", "HEAT_SOURCE", "MEASURE", "OTHER"),
    "material": OPT_STR, "reactive_with": STR_LIST, "max_safe_temperature_c": QVALUE,
}, ["canonical_name", "category"])

_add("COND", "full condition profile (W2)", {
    "duration": QVALUE,
    "temperatures": {"type": "array", "items": TEMPERATURE},
    "trajectory": TRAJECTORY,
    "ph_initial": QVALUE, "ph_final": QVALUE, "moisture": QVALUE, "water_activity": QVALUE,
    "pressure": QVALUE, "oxygen": QVALUE, "salt": QVALUE, "sugar": QVALUE, "fat": QVALUE,
    "medium": OPT_STR, "particle_size": QVALUE, "geometry": OPT_STR, "agitation": OPT_STR,
    "power": QVALUE, "humidity": QVALUE, "heat_transfer_mode": OPT_STR,
    "tool_ids": refs("TOOL"), "biological": OPT_STR,
    "completeness_mask": {"type": "object", "additionalProperties": enum("MEASURED", "RANGE", "QUALITATIVE",
                                                                           "UNKNOWN", "NOT_APPLICABLE")},
}, [])

_add("SVAR", "state variable registry (W3)", {
    "canonical_name": STR, "family": enum(*SVAR_FAMILIES), "dimension": OPT_STR, "preferred_unit": OPT_STR,
    "value_type": enum("SCALAR", "INTERVAL", "CATEGORY", "VECTOR", "TRAJECTORY", "BOOLEAN"),
    "preferred_measurement_ids": refs("MEAS"), "comparability_notes": OPT_STR,
    "observable_in_session": BOOL,
}, ["canonical_name", "family", "value_type", "observable_in_session"])

# ---------------- quantity / unit / portions (AY3, SSOT §235) ----------------
_add("UNIT", "unit concept", {
    "canonical_name": STR, "aliases": STR_LIST,
    "unit_type": enum("PHYSICAL", "CULINARY_VOLUME", "COUNT_PORTION", "PACKAGE", "VERBAL_QUALITATIVE",
                      "ENDPOINT_DESCRIPTOR"),
    "dimension": enum("MASS", "VOLUME", "COUNT", "TEMPERATURE", "TIME", "LENGTH", "NONE"),
    "si_unit": OPT_STR,
    "conventions": {"type": "array", "items": {
        "type": "object", "required": ["locale", "si_value"], "additionalProperties": False,
        "properties": {"locale": STR, "si_value": QVALUE, "source_ids": refs("SRC")}}},
    "ambiguity_notes": OPT_STR, "allowed_food_classes": STR_LIST,
}, ["canonical_name", "unit_type", "dimension"])

_add("QNT", "parsed quantity expression", {
    "raw": STR, "recipe_id": ref_or_null("REC"), "line_index": nullable(INT0),
    "span": nullable({"type": "array", "items": INT0, "minItems": 2, "maxItems": 2}),
    "parsed": {"type": "object", "additionalProperties": False, "properties": {
        "kind": enum("NUMBER", "RANGE", "FRACTION", "MIXED", "MULTIPLIER", "PACKAGE", "QUALITATIVE", "NONE"),
        "value": OPT_NUM, "low": OPT_NUM, "high": OPT_NUM, "multiplier": OPT_NUM,
        "unit_id": ref_or_null("UNIT"), "unit_raw": OPT_STR, "size": OPT_STR, "qualifier": OPT_STR,
        "package_size": QVALUE}},
    "normalized": QVALUE,                     # primary channel: g / mL / count, or UNKNOWN
    "mass_g": QVALUE, "volume_ml": QVALUE, "count": QVALUE,   # SSOT §235.7 channels; missing = UNKNOWN mask
    "qualifiers": STR_LIST,                   # about, heaped, level, divided, optional, to taste …
    "conversion_method": nullable(enum("EXACT_PHYSICAL", "LOCALE_CONVENTION", "SOURCE_STATED", "PORTION_RECORD",
                                       "NONE")),
    "conversion_path": {"type": "array", "items": {"type": "string"}},
    "portion_id": ref_or_null("POR"),
    "q_level": enum(*QLEVELS),
    "locale": OPT_STR, "ingredient_id": ref_or_null("ING"),
}, ["raw", "parsed", "normalized", "q_level"])

_add("POR", "ingredient/form/locale portion or density evidence", {
    "ingredient_id": ref("ING"), "form": OPT_STR, "packing": OPT_STR, "locale": OPT_STR,
    "from_unit_id": ref("UNIT"), "grams_per_unit": QVALUE, "density_g_per_ml": QVALUE,
    "basis": enum("MEASURED", "DATABASE", "CONVENTION", "RECIPE_CORPUS_EMPIRICAL_DISTRIBUTION"),
}, ["ingredient_id", "from_unit_id", "grams_per_unit", "basis"])

_add("ALLOC", "split / reserve / recombine allocation", {
    "parent_entity_id": ref("ENTITY"), "child_entity_id": ref("ENTITY"),
    "fraction": QVALUE, "basis": enum("MASS", "VOLUME", "COUNT", "UNSPECIFIED"),
    "kind": enum("SPLIT", "RESERVE", "REMAINDER", "RECOMBINE", "DISCARD"), "event_id": ref_or_null("EVT"),
}, ["parent_entity_id", "child_entity_id", "fraction", "kind"])

# ---------------- recipe semantic / state (AY5) ----------------
_add("REC", "recipe (immutable raw)", {
    "title": STR, "source_url": OPT_STR, "content_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "family_id": OPT_STR, "cuisine": OPT_STR, "n_ingredient_lines": INT0, "n_steps": INT0,
    "raw_location": OPT_STR,  # path inside data/raw (local only)
}, ["title", "content_sha256"])

_add("INST", "instruction semantic record", {
    "recipe_id": ref("REC"), "step_index": INT0, "raw_text": STR, "normalized_text": OPT_STR,
    "sentence_spans": {"type": "array", "items": {"type": "array", "items": INT0}},
    "event_ids": refs("EVT"),
}, ["recipe_id", "step_index", "raw_text"])

_add("EVT", "atomic recipe/session event", {
    "recipe_id": ref("REC"), "step_index": INT0, "ordinal": INT0,
    "process_id": ref_or_null("PROC"), "action_raw": OPT_STR,
    "input_state_ids": refs("STATE"), "output_state_ids": refs("STATE"),
    "tool_ids": refs("TOOL"), "condition_id": ref_or_null("COND"),
    "endpoint": OPT_STR, "optional": BOOL,
    "trajectory": enum("PLANNED", "OBSERVED_SESSION", "PREDICTED"),
    "omitted_step_candidate": BOOL, "span": nullable({"type": "array", "items": INT0}),
}, ["recipe_id", "step_index", "ordinal", "trajectory"])

_add("STATE", "entity version / state (append-only)", {
    "entity_id": ref("ENTITY"), "state_version": {"type": "integer", "minimum": 0},
    "previous_state_id": ref_or_null("STATE"), "produced_by_event_id": ref_or_null("EVT"),
    "belief": enum("PREDICTED", "OBSERVED", "PLANNED"),
    "overrides_state_id": ref_or_null("STATE"),   # observation override keeps the prior prediction
    "variables": {"type": "object", "additionalProperties": QVALUE},  # SVAR-id -> value
    "quantity": QVALUE, "location": OPT_STR, "form": OPT_STR,
}, ["entity_id", "state_version", "belief"])

_add("REF", "coreference / reference relation", {
    "recipe_id": ref("REC"), "mention_text": STR, "mention_span": nullable({"type": "array", "items": INT0}),
    "step_index": INT0, "resolves_to_entity_ids": refs("ENTITY"),
    "kind": enum("ANAPHOR", "BRIDGING", "INTERMEDIATE_NAME", "IMPLICIT", "UNRESOLVED"),
}, ["recipe_id", "mention_text", "step_index", "kind"])

_add("GRAPH", "recipe/session event-state graph", {
    "recipe_id": ref("REC"), "session_id": OPT_STR,
    "edges": {"type": "array", "items": {
        "type": "object", "required": ["src", "dst", "relation"], "additionalProperties": False,
        "properties": {"src": STR, "dst": STR, "relation": enum(*GRAPH_RELATIONS),
                       "event_id": ref_or_null("EVT"), "alloc_id": ref_or_null("ALLOC")}}},
    "event_ids": refs("EVT"), "replay_sha256": OPT_STR,
}, ["recipe_id", "edges"])

# ---------------- scientific evidence / chemistry (AY6, W4, W6) ----------------
_add("EVD", "state-change evidence atom (W4)", {
    "origin_type": enum(*ORIGIN_TYPES),
    "source_id": ref("SRC"),
    "source_family_id": STR,                     # AH1: always required
    "study_ids": refs("STUDY"),
    "study_id_status": enum("PRESENT", "NOT_IDENTIFIABLE", "NOT_APPLICABLE"),
    "extraction_version": STR,
    "matrix": {"type": "object", "required": ["ingredient_id"], "additionalProperties": False, "properties": {
        "ingredient_id": ref_or_null("ING"), "raw_name": STR, "food_group": OPT_STR, "variety": OPT_STR,
        "part": OPT_STR,
        "form": OPT_STR, "prior_processing": OPT_STR, "initial_state": OPT_STR, "geometry": OPT_STR,
        "storage_ripeness": OPT_STR}},
    "process": {"type": "object", "required": ["process_id"], "additionalProperties": False, "properties": {
        "process_id": ref_or_null("PROC"), "raw_name": STR, "family": OPT_STR, "tool_ids": refs("TOOL"),
        "steps": STR_LIST,                       # ordered canonical step names, e.g. ["boil", "drain"]
        "step_process_ids": refs("PROC"),
        "modifiers": {"type": "object", "additionalProperties": {"type": ["string", "boolean", "null"]}},
        "medium": OPT_STR, "condition_id": ref_or_null("COND")}},
    "target": {"type": "object", "required": ["state_variable_id"], "additionalProperties": False,
               "properties": {"state_variable_id": ref_or_null("SVAR"), "raw_name": STR,
                              "molecule_id": ref_or_null("MOL"), "reaction_id": ref_or_null("RXN"),
                              "basis": enum("WET", "DRY", "FRESH_WEIGHT", "PER_SERVING", "HEADSPACE",
                                            "AS_CONSUMED", "TRUE_RETENTION", "APPARENT_RETENTION", "PER_VOLUME",
                                            "RETENTION_TR_OR_AR", "UNKNOWN")}},
    "before": QVALUE, "after": QVALUE,
    "measurement_method_id": ref_or_null("MEAS"),
    "derived": {"type": "object", "additionalProperties": False, "properties": {
        "delta": QVALUE, "percent_change": QVALUE, "retention_factor": QVALUE, "log_fold_change": QVALUE,
        "yield_factor": QVALUE,
        "direction": enum("INCREASE", "DECREASE", "NO_CHANGE", "MIXED", "UNKNOWN")}},
    "design": enum("CONTROLLED_EXPERIMENT", "OBSERVATIONAL", "DATABASE_AGGREGATE", "REVIEW", "AUTHORITY",
                   "UNKNOWN"),
    "n_replicates": nullable(INT0),
    "tier": enum(*EVIDENCE_TIERS),
    "conflict_cluster": OPT_STR, "independence_group": OPT_STR,
    "applicability": enum("EXACT", "NEAR", "ANALOGOUS", "GENERIC", "UNKNOWN"),
    "censored": BOOL,
}, ["origin_type", "source_id", "source_family_id", "study_id_status", "extraction_version", "matrix",
    "process", "target", "tier", "censored"])

_add("RXN", "reaction / transformation relation (partial allowed)", {
    "relation": enum(*RXN_RELATIONS), "reactant_ids": refs("MOL"), "product_ids": refs("MOL"),
    "stoichiometry_known": BOOL, "mechanism_family": OPT_STR, "condition_id": ref_or_null("COND"),
    "reaction_smarts": OPT_STR, "matrix_applicability": OPT_STR, "evidence_ids": refs("EVD"),
    "confidence": enum("HIGH", "MEDIUM", "LOW", "UNKNOWN"),
}, ["relation", "confidence"])

_add("WARN", "evidence-backed warning rule", {
    "warning_class": enum("INGREDIENT_BEHAVIOUR", "UTENSIL", "FOOD_SAFETY", "ALLERGEN", "PREREQUISITE",
                          "STORAGE"),
    "trigger": {"type": "object", "additionalProperties": False, "properties": {
        "ingredient_ids": refs("ING"), "process_ids": refs("PROC"), "tool_ids": refs("TOOL"),
        "condition": OPT_STR, "state": OPT_STR, "user_context": OPT_STR}},
    "message": STR, "mitigation": OPT_STR, "severity": enum("INFO", "CAUTION", "WARNING", "DANGER"),
    "evidence_ids": refs("EVD"), "authority_source_ids": refs("SRC"), "suppression_rules": STR_LIST,
}, ["warning_class", "trigger", "message", "severity"])

_add("ALLERGEN", "authoritative allergen record (AH3)", {
    "allergen_name": STR, "jurisdiction": STR, "authority_source_id": ref("SRC"),
    "ingredient_ids": refs("ING"), "legal_reference": OPT_STR, "cross_contact_notes": OPT_STR,
}, ["allergen_name", "jurisdiction", "authority_source_id"])

# ---------------- research / model / claims (AY7) ----------------
_add("DATASET", "dataset release", {
    "name": STR, "release": STR, "source_ids": refs("SRC"), "sha256": OPT_STR, "n_rows": nullable(INT0),
    "card_path": OPT_STR, "eda_report_path": OPT_STR,
}, ["name", "release"])
_add("SPLIT", "split / fold registry", {
    "dataset_id": ref("DATASET"),
    "strategy": enum("RANDOM", "PAIR_HOLDOUT", "INGREDIENT_DISJOINT", "PROCESS_DISJOINT", "STUDY_DISJOINT",
                     "SOURCE_FAMILY_DISJOINT", "TEMPORAL", "OTHER"),
    "seed": nullable({"type": "integer"}), "roles": STR_LIST, "assignment_sha256": OPT_STR,
    "leakage_report_path": OPT_STR,
}, ["dataset_id", "strategy"])
_add("MODEL", "trained / released model", {
    "name": STR, "family": STR, "training_dataset_ids": refs("DATASET"), "split_ids": refs("SPLIT"),
    "checkpoint_path": OPT_STR, "card_path": OPT_STR, "selected_on": enum("DEV", "TEST", "UNKNOWN"),
    "reproduction_status": enum("SOURCE_REPORTED", "REPRODUCED", "REPRODUCED_WITH_DEVIATION", "FAILED",
                                "OURS"),
}, ["name", "family", "reproduction_status"])
_add("EXP", "experiment card / run / result", {
    "title": STR, "hypothesis": OPT_STR, "card_path": STR, "results_path": OPT_STR,
    "rq_ids": refs("RQ"), "gate_ids": refs("GATE"), "dataset_ids": refs("DATASET"), "model_ids": refs("MODEL"),
    "run_status": enum("PLANNED", "READY", "RUNNING", "DONE", "FAILED", "ABANDONED"),
    "compute": OPT_STR, "command": OPT_STR,
}, ["title", "card_path", "run_status"])
_add("GATE", "promotion / stop decision", {
    "gate_code": STR, "criterion": STR, "result": enum("PASS", "FAIL", "PENDING", "WAIVED"),
    "decided_by": OPT_STR, "experiment_ids": refs("EXP"), "decided_at": nullable(DATETIME),
}, ["gate_code", "criterion", "result"])
_add("RQ", "research question", {
    "question": STR, "block": OPT_STR, "priority": enum("P0", "P1", "P2", "P3"),
    "rq_status": enum("OPEN", "ANSWERED", "PARKED", "DROPPED"),
}, ["question", "priority", "rq_status"])
_add("RS", "research spawn", {
    "rq_id": ref_or_null("RQ"), "brief_path": OPT_STR,
    "spawn_status": enum("QUEUED", "RUNNING", "DONE", "REVIEWED", "DROPPED"), "outcome": OPT_STR,
}, ["spawn_status"])
_add("CLM", "final claim with support", {
    "statement": STR, "evidence_ids": refs("EVD"), "experiment_ids": refs("EXP"), "gate_ids": refs("GATE"),
    "claim_type": enum("DESCRIPTIVE", "COMPARATIVE", "CAUSAL", "SOTA", "NEGATIVE_RESULT"),
    "approval": enum("DRAFT", "HUMAN_APPROVED", "REJECTED"), "approved_by": OPT_STR,
}, ["statement", "claim_type", "approval"])

# ---------------- concept-level knowledge-graph edges (X3c, D-011) ----------------
KGE_PREDICATES = ["ING_HAS_CATEGORY", "ING_PARENT", "ING_PROCESSED_BY", "ING_CO_OCCURS", "ING_USED_IN_CUISINE",
                  "ING_MEASURED_IN_UNIT", "COMPONENT_CONTAINS_ING", "PROC_USES_TOOL", "PROC_FOLLOWED_BY",
                  "PROC_TYPICAL_DURATION", "PROC_TYPICAL_TEMPERATURE", "PROC_IN_FAMILY", "TOOL_HAS_CATEGORY",
                  "ING_ALTERNATIVE_TO", "ING_OFTEN_OPTIONAL", "ING_PREP_FORM", "PROC_USES_MEDIUM", "PROC_ENDPOINT_STATE",
                  "MOL_HAS_TASTE"]
ANY_ID = {"type": "string", "pattern": r"^[A-Z]{2,8}-\d{6}$"}
_QUANT = {"type": "object", "additionalProperties": False, "required": ["n", "unit"],
          "properties": {"n": INT0, "unit": STR, "p10": NUM, "p50": NUM, "p90": NUM, "min": NUM, "max": NUM}}
_add("KGE", "typed concept-level edge with support, association and confidence", {
    "predicate": enum(*KGE_PREDICATES), "subject_id": ANY_ID, "object_id": nullable(ANY_ID),
    "object_value": OPT_STR,
    "support": {"type": "object", "additionalProperties": False, "required": ["recipes"],
                "properties": {"recipes": INT0, "mentions": INT0, "subject_recipes": INT0, "object_recipes": INT0,
                               "by_source_family": {"type": "object", "additionalProperties": INT0}}},
    "association": {"type": "object", "additionalProperties": False,
                    "properties": {"p_object_given_subject": NUM, "lift": NUM, "pmi": NUM}},
    "quantiles": nullable(_QUANT),
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "confidence_band": enum("HIGH", "MEDIUM", "LOW"),
    "method": enum("CO_OCCURRENCE", "SEQUENCE", "TEXT_CONDITION", "ONTOLOGY", "CURATED", "EDITOR_LINK", "STRUCTURAL", "EXTERNAL_SOURCE",
                   "LLM", "HUMAN"),
    "corpus_ids": STR_LIST,
}, ["predicate", "subject_id", "support", "confidence", "confidence_band", "method"])

PREFIXES = tuple(R)
