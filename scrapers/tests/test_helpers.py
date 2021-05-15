from bs4 import BeautifulSoup
from ep_votes.helpers import (
    removeprefix,
    removesuffix,
    normalize_table,
    normalize_whitespace,
    extract_reference,
)


def test_removeprefix():
    assert removeprefix("original-string", "prefix-") == "original-string"
    assert removeprefix("prefix-original-string", "prefix-") == "original-string"


def test_removesuffix():
    assert removesuffix("original-string", "-suffix") == "original-string"
    assert removesuffix("original-string-suffix", "-suffix") == "original-string"


def test_normalize_table():
    xml = (
        "<TABLE>"
        "   <TBODY>"
        "       <TR>"
        "           <TD COLNAME='C1'>Column 1</TD>"
        "           <TD COLNAME='C2'>Column 2</TD>"
        "       </TR>"
        "       <TR>"
        "           <TD COLNAME='C1'>1 / 1</TD>"
        "           <TD COLNAME='C2'>1 / 2</TD>"
        "       </TR>"
        "   </TBODY>"
        "</TABLE>"
    )

    table_tag = BeautifulSoup(xml, "lxml-xml")

    expected = [
        {"Column 1": "1 / 1", "Column 2": "1 / 2"},
    ]

    assert normalize_table(table_tag) == expected


def test_normalize_table_rowspan_a():
    xml = (
        "<TABLE>"
        "   <TBODY>"
        "       <TR>"
        "           <TD COLNAME='C1'>Column 1</TD>"
        "           <TD COLNAME='C2'>Column 2</TD>"
        "       </TR>"
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
        {"Column 1": "1 / 1", "Column 2": "1 / 2"},
        {"Column 1": "1 / 1", "Column 2": "2 / 2"},
        {"Column 1": "3 / 1", "Column 2": "3 / 2"},
    ]

    assert normalize_table(table_tag) == expected


def test_normalize_table_rowspan_b():
    xml = (
        "<TABLE>"
        "   <TBODY>"
        "       <TR>"
        "           <TD COLNAME='C1'>Column 1</TD>"
        "           <TD COLNAME='C2'>Column 2</TD>"
        "           <TD COLNAME='C3'>Column 3</TD>"
        "       </TR>"
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
        {"Column 1": "1 / 1", "Column 2": "1 / 2", "Column 3": "1 / 3"},
        {"Column 1": "1 / 1", "Column 2": "1 / 2", "Column 3": "2 / 3"},
        {"Column 1": "1 / 1", "Column 2": "3 / 2", "Column 3": "3 / 3"},
    ]

    assert normalize_table(table_tag) == expected


def test_normalize_table_colspan():
    xml = (
        "<TABLE>"
        "   <TBODY>"
        "       <TR>"
        "           <TD COLNAME='C1'>Column 1</TD>"
        "           <TD COLNAME='C2'>Column 2</TD>"
        "           <TD COLNAME='C3'>Column 3</TD>"
        "           <TD COLNAME='C4'>Column 4</TD>"
        "       </TR>"
        "       <TR>"
        "           <TD COLNAME='C1'>1 / 1</TD>"
        "           <TD COLNAME='C2' COLSPAN='2'>1 / 2</TD>"
        "           <TD COLNAME='C3'>1 / 4</TD>"
        "       </TR>"
        "   </TBODY>"
        "</TABLE>"
    )

    table_tag = BeautifulSoup(xml, "lxml-xml")

    expected = [
        {"Column 1": "1 / 1", "Column 2": "1 / 2", "Column 4": "1 / 4"},
    ]

    assert normalize_table(table_tag) == expected


def test_normalize_table_column_names():
    xml = (
        "<TABLE>"
        "   <TBODY>"
        "       <TR>"
        "           <TD COLNAME='C1'>Column 1</TD>"
        "           <TD COLNAME='C2'>Column 2</TD>"
        "           <TD COLNAME='C3'>Column 3</TD>"
        "       </TR>"
        "       <TR>"
        "           <TD COLNAME='C1'>1 / 1</TD>"
        "           <TD COLNAME='C2'>1 / 2</TD>"
        "           <TD COLNAME='C3'>1 / 3</TD>"
        "       </TR>"
        "       <TR>"
        "           <TD COLNAME='C1' COLSPAN='2'>2 / 1</TD>"
        "           <TD COLNAME='C2'>2 / 3</TD>"
        "       </TR>"
        "   </TBODY>"
        "</TABLE>"
    )

    table_tag = BeautifulSoup(xml, "lxml-xml")

    expected = [
        {"Column 1": "1 / 1", "Column 2": "1 / 2", "Column 3": "1 / 3"},
        {"Column 1": "2 / 1", "Column 3": "2 / 3"},
    ]

    assert normalize_table(table_tag) == expected


def test_normalize_whitespace_double_space():
    string = "Contrôle des pêches - Am 1-7, 10, 13-14, 17-36,  38-42,  78-80, 83, 87-94, 96-97"
    expected = (
        "Contrôle des pêches - Am 1-7, 10, 13-14, 17-36, 38-42, 78-80, 83, 87-94, 96-97"
    )

    assert normalize_whitespace(string) == expected


def test_normalize_whitespace_plus():
    assert normalize_whitespace("Am 342+343") == "Am 342 + 343"
    assert normalize_whitespace("Am 342 +343") == "Am 342 + 343"


def test_extract_references():
    string = "Proposal for a regulation (COM(2020)0818 - C9-0420/2020 - 2020/0358(COD))"
    assert extract_reference(string) == "C9-0420/2020"

    string = "Report: Sven Simon (A9-0002/2021)"
    assert extract_reference(string) == "A9-0002/2021"

    string = "RC-Bblabla"
    assert True


def test_extract_references_no_match():
    string = "No reference in this string"
    assert extract_reference(string) is None


def test_extract_references_none():
    assert extract_reference(None) is None
