import datetime
from typing import Annotated, TypedDict

from ..models import (
    Committee,
    Country,
    EurovocConcept,
    Group,
    Member,
    PlenarySession,
    PlenarySessionLocation,
    PlenarySessionStatus,
    Vote,
    VotePosition,
    VoteResult,
)


class ProcedureDict(TypedDict):
    """European Union legislative procedure"""

    title: Annotated[str | None, "Nature restoration"]
    """Title of the legislative proceudre as listed in the Legislative Observatory"""

    reference: Annotated[str, "2022/0195(COD)"]
    """Procedure reference as listed in the Legislative Observatory"""


class GroupDict(TypedDict):
    """Political group in the European Parliament"""

    code: Annotated[str, "EPP"]
    """Unique identifier for the political group"""

    label: Annotated[str, "European People’s Party"]
    """Name of the political group"""

    short_label: Annotated[str | None, "EPP"]
    """Short label or acronym of the political group"""


def serialize_group(group: Group) -> GroupDict:
    return {
        "code": group.code,
        "label": group.label,
        "short_label": group.short_label,
    }


class CountryDict(TypedDict):
    """Country or territory published in the list of countries and territories by the
    Publications Office of the European Union."""

    code: Annotated[str, "FRA"]
    """Country code. If the country or territory is included in the ISO-3166-1 standard,
    this is the 3-letter ISO-3166-1 code. Otherwise this is a custom code [as assigned by
    the Publications Office of the European Union](https://op.europa.eu/en/web/eu-vocabularies/countries-and-territories)."""

    iso_alpha_2: Annotated[str | None, "FR"]
    """If the country or territory is included in the ISO-3166-1 standard, this is the two-
    letter ISO-3166-1 code. Empty if the country is not included in the ISO-3166-1 standard."""

    label: Annotated[str, "France"]
    """Name of the country or territory"""


def serialize_country(country: Country) -> CountryDict:
    return {
        "code": country.code,
        "iso_alpha_2": country.iso_alpha_2,
        "label": country.label,
    }


class CommitteeDict(TypedDict):
    """Committee of the European Parliament"""

    code: Annotated[str, "LIBE"]
    """Unique identifier for the committee"""

    label: Annotated[str, "Committee on Civil Liberties, Justice and Home Affairs"]
    """Name of the committee"""

    abbreviation: Annotated[str | None, "LIBE"]
    """Abbreviation"""


def serialize_committee(committee: Committee) -> CommitteeDict:
    return {
        "code": committee.code,
        "label": committee.label,
        "abbreviation": committee.abbreviation,
    }


class EurovocConceptDict(TypedDict):
    """A concept from the [EuroVoc thesaurus](https://eur-lex.europa.eu/browse/eurovoc.html)"""

    id: Annotated[str, 3030]
    """ID of the concept in the EuroVoc thesaurus"""

    label: Annotated[str, "artificial intelligence"]
    """Primary label of the concept in the EuroVoc thesaurus"""


def serialize_eurovoc_concept(eurovoc_concept: EurovocConcept) -> EurovocConceptDict:
    return {
        "id": eurovoc_concept.id,
        "label": eurovoc_concept.label,
    }


class MemberDict(TypedDict):
    """Member of the European Parliament (MEP)"""

    id: Annotated[int, 118859]
    """MEP ID. This is the same ID that the European Parliament uses on its website at
    https://europarl.europa.eu/meps."""

    first_name: Annotated[str, "Roberta"]
    """First name"""

    last_name: Annotated[str, "METSOLA"]
    """Last name"""

    date_of_birth: Annotated[datetime.date | None, "1979-01-18"]
    """Date of birth"""

    terms: Annotated[list[int], [7, 8, 9]]
    """List of parliamentary terms"""

    country: CountryDict

    group: GroupDict | None
    """The MEP’s political group at the time of the vote"""

    photo_url: str
    """URL to the MEP’s official portrait photo"""

    thumb_url: str
    """URL to a smaller, optimized variant of the official portrait photo"""

    email: str | None
    """Official email address"""

    facebook: str | None
    """URL to the MEP’s Facebook profile"""

    twitter: str | None
    """URL ot the MEP’s Twitter account"""


def serialize_member(
    member: Member, date: datetime.date | datetime.datetime | None = None
) -> MemberDict:
    if not date:
        date = datetime.date.today()

    group = member.group_at(date)

    return {
        "id": member.id,
        "first_name": member.first_name,
        "last_name": member.last_name,
        "date_of_birth": member.date_of_birth,
        "terms": member.terms,
        "country": serialize_country(member.country),
        "group": serialize_group(group) if group else None,
        "photo_url": member.photo_url(),
        "thumb_url": member.photo_url(104),
        "email": member.email,
        "facebook": member.facebook,
        "twitter": member.twitter,
    }


class MemberVoteDict(TypedDict):
    member: MemberDict
    position: VotePosition


class VotePositionCountsDict(TypedDict):
    FOR: int
    AGAINST: int
    ABSTENTION: int
    DID_NOT_VOTE: int


class VoteStatsByGroupDict(TypedDict):
    group: GroupDict
    stats: VotePositionCountsDict


class VoteStatsByCountryDict(TypedDict):
    country: CountryDict
    stats: VotePositionCountsDict


