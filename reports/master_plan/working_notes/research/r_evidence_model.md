# r_evidence_model — scientific evidence / provenance model (spine steps 04, 05, 08, 09, 15)

Researcher: r_evidence_model · date 2026-10-22 · PLAN-RESEARCH ONLY (no Step 08 work done; repo read-only).
The 36-step plan with step cards is MISSING (ctx.md). Everything said here about "what Step NN is for" is
RECONSTRUCTED from SSOT v15, Master Plan v4.0 and repo artifacts, not quoted from the missing plan.

---------------------------------------------------------------------------------------------------
## 0. Internal baseline (what exists today — verified by read-only inspection)

| Item | Observation | Where |
|---|---|---|
| SSOT evidence atom | E_k=(subject,relation,object,conditions,measurement,provenance); must state method, fidelity, exact doc/table/row/span, explicit/derived/inferred/simulated | SSOT L25248-25262 |
| SSOT lineage law | "Five webpages repeating the same underlying paper are one independent measurement lineage, not five independent studies"; dedupe derived copies before agreement analysis | SSOT L25307-25310; also L26294, L26355-26368 (contradiction checklist step 7 = lineage) |
| SSOT field dictionary | `EvidenceAtom.15 study_id`, `.16 source_id`, `.22 independence_group` exist but their entries are generic boilerplate (no semantic definition of "independence group") | SSOT L31100-31179 |
| SSOT split law | Split 6 source/study-disjoint "Keep all rows from a paper/study/experimental campaign together … mandatory for literature-mined quantitative process data" | SSOT L16886-16891; L22097-22102; L23656-23667 ("Propensity weighting does not license random row splits") |
| SSOT platform | platform = covariate, split key, provenance field, domain-shift variable | SSOT L15795-15808, L17612-17622, L24022-24039 |
| SSOT censoring | ND/<LOD: no zero imputation; censored likelihood; store censor_flag, LOD, platform | SSOT L19291-19317, L23992-24001 |
| SSOT pooling | within-study fit first, then random-effects pooling log k_s = mu+u_s; study nuisance b_s | SSOT L19659-19694 |
| SSOT tiers | E1–E6 (L16651-16675) — Master Plan says E1–E7 (Plan L1409, L1640) → tier-count inconsistency to resolve in Step 04 | |
| SSOT regimes | D-A aggregated retention / D-B curated panels / D-C focused kinetics / D-D recipe corpora; "Do not flatten these regimes into one exchangeable dataset" | SSOT L23445-23464 |
| Plan W4/W5 | EVD required fields incl. before/after value+uncertainty+LOD/LOQ+method, basis, n/replicates, conflict cluster, "source independence group"; MEAS- (method) and STUDY- ledgers | Plan L1573-1691 |
| Plan AH1 | origin_type PRIMARY_STUDY / DATABASE_AGGREGATE / REVIEW_AGGREGATE / AUTHORITY_STANDARD / PROJECT_MEASUREMENT; study_ids never fabricated | Plan L2759-2787 |
| Plan AM3 | row → source/database → publication IDs → study families; split by connected components; if giant component, report and fall back; "do not claim a study-disjoint result that did not exist" | Plan L3597-3613; DEL-2 card L3104-3107 |
| Ledger EVD | 57,280 version lines; ES-1.1 export 17,978 ACTIVE rows (USDA R6 7,018 / Bognár 7,090 / Phenol-Explorer 3,870) | `ledgers/data/EVD.jsonl`, `reports/es1/es1_1_audit.md` |
| independence_group today | DATABASE_AGGREGATE rows: whole source family is one group (`USDA-RETN-R6`, `BOGNAR-2002`); Phenol-Explorer: one group per publication hash (`pe_pub:…`), 125 groups, 1 STUDY per group | computed from EVD.jsonl (read-only) |
| STUDY ledger | 125 rows, all `design: UNKNOWN`, `verification: UNVERIFIED` | `ledgers/data/STUDY.jsonl` |
| MEAS ledger | 3 rows; this is a measurement-METHOD ledger (e.g. %TR formula Murphy 1975), `basis: UNKNOWN` | `ledgers/data/MEAS.jsonl` |
| EXP ledger | 8 rows = ML/benchmark experiments (DEL-2 runs), NOT scientific experiments | `ledgers/data/EXP.jsonl` |
| EVD before/after | only {value, unit, status}; NO SD/SE, NO n/replicates, NO LOD/LOQ values (lod_loq_status NOT_REPORTED_BY_SOURCE_ROW) | EVD.jsonl; es1_1_audit.md |
| EVD export v1 schema | 64 fields; **no `independence_group` field**, no dispersion, no n, no sample/experiment ids, no document locator (only `source_row_sha256`) | `registry/schemas/evd_export_v1.schema.json` |
| Multi-parent derived values | Phenol-Explorer rows carry a yield factor whose source is a different publication (e.g. `yield_source: "BERGSTROM 1994_GAINS-AND-LOSSES"`) — the derived retention depends on 2 publications but is assigned to 1 group | EVD-007019 |
| DEL-2 study-disjoint | only possible for Phenol-Explorer; USDA & Bognár "NOT POSSIBLE (single source family or one giant component)" | `reports/del2/*_results.md` |
| Cross-source agreement | USDA-R6 vs Bognár treated as independent sources (67 overlapping cells, Spearman 0.611); whether Bognár compiled studies that also feed USDA R6 is **UNVERIFIED** | `reports/del2/cross_source_v1.md` |

