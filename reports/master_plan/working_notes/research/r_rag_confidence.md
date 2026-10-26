# r_rag_confidence — CulinaryState-RAG: retrieval layers, evidence packets, confidence & abstention

Researcher role: r_rag_confidence · spine steps 36 (primary), 09 and 15 (evidence features) · date 2026-10-22
Mode: PLAN-RESEARCH only. Repo read-only. No project data sent to any external service (searches were literature-only).
The 36-step plan (step cards) is MISSING from this machine. Step content below is RECONSTRUCTED from SSOT v15,
Master Plan v4.0 and repo artifacts, and is labelled so. Nothing here is quoted from the missing plan.

---------------------------------------------------------------------------------------------------------------
## 0. Internal baseline: what the SSOT already says and what the repo already built

### 0.1 SSOT v15 text that already covers this area (read in full)
- §241.1 (L26322–26334): 8-stage retrieval R1 structured filters → R2 BM25 → R3 dense → R4 graph/evidence expansion →
  R5 cross-encoder rerank → R6 state/process/condition/target compatibility → R7 dedup+lineage+conflict → R8 packet.
- §241.2 (L26335): fuse candidate pools; RRF as baseline because retriever scores are not calibrated probabilities.
- §241.3 (L26339–26348): compatibility vector m_j = [food, state, process, T, t, pH, target, matrix, measurement, source];
  keep categorical match types (EXACT, SAME_SPECIES, SAME_FOOD_GROUP, SAME_PROCESS_FAMILY, GENERIC_MECHANISM) before
  any learned scalar.
- §241.4 (L26349): scientific hard negatives (same food/wrong process; same process/wrong t/T; same target/related food;
  raw vs processed; wrong analytical endpoint).
- §241.5 (L26353–26367): 8-step contradiction workflow before a conflict cluster may be declared.
- §241.6 (L26368): packet compiled by reasoning role, not retriever rank. §241.7: table/figure evidence, DIGITIZED label.
- §242.1 (L26379): confidence VECTOR q = [retrieval, entity, quantity, process, condition, target, source, measurement,
  extraction, agreement, state, model, OOD]; "do not start with confidence = 0.83".
- §242.2 (L26387): separate calibrated probabilities per task (support, link, quantity, citation, transition, feasibility,
  answer-vs-abstain). §242.3: calibration labels must be independent of the model being calibrated.
- §242.4: Platt/isotonic/small trees. §242.5: Brier, ECE/reliability, error-detection AUROC/AUPRC, risk–coverage.
- §242.6 (L26411): sufficiency modes DIRECT / NEAR-PARTIAL / MODEL-INTERPOLATION / BROAD-QUALITATIVE / IRRELEVANT / NONE / CONFLICTING.
- §242.7: output precision ≤ evidence precision. §242.8 (L26434): cascade DIRECT → interpolation → calibrated L15 model →
  broad qualitative → abstain; imputed/simulated values may not masquerade as direct evidence.
- §243.1 (L26449): decision modes {ANSWER, COMPARE, ASK, DIAGNOSE, RECOVER, RECOMMEND, ABSTAIN}; §243.8 (L26481): ASK only
  with positive value of information. §245.10: NeverAsk vs AskEverything vs VOIAsk benchmark.
- §245.6–245.8 (L26639–26654): condition-compatible Recall@K; citation precision/recall, UCR; sufficiency/abstention mode F1 and risk–coverage.
- §245.12 (L26604ff): baseline ladder B0 LLM-only … B7 calibrated recommend/ask/abstain; §245.13 mandatory ablations; §245.14 oracle cascades.
- §247.3 RQ16-03 (L26825): compatibility reranker vs generic cross-encoder, human-labelled pairs, food/process/source-cold splits.
- §247.6 RQ16-06 (L26885): sufficiency policy vs always-answer, risk–coverage + UCR, "main risk: false abstention".
- §257A.13 (L28285): DISALLOWED_CLAIMS. §257B.7 (L28807): C7 compatibility layer contract (UNKNOWN states, emit features for calibration, oracle-upstream eval).
- §257M (L42160ff): every packet must carry query ID, current-state version, packet version, evidence class, known unknowns,
  claim/citation map, model version if used, confidence features, response mode; forbidden: silent class upgrade.
- §49.x v4.2 (L2982): evidence status (unsupported / physically_possible / evidence_supported) is NOT model confidence; report separately.
  §49.x v8 (L3010–3044): confidence is multi-source; "do not multiply arbitrary confidence values"; confidence ledger fields.
- §202.10 (L16999) and §212.26 (L20192): conformal intervals; coverage assumptions/shift must be stated; one-step coverage ≠ rollout coverage.
- §203.8 (L17330): evidence-ledger key for citation-level retrieval (ingredient/state, process family+leaf, condition bucket, target family, tier, source/study).

=> The SSOT design is already close to current best practice. The gaps are (a) operational definitions of each rung's entry
condition, (b) where ASK sits in the cascade (§242.8 has no ASK; §243.1 has ASK as a mode; brief §28 inserts ASK before ABSTAIN),
(c) how CONFLICT relates to the rungs (§242.6 lists it as a mode; Master Plan v4.0 L3228 lists it inside the cascade),
(d) the calibration-data budget, which is far too small for the guarantees the SSOT implies.

### 0.2 What the repo already implements (course DEL-4/DEL-5; status = PROTOTYPE, silver-evaluated only)
- `src/culinarystate/retrieval/retriever.py`: BM25 ∪ structured candidate pool (ING/parents/graph relations/target); rank =
  0.35·bm25_norm + 0.65·compatibility, ×0.3 on hard mismatch (HAND-SET weights); dedup by (cell, independence_group);
  packet class DIRECT / INTERPOLATED / QUALITATIVE / CONFLICT / UNSUPPORTED. `EvidencePacket` fields: question, query,
  evidence_class, direct, near, conflicts, condition_differences, known_unknowns, disallowed_claims, citation_map.
  MISSING vs §257M: query ID, state version, packet version, model version, response mode, confidence features, history,
  goal, constraints, mechanistic background, model estimates, feasible actions (some live in decision/ modules).
