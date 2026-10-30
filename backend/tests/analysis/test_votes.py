import datetime

from howtheyvote.analysis.votes import (
    MainVoteAnalyzer,
    OEILSummaryAnalyzer,
    PressReleaseAnalyzer,
    RequiredGroupsAnalyzer,
    VoteGroupsAnalyzer,
)
from howtheyvote.models import (
    Fragment,
    Group,
    GroupMembership,
    MajorityType,
    Member,
    MemberVote,
    OEILSummary,
    PressRelease,
    Vote,
    VotePosition,
    VoteResult,
)

from ..helpers import record_to_dict


def test_vote_group_analyzer_title():
    votes = [
        Vote(
            id=1,
            timestamp=datetime.date(2026, 1, 1),
            title="Lorem ipsum dolor sit amet",
            description="Am 1",
        ),
        Vote(
            id=2,
            timestamp=datetime.date(2026, 1, 1),
            title="Lorem ipsum dolor sit amet",
            description="Proposition de résolution",
        ),
        Vote(
            id=3,
            timestamp=datetime.date(2026, 1, 1),
            title="Aenean commodo ligula eget dolor",
            description="Proposition de résolution",
        ),
    ]

    analyzer = VoteGroupsAnalyzer(
        session_start_date=datetime.date(2026, 1, 1),
        votes=votes,
    )
    fragments = list(analyzer.run())

    assert len(fragments) == 3
    assert fragments[0].data["group_key"] == fragments[1].data["group_key"]
    assert fragments[0].data["group_key"] != fragments[2].data["group_key"]
    assert fragments[1].data["group_key"] != fragments[2].data["group_key"]


def test_vote_group_analyzer_dlv_title():
    votes = [
        Vote(
            id=1,
            timestamp=datetime.date(2026, 1, 1),
            dlv_title="Lorem ipsum dolor sit amet",
            description="Am 1",
        ),
        Vote(
            id=2,
            timestamp=datetime.date(2026, 1, 1),
            dlv_title="Lorem ipsum dolor sit amet",
            description="Proposition de résolution",
        ),
        Vote(
            id=3,
            timestamp=datetime.date(2026, 1, 1),
            dlv_title="Aenean commodo ligula eget dolor",
            description="Proposition de résolution",
        ),
    ]

    analyzer = VoteGroupsAnalyzer(
        session_start_date=datetime.date(2026, 1, 1),
        votes=votes,
    )
    fragments = list(analyzer.run())

    assert len(fragments) == 3
    assert fragments[0].data["group_key"] == fragments[1].data["group_key"]
    assert fragments[0].data["group_key"] != fragments[2].data["group_key"]
    assert fragments[1].data["group_key"] != fragments[2].data["group_key"]


def test_vote_group_analyzer_across_session_days():
    votes = [
        Vote(
            id=130991,
            timestamp=datetime.datetime(2021, 5, 18),
            title="2019-2020 Reports on Montenegro",
            reference="A9-0131/2021",
            description="Am 6",
        ),
        Vote(
            id=131714,
            timestamp=datetime.datetime(2021, 5, 19),
            title="2019-2020 Reports on Montenegro",
            reference="A9-0131/2021",
            description="Proposition de résolution",
        ),
    ]

    analyzer = VoteGroupsAnalyzer(
        session_start_date=datetime.date(2021, 5, 17),
        votes=votes,
    )
    fragments = list(analyzer.run())

    assert len(fragments) == 2
    assert fragments[0].group_key == 130991
    assert fragments[1].group_key == 131714
    assert fragments[0].data["group_key"] == fragments[1].data["group_key"]


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


