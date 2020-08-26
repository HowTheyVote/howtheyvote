from ep_votes.country import Country


def test_from_str():
    assert Country.from_str("Austria") == Country.AT


def test_from_str_alternates():
    assert Country.from_str("Czech Republic") == Country.CZ
    assert Country.from_str("Czechia") == Country.CZ
