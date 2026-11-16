# Final pipeline specification (canonical)

**`AI_DRAFTED` · `NOT_HUMAN_REVIEWED` · 17 Nov 2026.** Describes code that exists; introduces no new
architecture. Component labels (BUILT / PARTIAL / PLANNED_ONLY) are in
`docs/final/FINAL_COMPONENT_INVENTORY.md`; diagrams in `docs/final/FINAL_ARCHITECTURE.mmd`.

```
Recipe / Query → Semantic Recipe Compiler → ambiguity trigger → (optional) LLM structured proposal
 → Typed Event IR → invariant validator → event-sourced state S_t=(G,C,Q,Y,P)
 → query-specific evidence compiler → candidate retrieval → compatibility → route
 → Claim Packet → verbalizer → claim verifier → grounded answer OR abstention
```

Every scientific decision is deterministic; the LLM proposes and phrases and is never an authority
(`handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md` §5). Source keys: `[IR]` `docs/EVENT_IR_CONTRACT.md` ·
`[SI]` `reports/s179/state_inventory_FINAL_2026-11-15.md` · `[S7]` `reports/s180/step7_FINAL_COMPARISON_2026-11-16.md` ·
`[D]` `DECISIONS.md` · `[ST]` `STATUS.md` · `[BT]` `docs/BUILD_TRACKER.md` · `[NER]` `reports/ner/culinaryner_kf_final_report.md` ·
`[CM]` `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md`. Paths abbreviated `…/` = `src/culinarystate/`.

---

## 1. Semantic Recipe Compiler (Rung A)

- **Purpose:** turn recipe text into events, entities (lots) and allocations.
- **Inputs:** raw recipe text (`SourceText.from_raw`), quantity schema, ING/PROC ledgers.
- **Internal flow:** line/step segmentation → ingredient linking → quantity parse → process recognition → binding of consumes/produces → lineage vNext rules (A guard `to/over/into`, B fat stays, C mixture coref, D alternatives).
- **Decision logic:** rules only. `RungA(coord_food_guard=True, lineage_vnext=True)` is the configuration for State v2 `[D] D-134`.
- **Outputs:** an `EventGraph` plus diagnostic flags (`VNEXT_MIXTURE_COREF`, `VNEXT_FAT_STAYS`, `VNEXT_ALTERNATIVE_SKIPPED`, `AMBIGUOUS_*`, `UNRESOLVED_LOT`).
- **Provenance:** every `ValueClaim` carries `origin` / `status` / `claim_route` and a span `[IR §3]`.
- **Failure modes:** wrong antecedent; first-named alternative bound by heuristic `[IR §4]`; unlinked ingredient → `MEMBER_UNLINKED` downstream.
- **Evaluation:** vNext differential only — 29.3% of recipes changed, **DIAGNOSTIC**, no gold regression set; 0 exceptions raised over 611,902 recipes (not "no recipe parsed wrongly") `[D] D-134`. NER component separately: TIE on clean grouped split `[NER]`.
- **Artifact:** `…/extraction/rung_a.py`, `rung_a_binding.py`, `rung_a_rules.py`, `rung_a_lexicon.py`, `rung_a_measure.py`; `reports/s179/lineage_vnext_diff_full_2026-11-14.json`.
- **What is novel:** nothing claimed for the parser itself.
- **What is not novel:** rule-based recipe parsing; recipe flow graphs (prior art exists).
- **Next component:** ambiguity trigger.

## 2. Ambiguity trigger

- **Purpose:** decide whether any LLM call is licensed.
- **Inputs:** compiler flags + lot accounting (`triggers_for`).
- **Internal flow:** map fired flags to licensed fields.
- **Decision logic:** only `VNEXT_ALTERNATIVE_SKIPPED` licenses a field. `VNEXT_FAT_STAYS`, `VNEXT_MIXTURE_COREF`, `AMBIGUOUS_ACTION/ANTECEDENT/CANDIDATES/OR_MISSING/REFERENCE`, `UNRESOLVED_LOT` license **nothing**: detected, recorded UNKNOWN, rules-only `[D] D-135`.
- **Outputs:** list of fired triggers (possibly empty → skip step 3).
- **Provenance:** flag names recorded on the graph diagnostics.
- **Failure modes:** an ambiguity with no flag is invisible; recall unmeasured `[S7 §5]`.
- **Evaluation:** 18 of the 60 sealed cases carried a licensed trigger `[ST]`.
- **Artifact:** `…/composition/layer1_proposer.py` (`triggers_for`).
- **What is novel:** licensing an LLM per trigger rather than per document (system contribution).
- **What is not novel:** flagging.
- **Next component:** LLM proposal (if fired) or Typed Event IR directly.

