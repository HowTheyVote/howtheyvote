import pytest

from howtheyvote.analysis.helpers import extract_vote_results, parse_int


def test_parse_int():
    assert parse_int("1") == 1
    assert parse_int("one") == 1
    assert parse_int("One") == 1
    assert parse_int("12") == 12
    assert parse_int("twelve") == 12

    with pytest.raises(ValueError):
        assert parse_int("")

    with pytest.raises(ValueError):
        assert parse_int("invalid")


def test_extract_vote_results():
    for example in [
        "400 votes in favour, 63 against with 81 abstentions",
        "400 votes in favor, 63 against with 81 abstentions",
        "400 votes in favour, 63 against, with 81 abstentions",
        "400 votes in favour, 63 against and 81 abstentions",
        "400 votes in favour, 63 against, and 81 abstentions",
        "400 MEPs voted in favour, 63 against and 81 abstained",
        "400 MEPs voted in favour, 63 against, and 81 abstained",
        "400 MEPs voted in favor, 63 against, and 81 abstained",
    ]:
        expected = [{"FOR": 400, "AGAINST": 63, "ABSTENTION": 81, "DID_NOT_VOTE": 0}]
        actual = extract_vote_results(example)
        assert actual == expected

    expected = [{"FOR": 500, "AGAINST": 143, "ABSTENTION": 9, "DID_NOT_VOTE": 0}]
    actual = extract_vote_results("500 votes in favour, 143 against, and nine abstentions")
    assert actual == expected

    expected = [{"FOR": 1, "AGAINST": 1, "ABSTENTION": 1, "DID_NOT_VOTE": 0}]
    actual = extract_vote_results("one vote in favour, one against, and one abstention")
    assert actual == expected

    expected = [{"FOR": 455, "AGAINST": 85, "ABSTENTION": 105, "DID_NOT_VOTE": 0}]
    actual = extract_vote_results("adopted with 455 votes to 85 and 105 abstentions")
    assert actual == expected

    expected = [{"FOR": 531, "AGAINST": 69, "ABSTENTION": 17, "DID_NOT_VOTE": 0}]
    actual = extract_vote_results(
        "With 531 votes for, 69 against and 17 abstentions, MEPs supported the Commission proposal"
    )
    assert actual == expected

    expected = [{"FOR": 477, "AGAINST": 7, "ABSTENTION": 69, "DID_NOT_VOTE": 0}]
    actual = extract_vote_results(
        "adopted by 477 votes to 7, with 69 abstentions, a resolution"
    )
    assert actual == expected

    expected = [{"FOR": 513, "AGAINST": 18, "ABSTENTION": 87, "DID_NOT_VOTE": 0}]
    actual = extract_vote_results("adopted by 513 to 18, with 87 abstentions, a resolution")
    assert actual == expected

    expected = [{"FOR": 593, "AGAINST": 34, "ABSTENTION": 38, "DID_NOT_VOTE": 0}]
    actual = extract_vote_results(
        "adopted by 593 votes to 34 against, 38 abstentions, a resolution"
    )
    assert actual == expected

    expected = [{"FOR": 688, "AGAINST": 8, "ABSTENTION": 1, "DID_NOT_VOTE": 0}]
    actual = extract_vote_results("adopted by 688 votes to 8, with 1 abstention, a resolution")
    assert actual == expected

    expected = [{"FOR": 340, "AGAINST": 100, "ABSTENTION": 245, "DID_NOT_VOTE": 0}]
    actual = extract_vote_results("adopted by 340 votes to 100, 245 abstentions, a resolution")
    assert actual == expected
