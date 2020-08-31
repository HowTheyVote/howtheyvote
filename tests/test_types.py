import pytest
from ep_votes.models import Country, Group, DocReference, DocType, Member


def test_country_from_str():
    assert Country.from_str("Austria") == Country.AT


def test_country_from_str_alternates():
    assert Country.from_str("Czech Republic") == Country.CZ
    assert Country.from_str("Czechia") == Country.CZ


def test_group_from_str():
    assert Group.from_str("Group of the Greens/European Free Alliance") == Group.GREENS


def test_group_from_str_short():
    assert Group.from_str("GREENS") == Group.GREENS


def test_doc_reference_from_str():
    ref = DocReference(type=DocType.B, term=9, number=154, year=2019)
    assert DocReference.from_str("B9-0154/2019") == ref


def test_doc_reference_from_str_malformed():
    with pytest.raises(ValueError):
        DocReference.from_str("XYZ")


def test_member_parse_full_name():
    assert Member.parse_full_name("Katarina BARLEY") == ("Katarina", "BARLEY")


def test_member_parse_full_name_multiple_first_names():
    assert Member.parse_full_name("Marek Paweł BALT") == ("Marek Paweł", "BALT")
    assert Member.parse_full_name("Anna-Michelle ASIMAKOPOULOU") == (
        "Anna-Michelle",
        "ASIMAKOPOULOU",
    )


def test_member_parse_full_name_multiple_last_names():
    assert Member.parse_full_name("Pablo ARIAS ECHEVERRÍA") == (
        "Pablo",
        "ARIAS ECHEVERRÍA",
    )
    assert Member.parse_full_name("Attila ARA-KOVÁCS") == ("Attila", "ARA-KOVÁCS")


def test_member_parse_full_name_middle_initial():
    assert Member.parse_full_name("Jakop G. DALUNDE") == ("Jakop G.", "DALUNDE")


def test_member_parse_full_name_special_affixes():
    assert Member.parse_full_name("David McALLISTER") == ("David", "McALLISTER")
    assert Member.parse_full_name("Pilar del CASTILLO VERA") == (
        "Pilar",
        "del CASTILLO VERA",
    )
    assert Member.parse_full_name("Rosa d'AMATO") == ("Rosa", "d'AMATO")
    assert Member.parse_full_name("Peter van DALEN") == ("Peter", "van DALEN")
    assert Member.parse_full_name("Ursula von der LEYEN") == ("Ursula", "von der LEYEN")
    assert Member.parse_full_name("Sophie in ’t VELD") == ("Sophie", "in ’t VELD")


def test_member_parse_full_name_special_chars():
    assert Member.parse_full_name("Jörg MEUTHEN") == ("Jörg", "MEUTHEN")
    assert Member.parse_full_name("Leïla CHAIBI") == ("Leïla", "CHAIBI")
    assert Member.parse_full_name("Stéphane SÉJOURNÉ") == ("Stéphane", "SÉJOURNÉ")


def test_member_parse_full_name_aristocratic_title():
    assert Member.parse_full_name("William (The Earl of) DARTMOUTH") == (
        "William",
        "(The Earl of) DARTMOUTH",
    )
