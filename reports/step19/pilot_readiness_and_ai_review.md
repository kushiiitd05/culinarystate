# Step 19 readiness and independent agent review

Status: **AI_DRAFT; synthetic preparation only**, 2026-10-28. This review was delegated by Parv's instruction to advance engineering and the pilot lane. It supplies no human annotation, signature, expertise credential, scientific agreement or waiver. No real recipe text was opened, no frame inspected or drawn, and no packet or Gold label created for this review.

## What can proceed now

Engineering, adversarial synthetic rehearsal, documentation and review can proceed under the current instruction. Building tools is distinct from exercising their real-data draw/start/seal actions. The latest instruction supersedes the design's historical “scripts not authorised” wording for engineering; it supplies neither Kush's nonce nor the missing signed preregistration and human observations. AI can review proposed conventions and check software; two agent outputs cannot be counted as two independent human annotators.

This artifact and `annotation/annotation_handbook_v2_DRAFT.md` are **analyst-only proposals**. Do not issue either new document or the new catalog to P1 annotators without an explicit protocol decision: design §5.6 intentionally measures v0 + handbook v1/Addendum A. Exposing known gaps or a corrected handbook before that wave would change the measurement. The current user instruction does not specify a replacement measurement contract.

## Verified source trail

| Evidence read | Result |
|---|---|
| `CLAUDE.md`, `STATUS.md`, WORKLOG S151, DECISIONS D038–D042 | rc2 remains a draft; Step08 has run; Parv recommends reserve_split_v2 pending Kush; no human pilot start/draw recorded |
| `reports/step19/README.md` §§3–5 | 25 local decisions, signature requirement, tracked commitment path and six planned tool functions |
| `reports/step19/deep_gold_pilot_design_v1_draft.md` §§4.4–5.7, 6, 9–10 | exact draw, exposure, wave freeze, provenance and reporting requirements below |
| `annotation/annotation_handbook_v1.md`, Addendum A; `UNKNOWN_examples.md`; `annotation_checklist.md`; `hard_examples.md` | existing human workflow plus the quantity/conflict issues below |
| SSOT §237.5, lines 25721–25744 via `docs/SSOT_INDEX.md` | 17 hard-case classes represented in the synthetic catalog |

These paths and section references are reproducible evidence pointers, not a claim that the whole project or all implementations were audited. Root integrates this review and records the final commit and checks in WORKLOG. This delegated lane adds three documentation/catalog files and a separate module, CLI, tests and generated synthetic report; frozen/v1 files are unchanged.

## Real-pilot prerequisites and who supplies the evidence

