from datetime import date
from bs4 import BeautifulSoup
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
    normalize_rowspan,
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


def test_normalize_rowspan():
    xml = (
        "<TABLE>"
        "   <TBODY>"
        "       <TR>"
        "           <TD COLNAME='C1'>1 / 1</TD>"
        "           <TD COLNAME='C2'>1 / 2</TD>"
        "       </TR>"
        "   </TBODY>"
        "</TABLE>"
    )

    table_tag = BeautifulSoup(xml, "lxml-xml")

    expected = [
        {"c1": "1 / 1", "c2": "1 / 2"},
    ]

    assert normalize_rowspan(table_tag) == expected


def test_normalize_rowspan_rowspan_a():
    xml = (
        "<TABLE>"
        "   <TBODY>"
        "       <TR>"
        "           <TD COLNAME='C1' ROWSPAN='2'>1 / 1</TD>"
        "           <TD COLNAME='C2'>1 / 2</TD>"
        "       </TR>"
        "       <TR>"
        "           <TD COLNAME='C2'>2 / 2</TD>"
        "       </TR>"
        "       <TR>"
        "           <TD COLNAME='C1'>3 / 1</TD>"
        "           <TD COLNAME='C2'>3 / 2</TD>"
        "       </TR>"
        "   </TBODY>"
        "</TABLE>"
    )

    table_tag = BeautifulSoup(xml, "lxml-xml")

    expected = [
        {"c1": "1 / 1", "c2": "1 / 2"},
        {"c1": "1 / 1", "c2": "2 / 2"},
        {"c1": "3 / 1", "c2": "3 / 2"},
    ]

    assert normalize_rowspan(table_tag) == expected


def test_normalize_rowspan_rowspan_b():
    xml = (
        "<TABLE>"
        "   <TBODY>"
        "       <TR>"
        "           <TD COLNAME='C1' ROWSPAN='3'>1 / 1</TD>"
        "           <TD COLNAME='C2' ROWSPAN='2'>1 / 2</TD>"
        "           <TD COLNAME='C3'>1 / 3</TD>"
        "       </TR>"
        "       <TR>"
        "           <TD COLNAME='C3'>2 / 3</TD>"
        "       </TR>"
        "       <TR>"
        "           <TD COLNAME='C2' ROWSPAN='2'>3 / 2</TD>"
        "           <TD COLNAME='C3'>3 / 3</TD>"
        "       </TR>"
        "   </TBODY>"
        "</TABLE>"
    )

    table_tag = BeautifulSoup(xml, "lxml-xml")

    expected = [
        {"c1": "1 / 1", "c2": "1 / 2", "c3": "1 / 3"},
        {"c1": "1 / 1", "c2": "1 / 2", "c3": "2 / 3"},
        {"c1": "1 / 1", "c2": "3 / 2", "c3": "3 / 3"},
    ]

    assert normalize_rowspan(table_tag) == expected


def test_normalize_rowspan_colspan():
    xml = (
        "<TABLE>"
        "   <TBODY>"
        "       <TR>"
        "           <TD COLNAME='C1'>1 / 1</TD>"
        "           <TD COLNAME='C2'>1 / 2</TD>"
        "       </TR>"
        "       <TR>"
        "           <TD COLNAME='C1' COLSPAN='2'>2 / 1</TD>"
        "       </TR>"
        "   </TBODY>"
        "</TABLE>"
    )

    table_tag = BeautifulSoup(xml, "lxml-xml")

    expected = [
        {"c1": "1 / 1", "c2": "1 / 2"},
        {"c1": "2 / 1"},
    ]

    assert normalize_rowspan(table_tag) == expected
