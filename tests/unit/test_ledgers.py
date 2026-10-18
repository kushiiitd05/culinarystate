import copy

import pytest

from culinarystate.ledgers.registry import PREFIXES, R
from culinarystate.ledgers.store import IdMinter, LedgerStore
from culinarystate.ledgers.validate import ValidationFailed, errors
from tests.fixtures.ledger_examples import EXAMPLES, UNK, i, m

REQUIRED_PREFIXES = """SRC SNAP API STUDY MEAS ING ALIAS MOL IMAP PROC TOOL COND SVAR UNIT QNT POR ALLOC
INST EVT STATE REF GRAPH EVD RXN WARN ALLERGEN MODEL DATASET SPLIT EXP GATE RQ RS CLM ENTITY REC""".split()


def ex(prefix, **changes):
    rec = copy.deepcopy(EXAMPLES[prefix])
    rec.update(changes)
    return rec


def test_every_required_prefix_has_schema_and_example():
    assert set(REQUIRED_PREFIXES) <= set(PREFIXES)
    assert set(EXAMPLES) == set(PREFIXES)


@pytest.mark.parametrize("prefix", sorted(EXAMPLES))
def test_examples_are_valid(prefix):
    assert errors(EXAMPLES[prefix]) == []


@pytest.mark.parametrize("prefix", sorted(R))
def test_id_pattern_enforced(prefix):
    assert errors(ex(prefix, id=f"{prefix}-12"))


def test_unknown_field_rejected():
    assert errors(ex("ING", favourite_colour="red"))


# ---- UNKNOWN / values ----
def test_unknown_value_cannot_carry_number():
    rec = ex("QNT", normalized={"status": "UNKNOWN", "value": 120, "unit": "g"})
    assert any("normalized" in e for e in errors(rec))


def test_measured_needs_value_and_unit():
    assert errors(ex("COND", duration={"status": "MEASURED", "value": 10}))


def test_censored_needs_censor_block():
    assert errors(ex("COND", duration={"status": "CENSORED"}))


# ---- human vs AI verification ----
def test_ai_cannot_be_human_verifier():
    rec = ex("ING", verification={"status": "HUMAN_VERIFIED", "verifier": "claude",
                                  "verified_at": "2026-10-18T05:00:00+00:00"})
    assert any("verifier" in e for e in errors(rec))


def test_human_verification_ok():
    rec = ex("ING", verification={"status": "HUMAN_VERIFIED", "verifier": "Parv",
                                  "verified_at": "2026-10-18T05:00:00+00:00"})
    assert errors(rec) == []


def test_human_verification_needs_timestamp():
    assert errors(ex("ING", verification={"status": "HUMAN_VERIFIED", "verifier": "Kush"}))


# ---- EVD laws ----
def _llm_evd(**kw):
    rec = ex("EVD", origin_type="PRIMARY_STUDY", study_id_status="NOT_IDENTIFIABLE", design="CONTROLLED_EXPERIMENT",
             provenance={"method": "LLM", "source_ids": [i("SRC")], "locator": "Table 2", "agent": "claude"})
    rec.update(kw)
    return rec


def test_e4_requires_human_verification():
    assert any("E4" in e for e in errors(_llm_evd(tier="E4")))
    ok = _llm_evd(tier="E4", verification={"status": "HUMAN_VERIFIED", "verifier": "Kush",
                                           "verified_at": "2026-10-18T05:00:00+00:00"})
    assert errors(ok) == []


def test_e5_ok_unverified_and_not_human():
    assert errors(_llm_evd(tier="E5")) == []
    bad = _llm_evd(tier="E5", verification={"status": "HUMAN_VERIFIED", "verifier": "Kush",
                                            "verified_at": "2026-10-18T05:00:00+00:00"})
    assert errors(bad)


def test_primary_study_cannot_be_study_not_applicable():
    assert errors(_llm_evd(tier="E5", study_id_status="NOT_APPLICABLE"))


def test_primary_study_present_needs_ids():
    assert errors(_llm_evd(tier="E5", study_id_status="PRESENT"))
    assert errors(_llm_evd(tier="E5", study_id_status="PRESENT", study_ids=[i("STUDY")])) == []


def test_database_aggregate_may_omit_study_ids():  # AH1
    assert errors(EXAMPLES["EVD"]) == []


def test_grounded_tier_needs_locator():
    rec = ex("EVD", provenance={"method": "IMPORT", "source_ids": [i("SRC")]})
    assert any("locator" in e for e in errors(rec))


def test_source_family_always_required():
    rec = ex("EVD")
    del rec["source_family_id"]
    assert errors(rec)


