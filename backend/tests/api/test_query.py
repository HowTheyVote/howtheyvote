import datetime

import pytest

from howtheyvote.api.query import DatabaseQuery, Order, SearchQuery
from howtheyvote.models import Committee, Country, Vote
from howtheyvote.store import index_search


@pytest.fixture()
def votes(db_session, search_index):
    votes = [
        Vote(
            id=1,
            is_main=True,
            title="Vote One",
            timestamp=datetime.datetime(2024, 1, 1),
            geo_areas=[Country["DEU"], Country["FRA"]],
            responsible_committees=[Committee["AFCO"]],
        ),
        Vote(
            id=2,
            is_main=True,
            title="Vote Two",
            timestamp=datetime.datetime(2024, 1, 2),
            press_release_id="abc",
            geo_areas=[Country["DEU"], Country["ITA"]],
            responsible_committees=[Committee["IMCO"]],
        ),
        Vote(
            id=3,
            is_main=True,
            title="Vote Three",
            timestamp=datetime.datetime(2024, 1, 3),
        ),
    ]

    db_session.add_all(votes)
    db_session.commit()
    index_search(Vote, votes)

    yield


def test_database_query_handle(votes):
    response = DatabaseQuery(Vote).handle()
    results = response["results"]
    assert response["total"] == 3
    assert len(results) == 3
    assert [r.id for r in results] == [3, 2, 1]


def test_database_query_handle_sort(votes):
    response = DatabaseQuery(Vote).sort("date").handle()
    results = response["results"]
    assert len(results) == 3
    assert [r.timestamp for r in results] == [
        datetime.datetime(2024, 1, 3),
        datetime.datetime(2024, 1, 2),
        datetime.datetime(2024, 1, 1),
    ]

    response = DatabaseQuery(Vote).sort("date", Order.ASC).handle()
    results = response["results"]
    assert len(results) == 3
    assert [r.timestamp for r in results] == [
        datetime.datetime(2024, 1, 1),
        datetime.datetime(2024, 1, 2),
        datetime.datetime(2024, 1, 3),
    ]


def test_database_query_handle_pagination(votes):
    response = DatabaseQuery(Vote).page(1).handle()
    assert response["page"] == 1
    assert response["has_prev"] is False
    assert response["has_next"] is False
    assert len(response["results"]) == 3

    response = DatabaseQuery(Vote).page(1).page_size(1).handle()
    assert response["page"] == 1
    assert response["has_prev"] is False
    assert response["has_next"] is True
    assert response["results"][0].id == 3

    response = DatabaseQuery(Vote).page(2).page_size(1).handle()
    assert response["page"] == 2
    assert response["has_prev"] is True
    assert response["has_next"] is True
    assert response["results"][0].id == 2

    response = DatabaseQuery(Vote).page(3).page_size(1).handle()
    assert response["page"] == 3
    assert response["has_prev"] is True
    assert response["has_next"] is False
    assert response["results"][0].id == 1


def test_database_query_handle_filters(votes):
    response = DatabaseQuery(Vote).handle()
    assert response["total"] == 3

    response = DatabaseQuery(Vote).filter("geo_areas", "=", Country["FRA"]).handle()
    assert response["total"] == 1
    assert len(response["results"]) == 1
    assert response["results"][0].id == 1
    assert response["results"][0].display_title == "Vote One"

    response = DatabaseQuery(Vote).filter("geo_areas", "=", Country["DEU"]).handle()
    assert response["total"] == 2
    assert len(response["results"]) == 2
    assert response["results"][0].id == 2
    assert response["results"][0].display_title == "Vote Two"
    assert response["results"][1].id == 1
    assert response["results"][1].display_title == "Vote One"

    response = (
        DatabaseQuery(Vote)
        .filter("geo_areas", "in", [Country["FRA"], Country["ITA"]])
        .handle()
    )
    assert response["total"] == 2
    assert response["results"][0].id == 2
    assert response["results"][1].id == 1

    response = DatabaseQuery(Vote).filter("date", "=", datetime.date(2024, 1, 2)).handle()
    assert response["total"] == 1
    assert response["results"][0].id == 2

    response = DatabaseQuery(Vote).filter("date", ">", datetime.date(2024, 1, 1)).handle()
    assert response["total"] == 2
    assert len(response["results"]) == 2
    assert response["results"][0].id == 3
    assert response["results"][1].id == 2

    response = DatabaseQuery(Vote).filter("date", ">=", datetime.date(2024, 1, 2)).handle()
    assert response["total"] == 2
    assert len(response["results"]) == 2
    assert response["results"][0].id == 3
    assert response["results"][1].id == 2

    response = (
        DatabaseQuery(Vote)
        .filter("date", ">", datetime.date(2024, 1, 1))
        .filter("date", "<", datetime.date(2024, 1, 3))
        .handle()
    )
    assert response["total"] == 1
    assert len(response["results"]) == 1
    assert response["results"][0].id == 2

    response = (
        DatabaseQuery(Vote)
        .filter("date", ">=", datetime.date(2024, 1, 2))
        .filter("date", "<=", datetime.date(2024, 1, 2))
        .handle()
    )
    assert response["total"] == 1
    assert len(response["results"]) == 1
    assert response["results"][0].id == 2


