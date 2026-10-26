# Step 04.1 — Evidence entity, lineage and independence contract v1.1

**Status: DRAFT_PENDING_H4.** Written 2026-10-26 under D-027 / Execution Plan v2 §7 as contract and documentation work only. Not approved, not frozen, not applied. Numeric values that appear here are PROPOSED_PILOT (their registry is `registry/preregistered_thresholds_v1.csv`, unsigned). Step 08 is not started and not authorised by this document.

**Revision r1 (2026-10-26, same day, still DRAFT_PENDING_H4):** the governance review (A) and the scientific review (B) of this draft were applied. New or changed rules are marked PROPOSED and carry an H4 decision (D-11..D-17, §7); every threshold added or edited is PROPOSED_PILOT and unsigned (`registry/preregistered_thresholds_v1.csv`, 47 rows). Nothing in this revision is approved, signed or frozen.

Authority: R-03 (lineage extension SRC → DOC → STUDY → SEXP → SMP → OBS → AGG/DRV, typed edges, three separate keys), R-04 (companion: `kinetic_trajectory_contract_v1.md`), R-08 (plane-qualified split groups), R-02 (additive only; Steps 01–07 are not reopened), R-20 (laws). Plan anchors: Step 04 card 04.1, Step 08 card, §7 "Exact next authorised step", CHG-04-1 / CHG-04-7.
Research basis: `reports/master_plan/working_notes/research/r_evidence_model.md` (cited below as RE), `r_simulator_vv.md` (RV), `r_acquisition.md` (RA). Source tags (VERIFIED / UNVERIFIED) are those notes' own and were not re-checked.

Laws applied throughout: UNKNOWN ≠ 0 (nullable with an explicit status, never a default 0); raw preserved, normalisation is a new field; append-only, ids never reused; no invented scientific value; AI review ≠ human verification; simulation ≠ measured evidence.

Companion drafts (all `DRAFT_PENDING_H4`): `registry/schemas/{DOC,LIN,SEXP,SMP,OBS,AGG,DRV}.draft_v1_1.schema.json` (draft 2020-12, same envelope as `ledgers/schemas/*`), `04_2_min_value_documentation.md`, `04_6_min_data_plane_rules.md`, `04_9_min_namespace_reservation.md`, `kinetic_trajectory_contract_v1.md`.

---

## 1. Entity model

### 1.1 The chain

```
SRC ──< DOC          DOC *──* STUDY  (stored on STUDY.report_doc_ids)      SNAP 0..1 ── 1 DOC
STUDY ──< SEXP ──< SMP ──< OBS          SMP ──(derived_from)──> parent SMP
SEXP ──< KIN ──< KINPT ──(exactly one)──> OBS
AGG  = compiled value;  parent_ids = OBS/AGG, or none (member lineage NOT_IDENTIFIABLE)
DRV  = derived value;   parent_ids = OBS/AGG/DRV/KIN/KINPT, at least one
LIN  = typed edges between SRC / DOC / STUDY / SEXP / SMP / OBS / AGG / DRV nodes (KIN and PARAM may be nodes of QUOTES_VALUES_FROM, KIN of SHARES_SAMPLES_WITH)
EVD  = the consumer-facing evidence-atom VIEW over this graph (unchanged contract; gains pointers)
```

### 1.2 Entities

