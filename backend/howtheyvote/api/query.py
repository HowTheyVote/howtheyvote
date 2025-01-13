import copy
import datetime
import enum
from abc import ABC, abstractmethod
from typing import Any, Generic, Self, TypedDict, TypeVar

from sqlalchemy import desc, func, select
from sqlalchemy.sql import ColumnElement
from xapian import (
    BM25Weight,
    Database,
    Enquire,
    QueryParser,
    ValuePostingSource,
    ValueWeightPostingSource,
    Weight,
    sortable_unserialise,
)
from xapian import (
    Query as XapianQuery,
)

from ..db import Session
from ..models import BaseWithId
from ..search import (
    FIELD_TO_SLOT_MAPPING,
    SLOT_IS_FEATURED,
    SLOT_TIMESTAMP,
    boolean_term,
    get_index,
    get_stopper,
)

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
    DEFAULT_SORT_FIELD = "timestamp"
    DEFAULT_SORT_ORDER = Order.DESC

    def __init__(self, model: type[T]):
        self.model: type[T] = model
        self._sort: tuple[str, Order] | None = None
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

        if not order:
            order = self.DEFAULT_SORT_ORDER

        if not field:
            query._sort = None
        else:
            query._sort = (field, order)

        return query

    def get_sort(self) -> tuple[str, Order] | None:
        if not self._sort:
            return None

        return self._sort

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


class ValueDecayWeightPostingSource(ValuePostingSource):
    """A posting source that returns a weight that decreases the larger the difference between
    a given constant origin and a document value is. If the document value equals the given
    origin, the posting source returns a weight of 1. The weight decreases linearly until the
    maximum difference is reached, at which point the posting source returns a weight of 0.

    For example, this can be used to boost recent documents by using the current time as the
    origin.

    In order to adjust the range of the returned weight, combine this with a OP_SCALE_WEIGHT
    query. For example, to assign a weight between 0 and 0.5, use a scaling factor of 0.5.

    See: https://getting-started-with-xapian.readthedocs.io/en/latest/advanced/postingsource.html
    """

    def set_max_diff(self, max_diff: float) -> None:
        self.max_diff = max_diff

    def set_origin(self, origin: float) -> None:
        self.origin = origin

    def get_weight(self) -> float:
        value = sortable_unserialise(self.get_value())
        diff = self.origin - value
        weight = 1 - min(1, diff / self.max_diff)

        return weight


