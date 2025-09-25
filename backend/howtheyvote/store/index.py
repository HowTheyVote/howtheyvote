from collections.abc import Iterable
from typing import TypeVar, cast

from sqlalchemy.dialects.sqlite import insert
from structlog import get_logger
from xapian import Document, TermGenerator

from ..db import Session
from ..helpers import chunks
from ..models import BaseWithId, Vote
from ..search import (
    AccessType,
    boolean_term,
    field_to_prefix,
    field_to_slot,
    get_index,
    get_stopper,
    serialize_list,
    serialize_value,
)

log = get_logger(__name__)

RecordType = TypeVar("RecordType", bound=BaseWithId)


def index_records(
    model_cls: type[RecordType],
    records: Iterable[RecordType],
    chunk_size: int | None = None,
) -> None:
    """Writes aggregated records to the database and search backend."""
    records = _filter_records(records)

    if chunk_size:
        for i, chunk in enumerate(chunks(records, size=chunk_size), start=1):
            log.info(
                "Indexing records",
                model=model_cls.__name__,
                chunk=i,
                chunk_size=chunk_size,
            )
            chunk_records = list(chunk)
            index_db(model_cls, chunk_records)
            index_search(model_cls, chunk_records)
    else:
        all_records = list(records)
        index_db(model_cls, all_records)
        index_search(model_cls, all_records)


def index_db(model_cls: type[RecordType], records: Iterable[RecordType]) -> None:
    values = []

    for record in records:
        values.append(
            {column.name: getattr(record, column.name) for column in record.__table__.columns}
        )

    if not len(values):
        log.warning("Skipping indexing to database as list of records is empty")
        return

    log.info(
        "Writing aggregated records to database.",
        model=model_cls.__name__,
        count=len(values),
    )

    stmt = insert(model_cls).values(values)
    stmt = stmt.on_conflict_do_update(
        index_elements=[model_cls.id],
        set_=dict(stmt.excluded),
    )

    Session.execute(stmt)
    Session.commit()


def index_search(
    model_cls: type[RecordType],
    records: Iterable[RecordType],
) -> None:
    # At the moment, only votes are searchable
    if model_cls != Vote:
        return

    votes = cast(Iterable[Vote], records)
    filtered_votes = [vote for vote in votes if vote.is_main and vote.display_title]

    if not filtered_votes:
        log.warning("Skipping indexing to search index as list of records is empty")
        return

    log.info("Indexing aggregated records", count=len(filtered_votes))

    with get_index(Vote, AccessType.WRITE) as index:
        generator = TermGenerator()
        generator.set_database(index)
        generator.set_stopper(get_stopper())
        generator.set_stopper_strategy(TermGenerator.STOP_ALL)

        # Automatically add words from indexed documents to spelling dictionary to
        # enable spelling correction
        generator.set_flags(TermGenerator.FLAG_SPELLING)

        for vote in filtered_votes:
            doc = _serialize_vote(vote, generator)
            index.replace_document(int(vote.id), doc)


def _filter_records(records: Iterable[RecordType]) -> Iterable[RecordType]:  #  noqa: UP047
    # This is a bit hacky: If we’ve successfully scraped a VOT list for a given day,
    # but couldn’t scrape the RCV list for the same day, we’d end up indexing incomplete
    # vote records without the member votes
    for record in records:
        if isinstance(record, Vote) and not record.member_votes:
            log.warning(
                "Skipping indexing of vote record without member votes", vote_id=record.id
            )
            continue
        yield record


def _serialize_vote(vote: Vote, generator: TermGenerator) -> Document:
    doc = Document()
    generator.set_document(doc)

    if not vote.display_title:
        raise ValueError("Cannot index vote without `display_title`.")

    generator.index_text(vote.display_title, 1, field_to_prefix("display_title"))

    # Calling this method between indexing of different fields prevents
    # searches matching terms from different fields, (e.g. last term of
    # the title and first term of the following field).
    generator.increase_termpos()

    # Index EuroVoc concept labels for full-text search
    for concept in vote.eurovoc_concepts:
        for term in set([concept.label, *concept.alt_labels]):
            generator.index_text(term, 1, field_to_prefix("eurovoc_concept_labels"))
            generator.increase_termpos()

    # Index geographic area labels for full-text search
    for geo_area in vote.geo_areas:
        generator.index_text(geo_area.label, 1, field_to_prefix("geo_area_labels"))
        generator.increase_termpos()

    # Index rapporteur name
    if vote.rapporteur:
        generator.index_text(vote.rapporteur, 1, field_to_prefix("rapporteur"))

    # Store date in slot for ranking and range filters
    date = serialize_value(vote.date)
    doc.add_value(field_to_slot("date"), date)

    # Also store date as boolean term for eqaulity filters
    term = boolean_term("date", vote.date)
    doc.add_boolean_term(term)

    # Store press release in slot for ranking
    has_press_release = serialize_value(int(vote.press_release is not None))
    doc.add_value(field_to_slot("has_press_release"), has_press_release)

    # Store categorical values as boolean terms for filtering.
    if vote.reference:
        term = boolean_term("reference", vote.reference)
        doc.add_boolean_term(term)

    if vote.procedure_reference:
        term = boolean_term("procedure_reference", vote.procedure_reference)
        doc.add_boolean_term(term)

    for geo_area in vote.geo_areas:
        term = boolean_term("geo_areas", geo_area)
        doc.add_boolean_term(term)

    for committee in vote.responsible_committees:
        term = boolean_term("responsible_committees", committee)
        doc.add_boolean_term(term)

    # Store categorical values in slots to compute facets. Slots can only store a single
    # value, so we have to serialize the list first.
    # https://lists.tartarus.org/pipermail/xapian-discuss/2011-June/008264.html
    value = serialize_list([geo_area.code for geo_area in vote.geo_areas])
    doc.add_value(field_to_slot("geo_areas"), value)

    value = serialize_list([committee.code for committee in vote.responsible_committees])
    doc.add_value(field_to_slot("responsible_committees"), value)

    return doc
