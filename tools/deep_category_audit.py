"""Deep audit of RecipeDB2 ingredient categories — find systematic mislabelings."""
import csv
from collections import Counter, defaultdict

BASE = "/Users/bournesmartasfuck_kush/Desktop/CGAS/culinarystate/data/external"
fpath = f"{BASE}/recipedb2/Category_manually_labelled.csv"

# Known food category rules
VEGETABLE_WORDS = {"onion", "shallot", "garlic", "leek", "scallion", "celery", "carrot",
                   "potato", "tomato", "pepper", "cucumber", "zucchini", "eggplant",
                   "broccoli", "cauliflower", "spinach", "lettuce", "cabbage", "kale",
                   "radish", "turnip", "beet", "pea", "bean", "asparagus", "artichoke",
                   "corn", "squash", "pumpkin", "mushroom"}
FRUIT_WORDS = {"apple", "banana", "orange", "lemon", "lime", "cherry", "grape", "peach",
               "pear", "plum", "mango", "pineapple", "strawberry", "blueberry", "raspberry",
               "blackberry", "watermelon", "melon", "papaya", "kiwi", "fig", "date",
               "coconut", "avocado", "pomegranate", "cranberry", "apricot", "nectarine"}
HERB_WORDS = {"basil", "oregano", "thyme", "rosemary", "mint", "cilantro", "parsley",
              "dill", "sage", "tarragon", "chive", "bay leaf", "marjoram"}
DAIRY_WORDS = {"milk", "cheese", "cream", "butter", "yogurt", "whey", "curd"}

errors = []
categories = Counter()
cat_examples = defaultdict(list)

with open(fpath) as f:
    reader = csv.DictReader(f)
    for row in reader:
        ing = row.get("ingredient", "").strip().lower()
        cat = row.get("Dietrx_Category", "").strip()
        if not ing or not cat:
            continue
        categories[cat] += 1
        cat_examples[cat].append(ing)

        # Vegetable labeled as non-vegetable
        for veg in VEGETABLE_WORDS:
            if veg in ing and cat in ["Seafood", "Meat", "Dairy", "Spice", "Bakery"]:
                errors.append((row["ingredient"].strip(), cat, f"Contains '{veg}' → likely Vegetable"))
                break

        # Fruit labeled as non-fruit
        for fruit in FRUIT_WORDS:
            if fruit in ing and cat in ["Additive", "Seafood", "Meat", "Vegetable Tuber"]:
                errors.append((row["ingredient"].strip(), cat, f"Contains '{fruit}' → likely Fruit"))
                break

        # Dairy labeled as non-dairy
        for dairy in DAIRY_WORDS:
            if dairy in ing and cat in ["Seafood", "Vegetable", "Fruit"]:
                errors.append((row["ingredient"].strip(), cat, f"Contains '{dairy}' → likely Dairy"))
                break

        # Herb labeled as non-herb
        for herb in HERB_WORDS:
            if herb in ing and cat in ["Seafood", "Meat", "Dairy"]:
                errors.append((row["ingredient"].strip(), cat, f"Contains '{herb}' → likely Herb/Spice"))
                break

# Deduplicate
seen = set()
unique_errors = []
for e in errors:
    key = (e[0].lower(), e[1])
    if key not in seen:
        seen.add(key)
        unique_errors.append(e)

print(f"Total ingredients: {sum(categories.values())}")
print(f"Total categories: {len(categories)}")
print(f"\nAll categories:")
for cat, count in categories.most_common():
    print(f"  {cat:30s} {count:5d}")

print(f"\n\nMISLABELING ERRORS FOUND: {len(unique_errors)}")
print("-" * 70)
for ing, cat, reason in unique_errors:
    print(f"  '{ing}' → {cat} | {reason}")

# Category confusion matrix — ingredients appearing in multiple categories
print(f"\n\nDUPLICATE INGREDIENTS IN MULTIPLE CATEGORIES:")
ing_cats = defaultdict(set)
with open(fpath) as f:
    reader = csv.DictReader(f)
    for row in reader:
        ing = row.get("ingredient", "").strip().lower()
        cat = row.get("Dietrx_Category", "").strip()
        if ing and cat:
            ing_cats[ing].add(cat)

dupes = {ing: cats for ing, cats in ing_cats.items() if len(cats) > 1}
print(f"  {len(dupes)} ingredients appear in multiple categories")
for ing, cats in sorted(dupes.items())[:20]:
    print(f"    '{ing}' → {', '.join(sorted(cats))}")
