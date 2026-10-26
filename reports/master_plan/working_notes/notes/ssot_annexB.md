# READER ssot_annexB — SSOT v15 annex §257D → §257P (+ §258 boundary), L31465–42743

Source: `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` (cited "SSOT Lnnnnn"). Index: `docs/SSOT_INDEX.md`.
Read-only. No repo file was modified. Cross-references to sections outside my range (§236, §245.12, §247, §249) were read only to resolve pointers that the annex itself depends on; they are marked "(outside range)".

## 0. Heading inventory and what is actually in the range (READ THIS FIRST)

| § | Lines | Content type | Real substance? |
|---|---|---|---|
| 257D Gold test catalog (vocab/quantity/entity/state) | L31465–33895 | 162 quantity cases Q001–Q162 (L31469–32926) + 121 vocabulary cases V001–V121 (L32927–33895) | **Templated.** Every Q case has the same 7 bullets; every V case has the same 6 bullets (verified by `uniq -c`: each bullet appears exactly 162× / 121×). Only the phrase in the heading varies. **No expected outputs per case. No ENTITY or STATE cases exist despite the title.** |
| 257E Research-protocol template for RQ16-01…30 | L33896–34680 | 30 × 25-field protocol | **Templated.** All 30 protocols identical except the heading (each bullet appears 30×). |
| 257F Source acquisition & evidence-curation protocols | L34681–34765 | 7 subsections, field lists | **Substantive** (unique content). |
| 257G Dataset audit report — required tables per release | L34766–34862 | 9 table blocks | **Substantive.** |
| 257H Annotation few-shot design requirements | L34863–34945 | 8 example classes with expected structures | **Substantive.** |
| 257I Software test strategy | L34946–34982 | 6 test layers | Substantive (short). |
| 257J User-facing behaviour / human-agency contract | L34983–35013 | 5 rules | Substantive (short). |
| 257K Semester-scale implementation sequencing (Blocks 1–8) | L35014–35074 | step-like ordered blocks | **Substantive; step-like.** |
| 257L RQ execution cards A–Z for RQ16-01…30 | L35075–42159 | 30 × 26 stages, each with a 4-item checklist | **Templated.** All 30 cards identical except heading (every non-heading line appears ≥30×). The RQ-specific content (data, baseline, split, metrics, promotion criterion) lives only in §247 (outside range, L26783–27385). |
| 257M End-to-end semantic evidence packet examples | L42160–42329 | 15 scenarios | Partly templated: "Scenario / Packet must contain / Response policy" vary; "Mandatory fields" and "Forbidden behaviour" identical across all 15. |
| 257N Decision trace examples | L42330–42634 | 10 trace types | **Templated:** each trace type lists the same 28 trace fields. |
| 257O Lookup/retrieval playbook by query type | L42635–42704 | 7 pipelines | **Substantive.** |
| 257P Final critical-path checklist before large-scale build | L42705–42743 | 3 checklists (15 + 8 + 5 items) | **Substantive; hard gate list.** |
| 258 v14 merge/change register | L42744–42795 (boundary) | v13→v14 change log (35 items) + "what did not change" | Historical/changelog. |

**Corrections to the assignment's premises (verified):**
- The task text calls §257G/H "Silver/Gold staging". In SSOT v15, **§257G is the dataset release audit-table spec and §257H is the few-shot annotation design requirement**. The Silver/Gold tier definitions and scale-up stages are in **§236 (L25587–25658, outside range)** and the Gold handbook in **§237 (L25659–25744, outside range)**. I summarise §236 below only because §257P/§257K depend on it.
- §257D's title promises "ENTITY, AND STATE PARSING" cases; there are none (only Q and V). This is an SSOT gap, not a reading omission.
- "Evidence tiers" (E1…E8) are not defined in this range; they are referenced indirectly (257F.3 "source quality/evidence tier", L34729; 257G.8 "direct vs near/model/simulated counts", L34846). The repo's operational tier map is `registry/evidence_tier_provenance_map_v1.csv`.
- "Split/leakage rules" in this range: 257E "Split"/"Leakage audit" bullets (L33910–33911 for RQ16-01, repeated), 257L stages F/G (L35106–35119, repeated), 257G.9 (L34854–34862), 257P item L42720. The canonical split-construction rule is 257A.15 (L28326–28340, outside range; read by another reader).

---

## 1. Definitions, entities and data contracts (field-level where given)

### 1.1 Quantity test-class contract (257D.Q*, L31469–32926)
Preamble L31467: "These are semantic test classes, not a claim that every phrase has an authoritative gram conversion. The expected behavior is often to parse correctly and return UNKNOWN for unsupported conversion."
Seven behaviours required for every Q case (e.g. Q001 L31469–31476):
1. Preserve exact raw phrase **and source span**.
2. Parse fields: **scalar / range / fraction / count / unit / size / packing / container / qualifier**.
3. Resolve locale-sensitive unit only when source/locale evidence is sufficient.
4. Exact physical conversion only through deterministic unit logic.
5. Food-specific mass conversion only with a portion/density/empirical record; otherwise **mass = UNKNOWN**.
6. Preserve state/form distinctions (raw/cooked, chopped/whole, melted/solid, packed/loose).
7. Validator must reject **silent midpoint substitution for ranges** and **silent numericization of qualitative quantities**.

Phenomenon coverage implied by the 162 phrases (I grouped them; SSOT gives no grouping):
- Fractions & unicode: `1 1/2`, `1½`, `¼ ⅓ ⅔`, `1⁄8` (Q002–Q003, Q117–Q120 approx.).
- Ranges: `1½–2 cups`, `2 to 3`, `2–3`, `between 3 and 4`, `roughly 300–350 g` (Q004, Q039–Q040, Q130s).
- Approximators/qualifiers: about, approximately, scant, generous, heaped, level, packed, loosely packed.
- Count + size: `2 large eggs`, small/medium/large onion (Q031–Q033).
- Container + stated mass: `1 (14 oz) can`, `one 400 g tin`, `2 x 200 g chicken breasts`, `three 250-mL bottles`, `one-half 400-g can beans`, `half a 750-mL bottle`.
- Packaging units: packet, sachet, envelope, cube, bouillon cube, tea bag, jar, carton, bottle, block, sheet.
- Botanical/anatomical count units: clove, head, stalk, stick, sprig, bunch, ear, cob, rack, leg, breast, pod, leaf, wedge, slice.
- Part-of-food: `juice of 1/2 lemon`, `zest of one lemon`, egg whites/yolks.
- Qualitative/unquantified: pinch, dash, splash, handful, few drops, to taste, as needed, for frying/dusting/greasing/sprinkling, enough to cover, optional.
- Relative/allocation (needs entity state): `half the reserved sauce`, `one third of the dough`, `remaining batter`, `1/2 cup nuts, divided`, `1 cup flour + 2 tbsp for dusting`, `2 cups broth, plus more as needed`.
- Arithmetic: `1 cup plus 2 tablespoons`, `1 cup minus 1 tablespoon`, `pinch each of salt and pepper`.
- State-dependent density pairs: cooked vs raw rice/millet, sifted vs unsifted flour, melted vs solid butter, frozen vs thawed berries, chopped vs whole nuts, crushed tomatoes vs puree, minced garlic vs paste, dried vs fresh oregano, `3 cups spinach, packed`.
- Locale-variant units: rice-cooker cup, Japanese cup, metric cup, US cup, Australian tablespoon, dessertspoon, coffee spoon, wineglass, glass, `250 cc`, `8 fl oz`, `12 oz`, `1 lb`.
- Serving/vessel units: serving, bowl, plate, ladle(ful), scoop, spoonful.
- Size-analogy units: fist-sized, golf-ball, pea-sized, walnut-sized, matchstick, coin-sized, finger-length, thumb-sized, `2-inch`/`5 cm` piece (Q148–Q162; Q162 at L32918).

