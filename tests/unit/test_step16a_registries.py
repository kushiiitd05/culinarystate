"""Step 16a batch 1: DRAFT registries parse, enums complete, generator deterministic, ledgers untouched."""
import csv
import hashlib
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("b16a", ROOT / "tools/step16a_build_registries.py")
b16a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b16a)

CARD = {
    "event_kind": {"ACTION", "ENDPOINT_CHECK", "OBSERVATION", "CONDITIONAL", "WAIT_REST", "CONTROL"},
    "modality": {"REQUIRED", "OPTIONAL", "NEGATED", "CONDITIONAL", "HYPOTHETICAL"},
    "temporal_relation": {"SEQUENTIAL", "PARALLEL", "OVERLAPS", "UNTIL", "REPEAT_UNTIL"},
    "transformation_mode": {"MECHANICAL", "THERMAL", "CHEMICAL_CURING", "BIOCHEMICAL_FERMENTATION",
                            "TRANSFER", "TEMPORAL_REST"},
    "tool_role": {"INSTRUMENT", "CONTAINER", "HEAT_SOURCE", "MEASURE"},
    "entity_type": {"INGREDIENT_LOT", "INTERMEDIATE", "MIXTURE", "RESERVED_PORTION",
                    "DISCARDED_PORTION", "TOOL_CONTENTS"},
    "lifecycle": {"ACTIVE", "RESERVED", "INCORPORATED", "DISCARDED", "SERVED", "UNRESOLVED"},
    "field_status": {"KNOWN", "UNKNOWN", "NOT_APPLICABLE", "CONFLICTING", "CENSORED"},
    "claim_route": {"EXPLICIT", "INFERRED_RULE", "INFERRED_LLM", "MODEL", "SIMULATED"},
    "annotation_mode": {"OPEN"},
}
OUT = [ROOT / "registry/processes/process_hierarchy_v1_DRAFT.csv",
       ROOT / "registry/processes/endpoint_vocabulary_v1_DRAFT.csv",
       ROOT / "registry/tools/tool_hierarchy_v1_DRAFT.csv"] + \
      [ROOT / f"registry/recipe_semantics/{n}_registry_v1_DRAFT.csv" for n in CARD]
LEDGERS = ["SRC", "MEAS", "EVD", "COND", "PROC", "TOOL", "STUDY", "SNAP", "_ids"]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rows(p: Path):
    with p.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def ledger_hashes():
    return {n: sha(ROOT / f"ledgers/data/{n}.jsonl") for n in LEDGERS}


@pytest.fixture(scope="module", autouse=True)
def built():
    before = ledger_hashes()
    b16a.main()
    snap = {p: p.read_bytes() for p in OUT}
    b16a.main()
    return before, snap


@pytest.mark.parametrize("name", list(CARD))
def test_enum_registry(name):
    rs = rows(ROOT / f"registry/recipe_semantics/{name}_registry_v1_DRAFT.csv")
    assert list(rs[0].keys()) == ["code", "label", "definition", "source_ref", "status"]
    codes = [r["code"] for r in rs]
    assert len(codes) == len(set(codes))
    assert set(codes) == CARD[name]
    assert {r["status"] for r in rs} == {"DRAFT_PENDING_H4"}
    assert all(r["definition"] and r["source_ref"] for r in rs)


@pytest.mark.parametrize("p", OUT, ids=lambda p: p.name)
def test_csv_parses_and_ids_unique(p):
    rs = rows(p)
    assert rs
    key = "code" if "code" in rs[0] else "id"
    assert len({r[key] for r in rs}) == len(rs)


def test_hierarchy_rules():
    rs = rows(ROOT / "registry/processes/process_hierarchy_v1_DRAFT.csv")
    ids = {r["id"] for r in rs}
    assert all(r["level"] in ("", "1", "2", "3") for r in rs)
    for r in rs:
        if r["proposed_parent_id"]:
            assert r["proposed_parent_id"] in ids
        if r["endpoint_flag"] == "true":
            assert r["proposed_parent_id"] == "" and r["level"] == ""
    ep = {r["id"] for r in rows(ROOT / "registry/processes/endpoint_vocabulary_v1_DRAFT.csv")}
    assert ep == {r["id"] for r in rs if r["endpoint_flag"] == "true"}


def test_tool_needs_human_has_no_parent():
    for r in rows(ROOT / "registry/tools/tool_hierarchy_v1_DRAFT.csv"):
        if "NEEDS_HUMAN" in r["evidence"]:
            assert r["proposed_parent_id"] == ""


def test_generator_byte_identical(built):
    _, snap = built
    for p, data in snap.items():
        assert p.read_bytes() == data, p.name


def test_ledgers_unchanged(built):
    before, _ = built
    assert ledger_hashes() == before
    base = {r["path"]: r for r in rows(ROOT / "registry/baseline_ledger_hashes_08a_v1.csv")}
    for n in ["SRC", "MEAS", "EVD", "COND"]:
        assert base[f"ledgers/data/{n}.jsonl"]["sha256"] == before[n]
    for n in ["STUDY", "SNAP", "_ids"]:  # append-only ledgers: baseline bytes must remain a prefix
        row = base[f"ledgers/data/{n}.jsonl"]
        size = int(row["bytes"])
        with (ROOT / f"ledgers/data/{n}.jsonl").open("rb") as fh:
            head = fh.read(size)
        assert len(head) == size and hashlib.sha256(head).hexdigest() == row["sha256"]
