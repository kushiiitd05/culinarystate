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
COREF_DOCS: dict = {}
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
    out = {"RESOLVABLE_EXPLICIT": 0, "RESOLVABLE_STRUCTURAL": 0, "GENUINELY_AMBIGUOUS": 0, "NOT_APPLICABLE": 0, "SPURIOUS_SUBSTRING": 0}
    examples = {k: [] for k in out}
    for rid, d in COREF_DOCS.items():
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
            t_ = st["text"]
            spur = [c for c in st["coref"] if (c["start"] > 0 and t_[c["start"] - 1].isalnum())
                    or (c["end"] < len(t_) and t_[c["end"]].isalnum())]
            if spur:
                out["SPURIOUS_SUBSTRING"] = out.get("SPURIOUS_SUBSTRING", 0) + len(spur)
                if len(examples.setdefault("SPURIOUS_SUBSTRING", [])) < 4:
                    examples["SPURIOUS_SUBSTRING"].append(f"{rid} s{k} '{spur[0]['mention']}' inside '{t_[max(0, spur[0]['start'] - 6):spur[0]['end'] + 6]}'")
                rows.append({"recipe_id": rid, "step_index": k, "item_type": "COREF_SPURIOUS", "current_value": json.dumps([c["mention"] for c in spur]),
                             "problem": f"{len(spur)} coref mention(s) are letters inside another word (e.g. 'it' in 'with'), not references",
                             "proposed_correction": "AI_PROPOSED_CORRECTION: remove these coref entries",
                             "source_text": t_[:200], "reason": "text at the offsets is a substring of a longer word",
                             "human_review_required": "yes", "decision": "", "reviewer": "", "item_id": f"GC-{len(rows) + 1:03d}",
                             "patch_json": json.dumps({"op": "drop_coref", "recipe": rid, "step": k, "starts": [c["start"] for c in spur]}),
                             "problem_class": "ANNOTATION_ERROR (draft coref noise)"})
            expl = [c for c in st["coref"] if c not in spur and c["mention"].lower().strip() == "it"
                    and re.match(r"[\u2019']?s?\s*(important|worth|best|necessary|possible|better)", t_[c["end"]:c["end"] + 24], re.I)]
            if expl:
                out["NOT_APPLICABLE"] += len(expl)
                examples["NOT_APPLICABLE"].append(f"{rid} s{k} 'it' + '{t_[expl[0]['end']:expl[0]['end'] + 14]}' (expletive)")
                rows.append({"recipe_id": rid, "step_index": k, "item_type": "COREF_NONREFERRING", "current_value": json.dumps([c["mention"] for c in expl]),
                             "problem": "expletive 'it' ('it's important ...') does not refer to an entity",
                             "proposed_correction": "AI_PROPOSED_CORRECTION: remove these coref entries",
                             "source_text": t_[max(0, expl[0]["start"] - 40):expl[0]["end"] + 40], "reason": "NOT_APPLICABLE",
                             "human_review_required": "yes", "decision": "", "reviewer": "", "item_id": f"GC-{len(rows) + 1:03d}",
                             "patch_json": json.dumps({"op": "drop_coref", "recipe": rid, "step": k, "starts": [c["start"] for c in expl]}),
                             "problem_class": "ANNOTATION_ERROR (non-referring pronoun)"})
            spur_starts = {c["start"] for c in spur} | {c["start"] for c in expl}
            for ci, c in enumerate(st["coref"]):
                if c["start"] in spur_starts:
                    continue
                m = c["mention"]
                head = norm(re.sub(r"^(the|a|an|its|their|this|that|these|those)\s+", "", m.lower()))
                if tool_re.search(m):
                    cls, ent = "NOT_APPLICABLE", None
                elif pron_re.match(m.strip()):
                    before = norm(st["text"][:c["start"]])
                    named_before = [e for e, l in ents_all.items()
                                    if any(w in before.split() for w in norm(l["concept"]).split() if len(w) >= 4)]
                    cls, ent = (("RESOLVABLE_STRUCTURAL", derived_alive[0])
                                if len(derived_alive) == 1 and k > 0 and not named_before else ("GENUINELY_AMBIGUOUS", None))
                else:
                    cands = [e for e, l in ents_all.items() if head and (norm(e) == head or norm(l["concept"]) == head)]
                    cands += [x for x in alive if head and norm(x) == head]
                    cands = list(dict.fromkeys(cands))
                    if len(cands) == 1:
                        cls, ent = "RESOLVABLE_EXPLICIT", cands[0]
                    elif generic.search(m) and len(derived_alive) == 1 and k > 0 and not [
                            e for e, l in ents_all.items() if any(w in norm(st["text"][:c["start"]]).split()
                                                      for w in norm(l["concept"]).split() if len(w) >= 4)]:
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
                                 "patch_json": json.dumps({"op": "set_coref", "recipe": rid, "step": k, "start": c["start"], "entity": ent}),
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


