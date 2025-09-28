import datetime
from typing import TypedDict

from howtheyvote.models import Country, Fragment
from howtheyvote.store import Aggregator, CompositeRecord


class User(TypedDict):
    id: str
    first_name: str
    last_name: str
    date_of_birth: datetime.date


def map_user(record: CompositeRecord) -> User:
    return {
        "id": record.group_key,
        "first_name": record.get("first_name"),
        "last_name": record.get("last_name"),
        "date_of_birth": record.get("date_of_birth"),
    }


def create_fragments(db_session):
    user_1_fragment_1 = Fragment(
        model="User",
        source_name="index-page",
        source_id="index:1",
        group_key="1",
        data={
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    user_1_fragment_2 = Fragment(
        model="User",
        source_name="detail-page",
        source_id="deail:1",
        group_key="1",
        data={
            "date_of_birth": "1980-01-01",
        },
    )

    user_2_fragment_1 = Fragment(
        model="User",
        source_name="xml",
        source_id="xml:2",
        group_key="2",
        data={
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1990-12-31",
        },
    )

    db_session.add_all([user_1_fragment_1, user_1_fragment_2, user_2_fragment_1])
    db_session.commit()


def test_aggregator_records(db_session):
    create_fragments(db_session)

    aggregator = Aggregator(User)
    records = list(aggregator.records())

    assert len(records) == 2

    user_1 = records[0]
    user_2 = records[1]

    assert user_1.group_key == "1"
    assert user_1.getlist("first_name") == ["John"]
    assert user_1.getlist("last_name") == ["Doe"]
    assert user_1.getlist("date_of_birth") == ["1980-01-01"]

    assert user_2.group_key == "2"
    assert user_2.getlist("first_name") == ["Jane"]
    assert user_2.getlist("last_name") == ["Smith"]
    assert user_2.getlist("date_of_birth") == ["1990-12-31"]


def test_aggregator_records_filtered(db_session):
    create_fragments(db_session)

    aggregator = Aggregator(User)
    users = list(aggregator.records(group_keys={"1"}))

    assert len(users) == 1
    assert users[0].group_key == "1"


def test_aggregator_records_filtered_empty(db_session):
    create_fragments(db_session)

    aggregator = Aggregator(User)
    users = list(aggregator.records(group_keys={}))

    assert len(users) == 0


def test_aggregator_mapped_records(db_session):
    create_fragments(db_session)

    aggregator = Aggregator(User)
    users = list(aggregator.mapped_records(map_user))

    user_1 = users[0]
    user_2 = users[1]

    assert len(users) == 2

    assert user_1 == {
        "id": "1",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1980-01-01",
    }

    assert user_2 == {
        "id": "2",
        "first_name": "Jane",
        "last_name": "Smith",
        "date_of_birth": "1990-12-31",
    }


def test_aggregator_mapped_records_filtered(db_session):
    create_fragments(db_session)

    aggregator = Aggregator(User)
    users = list(aggregator.mapped_records(map_user, group_keys={"1"}))

    assert len(users) == 1
    assert users[0]["id"] == "1"


def test_composite_record_chain():
    record = CompositeRecord(
        group_key="1",
        data={
            "memberships": [
                [
                    {"start_date": "2000-01-01", "end_date": "2000-06-30"},
                    {"start_date": "2000-07-01", "end_date": "2000-12-31"},
                ],
                [
                    {"start_date": "2005-01-01", "end_date": "2000-12-31"},
                ],
            ],
        },
    )

    assert record.chain("memberships") == [
        {"start_date": "2000-01-01", "end_date": "2000-06-30"},
        {"start_date": "2000-07-01", "end_date": "2000-12-31"},
        {"start_date": "2005-01-01", "end_date": "2000-12-31"},
    ]


def test_composite_record_chain_none():
    record = CompositeRecord(
        group_key="1",
        data={
            "amendment_authors": [None],
        },
    )

    assert record.chain("amendment_authors") == []

    record = CompositeRecord(
        group_key="1",
        data={
            "amendment_authors": [None, ["original text"]],
        },
    )

    assert record.chain("amendment_authors") == ["original text"]


def test_composite_record_chain_type():
    record = CompositeRecord(
        group_key="1",
        data={
            "date": [["2024-01-01"], ["2025-01-01"]],
        },
    )

    dates = record.chain("date", type=datetime.date.fromisoformat)
    assert dates == [
        datetime.date(2024, 1, 1),
        datetime.date(2025, 1, 1),
    ]


def test_composite_record_chain_unique():
    record = CompositeRecord(
        group_key="1",
        data={
            "geo_areas": [["DEU", "ITA"], ["ITA", "FRA", "DEU"]],
        },
    )
    geo_areas = record.chain("geo_areas", unique=True)
    assert geo_areas == ["DEU", "ITA", "FRA"]

    geo_areas = record.chain("geo_areas", unique=True, type=lambda x: Country[x])
    assert geo_areas == [Country["DEU"], Country["ITA"], Country["FRA"]]
