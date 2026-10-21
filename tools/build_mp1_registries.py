#!/usr/bin/env python3
"""MP-1 registries (contracts only, no evidence invented): tier<->provenance map, EVD contract field map, simulation schema, human verification queue, frozen similarity registry.
  python tools/build_mp1_registries.py"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "registry"


def w(name, hdr, rows):
    with open(R / name, "w", newline="", encoding="utf-8") as f:
        c = csv.writer(f)
        c.writerow(hdr)
        c.writerows(rows)
    print(name, len(rows))


# ---------------- tier <-> provenance ----------------
w("evidence_tier_provenance_map_v1.csv",
  ["tier", "meaning (SSOT Part I)", "answers", "allowed_provenance_classes", "requires_human_verification", "primary_evaluation_eligible", "may_be_training_prior", "current_rows", "notes"],
  [["E1", "controlled experiment with measured conditions", "how strong is the scientific evidence", "EXPLICIT_SOURCE; EXTERNAL_VERIFIED", "YES (to be assigned E1)", "YES", "YES", 0, "design evidence must be in the source; verification status is recorded separately (see OPEN CONFLICT C1)"],
   ["E2", "experiment with partial conditions", "how strong is the scientific evidence", "EXPLICIT_SOURCE; EXTERNAL_VERIFIED", "YES (to be assigned E2)", "YES", "YES", 0, "condition_completeness must list unknown axes"],
   ["E3", "database aggregate (USDA R6, Phenol-Explorer, Bognar)", "how strong is the scientific evidence", "EXPLICIT_SOURCE; DERIVED_DETERMINISTIC", "no (source is a curated database); needed for held-out test labels (G14-3, G15-H)", "YES (conditional: held-out test rows need human verification)", "YES", 17978, "USDA R6 %TR/%AR not distinguished at row level; many values imputed from similar foods; 5,894 rows censored"],
   ["E4", "structured/LLM-extracted AND human verified", "how strong is the scientific evidence", "INFERRED_LLM (verified) ; EXPLICIT_SOURCE", "YES (Kush + Parv)", "YES", "YES", 0, "only route from extraction to evaluation eligibility"],
   ["E5", "LLM-extracted, unverified", "how strong is the scientific evidence", "INFERRED_LLM; UNKNOWN", "no (that is the point: unverified)", "NO", "restricted: candidate generation only, never silently promoted", 0, "Phenol-Explorer 3,870 rows are AI_PRECHECKED by a rule/AI pass, tier E3 from a curated database, not E5"],
   ["E6", "mechanism-family rule or heuristic (MODEL_ESTIMATED)", "how strong is the scientific evidence", "MODEL_ESTIMATED; IMPUTED", "n/a", "NO", "prior or stress test only", 0, "FDC raw/cooked pairs (867) are E6 candidates, not ingested"],
   ["E7", "simulator output", "how strong is the scientific evidence", "SIMULATED", "n/a", "NO", "prior / stress test only; never Gold truth", 0, "must carry simulator id, version, parameters, uncertainty"]])
w("provenance_class_registry_v1.csv",
  ["provenance_class", "answers: where did this value come from", "typical tiers", "example", "evaluation use"],
  [["EXPLICIT_SOURCE", "value stated in the cited source (table/figure/text)", "E1-E4", "retention factor printed in USDA R6", "yes if tier E1-E4"],
   ["EXTERNAL_VERIFIED", "value checked against the cited source by an independent human or authority", "E1-E4", "Kush+Parv verified literature row", "yes"],
   ["DERIVED_DETERMINISTIC", "computed from stated values by a documented deterministic rule", "E1-E4 (inherits)", "log_fold_change = ln(after/before); percent_change", "yes if inputs eligible"],
   ["INFERRED_LLM", "extracted/inferred by an LLM", "E4 (after human verification) or E5", "LLM-extracted literature candidate", "only after human verification"],
   ["MODEL_ESTIMATED", "predicted by a statistical/ML model or mechanism-family rule", "E6", "rule-based mechanism prior", "no"],
   ["IMPUTED", "filled by an imputation rule (including source-side imputation if declared)", "E6 or inherited", "USDA values imputed from similar foods", "no as Gold truth unless declared and censor-aware"],
   ["SIMULATED", "output of a simulator", "E7", "heat-transfer simulation", "no"],
   ["UNKNOWN", "origin not recorded", "any", "legacy rows", "no"]])

# ---------------- EVD contract field map ----------------
NA = "n/a"
w("evd_contract_v1.csv",
  ["contract_field", "required", "current_ledger_field (ledgers/schemas/EVD.schema.json)", "current_population", "action", "semantics_when_unavailable"],
  [["evd_id", "yes", "id", "100%", "keep", NA],
   ["source_id", "yes", "source_id", "100%", "keep", NA],
   ["study_id", "no (database aggregates)", "study_ids[] + study_id_status", "PE 3,870 PRESENT; others NOT_IDENTIFIABLE", "keep", "study_id_status = NOT_IDENTIFIABLE, never blank"],
   ["measurement_id", "yes", "measurement_method_id", "USDA/Bognar 3 MEAS records; PE null", "expand MEAS to study-level methods in MP-5A", "UNKNOWN"],
   ["ingredient_id", "yes (or explicit raw_name + UNRESOLVED)", "matrix.ingredient_id", "11,569 of 17,978 (64%)", "keep; unresolved stays UNRESOLVED", "null + matrix.raw_name"],
   ["matrix_id", "no (v1)", "NONE (matrix is an object: raw_name, food_group, variety, part, form, prior_processing, initial_state, geometry, storage_ripeness)", "raw_name 100%; other facets mostly null", "ADD matrix_id as a hash of the normalised matrix object in the export view; no ledger rewrite", "null"],
   ["prior_state_id", "no (v1)", "matrix.initial_state (free text) + matrix.prior_processing", "PE initial_state populated; USDA/Bognar mostly null", "ADD controlled vocabulary + id in MP-5A; free text kept", "UNKNOWN"],
   ["process_id", "yes", "process.process_id", "17,821 of 17,978 (99%)", "keep", "null + process.raw_name"],
   ["condition_id", "yes", "process.condition_id", "100% (COND 4,414)", "keep", "COND completeness_mask axes UNKNOWN"],
   ["target_state_variable_id", "yes", "target.state_variable_id", "100% (224 SVAR)", "keep; map duplicates to canonical_variable_id (state_variable_registry_v1)", NA],
   ["before_value", "no", "before.{status,value,low,high,unit,uncertainty,censor,raw}", "PE 3,870 MEASURED; USDA/Bognar status None", "keep nested form; export flattens", "status UNKNOWN or NOT_REPORTED, never 0"],
   ["after_value", "no", "after.{...}", "same", "keep", "same"],
   ["delta_value", "no", "derived.delta", "absent in all rows", "derive deterministically where before and after both MEASURED (provenance DERIVED_DETERMINISTIC)", "absent"],
   ["direction", "no", "derived.direction", "100% (17,978; UNKNOWN allowed)", "keep", "UNKNOWN"],
   ["retention_fraction", "no", "derived.retention_factor", "USDA 4,374 measured / 2,620 censored / 24 unknown; Bognar 3,320 / 3,274 / 0; PE 3,870 measured", "keep; censored kept censored", "absent; never imputed to 0 or 1"],
   ["log_fold_change", "no", "derived.log_fold_change", "absent in all rows", "derive deterministically where before, after > 0 (DERIVED_DETERMINISTIC); for retention-only rows ln(RF) only if RF > 0 and not censored", "absent"],
   ["yield_fraction", "no", "derived.yield_factor", "Bognar 496 measured (food mass); PE 3,870 attached from a separate yield source", "keep; PE yields carry yield_source in process.modifiers; not independent of the retention rows", "absent"],
   ["unit", "yes if a value exists", "before.unit / after.unit / derived.*.unit", "PE mg/100 g fresh weight|mL|dry weight; others fraction/percent", "keep; no silent conversion across bases", "null"],
   ["value_low / value_high", "no", "*.low / *.high", "sparse", "keep", "null"],
   ["measurement_method", "no", "measurement_method_id -> MEAS", "see measurement_id", "see measurement_id", "UNKNOWN"],
   ["evidence_tier", "yes", "tier", "E3 = 17,978", "keep field name `tier`; export alias evidence_tier", NA],
   ["provenance_class", "yes", "NONE (origin_type + provenance.method only)", "origin_type: DATABASE_AGGREGATE 14,108; PRIMARY_STUDY 3,870", "ADD provenance_class (registry/provenance_class_registry_v1.csv) in the export view; backfill by rule: all current rows EXPLICIT_SOURCE except derived fields DERIVED_DETERMINISTIC", "UNKNOWN"],
   ["censoring_flag", "yes", "censored (bool) + *.censor object", "5,894 censored", "keep", "false only if source states exact value"],
   ["lod / loq", "no", "NONE as columns (censor.kind/limit inside derived)", "censor limits only for USDA/Bognar", "ADD explicit lod / loq in the export view where the source gives them", "null"],
   ["condition_completeness", "yes", "COND.completeness_mask", "temperature known 6,015; duration known 3,083; moisture/pH/aw 0", "keep; per-axis UNKNOWN is a valid value", "UNKNOWN per axis"],
   ["confidence", "no", "NONE (applicability + verification.status)", "applicability EXACT/GENERIC/NEAR", "ADD only if a calibrated definition is agreed; do not invent a score", "null"],
   ["notes", "no", "notes", "sparse", "keep", "null"]])

# ---------------- simulation schema (schema only; no rows) ----------------
w("simulated_state_changes_schema_v1.csv",
  ["field", "type", "required", "constraint / semantics"],
  [["simulation_id", "string", "yes", "SIM-######; minted by ID minter; never reused"],
   ["ingredient_id_or_entity", "string", "yes", "ING id or ENTITY version id"],
   ["matrix_descriptor", "object", "yes", "geometry, initial moisture, composition inputs actually used"],
   ["process_id", "string", "yes", "PROC id"],
   ["conditions", "object", "yes", "full COND-equivalent inputs (temperature trajectory, medium, time, pressure ...)"],
   ["input_state", "object", "yes", "factorised state S_t with masks"],
   ["predicted_output_state", "object", "yes", "factorised S_t+1 for supported variables only; all else UNKNOWN"],
   ["state_variable_ids", "array", "yes", "must be a subset of the simulator's declared validated scope"],
   ["simulator_id", "string", "yes", "registry entry with equations/assumptions"],
   ["simulator_version", "string", "yes", "code hash or release"],
   ["parameters", "object", "yes", "all parameters with source or SIMULATED_PARAMETER flag"],
   ["uncertainty", "object", "yes", "interval or distribution; unquantified = UNKNOWN, not 0"],
   ["validation_scope", "object", "yes", "variables, matrices, condition ranges where validated against E1-E4 data"],
   ["extrapolation_flag", "bool", "yes", "true outside validation_scope"],
   ["provenance_class", "enum", "yes", "SIMULATED (only value allowed)"],
   ["evidence_tier", "enum", "yes", "E7 (only value allowed)"],
   ["may_enter_gold_evaluation", "bool", "yes", "always false"],
   ["created_at", "datetime", "yes", ""],
   ["notes", "string", "no", ""]])

# ---------------- human verification queue (tasks over existing artifacts; no invented evidence) ----------------
w("human_verification_queue.csv",
  ["task_id", "type", "artifact", "rows_or_items", "priority", "primary_reviewer", "secondary_reviewer", "blind_required", "adjudication_required", "blocking_dependency", "status"],
  [["HV-001", "E4 evidence verification (first milestone)", "registry/evidence/verification_queue_ranked_v1.csv", "634 ranked literature rows (0 verified); first target >=40, aim 60-80 across several mechanisms", 1, "Kush", "Parv (audit sample, predeclared)", "no", "on disagreement", "MP-1 contracts reviewed; MP-5A schema", "NOT_STARTED"],
   ["HV-002", "mechanism evidence verification (zero-row cells)", "to be created in MP-5B (garlic/onion alliinase-LFS, potato acrylamide, broccoli/cabbage myrosinase, chlorophyll, PPO, dough, rice, beef)", "TBD (not populated)", 1, "Kush", "Parv (two-person verification for benchmark-critical rows)", "yes for benchmark-critical rows", "yes", "HV-001 protocol; MP-5B extraction", "PLANNED"],
   ["HV-003", "E3 AI_PRECHECKED rows sample audit", "ledgers/data/EVD.jsonl (Phenol-Explorer)", "3,870 AI_PRECHECKED; audit sample size to be predeclared", 2, "Parv", "Kush", "no", "on disagreement", "none", "NOT_STARTED"],
   ["HV-004", "Gold recipe/state verification", "annotation/gold/foodcom_ai_assisted_v1_1", "20 recipes (AI-assisted, not independent); 310 events", 2, "Parv (blind pass)", "Kush", "yes", "yes", "none", "BLOCKED_HUMAN"],
   ["HV-005", "S116 Food.com eligibility", "annotation/gold/evidence_first_expansion/s116_eligibility_confirmation_sheet.csv", "84 rows (54 selected + 30 audit); 0 confirmed", 2, "Kush", "-", "no", "no", "none", "BLOCKED_HUMAN"],
   ["HV-006", "scripted session review", "annotation/sessions/SES-*.json", "30 AI-drafted sessions", 3, "Kush", "Parv", "no", "no", "none", "NOT_STARTED"],
   ["HV-007", "H_STATE question authoring (EXP-000007)", "benchmark/h_state/questions_to_write.csv", "53 current slots (14 supported pairs max); layout update pending", 3, "Kush", "-", "no", "no", "ledger evidence coverage (MP-5)", "BLOCKED_HUMAN"],
   ["HV-008", "EVD ingredient-link holds", "registry/evidence/evd_ingredient_link_decisions.csv", "129 held, 23 concept-missing", 3, "Kush", "-", "no", "no", "none", "NOT_STARTED"],
   ["HV-009", "allergen table sign-off", "registry/allergens/ing_allergen_review.csv", "8 ALLERGEN records", 4, "Kush", "-", "no", "no", "none", "NOT_STARTED"],
   ["HV-010", "process mechanism-family verification", "ledgers/data/PROC.jsonl", "93 PROC with AI-drafted mechanism_families", 3, "Parv", "Kush", "no", "no", "HV-001 protocol", "NOT_STARTED"]])

# ---------------- similarity registry (FROZEN v1) ----------------
SH = ["id", "registry_version", "freeze_status", "similarity_type", "OBJECT_A", "OBJECT_B", "REPRESENTATION", "METRIC", "REQUIRED_DATA", "CONFOUNDS", "BASELINE", "GOLD_REQUIREMENT", "allowed_learned_representation", "ssot_section", "CURRENT_STATUS"]
V = ("v1", "FROZEN")
S = [
    ["SIM-01", "exact molecular identity", "molecule", "molecule", "InChIKey (stereochemistry kept)", "equality", "MOL ledger", "identifier errors, salts/stereo conventions", "none (identity)", "none", "none", "SSOT 132, 142.1 E0", "available: MOL 1,726 with InChIKey"],
    ["SIM-02", "shared-compound overlap (E0)", "ingredient", "ingredient", "set of molecule ids", "n_ij (shared count)", "IMAP presence", "profile size, source count, provenance", "n_ij is the baseline", "none (descriptive)", "none", "SSOT 142.1 E0, 80", "data present (IMAP 30,294); metric not implemented"],
    ["SIM-03", "normalised profile overlap (E1)", "ingredient", "ingredient", "set of molecule ids", "Jaccard, Ochiai, IDF-weighted overlap, null percentile", "IMAP presence", "category/source strata; degree-preserving null; profile size", "n_ij", "none", "none", "SSOT 142.1 E1", "data present; metric not implemented"],
    ["SIM-04", "atom-environment similarity, ECFP radius 0", "molecule", "molecule", "Morgan/ECFP radius 0 (atom types only)", "Tanimoto on radius-0 environments", "canonical SMILES -> RDKit", "bit length/folding; size", "radius 2 is the frozen baseline", "none", "none (this is a diagnostic scale)", "SSOT 142.1 E2, 132", "DATA-MISSING (not stored; derivable)"],
    ["SIM-05", "atom-environment similarity, ECFP radius 1", "molecule", "molecule", "Morgan/ECFP radius 1", "Tanimoto", "canonical SMILES -> RDKit", "same", "radius 2", "none", "none", "SSOT 142.1 E2", "DATA-MISSING (derivable)"],
    ["SIM-06", "atom-environment similarity, ECFP radius 2 (frozen baseline fingerprint)", "molecule", "molecule", "Morgan r2, 2048-bit, chirality on, binary", "Tanimoto (Dice excluded: monotone transform)", "canonical SMILES -> RDKit", "bit length (4096 sensitivity), count/MinMax variants, size effects; no universal cutoff", "this is the baseline", "none", "none", "SSOT 142.1 E2", "DATA-MISSING (derivable)"],
    ["SIM-07", "atom-environment similarity, ECFP radius 3", "molecule", "molecule", "Morgan/ECFP radius 3", "Tanimoto", "canonical SMILES -> RDKit", "same", "radius 2", "none", "none", "SSOT 142.1 E2", "DATA-MISSING (derivable)"],
    ["SIM-08", "fingerprint family similarity (MACCS/path/FCFP/PubChem 881)", "molecule", "molecule", "MACCS, path, FCFP, PubChem cactvs 881", "Tanimoto / MinMax", "SMILES; PubChem fp stored", "family choice is an ablation axis", "Morgan r2 2048", "none", "none", "SSOT 142.1 E2 sensitivity", "PARTIAL (PubChem 881 stored only)"],
    ["SIM-09", "scaffold / functional-group / class similarity", "molecule", "molecule", "Murcko scaffold; reactive-motif counts; class label", "scaffold identity; count-vector distance; class match", "SMILES; class ontology NOT selected", "class label quality; scaffold-split leakage", "ECFP r2", "none", "none", "SSOT 143 T0, 135", "DATA-MISSING / RESEARCH-REQUIRED (class ontology source)"],
    ["SIM-10", "ingredient molecule-set similarity", "ingredient", "ingredient", "weighted molecule set (presence, concentration, OAV where evidenced)", "kernel mean over Tanimoto; balanced OT (candidate); max/top-k/matching", "IMAP + MOL fingerprints", "profile size, source count; cardinality-matched downsampling", "kernel mean of Tanimoto", "none", "learned z_i must beat it", "SSOT 142.1 E2 ingredient, 179", "MISSING (metric not implemented)"],
    ["SIM-11", "state-dependent chemical composition similarity", "ingredient state S_t", "ingredient state S_t'", "masked composition vector at each level", "level-wise distance restricted to evidenced variables", "EVD before/after, IMAP PROCESS_CHANGE (419)", "missingness mask; censoring", "persistence (S_t+1 = S_t)", "yes: E1-E4 composition pairs", "learned z_{i,t} must beat it", "SSOT 106-107, 141", "DATA-MISSING (compositions sparse)"],
    ["SIM-12", "process-conditioned change in similarity", "(A_t, B_t)", "(A_t+1, B_t+1)", "per-level delta of SIM-02..SIM-11", "change in similarity under a process; includes reaction-center edit distance", "transition evidence + reaction catalogue", "mechanism-class confounds", "persistence", "yes: process-disjoint E1-E4", "none yet", "SSOT 141, 209-216", "DATA-MISSING / RESEARCH-REQUIRED (RXN has 0 rows; reaction-center similarity cannot be defined yet)"],
    ["SIM-13", "reaction-center similarity", "reaction", "reaction", "reaction SMARTS / bond-edit graph", "edit-set overlap", "RXN ledger", "mapping errors", "none", "yes", "none", "SSOT 135, 143 T2-T3", "DATA-MISSING / RESEARCH-REQUIRED"],
    ["SIM-14", "learned chemical similarity", "molecule / ingredient", "molecule / ingredient", "z_m, z_i", "cosine/Euclid in latent space", "MOL + IMAP", "frequency, profile size, source count", "ECFP r2 / descriptors", "two leakage-safe splits", "must beat ECFP/descriptors (G12 decision 1)", "SSOT 178-179, 183", "MISSING; defer"],
    ["SIM-15", "sensory similarity (separate space)", "ingredient / molecule", "ingredient / molecule", "descriptor / panel profile", "profile distance", "taste classes (ChemTastesDB 204), odor labels absent", "structural similarity is NOT sensory similarity", "structural similarity as the (non-)baseline", "yes: sensory benchmark", "none", "SSOT 145, 279.2", "PARTIAL data"],
    ["SIM-16", "nutritional similarity (separate space)", "ingredient", "ingredient", "nutrient vector", "vector distance (stated basis)", "FDC/FNDDS", "basis (dry/fresh), matrix", "none", "no", "none", "SSOT layer F", "PARTIAL"],
    ["SIM-17", "functional / culinary-role similarity (separate)", "ingredient", "ingredient in a role", "role label / context", "role match; substitutability judgement", "recipes, ING_ALTERNATIVE_TO (220)", "role context, cuisine", "co-occurrence", "yes: expert role labels", "none", "SSOT 186-194", "MISSING benchmark"],
    ["SIM-18", "substitution fitness (separate)", "ingredient (original)", "ingredient (candidate)", "recipe context + state", "calibrated acceptability", "substitution gold", "context dependence; cultural prior", "co-occurrence / SIM-17", "yes", "none", "SSOT 186-194, SX-14-05", "MISSING benchmark"],
    ["SIM-19", "cultural / co-occurrence similarity (separate)", "cuisine / ingredient", "cuisine / ingredient", "prevalence, authenticity, F_{i|c,t}", "fingerprint distance", "REC with cuisine (60,144)", "frequency, size, source; prevalence is not flavour similarity", "frequency / IDF", "held-out cuisine/period", "none", "SSOT 160, 265, 279.2", "MISSING"],
    ["SIM-20", "recipe similarity (separate)", "recipe", "recipe", "ingredient set, quantities, process sequence, state trajectory", "set/graph/trajectory similarity; calibrated same-family probability", "REC, Gold events", "recipe size, source, duplicates", "Jaccard", "yes: expert variants", "learned z_R must beat baseline", "SSOT 187-188, 279.1", "MISSING"],
    ["SIM-21", "cuisine similarity (separate)", "cuisine", "cuisine", "cuisine fingerprint", "explicit fingerprint distance", "REC with cuisine", "size, source, era", "explicit fingerprint", "non-circular held-out", "learned z_C must add value (G13-4)", "SSOT 189-190", "MISSING"],
]
w("ssot15_similarity_registry.csv", SH, [[s[0], *V, *s[1:]] for s in S])