| Entity | Prefix | Definition (and standard analogue) | Cardinality | Mandatory fields (explicit status where a value may be unknown) | Mint key (idempotent, `IdMinter` style) |
|---|---|---|---|---|---|
| Source | `SRC-` (exists) | Publisher-level origin: article, database release, book, review, web page, dataset, authority, project. EuroFIR "Reference"; PROV Entity + Agent. | SRC 1—* DOC (0 allowed: cited but never held) | existing SRC schema (kind, title, licence, licence_status, storage_rule, source_family_id …) | existing |
| Snapshot | `SNAP-` (exists) | Hashed retrieval of a source file. | SNAP 0..1—1 DOC | existing | existing (`sha256:<hex>`) |
| Document | `DOC-` | The concrete manifestation **actually read**: PDF, HTML snapshot, table file, release text, metadata record. PROV specializationOf / alternateOf. A cited-but-never-held publication is an SRC, not a DOC. | DOC *—1 SRC; DOC 0..1—1 SNAP; DOC *—* STUDY (stored on the STUDY side, §2.3) | `src_id`, `snapshot_id` (nullable), `sha256`, `doc_kind`, `content_access`, `report_kind`, `is_compilation_hub` (YES / NO / UNKNOWN), `authorship` (authors_raw[], affiliations_raw[], corresponding_author_raw, year_published; status READ_FROM_DOCUMENT / FROM_METADATA_RECORD / NOT_AVAILABLE / UNKNOWN), `version_label`, `identifiers`, `licence_status`, `storage_rule` | `<src_id>\|sha256:<hex>` (SNAP's key is `sha256:<hex>` alone; the same bytes held under two SRC would otherwise mint one DOC with two `src_id`: D-11) |
| Study | `STUDY-` (exists) | The data-generating campaign: Cochrane's "study, not report"; ISA Study. `NOT_IDENTIFIABLE` is allowed and never fabricated. | STUDY 1—* SEXP; STUDY *—* DOC | existing STUDY schema (125 rows, all `design = UNKNOWN`); additive v1.1 fields in Appendix A | existing |
| Scientific experiment | `SEXP-` | One comparison set within a study: the factors varied plus the shared reference. ISA Assay / factor set. **Not** `EXP-` (ML/benchmark run, keeps its meaning). | SEXP *—1 STUDY; SEXP 1—* SMP; SEXP 1—* KIN | `study_id`, `comparison_type`, `factors_varied[]`, `reference_design`, `borrowed_reference_sample_ids[]`, `condition_ids[]` + `condition_status`, `protocol_locator`; optional `context` (an absent key means UNKNOWN = not assessed; NOT_REPORTED is written explicitly when the source was read and is silent; the plan card says "default NOT_REPORTED": D-17) | `<study_id>\|<label or ordinal>` |
| Sample | `SMP-` | Food material at a state within one experiment (faceted description, LanguaL/FoodOn-style). ISA Sample, SOSA Sample. | SMP *—1 SEXP; SMP 1—* OBS; SMP 0..1—1 parent SMP | `sexp_id`, `role` (REFERENCE_BEFORE / TREATED_AFTER / INTERMEDIATE / COOKING_MEDIUM / BLANK / UNKNOWN), `derived_from{status,sample_id,process,condition}`, `matrix{…}`, `pooled`, `material_origin{batch / cultivar / purchase-or-harvest, as printed}`, `n_biological_units` | `<sexp_id>\|<label or ordinal>` |
| Observation | `OBS-` | One property value of one sample by one method. SOSA Observation; EuroFIR "Value". **Not** `MEAS-` (the method). | OBS *—1 SMP; OBS *—1 SVAR; OBS 0..1 MEAS; OBS 0..1 COND | value, statistic, n_biological / n_technical, dispersion (type!), censoring, LOD / LOQ, basis (+ `basis_raw`, required), retention_definition (+ evidence), method_indicator, method ref, condition ref, value_origin, locator, `series_link` (R-04 guard), `measurement_dedup` (one canonical OBS per measurement across reports), licence_status — see `04_2_min_value_documentation.md` | `<sample_id>\|<svar>\|<compartment>\|<locator key>` |
| Aggregate | `AGG-` | A compiled value over measurements or studies (database or review row; FAO "reference/user level"). Members may be unidentifiable. | AGG *—* OBS/AGG (`parent_ids`) or none | compiler SRC, aggregation_method, `member_lineage_status`, `membership_screen_status`, `parent_ids`, `n_members`, `imputation`, lineage block, plus the OBS value block | export-builder view key |
| Derived value | `DRV-` | Deterministic computation from ≥ 1 parent (delta, log quantities, true retention from yield, basis conversion, endpoint from series). PROV qualifiedDerivation. | DRV *—+ parents | `derived_quantity`, `formula_id` + version, `parent_ids` (ALL inputs), uncertainty / censor propagation, lineage block with parent union | export-builder view key |
| Lineage edge | `LIN-` | Typed relation between two nodes (§3). | n/a | `from_id`, `to_id`, `edge_type`, `detection_method`, `detector_level`, `score`, `edge_status`, `reviewer`, `rule_version` | `<edge_type>\|<from>\|<to>` |
| Kinetic series / point | `KIN-`, `KINPT-` | See `kinetic_trajectory_contract_v1.md` (04.3). | SEXP 1—* KIN 1—* KINPT 1—1 OBS | — | KIN `<sexp_id>\|<state_variable_id>\|<compartment>\|<temperature profile key>\|<locator key>`; KINPT `<kin_id>\|<sequence_index>\|<run_id or SINGLE>\|<unit_label or AGG>` |
| Evidence atom | `EVD-` (exists) | **Stays the consumer view** (SSOT L25248). Not replaced, not renumbered. | EVD 1—1 {OBS, AGG or DRV} after export v2 | existing 27-field contract + pointers (Appendix A) | existing |

Bound but outside the chain (unchanged meaning): `MEAS-` = analytical **method** (3 rows today); `COND-` = condition profile; `SVAR-` = state variable; `EXP-` = ML/benchmark run; `XTR-` / `ADJ-` = Step-09 extraction and adjudication records (prefixes reserved, no schema here).

### 1.3 Distinctions that the contract keeps apart

study (campaign) ≠ report (DOC) ≠ experiment (SEXP) ≠ sample (SMP) ≠ observation (OBS) ≠ method (MEAS) ≠ ML experiment (EXP) ≠ aggregate (AGG) ≠ derived value (DRV). Five web pages repeating one paper are **one** lineage, not five studies (SSOT L25307–25310; Cochrane ch. 5: "It is wrong to consider multiple reports of the same study as if they are multiple studies", RE Q3).

### 1.4 Status vocabulary (used by every draft schema)

| Token | Meaning |
|---|---|
| `NOT_REPORTED` | The source was read and is silent. |
| `UNKNOWN` | Not assessed, or cannot be told. Never replaced by 0 or a default. |
| `NOT_APPLICABLE` | The field does not apply to this record. |
| `NOT_IDENTIFIABLE` | (study / member lineage) The source does not allow the study or members to be named. Never fabricated; allowed to stand permanently. |
| `PENDING` | Not computed yet (lineage assignment only). |

---

## 2. Non-destructive mapping of what exists

### 2.1 Existing artefacts

| Existing | Today (plan/ledger counts) | Role under v1.1 | Change |
|---|---|---|---|
| `SRC` | 609 lines / 488 ACTIVE | Source level | none; `DOC.src_id` points here; yield-source publications referenced only by a string (PE) become new SRC nodes in 08a.2 (append) |
| `SNAP` | 347 | Hashed retrieval | none; `DOC.snapshot_id` reuses it; `DOC.sha256` must equal `SNAP.sha256` when both exist (semantic validator) |
| `STUDY` | 125, all `design = UNKNOWN` | Study level | none now; appended versions in 08a.2 (Appendix A); `design` stays UNKNOWN unless stated |
| `MEAS` | 3 rows = methods | Method referenced by `OBS.method.method_id` | none; **never** repurposed as "measurement" |
| `COND` | 4,746 lines | Condition profile referenced by SMP / OBS / KIN | none; normaliser stays frozen (07H-R fingerprint `e7d58913…`) |
| `SVAR` | SVAR ledger (224 ids per the EVD contract) and the 254-row registry | Target variable | none |
| `EVD` | 17,978 ACTIVE / 18,156 ids / 57,280 lines, all E3 | Consumer view | none to the ledger or to export v1 (`e61d7db4…`); export v2 (05.1) adds pointers |
| `EXP` | 7 ids (8 ledger lines) | ML runs | none; prefix never reused |
| `independence_group` (EVD field, 127 values) | USDA 1, Bognár 1, PE 125 | **B0 baseline partition** (kept as `independence_group_b0` in the registry, §4.8) | not authoritative any more; kept for the detector comparison |

### 2.2 Intended materialisation of the legacy EVD rows (to be verified and executed in 08a, which is not authorised)

| Legacy family | Rows | Target entities | Resolution |
|---|---|---|---|
| USDA R6 retention | 7,018 | AGG per row; `compiler_src_id` SRC-000001; DOC = the R6 release file; `member_lineage_status = NOT_IDENTIFIABLE`; `method_indicator = IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE`; `value_origin = SOURCE_IMPUTATION_POSSIBLE`; censoring GT_CAP with the cap kept as printed in `limit_low` (100) and `resolution` 5 (notes "nearest 5%", "values > 100 reported as 100", RE Q2; a reported 100 means true >= 97.5, derived as a NEW field `limit_low - resolution/2`, never by overwriting the printed cap; one `censoring.kind` cannot carry GT_CAP and ROUNDED_INTERVAL at once); `retention_definition = TR_OR_AR_UNDISCLOSED`; `membership_screen_status = NOT_SCREENED` until the R6 bibliography is screened | `SOURCE_FAMILY_ONLY` |
| Bognár 2002 | 7,090 (6,594 retention + 496 yield) | AGG per row; `retention_definition = TRUE_MURPHY` (RT-001; `retention_definition_evidence` set from the source text in 08a, UNKNOWN until read); yield rows are AGG with the food-mass SVAR | `SOURCE_FAMILY_ONLY` |
| Phenol-Explorer | 3,870 over 125 papers | per row: two OBS on two SMP (REFERENCE_BEFORE, TREATED_AFTER) in one SEXP of the paper's STUDY; where the retention factor uses a **yield factor from another publication** (MP-1 C5: 103 distinct yield records, to be verified): DRV with parents {OBS after, OBS before, yield OBS/AGG} and `parent_roles` (YIELD_FACTOR); `retention_definition = TRUE_MURPHY` with evidence `STATED_IN_SECONDARY` (keeps the D-020 ambiguity explicit); the PE release DOC is a hub (`is_compilation_hub = YES`) used only as `OBS.locator.doc_id`, never as a report DOC of the 125 STUDY rows (hub rule, §4.2 step 2a) | `PUBLICATION_ONLY` until experiment boundaries inside a paper are confirmed |

Nothing is materialised by this document. Only the target shapes are fixed here.

### 2.3 What the existing schemas would need (additive, not applied; goes into the 04.8-min / 05.1 diff proposal)

See Appendix A. No existing schema file is edited by this draft. `ledgers/schemas/*.schema.json` are generated from `src/culinarystate/ledgers/registry.py` (`tools/export_schemas.py`), so copying the drafts into `ledgers/schemas/` (CHG-04-7, done by 08a) must go through that registry or the files would be overwritten at the next export (decision D-6 in §7).

---

## 3. Typed LIN edge vocabulary

### 3.1 Registry (draft content of `registry/lineage_edge_type_registry_v1.csv`)

Direction for directed types: `from` = the quoting / newer / compiling / citing node; `to` = the quoted / older / primary / cited node. Symmetric types are stored once with `from_id < to_id`.

| edge_type | merge class | Sym. | Allowed `from → to` node types | Definition | Typical detector (ladder §3.4) | Justification (research) |
|---|---|---|---|---|---|---|
| `SAME_STUDY_AS` | MERGING (lineage_root) | yes | DOC / STUDY / SRC, any mix (SRC admitted so that a publication that is cited but never held — the Phenol-Explorer primaries — can be linked by B1 DOI matching without a STUDY stub) | Two documents (or study records) report the same data-generating campaign: companion papers, duplicate or covert duplicate publications, thesis and its journal paper. | B1 DOI/PMID/title exact; B2 fuzzy title/authors (PROVISIONAL) | Cochrane ch. 5 (link reports of one study; compare data lists); Tramèr 1997 (17% of full reports and 28% of patient data duplicated, effect inflated 23%); von Elm 2004 (6 duplication patterns; 64% of duplicates had different authorship, so authorship is unreliable and matching needs data fingerprints) (RE Q3, Q5). RA §5: link a thesis and its journal paper (Knol thesis ↔ JAFC 2005). |
| `QUOTES_VALUES_FROM` | MERGING | no | SRC/DOC/STUDY/AGG/OBS/DRV/KIN/PARAM → SRC/DOC/STUDY/AGG/OBS/KIN/PARAM (KIN: a review that re-plots a primary series; PARAM: a compendium that re-reports k / Ea — the "re-report edges" the Step 26 / 27 leakage proofs require) | Values were copied or tabulated from another source (review table, web repost, database row quoting a paper). PROV Quotation. | B3 numeric fingerprint over (matrix, analyte, unit, value tuple); review-vs-primary flag (Step 09) | SSOT lineage law L25307–25310 and checklist step 7; FAO Greenfield & Southgate ch. 10 warns that tracing values in secondary tables "leads only to another set of tables" (circular lineage) (RE Q2). Re-pooling a copy with its original double-counts. A quoting hub is linked PER RECORD (record -> primary), never hub -> primary (§4.2 step 2a). |
| `ALTERNATE_OF` | MERGING | no | DOC → DOC | Same document, other manifestation (PDF vs HTML, preprint vs accepted manuscript). PROV alternateOf. | B1 DOI / file hash / exact title | PROV-DM (RE Q1); FAIR R1.2 provenance of manifestations. |
| `REVISION_OF` | MERGING | no | SRC/DOC → SRC/DOC | A later release or corrected edition of an earlier one (USDA R6 release n+1; Phenol-Explorer 3.0 → 3.6). PROV Revision. | B1 version string / identifier chain | PROV-DM Revision; EuroFIR Acquisition Type "host system" (RE Q1, Q2). |
| `SHARES_SAMPLES_WITH` | MERGING | yes | STUDY/SEXP/SMP/KIN (any mix) | Two studies or experiments report measurements on the **same physical samples** (secondary analyses, companion measurements of one batch). | B3 fingerprint of (matrix, n, values); author/lab + batch statements | ISA material graph (one source → many assays); Cochrane 23.3.4 and Lajeunesse 2011: shared units give correlated effect sizes (RE Q1, Q3). |
| `PRIMARY_SOURCE` | MERGING **iff** `membership_status = KNOWN`; otherwise GROUPING_DEFAULT | no | SRC/DOC/STUDY/AGG → SRC/DOC/STUDY | A compilation (database, review) lists a primary source for its values. PROV PrimarySource. Recorded per AGG record for KNOWN members; an edge from a hub node to a primary is never used to connect two primaries of the same hub (§4.2 step 2a). | STRONG: bibliography listing (R6 / Bognár / PE bibliographies; local availability UNVERIFIED) | FAO ch. 10 three-level database model (archival → reference → user); the compilation is not independent of its primaries (RE Q2). Wording of the Step 04 card: "when membership known". |
| `SAME_LAB_AS` | GROUPING_OPTIONAL_TIER (evidence plane in general); `lab_group_id` is MANDATORY on the kinetic plane | yes | SRC/DOC/STUDY | Same laboratory or research group, recall-oriented: shared corresponding / senior author OR the same affiliation unit within ±N years (N: THR-08A-22, value OPEN). The inputs are `DOC.authorship`; where authorship was not read the lab is UNKNOWN, never guessed. | author/affiliation match | RV §4 (Step 27 "unit of independence = research group / lab") and §5 item 2: several AA and carotenoid groups publish many papers; Step 27 wants group-level held-out validation. |
| `SHARES_REFERENCE_SAMPLE` | GROUPING_DEFAULT (PROVISIONAL) | yes | SEXP/SMP | Two experiments or samples are compared with one shared reference/control (one raw sample against boiled, steamed, fried), so the same `before` value is reused. | reused `before` value / same reference label | Cochrane 23.3.4: treatment arms sharing one control must not be treated as independent; Lajeunesse 2011; RE Q3. |
| `CITES` | NON_MERGING | no | SRC/DOC → SRC/DOC | Citation only. | any | Citation is not data re-use; kept for graph analysis, never merges. |

Merge classes, effect on keys:

| Class | `lineage_root_id` | `split_group_id` (default) | optional lab tier |
|---|---|---|---|
| MERGING | merges | merges (split ⊇ lineage) | merges |
| GROUPING_DEFAULT | no | merges | merges |
| GROUPING_OPTIONAL_TIER | no | no | merges |
| NON_MERGING | no | no | no |

All of the above apply to edges with `edge_status ≠ REJECTED`. PROVISIONAL edges merge (conservative merging costs test-set size, never validity). `REJECTED` edges are ignored but kept (append-only, with `rejection_reason`).

**Structural (implicit) edges** are not stored as LIN rows. Always merging for `lineage_root_id`: STUDY–its report DOCs (primary manifestations only; never a hub DOC), SEXP–STUDY, SMP–SEXP, OBS–SMP, and — **only for aggregates whose `member_lineage_status` is NOT_IDENTIFIABLE or PARTIAL** — DOC–SRC and AGG–`compiler_src_id` (the compiler node is then the source-family node). A locator DOC (`OBS.locator.doc_id`) is never a structural edge. AGG–its KNOWN `parent_ids` (equivalent to PRIMARY_SOURCE with known membership) is a per-record relation and obeys the hub rule of §4.2 step 2a. Acting **only at split level**: DRV–`parent_ids` (parent union, gate G08-2 — unchanged) and `borrowed_reference_sample_ids` (same-study only; cross-study sharing must be a `SHARES_SAMPLES_WITH` edge).

### 3.2 Crosswalk of other names in circulation

The Step 04 card names the nine types above; the brief for this draft used other names as examples. They are mapped, not added:

| Name in the brief | Where it lives in this contract |
|---|---|
| `REPORTS` (DOC reports STUDY) | structural relation: `STUDY.report_doc_ids` (Appendix A), not an edge |
| `REPUBLISHES` | `ALTERNATE_OF` (same document, other format), `QUOTES_VALUES_FROM` (values copied) or `REVISION_OF` (new release), by case |
| `COMPILES_FROM` | `PRIMARY_SOURCE` (+ `membership_status`) |
| `SHARES_SAMPLE` | `SHARES_SAMPLES_WITH` (physical samples) or `SHARES_REFERENCE_SAMPLE` (shared control) |
| `DERIVED_FROM` | `parent_ids` of AGG / DRV (single source of truth; a second LIN encoding would duplicate it) |
| `DUPLICATE_OF` | `SAME_STUDY_AS` with `detection_method` (DOI_MATCH, NUMERIC_FINGERPRINT …) |

### 3.3 Edge record

`id`, envelope, `from_id`, `to_id`, `edge_type`, `membership_status` (required for PRIMARY_SOURCE: KNOWN | UNKNOWN), `detection_method`, `detector_level` (B0, B1, B2, B3, STRONG, MANUAL), `score` (nullable, [0,1]) + `score_basis`, `matched_fields[]`, `evidence_note`, `edge_status` (PROVISIONAL | HUMAN_CONFIRMED | REJECTED), `reviewer`, `reviewed_at`, `rejection_reason`, `rule_version` (hashed, stamped on every output; 08b). Rules enforced by the draft schema (node types now include KIN / PARAM where §3.1 says so): `HUMAN_CONFIRMED` requires `reviewer ∈ {Kush, Parv}` and `reviewed_at` (AI review is never human confirmation); `REJECTED` requires a reason; node-type pairs per §3.1; a status change is a new version of the same LIN id.

### 3.4 Detector ladder (Step 08) and which edges each level may propose

B0 = the current `independence_group` partition (no edges; the baseline the other levels are compared against) → B1 DOI / PMID / exact title / file hash (`SAME_STUDY_AS`, `ALTERNATE_OF`, `REVISION_OF`) → B2 + fuzzy title / authors (`SAME_STUDY_AS`, PROVISIONAL) → B3 + numeric fingerprint (`QUOTES_VALUES_FROM`, `SHARES_SAMPLES_WITH`, PROVISIONAL until audited) → STRONG = B3 + bibliography listing (`PRIMARY_SOURCE`). Reporting how many merges each level adds is a Step-08 metric. A learned duplicate classifier is out of scope (no labels).

---

## 4. The three keys

### 4.1 Definitions

| Key | Meaning | Value | Role | Never |
|---|---|---|---|---|
| `study_id` | The data-generating campaign (Cochrane study). | `STUDY-######`, or null with `study_id_status ∈ {NOT_IDENTIFIABLE, NOT_APPLICABLE}` | pooling cluster id (RVE / three-level models), descriptive | fabricated; every non-null id needs a DOC locator (gate G08-8) |
| `lineage_root_id` | Connected component of nodes under MERGING edges (explicit and structural). | `LROOT-######` (proposed new prefix, §7 D-3) | **statistical unit**; counts "k independent lineages"; consensus / conflict counting | used as the evaluation unit |
| `split_group_id` | Component of the lineage components additionally merged by (a) GROUPING_DEFAULT edges, (b) the **parent union of every DRV and of every non-hub AGG** (a hub AGG with KNOWN members is never merged with its members: §4.2 step 2a(e)), (c) the **source-family node** for aggregates whose members are NOT_IDENTIFIABLE or PARTIAL. | evidence plane `SPLITGRP-EVD-######`; recipe plane `SPLITGRP-REC-######` (§4.6) | **evaluation unit** (Split 6, SSOT L16886–16891) | aliased to `lineage_root_id` or `study_id`; joined across planes |

Nesting that must hold on every ASSIGNED row (gate G08-10): `study` ⊆ `lineage_root` ⊆ `split_group` (a study lies inside one lineage root; a lineage root inside one split group). On **kinetic rows** (KIN, and DRV with a KIN parent) the chain continues `split_group` ⊆ `lab_group` (`lab_group_id`, `LABGRP-######`, proposed prefix D-15): Steps 11 / 26 / 27 / 32 use the lab group as the unit of independence (CHG-11-3). `lab_group_id` is a mandatory key on those rows; its status may be UNKNOWN (authorship not read), and such a series is not SIM-VAL / DS-TEST eligible.

Companion field `independence_resolution` ∈ {`STUDY`, `PUBLICATION_ONLY`, `SOURCE_FAMILY_ONLY`, `UNKNOWN`}: how fine the grouping really is.

### 4.2 Computation (Step 08 algorithm, deterministic, CPU)

1. Normalise ids (DOI, PMID, titles, hashes).
2. Detector proposes LIN edges (typed, with `rule_version`).
2a. **Hub rule** (PROPOSED, D-12; review B #1, CRITICAL). Union-find is transitive: a node linked by MERGING edges to many independent primaries would put all of them into one `lineage_root_id`, destroying the "k independent lineages" count and forcing a giant component (Step 15 already fears this through the 103 shared Phenol-Explorer yield records). Therefore:
   - (a) *Hubs* are DOC with `report_kind` in {COMPILATION_DATABASE, REVIEW, SECONDARY_COPY} (`DOC.is_compilation_hub = YES`) and SRC of kind DATABASE / REVIEW (flag `is_compilation_hub` in the independence registry).
   - (b) Edges are recorded **per record** (AGG / OBS / DRV → primary STUDY / DOC), never hub → primary.
   - (c) A locator DOC is never a structural edge, and a hub DOC is never listed in a STUDY's `report_doc_ids`.
   - (d) The structural merges DOC–SRC and AGG–`compiler_src_id` apply only when `member_lineage_status` is NOT_IDENTIFIABLE or PARTIAL (then the compiler node is the source-family node and one release is one root, D-8). A KNOWN-member AGG is its own singleton lineage node: it contributes no MERGING edge, its `parent_union` records the parents' roots and groups as information, and it is not counted as an independent lineage.
   - (e) An AGG / review row with KNOWN members never enters VALIDATION / CALIBRATION / TEST (analyse the studies, not the review: Cochrane); its members are used instead. It may train only if none of its KNOWN members lies in an evaluation partition, otherwise `train_eligibility = QUARANTINED_MEMBER_HELDOUT`; the quarantine propagates to DRV children. This replaces, for hubs only, the card's blanket "parent union of every AGG"; the DRV parent union and gate G08-2 are unchanged.
   - (f) Shared-input DRVs (one yield factor used by many Phenol-Explorer rows) merge at split level as the PRIMARY analysis, and a pre-registered **sensitivity analysis with that merge switched off** (parent role YIELD_FACTOR) is reported side by side (THR-08A-21).
   - (g) PARTIAL membership (known parents plus an unknown remainder): the known-parent relation **and** the source-family node apply, and `independence_resolution` is SOURCE_FAMILY_ONLY or UNKNOWN (schema rule).
3. Union-find over structural edges (as limited by 2a) + MERGING edges with `edge_status ≠ REJECTED` (PRIMARY_SOURCE only if `membership_status = KNOWN`) → components = `lineage_root_id`.
4. Add GROUPING_DEFAULT edges (SHARES_REFERENCE_SAMPLE; PRIMARY_SOURCE with unknown membership), DRV parent unions (and AGG parent unions for non-hub AGG), and one source-family node per `source_family_id` joining its NOT_IDENTIFIABLE and PARTIAL aggregates → union-find → `split_group_id`.
5. Lab groups: add GROUPING_OPTIONAL_TIER edges (SAME_LAB_AS, computed from `DOC.authorship`) → `lab_group_id`. Optional (sensitivity split) for the evidence plane in general; **mandatory** (status UNKNOWN allowed) for KIN and DRV with a KIN parent, with `split_group` ⊆ `lab_group` on those rows.
6. Assign `independence_resolution` per row (§4.4), emit the independence registry (§4.8) and the component report.
7. Contamination screen (L-04b): fingerprint every UNKNOWN row against all VALIDATION / CALIBRATION / TEST rows at a recall-oriented threshold; matches get `train_eligibility = QUARANTINED_NEAR_HELDOUT`.

### 4.3 Stability, versioning, aliasing

- Assignments are produced **per `rule_version`** (a hash of detector code + thresholds + edge-type registry). A new `rule_version` produces a new complete table; old tables are kept (append-only).
- `LROOT-` / `SPLITGRP-EVD-` ids are minted from a content key, `sha256(sorted member node ids)`, through the idempotent minter: an unchanged component keeps its id across rule versions, a changed component gets a **new** id, and no id is ever reassigned to different membership. Old ids stay valid for the old table.
- Rows (KIN, AGG, DRV) store the keys as a cached copy with `rule_version`; the registry at that version is authoritative. Step 15 freezes one `rule_version`.
- The three keys are separate columns. A validator rejects any row in which two of them are string-equal or derived from each other by a naming convention.

### 4.4 Independence resolution and what each value may be used for

| independence_resolution | Meaning | TRAIN | VALIDATION | CALIBRATION | TEST |
|---|---|---|---|---|---|
| `STUDY` | `study_id` PRESENT with DOC locator; lineage resolved at study level | yes | yes | yes | yes (subject to tier and verification rules, §5) |
| `PUBLICATION_ONLY` | grouped at publication (DOC) level; study boundaries inside the publication not established (PE today) | yes | yes | yes | yes, but the evaluation is named "publication-component CV", never "study-disjoint" |
| `SOURCE_FAMILY_ONLY` | database aggregate without member lineage; the source family is one node | yes | only as a whole family | only as a whole family | only as leave-one-source-family-out (the family is the held-out unit) |
| `UNKNOWN` | the grouping cannot be relied on (missing DOC / locator, unresolved conflict, intake not yet processed) | yes, unless quarantined by L-04b | **no** | **no** | **no** |

The card states "UNKNOWN rows may train, never test"; this draft **extends it to validation and calibration** because an UNKNOWN row can duplicate test content undetected (decision D-5 in §7). **TRAIN-only does not by itself prevent leakage** (review B #2): leakage is a TRAIN copy of TEST content, and an undetected duplicate in TRAIN inflates test scores as much as one in TEST. Hence rule L-04b (§5): a recall-oriented near-duplicate screen of every UNKNOWN row against the evaluation partitions before the freeze (`train_eligibility = QUARANTINED_NEAR_HELDOUT`), plus a pre-registered sensitivity run with all UNKNOWN rows removed from TRAIN (THR-08A-19).

Eligibility values written to the independence registry (§4.8), in addition to the resolution: `train_eligibility` ∈ {ELIGIBLE, TRAIN_ONLY_UNKNOWN_RESOLUTION, QUARANTINED_NEAR_HELDOUT, QUARANTINED_MEMBER_HELDOUT, NOT_ASSESSED}; `eval_eligibility` ∈ {ELIGIBLE_BY_RESOLUTION, TRAIN_ONLY_UNKNOWN_RESOLUTION, TRAIN_ONLY_COMPILATION_KNOWN_MEMBERS, NOT_ASSESSED}. Compilation families also carry `membership_screen_status` ∈ {BIBLIOGRAPHY_SCREENED, NOT_SCREENED, NOT_AVAILABLE}: when it is not BIBLIOGRAPHY_SCREENED, any train-on-compilation / test-on-primary evaluation (or the reverse) is labelled `NOT_INDEPENDENT_VERIFIED` for cells that share (matrix family × analyte × process family) where the primary's year ≤ the release year (review B #3; THR-08A-23). Absence of a bibliography is not evidence of independence (recall-oriented default). UNKNOWN rows still receive best-effort component ids when ASSIGNED (gate G08-1 requires non-null keys); `PENDING` rows have null ids and are UNKNOWN by definition.

### 4.5 Giant-component rule (card rule PROPOSED_PILOT 40%, THR-08A-08; refinement THR-08A-20)

**Card rule (unchanged, kept in force).** If the largest `split_group_id` of a target family holds more than the pre-registered share (proposal 40%) of that family's rows, the 08a report states it and the evaluation is labelled "publication-component CV" and/or leave-one-source-family-out, never "study-disjoint"; headline claims for that family become DIAGNOSTIC_ONLY; Step 14 targets independent lineage components, not rows. No threshold is chosen to change group sizes (R-08). Context for the signer: the B0 groups already hold 39.0% (USDA, 7,018 / 17,978) and 39.4% (Bognár, 7,090 / 17,978) of all ACTIVE rows, so the rule is expected to bind for the nutrient-retention families (a forecast from counts in the plan, not a computed result). The 40% sits next to those shares: one PROVISIONAL edge or a new `rule_version` could flip the label (a forking path).

**Refinement proposed on review B #6 (PROPOSED_PILOT, THR-08A-20; reported side by side, nothing weakened; if either rule fails the weaker label applies).**
1. Compute the rule **only on the evaluation-eligible pool** per target family: rows with `independence_resolution` in {STUDY, PUBLICATION_ONLY} in TEST-eligible tiers. SOURCE_FAMILY_ONLY rows can never be study-disjoint, so including them makes the card rule fire for reasons unrelated to literature independence.
2. Primary criterion: the Kish effective number of groups n_eff = (Σ n_g)² / Σ n_g² must be ≥ K (K = 10, the same K as G15-c, PROPOSED) **and** the largest share ≤ 0.40. The largest share alone is a poor proxy for effective cluster count.
3. Evaluate it **once**, on the `rule_version` frozen at Step 15; no relabelling across versions.
4. Weight every metric by cluster (each group once); always report results with and without the largest component.

### 4.6 Plane-qualified `split_group_id` and the no-join rule

The column name `split_group_id` is used in two planes (R-03 evidence, R-08 recipe). One column name, two planes, plane-qualified values:

| Plane | Value | Produced by | Applies to |
|---|---|---|---|
| Evidence (P-EVD) | `SPLITGRP-EVD-######` | Step 08a / 08b | EVD export rows, DOC, STUDY, SEXP, SMP, OBS, AGG, DRV, KIN, KINPT |
| Recipe (P-REC) | `SPLITGRP-REC-######` | Step 07I-S (recall-oriented, OP-SPLIT from 07I-C) | recipe base members, recipe identity, Gold firewall v2 |

Rules: (1) **no cross-plane join** on `split_group_id`: no table, view, split builder or metric may join or union an EVD-plane group with a REC-plane group; (2) a record carries at most one plane's value; the draft schemas pin the evidence pattern, so a `SPLITGRP-REC-` value in an evidence record fails validation; (3) a future claim that needs both planes (for example the Step-36 evidence compiler evaluated on recipes) needs an explicit cross-plane link artefact with its own H4 decision; none is defined here; (4) the CI scan of FW-12 flags any table mixing both prefixes. Related but different recipe-plane keys, kept distinct: `duplicate_group_id` (exact copies), `FAM-` family (precision-oriented, provisional, `calibrated=false`), `split_lock_group_id` (Gold firewall v1, exact groups).

### 4.7 Mapping the existing key

`EVD.independence_group` (127 values) is the **B0 baseline**: USDA and Bognár one group each, PE one per publication hash. It is not `study_id`, not `lineage_root_id`, not `split_group_id`. Under B0, USDA R6 and Bognár are two source families whose mutual independence is UNVERIFIED (gate G08-9 verdict required before `cross_source_v1` agreement is reused as independent).

### 4.8 Independence registry (draft content of `registry/independence_key_contract_v1.csv` / `independence_registry_v1.csv`)

`rule_version, evd_id, evidence_level, record_id, study_id, study_id_status, lineage_root_id, split_group_id, independence_resolution, independence_group_b0, source_family_id, is_compilation_hub, membership_screen_status, parent_union_split_group_ids, provisional_edges_in_component, lab_group_id (nullable; mandatory key on kinetic rows), lab_group_status, train_eligibility, eval_eligibility, assignment_status`. Append-only per `rule_version`.

---

## 5. Leakage rules for study- and lineage-disjoint splits

Keys come first, metrics last. "Validator" = semantic validator on the Mac (the JSON Schema drafts enforce what a single record can express). Revision r1 adds L-04b, L-11b and L-19 (21 rules).

| # | Rule | Enforced by |
|---|---|---|
| L-01 | Split assignment is computed from the keys **before** any test metric is seen, frozen with `assignment_sha256`, and examples are never moved after test performance is observed (SSOT §257A.15; L28338). | split builder + sealed-test access log (FW-11) |
| L-02 | Evaluation unit = `split_group_id`; counting unit = `lineage_root_id`; `study_id` = pooling cluster. Rows are never the unit. | validator |
| L-03 | Four partitions TRAIN / VALIDATION / CALIBRATION / TEST; no `split_group_id` appears in more than one. | validator |
| L-04 | `independence_resolution = UNKNOWN` → TRAIN only (§4.4), subject to L-04b. | validator |
| L-04b | Contamination screen: before the freeze every UNKNOWN row is fingerprinted with B3 at a recall-oriented threshold (looser than the edge threshold; value OPEN, THR-08A-19) against all VALIDATION / CALIBRATION / TEST rows; matches get `train_eligibility = QUARANTINED_NEAR_HELDOUT` and are dropped from TRAIN. Every Step-15 confirmatory claim also reports a pre-registered sensitivity run with ALL UNKNOWN rows removed from TRAIN. | Step 15 freeze + split builder |
| L-05 | `SOURCE_FAMILY_ONLY` rows enter evaluation only as a whole source family (leave-one-family-out). | validator |
| L-06 | Naming: "study-disjoint" only if every TEST row has resolution `STUDY` and groups are disjoint; otherwise "publication-component CV" or "source-family held-out"; a giant component (§4.5) forces the weaker name. | report generator |
| L-07 | A DRV and **all** its parents are in the same partition (gate G08-2, hard stop). Same for a DRV derived from a KIN / KINPT. | validator; `DRV.lineage.parent_union` |
| L-08 | E5, E6, E7 and IMPUTED rows never enter TEST or CALIBRATION (FW-09); held-out test/calibration labels additionally need human verification (G14-3, G15-H); SIMULATED rows never appear in observed tables (DRV parents cannot be SIM-). | export-v2 validator + split builder |
| L-09 | `SHARES_REFERENCE_SAMPLE` partners and every treatment compared with one shared control stay together (the reused `before` value must not sit on both sides). | split builder |
| L-10 | Series atomicity (04.3): all KINPT of a KIN, all KIN of one `condition_grid_id`, and all KIN of one SEXP are in one partition. L-10 binds the *partitions* (TRAIN / VALIDATION / CALIBRATION / TEST; SIM-CAL / SIM-VAL / DS-TEST). Internal CV folds inside one partition (for example leave-one-temperature-out inside SIM-CAL) may split a condition grid and are labelled "within-study extrapolation". | validator |
| L-11 | Simulator calibration groups must be a subset of downstream TRAIN groups; the locked validation groups are never used in fitting; the assignment is frozen before any parameter fit (RV §2 Q6 gap 3 and §5 item 6). A PARAM / fit disjointness proof (`fitted_on` ∩ SIM-VAL = ∅; "PARAM calibration sources ⊂ training lineage components") is made on `split_group_id` and `lab_group_id`, **never on `lineage_root_id`**: GROUPING_DEFAULT links and PRIMARY_SOURCE with UNKNOWN membership escape a lineage-root check (review B #29; CHG note owed to the Step 26 / 32 cards). | Step 15 freeze |
| L-11b | Cross-task leakage: a split group in SIM-VAL or DS-TEST is held out for **every** evidence-plane model that is compared with the simulator (the Step 29 / 30 / 33 tabular comparators are scored against the simulator on the same queries), and its DRVs (including ENDPOINT_FROM_SERIES) are excluded from all TRAIN sets. One partition table keyed by `split_group_id` serves both planes' uses. | Step 15 freeze + split builder |
| L-12 | A non-hub AGG and its KNOWN members share a group; a hub AGG (compilation / review with KNOWN members) is never evaluated and trains only if no KNOWN member lies in an evaluation partition (§4.2 step 2a(e)); source-side imputation donors stay in the same fold as their recipients (transition-bootstrap contract L20). | validator |
| L-13 | Method / platform (`OBS.method`) is a covariate and a possible split key; train–test platform overlap is **disclosed** with each release. | report generator |
| L-14 | Prompts and few-shot exemplars are never drawn from documents in a TEST lineage component (resolved through 08b). | Step 09 extraction harness |
| L-15 | A later edge that merges a TRAIN and a TEST component does not edit the frozen release: it creates a new `rule_version`, and the contamination count of the old release is reported. | Step 15 / 08b |
| L-16 | No cross-plane join (§4.6). | FW-12 scan |
| L-17 | Residual risk is disclosed, not hidden: L-04b reduces but does not remove the risk that TRAIN-only UNKNOWN rows duplicate TEST content; the UNKNOWN row count and the number of quarantined rows are published with every split release. | split report |
| L-18 | Each headline claim gets a feasibility verdict FEASIBLE / DIAGNOSTIC_ONLY / NEED_DATA with the number of independent split groups of its cell (08a.6; 04.8-min). | feasibility report |
| L-19 | Hub rule: a compilation / review / database release never connects its primaries (§4.2 step 2a). | 08b library test (negative control below) |

### 5.1 Negative controls (scratch copy only, never in a ledger)

From the Step 04 card, plus controls that the drafts make checkable:

| Control | Expected | Where it is caught |
|---|---|---|
| UNKNOWN-independence row placed in TEST | rejected | validator L-04 (record-level shape: `lineage` block, draft schemas) |
| DRV whose parents span two split groups | rejected | validator L-07; record-level hint `parent_union.union_status` (schemas) |
| time series stored only as one endpoint | rejected | KIN/DRV rules in the 04.3 contract (`ENDPOINT_FROM_SERIES` needs a KIN parent) |
| SIMULATED row in an observed table | rejected | DRV parent pattern (schemas: no `SIM-` parent) + export validator |
| `EXTERNAL_VERIFIED` provenance on a DATABASE_AGGREGATE row | rejected | export-v2 validator (provenance_class is an export field, not in these drafts) |
| `SPLITGRP-REC-` value in an evidence record | rejected | schema pattern (`lineage.split_group_id`) |
| E4 / E1 / E2 KIN tier without `HUMAN_VERIFIED` | rejected | KIN schema |
| two of the three keys equal | rejected | validator |
| a review / database DOC quoting two independent primary studies | the two studies stay **two** lineage roots | 08b library test (hub rule, L-19) |
| the same series digitised from a review figure and from the primary paper | one lineage root (QUOTES_VALUES_FROM KIN → KIN) | LIN schema (node types) + 08b |
| UNKNOWN-resolution row that is a near copy of a TEST row (seeded) | `QUARANTINED_NEAR_HELDOUT`, absent from TRAIN | L-04b screen |
| hub AGG with a KNOWN member in TEST, AGG in TRAIN | AGG quarantined (`QUARANTINED_MEMBER_HELDOUT`) | split builder |
| MEASURED value 0 with censoring NOT_REPORTED / DETECTED / ROUNDED_INTERVAL | rejected | OBS / AGG schema (TRUE_ZERO is the only door) |
| KIN lineage without `lab_group_status`; DRV with a KIN parent without lab fields | rejected | KIN / DRV schema |
| endpoint DRV of a SIM-VAL / DS-TEST series inside a Step 29 / 30 / 33 TRAIN set | rejected | L-11b |
| PROJECT_FIT parameter in the evidence plane | rejected | KIN schema (`fit_origin` admits AUTHOR_REPORTED only) |

The JSON-Schema-expressible controls were exercised against the drafts with a throw-away stdlib checker on 2026-10-26 (revision r1: 220 cases, all as expected: baseline instances, accepted variants, rejected variants and structural checks); `jsonschema` is not installed on this server, so the proposed contract test for the Mac is in `README.md`.

---

## 6. Schema index

| File | Entity | Notes |
|---|---|---|
| `registry/schemas/DOC.draft_v1_1.schema.json` | DOC | sha256 required; snapshot link nullable; `is_compilation_hub`, `authorship` required |
| `registry/schemas/LIN.draft_v1_1.schema.json` | LIN | per-type node-pair constraints (KIN / PARAM nodes of QUOTES_VALUES_FROM; SRC in SAME_STUDY_AS); human-confirmation rule |
| `registry/schemas/SEXP.draft_v1_1.schema.json` | SEXP | optional `context` (water:food ratio, lid, start mode, geometry, O2/headspace, pH tissue/medium, cooking-water assay, open/sealed); absent key = UNKNOWN |
| `registry/schemas/SMP.draft_v1_1.schema.json` | SMP | `derived_from` = state-transition edge; EVD.matrix facets; role COOKING_MEDIUM; `material_origin` |
| `registry/schemas/OBS.draft_v1_1.schema.json` | OBS | n, dispersion type (+ n-basis, CV, pooled SE, LSD), censoring (+ TRACE) + LOD/LOQ, basis (+ raw), retention definition (+ evidence), method/platform ref, condition ref, digitisation provenance, `series_link`, `measurement_dedup` (04.2-min) |
| `registry/schemas/AGG.draft_v1_1.schema.json` | AGG | `member_lineage_status`, `membership_screen_status`, `parent_ids`, `lineage` block. Beyond the Plan §7 list (which names DOC, LIN, SEXP, SMP, OBS); optional; presupposes the D-2 outcome (it gives AGG a full ledger envelope while its `$comment` calls it an export-view key) |
| `registry/schemas/DRV.draft_v1_1.schema.json` | DRV | parents OBS/AGG/DRV/KIN/KINPT only; censor-propagation law; correlation assumption + shared-parent set; lab fields when a KIN parent exists. Beyond the Plan §7 list; optional; presupposes the D-2 outcome |
| (04.3) `KIN.draft_v1`, `KINPT.draft_v1` | KIN, KINPT | `kinetic_trajectory_contract_v1.md` |

Common to all: the existing envelope (`id`, `record_type`, `schema_version`, `version`, `status`, `superseded_by`, `created_at`, `created_by`, `provenance`, `verification`, `external_refs`, `notes`), `additionalProperties: false`, and a schema-level echo of `rule_human_verification` (HUMAN_VERIFIED / HUMAN_REJECTED need a named human and a timestamp).

---

## 7. Open decisions for H4 (Kush, Parv)

| # | Decision | Draft default |
|---|---|---|
| D-1 | Approve the entity chain and the nine edge types; confirm that the brief's other names (§3.2) are aliases only. | approve as written |
| D-2 | AGG / DRV: separate ledgers, or `evidence_level` + `parent_ids[]` on export-v2 rows (card default: no separate ledgers). | export-v2 rows; schemas validate the exported view |
| D-3 | New prefixes beyond the 01.3-min list: `LROOT-` (lineage root), `CGRID-` (condition grid, 04.3), a formula-registry prefix for `DRV.formula_id` (suggested `DFORM-`). | reserve all three |
| D-4 | `SAME_LAB_AS` enters only the optional lab tier (not the default `split_group_id`); `SHARES_REFERENCE_SAMPLE` and PRIMARY_SOURCE-with-unknown-membership are default-tier grouping. The card calls both SAME_LAB_AS and SHARES_REFERENCE_SAMPLE "grouping-only" without saying which tier they belong to. | as in §3.1 |
| D-5 | UNKNOWN resolution is TRAIN-only (stricter than the card's "never test"). | stricter |
| D-6 | How the approved drafts reach `ledgers/schemas/` (CHG-04-7): port into `registry.py` (so `export_schemas.py` regenerates them) or hand-maintain. Also the ID minter rejects prefixes missing from `R`. | port into `registry.py` at 08a |
| D-7 | Value for the giant-component share (40%), audit size and precision bound: `registry/preregistered_thresholds_v1.csv` THR-08A-04, THR-08A-08. | sign or change before 08a |
| D-8 | Meaning of `lineage_root_id` for NOT_IDENTIFIABLE aggregates: the component of the compiled release's SRC/DOC node (one release = one root, a lower bound on independent lineages). | as stated |
| D-9 | `STUDY.report_doc_ids` (STUDY side) is authoritative for "DOC reports STUDY"; DOC carries no study pointer. | as stated |
| D-10 | `independence_resolution` for the Phenol-Explorer rows: `PUBLICATION_ONLY` until experiment boundaries are confirmed (not `STUDY`). | as stated |
| D-11 | DOC mint key: `<src_id>\|sha256:<hex>` (draft default) or one DOC per distinct sha256 with the first SRC as `src_id`. | `<src_id>\|sha256:<hex>` |
| D-12 | Hub rule (§4.2 step 2a): hubs never connect their primaries; KNOWN-member AGG never evaluated, train only if no member is held out; shared-input DRV merge kept as primary analysis with a sensitivity run (THR-08A-21). Replaces, for hubs only, the card's blanket AGG parent union; DRV parent union and G08-2 unchanged. | as stated |
| D-13 | UNKNOWN-resolution leakage: L-04b recall-oriented screen + sensitivity run with all UNKNOWN rows removed from TRAIN (THR-08A-19; threshold value OPEN). | as stated |
| D-14 | Giant-component refinement: evaluation-eligible pool + Kish n_eff ≥ K (K = 10) + largest share ≤ 0.40, evaluated once on the frozen rule_version; card rule THR-08A-08 stays; weaker label wins (THR-08A-20). | as stated |
| D-15 | `lab_group_id` mandatory (status UNKNOWN allowed) on the kinetic plane; `DOC.authorship`; new prefixes `LABGRP-` (lab group) and `MBSET-` (mass-balance set, kinetic contract); `PARAM-` is referenced as a LIN node pattern only (Step 24 owns it, prefix not reserved here). SAME_LAB_AS rule and N: THR-08A-22 (N OPEN). | reserve LABGRP-, MBSET- |
| D-16 | `retention_definition` split (TRUE_MURPHY / APPARENT_FRESH_BASIS / APPARENT_DRY_BASIS / APPARENT_BASIS_UNSTATED / TR_OR_AR_UNDISCLOSED / UNKNOWN / NOT_APPLICABLE) with a separate evidence field; the card's five tokens map as in `04_2_min_value_documentation.md` §1. Deviates from the card's token list. | split |
| D-17 | SEXP optional `context`: absent key = UNKNOWN (draft), not NOT_REPORTED (plan card). | UNKNOWN |

---

## Appendix A — Additive field proposals (NOT applied; for the 04.8-min / 05.1 schema-diff proposal)

STUDY (next appended version, 08a.2): `origin_type` (EVD origin_type vocabulary: PRIMARY_STUDY, DATABASE_AGGREGATE, REVIEW_AGGREGATE, AUTHORITY_STANDARD, PROJECT_MEASUREMENT), `report_doc_ids[]` (DOC-; primary manifestations only, never a hub DOC), `design` stays UNKNOWN unless stated, optional `lab_group_note`.
EVD export v2 (05.1, built inside 08a): `evidence_level` ∈ {OBS_DIRECT, AGG, DRV}, `parent_ids[]`, `obs_ids[]`, `sample_ids[]`, `sexp_id`, `study_id`, `lineage_root_id`, `split_group_id` (SPLITGRP-EVD-), `independence_resolution`, `rule_version`, `series_link{status, kin_id, kinpt_ids[]}` (04.3; the record-level guard already exists on OBS as `series_link{status, kinpt_id}`), `dispersion_status`, `n_status`, `licence_status`, `doc_id` + locator. Export v1 (64 properties, sha `e61d7db4…`) stays untouched.
SPLIT.strategy / partition roles / feasibility fields: 04.8-min, due before Step 15 (not part of this draft).

## Appendix B — Legacy EVD field → target

| EVD (v1 ledger) | Target |
|---|---|
| `origin_type` PRIMARY_STUDY / PROJECT_MEASUREMENT | OBS (+ STUDY) |
| `origin_type` DATABASE_AGGREGATE / REVIEW_AGGREGATE | AGG (`aggregation_method` UNKNOWN unless stated) |
| `source_id`, `source_family_id` | `DOC.src_id` / `AGG.compiler_src_id`; `source_family_id` stays on SRC and in the registry |
| `study_ids`, `study_id_status` | `lineage.study_id`, `lineage.study_id_status` (identical enum) |
| `matrix{…}`, `process{…}` | `SMP.matrix` / `AGG.matrix`; `SMP.derived_from` / `AGG.process` (same facets) |
| `target.state_variable_id`, `target.raw_name`, `target.molecule_id` | `OBS.state_variable_id`, `analyte_raw_name`, `molecule_id` |
| `target.basis` | `OBS.basis_id` (MB-); registry aliases cover FRESH_WEIGHT → MB-001, DRY → MB-002, PER_VOLUME → MB-005, RETENTION_TR_OR_AR / TRUE_RETENTION → MB-007. **Gaps to settle at H4 (proposed alias rows and three new bases MB-009..011 are in `04_2_min_value_documentation.md` §1a):** `WET`, `AS_CONSUMED`, `PER_SERVING` (semantic matches MB-001, MB-003, MB-006 but no alias recorded), `APPARENT_RETENTION` (no alias on MB-007; it needs the fresh / dry basis in `retention_definition`) and `HEADSPACE` (no MB entry; stays MB-008 with `basis_raw` until H4 decides). Raw kept in `basis_raw` (now a required key). |
| `before`, `after` (qvalue) | two OBS (REFERENCE_BEFORE, TREATED_AFTER); `status/value/low/high/unit/raw` → `value`; `uncertainty` (number, type unstated) → `dispersion.type = REPORTED_UNSPECIFIED`, absent → `NONE_REPORTED` |
| `censor.kind` LT_LOD, LT_LOQ, GT_ULOQ, GT_CAP, ND, GT_STATED, LT_STATED; `censor.limit` | `censoring.kind` (same tokens), `limit_low` / `limit_high` (strictly positive; a limit of 0 is not a limit). The ledger has no TRACE token: TRACE_BETWEEN_LOD_LOQ is new (CS-011) |
| `derived.{delta, percent_change, log_fold_change, yield_factor}` | DRV records (parents named); a retention factor **reported by the source** is the value of an OBS/AGG with basis MB-007, not a DRV |
| `measurement_method_id` | `OBS.method.method_id` (MEAS-) |
| `n_replicates` | `n_biological` / `n_technical` with status UNKNOWN (ledger-null alone) or NOT_REPORTED (only where the source file's column list shows no n; none of the 17,978 rows has n, RE §0) |
| `design`, `tier`, `applicability`, `conflict_cluster` | stay EVD / STUDY view fields (D-018: tier, provenance, verification, design stay four fields) |
| `independence_group` | B0 baseline only (§4.7) |