class SearchQuery(Query[T]):
    BOOST_FEATURED = 0.075
    """Constant weight added for featured votes."""

    BOOST_PHRASE = 0.1
    """Scaling factor for the phrase subquery. Every user-provided search query is also
    converted to a phrase query to slightly boost votes matching the search query exactly."""

    BOOST_AGE = 0.25
    """Maximum weight added for recent votes. If a vote’s timestamp equals the current time
    this weight is added. The weight decreases linearly with a vote’s age up to
    `AGE_DECAY_DAYS`. For details, see `ValueDecayWeightPostingSource`."""

    AGE_DECAY_DAYS = 365
    """Maximum vote age in days. Older votes aren't boosted."""

    def __init__(self, model: type[T]):
        super().__init__(model)
        self._query: str | None = None

    def handle(self) -> QueryResponse[T]:
        page = self.get_page()
        page_size = self.get_page_size()
        limit = self.get_limit()
        offset = self.get_offset()

        with get_index(self.model) as index:
            query = self._xapian_query(index)
            enquire = Enquire(index)
            enquire.set_query(query)
            enquire.set_weighting_scheme(self._xapian_bm25_weight())

            sort = self.get_sort()
            if sort:
                field, order = sort

                # Fields need to be stored as values in order to be used for sorting
                slot = FIELD_TO_SLOT_MAPPING.get(field)

                reverse = order == Order.DESC
            else:
                slot = None

            if slot is not None:
                enquire.set_sort_by_value(slot, reverse)
            else:
                enquire.set_sort_by_relevance_then_value(SLOT_TIMESTAMP, False)

            # Fetch one extra result to check if there is a next page
            mset = enquire.get_mset(offset, limit + 1)

        # Based on the IDs fetched from the search index, fetch full records
        # from the database
        ids = [int(match.docid) for match in mset]

        # Remove the extra item fetched only to test if there is a next page
        ids = ids[:limit]

        db_query = select(self.model).where(self.model.id.in_(ids))
        results = list(Session.execute(db_query).scalars())

        # Sort in the same order as returned in search response
        results = sorted(results, key=lambda r: ids.index(int(r.id)))

        response: QueryResponse[T] = {
            "total": mset.get_matches_estimated(),
            "page": page,
            "page_size": page_size,
            "has_prev": page > 1,
            "has_next": mset.size() > limit,
            "results": results,
        }

        return response

    def query(self, query: str | None = None) -> Self:
        copy = self.copy()
        copy._query = query
        return copy

    def get_query(self) -> str:
        return self._query or ""

    def _xapian_query_parser(self, index: Database) -> QueryParser:
        parser = QueryParser()
        parser.set_stopper(get_stopper())
        parser.set_database(index)

        return parser

    def _xapian_query(self, index: Database) -> XapianQuery:
        parser = self._xapian_query_parser(index)
        query = parser.parse_query(self.get_query())

        if query.empty():
            query = XapianQuery.MatchAll
        else:
            query = XapianQuery(
                XapianQuery.OP_AND_MAYBE,
                query,
                self._xapian_featured_subquery(),
            )

            query = XapianQuery(
                XapianQuery.OP_AND_MAYBE,
                query,
                self._xapian_age_subquery(),
            )

            query = XapianQuery(
                XapianQuery.OP_AND_MAYBE,
                query,
                self._xapian_phrase_subquery(index),
            )

        for field, value in self.get_filters().items():
            # Fields have to be indexed as boolean terms to be used as filters
            term = boolean_term(field, value)
            query = XapianQuery(XapianQuery.OP_FILTER, query, XapianQuery(term))

        return query

    def _xapian_phrase_subquery(self, index: Database) -> XapianQuery:
        # This is a phrase subquery, i.e. it matches documents that contain the terms of the
        # search query in the original order. It's used to boost phrase matches even if
        # a user hasn't explicitly specified a phrase query.
        parser = self._xapian_query_parser(index)
        parser.set_default_op(XapianQuery.OP_PHRASE)
        query = parser.parse_query(self.get_query())

        return XapianQuery(
            XapianQuery.OP_SCALE_WEIGHT,
            query,
            self.BOOST_PHRASE,
        )

    def _xapian_featured_subquery(self) -> XapianQuery:
        # This subquery assigns a constant weight to featured votes and 0 otherwise.
        return XapianQuery(
            XapianQuery.OP_SCALE_WEIGHT,
            XapianQuery(ValueWeightPostingSource(SLOT_IS_FEATURED)),
            self.BOOST_FEATURED,
        )

    def _xapian_age_subquery(self) -> XapianQuery:
        # This subquery assigns a decreasing weight based on age, i.e. recent votes get a
        # higher weight.
        now = datetime.datetime.now().timestamp()
        max_diff = datetime.timedelta(days=self.AGE_DECAY_DAYS).total_seconds()

        age_source = ValueDecayWeightPostingSource(SLOT_TIMESTAMP)
        age_source.set_max_diff(max_diff)
        age_source.set_origin(now)

        return XapianQuery(
            XapianQuery.OP_SCALE_WEIGHT,
            XapianQuery(age_source),
            self.BOOST_AGE,
        )

    def _xapian_bm25_weight(self) -> Weight:
        # This parameter controls document length normalization. As we currently index mostly
        # short vote titles and a few keywords, we set b=0 to disable normalization. We do
        # not want a vote to score higher just because its title is shorter. If that changes
        # (and we start indexing longer documents), we should reconsider this.
        b = 0  # Xapian default: 0.5

        # The following BM25 parameters are Xapian’s defaults.
        # See: https://xapian.org/docs/apidoc/html/classXapian_1_1BM25Weight.html
        k1 = 1
        k2 = 0
        k3 = 1
        min_normlen = 0.5

        return BM25Weight(k1, k2, k3, b, min_normlen)
