# r_acquisition — Data-availability reality for food process-effect evidence
Researcher: r_acquisition · Spine steps 10, 11, 12, 13, 14, 15, 24, 27 · Date 2026-10-22 · PLAN-RESEARCH ONLY (nothing downloaded, ingested or edited)

Note on provenance: the 36-step plan cards are MISSING (ctx.md). Step intents below are reconstructed from the brief §9 titles, SSOT v15 and repo artifacts; no card text is quoted or invented.
Internal anchors used: SSOT §203.3 Resource acquisition priority (L17191–17248), §203.4 resource-fidelity table (L17250ff), §203.6 automated literature extraction (L17299–17316), §205.5 extraction reliability (L17623–17628), §201.7 evidence tiers E1–E6 (L16651–16675), §201.8 literature extraction (L16676–16691), §210.28 kinetic data hierarchy K0–K4 (L19089–19110), §210.29 kinetic evidence schema (L19111–19136), §210.29A focused kinetic anchors (L19137–19163), §211.48 aggregate-database limitation (L19782–19793), §216.2 kinetic-experiment table (L22800–22824), §224 active literature acquisition (L24269–24387), §227.8 dataset acquisition list (L24742–24758). Master Plan v4.0 SX-06-04 (L363), RS-06 Q5 (L917), RS-02 Q7 (L867).
Repo state read (read-only): `registry/data_source_acquisition_manifest.csv` (64 sources, DS-001..DS-064), `reports/h_state/es_1_2_source_census.md`, `registry/source_claim_capability_matrix.csv` (header), `registry/evd_contract_v1.csv`, `ledgers/schemas/EVD.schema.json` (32 properties), `ledgers/data/` listing, `data/external/usda_yields/*` (header + row count only).

---------------------------------------------------------------------
## 1. Questions
Q1. For each process-effect variable class, which concrete structured sources exist, at what size, recording which conditions, endpoint vs trajectory, under what licence? Classify STRUCTURED_DB / LITERATURE_ONLY / RARE / COMMERCIAL_RESTRICTED / NOT_REALISTIC.
Q2. What is already acquired in the repo (so no duplicated recommendation), and what cheap structured wins remain?
Q3. Is there any open compiled food kinetic-parameter database (would change Steps 24/26/27)?
Q4. Literature-discovery APIs (OpenAlex, Crossref, Europe PMC/PMC, Semantic Scholar, Unpaywall, CORE): licence and rate limits for a large Step-13 corpus; any 2026 changes.
Q5. Is LLM-assisted extraction of multi-field quantitative data credible enough to plan Steps 10–14 around (with human verification)?
Q6. Which earlier-step schema/contract gaps would break Steps 24/27 (look-ahead)?

---------------------------------------------------------------------
## 2. Findings

### 2.0 What the repo already holds (do NOT re-acquire)
- EVD = 17,978 rows, all E3: USDA R6 7,018; Bognár 7,090 (6,594 retention + 496 yield; 28/39 Part-2 tables); Phenol-Explorer 3.6 3,870 rows / 125 papers (census §2). [VERIFIED in repo]
- Local but NOT ingested / not in SRC: USDA Cooking Yields R2 (`data/external/usda_yields/cooking_yields_meat_poultry_r2.csv`, 173 data rows; columns include Cooking Yield %, n, SD, min %, max %, Moisture gain/loss %, Fat gain/loss %, Preparation Method; NO temperature/time), FNDDS (67 MB), INFOODS density_v2 / AnFooD2.0 / uFiSh1.0, FDC SR Legacy (crosswalk only). [VERIFIED in repo]
- EVD schema is ENDPOINT-ONLY: before/after/delta/retention/yield, n_replicates, value_low/high; there is no time-series / kinetic-experiment ledger (no KIN ledger in `ledgers/data/`), no SD/SE/dispersion-type field, no aggregation-level field. SSOT §210.29 and §216.2 specify such a table. [VERIFIED in repo] → critical look-ahead gap (§5).
- Census conclusion already reached in S130: no structured open source for mechanism/kinetic/physical time series; 13/16 priority cells SOURCE_GAP with literature route. My research CONFIRMS this independently (Q3).

### 2.1 Variable-class availability table (Q1)
Legend: EP = endpoint (before/after or single state), TR = trajectory/time series. "Cond." = what conditions are recorded.

