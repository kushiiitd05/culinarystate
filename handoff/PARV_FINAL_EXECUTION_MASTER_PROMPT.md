# PARV — FINAL EXECUTION MASTER PROMPT (CulinaryState)

**Self-contained. You should not need to rediscover the project from this document.**
Written 16 Nov 2026. Freeze **19 Nov** · verify **20 Nov** · submit **21 Nov** · present **25–26 Nov**.
Branch `kush/s179-finish-fixes` · PR #12 **open, not merged** · tests 5,977 pass, 0 fail.

---

## 1. Project thesis

> CulinaryState is not an LLM that guesses cooking chemistry. It is a structured, event-sourced
> culinary-state system in which language understanding **proposes** events, the state engine
> **records** what changes, scientific evidence is **retrieved**, compatibility **decides** what
> transfers, UNKNOWN is **preserved**, and the LLM is allowed to explain only what the evidence
> permits.

Public name **CulinaryState** · demo **CulinaryState Explorer** · tagline *"From recipe text to
evidence-grounded cooking state."*

## 2. Authority order

1. `docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf` — **it is in the repo**, it is the D1…D5
   contract, and it outranks every operational plan.
2. SSOT + approved v16 change set → 3. the 36-step spine → 4. `DECISIONS.md` → 5. frozen artifacts →
6. handoff/status → 7. master plans → 8. live instruction from Kush.

## 3. D1…D5 compliance — the honest result

Full matrix: `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md`.

| | Status | Evidenced | **Gap** |
|---|---|---|---|
| **D1** evidence ledger | **PARTIAL** | 17,978 ACTIVE rows (≥1,000 ✓), every row has source + tier | **0 of ≥40 hand-verified literature rows** |
| **D2** sparsity + cold splits | **PARTIAL** | splits, baselines, **negative results reported** ✓ | not every prescribed statistic demonstrated |
| **D3** state engine | **PARTIAL** (strong core) | engine ✓, 30 scripted sessions ✓, corpus-wide replay ✓ | **40-gold-recipe evaluation not performed** |
| **D4** retrieval + abstention | **PARTIAL** (strong core) | compatibility ✓, evidence classes ✓, answer/ask/abstain ✓ | **Recall@K, risk–coverage, ECE not all reported** |
| **D5** end-to-end + demo | **PARTIAL** | 74 questions / 8 task types ✓, ladder ✓, ablations ✓, 8 backend scenarios ✓ | **chef/peer review not done**; demo is a runner, not the named interactive demo |

**No deliverable is PASS. Do not write "completed" for any of them.**

## 4. Remaining gaps, ranked

| # | Gap | Closable by 19 Nov? | Owner |
|---|---|---|---|
| 1 | **D1: 40 hand-verified literature rows** | yes, if started now | **human only** |
| 2 | **D5: chef/peer review** (3–5 reviewed scenarios closes it honestly) | yes | **human only** |
| 3 | **D4: Recall@K / risk–coverage / ECE** | yes | agent |
| 4 | **The 35-proposal packet** — 9 divergent rows need a verdict (~20 min) | yes | **human only** |
| 5 | **D3: 40 gold recipes** | unlikely | human + agent |
| 6 | D2 remaining statistics | partially | agent |

**Items 1, 2, 4 cannot be closed by any amount of UI or report work.**

## 5. The final pipeline

```
Recipe / query → Semantic Recipe Compiler → ambiguity trigger?
   → (yes) LLM structured proposal, span-grounded → Typed Event IR
   → Invariant Validator → Event-sourced CulinaryState  S_t=(G,C,Q,Y,P)
   → Query-specific Evidence Compiler → Candidate Retrieval
   → Compatibility Engine → Route → Claim Packet
   → LLM Verbalizer → Claim Verifier → grounded answer OR abstention
```

Every scientific decision is deterministic. The LLM proposes and phrases; it is never an authority.

## 6. Component flow — what each does and what it proves

**Semantic compiler** (rules + NER + linking + quantities + processes). Runs corpus-wide: 611,902
recipes, no exceptions raised. *Honest limit:* NER is **not** a win — clean grouped split macro
**0.9545**, no improvement over baseline, same encoder family. The real finding is that the standard
RecipeDB3 protocol **leaks**: 13.6% masked-family overlap, 5.4% duplicate test rows, leaked rows
0.9937 vs 0.9558 clean. **Claim the leak, never SOTA NER.**

**LLM proposer (Layer-1).** ⚠️ **Changed 15 Nov; older diagrams are wrong.** Under **D-135** the LLM
may propose **one field** (`alternative_group`) on **one trigger** (`VNEXT_ALTERNATIVE_SKIPPED`).
Nothing else. Everything else is detected, recorded UNKNOWN, left alone. Why: `condition_profile_id`
was a reference field with no referent, so `pan`, `chicken`, `bowl_content` all passed as "condition
profiles". Result on the 60 hardest cases: **21 grounded proposals** (72B, prompt v3), 17 judged
well-formed. Say: *the surface is small because the destinations for the other answers do not exist
yet, not because the questions are uninteresting.*

