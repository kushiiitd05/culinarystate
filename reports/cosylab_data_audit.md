# CoSyLab Public Data & API Audit

**Date:** 2026-10-19
**Purpose:** Inventory of all publicly available data from CoSyLab (IIIT-Delhi) GitHub repos and
web services, with vulnerabilities and data points useful for CulinaryState.

---

## 1. GitHub Repositories (26 public repos under `cosylabiiit/`)

### 1A. NER & Recipe Knowledge (DIRECT USE)

| Repo | Data | Size | License | Relevance |
|------|------|------|---------|-----------|
| `RecipeDB3_NER_Research_Paper` | Ingredient + Instruction annotated CSVs, DeBERTa + spaCy notebooks | ~26K phrases | **NONE** | NER vulnerability analysis (10 issues found); annotation data NOT downloaded |
| `Recipe_NER_DL` | `final_train.csv`, `final_test.csv`, `Machine_Annotated_*.csv`, augmentation notebook, saved BERT results | ~6K manual + augmented | **NONE** | Predecessor NER; augmentation code reveals leakage bugs |
| `Recipedb-companion-data` | AllRecipes + FOOD.com tagged ingredients (7 labels: NAME, QUANTITY, UNIT, STATE, **SIZE**, DF, TEMP) | ~450KB train, ~137KB test | **NONE** | Original tagged data; proves SIZE label exists but dropped in RecipeDB3 |
| `recipe-knowledge-mining` | AllRecipes + FOOD.com complete datasets, combined results, ingredient phrases (>10MB) | large | **NONE** | Named entity approach paper data; relation extraction sub-folder |

### 1B. Ingredient Categories & Sustainability

| Repo | Data | Size | License | Relevance |
|------|------|------|---------|-----------|
| `RecipeDB2` | `Category_manually_labelled.csv` — ingredient→DietRx category mappings | 507KB (~5K+ rows) | **NONE** | Ingredient categories; **VULNERABILITY: "shallot" labeled as Seafood** and other errors |
| `SustainableFoodDB` | Recipe carbon footprints, ingredient-level CFP, RecipeDB ingredient categories, preprocessed data | multiple CSVs | **NONE** | Sustainability evidence; ingredient category crosswalk |
| `NOVA_Food_Processing` | 3 nutrient datasets (102-nutrient, 65-nutrient, FDA) in numerical and textual form | CSVs | **NONE** | NOVA food processing classification; nutrient data |

### 1C. Taste & Molecule Prediction

| Repo | Data | Size | License | Relevance |
|------|------|------|---------|-----------|
| `bittersweet` | Bitter/sweet molecule train/test TSVs, trained models | ~4 files | **AGPL-3.0** ✅ | Taste prediction; actually licensed and usable |
| `SweetpredDB` | Sweetness prediction database + trained model | 59KB CSV | **NONE** | Sweet molecule data |
| `UmamiPredict` | Umami datasets (3 encodings), SMOTE experiments | CSV | **NONE** | Umami taste prediction |
| `MultiTox` | Toxicity prediction data, ESM2 embeddings | CSV + ZIP | **NONE** | Molecule toxicity |
| `AllerStack` | Allergen prediction train/test/validation data (ESM embeddings) | CSVs + ZIP | **NONE** | Food allergen prediction |
| `ToxinPredictor` | Toxin prediction source code | code only | **NONE** | Toxicity methods |

### 1D. Clustering & Patterns

| Repo | Data | Size | License | Relevance |
|------|------|------|---------|-----------|
| `Hierarchical-Clustering-Ingredients` | Australian + Indian Subcontinent ingredient patterns | 2 CSVs | **NONE** | Regional cuisine patterns |
| `biclique-clustering` | Biclique clustering algorithm | code only | **MIT** ✅ | Algorithm; properly licensed |
| `Universal-statistical-laws-governing-culinary-design` | Culinary laws paper data (README only visible) | unclear | **NONE** | Statistical laws paper |
| `Nutritional-Estimation-In-Recipes` | Ingredient matching from nutrition tables, nutrition calculation | sub-folders | **NONE** | Nutritional estimation methods |

### 1E. Other

| Repo | Data | License | Notes |
|------|------|---------|-------|
| `spice-disease-associations` | Annotated + unannotated spice-disease sentences | **NONE** | Biomedical NER; spice health |
| `foodevpred` | Protein features (ProtT5 embeddings) + split indices | **NONE** | Food evolution prediction |
| `drugADR` | Drug ADR data + code | **Apache-2.0** ✅ | Drug adverse reactions |
| `chemopy` | ChemoPy package (descriptor calculator) | **NONE** | Chemistry descriptors |
| `Open_Food_Facts_ML` | ML notebooks for Open Food Facts | **NONE** | OFF analysis methods |
| `design-a-diet-iiitd` | Diet design web app | **NONE** | DietRx interface |
| `BitterSweet-WebServer` | Web server for BitterSweet | **NONE** | Web interface |
| `chemoinformatics-2018` | Course assignments + tutorials | **NONE** | Teaching material |
| `utilities` | Anaconda + ChemoPy setup guides | **NONE** | Setup docs |

---

## 2. Web Services & APIs

Found via `cosylab.iiitd.edu.in`:

