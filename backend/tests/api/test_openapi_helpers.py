import datetime
from enum import Enum
from typing import Annotated, TypedDict

from howtheyvote.api.openapi_helpers import get_schema


def test_schema_description():
    class TestDict(TypedDict):
        """This is a test schema."""

    expected = {
        "type": "object",
        "description": "This is a test schema.",
        "properties": {},
    }

    assert get_schema(TestDict) == expected


def test_primitive_types():
    class TestDict(TypedDict):
        string: str
        integer: int
        float: float
        boolean: bool

    expected = {
        "type": "object",
        "properties": {
            "string": {
                "type": "string",
            },
            "integer": {
                "type": "integer",
            },
            "float": {
                "type": "number",
            },
            "boolean": {
                "type": "boolean",
            },
        },
        "required": ["string", "integer", "float", "boolean"],
    }

    assert get_schema(TestDict) == expected


def test_datetime_types():
    class TestDict(TypedDict):
        date: datetime.date
        datetime: datetime.datetime

    expected = {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "format": "date",
            },
            "datetime": {
                "type": "string",
                "format": "date-time",
            },
        },
        "required": ["date", "datetime"],
    }

    assert get_schema(TestDict) == expected


def test_enum_types():
    class TestEnum(Enum):
        ONE = "ONE"
        TWO = "TWO"
        THREE = "THREE"

    class TestDict(TypedDict):
        enum: TestEnum

    expected = {
        "type": "object",
        "properties": {
            "enum": {
                "type": "string",
                "enum": ["ONE", "TWO", "THREE"],
            },
        },
        "required": ["enum"],
    }

    assert get_schema(TestDict) == expected


def test_optional_types():
    class TestDict(TypedDict):
        optional: str | None
        required: str

    expected = {
        "type": "object",
        "properties": {
            "optional": {
                "type": "string",
            },
            "required": {
                "type": "string",
            },
        },
        "required": ["required"],
    }

    assert get_schema(TestDict) == expected


def test_list_types():
    class TestDict(TypedDict):
        numbers: list[int]

    expected = {
        "type": "object",
        "properties": {
            "numbers": {
                "type": "array",
                "items": {
                    "type": "integer",
                },
            },
        },
        "required": ["numbers"],
    }

    assert get_schema(TestDict) == expected


def test_nested_types():
    class UserDict(TypedDict):
        name: str

    class OrderDict(TypedDict):
        buyer: UserDict

    expected = {
        "type": "object",
        "properties": {
            "buyer": {
                "$ref": "#/components/schemas/User",
            },
        },
        "required": ["buyer"],
    }

    assert get_schema(OrderDict) == expected


def test_property_descriptions():
    class UserDict(TypedDict):
        """Represents a user."""

        id: str
        """User ID"""

        name: str
        """The user’s real first and last name"""

    expected = {
        "type": "object",
        "description": "Represents a user.",
        "properties": {
            "id": {
                "type": "string",
                "description": "User ID",
            },
            "name": {
                "type": "string",
                "description": "The user’s real first and last name",
            },
        },
        "required": ["id", "name"],
    }

    assert get_schema(UserDict) == expected


def test_examples():
    class UserDict(TypedDict):
        name: Annotated[str, "John Doe"]

    expected = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "example": "John Doe",
            },
        },
        "required": ["name"],
    }

    assert get_schema(UserDict) == expected


def test_inheritance():
    class AnimalDict(TypedDict):
        name: str

    class DogDict(AnimalDict):
        color: str

    expected = {
        "type": "object",
        "allOf": [
            {"$ref": "#/components/schemas/Animal"},
        ],
        "properties": {
            "color": {
                "type": "string",
            },
        },
        "required": ["color"],
    }

    assert get_schema(DogDict) == expected
