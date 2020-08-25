import pytest
from ep_votes.document import parse_ref, Type, Reference, url


def test_parse_ref():
    ref = Reference(type=Type.B, term=9, number=154, year=2019)
    assert parse_ref("B9-0154/2019") == ref


def test_parse_ref_malformed():
    with pytest.raises(ValueError):
        parse_ref("XYZ")


def test_url():
    ref = Reference(type=Type.B, term=9, number=154, year=2019)
    expected = "https://www.europarl.europa.eu/doceo/document/B-9-2019-0154_EN.html"
    assert url(ref) == expected
