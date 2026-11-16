# Plan to finish — scope freeze, full-corpus results, presentation, deployed app (14 Nov 2026)

Owner: Kush session (ksh+prv AI under D-085 where marked); Kush approves at each ☐ marked **KUSH**.
Deadlines: code/result freeze **21 Nov**, rehearsal **24 Nov**, presentation **25–26 Nov**.

## 0. Where we are (14 Nov, morning)

| Item | State |
|---|---|
| 36-step gate audit (269 clauses) | 0 complete · 2 run with recorded gate failure (07, 08) · 18 partial · 7 not started · 5 blocked · 4 cut — `reports/orchestration/step_gate_audit_36_2026-11-13.{csv,md}` |
| Board | MUST 52/84 · SHOULD 89/117 in scope |
| Parv takeover | reduced submission candidate (draft, not author-approved) — `reports/final/submission_candidate_2026-11-13/`; R1 and CAL paired AI reviews done (NOT_COUNTED) |
| Running: vinayak | L4 effect map, 224 targets × all non-BBC recipes (110 workers, ETA ~3–4 h); 72B second pass on 2,048 ING attributes (GPU, ETA ~2.6 h) |
| Running: manjot | L2 state-dataset fill, 20 shards (Wikibooks done: 3,676 recipes, 59,357 rows, 0 exceptions, 11,433/11,433 heat events joined) |
| Running: Mac | L2 BBC leg |
| Done 13 Nov | L5 process→state map (612,782 recipes); SSOT column map v2 (146/210 fields with a producer); AA formula census per event (D-106); D-097/D-102 type tables; 15a registry; NER vs Rung A; paired vs D0 |

## 1. Scope freeze — D-112 (**KUSH approves**)

Draft decision text (to append after approval):
> The 25–26 Nov submission is the **reduced CulinaryState**: state-aware recipe representation over the full corpus (parser → engine → physics v06 → evidence router), evidence-bounded answers with abstention (D4), the D5 benchmark with its recorded H1/H3 RULE_NOT_MET results, and the 13–14 Nov full-corpus state/effect results as a technical addendum. Out of scope and reported as such: validated simulator (Step 27), synthetic prior / hybrid (28, 33), rollout (34), FlavorTwin, full H2/H4/H5 (H8 register). The 36-step gate audit verdicts stand as the step status of record. Every negative result and AI label is preserved. Human-only gates (07.A, independent Gold, signatures) stay open and are named as limitations.

Effect: "the plan is final" becomes a true statement about the *reduced* scope; nothing is relabelled complete.

## 2. Finish the full-corpus lanes (agent, today)

| # | Task | Output | Check |
|---|---|---|---|
| 2.1 | Collect L2 shards (manjot + Mac BBC), merge with `tools/s179_state_dataset_fill_merge.py` | `reports/s179/state_dataset_fill_full_2026-11-14.json` (+ ignored rows) | recipes = 612,782; joined heat rows = v06 heat events per family; 0 exceptions |
| 2.2 | Collect L4 non-BBC; run BBC leg on the Mac; merge | `reports/s179/effect_map_224_{nonBBC,BBC}_2026-11-14.json` | per-target DIRECT ≥ vitamin-C router census counts for the same target |
| 2.3 | 72B pass lands → agreement table 7B vs 72B; ING attributes = agreed values only, rest UNKNOWN (new D-114) | `registry/ing_attributes_consensus_v1.csv` | spot list (tomato, lemon, lime juice, apple) correct or UNKNOWN |
| 2.4 | D-108 lot-level formula over all heat events (manjot) | `reports/s179/formula_census_aa_lot_2026-11-14.json` | in-domain counts by reason; numbers only in domain |
| 2.5 | External check: formula vs EVD vitamin-C retention where both apply | `reports/s179/formula_vs_evd_check_2026-11-14.json` | paired differences reported, no tuning |
| 2.6 | Technical addendum + rebuild Parv's candidate to a **new** archive and `build_manifest_v2.json` | `reports/final/submission_candidate_2026-11-13/` v2 | Parv's files untouched; checks on exact revision |

## 3. Parv's open experiment item (agent, GPU on vinayak, 14–16 Nov)

- **D-098 ablations (T8-C21-R2)**: pre-register first (components removed one at a time from the frozen D5 ladder: state, evidence index, enforcement, abstention), frozen qwen2.5:7b-instruct 845dbda0 on the user-space GPU ollama, temperature 0; new paths; original B0–B7 untouched.
- **H1/B7 regeneration (T9-C24-R2)**: rerun frozen B7 and H1 inputs with the frozen 7B; report byte/metric equality against the recorded outputs.
- **Source-held-out retrieval (T8-C06-R1)** and **versioned D5 re-emission through strict-v3 (T0-C06-R2)**: new versioned outputs; original 30 flags retained.
- **Router replay gap (Step 23, G23.5)**: find why `gates` differs in Parv's rerun; fix serialisation or record the version difference.

## 4. Cheap gate closes (agent, 1–2 h total)

Step 14 `consumer_readiness_v1.json` (NEED_DATA is a valid verdict) · Step 36 empty L15 whitelist (B6 ≡ B5), OOD strata, §257P checklist · Step 02 `count_definitions_v1.md` · Step 01 `plan_authority_map_v1_1.csv` + `namespace_registry_v1.csv` · Step 08 copy 08a gate report into `reports/step08`. Re-run the affected audit rows; update the audit to v2 (v1 kept).

