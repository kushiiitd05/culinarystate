# mp_part1 — Final Master Plan v4.0, lines 1–2460 (READER notes)

Source: `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md` (cited as **MP Lnnn**). SSOT = `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` (cited as **SSOT Lnnn**). All lines 1–2460 were read in full (headings + bodies). Repo cross-checks are read-only and marked "repo-verified" or UNVERIFIED.

Scope reminder: the 36-step "Master Execution Plan v1" is NOT in the repo (ctx.md L13–16). Nothing in MP v4.0 uses the 36-step numbering; every mapping in §8 below is my reconstruction from MP block/part content. MP v4.0 is organised as Parts A–E (identity, laws, interaction, session OS, program structure B00–B17), H (IDs/ledgers), I (state-change KB), J (quantity), K (NER), L (models), M (EDA), N (hypothesis ladder), O–P (research spawns RS-00…RS-17, RS-EDA), Q (experiment protocol), R (compute), S (GitHub), T (deliverables DEL-1…5), U (first 14 days), V (templates), App. 1–3, then the v2.0 normative extensions W (evidence-on-demand compiler), X (extra ledgers), Y (agent harness), Z (expanded spawn bank), AA (EDA), AB (bench/lab). Parts AC–AF lie beyond L2460 (other reader).

Precedence note: MP L6 says Parts W–AF are "normative v2.0 extensions" that govern over Parts A–V when more specific, unless they conflict with SSOT-frozen statements, course contract, licence, safety or explicit human decision. MP L56–61: SSOT frozen statements beat everything; never reinterpret SSOT fields; change only via versioned CR (D5, MP L200–211).

---

## 1. Definitions, entities and data contracts

### 1.1 Mission formulae (MP L25–33)
- `CulinaryState-RAG = State + Evidence + Transition + Constraints + Uncertainty + Decision` (MP L26).
- Data foundation: `Real Recipes + Semantic Annotation + Quantity/Portion Grounding + Evidence Provenance + Gold/Silver QA` (MP L32).
- FlavorTwin V2 = second application, kept at SSOT §246 boundary (MP L35).
- "Done" = every component built only after sub-experiments ran, results recorded, hypotheses passed Part N ladder, gate passed (MP L37–44).

### 1.2 Laws (Part B, MP L73–105) — load-bearing definitions
- L76 law 1: never invent quantity/temperature/pH/duration/concentration/property/intermediate/mechanism/condition (SSOT §239.1 rules 1–20 verbatim).
- L77 law 2: UNKNOWN preferred; missing = masks, never 0; non-detects = censored, not zero (§144.2, §222).
- L78 law 3: **provenance enum** `EXPLICIT_SOURCE | EXTERNAL_VERIFIED | DERIVED_DETERMINISTIC | INFERRED_LLM | MODEL_ESTIMATED | IMPUTED | SIMULATED | UNKNOWN`; "never promote the last five to observed or Gold" (INFERRED_LLM, MODEL_ESTIMATED, IMPUTED, SIMULATED, UNKNOWN).
- L79 law 4: prediction precision ≤ evidence precision.
- L80 law 5: empirical-first (Bagler principle) → Part N ladder.
- L81: procedure/state graphs ≠ chemistry truth; culture ≠ mechanism; structural ≠ sensory similarity; cultural prevalence ≠ flavor similarity (§279.2).
- L82: never average pH; never infer concentration from presence; never infer chemistry from generic verb without approved evidence.
- L83: conflicts preserved as conflict records.
- L84 law 9: **food identity, form, state, process, quantity, unit, size, role, intermediate identity are different variables** (key for Steps 03/16).
- L88: LLM = semantics/extraction/proposals; deterministic code = arithmetic, schema, units, IDs, provenance, dedup, stats.
- L89: Silver ≠ Gold; Deep Gold independent and protected from anchoring (§236–237).
- L90: baselines before models; keep simpler on tie; report negative (§248.3).
- L91–94: leakage: duplicate/source/lineage families formed **before** splitting; no tuning on locked test; random split only sanity.
- L95–96: version everything; append-only ledgers, stable IDs, corrections = new versions.
- L97: no claims beyond gates; read §257P before large build.
- L101–105: conduct laws (approval, no email/push/money/large compute without approval, polite scraping, honest authorship, respectful to CoSyLab).

### 1.3 Hierarchy (MP L217–227)
PROGRAM → LEVEL (L0–L17 + L13E + D1–D5) → BLOCK (B00–B17) → WORK PACKAGE (WPxx.y, 1–5 days, one owner one reviewer) → EXPERIMENT (SSOT ID or SX-xx-yy) → SUB-EXPERIMENT (SX-xx-yy.z) → TASK/TEST/COMMIT. L0–L11 frozen; L12–L16 spec complete, empirical gates open; L13E parallel; L17 optional (MP L231).

### 1.4 Part H1 ID scheme (MP L533–552) — exact
| NS | Object | Dedup key |
|---|---|---|
| SRC- | source/dataset/paper/API | DOI/URL/repo SHA + version |
| REC- | recipe (immutable raw) | content hash; family `FAM-` via MinHash ≥ 0.8 on instructions + title/ingredient signature (L538) |
| ING- | canonical food concept | curated; alias registry |
| LOT-/ENT- | recipe-local entity/version | recipe ID + ordinal |
| MOL- | molecule | full InChIKey; first block for skeleton grouping |
| PROC- | process node | curated; synonym registry |
| COND- | condition (T, t, pH, aw, P, medium, O₂) | normalized tuple + unit |
| QTY- | quantity expression | recipe/line/span |
| UNIT- | unit | curated |
| POR- | portion/density evidence | source + food + form + packing |
| EVT- | recipe event | recipe + step + ordinal |
| EVD- | scientific evidence row | source + matrix + process + condition + target |
| RXN- | reaction | reactant & product InChIKeys + mechanism family + conditions |
| WARN- | warning rule | trigger signature + evidence IDs |
| HYP- | hypothesis | registry |
| EXP-/SX- | experiment | registry |
v2.0 additions (Part X/W): SVAR- (W3 L1511), MEAS-, STUDY- (W5 L1658), TOOL- (X1 L1923), INST- (X2 L1947), API- (X3 L1970), CLM- (X4 L1993), SNAP- (X5 L2012), MODEL- (X6 L2028), SAMPLE- (X7 L2049). App. 3 glossary (MP L1394–1413) lists B00–B17, WP, SX, RS, HYP, RQ16/E16/G16, RQ13E/E13E/G13E, G13/14/15, T0–T9, D0–D11, Q0–Q6, **E1–E7 (state-change evidence tiers)**, P0–P10, E0–E14 (merged plan), DEL-1…5, H1–H8.

