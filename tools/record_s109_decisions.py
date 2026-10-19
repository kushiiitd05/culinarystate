#!/usr/bin/env python3
"""S109: record Kush's decisions (made after review with ChatGPT) in the correction queue and write the 19 MODIFY patches.

  /opt/anaconda3/bin/python tools/record_s109_decisions.py      # then: tools/apply_gold_corrections.py
Decision owner: Kush. APPROVE every proposal row except the 19 MODIFY rows; GC-017 stays a documented schema limitation (no Gold
change); audit flags need no decision. Rationales come from gold_v1_1_AI_review_recommendations.csv (ChatGPT review, adopted by Kush).
MODIFY patches below follow Kush's modification rules; they are AI-written patches for the human decision. Re-running the queue
builder would overwrite decisions: do not.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "annotation" / "gold"
Q = G / "gold_v1_correction_queue.csv"
docs = {p.name.split(".")[0]: json.loads(p.read_text()) for p in sorted((G / "pilot_20_adjudicated").glob("*.json"))}


def cur(rid, i):
    return docs[rid]["steps"][i]["events"]


def T(tgt, proc, **kw):
    return {"type": "Transform", "target": tgt, "process": proc, **kw}


def M(ins, out, proc):
    return {"type": "Merge", "inputs": ins, "output": out, "process": proc}


def split(tgt, outs, fr=None):
    return {"type": "Split", "target": tgt, "outputs": [{"label": o, "fraction": (fr[i] if fr else None)} for i, o in enumerate(outs)]}


def rep(rid, step, events):
    return {"op": "replace_events", "recipe": rid, "step": step, "events": events}


MOULDS = [f"mousse in mould {i}" for i in range(1, 7)]
STEAM = dict(time="3-5 minutes", endpoint="just tender but still bright green", tool="steamer")


def modify_patches(queue):
    q = {r["item_id"]: json.loads(r["patch_json"]) for r in queue}
    out = {}
    r = "R004275"
    out["GC-008"] = rep(r, 0, [T("garden peas", "shell"), {"type": "Discard", "target": "green asparagus tips", "portion": "cut end of the asparagus"},
                              T("green asparagus tips", "chop", sets={"form": "short lengths"}),
                              T("garden peas", "steam", **STEAM), T("green asparagus tips", "steam", **STEAM),
                              {"type": "Reserve", "target": "garden peas", "output": "reserved peas", "portion": "6 tbsp"},
                              M(["reserved peas", "mild olive oil"], "dressed reserved peas", "spoon over")])
    out["GC-009"] = rep(r, 1, [M(["green asparagus tips", "garden peas"], "vegetable purée", "blend"),
                              T("vegetable purée", "blend", tool="food processor", endpoint="purée")] + cur(r, 1)[1:])
    out["GC-010"] = rep(r, 2, [cur(r, 2)[0], cur(r, 2)[1], M(["vegetable purée", "softened gelatine mixture", "whipped tarragon cream"], "mousse mixture", "stir"),
                              split("mousse mixture", MOULDS)] + [T(m, "chill", time="2-3 hours", medium="fridge", endpoint="set") for m in MOULDS])
    out["GC-011"] = rep(r, 3, [{"type": "Transfer", "target": m, "location": "small plate"} for m in MOULDS] +
                       [M(MOULDS + ["dressed reserved peas", "olive oil balsamic vinegar tarragon"], "served pea-asparagus mousses", "decorate")])
    ln = docs[r]["ingredient_lines"][3]
    alt = "2 tsp or powdered gelatine"
    i = ln["text"].find(alt)
    out["GC-115"] = {"op": "set_line_alt", "recipe": r, "line": 3, "alternatives": ["2 tsp powdered gelatine"],
                     "spans": [{"start": i, "end": i + len(alt), "label": "ALTERNATIVE", "text": alt}]}
    r = "R006967"
    out["GC-111"] = rep(r, 1, [cur(r, 1)[0], T("rice cooking mixture", "boil"),
                              T("rice cooking mixture", "cook", temperature="medium heat", time="12-15 minutes",
                                endpoint="all the liquid absorbed and the rice tender")])
    out["GC-012"] = rep(r, 2, [T("leaf spinach", "squeeze"), {"type": "Discard", "target": "leaf spinach", "portion": "excess water"},
                              M(["rice cooking mixture", "leaf spinach"], "spinach rice", "tip"),
                              T("spinach rice", "mix", medium="2 tbsp hot water"), M(["spinach rice", "cashew nuts"], "cashew spinach rice", "toss")])
    r = "R011207"
    c0 = cur(r, 0)
    out["GC-015"] = rep(r, 1, [T("tuna-sweetcorn fritter batter", "fry", medium="oil", tool="non-stick or cast iron frying pan",
                               temperature="medium heat", time="2-3 mins each side", endpoint="crisp and golden",
                               sets={"form": "cooked fritters"})])
    out["GC-016"] = [rep(r, 0, [c0[0], c0[1], split("lemon", ["lemon zest", "lemon wedges"]),
                                M(["basic batter", "sweetcorn or fresh corn", "spring onions", "lemon zest", "tuna"], "tuna-sweetcorn fritter batter", "stir")]),
                     rep(r, 2, [M(["tuna-sweetcorn fritter batter", "lemon wedges", "soured cream"], "served fritters", "serve")])]
    r = "R000312"
    s1 = list(q["GC-089"]["events"])
    for e in s1:
        if e["type"] == "Split":
            for o in e["outputs"]:
                o["fraction"] = None
    out["GC-089"] = rep(r, 1, s1)
    r = "R007363"
    c = cur(r, 0)
    out["GC-096"] = rep(r, 0, [split("avocado oil", ["first tbsp oil", "second tbsp oil"], ["1/2", "1/2"]),
                              M(["chicken thighs", "first tbsp oil"], "browned chicken", "brown"), c[1], c[2],
                              M(["onion", "garlic", "red chillies", "ginger", "second tbsp oil"], "aromatic base", "add"),
                              T("aromatic base", "fry", time="1 min"), c[4], T("spiced aromatic base", "fry", time="1 min more")])
    c1 = cur(r, 1)
    out["GC-097"] = rep(r, 1, [split("coriander", ["chopped coriander", "coriander leaves"], ["1/2", "1/2"]),
                              M(["spiced aromatic base", "peanut butter", "coconut milk", "tomatoes"], "peanut-coconut sauce", "stir"),
                              T("peanut-coconut sauce", "simmer"),
                              M(["peanut-coconut sauce", "browned chicken", "chopped coriander"], "chicken in peanut sauce", "return"), c1[3]])
    out["GC-098"] = rep(r, 2, [M(["chicken in peanut sauce", "coriander leaves"], "served peanut butter chicken", "serve")])
    r = "R008469"
    c = q["GC-100"]["events"]
    cs = "roasted carrots with oil and thyme leaves"
    out["GC-100"] = rep(r, 1, [c[0], c[1], split("seasoned roasting mixture", [cs, "roasted garlic flesh", "garlic skins and woody thyme stalks"]),
                              {"type": "Discard", "target": "garlic skins and woody thyme stalks"},
                              M(["onion base", cs, "roasted garlic flesh", "chicken stock"], "soup base", "add"),
                              T("soup base", "boil"), T("soup base", "simmer", time="10 mins")])
    c3 = q["GC-102"]["events"]
    out["GC-102"] = rep(r, 3, [c3[0], c3[1], split("double cream", ["cream for the soup", "remaining cream"], ["5/6", "1/6"])] + c3[3:])
    r = "R008637"
    out["GC-104"] = rep(r, 1, q["GC-104"]["events"] + [T("served rice salad", "drizzle", medium="juice from the baking tray")])
    r = "R010426"
    c = cur(r, 0)
    out["GC-105"] = rep(r, 0, [c[0], c[1], c[2], c[3], split("lemon", ["lemon zest", "lemon juice"]),
                              M(["olive oil", "lemon zest", "pine nuts"], "lemon-pine-nut oil base", "add"),
                              M(["lemon-pine-nut oil base", "drained vegetables"], "stir-fried vegetables", "add"),
                              T("stir-fried vegetables", "stir-fry", time="3-4 mins", endpoint="sprouts colour a little"),
                              M(["stir-fried vegetables", "lemon juice"], "finished vegetables", "add")])
    r = "R011481"
    out["GC-107"] = rep(r, 2, [T("raw naan dough", "roll", sets={"form": "oval"}), {"type": "Transfer", "target": "raw naan dough", "location": "hot dry pan"},
                              T("raw naan dough", "cook", time="1-2 mins first side, then other side", endpoint="puffed up and blistered"),
                              {"type": "Transfer", "target": "raw naan dough", "location": "wrapped in a tea towel to keep warm"}])
    r = "R010532"
    out["GC-110"] = rep(r, 3, [T("sunflower oil", "heat", endpoint="bread cube browns in 20 seconds"),
                              M(["stuffed courgette flowers", "batter"], "battered stuffed flowers", "coat"),
                              T("battered stuffed flowers", "deep-fry", medium="sunflower oil", endpoint="lightly golden"),
                              T("battered stuffed flowers", "drain", medium="kitchen paper"),
                              {"type": "Transfer", "target": "battered stuffed flowers", "location": "low oven while remaining batches cook"},
                              M(["battered stuffed flowers", "basil-finished dressing"], "served stuffed courgette flowers", "drizzle")])
    return out


MOD = "GC-008 GC-009 GC-010 GC-011 GC-012 GC-015 GC-016 GC-089 GC-096 GC-097 GC-098 GC-100 GC-102 GC-104 GC-105 GC-107 GC-110 GC-111 GC-115".split()
RULES = {"GC-008": "separate pea/asparagus lineages; reserve 6 tbsp from peas only", "GC-009": "puree = asparagus + remaining peas",
         "GC-010": "puree + gelatine + cream; 6 mould outputs, null fractions", "GC-011": "serve with dressed reserved peas",
         "GC-012": "optional yogurt not an unconditional event", "GC-015": "batch frying, no remainder, form cooked fritters",
         "GC-016": "lemon wedges preserved; hot sauce optional", "GC-089": "four dough outputs with null fractions (equality not explicit)",
         "GC-096": "split 2 tbsp oil into two 1 tbsp uses; chicken stays separate", "GC-097": "chicken returned in step 1; coriander 1/2+1/2",
         "GC-098": "peanuts/rice optional, not unconditional", "GC-100": "keep oil/thyme leaves with carrots; discard only skins and stalks",
         "GC-102": "explicit 5 tbsp + remainder of 6 tbsp cream", "GC-104": "include final drizzle of tray juices",
         "GC-105": "zest and juice distinct uses", "GC-107": "tea-towel wrap as location, not a food transformation",
         "GC-110": "no excess-batter entity; oil is the frying medium", "GC-111": "boil separate from 12-15 min cook",
         "GC-115": "alternative = 2 tsp powdered gelatine"}


def main():
    rows = list(csv.DictReader(Q.open()))
    rec = {r["item_id"]: r for r in csv.DictReader((G / "gold_v1_1_AI_review_recommendations.csv").open())}
    patches = modify_patches(rows)
    assert set(patches) == set(MOD)
    cols = list(rows[0]) + (["decision_rationale"] if "decision_rationale" not in rows[0] else [])
    n = {"APPROVE": 0, "MODIFY": 0, "NOTED": 0}
    for r in rows:
        i, ai = r["item_id"], rec[r["item_id"]]["ai_recommendation"]
        r["decision_rationale"] = ""
        if i in MOD:
            assert ai == "MODIFY"
            r["decision"], n["MODIFY"] = "MODIFY", n["MODIFY"] + 1
            r["patch_json"] = json.dumps(patches[i], ensure_ascii=False)
            r["decision_rationale"] = RULES[i] + " | ChatGPT review: " + rec[i]["ai_review_reason"][:160]
        elif ai == "APPROVE":
            r["decision"], n["APPROVE"] = "APPROVE", n["APPROVE"] + 1
            r["decision_rationale"] = "approved after review (ChatGPT review adopted by Kush)"
        elif ai == "NO_CHANGE_SCHEMA_LIMITATION":
            r["decision"], n["NOTED"] = "NOTED_NO_CHANGE", n["NOTED"] + 1
            r["decision_rationale"] = "documented schema limitation; no Gold change"
        if r["decision"]:
            r["reviewer"] = "Kush (decision after review with ChatGPT; recorded by claude)"
    with Q.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(n)


if __name__ == "__main__":
    main()