## 5. Presentation material — "how the state-aware representation works" (agent draft, **KUSH/PARV edit**)

1. **SSOT crosswalk**: each SSOT state component (§4 spine, §62 recipe state schema, §63 food state schema, §106 factorized state, §108 observation vs latent, §112 transition learning) → our implementation (module/ledger) → full-corpus evidence file → status.
2. **Five-layer figure**: entities/lots → events (process, consumes/produces/discards) → state change (D-102 types) → physical state (L1 stated, L2 scenario, cell = value+basis or UNKNOWN+reason) → evidence state (EVD DIRECT / formula interval / UNKNOWN).
3. **Worked example** on a self-written recipe (no third-party text): timeline table showing correct and wrong cases (implicit-object Merge missed; "pour" typed as Merge) — negative results kept.
4. **Full-corpus numbers**: 612,782 recipes, 9.47 M step events, Merge 24 %→10 % / Transform 48 %→76 % through a recipe, physics coverage (T 15 %, t 31 % stated on Food.com heat events), router DIRECT 0.09 %, formula reach, effect-map rows.
5. Update the overview artifact (https://claude.ai/artifact/XLS6dAk4meYKteM9G273hU) with the crosswalk and final lane numbers.

## 6. Deployed application (Vercel)

**Goal:** a public, honest demo — type or pick a recipe → state timeline → physics and evidence per step → cited answer or abstention. No corpora hosted; BBC never leaves the Mac (D-003); every number shows its basis.

**Screens:** (1) recipe input + 4 sample recipes we wrote; (2) state timeline (lots, events, D-102 state change, step position); (3) step detail: stated conditions vs scenario defaults, moisture cap, formula interval if in domain, EVD values with ids; (4) ask box (`/api/ask`, strict-v3 guard: refuses unsupported); (5) "About the evidence" page with limitations and labels.

**Architecture — decision needed (KUSH):**
- **A (recommended): Vercel for the UI + a Python backend on a container host** (Hugging Face Spaces / Render / Railway free tier). The existing strict-v3 backend (`culinarystate.app.strict_server_v3`, `POST /api/ask`, `GET /api/health`) runs unchanged in a Dockerfile; Vercel rewrites `/api/*` to it. Lowest risk: no backend rewrite, audited code path.
- **B: Vercel only (Python serverless function).** Needs a slim public data pack: the demo context loads the ledger store (~300 MB tracked; EVD 85 MB, KGE 58 MB, REC 90 MB) and Vercel functions are limited to 250 MB unzipped. Requires a pack builder (only fields the router/decision layer reads) and a pack-backed store, plus cold-start testing. ~1 extra day.

**Build steps:** (1) measure the public-mode data the context actually reads; (2) pick A or B; (3) UI in Next.js on Vercel (or the existing static `strict_v3.html` restyled) calling `/api/*`; (4) add `/api/trace` that returns the timeline JSON for an input recipe (thin wrapper over Rung A + D-102 + v06 L1 binder + L2 scenario + router; read-only, rate-limited like `/api/ask`); (5) tests: unit for `/api/trace` schema, Playwright e2e on the four sample recipes + a refusal case, the existing strict-v3 1,000-call audit re-run against the deployed URL; (6) deploy preview → check → production.

**Needs from Kush:** `! vercel login` once (and a host account for option A); approval that the repo/app may be public (repo is already PUBLIC per STATUS).

**Guards:** no hosted LLM key required (B5T template path is LLM-free); rate limit kept; no BBC, Food.com or paper text served; display labels NON_CITABLE / RESEARCH_ONLY where they apply.

## 7. Human-only (Kush, Parv)

Approve D-112 · review paired AI R1/CAL summaries and write a real review entry · author-final report/deck, contributions, permission statements · decide AAK-04/10 (usable, not yet downloaded) — AAK-05 excluded (NC-SA) · PR #11/#12 review · MPU, 21 Nov freeze, 24 Nov rehearsal.

## 8. Timeline

| Date | Agent | Humans |
|---|---|---|
| 14 Nov | §2 lanes land and merge; §4 cheap closes; D-098 prereg; app data measurement | approve D-112; `vercel login`; pick A/B |
| 15–16 Nov | §3 experiments on GPU; app backend + `/api/trace`; UI v1 | review AI summaries |
| 17–18 Nov | e2e tests, preview deploy; §5 crosswalk/figures; candidate rebuild v2 | author edits start |
| 19–20 Nov | production deploy; audit v2; final numbers into addendum | MPU after 19 Nov; author edits |
| 21 Nov | freeze: tag, manifests, full suite | sign-off of what is frozen |
| 22–24 Nov | fixes only; rehearsal support | rehearsal 24 Nov |

## 9. Risks

VPN drops (runs are nohup/setsid on servers; Mac only for BBC) · manjot disk 93 % full (rows are gzip; check before 2.4) · 72B attributes still AI-drafted (used only where 7B and 72B agree, labelled) · Vercel size limit (option A avoids it) · demo must not imply validated nutrient predictions (labels on every number).
