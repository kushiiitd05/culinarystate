#!/usr/bin/env python3
"""STEP 07I: structural-class map for the existing TOOL vocabulary (deterministic keyword rules over canonical_name + existing category; unknown stays UNKNOWN/OTHER -> registry/recipe_tool_structural_class_map_v1.csv)."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = [("MEASUREMENT_TOOL", r"thermometer|scale|timer|measur|jug|cup\b|spoon set"), ("PRESSURE_EQUIPMENT", r"pressure|instant pot|autoclave"), ("COOLING_APPLIANCE", r"fridge|freezer|refrigerat|cooler|ice cream (maker|machine)"),
         ("MECHANICAL_APPLIANCE", r"blender|mixer|processor|grinder|juicer|mill\b|stick blender|food mill|mincer|slicer machine|spiralizer"), ("HEATING_APPLIANCE", r"oven|hob|stove|microwave|grill|toaster|air.?fryer|fryer|kettle|griddle|barbecue|bbq|hotplate|cooker|steamer|rice cooker|slow cooker|broiler"),
         ("FERMENTATION/STORAGE_EQUIPMENT", r"ferment|crock|brine|proof|storage|airtight|vacuum"), ("CUTTING_TOOL", r"knife|peeler|grater|cleaver|scissors|shears|mandolin|zester|slicer|cutter|corer"), ("MIXING_TOOL", r"whisk|spoon|spatula|ladle|beater|masher|fork|tongs|scraper|muddler|rolling pin"),
         ("BAKEWARE", r"\btin\b|tray|baking|mould|mold|ramekin|loaf|muffin|pie dish|cake|sheet\b|bundt"), ("COOKWARE", r"pan\b|pot\b|skillet|wok|saucepan|casserole|dutch oven|frying|roasting|tagine|pressure cooker")]
CAT = {"UTENSIL": "HAND_TOOL", "COOKWARE": "COOKWARE", "VESSEL": "CONTAINER", "HEAT_SOURCE": "HEATING_APPLIANCE", "MEASURE": "MEASUREMENT_TOOL", "OTHER": "OTHER", "APPLIANCE": "UNKNOWN"}


def main():
    last = {}
    for l in open(ROOT / "ledgers/data/TOOL.jsonl", encoding="utf-8"):
        r = json.loads(l)
        last[r["id"]] = r
    rows = []
    for t in sorted(last):
        r = last[t]
        if r.get("status") != "ACTIVE":
            continue
        name = r["canonical_name"].lower()
        cls, why = None, None
        for c, rx in RULES:
            if re.search(rx, name):
                cls, why = c, f"keyword:{rx[:30]}"
                break
        if cls is None:
            cls, why = CAT.get(r.get("category"), "UNKNOWN"), f"category:{r.get('category')}"
        rows.append({"tool_id": t, "canonical_name": r["canonical_name"], "existing_category": r.get("category"), "structural_class": cls, "rule": why, "status": "DETERMINISTIC_RULE_UNVERIFIED"})
    with open(ROOT / "registry/recipe_tool_structural_class_map_v1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(len(rows), Counter(r["structural_class"] for r in rows))


main()