def test_oeil_summary_analyzer():
    summaries = [
        OEILSummary(
            id="1739466",
            date=datetime.date(2023, 3, 30),
            procedure_reference="2022/0099(COD)",
            position_counts=[
                {"FOR": 426, "AGAINST": 109, "ABSTENTION": 52, "DID_NOT_VOTE": 0},
            ],
        ),
        OEILSummary(
            id="1772308",
            date=datetime.date(2024, 1, 16),
            procedure_reference="2022/0099(COD)",
            position_counts=[
                {"FOR": 457, "AGAINST": 92, "ABSTENTION": 32, "DID_NOT_VOTE": 0},
            ],
        ),
    ]

    votes = [
        Vote(
            id="162974",
            is_main=True,
            timestamp=datetime.datetime(2024, 1, 16, 0, 0, 0),
            procedure_reference="2022/0099(COD)",
            member_votes=_make_member_votes(457, 92, 32),
        ),
        Vote(
            id="153971",
            is_main=True,
            timestamp=datetime.datetime(2023, 3, 30, 0, 0, 0),
            procedure_reference="2022/0099(COD)",
            member_votes=_make_member_votes(426, 109, 52),
        ),
    ]

    analyzer = OEILSummaryAnalyzer(votes, summaries)
    fragments = list(analyzer.run())

    expected = [
        Fragment(
            model="Vote",
            source_id="162974:1772308",
            source_name="OEILSummaryAnalyzer",
            group_key="162974",
            data={"oeil_summary_id": "1772308"},
        ),
        Fragment(
            model="Vote",
            source_id="153971:1739466",
            source_name="OEILSummaryAnalyzer",
            group_key="153971",
            data={"oeil_summary_id": "1739466"},
        ),
    ]

    assert len(fragments) == 2
    assert record_to_dict(fragments[0]) == record_to_dict(expected[0])
    assert record_to_dict(fragments[1]) == record_to_dict(expected[1])


def test_oeil_summary_analyzer_no_position_counts():
    summaries = [
        OEILSummary(
            id="123",
            date=datetime.date(2026, 1, 1),
            procedure_reference="2026/1234(COD)",
            position_counts=None,
        )
    ]

    votes = [
        Vote(
            id="123456",
            is_main=False,
            timestamp=datetime.datetime(2026, 1, 1, 0, 0, 0),
            procedure_reference="2026/1234(COD)",
            member_votes=_make_member_votes(1, 2, 3),
        )
    ]

    analyzer = OEILSummaryAnalyzer(votes, summaries)
    fragments = list(analyzer.run())
    assert len(fragments) == 0


def test_oeil_summary_no_main_vote():
    summaries = [
        OEILSummary(
            id="123",
            date=datetime.date(2026, 1, 1),
            procedure_reference="2026/1234(COD)",
            position_counts=[
                {"FOR": 1, "AGAINST": 2, "ABSTENTION": 3, "DID_NOT_VOTE": 0},
            ],
        )
    ]

    votes = [
        Vote(
            id="123456",
            is_main=False,
            timestamp=datetime.datetime(2026, 1, 1, 0, 0, 0),
            procedure_reference="2026/1234(COD)",
            member_votes=_make_member_votes(1, 2, 3),
        )
    ]

    analyzer = OEILSummaryAnalyzer(votes, summaries)
    fragments = list(analyzer.run())
    assert len(fragments) == 0


def test_oeil_summary_analyzer_multiple_votes_mentioned_in_summary():
    summaries = [
        OEILSummary(
            id="1720854",
            date=datetime.date(2021, 10, 18),
            procedure_reference="2021/2146(DEC)",
            position_counts=[
                {"FOR": 345, "AGAINST": 284, "ABSTENTION": 8, "DID_NOT_VOTE": 0},
                {"FOR": 467, "AGAINST": 136, "ABSTENTION": 15, "DID_NOT_VOTE": 0},
            ],
        )
    ]

    votes = [
        Vote(
            id="149084",
            is_main=True,
            timestamp=datetime.datetime(2021, 10, 18, 0, 0, 0),
            procedure_reference="2021/2146(DEC)",
            description="Propositions de décision",
            member_votes=_make_member_votes(345, 284, 8),
        ),
        Vote(
            id="148972",
            is_main=True,
            timestamp=datetime.datetime(2021, 10, 18, 0, 0, 0),
            procedure_reference="2021/2146(DEC)",
            description="Proposition de résolution (ensemble du texte)",
            member_votes=_make_member_votes(467, 136, 15),
        ),
    ]

    analyzer = OEILSummaryAnalyzer(votes, summaries)
    fragments = list(analyzer.run())
    assert len(fragments) == 0


def test_oeil_summary_analyzer_multiple_votes_only_one_mentioned():
    summaries = [
        OEILSummary(
            id="1880954",
            date=datetime.date(2025, 12, 17),
            procedure_reference="2025/3007(RSP)",
            position_counts=[
                {"FOR": 358, "AGAINST": 202, "ABSTENTION": 79, "DID_NOT_VOTE": 0},
            ],
        )
    ]

    votes = [
        Vote(
            id="182713",
            is_main=True,
            timestamp=datetime.datetime(2025, 12, 17, 0, 0, 0),
            procedure_reference="2025/3007(RSP)",
            member_votes=_make_member_votes(241, 356, 48),
        ),
        Vote(
            id="182767",
            is_main=True,
            timestamp=datetime.datetime(2025, 12, 17, 0, 0, 0),
            procedure_reference="2025/3007(RSP)",
            member_votes=_make_member_votes(358, 202, 79),
        ),
    ]

    analyzer = OEILSummaryAnalyzer(votes, summaries)
    fragments = list(analyzer.run())

    expected = (
        Fragment(
            model="Vote",
            source_id="182767:1880954",
            source_name="OEILSummaryAnalyzer",
            group_key="182767",
            data={"oeil_summary_id": "1880954"},
        ),
    )

    assert len(fragments) == 1
    assert record_to_dict(fragments[0]) == record_to_dict(expected[0])


