# Parv input manifest — frozen files a UI / report builder consumes

**`AI_DRAFTED` · `NOT_HUMAN_REVIEWED` · 17 Nov 2026.** sha256 computed with `shasum -a 256` on
17 Nov 2026, branch `kush/s181-explorer-build`, working tree (not from git objects). Re-hash before
use; a mismatch means the file changed after this manifest.

- **Frozen?** `YES` = a source document states it is frozen/sealed (`handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md` §23 or the file itself). `LIVING` = governance file that is still appended to; pin the hash at the 19 Nov freeze. `DRAFT` = labelled draft.
- **Read-only?** Every file here is read-only for the UI/report builder. "If the engine needs a change, it needs a decision record first" (master prompt §23).
- **Consumed by** uses the four routes of master prompt §9 (`/`, `/lab`, `/compare`, `/method`). **Slide numbers are `NOT_EVIDENCED`** — no final slide numbering was found; "deck" names the topic only.
- Page/slide assignments are this drafter's mapping from master prompt §9–§10, **not** a recorded decision.

## 1. Contract and governance

| Path | Purpose | sha256 | Frozen? | Read-only? | Consumed by | Expected output |
|---|---|---|---|---|---|---|
| `docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf` | the D1…D5 contract | `7397150de6f3309ac563b1feaaec7b77f9534b3c908cd206d9f83318ff2a32d5` | YES | yes | report: deliverables section; deck: contract slide | quoted success checks |
| `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md` | D1…D5 status + allowed wording | `035ef22e92826f42dec69193c676f988a2d4e645829f72075572d5ef1e534241` | YES (dated; D4 row superseded by `reports/s181/d4_contract_metrics.md`) | yes | `/method`; report compliance table | five PARTIAL rows, gap named |
| `reports/s181/d4_contract_metrics.md` | D4's four contract metrics | `30773e1ab07ec0a3e2814edeee07016297441a6afcbbb5d1a67d1c4989f04b04` | NOT_EVIDENCED (new 17 Nov) | yes | report D4 section; `/method` | risk–coverage, unsupported-claim rate, degenerate Recall@K, ECE NOT_COMPUTABLE — with labels |
| `reports/s181/d4_contract_metrics.json` | machine output of the above | `bf2f59dc9f7585be431ad03ef2c2d5fc4ecc9297237ee14081830817edf12d7f` | NOT_EVIDENCED | yes | report D4 table generation | numbers, not hand-copied |
| `DECISIONS.md` | decisions incl. D-134…D-139 | `f9a239c29c41bc0573d8ef240a1f8778ee618441a17c924ca69bb00ce3a26c7a` | LIVING | yes (append-only by scribe) | `/method` provenance; report governance | decision ids + approver class |
| `STATUS.md` | current state | `9bc609da7e47f0a874bf3a910e4cedb0ae5356a7fc808bb2250c67e39fb84418` | LIVING | yes | report limitations | — |
| `reports/s180/HUMAN_CONCURRENCE_2026-11-16.md` | Kush concurrence record (not independent verification) | `ffed8e64cfe45c4aa776763d6c4b60c9754ec1e7d3854f9b6432b9e25d519e84` | YES | yes | report governance paragraph | wording "concurrence, AI_DELEGATED_D085" |

## 2. Engine (never edit for UI reasons)

| Path | Purpose | sha256 | Frozen? | Read-only? | Consumed by | Expected output |
|---|---|---|---|---|---|---|
| `src/culinarystate/composition/state_full.py` | State v2 assembly; shapes of G/C/Q/Y cells | `1442f38de471b9269bf6ee77bd7a5923913002abe19d112e7a584f65e38b2262` | YES | yes | `/lab` State tab; `/compare` | per-(food, step) cells |
| `src/culinarystate/composition/state.py` | `V(v,b)` / `U(reason)` wire format | `dee0b7ffacb0542dbe7325ba9c115222e405139c57467049fc0385501b2b455e` | YES | yes | `/lab` — UNKNOWN rendering types | branded TS types |
| `src/culinarystate/composition/claim_packet.py` | Claim Packet keys | `11fbd284b043b19ca637968150989afc710882449be0d7e3b6ad556f7dd97255` | YES | yes | `/lab` Claim Packet tab | allowed/forbidden/caveats |
| `src/culinarystate/retrieval/compatibility.py` | 9 axes + VALUE map | `7c7fd394c16221ab28421d6c7204edb3b68a986626f66de89783afdaa7a9ac49` | YES | yes | `/lab` Compatibility tab | MATCH/NEAR/UNKNOWN/MISMATCH |
| `src/culinarystate/app/server.py` | stdlib demo server (`/api/health`, `/api/ask`) | `d453451da2333568c456e18fe0090345b0ed55f12ee0f7b8464490aa7c4bc8af` | YES | yes | live mode (optional) | JSON responses |
| `src/culinarystate/app/strict_server_v3.py` | audited strict gateway | `de0ba9d07cec8c9341500fc5a55f57a6513ec684ffef17f4ea1ae0379401ca5f` | YES | yes | live mode; must start with `--public` | JSON responses |
| `tools/s179_submission_demo.py` | the 8 contractual scenarios | `1c12d7466439ae8c89bb02655dd9f82b254ca05993e94bf733ac978ad511f77a` | YES | yes | `/lab`, `/compare`; deck demo | 8 scenario outputs — consume, do not invent new ones |