def alt_rows():
    """The draft marked the WORD 'or' as the ALTERNATIVE span and listed ['or'] as the alternatives (9 lines)."""
    items = [("R003456", 6, "rapeseed oil"), ("R003595", 4, "marmalade"), ("R004275", 3, "2 tsp or powdered gelatine"),
             ("R004275", 4, "lemon juice"), ("R008637", 3, "rapeseed oil"), ("R008637", 11, "rapeseed oil"),
             ("R009484", 4, "crème fraîche"), ("R011207", 3, "cooked fresh corn"), ("R011207", 7, "vegetable oil")]
    for rid, ln, alt in items:
        line = docs[rid]["ingredient_lines"][ln]
        i = line["text"].find(alt)
        if i < 0:                                                  # source has 'cr me fra che' style damage: skip rather than guess
            continue
        patch = {"op": "set_line_alt", "recipe": rid, "line": ln, "alternatives": [alt],
                 "spans": [{"start": i, "end": i + len(alt), "label": "ALTERNATIVE", "text": alt}]}
        add_row(rid, None, "AUDIT_CORRECTION", {"alternatives": line.get("alternatives")},
                f"line {ln}: the ALTERNATIVE span and `alternatives` hold the word 'or' instead of the alternative item",
                {"alternatives": [alt]}, f"Source line: '{line['text']}' (handbook section 2: 'butter or margarine' -> ALTERNATIVE margarine)",
                "ANNOTATION_ERROR (draft)", patch=patch)
        rows[-1]["source_text"] = line["text"]


