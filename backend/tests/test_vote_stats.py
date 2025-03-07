from howtheyvote.models import MemberVote, VotePosition
from howtheyvote.vote_stats import count_vote_positions, count_vote_positions_by_group


def test_count_vote_positions():
    assert count_vote_positions([]) == {
        "FOR": 0,
        "AGAINST": 0,
        "ABSTENTION": 0,
        "DID_NOT_VOTE": 0,
    }

    member_votes = [
        MemberVote(web_id=1, position=VotePosition.FOR),
        MemberVote(web_id=2, position=VotePosition.FOR),
        MemberVote(web_id=3, position=VotePosition.DID_NOT_VOTE),
        MemberVote(web_id=4, position=VotePosition.ABSTENTION),
    ]

    assert count_vote_positions(member_votes) == {
        "FOR": 2,
        "AGAINST": 0,
        "ABSTENTION": 1,
        "DID_NOT_VOTE": 1,
    }


def test_count_vote_positions_by_group():
    member_countries = {
        1: "FRA",
        2: "DEU",
        3: "ITA",
        4: "DEU",
    }

    member_votes = [
        MemberVote(web_id=1, position=VotePosition.FOR),
        MemberVote(web_id=2, position=VotePosition.FOR),
        MemberVote(web_id=3, position=VotePosition.ABSTENTION),
        MemberVote(web_id=4, position=VotePosition.DID_NOT_VOTE),
    ]

    grouped_counts = count_vote_positions_by_group(
        member_votes=member_votes, group_by=lambda mv: member_countries[mv.web_id]
    )

    expected = {
        "DEU": {
            "FOR": 1,
            "AGAINST": 0,
            "ABSTENTION": 0,
            "DID_NOT_VOTE": 1,
        },
        "FRA": {
            "FOR": 1,
            "AGAINST": 0,
            "ABSTENTION": 0,
            "DID_NOT_VOTE": 0,
        },
        "ITA": {
            "FOR": 0,
            "AGAINST": 0,
            "ABSTENTION": 1,
            "DID_NOT_VOTE": 0,
        },
    }

    assert grouped_counts == expected
    assert list(grouped_counts.keys()) == ["DEU", "FRA", "ITA"]  # Sorted by group size