- `retrieval/compatibility.py`: 9-axis vector (matrix, state, process, time, temperature, medium, target, basis, tier), values
  MATCH/NEAR/MISMATCH/UNKNOWN, UNKNOWN never a mismatch; categorical match types EXACT/PARENT/CHILD/SIBLING/ANCESTOR/GROUP_ROW/FOOD_GROUP; scalar only for ranking.
- Conflict detection = INCREASE vs DECREASE direction among pooled hits only (does NOT implement the §241.5 harmonisation workflow).
- `decision/confidence.py`: §242.1 vector as ordinal features (None = unknown, never 0); NOT calibrated; `retrieval` dimension = the hand-weighted rank score.
- `decision/policy.py`: rule policy (relevance gate → intent → critical-slot ASK → feasibility → sufficiency → precision cap).
- `scoring/calibration.py`: Brier, ECE (equal-width bins), risk–coverage, AURC, error-detection AUROC, UCR. No calibrator fitted.
- Empirical results (silver, templated, dev only; NOT benchmark results):
  - `reports/del4/retrieval_silver_v1.md` (600 templated queries, 17,978 rows): MRR@10 BM25 0.597; best dense e5-large-v2 0.700;
    RRF BM25+e5-large 0.762; structured (oracle slots) 0.856; structured+e5-large vs structured Δ +0.005 [−0.006,+0.015] (n.s.);
    generic cross-encoders bge-reranker-large Δ −0.056 [−0.091,−0.017], base Δ −0.091 vs the RRF list they rerank (NEGATIVE result kept).
  - `reports/del4/rq1603_pilot_v1.md` (EXP-000006, 800 templated queries): within-query AUROC on HARD negatives: BM25 0.918,
    CE-large 0.924, structured 0.995, structured with PREDICTED slots 0.975; structured − CE on HARD +0.071 [+0.055,+0.090]. Silver labels; cannot promote.
  - `reports/del4/graph_expansion_v1_analysis.md`: vertical food-hierarchy expansion promoted (coverage 7.1%→20.3%, MAE Δ −0.026 [−0.035,−0.017]
    vs global median); OFF siblings worse (+0.036) → not used; unlinked-food rows → BROAD_QUALITATIVE, never NEAR numbers.
  - `reports/del5/generator_c16_v1.md`, `ladder_v2_qwen32b.md` (20 AI-authored dev questions): deterministic template B5T and
    LLM+post-hoc enforcement B5F+E reach 0 unsupported numeric claims; prompting alone ignores the precision cap. Template promoted.
- Benchmark / calibration labels: `benchmark/benchmark_registry_template.csv` (template only); D-008 task types PROPOSED, not approved;
  `benchmark/h_state/questions_to_write.csv` 53 rows all UNWRITTEN; `s114_snapshot_freeze.json`: 20 Gold recipes, 8 with a supported cut,
  max 14 recipe–evidence pairs. Master Plan v4.0 L3166–3169: benchmark tiers min 104 / target 320 / stretch 440. No human-labelled
  query–evidence pairs exist (RQ16-03 needs them).
- Evidence plane facts that constrain confidence features (`reports/es1/es1_1_audit.md`, recount of latest-ACTIVE EVD by this agent):
  17,978 ACTIVE rows, all tier E3; verification UNVERIFIED 14,108 / AI_PRECHECKED 3,870 / human-verified 0; design DATABASE_AGGREGATE
  14,108 / UNKNOWN 3,870; study_id NOT_IDENTIFIABLE 14,108; 127 independence groups but BOGNAR-2002 (7,090) + USDA-RETN-R6 (7,018) = 78% of rows;
  USDA rows carry SOURCE_SIDE_IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE; LOD/LOQ null in all rows; pH and moisture UNKNOWN in all rows;
  temperature UNKNOWN 11,963; duration UNKNOWN 14,895.

---------------------------------------------------------------------------------------------------------------
## 1. Questions

Q1 Which retrieval layers (BM25, dense bi-encoder, late interaction, cross-encoder, structured/slot, graph) are useful for a
   structured scientific-evidence corpus of ~10^4–10^5 typed rows, and when?
Q2 Do structured/graph RAG methods (GraphRAG 2024, KG-RAG surveys) fit evidence retrieval, or only parts of it?
Q3 What does scientific claim verification (SciFact, MultiVerS) contribute (Step 09 extraction verification vs Step 36 runtime)?
Q4 How should conflicting evidence be represented (knowledge-conflict surveys 2024; conflicting-evidence RAG 2025)?
Q5 Is "evidence sufficiency" a separately estimable quantity, and does using it improve abstention (sufficient context 2024–2025)?
Q6 What does selective prediction / abstention theory and LLM-abstention evaluation give us (risk–coverage, AURC, abstention F1)?
Q7 Can conformal prediction give guarantees for RAG outputs here; under which assumptions; with how much calibration data?
Q8 How to calibrate confidence with tiny independent label sets (Platt vs isotonic, ECE estimation bias, LLM self-confidence)?
Q9 How to evaluate citation faithfulness (ALCE, AIS, FActScore) and what the project's UCR adds.
Q10 Is GRADE a usable template for separate, non-scalar confidence domains?
Q11 Which packet fields are needed beyond brief §27, and what must earlier steps capture so that Step 36 can compute them?

---------------------------------------------------------------------------------------------------------------
## 2. Findings per question (sources; confidence)

### Q1 Retrieval layers — confidence HIGH (literature) / MEDIUM (project-specific, silver only)
- BM25 is a robust zero-shot baseline; dense models often generalise worse out of domain; re-ranking and late interaction
  give the best average zero-shot results but cost more compute (Thakur et al., BEIR, NeurIPS 2021 D&B [VERIFIED abstract]).
  BEIR includes NFCorpus (nutrition-facts queries → PubMed docs; Boteva et al., ECIR 2016 [search-verified, abstract via search only]) and SciFact, the closest domains.
- Dense bi-encoders beat BM25 in-domain with training data (DPR, Karpukhin et al., EMNLP 2020: +9–19 pts top-20 [VERIFIED abstract]);
  hard negatives drawn from the corpus fix the train/test negative mismatch (ANCE, Xiong et al., arXiv 2020; ICLR 2021 per memory [VERIFIED abstract, venue UNVERIFIED]).