Two prefix collisions already exist and will bite Step 08/09: **`MEAS-` = method, not observation** and
**`EXP-` = ML experiment, not scientific experiment**. The new scientific EXPERIMENT and MEASUREMENT
entities must get new prefixes (proposal below: `SEXP-`, `OBS-`).

---------------------------------------------------------------------------------------------------
## 1. Research questions

- Q1 Which established provenance / experiment models fit SOURCE→DOCUMENT→STUDY→EXPERIMENT→SAMPLE→MEASUREMENT→AGGREGATE→DERIVED, and should we adopt one as runtime storage or only as a conceptual mapping?
- Q2 What do food-composition compilation standards (FAO/INFOODS, EuroFIR, LanguaL) require for value documentation, aggregation and derived values?
- Q3 What does "independent study" mean operationally (Cochrane, meta-analysis), and how should dependent effect sizes (shared controls, multiple targets per sample, multiple experiments per paper) be represented?
- Q4 Which per-measurement fields (replicates, SD/SE/n, censoring, basis, method/platform) are needed for downstream effect-size / kinetics / censored-likelihood use?
- Q5 How are duplicate publications / data re-use detected, and how reliable are cheap signals (DOI, authorship)?
- Q6 What split construction gives a valid study-disjoint evaluation, and what to do when components are giant?
- Q7 What does evidence say about single vs double data extraction and LLM-assisted extraction accuracy (2023-2026), for Step 09 machinery?
- Q8 What must Step 08 produce for Step 15 (DATA-EVIDENCE v1 freeze) and later study-disjoint evaluation?

---------------------------------------------------------------------------------------------------
## 2. Findings

### Q1 Provenance / experiment models — confidence HIGH
- **W3C PROV-DM / PROV-O (W3C Recommendations, 30 Apr 2013)** [VERIFIED]: Entity/Activity/Agent; `wasDerivedFrom` with subtypes Revision, Quotation ("derived by copying, or 'quoting', some or all of it") and PrimarySource ("derivation relation from secondary materials to their primary sources"); `alternateOf`/`specializationOf`; Bundles (provenance of provenance); `qualifiedDerivation`. These map 1:1 onto the lineage edges we need (repost = Quotation, database release update = Revision, compilation→original paper = PrimarySource, PDF vs HTML of same article = alternateOf).
- **ISA abstract model (ISA-Tab specs; Sansone et al. 2012 Nat Genet 44:121-126)** [VERIFIED spec page + Crossref metadata]: Investigation ⊃ Study ("central concept containing information on the subject under study … and any treatments applied"; design, factors, protocols) ⊃ Assay ("test performed … producing qualitative or quantitative measurements"; measurement type, technology, platform). Material graph Source→(process+protocol+parameter values)→Sample→Extract→Data is a DAG; supports split (one source → many samples) and pooling. Factor = independent variable manipulated. This is exactly the STUDY / EXPERIMENT(factor set) / SAMPLE / MEASUREMENT(assay, platform) layering, with process parameters ≈ our COND.
- **W3C/OGC SOSA/SSN (W3C Rec 19 Oct 2017)** [VERIFIED]: Observation (act of carrying out a Procedure to estimate a property of a FeatureOfInterest), Sample (`isSampleOf` FeatureOfInterest), Sampling, Procedure (reusable protocol/method), Result; has a PROV alignment module. Gives a clean pattern for SAMPLE vs MEASUREMENT (observation) vs METHOD (procedure = our existing `MEAS-`).
- **FAIR (Wilkinson et al. 2016, Sci Data 3:160018)** [VERIFIED principles text]: R1.1 clear usage licence; R1.2 "(meta)data are associated with detailed provenance"; R1.3 community standards; F1 persistent identifiers; I3 qualified references. → DATA-EVIDENCE v1 card must carry licence + provenance per row and stable IDs.
- Claim/evidence ontologies: Micropublications (Clark et al. 2014 J Biomed Semantics 5:28) [VERIFIED abstract] — claims with supporting/challenging evidence; ECO (Nadendla et al. 2022 NAR 50:D1515) [VERIFIED abstract] — evidence-type terms. Useful for the Step 36 claim ledger / conflict structure, not for the measurement core.
- Conclusion: none of these is a drop-in food-process schema; ISA gives the right *layering*, PROV the right *lineage edge semantics*, SOSA the right *sample/observation/procedure* separation. Adopting their RDF serialisations as runtime storage is unnecessary for a JSONL-ledger project.

