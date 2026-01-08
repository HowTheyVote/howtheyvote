import csv
from collections.abc import Iterable
from datetime import date
from io import StringIO
from typing import Any

from flask import Blueprint, Request, Response, abort, jsonify, request
from flask.typing import ResponseReturnValue
from sqlalchemy import select
from structlog import get_logger

from ..db import Session
from ..helpers import (
    PROCEDURE_REFERENCE_REGEX,
    REFERENCE_REGEX,
    flatten_dict,
    parse_procedure_reference,
    subset_dict,
)
from ..links import (
    doceo_document_url,
    doceo_texts_adopted_url,
    oeil_procedure_url,
    press_release_url,
)
from ..models import (
    Committee,
    Country,
    Fragment,
    Member,
    PressRelease,
    Topic,
    Vote,
)
from ..query import fragments_for_records
from ..vote_stats import count_vote_positions, count_vote_positions_by_group
from .query import Order, SearchQuery
from .serializers import (
    LinkDict,
    MemberVoteDict,
    MemberVotesQueryResponseDict,
    ProcedureDict,
    RelatedVoteDict,
    SourceDict,
    VoteDict,
    VotePositionCountsDict,
    VotesQueryResponseDict,
    VoteStatsByCountryDict,
    VoteStatsByGroupDict,
    VoteStatsDict,
    serialize_amendment_author,
    serialize_base_member,
    serialize_base_vote,
    serialize_base_vote_with_member_position,
    serialize_country,
    serialize_group,
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


@bp.route("/votes/search")
@bp.route("/votes")
def index() -> ResponseReturnValue:
    """
    Get votes
    ---
    get:
        operationId: getVotes
        tags:
            - Votes
        summary: List votes
        description: |
            Get a list of roll-call votes. You can optionally provide a search query
            and filters.
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
                        - date
            -
                in: query
                name: sort_order
                description: Sort results in ascending or descending order
                schema:
                    type: string
                    enum:
                        - asc
                        - desc
            -
                in: query
                name: date
                description: |
                    Filter votes by date and return only votes that were cast on the given
                    date.
                schema:
                    type: string
                    format: date
            -
                in: query
                name: date[gte]
                description: |
                    Filter votes by date and return only votes that were cast on or after the
                    given date.
                schema:
                    type: string
                    format: date
            -
                in: query
                name: date[lte]
                description: |
                    Filter votes by date and return only votes that were cast on or before the
                    given date.
                schema:
                    type: string
                    format: date
            -
                in: query
                name: geo_areas
                description: |
                    Filter votes by geographic area. Valid values are 3-letter country codes
                    [as assigned by the Publications Office of the European Union](https://op.europa.eu/en/web/eu-vocabularies/countries-and-territories).
                schema:
                    type: array
                    items:
                        type: string
            -
                in: query
                name: responsible_committees
                description: |
                    Filter votes by responsible committees. Valid values are 4-letter
                    committee codes.
                schema:
                    type: array
                    items:
                        type: string
            -
                in: query
                name: facets
                description: |
                    Return facet options for the given fields. Can be set multiple times.
                style: form
                explode: true
                schema:
                    type: array
                    items:
                        type: string
                        enum:
                            - geo_areas
                            - responsible_committees
                            - topics
        responses:
            '200':
                description: Ok
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/VotesQueryResponse'
    """
    query = _query_from_request(request)
    return jsonify(_serialize_votes_query(query))


@bp.route("/members/<int:member_id>/votes")
def member_votes_index(member_id: int) -> ResponseReturnValue:
    """
    ---
    get:
        operationId: getMemberVotes
        tags:
            - Members
        summary: List member’s votes
        description: |
            Get a list of roll-call votes along with the member’s vote position. You can
            optionally provide a search query and filters.
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
                        - date
            -
                in: query
                name: sort_order
                description: Sort results in ascending or descending order
                schema:
                    type: string
                    enum:
                        - asc
                        - desc
            -
                in: query
                name: date
                description: |
                    Filter votes by date and return only votes that were cast on the given
                    date.
                schema:
                    type: string
                    format: date
            -
                in: query
                name: date[gte]
                description: |
                    Filter votes by date and return only votes that were cast on or after the
                    given date.
                schema:
                    type: string
                    format: date
            -
                in: query
                name: date[lte]
                description: |
                    Filter votes by date and return only votes that were cast on or before the
                    given date.
                schema:
                    type: string
                    format: date
            -
                in: query
                name: geo_areas
                description: |
                    Filter votes by geographic area. Valid values are 3-letter country codes
                    [as assigned by the Publications Office of the European Union](https://op.europa.eu/en/web/eu-vocabularies/countries-and-territories).
                schema:
                    type: array
                    items:
                        type: string
            -
                in: query
                name: responsible_committees
                description: |
                    Filter votes by responsible committees. Valid values are 4-letter
                    committee codes.
                schema:
                    type: array
                    items:
                        type: string
            -
                in: query
                name: facets
                description: |
                    Return facet options for the given fields. Can be set multiple times.
                style: form
                explode: true
                schema:
                    type: array
                    items:
                        type: string
                        enum:
                            - geo_areas
                            - responsible_committees
                            - topics
        responses:
            '200':
                description: Ok
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/MemberVotesQueryResponse'
    """
    query = _query_from_request(request)
    query = query.filter("member_id", "=", member_id)
    return jsonify(_serialize_member_votes_query(query, member_id))


@bp.route("/votes/<int:vote_id>")
def show(vote_id: int) -> ResponseReturnValue:
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

    facts = vote.press_release.facts if vote.press_release else None

    fragments = _load_fragments(vote, vote.press_release)
    sources = _format_sources(fragments)

    links = _format_links(vote)

    data: VoteDict = {
        **base_vote,
        "procedure": procedure,
        "facts": facts,
        "sharepic_url": vote.sharepic_url,
        "stats": stats,
        "member_votes": member_votes,
        "sources": sources,
        "links": links,
        "related": related_votes,
    }

    return jsonify(data)


@bp.route("/votes/<int:vote_id>.csv")
@bp.route("/votes/<int:vote_id>/members.csv")
def show_csv_meps(vote_id: int) -> ResponseReturnValue:
    """
    ---
    get:
        operationId: getVoteCSVMEPs
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
                    type: int
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
            "Content-Disposition": f'attachment; filename="{vote_id}_members.csv"',
        },
    )


def _format_group_row(group_stat: VoteStatsByGroupDict) -> dict[str, Any]:
    group = group_stat["group"]
    stats = group_stat["stats"]

    return {
        "code": group["code"],
        "label": group["label"],
        "short_label": group["short_label"],
        "count_for": stats["FOR"],
        "count_against": stats["AGAINST"],
        "count_abstentions": stats["ABSTENTION"],
        "count_did_not_vote": stats["DID_NOT_VOTE"],
    }


@bp.route("/votes/<int:vote_id>/groups.csv")
def show_csv_groups(vote_id: int) -> ResponseReturnValue:
    """
    ---
    get:
        operationId: getVoteCSVGroups
        summary: Get vote as CSV (Groups)
        tags:
            - Votes
        description: |
            Get voting behavior among groups as CSV.
        parameters:
            -
                in: path
                name: vote_id
                required: true
                schema:
                    type: int
    """
    vote = Session.get(Vote, vote_id)

    if not vote:
        return abort(404)

    members = _load_members(vote)
    members_by_id: MembersById = {m.id: m for m in members}
    group_stats = _format_group_stats(vote, members_by_id)

    fieldnames = [
        "code",
        "label",
        "short_label",
        "count_for",
        "count_against",
        "count_abstentions",
        "count_did_not_vote",
    ]

    io = StringIO()
    writer = csv.DictWriter(io, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(_format_group_row(gs) for gs in group_stats)

    return Response(
        io.getvalue(),
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": f'attachment; filename="{vote_id}_groups.csv"',
        },
    )


def _format_country_row(group_stat: VoteStatsByCountryDict) -> dict[str, Any]:
    country = group_stat["country"]
    stats = group_stat["stats"]

    return {
        "code": country["code"],
        "label": country["label"],
        "iso_alpha_2": country["iso_alpha_2"],
        "count_for": stats["FOR"],
        "count_against": stats["AGAINST"],
        "count_abstentions": stats["ABSTENTION"],
        "count_did_not_vote": stats["DID_NOT_VOTE"],
    }


@bp.route("/votes/<int:vote_id>/countries.csv")
def show_csv_countries(vote_id: int) -> ResponseReturnValue:
    """
    ---
    get:
        operationId: getVoteCSVCountries
        summary: Get vote as CSV (Countries)
        tags:
            - Votes
        description: |
            Get voting behavior among countries as CSV.
        parameters:
            -
                in: path
                name: vote_id
                required: true
                schema:
                    type: int
    """
    vote = Session.get(Vote, vote_id)

    if not vote:
        return abort(404)

    members = _load_members(vote)
    members_by_id: MembersById = {m.id: m for m in members}
    country_stats = _format_country_stats(vote, members_by_id)

    fieldnames = [
        "code",
        "label",
        "iso_alpha_2",
        "count_for",
        "count_against",
        "count_abstentions",
        "count_did_not_vote",
    ]

    io = StringIO()
    writer = csv.DictWriter(io, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(_format_country_row(cs) for cs in country_stats)

    return Response(
        io.getvalue(),
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": f'attachment; filename="{vote_id}_countries.csv"',
        },
    )


def _query_from_request(request: Request) -> SearchQuery[Vote]:
    query = SearchQuery(Vote)

    q = request.args.get("q", "").strip()

    # Detect document references and apply a filter
    references = [match.group(0) for match in REFERENCE_REGEX.finditer(q)]
    q = REFERENCE_REGEX.sub("", q)

    for reference in references:
        query = query.filter("reference", "=", reference)

    # Detect procedure references and apply a filter
    procedure_references = [match.group(0) for match in PROCEDURE_REFERENCE_REGEX.finditer(q)]
    q = PROCEDURE_REFERENCE_REGEX.sub("", q)

    for procedure_reference in procedure_references:
        query = query.filter("procedure_reference", "=", procedure_reference)

    if q:
        query = query.query(q)

    # Pagination
    query = query.page(request.args.get("page", type=int))
    query = query.page_size(request.args.get("page_size", type=int))

    # Sort
    sort_field = request.args.get("sort_by", type=one_of("date"))
    sort_order = request.args.get("sort_order", type=Order)

    if sort_field:
        query = query.sort(field=sort_field, order=sort_order)

    # Filters
    query = query.filter("date", "=", request.args.get("date", type=date.fromisoformat))
    query = query.filter("date", ">=", request.args.get("date[gte]", type=date.fromisoformat))
    query = query.filter("date", "<=", request.args.get("date[lte]", type=date.fromisoformat))

    geo_areas = request.args.getlist("geo_areas", type=_as_country)
    query = query.filter("geo_areas", "in", geo_areas)

    committees = request.args.getlist("responsible_committees", type=_as_committee)
    query = query.filter("responsible_committees", "in", committees)

    topics = request.args.getlist("topics", type=_as_topic)
    query = query.filter("topics", "in", topics)

    # Facets
    facets = request.args.getlist(
        "facets",
        type=one_of("geo_areas", "responsible_committees", "topics"),
    )

    for field in facets:
        query = query.facet(field)

    return query


def _as_country(code: str) -> Country:
    try:
        return Country[code]
    except KeyError as exc:
        raise ValueError() from exc


def _as_committee(code: str) -> Committee:
    try:
        return Committee[code]
    except KeyError as exc:
        raise ValueError() from exc


def _as_topic(code: str) -> Topic:
    try:
        return Topic[code]
    except KeyError as exc:
        raise ValueError() from exc


def _serialize_votes_query(query: SearchQuery[Vote]) -> VotesQueryResponseDict:
    response = query.handle()

    return {
        **response,
        "results": [serialize_base_vote(result) for result in response["results"]],
        "facets": response["facets"],
    }


def _serialize_member_votes_query(
    query: SearchQuery[Vote], member_id: int
) -> MemberVotesQueryResponseDict:
    response = query.handle()

    return {
        **response,
        "results": [
            serialize_base_vote_with_member_position(result, member_id)
            for result in response["results"]
        ],
        "facets": response["facets"],
    }


def _load_fragments(vote: Vote, press_release: PressRelease | None) -> Iterable[Fragment]:
    stmt = select(Fragment).where(fragments_for_records([vote, press_release]))
    return Session.execute(stmt).scalars()


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
        authors = []
        if vote.amendment_authors:
            authors = [serialize_amendment_author(author) for author in vote.amendment_authors]
        formatted.append(
            {
                "id": vote.id,
                "is_main": vote.is_main,
                "timestamp": vote.timestamp,
                "description": vote.description,
                "amendment_subject": vote.amendment_subject,
                "amendment_number": vote.amendment_number,
                "amendment_authors": authors,
                "result": vote.result,
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


def _format_links(vote: Vote) -> list[LinkDict]:
    links: list[LinkDict] = []

    if vote.press_release_id:
        links.append(
            {
                "title": "Press release",
                "description": "Press release published by the European Parliament’s Press Service. Press releases often contain more information about the subject of the vote and next steps.",  #  noqa: E501
                "url": press_release_url(vote.press_release_id),
            }
        )

    if vote.reference:
        links.append(
            {
                "title": "Report or resolution",
                "description": "Original text of the report or resolution as tabled. The text may be different from the adopted text if MEPs have adopted amendments.",  #  noqa: E501
                "url": doceo_document_url(vote.reference),
            }
        )

    if vote.texts_adopted_reference:
        links.append(
            {
                "title": "Texts adopted",
                "description": "Texts adopted during the plenary session, including changes from amendments.",  #  noqa: E501
                "url": doceo_texts_adopted_url(vote.texts_adopted_reference),
            }
        )

    if vote.procedure_reference:
        links.append(
            {
                "title": "Legislative Observatory",
                "description": "Find out more about the procedure this vote is part of. This includes information about the current state of the procedure, past and upcoming steps, as well as key players.",  #  noqa: E501
                "url": oeil_procedure_url(vote.procedure_reference),
            }
        )

    return links


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
                "member": serialize_base_member(member, vote.timestamp.date()),
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
