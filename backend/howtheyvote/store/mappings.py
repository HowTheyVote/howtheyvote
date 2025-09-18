import datetime

from ..models import (
    Committee,
    Country,
    Member,
    PlenarySession,
    PressRelease,
    ProcedureStage,
    Vote,
    VoteGroup,
    VoteResult,
    deserialize_group_membership,
    deserialize_member_vote,
)
from ..models.eurovoc import EurovocConcept
from ..models.oeil import OEILSubject
from .aggregator import CompositeRecord


def map_member(record: CompositeRecord) -> Member:
    """Maps a `howtheyvote.store.CompositeRecord` to a `howtheyvote.models.Member` object."""
    country = record.first("country")
    country = Country[country] if country else None

    date_of_birth = record.first("date_of_birth")
    if date_of_birth:
        date_of_birth = datetime.date.fromisoformat(date_of_birth)

    group_memberships = [
        deserialize_group_membership(gm) for gm in record.chain("group_memberships")
    ]

    return Member(
        id=record.group_key,
        first_name=record.first("first_name"),
        last_name=record.first("last_name"),
        country=country,
        date_of_birth=date_of_birth,
        terms=record.all("term"),
        group_memberships=group_memberships,
        email=record.first("email"),
        facebook=record.first("facebook"),
        twitter=record.first("twitter"),
    )


def map_plenary_session(record: CompositeRecord) -> PlenarySession:
    """Maps a `howtheyvote.store.CompositeRecord` to a `howtheyvote.models.PlenarySession`
    object."""

    return PlenarySession(
        id=record.group_key,
        term=record.first("term"),
        start_date=datetime.date.fromisoformat(record.first("start_date")),
        end_date=datetime.date.fromisoformat(record.first("end_date")),
        location=record.first("location"),
    )


def map_vote(record: CompositeRecord) -> Vote:
    """Maps a `howtheyvote.store.CompositeRecord` to a `howtheyvote.models.Vote` object."""
    member_votes = [deserialize_member_vote(mv) for mv in record.first("member_votes")]
    geo_areas = {Country[code] for code in record.chain("geo_areas")}
    eurovoc_concepts = {EurovocConcept[id_] for id_ in record.chain("eurovoc_concepts")}
    oeil_subjects = {OEILSubject[code] for code in record.chain("oeil_subjects")}
    responsible_committees = {
        Committee[code] for code in record.chain("responsible_committees")
    }
    result = VoteResult[record.first("result")] if record.first("result") else None
    procedure_stage = (
        ProcedureStage[record.first("procedure_stage")]
        if record.first("procedure_stage")
        else None
    )

    press_release = record.first("press_release")

    return Vote(
        id=record.group_key,
        timestamp=datetime.datetime.fromisoformat(record.first("timestamp")),
        term=record.first("term"),
        order=record.first("order"),
        title=record.first("title_en") or record.first("title"),
        dlv_title=record.first("dlv_title"),
        description=record.first("description_en") or record.first("description"),
        reference=record.first("reference"),
        texts_adopted_reference=record.first("texts_adopted_reference"),
        rapporteur=record.first("rapporteur"),
        procedure_title=record.first("procedure_title"),
        procedure_reference=record.first("procedure_reference"),
        procedure_stage=procedure_stage,
        is_main=record.first("is_main") or False,
        group_key=record.first("group_key"),
        result=result,
        member_votes=member_votes,
        geo_areas=geo_areas,
        eurovoc_concepts=eurovoc_concepts,
        oeil_subjects=oeil_subjects,
        responsible_committees=responsible_committees,
        press_release=press_release,
    )


def map_vote_group(record: CompositeRecord) -> VoteGroup:
    date = record.first("date")

    if date:
        date = datetime.date.fromisoformat(date)

    return VoteGroup(
        id=record.group_key,
        date=date,
    )


def map_press_release(record: CompositeRecord) -> PressRelease:
    published_at = record.first("published_at")

    if published_at:
        published_at = datetime.datetime.fromisoformat(published_at)

    return PressRelease(
        id=record.group_key,
        term=record.first("term"),
        title=record.first("title"),
        published_at=published_at,
        references=record.chain("reference"),
        procedure_references=record.chain("procedure_reference"),
        facts=record.first("facts"),
        text=record.first("text"),
        position_counts=record.first("position_counts"),
    )
