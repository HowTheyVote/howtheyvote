from collections.abc import Iterable, Iterator
from typing import Literal, TypedDict, TypeVar, cast

from sqlalchemy.dialects.sqlite import insert
from structlog import get_logger

from ..db import Session
from ..helpers import chunks
from ..meili import votes_index
from ..models import BaseWithId, Vote

log = get_logger(__name__)

RecordType = TypeVar("RecordType", bound=BaseWithId)


def index_records(
    model_cls: type[RecordType],
    records: Iterator[RecordType],
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

    log.info("Writing aggregated records to database.", count=len(values))

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
    sync: bool = False,
) -> None:
    # At the moment, only votes are indexed in Meilisearch
    if model_cls != Vote:
        return

    votes = cast(Iterable[Vote], records)
    formatted_records = []

    for vote in votes:
        if vote.is_main and vote.display_title:
            formatted_records.append(_serialize_vote(vote))

    if not len(formatted_records):
        log.warning("Skipping indexing to search index as list of records is empty")
        return

    log.info("Writing aggregated records to search index", count=len(formatted_records))

    # `Index.add_documents` requires `list[dict[str, any]]` which is incompatible with
    # the `SerializedVote` typed dict. See https://github.com/python/mypy/issues/4976
    documents = [dict(td) for td in formatted_records]
    task = votes_index.add_documents(documents)

    if sync:
        # This is primarily used in tests
        votes_index.wait_for_task(task.task_uid)


class SerializedVote(TypedDict):
    id: int
    timestamp: float
    display_title: str | None
    reference: str | None
    procedure_reference: str | None
    description: str | None
    is_featured: Literal[0, 1]
    geo_areas: list[str]
    keywords: list[str]


def _serialize_vote(vote: Vote) -> SerializedVote:
    keywords = set()

    for concept in vote.eurovoc_concepts:
        keywords.add(concept.label)
        keywords.update(concept.alt_labels)
        keywords.update(bc.label for bc in concept.broader)

    return {
        "id": vote.id,
        # Meilisearch requires dates to be indexed as a numeric timestamp
        "timestamp": vote.timestamp.timestamp(),
        "display_title": vote.display_title,
        "reference": vote.reference,
        "procedure_reference": vote.procedure_reference,
        "description": vote.description,
        "is_featured": 1 if vote.is_featured else 0,
        "geo_areas": [country.label for country in vote.geo_areas],
        "keywords": list(keywords),
    }
