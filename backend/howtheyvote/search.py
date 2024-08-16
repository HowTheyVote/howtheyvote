import enum
import pathlib
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Literal, overload

from structlog import get_logger
from xapian import DB_CREATE_OR_OPEN, Database, SimpleStopper, WritableDatabase

from . import config
from .data import DATA_DIR
from .models import BaseWithId

log = get_logger(__name__)


class AccessType(enum.Enum):
    READ = "READ"
    WRITE = "WRITE"


PREFIX_REFERENCE = "XDR"
PREFIX_PROCEDURE_REFERENCE = "XPR"

SLOT_TIMESTAMP = 0
SLOT_IS_FEATURED = 1

FIELD_TO_SLOT_MAPPING = {
    "timestamp": SLOT_TIMESTAMP,
    "is_featured": SLOT_IS_FEATURED,
}

BOOST_DISPLAY_TITLE = 15
BOOST_EUROVOC_CONCEPTS = 2
BOOST_GEO_AREAS = 2


@overload
@contextmanager
def get_index(
    model_cls: type[BaseWithId],
    access_type: Literal[AccessType.READ],
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

    if access_type == AccessType.WRITE:
        index = WritableDatabase(path, DB_CREATE_OR_OPEN)
    else:
        index = Database(path)

    try:
        yield index
    finally:
        index.close()


def get_stopper() -> SimpleStopper:
    path = DATA_DIR.joinpath("stopwords.txt")
    return SimpleStopper(str(path))


def delete_indexes() -> None:
    """Delete all search indexes."""
    root = pathlib.Path(config.SEARCH_INDEX_DIR)

    for path in root.iterdir():
        if not path.is_dir():
            continue

        log.info("Deleting index", path=path.name)
        shutil.rmtree(path)
