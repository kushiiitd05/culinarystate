# Local NER artifact inventory — 12 November 2026

**AI_PRECHECKED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.** T3-C09-R1 remains PARTIAL.

The restored bundle was inspected locally by paths and schema; raw source text was not emitted.

| Local artifact | What it contains | Why it does not close the requested comparison |
|---|---|---|
| `data/interim/evidence_first/foodcom_full_with_spans.csv` | Procedural screening rows: instruction spans, process families and EVD fields | These are not learned ingredient-NER spans. |
| `data/interim/wikibooks/ner_silver.jsonl` | `rec_id/kind/text/spans` silver/source annotation records | Silver annotation is not checkpoint inference. |
| `gpu/ner_tasteset/runs/*.pred.jsonl` | Archived TASTEset `recipe/gold/pred` records | Single-family artifacts, without demonstrated identity to the current frozen checkpoint or cross-family coverage. |
| `reports/ner_v2/_final_sys/*.jsonl` and `_dm_raw/*.jsonl` | Candidate scores and linker/model-response records | They do not provide the full-corpus ingredient-NER span stream being requested. |

No learned checkpoint (`.pt`, `.pth`, `.bin`, `.safetensors` or `config.json`) was found under the inspected
local `data`, `gpu` and NER-report roots. `data/interim/models` and `data/interim/embeddings` are absent.
The bundle-builder separates those optional model assets into tier 2; it does not promise that the later
server `data/derived` corpus span outputs are included. A filename containing “spans” is not sufficient provenance.

The new frozen-D5 ingredient-line leakage check is complete in `d5_frozen_split_leakage_v3.md`. It measures
exact normalized surface exposure of nine Wikibooks ingredient lines, not NER-versus-Rung-A inference agreement.
The earlier TASTEset gold/lexicon proxy remains a separately labelled proxy, not a substitute full-family result.

To close T3-C09-R1 locally, restore the actual persisted current-checkpoint Food.com/Wikibooks span outputs,
or restore the exact checkpoint/tokenizer/configuration and run a separately recorded local inference job
on a declared corpus/sample. Report checkpoint identity, alignment denominators and provenance, with no accuracy
claim from model/lexicon agreement. Do not quietly rename archived, silver or procedural spans as learned output.

Machine-readable inventory and selected input hashes: `ner_local_artifact_inventory_2026-11-12.json`.


## Later same-day optional-bundle check

The inventory above records the earlier state. The optional tier-2 archive was subsequently obtained and checksum-verified. It contains DeBERTa-v3-base+CRF metadata/weights, whereas the recorded primary checkpoint is DeBERTa-base+CRF (sha256 prefix `582c056ac20625ac`). Only configuration metadata was extracted. It was not substituted or used for inference. See `optional_model_bundle_check_2026-11-12.json`. The directory-presence statements above are historical; the exact primary model and current cross-family inference streams remain unavailable in the inspected artifacts.