### 1.2 Vocabulary test-class contract (257D.V*, L32927–33895)
Six behaviours for every V case (V001 L32927–32933):
1. Determine **food head** and whether phrase is **alias / subtype-variety / state-form / compound food / separate canonical concept**.
2. Keep raw surface form, **locale/language and context**.
3. Do not collapse semantically distinct products merely because strings are similar.
4. Do not create separate canonical concepts for quantity/size/cut/preparation modifiers when factorization suffices.
5. If multiple mappings plausible, emit **candidates/AMBIGUOUS** rather than guessing.
6. External ontology/database links are **optional alignments, not forced identity**.
Phenomena in the 121 phrases: plural/modifier factorization (red onion → large red onion → finely chopped red onions); regional synonyms (spring onion/green onion/scallion; coriander leaves/cilantro; gram flour/chickpea flour/besan; ragi/finger millet; jowar/sorghum; curd/yogurt; double/heavy cream); **dangerous near-strings** (clove spice vs garlic clove; corn flour vs cornstarch vs maize flour [UK/US divergence]; coconut milk vs cream vs cream of coconut; pepper → black pepper/bell pepper/chili; tomato paste vs puree; stock/broth/bouillon; rice vinegar vs rice wine vs cooking wine; cottage cheese vs paneer; Parmesan vs Parmigiano-Reggiano); **state/form** (frozen/thawed spinach, cooked rice, canned diced tomatoes, smoked salmon, canned vs fresh tuna); **part-of-food** (egg white/yolk/whole egg); **derived products** (potato starch vs potato; rice flour vs rice; soy sauce dark/light vs soybean; ghee/clarified butter vs butter; salted/unsalted).

### 1.3 Source acquisition contracts (257F, L34681–34765) — the only field-level acquisition spec in range
**257F.1 Recipe sources (L34683–34697)** — per corpus/source capture: source/dataset name+version; URL/PID where allowed; licensing/terms + redistribution status; language/locale; **source-domain/template ID**; raw-text availability; ingredient/instruction/serving fields; existing IDs/metadata; known duplicates/lineage; **acquisition date/checksum**.
**257F.2 Food composition / portion sources (L34698–34714)** — whether source provides: canonical food description; state/form; household portion; gram weight; density; edible portion; preparation notes; country/locale; source provenance; version/date. Rule L34713: "Do not merge portion values across states/forms/locales until compatibility is established."
**257F.3 Scientific process-effect papers (L34715–34730)** — study-level metadata *before extraction*: food species/variety/matrix; raw/pretreated state; process/equipment; condition ranges; target compounds/properties; **analytical platform**; **replicate/sample structure**; table/figure availability; study design/control; DOI/source; source quality/evidence tier.
**257F.4 Table extraction (L34731–34746)** — per extracted cell: row header; column header; value; unit; **basis/normalization**; **footnote markers**; table caption; study ID; **exact cell/row locator**; extraction method; human verification status.
**257F.5 Figure digitization (L34747–34756)** — original figure ref; digitization tool/version; approximate extraction uncertainty; label value **DIGITIZED**; L34755 "never silently merge digitized values with exact tabular values without a quality flag."
**257F.6 Mechanism/review evidence (L34757–34760)** — reviews support mechanism/background + source discovery; must not automatically replace the primary quantitative experiment when primary source is available.
**257F.7 Evidence conflict protocol (L34761–34765)** — L34763: conflict record created **only after compatibility checks**; record = supporting sets, opposing sets, matched variables, differing conditions/platforms, **independent-source count**, unresolved explanation.

### 1.4 Release audit contract (257G, L34766–34862) — "Each release report must include the following blocks" (L34768)
- G.1 Source distribution (L34770–34779): total recipes; unique source domains; recipes/source; top-source concentration; source-disjoint split counts; duplicate groups per source and cross-source; licence/release eligibility counts.
- G.2 Linguistic/locale (L34780–34787): languages; locales/measurement systems; regional alias counts; unresolved locale-sensitive units; transliteration/non-ASCII term counts.
- G.3 Recipe complexity (L34788–34797): ingredients/recipe; steps/events/recipe; intermediate entities; graph nodes/edges; merge/split/reserve/discard/recombine frequencies; coreference instances; qualitative endpoint frequency.
- G.4 Vocabulary coverage (L34798–34807): canonical concepts; aliases; mentions mapped exact/alias/hierarchical/ambiguous/unmapped; coverage by frequency decile; by source/locale; top unresolved phrases; concept merge/split changes since prior version.
- G.5 Quantity coverage (L34808–34820): mentions with explicit quantity; numeric/range/fraction/count/qualitative proportions; resolved physical units; locale-ambiguous units; authoritative portion conversions; density-based conversions; empirical-distribution conversions; model estimates; unknown mass/volume rate; outliers/review queue.
- G.6 Process/state coverage (L34821–34831): canonical process counts; process-family distribution; states/forms/tools; duration coverage; temperature coverage; **pH/water-activity/pressure coverage**; endpoint-phrase distribution; unknown-state field rates.
- G.7 Annotation quality (L34832–34842): **Deep-Gold IAA by field/task**; Silver vs Gold field F1; graph errors; provenance violations; validator failure rate; reannotation rate; human review rate; **cost per accepted record**.
- G.8 Scientific evidence support (L34843–34853): evidence atoms by target/process/food; direct vs near/model/simulated counts; study/source independence; condition coverage; target/compound coverage; conflict clusters; human-verified fraction; unsupported query-space analysis.
- G.9 Split integrity (L34854–34862): train/val/**calibration**/test counts; duplicate groups crossing splits **"must be zero under policy"** (L34857); source groups crossing source-disjoint split "must follow design"; ingredient/process cold counts; target leakage audit results.