def test_database_query_sql_where(votes):
    response = DatabaseQuery(Vote).handle()
    assert response["total"] == 3

    response = DatabaseQuery(Vote).where(Vote.timestamp >= "2024-01-02").handle()
    assert response["total"] == 2
    assert response["results"][0].id == 3
    assert response["results"][0].display_title == "Vote Three"
    assert response["results"][1].id == 2
    assert response["results"][1].display_title == "Vote Two"


def test_search_query_handle(votes):
    response = SearchQuery(Vote).handle()
    assert response["page"] == 1
    assert response["page_size"] == 20
    assert response["total"] == 3

    results = response["results"]
    assert len(results) == 3
    assert [r.id for r in results] == [3, 2, 1]


def test_search_query_handle_sort(votes):
    response = SearchQuery(Vote).sort("date").handle()
    results = response["results"]
    assert len(results) == 3
    assert [r.timestamp for r in results] == [
        datetime.datetime(2024, 1, 3),
        datetime.datetime(2024, 1, 2),
        datetime.datetime(2024, 1, 1),
    ]

    response = SearchQuery(Vote).sort("date", Order.ASC).handle()
    results = response["results"]
    assert len(results) == 3
    assert [r.timestamp for r in results] == [
        datetime.datetime(2024, 1, 1),
        datetime.datetime(2024, 1, 2),
        datetime.datetime(2024, 1, 3),
    ]


def test_search_query_handle_query(votes):
    response = SearchQuery(Vote).query("vote").handle()
    assert response["total"] == 3

    results = response["results"]
    assert {r.id for r in response["results"]} == {1, 2, 3}

    response = SearchQuery(Vote).query("two").handle()
    assert response["total"] == 1

    results = response["results"]
    assert results[0].id == 2


def test_search_query_handle_britihs_vs_american(db_session, search_index):
    votes = [
        Vote(
            id=182483,
            timestamp=datetime.datetime(2025, 12, 16),
            title="Incentivising defence-related investments in the EU budget to implement the ReArm Europe Plan",
            is_main=True,
        ),
        Vote(
            id=166228,
            timestamp=datetime.datetime(2024, 3, 12),
            title="Council decision inviting Member States to ratify the Violence and Harassment Convention, 2019 (No 190) of the International Labour Organization",
            is_main=True,
        ),
        Vote(
            id=150459,
            timestamp=datetime.datetime(2022, 11, 23),
            title="Recognising the Russian Federation as a state sponsor of terrorism",
            is_main=True,
        ),
        Vote(
            id=162985,
            timestamp=datetime.datetime(2024, 1, 15),
            title="Current and future challenges regarding cross-border cooperation with neighbouring countries",
            is_main=True,
        ),
    ]

    db_session.add_all(votes)
    db_session.commit()
    index_search(Vote, votes)

    # defense vs. defence
    response = SearchQuery(Vote).query("defence").handle()
    assert response["total"] == 1
    assert response["results"][0].id == 182483

    response = SearchQuery(Vote).query("defense").handle()
    assert response["total"] == 1
    assert response["results"][0].id == 182483

    # organization vs. organisation
    response = SearchQuery(Vote).query("organization").handle()
    assert response["total"] == 1
    assert response["results"][0].id == 166228

    response = SearchQuery(Vote).query("organisation").handle()
    assert response["total"] == 1
    assert response["results"][0].id == 166228

    # recognizing vs. recognising
    response = SearchQuery(Vote).query("recognizing").handle()
    assert response["total"] == 1
    assert response["results"][0].id == 150459

    response = SearchQuery(Vote).query("recognising").handle()
    assert response["total"] == 1
    assert response["results"][0].id == 150459

    # neighboring vs. neighbouring
    response = SearchQuery(Vote).query("neighboring").handle()
    assert response["total"] == 1
    assert response["results"][0].id == 162985

    response = SearchQuery(Vote).query("neighbouring").handle()
    assert response["total"] == 1
    assert response["results"][0].id == 162985


