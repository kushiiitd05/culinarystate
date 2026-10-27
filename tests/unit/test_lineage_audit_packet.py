import csv
import hashlib

import pytest

from culinarystate.lineage import audit_packet as P


def _edges(nb2=80, nb3=60, nstrong=12, nb1=20):
    out = []
    for lvl, n in (("B1", nb1), ("B2", nb2), ("B3", nb3), ("STRONG", nstrong)):
        for i in range(n):
            out.append({"edge_id": f"LIN-{lvl}-{i:03d}", "from_id": f"R{len(out)}a", "to_id": f"R{len(out)}b", "edge_type": "SAME_STUDY_AS",
                        "detector_level": lvl, "detection_method": f"det_{lvl}", "score": 0.5 + i / 1000,
                        "from_summary": f"summary a {i}", "to_summary": f"summary b {i}"})
    return out


def _rd(p):
    with open(p, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def test_constants_and_ambiguity_codes():
    assert P.EDGE_JUDGEMENT_CODES == ("CORRECT_EDGE", "WRONG_EDGE", "UNCERTAIN")
    assert P.STRATA == ("B2", "B3", "STRONG")


def test_stratified_sampling_sizes_and_full_audit(tmp_path):
    res = P.build_edge_audit_packets(_edges(), seed=11, out_dir=tmp_path, prefix="ea")
    _, a = _rd(res["reviewer_files"]["Kush"])
    assert len(a) == 50 + 50 + 12  # B1 not audited; STRONG 100% audit
    key_h, key = _rd(res["key_file"])
    from collections import Counter
    assert Counter(r["stratum"] for r in key) == {"B2": 50, "B3": 50, "STRONG": 12}
    assert res["strata_counts"] == {"B2": {"available": 80, "audited": 50}, "B3": {"available": 60, "audited": 50}, "STRONG": {"available": 12, "audited": 12}}


def test_blinding_same_rows_different_order(tmp_path):
    res = P.build_edge_audit_packets(_edges(), seed=11, out_dir=tmp_path, prefix="ea")
    hk, k = _rd(res["reviewer_files"]["Kush"])
    hp, p = _rd(res["reviewer_files"]["Parv"])
    assert hk == hp
    assert [r["audit_id"] for r in k] != [r["audit_id"] for r in p]
    assert sorted(map(str, (sorted(r.items()) for r in k))) == sorted(map(str, (sorted(r.items()) for r in p)))
    text = (tmp_path / "ea_Kush.csv").read_text()
    for banned in ("det_B2", "det_B3", "det_STRONG", "STRONG", "detector", "score", "stratum"):
        assert banned not in text
    assert all(r["edge_judgement"] == "" and r["reason_if_not_correct"] == "" for r in k + p)
    key_text = open(res["key_file"]).read()
    assert "det_B2" in key_text and "detector_level" in key_text
    assert (tmp_path / "ea_INSTRUCTIONS.md").read_text().count("CORRECT_EDGE") >= 1


def test_audit_ids_not_ordered_by_stratum(tmp_path):
    res = P.build_edge_audit_packets(_edges(), seed=11, out_dir=tmp_path, prefix="ea")
    _, key = _rd(res["key_file"])
    levels = [r["stratum"] for r in sorted(key, key=lambda r: r["audit_id"])]
    assert levels != sorted(levels)


def test_determinism_byte_identical_and_seed_sensitive(tmp_path):
    d1, d2, d3 = tmp_path / "1", tmp_path / "2", tmp_path / "3"
    for d, s in ((d1, 5), (d2, 5), (d3, 6)):
        d.mkdir()
        P.build_edge_audit_packets(_edges(), seed=s, out_dir=d, prefix="ea")
    h = lambda d: {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(d.iterdir())}
    assert h(d1) == h(d2)
    assert h(d1) != h(d3)


def test_input_order_irrelevant(tmp_path):
    e = _edges()
    d1, d2 = tmp_path / "1", tmp_path / "2"
    d1.mkdir(); d2.mkdir()
    P.build_edge_audit_packets(e, seed=3, out_dir=d1, prefix="ea")
    P.build_edge_audit_packets(list(reversed(e)), seed=3, out_dir=d2, prefix="ea")
    assert (d1 / "ea_Kush.csv").read_bytes() == (d2 / "ea_Kush.csv").read_bytes()


def test_unlinked_pair_draw():
    blocked = [(f"X{i}", f"Y{i}") for i in range(500)]
    edges = {frozenset(("X0", "Y0")), frozenset(("Y1", "X1"))}
    a = P.draw_unlinked_pairs(blocked, edges, seed=2)
    assert a == P.draw_unlinked_pairs(blocked, edges, seed=2)
    assert len(a) == 200 and len(set(map(frozenset, a))) == 200
    assert not any(frozenset(p) in edges for p in a)
    short = P.draw_unlinked_pairs(blocked[:50], set(), seed=2)
    assert len(short) == 50
    with pytest.raises(ValueError):
        P.draw_unlinked_pairs(blocked, edges, seed=2, n=199)


def test_miss_rate_report():
    r = P.miss_rate_report(duplicates_found=0, n_reviewed=200)
    assert r["wilson_upper_miss_rate"] == pytest.approx(0.0188, abs=1e-3)
    assert r["gate"] == "REPORT_ONLY"


def test_missed_pair_packets_use_own_codes(tmp_path):
    pairs = [{"pair_id": f"P{i}", "from_id": f"a{i}", "to_id": f"b{i}", "from_summary": "s", "to_summary": "t"} for i in range(200)]
    res = P.build_missed_pair_packets(pairs, seed=1, out_dir=tmp_path, prefix="mp")
    h, rows = _rd(res["reviewer_files"]["Kush"])
    assert len(rows) == 200 and "pair_judgement" in h
    assert P.MISSED_PAIR_JUDGEMENT_CODES == ("TRUE_DUPLICATE", "NOT_DUPLICATE", "UNCERTAIN")


def _complete(src, dst, labels):
    h, rows = _rd(src)
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=h, lineterminator="\n")
        w.writeheader()
        for i, r in enumerate(rows):
            r["edge_judgement"] = labels[i % len(labels)]
            w.writerow(r)


