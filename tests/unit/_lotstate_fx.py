"""Synthetic SR Legacy fixture for the lot-state tests (values are invented for tests only, not USDA data)."""
from fractions import Fraction as F

from culinarystate.lotstate.sr_legacy import SRFood, SRLegacy, parse_portion

NUT = ("water", "protein", "fat", "carbohydrate", "sugars", "starch", "fibre", "ash", "sodium", "vitamin_c")


def food(fdc, desc, cat, **nut):
    return SRFood(fdc, desc, cat, {k: F(str(v)) for k, v in nut.items()})


def make_sr():
    foods = [
        food(1, "Onions, raw", "Vegetables and Vegetable Products", water=89, protein=1, fat=0, carbohydrate=9, sugars=4,
             starch=0, fibre=2, ash=1, sodium=4, vitamin_c=7),
        food(2, "Butter, salted", "Dairy and Egg Products", water=16, protein=1, fat=81, carbohydrate=0, sugars=0,
             fibre=0, ash=2, sodium=640, vitamin_c=0),
        food(3, "Sugars, granulated", "Sweets", water=0, protein=0, fat=0, carbohydrate=100, sugars=100, fibre=0, ash=0,
             sodium=0, vitamin_c=0),
        food(4, "Salt, table", "Spices and Herbs", water=0, protein=0, fat=0, carbohydrate=0, sugars=0, fibre=0, ash=100,
             sodium=38000, vitamin_c=0),
        food(5, "Oil, olive, salad or cooking", "Fats and Oils", water=0, protein=0, fat=100, carbohydrate=0, fibre=0,
             ash=0, sodium=2, vitamin_c=0),
        food(6, "Onions, dehydrated flakes", "Vegetables and Vegetable Products", water=4, protein=8, fat=0,
             carbohydrate=80, sugars=30, fibre=10, ash=3, sodium=20, vitamin_c=30),
        food(7, "Lemons, raw, without peel", "Fruits and Fruit Juices", water=89, protein=1, fat=0, carbohydrate=9,
             sugars=2, fibre=3, ash=0, sodium=2, vitamin_c=53),
        food(8, "Lemon juice, raw", "Fruits and Fruit Juices", water=92, protein=0, fat=0, carbohydrate=7, sugars=2,
             fibre=0, ash=0, sodium=1, vitamin_c=39),
        food(9, "Cheese, parmesan, grated", "Dairy and Egg Products", water=18, protein=29, fat=28, carbohydrate=13,
             sugars=1, fibre=0, ash=7, sodium=1800, vitamin_c=0),
        food(10, "Cheese, cheddar", "Dairy and Egg Products", water=37, protein=25, fat=33, carbohydrate=1, sugars=0,
             fibre=0, ash=4, sodium=650, vitamin_c=0),
        food(11, "Cheese, cream", "Dairy and Egg Products", water=54, protein=6, fat=34, carbohydrate=4, sugars=3,
             fibre=0, ash=1, sodium=320, vitamin_c=0),
        food(12, "Beef, ground, 80% lean meat / 20% fat, raw", "Beef Products", water=62, protein=17, fat=20,
             carbohydrate=0, fibre=0, ash=1, sodium=66, vitamin_c=0),
        food(13, "Beef, cured, dried", "Beef Products", water=50, protein=30, fat=5, carbohydrate=2, fibre=0, ash=10,
             sodium=3000, vitamin_c=0),
        food(14, "Spices, pepper, black", "Spices and Herbs", water=12, protein=10, fat=3, carbohydrate=64, fibre=25,
             ash=4, sodium=20, vitamin_c=0),
        food(15, "Peppers, sweet, red, raw", "Vegetables and Vegetable Products", water=92, protein=1, fat=0,
             carbohydrate=6, sugars=4, fibre=2, ash=0, sodium=4, vitamin_c=128),
        food(16, "Onions, frozen, chopped, cooked, boiled, drained, without salt", "Vegetables and Vegetable Products",
             water=91, protein=1, fat=0, carbohydrate=7, sugars=3, fibre=1, ash=0, sodium=4, vitamin_c=3),
        food(17, "Baby food, fruit, applesauce", "Baby Foods", water=88, protein=0, fat=0, carbohydrate=11, sugars=9,
             fibre=1, ash=0, sodium=2, vitamin_c=1),
        food(18, "Beverages, water, tap, drinking", "Beverages", water=100, protein=0, fat=0, carbohydrate=0, sugars=0,
             fibre=0, ash=0, sodium=0, vitamin_c=0),
    ]
    por_rows = [
        (1, 1, "1", "cup, chopped", "160"), (2, 1, "1", "cup, sliced", "115"), (3, 1, "1", "large", "150"),
        (4, 1, "1", "medium (2-1/2\" dia)", "110"), (5, 1, "1", "small", "70"),
        (6, 2, "1", "tbsp", "14.2"), (7, 2, "1", "cup", "227"), (8, 2, "1", "stick", "113"),
        (9, 3, "1", "cup", "200"), (10, 3, "1", "tbsp", "12.6"),
        (11, 4, "1", "tsp", "6"), (12, 5, "1", "tbsp", "13.5"),
        (13, 8, "1", "cup", "244"),
    ]
    portions = {}
    for pid, fdc, amt, mod, gw in por_rows:
        p = parse_portion(pid, fdc, amt, mod, gw)
        portions.setdefault(fdc, []).append(p)
    return SRLegacy({f.fdc_id: f for f in foods}, portions, "SYNTHETIC")