### 1.5 Few-shot / annotation policy examples (257H, L34863–34945)
Principle L34865: few-shots "should teach the policy boundaries, not merely easy formatting."
- H.1 clean ingredient `2 tomatoes, chopped` → food=tomato, count=2, form=chopped, mass=UNKNOWN unless portion evidence separately invoked; forbidden shortcut L34880 "inventing a gram mass from general knowledge."
- H.2 `1 (14 oz) can diced tomatoes` → container=can; container stated mass=14 oz raw expression; deterministic normalization only if requested; **do not assume drained/edible mass** (L34896).
- H.3 `3 cloves garlic` vs `1/4 tsp ground cloves` → context resolves identity and quantity role.
- H.4 split/reserve "Reserve half. Add half of the reserved sauce later." → split entities/allocations; preserve reserved branch; use correct descendant.
- H.5 `Bake until golden.` → process=BAKE, endpoint_state=golden, time=UNKNOWN, temperature=UNKNOWN unless specified elsewhere.
- H.6 chemistry firewall `Boil the broccoli for 8 minutes.` → procedural annotation must not invent vitamin retention, pH or compound concentrations; enrichment is a separate evidence process.
- H.7 conflicting source: ingredient list 2 eggs vs instruction 3 eggs → preserve both, flag conflict.
- H.8 user observation overrides prediction: predicted `light_brown`, user reports `black` → current observable colour = user-observed black with timestamp/provenance; prior prediction stays in audit history.

### 1.6 Evidence packet contract (257M, L42160–42329)
Mandatory fields for every packet (identical in all 15, e.g. L42170): **query ID, current state version, evidence packet version, evidence class, known unknowns, claim/citation map, model version if used, confidence features, response mode.**
Forbidden for every packet (e.g. L42172): silently upgrade evidence class; erase conflicting conditions; create exact quantities/chemistry without support; cite a related source that does not support the associated claim.
Scenario-specific "packet must contain":
- M.1 direct (L42164): DIRECT FACTS + DIRECT EXPERIMENTAL EVIDENCE + conditions + citation map.
- M.2 near (L42175): DIRECT facts + NEAR EVIDENCE + interpolation status + uncertainty; "preserve condition distance".
- M.3 model fallback (L42186): training-support summary + model estimate + interval + OOD/evidence distance; "say model estimates; never studies show"; requires "validated Level-15 model".
- M.4 no evidence (L42197): known unknowns + broad background + disallowed quantitative claim.
- M.5 conflict (L42208): conflict clusters + differing conditions/platforms + **independence groups**; "do not majority-vote blindly".
- M.6 quantity exact / M.7 portion / M.8 ambiguous (L42219–42251): raw quantity + canonical unit + deterministic conversion record; + ingredient/state/form + portion evidence + uncertainty; ambiguity + candidates + missing locale/portion evidence → ask or range/UNKNOWN.
- M.9 state-aware action; M.10 critical unknown (unknown field + VOI reason + conditional decisions → ASK one observation); M.11 diagnosis (hypotheses + supports/contradicts + missing discriminators); M.12 recovery (recoverability + actions + evidence + stop criterion); M.13 irreversible (recoverability=IRREVERSIBLE/CONTAINABLE + alternatives).
- M.14 FlavorTwin structural: "no sensory proof", call it structural/chemical match only. M.15 process-conditioned: static baseline + process transition + support/OOD + target distance; "no human flavor-equivalence claim".

### 1.7 Decision trace contract (257N, L42330–42634) — 28 fields, same for all 10 trace types
`request_id, raw_query, decision_mode, state_graph_version, current_state_fields, history_summary, goals, hard_constraints, soft_preferences, retrievers_called, candidate_evidence_ids, evidence_compatibility_features, conflict_groups, known_unknowns, candidate_actions_or_hypotheses, rejected_candidates_and_reasons, transition_model_if_used, model_support_distance, uncertainty_features, VOI_question_if_any, selected_action_or_answer, claim_ledger_ids, citations, response_text, session_update, latency, cost, module_versions` (L42335–42362). Trace types: ANSWER direct, COMPARE two processes, RECOMMEND, ASK (high-VOI), DIAGNOSE, RECOVER, ABSTAIN unsupported chemistry, QUALITATIVE broad, CONFLICT report, FlavorTwin inverse candidate.

### 1.8 Retrieval playbooks (257O, L42635–42704) — these are de facto contracts for Step 36
- O.1 quantity (L42637–42647): parse food+state/form+quantity+unit+locale → exact unit engine → portion/density lookup → empirical distribution if permitted → model estimate only if explicitly enabled → UNKNOWN/clarification.
- O.2 recipe-procedure (L42648–42657): state/entity graph → process ontology → event/state corpus → source examples → **no chemistry inference**.
- O.3 scientific process-effect (L42658–42669): food/matrix + state + process + target + conditions → structured evidence filter → lexical scientific terms → dense atoms/passages → hard-negative-aware reranking → compatibility + lineage/conflict → direct/near/model/qualitative/abstain.
- O.4 mechanism (L42670–42673): mechanism text may come from reviews but quantitative result stays tied to compatible measurements; distinguish "why this may happen" from "how much happened".
- O.5 diagnosis; O.6 recovery (includes "short transition evaluation", L42690–42692); O.7 FlavorTwin: target views → structural/static baselines → sensory/functional/context filters where evidenced → process-conditioned expansion only for supported candidates → inverse optimisation under evidence/OOD/constraints.

### 1.9 Test layers (257I, L34946–34982)
Layers L34950–34960: unit; schema; property-based quantity/unit; golden semantic examples; graph replay; retrieval regression; calibration regression; end-to-end scenario; data-release audits. I.2 (L34962–34965): equivalent expressions must give identical canonical physical results for exact units (kg↔g, L↔mL, °C↔°F); **no invariance enforced for ambiguous locale portions**. I.3 graph replay (L34966–34969): frozen event sequence → same state deterministically; corrected upstream events → new version. I.4 retrieval regression with gold evidence IDs + hard negatives. I.5 prompt regression on same hard Gold subset before production reannotation. I.6 (L34980): "A release fails if required provenance, source checksum, split registry or schema versions are missing even when model metrics are high."

---

## 2. Models and baseline ladders (simple → strong → advanced)

The annex itself does not define model families; it imposes **baseline discipline** and points to ladders defined elsewhere:
- Generic rule (257E "Baseline hierarchy", L33907: "run the cheapest credible null/simple baselines first"; 257L.E "Baseline freeze", L35100–35104: "Run the simplest null plus the strongest simple baseline before tuning the proposed method. Store baseline artifacts and splits."). 257L.H (L35124): add only the component necessary; no bundled architecture changes. 257L.I: comparable hyper-parameter budget across methods.
- RAG ladder referenced by 257K (Block 5 "strong B1–B3 baselines" L35052; Block 6 "B4/B5 evaluation" L35058; Block 7 "B6/B7 comparison" L35064). Ladder defined at §245.12 (outside range, L26667–26678): B0 LLM only → B1 dense RAG → B2 BM25+dense hybrid → B3 structured metadata RAG → B4 state-aware RAG → B5 state + compatibility/conflict packet → B6 + Level-15 transition fallback → B7 + calibrated recommend/ask/abstain.
- Quantity ladder implied by 257O.1 (L42638–42646): exact unit engine → portion/density record → empirical distribution → model estimate (only if explicitly enabled) → UNKNOWN. This is a **lookup-first ladder**: model estimates are the last resort, consistent with §249.3 promotion order Rules/lookup → strong simple baseline → structured → learned → agentic (outside range, L27508–27519).
- FlavorTwin: 257P L42738 requires "static structural/descriptor/embedding baselines" before process-conditioned claims; 257O.7 starts from "structural/static retrieval baselines". Ladder B0–B6 for Project B is at SSOT L5195–5224 (outside range).
- Annotation ladder: one-shot prompt vs multi-pass (RQ16-11), LLM output alone vs deterministic validators (RQ16-12), Gold-only vs incremental Silver (RQ16-09), random vs active learning (RQ16-10) — RQ content §247 (outside range), operational protocol 257E/257L.
- Confidence: LLM verbal self-score is the baseline for the confidence-vector RQ16-05 (§247.5).