- Late interaction (ColBERT SIGIR 2020; ColBERTv2 NAACL 2022 [both VERIFIED abstracts]) gives near-cross-encoder quality with precomputed
  doc vectors; value is at large corpus scale. Cross-encoder reranking (monoBERT, Nogueira & Cho 2019 [VERIFIED]) is topical-relevance trained (MS MARCO).
- RRF (Cormack, Clarke & Büttcher, SIGIR 2009, pp. 758–759, k=60 [VERIFIED via search + publisher listing; ACM page 403]) fuses ranks
  without pretending scores are comparable — SSOT §241.2 already chose it.
- PROJECT EVIDENCE (silver, templated): structured slot retrieval dominates (MRR 0.856 oracle slots); dense adds nothing on top of
  structured (+0.005 n.s.); generic cross-encoders HURT (−0.056/−0.091) because relevance here is cell identity (matrix×process×target),
  not topicality; structured beats CE on hard negatives even with predicted slots (+0.051 HARD AUROC). These match the mechanism the
  literature predicts: MS-MARCO rerankers have never seen "same food, wrong process" negatives.
- Consequence: for a typed evidence ledger the primary retriever is STRUCTURED (slot → key lookup + hierarchy expansion), with
  BM25 ∪ dense (RRF) as recall fallback for free text, unlinked rows (ingredient_id UNKNOWN 6,409 / 17,978) and rare lexical terms.
  Late interaction is unjustified at ~10^4–10^5 rows (an exhaustive compatibility scorer over the structured pool is cheap).
- Caveat (MEDIUM): all project numbers are silver with templated questions and oracle/near-oracle slot parsing (parser slot accuracy
  0.945–0.994 on templates). Real user questions will degrade slot parsing; this is exactly where the BM25/dense fallback earns its place.

### Q2 Structured / graph RAG — confidence HIGH
- GraphRAG (Edge et al., arXiv 2404.16130, 2024; v2 2025 [VERIFIED]) builds an LLM-extracted entity graph and pre-computed community
  summaries to answer GLOBAL sensemaking questions; it beats vector RAG on comprehensiveness/diversity for corpus-level questions.
  It is not designed for local, citation-level factual lookup, and its index is LLM-generated text.
- Graph RAG survey (Peng et al., arXiv 2408.08921, 2024, "ongoing work" [VERIFIED]) frames G-RAG as graph indexing → graph-guided retrieval → graph-enhanced generation.
- Consequence: REJECT GraphRAG community summaries as an evidence source (they would put model-written text in the evidence plane:
  violates "model memory ≠ evidence memory"; not citable to a measurement). ACCEPT curated graphs as retrieval STRUCTURE only:
  (i) food/ingredient hierarchy expansion (already promoted, vertical relations only), (ii) process hierarchy (SAME_FAMILY),
  (iii) source-lineage graph for dedup/independence (Step 08), (iv) mechanism/applicability graph (Steps 21–23) feeding MECHANISTIC BACKGROUND,
  never numeric DIRECT evidence. A corpus-level "what is known about X" overview (GraphRAG's use case) is a possible later analytic view, not Step 36 core.

### Q3 Scientific claim verification — confidence HIGH
- SciFact (Wadden et al., EMNLP 2020 [VERIFIED]): claim → abstracts → SUPPORTS/REFUTES + rationale sentences; domain adaptation matters.
  (NOT-ENOUGH-INFO claims exist in the released data per dataset docs — UNVERIFIED in this session; abstract names only SUPPORTS/REFUTES.)
- MultiVerS (Wadden et al., Findings NAACL 2022 [VERIFIED]): label + rationale from full-document encoding; weak supervision from
  document-level labels; strong zero/few-shot domain adaptation.
- Consequence: the natural home is STEP 09 (evidence extraction & verification machinery) and STEP 13 (literature discovery), not the
  Step 36 runtime over structured rows: each literature-extracted EVD row should carry a verifier label {SUPPORTS, REFUTES, NEI} for
  "this row's value/direction is stated by the cited span", plus the rationale locator. At runtime, the claim checker (repo
  generation/claims.py) verifies generated claims against packet rows — that is AIS-style attribution (Q9), not SciFact.
  SciFact/MultiVerS-style verifiers become runtime components only if Step 36 serves free-text literature passages (Step 13 corpus).

### Q4 Knowledge conflict — confidence HIGH (taxonomy) / MEDIUM (methods)
- Xu et al., "Knowledge Conflicts for LLMs: A Survey", EMNLP 2024, pp. 8541–8565 [VERIFIED]: context–memory, inter-context, intra-memory conflicts.
- Wang, Prasad, Stengel-Eskin & Bansal, "RAG with Conflicting Evidence" (RAMDocs / MADAM-RAG), arXiv 2504.13079, 2025 [search-verified; venue UNVERIFIED]:
  ambiguity, misinformation and noise co-occur; best systems still weak, especially with imbalanced support.
- Consequence: in CulinaryState the dominant conflict type is INTER-CONTEXT between evidence rows, and most apparent conflicts are
  not real (different basis, cultivar, process leaf, condition, platform, lineage duplicate). SSOT §241.5's harmonise-first workflow is
  the right design and is stricter than the LLM literature; the repo's direction-only detector should be replaced by it.
  Context–memory conflict (LLM parametric belief vs packet) is controlled by the template/enforcer design (B5T/B5F+E), which already
  forbids uncited numbers. Debate-style multi-agent conflict resolution (MADAM-RAG) is REJECTED for the evidence plane:
  conflicts are reported, not adjudicated by LLM vote (SSOT §257M.5 "do not majority-vote blindly").

### Q5 Evidence sufficiency — confidence HIGH (concept) / MEDIUM (transfer)
- Joren et al., "Sufficient Context", ICLR 2025 [VERIFIED arXiv + ICLR proceedings listing]: sufficiency of retrieved context can be
  classified separately from answer correctness; strong LLMs answer wrongly instead of abstaining when context is insufficient;
  combining a sufficiency signal with model confidence for selective generation raises accuracy among answered items by ~2–10%.
- Corrective RAG (Yan et al., arXiv 2401.15884, 2024 [VERIFIED; peer-review venue not listed]) and Self-RAG (Asai et al., arXiv 2310.11511;
  ICLR 2024 per memory [VERIFIED abstract, venue UNVERIFIED]): a retrieval-quality evaluator triggers different actions.
- Consequence: SUFFICIENCY is a first-class, separately labelled target (SSOT §242.6 already enumerates the modes). For structured rows,
  sufficiency is mostly computable from the compatibility vector (is there a row whose matrix/process/target/basis match and whose
  conditions bracket the query?) — rule-derivable, then validated against human sufficiency labels. A learned sufficiency autorater
  (Joren-style) is a BASELINE for free-text questions, not the primary mechanism.

### Q6 Selective prediction / abstention — confidence HIGH
- El-Yaniv & Wiener, JMLR 11:1605–1641, 2010 [VERIFIED]: risk–coverage trade-off for classification with reject option.
- Geifman & El-Yaniv, "Selective Classification for DNNs", arXiv 1705.08500, 2017 (NeurIPS 2017 per memory) [VERIFIED abstract]:
  choose a rejection threshold that guarantees a user-specified selective risk with high probability (binomial bound on calibration set).
- Geifman, Uziel & El-Yaniv, ICLR 2019 [VERIFIED, §3 of paper]: AURC = area under empirical RC curve; E-AURC = AURC − AURC of the
  in-hindsight optimal confidence ordering (removes dependence on base accuracy).
- Kamath, Jia & Liang, ACL 2020 [VERIFIED]: under domain shift, softmax confidence is overconfident on OOD questions; a SEPARATE
  calibrator trained on features (incl. some OOD data) gives better coverage at fixed accuracy (56% vs 48% at 80% accuracy).
- Wen et al., "Know Your Limits: A Survey of Abstention in LLMs", TACL (arXiv 2407.18418, v3 2025) [VERIFIED]: query / model / human-values
  perspectives; abstention metrics. Feng et al., ACL 2024 (Outstanding Paper) [VERIFIED]: calibration/prompting baselines often fail to
  abstain; reports "abstain accuracy". Kirichenko et al., AbstentionBench, arXiv 2506.09038, 2025 [VERIFIED; venue not listed]: abstention
  unsolved for frontier LLMs, reasoning fine-tuning degrades it ~24%; scaling helps little.
- Consequence: (a) the abstain decision must NOT be delegated to the generator LLM's self-assessment (Feng 2024, AbstentionBench, Joren 2025
  all show LLMs over-answer); the repo's rule policy + template generator is the right shape. (b) Use a small feature-based calibrator
  per decision (Kamath 2020) over the confidence profile. (c) Report RC curves, AURC and E-AURC, plus selective risk at fixed coverage with
  binomial upper bounds.

