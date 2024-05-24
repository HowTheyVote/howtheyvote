import pytest
from sqlalchemy import Column, MetaData, Table, create_engine, select, text

from howtheyvote.models import Country, CountryType


def test_country_getitem():
    austria = Country["AUT"]
    assert isinstance(austria, Country)
    assert austria.code == "AUT"

    with pytest.raises(KeyError):
        Country["invalid"]


def test_country_get():
    austria = Country.get("AUT")
    assert isinstance(austria, Country)
    assert austria.code == "AUT"

    invalid = Country.get("invalid")
    assert invalid is None


def test_country_from_label():
    assert Country.from_label("Austria") == Country["AUT"]


def test_country_from_label_alternates():
    assert Country.from_label("Czechia") == Country["CZE"]
    assert Country.from_label("Czech Republic") == Country["CZE"]


def test_country_from_label_fuzzy():
    # Sanity check: exact match
    assert Country.from_label("Kosovo*") == Country["XKX"]

    # Sanity check: By default, only exact matches are returned
    assert Country.from_label("Kosovo") is None
    assert Country.from_label("Kosovo under UNSCR 1244/1999") is None

    # If fuzzy=True, countries that start with the same substring are matched, too.
    assert Country.from_label("Kosovo under UNSCR 1244/1999", fuzzy=True) == Country["XKX"]
    assert Country.from_label("Kosovo", fuzzy=True) == Country["XKX"]


def test_country_type():
    engine = create_engine("sqlite://")
    metadata = MetaData()

    table = Table(
        "countries",
        metadata,
        Column("country", CountryType()),
    )

    with engine.connect() as connection:
        metadata.create_all(connection)
        stmt = table.insert().values(country=Country["FRA"])
        connection.execute(stmt)
        connection.commit()

        unprocessed = connection.execute(text("SELECT country from countries")).scalar()
        assert unprocessed == "FRA"

        processed = connection.execute(select(table)).scalar()
        assert isinstance(processed, Country)
        assert processed.code == "FRA"