## 3. Experiments / hypotheses / RQs

- 257E (L33896–34680) and 257L (L35075–42159) are **procedural wrappers for the 30 RQ16 questions**; they add no RQ-specific content. The RQ-specific content is §247 (L26783–27385, outside range), which I extracted to resolve the pointers (question / data / baseline / split / metric / promotion):
  - RQ16-01 state value: B2/B3 without state; source/duplicate-disjoint; ConditionCompatible@K, ModeF1, UCR; promote "only if improvement persists beyond bootstrap CI".
  - 02 structured retrieval vs dense; source-disjoint; Recall@K, citation precision, UCR.
  - 03 compatibility reranker vs generic cross-encoder; food/process/source cold; AUROC/F1, compatible Recall@K; "gain on hard negatives".
  - 04 packet vs raw chunks; UCR, citation precision, conflict handling.
  - 05 confidence vector vs LLM self-score; Brier, ECE, error AUROC, risk–coverage.
  - 06 sufficiency cascade vs always-answer; support-regime held-out; risk–coverage, UCR, quantitative error.
  - 07 quantity ontology vs raw/unit-only; ingredient/source cold; mass error/coverage + downstream gain; must improve grounding **and** ≥1 downstream task.
  - 08 canonical vocab vs raw strings; source/locale cold; link accuracy, fragmentation.
  - 09 Silver utility 10k/25k/60k/100k vs Gold-only; fixed source-disjoint Gold test; macro F1, calibration; "identify saturation curve".
  - 10 active learning vs random; F1/coverage per human label.
  - 11 Claude multi-pass vs one-shot; field F1, graph F1, provenance violations.
  - 12 deterministic validators vs LLM-only; critical error rate.
  - 13 duplicate leakage: random vs group-safe split; "metric inflation delta".
  - 14–22: session memory, observation override, feasibility filter, VOI, diagnosis verifier, recovery separation, transition fallback (cold pair/study split), completion visibility, conflict clustering.
  - 23 quantity encoder downstream; 24 recipe graph downstream (step F1, state accuracy; source/process cold); 25–27 FlavorTwin process conditioning / recipe context / human sensory boundary; 28 source/domain generalisation; 29 long-tail equity; 30 full system vs B0–B5, locked final test.
- 257E's 25 protocol fields (L33901–33924): claim; unit of analysis; population/domain; inclusion (frozen before viewing final test); exclusion ("do not exclude hard cases after failure"); target definition (incl. evidence precision); baseline hierarchy; proposed model; confounds; split; leakage audit; metrics (macro/per-bucket + CIs); calibration (reserved data, risk–coverage); seeds/repeats (or grouped bootstrap); compute budget; ablation; oracle test; error taxonomy; success gate; null gate; negative gate; external validity; provenance freeze; decision record (KEEP/MODIFY/DROP/NEED_DATA).
- 257L 26 stages A–Z (L35081–35314): A claim freeze, B data-support audit ("If the target is not supported at the intended fidelity, downgrade the claim before modeling", L35089), C Gold/evidence status (headline eval "uses the allowed real/gold regime only", L35096), D confound register, E baseline freeze, F split freeze, G leakage audit, H proposed method, I hyper-parameter budget, J calibration (distinct from final test), K primary metric (declared before final test), L secondary metrics (cost, latency, coverage, provenance violations), M macro/subgroup, N uncertainty (grouped bootstrap / seeds / CIs "appropriate to the unit of independence"), O ablation, P oracle upstream, Q error analysis (predeclared sample), R negative control (randomized topology, shuffled quantity, wrong-condition retrieval), S positive control, T reproducibility, U success gate ("do not redefine success after observing results"), V null decision, W negative decision ("Do not remove negative result from the SSOT"), X data-limited decision (NEED_DATA "instead of escalating architecture"), Y external validity, Z downstream update (architecture decision register). Every stage repeats the 4-item checklist: decision recorded before final test; artifacts/version IDs attached; no unverified synthetic/imputed final targets; result interpreted within evidence precision.
- Repo use: Master Plan v4.0 Q1 (docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md L1080) mandates "Every experiment and sub-experiment uses the SSOT §257L card (A–Z)". `registry/ssot15_state_experiment_map.csv` lists SX experiments with nearly all design columns = `NOT_SPECIFIED_IN_PLAN` (e.g. rows SX-07-01…06, SX-10-01…06), i.e. no 257L card has actually been filled for these.

## 4. Gates, promotion and stop rules (exact quotes, line numbers)

### 4.1 §257P — the only hard gate list in the range (L42705–42743)
**P-A "Do not authorize 60k–100k production annotation until:" (L42707)**
- P-A1 L42709 "schema v1 fields and missingness meanings are documented;"
- P-A2 L42710 "provenance enum is enforced in code;"
- P-A3 L42711 "raw-source checksum/manifest exists;"
- P-A4 L42712 "at least 100–500 difficult Gold seed cases exist;"
- P-A5 L42713 "unit engine passes property-based tests;"
- P-A6 L42714 "canonical vocab proposal/review workflow works;"
- P-A7 L42715 "quantity lookup can return exact/interval/UNKNOWN without guessing;"
- P-A8 L42716 "event/state graph can represent intermediate, split, merge, reserve and recombine;"
- P-A9 L42717 "QA reviewer flags fabricated chemistry/conditions;"
- P-A10 L42718 "batch report includes source/vocab/quantity/graph/unknown/provenance statistics;"
- P-A11 L42719 "pilot cost and reannotation rate are known;"
- P-A12 L42720 "duplicate grouping runs before split assignment;"
- P-A13 L42721 "Deep-Gold annotators remain independent of Silver predictions;"
- P-A14 L42722 "prompt/model/schema versions are logged;"
- P-A15 L42723 "a rollback/reprocess strategy exists if a schema/prompt bug is discovered."
(The IDs P-A1… are mine for reference; the SSOT uses unnumbered checkboxes.)
**P-B "Do not authorize final CulinaryState-RAG claims until:" (L42725)**
- L42727 compatible retrieval benchmark exists; L42728 citation precision/unsupported-claim rate measured; L42729 evidence conflicts represented; L42730 "confidence is calibrated on held-out gold"; L42731 "Level-15 fallback domains are explicitly whitelisted by gates"; L42732 feasibility filter evaluated; L42733 decision/abstention baseline ladder run; L42734 "locked test data have not been used for iterative prompt/model tuning."
**P-C "Do not authorize strong FlavorTwin V2 claims until:" (L42736)**
- L42738 static structural/descriptor/embedding baselines exist; L42739 process transition inputs supported/calibrated; L42740 candidate constraints/OOD tracked; L42741 "process-conditioned model beats static baselines on a held-out process-sensitive task"; L42742 "sensory-equivalence wording is backed by sensory data or avoided."

