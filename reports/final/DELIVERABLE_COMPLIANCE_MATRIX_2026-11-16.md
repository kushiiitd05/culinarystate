# Deliverable compliance matrix — D1…D5 against the submitted proposal

**Contract:** `docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf` (in the repo, 18 Oct 2026). The
master plan states the proposal PDF outranks the operational plans as the course contract, so this
matrix is built from the PDF's own wording, quoted per row.

**Status written 16 Nov 2026 by the coding agent. `AI_DRAFTED` — not a human attestation of
compliance.** Each row gives the contract's own success check, the evidence path, and the gap in the
words a reader could check.

---

## D1 — Process-Effect Evidence Ledger + data card

> *"≥1,000 rows from public retention databases (Phenol-Explorer, USDA) **+ ≥40 hand-verified
> literature rows** (raw-vs-cooked, kinetics) … Check: every row has source + tier; coverage and
> bias report."*

| | |
|---|---|
| **Status** | **PARTIAL** |
| Met | **17,978 ACTIVE rows** (≥1,000 comfortably exceeded), every row carries source and tier; coverage and bias reporting exists in the D1 section |
| **Not met** | **≥40 hand-verified literature rows. The ledger records 0 human-verified rows — all 17,978 are tier E3.** (`reports/h_state/ssot15_state_program_inventory.md`) |
| Evidence | `reports/final/sections/S179_D1_evidence_resource_DRAFT.md`, `reports/h_state/ledger_stats.json` |
| Report wording | "The row-count and provenance requirements are met; the hand-verified literature requirement is not. No row in the ledger has been verified by a human." |

**This is the single clearest contractual gap and it is human-only work.** Forty rows of literature
verification cannot be delegated to an AI under D-085.

---

## D2 — Sparsity-aware completion and cold-split benchmark

> *"pair-holdout, ingredient-disjoint and study-disjoint splits; baselines (persistence,
> process-mean, nearest-evidence, LightGBM) vs biased matrix factorization / factorization machine
> with side information; propensity-weighted evaluation; split-conformal intervals. Check: answers
> H2 with study-level bootstrap CIs, negative results reported."*

| | |
|---|---|
| **Status** | **PARTIAL** |
| Met | Splits, baselines and completion models exist; **negative results are reported**, which the contract explicitly requires |
| Not demonstrated | That every one of propensity weighting, split-conformal intervals and study-level bootstrap CIs was completed to the stated form |
| Evidence | `reports/del2/`, `reports/final/sections/S179_H2_and_lineage_statements_DRAFT.md` |
| Report wording | "H2 is addressed with negative results reported as the contract requires; not every prescribed statistical treatment is demonstrated." |

---

## D3 — State-tracking engine

> *"Typed operations (merge, split, reserve, recombine), belief-state fields with provenance, and
> direct-observation override … Evaluated on **40 gold recipes and 30 scripted sessions**:
> state-field accuracy, replay consistency, merge/split F1."*

| | |
|---|---|
| **Status** | **STRONG CORE, EVALUATION PARTIAL** |
| Met | Engine built and event-sourced; **30 scripted sessions pass** (`docs/BUILD_TRACKER.md` C3); typed operations and provenance fields present; this is the project's central contribution and it exceeds the contract in representation terms (`S_t=(G,C,Q,Y,P)`, lot-aware, 611,902 recipes replayed) |
| **Not met** | **The 40-gold-recipe evaluation.** State-field accuracy, replay consistency and merge/split F1 against a gold set are not demonstrated |
| Evidence | `reports/final/sections/S179_D3_state_tracking_DRAFT.md`, `src/culinarystate/state_graph/engine.py` |
| Report wording | "The engine is built and runs corpus-wide; the 40-gold-recipe scoring prescribed by the contract was not performed, so no state-field accuracy or merge/split F1 is reported." |

---

## D4 — Evidence-aware retrieval with calibrated abstention

> *"condition-compatibility scoring (unknown is not a mismatch); evidence classes … confidence
> vector; answer-ask-abstain policy. Check: condition-compatible Recall@K, risk–coverage,
> unsupported-claim rate, ECE."*

| | |
|---|---|
| **Status** | **STRONG CORE, METRICS PARTIAL** |
| Met | Compatibility layer with UNKNOWN-neutral semantics (contract wording honoured exactly), evidence classes, answer-ask-abstain routing, unsupported-claim enforcement |
| Not demonstrated | The full prescribed metric set — condition-compatible Recall@K, risk–coverage curves and **ECE** — is not all reported |
| Evidence | `src/culinarystate/retrieval/compatibility.py`, `reports/final/sections/S179_D4_retrieval_and_abstention_DRAFT.md` |
| Report wording | "The policy and compatibility machinery are built; calibration is not fully characterised and ECE is not reported." |

---

## D5 — End-to-end CulinaryState-RAG + benchmark + demo

> *"Benchmark of **~80 questions over 8 task types**, baseline ladder B0 … B5; one-at-a-time
> ablations; oracle-upstream tests; **small chef/peer review**; **8-scenario Streamlit demo**."*

| | |
|---|---|
| **Status** | **PARTIAL** |
| Met | **74 questions across 8 task types** (D-090: S1 12, S2 12, P1/P2/P3/C 10 each, U/X 5 each) — the contract says "~80", so 74 is within tolerance but should be stated as 74, not 80. Baseline ladder and ablations exist. **8 authored demo scenarios exist** (`tools/s179_submission_demo.py`) |
| **Not met** | **(a) chef/peer review — not performed.** **(b) The demo is a backend scenario runner, not the "8-scenario Streamlit demo" the contract names.** The file's own docstring says "not a human rehearsal/benchmark". Streamlit is pinned in the environment lock but no Streamlit app exists |
| Evidence | `tools/s179_submission_demo.py`, `reports/del5/`, `reports/final/sections/S179_D4_retrieval_and_abstention_DRAFT.md` |
| Report wording | "The benchmark and ablations exist at n=74 over 8 task types. The chef/peer review was not performed. The demo exists as eight backend scenarios rather than the interactive demo the proposal names." |

---

## Summary

| Deliverable | Status | Blocking gap | Who can close it |
|---|---|---|---|
| D1 | PARTIAL | **0 of ≥40 hand-verified literature rows** | **human only** |
| D2 | PARTIAL | not every prescribed statistical treatment demonstrated | agent, if scoped |
| D3 | STRONG CORE | **40-gold-recipe evaluation not performed** | human (gold) + agent (scoring) |
| D4 | STRONG CORE | Recall@K / risk–coverage / ECE not all reported | agent |
| D5 | PARTIAL | **chef/peer review**; interactive demo | human; agent |

**Three gaps are human-only and none can be closed by building a UI.** A deployed app does not
substitute for hand-verified rows, a gold recipe set, or a chef review.

## Two findings that change the UI plan

1. **The contract names a Streamlit demo.** Building a Next.js/Vercel app instead is a *substitution*
   and must be declared as one. It is defensible — arguably better than what was promised — but if
   the report simply shows a web app without saying so, D5's demo line is not met as written. The
   safest path is to state plainly: "the proposal specified an 8-scenario Streamlit demo; we built an
   interactive web application covering the same eight scenarios."
2. **The proposal says "no GPU required"** (§8 feasibility). The 7B/72B work is beyond the contract's
   scope, not required by it. That is fine, but it should not be presented as a contractual
   deliverable.

## What this matrix is not

`AI_DRAFTED`. It is a reading of the contract against repo evidence, not an attestation that the
project complies. Kush and Parv own the compliance claim. Where a row says "not demonstrated", that
means the evidence was not found by this agent — not that the work definitely was not done.