**Typed Event IR + validator.** Six invariants: lineage conservation · UNKNOWN ≠ zero · no
unsupported numerics · alternatives ≠ conjunctions · every value carries a basis · evidence-context
UNKNOWN is never MATCH. **Three defects were caught this month because a check failed — never
because a model behaved well.** That is the project's best sentence.

**State engine `S_t=(G,C,Q,Y,P)`.** G lineage/structure (lot-aware) · C composition · Q physical
conditions (incl. thermal dose, lid, geometry) · Y analyte/evidence state · P provenance. **Broad
even when sparse. Never describe CulinaryState as "the salt/acid/lipid fields"** — that is a
populated subset, not the definition. Full inventory: `docs/final/FINAL_STATE_SCHEMA.md`.

**Evidence compiler.** Selects relevant axes *before* retrieval from a canonical **13-axis** registry
(`registry/rag/compatibility_axes_v1.csv`): 9 implemented · 2 in compiler (pH, geometry) · 2
schema-only (a_w no producer, measurement-method no data). An unavailable axis stays **UNKNOWN with
a stated reason**, never dropped.

**Compatibility engine.** MATCH / MISMATCH / UNKNOWN_IN_SOURCE / UNKNOWN_IN_QUERY. **Unknown is not
a mismatch** — contract wording, honoured exactly.

**Claim packet + verifier.** allowed / forbidden claims · required caveats · evidence ids · max
precision · UNKNOWN reasons. Verbaliser output is checked against the packet; failure falls back to a
deterministic template. A model cannot widen what may be said.

**pH (axis 7).** FDA/CFSAN 2003, public domain, 479 rows → **140 ING bands**: 31 acidic · 101
low-acid · **8 inconclusive**. No midpoints, no clipping. **Tomato is 4.3–4.9 and straddles 4.6**, so
the system refuses to call it acidic. *That refusal is the demo.* Crosswalk is
`UNVERIFIED_CROSSWALK_AI_DRAFTED`; `C_t` is deliberately **not** wired (D-136).

**Retrieval diagnostic.** 5,181 states, 40 queries, k=10. Chance Jaccard **0.001**; observed
0.0455–0.1164; nothing shared by all three views on 34/40 queries. **DIAGNOSTIC_ONLY — no relevance
gold, so overlap is not precision.**

## 7. Claim / SOTA status

| Component | Status |
|---|---|
| NER | **TIE** on a clean split + **protocol-leak finding** (the stronger result) |
| Linker, retrieval | SYSTEM_CONTRIBUTION_ONLY |
| Recipe flow graphs | prior art exists — **do not claim invention** |
| State representation + evidence compatibility + claim-constrained RAG | **our contribution: the integration** |
| Layer-1 comparison | **DIAGNOSTIC_ONLY** — no gold |
| H1, H3 | **RULE_NOT_MET** — retain |
| Lineage vNext | **DIAGNOSTIC** — 29.3% changed, **no gold regression set** |

**No overall SOTA claim anywhere.**

## 8. Language rules — report, PPT and app

**Never write:** "SOTA" / "beats state of the art" · "clean", "validated" or "verified" about lineage
vNext · "tomato sauce is acidic" · any accuracy number from the Layer-1 comparison · "completed" for
any deliverable.

**Do write:** *"We introduce a large-scale, composition-aware, evidence-grounded cooking-state
representation and evaluate how explicit state changes scientific-evidence applicability."*

## 9. UI product definition

Routes: `/` landing · `/lab` workbench · `/compare` A–D · `/method`. **Four only.**

`/lab`: LEFT recipe/steps · CENTRE event timeline + lot graph + **ΔS animation** · RIGHT tabs (State,
Evidence, Compatibility, Claim Packet, Provenance) · BOTTOM query + grounded answer. Clicking any
step must expose `S_t`, `E_t`, `S_{t+1}`, `ΔS`, evidence, compatibility, route, claim restrictions,
final answer.

**UNKNOWN must be visually first-class.** A UI that shows only confident answers misrepresents the
system and an examiner will catch it.

**Build `/lab` first against precomputed JSON. Landing page last.**

## 10. Required demo flows

1. **Tomato A–D** (A water · B +salt · C +salt+vinegar · D +salt+vinegar+oil) — the UI must show *why*
   state differs. 2. Lineage/coref: "the sauce" continues the prior lot. 3. Alternatives: "A or B"
   must not become A AND B. 4. UNKNOWN: source does not encode a compatibility axis. 5. Claim
   restriction: near evidence exists, numeric transfer forbidden. 6. One legitimate numeric answer
   from compatible cited evidence. 7. **At least one abstention.** 8. The contractual 8 scenarios
   already exist in `tools/s179_submission_demo.py` — consume them, do not invent new ones.

## 11. API contract

