from collections.abc import Iterable
from typing import TypeVar, cast

from sqlalchemy.dialects.sqlite import insert
from structlog import get_logger
from xapian import Document, TermGenerator, sortable_serialise

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
)

log = get_logger(__name__)

RecordType = TypeVar("RecordType", bound=BaseWithId)


def index_records(
    model_cls: type[RecordType],
    records: Iterable[RecordType],
    chunk_size: int | None = None,
) -> None:
    """Writes aggregated records to the database and search backend."""
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

    # Index EuroVoc concepts for full-text search
    for concept in vote.eurovoc_concepts:
        for term in set([concept.label, *concept.alt_labels]):
            generator.index_text(term, 1, field_to_prefix("eurovoc_concepts"))
            generator.increase_termpos()

    # Index geographic areas for full-text search
    for geo_area in vote.geo_areas:
        generator.index_text(geo_area.label, 1, field_to_prefix("geo_areas"))
        generator.increase_termpos()

    # Index rapporteur name
    if vote.rapporteur:
        generator.index_text(vote.rapporteur, 1, field_to_prefix("rapporteur"))

    # Store timestamp and press release as sortable values for ranking
    timestamp = sortable_serialise(vote.timestamp.timestamp())
    doc.add_value(field_to_slot("timestamp"), timestamp)

    has_press_release = sortable_serialise(int(vote.press_release is not None))
    doc.add_value(field_to_slot("has_press_release"), has_press_release)

    # Store document and procedure references as boolean terms. Boolean terms
    # aren’t searchable, but can be used for filtering.
    if vote.reference:
        term = boolean_term("reference", vote.reference)
        doc.add_boolean_term(term)

    if vote.procedure_reference:
        term = boolean_term("procedure_reference", vote.procedure_reference)
        doc.add_boolean_term(term)

    return doc
