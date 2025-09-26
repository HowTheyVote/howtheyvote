import dataclasses
import datetime
from enum import Enum
from typing import Any

import sqlalchemy as sa
from sqlalchemy import Column, MetaData, Table, create_engine, or_, select, text
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from howtheyvote.json import json_dumps, json_loads
from howtheyvote.models.types import ListType


class Committee(Enum):
    """Example enum"""

    BUDG = "BUDG"
    ECON = "ECON"
    ITRE = "ITRE"
    JURI = "JURI"


@dataclasses.dataclass
class Country:
    """Example dataclass"""

    code: str


class CountryType(TypeDecorator[Country]):
    """Example type decorator that serializes `Country` instances to strings"""

    impl = sa.Unicode
    cache_ok = True

    def process_bind_param(self, value: Country | None, dialect: Dialect) -> str | None:
        if not value:
            return None

        return value.code

    def process_result_value(self, value: str | None, dialect: Dialect) -> Country | None:
        if not value:
            return None

        return Country(code=value)


@dataclasses.dataclass
class MemberVote:
    """Example dataclass"""

    position: str
    member_id: int


class MemberVoteType(TypeDecorator[MemberVote]):
    """Example type decorator that serializes `MemberVote` instances to JSON strings."""

    impl = sa.JSON
    cache_ok = True

    def process_bind_param(self, value: MemberVote | None, dialect: Dialect) -> Any | None:
        if not value:
            return None

        return dataclasses.asdict(value)

    def process_result_value(self, value: Any | None, dialect: Dialect) -> MemberVote | None:
        if not value or not isinstance(value, dict):
            return None

        return MemberVote(**value)


def test_list_type_enum():
    engine = create_engine("sqlite://")
    metadata = MetaData()

    table = Table(
        "votes",
        metadata,
        Column("committees", ListType(sa.Enum(Committee))),
    )

    with engine.connect() as connection:
        metadata.create_all(connection)
        stmt = table.insert().values(committees=[Committee.ITRE, Committee.ECON])
        connection.execute(stmt)
        connection.commit()

        unprocessed = connection.execute(text("SELECT committees from votes")).scalar()
        assert unprocessed == '["ITRE", "ECON"]'

        processed = connection.execute(select(table)).scalar()
        assert processed == [Committee.ITRE, Committee.ECON]


def test_list_type_date():
    engine = create_engine(
        "sqlite://",
        json_serializer=json_dumps,
        json_deserializer=json_loads,
    )
    metadata = MetaData()

    table = Table(
        "procedures",
        metadata,
        Column("dates", ListType(sa.Date)),
    )

    with engine.connect() as connection:
        metadata.create_all(connection)
        stmt = table.insert().values(
            dates=[datetime.date(2023, 1, 1), datetime.date(2022, 1, 1)]
        )
        connection.execute(stmt)
        connection.commit()

        unprocessed = connection.execute(text("SELECT dates from procedures")).scalar()
        assert unprocessed == '["2023-01-01", "2022-01-01"]'

        processed = connection.execute(select(table)).scalar()
        assert processed == [datetime.date(2023, 1, 1), datetime.date(2022, 1, 1)]


def test_list_type_type_decorator():
    engine = create_engine(
        "sqlite://",
        json_serializer=json_dumps,
        json_deserializer=json_loads,
    )
    metadata = MetaData()

    table = Table(
        "votes",
        metadata,
        Column("countries", ListType(CountryType)),
    )

    with engine.connect() as connection:
        metadata.create_all(connection)
        stmt = table.insert().values(countries=[Country(code="FRA"), Country(code="DEU")])
        connection.execute(stmt)
        connection.commit()

        unprocessed = connection.execute(text("SELECT countries from votes")).scalar()
        assert unprocessed == '["FRA", "DEU"]'

        processed = connection.execute(select(table)).scalar()
        assert processed == [Country(code="FRA"), Country(code="DEU")]


def test_list_type_type_decorator_json():
    engine = create_engine(
        "sqlite://",
        json_serializer=json_dumps,
        json_deserializer=json_loads,
    )
    metadata = MetaData()

    table = Table(
        "votes",
        metadata,
        Column("member_votes", ListType(MemberVoteType)),
    )

    member_votes = [MemberVote(position="FOR", member_id=12345)]

    with engine.connect() as connection:
        metadata.create_all(connection)
        stmt = table.insert().values(member_votes=member_votes)
        connection.execute(stmt)
        connection.commit()

        unprocessed = connection.execute(text("SELECT member_votes from votes")).scalar()
        assert unprocessed == '[{"position": "FOR", "member_id": 12345}]'

        processed = connection.execute(select(table)).scalar()
        assert processed == member_votes


def test_list_type_empty_none():
    engine = create_engine(
        "sqlite://",
        json_serializer=json_dumps,
        json_deserializer=json_loads,
    )
    metadata = MetaData()

    table = Table(
        "test",
        metadata,
        Column("list", ListType(sa.Unicode)),
    )

    with engine.connect() as connection:
        metadata.create_all(connection)
        connection.execute(table.insert().values(list=[]))
        connection.execute(table.insert().values(list=None))
        connection.commit()

        unprocessed = connection.execute(text("SELECT list from test")).scalars().all()
        assert unprocessed[0] == "[]"
        assert unprocessed[1] == "null"

        processed = connection.execute(select(table)).scalars().all()
        assert processed[0] == []
        assert processed[1] is None


def test_list_type_type_decorator_contains():
    engine = create_engine(
        "sqlite://",
        json_serializer=json_dumps,
        json_deserializer=json_loads,
    )
    metadata = MetaData()

    table = Table(
        "votes",
        metadata,
        Column("countries", ListType(CountryType)),
    )

    deu = Country(code="DEU")
    fra = Country(code="FRA")
    ita = Country(code="ITA")

    with engine.connect() as connection:
        metadata.create_all(connection)
        connection.execute(table.insert().values(countries=[deu, fra]))
        connection.execute(table.insert().values(countries=[fra]))
        connection.execute(table.insert().values(countries=[ita]))
        connection.commit()

        query = select(table.c.countries).where(
            or_(table.c.countries.contains(deu), table.c.countries.contains(ita))
        )
        results = list(connection.execute(query).scalars())

        assert len(results) == 2
        assert results[0] == [deu, fra]
        assert results[1] == [ita]


def test_list_type_type_decorator_overlap():
    engine = create_engine(
        "sqlite://",
        json_serializer=json_dumps,
        json_deserializer=json_loads,
    )
    metadata = MetaData()

    table = Table(
        "votes",
        metadata,
        Column("countries", ListType(CountryType)),
    )

    deu = Country(code="DEU")
    fra = Country(code="FRA")
    ita = Country(code="ITA")

    with engine.connect() as connection:
        metadata.create_all(connection)
        connection.execute(table.insert().values(countries=[deu, fra]))
        connection.execute(table.insert().values(countries=[fra]))
        connection.execute(table.insert().values(countries=[ita]))
        connection.commit()

        query = select(table.c.countries).where(table.c.countries.overlap([deu, ita]))
        results = list(connection.execute(query).scalars())

        assert len(results) == 2
        assert results[0] == [deu, fra]
        assert results[1] == [ita]
