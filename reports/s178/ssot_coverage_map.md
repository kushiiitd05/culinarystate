# SSOT coverage map: sections no ledger component anchors (T0-C19-R1)

Status: **AI_DRAFTED / PROPOSED** (S178 GOVDOC lane, 9 Nov 2026). The classes are the agent's reading of each section's title and its relation to the ledger components; they are not human-verified. Machine-readable twin: `reports/s178/ssot_coverage_map.csv` (all 295 numbered top-level sections; 122 UNANCHORED rows carry a class), class source `registry/ssot_coverage_classes_S178.csv`, tool `tools/s178_ssot_coverage_map.py` (`--check` fails if a class is missing), test `tests/unit/test_s178_ssot_coverage_map.py`.

## 1. Method and result

Top-level numbered sections come from `docs/SSOT_INDEX.md` (295 rows of the form `N. TITLE`, letters kept: 257A to 257P). A section is **anchored** if a component of `registry/component_ledger_v1.csv` names its number in `ssot_anchor` or an anchor's line range overlaps the section's lines. Component T0-C19 (this coverage item's own component) is excluded, because it exists to classify what the others do not anchor.

- Numbered top-level sections: **295**; anchored by at least one component: **173**; **unanchored: 122**, every one with a class (zero blanks).
- Classes: **OWNER 59** (an existing item or component covers it; the owner is named), **OUT_OF_SCOPE_25NOV 40**, **SUPERSEDED 21**, **UNCOVERED 2** (sections 61 and 151; neither is needed for the 25 Nov talk).
- **Reconciliation with the acceptance text ("87 unanchored sections") and the item's own list.** The item text lists 67 sections once ranges are expanded (§51, §61-64, §72-74, §80-86, §99-102, §111-127, §143, §146, §152-170, §257G-257P). 22 of those 67 turn out to be anchored by other components (§64, §80-§86, §111-§113, §117, §121-§127, §159, §160, §168: classical-pairing and representation sections that T0-C15, T7-C05 and others cite), and the same method finds 77 unanchored sections that the item's list does not name (for example §17-§37 multimodal and fine-tuning text, §54-§60 roadmap text, §87-§95 encoder text, §184-§218 merge registers and return points). The figure 87 is not reproducible with this method; the map covers all 122 that it finds, which is a superset of what the item lists that is truly unanchored (45 of its 67).
- No section is classed UNCOVERED and needed for 25 Nov. The two UNCOVERED rows (user-context schema, terminology freeze) have code or a registry but no ledger owner; per the consensus rule they would "come back as new items" only if a 25 Nov deliverable needed them, and none does.

## 2. The sections, by class


### OWNER (59)

| § | lines | title | owner | reason |
|---|---|---|---|---|
| 20 | 1755-1795 | HOW PROJECT A AND B SHARE INFRASTRUCTURE | T0-C03 | shared infrastructure of the two projects = the shared research spine |
| 37 | 2410-2459 | LLM INPUT/OUTPUT — KEEP IT STRUCTURED | T8-C15 | structured LLM input/output = grounded response generator; prompt registry T8-C17-R1 |
| 44 | 2667-2725 | SENSORY COMPUTATION — WHAT EACH SENSE MEANS FOR THE PROJECT | T7-C08-R1 | sensory computation: decision 'sensory UNSUPPORTED' (T7-C08-R1) |
| 49 | 2943-3072 | CONFIDENCE AND UNCERTAINTY | T8-C12 | confidence and uncertainty = confidence vector, calibration (§242); also T6-C10 |
| 51 | 3096-3139 | SOFTWARE ARCHITECTURE | T0-C09 | software architecture = system architecture component |
| 52 | 3140-3165 | EXPERIMENT REPRODUCIBILITY | T9-C24 | experiment reproducibility = reproducibility, release semantics |
| 62 | 3822-3842 | RECIPE STATE SCHEMA | T9-C06-R1 | recipe state schema: covered by the section 238 conformance table (Recipe, State) |
| 63 | 3843-3866 | FOOD STATE SCHEMA | T9-C06-R1 | food state schema: covered by the section 238 conformance table (State, Entity) |
| 67 | 4039-4060 | ERROR ANALYSIS CATEGORIES | T0-C12 | error analysis categories = metrics and statistical reporting |
| 69 | 4091-4096 | THE 90-SECOND PITCH | T9-C21 | 90-second pitch = presentation slides |
| 72 | 4124-4153 | PUBLIC DEMOS | T9-C22 | public demos = demo scenarios |
| 75 | 4201-4246 | CORE READING LIST — ORDERED | T0-C02-R1 | core reading list = targeted related-work re-search |
| 76 | 4247-4293 | REFERENCE LINKS — VERIFIED 15 AUGUST 2026 | T0-C02-R1 | reference links verified 15 Aug 2026; re-check inside the related-work item |
| 77 | 4294-4304 | SOURCE INTERPRETATION NOTES | T0-C02-R1 | source interpretation notes |
| 88 | 4819-4852 | BEFORE DEEP LEARNING — BETTER NON-LEARNED SIMILARITIES | T7-C06 | non-learned ingredient similarities = set similarity E0/E1 (Step 35 'designed, not run' under decision #3) |
| 89 | 4853-4894 | CHEMICAL-STRUCTURE SIMILARITY — BEYOND EXACT COMPOUND IDENTITY | T7-C03 | chemical-structure similarity = molecule rung 35a |
| 93 | 5052-5087 | FREQUENCY BIAS IN LEARNED EMBEDDINGS | T7-C19 | frequency bias = mandatory confound audits |
| 95 | 5164-5190 | CULINARY CHARACTERISTICS VS. PAIRING CHARACTERISTICS | T7-C16 | culinary vs pairing characteristics = typed similarity registry (nine notions) |
| 99 | 5347-5432 | PRE-LEVEL-7 REPRESENTATION FREEZE — WHAT EXACTLY IS AN INGREDIENT PROF | T7-C05 | ingredient profile definition = ingredient chemical profile x_ij |
| 100 | 5433-5529 | MOLECULE / COMPOUND REPRESENTATION — THREE DIFFERENT THINGS | T7-C03 | molecule representation = molecule rung 35a |
| 101 | 5530-5618 | INGREDIENT CHEMICAL PROFILE — DO NOT CONFUSE INCIDENCE WITH MOLECULE R | T7-C05 | incidence vs molecule representation = ingredient chemical profile |
| 102 | 5619-5690 | FROM MOLECULE EMBEDDINGS TO AN INGREDIENT CHEMICAL EMBEDDING | T7-C07 | molecule to ingredient embedding = E2/E3 aggregators (learned part deferred, T7-C20) |
| 103 | 5691-5727 | FLAVOR-RELEVANT CHEMICAL PROFILE VS. COMPLETE CHEMICAL COMPOSITION | T7-C05 | flavour-relevant vs complete composition = ingredient chemical profile |
| 114 | 6418-6463 | HOW THIS CONNECTS TO LEVEL 7 WITHOUT CHANGING THE CLASSICAL FORMULA | T0-C15 | connection to Level 7 = classical replication |
| 118 | 6551-6587 | RESEARCH QUESTIONS CREATED BY THIS REPRESENTATION | T7-C01 | research questions of the representation freeze = Step 35 pre-registration |
| 119 | 6588-6640 | WHAT WE FREEZE BEFORE MOVING TO LEVEL 7 | T7-C01 | what is frozen before Level 7 = Step 35 pre-registration package |
| 120 | 6641-6658 | GO / NO-GO CHECKPOINT FOR LEVEL 7 | T0-C15 | go/no-go for Level 7 = classical replication |
| 140 | 8802-8821 | PROVENANCE AND EVIDENCE STATUS | T9-C03 | provenance and evidence status = evidence/provenance contracts |
| 143 | 8872-8973 | DESCRIPTOR AND REACTIVITY COMPUTE TIERS | T7-C04 | descriptor and reactivity compute tiers = RDKit toolkit and fingerprint rungs |
| 147 | 9055-9076 | OPEN-QUESTION DECISION REGISTER AFTER R1–R5 | T0-C18 | open-question decision register = governance and human gates |
| 152 | 9149-9368 | ASSIGNMENT-1 TRANSFER — RECIPE SEMANTIC PARSING & STATE RECONSTRUCTION | T3-C01 | assignment-1 transfer (recipe semantic parsing, state reconstruction) = recipe-semantics schema contract |
| 153 | 9369-9386 | RECIPE SEMANTIC PARSING — MODEL RESEARCH LADDER | T3-C11 | semantic parsing model ladder = Rung A deterministic extraction (learned rungs deferred) |
| 154 | 9387-9401 | COUNTING AND RANKING SEMANTICS — FROZEN BEFORE ANALYSIS | T0-C15 | counting and ranking semantics for the classical replication |
| 155 | 9402-9420 | MULTI-SOURCE INGESTION CONTRACT | T3-C23 | multi-source ingestion contract = recipe-level metadata, source/licence fields |
| 158 | 9521-9587 | COURSE-LEVEL COMPUTATIONAL OBJECTS — FROZEN ONTOLOGY | T3-C01 | course-level computational objects ontology = recipe-semantics schema contract |
| 161 | 9875-9941 | CULINARY GRAMMAR, FINGERPRINTS AND CONTEXT — PROJECT INTERPRETATION | T7-C14 | culinary grammar and fingerprints = cuisine rungs 35d |
| 162 | 9942-10043 | FLAVORDB — STATIC MOLECULAR INFRASTRUCTURE FROZEN INTO THE SSOT | T0-C17 | FlavorDB infrastructure: API/licence blocker owned by the professor-endpoint item (handoff/API_BLOCKERS.md #2) |
| 163 | 10044-10103 | RECIPE REPRESENTATION — COURSE SIMPLIFICATIONS AND OUR EXTENSION | T7-C12 | recipe representation = recipe rungs 35c |
| 164 | 10104-10181 | PROCESS-CONDITIONED FLAVOR TRANSFORMATION — NOW A COURSE-ALIGNED CORE  | T0-C03 | process-conditioned flavour transformation = the shared research spine |
| 169 | 10356-10392 | MULTIDISCIPLINARY CONTEXT IS A FIRST-CLASS VARIABLE | T7-C24 | multidisciplinary context variable = Level 13E scope and nullable historical metadata |
| 170 | 10393-10435 | HYPOTHESIS-FIRST EXPERIMENT DESIGN | T9-C08 | hypothesis-first design = pre-registration policy |
| 184 | 13279-13305 | v9 MERGE / CHANGE REGISTER | T0-C01-R2 | merge/change register named in the T0-C01-R2 acceptance |
| 195 | 15366-15397 | v10 MERGE / CHANGE REGISTER | T0-C01-R2 | merge/change register named in the T0-C01-R2 acceptance |
| 197 | 15516-15685 | LEVEL 14 — MASTER CONTRACT, STATUS, EVIDENCE REALITY, AND DATA-FEASIBI | T0-C16 | Level 14 master contract and status = Levels 12-17 frozen status |
| 204 | 17391-17575 | LEVEL-14 EXECUTION PROGRAM, WORTH RANKING, MVP, STRETCH, AND DEFER LIS | T0-C13 | Level 14 MVP/stretch/defer list = minimum publishable unit checklist |
| 206 | 17742-17782 | v11 MERGE / CHANGE REGISTER | T0-C01-R2 | merge/change register named in the T0-C01-R2 acceptance |
| 217 | 23053-23099 | v12 MERGE / CHANGE REGISTER | T0-C01-R2 | merge/change register named in the T0-C01-R2 acceptance |
| 254 | 27697-27722 | MASTER DEPENDENCY GRAPH — THEORY TO IMPLEMENTATION | T9-C26 | master dependency graph = timeline and critical path |
| 255 | 27723-27740 | R&D DECISION MATRIX AND PRIORITY ORDER | T9-C26 | R&D decision matrix and priority order = critical path |
| 257E | 33896-34680 | EXPANDED RESEARCH-PROTOCOL TEMPLATE FOR ALL RQ16 QUESTIONS | T9-C08 | research-protocol template = pre-registration policy |
| 257G | 34766-34862 | DATASET AUDIT REPORT — REQUIRED TABLES FOR EVERY MAJOR RELEASE | T2-C15 | dataset audit report tables = dataset card (T2-C15-R1) |
| 257H | 34863-34945 | ANNOTATION FEW-SHOT DESIGN REQUIREMENTS | T3-C02 | annotation few-shot design = annotation handbook |
| 257I | 34946-34982 | SOFTWARE TEST STRATEGY AND CONTINUOUS DATA VALIDATION | T9-C24 | software test strategy and data validation = reproducibility |
| 257J | 34983-35013 | USER-FACING BEHAVIOR AND HUMAN-AGENCY CONTRACT | T8-C14 | user-facing behaviour and human agency = decision policy (ASK, ABSTAIN) |
| 257M | 42160-42329 | END-TO-END SEMANTIC EVIDENCE PACKET EXAMPLES | T8-C07 | end-to-end evidence packet examples = context-packet component |
| 257N | 42330-42634 | DECISION TRACE EXAMPLES FOR DEBUGGING AND EVALUATION | T8-C14 | decision trace examples = decision policy |
| 257O | 42635-42704 | LOOKUP AND RETRIEVAL PLAYBOOK BY QUERY TYPE | T8-C01 | lookup/retrieval playbook by query type = query router |
| 257P | 42705-42743 | FINAL CRITICAL-PATH CHECKLIST BEFORE LARGE-SCALE BUILD | T9-C26 | final critical-path checklist rows go to T9-C26 as pass/fail lines (consensus note on C09) |
| 258 | 42744-42795 | v14 MERGE / CHANGE REGISTER | T0-C01-R2 | v14 register: same kind as the four named; added by this map |

### OUT_OF_SCOPE_25NOV (40)

| § | lines | title | - | reason |
|---|---|---|---|---|
| 21 | 1796-1820 | MULTIMODAL MODEL — THE COMPLETE INPUT/OUTPUT MAP |  | multimodal extension is L17, FUTURE/OPTIONAL (§129) |
| 22 | 1821-1875 | TEXT ENCODER — EXACT ROLE |  | multimodal text encoder design; learned encoders deferred (T7-C20, T7-C22-R1 'learned rungs deferred') |
| 23 | 1876-1919 | VISION ENCODER — EXACT ROLE |  | vision encoder; L17 |
| 24 | 1920-2003 | MOLECULAR ENCODER — EXACT ROLE |  | learned molecular encoder; deferred (T7-C20) |
| 25 | 2004-2043 | PROCESS ENCODER |  | learned process encoder; deferred (T4-C24) |
| 26 | 2044-2063 | STRUCTURED METADATA ENCODER |  | structured metadata encoder; deferred |
| 27 | 2064-2107 | AUDIO — WHERE IT ACTUALLY FITS |  | audio; L17 |
| 28 | 2108-2146 | VIDEO — WHERE IT ACTUALLY FITS |  | video; L17 |
| 29 | 2147-2192 | MULTIMODAL FUSION — DO NOT SIMPLY CONCATENATE EVERYTHING |  | multimodal fusion; L17 |
| 30 | 2193-2230 | MULTIMODAL ALIGNMENT — WHAT “SHARED EMBEDDING” REALLY MEANS |  | multimodal alignment; L17 |
| 31 | 2231-2271 | FINE-TUNING — THE FINAL STRATEGY |  | fine-tuning strategy; no new fine-tuning before 25 Nov (NER checkpoint exists, T3-C09) |
| 32 | 2272-2320 | TEXT FINE-TUNING |  | text fine-tuning; as 31 |
| 33 | 2321-2345 | VISION FINE-TUNING |  | vision fine-tuning |
| 34 | 2346-2379 | MOLECULAR FINE-TUNING |  | molecular fine-tuning |
| 35 | 2380-2393 | AUDIO FINE-TUNING |  | audio fine-tuning |
| 36 | 2394-2409 | VIDEO FINE-TUNING |  | video fine-tuning |
| 41 | 2557-2578 | MILLION-SCALE RAG — WHAT TO LEARN VS. WHAT TO BUILD |  | million-scale RAG; the 25 Nov scope is the 612,782-recipe base and 17,978 EVD rows (T8-C06 is the retriever) |
| 45 | 2726-2837 | HEALTH / NUTRITION / SUSTAINABILITY — HOW TO INCLUDE WITHOUT DERAILING |  | health/nutrition/sustainability; boundary only (see §165) |
| 46 | 2838-2859 | FLAVORQUEST / TRIVIA — FINAL ROLE |  | FlavorQuest/trivia product role |
| 47 | 2860-2904 | CONTEXT-AWARE COOKING SaaS — FINAL ROLE |  | cooking SaaS product role |
| 50 | 3073-3095 | INTERPRETABILITY |  | interpretability of learned models; no learned model in the talk |
| 56 | 3630-3693 | LEARNING TRACK — MACHINE LEARNING ORDER |  | ML learning order (curriculum) |
| 57 | 3694-3711 | WHAT NOT TO LEARN YET |  | 'what not to learn yet' (curriculum) |
| 60 | 3768-3800 | LOSSES TO UNDERSTAND |  | losses to understand (curriculum) |
| 73 | 4154-4183 | LONGER-TERM PRODUCT ROADMAP |  | longer-term product roadmap |
| 74 | 4184-4200 | FUTURE SENSOR RESEARCH |  | future sensor research |
| 87 | 4783-4818 | THE ENCODER IDEA — FIRST PRINCIPLE |  | learned encoder first principles; deferred (T7-C20) |
| 90 | 4895-4949 | LEARNED INGREDIENT ENCODER — THE RESEARCH VERSION |  | learned ingredient encoder; deferred (T7-C20) |
| 91 | 4950-4979 | HOW TO TRAIN THE ENCODER WITHOUT LOSING THE CLASSICAL BASELINE |  | encoder training protocol; deferred (T7-C20) |
| 92 | 4980-5051 | ENCODER TRAINING OBJECTIVES |  | encoder training objectives; deferred (T7-C20, T7-C21) |
| 94 | 5088-5163 | FOOD-AS-MEDICINE / AYURVEDA — KEEP AS A THIRD FUTURE TRACK |  | food-as-medicine / Ayurveda: third future track |
| 136 | 8679-8692 | RESEARCH REPORT INDEX |  | research report index (R1-R5); no obligation |
| 146 | 9025-9054 | LEARNED ENCODERS, PRIOR ART AND DATA JOINS |  | learned encoders, prior art and data joins; deferred (T7-C20) |
| 157 | 9429-9520 | MIDSEM SOURCE SET, PROVENANCE RULE AND CONSENSUS POLICY |  | midsem source set and consensus policy (course material) |
| 165 | 10182-10227 | PERSONALIZED NUTRITION, HEALTH AND SUSTAINABILITY — BOUNDARY CONDITION |  | personalised nutrition/health boundary conditions; boundary only |
| 166 | 10228-10324 | OPEN RESEARCH QUESTIONS IMPORTED FROM THE MIDSEM PAPERS |  | open questions imported from midsem papers |
| 177 | 10964-11060 | LEVEL 12.2 — DEPENDENCIES, PHASED EXECUTION, COMPUTE, RISKS, AND FIRST |  | Level 12.2 execution, compute, risks; Level 12 empirical track deferred (T7-C20) |
| 200 | 16274-16509 | LEVEL 14.3 — PROCESS-CONDITIONED STATE ENCODERS |  | Level 14.3 learned state encoders; deferred (T4-C24) |
| 257L | 35075-42159 | RESEARCH-QUESTION EXECUTION FLOW — DECISION-MAKING PROCEDURE FOR ALL R |  | RQ16 execution flow, 7,000 lines of per-RQ procedures; the 25 Nov scope is D1-D5 (board); RQ decision register stays with T9-C31 |
| 263 | 43318-43394 | NOTATION SPECIFICATION — CULTURAL / HISTORICAL TIME |  | notation for cultural/historical time; Level 13E, nullable metadata only (T7-C24) |

### SUPERSEDED (21)

| § | lines | title | superseded by | reason |
|---|---|---|---|---|
| 17 | 1455-1660 | FLAVORTWIN — CORE SEARCH PROBLEM | §246 | v3.3 FlavorTwin search text; replaced by the FlavorTwin V2 boundary (§246); boundary statement owned by T7-C27-R1 |
| 18 | 1661-1709 | FLAVORTWIN — COMBINATION SEARCH | §246 | as 17 |
| 54 | 3204-3531 | 16-WEEK MASTER ROADMAP | finish plan 2026-11-07 / S178 board | 16-week roadmap; timeline is now handoff/FINISH_PLAN_2026-11-07.md and the board (T9-C26) |
| 55 | 3532-3629 | NEXT WEEK — EXACT STARTING PLAN | finish plan 2026-11-07 / S178 board | 'next week' starting plan of August |
| 58 | 3712-3747 | MODEL TRAINING PLAN — BY STAGE | 36-step plan v2 (Steps 29-35) | model training plan by stage |
| 59 | 3748-3767 | WHICH COMPONENTS SHOULD BE FROZEN FIRST? | 36-step plan v2 (Step 15 freezes) | freeze order is now the 15.0 / 15a / 15b structure (T2-C14, T2-C15, T2-C16) |
| 65 | 3916-3943 | FLAVORTWIN PROFILE SCHEMA | §246 | FlavorTwin profile schema; boundary in §246 |
| 97 | 5247-5270 | UPDATED WEEK-1 CHECKPOINT QUESTIONS | 36-step plan v2 | week-1 checkpoint questions of an earlier schedule |
| 115 | 6464-6499 | HOW THIS CHANGES FLAVORTWIN | §246 | how the representation changes FlavorTwin; boundary in §246 |
| 116 | 6500-6525 | HOW THIS CHANGES CULINARYSTATE-RAG | §230-§259 | how the representation changes the RAG; replaced by Part XII |
| 148 | 9077-9095 | NEXT EXECUTION BLOCK — v4.2 | finish plan 2026-11-07 | v4.2 next execution block |
| 149 | 9098-9103 | R1–R5 RECONCILIATION STATUS | §185 / v4.2 closeout | R1-R5 reconciliation status block |
| 150 | 9104-9130 | UNCERTAINTY LEDGER — R1–R5 RECONCILIATION | §185 / v4.2 closeout | R1-R5 uncertainty ledger of the reconciliation |
| 156 | 9421-9426 | LEARNING RETURN POINT | §185 | learning return point |
| 167 | 10325-10353 | MIDSEM-TO-PROJECT WRITE-BACK MATRIX | §185 / later canonicalisations | midsem-to-project write-back matrix |
| 171 | 10436-10485 | RESEARCH QUESTIONS ADDED IN v8 | §276-§278 | v8 research questions; RQ portfolio now in §276-§278 |
| 172 | 10486-10523 | v8 FINAL RETURN POINT — SUPERSEDED BY §185 | §185 | marked in its own title: superseded by §185 |
| 173 | 10524-10583 | LEGACY v7 RETURN POINT — SUPERSEDED BY §172 | §172 | marked in its own title: superseded by §172 |
| 207 | 17783-17931 | v11 HISTORICAL RETURN POINT — SUPERSEDED BY §218 | §218 | marked in its own title: superseded by §218 |
| 218 | 23100-23316 | v12 HISTORICAL RETURN POINT — SUPERSEDED BY §229 | §229 | marked in its own title: superseded by §229 |
| 257K | 35014-35074 | IMPLEMENTATION SEQUENCING CHECKLIST FOR A SEMESTER-SCALE PROJECT | finish plan 2026-11-07 | semester implementation sequencing checklist; replaced by the finish plan and board |

### UNCOVERED (2)

| § | lines | title | - | reason |
|---|---|---|---|---|
| 61 | 3801-3821 | USER CONTEXT SCHEMA |  | USER CONTEXT SCHEMA: code exists (decision/session_state.py) but no ledger component owns a conformance check; not needed for 25 Nov |
| 151 | 9131-9148 | SYMBOL / TERMINOLOGY COLLISION FREEZE |  | symbol/terminology collision freeze: registry/notation_rule_registry_v1.csv exists, no component owns it; low priority for 25 Nov |

## 3. Use in the report

Cite this table as the answer to "which SSOT sections did the project not touch, and why": 59 are covered by an existing item, 40 are outside the 25 Nov scope (multimodal, learned encoders, health and product tracks, per-RQ execution procedures), 21 are superseded or are historical return points, and 2 are low-priority orphans. §257P rows go to T9-C26 as pass/fail lines; the four merge registers (§184, §195, §206, §217) plus §258 are covered by the T0-C01-R2 delta table (`reports/s178/ssot_v15_status_block_vs_repo.md`).

Limits: anchors are parsed from the ledger's `ssot_anchor` text, which mixes notations; a section anchored only by a plan-step or SVAR id would show here as unanchored. The method was fixed before looking at the result, and the result was not tuned to reach 87.