```
POST /api/analyze  recipe            -> events, states, deltas, provenance
POST /api/ask      session + question-> intent, axes, evidence, compatibility, route,
                                        claim packet, answer, citations, unknowns
POST /api/compare  scenario ids      -> state/evidence diff
GET  /api/health   -> frontend ver, backend ver, model status, index ver, LIVE|FALLBACK
```
Internal only: `/propose` `/state` `/retrieve` `/compile` `/verbalize` `/verify`.
**The browser never calls Ollama.**

## 12–14. Design system, component libraries, frontend architecture

**Pending — four design research agents were commissioned 16 Nov** covering the design system
(palette, type, semantic state rendering), frontend architecture (component tree, TS interfaces,
ΔS visualisation, React Flow plan), backend/deployment, and motion. Their outputs land in
`design/FINAL_DESIGN_SYSTEM.md`, `design/FINAL_UI_RESEARCH.md`,
`deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md`. **Fixed regardless of their findings:**

- Next.js + TypeScript + Tailwind + shadcn/ui · React Flow (graph) · Motion (transitions only)
- **No full glassmorphism.** Glass only on nav, floating query bar, transient overlays. **Scientific
  panels are solid.**
- WCAG 4.5:1 minimum. **Colour is never the only signal** — every state also carries icon + label.
- Aceternity: at most 1–2 decorative effects, landing/hero only. 21st.dev: inspiration only, audit
  anything copied.
- Avoid: chef-hat logos, stock food photography, neon AI gradients, translucent tables, bento sprawl.

## 15–17. Backend, Ollama, deployment

```
Browser → Vercel (Next.js + BFF API routes) → HTTPS, secret server-side
        → Cloudflare Tunnel → FastAPI gateway on the research server
        → frozen CulinaryState engine + ledgers + Ollama (local model)
```
**Ollama is never exposed to the browser.** One provider abstraction for local Ollama and any hosted
fallback; **a hosted LLM is not scientific authority.** Secrets in environment variables only, never
committed. CORS restricted to the Vercel production origin. Rate-limit demo endpoints. Return a
request id and backend/model version on every response.

Measured footprint for the deterministic path: **src ~10 MB + registries ~13 MB ≈ 25 MB.** The
3.2 GB `data/` directory is build-time only and is never on the request path.

## 18. Fallback mode — hard requirement

Ship **LIVE** and **PRECOMPUTED DEMO**. Frozen signed JSON for Tomato A–D, the 8 scenarios and
benchmark examples. **The UI must visibly label which mode it is in. Never silently fake a live
request.** The demo must survive GPU down, VPN down, Ollama down, tunnel failure, server reboot.

## 19–21. Test plan, audit, verification

UI: desktop + mobile, keyboard, reduced motion, no colour-only statuses, no horizontal overflow.
API: timeouts, actionable errors, model-unavailable path, rate limit. Server: Ollama not public,
health visible, no committed secret. Demo: live path **and** fallback path both tested.
Report/PPT: **every number generated from final artifacts — no stale number copied by hand**; all
negative results retained. Public: no private host paths, no secrets, no restricted recipe or paper
text.

## 22. Submission package

Frozen tree + manifest hashes · report + figures · PPT · demo (live + fallback) · release card ·
compliance matrix · decisions · worklog.

## 23. Files Kush provides — read-only, do not modify

| Path | Purpose |
|---|---|
| `src/culinarystate/**` | frozen engine — **never edit for UI reasons** |
| `registry/**` | frozen registries (13 axes, pH, ING, processes) |
| `reports/s180/*.json` | frozen step-7 results |
| `reports/final/figures_s180_2026-11-16/` | current figures + source hashes |
| `reports/final/sections/S180_freeze_results_DRAFT.md` | the S180 report section |
| `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md` | contract compliance |
| `tools/s179_submission_demo.py` | the 8 contractual scenarios |
| `DECISIONS.md` (D-134…D-137) · `STATUS.md` | governance + state |

**If the engine needs a change, it needs a decision record first.** Not a UI convenience.

## 24. Acceptance criteria

Report and PPT tell the same story as the app · every deliverable stated honestly as PARTIAL with its
gap named · no SOTA language · UNKNOWN visible in the UI · fallback demo proven offline · all numbers
traceable to a frozen artifact · Kush signs the science, Parv signs report/deployment.

## 25. Stop conditions — raise to Kush, do not improvise

(a) a scientific or governance decision is required · (b) a course requirement conflicts with the
SSOT · (c) a required file is unavailable · (d) a credential or login needs a human · (e) a missing
contractual experiment would materially change a scientific claim.

When stopping, give: **QUESTION · RECOMMENDED CHOICE · ALTERNATIVES · CONSEQUENCE · DEADLINE IMPACT.**

---

## The one thing to remember

**Three gaps — D1's 40 verified rows, D5's chef review, and the 9-row proposal packet — are
human-only and no amount of UI, report or PPT work closes any of them.** They are what an examiner
checks against the proposal first.
