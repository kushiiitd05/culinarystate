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
            extra: list[dict] | None = None, defs: dict | None = None, comment: str | None = None) -> dict:
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
    if defs:
        s["$defs"] = defs
    if comment:
        s["$comment"] = comment
    return s


R: dict[str, dict] = {}


def _add(prefix: str, title: str, props: dict, required: list[str] | None = None,
         extra: list[dict] | None = None, defs: dict | None = None, comment: str | None = None) -> None:
    R[prefix] = _schema(prefix, title, props, required, extra, defs, comment)


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
                  "MOL_HAS_TASTE", "ING_HEALTH_ASSOCIATION", "ING_COSYLAB_CATEGORY",
                  "ING_CARBON_FOOTPRINT"]
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

# ---------------- evidence lineage chain (D-029 D-6; ported from registry/schemas/*.draft_v1_1.schema.json) ----------------
# Drafts approved at H4 (D-029). Envelope is the shared one; only the record-specific fields, $defs, allOf rules and
# the draft $comment are ported. AGG/DRV are NOT ledgers (export-v2 view keys, D-029 D-2); no KINETIC- prefix.

_DOC_PROPS = {'src_id': {'type': 'string', 'pattern': '^SRC-\\d{6}$'},
              'snapshot_id': {'anyOf': [{'type': 'string', 'pattern': '^SNAP-\\d{6}$'}, {'type': 'null'}]},
              'sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'},
              'bytes': {'type': 'integer', 'minimum': 0},
              'media_type': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
              'doc_kind': {'type': 'string',
                           'enum': ['FULL_TEXT_PDF', 'FULL_TEXT_HTML', 'FULL_TEXT_XML', 'TABLE_FILE',
                                    'DATABASE_RELEASE_FILE', 'WEB_PAGE_SNAPSHOT', 'METADATA_RECORD', 'SUPPLEMENT',
                                    'OTHER', 'UNKNOWN']},
              'content_access': {'type': 'string',
                                 'enum': ['FULL_TEXT', 'TABLES_ONLY', 'METADATA_ONLY', 'ABSTRACT_ONLY', 'UNKNOWN']},
              'report_kind': {'type': 'string',
                              'enum': ['PRIMARY_REPORT', 'THESIS', 'REVIEW', 'COMPILATION_DATABASE', 'SECONDARY_COPY',
                                       'SUPPLEMENT', 'OTHER', 'UNKNOWN']},
              'is_compilation_hub': {'type': 'string',
                                     'enum': ['YES', 'NO', 'UNKNOWN'],
                                     'description': 'Hub = a compilation / review / secondary copy that quotes many '
                                                    'primaries. A hub is never a connecting node between its '
                                                    'primaries (lineage contract 4.2 step 2a).'},
              'authorship': {'type': 'object',
                             'required': ['status', 'authors_raw', 'affiliations_raw', 'corresponding_author_raw',
                                          'year_published'],
                             'additionalProperties': False,
                             'properties': {'status': {'type': 'string',
                                                       'enum': ['READ_FROM_DOCUMENT', 'FROM_METADATA_RECORD',
                                                                'NOT_AVAILABLE', 'UNKNOWN']},
                                            'authors_raw': {'type': 'array',
                                                            'items': {'type': 'string', 'minLength': 1}},
                                            'affiliations_raw': {'type': 'array',
                                                                 'items': {'type': 'string', 'minLength': 1}},
                                            'corresponding_author_raw': {'anyOf': [{'type': 'string', 'minLength': 1},
                                                                                   {'type': 'null'}]},
                                            'year_published': {'anyOf': [{'type': 'integer',
                                                                          'minimum': 1000,
                                                                          'maximum': 2999},
                                                                         {'type': 'null'}]}},
                             'allOf': [{'if': {'properties': {'status': {'enum': ['READ_FROM_DOCUMENT',
                                                                                  'FROM_METADATA_RECORD']}}},
                                        'then': {'properties': {'authors_raw': {'minItems': 1}}}},
                                       {'if': {'properties': {'status': {'enum': ['NOT_AVAILABLE', 'UNKNOWN']}}},
                                        'then': {'properties': {'authors_raw': {'maxItems': 0},
                                                                'affiliations_raw': {'maxItems': 0},
                                                                'corresponding_author_raw': {'type': 'null'},
                                                                'year_published': {'type': 'null'}}}}],
                             'description': 'Authorship as printed (raw), the only inputs from which a lab group '
                                            '(SAME_LAB_AS: shared corresponding / senior author, or the same '
                                            'affiliation unit within +-N years, N in THR-08A-22) can be computed. '
                                            'NOT_AVAILABLE / UNKNOWN keep the arrays empty: a lab is never guessed. '
                                            'A KIN whose DOC has no authorship cannot get lab_group_status '
                                            'ASSIGNED.'},
              'version_label': {'type': 'string',
                                'enum': ['PREPRINT', 'ACCEPTED_MANUSCRIPT', 'VERSION_OF_RECORD', 'DATABASE_RELEASE',
                                         'CORRECTED', 'UNKNOWN']},
              'edition_version': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
              'identifiers': {'type': 'object',
                              'required': [],
                              'additionalProperties': False,
                              'properties': {'doi': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                             'pmid': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                             'pmcid': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                             'isbn': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                             'other': {'type': 'array', 'items': {'type': 'string'}}},
                              'description': 'Identifiers AS PRINTED on this manifestation (a preprint and the '
                                             'published version may differ). Used by detector B1.'},
              'retrieved_at': {'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'null'}]},
              'page_count': {'anyOf': [{'type': 'integer', 'minimum': 1}, {'type': 'null'}]},
              'parser': {'type': 'object',
                         'required': ['tool', 'tool_version', 'ocr_used'],
                         'additionalProperties': False,
                         'properties': {'tool': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                        'tool_version': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                        'ocr_used': {'type': 'string', 'enum': ['YES', 'NO', 'UNKNOWN']}}},
              'local_path': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
              'licence_status': {'type': 'string', 'enum': ['VERIFIED', 'ASSUMED', 'UNKNOWN', 'RESTRICTED']},
              'storage_rule': {'type': 'string', 'enum': ['COMMIT_OK', 'DERIVED_ONLY', 'LOCAL_ONLY', 'DO_NOT_STORE']}}
_DOC_REQUIRED = ['src_id', 'snapshot_id', 'sha256', 'doc_kind', 'content_access', 'report_kind',
                  'is_compilation_hub', 'authorship', 'version_label', 'identifiers', 'licence_status',
                  'storage_rule']
_DOC_RULES = [{'if': {'properties': {'verification': {'properties': {'status': {'enum': ['HUMAN_VERIFIED',
                                                                                         'HUMAN_REJECTED']}},
                                                      'required': ['status']}},
                      'required': ['verification']},
               'then': {'properties': {'verification': {'required': ['verifier', 'verified_at'],
                                                        'properties': {'verifier': {'type': 'string',
                                                                                    'enum': ['Kush', 'Parv']},
                                                                       'verified_at': {'type': 'string',
                                                                                       'format': 'date-time'}}}}}},
              {'if': {'properties': {'report_kind': {'enum': ['COMPILATION_DATABASE', 'REVIEW', 'SECONDARY_COPY']}}},
               'then': {'properties': {'is_compilation_hub': {'const': 'YES'}}}},
              {'if': {'properties': {'report_kind': {'enum': ['PRIMARY_REPORT', 'THESIS']}}},
               'then': {'properties': {'is_compilation_hub': {'const': 'NO'}}}}]
_DOC_COMMENT = ('DOC = file/page/record held locally and hashed. A cited-but-never-held publication is an SRC (kind '
                'PAPER), not a DOC. If snapshot_id is set, sha256 MUST equal SNAP.sha256 (semantic validator). Mint '
                "key: '<src_id>|sha256:<hex>' (SNAP's key is 'sha256:<hex>' alone; DOC adds the src_id because the "
                'same bytes may be held under two SRC; H4 decision D-11).')
_add('DOC', 'concrete manifestation of a source that was actually read', _DOC_PROPS, _DOC_REQUIRED, _DOC_RULES,
     defs=None, comment=_DOC_COMMENT)

_LIN_PROPS = {'from_id': {'type': 'string', 'pattern': '^(SRC|DOC|STUDY|SEXP|SMP|OBS|AGG|DRV|KIN|PARAM)-\\d{6}$'},
              'to_id': {'type': 'string', 'pattern': '^(SRC|DOC|STUDY|SEXP|SMP|OBS|AGG|DRV|KIN|PARAM)-\\d{6}$'},
              'edge_type': {'type': 'string',
                            'enum': ['SAME_STUDY_AS', 'QUOTES_VALUES_FROM', 'ALTERNATE_OF', 'REVISION_OF',
                                     'SHARES_SAMPLES_WITH', 'PRIMARY_SOURCE', 'SAME_LAB_AS',
                                     'SHARES_REFERENCE_SAMPLE', 'CITES']},
              'membership_status': {'type': 'string', 'enum': ['KNOWN', 'UNKNOWN', 'NOT_APPLICABLE']},
              'detection_method': {'type': 'string',
                                   'enum': ['FILE_HASH_MATCH', 'DOI_MATCH', 'PMID_MATCH', 'TITLE_EXACT',
                                            'TITLE_FUZZY', 'AUTHOR_OVERLAP', 'NUMERIC_FINGERPRINT',
                                            'BIBLIOGRAPHY_LISTING', 'DECLARED_BY_SOURCE', 'SOURCE_FAMILY_RULE',
                                            'MANUAL', 'OTHER']},
              'detector_level': {'type': 'string', 'enum': ['B0', 'B1', 'B2', 'B3', 'STRONG', 'MANUAL']},
              'score': {'anyOf': [{'type': 'number', 'minimum': 0, 'maximum': 1}, {'type': 'null'}]},
              'score_basis': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
              'matched_fields': {'type': 'array', 'items': {'type': 'string'}},
              'evidence_note': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
              'edge_status': {'type': 'string', 'enum': ['PROVISIONAL', 'HUMAN_CONFIRMED', 'REJECTED']},
              'reviewer': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
              'reviewed_at': {'anyOf': [{'type': 'string', 'format': 'date-time'}, {'type': 'null'}]},
              'rejection_reason': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
              'rule_version': {'type': 'string', 'minLength': 1}}
