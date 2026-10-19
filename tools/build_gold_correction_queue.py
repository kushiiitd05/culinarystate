#!/usr/bin/env python3
"""S108: build the Gold-v1 correction queue (AI_PROPOSED_CORRECTION) and a provisional v1.1 for the oracle-arm check.

  /opt/anaconda3/bin/python tools/build_gold_correction_queue.py
Reads annotation/gold/pilot_20_adjudicated (unchanged), the AI draft and the conversion log. Writes
  annotation/gold/gold_v1_correction_queue.csv           one row per problem, decision/reviewer empty (Kush fills in)
  annotation/gold/pilot_20_adjudicated_v1_1_proposed/    v1 + ALL proposals, status DRAFT, NOT approved, NOT HUMAN_VERIFIED
Every proposal cites the source step text; ambiguous items stay UNKNOWN; no chemistry, quantities or temperatures are invented.
The rule compiler is not touched.
"""
import copy
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.gold import to_events, validate_gold  # noqa: E402
from culinarystate.state_graph.engine import Add, replay  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

G = ROOT / "annotation" / "gold"
SRC, OUT = G / "pilot_20_adjudicated", G / "pilot_20_adjudicated_v1_1_proposed"
AI = ROOT / "annotation" / "ai_review" / "pilot_20"
COLS = ["recipe_id", "step_index", "item_type", "current_value", "problem", "proposed_correction", "source_text", "reason",
        "human_review_required", "decision", "reviewer", "item_id", "patch_json", "problem_class"]
rows: list[dict] = []
docs = {p.name.split(".")[0]: json.loads(p.read_text()) for p in sorted(SRC.glob("*.ADJUDICATED.json"))}


def T(e, tgt, proc, **kw):
    return {"type": "Transform", "target": tgt, "process": proc, **kw}


def M(inputs, out, proc):
    return {"type": "Merge", "inputs": inputs, "output": out, "process": proc}


def add_row(rid, step, itype, cur, problem, proposed_events, reason, pclass, patch=None):
    d = docs[rid]
    src = d["steps"][step]["text"] if step is not None else ""
    rows.append({"recipe_id": rid, "step_index": step if step is not None else "", "item_type": itype,
                 "current_value": json.dumps(cur, ensure_ascii=False), "problem": problem,
                 "proposed_correction": "AI_PROPOSED_CORRECTION: " + json.dumps(proposed_events, ensure_ascii=False),
                 "source_text": src, "reason": reason, "human_review_required": "yes", "decision": "", "reviewer": "",
                 "item_id": f"GC-{len(rows) + 1:03d}",
                 "patch_json": json.dumps(patch or {"op": "replace_events", "recipe": rid, "step": step, "events": proposed_events},
                                          ensure_ascii=False),
                 "problem_class": pclass})


def cur(rid, step):
    return docs[rid]["steps"][step]["events"]


