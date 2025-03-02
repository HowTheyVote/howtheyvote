from collections import defaultdict
from collections.abc import Callable
from typing import TypeVar

from .models import MemberVote, VotePositionCounts

GroupBy = TypeVar("GroupBy")


def count_vote_positions(member_votes: list[MemberVote]) -> VotePositionCounts:
    """Calculates the number of MEPs that voted for/against/abstention for the given
    list of member votes."""
    counts: VotePositionCounts = {
        "FOR": 0,
        "AGAINST": 0,
        "ABSTENTION": 0,
        "DID_NOT_VOTE": 0,
    }

    for member_vote in member_votes:
        counts[member_vote.position.value] += 1

    return counts


def count_vote_positions_by_group(
    member_votes: list[MemberVote],
    group_by: Callable[[MemberVote], GroupBy],
) -> dict[GroupBy, VotePositionCounts]:
    """Calculates the number of MEPs that voted for/against/abstention for the given
    list of member votes for each group. The second argument is a function that returns
    the group for each member vote."""
    grouped_member_votes: dict[GroupBy, list[MemberVote]] = defaultdict(list)

    for member_vote in member_votes:
        group = group_by(member_vote)
        grouped_member_votes[group].append(member_vote)

    # Sort by group size
    grouped_member_votes = dict(
        sorted(
            grouped_member_votes.items(),
            key=lambda item: len(item[1]),
            reverse=True,
        )
    )

    grouped_counts: dict[GroupBy, VotePositionCounts] = {}

    for group, member_votes in grouped_member_votes.items():
        grouped_counts[group] = count_vote_positions(member_votes)

    return grouped_counts
