import csv
from collections.abc import Iterable
from io import StringIO

from flask import Blueprint, Request, Response, abort, jsonify, request
from sqlalchemy import or_, select
from structlog import get_logger

from ..db import Session
from ..helpers import (
    PROCEDURE_REFERENCE_REGEX,
    REFERENCE_REGEX,
    flatten_dict,
    parse_procedure_reference,
    subset_dict,
)
from ..models import Fragment, Member, PressRelease, Vote
from ..query import fragments_for_records
from ..vote_stats import count_vote_positions, count_vote_positions_by_group
from .query import DatabaseQuery, Order, Query, SearchQuery
from .serializers import (
    BaseVoteDict,
    MemberVoteDict,
    ProcedureDict,
    RelatedVoteDict,
    SourceDict,
    VoteDict,
    VotePositionCountsDict,
    VotesQueryResponseDict,
    VoteStatsByCountryDict,
    VoteStatsByGroupDict,
    VoteStatsDict,
    serialize_base_vote,
    serialize_country,
    serialize_group,
    serialize_member,
)
from .util import one_of

log = get_logger(__name__)

bp = Blueprint("votes_api", __name__)

MembersById = dict[int, Member]

SOURCE_INFO = {
    "RCVListScraper": {
        "name": "Results of roll-call votes (XML)",
    },
    "VOTListScraper": {
        "name": "Results of votes (XML)",
    },
    "RCVListEnglishScraper": {
        "name": "Results of roll-call votes (XML)",
    },
    "ProcedureScraper": {
        "name": "Procedure file (Legislative Observatory)",
    },
    "PressReleaseScraper": {
        "name": "Press release",
    },
    "EurlexProcedureScraper": {
        "name": "Procedure file (EUR-Lex)",
    },
    "DocumentScraper": {
        "name": "Report or resolution",
    },
    "EurlexDocumentScraper": {
        "name": "Report or resolution (EUR-Lex)",
    },
}


@bp.route("/votes")
def index() -> Response:
    """List votes
    ---
    get:
        operationId: getVotes
        tags:
            - Votes
        summary: List votes
        description: List votes in chronological order.
        parameters:
            -
                in: query
                name: page
                description: Results page
                schema:
                    type: integer
                    default: 1
            -
                in: query
                name: page_size
                description: Number of results per page
                schema:
                    type: integer
                    default: 20
            -
                in: query
                name: sort_by
                description: Sort results by this field. Omit to sort by relevance.
                schema:
                    type: string
                    enum:
                        - timestamp
            -
                in: query
                name: sort_order
                description: Sort results in ascending or descending order
                schema:
                    type: string
                    enum:
                        - asc
                        - desc
        responses:
            '200':
                description: Ok
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/VotesQueryResponse'
    """
    query = _query_from_request(DatabaseQuery, request)
    query = query.filter("is_main", True)
    query = query.where(or_(Vote.title != None, Vote.procedure_title != None))  # noqa: E711

    return jsonify(_serialize_query(query))


@bp.route("/votes/search")
def search() -> Response:
    """
    Search votes
    ---
    get:
        operationId: searchVotes
        tags:
            - Votes
        summary: Search votes
        description: |
            Search votes by title and reference. This endpoint returns a maximum of 1,000
            results, even if more than 1,000 votes match the search query.
        parameters:
            -
                in: query
                name: q
                description: Search query
                schema:
                    type: string
            -
                in: query
                name: page
                description: Results page
                schema:
                    type: integer
                    default: 1
            -
                in: query
                name: page_size
                description: Number of results per page
                schema:
                    type: integer
                    default: 20
            -
                in: query
                name: sort_by
                description: Sort results by this field. Omit to sort by relevance.
                schema:
                    type: string
                    enum:
                        - timestamp
            -
                in: query
                name: sort_order
                description: Sort results in ascending or descending order
                schema:
                    type: string
                    enum:
                        - asc
                        - desc
        responses:
            '200':
                description: Ok
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/VotesQueryResponse'

    """
    q = request.args.get("q", "").strip()
    query = _query_from_request(SearchQuery, request)

    # Detect document references and apply a filter
    references = [match.group(0) for match in REFERENCE_REGEX.finditer(q)]
    q = REFERENCE_REGEX.sub("", q)

    for reference in references:
        query = query.filter("reference", reference)

    # Detect procedure references and apply a filter
    procedure_references = [match.group(0) for match in PROCEDURE_REFERENCE_REGEX.finditer(q)]
    q = PROCEDURE_REFERENCE_REGEX.sub("", q)

    for procedure_reference in procedure_references:
        query = query.filter("procedure_reference", procedure_reference)

    if q:
        query = query.query(q)

    return jsonify(_serialize_query(query))