| Service | URL | What it provides | API? |
|---------|-----|-----------------|------|
| **Foodoscope** | foodoscope.com | Unified computational gastronomy APIs (recipes, flavors, nutrition, health, sustainability) | **YES — this is their main API platform** |
| **RecipeDB** | cosylab.iiitd.edu.in/recipedb/ | 100K+ recipes with cuisine/ingredient/process structure | Web interface; API via Foodoscope |
| **RecipeDB2** | cosylab.iiitd.edu.in/recipedb2/ | Next-generation RecipeDB | Web (SPA) |
| **FlavorDB** | cosylab.iiitd.edu.in/flavordb/ | Flavor molecules in food ingredients | Web search |
| **FlavorDB2** | cosylab.iiitd.edu.in/flavordb2/ | 25,595 flavor molecules, 936 ingredients, 34 categories; FEMA/FooDB flavor profiles; structure search via SMILES | Web search + autocomplete (implies API) |
| **CulinaryDB** | cosylab.iiitd.edu.in/culinarydb/ | Structured recipes for research | Web |
| **DietRx** | cosylab.iiitd.edu.in/dietrx/ | Health impact of dietary ingredients | Web |
| **SpiceRx** | cosylab.iiitd.edu.in/spicerx/ | Health effects of herbs and spices | Web |
| **BitterSweet** | cosylab.iiitd.edu.in/bittersweet/ | Bitter/sweet molecule prediction (ML web server) | Web interface |
| **SweetPred** | cosylab.iiitd.edu.in/sweetpred/ | Sweetness intensity/quality prediction | Web |
| **UmamiDB** | cosylab.iiitd.edu.in/umami/ | Umami taste molecules | Web |
| **Carbon Footprint** | cosylab.iiitd.edu.in/SustainableFoodDB/ | Recipe carbon footprints | Web |
| **Food Processing** | cosylab.iiitd.edu.in/food-processing/ | Processing methods impact | Web |
| **AllerStack** | cosylab.iiitd.edu.in/allerstack/ | Allergenicity prediction | Web |
| **ToxinPredictor** | cosylab.iiitd.edu.in/toxinpredictor/ | Food toxicity prediction | Web |
| **MilletDB** | cosylab.iiitd.edu.in/millet/ | Millets + nutrition | Web |
| **Ratatouille** | cosylab.iiitd.edu.in/ratatouille/ | AI recipe generation | Web |
| **Recipe Chatbot** | cosylab.iiitd.edu.in/recipe-voice-bot/ | Voice recipe assistant | Web |

---

## 3. Vulnerabilities Found (AI/Data Science Issues)

### 3A. NER Pipeline (10 issues — see `recipedb3_vulnerability_analysis.md`)

| ID | Issue | Severity |
|----|-------|----------|
| V1 | Test-set model selection (best of 15 epochs on test) | CRITICAL |
| V2 | SIZE label dropped (1,476 tokens → O) | HIGH |
| V3 | Augmentation leakage (13.6% near-duplicates across split) | CRITICAL |
| V4 | Head-heavy test (70.4% NAME seen in train) | MEDIUM |
| V5 | No validation set (test = dev) | HIGH |
| V6 | Test set augmentation in predecessor | HIGH |
| V7 | Wrong variable saved in augmentation | MEDIUM |
| V8 | Silent error swallowing (KeyError pass) | MEDIUM |
| V9 | No recipe-level grouping in augmentation | HIGH |
| V10 | Copy-pasted cocktail code without review | LOW |

### 3B. Ingredient Categories (RecipeDB2)

| Issue | Evidence |
|-------|----------|
| **Mislabeled ingredients** | "shallot" labeled as Seafood (should be Vegetable); "cherry" as Additive |
| **Inconsistent category granularity** | Mix of broad (Vegetable, Fruit) and specific (Additive-Salt, Additive-Sugar, Additive-Vinegar, Beverage-Alcoholic, Beverage Caffeinated) |
| **No validation** | Single CSV with no quality metrics or inter-annotator agreement |

### 3C. Licensing Issues

| Issue | Evidence |
|-------|----------|
| **22 of 26 repos have NO license** | Public code with no license = all rights reserved by default |
| **Only 4 repos have licenses** | bittersweet (AGPL-3.0), drugADR (Apache-2.0), biclique-clustering (MIT), — 3 usable |
| **Data redistribution unclear** | Datasets in unlicensed repos cannot be legally redistributed |

### 3D. Reproducibility Issues

| Issue | Evidence |
|-------|----------|
| **No environment specs in most repos** | Only bittersweet and drugADR have requirements files |
| **Hardcoded Kaggle paths** | RecipeDB3 NER notebook uses `/kaggle/input/` paths |
| **Missing data provenance** | No documentation of how annotations were created or validated |
| **Python 2.7 dependency** | bittersweet requires Python 2.7 (its own README says so) |

---

## 4. What We Can Use for CulinaryState

### Immediately usable (properly licensed):
1. **bittersweet** (AGPL-3.0) — bitter/sweet prediction data as EVD source
2. **biclique-clustering** (MIT) — algorithm for ingredient clustering
3. **drugADR** (Apache-2.0) — drug adverse reaction patterns

### Usable for analysis/comparison (public code, read-only):
4. **All NER code** — vulnerability analysis already done
5. **RecipeDB2 categories** — cross-reference against our FoodOn-linked categories
6. **NOVA nutrient data** — compare against our USDA/FDC evidence

### Requires professor permission (no license):
7. **RecipeDB3 annotation data** — waiting on H1 email
8. **Companion data** (AllRecipes + FOOD.com tags) — no license
9. **Recipe_NER_DL datasets** — no license
10. **SustainableFoodDB data** — no license

### Accessible via web (Foodoscope API):
11. **Foodoscope API** — needs API key from professor
12. **FlavorDB2 search** — 25,595 molecules, queryable

---

## 5. Recommended Actions

1. **Show professor the vulnerability analysis** — 10 concrete issues in their NER pipeline
2. **Ask about Foodoscope API access** — add to H1 email or ask in person
3. **Use bittersweet data** (AGPL-3.0) for MOL_HAS_TASTE evidence
4. **Cross-reference RecipeDB2 categories** against our FoodOn-linked ING to find their labeling errors
5. **Document all findings** for presentation under "evaluation methodology" section
