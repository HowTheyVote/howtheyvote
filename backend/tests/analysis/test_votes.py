import datetime

from howtheyvote.analysis.votes import MainVoteAnalyzer, PressReleaseAnalyzer
from howtheyvote.models import Fragment, MemberVote, PressRelease, Vote, VotePosition

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
        PressRelease(
            id="20240223IPR18077",
            published_at=datetime.datetime(2024, 2, 27, 12, 51, 0),
            references=["A9-0051/2024"],
        ),
        PressRelease(
            id="20240223IPR18074",
            published_at=datetime.datetime(2024, 2, 27, 12, 27, 0),
            references=[],
        ),
    ]

    votes = [
        Vote(
            id="1",
            timestamp=datetime.datetime(2024, 2, 27, 0, 0, 0),
            reference=None,
            is_main=True,
            member_votes=[],
        ),
        Vote(
            id="2",
            timestamp=datetime.datetime(2024, 2, 27, 0, 0, 0),
            reference="A9-0051/2024",
            is_main=True,
            member_votes=[],
        ),
        Vote(
            id="3",
            timestamp=datetime.datetime(2024, 2, 27, 0, 0, 0),
            reference="A9-0051/2024",
            is_main=False,
            member_votes=[],
        ),
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
        PressRelease(
            id="20241111IPR25339",
            published_at=datetime.datetime(2024, 11, 14, 11, 55, 0),
            procedure_references=["2024/2718(RSP)"],
        ),
        PressRelease(
            id="20241111IPR25341",
            published_at=datetime.datetime(2024, 11, 14, 12, 2, 0),
            procedure_references=[],
        ),
    ]

    votes = [
        Vote(
            id="1",
            timestamp=datetime.datetime(2024, 11, 14, 0, 0, 0),
            procedure_reference=None,
            is_main=True,
            member_votes=[],
        ),
        Vote(
            id="2",
            timestamp=datetime.datetime(2024, 11, 14, 0, 0, 0),
            procedure_reference="2024/2718(RSP)",
            is_main=True,
            member_votes=[],
        ),
        Vote(
            id="3",
            timestamp=datetime.datetime(2024, 11, 14, 0, 0, 0),
            procedure_reference="2024/2718(RSP)",
            is_main=False,
            member_votes=[],
        ),
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


def _make_member_votes(for_: int, against: int, abstention: int) -> list[MemberVote]:
    member_votes = []
    member_id = 0

    for _ in range(for_):
        member_id += 1
        member_votes.append(
            MemberVote(web_id=member_id, position=VotePosition.FOR),
        )

    for _ in range(against):
        member_id += 1
        member_votes.append(
            MemberVote(web_id=member_id, position=VotePosition.AGAINST),
        )

    for _ in range(abstention):
        member_id += 1
        member_votes.append(
            MemberVote(web_id=member_id, position=VotePosition.ABSTENTION),
        )

    return member_votes


def test_press_release_analyzer_by_position_counts():
    press_releases = [
        PressRelease(
            id="20250204IPR26689",
            published_at=datetime.datetime(2025, 2, 13, 12, 47, 0),
            position_counts=[
                {"FOR": 400, "AGAINST": 63, "ABSTENTION": 81, "DID_NOT_VOTE": 0},
            ],
        ),
        PressRelease(id="20250213IPR26920", position_counts=[]),
        PressRelease(
            id="20250206IPR26752",
            published_at=datetime.datetime(2025, 2, 13, 12, 59, 0),
            position_counts=[
                {"FOR": 443, "AGAINST": 4, "ABSTENTION": 48, "DID_NOT_VOTE": 0},
            ],
        ),
    ]

    votes = [
        Vote(
            id="1",
            timestamp=datetime.datetime(2025, 2, 13, 0, 0, 0),
            is_main=True,
            member_votes=_make_member_votes(398, 65, 81),
        ),
        Vote(
            id="2",
            timestamp=datetime.datetime(2025, 2, 13, 0, 0, 0),
            is_main=True,
            member_votes=_make_member_votes(400, 63, 81),
        ),
    ]

    analyzer = PressReleaseAnalyzer(votes, press_releases)
    fragments = list(analyzer.run())

    expected = Fragment(
        model="Vote",
        source_id="2:20250204IPR26689",
        source_name="PressReleaseAnalyzer",
        group_key="2",
        data={"press_release": "20250204IPR26689"},
    )

    assert len(fragments) == 1
    assert record_to_dict(fragments[0]) == record_to_dict(expected)


def test_press_release_analyzer_by_position_counts_multiple_counts():
    # If a press release contains multiple vote results, don't try to match it
    # to votes as it might be about multiple unrelated votes.
    press_releases = [
        PressRelease(
            id="20250116IPR26326",
            position_counts=[
                {"FOR": 556, "AGAINST": 6, "ABSTENTION": 42, "DID_NOT_VOTE": 0},
                {"FOR": 533, "AGAINST": 24, "ABSTENTION": 48, "DID_NOT_VOTE": 0},
            ],
        )
    ]

    votes = [
        Vote(
            id="1",
            timestamp=datetime.datetime(2025, 1, 23, 0, 0, 0),
            is_main=True,
            member_votes=_make_member_votes(556, 6, 42),
        ),
        Vote(
            id="2",
            timestamp=datetime.datetime(2025, 1, 23, 0, 0, 0),
            is_main=True,
            member_votes=_make_member_votes(533, 24, 48),
        ),
    ]

    analyzer = PressReleaseAnalyzer(votes, press_releases)
    fragments = list(analyzer.run())

    assert fragments == []


def test_press_release_analyzer_by_position_counts_multiple_votes():
    # If there are multiple votes with the same number of votes for/against/abstention,
    # don’t try to match it as it is ambiguous.
    press_releases = [
        PressRelease(
            id="abc",
            published_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
            position_counts=[
                {"FOR": 200, "AGAINST": 200, "ABSTENTION": 200, "DID_NOT_VOTE": 0},
            ],
        )
    ]

    votes = [
        Vote(
            id="1",
            timestamp=datetime.datetime(2025, 1, 1, 0, 0, 0),
            is_main=True,
            member_votes=_make_member_votes(200, 200, 200),
        ),
        Vote(
            id="2",
            timestamp=datetime.datetime(2025, 1, 1, 0, 0, 0),
            is_main=True,
            member_votes=_make_member_votes(200, 200, 200),
        ),
    ]

    analyzer = PressReleaseAnalyzer(votes, press_releases)
    fragments = list(analyzer.run())

    assert fragments == []


def test_press_release_analyzer_by_position_counts_different_dates():
    # Do not match press releases and votes with same position counts but different dates
    press_releases = [
        PressRelease(
            id="abc",
            published_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
            position_counts=[
                {"FOR": 200, "AGAINST": 200, "ABSTENTION": 200, "DID_NOT_VOTE": 0},
            ],
        )
    ]

    votes = [
        Vote(
            id="1",
            is_main=True,
            timestamp=datetime.datetime(2025, 1, 2, 0, 0, 0),
            member_votes=_make_member_votes(200, 200, 200),
        ),
    ]

    analyzer = PressReleaseAnalyzer(votes, press_releases)
    fragments = list(analyzer.run())

    assert fragments == []


def test_press_release_analyzer_by_reference_prefer():
    # Do not try to match by position counts if matching by document/procedure reference
    # has already returned a result
    press_releases = [
        PressRelease(
            id="20201217IPR94207",
            published_at=datetime.datetime(2020, 12, 18, 0, 0, 0),
            procedure_references=["2020/0362(COD)", "2020/0364(COD)"],
            position_counts=[
                {"FOR": 677, "AGAINST": 4, "ABSTENTION": 6, "DID_NOT_VOTE": 17},
            ],
        ),
        PressRelease(
            id="20201217IPR94211",
            published_at=datetime.datetime(2025, 12, 18, 0, 0, 0),
            procedure_references=["2020/0366(COD)"],
            position_counts=[
                {"FOR": 677, "AGAINST": 4, "ABSTENTION": 6, "DID_NOT_VOTE": 17},
            ],
        ),
    ]

    votes = [
        Vote(
            id="126356",
            is_main=True,
            timestamp=datetime.datetime(2025, 1, 1, 0, 0, 0),
            procedure_reference="2020/0366(COD)",
            member_votes=_make_member_votes(677, 4, 6),
        ),
    ]

    analyzer = PressReleaseAnalyzer(votes, press_releases)
    fragments = list(analyzer.run())

    expected = Fragment(
        model="Vote",
        source_id="126356:20201217IPR94211",
        source_name="PressReleaseAnalyzer",
        group_key="126356",
        data={"press_release": "20201217IPR94211"},
    )

    assert len(fragments) == 1
    assert record_to_dict(fragments[0]) == record_to_dict(expected)
