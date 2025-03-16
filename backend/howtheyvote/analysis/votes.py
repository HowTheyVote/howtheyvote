import datetime
from collections import defaultdict
from collections.abc import Iterable, Iterator

from unidecode import unidecode

from ..helpers import make_key
from ..models import DataIssue, Fragment, PressRelease, Vote
from ..vote_stats import count_vote_positions


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
    """This analyzer checks the vote description and title for common keywords
    that indicate that the vote is a main vote in its vote group. Only main
    votes are displayed in index pages and are searchable."""

    MAIN_DESCRIPTIONS = set(
        [
            "draft council decision",
            "projet de decision du conseil",
            "projet de reglement du conseil",
            "projet du conseil",
            "projet de recommendation",
            "projet commun",
            "motion for resolution",
            "motion for resolution (as a whole)",
            "motion for resolution (text as a whole)",
            "motion for a resolution",
            "motion for a resolution (as a whole)",
            "motion for a resolution (text as a whole)",
            "proposition de resolution",
            "proposition de resolution (ensemble du texte)",
            "proposition de la résolution",
            "proposition de la résolution (ensemble du texte)",
            "proposition de recommandation",
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
            "accord provisoire (proposition de la commission - non modifiee)",
            "final vote",
            "decision d'engager des negociations interinstitutionnelles",
            "projet de decision du conseil europeen",
            "projet de decision",
        ]
    )

    MAIN_TITLES = set(
        [
            "election de la commission",
            "election of the commission",
        ]
    )

    def __init__(self, vote_id: int, description: str | None, title: str | None):
        self.vote_id = vote_id
        self.description = description
        self.title = title

    def run(self) -> Fragment | None:
        if self._description_is_main() or self._title_is_main():
            return Fragment(
                model="Vote",
                source_id=self.vote_id,
                source_name=type(self).__name__,
                group_key=self.vote_id,
                data={"is_main": True},
            )

        return None

    def _description_is_main(self) -> bool:
        if not self.description:
            return False

        description = unidecode(self.description).lower()
        parts = description.split(" - ")

        if any([part in self.MAIN_DESCRIPTIONS for part in parts]):
            return True

        return False

    def _title_is_main(self) -> bool:
        if not self.title:
            return False

        title = unidecode(self.title).lower()

        if title in self.MAIN_TITLES:
            return True

        return False


PositionCounts = tuple[int, int, int]
ReleasesByDatePositionCounts = dict[tuple[datetime.date, PositionCounts], set[str]]
ReleasesByReference = dict[str, set[str]]
ReleasesByProcedureReference = dict[str, set[str]]
VotesByDatePositionCounts = dict[tuple[datetime.date, PositionCounts], int]
DatePositionCountsByVote = dict[int, tuple[datetime.date, PositionCounts]]


