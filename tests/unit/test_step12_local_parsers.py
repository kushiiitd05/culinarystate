"""Step 12-local parsers: USDA Cooking Yields R2 CSV and the 11 remaining Bognar (2002) Part 2 tables.

PROVISIONAL_PENDING_G12_AUDIT. Every row, number and food name here is SYNTHETIC (self-authored to
mimic the file layouts the existing tools read: tools/infoods_transition_candidates.py for the R2
header, src/culinarystate/ingest/bognar.py for the pdftotext -layout table shape). No real value.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from culinarystate.ingest import bognar_remaining as B
from culinarystate.ingest import usda_yields_r2 as Y

R2_HEADER = ("NDB,Yield Description,Preparation Method1,Cooking Yield %,n,SD,Min,Max,"
             "Moisture Gain/ Loss %,Fat   Gain/ Loss %,Release Year2,Notes3")
R2_ROWS = [
    '99001,"SYNTHETIC beef cut A, separable lean",Braised,70.0,20,3.0,62.0,77.0,-25.00,-10.00,2010,',
    '99002,SYNTHETIC chicken part B,Roasted,75.5,,,,,,,1975,synthetic note',
    '99003,SYNTHETIC pork cut C,Grilled,abc,12,2.5,70,80,-20,-3,2012,',
]


def r2_text(header: str = R2_HEADER, rows: list[str] | None = None) -> str:
    return "\n".join([header, *(R2_ROWS if rows is None else rows)]) + "\n"


# ---------------------------------------------------------------- R2
def test_r2_status_and_roles() -> None:
    assert Y.STATUS == "PROVISIONAL_PENDING_G12_AUDIT"
    res = Y.parse_r2_text(r2_text())
    assert res.column_roles["Preparation Method1"] == "preparation_method"
    assert res.column_roles["Fat   Gain/ Loss %"] == "fat_change_pct"
    assert res.column_roles["Release Year2"] == "release_year"
    assert res.unmapped_columns == ("Notes3",)
    assert len(res.rows) == 3


def test_r2_raw_preserved_and_normalised_new_columns() -> None:
    row = Y.parse_r2_text(r2_text()).rows[0]
    assert row["raw"]["Yield Description"] == "SYNTHETIC beef cut A, separable lean"
    assert row["raw"]["Cooking Yield %"] == "70.0"
    n = row["normalised"]
    assert n["cooking_yield_pct"] == {"status": "MEASURED", "value": "70.0", "raw": "70.0"}
    assert n["n"]["value"] == "20" and n["sd"]["value"] == "3.0"
    assert n["moisture_change_pct"]["value"] == "-25.00"
    assert row["dispersion_type"] == "SD" and row["aggregation_level"] == "COMPILED_MEAN"
    assert row["regime"] == "D-A" and row["plane"] == "12-E" and row["time_series"] == "NONE"
    assert row["temperature"] == {"status": "UNKNOWN"} and row["duration"] == {"status": "UNKNOWN"}
    assert row["independence_resolution"] == "SOURCE_FAMILY_ONLY"
    assert row["censor_kind"] == "NOT_ASSESSED"               # "nearest 5%" needs the data dictionary read
    assert row["source_line"] == 2


def test_r2_blank_is_not_reported_never_zero() -> None:
    row = Y.parse_r2_text(r2_text()).rows[1]
    for role in ("n", "sd", "min", "max", "moisture_change_pct", "fat_change_pct"):
        assert row["normalised"][role] == {"status": "NOT_REPORTED", "raw": ""}
    assert row["dispersion_type"] == "NOT_REPORTED"
    assert row["release_year_flag"] == "RELEASE_YEAR_1975"


def test_r2_unparsed_value_kept_raw() -> None:
    row = Y.parse_r2_text(r2_text()).rows[2]
    assert row["normalised"]["cooking_yield_pct"] == {"status": "UNPARSED", "raw": "abc"}
    assert "UNPARSED:cooking_yield_pct" in row["flags"]


def test_r2_optional_column_absent_and_required_missing() -> None:
    hdr = "NDB,Yield Description,Preparation Method1,Cooking Yield %"
    res = Y.parse_r2_text(r2_text(hdr, ["99004,SYNTHETIC lamb D,Broiled,80.0"]))
    assert res.rows[0]["normalised"]["sd"] == {"status": "NOT_PRESENT_IN_FILE"}
    with pytest.raises(Y.R2ParseError):
        Y.parse_r2_text(r2_text("NDB,Yield Description,Cooking Yield %", ["1,x,2"]))
    with pytest.raises(Y.R2ParseError):
        Y.parse_r2_text(r2_text("NDB,NDB ,Yield Description,Preparation Method,Cooking Yield %", ["1,1,x,y,2"]))


def test_r2_ragged_row_flagged_not_guessed() -> None:
    res = Y.parse_r2_text(r2_text(rows=["99005,SYNTHETIC veal E,Braised"]))
    assert res.rows == [] and res.problems == ("line 2: 3 cells vs 12 header columns, row skipped",)


def test_r2_file_reader_encoding_and_hash(tmp_path: Path) -> None:
    p = tmp_path / "r2.csv"
    p.write_bytes(r2_text(rows=['99006,SYNTHETIC cut \xb0F,Roasted,71.0,,,,,,,2010,']).encode("cp1252"))
    res = Y.parse_r2_file(p)
    assert res.encoding == "cp1252" and res.input_sha256 and res.input_bytes == p.stat().st_size
    assert res.rows[0]["raw"]["Yield Description"] == "SYNTHETIC cut °F"
    p2 = tmp_path / "r2u.csv"
    p2.write_text(r2_text(), encoding="utf-8-sig")
    assert Y.parse_r2_file(p2).encoding == "utf-8-sig"


def test_r2_deterministic() -> None:
    assert Y.parse_r2_text(r2_text()) == Y.parse_r2_text(r2_text())


# ---------------------------------------------------------------- Bognar remaining tables
def at(*pairs: tuple[int, str]) -> str:
    """Place tokens at fixed character columns (mimics pdftotext -layout)."""
    out = ""
    for col, tok in pairs:
        out = out.ljust(col) + tok
    return out


def bognar_text() -> str:
    lines = [
        "Part 1 : Weight yield",
        "Table 2: Weight yield factors by cooking of synthetic group two",
        at((0, "Synthetic dish"), (30, "0.95")),
        "Part 2 : Average retention factors of food constituents",
        "Table 1: Retention factors by cooking of synthetic group one",
        at((25, "Retention factor")),
        at((0, "Constituents"), (20, "boil"), (30, "steam")),
        at((20, "A"), (30, "A")),
        at((0, "Vitamin C"), (20, "0.70"), (30, "0.80")),
        "Table 2: Retention factors by cooking of synthetic group two",
        "- synthetic dish family",
        at((30, "Retention factor")),
        at((0, "Constituents"), (24, "boil"), (49, "steam")),
        at((21, "a)"), (31, "b)"), (45, "a)"), (55, "b)")),
        at((21, "A"), (31, "A"), (45, "A"), (55, "A")),
        at((0, "Vitamin C"), (20, "0.60"), (30, "0.65"), (44, "0.75"), (54, "0.78")),
        at((0, "Thiamin 1)"), (20, "0.80"), (30, "-"), (44, "0.85"), (54, "1.00")),
        at((0, "Fat uptake"), (20, "0.10"), (30, "0.10"), (44, "0.10"), (54, "0.10")),
        at((0, "Riboflavin"), (20, "0.90"), (30, "0.95")),
        at((0, "Folate"), (20, "0.50"), (30, "0.55"), (44, "0.70"), (54, "0.72")),
        "a) synthetic variant one; b) synthetic variant two",
        "Table 13: Retention factors by cooking of synthetic group thirteen",
        at((30, "Retention factor")),
        at((0, "Constituents"), (24, "boil"), (40, "steam")),
        at((21, "a)"), (31, "b)"), (43, "*")),
        at((21, "A"), (31, "A"), (43, "A")),
        at((0, "Folate"), (20, "0.50"), (30, "0.55"), (42, "0.70")),
        "Table 29: Retention factors by preparation of synthetic beverages",
        at((18, "Retention factor")),
        at((0, "Constituents"), (18, "infusion with water")),
        at((0, "Caffeine"), (20, "0.95")),
        at((0, "Vitamin C"), (20, "-")),
        "Table 37: Retention factors by cooking of synthetic cereals",
        at((25, "Retention factor")),
        at((22, "whole"), (37, "polished")),
        at((0, "Constituents"), (22, "boil"), (37, "boil")),
        at((22, "A"), (37, "B")),
        at((0, "Thiamin"), (21, "0.70"), (36, "0.60")),
        "Table 38: Retention factors by cooking of synthetic pastry",
        "nothing that looks like a header or a data row",
        "Part 3 : Something else",
    ]
    return "\n".join(lines) + "\n"


def cells(res: B.BognarResult, table: int) -> list[dict]:
    return [c for c in res.cells if c["table"] == table]


def test_bognar_status_and_table_selection() -> None:
    assert B.STATUS == "PROVISIONAL_PENDING_G12_AUDIT"
    assert B.REMAINING_TABLES == (2, 13, 16, 29, 31, 32, 35, 36, 37, 38, 39)
    res = B.parse_remaining(bognar_text())
    assert {c["table"] for c in res.cells} == {2, 13, 29, 37}       # table 1 is a v1-parsed table; Part 1 ignored
    assert res.tables_found == (2, 13, 29, 37, 38)
    assert res.tables_missing == (16, 31, 32, 35, 36, 39)
    assert res.tables[38]["cells"] == 0 and res.tables[38]["problem"]


def test_bognar_equal_groups_mapping_with_sub_variants() -> None:
    t2 = cells(B.parse_remaining(bognar_text()), 2)
    vc = [c for c in t2 if c["constituent_raw"] == "Vitamin C"]
    assert [c["method_raw"] for c in vc] == ["boil", "boil", "steam", "steam"]
    assert [c["sub_variant_raw"] for c in vc] == ["a)", "b)", "a)", "b)"]
    assert {c["method_mapping"] for c in vc} == {"EQUAL_GROUPS_AND_POSITION_AGREE"}
    assert [c["basis"] for c in vc] == ["A"] * 4 and vc[0]["portion"] == "FOOD_EDIBLE_PART"
    assert [c["value_raw"] for c in vc] == ["0.60", "0.65", "0.75", "0.78"]
    assert vc[0]["source_line"] == 16 and vc[0]["column_index"] == 0


def test_bognar_value_statuses_and_estimated() -> None:
    t2 = cells(B.parse_remaining(bognar_text()), 2)
    th = [c for c in t2 if c["constituent_raw"] == "Thiamin"]
    assert [c["value_status"] for c in th] == ["MEASURED", "NOT_AVAILABLE", "MEASURED", "CENSORED_GT_CAP_CANDIDATE"]
    assert th[3]["value_origin"] == "SOURCE_IMPUTATION_POSSIBLE"
    assert all("value" not in c for c in th if c["value_status"] == "NOT_AVAILABLE")
    fol = [c for c in t2 if c["constituent_raw"] == "Folate"]
    assert fol and all(c["estimated"] for c in fol) and not th[0]["estimated"]


def test_bognar_skips_are_counted_not_guessed() -> None:
    res = B.parse_remaining(bognar_text())
    t2 = cells(res, 2)
    assert not [c for c in t2 if c["constituent_raw"] in ("Fat uptake", "Riboflavin")]
    assert res.tables[2]["skipped_non_retention_rows"] == 1
    assert res.tables[2]["skipped_ragged_rows"] == 1
    assert any("Riboflavin" not in p and "line 19" in p for p in res.problems)


def test_bognar_positional_only_mapping() -> None:
    t13 = cells(B.parse_remaining(bognar_text()), 13)
    assert [c["method_raw"] for c in t13] == ["boil", "boil", "steam"]
    assert {c["method_mapping"] for c in t13} == {"POSITIONAL_ONLY_UNCONFIRMED"}
    assert [c["sub_variant_raw"] for c in t13] == ["a)", "b)", "*"]


def test_bognar_no_basis_line_and_product_sub_columns() -> None:
    res = B.parse_remaining(bognar_text())
    t29 = cells(res, 29)
    assert [c["constituent_raw"] for c in t29] == ["Caffeine", "Vitamin C"]
    assert {c["basis"] for c in t29} == {"UNKNOWN"} and {c["portion"] for c in t29} == {"UNKNOWN"}
    assert t29[0]["method_raw"] == "infusion with"
    t37 = cells(res, 37)
    assert [c["sub_column_raw"] for c in t37] == ["whole", "polished"]
    assert [c["basis"] for c in t37] == ["A", "B"]
    assert t37[1]["portion"] == "TOTAL_DISH_INCL_COOKING_LIQUID"


def test_bognar_common_fields_and_notes() -> None:
    res = B.parse_remaining(bognar_text())
    c = res.cells[0]
    assert c["source_family_id"] == "BOGNAR-2002" and c["plane"] == "12-E" and c["regime"] == "D-A"
    assert c["aggregation_level"] == "COMPILED_MEAN" and c["time_series"] == "NONE"
    assert c["licence_gate"] == "BOGNAR_LICENCE_RECHECK_PENDING"
    assert c["staging_key"].startswith("bognar:part2:T2:")
    assert res.tables[2]["notes_raw"] == ("a) synthetic variant one; b) synthetic variant two",)
    keys = [x["staging_key"] for x in res.cells]
    assert len(keys) == len(set(keys))


def test_bognar_requires_part2_and_is_deterministic() -> None:
    with pytest.raises(B.BognarParseError):
        B.parse_remaining("Table 2: Retention factors\n")
    assert B.parse_remaining(bognar_text()) == B.parse_remaining(bognar_text())
    only = B.parse_remaining(bognar_text(), tables=(29,))
    assert {c["table"] for c in only.cells} == {29}