### Q7 Conformal prediction for LLM/RAG — confidence HIGH (theory) / LOW-MEDIUM (applicability at our n)
- Angelopoulos & Bates, gentle introduction, arXiv 2107.07511 (FnT ML 2023 per memory) [VERIFIED abstract]: distribution-free, finite-sample
  coverage under exchangeability; extensions incl. shift and abstaining models.
- Conformalized quantile regression (Romano, Patterson & Candès, arXiv 1905.03222; NeurIPS 2019 per memory) [VERIFIED abstract]: adaptive-width
  intervals — the right wrapper for MODEL-rung numeric estimates (retention factors, log fold change).
- Weighted conformal under covariate shift (Tibshirani, Barber, Candès & Ramdas, arXiv 1904.06019; NeurIPS 2019 per memory) [VERIFIED abstract]:
  needs a known/estimable likelihood ratio — NOT available for food-cold or study-cold shift; so coverage under those shifts must be
  measured empirically, not claimed.
- Conformal risk control (Angelopoulos et al., ICLR 2024 [VERIFIED]): controls expected monotone loss (e.g. unsupported-claim rate) — fits
  "choose the back-off level so UCR ≤ α".
- Conformal factuality (Mohri & Hashimoto, ICML 2024, PMLR 235:36029–36047 [VERIFIED]): back-off to less specific claims until a correctness
  guarantee holds — directly mirrors §242.7 "output precision ≤ evidence precision" and the cascade's numeric→interval→qualitative back-off.
- TRAQ (Li, Park, Lee & Bastani, NAACL 2024 [search-verified]): conformal sets over retrieval + answer for RAG QA.
  C-RAG (Kang et al., ICML 2024 [VERIFIED]): certified conformal generation-risk bounds for RAG, incl. some shift settings.
- Consequence: conformal is the right formalism for (i) MODEL-rung intervals (CQR, Steps 30–33) and (ii) choosing cascade back-off
  thresholds (risk control). BUT guarantees hold only for exchangeable calibration/test data and are marginal, not per-stratum;
  rollout coverage ≠ one-step coverage (SSOT §212.26). With the label budget in §6, report conformal coverage as an EMPIRICAL
  property per split; do not market guarantees for cold/shifted splits.

### Q8 Calibration with small independent label sets — confidence HIGH
- Guo et al., ICML 2017 [VERIFIED]: modern nets miscalibrated; temperature/Platt scaling a simple strong post-hoc fix.
- scikit-learn official docs (calibration module) [VERIFIED]: isotonic "more prone to overfitting, especially on small datasets";
  isotonic matches or beats sigmoid only with "enough data (greater than ~1000 samples)"; sigmoid most effective for small samples;
  lower Brier does not by itself mean better calibration. Underlying paper: Niculescu-Mizil & Caruana, ICML 2005 [UNVERIFIED body; listing seen].
- Kumar, Liang & Ma, NeurIPS 2019 [VERIFIED]: plug-in binned ECE is a biased estimator, binning is sample-inefficient; use debiased estimators / scaling-binning.
- Kadavath et al., arXiv 2207.05221, 2022 [VERIFIED]: LLM P(True)/P(IK) calibration is task-format dependent; P(IK) calibration on new tasks weak.
- Consequence: per-decision calibrators must be logistic/Platt (1–6 features) on ≤ a few hundred labels; isotonic forbidden below ~1000;
  report ECE with equal-mass bins + debiased estimate + Brier + reliability plot + bootstrap CI; the repo's equal-width ECE (scoring/calibration.py)
  should gain an equal-mass/debiased variant. LLM verbal confidence is a BASELINE only.