def _make_grouped_member_votes(
    timestamp: datetime.datetime,
    *groups: tuple[str | None, VotePosition, int],
) -> tuple[list[MemberVote], dict[int, Member]]:
    member_votes = []
    members_by_id = {}
    member_id = 0

    for group_code, position, count in groups:
        for _ in range(count):
            member_id += 1
            group_membership = GroupMembership(
                term=10,
                group=Group[group_code],
                start_date=timestamp.date(),
                end_date=None,
            )

            member_votes.append(MemberVote(web_id=member_id, position=position))
            members_by_id[member_id] = Member(
                id=member_id,
                group_memberships=[group_membership],
            )

    return member_votes, members_by_id


def test_required_groups_analyzer_finds_minimum_coalitions_in_stable_order():
    timestamp = datetime.datetime(2026, 1, 1)
    member_votes, members_by_id = _make_grouped_member_votes(
        timestamp,
        ("EPP", VotePosition.FOR, 4),
        ("SD", VotePosition.FOR, 3),
        ("RENEW", VotePosition.FOR, 3),
    )
    vote = Vote(
        id=1,
        timestamp=timestamp,
        result=VoteResult.ADOPTED,
        majority_type=MajorityType.MAJORITY_OF_VOTES_CAST,
        member_votes=member_votes,
    )

    fragment = RequiredGroupsAnalyzer(vote, members_by_id).run()

    assert fragment is not None
    assert fragment.data == {
        "groups_required_for_majority": [
            ["EPP", "RENEW"],
            ["EPP", "SD"],
            ["RENEW", "SD"],
        ]
    }


def test_required_groups_analyzer_treats_tied_split_vote_as_adopted():
    timestamp = datetime.datetime(2026, 1, 1)
    member_votes, members_by_id = _make_grouped_member_votes(
        timestamp,
        ("EPP", VotePosition.FOR, 1),
        ("SD", VotePosition.FOR, 4),
        ("ECR", VotePosition.AGAINST, 3),
    )

    ordinary_vote = Vote(
        id=1,
        timestamp=timestamp,
        result=VoteResult.ADOPTED,
        majority_type=MajorityType.MAJORITY_OF_VOTES_CAST,
        member_votes=member_votes,
    )
    split_vote = Vote(
        id=2,
        timestamp=timestamp,
        result=VoteResult.ADOPTED,
        majority_type=MajorityType.MAJORITY_OF_VOTES_CAST,
        amendment_number="§",
        member_votes=member_votes,
    )

    ordinary_fragment = RequiredGroupsAnalyzer(ordinary_vote, members_by_id).run()
    split_fragment = RequiredGroupsAnalyzer(split_vote, members_by_id).run()

    assert ordinary_fragment is not None
    assert split_fragment is not None
    assert ordinary_fragment.data == {"groups_required_for_majority": [["EPP"], ["SD"]]}
    assert split_fragment.data == {"groups_required_for_majority": [["SD"]]}


def test_required_groups_analyzer_component_majority():
    timestamp = datetime.datetime(2026, 1, 1)
    member_votes, members_by_id = _make_grouped_member_votes(
        timestamp,
        ("EPP", VotePosition.FOR, 2),
        ("SD", VotePosition.FOR, 1),
        ("RENEW", VotePosition.FOR, 360),
    )
    vote = Vote(
        id=1,
        timestamp=timestamp,
        result=VoteResult.ADOPTED,
        majority_type=MajorityType.MAJORITY_OF_COMPONENT_MEMBERS,
        member_votes=member_votes,
    )

    fragment = RequiredGroupsAnalyzer(vote, members_by_id).run()

    assert fragment is not None
    assert fragment.data == {"groups_required_for_majority": [["RENEW"], ["EPP", "SD"]]}


