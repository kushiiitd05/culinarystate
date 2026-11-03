# S160 build note — freeze preparation, Step 35 v2 package, evaluation scaffolds

2026-11-03. Branch `cloud/s160-freeze-prep`, stacked on `cloud/s159-simulator-core`. This is the last cloud session before **checkpoint H-A**.
Everything is a DRAFT: nothing was frozen, sealed or signed by an agent.

Workflow (D-045): AI worker "ksh" built A–C; AI worker "prv" built D and cross-reviewed A–C; the coordinator verified both.
Also recorded on this branch: D-049 (block F), D-050 (block G and scipy), D-051 (THR-04K signed), D-052 (sim_aa_1 selected, with a signed 26.0 record).

## What was built

| Part | Files | Content |
|---|---|---|
| A — 15.0 | `reports/step15/pre_freeze_rulings_DRAFT.md` | Options with exact citations, plus labelled AI recommendations for each item. Nothing is decided and there is no D-number. C2-a: unverified E3 is bootstrap-only. H-3: per-claim-family strictest feasible split. X-1: tier crosswalk. G-1 and K-1: reuse signed THR-08A-08/15/20, K = 10. The RESERVED fraction is **UNKNOWN; Kush supplies it.** STUDY_THEN_CELL is recommended because the literal cell key splits one paper's cells across both sides. |
| B — 15a.R | `src/culinarystate/lineage/reserved_seal.py`, `tools/step15a_R_seal.py` | Deterministic, group-level, hash-committed seal. **It refuses today** because there is no signed 15.0 entry. It requires `--execute`; a signed 15.0 entry approved by Kush with the fraction, unit, stratify and seed-hash markers; a seed file outside git; and sealed-list and commitment paths outside protected or tracked areas. The seed and the reserved ids never go into git. It has not been run. |
| C — Step 35 v2 | `reports/step35/{preregistration_35_0_v2_draft.md,35_0_v2_threshold_rows.csv,preregistration_35_0_v2_package.sha256.UNSIGNED.json,35_0_v2_signature_sheet.md}`, `src/culinarystate/representation/explicit_runner.py` | v2 includes v1 byte-unchanged (sha256 `47c6ba6e…`) and quotes D1–D8 and D-040. The D-041 amendments appear only as an unadopted Appendix P. The UNSIGNED record binds 21 inputs. `run_explicit_baseline` refuses every task until a SIGNED record names Kush and Parv. |
| D — evaluation scaffolds | `src/culinarystate/evaluation/{splits,leakage,bootstrap_diag,bakeoff,composition,abstention_spec}.py`, `reports/step34/rollout_abstention_spec_v1_DRAFT.json` | Group-disjoint splits (union-find, property-tested); counts-only leakage checks; reserved-group exclusion verified against the 15a.R commitment; HEADLINE mode is refused until 15b. A 29-diag NON_CITABLE runner that refuses every snapshot today. A Step 30 registry and a paired cluster bootstrap with no default margin. The 34a composition test (ρ and c_floor required). The 34c abstention spec is unsigned and every threshold is UNKNOWN. |

**Step 35 v2 hashes for signature:**

| Item | sha256 |
|---|---|
| Protocol | `009c9047ce78da21dd7d7061a64bc9fbb86d38d3eada5b3d8c9769ce5dd60145` |
| UNSIGNED record | `8885a63a0dc0181d4aec5d05fea124776d6a0afbbe5a1e162da7cbb9a4b582e5` |
| Rows THR-35P-01..43 | `8b696b08…` |

## AI cross-review (`reports/step15/S160_ai_review.md`)

| ID | Severity | Fix |
|---|---|---|
| R1 | medium | The seal accepted any Approver line containing "kush" (it would match "Kush (pending confirmation)") |
| R1b | low | Marker lines inside a code block were read as a ruling |
| R2 | medium | The Step 35 runner accepted any two signer names, including "ksh"/"prv"; it now requires Kush and Parv |
| R3 | low | Two plan-line citations were wrong |
| R4 | low | The D1 coverage list did not match the sign-off sheet |

Open items O1–O5 and I2 are in block I.

## Verification

| Check | Result |
|---|---|
| Full unit suite (thread caps) | **3185 passed**, 17 skipped, 1 deselected. The 1 failed + 11 errors are missing bundle files, unchanged. |
| Ledger guard | 7/7 |
| Attribution lines | 0 |
| Pre-S160 code edited | 0 |
| Signed Step 35 record present | none, so every task is refused (by design) |

## Needs human: checkpoint H-A

Review-sheet block I.
