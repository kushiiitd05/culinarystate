"""Phenol-Explorer parser/builder tests on synthetic HTML (same structure as the live site, fake values)."""
from culinarystate.ingest.phenol_explorer import FoodRow, parse_details, parse_food_processing, parse_list_page
from culinarystate.ingest.phenol_explorer_build import basis_of, build, process_steps
from culinarystate.ledgers.store import LedgerStore
from culinarystate.ledgers.validate import errors

LIST_HTML = """<table><tr><th>Name</th></tr><tr><th colspan="7">Flavonoids - Flavonols</th></tr>
<tr><td>Quercetin</td><td>boiled</td><td>2</td><td>5</td><td><a href="/food-processing/7/compounds">RF</a></td></tr>
</table><a href="/retention-factors/polyphenols?page=3">3</a>"""

FP_HTML = """<table><tr class="header"><th colspan="8" class="outer"> Flavonoids - <strong>
<a href="/compounds/99">Quercetin</a></strong></th></tr><tr class="header"><th class="inner" colspan="8">Vegetables</th></tr>
<tr class="odd"><td> Onions </td><td>Onion [Red], raw</td><td><a href="/retention-factors/details/5">0.50</a></td>
<td>0.4</td><td>0.6</td><td>0.1</td><td>2</td><td><a href="/retention-factors/details/5">1</a></td></tr></table>"""

DET_HTML = """<main><h1> Showing retention factors for <em>Quercetin</em> in <em>Onion [Red], raw</em> with the process
<em>boiled <i class="tips icon-info-sign" title="boiled|cooked in boiling water"> </i></em></h1>
<p> Yield factor value: <strong>0.90</strong> (<strong>Onion, boiled</strong>, <a href="/publications/1">USDA_SR</a>) </p>
<h2>Calculated Mean Retention Factor Value</h2><table><tbody><tr><td>0.50</td><td>0.4</td></tr></tbody></table>
<div class="well publication-values"><blockquote class="publication">Doe J. (2001) Fake study. <em>J Fake</em></blockquote>
<table><tbody><tr><td>0.45</td><td>Red onion</td><td>Red onion, boiled for 15 min</td><td>10.0</td><td>5.0</td>
<td>mg/100 g fresh weight</td></tr><tr><td>0.55</td><td>Red onion</td><td>Red onion, boiled 100 °C 30 min</td>
<td>8.0</td><td>4.9</td><td>mg/100 g fresh weight</td></tr></tbody></table></div></main>"""


def test_parse_list_page():
    rows, last = parse_list_page(LIST_HTML)
    assert last == 3 and len(rows) == 1
    assert rows[0].compound_class == "Flavonoids - Flavonols" and rows[0].fp_path == "/food-processing/7/compounds"


def test_parse_food_processing():
    (row,) = parse_food_processing(FP_HTML)
    assert row.compound == "Quercetin" and row.food_subgroup == "Onions" and row.mean_rf == 0.5 and row.n == 2


def test_parse_details():
    d = parse_details(DET_HTML)
    assert (d.compound, d.food, d.process) == ("Quercetin", "Onion [Red], raw", "boiled")
    assert d.process_definition == "cooked in boiling water"
    assert d.yield_factor == 0.9 and d.yield_food == "Onion, boiled" and d.yield_source == "USDA_SR"
    assert len(d.values) == 2 and d.values[0].content_before == 10.0 and d.values[1].rf == 0.55


def test_helpers():
    assert process_steps("dehulled, soaked, pressure-boiled") == ["dehull", "soak", "pressure-boil"]
    assert basis_of("mg/100 g dry weight") == "DRY" and basis_of("mg/100 ml") == "UNKNOWN"


def test_build(tmp_path):
    st = LedgerStore(tmp_path)
    food = parse_food_processing(FP_HTML)[0]
    c = build(st, [(food, parse_details(DET_HTML))])
    assert c[("EVD", "created")] == 2 and c[("STUDY", "created")] == 1 and c[("SRC", "created")] == 2
    evd = sorted(st.all_latest("EVD"), key=lambda e: e["id"])
    assert all(errors(e) == [] for e in evd)
    e1 = evd[0]
    assert e1["origin_type"] == "PRIMARY_STUDY" and e1["study_id_status"] == "PRESENT" and e1["tier"] == "E3"
    assert e1["derived"]["percent_change"]["value"] == -50.0           # from contents, not from RF
    assert e1["derived"]["retention_factor"]["value"] == 0.45          # PE RF includes yield
    assert e1["derived"]["yield_factor"]["value"] == 0.9
    assert e1["target"]["basis"] == "FRESH_WEIGHT"
    cond2 = st.latest(evd[1]["process"]["condition_id"])
    assert cond2["duration"]["value"] == 30.0 and cond2["temperatures"][0]["location"] == "UNSPECIFIED"
    assert e1["independence_group"] == evd[1]["independence_group"]   # same publication
    assert set(a for _, a in build(LedgerStore(tmp_path), [(food, parse_details(DET_HTML))])) == {"unchanged"}