_LIN_REQUIRED = ['from_id', 'to_id', 'edge_type', 'detection_method', 'detector_level', 'score', 'edge_status',
                  'reviewer', 'rule_version']
_LIN_RULES = [{'if': {'properties': {'verification': {'properties': {'status': {'enum': ['HUMAN_VERIFIED',
                                                                                         'HUMAN_REJECTED']}},
                                                      'required': ['status']}},
                      'required': ['verification']},
               'then': {'properties': {'verification': {'required': ['verifier', 'verified_at'],
                                                        'properties': {'verifier': {'type': 'string',
                                                                                    'enum': ['Kush', 'Parv']},
                                                                       'verified_at': {'type': 'string',
                                                                                       'format': 'date-time'}}}}}},
              {'if': {'properties': {'edge_type': {'const': 'SAME_STUDY_AS'}}},
               'then': {'properties': {'from_id': {'type': 'string', 'pattern': '^(SRC|DOC|STUDY)-\\d{6}$'},
                                       'to_id': {'type': 'string', 'pattern': '^(SRC|DOC|STUDY)-\\d{6}$'}}}},
              {'if': {'properties': {'edge_type': {'const': 'QUOTES_VALUES_FROM'}}},
               'then': {'properties': {'from_id': {'type': 'string',
                                                   'pattern': '^(SRC|DOC|STUDY|AGG|OBS|DRV|KIN|PARAM)-\\d{6}$'},
                                       'to_id': {'type': 'string',
                                                 'pattern': '^(SRC|DOC|STUDY|AGG|OBS|KIN|PARAM)-\\d{6}$'}}}},
              {'if': {'properties': {'edge_type': {'const': 'ALTERNATE_OF'}}},
               'then': {'properties': {'from_id': {'type': 'string', 'pattern': '^(DOC)-\\d{6}$'},
                                       'to_id': {'type': 'string', 'pattern': '^(DOC)-\\d{6}$'}}}},
              {'if': {'properties': {'edge_type': {'const': 'REVISION_OF'}}},
               'then': {'properties': {'from_id': {'type': 'string', 'pattern': '^(SRC|DOC)-\\d{6}$'},
                                       'to_id': {'type': 'string', 'pattern': '^(SRC|DOC)-\\d{6}$'}}}},
              {'if': {'properties': {'edge_type': {'const': 'SHARES_SAMPLES_WITH'}}},
               'then': {'properties': {'from_id': {'type': 'string', 'pattern': '^(STUDY|SEXP|SMP|KIN)-\\d{6}$'},
                                       'to_id': {'type': 'string', 'pattern': '^(STUDY|SEXP|SMP|KIN)-\\d{6}$'}}}},
              {'if': {'properties': {'edge_type': {'const': 'PRIMARY_SOURCE'}}},
               'then': {'properties': {'from_id': {'type': 'string', 'pattern': '^(SRC|DOC|STUDY|AGG)-\\d{6}$'},
                                       'to_id': {'type': 'string', 'pattern': '^(SRC|DOC|STUDY)-\\d{6}$'}}}},
              {'if': {'properties': {'edge_type': {'const': 'SAME_LAB_AS'}}},
               'then': {'properties': {'from_id': {'type': 'string', 'pattern': '^(SRC|DOC|STUDY)-\\d{6}$'},
                                       'to_id': {'type': 'string', 'pattern': '^(SRC|DOC|STUDY)-\\d{6}$'}}}},
              {'if': {'properties': {'edge_type': {'const': 'SHARES_REFERENCE_SAMPLE'}}},
               'then': {'properties': {'from_id': {'type': 'string', 'pattern': '^(SEXP|SMP)-\\d{6}$'},
                                       'to_id': {'type': 'string', 'pattern': '^(SEXP|SMP)-\\d{6}$'}}}},
              {'if': {'properties': {'edge_type': {'const': 'CITES'}}},
               'then': {'properties': {'from_id': {'type': 'string', 'pattern': '^(SRC|DOC)-\\d{6}$'},
                                       'to_id': {'type': 'string', 'pattern': '^(SRC|DOC)-\\d{6}$'}}}},
              {'if': {'properties': {'edge_type': {'const': 'PRIMARY_SOURCE'}}},
               'then': {'required': ['membership_status'],
                        'properties': {'membership_status': {'type': 'string', 'enum': ['KNOWN', 'UNKNOWN']}}}},
              {'if': {'properties': {'edge_status': {'const': 'HUMAN_CONFIRMED'}}},
               'then': {'required': ['reviewed_at'],
                        'properties': {'reviewer': {'type': 'string', 'enum': ['Kush', 'Parv']},
                                       'reviewed_at': {'type': 'string', 'format': 'date-time'}}}},
              {'if': {'properties': {'edge_status': {'const': 'REJECTED'}}},
               'then': {'required': ['rejection_reason'],
                        'properties': {'rejection_reason': {'type': 'string', 'minLength': 1}}}},
              {'if': {'properties': {'detection_method': {'const': 'MANUAL'}}},
               'then': {'properties': {'detector_level': {'const': 'MANUAL'}}}}]
_LIN_COMMENT = ('Edge semantics, merge classes and symmetric types are fixed by the edge-type registry in '
                'lineage_contract_v1_1.md. Symmetric types (SAME_STUDY_AS, SHARES_SAMPLES_WITH, SAME_LAB_AS, '
                'SHARES_REFERENCE_SAMPLE) are stored once with from_id < to_id (semantic validator). Status changes '
                "are NEW versions of the same LIN id (append-only). Mint key: '<edge_type>|<from>|<to>'. KIN "
                '(series) and PARAM (Step-24 fitted-parameter record; prefix not reserved by this step) may be nodes '
                'of QUOTES_VALUES_FROM (a review that re-plots a primary series, or a compendium that re-reports k / '
                'Ea, is a copy: MERGING) and KIN of SHARES_SAMPLES_WITH. No tenth edge type is added (card: nine '
                'types). SAME_STUDY_AS also accepts SRC: a publication that is cited but never held (the '
                'Phenol-Explorer primaries) has no DOC, so B1 DOI matching must be able to link SRC to SRC / DOC.')
_add('LIN', 'typed lineage / independence edge between two evidence-graph nodes', _LIN_PROPS, _LIN_REQUIRED, _LIN_RULES,
     defs=None, comment=_LIN_COMMENT)

_SEXP_PROPS = {'study_id': {'type': 'string', 'pattern': '^STUDY-\\d{6}$'},
               'experiment_label_raw': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
               'comparison_type': {'type': 'string',
                                   'enum': ['BEFORE_AFTER', 'TIME_COURSE', 'MULTI_TREATMENT_VS_REFERENCE',
                                            'FACTORIAL', 'SURVEY', 'OTHER', 'UNKNOWN']},
               'factors_varied': {'type': 'array',
                                  'items': {'type': 'object',
                                            'required': ['factor', 'name', 'levels_raw'],
                                            'additionalProperties': False,
                                            'properties': {'factor': {'type': 'string',
                                                                      'enum': ['PROCESS', 'TEMPERATURE', 'TIME', 'PH',
                                                                               'MEDIUM', 'MATRIX', 'GEOMETRY',
                                                                               'ATMOSPHERE', 'STORAGE', 'OTHER']},
                                                           'name': {'type': 'string', 'minLength': 1},
                                                           'levels_raw': {'anyOf': [{'type': 'string'},
                                                                                    {'type': 'null'}]}}}},
               'reference_design': {'type': 'string',
                                    'enum': ['OWN_REFERENCE', 'BORROWED_REFERENCE', 'NO_REFERENCE', 'NOT_REPORTED',
                                             'UNKNOWN']},
               'borrowed_reference_sample_ids': {'type': 'array',
                                                 'items': {'type': 'string', 'pattern': '^SMP-\\d{6}$'},
                                                 'minItems': 0,
                                                 'uniqueItems': True},
               'condition_ids': {'type': 'array',
                                 'items': {'type': 'string', 'pattern': '^COND-\\d{6}$'},
                                 'minItems': 0,
                                 'uniqueItems': True},
               'condition_status': {'type': 'string', 'enum': ['LINKED', 'NOT_REPORTED', 'UNKNOWN']},
               'protocol_locator': {'anyOf': [{'$ref': '#/$defs/locator'}, {'type': 'null'}]},
               'equipment_tool_ids': {'type': 'array',
                                      'items': {'type': 'string', 'pattern': '^TOOL-\\d{6}$'},
                                      'minItems': 0,
                                      'uniqueItems': True},
               'context': {'type': 'object',
                           'required': [],
                           'additionalProperties': False,
                           'properties': {'water_food_ratio': {'$ref': '#/$defs/context_item'},
                                          'lid_covered': {'$ref': '#/$defs/context_item'},
                                          'start_mode': {'$ref': '#/$defs/context_item'},
                                          'geometry_class_or_thickness': {'$ref': '#/$defs/context_item'},
                                          'oxygen_headspace': {'$ref': '#/$defs/context_item'},
                                          'ph_tissue': {'$ref': '#/$defs/context_item'},
                                          'ph_medium': {'$ref': '#/$defs/context_item'},
                                          'cooking_water_assayed': {'$ref': '#/$defs/context_item'},
                                          'open_vs_sealed': {'$ref': '#/$defs/context_item'}},
                           'description': 'Optional context (Step 09 / 07.B interface). Absent key = UNKNOWN (not '
                                          'assessed); NOT_REPORTED must be written explicitly by an extractor that '
                                          'read the source (plan card says default NOT_REPORTED: H4 item). Needed '
                                          'later to separate leaching from degradation.'}}
