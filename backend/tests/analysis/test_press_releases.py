from howtheyvote.analysis.press_releases import VotePositionCountsAnalyzer
from howtheyvote.models import Fragment

from ..helpers import record_to_dict


def test_vote_position_counts_analyzer():
    analyzer = VotePositionCountsAnalyzer(
        release_id="20250204IPR26689",
        text="The text was adopted by 400 votes in favour, 63 against with 81 abstentions.",
    )
    expected = Fragment(
        model="PressRelease",
        source_id="20250204IPR26689",
        source_name="VotePositionCountsAnalyzer",
        group_key="20250204IPR26689",
        data={
            "position_counts": [
                {
                    "FOR": 400,
                    "AGAINST": 63,
                    "ABSTENTION": 81,
                    "DID_NOT_VOTE": 0,
                },
            ],
        },
    )
    assert record_to_dict(analyzer.run()) == record_to_dict(expected)


def test_vote_position_counts_analyzer_multiple_counts():
    analyzer = VotePositionCountsAnalyzer(
        release_id="20190711IPR56828",
        text="The text was adopted with 458 votes in favour, 80 against and 89 abstentions. The text was adopted with 330 votes in favour, 252 against and 55 abstentions",
    )
    expected = Fragment(
        model="PressRelease",
        source_id="20190711IPR56828",
        source_name="VotePositionCountsAnalyzer",
        group_key="20190711IPR56828",
        data={
            "position_counts": [
                {
                    "FOR": 458,
                    "AGAINST": 80,
                    "ABSTENTION": 89,
                    "DID_NOT_VOTE": 0,
                },
                {
                    "FOR": 330,
                    "AGAINST": 252,
                    "ABSTENTION": 55,
                    "DID_NOT_VOTE": 0,
                },
            ],
        },
    )
    assert record_to_dict(analyzer.run()) == record_to_dict(expected)


def test_vote_position_counts_analyzer_no_text():
    analyzer = VotePositionCountsAnalyzer(
        release_id="20250219IPR26999",
        text=None,
    )
    assert analyzer.run() is None


def test_vote_position_counts_analyzer_no_counts():
    analyzer = VotePositionCountsAnalyzer(
        release_id="20250219IPR26999",
        text="EU and Ukrainian flags will be flown at the European Parliament’s three sites from Sunday 23 February to Tuesday 25 February, marking three years since Russia’s invasion.",
    )
    assert analyzer.run() is None
