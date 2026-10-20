#!/usr/bin/env python3
"""S118 Part I pass 2: build annotation/gold/foodcom_ai_assisted_v1_1/ from the hand-authored spec (S117 version left unchanged).

  /opt/anaconda3/bin/python tools/repair_foodcom_gold.py

Per recipe: S117 ingredient lines (entity labels cleaned) + step-only entities from the spec, step spans/text from S117, events from
annotation/gold/foodcom_ai_assisted_v1_1/spec.py, coref remapped (targets that no longer exist -> UNKNOWN). Each file must pass
schema validation, replay with no issues, and deterministic replay, else it stays DRAFT. Writes repair_log.csv.
"""
import csv
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))
import convert_ai_review as car  # noqa: E402
from culinarystate.annotation.gold import validate_gold, to_events  # noqa: E402
from culinarystate.state_graph.engine import replay  # noqa: E402

V0 = ROOT / "annotation" / "gold" / "foodcom_ai_assisted"
V1 = ROOT / "annotation" / "gold" / "foodcom_ai_assisted_v1_1"
PROV = ("PROVENANCE: AI_REAUTHORED_SOURCE_GROUNDED; HUMAN_REVIEW_PENDING (v1.1, S118A). v1 = AI Pass-1 proposal batch-approved by Kush in chat "
        "(Parv relayed); that approval covers v1 ONLY. v1.1 re-authors every step's events from the source text by the AI (Claude), restoring "
        "the 126 events dropped in S117 and replacing mechanical output names; step-only foods become entities with quantity UNKNOWN. "
        "NOT human-verified line by line, NOT independent; Kush and Parv files identical. Promote to AI_ASSISTED_HUMAN_REVIEWED only after "
        "Kush reviews v1.1.")


def load_spec():
    spec = importlib.util.spec_from_file_location("foodcom_spec", V1 / "spec.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.SPEC


def clean(label):
    return re.sub(r"^fc\d+ ing \d+ ", "", label)


def build(old, sp, names):
    rid = old["recipe_id"]
    used, ren = set(), {}
    lines = []
    for li in old["ingredient_lines"]:
        base, k = clean(li["entity"]), 2
        lab = base
        while lab in used:
            lab, k = f"{base} {k}", k + 1
        used.add(lab)
        ren[li["entity"]] = lab
        row = {**li, "entity": lab}
        row.update(sp.get("line_flags", {}).get(li["line_index"], {}))
        lines.append(row)
    n = len(lines)
    for j, (ent, concept, why) in enumerate(sp.get("add", [])):
        assert ent not in used, (rid, ent)
        used.add(ent)
        c = names.get(car.norm(concept)) or "UNKNOWN"
        row = {"line_index": n + j, "text": ent, "spans": [], "entity": ent, "concept": c, "notes": "STEP_ONLY_ENTITY, quantity UNKNOWN; " + why}
        if ent in sp.get("alternatives", {}):
            row["alternatives"] = sp["alternatives"][ent]
        lines.append(row)
    for ent, alts in sp.get("alternatives", {}).items():
        row = next(r for r in lines if r["entity"] == ent)
        row.setdefault("alternatives", alts)
    steps = []
    for st in old["steps"]:
        evs = []
        for e in sp["steps"].get(st["step_index"], []):
            e = dict(e)
            e["process"] = car.canon_proc(rid, f"step {st['step_index']}", e["process"]) if "process" in e else None
            if e["process"] is None:
                del e["process"]
            evs.append(e)
        coref = [{**c, "entity": ren.get(c["entity"], "UNKNOWN") if c["entity"] != "UNKNOWN" else "UNKNOWN"} for c in st.get("coref", [])]
        steps.append({"step_index": st["step_index"], "text": st["text"], "spans": st["spans"], "events": evs, "coref": coref})
    unk = old.get("unknowns", []) + [{"what": u, "why": "S118 source-supported repair: not stated in the text"} for u in sp.get("unknowns", [])]
    return {**{k: old[k] for k in ("schema_version", "recipe_id", "source_ref", "locale")}, "ingredient_lines": lines, "steps": steps,
            "unknowns": unk, "notes": PROV}


def main():
    spec, names = load_spec(), car.registry()
    log, stats = [], []
    for who in ("Kush", "Parv"):
        (V1 / who).mkdir(parents=True, exist_ok=True)
    for f in sorted((V0 / "Kush").glob("*.Kush.json")):
        old = json.loads(f.read_text())
        rid = old["recipe_id"]
        doc = build(old, spec[rid], names)
        errs = validate_gold({**doc, "annotator": "Kush", "status": "DONE"})
        iss, det = [], True
        if not errs:
            ev = to_events({**doc, "annotator": "Kush", "status": "DONE"})
            r1, r2 = replay(ev), replay(to_events({**doc, "annotator": "Kush", "status": "DONE"}))
            iss = list(r1.issues)
            det = repr(r1.__dict__) == repr(r2.__dict__) if hasattr(r1, "__dict__") else True
        status = "DONE" if not errs and not iss and det else "DRAFT"
        n_ev = sum(len(s["events"]) for s in doc["steps"])
        for who in ("Kush", "Parv"):
            (V1 / who / f"{rid}.{who}.json").write_text(json.dumps({**doc, "annotator": who, "status": status}, indent=2, ensure_ascii=False) + "\n")
        stats.append((rid, status, n_ev, errs[:2], [str(i) for i in iss[:4]], det))
    for s in stats:
        print(s)
    print("DONE:", sum(s[1] == "DONE" for s in stats), "events:", sum(s[2] for s in stats))
    with (V1 / "repair_log.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["recipe_id", "where", "kind", "detail"])
        w.writeheader()
        w.writerows(car.log)


if __name__ == "__main__":
    main()
