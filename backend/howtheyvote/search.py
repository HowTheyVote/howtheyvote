import enum
import pathlib
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Literal, overload

from structlog import get_logger
from xapian import DB_CREATE_OR_OPEN, Database, SimpleStopper, WritableDatabase

from . import config
from .models import BaseWithId

log = get_logger(__name__)


class AccessType(enum.Enum):
    READ = "READ"
    WRITE = "WRITE"


# By convention, field prefixes in Xapian start with an uppercase X
# See: https://getting-started-with-xapian.readthedocs.io/en/latest/howtos/boolean_filters.html
PREFIX_REFERENCE = "XDR"
PREFIX_PROCEDURE_REFERENCE = "XPR"

# Each document can have a set of values associated with it. Values are similar to DocValues
# in Lucene and stored in a column-oriented way that makes value lookups for many documents
# at a time more efficient. If it should be possible to use certain document fields for
# sorting, custom scoring, aggregations, etc. it makes sense to store them as a value. Each
# value is stored in a numbered slot.
# See: https://getting-started-with-xapian.readthedocs.io/en/latest/concepts/indexing/values.html
SLOT_TIMESTAMP = 0
SLOT_IS_FEATURED = 1

FIELD_TO_SLOT_MAPPING = {
    "timestamp": SLOT_TIMESTAMP,
    "is_featured": SLOT_IS_FEATURED,
}

# Constant WDF (within-document frequency) boost. This can be used to attach extra importance
# to certain parts of a document (such as the title) compared to the rest of the document.
# For example, a factor of 5 means that a single occurence of a term is counted as if it had
# occurred 5 times. Applied at index time (not query time).
# See: https://xapian.org/docs/intro_ir.html#wdp-wdf-ndl-and-wqf
# See: https://trac.xapian.org/wiki/FAQ/ExtraWeight
BOOST_DISPLAY_TITLE = 15
BOOST_EUROVOC_CONCEPTS = 2
BOOST_GEO_AREAS = 2


@overload
@contextmanager
def get_index(
    model_cls: type[BaseWithId],
    access_type: Literal[AccessType.READ] = ...,
) -> Iterator[Database]: ...


@overload
@contextmanager
def get_index(
    model_cls: type[BaseWithId],
    access_type: Literal[AccessType.WRITE],
) -> Iterator[WritableDatabase]: ...


@contextmanager
def get_index(
    model_cls: type[BaseWithId],
    access_type: AccessType = AccessType.READ,
) -> Iterator[Database | WritableDatabase]:
    name = model_cls.__table__.name  # type: ignore
    path = str(pathlib.Path(config.SEARCH_INDEX_DIR).joinpath(name))

    if access_type == AccessType.READ:
        index = Database(path)
    else:
        index = WritableDatabase(path, DB_CREATE_OR_OPEN)

    try:
        yield index
    finally:
        index.close()


def get_stopper() -> SimpleStopper:
    return SimpleStopper(config.SEARCH_STOPWORDS_PATH)


def delete_indexes() -> None:
    """Delete all search indexes."""
    root = pathlib.Path(config.SEARCH_INDEX_DIR)

    for path in root.iterdir():
        if not path.is_dir():
            continue

        log.info("Deleting index", path=path.name)
        shutil.rmtree(path)
