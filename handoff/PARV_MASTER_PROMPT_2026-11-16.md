# CulinaryState — master handoff for Parv

**Written 16 Nov 2026 by the coding agent, for Parv Goyal.** Freeze 19 Nov · submit 21 Nov ·
present 25–26 Nov. Branch `kush/s179-finish-fixes`, PR #12 open and **not merged**.

Read this before touching anything. It says what exists, what it actually proves, and what is still
owed. The hardest part of this project is not the code — it is that almost nothing is *verified*,
and the report's credibility depends on saying so precisely.

---

## 0. The five laws (from `CLAUDE.md`, non-negotiable)

1. **No invented scientific values.** If a number is not sourced, it does not exist.
2. **UNKNOWN is a valid answer** — and a first-class state, never a zero.
3. **AI review ≠ human verification** (D-085). This one is why D1/D3/D5 are still open.
4. **Raw text preserved**; normalisation is a new column, never an edit.
5. **Ledgers append-only; IDs never reused.**

A sixth, added 15 Nov: **the validator decides, not the model.**

---

## 1. What the system is, in one paragraph

CulinaryState parses recipe text into typed events, replays them into an event-sourced food state
`S_t = (G, C, Q, Y, P)`, compiles the evidence relevant to a specific question, decides what may and
may not be claimed, and only then lets a language model phrase the answer — which is checked again
before it is shown. **Every scientific decision is made by deterministic code. The LLM proposes and
verbalises; it is never an authority.**

---

## 2. Component-by-component: what each does, and what it actually proves

### 2.1 Semantic recipe compiler
Rules + NER + entity linking + quantities + processes → event candidates.
**Real.** Runs corpus-wide: 611,902 recipes, no exceptions raised.
**Honest limit:** NER is not a win. Our frozen model on a clean grouped split is macro 0.9545 —
**no improvement over the baseline, same encoder family.** The interesting finding is that the
standard RecipeDB3 protocol **leaks**: 13.6% masked-family overlap, 5.4% duplicate test rows, and
leaked rows score 0.9937 against 0.9558 clean. **Claim the leak finding, never a SOTA NER claim.**

### 2.2 LLM state proposer (Layer-1)
**Read this carefully — it changed on 15 Nov and the old diagrams are wrong.**
After decision **D-135**, the LLM may propose **exactly one field** (`alternative_group`) on **exactly
one trigger** (`VNEXT_ALTERNATIVE_SKIPPED`). Nothing else. Every other ambiguity is detected, recorded
as UNKNOWN, and left alone.
**Why it shrank:** `condition_profile_id` was a reference field with no referent, so any noun passed
the gate — `pan`, `chicken`, `bowl_content` were all accepted as "condition profiles".
**What it produces:** on the 60 hardest cases in the corpus, **21 grounded proposals** (72B, prompt
v3), of which an AI-delegated review judges 17 well-formed.
**Say it like this:** the LLM's licensed surface is small *because the destinations for the other
answers do not exist yet*, not because the questions are uninteresting.

### 2.3 Typed Event IR + invariant validator
Six invariants: lineage conservation · UNKNOWN ≠ zero · no unsupported numerics · alternatives are
not conjunctions · every value carries a basis · evidence-context UNKNOWN is never a MATCH.
**Real and load-bearing.** Three separate defects this month were caught *because a check failed*,
never because a model behaved well. That sentence is the project's best argument.

### 2.4 Event-sourced state engine — `S_t = (G, C, Q, Y, P)`
- **G** lineage and structure (lot-aware: merges, splits, coreference)
- **C** composition (water/salt/acid/lipid + a broader sparse schema)
- **Q** physical conditions (process, medium, time, temperature, lid, geometry, thermal dose)
- **Y** analyte/evidence state (vitamin C, lycopene)
- **P** provenance — basis, source, status, UNKNOWN reason
**This is the central contribution.** It is broad even when sparse. Do **not** describe
CulinaryState as "the salt/acid/lipid fields" — that is a populated subset, not the definition.

### 2.5 Query-specific evidence compiler
Selects the relevant axes **before** retrieval, from a canonical **13-axis** registry
(`registry/rag/compatibility_axes_v1.csv`). 9 implemented · 2 in the compiler (pH, geometry) · 2
schema-only (a_w has no producer, measurement-method has no data).
An unavailable axis stays **UNKNOWN with a stated reason** and is never dropped.

### 2.6 Compatibility engine
Four-way: MATCH / MISMATCH / UNKNOWN_IN_SOURCE / UNKNOWN_IN_QUERY. **Unknown is not a mismatch** —
this is contract wording from the proposal and it is honoured exactly.

### 2.7 Claim packet + verifier
Allowed claims · forbidden claims · required caveats · evidence ids · maximum permitted precision ·
UNKNOWN reasons. The verbaliser's output is checked against the packet; on failure it falls back to a
deterministic template. **A model cannot widen what may be said.**