# ---- hand-written proposals; each cites the step text. keep = unchanged events copied from v1.
def proposals():
    r = "R002919"
    c = cur(r, 0)
    ev = [c[0], c[1], c[2], T(0, "drained cooked eggs", "cool", medium="cold running water"),
          T(0, "drained cooked eggs", "peel"), T(0, "drained cooked eggs", "chop"),
          M(["drained cooked eggs", "mayo", "greek yogurt", "mango chutney", "korma curry paste", "spring onions", "coriander"],
            "egg mixture", "mix"), c[5], c[6], c[7], c[8],
          T(0, "closed sandwiches", "halve", sets={"form": "halved"})]
    add_row(r, 0, "UNCONVERTED_EVENT+PADDED_REMAINDER", [e.get("type") for e in c],
            "mayo missing from the mixing Merge (draft wrote 'mayonnaise', converter could not tie it to the 'mayo' line, so mayo stays alive); "
            "'Peel and chop' not recorded; 'halve' created a synthetic remainder entity",
            ev, "Text: 'mix with the mayo, yogurt, ...'; 'Peel and chop the eggs'; 'then halve' is cutting (handbook: cut into pieces = Transform sets form), "
                "not a split with a second output", "CONVERTER_LIMITATION (name mismatch) + ANNOTATION/REPRESENTATION (pad)")
    r = "R003595"
    c = cur(r, 0)
    add_row(r, 0, "UNCONVERTED_EVENT", [], "4 draft events (soak, drain, discard water, dry) not written: 'blanched almonds' matched two almond lines",
            [{"type": "Transfer", "target": "almonds", "location": "small bowl"}, T(0, "almonds", "soak", time="5 mins", medium="boiling water"),
             {"type": "Split", "target": "almonds", "outputs": [{"label": "drained almonds", "fraction": None}, {"label": "soaking water", "fraction": None}]},
             {"type": "Discard", "target": "soaking water"}, T(0, "drained almonds", "dry")],
            "Text: 'Put the almonds into a small bowl and pour over boiling water ... Leave for 5 mins then drain in a sieve and leave to dry' (L0 'blanched almonds', not L8 'ground almonds')",
            "CONVERTER_LIMITATION (ambiguous fuzzy match between two almond lines)")
    c = cur(r, 3)
    add_row(r, 3, "ANNOTATION_ERROR_FOUND_ON_AUDIT", [e.get("output") for e in c],
            "'anti-curdle correction' merges ALL the flour mix into the batter, but the text says to add a little flour only IF the mixture curdles (conditional)",
            [c[0], c[1]], "Text: 'If the mixture starts to curdle, stir in a little flour.' A hypothetical is not an event; remaining flour is added in step 4",
            "ANNOTATION_ERROR (draft); downstream effect on state")
    add_row(r, 4, "ANNOTATION_ERROR_FOUND_ON_AUDIT", [e.get("inputs") for e in cur(r, 4)],
            "batter Merge omits the remaining flour and the ground almonds and uses the glaze milk (L12) instead of the batter milk (L9)",
            [M(["egg-creamed mixture", "dry flour mix", "almonds 2", "milk", "mixed fruit", "glac cherry"], "cake batter", "mix")],
            "Text: 'Add the remaining flour and ground almonds ... Mix in the milk ... add the dried fruit and cherries' (L9 '2 tbsp milk'; L12 '1 tbsp milk' is the step 7 glaze)",
            "ANNOTATION_ERROR (draft)")
    add_row(r, 5, "UNCONVERTED_EVENT", [e.get("type") for e in cur(r, 5)],
            "arrange almonds / bake events not written (intermediate names unresolved)",
            [{"type": "Transfer", "target": "cake batter", "location": "prepared tin"},
             M(["cake batter", "drained almonds"], "almond-topped raw cake", "arrange"),
             T(0, "almond-topped raw cake", "bake", time="45 mins", temperature="180C/160 C fan/Gas Mark 4")],
            "Text: 'Spoon the mixture into the prepared tin ... Arrange the whole almonds ... Bake in the oven for 45 mins' (oven setting from step 1)",
            "CONVERTER_LIMITATION (named intermediates)")
    add_row(r, 6, "UNCONVERTED_EVENT", [],
            "second bake not written",
            [T(0, "almond-topped raw cake", "bake", time="a further 60-80 minutes", temperature="160C/140 C fan/Gas Mark 3",
               endpoint="skewer has just a few crumbs; centre a little soft")],
            "Text: 'cook for a further 60-80 minutes ... When it's done it should have just a few crumbs attached ... centre will be a little soft'",
            "CONVERTER_LIMITATION")
    add_row(r, 7, "ANNOTATION_ERROR_FOUND_ON_AUDIT+UNCONVERTED_EVENT", [e.get("inputs") for e in cur(r, 7)],
            "glaze is built from 'cake batter' + caster sugar (should be milk L12 + sugar L13) and brushed on nothing; return-to-oven, cooling and wrapping not written",
            [M(["milk 2", "caster sugar"], "milk-sugar glaze", "heat"), T(0, "milk-sugar glaze", "heat", endpoint="sugar dissolved"),
             M(["almond-topped raw cake", "milk-sugar glaze"], "glazed cake", "brush"),
             T(0, "glazed cake", "bake", time="2-3 mins"), T(0, "glazed cake", "cool", endpoint="quite cold"),
             T(0, "glazed cake", "wrap", medium="foil"), T(0, "glazed cake", "rest", time="at least 2 days")],
            "Text: 'put the milk and sugar into a small pan and heat gently until the sugar has dissolved. Brush over the top of the cake and return the cake to the oven for 2-3 mins ... cool in the tin ... wrap in foil and keep for at least 2 days'",
            "ANNOTATION_ERROR (draft) + CONVERTER_LIMITATION")
    r = "R004275"
    c0, c1, c2, c3 = cur(r, 0), cur(r, 1), cur(r, 2), cur(r, 3)
    add_row(r, 0, "UNCONVERTED_EVENT+DOWNSTREAM_ARTEFACT", [e.get("type") for e in c0],
            "'discard the cut end of the asparagus' and 'set aside 6 tbsp peas' not written; a Split produced a mislabelled entity 'tbsp steamed peas' that later steps use as the purée",
            [T(0, "garden peas", "shell"), {"type": "Discard", "target": "green asparagus tips", "portion": "cut end of the asparagus"},
             T(0, "green asparagus tips", "chop", sets={"form": "short lengths"}), c0[0], c0[1],
             {"type": "Reserve", "target": "steamed peas and asparagus", "output": "reserved peas", "portion": "6 tbsp"},
             M(["reserved peas", "mild olive oil"], "dressed reserved peas", "spoon over")],
            "Text: 'Shell the peas and trim away and discard the cut end of the asparagus ... Put 6 tbsp of steamed peas into a small bowl, spoon over the 1 tbsp olive oil and set aside' (portion of a larger entity = Reserve)",
            "CONVERTER_LIMITATION (portion phrase) causing ANNOTATION ARTEFACT")
    add_row(r, 1, "DOWNSTREAM_ARTEFACT", [e.get("target") for e in c1],
            "purée blends the wrong entity ('tbsp steamed peas' = the reserved portion) instead of the asparagus and the rest of the cooked peas",
            [T(0, "steamed peas and asparagus", "blend", tool="food processor", endpoint="purée"), c1[1], c1[2]],
            "Text: 'Put the asparagus and the rest of the cooked peas in a food processor and whizz to a purée'", "ANNOTATION ARTEFACT from the Reserve failure")
    mould = [f"mousse in mould {i}" for i in range(1, 7)]
    add_row(r, 2, "PADDED_REMAINDER+DOWNSTREAM_ARTEFACT", [e.get("type") for e in c2],
            "mousse Merge uses the reserved peas; the Split into moulds adds a synthetic 'remainder' entity",
            [c2[0], c2[1], M(["steamed peas and asparagus", "softened gelatine mixture", "whipped tarragon cream"], "mousse mixture", "stir"),
             {"type": "Split", "target": "mousse mixture", "outputs": [{"label": m, "fraction": None} for m in mould]}] +
            [T(0, m, "chill", time="2-3 hours", medium="fridge", endpoint="set") for m in mould],
            "Text: 'Stir the gelatine into the purée and fold in the cream ... Divide the mixture between the moulds' (6 moulds from step 0; shares unstated, so fractions stay null: handbook H5)",
            "ANNOTATION ARTEFACT + REPRESENTATION (pad)")
    add_row(r, 3, "DOWNSTREAM_ARTEFACT", [e.get("type") for e in c3],
            "serving events refer to a single 'portions in moulds' entity and omit the reserved peas",
            [{"type": "Transfer", "target": m, "location": "small plate"} for m in mould] +
            [M(mould + ["dressed reserved peas", "olive oil balsamic vinegar tarragon"], "served pea-asparagus mousses", "decorate")],
            "Text: 'turn out each one on a small plate. Sprinkle the reserved peas around the base of each mousse ... Drizzle a little more olive oil and a few dashes of balsamic vinegar'",
            "ANNOTATION ARTEFACT")
    r = "R006967"
    add_row(r, 2, "UNCONVERTED_EVENT+DOWNSTREAM_ARTEFACT", [e.get("target") for e in cur(r, 2)],
            "squeezing the spinach and discarding the water not written; the spinach (L7) is never used",
            [T(0, "leaf spinach", "squeeze"), {"type": "Discard", "target": "leaf spinach", "portion": "excess water"},
             M(["rice cooking mixture", "leaf spinach"], "spinach rice", "tip"), T(0, "spinach rice", "mix", medium="2 tbsp hot water"),
             M(["spinach rice", "cashew nuts"], "cashew spinach rice", "toss"),
             M(["cashew spinach rice", "natural yogurt"], "served cashew spinach rice", "drizzle")],
            "Text: 'Squeeze the excess water from the spinach ... Tip it into the pan along with 2 tbsp of hot water and fluff up the rice ... Toss in the cashews. Serve drizzled with natural yogurt if you like' (yogurt line is optional)",
            "CONVERTER_LIMITATION + ANNOTATION ARTEFACT")
    r = "R009484"
    c = cur(r, 0)
    add_row(r, 0, "UNCONVERTED_EVENT", [e.get("type") for e in c],
            "squeezed-out liquid discard not written; wilting, chopping and placing spinach not recorded",
            [T(0, "leaf spinach", "wilt", medium="kettleful of hot water", tool="colander"), T(0, "leaf spinach", "cool", medium="cold tap"),
             T(0, "leaf spinach", "squeeze"), {"type": "Discard", "target": "leaf spinach", "portion": "liquid squeezed out"},
             c[1], T(0, "leaf spinach", "chop"), c[2]],
            "Text: 'pour over a kettleful of hot water to wilt it. Cool again under the cold tap then squeeze out as much liquid from the spinach as possible ... Roughly chop the spinach'",
            "CONVERTER_LIMITATION")
    r = "R007017"
    add_row(r, 0, "PADDED_REMAINDER", [e.get("type") for e in cur(r, 0)],
            "guacamole Split padded with a synthetic remainder; sandwiches chain mislabels bread/guacamole entities",
            [{"type": "Split", "target": "guacamole", "outputs": [{"label": "guacamole on rye slice 1", "fraction": None},
                                                                {"label": "guacamole on rye slice 2", "fraction": None}]},
             M(["rye bread", "guacamole on rye slice 1", "guacamole on rye slice 2"], "open sandwiches", "spread"),
             M(["open sandwiches", "tomato", "cajun grilled chicken breasts"], "topped open sandwiches", "arrange"),
             M(["topped open sandwiches", "lime"], "finished open sandwiches", "finish with")],
            "Text: 'Divide guacamole between rye bread (2 slices), spreading it evenly. Arrange 4 slices of tomato on each sandwich, and top with a sliced Cajun grilled chicken breast ... Finish with lime juice' (shares unstated: null; 'ground black pepper' has no ingredient line: left as an implicit seasoning)",
            "REPRESENTATION (pad)")
    r = "R011207"
    c = cur(r, 1)
    add_row(r, 1, "PADDED_REMAINDER", [e.get("type") for e in c],
            "batter Split into 'spoonful portions' with a synthetic remainder; frying 'in batches' is not a new entity",
            [T(0, "tuna-sweetcorn fritter batter", "fry", medium="oil", tool="non-stick or cast iron frying pan",
               temperature="medium heat", time="2-3 mins each side", endpoint="crisp and golden")],
            "Text: 'Heat a drop of oil ... Drop spoonfuls of the batter into the pan and cook until crisp and golden, about 2-3 mins, flip ... (you'll need to do this in batches)'. Handbook H16: batches do not create entities",
            "REPRESENTATION (pad)")
    add_row(r, 2, "DOWNSTREAM_ARTEFACT", [e.get("inputs") for e in cur(r, 2)],
            "serving Merge refers to 'cooked fritters', the entity removed by the step 1 correction; the fried batter keeps its label",
            [M(["tuna-sweetcorn fritter batter", "soured cream", "hot sauce"], "served fritters", "serve")],
            "Text: 'Serve the hot fritters with the lemon wedges ..., the soured cream and hot sauce, if using.' The lemon line was already consumed as zest in step 0; the separate wedges cannot be represented without splitting that line (left as is, documented)",
            "ANNOTATION ARTEFACT (downstream of the step 1 pad)")
    r = "R009647"
    add_row(r, 0, "UNSUPPORTED_BY_SCHEMA", [], "draft TRANSFER 'chill the glass' not written: the glass is a tool, not a food entity",
            [], "Text: 'Put a coupe or martini glass into the fridge to chill.' Handbook has no tool entities; document, do not force. No correction proposed",
            "SCHEMA LIMITATION (documented; no change)", patch={"op": "none"})