| # | Variable class | Best concrete sources (size; licence) | Cond. recorded | EP/TR | Class | Conf. |
|---|---|---|---|---|---|---|
| 1 | Retention (vitamins/minerals) | USDA R6 (ingested); Bognár 2002 (ingested 28/39); FSANZ/AUSNUT retention (licence conflict, DS-009); EuroFIR recipe-calculation rules report (Vásquez-Caicedo et al. 2007; content not opened) | process name/category only; no T/t; R6 values partly imputed from similar foods, rounded to 5% (capability matrix note) | EP aggregate | STRUCTURED_DB (already acquired; low marginal value) | HIGH |
| 2 | Nutrients (composition, raw vs cooked) | FDC Foundation Foods (sample-level values, per-sample metadata incl. analytical method, n samples, purchase location/date; descriptor "raw or cooked"; inaugural 73 foods, now expanded; 12/2025 release; CC0 per repo manifest); SR Legacy (final 2018; ingested crosswalk); FNDDS (local) | preparation descriptor only | EP, UNPAIRED (raw and cooked samples are not the same specimen) | STRUCTURED_DB | HIGH |
| 3 | Phenolics | Phenol-Explorer 3.0 processing module: 1,253 aggregated RFs derived from 4,626 published RFs, 129 papers, >100 foods, 161 polyphenols, 35 processes; analytical method + hydrolysis recorded; mean/min/max/SD; yield-corrected; T/t not recorded as fields (Rothwell et al. 2013, CC BY 3.0 article) — INGESTED. USDA Flavonoid DB 3.3 (composition only). EuroFIR eBASIS (critically evaluated content data, >300 plant foods, 17 compound classes incl. glucosinolates; individual login, trial then contact EuroFIR) | process descriptor; method | EP aggregate | STRUCTURED_DB (acquired) + COMMERCIAL_RESTRICTED (eBASIS) | HIGH |
| 4 | Volatiles / aroma | VCF Volatile Compounds in Food (BeWiDo B.V., ex-Triskelion; v16.10; ~1,445 products per site; quantitative min/max ranges with number of observations; subscription only); FlavorDB2 (25,595 molecules / 936 ingredients per abstract version; arXiv 2205.05451, no journal ref; licence unknown, access via Prof. Bagler); FooDB (CC BY-NC 4.0 footer); Leibniz-LSB@TUM Odorant DB (odorant reference data; licence not found) | VCF: product names occasionally encode processing; no T/t | EP presence/semi-quant | Process-conditioned: LITERATURE_ONLY (GC-MS raw-vs-cooked studies); absolute quant: RARE; VCF: COMMERCIAL_RESTRICTED | MEDIUM |
| 5 | Texture | none found; literature TPA/compression values depend on test settings (compression %, crosshead speed shown to change cooked-rice TPA) | instrument settings needed | EP & TR in literature | LITERATURE_ONLY; cross-study comparable values RARE | MEDIUM |
| 6 | Colour | none found; CIELAB standard in literature; colour kinetics (L*, a*, browning index) in kinetic reviews | illuminant/observer/instrument needed | EP & TR | LITERATURE_ONLY | MEDIUM |
| 7 | pH | static pH-of-foods tables exist only as FDA-derived secondary copies (Clemson extension table cites FDA BAM/AOAC) — primary not opened; pH trajectories (fermentation/cooking) only in papers | — | static EP | static: STRUCTURED (weak, UNVERIFIED primary); trajectory: LITERATURE_ONLY | MEDIUM |
| 8 | Moisture | FDC raw/cooked composition; USDA Cooking Yields R2 moisture gain/loss (173 rows, with n/SD); Bognár yields (ingested); drying curves in literature (abundant) | method only | EP structured; TR literature | STRUCTURED_DB (EP) + LITERATURE_ONLY (TR) | HIGH |
| 9 | Water activity | no verified open structured food-aw database; sorption isotherms in literature; ComBase records aw only as an experimental condition | — | EP/isotherm | LITERATURE_ONLY (structured = RARE) | MEDIUM |
| 10 | Thermal properties (cp, k, ρ, α) | Choi & Okos (1986) composition-based correlations, −40…150 °C, inputs = proximate mass fractions + T (good for cp/ρ, poorer for k/α per a 2021 mortadella validation); proximates from FDC. ASHRAE handbook = copyrighted (DS-042 BLOCKED) | model, not measurement | model-derived | Not a DB: DERIVED via published correlation from STRUCTURED_DB inputs; label value_origin=MODEL_DERIVED, never EVD measured | HIGH (correlation exists) / MEDIUM (accuracy) |
| 11a | Acrylamide | Occurrence: EFSA CONTAM 2015 opinion used 43,419 analytical results (samples since 2010, 24 countries + 6 food associations) — raw EU-pooled data not public; some national monitoring datasets on Zenodo (e.g. BVL Germany, CC BY 4.0; acrylamide inclusion not confirmed). Process effect/kinetics: literature (OpenAlex search "acrylamide potato frying kinetics" = 1,227 hits, upper bound); model-system kinetic anchor Knol et al. 2005 (JAFC 53:6133) | occurrence: product category, not process | EP occurrence; TR in literature | occurrence STRUCTURED (aggregate, plausibility only); process-effect LITERATURE_ONLY | MEDIUM-HIGH |
| 11b | HMF | literature only (e.g. grapefruit-juice continuous-processing kinetics, HMF + browning index) | — | TR | LITERATURE_ONLY | MEDIUM |
| 11c | Furosine | literature only (not found in any structured DB this run) | — | — | LITERATURE_ONLY / RARE | LOW |
| 11d | CML/CEL/MG-H1 (AGEs) | Scheijen et al. 2016 dietary AGE database: 190 foods, UPLC-MS/MS (protein-bound CML, CEL, MG-H1), Food Chem 190:1145–1150; Abertay Glycation Database: >8,257 content values, 50 compounds, >3,231 foods, ~148 publications (licence not stated) | food description (e.g. "canned meat"), no controlled process | EP occurrence | STRUCTURED_DB (occurrence) — process effect LITERATURE_ONLY | MEDIUM |
| 12 | Fermentation (pH/acid/microbial trajectories) | ComBase (>60,000–65,000 records; microbial growth & survival curves under T, pH, aw, preservatives, atmosphere; public domain per data.gov, metadata updated 2025-11-21; food-fermentation LAB coverage UNVERIFIED); fermented-food acidification curves only in papers | T, pH, aw (ComBase) | TR | microbial safety: STRUCTURED_DB; food fermentation chemistry: LITERATURE_ONLY | MEDIUM |
| 13 | Enzymatic transitions (PPO/POD/LOX inactivation; alliinase, myrosinase) | BRENDA Release 2026.1 (March 2026; CC BY 4.0, licence acceptance before download; text 71.6 MB / JSON 79.4 MB) gives in-vitro enzyme parameters, not in-food inactivation kinetics; in-food D/z or k/Ea in literature (OpenAlex "polyphenol oxidase thermal inactivation kinetics" = 4,442 hits) | literature: T, t, pH | TR (literature) | LITERATURE_ONLY (BRENDA = reference prior only) | HIGH |
| 14 | Protein denaturation | literature (DSC Td; cooking loss); USDA yields = outcome proxy only | — | EP/TR | LITERATURE_ONLY | MEDIUM |
| 15 | Starch gelatinisation / retrogradation | literature (DSC onset/peak/conclusion, ΔH; retrogradation time courses); variety/matrix specific | T, water ratio | EP/TR | LITERATURE_ONLY | MEDIUM |
| 16 | Lipid oxidation | literature (PV, TBARS, hexanal; method-heterogeneous) | — | TR | LITERATURE_ONLY; comparable values RARE | MEDIUM |
| 17 | Vitamin degradation kinetics | literature; richest pool (OpenAlex "ascorbic acid degradation kinetics vegetables" = 15,482 hits, upper bound); reviews tabulate parameters (Ling et al. 2015) | T, t (often isothermal), sometimes O2, pH | TR (K1–K2) | LITERATURE_ONLY (rich) | HIGH |
| 18 | Maillard / browning | model systems: Martins & van Boekel 2005 multiresponse glucose/glycine (Food Chem 90:257–269); food browning kinetics in papers | T, t, pH | TR (K3 multiresponse) | LITERATURE_ONLY | HIGH |
| 19 | Process yields | USDA Cooking Yields R2 (173 meat/poultry rows; yield %, n, SD, min, max, moisture & fat change; method only; posted Ag Data Commons 2023-11-30; CC0 per catalog) — LOCAL, NOT INGESTED; Bognár 496 yields (ingested) | method; no T/t | EP aggregate with dispersion | STRUCTURED_DB | HIGH |
| 20 | Kinetic parameters (k, Ea, D, z, order) | NO open compiled food kinetic-parameter database found (targeted search); parameters live in papers and narrative reviews; ComBase only microbial | — | — | LITERATURE_ONLY | MEDIUM-HIGH (absence is a search result, not proof) |