@bp.route("/votes/<int:vote_id>")
def show(vote_id: int) -> Response:
    """
    ---
    get:
        operationId: getVote
        summary: Get vote
        tags:
            - Votes
        description: |
            Get information about a vote. This includes metadata (e.g. vote title and
            timestamp), aggregated statistics, and the votes of individual MEPs.
        parameters:
            -
                in: path
                name: vote_id
                required: true
                schema:
                    type: string
        responses:
            '200':
                description: Ok
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Vote'
    """
    vote = Session.get(Vote, vote_id)

    if not vote:
        return abort(404)

    base_vote = serialize_base_vote(vote)
    procedure: ProcedureDict | None = None

    if vote.procedure_reference:
        procedure_reference = parse_procedure_reference(vote.procedure_reference)

        procedure = {
            "title": vote.procedure_title,
            "type": procedure_reference["type"],
            "reference": vote.procedure_reference,
            "stage": vote.procedure_stage,
        }

    members = _load_members(vote)
    members_by_id: MembersById = {m.id: m for m in members}

    stats: VoteStatsDict = {
        "total": _format_total_stats(vote),
        "by_group": _format_group_stats(vote, members_by_id),
        "by_country": _format_country_stats(vote, members_by_id),
    }

    member_votes = _format_member_votes(vote, members_by_id)

    related_votes = _format_related(_load_related(vote))

    press_release = _load_press_release(vote)
    facts = press_release.facts if press_release else None

    fragments = _load_fragments(vote, press_release)
    sources = _format_sources(fragments)

    data: VoteDict = {
        **base_vote,
        "procedure": procedure,
        "facts": facts,
        "sharepic_url": vote.sharepic_url,
        "stats": stats,
        "member_votes": member_votes,
        "sources": sources,
        "related": related_votes,
    }

    return jsonify(data)