## 3. Optional LLM structured proposal (Layer-1) — `alternative_group` only (D-135)

- **Purpose:** name a mutually exclusive choice the rules skipped.
- **Inputs:** raw text, `EventGraph`, fired triggers.
- **Internal flow:** prompt v3 asks for the licensing **quote**; the runner locates it in code → `Proposal` → `review` gate → `apply` → back through V4.
- **Decision logic:** refuse any field outside the proposable set (`condition_profile_id` → `FIELD_REQUIRES_EXISTING_REFERENT`); `span_grounds_value`: span must contain a standalone `or`/`either` on word boundaries and not `or until|till|when|so` → else `SPAN_DOES_NOT_GROUND_VALUE` `[D] D-137`. Allocations are never proposable. The proposer never writes state directly `[IR §6]`.
- **Outputs:** accepted proposals setting `alternative_group` on events; everything else rejected with a code.
- **Provenance:** `claim_route` records model origin; span/quote stored.
- **Failure modes (observed):** gloss read as a choice (`channa_or_choley`); endpoint construction escaping the filter (`microwave_duration`); same group minted on several events `[S7 §3]`; one prompt clause flips the 7B to returning nothing `[S7 §2]`.
- **Evaluation:** sealed 60 cases. 72B v3: 63 returned, 21 accepted, 21 grounded; v1 arms grounded 0 `[S7 §1]`. **DIAGNOSTIC_ONLY, NOT_GOLD — no accuracy claim.** 59 cases in one pass + 1 repaired call `[S7 §5]`.
- **Artifact:** `…/composition/layer1_proposer.py`; `reports/s180/step7_arm_L72b_v3prompt_2026-11-15.json`.
- **What is novel:** nothing claimed beyond the gating design; the finding is that grounding was a protocol defect, not a model-scale effect `[S7 §2]`.
- **What is not novel:** LLM structured extraction.
- **Runtime note:** offline/batch only. It is **not** on the demo request path (`deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md` §1).
- **Next component:** Typed Event IR.

## 4. Typed Event IR

- **Purpose:** the single contract between producers and the state engine.
- **Inputs:** rule output and accepted proposals.
- **Internal flow:** frozen dataclasses `EventCandidate`, `EntityCandidate`, `AllocationCandidate`, `EventGraph`.
- **Decision logic:** none (a type). Ids are local and never minted by a producer.
- **Outputs:** `EventGraph(source_text_id, raw_sha256, events, entities, allocations, lot_accounting, provenance, failure, diagnostics)`.
- **Provenance:** CR-02 triple on every `ValueClaim` `[IR §3]`.
- **Failure modes:** `condition_profile_id` is a reference with no referent/consumer `[D] D-135`.
- **Evaluation:** 12 tests for the 15 Nov fields; 160 existing tests unchanged `[IR §2, §7]`.
- **Artifact:** `…/extraction/interfaces.py`.
- **What is novel:** one contract held equally by parser rules and LLM proposals (system contribution).
- **What is not novel:** event/entity graphs for recipes.
- **Next component:** invariant validator.

## 5. Invariant validator (V1–V4)

- **Purpose:** report violations; never repair.
- **Inputs:** `EventGraph`, raw bytes, vocab registries `registry/recipe_semantics/*_registry_v1_DRAFT.csv`.
- **Internal flow:** V1 span round-trip → V2 quantity records → V3 vocabulary → V4 Step-18 invariants.
- **Decision logic (six freeze invariants `[IR §4]`):** lineage conservation · UNKNOWN ≠ zero · no unsupported numerics (enforced in `auditor`) · alternatives are not conjunctions (`ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION`) · every value carries basis/provenance · evidence-context UNKNOWN ≠ MATCH (enforced in `retrieval/compatibility.py`).
- **Outputs:** issue list + explicitly reported open scopes.
- **Provenance:** `VALIDATOR_ID = "V4_STEP18_INVARIANTS"`.
- **Failure modes / open:** `STATE_REPLAY_FROM_EVENT_HISTORY`, `INFERRED_EVENTS_NOT_IN_EXPLICIT_ONLY_QUERIES`, `MASS_BALANCE_SCOPE`, `INVENTED_GRAMS_SEE_AUDITOR`, `SPAN_ROUNDTRIP_SEE_V1` are **not checked by V4** `[IR §5]`. Module status `DRAFT_PENDING_16c`.
- **Evaluation:** unit tests only.
- **Artifact:** `…/extraction/validators.py`, `invariants.py`, `auditor.py`.
- **What is novel:** system contribution (defects in Layer-1 were found because a check failed `[S7 §4]`).
- **What is not novel:** schema validation.
- **Next component:** state engine.