## 3. Registries

| Path | Purpose | sha256 | Frozen? | Read-only? | Consumed by | Expected output |
|---|---|---|---|---|---|---|
| `registry/rag/compatibility_axes_v1.csv` | canonical 13 axes + status | `c06db1af67fadf01179d63c6c09714fdc743d397ce86121b61893f056b8ded61` | YES | yes | `/lab` Compatibility tab; `/method` | 9 / 2 / 2 axis status |
| `registry/food_ph_fda2003_v1.csv` | FDA/CFSAN 2003 pH table (479 rows per `STATUS.md`) | `e5191f2b72de95332215f9514ac4c494b3d2c6b0b28736b0929e3e1511912cfc` | YES | yes | `/lab` pH cell; tomato flow | intervals, never midpoints |
| `registry/food_ph_fda_ing_crosswalk_draft_v1.csv` | AI-drafted ING crosswalk — `UNVERIFIED_CROSSWALK_AI_DRAFTED` | `bb39c2c29701ab9ecb5b2318f1d54c822f4899183b8cd86467c1bf6fa01b03fc` | DRAFT (frozen as unverified) | yes | same; must display the unverified label | band + verify_status |
| `registry/composition_markers_v2.csv` | salt/acid/lipid/aqueous markers (AI-drafted) | `54bc64597380ca204822efac7d19e2ab16edb0d0bd5ed02f60db21ddf8094547` | YES | yes | `/lab` C block | presence cells |
| `registry/ing_sr_composition_v1.csv` | USDA SR composition per ING | `dbda6323c2c0393a6d795b2c48a71f2e7c23e81ead91cba0fbc0b86a67cc5e2a` | YES | yes | `/lab` C block | own/member composition |

The first two pH hashes match those recorded in `reports/final/figures_s180_2026-11-16/MANIFEST.json`.

## 4. Frozen results (S180)

