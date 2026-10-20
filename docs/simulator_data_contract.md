# Simulator data-fidelity contract (S116)
Every state-transition input to a future simulator carries a `source_class` (`src/culinarystate/state_graph/source_class.py`):
STRUCTURAL_RECIPE, COMPOSITION, MEASURED_TRANSITION, COMPILED_RETENTION, KINETIC, MOLECULAR_PRIOR, SENSORY_PRIOR, MODEL_GENERATED, SYNTHETIC,
plus source_id, source_record_id, evidence_tier, process, conditions, initial/final_state_support, uncertainty, licence, provenance.
**Permanent rule:** STRUCTURAL_RECIPE (recipe text, recipe APIs) may define that a process occurred. It may NOT by itself define the measured
physical/chemical magnitude of the transition. Only MEASURED_TRANSITION, COMPILED_RETENTION, KINETIC (or an explicitly labelled MODEL_GENERATED /
SYNTHETIC input with stated uncertainty) may carry a magnitude. Enforced by `TransitionInput` (tests/unit/test_external_data_policy.py).
Ingest policy (`sources/policy.py`): LIVE_ONLY / DO_NOT_STORE / licence-unresolved / research-only rows cannot enter canonical ledgers or datasets.
