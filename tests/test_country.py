from ep_votes.country import Country


def test_from_str():
    assert Country.from_str("Austria") == Country.AT
