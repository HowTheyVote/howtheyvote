from datetime import date
from ep_votes.models import (
    Country,
    Voting,
    Position,
    DocReference,
)
from ep_votes.helpers import (
    to_json,
    removeprefix,
    removesuffix,
)


def test_to_json_date():
    data = {"date": date(2021, 1, 1)}
    assert to_json(data) == '{"date": "2021-01-01"}'


def test_to_json_set():
    data = {"set": set([1, 2, 3])}
    assert to_json(data) == '{"set": [1, 2, 3]}'


def test_to_json_enum():
    data = {"enum": Country.DE}
    assert to_json(data) == '{"enum": "DE"}'


def test_to_json_voting():
    data = {"voting": Voting(doceo_member_id=1, name="Name", position=Position.FOR)}
    assert to_json(data) == '{"voting": ["Name", "FOR"]}'


def test_to_json_dataclass():
    data = {"dataclass": DocReference.from_str("A9-0001/2021")}
    expected = '{"dataclass": {"type": "A", "term": 9, "number": 1, "year": 2021}}'

    assert to_json(data) == expected


def test_removeprefix():
    assert removeprefix("original-string", "prefix-") == "original-string"
    assert removeprefix("prefix-original-string", "prefix-") == "original-string"


def test_removesuffix():
    assert removesuffix("original-string", "-suffix") == "original-string"
    assert removesuffix("original-string-suffix", "-suffix") == "original-string"