def s109_proposals():
    r = "R000312"
    c = cur(r, 1)
    add_row(r, 1, "AUDIT_CORRECTION", [e.get("type") for e in c],
            "only dough ball 1 is rolled and used; balls 2-4 stay alive although the text uses each ball ('roll each one out ... Spread one side of each')",
            [c[0], c[1]] + [T(0, f"dough ball {i}", "roll") for i in range(1, 5)] +
            [M(["dough ball 1", "dough ball 2", "dough ball 3", "dough ball 4", "ricotta-garlic filling", "green olives",
                "cooked artichoke-rosemary", "mozzarella"], "filled calzones", "fill"), c[4], c[5], c[6], c[7]],
            "Text: 'Divide into 4 balls and roll each one out ... Spread one side of each with the ricotta, scatter with the olives, the artichokes and rosemary, then top with the mozzarella' (the four calzones are kept as one lot; shares of filling are unstated)",
            "ANNOTATION_ERROR (draft)")
    r = "R000387"
    c = cur(r, 0)
    add_row(r, 0, "AUDIT_CORRECTION", [e.get("process") for e in c],
            "the two 'fry for a few mins' phases are not recorded as processes",
            [c[0], c[1], c[2], T(0, "spiced base", "fry", time="a few mins"), c[3], T(0, "pickle base", "fry", time="a few mins more")],
            "Text: 'Stir in the spices and curry leaves and fry for a few mins, then add the tomato purée and tamarind and fry for a few mins more'",
            "ANNOTATION_ERROR (omitted process)")
    r = "R001894"
    c = cur(r, 1)
    add_row(r, 1, "AUDIT_CORRECTION", [e.get("process") for e in c if e["type"] == "Merge"],
            "Merge process is 'trim' (a mis-canonicalised verb)",
            [c[0], M(["pizza base", "balsamic caramelised onions", "goat s cheese"], "topped pizza", "spoon"), c[2]],
            "Text: 'Spoon the caramelised onions over the base and top with slices of goat's cheese'", "ANNOTATION_ERROR (event argument)")
    r = "R002843"
    add_row(r, 0, "AUDIT_CORRECTION", [e.get("target") for e in cur(r, 0)],
            "'Butter the baking dish' transfers the SAUCE butter (butter 2) into the dish; the text does not say which butter or how much",
            [], "Text: 'Butter the baking dish.' (L1 'butter for the fish', L2 'butter for the sauce'): amount and lot unstated -> no event; UNKNOWN",
            "ANNOTATION_ERROR (wrong lot) + AMBIGUOUS")
    add_row(r, 1, "AUDIT_CORRECTION", [e.get("inputs") for e in cur(r, 1)],
            "the fish assembly uses the sauce butter (butter 2); it should use the fish butter",
            [M(["cod fillets", "butter", "white wine"], "cod cooking assembly", "add")],
            "Text: 'Add the cod, butter and white wine.' with L1 '50g butter for the fish'", "ANNOTATION_ERROR (lineage)")
    c = cur(r, 5)
    add_row(r, 5, "AUDIT_CORRECTION", [e.get("inputs") for e in c if e["type"] == "Merge"],
            "the cooked cod is merged into the sauce, but the fish was removed and kept warm; the sauce is the juices plus the remaining butter",
            [M(["cooking juices", "butter 2"], "butter sauce base", "add"), c[1]],
            "Text: 'Remove fish ... and keep warm, Add the juices ... to a pan. Add the remaining butter and reduce until the sauce slightly thickens' (L2 '30g butter for the sauce')",
            "ANNOTATION_ERROR (lineage)")
    add_row(r, 6, "AUDIT_CORRECTION", [e.get("inputs") for e in cur(r, 6)],
            "serving Merge omits the cooked cod",
            [M(["cooked cod", "butter sauce base", "parsley"], "served cod with butter sauce", "serve")],
            "Text: 'Serve with sprigs of parsley.' (the dish is cod with butter sauce)", "ANNOTATION_ERROR (lineage)")
    r = "R007363"
    c = cur(r, 0)
    add_row(r, 0, "AUDIT_CORRECTION", [e.get("inputs") for e in c if e["type"] == "Merge"],
            "the browned chicken, set aside, is merged into the aromatic base in step 0 but returned only in step 1",
            [c[0], c[1], c[2], M(["onion", "garlic", "red chillies", "ginger"], "aromatic base", "add"), c[4]],
            "Text: 'Brown the chicken in batches, setting aside once golden. Fry the onion ... add the garlic, chilli and ginger' ... step 1: 'Return the chicken to the pan'",
            "ANNOTATION_ERROR (lineage)")
    c = cur(r, 1)
    add_row(r, 1, "AUDIT_CORRECTION", [e.get("inputs") for e in c if e["type"] == "Merge"],
            "the chicken is never returned; the whole coriander lot is added although only half is chopped into the sauce",
            [{"type": "Split", "target": "coriander", "outputs": [{"label": "chopped coriander", "fraction": "1/2"},
                                                                  {"label": "coriander leaves", "fraction": "1/2"}]},
             M(["spiced aromatic base", "peanut butter", "coconut milk", "tomatoes"], "peanut-coconut sauce", "stir"),
             T(0, "peanut-coconut sauce", "simmer"),
             M(["peanut-coconut sauce", "browned chicken", "chopped coriander"], "chicken in peanut sauce", "return"), c[3]],
            "Text: coriander 'bunch of coriander 1/2 roughly chopped, 1/2 leaves picked'; 'Return the chicken to the pan and add the chopped coriander'; 'bring to a simmer'",
            "ANNOTATION_ERROR (lineage, repeated lot)")
    add_row(r, 2, "AUDIT_CORRECTION", [e.get("inputs") for e in cur(r, 2)],
            "serving Merge omits the remaining coriander",
            [M(["chicken in peanut sauce", "coriander leaves", "roasted peanuts", "cauliflower rice"], "served peanut butter chicken", "serve")],
            "Text: 'Serve with the remaining coriander, roasted peanuts and rice, if you like.'", "ANNOTATION_ERROR (repeated lot)")
    r = "R008469"
    c0, c1, c2, c3 = cur(r, 0), cur(r, 1), cur(r, 2), cur(r, 3)
    add_row(r, 0, "AUDIT_CORRECTION", [e.get("inputs") for e in c0 if e["type"] == "Merge"],
            "the roasting Merge uses the croutons' drizzle oil (olive oil 2) instead of half of the 2 tbsp oil",
            [{"type": "Split", "target": "olive oil", "outputs": [{"label": "roasting oil", "fraction": "1/2"},
                                                                  {"label": "remaining oil", "fraction": "1/2"}]},
             M(["carrot", "roasting oil", "garlic", "thyme"], "seasoned roasting mixture", "toss"), c0[1]],
            "Text: 'Put the carrots, half the oil, the garlic and thyme in a roasting tin'; step 1: 'heat the remaining oil' (L10 'drizzle olive oil' is for the croutons)",
            "ANNOTATION_ERROR (lineage, repeated lot)")
    add_row(r, 1, "AUDIT_CORRECTION", [e.get("type") for e in c1],
            "soft onions are Split into carrots/garlic/stalks (they are the onions); the roasted mixture is merged into the onions at the start; the remaining oil is unused",
            [M(["onions", "remaining oil", "butter"], "onion base", "cook"),
             T(0, "onion base", "cook", temperature="low heat", time="10 mins", endpoint="soft"),
             {"type": "Split", "target": "seasoned roasting mixture", "outputs": [
                 {"label": "roasted carrots", "fraction": None}, {"label": "roasted garlic flesh", "fraction": None},
                 {"label": "garlic skins and woody thyme stalks", "fraction": None}]},
             {"type": "Discard", "target": "garlic skins and woody thyme stalks"},
             M(["onion base", "roasted carrots", "roasted garlic flesh", "chicken stock"], "soup base", "add"),
             T(0, "soup base", "boil"), T(0, "soup base", "simmer", time="10 mins")],
            "Text: 'heat the remaining oil and butter in a large saucepan. Tip in the onions and cook ... until soft. ... Squeeze the soft roasted garlic cloves out of their skins ... Tip in the carrots and discard any woody thyme stalks. Pour over the stock, bring to the boil, then simmer for 10 mins'",
            "ANNOTATION_ERROR (lineage)")
    add_row(r, 2, "AUDIT_CORRECTION", [e.get("inputs") for e in c2 if e["type"] == "Merge"],
            "the croutons are built from the SOUP BASE and pancetta; the bread and the drizzle oil are never used",
            [M(["pancetta", "rustic bread", "olive oil 2"], "pancetta croutons", "wrap"),
             {"type": "Transfer", "target": "pancetta croutons", "location": "baking tray"},
             T(0, "pancetta croutons", "bake", time="10 mins", endpoint="pancetta and bread edges crisp"),
             T(0, "pancetta croutons", "drain", medium="kitchen paper")],
            "Text: 'wrap the pancetta around the soldiers ... Put on a baking tray, drizzle with a little oil ... Bake for 10 mins until the pancetta and bread edges are crisp. Drain on kitchen paper'",
            "ANNOTATION_ERROR (lineage)")
    add_row(r, 3, "AUDIT_CORRECTION", [e.get("type") for e in c3],
            "blending/sieving is applied to the croutons; the cream is added whole; the croutons are not served with the soup",
            [T(0, "soup base", "blend", tool="hand blender"),
             {"type": "Split", "target": "soup base", "outputs": [{"label": "sieved soup", "fraction": None},
                                                                  {"label": "sieve residue", "fraction": None}]},
             {"type": "Split", "target": "double cream", "outputs": [{"label": "cream for the soup", "fraction": None},
                                                                    {"label": "remaining cream", "fraction": None}]},
             M(["sieved soup", "cream for the soup"], "creamed carrot soup", "add"), T(0, "creamed carrot soup", "heat"),
             M(["creamed carrot soup", "remaining cream", "pancetta croutons"], "served carrot soup", "serve")],
            "Text: 'blitz the soup with a hand blender, then sieve into a clean saucepan ... Add 5 tbsp of the cream, heat through ... Serve drizzled with the remaining cream ... with the croutons' (what happens to the sieve residue is not stated: not discarded; 5 of 6 tbsp not turned into fractions)",
            "ANNOTATION_ERROR (lineage)")
    r = "R008637"
    c0, c1 = cur(r, 0), cur(r, 1)
    add_row(r, 0, "AUDIT_CORRECTION", [e.get("type") for e in c0],
            "carrots and grapes are merged into one entity although the text keeps them apart on the tray (grapes later scattered over the salad)",
            [c0[0], M(["baby carrot", "extra virgin olive oil or rapeseed oil"], "oiled carrots", "drizzle"),
             {"type": "Transfer", "target": "oiled carrots", "location": "large baking tray"},
             {"type": "Transfer", "target": "red seedless grape", "location": "large baking tray"},
             T(0, "oiled carrots", "roast", time="10 mins", temperature="200C/180C fan/gas 6"),
             T(0, "red seedless grape", "roast", time="10 mins", temperature="200C/180C fan/gas 6"),
             T(0, "oiled carrots", "cool"), T(0, "red seedless grape", "cool"), c0[4], c0[5]],
            "Text: 'Place the carrots and grapes on a large baking tray, keeping the grapes at one end and the carrots at the other ... Drizzle the carrots with the oil ... Roast for 10 mins ... set aside to cool'",
            "ANNOTATION_ERROR (lineage)")
    add_row(r, 1, "AUDIT_CORRECTION", [e.get("inputs") for e in c1 if e["type"] == "Merge"],
            "the dressing contains the roasted carrots and grapes and omits the oil; the beans' water is not discarded; half the feta is not separated",
            [c1[0], c1[1], {"type": "Discard", "target": "discarded bean water"},
             M(["maple syrup", "balsamic vinegar", "lemon", "extra virgin olive oil or rapeseed oil 2"], "balsamic-maple dressing", "whisk"),
             {"type": "Split", "target": "feta cheese", "outputs": [{"label": "feta for the salad", "fraction": "1/2"},
                                                                   {"label": "remaining feta", "fraction": "1/2"}]},
             M(["cooled drained rice", "balsamic-maple dressing", "oiled carrots", "drained green beans", "pecan", "rocket leaves",
                "feta for the salad"], "rice salad base", "toss"),
             {"type": "Transfer", "target": "rice salad base", "location": "serving plate"},
             M(["rice salad base", "remaining feta", "red seedless grape"], "served rice salad", "scatter")],
            "Text: 'whisk the dressing ingredients together ... Add the rice, carrots, beans, pecans, rocket and half the feta, and toss ... scatter over the remaining feta and the roasted grapes' (dressing ingredients = maple syrup, balsamic vinegar, lemon juice, 2 tbsp oil)",
            "ANNOTATION_ERROR (lineage)")
    r = "R010426"
    c = cur(r, 0)
    add_row(r, 0, "AUDIT_CORRECTION", [e.get("process") for e in c if e["type"] == "Transform"],
            "the last event is the label 'finish with'; the stir-fry (3-4 mins, until the sprouts colour a little) is not recorded",
            c[:-1] + [T(0, "stir-fried vegetables", "stir-fry", time="3-4 mins", endpoint="sprouts colour a little")],
            "Text: 'add the vegetables and stir-fry for 3-4 mins until the sprouts colour a little'", "ANNOTATION_ERROR (event argument)")
    r = "R011481"
    c1, c2 = cur(r, 1), cur(r, 2)
    add_row(r, 1, "AUDIT_CORRECTION", [e.get("type") for e in c1],
            "dough is Split into 8 entities labelled 'or 10 dough portion N' (the text says 'eight or 10'); only portion 1 is ever used",
            [c1[0], T(0, "raw naan dough", "divide", sets={"form": "8 or 10 balls, about 75g each"}), T(0, "raw naan dough", "roll"),
             T(0, "raw naan dough", "rise", time="30-45 mins", endpoint="doubled in size again")],
            "Text: 'Divide into eight or 10 pieces (about 75g each), and roll into balls. Cover and leave to rise for 30-45 mins' (count is an alternative: unstated; handbook H16 for batches)",
            "ANNOTATION_ERROR + REPRESENTATION")
    add_row(r, 2, "AUDIT_CORRECTION", [e.get("target") for e in c2],
            "cooking is applied to 'dough portion 1' only; 'Repeat with the remaining dough balls' means batches, not separate entities",
            [T(0, "raw naan dough", "roll", sets={"form": "oval"}), {"type": "Transfer", "target": "raw naan dough", "location": "hot dry pan"},
             T(0, "raw naan dough", "cook", time="1-2 mins first side, then other side", endpoint="puffed up and blistered"),
             T(0, "raw naan dough", "wrap", medium="tea towel")],
            "Text: 'Roll one dough ball out at a time ... put in the hot pan ... cook for 1-2 mins until puffed up and blistered. Flip and cook on the other side, then wrap in a tea towel to keep warm. Repeat with the remaining dough balls.'",
            "ANNOTATION_ERROR + REPRESENTATION")
    add_row(r, 3, "AUDIT_CORRECTION", [e.get("inputs") for e in cur(r, 3) if e["type"] == "Merge"],
            "the naan Merge refers to 'dough portion 1'",
            [cur(r, 3)[0], cur(r, 3)[1], M(["raw naan dough", "coriander garlic butter"], "finished garlic-coriander naans", "brush")],
            "Text: 'Brush this over the warm naans and serve.'", "ANNOTATION ARTEFACT (downstream)")
    r = "R010532"
    c2, c3 = cur(r, 2), cur(r, 3)
    add_row(r, 2, "AUDIT_CORRECTION", [e.get("process") for e in c2],
            "'tear into small pieces' is not recorded",
            [c2[0], T(0, "mozzarella", "tear", sets={"form": "small pieces"}), c2[1]],
            "Text: 'Drain and pat the mozzarella balls dry, tear into small pieces, then season.'", "ANNOTATION_ERROR (omitted process)")
    add_row(r, 3, "AUDIT_CORRECTION", [e.get("process") for e in c3 if e["type"] == "Transform"],
            "'Drain on kitchen paper' after frying is not recorded",
            c3[:5] + [T(0, "fried stuffed courgette flowers", "drain", medium="kitchen paper")] + c3[5:],
            "Text: 'Fry in batches of two or three until lightly golden. Drain on kitchen paper and season with salt.'",
            "ANNOTATION_ERROR (omitted process)")
    r = "R006967"
    c = cur(r, 1)
    add_row(r, 1, "AUDIT_CORRECTION", [e.get("process") for e in c],
            "the 12-15 minute cook until the liquid is absorbed is not recorded",
            [c[0], c[1], T(0, "rice cooking mixture", "cook", temperature="medium heat", time="12-15 minutes",
                           endpoint="all the liquid absorbed and the rice tender")],
            "Text: 'cover and bring to the boil. Reduce to a medium heat and cook for 12-15 minutes or until all the liquid has been absorbed and the rice is tender'",
            "ANNOTATION_ERROR (omitted process)")
    r = "R009484"
    c = cur(r, 1)
    add_row(r, 1, "AUDIT_CORRECTION", [e.get("process") for e in c if e["type"] == "Transform"],
            "the optional grill step ('If you like things really grilled') is recorded as an unconditional Transform",
            [e for e in c if not (e["type"] == "Transform" and e.get("process") == "grill")],
            "Text: 'If you like things really grilled finish for a few minutes under the grill' (conditional/optional: not an event)",
            "ANNOTATION_ERROR (conditional treated as unconditional)")