### 4.2 Other gate-like rules in range
- 257G.9 L34857 duplicate groups crossing splits "must be zero under policy"; L34858 source groups crossing source-disjoint split "must follow design".
- 257I.6 L34980 release-fail rule (missing provenance / source checksum / split registry / schema versions ⇒ fail regardless of metrics).
- 257F.5 L34755 digitized-vs-tabular quality flag mandatory; 257F.2 L34713 no cross-state/form/locale portion merge; 257F.7 L34763 conflict only after compatibility.
- 257E success/null/negative gate trio (L33919–33921) and 257L U/V/W/X (L35260–35290): null ⇒ "retain simpler baseline unless another predeclared advantage is meaningful"; worse ⇒ DROP/MODIFY; huge CIs/unreliable labels ⇒ NEED_DATA.
- 257K closing rule L35073: "FlavorTwin process-conditioned implementation runs after the shared state/evidence core is stable".
- 257J.5 L35011: "Reserve human flavor-equivalence language for sensory validation."
- 257M.3 L42186: model-fallback packet requires a "validated Level-15 model"; ties to G16-TRANS.

### 4.3 Gate IDs that the annex points to (outside range, quoted for the mapping)
§249.1 (L27444–27486): G16-DATA "Deep Gold exists with independent annotation/adjudication; Silver quality and source/duplicate controls documented." · G16-VOCAB · G16-QTY "Deterministic units correct; food-specific portion conversions have provenance; qualitative/unknown quantities are not fabricated; interval calibration reported where distributional." · G16-SEM · G16-GRAPH · G16-EVID · G16-CONFLICT · G16-CAL "calibrated on held-out independent gold; risk–coverage reported" · G16-TRANS "No Level-15 fallback is used for a target/domain until the relevant G15 gates pass." · G16-DEC · G16-REC · G16-PROV · G16-OOD · G16-FT. §249.2 stop rules (L27489–27500) include "Silver does not improve held-out Gold performance", "quantity conversions are mostly unsupported", "human verification cost exceeds the value of the proposed feature". **Note: none of the G16 gates has a numeric threshold; they say "declared threshold"/"declared acceptance criteria". The annex (257E/257L) requires the threshold to be pre-declared per RQ but never supplies one.**

### 4.4 Repo status of §257P (verified where possible; not a full audit)
- P-A2 provenance enum: `registry/provenance_class_registry_v1.csv` exists; schema/law validators in tests (SX-07-03 marked PARTIAL in `registry/ssot15_state_experiment_map.csv`). Partially met.
- P-A3 raw-source checksum/manifest: `registry/data_source_acquisition_manifest.csv` (64 sources + header, has `checksum_if_existing`, `licence*`, `snapshot_version_date`); recipe_base freeze fingerprint e7d58913 per ctx (S133). Partially met (recipe base yes; scientific sources not acquired).
- P-A4 Gold seed ≥100–500 hard cases: **NOT met.** `reports/gold/foodcom_v1_1_review_record.json`: 20 recipes, AI-assisted, `"not_independent": true`, batch-level approval, 0 row-level decisions; `reports/gold/foodcom_ai_assisted_human_review.md`: "NOT independent annotation… agreement is trivially 1.0 and non-informative", 126 proposed events not written. `registry/human_verification_queue.csv` HV-004 (blind pass) BLOCKED_HUMAN.
- P-A5 unit engine property tests: `tests/property/test_quantity_properties.py` (header cites §257I.2); WORKLOG S058. Met at code level.
- P-A7 exact/interval/UNKNOWN: `tests/unit/test_quantity.py::test_no_invented_grams_for_counts_and_volumes` (SX-10-02 COMPLETE). But POR ledger 0 rows (SX-10-03 MISSING) so "interval" via portion evidence untested.
- P-A11 pilot cost/reannotation: no 10k Silver pilot exists (SX-07-02/05 MISSING). NOT met.
- P-A12 duplicate grouping before split: Step 07I-R produced provisional families (605,476) and a 400-pair blind packet UNLABELED (ctx/WORKLOG S134). Grouping exists but threshold is not human-calibrated ⇒ PARTIAL.
- P-A13 independence of Deep-Gold from Silver: no Deep Gold yet; risk that current AI-assisted Gold becomes anchored. NOT met.
- P-B, P-C: not started (no RAG claims or FlavorTwin V2 claims authorised). Repo has §257I.4 retrieval regression test (`tests/integration/test_retrieval_regression.py`) but no compatible retrieval benchmark on real Deep Gold.
- 257D catalog: `tools/build_ssot15_experiment_map.py` L72 records SX-10-01 PARTIAL: "no frozen gold quantity catalog exact-match". Only isolated phrases (e.g. `thumb-sized piece ginger`, tests/unit/test_quantity.py L110) are tested.

## 5. Data requirements and named sources (licence notes)

- The annex names **no specific datasets**. It specifies what must be captured *per source* (257F.1–F.3) and what release audits must report (257G). Source naming is elsewhere (§182, §203.3, §250, §275; Master Plan B06/B02).
- Licence-relevant requirements in range: 257F.1 "licensing/terms and redistribution status", "URL or persistent identifier **where allowed**", "raw-text availability"; 257G.1 "license/release eligibility counts"; 257K Block 2 "authoritative portion imports **where permitted**" (L35029); 257O.1 "empirical distribution **if permitted**".
- Data volumes implied: Gold seed 100–500 hard cases (L42712); Deep Gold ~750–1,000, Gold-Light ~3–5k, Silver 60–100k, weak corpus 1M+ (§236.1 L25593–25597, outside range); 10k pilot (257K Block 3, L35032). RQ16-08 needs "100k aliases + Deep Gold links" (§247.8) — unrealistic as stated given the repo has ALIAS ledger in the thousands-scale (UNVERIFIED count; not inspected).
- Scientific evidence requirements (257F.3/F.4/F.5) presuppose full-text/table access to primary papers; licence/terms for table extraction and figure digitisation are not discussed in-range.
- Portion sources (257F.2): fields required (household portion, gram weight, density, edible portion, state/form, locale). Repo has 0 POR rows (SX-10-03). Candidates such as USDA FDC portion data exist in `registry/ingredients/fdc_crosswalk_candidates_v0.csv` (not inspected in detail).
- Licence context from ctx.md: BBC A1 RESTRICTED local-only; Food.com CC0 uploader-declared only; TASTEset unverified; CoSyLab permitted per D-015 (ASSUMED/DERIVED_ONLY). 257G.1 "license/release eligibility counts" must therefore be computed from `registry/recipe_source_usage_registry_v1.csv` (has `training_allowed`, `raw_redistribution_allowed`, `derived_redistribution_allowed`, `H2_required`).

## 6. Dependencies on other levels/steps