_SEXP_REQUIRED = ['study_id', 'comparison_type', 'factors_varied', 'reference_design',
                   'borrowed_reference_sample_ids', 'condition_ids', 'condition_status', 'protocol_locator']
_SEXP_DEFS = {'locator': {'type': 'object',
                          'required': ['doc_id', 'locator_type', 'raw_text'],
                          'additionalProperties': False,
                          'properties': {'doc_id': {'type': 'string', 'pattern': '^DOC-\\d{6}$'},
                                         'locator_type': {'type': 'string',
                                                          'enum': ['TABLE_CELL', 'TEXT_SPAN', 'FIGURE_DIGITIZED',
                                                                   'DATABASE_ROW', 'SUPPLEMENT_FILE', 'OTHER']},
                                         'page': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                         'table_id': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                         'row_label': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                         'column_label': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                         'figure_id': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                         'char_span': {'anyOf': [{'type': 'array',
                                                                  'items': {'type': 'integer', 'minimum': 0},
                                                                  'minItems': 2,
                                                                  'maxItems': 2},
                                                                 {'type': 'null'}]},
                                         'raw_text': {'anyOf': [{'type': 'string'}, {'type': 'null'}]}},
                          'description': 'Exact place in a DOC. raw_text is the verbatim cell/span/row (key '
                                         'required, null only when the source has no text form).'},
              'context_item': {'type': 'object',
                               'required': ['status'],
                               'additionalProperties': False,
                               'properties': {'status': {'type': 'string',
                                                         'enum': ['REPORTED', 'NOT_REPORTED', 'NOT_APPLICABLE',
                                                                  'UNKNOWN']},
                                              'value_text': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                              'value_number': {'anyOf': [{'type': 'number'}, {'type': 'null'}]},
                                              'unit': {'anyOf': [{'type': 'string'}, {'type': 'null'}]}},
                               'allOf': [{'if': {'properties': {'status': {'const': 'REPORTED'}}},
                                          'then': {'anyOf': [{'properties': {'value_text': {'type': 'string',
                                                                                            'minLength': 1}},
                                                              'required': ['value_text']},
                                                             {'properties': {'value_number': {'type': 'number'}},
                                                              'required': ['value_number']}]}},
                                         {'if': {'properties': {'status': {'enum': ['NOT_REPORTED', 'NOT_APPLICABLE',
                                                                                    'UNKNOWN']}}},
                                          'then': {'properties': {'value_text': {'type': 'null'},
                                                                  'value_number': {'type': 'null'},
                                                                  'unit': {'type': 'null'}}}}],
                               'description': 'Optional experiment-context item. A key that is absent means UNKNOWN '
                                              '(not assessed); NOT_REPORTED is written explicitly when the source '
                                              'was read and is silent.'}}
_SEXP_RULES = [{'if': {'properties': {'verification': {'properties': {'status': {'enum': ['HUMAN_VERIFIED',
                                                                                          'HUMAN_REJECTED']}},
                                                       'required': ['status']}},
                       'required': ['verification']},
                'then': {'properties': {'verification': {'required': ['verifier', 'verified_at'],
                                                         'properties': {'verifier': {'type': 'string',
                                                                                     'enum': ['Kush', 'Parv']},
                                                                        'verified_at': {'type': 'string',
                                                                                        'format': 'date-time'}}}}}},
               {'if': {'properties': {'reference_design': {'const': 'BORROWED_REFERENCE'}}},
                'then': {'properties': {'borrowed_reference_sample_ids': {'minItems': 1}}}},
               {'if': {'properties': {'reference_design': {'enum': ['OWN_REFERENCE', 'NO_REFERENCE', 'NOT_REPORTED',
                                                                    'UNKNOWN']}}},
                'then': {'properties': {'borrowed_reference_sample_ids': {'maxItems': 0}}}},
               {'if': {'properties': {'condition_status': {'const': 'LINKED'}}},
                'then': {'properties': {'condition_ids': {'minItems': 1}}}},
               {'if': {'properties': {'condition_status': {'enum': ['NOT_REPORTED', 'UNKNOWN']}}},
                'then': {'properties': {'condition_ids': {'maxItems': 0}}}}]
_SEXP_COMMENT = ('SEXP- is the scientific experiment; EXP- stays the ML/benchmark run. Reference samples are homed '
                 'on SMP (role REFERENCE_BEFORE, sexp_id = home SEXP); a reference reused from another SEXP is '
                 'listed in borrowed_reference_sample_ids (single source of truth, no cycle). Mint key: '
                 "'<study_id>|<experiment_label_raw or ordinal>'.")
_add('SEXP', 'scientific experiment: one comparison set within a study (NOT the ML run EXP-)', _SEXP_PROPS, _SEXP_REQUIRED, _SEXP_RULES,
     defs=_SEXP_DEFS, comment=_SEXP_COMMENT)

_SMP_PROPS = {'sexp_id': {'type': 'string', 'pattern': '^SEXP-\\d{6}$'},
              'role': {'type': 'string',
                       'enum': ['REFERENCE_BEFORE', 'TREATED_AFTER', 'INTERMEDIATE', 'COOKING_MEDIUM', 'BLANK',
                                'UNKNOWN']},
              'sample_label_raw': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
              'derived_from': {'type': 'object',
                               'required': ['status', 'sample_id', 'process_id', 'process_raw_name', 'condition_id',
                                            'condition_status'],
                               'additionalProperties': False,
                               'properties': {'status': {'type': 'string', 'enum': ['ROOT', 'DERIVED', 'UNKNOWN']},
                                              'sample_id': {'anyOf': [{'type': 'string', 'pattern': '^SMP-\\d{6}$'},
                                                                      {'type': 'null'}]},
                                              'process_id': {'anyOf': [{'type': 'string', 'pattern': '^PROC-\\d{6}$'},
                                                                       {'type': 'null'}]},
                                              'process_raw_name': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                              'condition_id': {'anyOf': [{'type': 'string',
                                                                          'pattern': '^COND-\\d{6}$'},
                                                                         {'type': 'null'}]},
                                              'condition_status': {'type': 'string',
                                                                   'enum': ['LINKED', 'NOT_REPORTED',
                                                                            'NOT_APPLICABLE', 'UNKNOWN']}},
                               'allOf': [{'if': {'properties': {'status': {'const': 'DERIVED'}}},
                                          'then': {'properties': {'sample_id': {'type': 'string',
                                                                                'pattern': '^SMP-\\d{6}$'}}}},
                                         {'if': {'properties': {'status': {'enum': ['ROOT', 'UNKNOWN']}}},
                                          'then': {'properties': {'sample_id': {'type': 'null'},
                                                                  'process_id': {'type': 'null'},
                                                                  'condition_id': {'type': 'null'}}}},
                                         {'if': {'properties': {'condition_status': {'const': 'LINKED'}}},
                                          'then': {'properties': {'condition_id': {'type': 'string',
                                                                                   'pattern': '^COND-\\d{6}$'}}}},
                                         {'if': {'properties': {'condition_status': {'enum': ['NOT_REPORTED',
                                                                                              'NOT_APPLICABLE',
                                                                                              'UNKNOWN']}}},
                                          'then': {'properties': {'condition_id': {'type': 'null'}}}}],
                               'description': 'State-transition edge from the parent sample: which process under '
                                              'which condition produced THIS sample.'},
              'matrix': {'$ref': '#/$defs/matrix'},
              'pooled': {'type': 'string', 'enum': ['POOLED', 'NOT_POOLED', 'UNKNOWN']},
              'material_origin': {'type': 'object',
                                  'required': ['status', 'batch_label_raw', 'cultivar_raw',
                                               'purchase_or_harvest_raw'],
                                  'additionalProperties': False,
                                  'properties': {'status': {'type': 'string',
                                                            'enum': ['REPORTED', 'NOT_REPORTED', 'UNKNOWN']},
                                                 'batch_label_raw': {'anyOf': [{'type': 'string', 'minLength': 1},
                                                                               {'type': 'null'}]},
                                                 'cultivar_raw': {'anyOf': [{'type': 'string', 'minLength': 1},
                                                                            {'type': 'null'}]},
                                                 'purchase_or_harvest_raw': {'anyOf': [{'type': 'string',
                                                                                        'minLength': 1},
                                                                                       {'type': 'null'}]}},
                                  'allOf': [{'if': {'properties': {'status': {'const': 'REPORTED'}}},
                                             'then': {'anyOf': [{'required': ['batch_label_raw'],
                                                                 'properties': {'batch_label_raw': {'type': 'string'}}},
                                                                {'required': ['cultivar_raw'],
                                                                 'properties': {'cultivar_raw': {'type': 'string'}}},
                                                                {'required': ['purchase_or_harvest_raw'],
                                                                 'properties': {'purchase_or_harvest_raw': {'type': 'string'}}}]}},
                                            {'if': {'properties': {'status': {'enum': ['NOT_REPORTED', 'UNKNOWN']}}},
                                             'then': {'properties': {'batch_label_raw': {'type': 'null'},
                                                                     'cultivar_raw': {'type': 'null'},
                                                                     'purchase_or_harvest_raw': {'type': 'null'}}}}],
                                  'description': 'Material origin as printed: batch / lot, cultivar, purchase or '
                                                 'harvest statement. Input of the B3 SHARES_SAMPLES_WITH detector '
                                                 'and of matrix OOD. NOT_REPORTED is a valid answer.'},
              'n_biological_units': {'$ref': '#/$defs/count'}}