def test_percent_change_consistency():
    rec = ex("EVD", before=m(50, "mg/100g"), after=m(25, "mg/100g"),
             derived={"percent_change": m(-50, "%")})
    assert errors(rec) == []
    rec["derived"]["percent_change"] = m(-10, "%")
    assert any("percent_change" in e for e in errors(rec))


def test_censored_flag_must_match():
    rec = ex("EVD", after={"status": "CENSORED", "censor": {"kind": "LT_LOD", "limit": 0.1}, "unit": "mg"})
    assert any("censored" in e for e in errors(rec))


# ---- quantity: no invented grams ----
def test_no_invented_grams_from_cup():
    rec = ex("QNT", normalized=m(125, "g"))
    assert any("portion_id" in e for e in errors(rec))
    assert errors(ex("QNT", normalized=m(125, "g"), portion_id=i("POR"), q_level="Q2")) == []


def test_grams_from_mass_unit_ok():
    rec = ex("QNT", raw="200g feta", parsed={"kind": "NUMBER", "value": 200, "unit_raw": "g"},
             normalized=m(200, "g"))
    assert errors(rec) == []


def test_qualitative_quantity_never_numeric():
    rec = ex("QNT", raw="a pinch of salt", parsed={"kind": "QUALITATIVE", "unit_raw": "pinch"},
             normalized=m(0.3, "g"), portion_id=i("POR"))
    assert errors(rec)


def test_por_requires_source():
    assert errors(ex("POR", provenance={"method": "MANUAL", "source_ids": []}))


# ---- other laws ----
def test_imap_types():
    assert errors(ex("IMAP", relation="MEASURED_CONCENTRATION"))
    assert errors(ex("IMAP", relation="PRESENCE", concentration=m(3, "mg/kg")))
    assert errors(ex("IMAP", relation="PROCESS_CHANGE"))
    ok = ex("IMAP", relation="MEASURED_CONCENTRATION", concentration=m(3, "mg/kg"), basis="FRESH_WEIGHT")
    assert errors(ok) == []


def test_medium_heat_not_numeric():
    rec = ex("COND", temperatures=[{"location": "MEDIUM",
                                    "value": {"status": "MEASURED", "value": 180, "unit": "degC",
                                              "raw": "medium heat"}}])
    assert errors(rec)


def test_state_append_only_chain():
    assert errors(ex("STATE", state_version=1))
    assert errors(ex("STATE", state_version=1, previous_state_id=i("STATE"))) == []
    assert errors(ex("STATE", overrides_state_id=i("STATE", 2)))  # PLANNED cannot override


def test_allergen_not_flavordb():
    assert errors(ex("ALLERGEN", notes="category taken from FlavorDB"))


def test_sota_claim_needs_gate():
    assert errors(ex("CLM", claim_type="SOTA"))
    assert errors(ex("CLM", experiment_ids=[]))


def test_model_test_selection_not_clean_reproduction():
    assert errors(ex("MODEL", reproduction_status="REPRODUCED", selected_on="TEST"))


# ---- store / ids ----
def test_minter_dedup_and_no_reuse(tmp_path):
    ids = IdMinter(tmp_path)
    a = ids.mint("MOL", key="MWOOGOJBHIARFG-UHFFFAOYSA-N")
    assert ids.mint("MOL", key="MWOOGOJBHIARFG-UHFFFAOYSA-N") == a
    b = ids.mint("MOL")
    assert a == "MOL-000001" and b == "MOL-000002"
    assert IdMinter(tmp_path).mint("MOL") == "MOL-000003"  # persisted


def test_store_append_versioning_and_history(tmp_path):
    st = LedgerStore(tmp_path)
    rid = st.ids.mint("ING", key="spinach")
    rec = ex("ING", id=rid)
    st.append(rec)
    with pytest.raises(ValueError):
        st.append(rec)                                   # same version twice
    st.revise(rid, {"category": "leafy vegetable"}, created_by="Parv")
    hist = LedgerStore(tmp_path).history(rid)            # reload from disk
    assert [h["version"] for h in hist] == [1, 2]
    assert hist[0].get("category") is None and hist[1]["category"] == "leafy vegetable"


def test_store_rejects_unminted_and_invalid(tmp_path):
    st = LedgerStore(tmp_path)
    with pytest.raises(ValueError):
        st.append(ex("ING", id="ING-000099"))
    rid = st.ids.mint("QNT")
    with pytest.raises(ValidationFailed):
        st.append(ex("QNT", id=rid, normalized=m(125, "g")))


def test_store_does_not_mutate_input(tmp_path):
    st = LedgerStore(tmp_path)
    rid = st.ids.mint("TOOL")
    rec = ex("TOOL", id=rid)
    del rec["schema_version"]
    snapshot = copy.deepcopy(rec)
    st.append(rec)
    assert rec == snapshot