def test_search_query_handle_normalization(db_session, search_index):
    vote = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1),
        title="Vote",
        rapporteur="Markéta Gregorová",
        is_main=True,
    )

    db_session.add(vote)
    db_session.commit()
    index_search(Vote, [vote])

    response = SearchQuery(Vote).query("gregorova").handle()
    assert response["total"] == 1
    assert response["results"][0].id == 1


def test_search_query_handle_spelling_correction(db_session, search_index):
    vote = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1),
        title="Mercosur",
        is_main=True,
    )

    db_session.add(vote)
    db_session.commit()
    index_search(Vote, [vote])

    response = SearchQuery(Vote).query("mercosour").handle()
    assert response["total"] == 0
    assert response["corrected_query"] == "mercosur"


def test_search_query_handle_spelling_correction_stopwords(db_session, search_index):
    vote = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1),
        title="2019 discharge: European Agency for Safety and Health at Work",
        is_main=True,
    )

    db_session.add(vote)
    db_session.commit()
    index_search(Vote, [vote])

    # This should not suggest "at" as a corrected spelling
    response = SearchQuery(Vote).query("cat").handle()
    assert response["corrected_query"] is None


@pytest.mark.override_config(SEARCH_SYNONYMS="corona:covid")
def test_search_query_handle_synonyms(db_session, search_index, mocker):
    vote = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1),
        title="Covid-19",
        is_main=True,
    )

    db_session.add(vote)
    db_session.commit()
    index_search(Vote, [vote])

    response = SearchQuery(Vote).query("corona").handle()
    assert response["total"] == 1
    assert response["results"][0].id == 1


def test_search_query_handle_phrase(db_session, search_index):
    votes = [
        Vote(
            id=1,
            is_main=True,
            title="foo bar baz",
            timestamp=datetime.datetime(2024, 1, 1),
        ),
        Vote(
            id=2,
            is_main=True,
            title="foo baz",
            timestamp=datetime.datetime(2024, 1, 2),
        ),
    ]

    db_session.add_all(votes)
    db_session.commit()
    index_search(Vote, votes)

    response = SearchQuery(Vote).query("foo baz").handle()
    assert response["total"] == 2

    response = SearchQuery(Vote).query('"foo baz"').handle()
    assert response["total"] == 1


def test_search_query_handle_pagination(votes):
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
    assert response["results"][0].id == 3

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
    assert response["results"][0].id == 1


def test_search_query_handle_filters(votes):
    response = SearchQuery(Vote).handle()
    assert response["total"] == 3

    response = SearchQuery(Vote).filter("geo_areas", "=", Country["FRA"]).handle()
    assert response["total"] == 1
    assert response["results"][0].id == 1
    assert response["results"][0].display_title == "Vote One"

    response = SearchQuery(Vote).filter("geo_areas", "=", Country["DEU"]).handle()
    assert response["total"] == 2
    assert response["results"][0].id == 2
    assert response["results"][0].display_title == "Vote Two"
    assert response["results"][1].id == 1
    assert response["results"][1].display_title == "Vote One"

    response = (
        SearchQuery(Vote).filter("geo_areas", "in", [Country["FRA"], Country["ITA"]]).handle()
    )
    assert response["total"] == 2
    assert response["results"][0].id == 2
    assert response["results"][1].id == 1

    response = SearchQuery(Vote).filter("date", "=", datetime.date(2024, 1, 2)).handle()
    assert response["total"] == 1
    assert response["results"][0].id == 2

    response = SearchQuery(Vote).filter("date", ">", datetime.date(2024, 1, 1)).handle()
    assert response["total"] == 2
    assert response["results"][0].id == 3
    assert response["results"][1].id == 2

    response = SearchQuery(Vote).filter("date", ">=", datetime.date(2024, 1, 2)).handle()
    assert response["total"] == 2
    assert response["results"][0].id == 3
    assert response["results"][1].id == 2

    response = (
        SearchQuery(Vote)
        .filter("date", ">", datetime.date(2024, 1, 1))
        .filter("date", "<", datetime.date(2024, 1, 3))
        .handle()
    )
    assert response["total"] == 1
    assert len(response["results"]) == 1
    assert response["results"][0].id == 2

    response = (
        SearchQuery(Vote)
        .filter("date", ">=", datetime.date(2024, 1, 2))
        .filter("date", "<=", datetime.date(2024, 1, 2))
        .handle()
    )
    assert response["total"] == 1
    assert len(response["results"]) == 1
    assert response["results"][0].id == 2


