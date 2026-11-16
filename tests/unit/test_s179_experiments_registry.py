"""S179 (T9-C11-R1): M1..M9 experiment registry carries every SSOT 257A.20 field, none empty."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "registry" / "experiments_S171_S175.csv"
FIELDS = ("experiment_id", "research_question_id", "hypothesis", "code_commit", "dataset_version", "split_version",
          "schema_version", "ontology_version", "prompt_model_versions", "baselines", "model_config", "random_seeds",
          "compute", "metrics", "confidence_intervals", "artifacts", "failure_notes", "decision", "next_dependency")


def test_one_row_per_milestone_and_no_empty_mandatory_field():
    rows = list(csv.DictReader(P.open(newline="")))
    assert [r["milestone"] for r in rows] == [f"M{i}" for i in range(1, 10)]
    for r in rows:
        assert all(r.get(k, "").strip() for k in FIELDS), r["milestone"]
        assert r["decision"] in {"KEEP", "MODIFY", "DROP", "NEED_DATA"}


def test_no_ledger_id_is_minted_here():
    rows = list(csv.DictReader(P.open(newline="")))
    assert all(r["experiment_id"].startswith("NOT_ASSIGNED") for r in rows)
