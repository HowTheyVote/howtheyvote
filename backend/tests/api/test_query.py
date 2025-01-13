import datetime

import pytest

from howtheyvote.api.query import DatabaseQuery, Order, SearchQuery
from howtheyvote.models import Vote
from howtheyvote.store import index_search


@pytest.fixture(autouse=True)
def votes(db_session, search_index):
    votes = [
        Vote(
            id=1,
            is_main=True,
            is_featured=False,
            title="Vote One",
            timestamp=datetime.datetime(2024, 1, 1),
        ),
        Vote(
            id=2,
            is_main=True,
            is_featured=True,
            title="Vote Two",
            timestamp=datetime.datetime(2024, 1, 2),
        ),
        Vote(
            id=3,
            is_main=True,
            is_featured=False,
            title="Vote Three",
            timestamp=datetime.datetime(2024, 1, 3),
        ),
    ]

    db_session.add_all(votes)
    db_session.commit()
    index_search(Vote, votes)

    yield


def test_database_query_handle():
    response = DatabaseQuery(Vote).handle()
    results = response["results"]
    assert response["total"] == 3
    assert len(results) == 3
    assert [r.id for r in results] == [1, 2, 3]


def test_database_query_handle_sort():
    response = DatabaseQuery(Vote).sort("timestamp").handle()
    results = response["results"]
    assert len(results) == 3
    assert [r.timestamp for r in results] == [
        datetime.datetime(2024, 1, 1),
        datetime.datetime(2024, 1, 2),
        datetime.datetime(2024, 1, 3),
    ]

    response = DatabaseQuery(Vote).sort("timestamp", Order.DESC).handle()
    results = response["results"]
    assert len(results) == 3
    assert [r.timestamp for r in results] == [
        datetime.datetime(2024, 1, 3),
        datetime.datetime(2024, 1, 2),
        datetime.datetime(2024, 1, 1),
    ]


def test_database_query_handle_pagination():
    response = DatabaseQuery(Vote).page(1).handle()
    assert response["page"] == 1
    assert response["has_prev"] is False
    assert response["has_next"] is False
    assert len(response["results"]) == 3

    response = DatabaseQuery(Vote).page(1).page_size(1).handle()
    assert response["page"] == 1
    assert response["has_prev"] is False
    assert response["has_next"] is True
    assert response["results"][0].id == 1

    response = DatabaseQuery(Vote).page(2).page_size(1).handle()
    assert response["page"] == 2
    assert response["has_prev"] is True
    assert response["has_next"] is True
    assert response["results"][0].id == 2

    response = DatabaseQuery(Vote).page(3).page_size(1).handle()
    assert response["page"] == 3
    assert response["has_prev"] is True
    assert response["has_next"] is False
    assert response["results"][0].id == 3


def test_database_query_handle_filters():
    response = DatabaseQuery(Vote).handle()
    assert response["total"] == 3

    response = DatabaseQuery(Vote).filter("is_featured", True).handle()
    assert response["total"] == 1
    assert len(response["results"]) == 1
    assert response["results"][0].id == 2
    assert response["results"][0].display_title == "Vote Two"

    response = DatabaseQuery(Vote).filter("is_featured", False).handle()
    assert response["total"] == 2
    assert len(response["results"]) == 2
    assert response["results"][0].id == 1
    assert response["results"][0].display_title == "Vote One"
    assert response["results"][1].id == 3
    assert response["results"][1].display_title == "Vote Three"


def test_database_query_sql_where():
    response = DatabaseQuery(Vote).handle()
    assert response["total"] == 3

    response = DatabaseQuery(Vote).where(Vote.timestamp >= "2024-01-02").handle()
    assert response["total"] == 2
    assert response["results"][0].id == 2
    assert response["results"][0].display_title == "Vote Two"
    assert response["results"][1].id == 3
    assert response["results"][1].display_title == "Vote Three"


def test_search_query_handle():
    response = SearchQuery(Vote).handle()
    assert response["page"] == 1
    assert response["page_size"] == 20
    assert response["total"] == 3

    results = response["results"]
    assert len(results) == 3
    assert [r.id for r in results] == [1, 2, 3]


def test_search_query_handle_sort():
    response = SearchQuery(Vote).sort("timestamp").handle()
    results = response["results"]
    assert len(results) == 3
    assert [r.timestamp for r in results] == [
        datetime.datetime(2024, 1, 1),
        datetime.datetime(2024, 1, 2),
        datetime.datetime(2024, 1, 3),
    ]

    response = SearchQuery(Vote).sort("timestamp", Order.DESC).handle()
    results = response["results"]
    assert len(results) == 3
    assert [r.timestamp for r in results] == [
        datetime.datetime(2024, 1, 3),
        datetime.datetime(2024, 1, 2),
        datetime.datetime(2024, 1, 1),
    ]


def test_search_query_handle_query():
    response = SearchQuery(Vote).query("vote").handle()
    assert response["total"] == 3

    results = response["results"]
    assert {r.id for r in response["results"]} == {1, 2, 3}

    response = SearchQuery(Vote).query("two").handle()
    assert response["total"] == 1

    results = response["results"]
    assert results[0].id == 2


def test_search_query_handle_pagination():
    response = SearchQuery(Vote).page(1).handle()
    assert response["total"] == 3
    assert response["page"] == 1
    assert response["has_prev"] is False
    assert response["has_next"] is False

    response = SearchQuery(Vote).page(1).page_size(1).handle()
    assert response["total"] == 3
    assert response["page"] == 1
    assert response["has_prev"] is False
    assert response["has_next"] is True
    assert response["results"][0].id == 1

    response = SearchQuery(Vote).page(2).page_size(1).handle()
    assert response["total"] == 3
    assert response["page"] == 2
    assert response["has_prev"] is True
    assert response["has_next"] is True
    assert response["results"][0].id == 2

    response = SearchQuery(Vote).page(3).page_size(1).handle()
    assert response["total"] == 3
    assert response["page"] == 3
    assert response["has_prev"] is True
    assert response["has_next"] is False
    assert response["results"][0].id == 3


def test_search_query_handle_filters():
    response = SearchQuery(Vote).handle()
    assert response["total"] == 3

    response = SearchQuery(Vote).filter("is_featured", True).handle()
    assert response["total"] == 1
    assert len(response["results"]) == 1
    assert response["results"][0].id == 2
    assert response["results"][0].display_title == "Vote Two"

    response = SearchQuery(Vote).filter("is_featured", False).handle()
    assert response["total"] == 2
    assert len(response["results"]) == 2
    assert response["results"][0].id == 1
    assert response["results"][0].display_title == "Vote One"
    assert response["results"][1].id == 3
    assert response["results"][1].display_title == "Vote Three"
