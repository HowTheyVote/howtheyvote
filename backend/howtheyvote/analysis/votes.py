import datetime
from collections import defaultdict
from collections.abc import Iterable, Iterator
from itertools import chain

from unidecode import unidecode

from ..helpers import make_key
from ..models import DataIssue, Fragment, PressRelease, Vote


class VoteGroupsAnalyzer:
    """Most of the time, before casting a main/final vote, MEPs vote on a bunch
    amendments, split, or separate votes. These votes usually all have the same title.
    Most of the time, they will also have the same reference or procedure reference,
    but that is not always the case. The analyzer assigns a group key derived from the
    session and title. The key can be used to retrieve other votes from the same group,
    e.g. in order to display a list of amendment votes for a given main vote."""

    def __init__(self, date: datetime.date, votes: Iterable[Vote]):
        self.date = date
        self.votes = votes

    def run(self) -> Iterator[Fragment]:
        groups: dict[str, list[int]] = defaultdict(list)

        for vote in self.votes:
            group_key = self._make_group_key(self.date, vote)
            if group_key:
                groups[group_key].append(vote.id)

        for group_key, vote_ids in groups.items():
            yield Fragment(
                model="VoteGroup",
                source_id=group_key,
                source_name=type(self).__name__,
                group_key=group_key,
                data={"date": self.date.isoformat()},
            )

            for vote_id in vote_ids:
                yield Fragment(
                    model="Vote",
                    source_id=vote_id,
                    source_name=type(self).__name__,
                    group_key=vote_id,
                    data={"group_key": group_key},
                )

    def _make_group_key(self, date: datetime.date, vote: Vote) -> str | None:
        title = vote.display_title

        if not title:
            return None

        return make_key(date.isoformat(), title)


class MainVoteAnalyzer:
    """This analyzer checks the vote description for common keywords that indicate
    that the vote is a main vote in its vote group. Only main votes are displayed
    in index pages and are searchable."""

    MAIN_DESCRIPTIONS = set(
        [
            "draft council decision",
            "projet de decision du conseil",
            "projet de reglement du conseil",
            "projet de recommendation",
            "motion for resolution",
            "motion for resolution (as a whole)",
            "motion for resolution (text as a whole)",
            "motion for a resolution",
            "motion for a resolution (as a whole)",
            "motion for a resolution (text as a whole)",
            "proposition de resolution",
            "proposition de resolution (ensemble du texte)",
            "resolution",
            "proposals for decision",
            "proposition de decision",
            "proposal for a decision",
            "proposal for a decision (as a whole)",
            "proposition de decision (ensemble du texte)",
            "commission proposal",
            "proposition de la commission",
            "proposition de commission",
            "proposition de la commission et amendement",
            "proposition de la commission et amendements",
            "proposition de la commission au conseil",
            "provisional agreement",
            "accord provisoire",
            "final vote",
            "decision d'engager des negociations interinstitutionnelles",
            "projet de decision du conseil europeen",
        ]
    )

    def __init__(self, vote_id: int, description: str | None):
        self.vote_id = vote_id
        self.description = description

    def run(self) -> Fragment | None:
        if not self.description:
            return None

        description = unidecode(self.description).lower()
        parts = description.split(" - ")

        if all([part not in self.MAIN_DESCRIPTIONS for part in parts]):
            return None

        return Fragment(
            model="Vote",
            source_id=self.vote_id,
            source_name=type(self).__name__,
            group_key=self.vote_id,
            data={"is_main": True},
        )


class FeaturedVotesAnalyzer:
    """This analyzer takes a set of press releases and a set of votes (typically from
    # the same session) and finds matches between the two sets based on document or
    # procedure references. If a press release exists for a vote, we consider it to be
    # particularly relevant and assign a flag that can be used for filtering."""

    def __init__(self, votes: Iterable[Vote], press_releases: Iterable[PressRelease]):
        self.votes = votes

        self.by_procedure_reference: dict[str, set[str]] = defaultdict(set)
        self.by_reference: dict[str, set[str]] = defaultdict(set)

        for press_release in press_releases:
            if press_release.references:
                for reference in press_release.references:
                    self.by_reference[reference].add(press_release.id)

            if press_release.procedure_references:
                for procedure_reference in press_release.procedure_references:
                    self.by_procedure_reference[procedure_reference].add(press_release.id)

    def run(self) -> Iterator[Fragment]:
        for vote in self.votes:
            if not vote.is_main:
                continue

            release_ids = set()

            if vote.reference and vote.reference in self.by_reference:
                release_ids |= self.by_reference[vote.reference]

            if (
                vote.procedure_reference
                and vote.procedure_reference in self.by_procedure_reference
            ):
                release_ids |= self.by_procedure_reference[vote.procedure_reference]

            for release_id in release_ids:
                yield Fragment(
                    model="Vote",
                    source_id=f"{vote.id}:{release_id}",
                    source_name=type(self).__name__,
                    group_key=vote.id,
                    data={"is_featured": True},
                )


class VoteDataIssuesAnalyzer:
    """This analyzer checks a vote for common data quality issues. Depending on
    the issue type, we might decide not to display the vote at all or to show
    a warning message in the frontend. The analyzer also helps discovering new
    edge cases or short comings in other scrapers and analyzers."""

    def __init__(self, vote: Vote):
        self.vote = vote

    def run(self) -> Iterator[Fragment]:
        return chain(
            self.member_votes_count(),
            self.empty_titles(),
        )

    def empty_titles(self) -> Iterator[Fragment]:
        if self.vote.title or self.vote.procedure_title:
            return

        yield Fragment(
            model="Vote",
            source_id=self.vote.id,
            source_name=type(self).__name__,
            group_key=self.vote.id,
            data={"issues": [DataIssue.EMPTY_TITLES]},
        )

    def member_votes_count(self) -> Iterator[Fragment]:
        brexit_date = datetime.date(2020, 2, 1)
        tenth_term_date = datetime.date(2024, 7, 16)
        date = self.vote.timestamp.date()
        count = len(self.vote.member_votes)

        issues = []

        if (
            (date < brexit_date and count != 751)
            or (date >= brexit_date and count != 705)
            or (date >= tenth_term_date and count != 720)
        ):
            issues = [DataIssue.MEMBER_VOTES_COUNT_MISMATCH]

        yield Fragment(
            model="Vote",
            source_id=self.vote.id,
            source_name=type(self).__name__,
            group_key=self.vote.id,
            data={"issues": issues},
        )


class VoteGroupsDataIssuesAnalyzer:
    """This analyzer checks that there is at least one main vote per vote group. This is useful
    in order to identify votes that the `MainVoteAnalyzer` currently doesn’t ocrrectly classify
    as a main vote."""

    def __init__(self, votes: Iterable[Vote]):
        self.votes = votes

    def run(self) -> Iterator[Fragment]:
        groups: dict[str, list[Vote]] = defaultdict(list)

        for vote in self.votes:
            if vote.group_key:
                groups[vote.group_key].append(vote)

        for group_key, votes in groups.items():
            issues = []

            if all(not vote.is_main for vote in votes):
                issues = [DataIssue.VOTE_GROUP_NO_MAIN_VOTE]

            yield Fragment(
                model="VoteGroup",
                source_id=group_key,
                source_name=type(self).__name__,
                group_key=group_key,
                data={"issues": issues},
            )
