import pytest

from culinarystate.lotstate import ph as P


@pytest.fixture()
def reg(tmp_path):
    f = tmp_path / "ph.csv"
    f.write_text("\n".join([
        "name,ph_low,ph_high,source_id",
        "ING-LEMON,2.0,2.6,SYN-1",            # acid
        "ING-EGGWHITE,7.6,9.5,SYN-2",         # alkaline
        "ING-MILK,6.4,6.8,SYN-3",             # neither
        "ING-TOMATO,4.0,4.9,SYN-4",           # straddles 4.6
        "ING-OPEN,5.0,,SYN-5",                # lower bound only
        "baking soda,8.1,8.1,SYN-6",          # keyed by food name
    ]) + "\n", encoding="utf-8")
    return P.PhRegistry.load(f)


def flags(reg, members):
    return P.ph_record(members, reg)["flags"]


def test_member_status_thresholds():
    assert P.member_status(P.PhRange(2.0, 2.6, "s")) == {"acid": "YES", "alkaline": "NO"}
    assert P.member_status(P.PhRange(7.6, 9.5, "s")) == {"acid": "NO", "alkaline": "YES"}
    assert P.member_status(P.PhRange(6.4, 6.8, "s")) == {"acid": "NO", "alkaline": "NO"}
    assert P.member_status(P.PhRange(4.0, 4.9, "s"))["acid"] == "MAYBE"
    assert P.member_status(P.PhRange(4.6, 4.6, "s"))["acid"] == "YES"              # upper bound <= 4.6 is acid
    assert P.member_status(P.PhRange(5.0, None, "s")) == {"acid": "NO", "alkaline": "MAYBE"}   # open above: never POINT
    assert P.member_status(None) == {"acid": "UNKNOWN", "alkaline": "UNKNOWN"}


def test_lot_flags_kleene(reg):
    f = flags(reg, [("ING-LEMON", None), ("ING-MILK", None)])
    assert f == {"CONTAINS_ACID_MEMBER": "TRUE", "CONTAINS_ALKALINE_MEMBER": "FALSE", "ALL_MEMBERS_ACID": "FALSE"}
    f = flags(reg, [("ING-LEMON", None), ("ING-UNKNOWN", None)])        # one acid member decides CONTAINS, not ALL
    assert f["CONTAINS_ACID_MEMBER"] == "TRUE" and f["ALL_MEMBERS_ACID"] == "UNKNOWN"
    f = flags(reg, [("ING-LEMON", None)])
    assert f["ALL_MEMBERS_ACID"] == "TRUE"
    f = flags(reg, [("ING-TOMATO", None), ("ING-MILK", None)])          # straddling member: acid unknown, milk NO
    assert f["CONTAINS_ACID_MEMBER"] == "UNKNOWN" and f["ALL_MEMBERS_ACID"] == "FALSE"
    f = flags(reg, [("ING-EGGWHITE", None), ("ING-LEMON", None)])
    assert f["CONTAINS_ALKALINE_MEMBER"] == "TRUE" and f["CONTAINS_ACID_MEMBER"] == "TRUE"
    f = flags(reg, [("ING-MILK", None), ("ING-MILK", None)])
    assert f["CONTAINS_ACID_MEMBER"] == "FALSE" and f["CONTAINS_ALKALINE_MEMBER"] == "FALSE"


def test_name_keyed_rows_and_no_mixture_number(reg):
    rec = P.ph_record([("ING-X", "baking soda"), ("ING-MILK", None)], reg)
    assert rec["flags"]["CONTAINS_ALKALINE_MEMBER"] == "TRUE"
    assert rec["provenance"]["mixture_ph"] == "NOT_COMPUTED"
    assert "value" not in rec and "low" not in rec and "high" not in rec
    assert rec["member_ranges"][0]["source_id"] == "SYN-6"


def test_absent_registry_is_all_unknown():
    rec = P.ph_record([("ING-LEMON", "lemon")], None)
    assert rec["flags"] == {f: "UNKNOWN" for f in P.FLAGS} and rec["mask"] == 0
    assert rec["provenance"]["registry"] == "ABSENT"


def test_empty_lot_is_unknown(reg):
    assert flags(reg, []) == {f: "UNKNOWN" for f in P.FLAGS}


def test_other_lane_draft_format_with_crosswalk(tmp_path):
    reg_csv = tmp_path / "food.csv"
    reg_csv.write_text("ph_id,item_raw,item_norm,ph_low,ph_high,source_id\n"
                       "FDAPH-1,Lemon juice,lemon juice,2.00,2.60,SRC-X\n"
                       "FDAPH-2,Abalone mushroom,abalone mushroom,5.00,,SRC-X\n", encoding="utf-8")
    xw = tmp_path / "xw.csv"
    xw.write_text("ph_id,ing_id,confidence_band,rank\nFDAPH-1,ING-9,HIGH,1\nFDAPH-2,ING-8,LOW,1\n", encoding="utf-8")
    r = P.PhRegistry.load(reg_csv, crosswalk=xw, crosswalk_min_band="HIGH")
    assert r.lookup("ING-9").high == 2.6
    assert r.lookup("ING-8") is None                                      # LOW crosswalk rows are not used
    assert r.lookup(None, "Lemon Juice").low == 2.0
    assert P.ph_record([("ING-9", None)], r)["flags"]["ALL_MEMBERS_ACID"] == "TRUE"
