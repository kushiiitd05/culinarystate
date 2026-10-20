#!/usr/bin/env python3
"""S118 Part I pass 1: audit every proposed event that the S117 conversion dropped (UNRESOLVED_REFERENCE). No repair here.

  /opt/anaconda3/bin/python tools/audit_foodcom_dropped.py   # -> reports/gold/foodcom_dropped_event_audit.csv

Reads the S117 conversion log and the review sheet (local-only recipe text; the CSV carries step text, so it is git-ignored).
Root-cause table ROOTS is the AI auditor's reading of each unresolved root name against the recipe's ingredient list and step text.
A dropped event whose missing input is the output of an earlier proposed event is a cascade (BROKEN_LINEAGE) of that root.
"""
import ast
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "annotation" / "gold" / "foodcom_ai_assisted" / "conversion_log.csv"
SHEET = Path.home() / "Downloads" / "Kush_Parv_joint_review_sheet.csv"
OUT = ROOT / "reports" / "gold" / "foodcom_dropped_event_audit.csv"

# (recipe, root name) -> (repair_class, repairable, strategy, remaining_uncertainty)
OMIT = "SOURCE_LIST_OMISSION"
ROOTS = {
    ("FC100067", "bean"): ("STEP_ONLY_SOURCE_ENTITY", "yes", "add step-only entity 'beans' (named in step 0), quantity UNKNOWN", "bean variety and amount not stated"),
    ("FC100067", "water"): ("CONVERTER_LIMITATION", "no", "unlisted water is a cooking medium, not a tracked entity; pure-water events rejected, medium kept on food events", "none"),
    ("FC104592", "lasagne"): (OMIT, "yes", "add step-only entity 'lasagne sheets' (step 6 '3 sheets of lasagne')", "sheet weight/type unstated"),
    ("FC109905", "salt"): (OMIT, "yes", "add step-only seasoning entity 'salt' (step 3), quantity UNKNOWN", "amount 'to taste'"),
    ("FC109905", "pepper"): (OMIT, "yes", "add step-only seasoning entity 'pepper' (step 3), quantity UNKNOWN", "amount 'to taste'"),
    ("FC109905", "water"): ("CONVERTER_LIMITATION", "no", "unlisted boiling water = medium; spaghetti events kept with medium", "none"),
    ("FC113219", "oil"): (OMIT, "yes", "add step-only entity 'oil' ('about 2 tbsp oil', step 3)", "oil type unstated"),
    ("FC158166", "cannelloni"): (OMIT, "yes", "add step-only entity 'cannelloni tubes' (steps 3-4)", "count unstated"),
    ("FC158166", "lasagne"): ("ALTERNATIVE_BRANCH", "no", "step 4 is a note offering lasagne sheets instead of cannelloni; keep as alternative, not a second entity", "alternative path not modelled"),
    ("FC158166", "salt"): (OMIT, "yes", "add step-only seasoning 'salt' (step 1)", "amount 'to taste'"),
    ("FC158166", "pepper"): (OMIT, "yes", "add step-only seasoning 'pepper' (step 1)", "amount 'to taste'"),
    ("FC175640", "bread"): (OMIT, "yes", "add step-only entity 'bread' (sandwich base, steps 1+)", "bread type unstated"),
    ("FC175640", "salt"): ("ALTERNATIVE_BRANCH", "yes", "step-only entity 'onion salt' with alternative 'garlic salt' (user's choice)", "which alternative used is open"),
    ("FC197059", "water"): ("CONVERTER_LIMITATION", "no", "unlisted salted/ice water = medium; food events kept with medium", "none"),
    ("FC199083", "stuffing"): (OMIT, "yes", "add step-only entity 'stuffing mix' (step 3 'prepare stuffing according to package directions')", "package contents unknown"),
    ("FC329047", "oil"): (OMIT, "yes", "add step-only entity 'oil' (deep-fry oil, step 5)", "oil type and amount unstated ('2 inches')"),
    ("FC438595", "stock"): ("MISSING_INTERMEDIATE", "no", "pan juices/stock produced by roasting is not a written output; no safe name to attach", "origin of stock/drippings lineage UNKNOWN"),
    ("FC438863", "pepper"): (OMIT, "yes", "add step-only seasoning 'pepper' (step 1)", "amount unstated"),
    ("FC438863", "soup"): ("ALIAS_MISMATCH", "yes", "'the soup' = merged pot contents; alias to the last Merge output before step 6", "which earlier merge output is meant"),
    ("FC458306", "noodle"): ("OPTIONAL_BRANCH", "no", "'Serve with noodles' is a serving suggestion, not a recipe ingredient", "none"),
    ("FC464207", "water"): ("UNSUPPORTED_PROPOSAL", "yes", "AI labelled 'water' as the food in 'soak in water' / 'remove liver from water'; true target is the liver (listed); water is medium", "none"),
    ("FC484761", "couscous"): ("OPTIONAL_BRANCH", "no", "'Serve on or with couscous' is a serving suggestion", "none"),
}