## 6. Event-sourced state `S_t = (G, C, Q, Y, P)`

- **Purpose:** explicit per-(food, step) state.
- **Inputs:** events in text order, lot membership, physics L1 binding, L2 scenario, markers v2, USDA SR composition, EVD ledger, router.
- **Internal flow:** for each event and each non-medium food in the consumed lots: update running history (processes, dose, aqueous/fat minutes, cut integrity, prior salt/acid) → assemble G, C, Q, Y; P is the `b`/`u` on every cell.
- **Decision logic:** `V(value, basis)` or `U(reason)`; "Nothing here estimates a value that no producer gives" (`state_full.py` docstring). Partial sums are labelled `_PARTIAL`.
- **Outputs:** list of state dicts; full field list in `docs/final/FINAL_STATE_SCHEMA.md`.
- **Provenance:** P block = 100% by construction `[SI §3]`.
- **Failure modes:** sparse Q (see fill rates); `lot_acidity_band` always UNKNOWN; mass fractions always UNKNOWN; Y covers two targets only.
- **Evaluation:** corpus fill (612,782 recipes, 0 exceptions, `reports/s179/state_dataset_fill_full_2026-11-14.json`); 30 scripted sessions pass `[BT C3]`; **40-gold-recipe evaluation not performed** `[CM]`.
- **Artifact:** `…/composition/state_full.py`, `state.py`, `context_v12.py`, `…/state_graph/engine.py`.
- **What is novel:** the composition-aware, lot-aware, evidence-linked state representation (the project's contribution is the integration).
- **What is not novel:** each producer taken alone.
- **Next component:** evidence compiler.

## 7. Query-specific evidence compiler

- **Purpose:** choose question-relevant axes **before** retrieval.
- **Inputs:** one state, target, question kind, axis registry.
- **Internal flow:** `load_axes` → `select_axes(target, question_kind)` → per-axis cell (`ph_axis_cell`, `geometry_axis_cell`, router compat) → `compile_evidence`.
- **Decision logic:** an unavailable axis stays UNKNOWN with a stated reason, never dropped. Axis 9 reports `QUERY_ONLY`, never EVALUABLE `[ST]`. pH: no midpoints, no clipping; an interval straddling 4.6 → `INCONCLUSIVE_SPANS_THRESHOLD` `[SI]`.
- **Outputs:** compiled evidence with per-axis status and reason.
- **Provenance:** pH cell carries basis, source sha256, `verify_status` `[D] D-136`.
- **Failure modes:** unverified pH crosswalk; axes 8 and 12 have no producer / no data.
- **Evaluation:** unit tests; no aggregate metric (NOT_EVIDENCED).
- **Artifact:** `…/composition/evidence_compiler.py`, `registry/rag/compatibility_axes_v1.csv`.
- **What is novel:** system contribution.
- **What is not novel:** metadata filtering in retrieval.
- **Next component:** candidate retrieval.

## 8. Candidate retrieval

- **Purpose:** fetch evidence rows that could apply.
- **Inputs:** structured slots (ingredient, process, target) or free text.
- **Internal flow:** structured index (primary) → food-graph expansion → BM25 / dense fallback.
- **Decision logic:** DIRECT class + cell dedup `[BT C8]`.
- **Outputs:** candidate EVD rows.
- **Provenance:** EVD id, source, tier per row.
- **Failure modes:** all rows tier E3, 0 human-verified `[CM]`.
- **Evaluation:** silver only — structured MRR 0.856 vs hybrid 0.704 vs BM25 0.597 `[BT RQ02]`. Condition-compatible Recall@K not reported `[CM]`. State-vector views are DIAGNOSTIC_ONLY `[ST]`.
- **Artifact:** `…/retrieval/retriever.py`, `bm25.py`, `food_graph.py`.
- **What is novel:** nothing claimed. **What is not novel:** BM25, dense retrieval, RRF.
- **Next component:** compatibility.

## 9. Compatibility engine

- **Purpose:** decide whether a row transfers to the query state.
- **Inputs:** query state axes, evidence row axes.
- **Internal flow:** per-axis comparison on 9 axes: matrix, state, process, time, temperature, medium, target, basis, tier `[SI §5]`.
- **Decision logic:** `VALUE = {MATCH 1.0, NEAR 0.5, UNKNOWN 0.25, MISMATCH 0.0}` `[IR §4]`. **Unknown is not a mismatch and is never a match.** Hard exclusion from DIRECT on axes 1 / 3 / 10 / 11 `[SI §5]`.
- **Outputs:** per-axis verdicts.
- **Provenance:** axis table basis `D-122_AXIS_TABLE` on Y cells.
- **Failure modes:** rows lacking a field → UNKNOWN_ROW.
- **Evaluation:** unit tests; risk–coverage / ECE not reported `[CM]`.
- **Artifact:** `…/retrieval/compatibility.py`.
- **What is novel:** UNKNOWN-neutral, never-silent compatibility as part of the integration. **Not novel:** rule tables.
- **Next component:** route.

## 10. Route

- **Purpose:** one routing verdict per (event, ingredient, target).
- **Inputs:** router item, composition context, EVD.
- **Internal flow:** frozen router 0.4.1 → `composition_route` (added salt/acid/lipid → `CONTEXT_MISMATCH`; unstated context → SCENARIO suggestion `[ST]`).
- **Decision logic:** answer / ask / abstain policy `[CM]`.
- **Outputs:** `route`, reasons, applied evidence or near evidence (`FOUND_NOT_APPLIED`).
- **Provenance:** reasons stored as the cell basis.
- **Failure modes:** `NO_ROUTER_ITEM`, `NO_EVIDENCE_ROW`.
- **Evaluation:** H3 RULE_NOT_MET; abstention metrics partial `[CM]`.
- **Artifact:** `…/mechanism/router_demo.py`, `…/composition/router_v12.py`.
- **Novel / not novel:** system contribution / rule routing.
- **Next component:** Claim Packet.

## 11. Claim Packet

- **Purpose:** fix what may be said before any text exists.
- **Inputs:** state, target, question kind (`claim_packet(state, target, question_kind)`).
- **Internal flow:** compile → caveats → unknown reasons → `reported_precision`.
- **Decision logic:** allowed / forbidden claims, required caveats, evidence ids, max precision, UNKNOWN reasons.
- **Outputs:** packet dict.
- **Provenance:** evidence ids.
- **Failure modes:** NOT_EVIDENCED. **Evaluation:** unit tests.
- **Artifact:** `…/composition/claim_packet.py`.
- **Novel / not novel:** system contribution / structured prompts.
- **Next component:** verbalizer.

## 12. Verbalizer

- **Purpose:** phrase the packet.
- **Inputs:** packet. **Internal flow:** deterministic template. **Decision logic:** none.
- **Outputs:** answer text. **Provenance:** citations from the packet.
- **Failure modes:** stiff prose. LLM rephrase exists but is **unpromoted** `[BT C16]` and is not on the demo request path.
- **Evaluation:** template: "0 unsupported / 0 violations" `[BT C16]`.
- **Artifact:** `…/generation/verbalize.py`.
- **Novel / not novel:** none / templating.
- **Next component:** claim verifier.

## 13. Claim verifier → grounded answer or abstention

- **Purpose:** a model cannot widen what may be said.
- **Inputs:** text + packet. **Internal flow:** `claimed_numbers` vs evidence numbers; axis words; states-a-reason check → `VerificationReport`.
- **Decision logic:** any violation → `template_answer(packet)` (`answer_or_template`).
- **Outputs:** grounded answer with citations and UNKNOWNs, or abstention.
- **Provenance:** violations recorded.
- **Failure modes:** lexical instrument; semantic gaps (T0-C06-R2 remains PARTIAL `[ST]`).
- **Evaluation:** unit tests; 346 frozen answers scanned, 30 flagged `[ST]`.
- **Artifact:** `…/composition/claim_verifier.py`.
- **Novel / not novel:** system contribution / post-hoc checks.
- **Next component:** user / UI.
