import pytest

from howtheyvote.helpers import (
    ProcedureReference,
    Reference,
    flatten_dict,
    get_normalized_docstring,
    parse_procedure_reference,
    parse_reference,
    subset_dict,
)
from howtheyvote.models import DocumentType, ProcedureType


def test_parse_reference():
    ref = parse_reference("A9-1234/2024")
    assert ref == Reference(type=DocumentType.A, term=9, number=1234, year=2024)

    ref = parse_reference("B9-1234/2024")
    assert ref == Reference(type=DocumentType.B, term=9, number=1234, year=2024)

    ref = parse_reference("RC-B9-1234/2024")
    assert ref == Reference(type=DocumentType.RC, term=9, number=1234, year=2024)

    ref = parse_reference("C9-1234/2024")
    assert ref == Reference(type=DocumentType.C, term=9, number=1234, year=2024)

    ref = parse_reference("A9-1234/2024/rev")
    assert ref == Reference(type=DocumentType.A, term=9, number=1234, year=2024)

    ref = parse_reference("A9-1234/2024/rev1")
    assert ref == Reference(type=DocumentType.A, term=9, number=1234, year=2024)

    ref = parse_reference("a9-1234/2024")
    assert ref == Reference(type=DocumentType.A, term=9, number=1234, year=2024)

    with pytest.raises(ValueError, match="Invalid reference:"):
        parse_reference("D9-1234/2024")

    with pytest.raises(ValueError, match="Invalid reference:"):
        parse_reference("A9-1234/24")


def test_parse_procedure_reference():
    ref = parse_procedure_reference("2021/0106(COD)")
    assert ref == ProcedureReference(type=ProcedureType.COD, year=2021, number="0106")

    # In most cases the sequential number consists only of digits, but in some cases
    # it can also contain a letter at the end.
    ref = parse_procedure_reference("2023/0038M(NLE)")
    assert ref == ProcedureReference(type=ProcedureType.NLE, year=2023, number="0038M")

    ref = parse_procedure_reference("2023/0201R(APP)")
    assert ref == ProcedureReference(type=ProcedureType.APP, year=2023, number="0201R")

    with pytest.raises(ValueError, match="Invalid procedure reference:"):
        parse_procedure_reference("2021/106(COD)")


def test_flatten_dict():
    data = {
        "position": "FOR",
        "member": {
            "first_name": "Jane",
            "last_name": "Smith",
            "country": {
                "code": "FRA",
                "label": "France",
            },
        },
    }

    flattened = {
        "position": "FOR",
        "member.first_name": "Jane",
        "member.last_name": "Smith",
        "member.country.code": "FRA",
        "member.country.label": "France",
    }

    assert flatten_dict(data) == flattened


def test_subset_dict():
    data = {
        "member.id": 123,
        "member.first_name": "Jane",
        "member.last_name": "Smith",
        "member.twitter": "@janesmith",
        "member.photo_url": "https://example.org/janesmith.jpg",
    }

    keys = {"member.id", "member.first_name", "member.last_name"}

    expected = {
        "member.id": 123,
        "member.first_name": "Jane",
        "member.last_name": "Smith",
    }

    assert subset_dict(data, keys) == expected


def test_get_normalized_docstring():
    class TestClass:
        """Lorem ipsum dolor sit amet, consectetuer adipiscing elit.
        Aenean commodo ligula eget dolor.

        Aenean massa. Cum sociis natoque penatibus et magnis dis parturient
        montes, nascetur ridiculus mus."""

    expected = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor.\n\nAenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus."
    assert get_normalized_docstring(TestClass) == expected