def test_search_query_handle_facets(votes):
    response = SearchQuery(Vote).facet("geo_areas").handle()
    assert len(response["facets"]) == 1
    assert response["facets"]["geo_areas"] == [
        {
            "value": "DEU",
            "label": "Germany",
            "short_label": None,
            "count": 2,
        },
        {
            "value": "FRA",
            "label": "France",
            "short_label": None,
            "count": 1,
        },
        {
            "value": "ITA",
            "label": "Italy",
            "short_label": None,
            "count": 1,
        },
    ]


def test_search_query_handle_facets_filters(votes):
    response = (
        SearchQuery(Vote)
        .facet("geo_areas")
        .facet("responsible_committees")
        .filter("geo_areas", "=", Country["FRA"])
        .handle()
    )
    assert response["facets"] == {
        "geo_areas": [
            {
                "value": "DEU",
                "label": "Germany",
                "short_label": None,
                "count": 2,
            },
            {
                "value": "FRA",
                "label": "France",
                "short_label": None,
                "count": 1,
            },
            {
                "value": "ITA",
                "label": "Italy",
                "short_label": None,
                "count": 1,
            },
        ],
        "responsible_committees": [
            {
                "value": "AFCO",
                "label": "Constitutional Affairs",
                "short_label": "AFCO",
                "count": 1,
            },
        ],
    }

    response = (
        SearchQuery(Vote)
        .facet("geo_areas")
        .facet("responsible_committees")
        .filter("responsible_committees", "=", Committee["AFCO"])
        .handle()
    )
    assert response["facets"] == {
        "geo_areas": [
            {
                "value": "DEU",
                "label": "Germany",
                "short_label": None,
                "count": 1,
            },
            {
                "value": "FRA",
                "label": "France",
                "short_label": None,
                "count": 1,
            },
        ],
        "responsible_committees": [
            {
                "value": "AFCO",
                "label": "Constitutional Affairs",
                "short_label": "AFCO",
                "count": 1,
            },
            {
                "value": "IMCO",
                "label": "Internal Market and Consumer Protection",
                "short_label": "IMCO",
                "count": 1,
            },
        ],
    }


def test_search_query_handle_facets_selected(votes):
    response = (
        SearchQuery(Vote)
        .facet("geo_areas")
        .facet("responsible_committees")
        .filter("geo_areas", "=", Country["ITA"])
        .filter("responsible_committees", "=", Committee["AFCO"])
        .handle()
    )
    assert response["facets"] == {
        "geo_areas": [
            {
                "value": "DEU",
                "label": "Germany",
                "short_label": None,
                "count": 1,
            },
            {
                "value": "FRA",
                "label": "France",
                "short_label": None,
                "count": 1,
            },
            {
                "value": "ITA",
                "label": "Italy",
                "short_label": None,
                "count": 0,
            },
        ],
        "responsible_committees": [
            {
                "value": "IMCO",
                "label": "Internal Market and Consumer Protection",
                "short_label": "IMCO",
                "count": 1,
            },
            {
                "value": "AFCO",
                "label": "Constitutional Affairs",
                "short_label": "AFCO",
                "count": 0,
            },
        ],
    }

    response = (
        SearchQuery(Vote)
        .facet("geo_areas")
        .facet("responsible_committees")
        .filter("geo_areas", "in", [Country["ITA"]])
        .filter("responsible_committees", "in", [Committee["AFCO"]])
        .handle()
    )
    assert response["facets"] == {
        "geo_areas": [
            {
                "value": "DEU",
                "label": "Germany",
                "short_label": None,
                "count": 1,
            },
            {
                "value": "FRA",
                "label": "France",
                "short_label": None,
                "count": 1,
            },
            {
                "value": "ITA",
                "label": "Italy",
                "short_label": None,
                "count": 0,
            },
        ],
        "responsible_committees": [
            {
                "value": "IMCO",
                "label": "Internal Market and Consumer Protection",
                "short_label": "IMCO",
                "count": 1,
            },
            {
                "value": "AFCO",
                "label": "Constitutional Affairs",
                "short_label": "AFCO",
                "count": 0,
            },
        ],
    }