def classify_coref():
    draft = {x["recipe_id"]: x for x in json.loads((AI / "pilot20_AI_REVIEW_combined.json").read_text())}
    tool_re = re.compile(r"\b(pan|oven|tin|bowl|tray|dish|pot|sieve|colander|processor|jar|shaker|glass|mould|moulds|foil|board|spoon|fork)\b", re.I)
    pron_re = re.compile(r"^(it|them|they|this|that|these|those|one)$", re.I)
    generic = re.compile(r"\b(mixture|dough|batter|sauce|mix|paste|filling|dressing|base|purée|puree)\b", re.I)
    out = {"RESOLVABLE_EXPLICIT": 0, "RESOLVABLE_STRUCTURAL": 0, "GENUINELY_AMBIGUOUS": 0, "NOT_APPLICABLE": 0}
    examples = {k: [] for k in out}
    for rid, d in docs.items():
        ents_all = {l["entity"]: l for l in d["ingredient_lines"]}
        for st in d["steps"]:
            k = st["step_index"]
            derived_before = set()
            for s2 in d["steps"][:k]:
                for e in s2["events"]:
                    for key in ("output",):
                        if e.get(key):
                            derived_before.add(e[key])
                    for o in e.get("outputs", []):
                        derived_before.add(o["label"])
            try:
                alive = set(replay(to_events({**d, "steps": d["steps"][:k]})).alive()) if k else set()
            except Exception:
                alive = set()
            derived_alive = [a for a in alive if a not in ents_all]
            for ci, c in enumerate(st["coref"]):
                m = c["mention"]
                head = norm(re.sub(r"^(the|a|an|its|their|this|that|these|those)\s+", "", m.lower()))
                if tool_re.search(m):
                    cls, ent = "NOT_APPLICABLE", None
                elif pron_re.match(m.strip()):
                    before = norm(st["text"][:c["start"]])
                    named_before = [e for e, l in ents_all.items() if norm(l["concept"]) and norm(l["concept"]) in before]
                    cls, ent = (("RESOLVABLE_STRUCTURAL", derived_alive[0])
                                if len(derived_alive) == 1 and k > 0 and not named_before else ("GENUINELY_AMBIGUOUS", None))
                else:
                    cands = [e for e, l in ents_all.items() if head and (norm(e) == head or norm(l["concept"]) == head)]
                    cands += [x for x in alive if head and norm(x) == head]
                    cands = list(dict.fromkeys(cands))
                    if len(cands) == 1:
                        cls, ent = "RESOLVABLE_EXPLICIT", cands[0]
                    elif generic.search(m) and len(derived_alive) == 1 and k > 0 and not [
                            e for e, l in ents_all.items() if norm(l["concept"]) and norm(l["concept"]) in norm(st["text"][:c["start"]])]:
                        cls, ent = "RESOLVABLE_STRUCTURAL", derived_alive[0]
                    else:
                        cls, ent = "GENUINELY_AMBIGUOUS", None
                out[cls] += 1
                if len(examples[cls]) < 4:
                    examples[cls].append(f"{rid} s{k} '{m}'" + (f" -> {ent}" if ent else ""))
                if ent and c["entity"] == "UNKNOWN":
                    rows.append({"recipe_id": rid, "step_index": k, "item_type": "COREF", "current_value": f"{m} -> UNKNOWN",
                                 "problem": f"coref {cls}", "proposed_correction": f"AI_PROPOSED_CORRECTION: entity={ent}",
                                 "source_text": st["text"][max(0, c['start'] - 60):c['end'] + 40], "reason": cls,
                                 "human_review_required": "yes", "decision": "", "reviewer": "", "item_id": f"GC-{len(rows) + 1:03d}",
                                 "patch_json": json.dumps({"op": "set_coref", "recipe": rid, "step": k, "index": ci, "entity": ent}),
                                 "problem_class": cls})
    return out, examples