def apply_patches(rows_sel):
    new = copy.deepcopy(docs)
    for r in rows_sel:
        p = json.loads(r["patch_json"])
        if p["op"] == "replace_events":
            new[p["recipe"]]["steps"][p["step"]]["events"] = p["events"]
        elif p["op"] == "set_coref":
            for c in new[p["recipe"]]["steps"][p["step"]]["coref"]:
                if c["start"] == p["start"]:
                    c["entity"] = p["entity"]
        elif p["op"] == "drop_coref":
            st = new[p["recipe"]]["steps"][p["step"]]
            st["coref"] = [c for c in st["coref"] if c["start"] not in p["starts"]]
        elif p["op"] == "set_line_alt":
            ln = new[p["recipe"]]["ingredient_lines"][p["line"]]
            ln["alternatives"] = p["alternatives"]
            ln["spans"] = [x for x in ln["spans"] if x["label"] != "ALTERNATIVE"] + p["spans"]
            ln["spans"].sort(key=lambda x: (x["start"], x["end"]))
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
    global COREF_DOCS
    proposals(); s109_proposals(); alt_rows()                 # pass 1: event/line proposals -> state the coref audit should read
    COREF_DOCS = apply_patches(rows)
    rows.clear()
    proposals()                                              # pass 2: real ids (S108 ids stay stable)
    cs, ex = classify_coref()
    nflag = audit_flags()
    s109_proposals()
    alt_rows()
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
