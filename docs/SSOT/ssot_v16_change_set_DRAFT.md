# SSOT v16 — proposed change set (DRAFT, NOT APPLIED)

**Status: PROPOSED_ONLY. SSOT v15 was NOT edited.** Source: `ssot_change_requests_v2.md` (65 requests, CR-01…CR-65) from the Max/Ultra audit, a draft whose critique round was skipped. I read the summary of every request; I did not open every SSOT line it cites, so each line reference below is UNVERIFIED until checked against `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md`. Per §139 the SSOT is appended to, not rewritten.

Rule for this file: a change goes into v16 only if it (a) adds a crosswalk, definition or missing field without weakening any law or gate, or (b) is a data-contract addition needed by a step that is about to run. Anything that decides a scientific choice (e.g. the first simulator) is HOLD until the data in Steps 10/11 exist.

## A. Adopt in v16 now — crosswalks and consistency (no scientific change)
CR-01, CR-36 (tier E1–E6 vs repo E1–E7; publish crosswalk, namespace `TIER-E#`) · CR-02 (three orthogonal fields: origin_provenance / field_status / claim_route) · CR-05 (mark stale status lines "superseded", add artifact-to-repo-path map) · CR-06, CR-62 (six data planes + REFERENCE and GOVERNANCE layers; SIMULATION stays separate) · CR-07, CR-51 (one missingness/censoring superset; UNKNOWN ≠ 0) · CR-08, CR-29 (single NEEDS_HUMAN_REVIEW enum; endpoint handling) · CR-37 (rename ablation family KA0–KA6) · CR-41 (align minimum package with D0–D7) · CR-45, CR-46 (relabel preprint evidence; FlavorDB vs FlavorDB2 counts/licence UNVERIFIED) · CR-47, CR-48, CR-50, CR-54 (representation-ladder naming/definition clarifications; ECFP4/Morgan + LightGBM as the single reference) · CR-27 (10k pilot needs all 257P items except P-A11) · CR-22 (257D is a phrase inventory, not a Gold test catalog) · CR-63 (simulated sessions development-only).