Bottom line Q1: structured data exist only for ENDPOINT aggregates (retention, composition, yield, phenolic RFs, occurrence of acrylamide/AGEs, microbial curves). Everything the simulator/transition steps need as trajectories (vitamin kinetics, enzyme inactivation, Maillard, starch, protein, lipid oxidation, texture, colour, aw, pH trajectories) is LITERATURE_ONLY. Nothing is NOT_REALISTIC in absolute terms, but cross-study-comparable texture, lipid oxidation and absolute volatile quantification are RARE, and furosine is RARE/LOW-confidence. Thermal properties are obtainable only as MODEL_DERIVED values.

### 2.2 Cheap structured wins not yet done (Q2) — confirms census Wave A, with two additions
Already listed in the census: USDA Cooking Yields R2 (local, 173 rows with n/SD), Bognár 11 skipped tables, USDA Flavonoid 3.3, FDC Foundation Foods, FNDDS/FDC portions, INFOODS density v2 (638 entries, 20 food groups, 11 sources — FAO; licence still UNKNOWN), CoFID.
NEW candidates not in the 64-source manifest: (a) Abertay Glycation Database (AGEs/Amadori/volatiles; licence not stated → licence check before use); (b) Scheijen 2016 AGE table (CML/CEL/MG-H1, 190 foods; journal article, values = facts but table reuse to check); (c) EuroFIR eBASIS (glucosinolates for PC-08/PC-10; login/contact required → COMMERCIAL_RESTRICTED); (d) EFSA/national contaminant monitoring datasets on Zenodo (CC BY 4.0 example) for acrylamide plausibility bounds only; (e) VCF (subscription) — park unless budget; (f) Choi–Okos correlations as a property MODEL in the Step-24 registry (not a source).

