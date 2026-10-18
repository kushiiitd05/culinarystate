# BUILD TRACKER — every SSOT build unit, one by one (2026-10-18, after S056)

Source of truth: SSOT v15 §247 (RQ16-01…30), §245 (E16-A…L), §257B (C1…C18), Epic A…M, gates G16-*; plan Part T
(DEL-1…5). Status: ✅ done (v1, tested) · 🟡 partial · ⬜ todo · ⛔ blocked (reason) · ➖ after the course contract
(not in DEL-1…5; in the plan §A2 end-state, and the final execution prompt orders it last: "… → Decision System →
Later Scale/FlavorTwin", "do not spend capacity on FlavorTwin implementation").
Compute policy (final prompt + Kush 2026-10-18): better models on A100 are allowed, but no exhaustive sweeps — bounded
protocols (NER: 3 encoders × 5 seeds; larger only if base beats the floor; embeddings: a few model-card models).
Policy per unit: build → run → analyse vs strongest simpler
baseline → keep only if it earns its place (§257B promotion rule) → log WORKLOG step → next.

## Runtime modules (§257B)
| # | Module | Status | Evidence / gap |
|---|---|---|---|
| C1 | Query/intent parser | 🟡 | `decision/relevance.intent`, `decision/pipeline.parse_query` (rules); no learned parser, no eval set |
| C2 | Entity/coreference resolver | 🟡 | `LineLinker` (lexicon+aliases), gold coref tooling; no runtime coref across turns |
| C3 | State reconstructor | ✅ | `state_graph/engine.py`, `rule_compiler.py`; 30 sessions pass |
| C4 | Process-history tracker | 🟡 | engine `last_process` + TRANSFORMS_INTO edges; no history-conditioned features yet |
| C5 | Goal/constraint parser | ⬜ | constraints only structured (`Constraints`); no text → tools/time/allergen parsing |
| C6 | Multi-index retriever | 🟡 | BM25 + dense (bge/e5/gte) + structured + RRF; R4 graph expansion ⬜; R5 cross-encoder running |
| C7 | Evidence compatibility layer | ✅ | `retrieval/compatibility.py` (9 axes, UNKNOWN neutral, group-row NEAR) |
| C8 | Direct transition lookup | ✅ | retriever DIRECT class + cell dedup |
| C9 | Transition fallback | 🟡 | DEL-2 D0–D7 exist; not routed (G16-TRANS not passed: gains vanish cold) |
| C10 | Candidate action generator | 🟡 | corpus candidates (ING_PROCESSED_BY heat processes); no rules/LLM proposer |
| C11 | Feasibility filter | ✅ | `decision/feasibility.py` (allergen table awaits human sign-off) |
| C12 | Outcome comparator | 🟡 | COMPARE gives per-option evidence; no value-level comparison/intervals |
| C13 | Relevance gate | ✅ | rules pass SSOT §7 examples; held-out eval needs benchmark (D-008) |
| C14 | Uncertainty/OOD gate | 🟡 | confidence vector has `ood` slot, not computed |
| C15 | Multi-objective selector | 🟡 | alternatives without hidden weights; no Pareto front |
| C16 | Grounded response generator | ⬜ | needs LLM (A100) constrained by packet + precision cap |
| C17 | Citation/provenance layer | 🟡 | packet `citation_map`, SRC/SNAP ledgers; no claim→citation check |
| C18 | Session-state updater | 🟡 | engine Observe/Predict precedence; sessions runner; not wired to `ask` |

## Research questions (§247) — protocol §257E
| RQ | Topic | Status | Evidence / gap |
|---|---|---|---|
| 01 | Semantic state value | ⬜ | needs B3 vs B4 ladder on benchmark |
| 02 | Structured retrieval | 🟡 | silver: structured MRR 0.856 vs hybrid 0.704 vs BM25 0.597 (`reports/del4/`) |
| 03 | Compatibility reranker vs cross-encoder | 🟡 | R5 cross-encoder baseline running; scientific hard negatives ⬜ |
| 04 | Context restructuring | ⬜ | packet fields exist; generator needed |
| 05 | Confidence vector | ✅ | `decision/confidence.py`; calibration needs verified labels |
| 06 | Evidence sufficiency policy | ✅ | §242.6–8 modes + precision cap |
| 07 | Quantity ontology | 🟡 | quantity grammar (90% lines), symbolic qty; POR evidence partial |
| 08 | Canonical vocabulary | 🟡 | ING ~2k, PROC 156, TOOL 116 + FoodOn/OFF/Wikidata crosswalks |
| 09 | Silver utility | ⬜ | Silver factory scaffold not built |
| 10 | Active learning | ⬜ | |
| 11 | Claude multi-pass | ⛔ | Silver factory + human approval of cost (H-gate) |
| 12 | Deterministic validators | 🟡 | ledger schema+rules validators; Silver validators ⬜ |
| 13 | Duplicate leakage | 🟡 | near-dup families (BBC/Gutenberg); NER split leakage check ⬜ |
| 14 | State memory | 🟡 | engine; ablation ⬜ |
| 15 | Direct observation override | ✅ | engine: observation outranks prediction (audit kept); sessions SES-003/011 |
| 16 | Feasibility filter | ✅ | C11 |
| 17 | VOI clarification | ⬜ | policy asks on missing critical slot only |
| 18 | Diagnosis verifier | ⬜ | proposer/verifier separation not built |
| 19 | Recovery separation | 🟡 | policy keeps cause ≠ recovery evidence; recovery KB ⬜ |
| 20 | Transition fallback | 🟡 | DEL-2 negative result (cold) — report as such |
| 21 | Completion visibility | ⬜ | |
| 22 | Conflict handling | 🟡 | CONFLICT class + report; lineage-aware resolution ⬜ |
| 23 | Quantity encoder downstream | ⬜ | |
| 24 | Recipe graph downstream | ⬜ | |
| 25 | FlavorTwin process conditioning | ➖ | after DEL-5 (plan §A2 end-state) |
| 26 | FlavorTwin recipe context | ➖ | after DEL-5 (plan §A2 end-state) |
| 27 | Human sensory boundary | ➖ | after DEL-5 (plan §A2 end-state) |
| 28 | Source/domain generalization | 🟡 | cross-source USDA/Bognár/FDC agreement |
| 29 | Long-tail equity | ⬜ | frequency-bucket reports ⬜ |
| 30 | System contribution | ⬜ | B0–B5 ladder + ablations (DEL-5) |

## Experiment families (§245) and gates
| ID | Family | Status | Evidence / gap |
|---|---|---|---|
| E16-A | Semantic parsing (NER) | 🟡 | TASTEset rule floor 0.774 (test); encoder sweep ready (A100, VPN) |
| E16-B | Quantity | 🟡 | `reports/quantity_coverage_v0.md` |
| E16-C | Vocabulary/cold-start | 🟡 | coverage curves; cold-start eval ⬜ |
| E16-D | Recipe graph | 🟡 | 30 AI-drafted sessions; Gold ⛔ humans |
| E16-E | Evidence retrieval | 🟡 | silver comparison v1; benchmark ⛔ D-008 |
| E16-F | Evidence packet / grounded generation | ⬜ | C16 |
| E16-G | Confidence/abstention | 🟡 | metrics ready; verified labels ⛔ humans |
| E16-H | Decision policy | 🟡 | rule policy + demo; benchmark ⛔ |
| E16-I | Diagnosis/recovery | ⬜ | |
| E16-J | Transition integration | 🟡 | DEL-2 cards EXP-000001…4 |
| E16-K | FlavorTwin | ➖ | |
| E16-L | Full system | ⬜ | B0–B5 ladder |
| Gates | G16-DATA/VOCAB/QTY/SEM/GRAPH/EVID/CONFLICT/CAL/TRANS/DEC/REC/PROV/OOD | ⬜ | to be scored when the matching E16 runs exist |

## Order from here (one at a time)
1. RQ16-02/03 retrieval: large embeddings + R5 cross-encoder (running locally) → analyse.
2. E16-A NER: encoder sweep on A100 (needs VPN) → large encoders if base beats floor.
3. C14 OOD gate → C5 goal/constraint parser → C12 outcome comparator (value intervals).
4. RQ16-17 VOI ask policy → RQ16-18/19 diagnosis verifier + recovery KB.
5. C16 grounded generator + B0–B5 ladder on A100 (open LLM), E16-F/L.
6. After DEL-5: FlavorTwin (RQ16-25/26, E16-K, SSOT §246 boundary), sensory study (RQ16-27), deployment.
7. Human-gated throughout: 40 verified rows, Gold, benchmark (D-008), session review.
