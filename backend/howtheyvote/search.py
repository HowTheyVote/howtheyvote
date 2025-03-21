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


# These are the fields that are used for full-text search.
SEARCH_FIELDS = [
    "display_title",
    "geo_areas",
    "eurovoc_concepts",
    "rapporteur",
]


# By convention, field prefixes in Xapian start with an uppercase X
# See: https://getting-started-with-xapian.readthedocs.io/en/latest/howtos/boolean_filters.html
FIELD_TO_PREFIX_MAPPING = {
    "display_title": "XDT",
    "geo_areas": "XGA",
    "eurovoc_concepts": "XEC",
    "rapporteur": "XRA",
    "reference": "XR",
    "procedure_reference": "XPR",
}

# Each document can have a set of values associated with it. Values are similar to DocValues
# in Lucene and stored in a column-oriented way that makes value lookups for many documents
# at a time more efficient. If it should be possible to use certain document fields for
# sorting, custom scoring, aggregations, etc. it makes sense to store them as a value. Each
# value is stored in a numbered slot.
# See: https://getting-started-with-xapian.readthedocs.io/en/latest/concepts/indexing/values.html
FIELD_TO_SLOT_MAPPING = {
    "timestamp": 0,
    "has_press_release": 1,
}

# Some document fields are more important than others. The following factors are applied
# at search time if search terms are found in the respective document fields. For example,
# if a search term is found in the `display_title` field, this results in a higher score
# than if it is found in another field.
# See: https://trac.xapian.org/wiki/FAQ/ExtraWeight
FIELD_TO_BOOST_MAPPING = {
    "display_title": 5,
}


def field_to_slot(field: str) -> int:
    return FIELD_TO_SLOT_MAPPING[field]


def field_to_prefix(field: str) -> str:
    return FIELD_TO_PREFIX_MAPPING[field]


def field_to_boost(field: str) -> float:
    return FIELD_TO_BOOST_MAPPING.get(field, 1)


def boolean_term(field: str, value: str | int | bool) -> str:
    prefix = FIELD_TO_PREFIX_MAPPING[field]

    if type(value) is bool:
        # Index bools as integers
        value = int(value)
    elif type(value) is str:
        # Normalize strings
        value = value.lower()

    return f"{prefix}{value}"


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
