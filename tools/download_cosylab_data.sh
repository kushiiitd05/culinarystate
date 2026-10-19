#!/bin/bash
# Download all publicly available CoSyLab data from GitHub API
# Run: bash tools/download_cosylab_data.sh
# Requires: gh (GitHub CLI) authenticated

set -e
BASE="/Users/bournesmartasfuck_kush/Desktop/CGAS/culinarystate/data/external"

download() {
    local repo="$1" path="$2" dest="$3"
    local dir=$(dirname "$dest")
    mkdir -p "$dir"
    echo "  $repo/$path -> $dest"
    gh api "repos/cosylabiiit/$repo/contents/$path" --jq '.content' 2>/dev/null | base64 -d > "$dest" 2>/dev/null
    if [ ! -s "$dest" ]; then
        echo "    WARN: empty file (may be >1MB, try git clone for this one)"
    fi
}

echo "=== 1. Bittersweet (AGPL-3.0) ==="
for f in bitter-train.tsv bitter-test.tsv sweet-train.tsv sweet-test.tsv; do
    download bittersweet "data/$f" "$BASE/bittersweet/$f"
done
download bittersweet LICENSE "$BASE/bittersweet/LICENSE"

echo ""
echo "=== 2. Companion NER Data (AllRecipes + FOOD.com) ==="
for f in ar_gk_train.tsv ar_gk_test.tsv ar_train.tsv ar_test.tsv gk_train.tsv gk_test.tsv README.md; do
    download Recipedb-companion-data "$f" "$BASE/cosylab_companion/$f"
done

echo ""
echo "=== 3. Recipe_NER_DL (predecessor NER) ==="
for f in datasets/final_train.csv datasets/final_test.csv datasets/Machine_Annotated_train.csv datasets/Machine_Annotated_test.csv final_train_augmented.csv; do
    fname=$(basename "$f")
    download Recipe_NER_DL "$f" "$BASE/recipe_ner_dl/$fname"
done

echo ""
echo "=== 4. RecipeDB2 (ingredient categories) ==="
download RecipeDB2 Category_manually_labelled.csv "$BASE/recipedb2/Category_manually_labelled.csv"

echo ""
echo "=== 5. NOVA Food Processing (nutrient data) ==="
for f in "Data/Numerical/Data/65_Nutrients_Data.csv" "Data/Numerical/Data/FDA_Nutrients.csv" "Data/Numerical/Data/102_Nutrients_Data.csv" "Data/Textual/Data/102_Nutrients.csv" "Data/Textual/Data/65_Nutrients.csv" "Data/Textual/Data/FDA_Nutrients.csv"; do
    fname=$(basename "$f")
    dir=$(echo "$f" | sed 's|Data/||;s|/Data/.*||' | tr '[:upper:]' '[:lower:]')
    download NOVA_Food_Processing "$f" "$BASE/nova_food_processing/${dir}_${fname}"
done

echo ""
echo "=== 6. SustainableFoodDB ==="
for f in "Data/Recipe_cfp.csv" "Data/Recipe_ingredient_cfp.csv" "Data/RecipeDB_ingredient_category.csv" "Data/Sueatable_preprocessed_data.csv"; do
    fname=$(basename "$f")
    download SustainableFoodDB "$f" "$BASE/sustainablefooddb/$fname"
done

echo ""
echo "=== 7. Hierarchical Clustering Ingredients ==="
for f in "patterns_ex/Australian_Pattern.csv" "patterns_ex/Indian_Subcontinent_Pattern.csv"; do
    fname=$(basename "$f")
    download Hierarchical-Clustering-Ingredients "$f" "$BASE/hierarchical_clustering/$fname"
done

echo ""
echo "=== 8. Spice-Disease Associations ==="
for f in data/annotated-sentences.tsv data/unannotated-sentences.tsv; do
    fname=$(basename "$f")
    download spice-disease-associations "$f" "$BASE/spice_disease/$fname"
done

echo ""
echo "=== 9. SweetpredDB ==="
download SweetpredDB SweetpredDB.csv "$BASE/sweetpreddb/SweetpredDB.csv"

echo ""
echo "=== 10. AllerStack ==="
for f in Data/test_data_1727.csv Data/train_data_1727.csv Data/validation_data_433.csv; do
    fname=$(basename "$f")
    download AllerStack "$f" "$BASE/allerstack/$fname"
done

echo ""
echo "=== 11. recipe-knowledge-mining ==="
for f in ar_complete_dataset.tsv gk_complete_dataset.tsv gk_ingredient_phrases.csv Different_Models_Combined_Results.csv; do
    download recipe-knowledge-mining "$f" "$BASE/recipe_knowledge_mining/$f"
done

echo ""
echo "=== 12. drugADR (Apache-2.0) ==="
download drugADR LICENSE "$BASE/drugadr/LICENSE"

echo ""
echo "=== DONE ==="
echo "Files downloaded to: $BASE/"
find "$BASE" -name "*.csv" -o -name "*.tsv" | wc -l
echo "total CSV/TSV files"
du -sh "$BASE"
