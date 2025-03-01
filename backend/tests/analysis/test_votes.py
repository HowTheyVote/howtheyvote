from howtheyvote.analysis.votes import MainVoteAnalyzer, PressReleaseAnalyzer
from howtheyvote.models import Fragment, PressRelease, Vote

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


def test_press_release_analyzer_by_reference():
    press_releases = [
        PressRelease(id="20240223IPR18077", references=["A9-0051/2024"]),
        PressRelease(id="20240223IPR18074", references=[]),
    ]

    votes = [
        Vote(id="1", reference=None, is_main=True),
        Vote(id="2", reference="A9-0051/2024", is_main=True),
        Vote(id="3", reference="A9-0051/2024", is_main=False),
    ]

    analyzer = PressReleaseAnalyzer(votes, press_releases)
    fragments = list(analyzer.run())

    expected = Fragment(
        model="Vote",
        source_id="2:20240223IPR18077",
        source_name="PressReleaseAnalyzer",
        group_key="2",
        data={"press_release": "20240223IPR18077"},
    )

    assert len(fragments) == 1
    assert record_to_dict(fragments[0]) == record_to_dict(expected)


def test_press_release_analyzer_by_procedure_reference():
    press_releases = [
        PressRelease(id="20241111IPR25339", procedure_references=["2024/2718(RSP)"]),
        PressRelease(id="20241111IPR25341", procedure_references=[]),
    ]

    votes = [
        Vote(id="1", procedure_reference=None, is_main=True),
        Vote(id="2", procedure_reference="2024/2718(RSP)", is_main=True),
        Vote(id="3", procedure_reference="2024/2718(RSP)", is_main=False),
    ]

    analyzer = PressReleaseAnalyzer(votes, press_releases)
    fragments = list(analyzer.run())

    expected = Fragment(
        model="Vote",
        source_id="2:20241111IPR25339",
        source_name="PressReleaseAnalyzer",
        group_key="2",
        data={"press_release": "20241111IPR25339"},
    )

    assert len(fragments) == 1
    assert record_to_dict(fragments[0]) == record_to_dict(expected)
