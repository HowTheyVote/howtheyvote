from howtheyvote.analysis.votes import MainVoteAnalyzer
from howtheyvote.models.common import Fragment

from ..helpers import record_to_dict


def test_main_vote_analyzer_description():
    analyzer = MainVoteAnalyzer(
        vote_id=1,
        description="Am 123",
        title="Lorem Ipsum",
    )
    assert analyzer.run() is None

    analyzer = MainVoteAnalyzer(
        vote_id=2,
        description="Proposition de résolution",
        title="Lorem ipsum",
    )
    expected = Fragment(
        model="Vote",
        source_id=2,
        source_name="MainVoteAnalyzer",
        group_key=2,
        data={"is_main": True},
    )
    assert record_to_dict(analyzer.run()) == record_to_dict(expected)

    analyzer = MainVoteAnalyzer(
        vote_id=3,
        description="Accord provisoire - Am 123",
        title="Lorem ipsum",
    )
    expected = Fragment(
        model="Vote",
        source_id=3,
        source_name="MainVoteAnalyzer",
        group_key=3,
        data={"is_main": True},
    )
    assert record_to_dict(analyzer.run()) == record_to_dict(expected)


def test_main_vote_analyzer_title():
    analyzer = MainVoteAnalyzer(
        vote_id=1,
        description=None,
        title="Ordre du jour de mardi",
    )
    assert analyzer.run() is None

    expected = Fragment(
        model="Vote",
        source_id=2,
        source_name="MainVoteAnalyzer",
        group_key=2,
        data={"is_main": True},
    )
    analyzer = MainVoteAnalyzer(
        vote_id=2,
        description=None,
        title="Élection de la Commission",
    )
    assert record_to_dict(analyzer.run()) == record_to_dict(expected)