| Stage | Required evidence before advancing | Outstanding source/owner |
|---|---|---|
| Start and registration | Resolve applicable D19-1..25 choices; append/sign THR-19P-01..35 with data-seen disclosures; H4/H5 contract/start decision | Required humans; latest engineering “go” is not their signature |
| Seed and frame | Kush writes nonce in signed row **before frame is built** (§4.5, stricter than README's “before inspected”); choose draw runner; freeze source/tag/eligibility/group/exclusion rules | Kush nonce absent from supplied conversation; no substitute nonce generated here |
| Source and frame | Local-research eligibility/licence decision, available local texts, 4–20 ingredient lines and 2–15 steps; exclusions include all 50 Gold-index IDs + 90 additional screened IDs + groups/title twins | Human/source decision and mechanical preflight; Gutenberg/TASTEset excluded |
| Selection | Fixed P1 7 cells, P2 13; totals BBC6/Food.com10/Wikibooks4 and LOW5/MID9/HIGH6; seed from first8 bytes SHA256(frame_sha256 || wave || nonce); ordered two reserves per cell | Tool needs fully specified byte encoding, stable sort, PRNG, tie/group rules and signed hash before use; AI recommendation: record all in versioned draw spec |
| Issue | Fresh blank gold-1.0, handbook v1+A, separate packet IDs/order; one annotator's files absent from other's filesystem; sealed key local and tracked hash | Consenting human A/B, local machines/accounts; no AI prefill or analyst known-gap list |
| During wave | Private write-only questions; no convention changes/answers until both commitments; timing/replay/validate counts, representability log and >=2 interim snapshots per label | Each human annotator; facts recorded contemporaneously, not reconstructed by agent |
| Key opening | Both text-free commitments tracked and committed in git before opening; include packet/hash/size/mtime, handbook version, snapshot hashes/times, question/checklist hashes; sealed-key hash matches | Each human's session; PV9 git evidence, recorded opening time |
| Validity | PV1..10 checker + planted controls pass; FAIL makes wave NOT_COUNTED and requires fresh recipes; REVIEW needs written human explanation/decision | Provenance tool plus humans; agreement tool's default independence string insufficient |
| After P1 | Joint adjudication, all disagreement rows completed; dated B only after commitments; max(tool, per-pair category rate)>0.20 triggers revision; capacity check | Human adjudicators; both wave-specific agreement and mixed-version descriptive summaries |
| P2 and scale | Weekly capacities and later B_h explicitly supplied; P2 after 07I-C labelling closes; noninterleaved single-task sittings; projected <=40h per annotator or explicit capacity decision | Kush/Parv; 120 active min/recipe is a right-censored stop, not silent extension |

P1 cells are design §4.4: FOODCOM/baking/MID; BBC/drain_discard/LOW; WIKIBOOKS/indian/MID; FOODCOM/multi_component/HIGH; BBC/random/MID; FOODCOM/reserve_split/HIGH; WIKIBOOKS/simple/LOW. Indian cannot be sourced from Food.com under this explicit-label definition. P2 default is seeded coverage-greedy, not uniform random; report enrichment and uncovered classes without a coverage-driven redraw. Replacement is allowed only before annotation for listed source/duplicate/representability/availability/exposure causes, using the next same-cell reserve with rationale. Every selected group is DESIGN_PILOT, excluded from training, sealed tests, calibration, Silver, Gold-Light, demos and retrieval exemplars.

## Conflicts and recommended disposition

All dispositions below are **AI_DRAFT recommendations**, not adopted human rulings. Original v1 documents remain unchanged.

| ID | Reproducible discrepancy | Recommendation and verification |
|---|---|---|
| PR01 | README introduction says Step08 not started; STATUS/S144–145/D035 record built/run 08a, failed G08-3, authorised 08b-v0 | Treat README as historical design snapshot; future integrated index should point to current status and retain failures |
| PR02 | Design §4.4 pins broken `\b(reserv|...)\b`; D038 creates corrected twin and D040 recommends v2 | Confirm v2 explicitly in signed draw/tag spec; retain v1 comparison, avoid silently changing source definition |
| PR03 | Design §4.5 requires nonce before frame **built**; README checklist says before **inspected** | Use stronger pre-build condition; record nonce commitment time and canonical frame bytes. Existing descriptive frame counts remain disclosed |
| PR04 | `UNKNOWN_examples.md` says “recombine whole reserve” for a splash; handbook says unknown means unknown; physical quantity may be a partial unknown | Preserve qualitative amount, do not consume entire reserve by default. If current replay cannot represent unknown partial flow, log BLOCKING QUANTITY_MODEL_GAP and preserve labels; synthetic rehearsal case HC06 covers this |
| PR05 | v1 Split rule allows equal fractions for “obvious division”; H4 draft proposes explicit uncertainty preservation | Only stated equal division justifies equal fractions in v2 proposal; otherwise unknown fractions. Changing live v1 requires approved dated addendum, not retrospective relabelling |
| PR06 | v1 hard example H6 acknowledges meanwhile but says order by text position; draft contracts target temporal relations | Text order is an encoding order, not evidence of sequential causation. Keep parallel cue and log missing relation as gap; do not certify representability from successful replay |
| PR07 | Old v1 workflow says pick from existing batches and 15–25min target; new design excludes exposed batches and timeboxes120min | New pilot uses frozen fresh draw and measured timing, no reused S116 bundle. Earlier target is not observed DeepGold duration |
| PR08 | Design v0 pilot versus new rc2 and v2 proposal | Keep separate contract identities and side-by-side synthetic checks; human protocol decision required to change actual pilot instrument; no claim that 16c is frozen |
| PR09 | Sample seed expression lacks canonical byte encoding/PRNG; greedy design requests per-cell inclusion probabilities | Specify encoding and algorithm version before draw; do not report quota/N as exact probability under group-skipping/greedy selection. Mark unknown unless mathematically justified; report stratified/coverage design limits |
| PR10 | Default agreement tool emits INDEPENDENT_HUMAN_VS_HUMAN without provenance assessment | Wrapper must require valid provenance; no bypass on REVIEW/FAIL. PV8's 11-second pair has no explicit standalone timing threshold in PV1..10; fixture must declare its causal flag (e.g. <5 active minutes/PV4), not invent a new failure cutoff |

## Synthetic rehearsal to run and retain

Inputs must carry `AI_DRAFT_SYNTHETIC`, a distinct rehearsal namespace, no source IDs/text, and no claimed human verdict. Do not write them into actual pilot commitment paths or count them in n. New catalog `annotation/hard_case_catalog_v2_DRAFT.jsonl` supplies 17 source-free prompts, suggested checks and pending reviewer fields. The v2 handbook describes how to use them for engineering.

For every rehearsal retain run ID, code commit, input SHA256, contract/schema/handbook versions, case IDs, expected invariant, observed output/error, test verdict, provenance verdict, changed paths, rationale and unresolved expert question. `expected invariant` is an engineering assertion, not a human label. Keep planned expectations separate from observed results. The source-free six-stage workflow below has run; the17 catalog cases remain proposed reviewer prompts, with observed-output/verdict fields null.

Minimum planted protocol cases: (1) exact duplicate files -> PV1 FAIL; (2) changed file after commitment -> reject; (3) key opened before commitments -> PV6/PV9 FAIL; (4) untracked commitment -> PV9 FAIL; (5) no interim snapshots -> PV10 REVIEW; (6) identical content but different bytes -> PV2 REVIEW at the wave-specific fraction; (7) 11-second complete sitting with <5 active minutes -> PV4 REVIEW; (8) high-prevalence field uses chance correction, p_e=1 explicitly skipped; (9) clean controlled synthetic pair -> no planted flag. A fixture pass proves detection of these controls, not human independence in production.

Add negative controls for accidental recipe text in tracked manifests, real path/ID use in rehearsal, rc2 applied under v0 name, signed rows missing, stale hashes, zero package multiplier, unknown partial recombine, equal versus unstated shares, and alternative versus simultaneous ingredients. Parent engineering lane owns implementation and observed test results.

### Implemented narrow workflow and observations

`src/culinarystate/annotation/pilot_rehearsal.py` provides six stages: explicit synthetic frame/group draw, blank fixture packets, simulated hash commitments with interim snapshots, fixture integrity checks, controlled-code equality summary, and report. `tools/step19_pilot_rehearsal.py` accepts no data input; its CLI uses hardcoded fixture IDs only. It accepts an optional new `SYNTHETIC-*.json` output, refuses existing files and protected ledger/registry/schema/Gold paths. No human field or existing artifact can be overwritten.

Reproduce from repository root with the existing Python:

```sh
/Users/parvgoyal/wth/CGAS/Project/culinarystate/.venv/bin/python -m pytest tests/unit/test_step19_pilot_rehearsal.py -q
/Users/parvgoyal/wth/CGAS/Project/culinarystate/.venv/bin/python tools/step19_pilot_rehearsal.py
```

The CLI run generated `reports/step19/synthetic_rehearsal/SYNTHETIC-rehearsal-v1.json`: two selected synthetic recipes in distinct groups, two separate software fixture channels, empty issued annotations, controlled later code vectors and input/observation hashes. All six planted controls were detected: tampered label, missing commitment entry, wrong packet, wrong hash, group leakage and missing snapshots. The clean fixture passed these narrow integrity checks. This module does **not** implement the full proposed PV1..10 protocol, git timing/sealed-key workflow, real stratified quota algorithm, uncertainty intervals, alpha or F1. `counts_as_pilot_provenance` and `counts_as_human_gate` remain false even on clean fixtures. Snapshot times are declared simulated ticks, never UTC attestations. The code equality summary is explicitly not IAA.

Tests were written first and failed to import the absent implementation. Four later adversarial controls first failed, then passed after rejecting invented human verdict, git provenance and simulated commitment-time changes. Root records final targeted/full counts and commit identity in WORKLOG. The full17-class semantic rehearsal is future work; this workflow run does not mark those classes represented or expertly verified.

## Expert verification and closure

A reviewer should reproduce PR04–PR06 using only catalog prompts, compare v0 validation/replay with the separate rc2 model and check that no quantity, lineage or temporal fact is fabricated. Review all17 classes for FAITHFUL/WORKAROUND/IMPOSSIBLE under the **selected** instrument; a successful validator is only a structural check. Log category, severity, field family, rationale, proposal and affected version. Expert findings are pending; leave person/date/decision fields blank until supplied.

After actual human waves, classify each problem as SCHEMA_GAP, HANDBOOK_GAP, SOURCE_DEFECT, BOTH_VALID_AMBIGUOUS or NOT_A_PROBLEM. IMPOSSIBLE is BLOCKING; WORKAROUND is counted as silent schema debt. STOP-SCHEMA includes >=2 recipes with adjudicated BLOCKING schema/handbook gaps on the same family whoever logged them, plus existing supplementary rules. Preserve dismissed blocking items with written rationale. Uncovered classes are not “handled”. Use alpha cutoffs only for categorical families; F1 cutoffs are routing conventions. P1/P2 cannot be pooled into reliability evidence, and n20 feasibility cannot authorise19-M, N>40 or unrelated gates.

Human/expert review does not stall the synthetic engineering lane. It still limits claims, the real blind pilot and contract freeze; an AI recommendation cannot manufacture those missing observations. Later expert changes should produce a versioned correction with impact/retest evidence rather than overwrite historical labels, commitments or failed gates.