### Q2 Food-composition compilation standards — confidence HIGH (structure), MEDIUM (detailed thesaurus contents not read)
- **Greenfield & Southgate, Food composition data: production, management and use, 2nd ed., FAO 2003, ch. 10** [VERIFIED chapter page]: three database levels — archival (all data, with metadata) → reference database (acceptable archival values per food, linked back to records) → user database (one value per nutrient per food, built from reference, "should not entail actual data entry"). "Each stage in evaluation of the data must be documented." Combining: mean or median preferred when many values; selection by confidence when few, with documented rationale; weighting documented; sample counts are a quality criterion; outliers flagged not deleted; retention-based/recipe-calculated estimates "must be assigned lower confidence levels than analytical values"; warns that tracing values in secondary tables often "leads only to another set of tables" (circular lineage); compilers may need replicate values from authors.
- **EuroFIR** [VERIFIED thesauri page]: four mandatory entities Food, Component, Value, Reference; thesauri Acquisition Type (v1.2 2017: where the value came from — host system, literature, analytical), Method Type (v1.2), Method Indicator (v1.6 2022: analysis vs calculation vs imputation), Value Type (v1.4 2022: numeric vs qualitative description), Matrix Unit (v1.5 2019: per amount of what), Unit (v1.3), Reference Type (v1.1), food classification via LanguaL. Westenbrink et al. 2009 Food Chem 113:759-767 and 2016 Food Chem 193:69-74 describe the EuroFIR quality/compilation approach [metadata VERIFIED via Crossref; content UNVERIFIED].
- **FAO/INFOODS guidelines** [VERIFIED list page]: Guidelines for Checking Food Composition Data prior to Publication (v1.0 2012), Food Matching (v1.2 2012), Converting Units, Denominators and Expressions (v1.0 2012, erratum 2016). Unit/denominator/basis conversion has a published standard → our basis conversions must cite it and require the needed inputs (e.g. moisture) rather than assume.
- **LanguaL** [VERIFIED home page]: faceted food-description thesaurus (A Product type, B Food source, …), administered by the European LanguaL Technical Committee; the site states FoodOn is its successor. → matrix/food description for SAMPLE should be faceted (source, part, physical state, heat treatment, cooking method, preservation), consistent with r_ingredient work.
- Consequence: our existing three regimes map onto FAO levels: USDA R6 and Bognár rows are *user-level AGGREGATES* (Plan AH1 DATABASE_AGGREGATE); Phenol-Explorer is closer to a *reference-level* compilation pointing to primary papers. Re-pooling an aggregate with its own members double-counts.
- The USDA SRC note "nearest 5%; values >100 reported as 100" and MEAS-000001 "many factors imputed from similar foods" are exactly EuroFIR Method-Indicator / Value-Type information; today they live in free-text notes.

### Q3 What "independent study" means; dependent effect sizes — confidence HIGH
- **Cochrane Handbook v6.5, ch. 5 (Li, Higgins, Deeks)** [VERIFIED]: "studies rather than reports of studies are the principal unit of interest"; "It is wrong to consider multiple reports of the same study as if they are multiple studies"; link reports via registration IDs, authors, sponsor, location, intervention details, participant numbers, dates; compare data lists to detect duplicated studies.
- **Cochrane ch. 23 §23.3.4 (Higgins, Eldridge, Li)** [VERIFIED]: multiple treatment arms sharing one control must not enter as separate comparisons (unit-of-analysis error from "unaddressed correlation"); combine arms, split shared group (partial fix), model the correlation, or network MA. → In process-effect data, one raw sample measured once and compared with boiled/steamed/fried samples is a shared control; each EVD row's `before` is reused.
- **Lajeunesse 2011, Ecology 92:2049-2055** [VERIFIED abstract]: variances/covariances of the log response ratio for correlated designs, multiple treatments sharing a control, repeated measures, multivariate studies. **Hedges, Gurevitch & Curtis 1999, Ecology 80:1150-1156** [metadata VERIFIED]: the log response ratio, the natural effect size for retention/fold change (requires means, SD, n of both groups for its variance).
- **Three-level MA (Van den Noortgate et al. 2013, Behav Res Methods 45:576-594)** [VERIFIED abstract]: effect sizes nested in studies; no need to impute unknown sampling covariances. **RVE (Hedges, Tipton & Johnson 2010, Res Synth Methods 1:39-65)** [VERIFIED abstract]: "may yield accurate results with as few as 20-40 studies"; **Pustejovsky & Tipton 2022, Prev Sci 23:425-438** [VERIFIED abstract]: expanded working models (correlated-and-hierarchical effects) with small-sample corrections. **Noble et al. 2017, Mol Ecol 26:2410-2425** [VERIFIED abstract]: non-independence in ecological MA; sensitivity analyses recommended.
- Consequence: the data structure must record nesting (measurement ⊂ sample ⊂ experiment ⊂ study ⊂ lineage) and shared-control links, otherwise neither multilevel/RVE pooling (SSOT L19669-19684) nor cluster bootstrap (SSOT L23656-23667) can be computed correctly. With 125 Phenol-Explorer publications total — and far fewer per target/process cell — RVE small-sample corrections are required, and many cells will be below the 20-40 study regime.

