# Step 35 bound inputs and packages on three hosts (S179, T7-C01-R5)

Status: **AI_DRAFTED, read-only check**. Same tool on all three hosts: `tools/s178_manjot_env_check.py`, loaded
unchanged with only its output path changed. No recipe text, no private address.

Files:
- manjot `reports/s178/manjot_env_inputs_check.json` (S178);
- Mac `reports/s179/env_inputs_check_mac_S179.json`;
- vinayak `reports/s179/env_inputs_check_vinayak_S179.json` (clone `~/Kush/cs_s179` at bf2e635), both run 2026-11-10.

## Inputs (path × host × sha256)

| Input | Mac | manjot | vinayak |
|---|---|---|---|
| 21 Step 35 v2 bound files (template `preregistration_35_0_v2_package.sha256.UNSIGNED.json`) | 21/21 present, 21/21 sha256 match | 21/21, 21/21 | 21/21, 21/21 |
| `ledgers/recipe_base/recipe_base_v1.parquet` (frozen `5545da58…`) | present, match | present, match | **absent** |
| `ledgers/recipe_identity/gold_firewall_v1.parquet` (frozen `a4353f5c…`) | present, match | present, match | **absent** |
| `ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet` (frozen `98b3b43f…`) | present, match | **absent** | **absent** |

## Packages (importable in the project Python)

| Package | Mac (base 3.11.8) | manjot (.venv312 3.12.3) | vinayak (.venv311 3.11.18) |
|---|:-:|:-:|:-:|
| numpy, pandas, pyarrow, scipy, pytest, jsonschema | yes | yes | yes |
| sklearn, hypothesis, lxml, requests, tqdm | yes | no | yes |
| torch, rdkit, matplotlib, networkx, statsmodels, yaml | yes | no | no |
| lightgbm, transformers | no in base; **yes in `recsys_env`** (lightgbm 4.6.0, transformers 4.57.6) | no | no |
| faiss, rank_bm25, sentence_transformers, tabpfn, xgboost | no | no | no |

- **Project modules:** all import on the Mac and on vinayak. On manjot, `culinarystate.molecules.pubchem` fails.
- **Ollama:** vinayak serves `qwen2.5:7b-instruct`, digest pinned in RUN-S179-PIN-001. manjot has a server but not
  that tag. The Mac has none.

## Reading

- **Mac** is the only host with every bound input sha256-equal to its frozen hash and every needed package
  (base + `recsys_env`). This is consistent with the S178 agent lean "Route B on the Mac".
- **manjot** lacks the ingredient-mentions parquet and the ML packages. Installing them needs the install decision
  (T9-C25-R5, human).
- **vinayak** lacks all three recipe ledgers. It is the LLM run host only.

The Route B host is a **human decision**. No package was installed and no file was copied by this check.
