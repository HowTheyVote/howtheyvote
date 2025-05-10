import itertools
from collections import defaultdict
from collections.abc import Callable, Collection, Iterator
from typing import Any, TypeVar

from sqlalchemy import select
from structlog import get_logger

from ..db import Session
from ..models import Fragment

log = get_logger(__name__)

GroupKey = str
GroupKeys = Collection[GroupKey] | None


class CompositeRecord:
    """Represents a record merged from one or more `howtheyvote.models.Fragment`s.

    As multiple fragments can specify a value for the same property, property values
    are inherently multi-valued. For example, if a MEP had a mandate for two terms,
    there will be two `howtheyvote.models.Member` fragments specifying `group_memberships`,
    one for each term.

    `CompositeRecord` provides helper methods to access merged record data.
    """

    def __init__(self, group_key: str, data: dict[str, list[Any]]):
        self.group_key = group_key
        """Common group key for the record."""
        self.data = data
        """Merged data from all fragments."""

    def all(self, key: str) -> list[Any]:
        """Get a list of all values for the given key."""
        return self.data.get(key, [])

    def first(self, key: str, default: Any = None) -> Any:
        """Get the first value for the given key."""
        try:
            return self.all(key)[0]
        except IndexError:
            return default

    def chain(self, key: str) -> list[Any]:
        """Chain the values for the given key and return a single list."""
        iterables = self.all(key)
        return list(itertools.chain.from_iterable(iterables))


RecordType = TypeVar("RecordType")
MapFunc = Callable[[CompositeRecord], RecordType]


class Aggregator:
    """Reads `howtheyvote.models.Fragment`s from the database and merges them into records."""

    BUFFER_SIZE = 500

    def __init__(self, model_cls: type):
        self.model_cls = model_cls

    def mapped_records(
        self,
        map_func: MapFunc[RecordType],
        group_keys: GroupKeys = None,
    ) -> Iterator[RecordType]:
        """Returns an iterator over mapped records composed from fragments.

        :param map_func: A function to map each record to a different type. This can
        be used to map generic records to ORM objects.

        :param group_keys: If set, only records for the given group keys are returned.
        """
        for record in self.records(group_keys):
            yield map_func(record)

    def records(self, group_keys: GroupKeys = None) -> Iterator[CompositeRecord]:
        """Returns an iterator over records composed from fragments.

        :param group_keys: If set, only records for the given group keys are returned.
        """
        for group_key, fragments in self._grouped_fragments(group_keys):
            data = defaultdict(list)

            for fragment in fragments:
                for key, value in fragment.data.items():
                    data[key].append(value)

            yield CompositeRecord(group_key, data)

    def _grouped_fragments(
        self, group_keys: GroupKeys = None
    ) -> Iterator[tuple[GroupKey, list[Fragment]]]:
        curr_key: str | None = None
        curr_group: list[Fragment] = []

        for fragment in self._fragments(group_keys):
            if curr_key is None:
                curr_key = fragment.group_key

            if curr_key != fragment.group_key:
                yield curr_key, curr_group
                curr_key = fragment.group_key
                curr_group = []

            curr_group.append(fragment)

        if curr_key and curr_group:
            yield curr_key, curr_group

    def _fragments(self, group_keys: GroupKeys = None) -> Iterator[Fragment]:
        query = (
            select(Fragment)
            .where(Fragment.model == self.model_cls.__name__)
            .order_by(Fragment.group_key)
        )

        if group_keys is not None and len(group_keys) == 0:
            log.warn("Empty list of group keys given")
            return iter([])

        if group_keys:
            query = query.where(Fragment.group_key.in_(group_keys))

        options = {"yield_per": self.BUFFER_SIZE}
        return Session.execute(query, execution_options=options).scalars()
