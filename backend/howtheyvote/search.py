import enum
import pathlib
import shutil
from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime, time
from typing import Any, Literal, overload

from structlog import get_logger
from xapian import (
    DB_CREATE_OR_OPEN,
    Database,
    SimpleStopper,
    WritableDatabase,
    sortable_serialise,
)

from . import config
from .models import BaseWithId, Committee, Country

log = get_logger(__name__)


class AccessType(enum.Enum):
    READ = "READ"
    WRITE = "WRITE"


# These are the fields that are used for full-text search.
SEARCH_FIELDS = [
    "display_title",
    "geo_area_labels",
    "eurovoc_concept_labels",
    "rapporteur",
    "press_release",
]


# By convention, field prefixes in Xapian start with an uppercase X
# See: https://getting-started-with-xapian.readthedocs.io/en/latest/howtos/boolean_filters.html
FIELD_TO_PREFIX_MAPPING = {
    "display_title": "XDT",
    "date": "XD",
    "geo_areas": "XGA",
    "geo_area_labels": "XGAL",
    "eurovoc_concept_labels": "XECL",
    "rapporteur": "XRA",
    "responsible_committees": "XRC",
    "reference": "XR",
    "procedure_reference": "XPR",
    "press_release": "XPRR",
    "member_id": "XM",
}


class Type[T](ABC):
    @abstractmethod
    def serialize_value(self, value: T) -> str: ...

    @abstractmethod
    def deserialize_value(self, value: str) -> T: ...

    @abstractmethod
    def get_label(self, value: T) -> str: ...

    def get_short_label(self, value: T) -> str | None:
        return None


class StringType(Type[str]):
    def serialize_value(self, value: str) -> str:
        return value

    def deserialize_value(self, value: str) -> str:
        return value

    def get_label(self, value: str) -> str:
        return value


class IntegerType(Type[int]):
    def serialize_value(self, value: int) -> str:
        return str(value)

    def deserialize_value(self, value: str) -> int:
        return int(value)

    def get_label(self, value: int) -> str:
        return str(value)


class DateType(Type[date]):
    def serialize_value(self, value: date) -> str:
        return value.isoformat()

    def deserialize_value(self, value: str) -> date:
        return date.fromisoformat(value)

    def get_label(self, value: date) -> str:
        return value.isoformat()


class CountryType(Type[Country]):
    def serialize_value(self, value: Country) -> str:
        return value.code

    def deserialize_value(self, value: str) -> Country:
        return Country[value]

    def get_label(self, value: Country) -> str:
        return value.label


class CommitteeType(Type[Committee]):
    def serialize_value(self, value: Committee) -> str:
        return value.code

    def deserialize_value(self, value: str) -> Committee:
        return Committee[value]

    def get_label(self, value: Committee) -> str:
        return value.label

    def get_short_label(self, value: Committee) -> str | None:
        return value.abbreviation


FIELD_TO_TYPE_MAPPING: dict[str, Type[Any]] = {
    "date": DateType(),
    "geo_areas": CountryType(),
    "responsible_committees": CommitteeType(),
    "reference": StringType(),
    "procedure_reference": StringType(),
    "member_id": IntegerType(),
}


def field_to_type(field: str) -> Type[Any]:
    return FIELD_TO_TYPE_MAPPING[field]


PREFIX_TO_FIELD_MAPPING = {v: k for k, v in FIELD_TO_PREFIX_MAPPING.items()}

# Each document can have a set of values associated with it. Values are similar to DocValues
# in Lucene and stored in a column-oriented way that makes value lookups for many documents
# at a time more efficient. If it should be possible to use certain document fields for
# sorting, custom scoring, aggregations, etc. it makes sense to store them as a value. Each
# value is stored in a numbered slot.
# See: https://getting-started-with-xapian.readthedocs.io/en/latest/concepts/indexing/values.html
FIELD_TO_SLOT_MAPPING = {
    "date": 0,
    "has_press_release": 1,
    "geo_areas": 2,
    "responsible_committees": 3,
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


def prefix_to_field(prefix: str) -> str:
    return PREFIX_TO_FIELD_MAPPING[prefix]


def field_to_boost(field: str) -> float:
    return FIELD_TO_BOOST_MAPPING.get(field, 1)


def serialize_value(field: str, value: Any) -> str:
    return field_to_type(field).serialize_value(value)


def deserialize_value(field: str, value: str) -> Any:
    return field_to_type(field).deserialize_value(value)


def boolean_term(field: str, value: Any) -> str:
    prefix = field_to_prefix(field)
    value = serialize_value(field, value)
    return f"{prefix}{value.lower()}"


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


def serialize_sortable_value(value: int | float | date | datetime) -> str:
    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime.combine(value, time(0, 0))

    if isinstance(value, datetime):
        value = value.timestamp()

    return sortable_serialise(value)


LIST_SEPARATOR = b"\x03"


def serialize_list(values: list[str]) -> bytes:
    return LIST_SEPARATOR.join(value.encode("utf-8") for value in values)


def deserialize_list(value: bytes) -> list[str]:
    if not value:
        return []

    return [item.decode("utf-8") for item in value.split(LIST_SEPARATOR)]
