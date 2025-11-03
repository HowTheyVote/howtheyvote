import datetime

from ..models import (
    Committee,
    Country,
    Member,
    PlenarySession,
    PressRelease,
    ProcedureStage,
    Vote,
    VoteResult,
    deserialize_amendment_author,
    deserialize_group_membership,
    deserialize_member_vote,
)
from ..models.eurovoc import EurovocConcept
from ..models.oeil import OEILSubject
from .aggregator import CompositeRecord


def map_member(record: CompositeRecord) -> Member:
    """Maps a `howtheyvote.store.CompositeRecord` to a `howtheyvote.models.Member` object."""
    return Member(
        id=record.group_key,
        first_name=record.get("first_name"),
        last_name=record.get("last_name"),
        country=record.get("country", type=lambda x: Country[x]),
        date_of_birth=record.get("date_of_birth", type=datetime.date.fromisoformat),
        terms=record.getlist("term"),
        group_memberships=record.chain("group_memberships", type=deserialize_group_membership),
        email=record.get("email"),
        facebook=record.get("facebook"),
        twitter=record.get("twitter"),
    )


def map_plenary_session(record: CompositeRecord) -> PlenarySession:
    """Maps a `howtheyvote.store.CompositeRecord` to a `howtheyvote.models.PlenarySession`
    object."""
    return PlenarySession(
        id=record.group_key,
        term=record.get("term"),
        start_date=record.get("start_date", type=datetime.date.fromisoformat),
        end_date=record.get("end_date", type=datetime.date.fromisoformat),
        location=record.get("location"),
    )


def map_vote(record: CompositeRecord) -> Vote:
    """Maps a `howtheyvote.store.CompositeRecord` to a `howtheyvote.models.Vote` object."""
    if "amendment_authors" in record:
        amendment_authors = record.chain(
            "amendment_authors", type=deserialize_amendment_author
        )
    else:
        amendment_authors = None

    return Vote(
        id=record.group_key,
        timestamp=record.get("timestamp", type=datetime.datetime.fromisoformat),
        term=record.get("term"),
        order=record.get("order"),
        title=record.get("title_en") or record.get("title"),
        dlv_title=record.get("dlv_title"),
        description=record.get("description_en") or record.get("description"),
        reference=record.get("reference"),
        texts_adopted_reference=record.get("texts_adopted_reference"),
        rapporteur=record.get("rapporteur"),
        procedure_title=record.get("procedure_title"),
        procedure_reference=record.get("procedure_reference"),
        procedure_stage=record.get(
            key="procedure_stage",
            type=lambda x: ProcedureStage[x] if x else None,
        ),
        amendment_subject=record.get("amendment_subject"),
        amendment_number=record.get("amendment_number"),
        amendment_authors=amendment_authors,
        is_main=record.get("is_main") or False,
        group_key=record.get("group_key"),
        result=record.get(
            key="result",
            type=lambda x: VoteResult[x] if x else None,
        ),
        member_votes=record.chain(
            key="member_votes",
            type=deserialize_member_vote,
        ),
        geo_areas=record.chain(
            key="geo_areas",
            type=lambda x: Country[x],
            unique=True,
        ),
        eurovoc_concepts=record.chain(
            key="eurovoc_concepts",
            type=lambda x: EurovocConcept[x],
            unique=True,
        ),
        oeil_subjects=record.chain(
            key="oeil_subjects",
            type=lambda x: OEILSubject[x],
            unique=True,
        ),
        responsible_committees=record.chain(
            key="responsible_committees",
            type=lambda x: Committee[x],
            unique=True,
        ),
        press_release_id=record.get("press_release"),
        oeil_summary_id=record.get("oeil_summary_id"),
    )


def map_press_release(record: CompositeRecord) -> PressRelease:
    return PressRelease(
        id=record.group_key,
        term=record.get("term"),
        title=record.get("title"),
        published_at=record.get("published_at", type=datetime.datetime.fromisoformat),
        references=record.chain("reference"),
        procedure_references=record.chain("procedure_reference"),
        facts=record.get("facts"),
        text=record.get("text"),
        position_counts=record.get("position_counts"),
    )
