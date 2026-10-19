#!/usr/bin/env python3
"""Gold annotation CLI.

  python tools/gold_cli.py validate annotation/gold/R001.Kush.json
  python tools/gold_cli.py agree annotation/gold/R001.Kush.json annotation/gold/R001.Parv.json
  python tools/gold_cli.py replay annotation/gold/pilot_20/Kush/R001.Kush.json   # print the replayed final state
  python tools/gold_cli.py schema            # writes annotation/gold_schema.json
  python tools/gold_cli.py examples          # writes annotation/examples/*.json
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.agreement import adjudication_rows, agreement  # noqa: E402
from culinarystate.annotation.examples import write_examples  # noqa: E402
from culinarystate.annotation.gold import GOLD_SCHEMA, to_events, validate_gold  # noqa: E402
from culinarystate.state_graph.engine import replay  # noqa: E402


def load(p):
    return json.loads(Path(p).read_text())


def cmd_validate(path):
    doc = load(path)
    errs = validate_gold(doc)
    if not errs:
        g = replay(to_events(doc))
        errs = [f"replay: {x}" for x in g.issues]
        if not errs:
            print(f"OK {path}: {len(doc['ingredient_lines'])} lines, {len(doc['steps'])} steps, "
                  f"{sum(len(s['events']) for s in doc['steps'])} events, alive={g.alive()}")
            return 0
    print(f"FAIL {path}")
    for e in errs:
        print("  -", e)
    return 1


def cmd_replay(path):
    """Print the state the annotation replays to, so the annotator can check it against the recipe text."""
    doc = load(path)
    errs = validate_gold(doc)
    if errs:
        print(f"FAIL {path} (run validate)")
        return 1
    g = replay(to_events(doc))
    print(f"{doc['recipe_id']} ({doc['annotator']}, {doc['status']}): issues={list(g.issues)}")
    for ent in g.versions:
        v = g.current(ent)
        flags = [] if v.alive else ["DEAD"]
        print(f"  {ent}: {'/'.join(flags) or 'alive'} qty={v.qty.render()!r} location={v.location!r}")
        for name, b in v.fields:
            print(f"      {name} = {b.value!r} [{b.trajectory}]")
    print("  process history:", sorted({e.process for e in to_events(doc) if getattr(e, 'process', None)}))
    for e in g.edges:
        print("  edge:", e.src, e.relation, e.dst)
    return 0


def cmd_agree(a, b):
    da, db = load(a), load(b)
    r = agreement(da, db)
    rows = adjudication_rows(da, db)
    out = ROOT / "annotation" / "adjudication" / f"{da['recipe_id']}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["recipe_id", "where", "field", "kush", "parv", "adjudicated", "rationale",
                                           "handbook_rule"])
        w.writeheader()
        w.writerows(rows)
    summary = {k: r[k] for k in ("spans_relaxed", "char_kappa_mean", "concept_agreement")}
    summary["span_exact_f1"] = r["spans_exact"]["micro"]["f1"]
    summary["merge_split_f1"] = r["state"]["merge_split_f1"]["f1"]
    summary["state_field_accuracy"] = r["state"]["state_field_accuracy"]
    print(json.dumps(summary, indent=1))
    print(f"{len(rows)} disagreements -> {out}")
    return 0


if __name__ == "__main__":
    cmd, *args = sys.argv[1:] or ["help"]
    if cmd == "validate":
        sys.exit(max(cmd_validate(p) for p in args))
    if cmd == "replay":
        sys.exit(max(cmd_replay(p) for p in args))
    if cmd == "agree":
        sys.exit(cmd_agree(*args))
    if cmd == "schema":
        (ROOT / "annotation" / "gold_schema.json").write_text(json.dumps(GOLD_SCHEMA, indent=2) + "\n")
        print("wrote annotation/gold_schema.json")
        sys.exit(0)
    if cmd == "examples":
        for p in write_examples(ROOT / "annotation" / "examples"):
            print("wrote", p.relative_to(ROOT))
        sys.exit(0)
    print(__doc__)
