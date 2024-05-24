from collections.abc import Collection
from typing import TypeVar

import click

from ..models import BaseWithId, Member, PlenarySession, PressRelease, Vote
from ..store import (
    Aggregator,
    MapFunc,
    index_records,
    map_member,
    map_plenary_session,
    map_press_release,
    map_vote,
)


@click.group()
def aggregate() -> None:
    """Aggregate fragments into the database and the search index."""
    pass


RecordType = TypeVar("RecordType", bound=BaseWithId)


def _aggregate(
    model_cls: type[RecordType],
    map_func: MapFunc[RecordType],
    group_keys: Collection[str] | None,
    chunk_size: int | None = None,
) -> None:
    aggregator = Aggregator(model_cls)

    if group_keys is not None and len(group_keys) == 0:
        group_keys = None

    mapped_records = aggregator.mapped_records(map_func, group_keys)
    index_records(model_cls, mapped_records, chunk_size)


@aggregate.command()
@click.option("--id", "id_", multiple=True)
def members(id_: Collection[str] | None = None) -> None:
    _aggregate(Member, map_member, group_keys=id_)


@aggregate.command()
@click.option("--id", "id_", multiple=True)
def sessions(id_: Collection[str] | None = None) -> None:
    _aggregate(PlenarySession, map_plenary_session, group_keys=id_)


@aggregate.command()
@click.option("--id", "id_", multiple=True)
def votes(id_: Collection[str] | None = None) -> None:
    _aggregate(Vote, map_vote, group_keys=id_, chunk_size=1000)


@aggregate.command()
@click.option("--id", "id_", multiple=True)
def press_releases(id_: Collection[str] | None = None) -> None:
    _aggregate(PressRelease, map_press_release, group_keys=id_)