### Q9 Citation faithfulness — confidence HIGH
- ALCE (Gao, Yen, Yu & Chen, EMNLP 2023 [VERIFIED]): automatic citation-quality metrics (citation recall: is each statement supported by
  its cited set; citation precision: is each citation needed/relevant — defined in the paper body, UNVERIFIED in this session beyond abstract),
  correlate with human judgement; even best systems lack full citation support ~50% of the time on ELI5.
- AIS (Rashkin et al., arXiv 2112.12870; Computational Linguistics 49(4) 2023 per memory [VERIFIED arXiv abstract; journal page 403]): human
  attribution protocol "attributable to identified sources" with two-stage annotation.
- FActScore (Min et al., EMNLP 2023 [VERIFIED]): atomic-fact decomposition; automated estimator <2% error vs human.
- Consequence: keep SSOT UCR (§245.7) as headline; add ALCE-style citation recall/precision computed per atomic claim against the packet
  (deterministic for numeric claims, NLI/human for qualitative), and an AIS-style human audit on a fixed sample. The project's numeric
  claims can be checked exactly (value + cited row id), which is stronger than NLI-based ALCE; qualitative/direction claims need NLI/human.

### Q10 GRADE as template — confidence HIGH (template) / MEDIUM (fit to food-process evidence)
- GRADE (Guyatt et al., BMJ 336:924–926, 2008 [VERIFIED via Crossref]; Balshem et al., J Clin Epidemiol 64(4):401–406, 2011 [VERIFIED via Crossref];
  GRADE Handbook §5 [VERIFIED]): certainty is rated PER OUTCOME; rate down for risk of bias, inconsistency, indirectness, imprecision,
  publication bias; rate up for large effect, dose–response, plausible confounding; four levels high/moderate/low/very low.
- Consequence: GRADE's separation of domains is exactly the "no scalar" structure the brief demands, and "per outcome" maps to "per
  (food×process×target) cell". Its RCT-centric starting levels do NOT transfer (our rows are database aggregates and lab studies);
  use the DOMAINS, not GRADE's start-high/start-low arithmetic. Food-specific additions needed: measurement basis, censoring,
  source-side imputation, lineage duplication (database re-publishing the same primary data → false replication).

### Q11 Packet fields beyond brief §27 — see §3.3 (derived from SSOT §257M, Q4–Q10 and repo gaps). Confidence HIGH.

---------------------------------------------------------------------------------------------------------------
## 3. Architecture recommendation

### 3.1 Retrieval layers (Step 36; order = SSOT §241.1, with decisions)
| Layer | Keep? | When it is useful | Evidence |
|---|---|---|---|
| L1 slot parse → structured key lookup (ING/parents, PROC/family, target/SVAR canonical, basis) | PRIMARY | every process-effect / state query where slots parse | silver MRR 0.856 oracle; hard-neg AUROC 0.975 predicted slots |
| L2 hierarchy expansion (vertical food relations; process SAME_FAMILY) | KEEP, vertical only | cell has no exact row (coverage 7.1%→20.3%) | graph_expansion_v1: CHILD/ANCESTOR help, SIBLING hurts |
| L3 BM25 | KEEP as recall fallback + baseline | free text, unlinked rows, rare tokens (cultivar, compound names), slot-parse failure | BEIR "robust baseline"; silver 0.597 |
| L4 dense (e5-large-v2 currently) fused by RRF | KEEP as fallback, NOT blended into structured ranking | paraphrase / free-text queries; predicted-slot failures | RRF +0.165 over BM25; +0.005 n.s. over structured |
| L5 generic cross-encoder | DROP (negative result retained) | — | −0.056/−0.091 MRR; topicality ≠ cell compatibility |
| L5' compatibility classifier (RQ16-03): structured vector + categorical match types (+ optional text CE features), trained on SCIENTIFIC HARD NEGATIVES | CANDIDATE; promote only if it beats structured-with-predicted-slots on HUMAN-labelled pairs, food/process/source-cold | ranking within the compatible pool; producing P(support) for confidence | SSOT §247.3; S2p already 0.975, so headroom is small → small model |
| L6 condition-compatible filter (hard only on axes both query and row specify; UNKNOWN neutral but flagged; censoring-aware intervals; basis-aware) | KEEP, extend | always, after candidate generation | SSOT §241.3; D-013 censoring |
| L7 lineage dedup + independence + §241.5 conflict harmonisation | KEEP, REPLACE direction-only detector | always | SSOT §241.5; Xu 2024 |
| Late interaction (ColBERTv2) | DEFER | only if Step 13 builds a ≥10^6-passage full-text discovery index | BEIR cost/benefit; corpus too small at runtime |
| GraphRAG community summaries | REJECT for evidence plane | (possible later analytic overview only) | Edge 2024 targets global sensemaking; LLM-written index |
| LLM debate conflict resolution (MADAM-RAG) | REJECT | — | conflicts are reported, not voted |

Hand-set rank weights (0.35/0.65, ×0.3) are acceptable as a ranking heuristic but must never feed confidence; the confidence
`retrieval` dimension should become the calibrated P(support) from L5' (or remain a raw feature, explicitly not a probability).

Scientific hard negatives (extend SSOT §241.4 with data-driven types observed in this ledger):
same food/wrong process leaf · same process/other t or T bucket · same cell different BASIS (fresh vs dry weight, per raw vs per cooked) ·
reported retention factor (possibly yield-corrected, "apparent") vs concentration ratio (ES-1.1 conflict C4) · same analyte under a duplicate/
equivalent SVAR id · censored GT_CAP row vs measured · source-side-imputed (USDA) vs measured · raw vs processed initial state ·
related food (sibling) with the asked target · lineage duplicate of the same primary data in two databases (looks like replication) ·
wrong analytical endpoint (total vs specific compound) · group row ("vegetables, such as …"). Each negative type becomes a stratum in
RQ16-03 and in the RET benchmark; report per-type AUROC, not only pooled.