_SMP_REQUIRED = ['sexp_id', 'role', 'derived_from', 'matrix', 'pooled', 'material_origin', 'n_biological_units']
_SMP_DEFS = {'matrix': {'type': 'object',
                        'required': ['ingredient_id', 'raw_name'],
                        'additionalProperties': False,
                        'properties': {'ingredient_id': {'anyOf': [{'type': 'string', 'pattern': '^ING-\\d{6}$'},
                                                                   {'type': 'null'}]},
                                       'raw_name': {'type': 'string', 'minLength': 1},
                                       'food_group': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                       'variety': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                       'part': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                       'form': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                       'prior_processing': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                       'initial_state': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                       'geometry': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                       'storage_ripeness': {'anyOf': [{'type': 'string'}, {'type': 'null'}]}},
                        'description': 'Same facets as EVD.matrix (non-destructive). raw_name is required (raw '
                                       'preserved); ingredient_id null = UNRESOLVED.'},
             'count': {'type': 'object',
                       'required': ['status', 'value'],
                       'additionalProperties': False,
                       'properties': {'status': {'type': 'string',
                                                 'enum': ['REPORTED', 'NOT_REPORTED', 'NOT_APPLICABLE', 'UNKNOWN']},
                                      'value': {'anyOf': [{'type': 'integer', 'minimum': 1}, {'type': 'null'}]}},
                       'allOf': [{'if': {'properties': {'status': {'const': 'REPORTED'}}},
                                  'then': {'properties': {'value': {'type': 'integer', 'minimum': 1}}}},
                                 {'if': {'properties': {'status': {'enum': ['NOT_REPORTED', 'NOT_APPLICABLE',
                                                                            'UNKNOWN']}}},
                                  'then': {'properties': {'value': {'type': 'null'}}}}],
                       'description': 'Replicate/sample count with explicit status. NOT_REPORTED = the source was '
                                      'read and is silent; UNKNOWN = not assessed or cannot be told. Never 0 and '
                                      'never a default 1.'}}
_SMP_RULES = [{'if': {'properties': {'verification': {'properties': {'status': {'enum': ['HUMAN_VERIFIED',
                                                                                         'HUMAN_REJECTED']}},
                                                      'required': ['status']}},
                      'required': ['verification']},
               'then': {'properties': {'verification': {'required': ['verifier', 'verified_at'],
                                                        'properties': {'verifier': {'type': 'string',
                                                                                    'enum': ['Kush', 'Parv']},
                                                                       'verified_at': {'type': 'string',
                                                                                       'format': 'date-time'}}}}}}]
_SMP_COMMENT = ('A sample is a physical (or pooled) material state. Several analytes measured on one sample = '
                'several OBS on one SMP. A time series = several SMP (one per time/condition) or one SMP measured '
                'repeatedly; any cell with >= 2 distinct numeric tau MUST also have a KIN (R04-1, kinetic contract); '
                'the cooking medium is a physical sample too (role COOKING_MEDIUM) so that tissue and medium series '
                "of one run can be paired on the same SMP. Mint key: '<sexp_id>|<sample_label_raw or ordinal>'.")
_add('SMP', 'sample: food material at a state within one scientific experiment', _SMP_PROPS, _SMP_REQUIRED, _SMP_RULES,
     defs=_SMP_DEFS, comment=_SMP_COMMENT)

_OBS_PROPS = {'sample_id': {'type': 'string', 'pattern': '^SMP-\\d{6}$'},
              'state_variable_id': {'type': 'string', 'pattern': '^SVAR-\\d{6}$'},
              'analyte_raw_name': {'type': 'string', 'minLength': 1},
              'molecule_id': {'anyOf': [{'type': 'string', 'pattern': '^MOL-\\d{6}$'}, {'type': 'null'}]},
              'analyte_form': {'$ref': '#/$defs/analyte_form'},
              'compartment': {'type': 'string',
                              'enum': ['TISSUE', 'COOKING_MEDIUM', 'WHOLE_SYSTEM', 'NOT_APPLICABLE', 'UNKNOWN']},
              'n_biological': {'$ref': '#/$defs/count'},
              'n_technical': {'$ref': '#/$defs/count'},
              'aggregation_level': {'type': 'string',
                                    'enum': ['SINGLE_MEASUREMENT', 'MEAN_OF_REPLICATES', 'MEAN_OF_SAMPLES',
                                             'UNKNOWN']},
              'locator': {'$ref': '#/$defs/locator'},
              'series_link': {'type': 'object',
                              'required': ['status', 'kinpt_id'],
                              'additionalProperties': False,
                              'properties': {'status': {'type': 'string',
                                                        'enum': ['LINKED_KINPT', 'ENDPOINT_ONLY_SOURCE',
                                                                 'SERIES_NOT_EXTRACTED', 'UNKNOWN']},
                                             'kinpt_id': {'anyOf': [{'type': 'string', 'pattern': '^KINPT-\\d{6}$'},
                                                                    {'type': 'null'}]}},
                              'allOf': [{'if': {'properties': {'status': {'const': 'LINKED_KINPT'}}},
                                         'then': {'properties': {'kinpt_id': {'type': 'string'}}}},
                                        {'if': {'properties': {'status': {'enum': ['ENDPOINT_ONLY_SOURCE',
                                                                                   'SERIES_NOT_EXTRACTED',
                                                                                   'UNKNOWN']}}},
                                         'then': {'properties': {'kinpt_id': {'type': 'null'}}}}],
                              'description': 'Record-level R-04 guard: this OBS is the value behind a KINPT '
                                             '(LINKED_KINPT), or the source reports one time per cell '
                                             '(ENDPOINT_ONLY_SOURCE: asserted by the extractor and checked by the '
                                             'second extractor / adjudicator, not self-certified), or a series '
                                             'exists but was not extracted (SERIES_NOT_EXTRACTED), or not assessed '
                                             '(UNKNOWN). UNKNOWN is treated exactly like SERIES_NOT_EXTRACTED for '
                                             'exclusions: it never supports a statement that the source shows no '
                                             'time dependence. Mirror of KINPT.obs_id (semantic check).'},
              'measurement_dedup': {'type': 'object',
                                    'required': ['status', 'canonical_obs_id', 'report_priority'],
                                    'additionalProperties': False,
                                    'properties': {'status': {'type': 'string',
                                                              'enum': ['UNIQUE_MEASUREMENT', 'CANONICAL',
                                                                       'DUPLICATE_OF_CANONICAL', 'UNKNOWN']},
                                                   'canonical_obs_id': {'anyOf': [{'type': 'string',
                                                                                   'pattern': '^OBS-\\d{6}$'},
                                                                                  {'type': 'null'}]},
                                                   'report_priority': {'anyOf': [{'type': 'integer', 'minimum': 1},
                                                                                 {'type': 'null'}]}},
                                    'allOf': [{'if': {'properties': {'status': {'const': 'DUPLICATE_OF_CANONICAL'}}},
                                               'then': {'properties': {'canonical_obs_id': {'type': 'string'}}}},
                                              {'if': {'properties': {'status': {'enum': ['UNIQUE_MEASUREMENT',
                                                                                         'CANONICAL', 'UNKNOWN']}}},
                                               'then': {'properties': {'canonical_obs_id': {'type': 'null'}}}}],
                                    'description': 'De-duplication of ONE measurement reported in several reports of '
                                                   'one study (journal paper + thesis: two OBS with different '
                                                   'locators). Only UNIQUE_MEASUREMENT and CANONICAL observations '
                                                   'enter pooled or meta-analytic estimates and row-count metrics; '
                                                   'DUPLICATE_OF_CANONICAL rows are kept (append-only) but not '
                                                   'counted; UNKNOWN = not yet assessed (not counted as duplicate, '
                                                   'flagged). report_priority orders the reports when choosing the '
                                                   'canonical one (1 = preferred).'},
              'value': {'$ref': '#/$defs/value_obj'},
              'statistic': {'type': 'string',
                            'enum': ['MEAN', 'MEDIAN', 'SINGLE', 'GEOMETRIC_MEAN', 'MODE', 'MIN', 'MAX', 'OTHER',
                                     'UNKNOWN']},
              'dispersion': {'$ref': '#/$defs/dispersion'},
              'censoring': {'$ref': '#/$defs/censoring'},
              'lod': {'$ref': '#/$defs/measure'},
              'loq': {'$ref': '#/$defs/measure'},
              'basis_id': {'type': 'string', 'pattern': '^MB-\\d{3}$'},
              'basis_raw': {'anyOf': [{'type': 'string'}, {'type': 'null'}],
                            'description': 'Source wording of the basis, verbatim; null only when the source states '
                                           'none.'},
              'retention_definition': {'type': 'string',
                                       'enum': ['TRUE_MURPHY', 'APPARENT_FRESH_BASIS', 'APPARENT_DRY_BASIS',
                                                'APPARENT_BASIS_UNSTATED', 'TR_OR_AR_UNDISCLOSED', 'UNKNOWN',
                                                'NOT_APPLICABLE'],
                                       'description': 'TRUE_MURPHY = Murphy et al. 1975 true retention (nutrient '
                                                      'content of the cooked portion x cooked mass / nutrient '
                                                      'content of the raw portion x raw mass: weight change '
                                                      "accounted for; the card's TRUE and YIELD_ADJUSTED are the "
                                                      'same quantity and differ only in WHO states it, which is '
                                                      'recorded in retention_definition_evidence). APPARENT_* = '
                                                      'concentration ratio without yield correction, WITH the basis '
                                                      'it was computed on (fresh vs dry weight differ by the water '
                                                      'loss, often 10-50%). TR_OR_AR_UNDISCLOSED = the source mixes '
                                                      'true and apparent retention without marking which. UNKNOWN = '
                                                      'not assessed. NOT_APPLICABLE = the value is not a retention.'},
              'retention_type_id': {'anyOf': [{'type': 'string', 'pattern': '^RT-\\d{3}$'}, {'type': 'null'}]},
              'retention_definition_evidence': {'type': 'string',
                                                'enum': ['STATED_IN_PRIMARY', 'STATED_IN_SECONDARY',
                                                         'INFERRED_FROM_FORMULA', 'ASSUMED', 'NOT_APPLICABLE',
                                                         'UNKNOWN'],
                                                'description': 'Who states the retention definition: primary paper, '
                                                               'a secondary source (Phenol-Explorer: a secondary '
                                                               'snippet, D-020), inferred from the formula, or '
                                                               'assumed by the extractor. NOT_APPLICABLE when the '
                                                               'value is not a retention.'},
              'method_indicator': {'type': 'string',
                                   'enum': ['ANALYSIS', 'CALCULATION', 'IMPUTATION',
                                            'IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE', 'COMPILED', 'UNKNOWN']},
              'method': {'$ref': '#/$defs/method_ref'},
              'condition_ref': {'$ref': '#/$defs/condition_ref'},
              'value_origin': {'type': 'string',
                               'enum': ['MEASURED', 'REPORTED', 'DERIVED_DETERMINISTIC', 'SOURCE_IMPUTED',
                                        'SOURCE_IMPUTATION_POSSIBLE', 'UNKNOWN', 'DIGITIZED',
                                        'ESTIMATED_FROM_SUMMARY', 'DEFINITIONAL_NORMALISATION']},
              'digitization': {'anyOf': [{'$ref': '#/$defs/digitization'}, {'type': 'null'}]},
              'licence_status': {'type': 'string', 'enum': ['VERIFIED', 'ASSUMED', 'UNKNOWN', 'RESTRICTED']},
              'storage_rule': {'anyOf': [{'type': 'string',
                                          'enum': ['COMMIT_OK', 'DERIVED_ONLY', 'LOCAL_ONLY', 'DO_NOT_STORE']},
                                         {'type': 'null'}]},
              'extraction_version': {'type': 'string', 'minLength': 1},
              'extraction_record_ids': {'type': 'array',
                                        'items': {'type': 'string', 'pattern': '^XTR-\\d{6}$'},
                                        'uniqueItems': True}}
