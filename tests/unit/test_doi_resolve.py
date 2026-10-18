from culinarystate.evidence.doi_resolve import accept, citation_year, title_match

CIT = ("Lombard K., Peffley E., Geoffriau E., Thompson L., Herring A. (2005) Quercetin in onion (Allium cepa L.) "
       "after heat-treatment simulating home preparation. Journal of Food Composition and Analysis 18 :571-581")


def _item(title, year):
    return {"DOI": "10.1/x", "title": [title], "issued": {"date-parts": [[year, 9]]}}


def test_year_and_title():
    assert citation_year(CIT) == 2005
    assert title_match("Quercetin in onion (Allium cepa L.) after heat-treatment simulating home preparation", CIT) == 1.0


def test_accepts_true_match_only():
    assert accept(_item("Quercetin in onion (Allium cepa L.) after heat-treatment simulating home preparation", 2005), CIT)
    assert not accept(_item("Quantification of Quercetin in Onion (Allium Cepa) after Domestic Processing", 2000), CIT)
    assert not accept(_item("Quercetin in onion after heat-treatment simulating home preparation", 2012), CIT)  # year
    assert not accept(_item("Onion", 2005), CIT)                                                                 # too short
