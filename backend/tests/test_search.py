import datetime

from howtheyvote.models import Country
from howtheyvote.search import boolean_term


def test_boolean_term():
    assert boolean_term("reference", "A10-1234/2025") == "XRa10-1234/2025"
    assert boolean_term("timestamp", datetime.date(2025, 1, 1)) == "XD2025-01-01"
    assert boolean_term("geo_areas", Country["DEU"]) == "XGAdeu"
