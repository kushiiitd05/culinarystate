"""S179: every committed ledgers/schemas/<PREFIX>.schema.json equals the Python registry (single source). Before this
test, KGE.schema.json lacked three predicates the registry validates (ING_HEALTH_ASSOCIATION, ING_COSYLAB_CATEGORY,
ING_CARBON_FOOTPRINT)."""
import json
from pathlib import Path

from culinarystate.ledgers.registry import R

SCHEMAS = Path(__file__).resolve().parents[2] / "ledgers" / "schemas"


def test_every_registry_schema_is_committed_and_identical():
    drift = [p for p, s in R.items() if json.loads((SCHEMAS / f"{p}.schema.json").read_text(encoding="utf-8")) != s]
    assert drift == [], drift
