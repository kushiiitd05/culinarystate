# PARV — FINAL EXECUTION MASTER PROMPT (CulinaryState)

> **`AI_DRAFTED` · `NOT_HUMAN_REVIEWED` · execution handoff.**
> Compliance figures are quoted from `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md`,
> itself `AI_DRAFTED`. **Kush and Parv own the compliance claim.** Resolution rule: **ksh governs**
> (D-139). This document closes no deliverable and no D-085 gate.

> **17 Nov update:** Kush has handed the remaining work to Parv. Read `handoff/PARV_HANDOVER_2026-11-17.md` first; it adds the signed snapshot, the Explorer UI, the live RAG console (`/live`) and the remaining task list, and wins where the two differ.

**Self-contained. You should not need to rediscover the project from this document.**
Written 16 Nov 2026. Freeze **19 Nov** · verify **20 Nov** · submit **21 Nov** · present **25–26 Nov**.
Everything through 16 Nov is on **`main`** (PRs #11 and #12 merged, D-138). Current work branch: `kush/s181-explorer-build`. Unit tests: 5,977 passed at the 16 Nov merge; re-run before quoting a count.

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
| 4 | **The proposal packet** — 51 AI-prechecked rows across three arms (14 + 16 + 21); on the 21 grounded rows ksh and prv differ on 9, which is where a human verdict decides something (~20 min) | yes | **human only** |
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
profiles". Result on the 60 hardest cases: **21 grounded proposals** (72B, prompt v3). Counting rule, so the two figures in circulation are not confused: **19 of 21 name a real choice; 17 of 21 are distinct well-formed groups** once the 2 duplicates of an already-accepted group are set aside (ksh governing, D-139). 17 judged
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

## 12. Design system — `design/FINAL_DESIGN_SYSTEM.md`

**Every value measured, not chosen.** Colours generated in OKLCH, gamut-checked, WCAG-checked by
script: **zero clips, zero contrast failures in either mode**. Re-runnable audit in `design/audit/`
(`palette.py`, `emit.py`, `inspect_fonts.py`, `verify.py`, `tokens.json`) — **wire it into CI.**

**Light mode is the default.** Dark washes out on lecture projectors and prints as grey mud.

**Fonts — all three proposals replaced on measured evidence:**
- Instrument Sans → **IBM Plex Sans**. Instrument Sans ships 343 codepoints and is **missing
  `± ≈ µ Δ ≠ ≥ ≤ ₂ ² †`**. `pH ≤ 4.6` and `C₆H₈O₆` would fall back mid-word.
- Fraunces → **Source Serif 4**. Nine digit widths, **no `tnum` at all**, so heading numbers jitter
  and cannot be fixed. Source Serif 4 also has real small caps for structural labels.
- DM Mono → **JetBrains Mono**. One zero glyph, no disambiguated alternate. Highest x-height tested
  (0.550 em), so 12px IDs optically match 13px Plex.
- ⚠️ **`font-feature-settings: "calt" 0`** on mono, always. Left on, `pH >= 4.6` renders as a ligature
  **the font invented** — a correctness bug in an instrument that displays applicability conditions.

**Colour architecture — the six-hue palette was measurably impossible.** A search over 1,400 hue
assignments found a best worst case of ΔE 3.1, and under deuteranopia still put **evidence-match and
mismatch at ΔE 3.3** — the instrument's most consequential distinction, invisible to ~6% of male
examiners. So colour splits:
- **`--state-*`** even lightness, for text and table cells. **Colour is a redundant mnemonic only.**
- **`--viz-*`** staggered lightness, for graph nodes and chart series. CVD-separable at ΔE 6.5–12.3.

**The real signal is four non-colour channels: glyph + marker + border + fill.** Seven states, no two
sharing any channel. `✓ ✗ ⊘ ∅` are absent from all three families — **do not use them.**

Key rules: chrome is achromatic (every coloured thing is a claim about knowledge) · never round a
table · elevation 0 on evidence rows · glass at **0.86 alpha minimum** (0.70 fails at 3.33:1) ·
UNKNOWN fills sit **darker** than their surface so absence reads as a hole · `circle-question-mark` is
**reserved** for UNKNOWN_IN_QUERY and must never be a help icon.

**Build the `?vision=deut|prot|trit|mono` CVD flag early** and screenshot through it in CI. The stated
weakest link is behavioural: without it, the glyphs erode into colour-only chips before the 25th.

## 13. Motion — `design/MOTION_SPEC.md`

Motion is the delta channel; **stillness is a claim.** Unchanged rows have zero animated properties.

- **UNKNOWN is the slowest transition in the app (380 ms)** and fades **in place**, never translates —
  translation reads as *arrival of information*, which is wrong for absence.
- **The lot graph never animates layout.** Position is lineage; a node that moves reads as a lineage
  change. Computed once per recipe, memoized.
- **ABSTAIN gets 760 ms, `role="status"`, never `role="alert"`**, no amber, no red. Opens with 200 ms
  of nothing — the silence reads as the system finishing its check.
- **Never interpolate an interval.** Animating `(4.3, 4.9)` displays pH values the system never
  claimed — the no-invented-values law broken inside an animation.
- Reduced motion is **substitution, not removal**: every `was:` value becomes printed text, edge draw
  becomes edge weight, stagger order becomes list order.
- **Audit Tailwind for `transition-all`** — one stray global transition breaks the whole premise.

## 14. Frontend — `design/FRONTEND_ARCHITECTURE.md`

Hand-to-developer spec, **grounded in the engine's actual shapes** (`composition/state.py`'s
`V(v,b)`/`U(reason)`, `state_full.py`'s block assembly, `compatibility.py`'s AXES and VALUE map,
`claim_packet.py`'s keys). **Nothing in it asks the engine to change.**

- UNKNOWN is modelled on the engine's own wire format with **branded types**, so an unknown cell is
  *unrenderable as a value* and a `RankingScore` can never reach a component expecting a confidence.
  The project's laws enforced by `tsc`.
- Versions verified, not assumed: **Next 16.4.6** (`middleware.ts` → `proxy.ts`), **Tailwind 4 with no
  `tailwind.config.js`** (CSS-only theming), shadcn CLI v4, `@xyflow/react` 12.12.1.

## 15–17. Backend, Ollama, deployment — `deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md` governs

```
Browser → Vercel: Next.js UI + BFF + SIGNED PRECOMPUTED SNAPSHOT   ← default serving mode
              └─(opt-in, live)→ Cloudflare Tunnel → stdlib gateway on the PRESENTER'S MAC
                                 (existing app/strict_server_v3.py, started with --public)
```
**Superseded 16 Nov:** an earlier version of this section drew a FastAPI gateway on the research
server with Ollama behind it. Do not build that. No FastAPI rewrite (the stdlib server is the audited
one), not the GPU server (VPN + shared GPU on the critical path), and **Ollama is off the request path
entirely**.
**Ollama is never exposed to the browser.** One provider abstraction for local Ollama and any hosted
fallback; **a hosted LLM is not scientific authority.** Secrets in environment variables only, never
committed. CORS restricted to the Vercel production origin. Rate-limit demo endpoints. Return a
request id and backend/model version on every response.

**CORRECTED 16 Nov — an earlier "~25 MB" figure in this session was wrong.** It was `du` on `src/`
and `registry/` and never traced what the runtime loads. Measured: `DemoContext.load()` reads
**~153 MB of ledger JSONL** (EVD 85 MB, KGE 58 MB, ING, COND, ALIAS, PROC), takes **9.7 s**, and peaks
at **1.21 GB RSS**; a query is then **~30 ms**. The 3.2 GB `data/` tree is build-time only.

**Consequence: do not run the Python core on Vercel.** Not because of bundle size — Python's limit is
500 MB, not 250 MB — but because (i) `EVD.jsonl` and `KGE.jsonl` contain **BBC-derived rows filtered
at load time, not file level**, so uploading them violates D-003; (ii) 1.21 GB against a 2 GB instance
risks OOM; (iii) a 9.7 s cold load becomes 20–40 s on a shared vCPU, paid on the first click of the
talk. Full analysis: `deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md`.

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
| `design/FINAL_DESIGN_SYSTEM.md` | palette, type, the seven-state system |
| `design/audit/` | re-runnable contrast + font audit — wire into CI |
| `design/MOTION_SPEC.md` | motion tokens and the ΔS animation |
| `design/FRONTEND_ARCHITECTURE.md` | component tree, TS interfaces, React Flow plan |
| `deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md` | snapshot-primary deployment, the `--public` trap |

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