def main():
    rows = list(csv.DictReader(open(SHEET, encoding="utf-8-sig")))
    ev, text = {}, {}
    for r in rows:
        if r["section"] == "STEP":
            k = int(r["item_index"])
            text[(r["recipe_id"], k)] = r["source_text"]
            for j, e in enumerate(json.loads(r["proposed_annotation"])["events"]):
                ev[(r["recipe_id"], k, j)] = e
    total = len(ev)
    drops = [l for l in csv.DictReader(open(LOG)) if l["kind"] == "UNRESOLVED_REFERENCE"]
    dropped = {(d["recipe_id"], *map(int, re.match(r"step (\d+) E(\d+)", d["where"]).groups())) for d in drops}
    out, root_of = [], {}
    for d in drops:
        rid, (k, j) = d["recipe_id"], map(int, re.match(r"step (\d+) E(\d+)", d["where"]).groups())
        e = ev[(rid, k, j)]
        miss = ast.literal_eval(re.search(r"(\[.*?\])", d["detail"]).group(1))
        earlier = {(x.get("output") or "").lower(): key for key, x in ev.items() if key[0] == rid and (key[1], key[2]) < (k, j)}
        cls = defaultdict(list)
        for m in miss:
            src = earlier.get(m.lower())
            if src is not None and src in dropped:
                cls["BROKEN_LINEAGE"].append((m, f"{src[0]} s{src[1]}E{src[2]}"))
            else:
                cls["ROOT"].append(m)
        if cls["ROOT"]:
            m = cls["ROOT"][0]
            default = (("MISSING_INTERMEDIATE", "yes", "references 'the mixture of step N' that no proposed event creates; re-author the source step so the working mixture "
                        "has a named Merge/Transform output", "which components are in the working mixture")
                       if re.search(r"mixture step \d+", m) else ("OTHER", "unknown", "unclassified root", "needs manual read"))
            c, rep, strat, unc = ROOTS.get((rid, m.lower()), default)
            root = m
        elif not cls["BROKEN_LINEAGE"]:
            c, rep, strat, unc, root = "UNSUPPORTED_PROPOSAL", "no", "event proposed with no inputs", "none", ""
        else:
            m, up = cls["BROKEN_LINEAGE"][0]
            c, rep, strat, unc = "BROKEN_LINEAGE", "cascade", f"restore only if upstream {up} is restored; output name is AI-concatenated", "AI output names are mechanical"
            root = up
        out.append({"recipe_id": rid, "step_index": k, "event_index": j, "event_type": e["operation"], "process_action": e["action"],
                    "proposed_inputs": " | ".join(e["inputs"]), "proposed_output": e.get("output") or "", "missing_input": " | ".join(miss),
                    "source_text": text[(rid, k)], "drop_reason": d["detail"].split(":", 1)[-1].strip(), "repair_class": c, "repairable": rep,
                    "repair_strategy": strat, "remaining_uncertainty": unc, "root": root})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print(f"proposed {total} | dropped {len(out)} | written-or-by-design {total - len(out)}")
    print(Counter(o["repair_class"] for o in out))
    print(Counter(o["repairable"] for o in out))


if __name__ == "__main__":
    main()
