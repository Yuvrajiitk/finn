from finn.classify import classify
from finn.prices import eod_stats, is_unusual
from finn.results import headline, growth

def test_classifier():
    assert classify("Outcome of Board Meeting", "approved unaudited financial results for the quarter ended")[0] == "results"
    assert classify("Cessation of Chief Financial Officer")[0] == "management_change"
    assert classify("Allotment of shares under ESOP")[0] == "routine"
    assert classify("Newspaper publication of results")[1] == 1   # results-ad is low priority
    assert classify("Acquisition of stake in subsidiary")[0] == "M&A"
    assert classify("Disclosure of pledge by promoter")[0] == "pledging"
    assert classify("something odd")[0] == "unclassified"

def test_spike():
    s = eod_stats([100] * 21 + [106], [10] * 21 + [30])
    assert s["chg_pct"] == 6.0 and s["vol_x"] == 3.0
    assert len(is_unusual(s, 4, 2)) == 2 and is_unusual(s, 10, 5) == []

def test_headline_math_and_derived_ebitda():
    d = {"unit": "crore", "revenue": [110, 100, 88], "pbt": [20, 18, 15], "pat": [15, 14, 11],
         "finance_cost": [2, 2, 2], "depreciation": [5, 5, 4], "other_income": [3, 3, 2], "ebitda": None}
    h = headline(d)
    assert h["revenue"] == {"value": 110, "qoq": 10.0, "yoy": 25.0}
    assert h["ebitda"]["value"] == 24 and h["ebitda"]["derived"] is True
    assert growth(5, 0) is None
