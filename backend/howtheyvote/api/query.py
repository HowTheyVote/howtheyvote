import copy
import datetime
import enum
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Literal, Self, TypedDict

from sqlalchemy import and_, asc, desc, func, select, true
from sqlalchemy.sql import ColumnElement
from xapian import (
    BM25Weight,
    Database,
    Document,
    Enquire,
    MatchSpy,
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
from ..models.types import ListType
from ..search import (
    SEARCH_FIELDS,
    boolean_term,
    field_to_boost,
    field_to_prefix,
    field_to_slot,
    get_index,
    get_stopper,
    serialize_value,
    unserialize_list,
)


class Order(enum.Enum):
    ASC = "asc"
    DESC = "desc"


class FilterOperator(enum.Enum):
    EQ = "="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    IN = "in"


FilterOperatorSymbol = Literal["=", ">", ">=", "<", "<=", "in"]
Filters = dict[tuple[str, FilterOperator], Any]


class QueryResponse[T: BaseWithId](TypedDict):
    total: int
    results: list[T]
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


class FacetOption(TypedDict):
    value: str
    count: int


class Facet(TypedDict):
    field: str
    options: list[FacetOption]


class QueryResponseWithFacets[T: BaseWithId](QueryResponse[T]):
    facets: list[Facet]


class Query[T: BaseWithId](ABC):
    MAX_PAGE_SIZE = 200
    DEFAULT_PAGE_SIZE = 20
    DEFAULT_SORT_FIELD = "date"
    DEFAULT_SORT_ORDER = Order.DESC

    def __init__(self, model: type[T]):
        self.model: type[T] = model
        self._sort: tuple[str, Order] | None = None
        self._page: int | None = None
        self._page_size: int | None = None
        self._filters: Filters = {}
        self._facets: list[str] = []

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

    # TODO Figure out if there's a type-safe way to ensure that `field` is valid
    # for the given model and `value` has the respective type.
    def filter(self, field: str, op: FilterOperatorSymbol, value: Any) -> Self:
        query = self.copy()

        if value is not None:
            query._filters[(field, FilterOperator(op))] = value

        return query

    def get_filters(self) -> Filters:
        return self._filters

    def facet(self, field: str) -> Self:
        copy = self.copy()
        copy._facets.append(field)
        return copy

    def get_facets(self) -> list[str]:
        return self._facets


class DatabaseQuery[T: BaseWithId](Query[T]):
    def __init__(self, model: type[T]):
        super().__init__(model)
        self._where: list[ColumnElement[bool]] = []

    def where(self, expression: ColumnElement[bool]) -> Self:
        query = self.copy()
        query._where.append(expression)
        return query

    def handle(self) -> QueryResponse[T]:
        page = self.get_page()
        page_size = self.get_page_size()
        limit = self.get_limit()
        offset = self.get_offset()

        query = (
            select(self.model)
            .order_by(self._order_expr())
            .where(self._filters_expr())
            .where(*self._where)
        )

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

    def _order_expr(self) -> ColumnElement[Any]:
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
            return desc(order_expr)
        else:
            return asc(order_expr)

    def _filters_expr(self) -> ColumnElement[bool]:
        conditions = []

        for (field, op), value in self.get_filters().items():
            column = getattr(self.model, field)

            if op == FilterOperator.EQ:
                if isinstance(column.type, ListType):
                    conditions.append(column.contains(value))
                else:
                    conditions.append(column == value)
            elif op == FilterOperator.IN:
                if isinstance(column.type, ListType):
                    conditions.append(column.overlap(value))
                else:
                    conditions.append(column.in_(value))
            elif op == FilterOperator.GT:
                conditions.append(column > value)
            elif op == FilterOperator.GE:
                conditions.append(column >= value)
            elif op == FilterOperator.LT:
                conditions.append(column < value)
            elif op == FilterOperator.LE:
                conditions.append(column <= value)

        if not conditions:
            return true()

        return and_(*conditions)


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


class MultiValueCountMatchSpy(MatchSpy):
    """Match spies are called while Xapian matches documents against the query. They can
    be used to compute aggregates of the result set. Xapian includes a `ValueCountMatchSpy`
    which can be used to compute the number of documents per unique slot value. Natively,
    Xapian only supports a single value per slot, but we have many cases where we need to
    store multiple values in a single slot (for example geographic areas). To work aorund
    this, we serialize lists of values during indexing, and unserialize it when the match
    spy is called."""

    def __init__(self, slot: int):
        super().__init__()
        self.slot = slot
        self.counts: dict[str, int] = defaultdict(int)

    def __call__(self, doc: Document, _weight: float) -> None:
        for term in unserialize_list(doc.get_value(self.slot)):
            self.counts[term] += 1


class SearchQuery[T: BaseWithId](Query[T]):
    BOOST_FEATURED = 0.075
    """Constant weight added for featured votes."""

    BOOST_AGE = 0.25
    """Maximum weight added for recent votes. If a vote’s timestamp equals the current time
    this weight is added. The weight decreases linearly with a vote’s age up to
    `AGE_DECAY_DAYS`. For details, see `ValueDecayWeightPostingSource`."""

    AGE_DECAY_DAYS = 365
    """Maximum vote age in days. Older votes aren't boosted."""

    def __init__(self, model: type[T]):
        super().__init__(model)
        self._query: str | None = None
        self._facets: list[str] = []

    def handle(self) -> QueryResponseWithFacets[T]:
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
                # Use strict sorting if specified explicitly
                field, order = sort
                slot = field_to_slot(field)
                reverse = order == Order.DESC
                enquire.set_sort_by_value(slot, reverse)
            else:
                # Otherwise sort by relevance first and only use default sort params
                # if two documents have the same relevance score
                slot = field_to_slot(self.DEFAULT_SORT_FIELD)
                reverse = self.DEFAULT_SORT_ORDER == Order.DESC
                enquire.set_sort_by_relevance_then_value(slot, reverse)

            # Add spys to compute facets
            # https://getting-started-with-xapian.readthedocs.io/en/latest/howtos/facets.html#querying
            spies = {}

            for field in self.get_facets():
                spies[field] = MultiValueCountMatchSpy(field_to_slot(field))
                enquire.add_matchspy(spies[field])

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

        # Format facets
        facets: list[Facet] = []

        for field, spy in spies.items():
            options: list[FacetOption] = [
                {"value": term, "count": count} for term, count in spy.counts.items()
            ]

            options.sort(
                key=lambda option: option["count"],
                reverse=True,
            )

            facets.append(
                {
                    "field": field,
                    "options": options,
                }
            )

        response: QueryResponseWithFacets[T] = {
            "total": mset.get_matches_estimated(),
            "page": page,
            "page_size": page_size,
            "has_prev": page > 1,
            "has_next": mset.size() > limit,
            "results": results,
            "facets": facets,
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
        query = self._xapian_main_query(index)

        if query.empty():
            query = XapianQuery.MatchAll
        else:
            query = XapianQuery(
                XapianQuery.OP_AND_MAYBE,
                query,
                self._xapian_press_release_subquery(),
            )

            query = XapianQuery(
                XapianQuery.OP_AND_MAYBE,
                query,
                self._xapian_age_subquery(),
            )

        query = XapianQuery(XapianQuery.OP_FILTER, query, self._xapian_filters_subquery())

        return query

    def _xapian_main_query(self, index: Database) -> XapianQuery:
        # This subquery contains multiple other queries matching terms in different
        # fields and assigning different boost factors depending on the field. For
        # example, searching for "ukraine" would result in a subquery for this term
        # for the `display_title` field with a boost factor of 15, another subquery
        # for the `geo_areas` field with a boost factor of 2, etc. This means that
        # search terms can occur in any of these fields, but if they occur in certain
        # fields that leads to a higher result score.
        parser = self._xapian_query_parser(index)
        query = XapianQuery.MatchNothing

        for field in SEARCH_FIELDS:
            subquery = XapianQuery(
                XapianQuery.OP_SCALE_WEIGHT,
                parser.parse_query(
                    self.get_query(),
                    QueryParser.FLAG_BOOLEAN | QueryParser.FLAG_PHRASE,
                    field_to_prefix(field),
                ),
                field_to_boost(field),
            )

            query = XapianQuery(
                XapianQuery.OP_OR,
                query,
                subquery,
            )

        return query

    def _xapian_press_release_subquery(self) -> XapianQuery:
        # This subquery assigns a constant weight to votes with a press release and
        # 0 otherwise.
        return XapianQuery(
            XapianQuery.OP_SCALE_WEIGHT,
            XapianQuery(ValueWeightPostingSource(field_to_slot("has_press_release"))),
            self.BOOST_FEATURED,
        )

    def _xapian_age_subquery(self) -> XapianQuery:
        # This subquery assigns a decreasing weight based on age, i.e. recent votes get a
        # higher weight.
        now = datetime.datetime.now().timestamp()
        max_diff = datetime.timedelta(days=self.AGE_DECAY_DAYS).total_seconds()

        age_source = ValueDecayWeightPostingSource(field_to_slot("date"))
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

        # This parameter controls the impact of within-document frequency (WDF). Right now, we
        # only index vote titles and some keywords, all very short texts. In most cases, it
        # doesn’t make a difference if a search term occurs one or multiple times in the title,
        # and we wouldn’t want votes to be ranked differently just because of this. Setting k=0
        # means that WDF does not affect scores. When we start indexing longer texts (such as
        # vote summaries), we should reconsider this.
        k1 = 0

        # The following BM25 parameters are Xapian’s defaults.
        # See: https://xapian.org/docs/apidoc/html/classXapian_1_1BM25Weight.html
        k2 = 0
        k3 = 1
        min_normlen = 0.5

        return BM25Weight(k1, k2, k3, b, min_normlen)

    def _xapian_filters_subquery(self) -> XapianQuery:
        subqueries = []

        for (field, op), value in self.get_filters().items():
            # Fields have to be indexed as boolean terms to be used with equality filters
            # and in slots to be used with greater/less than filters
            if op == FilterOperator.EQ:
                subqueries.append(self._xapian_filter_eq_subquery(field, value))
            elif op == FilterOperator.IN:
                subqueries.append(self._xapian_filter_in_subquery(field, value))
            elif op == FilterOperator.GT:
                subqueries.append(self._xapian_filter_gt_subquery(field, value))
            elif op == FilterOperator.GE:
                subqueries.append(self._xapian_filter_ge_subquery(field, value))
            elif op == FilterOperator.LT:
                subqueries.append(self._xapian_filter_lt_subquery(field, value))
            elif op == FilterOperator.LE:
                subqueries.append(self._xapian_filter_le_subquery(field, value))

        query = XapianQuery.MatchAll

        for subquery in subqueries:
            query = XapianQuery(XapianQuery.OP_AND, query, subquery)

        return query

    def _xapian_filter_eq_subquery(self, field: str, value: Any) -> XapianQuery:
        return XapianQuery(boolean_term(field, value))

    def _xapian_filter_in_subquery(self, field: str, value: Any) -> XapianQuery:
        if not value:
            return XapianQuery.MatchAll

        query = XapianQuery.MatchNothing

        for item in value:
            query = XapianQuery(
                XapianQuery.OP_OR, query, self._xapian_filter_eq_subquery(field, item)
            )

        return query

    def _xapian_filter_gt_subquery(self, field: str, value: Any) -> XapianQuery:
        # Xapian doesn’t have native support for "<", so we need to emulate this:
        # field > value <==> field >= value AND !(field <= value)
        return XapianQuery(
            XapianQuery.OP_AND_NOT,
            self._xapian_filter_ge_subquery(field, value),
            self._xapian_filter_le_subquery(field, value),
        )

    def _xapian_filter_ge_subquery(self, field: str, value: Any) -> XapianQuery:
        return XapianQuery(
            XapianQuery.OP_VALUE_GE,
            field_to_slot(field),
            serialize_value(value),
        )

    def _xapian_filter_lt_subquery(self, field: str, value: Any) -> XapianQuery:
        # Xapian doesn’t have native support for "<", so we need to emulate this:
        # field < value <==> field <= value AND !(field >= value)
        return XapianQuery(
            XapianQuery.OP_AND_NOT,
            self._xapian_filter_le_subquery(field, value),
            self._xapian_filter_ge_subquery(field, value),
        )

    def _xapian_filter_le_subquery(self, field: str, value: Any) -> XapianQuery:
        return XapianQuery(
            XapianQuery.OP_VALUE_LE,
            field_to_slot(field),
            serialize_value(value),
        )