class PressReleaseAnalyzer:
    """This analyzer takes a set of press releases and a set of votes (typically from the
    same session) and finds matches between the two sets. If we find a match, we store a
    reference to the press release in the vote record. This can later be used to display
    press release excerpts for a vote, for search results ranking, etc."""

    def __init__(self, votes: list[Vote], press_releases: Iterable[PressRelease]):
        self.votes = votes
        self.press_releases = press_releases

        self._build_votes_lookups()
        self._build_press_releases_lookups()

    def run(self) -> Iterator[Fragment]:
        for vote in self.votes:
            if not vote.is_main:
                continue

            release_ids = set()
            release_ids |= self._match_by_reference(vote)
            release_ids |= self._match_by_procedure_reference(vote)
            release_ids |= self._match_by_position_counts(vote)

            for release_id in release_ids:
                yield Fragment(
                    model="Vote",
                    source_id=f"{vote.id}:{release_id}",
                    source_name=type(self).__name__,
                    group_key=vote.id,
                    data={"press_release": release_id},
                )

    def _build_votes_lookups(self) -> None:
        self._votes_by_date_position_counts: VotesByDatePositionCounts = defaultdict(int)
        self._date_position_counts_by_vote: DatePositionCountsByVote = {}

        for vote in self.votes:
            counts = count_vote_positions(vote.member_votes)
            key = (
                vote.timestamp.date(),
                (counts["FOR"], counts["AGAINST"], counts["ABSTENTION"]),
            )
            self._votes_by_date_position_counts[key] += 1
            self._date_position_counts_by_vote[vote.id] = key

    def _build_press_releases_lookups(self) -> None:
        self._releases_by_procedure_reference: ReleasesByProcedureReference = defaultdict(set)
        self._releases_by_reference: ReleasesByReference = defaultdict(set)
        self._releases_by_date_position_counts: ReleasesByDatePositionCounts = defaultdict(set)

        for release in self.press_releases:
            if release.references:
                for ref in release.references:
                    self._releases_by_reference[ref].add(release.id)

            if release.procedure_references:
                for ref in release.procedure_references:
                    self._releases_by_procedure_reference[ref].add(release.id)

            # We are conservative when a press release contains results of more than one vote.
            # While it could be a press release about multiple related votes, the Parliament
            # often publishes press releases with short summaries of multiple non-legislative
            # resolutions (e.g. on the human rights situation in different countries).
            if release.position_counts and len(release.position_counts) == 1:
                # Convert to tuple because dicts cannot be used as keys of another dict
                counts = release.position_counts[0]
                key = (
                    release.published_at.date(),
                    (counts["FOR"], counts["AGAINST"], counts["ABSTENTION"]),
                )
                self._releases_by_date_position_counts[key].add(release.id)

    def _match_by_reference(self, vote: Vote) -> set[str]:
        if not vote.reference:
            return set()

        return self._releases_by_reference[vote.reference]

    def _match_by_procedure_reference(self, vote: Vote) -> set[str]:
        if not vote.procedure_reference:
            return set()

        return self._releases_by_procedure_reference[vote.procedure_reference]

    def _match_by_position_counts(self, vote: Vote) -> set[str]:
        key = self._date_position_counts_by_vote[vote.id]

        if self._votes_by_date_position_counts[key] > 1:
            return set()

        return self._releases_by_date_position_counts[key]


class VoteDataIssuesAnalyzer:
    """This analyzer checks a vote for common data quality issues. Depending on
    the issue type, we might decide not to display the vote at all or to show
    a warning message in the frontend. The analyzer also helps discovering new
    edge cases or short comings in other scrapers and analyzers."""

    def __init__(self, vote: Vote):
        self.vote = vote

    def run(self) -> Fragment:
        issues = [
            self.member_votes_count(),
            self.empty_titles(),
        ]

        issues = [issue for issue in issues if issue is not None]

        return Fragment(
            model="Vote",
            source_id=self.vote.id,
            source_name=type(self).__name__,
            group_key=self.vote.id,
            data={"issues": issues},
        )

    def empty_titles(self) -> DataIssue | None:
        if not self.vote.title and not self.vote.procedure_title:
            return DataIssue.EMPTY_TITLES

        return None

    def member_votes_count(self) -> DataIssue | None:
        date = self.vote.timestamp.date()
        count = len(self.vote.member_votes)

        # 9th term, pre Brexit
        if (
            date >= datetime.date(2019, 7, 2)
            and date < datetime.date(2020, 2, 1)
            and count != 751
        ):
            return DataIssue.MEMBER_VOTES_COUNT_MISMATCH

        # 9th term, post Brexit
        if (
            date >= datetime.date(2020, 2, 1)
            and date < datetime.date(2024, 7, 16)
            and count != 705
        ):
            return DataIssue.MEMBER_VOTES_COUNT_MISMATCH

        # 10th term
        if date >= datetime.date(2024, 7, 16) and count != 720:
            return DataIssue.MEMBER_VOTES_COUNT_MISMATCH

        return None


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