Repo-verified: `ledgers/data/` contains ALIAS, ALLERGEN, COND, DATASET, EVD, EXP, IMAP, ING, KGE, MEAS, MOL, PROC, REC, SNAP, SRC, STUDY, SVAR, TOOL, UNIT, _ids. **Absent** relative to Part H/X: QTY, POR, EVT, RXN, WARN, HYP, LOT/ENT, FAM, INST, API, CLM, MODEL, SAMPLE (recipe_base / recipe_identity parquet exist git-ignored per ctx.md L20). Present but not in H1: IMAP, KGE, ALLERGEN, DATASET, ALIAS (ALIAS is H2 item 2's surface-form ledger).

### 1.5 Part H2 ledgers (MP L554–577) — fields
1. Source manifest: licence, retrieval date, checksum, storage rule, robots/terms notes (L556).
2. Ingredient-name ledger: surface → canonical candidates, link band, probability, provenance (L557).
3. Canonical-form ledger: concept + facets (variety, part, form, prep state, size, dry/fresh, packing, brand, locale sense); product-vs-modifier decision; relations DERIVED_FROM, HAS_INGREDIENT, IS_VARIANT_OF (L558).
4. Molecule ledger: InChIKey, SMILES, CID, names, physchem props, odor/taste descriptors + thresholds, each with provenance (L559).
5. Ingredient–molecule ledger: presence, concentration + unit + method if evidenced, detection limit, source (L560).
6. Process ledger: node + parameters, prerequisites, mechanism links, safety notes (L561).
7. Condition ledger: typed values/intervals, status measured/range/qualitative/unknown (L562).
8. Quantity ledger: raw text, parsed structure, normalized value/interval, conversion path with POR- evidence, allocation (fraction, basis, parent), uncertainty source variable (L563).
9. Event/state ledger: events with inputs/outputs, tools, conditions, endpoint; trajectory `PLANNED | OBSERVED_SESSION | PREDICTED`; before/after entity versions; `OMITTED_STEP_CANDIDATE` (L564–568).
10. EVD: ingredient/matrix, prior state, process, conditions, target variable, value/direction/retention/log-fold change, unit, method/platform, tier, study ID, censoring flag (L569).
11. RXN: reactants, products, mechanism family, condition window, marker compounds, evidence, confidence; reaction SMARTS/SMILES where possible (L570).
12. WARN: trigger (ingredient × process × condition × state × tool × user context), message, severity, evidence IDs, authority source, suppression rules (L571).
13. Hypothesis ledger: Part N state (L572).
Rules (L574–577): raw text and spans always preserved; normalization = new column, never overwrite; every batch emits §236.7 statistics + §257G audit tables. Validation stack: Pydantic/JSON Schema + pandera/Great Expectations (L554).

### 1.6 Evidence tiers (Part I1, MP L587–596)
E1 controlled experiment with measured conditions; E2 partial conditions; E3 DB aggregate (USDA RF, Phenol-Explorer); E4 LLM-extracted human-verified; E5 LLM-extracted unverified; E6 mechanism-family rule/heuristic (`MODEL_ESTIMATED`); E7 simulator output (`SIMULATED`). **"Only E1–E4 can enter evaluation sets. E6–E7 are priors or stress tests only"** (L595). Recipe corpus "never chemistry ground truth" (L596). "≈100k dataset" = "≥ 100k evidence-bearing rows across tiers ... not 100k invented completions" (L586; also B06 L359).
- **Divergence**: SSOT §201.7 (SSOT L16651–16661) defines only E1–E6 and E6 = "heuristic / qualitative / weak inference". E7 is an MP addition. Repo `registry/evidence_tier_provenance_map_v1.csv` adopts MP's E1–E7 (E7 = SIMULATED, "never Gold truth").
- MP is silent on E5 eligibility for training; repo map says "restricted: candidate generation only".

### 1.7 Transition cell (W1, MP L1431–1448)
`C = (matrix/ingredient, S_before, P, Θ, Y)` — matrix not molecule name; S_before known prior state; P canonical PROC-; Θ condition profile; Y one state variable/analyte/reaction/sensory/safety target. "A cell is covered only if the ledger contains evidence whose applicability to the requested matrix/process/condition/target is explicitly recorded" (L1448).

### 1.8 Condition profile COND- (W2, MP L1450–1509)
Record: typed values, intervals, raw source values, normalized values, units, masks, provenance, measurement status (L1452). Axes:
- time: start/end, duration, trajectory, rest/hold phases.
- temperature: setpoint, medium T, surface T, core T, time–T trajectory, heating/cooling rate, preheat status, uncertainty/measurement location.
- chemical: pH initial/final/trajectory, titratable acidity, aw, moisture/dry matter, oxygen/headspace, salt, sugar, fat/oil level, solvent/medium, additives/catalysts/enzymes.
- physical: pressure, humidity, flow/mixing/agitation, heat-transfer mode, power level when T absent, microwave power/frequency, geometry/thickness/particle size, SA:V proxy, batch size, container fill, tool/utensil/material ID.
- biological: organism/strain/starter, ripeness/maturity, storage age, fermentation inoculum.
Rules (L1504–1509): oven setpoint ≠ core T; "medium heat" qualitative unless a source defines a distribution; never average pH; preserve time-varying profiles; keep masks; store measurement method + location.
Repo-verified: `registry/condition_variable_registry_v1.csv` has 40 variables (CV-001…CV-040); `COND.jsonl` (4,746 lines) sample rows (USDA import) carry only a 5-axis completeness mask {duration, moisture, ph, pressure, temperature} with UNKNOWN status — i.e. imported DB rows have almost no condition content.

### 1.9 SVAR- registry (W3, MP L1511–1571)
Families: PHYSICAL (mass, moisture, aw, volume, density, phase, viscosity, texture/force/rheology, colour L*a*b*, browning index, particle size, microstructure, surface/core T); CHEMICAL (named compound conc., precursor conc., product conc., nutrient retention, volatile abundance, pH/acidity, oxidation markers, reaction progress, kinetic parameter); SENSORY (descriptor, intensity, threshold/OAV when supported, panel method); PROCEDURAL (form, cut, location, mixture/intermediate identity, cooked/raw/fermented); SAFETY (pathogen-control condition, allergen/cross-contact state, hazardous degradation marker). Per variable: canonical name, unit/dimension, value type (scalar/interval/category/vector/trajectory), preferred methods, comparability notes, transformation rules, **observable-in-session vs only-inferred-scientifically** (L1571). Every EVD- row points to exactly one SVAR- (L1513). Repo: `registry/state_variable_registry_v1.csv` 254 data rows; SVAR.jsonl 355 lines; `svar_duplicate_mapping_v1.csv` exists.

### 1.10 EVD- expanded record (W4, MP L1573–1656) — field-level
- identity: evidence_id, source_id, study_id, extraction_version, curator/verifier, timestamps.
- matrix: ingredient_id, variety/cultivar/species, food part, form, prior processing, initial state, mixture/intermediate composition, sample geometry/particle size, storage/ripeness state.
- process: process_id, process family, tool/utensil/material IDs, medium, condition_id, condition completeness mask.
- target: state_variable_id, analyte/molecule_id, reaction_id, measurement basis (wet/dry/fresh weight; per serving; headspace…).
- before / after: value, unit, uncertainty, LOD/LOQ/censoring, measurement method/platform (each).
- derived: delta, % change, retention factor, log fold-change, rate/kinetic parameter if justified, direction only when harmonization impossible.
- evidence: design (controlled experiment/observational/DB aggregate/review), sample size/replicates, source span/table/figure/page, DOI/URL/version, tier E1–E7, provenance class, human verification, conflict cluster, source independence group.
- applicability: exact/near/analogous/generic, interpolation domain, extrapolation flags, matrix similarity rationale, process similarity rationale, condition distance, trust horizon.
- "No row enters Gold evaluation without source traceability" (L1656).
Repo-verified: EVD.jsonl = 57,280 version lines, 18,156 distinct IDs, 56,828 ACTIVE / 452 DEPRECATED lines, **100% tier E3**; applicability GENERIC 43,392 / EXACT 13,888 lines; study_id_status NOT_IDENTIFIABLE 43,392 / PRESENT 13,888; verification UNVERIFIED in sampled rows. (ctx says ES-1.1 export 17,978 rows — the 178-ID gap vs 18,156 is UNVERIFIED; plausibly deprecated IDs.) No before/after split in the USDA sample row: value sits in `derived.retention_factor` with censor `GT_CAP` limit 97.5.

### 1.11 MEAS- and STUDY- (W5, MP L1658–1687)
MEAS-: measurement family (HPLC, LC-MS, GC-MS, GC-IMS, spectrophotometry, gravimetry, texture analyser, colorimeter, pH meter, sensory panel…), protocol/extraction, calibration, matrix basis, units, LOD/LOQ, normalization, comparability limitations, source.
STUDY-: design, matrix & sample prep, controls, replicates, randomized/blinded, analytical platform, process equipment, condition completeness, source, study-level quality flags.
Rule: never average across incompatible platforms without an explicit harmonization experiment (L1687).
Repo: MEAS.jsonl 3 lines; measurement_method_registry 11 rows; STUDY.jsonl 125 lines, sampled rows have `design: UNKNOWN`, no replicates/platform — STUDY is a stub (Phenol-Explorer papers). **No EXPERIMENT/SAMPLE/MEASUREMENT/AGGREGATE layers** for literature (SAMPLE- in X7 is in-house bench only, L2049–2069).

### 1.12 RXN- (W6, MP L1689–1725)
Defined reaction: reactants/products (InChIKeys), stoichiometry if known, mechanism family, condition window, rate law/kinetic params when identified, reaction SMARTS when meaningful, matrix applicability, evidence IDs. Otherwise relation vocabulary: FORMED, DEGRADED, RETAINED, VOLATILIZED, LEACHED, OXIDIZED, REDUCED, DENATURED/AGGREGATED, GELATINIZED, ISOMERIZED, FERMENTED/CONSUMED, UNKNOWN_TRANSFORMATION (L1709–1720). "Never manufacture a balanced reaction" (L1723); for roasting/frying/fermentation/smoking/pyrolysis model the measured subset + family (L1725).

### 1.13 Dynamic state compiler (W7, MP L1727–1766)
Input S_t, P_t, Θ_t, H_t. Steps: (1) resolve process/tool/medium/condition; (2) query local EVD/RXN exact; (3) else near evidence under compatibility hierarchy; (4) if insufficient/stale/conflicting → W9 refresh; (5) compile only supported changes (physical, measured composition, formed/degraded/retained links, quantity/mass allocation, procedural state); (6) UNKNOWN for unsupported; (7) recompute representation only from observed/verified state, supported transition estimate, masks+uncertainty; (8) emit S_{t+1}, evidence links, uncertainty/evidence class, OOD/extrapolation flag, warning triggers; (9) append trace, never overwrite S_t. Geometry-only evidence → update geometry only (L1764). The "compatibility hierarchy" (step 3) is **not defined** anywhere in L1–2460.

### 1.14 Representation update contract (W8, MP L1768–1791)
`z_{i,t} = F(z_i, S_t, P_t, Θ_t, H_t, M_t)`, M_t = explicit missingness/evidence mask (L1773–1776). Views: z_identity, z_structural, z_physchem, z_composition, z_sensory, z_process, z_culinary_context, z_evidence (L1781–1788). Unsupported → mask or retain prior with explicit uncertainty rule; never overwrite static identity embedding (L1791). (B12 L464 states the older form without M_t.)

### 1.15 W9 refresh triggers / order (MP L1793–1835)
Triggers: NO_LOCAL_EVIDENCE, LOCAL_EVIDENCE_BELOW_REQUIRED_TIER, CONDITION_OUTSIDE_LOCAL_SUPPORT, MATERIAL_CONFLICT, SOURCE_RETRACTED_OR_UPDATED, SAFETY_STANDARD_REQUIRES_FRESH_CHECK, DATASET/API_NEW_VERSION_AVAILABLE, HIGH_VALUE_CELL_SELECTED_BY_VOI. Source order 1–7: local ledgers/cache → official API/bulk → primary paper → recognized DB → open code/data repo ("not scientific truth by itself") → practitioner (hypothesis) → community (hypotheses/failure modes only). Per source: licence/terms/robots; retrieval date/version/hash; exact span/table/figure locator; candidate rows; deterministic validation; verify priority/claim-bearing rows; append-only; rerun experiments only after new ledger version frozen (L1820–1829). Freshness defaults are "proposals, not hard facts" (L1831–1835).

### 1.16 W10 query generator (MP L1837–1854) — 8 query families; synonyms from ledgers, scientific/cultivar/historical names; **record which queries were tried so failure-to-find is reproducible** (L1854).

### 1.17 W11 process condition template (MP L1858–1868): required axes, optional axes, typical observables, likely mechanism families, tool/medium dependencies, safety-critical fields, known source families. Priority = f(recipe freq, process freq, user relevance, evidence gap, uncertainty, scientific importance, warning importance, downstream benchmark need) — "multi-criteria queue until a weighting scheme is empirically justified" (L1886). "No requirement exists to populate every 10,000 × 300 combination" (L1890).

### 1.18 W12 consensus outputs (MP L1892–1915): group by independent study/lineage → harmonize units/basis → stratify matrix/cultivar/form/process/condition → is disagreement explained by conditions → heterogeneity → preserve conflict → never count mirrors/reposts as independent. Labels: CONSENSUS_SUPPORTED, CONDITIONALLY_SUPPORTED, MIXED/CONFLICTING, SINGLE_SOURCE, INSUFFICIENT, UNKNOWN. "No LLM majority vote substitutes for scientific synthesis" (L1915).

### 1.19 Part X ledgers (MP L1919–2069)
- TOOL- (L1927–1943): tool_id, preferred_name, aliases/regional, tool_family, material/coating, geometry, capacity/size, heat-source compatibility, pressure capability, thermal props when evidenced, reactivity/corrosion notes, process compatibility, cleaning/maintenance, warning links, provenance. Never invent "safe maximum temperature" (L1945). Repo TOOL.jsonl 297 lines.
- INST- (L1951–1966): raw span, language/script, normalized verb, process candidate IDs, arguments, quantity mentions, time/temp mentions, endpoint phrase, implicit subject/object, coreference pointers, negation/optionality, sequence relation, confidence, source. Stored **separately from the event graph** (L1949). Not in repo.
- API- (L1974–1990): provider, resource, endpoint, version, schema hash, auth, rate limits, terms/licence, allowed storage, allowed redistribution, IDs/crosswalks, pagination, last checked, status, fallback, owner/contact.
- CLM- (L1997–2007): claim_id, exact wording, scope, HYP IDs, EXP IDs, data versions, metric+CI, gate, evidence IDs, status DRAFT/SUPPORTED/QUALIFIED/REJECTED/RETRACTED. "No claim leaves the repo without a CLM-" (L2010).
- SNAP- (L2016–2025): source_id, retrieval timestamp, URL/DOI/repo SHA, ETag/version, content hash, licence snapshot, raw-storage permission, local cache path, parser/extractor version. Repo SNAP.jsonl 347 lines.
- MODEL- (L2032–2046): model_id, task, architecture/base, training data versions, split IDs, seed, hyperparameters/config hash, checkpoint hash, licence, metrics/CIs, calibration, known failures, promotion gate, deployment status. **This is an ML model registry, not a mechanistic formula/model registry.**
- SAMPLE- (L2053–2068): sample_id, matrix, lot/source, prep, mass, geometry, replicate, process, condition record, methods, raw measurements, QC/calibration, operator, date, tier. In-house bench only.

### 1.20 Quantity contracts (Part J, MP L649–687)
Three non-collapsible problems (§235.1): deterministic physical conversion; culinary volume by locale; volume/count→mass grounding needing POR- evidence (Q0–Q6). Unit map per unit: type (physical/culinary-volume/count-portion/package/verbal-qualitative), dimension, canonical SI value **or interval** per locale with source, ambiguity notes, allowed food classes (L659–664). Must-include list L667–672 (tsp, tbsp incl. half-tbsp, dessert spoon, cup variants, fl oz, glass, katori, pinch, dash, smidgen, drop, splash, handful, clove, fillet, slice, head, bunch, sprig, stick, can/tin/packet; sugar-syrup string stages = endpoint descriptor not volume; g, kg, oz, lb, mL, L). Verbal quantities stay QUALITATIVE; empirical distribution only as `CONVENTION` or `RECIPE_CORPUS_EMPIRICAL_DISTRIBUTION` (Q4), never in totals without flag (L674). Pipeline L679–684: raw span → grammar parse → unit resolution (locale from source else AMBIGUOUS) → deterministic conversion same dimension → grounding (portion/density record chosen by decision layer; code computes; Q-level recorded) → symbolic allocation → final interval g/mL/count + Q-level + provenance + UNKNOWN. Property tests L687: dimensional consistency, idempotence, raw-text round trip, no invented grams, interval coverage, correlated uncertainty under splits.

### 1.21 Warnings (Part I5, MP L629–645)
Classes: ingredient behaviour, utensil, food safety (temps, cross-contamination, allergens), process prerequisites, storage. Each rule: evidence chain (EVD/RXN/authority), trigger signature, severity, explanation, mitigation. "No warning without evidence. Safety-critical text comes only from authoritative sources" (L645). Food-safety temps: USDA FSIS, FSSAI only (L615).

### 1.22 Part I2 representation per (matrix × process × condition window) (MP L598–607)
Physical (moisture/aw, mass loss, texture, colour L*a*b*, phase, surface vs core T); chemical (precursor depletion, product formation, retention/loss, pH shift, markers, mechanism family list: Maillard/Strecker, caramelization, lipid oxidation, protein denaturation/aggregation, starch gelatinization/retrogradation, collagen solubilization, alliinase/LFS, myrosinase, LOX/HPL, PPO browning, fermentation, pyrolysis, pigment transitions, leaching/volatilization); molecular change via RXN- or formed/degraded/retained/unknown; sensory only with sensory evidence (§145); session dynamics: state version advances per event, recomputed from evidence-backed transition or UNKNOWN beyond trust horizon (L607). Delta profile ΔS=[ΔC, ΔP^phys, ΔY^sens, ΔN, ΔV, ΔA] (B06 L351, §107).

---

## 2. Models and baseline ladders

### 2.1 Part L table (MP L715–724) — "Baseline first → Then → Promotion evidence"
| Family | Simple | Advanced | Promotion |
|---|---|---|---|
| Molecular z_m | fingerprints + descriptors + kNN/LR | GNN (MPNN/GIN), MolFormer/ChemBERTa/Uni-Mol, odor-map-style | T1–T4 benchmarks; scaffold splits |
| Ingredient z_i | mean/max of z_m; co-occurrence PMI/SVD | DeepSets/Set Transformer/attention; multi-view contrastive | §181; frequency-bias audit |
| Recipe z_R, cuisine z_C | bag-of-ingredients TF-IDF; mean z_i | set/graph/text encoders; frequency-debiased | §191 leakage-controlled |
| Process z_P | one-hot + family hierarchy + physics descriptors | learned verb embeddings; hyperbolic (stretch) | process-disjoint splits |
| State/transition | persistence, mean-delta, retrieval, LightGBM/TabPFN | FiLM/cross-attention; kinetic+residual hybrids; state-space (if trajectories) | G14/G15 |
| NER/linking | CRF, spaCy-trf, Ingredient Parser | DeBERTa±CRF, GLiNER2.5, kNN-NER, retrieval-augmented verifier | Part K |
| Decision layer | logistic over features; cross-encoder | Jev (closed-set, calibrated by us), GLiNER2.5-Decide | merged plan E14 |
| Quantity z_q | deterministic features + masks | learned z_q (§235.7) | RQ16-23 |
Training rules (L726–729): pretraining/fine-tuning terminology per §110; pretraining corpora never include test families; every model has a card.

**Gap vs SSOT D0–D11 (SSOT §209.17, L18543–18600)**: D0 persistence, D1 global mean-delta, D2 process-conditioned mean-delta, **D3 hierarchical shrinkage/partial pooling (food class, process family, target class, study/source)**, D4 nearest-evidence retrieval, D5 GBDT, D6 TabPFN, **D7 evidence-aware low-rank/factorization completion (biased MF, BPMF/Macau, FM, coupled tensor)**, D8 classical kinetics (zero/first/nth, Arrhenius, Weibull, formation/degradation, compartment), D9 hybrid mechanistic+residual, D10 neural multi-output/latent dynamics ("not allowed to skip D0–D7"), D11 UDE/neural ODE/reaction networks, focused time-resolved only. MP Part L's transition row omits D3 and D7; B13 L474 just says "D0–D11 ladder"; SX-13-03 (L478) and DEL-2 (L1249, "MF/FM with side information") partially cover D7.

### 2.2 Block-level ladders
- B04 (L322–326): SX-04-02 fingerprint-family bake-off; SX-04-03 set aggregation mean/max/attention/DeepSets/Set Transformer; SX-04-05 pretrained encoders vs fingerprints ("benchmark, don't assume"). SSOT §183.B (SSOT L13146–13160) lists 10 mandatory decision gates incl. learned vs FP2/Morgan, single vs multi-view, pooling vs learned aggregation, attention vs DeepSets, Set Transformer vs interaction graph, static vs process-conditioned, universal vs task-conditioned, frozen vs FT vs PEFT, presence vs concentration vs OAV, automatic vs expert/sensory validation.
- B08 / Part K (L388–410, L691–709): reproduce RecipeDB3 (DeBERTa ingredient macro-F1 0.9557; spaCy instruction micro 0.9258 / macro 0.8698), Goel 2024 spaCy-trf 95.90, TASTEset v1/v2 0.935/0.943 (L392–395) — all UNVERIFIED externally in this run; then hygiene re-eval; hybrid tagger gazetteer → DeBERTa/RoBERTa±CRF → kNN-NER → GLiNER2.5 → Jev/Claude verifier → calibration (L701). Weak instruction labels quoted: QUANTITY 0.638, PREPROCESS 0.50, DRYFRESH 0.83, TEMPERATURE 0.88 (L702). MP L699: "5.1% exact and 13.6% number-masked duplicates on RecipeDB3's random split. Re-verify before citing." (NER block is closed/frozen per ctx L30; do not reopen.)
- B09 (L421–423): whole-string vs factorized linking; Recall@K then selector (cross-encoder vs FoodSEM-style vs Jev vs Claude).
- B11 (L456–460): recency vs contextual vs packet-constrained resolver; structural-similarity features; long-distance refs; hidden-step precision + hallucination audit; direct-observation override.
- B12 (L466–470): shortcut baselines (food-identity-only, process-only) → physics features (thermal dose, Arrhenius exposure) → conditioning bake-off concat/FiLM/cross-attention **vs LightGBM/TabPFN** → multi-task with missing-label masks → calibrated abstention.
- B13 (L476–482): persistence/mean-delta/retrieval/tabular → kinetic fits with identifiability (profile likelihood) → evidence-aware completion vs GBDT on masked-cell and cold-pair → MNAR propensity-corrected eval → simulator pretraining ablation (ratio sweep, TSTR) → short rollout with trust horizon → conservative inverse design.
- B14 (L490–494): recipe-set encoder bake-off with frequency debiasing; similarity-type separation; identity/variant calibration (shared E13E-05); cuisine fingerprints; substitution benchmark. SSOT §193.8 requires R0–R3 and C0–C2 explicit baselines + frequency-only and recipe-size shortcut baselines (SSOT L15262–15280).
- B16 (L510–518): BM25 + dense + structured retrieval; evidence packets; calibrated confidence vector; answer/ask/abstain; feasibility filter; diagnosis/recovery; warnings; FlavorTwin static → process-conditioned. DEL-5 "B0–B5 ladder" (L1252; ladder not defined in L1–2460).
- B03 classical (L304): n_ij, N_s(R), N_s(C), 4 null cuisines + control lattice, monkey-cuisine MC, ΔN_s, Z, p_emp, χ_i, authenticity, Jaccard/Ochiai/IDF, fingerprints + Tanimoto.

---

## 3. Experiments / hypotheses / RQs (as listed in L1–2460)

- B00: SX-00-01 CI catches injected schema violation; SX-00-02 1-node and 10-node fan-out with resumable checkpoints (L271–272).
- B01: SX-01-01 index completeness vs App. 1 counts (L284). Seeded registry must include RQ16-01…30, E16-A…L, RQ13E-01…22, E13E-01…18, T0–T9, L13 phase experiments (§193), L14 do-first/MVP (§204), L15 tables/tracks (§216), sparsity M1–M6 (§226), merged-plan E0–E14, all SX (L281).
- B02: SX-02-01 API field audit (§42 questions per endpoint); SX-02-02 licence audit top-30 sources; SX-02-03 pilot pull 1k records/source with checksums (L296–298).
- B03: SX-03-01 Ahn 2011; SX-03-02 Jain–Rakhi–Bagler 2015; SX-03-03 degree-preserving null; SX-03-04 FlavorDB vs FlavorDB2; SX-03-05 Kinouchi copy–mutate (L305–309).
- B04: SX-04-01…05 (L322–326).
- B05: SX-05-01 verb coverage in 10k recipes (mapped/unmapped/ambiguous); SX-05-02 synonym-merge precision (human audit); SX-05-03 hidden-step rule precision vs gold "missing prerequisite"; SX-05-04 process-family hierarchy usefulness for cold-process generalisation (L343–346).
- B06: SX-06-01 mechanism-family evidence census; SX-06-02 retention-factor ingestion (USDA R6, Phenol-Explorer 3.0) w/ schema validation; SX-06-03 raw-vs-cooked volatile extraction on first curation cells (§144.3: rice, potato, broccoli, garlic, beef, wheat dough, cabbage); SX-06-04 kinetic parameter table (acrylamide/potato, Maillard glucose/glycine, vitamin C, anthocyanin, chlorophyll); SX-06-05 pH-effect table (anthocyanin colour, chlorophyll→pheophytin, Maillard rate, protein gelation); SX-06-06 enzymatic/cutting table (alliinase/LFS onion & garlic, myrosinase, LOX/HPL, PPO); SX-06-07 warning-rule derivation; SX-06-08 LLM literature-extraction accuracy vs human (L360–367).
- B07: SX-07-01 annotation pilot (20 recipes, two annotators); SX-07-02 multi vs single pass (RQ16-11); SX-07-03 validators' catch rate (RQ16-12); SX-07-04 duplicate leakage audit (RQ16-13); SX-07-05 Silver utility vs size (RQ16-09); SX-07-06 active learning vs random (RQ16-10) (L380–385).
- B08: SX-08-01…08 (L402–409) incl. Hinglish robustness (Archana's Kitchen original vs translated), position/format robustness, distillation.
- B09: SX-09-01…05 (L421–425).
- B10: SX-10-01 grammar exact match on gold catalogue; SX-10-02 invented-grams audit (must be 0); SX-10-03 portion-record selection (Jev/LLM/lexical); SX-10-04 coverage vs RecipeDB2's 43.90% converted pairs; SX-10-05 Indian household measures interval coverage; SX-10-06 instruction quantity allocation; SX-10-07 z_q downstream value (RQ16-23) (L438–444).
- B11: SX-11-01…05 (L456–460) (RQ16-14/15/24, E16-D).
- B12: SX-12-01…05 (L466–470). B13: SX-13-01…07 (L476–482). B14: SX-14-01…05 (L490–494).
- B15: RQ13E-01…22 via E13E-01…18 under G13E-01…15; phases E0→E5 (§278.7); do-first in §279.3 (L498–501). (SSOT actually lists Phases E0–E7: SSOT L45358–45417; MP says E0→E5.)
- B16: SX-16-01…12 map 1:1 to E16-E…L + warnings/deploy (L519–521); SX-16-11 warning precision/recall + over-warning fatigue; SX-16-12 latency/cost/availability. Note E16-E…L = 8 families, + 2 = 10, not 12 — the "1:1" mapping of 12 SX IDs is arithmetically inconsistent (UNRESOLVED; SSOT E16-E…L at SSOT L27400–27424).
- Part N (L759–780): HYP ladder L0 Idea → L1 Observed pattern (EDA, effect size) → L2 Tested (nulls/control lattice, pre-registered, multiple-comparison §278.3) → L3 Replicated (independent source/split/region; confound controls) → L4 Mechanistically supported (E1–E4 consistent, or "statistical only") → L5 Adopted (ablation shows value). Only L5 influences product; L2–L4 publishable as findings; demotion logged. Stats: effect sizes + bootstrap CIs over families; paired tests; Holm/BH; report nulls; analysis plan fixed before test split touched.
- Part Q1 (L1080–1111): SSOT §257L card A–Z (claim freeze … downstream update); A–I and K–U committed before running on held-out data. Q2: ≥3 seeds for neural runs; pinned data; `results/<EXP-ID>/<run-id>/`. Q3 bug loop; invalidated results marked INVALIDATED not deleted. Q4 reflexion.
- Research spawn bank: RS-00…RS-17 + RS-EDA (L842–1074, ≈190) + Z1–Z7 Q1–80 (L2191–2294). Most decision-relevant for this audit: RS-06-5 kinetic params (P0, L917); RS-06-6 retention factors (P0, L918); RS-06-7 raw-vs-cooked GC-MS census (P0, L919); RS-06-17 mixture pH (P0, L929); RS-06-20 kinetic model families (L932); RS-13-1 MNAR completion; RS-13-3 UDE/PINN; RS-13-4 TSTR; RS-13-6 profile-likelihood identifiability; RS-13-9 (P0) LLM literature-extraction accuracy in food science (FoodAtlas, extrusion study) (L1019); RS-12-8 (P0) small-data tabular baselines (L1008); RS-14-2 (P0) similarity definitions (L1024); RS-05-1 (P0) ontologies FoodOn/LanguaL/FoodEx2 crosswalks (L899); RS-09-1 (P0) food entity linking (L963); RS-10-1/3/4 (P0) units, count portions, densities (L975–978); Z1-1 time-series vs endpoint (L2197); Z1-3 wet/dry basis (L2199); Z1-4 retention conflating degradation/leaching/water loss (L2200); Z1-12 identifiable reaction networks (L2208); Z1-15 volatile loss vs degradation (L2211); Z1-19 analytical batch effects (L2215); Z1-20 high-frequency cells with zero evidence (L2216); Z3-40 % molecule links traceable to primary measurement (L2242); Z5-52 NER gain under source/template-disjoint (L2260); Z7-76 source-independent replication rate (L2290).

---

## 4. Gates, promotion and stop rules (exact)

### 4.1 Human-approval gates H1–H8 (Part C3, MP L131–142) — verbatim
- **H1 External communication** — emails to Prof. Bagler / TypeSafe / dataset owners; posting issues on others' repos.
- **H2 Licences and acquisition** — new scraping target, any dataset whose licence is unclear, storing raw third-party text.
- **H3 Compute and money** — jobs above `{{COMPUTE_BUDGET_THRESHOLD}}` node-hours, any paid API, cluster-wide jobs.
- **H4 Schema/ontology MAJOR change** — label split/merge, ID scheme change, provenance enum change.
- **H5 Gold data** — starting, changing or unsealing Deep Gold / Sealed test.
- **H6 Claims** — any "SOTA", "first", "beats X" or causal/chemical claim leaving the repo; anything about CoSyLab's pipeline.
- **H7 Repository** — push to main, release tags, making the repo public, adding collaborators.
- **H8 Scope** — adding or dropping a Level, Block or deliverable; promoting a stretch item; changing the course contract.
Additional explicit uses: H1 before professor email (L295, L1288, App. 2 L1363); H2 before first request to any source (L1184); H3 for jobs above threshold (L1170); H6 before "beats CoSyLab" (L410, L709); H7 repo creation (L1286); H8 semester-cut scope (L1294). Threshold placeholder `{{COMPUTE_BUDGET_THRESHOLD}}` is **unfilled** (L137, L1170) → H3 has no numeric trigger.

### 4.2 Block exit gates (exact)
- B00 (L273): reproducible "hello pipeline" end-to-end (download → validate → EDA stub → report), hashes recorded.
- B01 (L285): humans approve portfolio + **semester cut** (§279.8). SX-01-01 counts "must match".
- B02 (L299): source manifest approved, no unlicensed raw text stored.
- B03 (L310): each frozen statement reproducible from code; deviations documented, never forced.
- B04 (L327): §183.B / §183.4 Level-12 gates (SSOT L13146–13278; §183.4 has 12 checklist items incl. frozen leakage-audited split manifests, E0–E3 baselines on real data, z_m justified vs ECFP/descriptors on ≥2 leakage-safe splits, missing-view/concentration behaviour quantified, final L12 decision record).
- B05 (L347): **G16-VOCAB for processes; ≥ 95% of process mentions in the Gold seed map to an ID or an explicit UNMAPPED with the raw verb kept.**
- B06 (L368): **G14-1…G14-12 for the evidence spine; G15 data gates before any transition model claim.** (G14-1…12 at SSOT §202.16, L17074–17089: G14-1 versioned process-event schema + provenance/tier/missingness; G14-2 dataset card per-field coverage, source/study/platform distribution; G14-3 human-verified held-out test labels; G14-4 shortcut/null/tabular baselines; G14-5 ingredient×process pair-holdout; G14-6 source/study-disjoint where study IDs exist; G14-7 condition contribution vs label-only; G14-8 missingness robustness; G14-9 calibration/interval coverage/risk–coverage; G14-10 evidence-quality stratification; G14-11 multi-seed/clustered uncertainty; G14-12 final decision record.)
- B07 (L386): **§257P checklist fully ticked before scaling past 10k** (SSOT L42705–42743: 15 items incl. 100–500 difficult Gold seed cases, unit engine property tests, quantity lookup exact/interval/UNKNOWN, graph supports intermediate/split/merge/reserve/recombine, duplicate grouping before split assignment, Deep-Gold annotators independent of Silver, pilot cost + reannotation rate known, rollback strategy). Silver ladder 10k pilot → 25k → 60k → 100k only if gates pass (L377).
- B08 (L410): G16-SEM; H6 before "beats CoSyLab". G16-SEM (SSOT ~L27458): parsers meet declared Deep-Gold thresholds and source-disjoint performance reported.
- B09 (L426): G16-VOCAB; ACCEPT-band precision ≥ pre-registered budget (budget value not given).
- B10 (L445): G16-QTY (deterministic units correct; portion conversions have provenance; qualitative/unknown not fabricated; interval calibration where distributional — SSOT L27452–27455). SX-10-02 invented grams **must be 0** (L439); Part U Day 5–8 gate "0 invented grams" (L1291).
- B11 (L461): G16-GRAPH.
- B12 (L471): G14-*.
- B13 (L483): **G15-1…12 plus G15-H/HYB/I/INV/R/RXN.** (SSOT §215 table ~L22380–22396: G15-1 data audit; G15-2 D0–D6 reported on all eligible headline splits before D7+; G15-3 process signal on process-disjoint split with CI; G15-4 ≥1 focused D-C dataset supports identifiable kinetic fit with uncertainty; G15-5 kinetic/hybrid beats best non-kinetic tabular on held-out T/condition; G15-6 study-disjoint real calibration; G15-7 abstention on REAL calibration; G15-8 consistency diagnostics; G15-9 D7 beats D5/D6 on masked-real-cell + cold tests or rejected; G15-10 synthetic/imputed rows improve REAL-only study-disjoint performance in ratio sweep, none in final test/calibration; G15-11 trust horizon only where true intermediate states exist; G15-12 inverse design beyond nearest-evidence/random/grid inside safe support; G15-R reproducibility; G15-H every LLM-extracted test/calibration row human-verified; G15-I integration logs. G15-RXN (SSOT L22402–22410), G15-HYB (L22412–22414), G15-INV inverse ceiling ≤ forward credibility.)
- B14 (L495): §193.8 Level-13 gate (SSOT L15262–15280).
- B15 (L501): G13E-*; humans choose whether it becomes a paper (§279.8).
- B16 (L522): G16-CAL / CONFLICT / DEC / EVID / OOD / PROV / REC / TRANS / FT; §257P final-claims checklist. (G16-TRANS: no L15 fallback for a target/domain until relevant G15 gates pass; G16-FT: process/context complexity only if beats static on process-sensitive held-out — SSOT L27470–27490.)
- B17 (L527): every claim traceable to experiment ID, artifact, commit (+ X4: every claim has CLM-, L2010).

### 4.3 Data/eval rules acting as gates
- E1–E4 only in evaluation; E6–E7 priors/stress only (L595).
- No EVD row in Gold eval without source traceability (L1656).
- No averaging across incompatible platforms without harmonization experiment (L1687).
- Rerun affected experiments only after new ledger version frozen (L1829).
- Pretraining never includes test families (L728).
- Analysis plan fixed before test split touched (L780); §257L A–I, K–U committed before held-out runs (L1111).
- Only HYP L5 influences product (L771).
- Warnings: no warning without evidence; unsupported safety claims must be zero (L645, AA3 L2356).
- SSOT §249.2 stop rules (SSOT L27492ff; quoted by reference, not in MP L1–2460): stop complexity when Silver doesn't improve Gold, canonicalization errors dominate, conversions mostly unsupported, structured retrieval doesn't beat hybrid RAG, confidence uncalibrated under source shift, L15 adds coverage but increases unsupported claims, etc.

### 4.4 Course deliverable acceptance (Part T1, MP L1246–1252) — exact
- **DEL-1** Process-Effect Evidence Ledger + data card (B02, B06): "≥ 1,000 rows from public retention DBs + ≥ 40 hand-verified literature rows; 100% rows have source + tier + condition status + censoring flag; names normalized to RecipeDB/FlavorDB; data card + audit (Part M)". Repo: ≥1,000 E3 rows met (18,156 IDs); **0 E4 rows** → ≥40 hand-verified literature rows NOT met (repo-verified tier counter); name normalisation: sampled USDA row has `ingredient_id: null` → UNVERIFIED/likely unmet.
- **DEL-2** Sparsity-aware completion + cold-split benchmark (B13): density/MNAR profile; pair-holdout, ingredient-disjoint, study-disjoint splits; baselines vs MF/FM with side info; propensity-weighted eval; conformal intervals; study-level bootstrap CIs; negative results.
- **DEL-3** Event-sourced state-tracking engine (B08–B11): consumes parsed recipes; merge/split/reserve/recombine; observation override; **≥ 40 gold recipes + 30 scripted sessions**; state-field accuracy, replay consistency, merge/split F1.
- **DEL-4** Evidence-aware retrieval + calibrated abstention (B16): hybrid retrieval; condition compatibility; evidence classes; confidence vector; answer/ask/abstain; condition-compatible Recall@K, risk–coverage, unsupported-claim rate, ECE vs always-answer baseline.
- **DEL-5** End-to-end CulinaryState-RAG + benchmark + demo (B16, B17): relevance gate, feasibility filter, diagnosis/recovery; **~80 questions × 8 task types**; B0–B5 ladder; ablations; oracle tests; peer/chef review; 8-scenario demo.
("Verified as it is" = artifact path, version hash, tests, metrics with CIs, gate result, experiment IDs — L1277.) Repo has `reports/del2..del5/` (not inspected here; status UNVERIFIED).

### 4.5 Promotion ladders
Part N L0–L5 (above). SSOT §183.3 unified promotion rule referenced indirectly via B04 (not quoted in MP).

---

## 5. Data requirements and named sources (licence notes as stated)

- CoSyLab/Foodoscope: RecipeDB, RecipeDB2, FlavorDB/FlavorDB2, DietRx, SpiceRx, SustainableFoodDB, CulinaryDB, Foodoscope suite (L292, RS-02-1 L861); App. 2 email asks for API keys/bulk snapshot with step-level instructions, process/utensil labels, form/state, durations/temperatures; permission to reuse RecipeDB3 NER data (L1373–1379). DietRx/SpiceRx "context only; no health claims" (L1376). Repo: D-015 says CoSyLab use permitted by Prof. Bagler, licence ASSUMED/DERIVED_ONLY (ctx L21).
- RecipeDB/RecipeDB3: ≈268 processes per Bagler grammar, expect ≥300 PROC IDs (L330); SSOT L457: RecipeDB published description 268 cooking processes and 69 utensils. Repo PROC.jsonl 552 lines, TOOL 297.
- Public recipe corpora (RS-02-3 L863): RecipeNLG, Recipe1M+, Food.com, ReciFine, TASTEset, r-FG, INDoRI, Archana's Kitchen 6000+, Cookpad research data, RELISH, Open Recipe Archive. Licence: none asserted in MP — all "to audit". ctx: Food.com CC0 only uploader-declared; TASTEset unverified; BBC A1 RESTRICTED local-only.
- Composition/portion (RS-02-5 L865): USDA FDC Foundation / SR Legacy / FNDDS portions, IFCT 2017 India, FAO/INFOODS, CoFID, Frida.
- Molecules (RS-02-6 L866): PubChem, FooDB, FlavorDB2, ChEBI, Pyrfume, GoodScents, Leffingwell, Flavornet; taste: BitterSweet, SweetpredDB, UmamiPredict (RS-04-7 L889); DREAM (L891); FoodAtlas (Z3-31 L2233, RS-13-9 L1019).
- Process chemistry (RS-02-7 L867; SX-06-02 L361): USDA retention factors R6, Phenol-Explorer 3.0, EuroFIR, kinetic reviews. Repo EVD origins: USDA R6 7,018; Bognár 7,090; Phenol-Explorer 3,870 / 125 papers (ctx L31) — Bognár is not named in MP L1–2460.
- Ontologies: FoodOn, LanguaL, FoodEx2 (RS-05-1 L899; B09 crosswalks FlavorDB/FooDB/FDC/FoodOn L419); Open Food Facts for branded (RS-09-8 L970).
- Safety authorities: USDA FSIS, FSSAI (L615, RS-06-13 L925); EFSA, NIST units (L814).
- Historical (RS-15-1 L1035): RELISH, Open Recipe Archive, Dutch trends, Transylvania.
- Licence matrix categories: store raw / store derived / reference only (L294). R4 (L1174–1184): prefer APIs/bulk dumps; obey robots/terms; UA with contact; rate limits; no logins/paywalls/personal data; store raw only where licence permits else offsets/hashes/derived; record in datasets.csv before first request (H2). App. 2 promise: "not redistribute raw data" (L1381).
- Copyright for research briefs: quote ≤1 short sentence per source (L838).
- Scale targets: Deep Gold ~750–1,000 (first 100–500 hard seeds), Gold-Light ~3–5k, Silver 10k→25k→60k→100k (L374–377; consistent with SSOT L25593–25594); ≥100k evidence rows across tiers (L359, L586 — plan-only, not found in SSOT by grep); verbs coverage on 10k recipes (SX-05-01).

---

## 6. Dependencies (as encoded in MP)

- E3 critical path (MP L235–246): B00 → B01 → B02 → {B03, B04, B05→B06, B07→B08→B09→B10→B11}; B12 ← B04, B06, B11; B13 ← B06, B12; B14 ← B04, B09, B11; B15 ← B02, B03, B14 (parallel); B16 ← B06–B14; B17 ← all. Parallelism: B03, B04, B05/B06, B07/B08 parallel after B02 (L250); B15 never delays core unless made primary (L251; SSOT §279.5 L45564–45590).
- SSOT §279.5 critical path: (L12 evidence/classical baselines + L16 schema/Deep Gold/semantic+quantity) → 10k Silver pilot + evidence ledger + state graph → retrieval/confidence/transition fallback/decision.
- B07 gate depends on B10 (unit engine), B09 (vocab workflow), B11 (graph supports split/merge) via §257P items.
- B13 requires B12 (G14) and B06 (evidence) — i.e. **transition modelling depends on representation gates**, which is a heavier coupling than the 36-step spine (where Phase G 29–34 precedes Phase H 35).
- B16 transition fallback requires G15 passes (G16-TRANS).
- W7 compiler depends on EVD, RXN, COND, PROC, TOOL, SVAR, quantity ledger and event ledger simultaneously.
- W9 refresh couples application runtime (B16) to acquisition machinery (B02/B06) — runtime "evidence-on-demand" means Step 36 depends on Steps 06/09/13 tooling remaining operational.
- DEL-3 depends on B08–B11; DEL-1 on B02/B06; DEL-2 on B13; DEL-4/5 on B16/B17.
- Human dependencies: H5 for any Deep Gold; H2 for any new source; H6 for claims.

---

## 7. Risks / failure modes surfaced in L1–2460

1. Dense-tensor illusion (L8, L585, L1890): pretending 10k × 300+ × condition grids is fillable.
2. Tier inflation: E5–E7 leaking into evaluation (L595); MODEL_ESTIMATED/SIMULATED promoted (L78).
3. Retention conflation: degradation vs leaching vs concentration-by-water-loss (Z1-4 L2200); volatile loss vs degradation (Z1-15 L2211); wet vs dry basis (Z1-3 L2199).
4. Platform incomparability (W5 L1687; Z1-19 batch effects).
5. Non-independence: mirrors/reposts counted as independent (L1902); dedup by study (I4 step 7, L625). Current repo: 43,392 EVD lines `study_id_status: NOT_IDENTIFIABLE` → study-disjoint splits (G14-6, DEL-2) not possible for USDA/Bognár rows as stored.
6. Setpoint ≠ core temperature; "medium heat" numericised (L1504–1505).
7. Balanced-reaction fabrication (L1723).
8. Invented grams / fake density conversions (SX-10-02, J1–J3).
9. Duplicate leakage (L91–94; RQ16-13; Part K 5.1%/13.6% figures UNVERIFIED).
10. Gold anchoring by Silver predictions (L89; §257P item; Z5-58).
11. Frequency bias in embeddings (SX-04-04, SX-14-01, Z3-37).
12. Over-warning fatigue (SX-16-11); unsupported safety text.
13. Prompt injection from untrusted content (Y6 L2175–2187) — critical for Steps 09/13 LLM extraction.
14. Agent self-evaluation (Y3 L2144: "Do not let one agent both invent the hypothesis and serve as its final evaluator"); Evaluator role cannot edit training data (L2120).
15. Compute assumptions: ≈100-node cluster (Part R L1142–1172) — does not match reality (Mac CPU, RTX GPU, A100 via 13–90 KB/s VPN, shared Linux server; ctx L23–26).
16. Lab-in-the-loop safety (AB L2413–2438): no hazardous chemistry/microbiology/pressurized rigs.
17. Bug invalidation of past results (Q3 L1127) and schema/prompt bug in data batch → §257P rollback.
18. Ontology drift (SX-09-05, RS-09-6).
19. Hinglish/regional long-tail (SX-08-06, Z5-60).
20. Rank–frequency mis-fitting (Part M L741: Clauset–Shalizi–Newman, never straight line on log–log).

---

## 8. MAPPING TO THE 36-STEP SPINE (reconstruction from MP; the 36 cards themselves are missing)

Format: Step — MP sources — Requires (inputs / outputs / gates / baselines / metrics).

**01 Freeze project authority** — A3 (L48–61), D5 (L200–211), C3 (L131–142), L6 precedence of W–AF over A–V. Outputs: authority order; CR process (`registry/change_requests.md` — not present in repo; `registry/plan_authority_map_v1.csv` is the repo equivalent); H1–H8 definitions with a **filled** `{{COMPUTE_BUDGET_THRESHOLD}}`. Gate: humans approve. Note: MP rank 3 input `CulinaryState_Recipe_Compiler_FINAL_MERGED_PLAN.md` v1.2 (L54) — presence in repo UNVERIFIED.

**02 Audit implementation state** — D1 registries (L162–176), App. 1 inventory (L1338–1359), SX-01-01 (L284), B00 gate (L273). Requires: index counts match App. 1 (309 top-level sections, 45,697 lines, 14 G16 gates, etc.); inventory of which Part H/X ledgers exist. Repo-verified gaps: no `experiments.csv`, `gates.csv`, `hypotheses.csv`, `research_spawns.csv`, `datasets.csv`, `change_requests.md`; no `compute/`, `research/briefs/`, `.github/`, DVC. Existing substitutes: `ledgers/data/EXP.jsonl` (8 lines), `experiments/EXP-000001…7`, `ledgers/data/DATASET.jsonl` (5), `registry/data_source_acquisition_manifest.csv`.

**03 Freeze state semantics** — Law 9 (L84), H2.9 event/state ledger (L564–568), I2 (L598–607), W1 transition cell (L1431–1448), W3 SVAR (L1511–1571), W7 (L1727–1766), W8 (L1768–1791), ΔS profile (L351). Requires: SVAR families + per-variable fields incl. observable-in-session flag; entity-version semantics (LOT-/ENT-); trajectory enum PLANNED/OBSERVED_SESSION/PREDICTED; missingness mask M_t; trust-horizon concept. Gate: H4 for any SVAR/enum MAJOR change.

**04 Freeze evidence / provenance / similarity contracts** — provenance enum (L78), tiers E1–E7 (L587–595), W4 EVD (L1573–1656), W12 consensus labels (L1906–1913), W6 relation vocabulary (L1709–1720), B14 typed similarity (L487: structural/chemical, sensory, functional/culinary-role, cultural/co-occurrence, nutritional, process-conditioned — each with own metric, eval set, null model), Part N ladder, X4 CLM-. Requires: resolution of E1–E7 vs SSOT E1–E6; similarity registry (repo has `registry/ssot15_similarity_registry.csv`, not inspected). Gate: H4.

**05 Normalize EVD** — SX-06-02 (L361), W4 fields, I4 steps 5–7 (L623–625), DEL-1 (L1248). Inputs: USDA R6, Phenol-Explorer, Bognár imports. Outputs: EVD v-next with SVAR-, COND-, MEAS-, STUDY- links, censoring, basis. Metrics: % rows with source + tier + condition status + censoring flag = 100% (DEL-1); names normalized to RecipeDB/FlavorDB. Repo: ES-1.1 export PASS per ctx; ingredient_id null in sampled rows.

**06 Freeze source acquisition manifest** — B02 (L287–299), SX-02-01…03, X3 API- (L1970–1991), X5 SNAP- (L2012–2026), R4 (L1174–1184), H1 (email), H2. Gate: "source manifest approved, and no unlicensed raw text stored" (L299). Outputs: licence matrix store-raw/derived/reference-only; per-source allowed storage + redistribution.

**07 Condition & measurement normalization** — W2 COND- (L1450–1509), W5 MEAS- (L1658–1687), Part J unit map (L657–674; for culinary-side quantities), condition ledger H2.7 (L562). Requires: all W2 axes representable, measured/range/qualitative/unknown status, measurement location; MEAS comparability notes. Repo: 40-variable condition registry; COND imports mostly UNKNOWN.

**08 Scientific source lineage** (NOT authorised in this run) — W4 identity + evidence blocks (study_id, source independence group, conflict cluster, DOI/version, L1580–1645), W5 STUDY- (L1674–1685), W12 step 1 & 7 (L1896, L1902), I4 step 7 "deduplicate by study" (L625), X5 SNAP-. Required downstream by G14-6 and G15-6 (study-disjoint), DEL-2 study-disjoint split + study-level bootstrap. Gap: MP has no SOURCE → DOCUMENT → STUDY → EXPERIMENT → SAMPLE → MEASUREMENT → AGGREGATE hierarchy; database aggregates (USDA/Bognár) have no study identity (43,392 NOT_IDENTIFIABLE lines) — Step 08 must define a lineage/independence proxy (e.g. source family `USDA-RETN-R6`, already used as `independence_group`).

**09 Evidence extraction & verification machinery** — I4 steps 1–4 (L619–622: research spawns, acquire under licence, typed-schema LLM multi-pass + validators, human verification on sampled/priority set), SX-06-08 (L367), W9 per-source procedure (L1820–1829), Y2 roles 13 Evidence Verifier / 18 Evaluator, Y3, Y6 prompt-injection rule, RS-13-9 (P0). Metrics: LLM-extraction accuracy vs human (no threshold given in MP). Gate: G15-H (every LLM-extracted test/calibration row human-verified against cited span/table).

**10 20-row mechanism pilot** — No "20-row" pilot exists in MP L1–2460 (UNVERIFIED origin; repo refers to "STEP 10 / ES-1.3 pilot"). Closest MP content: SX-06-03…06 first curation cells (L362–365) and DEL-1 "≥ 40 hand-verified literature rows" (L1248); Part U Day 10–14 first curation cells (L1294). Requires: E1/E2/E4 rows with full W4 fields, source span locator, verification by Kush + Parv.

**11 Wave-1 verified mechanism evidence** — SX-06-03 (volatiles: rice, potato, broccoli, garlic, beef, wheat dough, cabbage), SX-06-04 (kinetics: acrylamide/potato, Maillard glucose/glycine, vitamin C, anthocyanin, chlorophyll), SX-06-05 (pH), SX-06-06 (enzymatic/cutting: alliinase/LFS, myrosinase, LOX/HPL, PPO), I3 worked examples (L609–615). Must close DEL-1's ≥40 verified rows. Tier E1/E2 → E4 after verification.

**12 Structured database evidence** — SX-06-02, RS-02-5/6/7, RS-06-6, X3/X5. Sources: USDA R6, Phenol-Explorer 3.0, EuroFIR, FDC (FDC raw/cooked pairs 867 = E6 candidates per repo tier map), FooDB/FlavorDB2/PubChem for molecule side. Tier E3. Must handle %TR vs %AR (repo tier map note), imputed values, censoring.

**13 Large literature discovery corpus** — W10 query generator (L1837–1854, must log tried queries), W9 refresh order, RS-06-7 raw-vs-cooked GC-MS census, Z1-1 time-series availability. Tier E5 until verified. Y6 untrusted-content rule mandatory.

**14 Coverage-driven evidence growth** — W11 scheduler + process condition templates (L1856–1890), I4 step 8–9 (EDA sparsity matrix, VOI selection §224), AA1 coverage-growth curve and heatmaps (L2302–2335), Z1-20 / Z7-73. Metric: coverage of priority cells; no weighting until empirically justified.

**15 Freeze DATA-EVIDENCE v1** — G14-1, G14-2 (dataset card per-field coverage, source/study/platform distribution), G15-1 data audit, G15-H, Part M EDA sections 1–13 (L733–755), AA1 (L2302–2335), DEL-1 acceptance, W12 conflict synthesis labels, "rerun only after ledger frozen" (L1829). Outputs: frozen EVD/COND/SVAR/MEAS/STUDY versions with hashes; split manifests (study-disjoint, pair-holdout, ingredient-disjoint).

**16 Instruction semantic schema** — X2 INST- (L1947–1968), H2.9 event fields, Law 9, Part K L700 layered schema with legacy adapters (RecipeDB 7 tags, RecipeDB3 12 instruction labels, TASTEset 9/15, r-FG; raw character offsets; nested/discontinuous spans), B05 process fields (L331–340), X1 TOOL-, J unit/endpoint descriptors (sugar-syrup string stages as endpoint, L671), Z2-22/23/24 (tool-encoding and endpoint-encoding verbs; composite processes). Gate: H4; §257P "schema v1 fields and missingness meanings documented".

**17 Instruction-level extraction** — B08 SX-08-05 instruction weak labels (QUANTITY 0.638, PREPROCESS 0.50, DRYFRESH 0.83, TEMPERATURE 0.88 — RecipeDB3, UNVERIFIED), Part K L702, B05 SX-05-01 verb coverage, B10 SX-10-06 instruction quantity allocation, RS-08-11. Baselines: grammar vs learned. Gate: G16-SEM (source-disjoint reported). NER/linker v1 frozen (ctx L30).

**18 Event-sourcing engine** — B11 (L447–461), W7 compiler, H2.9, §257P graph item, DEL-3 metrics (state-field accuracy, replay consistency, merge/split F1), AA6 state-graph EDA (L2382–2391). Outputs: event/state ledger (EVT- absent in repo), replay engine with CI invariants, prefix state packets, OMITTED_STEP_CANDIDATE never facts. Gate: G16-GRAPH.

**19 Gold state-trajectory pilot** — SX-07-01 (20 recipes, two annotators, L380), Part U Day 8–12 "20-recipe Gold pilot (two annotators, no LLM pre-fill)" (L1293), DEL-3 "≥ 40 gold recipes + 30 scripted sessions" (L1250), Deep Gold first 100–500 hard seeds (L374), H5 gate, AB lab-in-the-loop (optional trajectories, L2411–2460). Metrics: agreement (span F1, κ — Part M item 11 L752).

**20 Scale procedural semantic corpus** — B07 Silver ladder 10k→25k→60k→100k (L377), §257P gate (L386), SX-07-02…06 (RQ16-09…13), batch audit every 5–10k (L378), duplicate/lineage groups before splits (L379), Part M + AA4/AA5/AA6. Must be reconciled with 612,782-recipe base (ctx L29) — MP does not plan tiers above Silver (no "large weak corpus" tier, except L728 "large weak recipe corpora" for pretraining).

**21 Effect / mechanism ontology** — I2 mechanism family list (L601), W6 relation vocabulary (L1709–1720), B05 "mechanism families possibly triggered" (L339), RS-06-1/2, §144.1. Requires: mechanism family IDs linking PROC- ↔ RXN- ↔ SVAR-. No mechanism ID namespace in Part H (RXN- is reaction-level; no MECH- namespace) — gap.

**22 Event → effect signatures** — W11 process condition template (required/optional axes, typical observables, likely mechanism families, tool/medium dependencies, safety-critical fields, L1860–1867), W7 steps 1–5, I3 (cutting alliums ⇒ enzymatic chemistry; "chopping changes nothing chemically is false for alliums", L611), Law 7 (never infer chemistry from generic verb), SX-05-03 hidden steps.

**23 Mechanism applicability engine** — W4 applicability block (exact/near/analogous/generic, interpolation domain, extrapolation flags, matrix/process similarity rationale, condition distance, trust horizon; L1646–1653), W7 step 3 "compatibility hierarchy" (undefined), W9 triggers CONDITION_OUTSIDE_LOCAL_SUPPORT / LOCAL_EVIDENCE_BELOW_REQUIRED_TIER, Z1-6 matrix-specific pH effects prohibiting transfer. Requires condition axes from Step 07 (aw, O₂, pH trajectory, enzyme state via "additives/catalysts/enzymes", ripeness, geometry).

**24 Formula / model registry** — MP L1–2460 has **no mechanistic formula registry**. Partial: RXN- "rate law / kinetic parameters when identified" (L1700); SX-06-04 kinetic parameter table (L363); RS-06-20 model families first-order/Weibull/Arrhenius/WLF (L932); X6 MODEL- (ML-oriented, L2028–2047). Brief §21 fields (equation, state vars, assumptions, IC/BC, matrix scope, identifiability, solver…) must be designed elsewhere (check MP Parts AC–AF, other reader).

**25 Parameter-compatibility retrieval** — W4 applicability + condition distance; W12 stratification by matrix/cultivar/form/process/condition; Z1-18 dominant uncertainty variables; Z1-19 batch effects; SX-13-02 profile-likelihood identifiability. No explicit parameter registry (PARAM-) in Part H — gap.

**26 One focused deterministic simulator** — MP L1–2460 only defines tier E7 = simulator output (L594) and SAMPLE-/AB for validation trajectories; RS-06-18 reduced-order heat transfer (P2, L930); Z1-17 compartment models (L2213); SX-06-04 focused systems candidate list (acrylamide/potato, Maillard glucose/glycine, vitamin C, anthocyanin, chlorophyll) = natural candidate pool. No simulator V&V spec in this range.

**27 Validate simulator on real held-out evidence** — Gates available: G15-4 (identifiable kinetic fit with uncertainty), G15-5 (beats non-kinetic tabular on held-out condition), G15-6 study-disjoint calibration. E1–E4 only in evaluation (L595). AB bench data could supply trajectories (L2423–2436).

**28 Controlled E7 synthetic prior** — E7 tier (L594–595), SX-13-05 simulator pretraining ratio sweep + TSTR (L480), G15-10 (SSOT), simulated_state_changes_schema_v1.csv exists in repo (not inspected). Rule: never Gold, never final test/calibration; must carry simulator id/version/params/uncertainty (repo tier map).

**29 TRANSITION_BOOTSTRAP_V0** — SX-13-01 persistence/mean-delta/retrieval/tabular (L476), SX-12-01 shortcut baselines (L466), Part L transition row (L721). Must add D3 shrinkage per SSOT. Repo contract `reports/h_state/transition_bootstrap_v0_contract.md` (other reader).

**30 Strong tabular / sparsity bake-off** — SX-13-03 completion vs GBDT on masked-cell & cold-pair (L478), SX-13-04 MNAR propensity (L479), SX-12-03 vs LightGBM/TabPFN (L468), SX-12-04 multi-task masks, DEL-2 (L1249). Gates: G15-2, G15-3, G15-9, G14-5, G14-6, G14-8. Metrics: conformal intervals, study-level bootstrap CIs, propensity-weighted eval.

**31 Physics / condition features** — SX-12-02 thermal dose, Arrhenius exposure (L467), RS-12-2, Z1-11 microwave power → physics features, G14-7 condition contribution vs label-only. Needs core/surface T, time–T trajectory, heating rate from Step 07.

**32 Focused kinetics** — SX-13-02 kinetic fits with profile-likelihood identifiability (L477), SX-06-04 kinetic param table, RS-06-5, RS-13-6, Z1-5 non-first-order matrices, Z1-12 identifiable networks. Gate: G15-4.

**33 Mechanistic vs ML vs hybrid** — Part L "kinetic + residual hybrids" (L721), RS-13-3 UDE/PINN, G15-HYB, G15-RXN, G15-5. Law 12 (keep simpler on tie).

**34 Short rollout** — SX-13-06 (L481), G15-11 (trust horizon only where true intermediates exist), W7 OOD flag + trust horizon (L1759, L1653), I2 session dynamics (L607), RS-13-7. Data: time-series/intermediate-state evidence (Z1-1) and DEL-3 scripted sessions.

**35 Representation ladder** — B04 (L312–327), B12 (L463–471), B14 (L485–495), Part L rows 1–4, W8 multi-view z (L1778–1791), AA7 representation EDA (L2393–2405), SSOT §183.B/§183.4/§193.8 gates, H2.4/H2.5 molecule & ingredient–molecule ledgers (presence vs concentration vs detection limit). Metrics: scaffold splits; frequency-bias audit; anisotropy/hubness.

**36 Evidence compiler → selective CulinaryState-RAG → FlavorTwin** — B16 (L503–522), W7 compiler, W9 refresh, I5 warnings, X4 CLM-, DEL-4 (condition-compatible Recall@K, risk–coverage, unsupported-claim rate, ECE vs always-answer), DEL-5 (~80 questions × 8 task types, B0–B5, oracle tests, chef review, 8-scenario demo), G16-CAL/CONFLICT/DEC/EVID/OOD/PROV/REC/TRANS/FT, §257P final-claims checklist, Z6 Q61–70, RS-16-*. FlavorTwin at §246 boundary (L35); G16-FT.

Cross-cutting (no single step): B03 classical replication and B15 L13E have no home in the 36-step spine titles (B03 → partly Step 35 / B14 nulls; B15 → parallel lane). Part M/AA EDA, Part N hypothesis ladder, Part Q card discipline, Part S authorship apply to all steps.

---

## 9. Contradictions, stale items, underspecified parts, open questions

**Contradictions / divergences**
1. Evidence tiers: MP E1–E7 (L587–594) vs SSOT §201.7 E1–E6 (SSOT L16651–16661); E6 meaning differs (MP "mechanism-family rule/heuristic (MODEL_ESTIMATED)" vs SSOT "heuristic / qualitative / weak inference"); E7 simulator tier is MP-only. Repo adopted MP's E7. Needs SSOT CR or explicit note (Step 04/28).
2. ID collisions: "E7" also = SSOT L12 encoder ladder E7 "fine-tuned multi-view ingredient encoder" (SSOT L8497–8501) and L13E Phase E7 (SSOT L45417); MP App. 3 also uses E0–E14 for merged-plan experiments (L1411). "Step 28 E7 synthetic prior" is ambiguous unless namespaced (e.g. TIER-E7).
3. H1 `FAM-` via MinHash ≥ 0.8 (L538) vs SSOT §264.8/E13E-05 (no universal threshold before calibration) — already logged as IMPLEMENTATION_DETAIL, SSOT wins (`reports/step07i/max_plan_consensus.md` L15, L41).
4. B06 gate cites G14-1…12 "for the evidence spine" (L368) but G14 are L14 process-conditioned-model gates (G14-3…G14-11 concern held-out labels, baselines, splits, calibration) — category error; the evidence spine's own gate should be G15-1/G15-H + DEL-1 + G14-1/G14-2.
5. B15 "Phases E0 → E5 (§278.7)" (L500) vs SSOT Phases E0–E7 (SSOT L45358–45417). Stale.
6. SX-16-01…12 "map 1:1 to E16-E…L plus the warnings and deploy experiments" (L519): E16-E…L = 8 families + 2 = 10 ≠ 12.
7. Part L transition baseline (L721) omits SSOT D3 (shrinkage) and D7 (low-rank completion); SSOT forbids D10 skipping D0–D7 (SSOT ~L18598).
8. B12 z formula (L464) lacks the mask M_t that W8 (L1773) adds — W8 governs per L6.
9. "≥100k evidence-bearing rows" (L359, L586) — target not found in SSOT; current 18,156 distinct EVD IDs all E3.
10. Typed similarity: MP B14 has 6 types merging structural+chemical (L487); brief §24 demands 9 (adds COMPOSITIONAL, PROCEDURAL, splits STRUCTURAL/CHEMICAL).
11. 36-step spine sequencing vs MP E3 DAG: MP runs recipe factory (B07–B11) in parallel with evidence (B05/B06) after B02; spine serialises Phase C (evidence acquisition) before Phase D (procedure/state). SSOT §279.5 also runs L12 evidence and L16 schema/Gold in parallel. Spine also places representation (35) after transition (29–34), whereas MP B13 depends on B12 (L242) and B12 on B04.

**Stale**
12. Part R "≈100 servers + CPU" (L1142–1172), `{{CLUSTER_TYPE}}`, `{{N_NODES≈100}}`, SX-00-02 10-node fan-out, C1 "MinHash dedup over 1M+ recipes" sharding — compute reality differs (ctx L23–26).
13. Part U first-14-days schedule (L1281–1294) — historical; project is at S134.
14. D1 repository memory files and registries (L162–176) mostly not created in that form (repo-verified absent: experiments.csv, gates.csv, hypotheses.csv, research_spawns.csv, datasets.csv, change_requests.md, `logs/sessions/` naming UNVERIFIED; `logs/` dir exists). B00 outputs CI/MLflow/DVC/CODEOWNERS: no `.github/`, no DVC found.
15. S2 ownership split (L1209–1215) vs actual authorship (EVD/COND `created_by: "Kush+Claude"`) — balance UNVERIFIED.
16. App. 2 email drafts — whether sent is a WORKLOG question (D-015 implies permission obtained).
17. Jev / TypeSafe dependence (L401, L423, L723, App. A2.2) — status UNVERIFIED; likely deprecated.
18. Placeholders `{{PARV_GITHUB_ID}}`, `{{COMPUTE_BUDGET_THRESHOLD}}`, `{{REPO_NAME}}` unfilled (L66, L137, L1194).

**Underspecified**
19. H3 has no numeric threshold; with no cluster, H3 should be re-expressed (e.g. GPU-hours on A100, LLM tokens/batch).
20. Gate thresholds not declared: G16-VOCAB "declared threshold", B09 "pre-registered budget", G16-SEM "declared Deep-Gold thresholds", G16-GRAPH "declared acceptance criteria", SX-06-08 extraction-accuracy bar, warning precision/recall bar, ECE bar. Only hard numerics in L1–2460: B05 ≥95% (but UNMAPPED counts as pass → nearly tautological), SX-10-02 = 0 invented grams, DEL-1 ≥1,000 + ≥40, DEL-3 ≥40 + 30, DEL-5 ~80 × 8, Deep Gold ~750–1,000, Gold-Light ~3–5k, Silver ladder, ≥3 seeds.
21. W7 "compatibility hierarchy" (L1741) never defined; W4 "condition distance" metric undefined; "trust horizon" operational definition only via G15-11.
22. No formula/model registry, no parameter registry, no simulator V&V contract, no mechanism ID namespace in L1–2460 (Steps 21, 24–27).
23. No literature evidence hierarchy below STUDY (experiment/sample/measurement/aggregate); `design` field partly covers aggregate vs controlled. SAMPLE- is bench-only.
24. No Gold sizing rationale for evidence verification (how many E4 rows needed for G15-H calibration sets); "sampled/priority set" (L622) unspecified.
25. No tiering of the 612k corpus beyond Silver (no weak-corpus / Gold-Light selection protocol for state trajectories).
26. DEL-5 B0–B5 ladder undefined in this range.
27. W11 priority function explicitly unweighted (L1886) — fine, but no tie-break/queue policy.

**Open questions needing external research**
- Evidence/provenance models for measurement hierarchies (e.g. W3C PROV-O; ISA-Tab investigation/study/assay; FoodOn/ENVO; EuroFIR food-composition data model) — to fill gap 23.
- Retention-factor semantics: USDA %TR vs %AR and EuroFIR/Bognár definitions (Z1-4) — affects Step 05/12 and law "presence ≠ abundance".
- Formula-registry standards (SBML/CellML/BioModels-style model cards) fit for food kinetics — Step 24.
- Simulator choice and V&V framework (ASME V&V 40-style credibility; first-order/Weibull vitamin C, chlorophyll, acrylamide kinetics availability) — Steps 26–27.
- Annotation-reliability targets for event/state Gold (κ / span F1 thresholds) — Steps 19/20.
- LLM literature extraction accuracy in food science (RS-13-9: FoodAtlas) — Step 09 gate threshold.
- MNAR-aware completion / conformal under MNAR (RS-13-1/2) — Step 30.
- Validity of the 5.1% / 13.6% RecipeDB3 duplicate figures (L699) and SOTA numbers (L392–394) — must not be cited unverified.

---

## 10. LOOK-AHEAD: fields earlier steps must capture

Derived from what W4/W5/W7/W8/W11/W12, G14/G15/G16 and DEL-1…5 later consume.

**Step 03 (state semantics)** — SVAR `observable_in_session` vs `scientific_only` (W3 L1571; needed by Step 34 rollout & Step 36 diagnosis); allowed value type incl. `trajectory` (needed by 32/34); entity version id + parent version + trajectory class PLANNED/OBSERVED_SESSION/PREDICTED (H2.9); explicit mask semantics distinguishing ND / LOD / true zero / unmeasured / unknown (SSOT §209 change list L24854ff item 13; MP law 2); trust-horizon field type; ΔS profile component tags (C, P^phys, Y^sens, N, V, A) so models can be per-component.

**Step 04 (contracts)** — provenance enum incl. SIMULATED/IMPUTED with non-promotion rule enforced in code; tier namespace disambiguated from E0–E14/E13E; applicability enum exact/near/analogous/generic + interpolation domain + extrapolation flags (Step 23/25); conflict_cluster_id and W12 consensus label (Step 36 conflicting-evidence packet); typed similarity registry with metric/eval set/null per type (Step 35); CLM- claim linkage (Step 36/B17).

**Step 05 (EVD normalize)** — separate before/after value + unit + uncertainty + LOD/LOQ + method per side (W4 L1613–1625) even when DB gives only derived RF (store "before/after NOT_REPORTED"); measurement basis wet/dry/fresh/per-serving (Z1-3); retention type %TR vs %AR (repo tier note); imputed-from-similar-food flag (repo note: "many values imputed from similar foods" → must map to provenance IMPUTED, else they could enter evaluation); ingredient_id linkage to ING- (currently null) for DEL-1 "names normalized to RecipeDB/FlavorDB" and Step 35 joins; food part/form/prior processing/initial state; process_id (null in sampled row) and process family.

**Step 06 (manifest)** — per source: allowed storage, allowed redistribution, licence snapshot, schema hash, version/ETag, fallback (X3/X5); whether the source can yield study identity (source_claim_capability_matrix exists in repo); whether it contains time series vs endpoints (Z1-1) — needed to route sources to Steps 32/34.

**Step 07 (conditions & measurement)** — all W2 axes, esp. those consumed by Steps 23/31/32: core vs surface vs medium vs setpoint temperature distinguished; time–temperature trajectory and heating rate; pH initial/final/trajectory; aw and moisture/dry matter; oxygen/headspace; salt/sugar/fat level; additives/enzymes (enzyme state for applicability); pressure; heat-transfer mode; microwave power; geometry/thickness/particle size; SA:V; batch size; container fill; tool/material ID; ripeness/storage age; organism/starter; measurement location + method per condition; qualitative-only status for "medium heat". MEAS-: platform family, LOD/LOQ, calibration, matrix basis, comparability limitations (Step 15 harmonisation, Step 30 platform-stratified evaluation).

**Step 08 (lineage)** — study_id with status (PRESENT / NOT_IDENTIFIABLE / PROXY), source independence group, mirror/repost detection, publication id, lab/author group, document id, table/figure locator, replicate count, sample size, design class (controlled/observational/aggregate/review), aggregate-of-what (n studies) for DB rows — required by G14-6, G15-6, DEL-2 study-disjoint split and study-level bootstrap, W12 step 1/7.

**Step 09 (extraction machinery)** — extraction_version, extractor model/prompt hash, source span/page locator, verifier identity + timestamp, verification status, PROMPT_INJECTION_CANDIDATE flag (Y6), query log from W10 (reproducible failure-to-find), confidence. Needed for G15-H and for training/eval eligibility filters.

**Steps 10–14 (acquisition)** — for every row: cultivar/variety, food part, form, cut/geometry, prior processing, initial state; mechanism family tag (Step 21/22); RXN link or W6 relation label (FORMED…UNKNOWN_TRANSFORMATION); time points (≥3 points needed for kinetic identifiability, G15-4/SX-13-02 — threshold UNVERIFIED); temperature levels per study (≥2–3 for Arrhenius/condition-OOD G15-5); separation of leaching vs degradation vs water-loss concentration (Z1-4) and volatile loss vs degradation (Z1-15); sensory panel method if sensory target; safety-authority source id for WARN-; coverage-priority score inputs (recipe frequency, process frequency — requires join to recipe corpus counts from Step 07H-R/07I-R) for W11.

**Step 15 (freeze)** — frozen split manifests: study-disjoint, ingredient-disjoint, ingredient×process pair-holdout, process-disjoint, condition-OOD (temperature hold-out), platform strata (G14-5/6, G15-3/5, DEL-2); dataset card with per-field coverage + source/study/platform distribution (G14-2); MNAR propensity covariates (popularity, cuisine, source — Part M item 6, Z7-77).

**Steps 16–20 (procedure/state)** — INST- fields separate from event graph (raw span, language/script, normalized verb, process candidates, arguments, quantity mentions, time/temp mentions, endpoint phrase, implicit subject/object, coreference pointers, negation/optionality, sequence relation, confidence); tool/utensil + material per event (W2 tool ID, X1); medium; endpoint descriptors (e.g. string stages, "until golden") as endpoints not quantities; qualitative heat level; explicit time/temp with raw strings; entity version transitions (merge/split/reserve/discard/recombine); quantity allocation fraction/basis/parent (H2.8) with Q-level; OMITTED_STEP_CANDIDATE kept separate; recipe family/dish-family id from 07I (for leakage-safe Gold/Silver splits, §257P "duplicate grouping before split"); locale/source (unit locale inference J3); language (Hinglish slices). These feed Step 22 (event→effect signature needs process_id + condition + matrix state per event), Step 29 (transition cells from recipe events need S_before), and Step 36 (current state/history in evidence packet, feasibility filter needs tool and time).