### 2.3 Kinetic databases (Q3)
No open, compiled, food-matrix kinetic-parameter database was found. Kinetic parameters must be extracted from primary papers (seeded by reviews: Ling et al. 2015, Food Bioprocess Technol 8:343–358). SSOT §211.48 already forbids Arrhenius estimation from food+process+RF aggregates. Consequence: Steps 24/26/27 depend entirely on Steps 11/13/14 literature extraction of K1–K2 series. Confidence MEDIUM-HIGH.

### 2.4 Literature APIs (Q4) — verified 2026 terms
| Service | Licence | Limits (verified) | 2026 change / note | Use in Step 13 |
|---|---|---|---|---|
| OpenAlex | data CC0; "full dataset openly downloadable" | no key 10 req/s; free key 30 req/s (key needed for cursor paging beyond page 1); free account budget "$1 of usage per day", resets 00:00 UTC; pay-as-you-go prepaid; Member $5k/yr ($20/day), Member+ $10k/yr ($100/day, daily snapshot sync); semantic search 1 req/s; per_page ≤100; basic paging ≤10,000 results (help page updated 2026-10-15) | metered model (credits per call; per-call costs on separate page NOT opened → UNVERIFIED). API responses contain a notice asking AI agents to register a key with the user's email — must NOT be done without the user's explicit consent | PRIMARY discovery index (metadata + abstracts) |
| Crossref REST | metadata "almost none subject to copyright… use for any purpose"; abstracts may be copyrighted | public 5 / concurrency 1; polite (mailto) 10 / concurrency 3; Plus 150 / no concurrency cap (page updated 2025-10-16) | observed this run: 3 parallel unauthenticated calls → HTTP 429 (consistent with concurrency 1) | licence/TDM link metadata, DOI resolution |
| Unpaywall | data licence NOT verified this run | ≤100,000 calls/day; email parameter required; snapshot recommended for bulk | — | OA location + licence string |
| Europe PMC | OA subset: per-article CC "or similar" licences; full-text XML FTP updated weekly, PDF monthly | rate limits not documented on the OA page (UNVERIFIED; REST pages returned 403) | — | OA full text for life-science-indexed food papers |
| PMC (NCBI) | per-article licence buckets | — | NLM Tech Bull 2026-02-17: in Aug 2026 PMC FTP article datasets AND the OA Web Service API are retired; PMC Cloud Service on AWS becomes primary; files individual only, NO bulk packages; post-August state not verified | individual file fetch from AWS; not bulk |
| Semantic Scholar | API License Agreement: terminable at any time, no redistribution/sublicensing; dataset licences vary (CC BY-NC, ODC-BY named as examples) | unauthenticated 1,000 req/s shared pool; keyed intro 1 req/s | — | optional ID/citation lookup only; NOT a stored corpus |
| CORE | UNVERIFIED (403 on docs) | UNVERIFIED | — | optional repository full-text fallback after terms check |