def test_validator_valid_and_invalid(tmp_path):
    res = P.build_edge_audit_packets(_edges(), seed=1, out_dir=tmp_path, prefix="ea")
    k, p = res["reviewer_files"]["Kush"], res["reviewer_files"]["Parv"]
    ka, pa = tmp_path / "k_done.csv", tmp_path / "p_done.csv"
    _complete(k, ka, ["CORRECT_EDGE", "WRONG_EDGE"])
    _complete(p, pa, ["CORRECT_EDGE", "UNCERTAIN", "CORRECT_EDGE"])
    ok = P.validate_returned_edge_packets(k, ka, pa)
    assert ok["status"] == "VALID", ok["problems"]
    # identical files
    same = P.validate_returned_edge_packets(k, ka, ka)
    assert same["status"] == "INVALID_PROVENANCE" and any("identical" in x for x in same["problems"])
    # bad code
    bad = tmp_path / "bad.csv"
    _complete(p, bad, ["MAYBE"])
    r = P.validate_returned_edge_packets(k, ka, bad)
    assert r["status"] == "INVALID_PROVENANCE" and any("not in the allowed" in x for x in r["problems"])
    # tampered fixed cell
    t = tmp_path / "t.csv"
    txt = pa.read_text().replace("summary a ", "summary TAMPERED ", 1)
    t.write_text(txt)
    r = P.validate_returned_edge_packets(k, ka, t)
    assert any("non-judgement" in x for x in r["problems"])
    # header change
    h = tmp_path / "h.csv"
    h.write_text(pa.read_text().replace("edge_type", "edge_typ", 1))
    assert any("header" in x for x in P.validate_returned_edge_packets(k, ka, h)["problems"])
    # blank judgement
    blank = P.validate_returned_edge_packets(k, ka, k)
    assert any("empty" in x for x in blank["problems"])