### Q4 Measurement fields (replicates, dispersion, censoring, basis, platform) — confidence HIGH
- Effect-size variance (Hedges 1999; Lajeunesse 2011) needs mean, dispersion and n per arm; Cochrane ch. 6 conversions (SE→SD etc.) require knowing *which* dispersion statistic was reported → store `dispersion_type ∈ {SD, SE, CI95, RANGE, IQR, NONE_REPORTED}` plus `n_biological`, `n_technical`, separately. Estimating mean/SD from median/range/IQR (Wan et al. 2014 BMC Med Res Methodol 14:135) [metadata VERIFIED] is allowed only as a flagged ESTIMATED derivation, never as MEASURED.
- None of the current 17,978 EVD rows has SD or n (verified). So inverse-variance weighting is impossible for the current corpus; this is a structural NOT_REPORTED, not a missing-value to impute.
- Censoring: **EFSA 2010, EFSA Journal 8(3):1557, "Management of left-censored data in dietary exposure assessment"** [metadata VERIFIED via Crossref; content UNVERIFIED]; **Hwang et al. 2023, Food Sci Nutr 11:5223-5235** [VERIFIED abstract]: MLE and robust ROS best; substitution workable below ~80% non-detects. SSOT already mandates censored likelihood. Our data actually have *upper* caps (USDA "values >100 reported as 100", GT_CAP) and *rounding* (USDA "nearest 5%") — interval censoring — in addition to future LOD/LOQ. Enumerate `censor_kind ∈ {LT_LOD, LT_LOQ, ND, GT_CAP, ROUNDED_INTERVAL, RANGE_ONLY}` with limit(s) and `resolution`.
- Basis: fresh/dry/as-eaten/per-serving/headspace and TR vs AR retention (Murphy et al. 1975 per MEAS-000001) are not interconvertible without moisture/yield; INFOODS conversion guideline governs. `basis_conversion` must be a DERIVED record citing inputs.
- Platform: SSOT already makes platform a split key; ISA Assay "technology/platform" and SOSA Procedure agree. Keep `method_id` (existing MEAS-) at MEASUREMENT level, not only at study level, because one paper can use HPLC for one analyte and GC-MS for another.

### Q5 Duplicate publication / data re-use — confidence MEDIUM-HIGH (clinical literature; food-science rates unknown)
- **Tramèr et al. 1997 BMJ 315:635-640** [VERIFIED abstract]: 17% of full reports and 28% of patient data duplicated; inclusion led to 23% overestimation of efficacy; studies with larger effects more likely duplicated.
- **von Elm et al. 2004 JAMA 291:974-980** [VERIFIED abstract]: six duplication patterns in 1,234 articles; covert duplicates 5.3%; 64% of duplicates had partly/completely different authorship — "Authorship was an unreliable criterion".
- FAO ch. 10: compiled tables trace to other tables (circularity).
- Consequence: DOI/title/author matching is necessary but insufficient. A *numeric fingerprint* (sorted tuple of reported values + units + matrix + n) is the strongest cheap signal for copied data, and is also how database-to-paper re-use can be detected (e.g. a Phenol-Explorer value reappearing in a later review or webpage). The duplication rate in food-processing literature is UNVERIFIED — measure, don't assume.

### Q6 Study-disjoint split construction — confidence HIGH
- Grouped/block CV is "nearly universally more appropriate than random cross-validation" when dependence structures exist (**Roberts et al. 2017, Ecography 40:913-929**) [VERIFIED abstract via Crossref]; non-independence between train/test is a recognised leakage class (**Kapoor & Narayanan 2023, Patterns 4:100804**, 294 papers in 17 fields affected) [VERIFIED abstract].
- Roberts et al. also warn blocks can force extrapolation → report the covariate coverage of held-out groups (the "study-disjoint" test then partly measures matrix/process OOD; report alongside pair-holdout per Plan L3141-3146).
- Master Plan AM3 connected-component rule (L3597-3613) is the right construction; it needs the lineage graph from Step 08 to be computed.

### Q7 Double extraction and LLM-assisted extraction — confidence HIGH on direction, MEDIUM on transfer to food-science tables
- **Cochrane ch. 5, MECIR C46 (mandatory)**: "(at least) two people working independently to extract outcome data"; automation "may first act as checks for manual data extraction" [VERIFIED].
- **Buscemi et al. 2006, J Clin Epidemiol 59:697-703** [VERIFIED abstract]: single extraction produced more errors than double (relative difference 21.7%, P=.019) but took 36.1% less time.
- **Mathes et al. 2017, BMC Med Res Methodol 17:152** [VERIFIED abstract]: extraction error rates up to 50%; errors often change effect estimates; evidence base for standards weak.
- **Gartlehner et al. 2024, Res Synth Methods 15:576-589** [VERIFIED abstract]: Claude 2, 10 RCTs, 160 data items, 96.3% accuracy; most errors were *missed* items. **Konet et al. 2024, Res Synth Methods 15:818-824** [VERIFIED]: Claude 2 96.3% vs GPT-4+plugin 68.8%, largely due to PDF parsing; with selected text 98.7% / 100% → PDF/table parsing is the key vulnerability.
- **Shankar, Lim & Qian 2026, J Biomed Inform 181:105086 (online 25 Jul 2026), systematic review of 27 studies** [VERIFIED abstract]: overall accuracy 47-99.9%; categorical/string 74-96% vs **numerical 47-88%**; omissions 60-74% of errors; hallucination 0.08-6%; assistive workflow 91.0% vs human-only 89.0%; recommends LLMs as "assistive tools within dual-extraction workflows requiring human verification".
- **Laignelot et al. 2026, J Clin Epidemiol 194:112221** [VERIFIED abstract]: 63 studies; data extraction accuracy median 0.95 (IQR 0.91-0.97) but range 0.36-1.00; use as assistants with human oversight.
- Science-domain numeric extraction: **Polak & Morgan 2024, Nat Commun 15:1569 (ChatExtract)** [VERIFIED abstract]: precision and recall ~90% with follow-up verification prompts for materials property values. **Dagdelen et al. 2024, Nat Commun 15:1418** [VERIFIED abstract]: fine-tuned LLM joint NER+RE to JSON schemas.
- Food-specific: **Youn et al. 2024, Comput Biol Med 181:109072 (FoodAtlas)** [VERIFIED abstract]: 230,848 food–chemical composition relations from 155,260 papers via LLM entailment + active learning (relations, not quantitative process-effect values). **Bölücü et al. 2025, Foods 14(8):1355** [VERIFIED abstract]: curated food-extrusion dataset (process parameters, formulations, characterisation metrics); LLMs extract structured info but hallucination and missing context persist; human validation needed but faster than manual extraction; no numeric accuracy in abstract.
- Consequence: Step 09 machinery = LLM-as-first-extractor + independent second extraction + adjudication for every row that may enter E4/Gold/test; numeric values, units, basis, n, dispersion type, censoring and condition fields must be scored per field (numeric is the weak class); omission recall must be measured, not only precision.

