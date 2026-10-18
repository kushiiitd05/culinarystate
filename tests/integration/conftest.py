"""Shared fixtures over the real local ledgers (marker `ledgers`; run with `pytest -m ledgers`)."""
from pathlib import Path

import pytest

from culinarystate.ledgers.store import LedgerStore

ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "ledgers" / "data" / "EVD.jsonl").exists():
    pytest.skip("local ledgers not present", allow_module_level=True)


@pytest.fixture(scope="session")
def store():
    return LedgerStore()


@pytest.fixture(scope="session")
def latest(store):
    cache = {}

    def get(prefix):
        if prefix not in cache:
            cache[prefix] = store.all_latest(prefix)
        return cache[prefix]
    return get