_OBS_REQUIRED = ['sample_id', 'state_variable_id', 'analyte_raw_name', 'analyte_form', 'compartment', 'n_biological',
                  'n_technical', 'aggregation_level', 'locator', 'series_link', 'measurement_dedup', 'value',
                  'statistic', 'dispersion', 'censoring', 'lod', 'loq', 'basis_id', 'basis_raw',
                  'retention_definition', 'retention_definition_evidence', 'method_indicator', 'method',
                  'condition_ref', 'value_origin', 'digitization', 'licence_status', 'extraction_version']
_OBS_DEFS = {'value_obj': {'type': 'object',
                           'required': ['status'],
                           'additionalProperties': False,
                           'properties': {'status': {'type': 'string',
                                                     'enum': ['MEASURED', 'RANGE', 'QUALITATIVE', 'CENSORED',
                                                              'UNKNOWN', 'NOT_APPLICABLE']},
                                          'value': {'anyOf': [{'type': 'number'}, {'type': 'null'}]},
                                          'low': {'anyOf': [{'type': 'number'}, {'type': 'null'}]},
                                          'high': {'anyOf': [{'type': 'number'}, {'type': 'null'}]},
                                          'unit': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                          'unit_id': {'anyOf': [{'type': 'string', 'pattern': '^UNIT-\\d{6}$'},
                                                                {'type': 'null'}]},
                                          'unit_id_status': {'type': 'string',
                                                             'enum': ['MAPPED', 'NOT_MAPPED', 'UNKNOWN']},
                                          'qualitative': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                          'raw': {'anyOf': [{'type': 'string'}, {'type': 'null'}]}},
                           'allOf': [{'if': {'properties': {'status': {'enum': ['UNKNOWN', 'NOT_APPLICABLE',
                                                                                'QUALITATIVE', 'CENSORED']}}},
                                      'then': {'properties': {'value': {'type': 'null'},
                                                              'low': {'type': 'null'},
                                                              'high': {'type': 'null'}}}},
                                     {'if': {'properties': {'status': {'const': 'MEASURED'}}},
                                      'then': {'required': ['value', 'unit'],
                                               'properties': {'value': {'type': 'number'},
                                                              'unit': {'type': 'string', 'minLength': 1}}}},
                                     {'if': {'properties': {'status': {'const': 'RANGE'}}},
                                      'then': {'required': ['low', 'high', 'unit'],
                                               'properties': {'low': {'type': 'number'},
                                                              'high': {'type': 'number'},
                                                              'unit': {'type': 'string', 'minLength': 1}}}},
                                     {'if': {'properties': {'status': {'const': 'QUALITATIVE'}}},
                                      'then': {'required': ['qualitative'],
                                               'properties': {'qualitative': {'type': 'string', 'minLength': 1}}}},
                                     {'if': {'properties': {'status': {'const': 'CENSORED'}}},
                                      'then': {'required': ['unit'],
                                               'properties': {'unit': {'type': 'string', 'minLength': 1}}}},
                                     {'if': {'properties': {'unit_id_status': {'const': 'MAPPED'}},
                                             'required': ['unit_id_status']},
                                      'then': {'required': ['unit_id'],
                                               'properties': {'unit_id': {'type': 'string',
                                                                          'pattern': '^UNIT-\\d{6}$'}}}},
                                     {'if': {'properties': {'unit_id_status': {'enum': ['NOT_MAPPED', 'UNKNOWN']}},
                                             'required': ['unit_id_status']},
                                      'then': {'properties': {'unit_id': {'type': 'null'}}}},
                                     {'if': {'properties': {'unit_id': {'type': 'string'}}, 'required': ['unit_id']},
                                      'then': {'required': ['unit_id_status'],
                                               'properties': {'unit_id_status': {'const': 'MAPPED'}}}}],
                           'description': 'UNKNOWN-aware value (same status vocabulary as ledgers/schemas/common '
                                          'QVALUE). A number is allowed only where the status says so; '
                                          'UNKNOWN/NOT_APPLICABLE/QUALITATIVE/CENSORED carry no number (the '
                                          'censoring limit lives in `censoring`). `raw` keeps the source string '
                                          'verbatim. `unit` is the raw unit string as printed and is never '
                                          'rewritten; `unit_id` (UNIT-) is the optional normalised pointer with an '
                                          'explicit mapping status (NOT_MAPPED / UNKNOWN keep it null; never a '
                                          'guessed id).'},
             'count': {'type': 'object',
                       'required': ['status', 'value'],
                       'additionalProperties': False,
                       'properties': {'status': {'type': 'string',
                                                 'enum': ['REPORTED', 'NOT_REPORTED', 'NOT_APPLICABLE', 'UNKNOWN']},
                                      'value': {'anyOf': [{'type': 'integer', 'minimum': 1}, {'type': 'null'}]}},
                       'allOf': [{'if': {'properties': {'status': {'const': 'REPORTED'}}},
                                  'then': {'properties': {'value': {'type': 'integer', 'minimum': 1}}}},
                                 {'if': {'properties': {'status': {'enum': ['NOT_REPORTED', 'NOT_APPLICABLE',
                                                                            'UNKNOWN']}}},
                                  'then': {'properties': {'value': {'type': 'null'}}}}],
                       'description': 'Replicate/sample count with explicit status. NOT_REPORTED = the source was '
                                      'read and is silent; UNKNOWN = not assessed or cannot be told. Never 0 and '
                                      'never a default 1.'},
             'measure': {'type': 'object',
                         'required': ['status', 'value', 'unit'],
                         'additionalProperties': False,
                         'properties': {'status': {'type': 'string',
                                                   'enum': ['REPORTED', 'NOT_REPORTED', 'NOT_APPLICABLE', 'UNKNOWN']},
                                        'value': {'anyOf': [{'type': 'number'}, {'type': 'null'}]},
                                        'unit': {'anyOf': [{'type': 'string'}, {'type': 'null'}]}},
                         'allOf': [{'if': {'properties': {'status': {'const': 'REPORTED'}}},
                                    'then': {'properties': {'value': {'type': 'number'},
                                                            'unit': {'type': 'string', 'minLength': 1}}}},
                                   {'if': {'properties': {'status': {'enum': ['NOT_REPORTED', 'NOT_APPLICABLE',
                                                                              'UNKNOWN']}}},
                                    'then': {'properties': {'value': {'type': 'null'}, 'unit': {'type': 'null'}}}}],
                         'description': 'LOD / LOQ of the method as stated for this observation (not an observed '
                                        'value).'},
             'dispersion': {'type': 'object',
                            'required': ['type', 'value', 'low', 'high', 'ci_level', 'unit', 'n_basis', 'scope',
                                         'significance_raw', 'derivation'],
                            'additionalProperties': False,
                            'properties': {'type': {'type': 'string',
                                                    'enum': ['SD', 'SE', 'VARIANCE', 'CI', 'RANGE', 'IQR',
                                                             'INSTRUMENT', 'REPORTED_UNSPECIFIED', 'CV_PERCENT',
                                                             'POOLED_SE', 'LSD', 'NONE_REPORTED', 'UNKNOWN']},
                                           'value': {'anyOf': [{'type': 'number'}, {'type': 'null'}]},
                                           'low': {'anyOf': [{'type': 'number'}, {'type': 'null'}]},
                                           'high': {'anyOf': [{'type': 'number'}, {'type': 'null'}]},
                                           'ci_level': {'anyOf': [{'type': 'number',
                                                                   'exclusiveMinimum': 0,
                                                                   'exclusiveMaximum': 1},
                                                                  {'type': 'null'}]},
                                           'unit': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                           'n_basis': {'type': 'string',
                                                       'enum': ['BIOLOGICAL', 'TECHNICAL', 'NOT_REPORTED', 'UNKNOWN',
                                                                'NOT_APPLICABLE']},
                                           'scope': {'type': 'string',
                                                     'enum': ['PER_VALUE', 'POOLED_TABLE', 'NOT_APPLICABLE',
                                                              'UNKNOWN']},
                                           'significance_raw': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                           'derivation': {'type': 'string',
                                                          'enum': ['AS_REPORTED', 'ESTIMATED_FROM_SUMMARY',
                                                                   'DIGITIZED', 'NOT_APPLICABLE']}},
                            'allOf': [{'if': {'properties': {'type': {'enum': ['SD', 'SE', 'VARIANCE', 'INSTRUMENT',
                                                                               'REPORTED_UNSPECIFIED', 'CV_PERCENT',
                                                                               'POOLED_SE', 'LSD']}}},
                                       'then': {'required': ['value'],
                                                'properties': {'value': {'type': 'number', 'minimum': 0},
                                                               'derivation': {'type': 'string',
                                                                              'enum': ['AS_REPORTED',
                                                                                       'ESTIMATED_FROM_SUMMARY',
                                                                                       'DIGITIZED']}}}},
                                      {'if': {'properties': {'type': {'const': 'CI'}}},
                                       'then': {'required': ['low', 'high', 'ci_level'],
                                                'properties': {'low': {'type': 'number'},
                                                               'high': {'type': 'number'},
                                                               'ci_level': {'type': 'number',
                                                                            'exclusiveMinimum': 0,
                                                                            'exclusiveMaximum': 1},
                                                               'derivation': {'type': 'string',
                                                                              'enum': ['AS_REPORTED',
                                                                                       'ESTIMATED_FROM_SUMMARY',
                                                                                       'DIGITIZED']}}}},
                                      {'if': {'properties': {'type': {'enum': ['RANGE', 'IQR']}}},
                                       'then': {'required': ['low', 'high'],
                                                'properties': {'low': {'type': 'number'},
                                                               'high': {'type': 'number'},
                                                               'derivation': {'type': 'string',
                                                                              'enum': ['AS_REPORTED',
                                                                                       'ESTIMATED_FROM_SUMMARY',
                                                                                       'DIGITIZED']}}}},
                                      {'if': {'properties': {'type': {'enum': ['NONE_REPORTED', 'UNKNOWN']}}},
                                       'then': {'properties': {'value': {'type': 'null'},
                                                               'low': {'type': 'null'},
                                                               'high': {'type': 'null'},
                                                               'ci_level': {'type': 'null'},
                                                               'derivation': {'const': 'NOT_APPLICABLE'},
                                                               'n_basis': {'const': 'NOT_APPLICABLE'},
                                                               'scope': {'const': 'NOT_APPLICABLE'},
                                                               'significance_raw': {'type': 'null'}}}},
                                      {'if': {'properties': {'type': {'const': 'CV_PERCENT'}}},
                                       'then': {'required': ['unit'], 'properties': {'unit': {'const': '%'}}}},
                                      {'if': {'properties': {'type': {'enum': ['SE', 'POOLED_SE']}}},
                                       'then': {'properties': {'n_basis': {'enum': ['BIOLOGICAL', 'TECHNICAL',
                                                                                    'NOT_REPORTED', 'UNKNOWN']}}}},
                                      {'if': {'properties': {'type': {'enum': ['POOLED_SE', 'LSD']}}},
                                       'then': {'properties': {'scope': {'enum': ['POOLED_TABLE', 'UNKNOWN']}}}},
                                      {'if': {'properties': {'type': {'enum': ['SD', 'SE', 'VARIANCE', 'CI', 'RANGE',
                                                                               'IQR', 'INSTRUMENT',
                                                                               'REPORTED_UNSPECIFIED',
                                                                               'CV_PERCENT']}}},
                                       'then': {'properties': {'scope': {'enum': ['PER_VALUE', 'POOLED_TABLE',
                                                                                  'UNKNOWN']}}}}],
                            'description': 'Dispersion with its TYPE always stated (SD vs SE vs CI cannot be '
                                           'confused). NONE_REPORTED = source gives none; UNKNOWN = not assessed. '
                                           'Estimates from median/range (Wan et al. 2014 type) are allowed only with '
                                           'derivation ESTIMATED_FROM_SUMMARY, never as AS_REPORTED. `unit` null '
                                           "means 'same unit as the value' (VARIANCE: squared unit, state it). "
                                           '`n_basis` says which n the SD/SE refers to (biological vs technical; '
                                           'needed for SE->SD conversion; NOT_REPORTED = source silent, UNKNOWN = '
                                           'not assessed). `scope` PER_VALUE vs POOLED_TABLE (one pooled SEM / LSD '
                                           'for a whole table). `significance_raw` keeps significance letters / p '
                                           "text verbatim. CV_PERCENT is stored as printed (unit '%'), never "
                                           'converted to an SD here.'},
             'censoring': {'type': 'object',
                           'required': ['kind', 'registry_id', 'limit_low', 'limit_high', 'limit_unit',
                                        'limit_origin', 'resolution', 'basis_note'],
                           'additionalProperties': False,
                           'properties': {'kind': {'type': 'string',
                                                   'enum': ['DETECTED', 'TRUE_ZERO', 'ND', 'LT_LOD', 'LT_LOQ',
                                                            'GT_ULOQ', 'GT_CAP', 'GT_STATED', 'LT_STATED',
                                                            'CENSORED_UNKNOWN', 'ROUNDED_INTERVAL', 'RANGE_ONLY',
                                                            'TRACE_BETWEEN_LOD_LOQ', 'NOT_REPORTED']},
                                          'registry_id': {'anyOf': [{'type': 'string', 'pattern': '^CS-\\d{3}$'},
                                                                    {'type': 'null'}]},
                                          'limit_low': {'anyOf': [{'type': 'number'}, {'type': 'null'}]},
                                          'limit_high': {'anyOf': [{'type': 'number'}, {'type': 'null'}]},
                                          'limit_unit': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                          'limit_origin': {'type': 'string',
                                                           'enum': ['STATED_IN_SOURCE', 'FROM_METHOD_LOD_LOQ',
                                                                    'FROM_CAP_RULE', 'NOT_STATED',
                                                                    'NOT_APPLICABLE']},
                                          'resolution': {'anyOf': [{'type': 'number', 'exclusiveMinimum': 0},
                                                                   {'type': 'null'}]},
                                          'basis_note': {'anyOf': [{'type': 'string'}, {'type': 'null'}]}},
                           'allOf': [{'if': {'properties': {'kind': {'enum': ['LT_LOD', 'LT_LOQ', 'LT_STATED']}}},
                                      'then': {'required': ['limit_high', 'limit_unit'],
                                               'properties': {'limit_high': {'type': 'number', 'exclusiveMinimum': 0},
                                                              'limit_unit': {'type': 'string', 'minLength': 1}}}},
                                     {'if': {'properties': {'kind': {'enum': ['GT_ULOQ', 'GT_CAP', 'GT_STATED']}}},
                                      'then': {'required': ['limit_low', 'limit_unit'],
                                               'properties': {'limit_low': {'type': 'number', 'exclusiveMinimum': 0},
                                                              'limit_unit': {'type': 'string', 'minLength': 1}}}},
                                     {'if': {'properties': {'kind': {'const': 'ROUNDED_INTERVAL'}}},
                                      'then': {'required': ['resolution'],
                                               'properties': {'resolution': {'type': 'number',
                                                                             'exclusiveMinimum': 0}}}},
                                     {'if': {'properties': {'kind': {'const': 'TRUE_ZERO'}}},
                                      'then': {'required': ['basis_note'],
                                               'properties': {'basis_note': {'type': 'string', 'minLength': 1}}}},
                                     {'if': {'properties': {'kind': {'enum': ['DETECTED', 'NOT_REPORTED',
                                                                              'CENSORED_UNKNOWN']}}},
                                      'then': {'properties': {'limit_low': {'type': 'null'},
                                                              'limit_high': {'type': 'null'}}}},
                                     {'if': {'properties': {'kind': {'const': 'TRACE_BETWEEN_LOD_LOQ'}}},
                                      'then': {'required': ['limit_low', 'limit_high', 'limit_unit'],
                                               'properties': {'limit_low': {'type': 'number', 'exclusiveMinimum': 0},
                                                              'limit_high': {'type': 'number', 'exclusiveMinimum': 0},
                                                              'limit_unit': {'type': 'string', 'minLength': 1}}}}],
                           'description': 'Censoring of ONE observation. kind NOT_REPORTED (CS-007) = no censoring '
                                          'information (UNKNOWN is not NON_DETECT); ND (CS-002) = reported not '
                                          'detected, limit may be unknown and is never zero; LT_LOD/LT_LOQ need the '
                                          'stated limit (limit_high); GT_CAP/GT_ULOQ/GT_STATED need limit_low; '
                                          "ROUNDED_INTERVAL needs the rounding `resolution` (e.g. 'nearest 5%'); "
                                          'RANGE_ONLY = only an interval was reported; TRUE_ZERO is allowed only '
                                          'with a basis_note naming why the zero is a real zero. Cross-field rules '
                                          'against value.status are in the parent schema. TRACE_BETWEEN_LOD_LOQ '
                                          "(proposed CS-011; INFOODS 'tr') = interval-censored between the stated "
                                          'LOD (limit_low) and LOQ (limit_high); value.status CENSORED, no number. '
                                          'Limits are strictly positive: a limit of 0 is not a limit and never a '
                                          "stand-in for a non-detect. GT_CAP together with a `resolution` (USDA: '> "
                                          "100 reported as 100', rounded to the nearest 5%) keeps the cap AS PRINTED "
                                          'in limit_low; the analysis reads the effective bound limit_low - '
                                          'resolution/2 as a NEW derived quantity and never overwrites limit_low.'},
             'digitization': {'type': 'object',
                              'required': ['tool', 'tool_version', 'uncertainty', 'uncertainty_unit',
                                           'uncertainty_status', 'uncertainty_type', 'axis_scale_x', 'axis_scale_y',
                                           'calibration_points_raw', 'digitizer', 'n_reads', 'read_sd',
                                           'figure_locator'],
                              'additionalProperties': False,
                              'properties': {'tool': {'type': 'string', 'minLength': 1},
                                             'tool_version': {'type': 'string', 'minLength': 1},
                                             'uncertainty': {'anyOf': [{'type': 'number', 'exclusiveMinimum': 0},
                                                                       {'type': 'null'}]},
                                             'uncertainty_unit': {'anyOf': [{'type': 'string', 'minLength': 1},
                                                                            {'type': 'null'}]},
                                             'uncertainty_status': {'type': 'string',
                                                                    'enum': ['READ_FROM_TOOL', 'ESTIMATED_BY_READER',
                                                                             'UNKNOWN']},
                                             'uncertainty_type': {'type': 'string',
                                                                  'enum': ['HALF_WIDTH', 'SD', 'AXIS_RESOLUTION',
                                                                           'UNKNOWN']},
                                             'axis_scale_x': {'type': 'string',
                                                              'enum': ['LINEAR', 'LOG10', 'LN', 'UNKNOWN']},
                                             'axis_scale_y': {'type': 'string',
                                                              'enum': ['LINEAR', 'LOG10', 'LN', 'UNKNOWN']},
                                             'calibration_points_raw': {'anyOf': [{'type': 'string'},
                                                                                  {'type': 'null'}]},
                                             'digitizer': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                             'n_reads': {'$ref': '#/$defs/count'},
                                             'read_sd': {'$ref': '#/$defs/measure'},
                                             'figure_locator': {'anyOf': [{'type': 'string'}, {'type': 'null'}]}},
                              'allOf': [{'if': {'properties': {'uncertainty_status': {'const': 'UNKNOWN'}}},
                                         'then': {'properties': {'uncertainty': {'type': 'null'},
                                                                 'uncertainty_unit': {'type': 'null'}}}},
                                        {'if': {'properties': {'uncertainty_status': {'enum': ['READ_FROM_TOOL',
                                                                                               'ESTIMATED_BY_READER']}}},
                                         'then': {'required': ['uncertainty', 'uncertainty_unit'],
                                                  'properties': {'uncertainty': {'type': 'number',
                                                                                 'exclusiveMinimum': 0},
                                                                 'uncertainty_unit': {'type': 'string',
                                                                                      'minLength': 1}}}}],
                              'description': 'Digitisation provenance. The read uncertainty is a number > 0 or '
                                             'explicitly UNKNOWN (uncertainty_status UNKNOWN, uncertainty null): an '
                                             'unknown read uncertainty is never forced to a number and never 0. Axis '
                                             'scale matters (a log axis gives asymmetric / multiplicative error); '
                                             'calibration points, digitizer identity and the repeat-read count / '
                                             'inter-read SD make a read reproducible. Two independent reads are '
                                             'required for any TEST / SIM-VAL eligible series (THR-04K-03, a rule '
                                             'outside this record schema).'},
             'method_ref': {'type': 'object',
                            'required': ['status', 'method_id', 'platform_family', 'platform_raw'],
                            'additionalProperties': False,
                            'properties': {'status': {'type': 'string',
                                                      'enum': ['REFERENCED', 'NOT_REPORTED', 'NOT_APPLICABLE',
                                                               'UNKNOWN']},
                                           'method_id': {'anyOf': [{'type': 'string', 'pattern': '^MEAS-\\d{6}$'},
                                                                   {'type': 'null'}]},
                                           'platform_family': {'anyOf': [{'type': 'string',
                                                                          'enum': ['HPLC', 'LC_MS', 'GC_MS', 'GC_IMS',
                                                                                   'GC_O', 'SPECTROPHOTOMETRY',
                                                                                   'GRAVIMETRY', 'TEXTURE_ANALYZER',
                                                                                   'COLORIMETER', 'PH_METER',
                                                                                   'AW_METER', 'THERMOCOUPLE',
                                                                                   'SENSORY_PANEL', 'TITRATION',
                                                                                   'NMR', 'CALCULATION', 'OTHER',
                                                                                   'UNKNOWN']},
                                                                         {'type': 'null'}]},
                                           'platform_raw': {'anyOf': [{'type': 'string'}, {'type': 'null'}]}},
                            'allOf': [{'if': {'properties': {'status': {'const': 'REFERENCED'}}},
                                       'then': {'properties': {'method_id': {'type': 'string',
                                                                             'pattern': '^MEAS-\\d{6}$'}}}},
                                      {'if': {'properties': {'status': {'enum': ['NOT_REPORTED', 'NOT_APPLICABLE',
                                                                                 'UNKNOWN']}}},
                                       'then': {'properties': {'method_id': {'type': 'null'}}}}],
                            'description': 'Method/platform reference. MEAS- = analytical METHOD (never an '
                                           'observation). platform_raw keeps the source wording.'},
             'condition_ref': {'type': 'object',
                               'required': ['status', 'condition_id'],
                               'additionalProperties': False,
                               'properties': {'status': {'type': 'string',
                                                         'enum': ['LINKED', 'INHERITED_FROM_SAMPLE', 'NOT_REPORTED',
                                                                  'NOT_APPLICABLE', 'UNKNOWN']},
                                              'condition_id': {'anyOf': [{'type': 'string',
                                                                          'pattern': '^COND-\\d{6}$'},
                                                                         {'type': 'null'}]}},
                               'allOf': [{'if': {'properties': {'status': {'const': 'LINKED'}}},
                                          'then': {'properties': {'condition_id': {'type': 'string',
                                                                                   'pattern': '^COND-\\d{6}$'}}}},
                                         {'if': {'properties': {'status': {'enum': ['INHERITED_FROM_SAMPLE',
                                                                                    'NOT_REPORTED', 'NOT_APPLICABLE',
                                                                                    'UNKNOWN']}}},
                                          'then': {'properties': {'condition_id': {'type': 'null'}}}}],
                               'description': 'Condition reference (COND-). INHERITED_FROM_SAMPLE = use '
                                              'SMP.derived_from.condition_id; an observation-level override must be '
                                              'LINKED.'},
             'locator': {'type': 'object',
                         'required': ['doc_id', 'locator_type', 'raw_text'],
                         'additionalProperties': False,
                         'properties': {'doc_id': {'type': 'string', 'pattern': '^DOC-\\d{6}$'},
                                        'locator_type': {'type': 'string',
                                                         'enum': ['TABLE_CELL', 'TEXT_SPAN', 'FIGURE_DIGITIZED',
                                                                  'DATABASE_ROW', 'SUPPLEMENT_FILE', 'OTHER']},
                                        'page': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                        'table_id': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                        'row_label': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                        'column_label': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                        'figure_id': {'anyOf': [{'type': 'string'}, {'type': 'null'}]},
                                        'char_span': {'anyOf': [{'type': 'array',
                                                                 'items': {'type': 'integer', 'minimum': 0},
                                                                 'minItems': 2,
                                                                 'maxItems': 2},
                                                                {'type': 'null'}]},
                                        'raw_text': {'anyOf': [{'type': 'string'}, {'type': 'null'}]}},
                         'description': 'Exact place in a DOC. raw_text is the verbatim cell/span/row (key required, '
                                        'null only when the source has no text form).'},
             'analyte_form': {'type': 'object',
                              'required': ['status', 'text'],
                              'additionalProperties': False,
                              'properties': {'status': {'type': 'string',
                                                        'enum': ['STATED', 'NOT_REPORTED', 'UNKNOWN']},
                                             'text': {'anyOf': [{'type': 'string'}, {'type': 'null'}]}},
                              'allOf': [{'if': {'properties': {'status': {'const': 'STATED'}}},
                                         'then': {'properties': {'text': {'type': 'string', 'minLength': 1}}}},
                                        {'if': {'properties': {'status': {'enum': ['NOT_REPORTED', 'UNKNOWN']}}},
                                         'then': {'properties': {'text': {'type': 'null'}}}}],
                              'description': "Analyte basis/form as stated (e.g. 'ascorbic acid' vs 'ascorbic acid + "
                                             "dehydroascorbic acid'). NOT_REPORTED is a valid answer."}}