### Q8 What Step 08 must output — see §4. Confidence MEDIUM-HIGH (the design is well supported; the achievable component structure of our own corpus is unknown until computed).

---------------------------------------------------------------------------------------------------
## 3. Recommended architecture

### 3.1 Entity model (relational JSONL ledgers; PROV/ISA/SOSA used as semantic mapping, optional export)

Hierarchy: `SRC ─< DOC ─< (reports) >─ STUDY ─< SEXP ─< SAMPLE ─< OBS` ; `AGG` and `DRV` are entities derived
from OBS/AGG/DRV with explicit parent lists; `LINEAGE` holds typed edges between SRC/DOC/STUDY/SAMPLE/OBS/AGG.
`EVD` stays as the consumer-facing **evidence atom view** (SSOT L25248) that points into this graph; it is
not replaced. Everything below that is new is a proposal; prefixes are placeholders.

| Entity (prefix) | Role / standard analogue | Mandatory fields (UNKNOWN / NOT_REPORTED / NOT_APPLICABLE allowed as explicit statuses, never 0/"" ) |
|---|---|---|
| SOURCE (`SRC-`, exists) | publisher-level origin: article, database release, book, review, webpage, dataset, authority, project; EuroFIR Reference; PROV Entity+Agent | id, kind, title, persistent_id (DOI/PMID/ISBN/URL) or status, release/version, year, publisher/authors, licence + licence_status, storage_rule, primary_or_secondary, source_family_id, retrieved_at |
| DOCUMENT (`DOC-`, new) | concrete manifestation actually read (PDF, HTML snapshot, table file, release txt); PROV specializationOf/alternateOf | id, src_id, sha256, format, retrieval date, edition/version, page count, parser/OCR tool + version, licence inherited |
| STUDY (`STUDY-`, exists, extend) | data-generating campaign = Cochrane "study not report", ISA Study; compilation record allowed only when typed | id, origin_type (Plan AH1), design ∈ {CONTROLLED_EXPERIMENT, OBSERVATIONAL_SURVEY, COMPILATION, REVIEW, UNKNOWN}, report_doc_ids[≥1], lab/group id if stated, year(s), country, linkage_evidence, verification |
| EXPERIMENT (`SEXP-`, new; **not** `EXP-`) | one comparison set within a study: factors varied + shared reference; ISA factor/assay set | id, study_id, factors_varied[] (process, condition fields), reference_sample_ids[] (the shared control/raw), protocol text/locator, equipment/tool ids, condition_id(s) |
| SAMPLE (`SMP-`, new) | food material at a state; ISA Source/Sample, SOSA Sample; LanguaL/FoodOn-style faceted description | id, sexp_id, role ∈ {REFERENCE_BEFORE, TREATED_AFTER, INTERMEDIATE, BLANK}, derived_from_sample_id + process/condition (state transition edge), matrix (ingredient_id or raw, cultivar, part, form, prior processing, geometry), pooled flag, n_biological_units, storage/ripeness |
| MEASUREMENT (`OBS-`, new; `MEAS-` stays = method) | one property value of one sample by one method; SOSA Observation; EuroFIR Value | id, sample_id, state_variable_id (SVAR), method_id (MEAS-), platform, value_kind ∈ {MEASURED, CENSORED, RANGE, QUALITATIVE, NOT_REPORTED}, value / low / high, unit, basis (fresh/dry/as-eaten/serving/headspace/…), statistic ∈ {MEAN, MEDIAN, SINGLE, …}, dispersion_type + value, n_biological, n_technical, censor_kind + limit + resolution, LOD/LOQ + status, locator (doc_id, page, table, row, col / char span), extraction_version, extraction_record_ids (double extraction), verification |
| AGGREGATE (`AGG-`, new view or EVD subtype) | compiled value over several measurements/studies; FAO reference/user level; EuroFIR Method Indicator | id, src_id (compiler), aggregation_method ∈ {MEAN, MEDIAN, WEIGHTED, SELECTED, BORROWED, IMPUTED_FROM_SIMILAR, UNKNOWN}, member_ids[] or member_lineage_status = NOT_IDENTIFIABLE, n_members if stated, imputation_possible flag (e.g. USDA R6), rounding/censoring as in OBS |
| DERIVED (`DRV-`, new view or EVD derived block) | deterministic computation (delta, LFC, log retention, true retention with yield, basis conversion, estimated SD); PROV qualifiedDerivation | id, formula_id + version, parent_ids[≥1] (ALL inputs, incl. yield factor from another paper), parent_independence_groups[] (union), uncertainty_propagation (value or UNKNOWN), censor propagation rule, provenance_class = DERIVED_DETERMINISTIC / ESTIMATED |
| LINEAGE edge (`LIN-`, new) | typed edges; PROV mapping | id, from_id, to_id, type ∈ {SAME_STUDY_AS (companion/duplicate report), QUOTES_VALUES_FROM (prov:Quotation), PRIMARY_SOURCE (prov:PrimarySource, compilation→paper), REVISION_OF (release), ALTERNATE_OF (same doc other format), SHARES_SAMPLES_WITH, SAME_LAB_AS, CITES}, detection_method (DOI/PMID match, title fuzzy, numeric fingerprint, author+matrix+n, manual), score, status ∈ {PROVISIONAL, HUMAN_CONFIRMED, REJECTED}, reviewer |
| EXTRACTION record (`XTR-`, new, Step 09) | one extractor's reading of one field set | id, doc_id+locator, extractor (model id+version+prompt hash, or human id), blind flag, field values, timestamp; adjudication record links ≥2 XTR to final OBS |