- 257D depends on §235 CQPO / Q0–Q6 portion ladder, §238/§257C field dictionary (Quantity, PortionProfile, CanonicalIngredient, Alias), §257A.1/§257A.2 decision trees (outside range).
- 257F depends on §238/§257C EvidenceAtom and ClaimLedger contracts (L30958–31301, outside range) and on the evidence-tier definitions (Part I; repo map `registry/evidence_tier_provenance_map_v1.csv`).
- 257G depends on §236.7 release statistics (L25655–25658) — 257G is the expanded table version of §236.7 — and on duplicate grouping (§264, Step 07I) and split registry (257A.15).
- 257H depends on §239 Claude annotation contract and prompt pack (L26102–26259) and §257A.6 chemistry firewall.
- 257K is a compressed ordering of §252 roadmap (L27585–27647) — Blocks 1–8 map to §236.5 Stages 0–10 + §252 Phases.
- 257L/E depend on §247 (RQ content), §248 (E16 experiments), §249 (G16 gates).
- 257M/N/O depend on §241 retrieval/compatibility/conflict, §242 confidence, §243 decision/VOI, §244 runtime, §245 benchmark, §246 FlavorTwin V2 boundary, and on Level-15 G15 gates (M.3, P-B L42731).
- 257P P-B depends on Level 15 (G15 gates) for the fallback whitelist; P-C depends on Level 13/14 representations and Level 15 transitions.

## 7. Risks / failure modes (as stated or directly implied)

1. **Template illusion of completeness.** 257D/E/L/N look like ~10k lines of specification but are 4 templates multiplied. A planner counting "283 Gold test cases" would overestimate what exists: there are 283 *phrases* and zero *expected answers*. Gold answer keys must still be authored (human effort).
2. **Missing entity/state Gold cases** (title vs content of 257D). Steps 16–20 have no SSOT test catalog for events, coreference, split/reserve, endpoints beyond the 8 few-shot classes in 257H.
3. **Gold anchoring** (P-A13). The only existing Gold (Food.com 20 recipes) is AI-assisted, not independent; if it is treated as Deep Gold, G16-DATA and G16-CAL become invalid.
4. **Silent numericisation** of qualitative quantities / midpoint substitution (257D validators; 257H.1) — leaks fake grams into CQPO and later into nutrition/retention calculations.
5. **Portion merge across state/form/locale** (L34713) — e.g. cooked vs raw rice density.
6. **Digitised vs tabular merge** (L34755) — biases kinetic fits in Steps 24–27/32.
7. **Review papers substituting for primaries** (257F.6) — inflates independence counts, breaks study-disjoint splits.
8. **Premature conflict records** (257F.7) — "conflicts" that are actually condition differences.
9. **Duplicate/source leakage** (257G.9, RQ16-13) — inflates parser/RAG metrics.
10. **Calibration/test contamination** (257L.J, P-B L42734).
11. **Architecture escalation under data scarcity** (257L.X NEED_DATA rule) — the main stop rule for Steps 30–35.
12. **FlavorTwin over-claiming** (257J.5, M.14/M.15, P-C) — chemical similarity presented as flavour equivalence.
13. **Cost risk**: 257G.7 "cost per accepted record" and P-A11 — no cost model exists yet for Silver annotation (Claude multi-pass at 10k–100k scale).

## 8. MAPPING TO THE 36-STEP SPINE (brief §9)

Caveat: the 36-step plan's step cards are not in the repo (ctx.md). Below, "requires" means "what this SSOT annex material demands of work that, by spine title, belongs to that step". Step assignment is my reconstruction.

