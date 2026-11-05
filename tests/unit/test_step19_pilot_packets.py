"""Synthetic-fixture tests for the Step 19 packet maker (no real recipe text)."""
import json

import pytest

from culinarystate.annotation import pilot_packets as pp

RECS = {
    "R1": {"source_family": "FOODCOM", "ingredient_lines": ["1 cup flour", "2 eggs"], "steps": ["Mix.", "Bake 20 minutes."]},
    "R2": {"source_family": "A1_BBC_GOOD_FOOD", "ingredient_lines": ["200g butter"], "steps": ["Melt."]},
    "R3": {"source_family": "WIKIBOOKS", "ingredient_lines": ["salt"], "steps": ["Add salt.", "Stir."]},
}
SEED = "9fa0008602a39537"


def build(letter, recs=RECS, seed=SEED):
    return pp.build_packets(sorted(recs), recs, letter=letter, seed_hex=seed)


def test_packets_are_blank_and_carry_no_model_output():
    packets, key = build("B")
    for p in packets:
        d = p["doc"]
        assert d["schema_version"] == "gold-1.0" and d["status"] == "DRAFT" and d["annotator"] == "Parv"
        assert all(l["entity"] == "TODO" and l["concept"] == "TODO" and l["spans"] == [] for l in d["ingredient_lines"])
        assert all(s["events"] == [] and s["spans"] == [] and s["coref"] == [] for s in d["steps"])
        assert d["unknowns"] == [] and d["notes"] == "" and pp.is_pristine(d)


def test_packet_ids_are_letter_scoped_and_hide_recipe_ids():
    pa, _ = build("A")
    pb, _ = build("B")
    assert {p["packet_id"] for p in pa} == {f"DGP-A-000{i}" for i in (1, 2, 3)}
    assert {p["packet_id"] for p in pb} == {f"DGP-B-000{i}" for i in (1, 2, 3)}
    for p in pa + pb:
        blob = json.dumps(p["doc"])
        assert not any(rid in blob for rid in RECS)


def test_order_is_seeded_and_differs_per_annotator_but_is_reproducible():
    _, ka = build("A")
    _, kb = build("B")
    assert build("A")[1] == ka and build("B")[1] == kb
    assert sorted(ka.values()) == sorted(kb.values()) == sorted(RECS)
    assert build("A", seed="0000000000000001")[1] != ka


def test_same_recipe_has_the_same_content_hash_for_both_annotators():
    pa, ka = build("A")
    pb, kb = build("B")
    ha = {ka[p["packet_id"]]: p["content_sha256"] for p in pa}
    hb = {kb[p["packet_id"]]: p["content_sha256"] for p in pb}
    assert ha == hb


def test_manifest_rows_are_text_free():
    packets, key = build("B")
    rows = pp.manifest_rows(packets)
    blob = json.dumps(rows)
    assert "flour" not in blob and not any(rid in blob for rid in RECS)
    assert all(r["ai_prefill"] == "NONE" and r["model_outputs_embedded"] == "NONE" for r in rows)


def test_refuses_bad_letter_empty_and_missing_text():
    with pytest.raises(pp.PacketError, match="letter"):
        build("C")
    with pytest.raises(pp.PacketError, match="seed"):
        build("A", seed="")
    with pytest.raises(pp.PacketError, match="no text"):
        pp.build_packets(["R9"], RECS, letter="A", seed_hex=SEED)
    with pytest.raises(pp.PacketError, match="no text"):
        pp.build_packets(["R1"], {"R1": {"source_family": "FOODCOM", "ingredient_lines": [], "steps": []}}, letter="A", seed_hex=SEED)


def test_pristine_detects_human_work():
    packets, _ = build("A")
    d = json.loads(json.dumps(packets[0]["doc"]))
    d["steps"][0]["events"].append({"type": "x"})
    assert not pp.is_pristine(d)
