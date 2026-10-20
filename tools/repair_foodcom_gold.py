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
PROV = ("PROVENANCE: AI_ASSISTED_HUMAN_REVIEWED (batch-level). v1.1 events were re-authored from the source steps by the AI (Claude) in S118A "
        "(v1 = AI Pass-1 proposal, batch-approved by Kush in chat on S117). Kush reviewed v1.1 and approved it, and Parv reviewed and approved "
        "(relayed by Kush) on 2026-10-20; the review sheet has no row-level decisions or remarks, so no events changed "
        "(reports/gold/foodcom_v1_1_review_record.json). NOT independent annotation; Kush and Parv share one AI proposal; agreement non-informative. "
        "S116 eligibility screen still unconfirmed.")


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
    V1.mkdir(parents=True, exist_ok=True)
    recipes = []
    for f in sorted((V0 / "Kush").glob("*.Kush.json")):
        old = json.loads(f.read_text())
        rid = old["recipe_id"]
        doc = build(old, spec[rid], names)
        errs = validate_gold({**doc, "annotator": "JOINT", "status": "DONE"})
        iss, det = [], True
        if not errs:
            ev = to_events({**doc, "annotator": "JOINT", "status": "DONE"})
            r1, r2 = replay(ev), replay(to_events({**doc, "annotator": "JOINT", "status": "DONE"}))
            iss = list(r1.issues)
            det = repr(r1.__dict__) == repr(r2.__dict__) if hasattr(r1, "__dict__") else True
        status = "DONE" if not errs and not iss and det else "DRAFT"
        n_ev = sum(len(s["events"]) for s in doc["steps"])
        recipes.append({**doc, "annotator": "JOINT", "status": status})
        stats.append((rid, status, n_ev, errs[:2], [str(i) for i in iss[:4]], det))
    bundle = {"annotator": "JOINT", "schema_version": "gold-1.0", "provenance": PROV, "n_recipes": len(recipes),
              "note": "Kush and Parv sets are identical (one AI proposal); from S118 on there is ONE joint file. Per-recipe tool copies: tools/bundle_gold_packs.py-style split on demand.",
              "recipes": recipes}
    (V1 / "foodcom_v1_1_joint.json").write_text(json.dumps(bundle, indent=1, ensure_ascii=False) + "\n")
    for s in stats:
        print(s)
    print("DONE:", sum(s[1] == "DONE" for s in stats), "events:", sum(s[2] for s in stats))
    with (V1 / "repair_log.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["recipe_id", "where", "kind", "detail"])
        w.writeheader()
        w.writerows(car.log)


if __name__ == "__main__":
    main()