EVD (existing) keeps its contract and gains pointers: `obs_ids[]`, `sample_ids[]`, `sexp_id`, `lineage_root_id`,
`split_group_id`, `independence_resolution`, `dispersion_status`, `n_status`. Existing rows that cannot populate
the new layers get explicit `NOT_IDENTIFIABLE_FROM_SOURCE` — no fabricated study, sample or n (Plan AH1; Law
"no scientific value may be invented to fill a schema").

### 3.2 Independence-group definition (for counting evidence and for study-disjoint splits)

Three nested keys per EVD/OBS row, all computed by Step 08 and frozen in Step 15:

1. `study_id` — data-generating campaign (Cochrane study, not report).
2. `lineage_root_id` — connected component of STUDY/DOC/AGG nodes under edges
   {SAME_STUDY_AS, QUOTES_VALUES_FROM, ALTERNATE_OF, REVISION_OF, SHARES_SAMPLES_WITH, PRIMARY_SOURCE when membership is known}.
   This is the **statistical independence unit**: used for "k independent lineages", consensus/conflict (Plan W12 L1896-1902), agreement analysis (SSOT L25309), RVE/three-level cluster id.
3. `split_group_id` — connected component of lineage_root_ids additionally merged by
   (a) DERIVED records whose parents span several lineages (e.g. Phenol-Explorer retention × Bergström yield),
   (b) DATABASE_AGGREGATE without member lineage → whole source_family is one node (current behaviour, labelled `independence_resolution = SOURCE_FAMILY_ONLY`),
   (c) optional stricter tier `SAME_LAB_AS` (lab-disjoint sensitivity split).
   This is the **evaluation unit** for Split 6 (SSOT L16886).

`independence_resolution ∈ {STUDY, PUBLICATION_ONLY, SOURCE_FAMILY_ONLY, UNKNOWN}` records how fine the grouping
really is. A row with UNKNOWN cannot be in a study-disjoint test set (it can be in train).

Giant-component rule (from Plan AM3): if the largest split component holds more than a pre-registered share of
the rows of a target family (proposal: >40%, to be fixed in Step 04/08 before computing), report it, use
grouped K-fold over remaining components + leave-one-source-family-out, and label the result
"publication-component CV", never "study-disjoint".

### 3.3 Rejected alternatives
- **Flat EVD table only (status quo)** — cannot express shared controls (Cochrane 23.3.4; Lajeunesse 2011), multi-parent derived values, replicate n/dispersion, or multiple analytes on one sample; makes multilevel/RVE pooling and correct cluster bootstrap impossible. Rejected as the *sole* model; kept as the view.
- **independence_group = source_id** — too fine for reposts/duplicates (SSOT L25309; Tramèr 1997) and too coarse for multi-study databases. Rejected.
- **independence_group = DOI/publication** — misses covert duplicates and companion papers (von Elm 2004: 64% different authorship) and splits multi-experiment papers incorrectly only if experiments share samples. Kept only as `PUBLICATION_ONLY` resolution.
- **Full ISA-Tab files or RDF/PROV-O triplestore as runtime storage** — tooling overhead, life-science/omics orientation, no benefit over JSONL ledgers + typed edges; adopt the semantics, offer an optional PROV-JSON export of the frozen release for FAIR R1.2. Rejected as storage.
- **Adopting EuroFIR/FoodEx2 as the core food identity** — out of scope of this question (see ingredient research); reuse EuroFIR thesaurus *categories* for value documentation (value type, method indicator, acquisition type, matrix unit) as enumerations.
- **Imputing SD/n to enable inverse-variance weighting** — violates no-invention law; use unweighted/cluster-robust estimators and record `NOT_REPORTED`; Wan-2014-type estimates only as flagged ESTIMATED DRV when median/range are reported.
- **LLM-only extraction for E4 rows** — contradicted by MECIR C46, Buscemi 2006, Shankar 2026 (numeric 47-88%). Rejected.

---------------------------------------------------------------------------------------------------
## 4. Changes per affected spine step (reconstructed step intents; card text unavailable)