class VoteStatsDict(TypedDict):
    total: VotePositionCountsDict
    """Total number of MEPs by vote position"""

    by_country: list[VoteStatsByCountryDict]
    """Total number of MEPs by country and vote position"""

    by_group: list[VoteStatsByGroupDict]
    """Total number of MEPs by political group and vote position"""


class SourceDict(TypedDict):
    name: str
    """Source name"""

    url: str
    """Source URL"""

    accessed_at: datetime.datetime
    """Date and time when the source was last accessed"""


class RelatedVoteDict(TypedDict):
    id: Annotated[int, 157420]
    """ID as published in the official roll-call vote results"""

    timestamp: Annotated[datetime.datetime, "2023-07-12T12:44:14"]
    """Date and time of the vote"""

    description: Annotated[str | None, "Am 123"]
    """Description of the vote as published in the roll-call vote results"""


class BaseVoteDict(TypedDict):
    id: Annotated[int, 157420]
    """ID as published in the official roll-call vote results"""

    timestamp: Annotated[datetime.datetime, "2023-07-12T12:44:14"]
    """Date and time of the vote"""

    display_title: Annotated[str | None, "Nature restoration"]
    """Title that can be used to refer to the vote. In most cases, this is the title
    published in the roll-call vote results. If the title in the roll-call vote results
    is empty, this falls back to the procedure title."""

    reference: Annotated[str | None, "A9-0220/2023"]
    """Reference to a plenary document such as a report or a resolution"""

    description: Annotated[str | None, "Commission proposal"]
    """Description of the vote as published in the roll-call vote results"""

    geo_areas: list[CountryDict]
    """Countries or territories related to this vote"""

    eurovoc_concepts: list[EurovocConceptDict]
    """Concepts from the [EuroVoc](https://eur-lex.europa.eu/browse/eurovoc.html) thesaurus
    that are related to this vote"""

    responsible_committee: CommitteeDict | None
    """Committee responsible for the legislative procedure"""

    result: VoteResult | None
    """Vote result. This field is only available for votes starting in 2024."""


def serialize_base_vote(vote: Vote) -> BaseVoteDict:
    geo_areas = [serialize_country(geo_area) for geo_area in vote.geo_areas]
    eurovoc_concepts = [serialize_eurovoc_concept(ec) for ec in vote.eurovoc_concepts]
    responsible_committee = (
        serialize_committee(vote.responsible_committee) if vote.responsible_committee else None
    )

    return {
        "id": vote.id,
        "timestamp": vote.timestamp,
        "display_title": vote.display_title,
        "description": vote.description,
        "reference": vote.reference,
        "geo_areas": geo_areas,
        "eurovoc_concepts": eurovoc_concepts,
        "responsible_committee": responsible_committee,
        "result": vote.result,
    }


class VoteDict(BaseVoteDict):
    procedure: ProcedureDict | None
    """Information about the legislative procedure to which this vote belongs"""

    facts: str | None
    """Facts about the vote. Usually an HTML formatted list of 3-4 bullet points extracted
    from press releases published by the European Parliament."""

    sharepic_url: str | None
    """URL to a share picture for this vote."""

    stats: VoteStatsDict
    """Statistics about this vote"""

    member_votes: list[MemberVoteDict]
    """List of MEPs and their vote positions"""

    sources: list[SourceDict]
    """List of official sources for this data record"""

    related: list[RelatedVoteDict]


class PlenarySessionDict(TypedDict):
    id: Annotated[str, "2019-07-02"]

    start_date: Annotated[datetime.date, "2019-07-02"]
    """Start date"""

    end_date: Annotated[datetime.date, "2019-07-04"]
    """End date"""

    status: Annotated[PlenarySessionStatus, "PAST"]
    """Whether this is a past, upcoming or current session"""

    location: Annotated[PlenarySessionLocation | None, "SXB"]
    """Location of the plenary session"""


def serialize_plenary_session(plenary_session: PlenarySession) -> PlenarySessionDict:
    return {
        "id": plenary_session.id,
        "start_date": plenary_session.start_date,
        "end_date": plenary_session.end_date,
        "status": plenary_session.status,
        "location": plenary_session.location,
    }


class QueryResponseDict(TypedDict):
    total: int
    """Total number of results. This is an approximate number and the exact number of search
    results that are returned when paging through all results may be different."""

    page: int
    """Search results page"""

    page_size: int
    """Number of results per page"""

    has_prev: bool
    """Whether there is a previous page of results"""

    has_next: bool
    """Whether there is a next page of results"""


# Using standard inheritance instead of generics as generics are a little
# difficult to represent in OpenAPI specs/JSONSchema
class VotesQueryResponseDict(QueryResponseDict):
    results: list[BaseVoteDict]
    """Votes"""


class PlenarySessionsQueryResponseDict(QueryResponseDict):
    results: list[PlenarySessionDict]
    """Plenary sessions"""


class Statistics(TypedDict):
    votes_total: Annotated[int, 12345]
    """Total number of votes"""

    members_total: Annotated[int, 987]
    """Total number of members"""

    years_total: Annotated[int, 5]
    """Total number of years since start of data collection"""

    last_update_date: datetime.datetime
    """Last data pipeline run time"""
