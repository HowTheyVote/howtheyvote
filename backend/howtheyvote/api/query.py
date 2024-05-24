import copy
import enum
from abc import ABC, abstractmethod
from typing import Any, Generic, Self, TypedDict, TypeVar

from sqlalchemy import desc, func, select
from sqlalchemy.sql import ColumnElement

from ..db import Session
from ..meili import get_index
from ..models import BaseWithId

T = TypeVar("T", bound=BaseWithId)


class Order(enum.Enum):
    ASC = "asc"
    DESC = "desc"


class QueryResponse(TypedDict, Generic[T]):
    total: int
    results: list[T]
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


class Query(ABC, Generic[T]):
    MAX_PAGE_SIZE = 200
    DEFAULT_PAGE_SIZE = 20
    DEFAULT_SORT_FIELD = "id"
    DEFAULT_SORT_ORDER = Order.ASC

    def __init__(self, model: type[T]):
        self.model: type[T] = model
        self._sort: tuple[str, Order | None] | None = None
        self._page: int | None = None
        self._page_size: int | None = None
        self._filters: dict[str, str | bool | int] = {}

    @abstractmethod
    def handle(self) -> QueryResponse[T]:
        raise NotImplementedError

    def copy(self) -> Self:
        return copy.copy(self)

    def page(self, page: int | None) -> Self:
        query = self.copy()
        query._page = page
        return query

    def get_page(self) -> int:
        if self._page is None:
            return 1

        return max(1, self._page)

    def page_size(self, page_size: int | None) -> Self:
        query = self.copy()
        query._page_size = page_size
        return query

    def get_page_size(self) -> int:
        if self._page_size is None:
            return self.DEFAULT_PAGE_SIZE

        return min(self.MAX_PAGE_SIZE, self._page_size)

    def get_limit(self) -> int:
        return self.get_page_size()

    def get_offset(self) -> int:
        page = self.get_page()

        if not page:
            return 0

        return (page - 1) * self.get_limit()

    def sort(self, field: str | None = None, order: Order | None = None) -> Self:
        query = self.copy()

        if not field:
            query._sort = None
        else:
            query._sort = (field, order)

        return query

    def get_sort(self) -> tuple[str, Order] | None:
        if not self._sort:
            return None

        field, order = self._sort
        return (field, order or self.DEFAULT_SORT_ORDER)

    def filter(self, field: str, value: str | bool | int | None) -> Self:
        query = self.copy()

        if value is not None:
            query._filters[field] = value

        return query

    def get_filters(self) -> dict[str, str | bool | int]:
        return self._filters


class DatabaseQuery(Query[T]):
    def __init__(self, model: type[T]):
        super().__init__(model)
        self._where: list[ColumnElement[Any]] = []

    def handle(self) -> QueryResponse[T]:
        page = self.get_page()
        page_size = self.get_page_size()
        limit = self.get_limit()
        offset = self.get_offset()

        query = select(self.model)

        # Apply default sorting if none is specified explicitly
        sort = self.get_sort()
        if not sort:
            sort_field = self.DEFAULT_SORT_FIELD
            sort_order = self.DEFAULT_SORT_ORDER
        else:
            sort_field, sort_order = sort

        # This evaluates to something like `Vote.timestamp`.
        order_expr = getattr(self.model, sort_field)

        if sort_order == Order.DESC:
            order_expr = desc(order_expr)

        query = query.order_by(order_expr)

        for field, value in self.get_filters().items():
            column = getattr(self.model, field)
            query = query.where(column == value)

        for expression in self._where:
            query = query.where(expression)

        total_query = query.with_only_columns(func.count(self.model.id))
        results_query = query.limit(limit).offset(offset)

        results = list(Session.execute(results_query).scalars())
        total = Session.scalar(total_query) or 0

        response: QueryResponse[T] = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_prev": page > 1,
            "has_next": (page * limit) < total,
            "results": results,
        }

        return response

    def where(self, expression: ColumnElement[Any]) -> Self:
        query = self.copy()
        query._where.append(expression)
        return query


class MeilisearchSearchParams(TypedDict):
    limit: int
    offset: int
    attributesToRetrieve: list[str]
    filter: list[str]
    sort: list[str]


class SearchQuery(Query[T]):
    def __init__(self, model: type[T]):
        super().__init__(model)
        self._query: str | None = None

    def handle(self) -> QueryResponse[T]:
        index = get_index(self.model)
        page = self.get_page()
        page_size = self.get_page_size()
        limit = self.get_limit()
        offset = self.get_offset()

        params: MeilisearchSearchParams = {
            # In order to determine if there is a next page, we fetch one additional
            # result from the search index.
            "limit": limit + 1,
            "offset": offset,
            # Retrieve only IDs from search index as everything else is fetched
            # from the database
            "attributesToRetrieve": ["id"],
            "sort": [],
            "filter": [],
        }

        sort = self.get_sort()
        q = self.get_query()

        if sort or not q:
            # Apply default sorting only if none is specified explicitly and
            # no search query is given
            if not sort:
                sort_field = self.DEFAULT_SORT_FIELD
                sort_order = self.DEFAULT_SORT_ORDER
            else:
                sort_field, sort_order = sort

            params["sort"] = [f"{sort_field}:{sort_order.value}"]

        for field, value in self.get_filters().items():
            if isinstance(value, bool):
                # Meilisearch represents booleans as integers
                value = int(value)

            params["filter"].append(f"{field} = {value}")

        res = index.search(q, params)

        # Based on the IDs fetched from the search index, fetch full records
        # from the database
        ids = [hit["id"] for hit in res["hits"]]

        # Remove the extra item fetched only to test if there is a next page
        ids = ids[:limit]

        query = select(self.model).where(self.model.id.in_(ids))
        results = list(Session.execute(query).scalars())

        # Sort in the same order as returned in search response
        results = sorted(results, key=lambda r: ids.index(r.id))

        response: QueryResponse[T] = {
            "total": res["estimatedTotalHits"],
            "page": page,
            "page_size": page_size,
            "has_prev": page > 1,
            "has_next": len(res["hits"]) > limit,
            "results": results,
        }

        return response

    def query(self, query: str | None = None) -> Self:
        copy = self.copy()
        copy._query = query
        return copy

    def get_query(self) -> str:
        return self._query or ""