_OBS_RULES = [{'if': {'properties': {'verification': {'properties': {'status': {'enum': ['HUMAN_VERIFIED',
                                                                                         'HUMAN_REJECTED']}},
                                                      'required': ['status']}},
                      'required': ['verification']},
               'then': {'properties': {'verification': {'required': ['verifier', 'verified_at'],
                                                        'properties': {'verifier': {'type': 'string',
                                                                                    'enum': ['Kush', 'Parv']},
                                                                       'verified_at': {'type': 'string',
                                                                                       'format': 'date-time'}}}}}},
              {'if': {'properties': {'censoring': {'properties': {'kind': {'enum': ['ND', 'LT_LOD', 'LT_LOQ',
                                                                                    'GT_ULOQ', 'GT_CAP', 'GT_STATED',
                                                                                    'LT_STATED', 'CENSORED_UNKNOWN',
                                                                                    'TRACE_BETWEEN_LOD_LOQ']}},
                                                   'required': ['kind']}},
                      'required': ['censoring']},
               'then': {'properties': {'value': {'properties': {'status': {'const': 'CENSORED'}}}}}},
              {'if': {'properties': {'value': {'properties': {'status': {'const': 'CENSORED'}},
                                               'required': ['status']}},
                      'required': ['value']},
               'then': {'properties': {'censoring': {'properties': {'kind': {'enum': ['ND', 'LT_LOD', 'LT_LOQ',
                                                                                      'GT_ULOQ', 'GT_CAP',
                                                                                      'GT_STATED', 'LT_STATED',
                                                                                      'CENSORED_UNKNOWN',
                                                                                      'TRACE_BETWEEN_LOD_LOQ']}}}}}},
              {'if': {'properties': {'censoring': {'properties': {'kind': {'const': 'RANGE_ONLY'}},
                                                   'required': ['kind']}},
                      'required': ['censoring']},
               'then': {'properties': {'value': {'properties': {'status': {'const': 'RANGE'}}}}}},
              {'if': {'properties': {'censoring': {'properties': {'kind': {'enum': ['ROUNDED_INTERVAL', 'DETECTED']}},
                                                   'required': ['kind']}},
                      'required': ['censoring']},
               'then': {'properties': {'value': {'properties': {'status': {'const': 'MEASURED'}}}}}},
              {'if': {'properties': {'censoring': {'properties': {'kind': {'const': 'TRUE_ZERO'}},
                                                   'required': ['kind']}},
                      'required': ['censoring']},
               'then': {'properties': {'value': {'properties': {'status': {'const': 'MEASURED'},
                                                                'value': {'const': 0}}}}}},
              {'if': {'properties': {'value_origin': {'const': 'DIGITIZED'}}, 'required': ['value_origin']},
               'then': {'properties': {'digitization': {'type': 'object'}}}},
              {'if': {'properties': {'value_origin': {'enum': ['MEASURED', 'REPORTED', 'DERIVED_DETERMINISTIC',
                                                               'SOURCE_IMPUTED', 'SOURCE_IMPUTATION_POSSIBLE',
                                                               'UNKNOWN', 'ESTIMATED_FROM_SUMMARY',
                                                               'DEFINITIONAL_NORMALISATION']}},
                      'required': ['value_origin']},
               'then': {'properties': {'digitization': {'type': 'null'}}}},
              {'if': {'properties': {'value_origin': {'const': 'ESTIMATED_FROM_SUMMARY'}},
                      'required': ['value_origin']},
               'then': {'properties': {'dispersion': {'properties': {'derivation': {'enum': ['ESTIMATED_FROM_SUMMARY',
                                                                                             'NOT_APPLICABLE']}}}}}},
              {'if': {'properties': {'basis_id': {'const': 'MB-007'}}, 'required': ['basis_id']},
               'then': {'properties': {'retention_definition': {'enum': ['TRUE_MURPHY', 'APPARENT_FRESH_BASIS',
                                                                         'APPARENT_DRY_BASIS',
                                                                         'APPARENT_BASIS_UNSTATED',
                                                                         'TR_OR_AR_UNDISCLOSED', 'UNKNOWN']}}}},
              {'if': {'properties': {'retention_definition': {'const': 'NOT_APPLICABLE'}}},
               'then': {'properties': {'retention_definition_evidence': {'const': 'NOT_APPLICABLE'}}}},
              {'if': {'properties': {'retention_type_id': {'const': 'RT-001'}}, 'required': ['retention_type_id']},
               'then': {'properties': {'retention_definition': {'enum': ['TRUE_MURPHY']}}}},
              {'if': {'properties': {'retention_type_id': {'const': 'RT-003'}}, 'required': ['retention_type_id']},
               'then': {'properties': {'retention_definition': {'enum': ['TRUE_MURPHY']}}}},
              {'if': {'properties': {'retention_type_id': {'const': 'RT-002'}}, 'required': ['retention_type_id']},
               'then': {'properties': {'retention_definition': {'enum': ['APPARENT_FRESH_BASIS', 'APPARENT_DRY_BASIS',
                                                                         'APPARENT_BASIS_UNSTATED']}}}},
              {'if': {'properties': {'retention_type_id': {'const': 'RT-004'}}, 'required': ['retention_type_id']},
               'then': {'properties': {'retention_definition': {'enum': ['TR_OR_AR_UNDISCLOSED']}}}},
              {'if': {'properties': {'retention_type_id': {'const': 'RT-005'}}, 'required': ['retention_type_id']},
               'then': {'properties': {'retention_definition': {'enum': ['UNKNOWN']}}}},
              {'if': {'properties': {'retention_type_id': {'const': 'RT-006'}}, 'required': ['retention_type_id']},
               'then': {'properties': {'retention_definition': {'enum': ['NOT_APPLICABLE']}}}},
              {'if': {'properties': {'value': {'properties': {'status': {'const': 'MEASURED'}, 'value': {'const': 0}},
                                               'required': ['status', 'value']}},
                      'required': ['value']},
               'then': {'properties': {'censoring': {'properties': {'kind': {'const': 'TRUE_ZERO'}}}}}}]
_OBS_COMMENT = ('OBS carries what the document reports. USDA/Bognar-type compiled values are AGG, not OBS. n_*, '
                'dispersion type, censoring (+LOD/LOQ), basis, method/platform and condition reference are mandatory '
                'FIELDS with explicit NOT_REPORTED / UNKNOWN statuses (never 0, never silently absent). Lineage keys '
                'are NOT stored on OBS: they derive from sample -> sexp -> study via the independence registry. Mint '
                "key: '<sample_id>|<state_variable_id>|<compartment>|<locator key>'. series_link is the record-level "
                'R-04 guard (a >= 2-time series must have a KIN; see the kinetic contract). measurement_dedup keeps '
                'one canonical OBS per measurement across reports of the same study.')
_add('OBS', 'observation: one property value of one sample by one method (NOT MEAS-, which is the method)', _OBS_PROPS, _OBS_REQUIRED, _OBS_RULES,
     defs=_OBS_DEFS, comment=_OBS_COMMENT)

PREFIXES = tuple(R)