### 3.2 Non-scalar confidence: "certainty profile" per (query × outcome cell) — GRADE domains + retrieval/model/OOD domains
Each domain = ordinal level {HIGH, MODERATE, LOW, VERY_LOW, UNKNOWN} + raw features; UNKNOWN is never coerced; domains are never multiplied.

| Domain | Analogue | Features (raw) | Source step |
|---|---|---|---|
| D1 source/design quality | GRADE risk of bias | tier, design_strength, provenance_class, verification_status (UNVERIFIED/AI_PRECHECKED/HUMAN), source-side-imputation flag, DIGITIZED flag | 08, 09, 15 |
| D2 extraction correctness | — | P(row correct) from Step-09 audit stratum; verifier label SUPPORTS/REFUTES/NEI + rationale locator | 09 |
| D3 indirectness / condition compatibility | GRADE indirectness | 10-axis vector (§241.3) with categorical match types + numeric distances (ΔT, Δt log-ratio, basis match, state match); bracketing flag | 07, 15, 36 |
| D4 inconsistency / conflict | GRADE inconsistency | post-harmonisation conflict-cluster status {NONE, EXPLAINED_BY_CONDITION, GENUINE, UNRESOLVED}; dispersion of log-retention across independence groups (only if ≥3 groups) | 15, 36 |
| D5 imprecision | GRADE imprecision | replicate n, SD/SE/range, censoring kind/limit, LOD/LOQ status, rounding precision of source value; model interval width | 09, 12, 15 |
| D6 independence / source concentration | GRADE publication bias (adapted) | # independence groups, # studies, # lineage-collapsed duplicates, share of support from a single database, review-vs-primary | 08, 15 |
| D7 retrieval relevance | — | calibrated P(support | query,row) (L5'), rank, which layer produced it | 36 |
| D8 parse / link / state | — | NER/linker calibrated confidence (S128 frozen), quantity grounding status, state-reconstruction confidence | NER block, 17–20 |
| D9 model uncertainty | — | conformal/CQR interval at stated level, ensemble spread, model version, validation split passed | 30–33 |
| D10 applicability / OOD | — | distance to nearest training/evidence cell, in-domain flag from validated domain (Step 23/27), mechanism applicability status | 23, 27, 30 |
| (separate) evidence status | SSOT §49.x frozen | unsupported / physically_possible / evidence_supported — reported beside, never merged | 15, 23 |

Per-decision calibrated probabilities (SSOT §242.2) are small logistic models over a FEW of these features, one per decision:
P(direct answer correct), P(interval covers truth) (conformal instead), P(claim supported), P(abstain is right). They set thresholds;
the profile is what the user and evaluator see.

### 3.3 Cascade DIRECT → INTERPOLATE → MODEL → QUALITATIVE → ASK → ABSTAIN (operational entry conditions)
The cascade is evaluated top-down; the FIRST rung whose entry predicate holds AND whose calibrated selective threshold is met wins.
CONFLICT is NOT a rung: it is the D4 status and, when GENUINE/UNRESOLVED among comparable rows, forces response mode REPORT_CONFLICT at
the highest rung where comparable evidence exists (reconciles SSOT §242.6 [CONFLICTING mode] with Master Plan L3228 [CONFLICT in cascade]).

| Rung | Entry predicate (all required) | Output precision cap | Disallowed |
|---|---|---|---|
| DIRECT | ≥1 non-conflicted row with matrix EXACT, process EXACT/STEP, target canonical MATCH, basis compatible; condition axes MATCH or UNKNOWN (UNKNOWN listed in KNOWN UNKNOWNS); D2 not REFUTES | value/range as reported, with conditions and independence count; never more decimals than source | universalising beyond reported conditions |
| INTERPOLATE | same cell; query condition lies BETWEEN ≥2 measured conditions on a continuous axis, preferably same study/independence group; monotonicity not contradicted | interval spanning the bracketing values (no curve fit unless Step 24 registry model is validated) | point value; extrapolation outside bracket |
| MODEL | Step 30–33 model passed its held-out gate; query in validated domain (D10 in-domain); conformal/CQR interval available at stated level; evidence label "model estimate" | interval + model flag + coverage statement with split | "studies show"; using model value as evidence |
| QUALITATIVE | broad/near evidence (vertical relatives, process family, unlinked-food rows) consistent in direction, or mechanism APPLICABLE (Step 23) | direction / ordinal only | any number for the asked condition |
| ASK | a missing or ambiguous slot whose candidate values would change the winning rung or the answer (computed by re-running the cascade over candidate slot values: VOI>0, SSOT §243.8); question cost acceptable | one targeted question with options | asking when all slot values give the same answer (NeverAsk/AskAll/VOIAsk test §245.10) |
| ABSTAIN | none of the above; or GENUINE conflict that cannot be reported informatively; or OOD with no qualitative support; or safety/out-of-scope | state the known unknowns and what evidence would be needed | any factual process-effect claim |

ASK placement: ASK is evaluated BEFORE rungs that would be degraded by the missing slot, not literally after QUALITATIVE; the brief's
linear order is kept as a precedence list for the fallback path, and the report must state ASK can pre-empt (as the repo policy already does
for CRITICAL_SLOT_MISSING). Precision rule = SSOT §242.7 / Mohri & Hashimoto back-off.

Threshold setting: per rung, choose the threshold on the calibrated per-decision probability so that the empirical selective risk's
upper Clopper–Pearson bound ≤ α_rung on the CALIBRATION split (Geifman & El-Yaniv 2017 style), or via conformal risk control with UCR as loss.
Guarantees claimed only for the exchangeable (random) split; cold splits reported empirically.

### 3.4 Evidence packet — fields to add beyond brief §27 (and beyond the repo dataclass)
Header (SSOT §257M mandatory): packet_id, query_id, packet_schema_version, current_state_version/hash, evidence-ledger snapshot hash
(e.g. ES-1.1 export hash), retriever/compatibility/model versions, response_mode, evidence_class, sufficiency_mode + machine-readable reasons.
Per evidence item: row id + source id + locator/rationale span; independence_group + lineage-collapsed duplicates; compatibility vector with
categorical match types and numeric condition distances; certainty-profile domains D1–D6; censoring/basis/imputation flags; value as reported +
unit + precision.
Packet-level: CERTAINTY PROFILE (D1–D10) per outcome cell · EVIDENCE STATUS (frozen 3-value) · CONFLICT CLUSTERS with harmonisation trace (which
§241.5 checks explained the disagreement) · REJECTED/EXCLUDED CANDIDATES with reason (hard mismatch, lineage duplicate, basis) — audit trail ·
INDEPENDENCE SUMMARY · MODEL ESTIMATE block (estimate, interval, coverage level, calibration split id, training-support summary, OOD distance) ·
APPLICABILITY (mechanism applicability status from Step 23, validated domain from Step 27) · ASSUMPTIONS/CONVERSIONS applied (unit, basis, alias
mappings, SVAR equivalences used) · ANSWERABILITY: missing slots + VOI estimate + candidate clarification question · OUTPUT PRECISION CAP ·
CLAIM LEDGER (claim_id → evidence ids → support type → allowed precision; filled after generation, used for UCR/citation metrics) ·
SAFETY/WARNING items kept separate from evidence (allergen/food-safety authority tables) · LICENCE/REDISTRIBUTION flag per cited source
(e.g. RESTRICTED local-only sources must not be quoted verbatim in a shared answer) · "WHAT WOULD CHANGE THIS ANSWER" (discriminating observation).
Ordering: by reasoning role (SSOT §241.6); put the decisive items first and last in the LLM context (Liu et al., "Lost in the Middle", TACL 2024
[VERIFIED: arXiv comments say accepted TACL]) — or, as promoted in the repo, verbalise deterministically (B5T) and let the LLM only rephrase under enforcement.

### 3.5 Rejected alternatives (with reasons)
- Single scalar confidence (e.g. weighted sum, or product of domain scores): SSOT §242.1, §49 forbid; hides which domain fails; not calibratable per decision.
- LLM self-reported / verbal confidence as the abstention signal: over-answers on insufficient context (Joren 2025), fails to abstain (Feng 2024), unsolved (AbstentionBench 2025). Keep as baseline B-LLMconf.
- Generic cross-encoder reranking: project negative result; mechanism understood.
- Pure dense / vector RAG as primary: dominated by structured retrieval on this corpus; kept as fallback.
- GraphRAG summaries / LLM-built KG as evidence: model text in evidence plane.
- Isotonic calibration and deep calibrators: overfit below ~1000 labels.
- Claiming conformal guarantees under food/study-cold shift: likelihood ratio unavailable (Tibshirani 2019); report empirical coverage only.
- Fully GRADE-scored overall certainty (start-high/low arithmetic): RCT-specific; we adopt domains, not arithmetic.

---------------------------------------------------------------------------------------------------------------
## 4. What each affected spine step must change/add (reconstructed step content; step cards missing)

### STEP 36 — Evidence compiler → selective CulinaryState-RAG → later FlavorTwin (status: PROTOTYPE exists from DEL-4/DEL-5; not gated)
- Inputs: DATA-EVIDENCE v1 (Step 15) with certainty-profile fields; COND (07); lineage/independence (08); verifier labels (09); state/episode
  memory (17–20); mechanism applicability (23); formula registry + validated domains (24, 27); transition models + conformal intervals (30–33);
  NER/linker frozen (S128).
- Outputs: packet schema v2 (§3.4) as JSON Schema in registry/schemas; certainty-profile spec; cascade policy spec with rung predicates;
  per-decision calibrators + calibration report; claim ledger; RET/EVID/CONF/DEC benchmark results; ablation table.
- Sub-steps (proposed, inside Step 36): 36a packet schema v2 + certainty profile (no learning); 36b §241.5 conflict harmoniser replacing
  direction-only detector; 36c human-labelled query–evidence pairs (RQ16-03) + compatibility classifier vs S2p; 36d sufficiency/must-abstain
  benchmark authoring (D-008 approval first); 36e calibrators + thresholds on calibration split; 36f locked evaluation of ladder B0–B7; 36g FlavorTwin boundary (separate).
- Baselines: B0 LLM-only; always-answer RAG (RQ16-06 control); BM25-only; RRF BM25+dense; structured (current); scalar-threshold abstention on the
  current hand-weighted retrieval score; LLM verbal confidence; Joren-style sufficiency autorater (free-text only); rule cascade without calibration.
- Metrics: Recall@K, MRR, nDCG + condition-compatible Recall@K (§245.6) per hard-negative type; support-classification AUROC/F1; mode macro-F1
  over {DIRECT, INTERPOLATE, MODEL, QUALITATIVE, ASK, ABSTAIN, REPORT_CONFLICT} + confusion matrix with an asymmetric cost matrix (over-claim cost >
  under-claim); abstention precision/recall/F1 vs gold must-abstain; selective risk at fixed coverage (e.g. 50/70/90%) with Clopper–Pearson bounds;
  RC curve, AURC, E-AURC; Brier, ECE (equal-mass + debiased) with bootstrap CI, reliability plots; interval coverage + width per split for
  INTERPOLATE/MODEL; UCR (§245.7); ALCE-style citation recall/precision per atomic claim; AIS human audit sample; precision-cap violations; silent
  class-upgrade count (must be 0); ASK: NeverAsk/AskAll/VOIAsk decision quality and #questions; paraphrase/unit invariance (§245.15).
- Gates (proposed, PROPOSED_ONLY until approved): G36-RET: structured+fallback ≥ best simpler rung on human questions, predicted slots, with CI;
  G36-CONF: calibrated cascade AURC < scalar-threshold baseline AURC at matched coverage (paired bootstrap CI excludes 0) AND UCR ≤ α AND 0 silent
  upgrades; G36-ABST: abstention F1 and over-claim rate on must-abstain items beat always-answer without coverage loss beyond a pre-registered
  bound (RQ16-06 "false abstention" risk). Fail actions: keep the simpler rung (SSOT §245.13 / Master Plan AI8 "B5 must earn itself"), report negative result.
- Splits: random (for guarantee claims), food-cold, process-cold, source/study-disjoint (needs Step 08), support-regime held-out (RQ16-06).
- Compute: CPU sufficient for everything except dense embedding refresh and optional LLM rephrase (GPU helpful, not required; deterministic template
  path needs no GPU). A100 unnecessary.
- Human: query–evidence pair labelling and must-abstain benchmark are the bottleneck (see §6).

### STEP 09 — Evidence extraction & verification machinery (reconstructed)
- Add a VERIFIER output per extracted row: {SUPPORTS, REFUTES, NEI} for "the cited span states this value/direction/condition", plus rationale
  locator (table cell/row/column header, sentence span) — SciFact/MultiVerS task shape; plus DIGITIZED flag (§241.7).
- Add a Step-09 audit design that yields P(row correct) per extraction stratum (source type × field), with human double labels — this becomes D2.
- Record per row: replicate n, dispersion (SD/SE/range), censoring kind/limit, LOD/LOQ status, source rounding/precision, measurement basis, analytical
  platform/method id, review-vs-primary flag, imputation flag. Keep UNKNOWN explicit.
- Baselines: rules/regex table extraction; LLM extraction; MultiVerS-style verifier vs NLI baseline. Metric: field-level P/R/F1, verifier label F1, calibration of P(row correct).

### STEP 15 — Freeze DATA-EVIDENCE v1 (reconstructed)
- Freeze must include the certainty-profile source fields (D1–D6) per row, the conflict-cluster table (after §241.5 harmonisation, with trace), the
  lineage-collapsed independence groups, canonical SVAR mapping with equivalence status, and the evidence-ledger snapshot hash cited by packets.
- Freeze the RET/EVID label sets (query–evidence pairs, hard-negative types) and the split assignment (study-disjoint needs Step 08 lineage).
- Gate addition: every row has D1, D3 raw fields, D5 fields present-or-UNKNOWN with reason; zero rows where imputed/simulated values carry a measured status.

---------------------------------------------------------------------------------------------------------------
## 5. Look-ahead requirements for earlier steps (so Step 36 can compute the profile)
- STEP 07 (conditions): condition vectors must keep raw text + parsed interval + censoring kind (D-013) + unit + per-axis UNKNOWN reason; buckets for
  T, t, medium, pH, aw, moisture; basis. Currently pH and moisture are UNKNOWN in 100% of rows, temperature 67%, duration 83% → many queries can
  never reach DIRECT on condition axes; the packet must say so (KNOWN UNKNOWNS), and Steps 10–14 acquisition should prioritise rows with conditions.
- STEP 08 (lineage): needed for D6 (independence) and study-disjoint calibration splits. Today 14,108 rows have study_id NOT_IDENTIFIABLE and two
  databases are 78% of rows — independence counts are near-degenerate; lineage must detect databases re-publishing the same primary data.
- STEP 09: verifier labels + P(row correct) strata (D2); replicate/dispersion/LOD fields (D5).
- STEPS 10–14 (acquisition): collect rows that BRACKET conditions within the same study (INTERPOLATE needs ≥2 conditions per cell from one study);
  record design and platform; tag source-side imputation; acquire some intentionally conflicting cells (genuine conflicts are needed to evaluate D4 and REPORT_CONFLICT).
- STEP 13 (literature corpus): if full-text passages are served at runtime, Step 36 needs a SciFact/MultiVerS-style verifier and possibly late interaction; otherwise Step 13 is discovery-only and feeds Step 09.
- STEPS 16–20 (state): state-reconstruction confidence (D8) and current_state_version hash in every packet; slot extraction quality is the main threat to structured retrieval (S2p vs S2 gap).
- STEP 19 (gold trajectories): benchmark questions that require state (H_STATE) — 53 rows UNWRITTEN; only 14 supported recipe–evidence pairs → too few for calibration; plan more.
- STEP 23 (applicability): output status per (mechanism, query) that the QUALITATIVE rung can cite; UNKNOWN applicability ⇒ no MODEL rung.
- STEPS 24/27 (registry, simulator validation): validated domain descriptors the MODEL rung can test (D10).
- STEPS 30–33 (transition models): every promoted model must ship conformal/CQR intervals with coverage reported per split and an OOD/support-distance
  function; models that fail their gate cannot enter the MODEL rung (cascade skips to QUALITATIVE).
- STEP 35 (representation): similarity notions used by L2/L4 must be labelled (structural ≠ sensory); FlavorTwin consumes the same packet/profile machinery.

---------------------------------------------------------------------------------------------------------------
## 6. Residual uncertainty; is a pilot cheaper than more reading?
- Calibration-data budget is the binding constraint, not method choice. Two-sided 95% Clopper–Pearson upper bounds on selective risk
  (computed here, stdlib): n=14, 0 errors → ≤23%; n=104, 5 errors (4.8%) → ≤10.9%; n=320, 16 (5%) → ≤8.0%; n=440, 22 → ≤7.5%;
  n=1000, 50 → ≤6.5%. So the planned benchmark (104/320/440, Master Plan L3166) supports at best "risk ≲ 8–11%" statements for the whole
  set, and much weaker per rung. Per-rung guarantees at α=5% need several hundred labelled items PER RUNG.
- Transfer of silver results to human questions is unknown (structured retrieval's advantage depends on slot parsing of real questions).
- Whether a learned compatibility classifier adds anything over S2p (0.975 HARD AUROC on silver) is unknown; headroom looks small.
- Whether genuine conflicts are frequent enough to evaluate D4 is unknown (repo conflict detector is direction-only).
- More reading will not change the architecture (stop rule §8 criteria 1 and 2 met: searches on calibration/conformal/abstention returned the
  same small set of foundational works; the architecture choice is stable). An EMPIRICAL PILOT IS CHEAPER:
  P1 (≈150–200 human-labelled query–evidence pairs, stratified by the hard-negative types in §3.1, double-labelled, food/process-cold) → decides
      L5' promotion and gives the first calibration set for P(support). Human cost estimate UNVERIFIED (~6–10 expert hours at 2–3 min/pair).
  P2 (≈100 must-abstain/sufficiency-stratified questions, the D-008 T5/T8 types) → first RC curve, AURC vs scalar-threshold baseline, abstention F1.
  Both are CPU-only and fit inside Step 36 (or the benchmark work in parallel with Steps 08–15); neither touches Step 08 or locked test data.
