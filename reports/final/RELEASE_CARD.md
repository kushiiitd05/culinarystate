# Release card (SSOT §257A.16), counts only (S179, T9-C24-R1)

Status: **AI_DRAFTED**. This card declares what exists at `kush/s179-finish-fixes`; it is not an approval, and
nothing listed here is a public release yet. Unknown fields read **UNKNOWN**. No recipe text is shown. Licences are
as recorded in `registry/recipe_source_usage_registry_v1.csv` (paragraph accepted in D-079:
`reports/final/sections/S179_licence_and_split_labels_DRAFT.md` §1).

Updated 2026-11-11 against D-085..D-092. D5 now has an AI-delegated freeze and run; it has no human sign-off.
Labels for its results: **NON_CITABLE / MODEL_ASSISTED_GOLD / NO_HUMAN_SIGNOFF_D085**.
Both H1 and H3 are RULE_NOT_MET. The original scorer leaves H1 NOT_COMPUTED; D-092 cites the separate rung-blind
resolution supplement. Both artifacts are retained in `reports/del5/d5_score_v1_D085/`.

Shared versions (all five artefacts):
- **Ledger schema:** `schema_version 1.0.0` (`ledgers/schemas/*.schema.json`; UNIT has the additive D-079 enum).
- **Ontology:** ING 2,048 ACTIVE (`ING.jsonl` sha256 `ef439951…`), ALIAS 4,103 ACTIVE (`65d89c0d…`), PROC 156
  ACTIVE (`b9248bf2…`), UNIT `2073074d…`.
- **Quantity database:** USDA FoodData Central SR Legacy, April 2018 CSV release
  (`data/raw/fdc/sr_legacy_csv_2018-04.zip`).
- **Split registry:** `registry/split_registry_v1.csv` sha256 `88b521bb…`.
- **Human gold revision:**
  - P1 pilot: 7 pairs, HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND, verdict HANDBOOK_REVISION_REQUIRED;
  - dev gold: pilot_20 Gold-v1.1 (AI-assisted, human-reviewed) and Food.com AI-assisted v1.1 (20).

  No independent human gold exists.

| Field | Recipe base v1 | EVD export v1 | D5 benchmark v1 | Physical layers L1 / L2 (v06) | NER corpus outputs |
|---|---|---|---|---|---|
| dataset_version | `recipe_base_v1.parquet` sha256 `5545da58…`; 612,782 recipes | `evd_export@1.0.0`, `exports/evd/evd_export_v1.jsonl` sha256 `e61d7db4…`; 17,978 rows (ledger `5b3b1939…`, 18,156 ids, 57,280 version lines) | **NOT RELEASED**: 74 questions, AI-reviewed/frozen D-090; D5-BENCH-2026-11-10 and supplementary 10b | L1 `condition-binding-L1-0.3.1-draft` (endpoint-cues 0.3.0); L2 `scenario-layer-L2-0.5.0-draft`; files `reports/step26/*_S179_v06.json` | `reports/ner_v2/ner_corpus_counts_S174.json`: Food.com 4,129,433 lines (4,098,353 with FOOD), Wikibooks 32,036, TASTEset 3,788 |
| schema_version | recipe base schema sha256 `3074955c…` (07H-R freeze) | EVD schema 1.0.0 | D5 frozen CSV files and reference hashes in freeze 10b | counts schemas validated 100 % (384 / 384 / 768 / 768 files) | NER_CORPUS_COUNTS record |
| ontology_version | as shared | as shared + SVAR duplicate mapping `4e60d1c6…` | as shared | `registry/proc_family_registry_v1.csv` (`e6b45ed2…`) | ING / ALIAS at S174 (UNKNOWN exact hash) |
| quantity_database_version | n/a | SR Legacy 2018-04 (portion and retention links) | n/a | n/a | n/a |
| source_snapshot_date | freeze manifest 2026-10-22 (`reports/step07/step07hr_freeze_manifest.json`) | manifest 2026-10-22 | n/a | runs 2026-11-10 (RUN-S179-PHYS6-*, BBC6-*) | 2026-11-08 (RUN-S174-003) |
| annotation_model / prompt versions | none (rule parsers; normaliser fingerprint in the freeze manifest) | none (rule extraction and imports) | qwen2.5:7b-instruct `845dbda0…`; e5-large-v2 revision `f169b11e…`; RUN-S179-D5-001, 346 answer records | none (no LLM; scenario defaults AI-recalled and unverified, NEG-0043) | DeBERTa-base + CRF, TASTEset train, DEV F1 0.940, model sha256 prefix `582c056a` |
| human gold revision | n/a | 0 of 40 literature rows hand-verified (DEL-1) | S gold AI_DRAFTED_GOLD, 24 questions; no independent human gold (D-090) | none | TASTEset gold (third party) |
| split registry hash | n/a | `88b521bb…` (29-diag rows) | `88b521bb…` remains draft-era registry; frozen benchmark files define actual 74 questions; registry refresh open | n/a (descriptive census) | NER TEST frozen before evaluation (commit 4ee0582) |
| licence / redistribution | mixed per source family: BBC LOCAL_RESEARCH_ONLY; Food.com and TASTEset LICENCE_UNVERIFIED; Wikibooks CC BY-SA 4.0; Gutenberg public domain (US). Counts only are redistributed | USDA public domain; Phenol-Explorer redistribution needs the authors' permission, so derived counts and ids only | questions and gold ids only; recipe text git-ignored | counts only; BBC records stay on the Mac (D-003) | counts only; spans stay on the servers or the Mac |
| known limitations | identity ledger provisional (07I-C kappas 0.571 / 0.588); near-duplicate leakage not controlled | G08-3 FAIL (lineage edges provisional); DEL-2 D7 = D1 on raw Phenol-Explorer (NEG-0050) | H1 n=24, AI self-consistency only; 22/24 S questions Gutenberg; near-duplicate leakage not controlled; H1/H3 RULE_NOT_MET; NEG-0051; claim audit NOT_RUN; compatible-recall inconsistency flagged in D4 section | mostly UNKNOWN by design; Layer 2 values are scenario brackets, not measurements | DEV F1 on TASTEset only; UNIT spans far below QUANTITY spans (NEG-0036) |

Not covered: BBC-derived corpus outputs are local-only and are never part of a public release (D-003).