### Step 04 — Freeze evidence / provenance / similarity contracts (status: "complete" per brief; KEEP + CLARIFY via a v1.1 contract addendum, no rewrite of frozen artifacts)
Add / clarify:
- Entity glossary §3.1 incl. the explicit distinction study vs report vs experiment vs sample vs observation vs method; resolve prefix collisions (`MEAS-`=method, `EXP-`=ML experiment; new `SEXP-`, `OBS-`, `SMP-`, `DOC-`, `LIN-`, `XTR-`, `AGG-/DRV-` or subtype flags).
- Definitions of `study_id`, `lineage_root_id`, `split_group_id`, `independence_resolution` (fills the SSOT L31170-31179 boilerplate gap → also file an SSOT change request PROPOSED_ONLY).
- Enumerations: origin_type (Plan AH1), design, value_kind, censor_kind incl. GT_CAP and ROUNDED_INTERVAL, basis, dispersion_type, statistic, aggregation_method, lineage edge types, verification states.
- Resolve E1–E6 (SSOT L16651) vs E1–E7 (Plan L1409, L1640, L2307) tier inconsistency; keep tier separate from verification and design (ES-1.1 ruling C1 already does).
- Pre-register the giant-component threshold and fallback naming rule.
Gate: contract reviewed by Kush+Parv; schema files validate on existing ledgers without changing any value.

### Step 05 — Normalize EVD (ES-1.1 PASS; KEEP, add v2 export as a non-breaking increment, possibly executed inside Step 08)
- Export v1 lacks `independence_group` entirely and has no dispersion/n/sample/experiment/locator fields. Add v2 fields with explicit status values (`NOT_REPORTED_BY_SOURCE_ROW` for SD/n/LOD on all current rows).
- Move USDA notes "nearest 5%", ">100 reported as 100", "imputed from similar foods" into structured fields (censor_kind=ROUNDED_INTERVAL resolution 5; GT_CAP; method_indicator=IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE) — ES-1.1 already partially does this via `provenance_note`.
- Re-express multi-source derived rows (Phenol-Explorer yield from a second publication) as DRV with two parents.
- Do not alter frozen v1 export (sha256 e61d7db4…); v2 is additive.

### Step 08 — Scientific source lineage (NOT STARTED; KEEP, MODIFY scope to the deliverables below)
Inputs: SRC (609), STUDY (125), EVD ACTIVE (17,978), MEAS (3), Phenol-Explorer per-row publication + yield-source references, ES-1.2 64-source manifest (for forward compatibility).
Outputs (all new, additive):
1. `DOC` ledger for every SRC actually read (sha256 of the local file/release).
2. Corrected/extended `STUDY` records (design kept UNKNOWN unless stated; report_doc_ids) and new STUDY/SRC nodes for yield-source publications referenced by Phenol-Explorer.
3. `LINEAGE` edge ledger with typed PROV-mapped edges, detection method, score, status.
4. Duplicate / re-use detector v0: normalised DOI/PMID; title fuzzy; author-set overlap; **numeric fingerprint** of (matrix, analyte, unit, value tuple) across sources; compilation-membership edges where the database cites primaries (USDA R6 / Bognár bibliography → PRIMARY_SOURCE edges; overlap between them is currently UNVERIFIED and must be checked before any cross-source agreement claim is reused).
5. Independence registry: per EVD row `study_id`, `lineage_root_id`, `split_group_id`, `independence_resolution`, parent-group union for DRV.
6. Component report per source regime (D-A/D-B/D-C, SSOT L23445) and per target family: #components, size distribution, giant-component share, feasibility verdict for study-disjoint / publication-component / source-family-held-out splits.
7. EVD export v2 (see Step 05) carrying the registry fields.
8. PROV-JSON export (optional, for FAIR R1.2).
Baselines (for the detector): B0 = current grouping (source_family / pe_pub); B1 = DOI/title exact; B2 = B1 + fuzzy title/authors; B3 = B2 + numeric fingerprint. Report how many merges each adds.
Metrics: edge precision on a human-audited stratified sample (by edge type & detector); recall on a **seeded negative control** (inject synthetic reposts/copies of known rows into a scratch copy — never into ledgers — and measure detection); % rows by independence_resolution; component statistics; # DRV rows whose parents span groups (must be 0 unmerged).
Pass gate (proposal, pre-register): 100% rows have non-null independence_resolution; 0 cross-group DRV unmerged; audited edge precision lower 95% Wilson bound ≥ 0.90 (≈ ≥150 audited edges with ≤ 5% errors gives [0.90, 0.97]); seeded-copy recall ≥ 0.95; canonical ledgers byte-identical before/after; deterministic rebuild ×2.
Fail action: if precision fails → edges stay PROVISIONAL and split_group uses the coarser safe grouping (merge on any edge ≥ low threshold — conservative merging only costs test-set size, never validity). If giant component → report and use fallback naming.
Human: ~3-6 h for edge audit at current scale (UNVERIFIED estimate); compute: CPU only, seconds-minutes.
Do NOT: acquire new literature, scrape, or extract new values (that is Step 09-12).

