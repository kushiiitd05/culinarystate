# State-awareness readiness audit v1 (S100, 2026-10-19)

Scope: the current end-to-end path raw recipe → … → ANSWER/ASK/COMPARE/DIAGNOSE/RECOVER/RECOMMEND/ABSTAIN. Read before auditing: CLAUDE.md,
STATUS.md, DONE_FROM_SSOT.md, WORKLOG through S099, SSOT §247.1/§257E.1/§245.14/§279 (the current return point says implementation and
empirical gates now dominate; the core CulinaryState-RAG substrate is thread 1), Master Plan DEL-3/4/5, AL3/AL4, AN (state contract), AI9 (B0–B7).
Nothing was ingested, no sweep launched, no A100 job attempted, no schema changed.

## 1. Headline findings
1. **B4 did not exist as a runnable rung.** `Query` carries `state/time_min/temperature_c/medium/basis` and the compatibility layer scores them, but
   `answer()` only passed ingredient/process/target; the session fed nothing except `process_history` for the diagnosis verifier. "State-conditioned
   retrieval" (Plan: B4 = B3 + reconstructed state) was therefore NOT_STARTED, and H_STATE could not be tested. S100 adds the minimum:
   `decision/state_conditioning.py` + `answer(use_state=False|True)` (B3|B4) + `ask.py --use-state`. Only ingredient and process are filled from
   state; `Query.state/time/temperature/medium` stay unpopulated (listed as the next B4 extension, not needed for the first test).
2. **There is no test set for H_STATE.** The 20 ladder questions are AI-authored single-turn questions with no session context; the 30 sessions have
   expected *state* but no *queries* and no gold evidence labels.
3. **Sessions test the engine, not extraction.** In all 30 sessions the events are hand-authored in the JSON (AI_DRAFTED, 0 human-reviewed). They verify
   replay semantics (237 checks), not text → events.
4. **Text → events has n=3 human-annotated examples, and they are not independent of the compiler.** GOLD-EX-001/002/003 (Kush, single annotator, handbook
   examples) double as the rule compiler's development fixtures (`tests/unit/test_rule_compiler.py` asserts on two of them). Measured today
   (`aligned_state_scores`): state-field accuracy 0.43 / 0.00 / 0.40 (7/3/5 fields); alive-entity F1 1.0 / 0.0 / 1.0; merge-split F1 1.0 / 0.35 / 1.0.
   This is a dev-contaminated sanity check, not validation; the one pasta example shows the compiler can fail badly.
