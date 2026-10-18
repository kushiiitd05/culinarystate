#!/usr/bin/env python3
"""X12: OpenPI 2.0 (MIT, allenai/openpi-dataset) food subset -> DEL-3 external entity-state set.

  /opt/anaconda3/bin/python tools/build_openpi_food.py
Keeps procedures with topic "Food and Entertaining" (train/dev/test kept separate). For each step: entity, attribute,
before -> after (crowd annotations, '|' = alternative phrasings). Also links entities to ING where the lexicon matches.
Writes data/interim/openpi/food_states.jsonl (local) + reports/openpi_food_v1.md (counts only).
"""
import ast
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402
from culinarystate.vocab.line_link import LineLinker  # noqa: E402

RAW = ROOT / "data" / "raw" / "openpi"
OUT = ROOT / "data" / "interim" / "openpi"
SPLITS = {"train": "train-ranked.json", "dev": "dev-ranked.json", "test": "test-ranked.json"}


def lit(x):
    return ast.literal_eval(x) if isinstance(x, str) else x


def main() -> None:
    st = LedgerStore()
    names = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en":
            names.setdefault(norm(a["normalized"]), a["ingredient_id"])
    linker = LineLinker(names, set())
    OUT.mkdir(parents=True, exist_ok=True)
    stats, attrs, n_link, n_ent = Counter(), Counter(), 0, 0
    with (OUT / "food_states.jsonl").open("w") as fh:
        for split, fn in SPLITS.items():
            data = json.loads((RAW / fn).read_text())
            for pid, p in (data.items() if isinstance(data, dict) else enumerate(data)):
                if p.get("topics") != "Food and Entertaining":
                    continue
                steps = lit(p["steps"])
                states = []
                for s in lit(p.get("states") or "[]"):
                    ent = s["entity"]
                    ing = next((linker.mentions(e)[0] for e in ent.split("|") if linker.mentions(e)), None)
                    n_ent += 1
                    n_link += bool(ing)
                    for step, changes in s["answers"].items():
                        for c in changes:
                            attrs[c["attribute"].split("|")[0].strip()] += 1
                            states.append({"entity": ent, "ingredient_id": ing, "step": int(step.removeprefix("step")),
                                           "attribute": c["attribute"], "before": c["before"], "after": c["after"]})
                stats[split] += 1
                stats[f"{split}_changes"] += len(states)
                fh.write(json.dumps({"split": split, "openpi_id": str(pid), "goal": p["goal"], "steps": steps,
                                     "states": states}, ensure_ascii=False) + "\n")
    lines = ["# OpenPI 2.0 food subset (X12, MIT)", "",
             f"- procedures: train {stats['train']}, dev {stats['dev']}, test {stats['test']}",
             f"- state changes: train {stats['train_changes']:,}, dev {stats['dev_changes']:,}, test {stats['test_changes']:,}",
             f"- entities linked to ING: {n_link}/{n_ent}",
             "- top attributes: " + ", ".join(f"{k} {v}" for k, v in attrs.most_common(15)),
             "- use: external check for DEL-3 state tracking (entity/attribute before→after per step); crowd labels, "
             "open vocabulary, '|' = alternative phrasings. Not our Gold."]
    (ROOT / "reports" / "openpi_food_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
