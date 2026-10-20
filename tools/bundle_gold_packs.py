#!/usr/bin/env python3
"""Split an annotator's single bundle JSON into per-recipe gold-1.0 files (for gold_cli validate / agree), or re-bundle them.

  /opt/anaconda3/bin/python tools/bundle_gold_packs.py split Kush     # Kush_all_20.json -> _split/Kush/<id>.Kush.json
  /opt/anaconda3/bin/python tools/bundle_gold_packs.py bundle Kush    # _split/Kush/*.json -> Kush_all_20.json
Only the annotator's own bundle is read or written. Local-only (recipe text).
"""
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "annotation" / "gold" / "evidence_first_expansion"


def main():
    cmd, who = sys.argv[1], sys.argv[2]
    bundle, split = D / f"{who}_all_20.json", D / "_split" / who
    if cmd == "split":
        b = json.loads(bundle.read_text())
        split.mkdir(parents=True, exist_ok=True)
        for d in b["recipes"]:
            (split / f"{d['recipe_id']}.{who}.json").write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
        print(f"{len(b['recipes'])} files -> {split}")
    elif cmd == "bundle":
        b = json.loads(bundle.read_text())
        b["recipes"] = [json.loads(f.read_text()) for f in sorted(split.glob(f"*.{who}.json"))]
        b["n_recipes"] = len(b["recipes"])
        bundle.write_text(json.dumps(b, indent=1, ensure_ascii=False) + "\n")
        print(f"{len(b['recipes'])} recipes -> {bundle.name}")
    else:
        sys.exit("usage: split|bundle Kush|Parv")


if __name__ == "__main__":
    main()
