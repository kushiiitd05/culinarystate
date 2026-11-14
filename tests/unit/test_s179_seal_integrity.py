"""S179 (T2-C14-R1): seal integrity check re-derives the reserved list and compares every hash; counts only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from culinarystate.lineage import seal_integrity as SI  # noqa: E402
from test_step15a_R_reserved_seal import _seal, world  # noqa: E402,F401  (fixture reuse)


def _args(world, commitment):
    return dict(root=world["root"], commitment=commitment,
                sealed_bytes=(world["private"] / "reserved.jsonl").read_bytes(),
                seed_text=(world["private"] / "seed.txt").read_text(encoding="utf-8"))


def test_intact_seal_passes_every_check(world):  # noqa: F811
    c = _seal(world)
    out = SI.check(**_args(world, c))
    assert out["verdict"] == "PASS", out
    assert all(v == "PASS" for v in out["checks"].values())
    assert out["n_reserved"] == c["n_reserved"]


def test_tampered_list_seed_or_ledger_fail(world):  # noqa: F811
    c = _seal(world)
    a = _args(world, c)
    bad = dict(a, sealed_bytes=a["sealed_bytes"].replace(b'"n_rows": ', b'"n_rows": 9', 1))
    assert SI.check(**bad)["checks"]["sealed_list_matches_commitment"] == "FAIL"
    assert SI.check(**dict(a, seed_text="other"))["checks"]["seed_matches_commitment"] == "FAIL"
    evd = world["root"] / "ledgers/data/EVD.jsonl"
    evd.write_bytes(evd.read_bytes() + b"\n")
    out = SI.check(**a)
    assert out["checks"]["evd_snapshot_unchanged"] == "FAIL" and out["verdict"] == "FAIL"


def test_output_has_no_group_ids_or_seed(world):  # noqa: F811
    c = _seal(world)
    a = _args(world, c)
    blob = json.dumps(SI.check(**a))
    first = json.loads(a["sealed_bytes"].decode().splitlines()[0])["group_id"]
    assert first not in blob and a["seed_text"].strip() not in blob