def audit_flags():
    """Automated plausibility flags (not corrections): unused/never-consumed ingredients and odd labels."""
    n = 0
    for rid, d in docs.items():
        ev = [e for s in d["steps"] for e in s["events"]]
        used = {x for e in ev for x in ([e.get("target")] + e.get("inputs", []))}
        try:
            alive = replay(to_events(d)).alive()
        except Exception:
            alive = []
        for l in d["ingredient_lines"]:
            if l["entity"] not in used and not l.get("optional") and "to serve" not in l["text"].lower() and "garnish" not in l["text"].lower():
                rows.append({"recipe_id": rid, "step_index": "", "item_type": "AUDIT_FLAG", "current_value": l["entity"],
                             "problem": "ingredient line never used by any event", "proposed_correction": "",
                             "source_text": l["text"], "reason": "automated check; read the steps", "human_review_required": "yes",
                             "decision": "", "reviewer": "", "item_id": f"GC-{len(rows) + 1:03d}", "patch_json": json.dumps({"op": "none"}),
                             "problem_class": "AUDIT_FLAG"})
                n += 1
        for a in alive:
            if re.search(r"remainder|^tbsp|\d", a):
                rows.append({"recipe_id": rid, "step_index": "", "item_type": "AUDIT_FLAG", "current_value": a,
                             "problem": "alive entity with a converter-looking label", "proposed_correction": "", "source_text": "",
                             "reason": "automated check", "human_review_required": "yes", "decision": "", "reviewer": "",
                             "item_id": f"GC-{len(rows) + 1:03d}", "patch_json": json.dumps({"op": "none"}), "problem_class": "AUDIT_FLAG"})
                n += 1
    return n