## B. Adopt in v16 now — data-contract additions the next steps need
- **Independence keys (CR-03, CR-09, CR-40):** `study_id`, `lineage_root_id` (statistical unit), `split_group_id` (evaluation unit), `independence_resolution` ∈ {STUDY, PUBLICATION_ONLY, SOURCE_FAMILY_ONLY, UNKNOWN}; UNKNOWN never in test sets; G15-1 audits status completeness, not study presence.
- **Recipe split unit (CR-04, CR-28, CR-49):** keep `duplicate_group_id` exact; add recall-oriented, calibrated `split_group_id` (from 07I-C) as the mandatory split unit. No destructive merge.
- **Evidence hierarchy annex (CR-10):** SOURCE→DOCUMENT→STUDY→EXPERIMENT→SAMPLE→MEASUREMENT→AGGREGATE→DERIVED with typed LINEAGE edges; EvidenceAtom remains the consumer view.
- **Measurement fields (CR-11, CR-12, CR-17):** basis, statistic, dispersion type/value, n_biological/n_technical, censor_kind {GT_CAP, ROUNDED_INTERVAL, RANGE_ONLY, …} with limit/resolution, trajectory/time-point ids, extraction_method, licence_status, value_origin (incl. DIGITIZED), lab_group_id, regime D-A…D-D, K_rung.
- **Kinetic contract (CR-16, CR-31):** one canonical kinetic-experiment/trajectory table and parameter contract (union of the five lists + K_level, T_ref, fit range, origin AUTHOR_REPORTED vs PROJECT_REFIT, ci_method, partition, lineage ids).
- **Test-set honesty (CR-13, CR-14, CR-18):** E3 aggregates may form a test set only as an "unverified-aggregate bootstrap benchmark" and never for headline claims; a Split-6 pass needs a pre-registered minimum number of independent clusters (PROPOSED K=10) or the result is DIAGNOSTIC_ONLY; fallback named "publication-component CV".
- **Pre-registration rule (CR-43, CR-61, CR-38):** every G15/G16 gate's numeric operationalisation must be frozen in the step contract before the first locked-test read; changes are logged decisions and the old result is kept. Gives the PROPOSED calibration-damage rule (coverage drop > 0.03 or width increase > 20%) a decidable form.
- **Acquisition governance (CR-20, CR-21):** acquisition log + fixed random audit share (PROPOSED >= 30%); licence status annotated per source; occurrence datasets are plausibility-only, never process-effect evidence.
- **Recipe-state fields (CR-25, CR-26):** event fields (kind, implicit args, alternative group, modality, temporal relation, condition profile id, allocation basis); entity parentage/lifecycle; quantity intervals (`normalized_mass_low_g/high_g`, interval semantics, scope, measured state) — never collapse an interval to a fake gram value.
- **Gold governance (CR-23, CR-24, CR-64):** staged Deep Gold DG-0 → DG-1 → DG-2 → full only if CI analysis requires; Deep Gold annotated BLANK; model-assisted review allowed only for Gold-Light with `MODEL_ASSISTED_HUMAN_REVIEWED` provenance; AI-assisted/joint Gold cannot support calibration (G16-CAL).
- **Mechanism/simulation contracts (CR-30, CR-32, CR-35, CR-39, CR-42, CR-44):** separate calibration domain / validated domain / M&S limits; the MODEL/SIMULATE rung requires applicability PASS + no unresolved competing mechanism + all inputs observed + compatible parameters + in-domain; synthetic-prior controls (matched-volume wrong-physics control, calibration-leakage rule, per-row provenance); a G15-11 pass on recipe data licenses R0/R1 only; physics-feature ordering clarified; D3 included in the G15-9 comparator set.
- **RAG contract (CR-57…CR-61, CR-65):** rung enum DIRECT/INTERPOLATE/MODEL/QUALITATIVE/ASK/ABSTAIN with VOI-pre-emptive ASK and orthogonal conflict status; isotonic only with ~1,000+ labels; generic cross-encoder is a control; packet v2 fields; per-gate G16 thresholds pre-registered; LLM zero-shot/RAG baselines and frequency-preserving nulls for FlavorTwin. **Design now, implement later** — these are breaking changes for Step 36.
- **Other representation/temporal items (CR-52, CR-53, CR-55, CR-56):** raw→processed pairs are never invariance positives; keep G3/G4/G7 verbatim but mark DATA-BLOCKED with separate available-task gates; add AUTHOR_BIRTH_PROXY / DOCUMENT_UPLOAD_DATE to `date_basis` and forbid using them as recipe-origin dates; split E13E-05 into 05a (near-duplicate calibration, core, = 07I-C) and 05b (multiview variants).

## C. HOLD — do not put in v16 yet
- **CR-15, CR-33, CR-34 (ascorbic-acid degradation + leaching as the first simulator):** record as "default candidate, chosen by a pre-registered extractability census; chlorophyll fallback" in the plan notes. Do NOT change the SSOT anchor (§210.29A, §226.5 M3) until Steps 10/11 show enough independent time-series studies, product-temperature data and a way to separate leaching. It also departs from the SSOT's acrylamide anchor, so it needs an explicit human decision.
- **CR-19 (volatile acquisition conditional on an H8 decision):** needs the H8 scope decision first.

## D. Items with no SSOT change but a recorded ruling needed
Step 04 rulings C2–C8 (MP-1 contract status), the Step-08 prerequisite (07-DEP), and the D-008 benchmark task-type decision. These belong in `DECISIONS.md`, not the SSOT.

## E. Checks before any of this is applied
1. Open every cited SSOT line range and confirm the quoted "current text" matches v15.
2. Check the claims that only exist as the audit's reading (e.g. SSOT E1–E6 tier text, §215/§216 gate wording).
3. Apply as an appended v16 addendum (§139), not as in-place edits; keep v15 intact.
4. Each applied CR gets a `DECISIONS.md` entry. The audit's own proposed "D-026/D-027" numbering must be reconciled with the actual D-026 (usage decision): the authority ruling becomes D-027.

*End of draft.*