| Step | What the annex requires |
|---|---|
| **01 Freeze project authority** | Adopt 257E/257L as the mandatory experiment protocol (Master Plan Q1 already does, L1080); adopt 257P as the large-build gate; record that 257D/E/L/N are templates (no RQ-specific gates in-range). Output: authority note that RQ-specific thresholds must be pre-declared in each card. |
| **02 Audit implementation state** | Audit against 257P P-A1…P-A15 item by item (status table in §4.4 above); audit 257I test layers (repo has property, replay, data-contract, retrieval regression, e2e tests). Output: 257P checklist status file. |
| **03 Freeze state semantics** | 257H.5 (endpoint_state with time/temperature UNKNOWN), 257H.8 (observation-over-prediction with timestamp/provenance; prior prediction retained), 257H.4 split/reserve descendants, P-A8 graph must represent intermediate/split/merge/reserve/recombine. Missingness meanings documented (P-A1). |
| **04 Freeze evidence / provenance / similarity contracts** | Provenance enum enforced in code (P-A2); evidence-class labels used in packets (257M mandatory field "evidence class"); DIGITIZED value label (257F.5); conflict record schema (257F.7); packet mandatory fields (257M); trace fields (257N); similarity naming vocabulary (257J.5: chemical-profile / descriptor / structural / model-estimated process-conditioned; sensory only with sensory validation). |
| **05 Normalize EVD** | Basis/normalization per value (257F.4); footnote markers; locator; extraction method; human verification status; quality flag for digitised values; direct vs near/model/simulated counts for 257G.8. Repo EVD has `target.basis`, `provenance.locator`, `extraction_version`, `verification.status`, `independence_group`, `tier`; **lacks DIGITIZED flag, footnote markers, table caption, row/column header fields** (UNVERIFIED that they are absent from the schema file; absent from ledger rows). |
| **06 Freeze source acquisition manifest** | 257F.1 fields for recipe sources (incl. source-domain/template ID, acquisition date/checksum, known duplicates/lineage); 257F.2 fields for portion sources; 257F.3 study-level fields at manifest level ("table/figure availability", "analytical platform", "replicate structure"). Repo manifest already has `replicate_information`, `measurement_method_available`, `study_lineage_available`, `checksum_if_existing`, licence fields — good alignment; missing an explicit "source-domain/template ID" for recipe corpora (UNVERIFIED; check `registry/recipe_source_usage_registry_v1.csv`). |
| **07 Condition & measurement normalization** | 257G.6 coverage of duration/temperature/pH/aw/pressure; 257F.3 "condition ranges", "analytical platform"; 257H.5 UNKNOWN conditions when endpoint-only; 257D Q-cases state/form preservation. The Step-07 human audit (07H, NOT_COUNTED_PROVENANCE_INVALID per ctx) is a P-A4/P-A13-type independence issue. |
| **08 Scientific source lineage** (NOT authorised) | 257F.3 study-level metadata **before extraction**; 257F.6 review vs primary distinction (lineage must mark review-derived values and link to primary); 257F.7 "independent-source count"; 257G.8 "study/source independence"; 257M.5 "independence groups". Output must allow study-disjoint and publication-disjoint splits (257E "Split", 257L.F) and grouped bootstrap by unit of independence (257L.N). Repo STUDY ledger (125 rows) has only id/design(=UNKNOWN)/source_id — none of the 11 257F.3 fields. |
| **09 Evidence extraction & verification machinery** | 257F.4 cell-level fields; 257F.5 digitisation tool/version/uncertainty; extraction method + human verification status; 257I.5 prompt regression on fixed hard subset; 257H.6 chemistry firewall for extractors; P-A9 QA reviewer flags fabricated chemistry/conditions. |
| **10 20-row mechanism pilot** | Run 257L card (A–Z) in miniature: claim freeze, data-support audit (L35089 "downgrade the claim before modeling"), Gold/evidence status labelling, predeclared error taxonomy; measure verification cost per row (257G.7 cost per accepted record). |
| **11 Wave-1 verified mechanism evidence** | Study-level metadata per 257F.3; conflict records per 257F.7; human-verified fraction (257G.8). |
| **12 Structured database evidence** | 257F.2 portion/composition fields; no cross-state/form/locale portion merging (L34713); version/date per source. Feeds POR (currently 0 rows) for 257O.1 and P-A7. |
| **13 Large literature discovery corpus** | 257F.6: reviews for discovery/mechanism background only; primary-source retrieval required for quantitative values; DOI/source per 257F.3. |
| **14 Coverage-driven evidence growth** | 257G.8 "unsupported query-space analysis" and coverage by target/process/food is the coverage metric; RQ16-06 support-regime strata need queries stratified by DIRECT/NEAR/MODEL/NONE regimes. |
| **15 Freeze DATA-EVIDENCE v1** | Must produce a 257G.8 + 257G.9 release audit; 257I.6 release-fail rule (provenance, source checksum, split registry, schema versions); split registry with calibration split separate from test (257G.9 "train/validation/calibration/test"). |
| **16 Instruction semantic schema** | 257H.4/H.5/H.7/H.8 cases as schema acceptance tests; P-A1 schema v1 + missingness documented; P-A8 graph expressiveness. |
| **17 Instruction-level extraction** | 257D Q/V catalogs need answer keys; 257H few-shots for prompts; RQ16-11 multi-pass vs one-shot; RQ16-12 validators; 257I.5 prompt regression; P-A9; P-A14 version logging. |
| **18 Event-sourcing engine** | 257I.3 graph replay determinism and versioned re-derivation; 257H.8 observation override with audit history; P-A15 rollback/reprocess. |
| **19 Gold state-trajectory pilot** | P-A4 ≥100–500 difficult Gold seed cases; P-A13 independence from Silver; 257G.7 Deep-Gold IAA by field/task; 257D entity/state cases must be authored (gap). Current 20-recipe AI-assisted Gold does **not** satisfy this. |
| **20 Scale procedural semantic corpus** | Gated by **all of P-A1…P-A15** (L42707: "Do not authorize 60k–100k production annotation until"); 257K Block 3 10k pilot first (multi-pass, audit, duplicate grouping, source distribution, cost/quality, prompt/schema repair); 257G.1–G.7 audit per release; RQ16-09 saturation curve and RQ16-10 active learning decide whether to go past 25k/60k. |
| **21 Effect / mechanism ontology** | 257O.4: mechanism explanation ("why") separate from quantitative effect ("how much"); 257F.6 review evidence role. |
| **22 Event → effect signatures** | 257H.6 chemistry firewall: procedural events never directly carry chemistry; effects come via separate evidence query (257O.2 "no chemistry inference" vs 257O.3). |
| **23 Mechanism applicability engine** | 257O.3 compatibility filter on food/matrix + state + process + target + conditions; 257F.7 compatibility before conflict. |
| **24 Formula / model registry** | 257L.T reproducibility metadata (dataset/split/code/model/prompt/ontology/schema/evidence versions + seeds/compute); 257M.3 "training-support summary"; 257N `module_versions`, `transition_model_if_used`. |
| **25 Parameter-compatibility retrieval** | 257O.3 "hard-negative-aware reranking → compatibility + lineage/conflict"; RQ16-03 compatibility reranker (food/process/source cold splits); 257I.4 retrieval regression with gold evidence IDs + hard negatives. |
| **26 Focused deterministic simulator** | Annex silent on simulator choice. Only constraints: 257L.C simulated labels never in headline eval; 257M forbids upgrading evidence class. |
| **27 Validate simulator on held-out evidence** | 257L.F split freeze, 257L.G leakage, 257L.N grouped uncertainty by unit of independence (study), 257F.5 digitised-value uncertainty must propagate. |
| **28 E7 synthetic prior** | 257L checklist item "no unverified synthetic/imputed final targets" (every stage, e.g. L35087). |
| **29 TRANSITION_BOOTSTRAP_V0** | 257L.B data-support audit; 257L.X NEED_DATA rule. |
| **30 Tabular / sparsity bake-off** | 257E baseline hierarchy; 257L.E/I/V (equal budgets; null ⇒ keep simpler). |
| **31 Physics / condition features** | 257L.O ablation; 257L.R negative control (e.g., shuffled conditions). |
| **32 Focused kinetics** | 257F.4/F.5 table vs digitised values with quality flag; replicate structure from 257F.3. |
| **33 Mechanistic vs ML vs hybrid** | 257L.V/W/X decision trio; 257L.Y external validity. |
| **34 Short rollout** | 257O.6 recovery "short transition evaluation"; RQ16-15 observation override error-vs-horizon. |
| **35 Representation ladder** | P-C L42738 static structural/descriptor/embedding baselines; RQ16-23 quantity encoder vs incidence/grams; RQ16-24 graph vs text/set; 257J.5 naming of similarity types. |
| **36 Evidence compiler → selective RAG → FlavorTwin** | 257M packet contract, 257N trace fields, 257O playbooks, 257J response layers/clarification/limitation, 257K Blocks 5–8 (B1–B3 → B4/B5 → B6/B7 → locked final test), **P-B gate (8 items) before any RAG claim**, **P-C gate (5 items) before FlavorTwin V2 claims**, L35073 FlavorTwin only after the shared core is stable. |

## 9. Contradictions, stale items, underspecified parts, open questions