def apply_patches(rows_sel):
    new = copy.deepcopy(docs)
    for r in rows_sel:
        p = json.loads(r["patch_json"])
        if p["op"] == "replace_events":
            new[p["recipe"]]["steps"][p["step"]]["events"] = p["events"]
        elif p["op"] == "set_coref":
            new[p["recipe"]]["steps"][p["step"]]["coref"][p["index"]]["entity"] = p["entity"]
    return new


def fix_T(events):
    """Proposals use T(0, target, ...) shorthand; normalise the dict shape."""
    out = []
    for e in events:
        if e.get("type") == "Transform" and e.get("target") == 0:
            pass
        out.append(e)
    return out


def main():
    global T
    _T = T

    def T(e, tgt, proc, **kw):                      # noqa: E306  (e is a throwaway positional)
        return {"type": "Transform", "target": tgt, "process": proc, **kw}
    proposals()
    cs, ex = classify_coref()
    nflag = audit_flags()
    with (G / "gold_v1_correction_queue.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    new = apply_patches(rows)
    OUT.mkdir(exist_ok=True)
    bad = []
    for rid, d in new.items():
        d = {**d, "status": "DRAFT",
             "notes": "AI_PROPOSED_CORRECTION (S108, pending Kush approval; not HUMAN_VERIFIED). " + d["notes"]}
        errs = validate_gold({**d, "status": "DONE"})
        iss = [] if errs else list(replay(to_events(d)).issues)
        if errs or iss:
            bad.append((rid, errs[:1], iss[:2]))
        (OUT / f"{rid}.ADJUDICATED.json").write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    from collections import Counter
    print("queue rows:", len(rows), dict(Counter(r["item_type"] for r in rows)))
    print("coref:", cs, "audit flags:", nflag)
    print("coref examples:", json.dumps(ex, ensure_ascii=False)[:900])
    print("proposed files invalid/replay issues:", bad)


if __name__ == "__main__":
    main()