| Path | Purpose | sha256 | Frozen? | Read-only? | Consumed by | Expected output |
|---|---|---|---|---|---|---|
| `reports/s180/hardcase_seal_2026-11-15.json` | sealed 60-case set | `a41abc1886b11641924020efdaa166e4731557ad74eb80b09bb36b9fa571fe6e` | YES (sealed) | yes | `/method` | case count only |
| `reports/s180/step7_arm_L_qwen7b_2026-11-15.json` | 7B prompt v1 arm | `da585d01def39c7f722ff0ede5a3e15396dd4f7badd04247dce28401385bd3a8` | YES | yes | report Layer-1 table | DIAGNOSTIC counts |
| `reports/s180/step7_arm_L_qwen7b_v2_2026-11-15.json` | 7B prompt v2 arm | `42dae68008b313ca57a1c8147cd283b0e4e95ea797c59976615efa4cd98efe81` | YES | yes | report | DIAGNOSTIC counts |
| `reports/s180/step7_arm_L72b_v1prompt_2026-11-15.json` | 72B prompt v1 arm | `6d8c466013b4f857d2083304c1bff7c43228ab353dc17bfc29f55613b9fe1837` | YES | yes | report | DIAGNOSTIC counts |
| `reports/s180/step7_arm_L72b_v3prompt_2026-11-15.json` | 72B prompt v3 arm | `4119f30cb8ca97f811f96a885ee8ab5eef98fc0fc7aacd1c2a19ff7a973ac4b4` | YES | yes | report; `/method`; alternatives flow | DIAGNOSTIC counts, no accuracy |
| `reports/s180/step7_arm_L7b_v3prompt_2026-11-15.json` | 7B prompt v3 arm | `7343081af85918f9f670cc650960b67c4e03e0c43233e269c6c44b9fdf6b8b03` | YES | yes | report | DIAGNOSTIC counts |
| `reports/s180/step7_FINAL_COMPARISON_2026-11-16.md` | step-7 narrative + limits | `b10da2e23c3248dc6a28942a79df939275e97374499e629516510c6a0bf4d1f2` | YES | yes | report Layer-1 section; deck | wording |
| `reports/s180/retrieval_diagnostic_2026-11-15.json` | V0 retrieval diagnostic | `8b69dbff1d5c8fcb26319ad873a45d25a22a564d8232e62e965a93e592a5a3b1` | YES | yes | report; `/method` | DIAGNOSTIC_ONLY overlaps |
| `reports/s180/retrieval_diagnostic_V1_2026-11-15.json` | V1 retrieval diagnostic | `a8f0e3e9af2e5c57676c7ec6319f2a330580a37890cb9be2c1b39205deb9784a` | YES | yes | same | same |
| `reports/final/sections/S180_freeze_results_DRAFT.md` | S180 report section | `a91bc12d775a723bfaba34a0244f831c69989d341e6a34a238515036d5b3649e` | DRAFT | yes | report | section text |
| `reports/final/figures_s180_2026-11-16/MANIFEST.json` | figure manifest + source hashes | `f23e10ee087612eeceb8400f93dde31ef57f7c2b91f83f8f0ec9cca463488db9` | YES | yes | report/deck figure captions | labels per figure |
| `reports/final/figures_s180_2026-11-16/fig_s180_1_retrieval_views.png` | figure | `61b5bbfb5bef92262dca528b6db7bc0e65815f3e6e794fac9f5ab6a02298a0db` | YES | yes | report; deck | DIAGNOSTIC_ONLY caption |
| `reports/final/figures_s180_2026-11-16/fig_s180_2_layer1_surface.png` | figure | `9904aa79867d9554630ad9154499350d336bd58a6d28a1cdf5c71cc6bb0a618f` | YES | yes | report; deck | NO_GOLD_SO_NOT_ACCURACY caption |
| `reports/final/figures_s180_2026-11-16/fig_s180_3_axis_status.png` | figure | `f4f44f398f8f07cdc00292bfaa85d13188d25e5006e8adf8cbd4c5f5d380d45c` | YES | yes | report; deck; `/method` | — |
| `reports/final/figures_s180_2026-11-16/fig_s180_4_ph_bands.png` | figure | `6d5c2c048e7ae373c38cb933b264161e078f2e3c05f9cf23da61ad5421a3b91a` | YES | yes | report; deck | PH_CROSSWALK_UNVERIFIED_AI_DRAFTED caption |

## 5. State, lineage, NER, ledger evidence

| Path | Purpose | sha256 | Frozen? | Read-only? | Consumed by | Expected output |
|---|---|---|---|---|---|---|
| `docs/EVENT_IR_CONTRACT.md` | Event IR + invariants | `e8e44d9448a64c57fe3bdd5f26b2832dd4bb473d19a93509d3bb3b912c804a4c` | YES ("FINAL for the 21 Nov submission") | yes | `/method`; report | six invariants + open scopes |
| `reports/s179/state_inventory_FINAL_2026-11-15.md` | state coverage view | `6830a45eb1d99f1c2f9a46ddf020091e5c9655457c8e10eec638d75b16ce483f` | YES (FINAL) | yes | report state section; `/method` | coverage table |
| `reports/s179/state_dataset_fill_full_2026-11-14.json` | corpus fill rates (all-row) | `52ff2eb87f401d8a70529ead7c5cc37bdacb644fdc10c6d36d4762ea9c9510d1` | YES | yes | report fill table | per-family rates |
| `reports/s179/state_dataset_fill_full_D116v1_2026-11-14.json` | corpus fill incl. C_t v1 columns | `e26db6aa45f734d1d2b22b73d98c11e9b35c19798f49da051f90e133fd7ddd43` | YES | yes | report | per-family rates |
| `reports/s179/lineage_vnext_diff_full_2026-11-14.json` | vNext differential — DIAGNOSTIC | `5507b67e3e3e24d5aca476e0a94045bcb589c16686704007f37371687a17d617` | YES | yes | report lineage paragraph; coref flow | 29.3% only with "DIAGNOSTIC" |
| `reports/ner/culinaryner_kf_final_report.md` | NER TEST report | `2abafa7a713b9bc64dab3769ac3a587d5fcf5869ff5fb80027243fcdca513ab5` | YES (TEST evaluated once) | yes | report NER section; deck | TIE + leak finding |
| `reports/h_state/ledger_stats.json` | ledger counts | `ef85891bda5b2194bce84ce9d725765d9f83e72a111384aa5b3d7f2409581949` | NOT_EVIDENCED | yes | report D1 | 17,978 ACTIVE |
| `reports/final/FINAL_REPORT_DRAFT_S179_2026-11-11.md` | integrated report draft (H1/H3 text) | `7a6800c9b6ebce3ce4ce307448553eda15d755d343b3d9c3797ec0450eeaf511` | DRAFT | yes (protected original) | report base | RULE_NOT_MET wording |

