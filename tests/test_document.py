import pytest
from ep_votes.document import parse_ref, Type, Reference

def test_parse_ref():
    ref = Reference(type=Type.B, term=9, number=154, year=2019)
    assert parse_ref('B9-0154/2019') == ref

def test_parse_ref_malformed():
    with pytest.raises(ValueError):
        parse_ref('XYZ')