Coverage caveat (MEDIUM): much food-engineering literature (J. Food Eng., LWT, Food Chem., JFS) is publisher-hosted and not in PMC; Europe PMC counts in the census underestimate the pool; OpenAlex search covers title/abstract/fulltext and is an upper bound. In this run the OpenAlex `group_by=open_access.is_oa` returned ~98% OA for all three test queries, which is implausible → OA split must be re-measured (pilot), not trusted. Binding constraint for Step 13 is lawful FULL-TEXT access (tables/figures), not discovery.

### 2.5 LLM-assisted extraction credibility (Q5)
Polak & Morgan 2024 (Nat. Commun. 15:1569): conversational-LLM extraction with follow-up verification prompts reached precision and recall "close to 90%" on materials property data. Dagdelen et al. 2024 (Nat. Commun. 15) show fine-tuned LLM structured extraction (joint NER + relation) from materials text. Neither is food-process data with multi-field conditions; SSOT §205.5 already states multi-field condition extraction is not reliable enough to skip human review. Consequence: plan LLM-proposes / human-verifies, with field-level precision measured in Step 10. Confidence MEDIUM (cross-domain transfer).

---------------------------------------------------------------------
## 3. Architecture recommendation
R1 TWO-TRACK EVIDENCE ACQUISITION, with planes kept apart
- Track S (structured, Step 12): endpoint aggregates only (E3, design=DATABASE_AGGREGATE). Finish the cheap wins (§2.2). Each row keeps aggregation level (sample / mean-of-samples / compiled mean), dispersion (n, SD/SE/min/max, dispersion_type) and `imputed_from` (R6 imputes from similar foods). No kinetics derived (SSOT §211.48). Occurrence databases (EFSA acrylamide, AGE tables, VCF) go in an OCCURRENCE sub-plane used for plausibility bounds and priors, never as process-effect EVD.
- Track L (literature, Steps 10/11/13/14): discovery OpenAlex (CC0) → licence via Crossref + Unpaywall → full text only where lawful (Europe PMC OA FTP, PMC Cloud on AWS per-file, CC-BY journals) → LLM-proposed extraction with span/table/figure pointer → human verification (SSOT §203.6). Seed with review-anchored citation snowballing (Phenol-Explorer's 125 papers; kinetic reviews such as Ling 2015; SSOT anchors Knol 2005, Martins & van Boekel 2005) rather than keyword-only search; use keyword queries (`registry/evidence_query_matrix_v1.csv`) for recall expansion.
R2 DEPTH BEFORE BREADTH, organised by the SSOT K-hierarchy (§210.28): triage every candidate study as K0–K4 at abstract stage. Steps 24/26/27 need K2 (multi-T × multi-t) series in ONE focused system with enough independent studies to hold some out study-disjointly. Breadth (more matrices) only after that cell is full.
R3 FOCUSED SYSTEM for the first simulator (look-ahead to 26/27): ascorbic-acid (vitamin C) thermal degradation/leaching in vegetables is the best-supplied candidate (largest literature pool, K1–K2 designs common, first-order + Arrhenius established, links to existing R6/Bognár/USDA endpoint data for endpoint cross-checks). Potato acrylamide is the SSOT-named anchor (§210.29A) with occurrence data for plausibility, but in-food formation needs co-reported precursors (asparagine, reducing sugars), moisture and surface temperature → higher identifiability risk. Recommend vitamin C as primary, acrylamide as secondary; decide with the Step 10 K-level yield measurement (MEDIUM).
R4 Thermal properties via Choi–Okos as a registered PROPERTY MODEL (Step 24), inputs from FDC proximates, outputs tagged MODEL_DERIVED with stated validity −40…150 °C and known weaker k/α accuracy.

Rejected alternatives
- Estimating rate constants / Ea from R6/Bognár/Phenol-Explorer endpoints — forbidden (SSOT §211.48); no T/t recorded.
- Treating FooDB/FlavorDB2/VCF composition as process-effect evidence — presence ≠ process effect; FooDB NC; FlavorDB2 licence unknown; VCF subscription.
- Buying VCF / eBASIS now — commercial/login; value for process effects unproven; park until a Step-14 coverage cell explicitly needs it.
- Semantic Scholar as the stored corpus — revocable licence, no redistribution.
- Bulk PMC packages — retired Aug 2026 (no bulk packages on AWS).
- Paywalled publisher TDM / scraping — BLOCKED_LICENSE (DS-041); H2 required anyway.
- ASHRAE handbook tables — copyrighted; replace with the Choi–Okos correlation.
- Keyword-only mass harvesting at Step 13 before the Step 10 pilot — census Wave D already conditions this on measured precision/throughput; I agree.

---------------------------------------------------------------------
## 4. What each affected step must change or add
STEP 10 (20-row mechanism pilot) — MODIFY
- Pick the pilot system for downstream value: vitamin C or potato acrylamide (both feed Steps 24/26/27). Garlic alliinase has the smallest OA pool (24 title/abstract OA hits, census §5) and no simulator path. The census already leans to acrylamide; I add vitamin C as a co-candidate.
- Per row record: K-level; value source (table / text / figure-digitised); n; dispersion type; condition completeness; licence of the source document; human minutes per row.
- Metrics: field-level extraction precision/recall vs human (separately for value, unit, T, t, matrix, method); fraction of rows with full T/t; K2-series yield per 100 screened abstracts; human minutes/row. Gate: report these numbers. Thresholds are set by human approval before running, never after.
STEP 11 (Wave-1 verified evidence) — MODIFY
- Target: complete K1–K2 series for the chosen focused system, enough independent STUDY groups for a study-disjoint held-out set in Step 27. Planning heuristic, not a literature standard: ≥8–10 independent studies so that ≥3 can be held out. The SSOT's ≥3–4 temperatures × ≥4–5 times rule is [SOURCE-REPORTED/PILOT], §210.29A.
- Requires the trajectory/kinetic table (see §5) to exist first.
STEP 12 (structured database evidence) — MODIFY
- Ingest USDA Cooking Yields R2 (173 rows, keep n/SD/min/max), Bognár 11 tables, FDC Foundation (sample-level rows; keep unpaired raw/cooked semantics: any "apparent retention" from FDC is DERIVED and needs a yield factor), USDA Flavonoid 3.3. After licence check: INFOODS density, CoFID, Glycation DB / Scheijen 2016 (occurrence plane), ComBase (microbial lane only).
- Schema: sd, se, dispersion_type, n_samples vs n_replicates, aggregation_level, imputed_from, value_origin (MEASURED / COMPILED / DERIVED / MODEL_DERIVED), occurrence_vs_process_effect flag.
- Gate: no row without licence status; no kinetic parameters derived.
STEP 13 (large literature discovery corpus) — MODIFY
- Corpus = metadata + abstracts (OpenAlex CC0), with per-document licence/TDM status (Crossref + Unpaywall) and full-text pointers. Full text is stored only where lawful; otherwise store pointers + human-verified extracted values + spans.
- Rate plan: OpenAlex free key (30 req/s, $1/day budget; the user creates the key, the agent never self-registers); Crossref polite pool (mailto, ≤3 concurrent); Unpaywall ≤100k/day; PMC AWS per-file.
- Metrics: known-item recall on a seed set (Phenol-Explorer's 125 papers + kinetic-review reference lists); triage precision on a human-labelled sample; K-level distribution; OA-full-text fraction (re-measured, not taken from group_by).
- Compute: CPU-only, streamed and checkpointed; no GPU.
STEP 14 (coverage-driven growth) — KEEP + CLARIFY
- Coverage cells = matrix × process × target × K-level (not only matrix × process). Use value-of-information acquisition (SSOT §224.8). Per-cell stop rule: stop when the cell reaches K2 with the target number of independent studies, or when two successive search rounds add no new independent study.
- Record cells that cannot be filled (texture, lipid oxidation, aw, furosine) as declared gaps.
STEP 15 (freeze DATA-EVIDENCE v1) — MODIFY
- The freeze manifest must include: per-document licence manifest; E-tier × K-level counts per focused system; study-disjoint split manifest built from Step 08 lineage; declared-gap register (LITERATURE_ONLY/RARE classes); and occurrence vs process-effect planes kept separate.
STEP 24 (formula/model registry) — MODIFY
- Each model entry carries: parameter_source_rows (pointer to kinetic table), parameter K-level, parameter CI, validity domain (T range, matrix, aw/pH), value_origin.
- Add PROPERTY_MODEL entries (Choi–Okos cp/ρ/k/α) with input requirements (proximate fractions from FDC) and known accuracy limits.
- Models without K≥1 support get status QUALITATIVE_ONLY.
STEP 27 (validate simulator on held-out evidence) — MODIFY
- Held-out = study-disjoint K1+ trajectories never used in calibration, preferably from different labs/matrices.
- Endpoint aggregates (R6/Bognár) can test endpoint plausibility only, with process conditions UNKNOWN. They cannot validate a time–temperature simulator.
- Occurrence data (EFSA acrylamide) gives range checks only.
- Fail → RESEARCH_ONLY status (brief §40).

---------------------------------------------------------------------
## 5. Look-ahead requirements for earlier steps
- Steps 04/05 (EVD contract, normalised EVD): add a TRAJECTORY / KINETIC-EXPERIMENT table (SSOT §216.2 kinetic_experiment_id, temperature_schedule, timepoints, observations, fitted params, uncertainty, identifiability; raw timepoints kept separately) and §210.29 fields. The current EVD is endpoint-only with no KIN ledger. Without this, Step 11 would flatten series into endpoints and Steps 24/27 would lose their inputs. Also add dispersion and aggregation-level fields. This is the single most important look-ahead finding.
- Step 06 (manifest): update DS-033 (PMC route change confirmed as planned: FTP/OA API retired Aug 2026, AWS individual files only), DS-031 (OpenAlex now metered: key + $1/day free budget), DS-035 (Crossref limits 5/1, 10/3, 150), DS-036 (100k/day). Add new rows: Abertay Glycation DB, Scheijen 2016, eBASIS, VCF (commercial), EFSA/national Zenodo occurrence sets. Record the Choi–Okos model as a registry item, not a source.
- Step 07 (condition normalisation): support time–temperature schedules (not single T/t; Master Plan Part W2 agrees), core vs medium vs surface temperature, heating-medium ratio (leaching), O2/packaging, pH and aw as both conditions and state variables. Also store instrument settings for texture (probe, compression %, speed) and colour (illuminant/observer, colour space).
- Step 08 (source lineage): independence groups must link a thesis and its journal paper (e.g. Knol thesis DOI 10.18174/122035 and JAFC 2005) and review-reported vs primary values, and track figure-digitised series back to the source figure.
- Step 09 (extraction machinery): extract from tables AND figures (digitisation with an uncertainty flag), run field-level verification UI, carry licence status on every extracted value, and store spans only for non-CC documents.

---------------------------------------------------------------------
## 6. Residual uncertainty and pilot vs reading
UNVERIFIED / open: OpenAlex per-call credit cost; Europe PMC rate limits; CORE terms; Unpaywall data licence; post-August-2026 PMC state; ComBase coverage of food-fermentation LAB and its terms page; Glycation DB licence; VCF price/terms; FDC Foundation current food count; static aw/pH primary sources; actual OA full-text fraction for food-engineering journals; K2-series yield per 100 abstracts for vitamin C vs acrylamide.
A pilot is now cheaper than more reading (stop rule §8.5). A 100-abstract triage sample per candidate system (vitamin C, acrylamide), labelled for K-level and full-text accessibility, costs a few human hours. It would settle the focused-system choice and the Step 13 sizing, which no further desk research can do. This fits inside Step 10 and needs no new step.
