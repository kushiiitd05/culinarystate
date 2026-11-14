# Step 31 effect-card boundary amendment — 12 November 2026

**AI_DRAFTED / PROPOSED_IMPLEMENTATION_CARD / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**
This named card records the existing D-080 #16 decision (T4-C22-R1); it is not a new scientific run, a signature or a release. Step 31 remains after 25 November under that decision.

## Data and prediction unit

The permitted first arm uses **EVD rows**, not recipe events. An EVD point, interval or censor bound retains its target, food/matrix, process, condition, source/study and quantity basis, plus explicit missingness masks. A source reference-table row does not become an independent experiment. Derived source values and unverified E3 provenance remain visible. Preserve censor type/direction; never train a point target by silently substituting a limit or midpoint.

**No recipe-event arm containing Layer 2 features is permitted by this card.** TEXT_STATED recipe input is distinct from an imported EVD condition. SCENARIO/default, corpus-quantile and MODEL_DERIVED features may not silently enter the first arm as observed conditions or labels. The current recipe physical fields are diagnostic and do not supply missing experimental measurements.

## Required card fields before any later run

| Field | Required entry |
|---|---|
| source snapshot | Exact immutable EVD/COND/SRC/DOC/lineage manifests and hashes; no protected snapshot overwrite |
| label definition | Named target/analyte/quantity basis; MEASURED/RANGE/CENSORED/UNKNOWN handling; excluded rows and reasons |
| feature contract | Explicit metadata-only field allowlist and masks; no recipe Layer 2 field; no label-derived/leakage feature |
| grouping | Study/source and matrix/process grouping with positive overlaps disclosed; provisional lineage is not independence |
| splits | Frozen train/calibration/dev/test IDs and seed before fit; diagnostic/source-stratified is not source-heldout |
| baselines | Applicable original static/persistence and equal-capacity comparators, exact configurations |
| evaluation | Predeclared task/metrics/intervals and practical rule; source-family denominators; no retroactive tune on D5 |
| claim status | DIAGNOSTIC / NON_CITABLE until its own criteria are met; no inherited scientific pass from engineering |

A later Layer 2 arm requires a **separate dated preregistered ablation**, a permuted-registry control and an equal-capacity comparator (D-080 #16). Freeze its features, labels, source controls and outputs before evaluation; report it beside the EVD-only arm. No such arm or amendment adoption is supplied here.

## Current outcome

- Named Step 31 card proposal: present (this artifact).
- D-entry: existing D-080 #16, preserved; no new choice inferred.
- Step 31 experiment: NOT_RUN; scientific gates and scope unchanged.
- Engineering interface consequence: no new runtime or data field is authorized or installed by this card.