### Step 09 — Evidence extraction & verification machinery (KEEP; MODIFY to specify dual-extraction protocol)
- Pipeline: DOC parse (PDF/table → structured cells with page/table/row/col; Konet 2024 shows parsing is the main failure point) → extractor A (LLM, schema-constrained to OBS/SAMPLE/SEXP fields) → extractor B independent (second LLM family or human; blind to A) → field-level disagreement → human adjudication → OBS with `extraction_record_ids`.
- Mandatory automatic checks: every numeric value must string-match a span in the DOC (anti-hallucination); unit/basis consistency; arithmetic consistency (percent change vs before/after, retention vs after/before × yield — reuse ES-1.1's 278-row diagnostic logic); n and dispersion_type present-or-NOT_REPORTED; censoring parse (<LOD, ND, "tr").
- Metrics per field class (numeric value, unit, basis, n, dispersion type, censoring, process/condition fields, matrix identity), reporting precision AND omission recall (omissions are 60-74% of LLM errors, Shankar 2026), with Wilson CIs.
- Sizing: a 20-row pilot (Step 10) gives at 95% observed accuracy a 95% CI of [0.76, 0.99] — too wide to accept machinery; target ≥150-300 adjudicated instances per critical field class ([0.90, 0.97] at n=150-200) before E4 promotion at scale. Step 10 should be treated as protocol shake-down, not as the accuracy gate.
- Gold protection: adjudicators blind to model output for the evaluation subset (anchoring); LLM pre-fill allowed only for non-evaluation production rows and recorded.
- Tiering: LLM-only rows = E5; dual-extracted + adjudicated = E4; only E1-E4 human-verified rows enter test sets (SSOT L16651-16675; SSOT L26294 "LLM-extracted scientific rows entering final evaluation are human verified").

### Step 15 — Freeze DATA-EVIDENCE v1 (KEEP + CLARIFY)
Must contain: frozen entity ledgers (DOC/STUDY/SEXP/SAMPLE/OBS/AGG/DRV/LIN) or EVD v2 with pointers; frozen independence registry + rule version; **split registry assigned at group level before any test metric is seen** (SSOT 257A.15 L28326-28340 order); per-split feasibility report (study-disjoint achieved / publication-component / source-held-out / NOT POSSIBLE per target family); evidence-tier × verification × design × independence_resolution counts; censoring and dispersion availability tables (so downstream knows weighting is impossible where SD/n absent); licence per row and dataset card (FAIR R1.1/R1.2); sha256 manifest.
Gate additions: no test-set row with independence_resolution UNKNOWN; no lineage component split across train/test; no E5 row in any test/calibration set; all DRV parents inside the same split partition.

---------------------------------------------------------------------------------------------------
## 5. Look-ahead requirements (what earlier steps must collect for later consumers)

| Downstream need | Required field / artifact | Owner step |
|---|---|---|
| Step 15 / 30 study-disjoint & cluster bootstrap (SSOT L23656) | lineage_root_id, split_group_id, independence_resolution | 08 (defined in 04) |
| Steps 24-27 parameter pooling & validation (SSOT L19659-19694), kinetics schema (SSOT L19111-19136) | time-series as multiple OBS on SAMPLEs within one SEXP with time/temperature condition per sample; initial conditions; n and dispersion; within-study grouping | 09 schema, 10-12 extraction |
| Step 27 simulator "real held-out evidence" | held-out by split_group, not by row; provenance that the evidence was not used for calibration (DRV parent tracking) | 08 + 15 |
| Steps 22/23 applicability (matrix/condition) | faceted SAMPLE description (part, form, cultivar, geometry, prior processing), COND per SAMPLE not per paper | 07 (conditions) + 09 |
| Step 30 censoring-aware models (SSOT L19291) | censor_kind incl. GT_CAP/ROUNDED, limits, LOD/LOQ | 05 v2 / 09 |
| Platform-disjoint split & block-missingness audit (SSOT L24022) | method_id/platform at OBS level | 09 (MEAS- link per OBS) |
| Step 36 conflict structure & "k independent lineages" in packets | lineage_root_id + LIN edges; conflict cluster after harmonisation checklist (SSOT L26355-26368) | 08, 14 |
| Step 13 discovery corpus | DOC + LIN detector must ingest DOI/PMID/title/author for discovered papers so duplicates are linked at discovery time, not after extraction | 08 detector reused in 13 |
| Step 06 acquisition manifest (ES-1.2) | per source: whether member-level lineage is recoverable (bibliography of compilations), licence, document format → feeds independence_resolution forecast | 06 (already has a "lineage quality" score, `reports/h_state/es_1_2_source_census.md` L50) |
| Step 12 structured DBs | for every compiled database, capture its bibliography/member list where published so AGG rows can get PRIMARY_SOURCE edges | 12 |

---------------------------------------------------------------------------------------------------
## 6. Residual uncertainty; pilot vs more reading

- UNKNOWN: real component structure of our corpus once Phenol-Explorer yield sources and database bibliographies are linked (could create a giant component). **Cheaper to compute than to read** — a read-only graph build over existing ledgers is minutes of CPU; it belongs inside Step 08 (not done here, Step 08 not authorised).
- UNKNOWN: duplicate/re-use rate in food-processing literature (clinical rates 5-17% are not transferable). Measured by the Step 08 detector + Step 13.
- UNVERIFIED: whether Bognár 2002 and USDA R6 share primary studies → current cross-source agreement (reports/del2/cross_source_v1.md) may overstate independence. Check their bibliographies in Step 08.
- MEDIUM: LLM numeric-extraction accuracy on food-science tables (no food-specific numeric accuracy figure found; clinical numeric 47-88%). Only an in-domain adjudicated sample (Step 09/10, ≥150 instances per field class) resolves it — empirical pilot cheaper than more reading.
- Thresholds proposed here (giant component 40%, edge precision lower bound 0.90, seeded recall 0.95) are design proposals, not literature-derived constants; must be pre-registered by humans before computation.
- EuroFIR thesaurus term lists and Westenbrink 2009/2016 contents were not opened (only structure/metadata) — sufficient for the architecture decision; reopen when writing enumerations.
- Stop rule §8: met (criteria 1 and 5) — evidence suffices to choose the layered model + typed lineage edges + three-key independence definition; remaining uncertainty is empirical.
