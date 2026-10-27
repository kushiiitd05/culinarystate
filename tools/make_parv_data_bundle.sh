#!/usr/bin/env bash
# Build the non-git data bundle for a new clone (Parv). Run from the repo root.
#   tools/make_parv_data_bundle.sh [OUT_DIR]      default OUT_DIR=~/Desktop/PARV_DATA_BUNDLE
# Tier 1 = required (extract in the repo root). Sibling = BBC raw files the tools read from ../a1 (extract in the repo's PARENT folder).
# Tier 2 = optional heavy files (models, embeddings, work files); everything in Tier 2 can be regenerated.
set -euo pipefail
OUT="${1:-$HOME/Desktop/PARV_DATA_BUNDLE}"
mkdir -p "$OUT"
T1=( data/external data/raw
     data/interim/gutenberg data/interim/evidence_first
     ledgers/recipe_base
     exports/evd/evd_export_v1.jsonl
     annotation/duplicate_calibration annotation/gold )
# recipe_identity: only the parquet files (no run/ folder, no .pkl work files)
while IFS= read -r f; do T1+=("$f"); done < <(ls ledgers/recipe_identity/*.parquet)
# any other data/interim folder except models and embeddings
for d in data/interim/*/; do case "$d" in data/interim/models/|data/interim/embeddings/|data/interim/gutenberg/|data/interim/evidence_first/) ;; *) T1+=("${d%/}");; esac; done
for f in data/interim/*; do [ -f "$f" ] && T1+=("$f"); done
tar -cf - "${T1[@]}" | gzip -1 > "$OUT/culinarystate_tier1_extract_in_repo_root.tar.gz"
( cd .. && tar -cf - "a1/A1 3/data/raw/recipes_raw.jsonl" "a1/A1 3/data/processed/recipes_processed.jsonl" | gzip -1 > "$OUT/a1_sibling_extract_in_repo_parent_folder.tar.gz" )
tar -cf - ledgers/recipe_semantics features data/interim/models data/interim/embeddings \
          ledgers/recipe_identity/run ledgers/recipe_identity/*.pkl reports/ner/_raw_all reports/ner/_raw_export reports/ner/_raw_v2 \
  | gzip -1 > "$OUT/culinarystate_tier2_optional_extract_in_repo_root.tar.gz"
( cd "$OUT" && shasum -a 256 *.tar.gz > SHA256SUMS.txt && ls -l *.tar.gz | awk '{print $5, $9}' )