## 6. Design and deployment specs

| Path | Purpose | sha256 | Frozen? | Read-only? | Consumed by | Expected output |
|---|---|---|---|---|---|---|
| `design/FINAL_DESIGN_SYSTEM.md` | palette, type, seven-state system | `95e2379654966136b9899027c63dd0d462e904e420908a62621323d287f5376f` | YES (binding on the build, D-139) | yes | all four routes | tokens |
| `design/MOTION_SPEC.md` | motion tokens, ΔS animation | `ccba509024269cab63af5a3b8b1158a75ab5a4db04939614fa6447c8fb48d780` | YES | yes | `/lab` | — |
| `design/FRONTEND_ARCHITECTURE.md` | component tree, TS interfaces | `9c8d385e63878c4e559cb9e71f9b12201a75dd97ca1104c13725bf3020eb2279` | YES | yes | all routes | — |
| `design/audit/tokens.json` | generated tokens | `4fe2ca51360eb0d1e84bf8bfcb91a073d5c5b7d37249fc6087fd063893327260` | YES | yes | CSS theme | — |
| `design/audit/palette.py` | palette generator | `554738a8d32eceaf65c472c001dd00de0847f4aa854353862d423066f3d901e8` | YES | yes | CI audit | — |
| `design/audit/emit.py` | token emitter | `7b3cfa75207e5298a4b9d57cc45129749d174e68649ef0affc7601f483a1a38b` | YES | yes | CI audit | — |
| `design/audit/inspect_fonts.py` | font coverage audit | `2a295a164a7fb6e176db1ccae5b81e87208d3fbb04b3844473e880e175e2e5f8` | YES | yes | CI audit | — |
| `design/audit/verify.py` | contrast/gamut verifier | `4401ce8fab82569fd738ba2188b8d5c4f06f0882da48050293491332594e031f` | YES | yes | CI audit | zero failures |
| `deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md` | snapshot-primary deployment | `20084ff8c09485bcfed7a5c89448e9ab2b56b667cb8d2365a89900943e5692dc` | YES | yes | deploy; `/api/health` badge | LIVE vs snapshot label |

## 7. Named as inputs but NOT on disk (17 Nov) — no hash possible

| Path | Named in | Status |
|---|---|---|
| `tools/build_demo_snapshot.py` | `deployment/FINAL_DEPLOYMENT_ARCHITECTURE.md` §4 | **absent** |
| `web/public/snapshot/` (signed snapshot JSON for Tomato A–D, the 8 scenarios) | same §4; master prompt §18 | **absent** — the precomputed JSON `/lab` is to be built against does not exist yet |
| `web/` (Next.js app) | master prompt §14 | **absent** |

## 8. Must NOT be shipped to the UI bundle or Vercel

`ledgers/data/EVD.jsonl`, `ledgers/data/KGE.jsonl` (BBC-derived rows are filtered at load time, not
file level — uploading violates D-003, master prompt §15–17) and anything under `data/raw/`. Not
hashed here: they are engine inputs on the presenter Mac, not UI/report inputs.

## 9. NOT_EVIDENCED / caveats

- Slide numbers; a recorded page-to-file mapping; frozen status of `reports/h_state/ledger_stats.json`
  and of the new `reports/s181/` files.
- Master prompt header names branch `kush/s179-finish-fixes`; the working tree is
  `kush/s181-explorer-build`. Hashes are for the latter.
- `src/culinarystate/**` and `registry/**` are frozen as whole trees (master prompt §23); only the
  files a builder reads directly are hashed above. A full-tree manifest: NOT_EVIDENCED in this pass.
