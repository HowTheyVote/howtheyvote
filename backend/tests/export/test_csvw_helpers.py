import datetime
from typing import TypedDict

from howtheyvote.export.csvw_helpers import get_schema


def test_get_schema_bool_type():
    class TestDict(TypedDict):
        flag: bool

    expected = {
        "columns": [
            {
                "name": "flag",
                "datatype": "boolean",
                "required": True,
            },
        ],
    }

    assert get_schema(TestDict) == expected


def test_get_schema_numeric_types():
    class TestDict(TypedDict):
        integer: int
        float: float

    expected = {
        "columns": [
            {
                "name": "integer",
                "datatype": "integer",
                "required": True,
            },
            {
                "name": "float",
                "datatype": "decimal",
                "required": True,
            },
        ],
    }

    assert get_schema(TestDict) == expected


def test_get_schema_datetime_types():
    class TestDict(TypedDict):
        date: datetime.date
        datetime: datetime.datetime

    expected = {
        "columns": [
            {
                "name": "date",
                "datatype": "date",
                "required": True,
            },
            {
                "name": "datetime",
                "datatype": "dateTime",
                "required": True,
            },
        ],
    }

    assert get_schema(TestDict) == expected


def test_get_schema_string_type():
    class TestDict(TypedDict):
        string: str

    expected = {
        "columns": [
            {
                "name": "string",
                "datatype": "string",
                "required": True,
            },
        ],
    }

    assert get_schema(TestDict) == expected


def test_get_schema_optional():
    class TestDict(TypedDict):
        title: str | None

    expected = {
        "columns": [
            {
                "name": "title",
                "datatype": "string",
                "required": False,
            },
        ],
    }

    assert get_schema(TestDict) == expected


def test_get_schema_column_description():
    class TestDict(TypedDict):
        title: str
        """Vote title"""

    expected = {
        "columns": [
            {
                "name": "title",
                "datatype": "string",
                "required": True,
                "dc:description": "Vote title",
            },
        ],
    }

    assert get_schema(TestDict) == expected