---

## 3. Deliverable status — the honest table

Full detail: `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md`.
Contract: `docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf` (it is in the repo).

| | Status | The gap | Who closes it |
|---|---|---|---|
| **D1** evidence ledger | PARTIAL | 17,978 rows ✓ but **0 of the required ≥40 hand-verified literature rows** | **human only** |
| **D2** sparsity + cold splits | PARTIAL | negative results reported ✓; not every prescribed statistic demonstrated | agent |
| **D3** state engine | STRONG CORE | engine ✓, 30 sessions ✓, **40-gold-recipe evaluation not performed** | human + agent |
| **D4** retrieval + abstention | STRONG CORE | policy ✓, **Recall@K / risk–coverage / ECE not all reported** | agent |
| **D5** end-to-end + demo | PARTIAL | 74 questions over 8 types ✓, **chef/peer review not done**, demo is a backend runner | human + agent |

**The three human-only gaps are the whole risk.** No amount of UI work moves them.

---

## 4. Parv — what only you and Kush can do

Ranked by how much each changes what the report may claim.

1. **D1: verify 40 literature rows.** The single clearest contractual gap. Pick 40 raw-vs-cooked or
   kinetics rows, check each against its source, mark tier and verification. Without this D1 reads
   "0 human-verified" to an examiner.
2. **D5: the chef/peer review.** Small and explicitly promised. Even 3–5 reviewed scenarios with
   written comments closes it honestly.
3. **The 35-proposal packet** — `reports/s180/alternatives_verification_2026-11-15/`. AI personas
   have already triaged it; **9 rows are where ksh and prv disagree** and those are the ones worth a
   human verdict. ~20 minutes.
4. **D3 gold:** 40 recipes with expected state fields. Large. If time is short, say in the report
   that it was not done rather than approximating it.
5. **Sign-offs:** D-134…D-137 currently carry AI-delegated approvals plus Kush's concurrence. A
   genuine two-person sign-off is stronger.

---

## 5. The app — contracts first, engine frozen

**The scientific core is frozen. The UI is a consumer of JSON, never a reason to change the engine.**

Four routes only: `/` landing · `/lab` workbench · `/compare` A–D · `/method`.
Build **`/lab` first against precomputed JSON**. Landing page last.

API surface (browser never sees internals):
```
POST /api/analyze   recipe            -> events + states + deltas
POST /api/ask       recipe + question -> evidence + claim packet + answer
POST /api/compare   scenario ids      -> state/evidence diff
GET  /api/health    backend/model/version
```

**Two rules for whoever builds it:**
- **UNKNOWN must be visible.** A UI that shows only confident answers misrepresents the system and an
  examiner will catch it. When tomato comes back `INCONCLUSIVE_SPANS_THRESHOLD`, show the interval,
  the 4.6 threshold and the source. *"It refuses to guess, and tells you what it would need"* is the
  pitch.
- **Ship a precomputed fallback.** If VPN/GPU dies mid-presentation, the examiner still sees the full
  interaction.

**Contract note:** the proposal names an *"8-scenario Streamlit demo"*. A Next.js app is a
substitution — fine, arguably better, but it must be stated once in the report: *"the proposal
specified a Streamlit demo; we built an interactive web application covering the same eight
scenarios."* The eight scenarios already exist in `tools/s179_submission_demo.py`.

---

## 6. Language rules for the report and the deck

**Never write:**
- "SOTA" or "beats state of the art" — we have no such result
- "clean", "validated" or "verified" about lineage vNext — it is **DIAGNOSTIC**, 29.3% of recipes
  changed with **no gold regression set**
- "tomato sauce is acidic" — tomato is **4.3–4.9**, straddling 4.6, so the system says
  `INCONCLUSIVE_SPANS_THRESHOLD`. That refusal is the demo, not a bug
- any accuracy number from the Layer-1 comparison — there is **no gold**

**Do write:**
- "We introduce a large-scale, composition-aware, evidence-grounded cooking-state representation and
  evaluate how explicit state changes scientific-evidence applicability."
- "The standard NER protocol leaks; on a clean grouped split we match the baseline."
- "Every defect was found because a check failed, not because a model behaved well."

---

## 7. Where to start reading

1. `handoff/KUSH_REVIEW_GUIDE_2026-11-15.md` — §5 lists the five claims an examiner will attack, with
   the defence for each
2. `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md` — contract compliance
3. `reports/s180/step7_FINAL_COMPARISON_2026-11-16.md` — the Layer-1 result and its limits
4. `STATUS.md` top section · `DECISIONS.md` D-134…D-137
5. `reports/final/figures_s180_2026-11-16/` — current figures

**Do not modify:** anything under `src/culinarystate/`, the registries, or the frozen result JSONs.
If the engine needs a change, it needs a decision record first.