1. **Title/content mismatch**: 257D says "ENTITY, AND STATE PARSING" (L31465); only Q and V cases exist. UNDERSPECIFIED → Steps 16–19 lack a Gold catalog.
2. **No expected outputs**: 257D cases have no answer keys; 257H gives 8 worked examples only. A real Gold quantity catalog (SX-10-01) must be authored; repo confirms "no frozen gold quantity catalog exact-match" (tools/build_ssot15_experiment_map.py L72).
3. **Templated RQ protocols**: 257E/257L are fully generic; RQ-specific "success/null/negative gate" thresholds are never defined anywhere (§247 promotion criteria are qualitative: "beyond bootstrap CI", "large reduction", "useful coverage gain"). G16 gates say "declared threshold". OPEN: every RQ needs a numeric pre-registration before running; the SSOT gives none.
4. **§257P scope vs Master Plan**: SSOT L42707 gates "60k–100k production annotation"; Master Plan v4.0 B07 (L386) gates "before scaling past 10k". Not contradictory (Master Plan is stricter/earlier) but P-A11 ("pilot cost and reannotation rate are known") presupposes a pilot run — the 10k pilot must therefore be allowed before 257P is fully ticked. The Master Plan's wording could be read as forbidding the pilot exit only; clarify.
5. **Gold seed size "100–500"** (L42712) is a range without criterion for "difficult" or for which tasks; §236.5 Stage 1 repeats it. Needs a reliability-based sizing (IAA CI width) — external research (e.g., annotation-reliability sample-size literature) required.
6. **"Deep-Gold IAA by field/task"** (257G.7) — no agreement statistic or threshold named in range (§237.3 outside range may define; not verified here).
7. **RQ16-08 "100k aliases"** data requirement (§247.8) is likely unrealistic relative to repo ALIAS scale (UNVERIFIED count).
8. **257K is a semester plan** ("course report/paper draft", Block 8; L35014 "semester-scale") — stale relative to a 36-step spine that front-loads Phase B/C evidence work. 257K puts the evidence store at Block 5, *after* the 10k pilot and parser (Blocks 3–4); the 36-step spine puts evidence (08–15) *before* procedural semantics (16–20). This is a sequencing contradiction between SSOT 257K and the spine; the SSOT text itself says "dependency order should remain" (L35016). Needs an explicit authority decision (possibly: the two are independent lanes, so both orders are compatible as parallel tracks).
9. **257M.3** requires a "validated Level-15 model" but defines no validation criterion beyond G16-TRANS → G15 gates (outside range).
10. **257F.3 vs repo STUDY ledger**: 125 STUDY rows have none of the required 11 fields (design=UNKNOWN). Step 08 must back-fill; it is the most concrete look-ahead debt found.
11. **EVD row count discrepancy**: `ledgers/data/EVD.jsonl` has 57,280 rows, while ctx.md cites ES-1.1 export PASS of 17,978 EVD rows. Possibly the export filtered a subset (e.g., retention rows only). UNVERIFIED; another reader should reconcile.
12. **257G.9 "calibration" split** is required, but whether the calibration split must be study-disjoint from test for evidence tasks is unspecified.
13. **Figure digitisation** (257F.5): no accepted tool or uncertainty-quantification method named. Open research: WebPlotDigitizer-style manual digitisation accuracy literature (not researched here).
14. **257I.2** expects °C↔°F invariance "when only temperature representation changes" — fine; but culinary oven "gas mark" and fan/conventional offsets are not mentioned (look-ahead for Step 07).
15. **§258 is stale**: it is the v13→v14 change register (L42746), carried into v15 unchanged; it calls §259 "the current return point" (item 35, L42783), whereas v15 return point is §279 (brief §1A). Do not treat §258 as current status.
16. 257K Block 5 uses "B1–B3 baselines", RQ16-30 baseline is "B0–B5", §252 compares B0–B7 — consistent but the headline comparison set should be fixed before the locked test (P-B L42734).

## 10. LOOK-AHEAD — variables/metadata earlier steps must capture

For **Step 03/04 (state & contracts)**
- `endpoint_state` (qualitative, e.g. golden) with explicit `time=UNKNOWN`, `temperature=UNKNOWN` (257H.5).
- `observation_source` ∈ {user_observed, model_predicted, source_text} + timestamp + superseded-prediction pointer (257H.8).
- Evidence class enum shared by packets (direct / near-interpolated / model / qualitative / none) and a `DIGITIZED` value-origin flag (257F.5) — check `registry/value_origin_registry_v1.csv` includes DIGITIZED (UNVERIFIED).
- Recoverability enum incl. IRREVERSIBLE / CONTAINABLE (257M.13).
- Similarity-type enum per 257J.5 (structural, chemical-profile, descriptor, model-estimated process-conditioned, sensory-validated).
- Packet mandatory fields (257M) and 28 trace fields (257N), esp. `state_graph_version`, `module_versions`, `model_support_distance`.

For **Step 05 (EVD)**
- Per value: `basis/normalization`, `footnote_markers`, `table_caption`, `row_header`, `column_header`, exact cell locator, `extraction_method`, `verification.status` (257F.4); `digitization_tool`, `tool_version`, `extraction_uncertainty` (257F.5); `is_review_derived` + `primary_source_ref` (257F.6).

For **Step 06 (manifest)**
- Recipe sources: `source_domain/template_id`, raw-text availability, serving fields present, known cross-source duplication, acquisition date + checksum, locale/measurement system (257F.1, 257G.1/G.2).
- Portion sources: state/form, household portion, gram weight, density, edible portion, locale, version/date (257F.2).

For **Step 07 (conditions/measurement)**
- Condition coverage axes for 257G.6: duration, temperature, pH, water activity, pressure; plus endpoint phrases; analytical platform (257F.3) linked to MEAS (repo MEAS has only 3 rows — platform granularity insufficient for "differing platforms" in 257F.7/257M.5).
- Locale-sensitive culinary units (US/metric/Japanese/Australian cup and tablespoon, rice-cooker cup, dessertspoon, coffee spoon, wineglass — 257D Q140–Q147) must carry `locale_resolution_status`.

For **Step 08 (lineage)** — highest-priority debt
- STUDY fields per 257F.3: species/variety/matrix, raw/pretreated state, process/equipment, condition ranges, target compounds/properties, analytical platform, replicate/sample structure, table/figure availability, design/control, DOI, evidence tier.
- Independence group / study group / publication group / platform group IDs to support study-, publication- and platform-disjoint splits and "independent-source count" in conflict records (257F.7, 257M.5, 257G.8).
- Review→primary links (257F.6) so derived values are not double-counted.

For **Step 09 (extraction machinery)**
- Prompt/model/schema version per extracted record (P-A14; 257L.T); human verification status; QA flag "fabricated chemistry/condition" (P-A9).

For **Steps 10–15 (acquisition)**
- Query-space stratification fields for RQ16-06 (support regime per query: DIRECT/NEAR/MODEL/NONE) and 257G.8 "unsupported query-space analysis".
- Conflict clusters with matched variables and differing conditions (257F.7).
- Cost per verified row (257G.7) — needed to decide Step 14 growth vs §249.2 stop rule "human verification cost exceeds the value".
- Calibration split membership assigned at freeze (257G.9), study-grouped.

For **Steps 16–20 (procedural semantics)**
- Ingredient-mention fields from 257D.Q: raw phrase + span, scalar/range(lower, upper, no midpoint)/fraction/count/unit/size/packing/container/container_stated_mass/qualifier, `qualitative_quantity` flag, relative-allocation reference (`half of reserved sauce` → entity id), arithmetic composition (`plus`, `minus`, `each`), purpose role (for dusting/frying/greasing → non-consumed or partially consumed), `optional` flag, `divided` allocation.
- State/form per mention (raw/cooked, sifted, packed/loose, melted/solid, frozen/thawed, drained/edible not assumed).
- Vocabulary fields from 257D.V: food head, mapping type (alias / subtype-variety / state-form / compound / separate concept), candidates + AMBIGUOUS, locale/language of surface form, optional external alignments (FoodOn/FDC) with alignment confidence — not identity.
- Source-conflict flags between ingredient list and instructions (257H.7).
- Recipe-level `source_domain/template_id`, `duplicate_group_id`, `family_id` assigned **before** split assignment (P-A12; 257G.9).
- Annotation provenance: annotator id, independence status relative to Silver (P-A13), adjudication record, IAA per field (257G.7).