@bp.route("/votes/<int:vote_id>.csv")
def show_csv(vote_id: int) -> Response:
    """
    ---
    get:
        operationId: getVoteCSV
        summary: Get vote as CSV
        tags:
            - Votes
        description: |
            Get votes of individual MEPs as CSV.
        parameters:
            -
                in: path
                name: vote_id
                required: true
                schema:
                    type: string
    """
    vote = Session.get(Vote, vote_id)

    if not vote:
        return abort(404)

    members = _load_members(vote)
    members_by_id: MembersById = {m.id: m for m in members}
    member_votes = _format_member_votes(vote, members_by_id)

    fieldnames = [
        "position",
        "member.id",
        "member.first_name",
        "member.last_name",
        "member.country.code",
        "member.country.label",
        "member.country.iso_alpha_2",
        "member.group.code",
        "member.group.label",
        "member.group.short_label",
    ]

    io = StringIO()
    writer = csv.DictWriter(io, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(subset_dict(flatten_dict(mv), fieldnames) for mv in member_votes)

    return Response(
        io.getvalue(),
        headers={
            "Content-Type": "text/csv",
        },
    )


def _query_from_request[T: Query[Vote]](cls: type[T], request: Request) -> T:
    query = cls(Vote)

    # Pagination
    query = query.page(request.args.get("page", type=int))
    query = query.page_size(request.args.get("page_size", type=int))

    # Sort
    sort_field = request.args.get("sort_by", type=one_of("timestamp"))
    sort_order = request.args.get("sort_order", type=Order)

    if sort_field:
        query = query.sort(field=sort_field, order=sort_order)

    return query


def _serialize_query(query: Query[Vote]) -> VotesQueryResponseDict:
    response = query.handle()
    results: list[BaseVoteDict] = [
        serialize_base_vote(result) for result in response["results"]
    ]

    return {
        **response,
        "results": results,
    }


def _load_fragments(vote: Vote, press_release: PressRelease | None) -> Iterable[Fragment]:
    stmt = select(Fragment).where(fragments_for_records([vote, press_release]))
    return Session.execute(stmt).scalars()


def _load_press_release(vote: Vote) -> PressRelease | None:
    if not vote.press_release:
        return None

    stmt = select(PressRelease).where(PressRelease.id == vote.press_release)
    return Session.execute(stmt).scalar()


def _load_members(vote: Vote) -> Iterable[Member]:
    member_ids = [mv.web_id for mv in vote.member_votes]
    stmt = select(Member).where(Member.id.in_(member_ids))
    return Session.execute(stmt).scalars()


def _load_related(vote: Vote) -> Iterable[Vote]:
    if not vote.group_key:
        return []

    stmt = select(Vote).where(Vote.group_key == vote.group_key).order_by(Vote.order)

    return Session.execute(stmt).scalars()


def _format_related(votes: Iterable[Vote]) -> list[RelatedVoteDict]:
    formatted: list[RelatedVoteDict] = []

    for vote in votes:
        formatted.append(
            {
                "id": vote.id,
                "timestamp": vote.timestamp,
                "description": vote.description,
            }
        )

    return formatted


def _format_sources(fragments: Iterable[Fragment]) -> list[SourceDict]:
    sources: list[SourceDict] = []

    for fragment in fragments:
        if fragment.source_name not in SOURCE_INFO:
            continue

        if not fragment.source_url:
            continue

        sources.append(
            {
                "url": fragment.source_url,
                "accessed_at": fragment.timestamp,
                "name": SOURCE_INFO[fragment.source_name]["name"],
            }
        )

    return sorted(sources, key=lambda s: s["accessed_at"])


def _format_member_votes(vote: Vote, members_by_id: MembersById) -> list[MemberVoteDict]:
    member_votes: list[MemberVoteDict] = []

    for member_vote in vote.member_votes:
        web_id = member_vote.web_id
        position = member_vote.position
        member = members_by_id.get(web_id)

        if not member:
            continue

        member_votes.append(
            {
                "member": serialize_member(member, vote.timestamp.date()),
                "position": position,
            }
        )
    return sorted(member_votes, key=lambda x: x["member"]["last_name"])


def _format_total_stats(vote: Vote) -> VotePositionCountsDict:
    return count_vote_positions(vote.member_votes)


def _format_group_stats(vote: Vote, members_by_id: MembersById) -> list[VoteStatsByGroupDict]:
    group_stats = count_vote_positions_by_group(
        member_votes=vote.member_votes,
        group_by=lambda mv: members_by_id[mv.web_id].group_at(vote.timestamp),
    )

    return [
        {
            "group": serialize_group(group),
            "stats": stats,
        }
        for group, stats in group_stats.items()
        if group is not None
    ]


def _format_country_stats(
    vote: Vote, members_by_id: MembersById
) -> list[VoteStatsByCountryDict]:
    country_stats = count_vote_positions_by_group(
        member_votes=vote.member_votes,
        group_by=lambda mv: members_by_id[mv.web_id].country,
    )

    return [
        {
            "country": serialize_country(country),
            "stats": stats,
        }
        for country, stats in country_stats.items()
        if country is not None
    ]