def test_required_groups_analyzer_two_thirds_votes_cast_and_majority_of_component_members_majority_calc():
    vote = Vote(
        majority_type=MajorityType.TWO_THIRDS_OF_VOTES_CAST_AND_MAJORITY_OF_COMPONENT_MEMBERS,
    )
    analyzer = RequiredGroupsAnalyzer(vote, members_by_id={})

    # Majority of component members and two-thirds - MAJORITY
    assert analyzer._has_majority(votes_in_favor=361, votes_against=180)
    # Majority if component members but not two-thirds - NO MAJORITY
    assert not analyzer._has_majority(votes_in_favor=361, votes_against=181)
    # No majority of component members but two thirds - NO MAJORITY
    assert not analyzer._has_majority(votes_in_favor=360, votes_against=180)


def test_required_groups_analyzer_two_thirds_votes_cast_and_majority_of_component_members():
    timestamp = datetime.datetime(2026, 1, 1)

    ### CASE 1: One Group can be flipped, component members threshold implicitly reached ###
    # 653 Votes
    # 436 FOR required to pass 2/3 => majority of component members reached as well
    member_votes, members_by_id = _make_grouped_member_votes(
        timestamp,
        ("EPP", VotePosition.FOR, 200),
        ("ESN", VotePosition.FOR, 22),
        ("SD", VotePosition.FOR, 100),
        ("RENEW", VotePosition.FOR, 114),
        ("ECR", VotePosition.FOR, 5),  # not required for 2/3
        ("PFE", VotePosition.AGAINST, 212),
    )
    vote = Vote(
        id=1,
        timestamp=timestamp,
        result=VoteResult.ADOPTED,
        majority_type=MajorityType.TWO_THIRDS_OF_VOTES_CAST_AND_MAJORITY_OF_COMPONENT_MEMBERS,
        member_votes=member_votes,
    )

    fragment = RequiredGroupsAnalyzer(vote, members_by_id).run()

    assert fragment is not None
    assert fragment.data == {
        "groups_required_for_majority": [["EPP"], ["ESN"], ["RENEW"], ["SD"]]
    }

    ### CASE 2: No group can be flipped, due to component members threshold ###
    # 400 Votes
    # 267 FOR required to pass 2/3 => majority of component members not necessarily reached
    member_votes, members_by_id = _make_grouped_member_votes(
        timestamp,
        ("EPP", VotePosition.FOR, 100),
        ("ESN", VotePosition.FOR, 67),
        ("SD", VotePosition.FOR, 193),
        (
            "RENEW",
            VotePosition.FOR,
            20,
        ),  # flipping would still suffice for 2/3 but not majority of component members
        ("PFE", VotePosition.AGAINST, 20),
    )
    vote = Vote(
        id=2,
        timestamp=timestamp,
        result=VoteResult.ADOPTED,
        majority_type=MajorityType.TWO_THIRDS_OF_VOTES_CAST_AND_MAJORITY_OF_COMPONENT_MEMBERS,
        member_votes=member_votes,
    )

    fragment = RequiredGroupsAnalyzer(vote, members_by_id).run()

    assert fragment is not None
    assert fragment.data == {
        "groups_required_for_majority": [["EPP"], ["ESN"], ["RENEW"], ["SD"]]
    }

    ### CASE 3: No single group can change outcome ###
    # 500 Votes
    # 334 FOR required to pass 2/3 => majority of component members not necessarily reached
    # but flipping a single group will always lead to 400/100 => both thresholds reached
    member_votes, members_by_id = _make_grouped_member_votes(
        timestamp,
        ("EPP", VotePosition.FOR, 100),
        ("ESN", VotePosition.FOR, 100),
        ("SD", VotePosition.FOR, 100),
        ("RENEW", VotePosition.FOR, 100),
        ("PFE", VotePosition.FOR, 100),
    )
    vote = Vote(
        id=2,
        timestamp=timestamp,
        result=VoteResult.ADOPTED,
        majority_type=MajorityType.TWO_THIRDS_OF_VOTES_CAST_AND_MAJORITY_OF_COMPONENT_MEMBERS,
        member_votes=member_votes,
    )

    fragment = RequiredGroupsAnalyzer(vote, members_by_id).run()

    assert fragment is not None
    assert fragment.data == {
        "groups_required_for_majority": [
            ["EPP", "ESN"],
            ["EPP", "PFE"],
            ["EPP", "RENEW"],
            ["EPP", "SD"],
            ["ESN", "PFE"],
            ["ESN", "RENEW"],
            ["ESN", "SD"],
            ["PFE", "RENEW"],
            ["PFE", "SD"],
            ["RENEW", "SD"],
        ]
    }
