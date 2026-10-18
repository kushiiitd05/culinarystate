#!/usr/bin/env python3
"""Write ledgers/schemas/<PREFIX>.schema.json from the Python registry (single source)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.registry import R  # noqa: E402

out = ROOT / "ledgers" / "schemas"
out.mkdir(parents=True, exist_ok=True)
for prefix, schema in R.items():
    (out / f"{prefix}.schema.json").write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {len(R)} schemas to {out.relative_to(ROOT)}")