5. **Runtime coreference across turns (C2) is not implemented.** Entity alignment exists only inside the scorer (`align_entities`, order/Jaccard).
6. **Housekeeping:** EXP-000005 and EXP-000006 cards exist on disk but are not EXP ledger records (ledger has 1–4; the minter's next ID is EXP-000005).
   EXP-000007 is created as a card only; register all three in one ledger step to avoid burning IDs.

## 2. Stage audit
Ground-truth labels: HUMAN_GOLD / SILVER / AI_DRAFT / RULE / UNKNOWN. "Can invalidate" = a failure here can void the claim that explicit state helps.

| # | Stage | Artifact | Input → output | Truth source | Existing metric | Missing evaluation | Upstream | Can invalidate |
|---|---|---|---|---|---|---|---|---|
| 1 | Semantic extraction | `ner/pipeline.py`, `encoder_tagger.py`, `rule_ner.py` | ingredient line/sentence → typed spans | HUMAN_GOLD (TASTEset, third-party) for ingredient lines; none for instruction text | test exact F1 rules 0.774 → large+CRF 0.933 (5 seeds); GLiNER 0.232/0.643 | instruction-side spans on our recipes; RecipeDB3 matched runs (A100) | — | Yes (via 4) |
| 2 | Ingredient linking | `vocab/line_link.py` (LineLinker) | phrase → ING id | RULE lexicon; SILVER surface eval | alias leave-one-out Acc@1 0.607 (bi-encoder) vs 0.555; 97.7% Wikibooks lines linked | mention-in-context linking gold; NIL gold | 1 | Yes (wrong ING = wrong evidence cell) |
| 3 | Quantity / state attributes | `quantity/*`, prep-form KGE | line → symbolic qty, forms | RULE; property + 1.7k fuzz tests | 78.7% NUMBER-parse of 116,997 BBC lines; no-invented-grams property | gold quantity/portion labels; attribute (state) accuracy | 1 | Partly (state fields) |
| 4 | Event extraction | `state_graph/rule_compiler.py` | ingredient lines + steps → Add/Transform/Merge/Split/Reserve… | 3 HUMAN_GOLD examples (single annotator, dev-contaminated) | state-field acc 0.43/0.00/0.40; merge-split F1 1.0/0.35/1.0 | 40 double-annotated Gold recipes; per-event-type PRF | 1–3 | **Yes** |
| 5 | Coreference / intermediates | engine derived entities; `scoring.align_entities` | "the mixture", "the sauce" → entity | RULE | roux alignment in 1 example | runtime cross-turn coref (C2) not built; no gold | 4 | **Yes** |
| 6 | Merge/split/reserve/recombine | `state_graph/engine.py`, `symqty.py` | events → entity graph, symbolic qty | AI_DRAFT sessions (hand-authored events) + 3 gold | 30/30 sessions pass (237 checks); no invented grams | human review of sessions; gold merge/split F1 at n≥40 | 4 | **Yes** |
| 7 | Replay / final state | `engine.replay`, `scoring/state_metrics.py` | events → current graph | RULE (determinism) | deterministic replay True; contract test; replay_consistency | correctness vs human gold state | 6 | Yes |
| 8 | Session observation override | `Observe`, `session_state.py` | user observation → field belief (OBSERVED outranks PLANNED, audit kept) | AI_DRAFT (SES-003/011/019 + 1) | 4 override sessions pass | human review; downstream effect on answers | 7 | **Yes** |
| 9 | State-conditioned retrieval | `state_conditioning.py` (NEW S100) → `answer(use_state)` | empty slots + retrieval text filled from state | none | smoke n=1 only: question "how much vitamin C is left?" after a boiled-broccoli session gives B3 ASK, B4 ANSWER with the same cited row as the fully explicit question (1 of 3 rows) | the H_STATE experiment | 4–8, 2 | **Yes — it is the claim** |
| 10 | Evidence compatibility | `retrieval/compatibility.py`, `retriever.py` | Query + EVD → 9-axis vector, class | SILVER (typed hard negatives) | RQ16-03 pilot: structured AUROC 0.995 (oracle) / 0.975 (predicted slots) vs CE-large 0.924 | human-labelled relevance pairs; free-text questions | 2, 9 | Yes |
| 11 | Calibrated abstention | `calibration.py`, `confidence.py`, `ood.py`, `policy.py` | packet → mode/precision cap | RULE; no labels | metrics implemented; OOD gate | verified labels; risk–coverage on human-labelled set | 10 | Yes (UCR) |
| 12 | Decision / diagnosis / recovery | `policy.py`, `diagnosis.py`, `comparator.py`, `candidates.py`, `selector.py` | packet + slots → ANSWER/ASK/COMPARE/DIAGNOSE/RECOVER/RECOMMEND/ABSTAIN | RULE; AI_DRAFT ladder (20 Qs) | template verbaliser 0 unsupported/0 violations on 20 Qs; diagnosis ≥2-source proposer | gold failure cases; benchmark ≥80 (D-008) | 9–11 | Yes |

## 3. STATE-AWARE CLAIM GATE
| # | Component | Class | Evidence / blocker |
|---|---|---|---|
| 1 | Semantic extraction | PARTIALLY_VALIDATED | ingredient-line NER measured on HUMAN_GOLD (TASTEset, 5 seeds); instruction-side not; RecipeDB3 reproduction BLOCKED_EXTERNAL (VPN) |
| 2 | Ingredient linking | IMPLEMENTED_NOT_HUMAN_VALIDATED | silver surface eval only |
| 3 | Quantity / state attributes | PARTIALLY_VALIDATED | grammar coverage + property/fuzz tests; no gold |
| 4 | Event extraction | PARTIALLY_VALIDATED (weak) | n=3 single-annotator, dev-contaminated; field acc 0.0–0.43; 40-recipe Gold BLOCKED_HUMAN |
| 5 | Coreference / intermediates | NOT_STARTED (runtime coref); intermediates IMPLEMENTED_NOT_HUMAN_VALIDATED | only the scorer aligns entities |
| 6 | Merge/split/reserve/recombine | IMPLEMENTED_NOT_HUMAN_VALIDATED | 30 AI_DRAFT sessions; human review BLOCKED_HUMAN |
| 7 | Replay / final-state reconstruction | VERIFIED (determinism and consistency only) | correctness vs human state not established |
| 8 | Session observation override | IMPLEMENTED_NOT_HUMAN_VALIDATED | 4 AI_DRAFT sessions |
| 9 | State-conditioned retrieval | IMPLEMENTED_NOT_HUMAN_VALIDATED (new, S100; was NOT_STARTED) | no test set; smoke n=1 |
| 10 | Evidence compatibility | PARTIALLY_VALIDATED | silver pilot positive; headline needs human pairs |
| 11 | Calibrated abstention | BLOCKED_HUMAN | no verified labels |
| 12 | Decision / diagnosis / recovery | IMPLEMENTED_NOT_HUMAN_VALIDATED | rule policy; AI-authored dev set |
| — | Transition fallback (off the chain) | FAILED/NEGATIVE | gains vanish cold (DEL-2); not routed |

**Verdict:** the claim "explicit reconstructed state improves retrieval and decisions" is **untested**. Rows 4–9 are the exposed chain and none is human-validated
beyond n=3. Not claimable now: any statement that the system is "state-aware" in the SSOT sense (RQ16-01) beyond "a replayable event-sourced state engine exists
and a B4 switch is wired".

## 4. Smallest human-Gold experiment for H_STATE
See `experiments/EXP-000007/card.md` (pre-registered, not run). Summary:
- **Human inputs (minimum):** (a) 20 Gold recipes (the `pilot_20` batch; gold events by two annotators, adjudicated), (b) 60 state-dependent questions
  authored by a human — 3 cut points per recipe, each omitting the ingredient and/or process that the gold state supplies, (c) per question the gold evidence
  cell (ING, PROC, target) or UNSUPPORTED and the gold mode, (d) blind relevance judgments on the pooled top-5 of B3, B4, B4-oracle, (e) 20 fully
  specified control questions (state should not matter). Double annotation of (c)/(d) on 20 questions for κ.
- **Systems:** B3 (`use_state=False`), B4-predicted (rule-compiler events replayed), B4-oracle (gold events replayed).
- **Primary metric:** ConditionCompatible@5 (paired), plus ModeF1 and UCR. **Mechanism metric:** slot accuracy (ingredient, process) after conditioning.
- **Power:** n=60 paired state-dependent queries gives ~80% power for Δ≈0.20 in CC@5 (paired SD≈0.45); it cannot resolve Δ≈0.10.
- **Failure criteria and decision rules:** in the card.

## 5. Minimum new code in S100
`src/culinarystate/decision/state_conditioning.py` (≈45 lines), `answer(use_state=…)` and `state_trace` in the result, `ask.py --use-state`,
4 unit tests (`tests/unit/test_state_conditioning.py`). Default behaviour is unchanged (B3). Suite: 2,951 passed, 40 deselected.
