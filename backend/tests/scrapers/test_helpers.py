import pytest

from howtheyvote.models import (
    AmendmentAuthorCommittee,
    AmendmentAuthorGroup,
    AmendmentAuthorMembers,
    AmendmentAuthorOrally,
    AmendmentAuthorOriginalText,
    AmendmentAuthorRapporteur,
    Committee,
    Fragment,
    Group,
    ProcedureStage,
)
from howtheyvote.scrapers.common import ScrapingError
from howtheyvote.scrapers.helpers import (
    fill_missing_by_reference,
    normalize_name,
    normalize_whitespace,
    parse_amendment_authors,
    parse_dlv_title,
    parse_full_name,
    parse_rcv_text,
)


def test_parse_full_name():
    assert parse_full_name("Katarina BARLEY") == ("Katarina", "BARLEY")


def test_parse_full_name_multiple_first_names():
    assert parse_full_name("Marek Paweł BALT") == ("Marek Paweł", "BALT")
    assert parse_full_name("Anna-Michelle ASIMAKOPOULOU") == ("Anna-Michelle", "ASIMAKOPOULOU")


def test_parse_full_name_multiple_last_names():
    assert parse_full_name("Pablo ARIAS ECHEVERRÍA") == ("Pablo", "ARIAS ECHEVERRÍA")
    assert parse_full_name("Attila ARA-KOVÁCS") == ("Attila", "ARA-KOVÁCS")


def test_parse_full_name_not_all_caps_last_name():
    assert parse_full_name("Ramon TREMOSA i BALCELLS") == ("Ramon", "TREMOSA i BALCELLS")


def test_parse_full_name_all_lowercase_word_in_first_name():
    assert parse_full_name("Francisco de Paula GAMBUS MILLET") == (
        "Francisco de Paula",
        "GAMBUS MILLET",
    )


def test_parse_full_name_middle_initial():
    assert parse_full_name("Jakop G. DALUNDE") == ("Jakop G.", "DALUNDE")


def test_parse_full_name_special_affixes():
    assert parse_full_name("David McALLISTER") == ("David", "McALLISTER")
    assert parse_full_name("Pilar del CASTILLO VERA") == ("Pilar", "del CASTILLO VERA")
    assert parse_full_name("Rosa d'AMATO") == ("Rosa", "d'AMATO")
    assert parse_full_name("Peter van DALEN") == ("Peter", "van DALEN")
    assert parse_full_name("Ursula von der LEYEN") == ("Ursula", "von der LEYEN")
    assert parse_full_name("Sophie in ’t VELD") == ("Sophie", "in ’t VELD")


def test_info_parse_full_name_special_chars():
    assert parse_full_name("Jörg MEUTHEN") == ("Jörg", "MEUTHEN")
    assert parse_full_name("Leïla CHAIBI") == ("Leïla", "CHAIBI")
    assert parse_full_name("Stéphane SÉJOURNÉ") == ("Stéphane", "SÉJOURNÉ")


def test_parse_full_name_aristocratic_title():
    assert parse_full_name("William (The Earl of) DARTMOUTH") == (
        "William",
        "(The Earl of) DARTMOUTH",
    )


def test_normalize_whitespace():
    assert normalize_whitespace("  Lorem ipsum  ") == "Lorem ipsum"
    assert normalize_whitespace("\n\nLorem ipsum\n\n") == "Lorem ipsum"
    assert normalize_whitespace("\t\tLorem ipsum\t\t") == "Lorem ipsum"
    assert normalize_whitespace("Lorem   ipsum") == "Lorem ipsum"
    assert normalize_whitespace("Lorem\n\nipsum") == "Lorem ipsum"


def test_normalize_name():
    assert normalize_name("Stéphane SÉJOURNÉ") == "stephane sejourne"
    assert normalize_name("Rosa d’AMATO") == "rosa d'amato"
    assert normalize_name("Attila ARA-KOVÁCS") == "attila ara kovacs"


def test_parse_rcv_text():
    actual = parse_rcv_text("Wednesday’s agenda – Request from the PPE Group")
    expected = ("Wednesday’s agenda - Request from the PPE Group", None, None, None)
    assert actual == expected

    actual = parse_rcv_text("Nature restoration – A9-0220/2023 – César Luena – Rejection")
    expected = ("Nature restoration", "César Luena", "A9-0220/2023", "Rejection")
    assert actual == expected

    actual = parse_rcv_text("A9-0220/2023 – César Luena – Commission proposal")
    expected = (None, "César Luena", "A9-0220/2023", "Commission proposal")
    assert actual == expected


def test_parse_rcv_text_extract_english():
    # Without a reference, rapporteur, description
    actual = parse_rcv_text(
        "Ordre du jour de mardi - Demande du groupe PPE - Tuesday’s Agenda - Request from the PPE Group - Tagesordnung für Dienstag - Antrag der PPE-Fraktion",
        extract_english=True,
    )
    expected = ("Tuesday’s Agenda - Request from the PPE Group", None, None, None)
    assert actual == expected

    # With title, reference, rapporteur, description
    actual = parse_rcv_text(
        "Aliments destinés à la consommation humaine: modification de certaines des directives \"petit-déjeuner\" - Foodstuffs for human consumption: amending certain 'Breakfast' Directives - Lebensmittel für die menschliche Ernährung: Änderung bestimmter „Frühstücksrichtlinien“ - A9-0385/2023 - Alexander Bernhuber - Amendements de la commission compétente - votes séparés - Am 12/1",
        extract_english=True,
    )
    expected = (
        "Foodstuffs for human consumption: amending certain 'Breakfast' Directives",
        "Alexander Bernhuber",
        "A9-0385/2023",
        "Amendements de la commission compétente - votes séparés - Am 12/1",
    )
    assert actual == expected

    # Without a title
    actual = parse_rcv_text(
        "A9-0385/2023 - Alexander Bernhuber - Amendements de la commission compétente - votes séparés - Am 12/2",
        extract_english=True,
    )
    expected = (
        None,
        "Alexander Bernhuber",
        "A9-0385/2023",
        "Amendements de la commission compétente - votes séparés - Am 12/2",
    )
    assert actual == expected

    # Note that the German translation has one additional dash in "Arzneimittel-Agentur"
    actual = parse_rcv_text(
        "Redevances et droits dus à l’Agence européenne des médicaments - Fees and charges payable to the European Medicines Agency - An die Europäische Arzneimittel-Agentur zu entrichtende Gebühren und Entgelte - A9-0224/2023 - Cristian-Silviu Buşoi - Accord provisoire - Am 64",
        extract_english=True,
    )
    expected = (
        "Fees and charges payable to the European Medicines Agency",
        "Cristian-Silviu Buşoi",
        "A9-0224/2023",
        "Accord provisoire - Am 64",
    )
    assert actual == expected

    # The heuristic fails in the following case and we simply use everything before the
    # reference as the title, even though that includes the German and French translations.
    # This case is quite (so rare that I couldn't find a real example ad hoc).
    actual = parse_rcv_text(
        "Français - English 1 - English 2 - Deutsch - John Doe - A9-1234/2023 - Am 123",
        extract_english=True,
    )
    expected = (
        "Français - English 1 - English 2 - Deutsch",
        "John Doe",
        "A9-1234/2023",
        "Am 123",
    )


def test_parse_dlv_title():
    title = "Election of the Commission"
    assert parse_dlv_title(title) == ("Election of the Commission", None)

    title = "Amending Regulation (EU) 2018/1806 as regards Vanuatu ***I"
    assert parse_dlv_title(title) == (
        "Amending Regulation (EU) 2018/1806 as regards Vanuatu",
        ProcedureStage.OLP_FIRST_READING,
    )

    title = "Amending Regulation (EU) 2018/1806 as regards Vanuatu *** I"
    assert parse_dlv_title(title) == (
        "Amending Regulation (EU) 2018/1806 as regards Vanuatu",
        ProcedureStage.OLP_FIRST_READING,
    )

    title = "Multiannual financial framework for the years 2021 to 2027 ***"
    assert parse_dlv_title(title) == (
        "Multiannual financial framework for the years 2021 to 2027",
        None,
    )


def test_fill_missing_by_reference():
    fragments = [
        Fragment(data={"reference": "A9-1234/2023", "title": "Title 1234"}),
        Fragment(data={"reference": "A9-1234/2023"}),
        Fragment(data={"reference": "A9-5678/2023"}),
        Fragment(data={"reference": "A9-5678/2023", "title": "Title 5678"}),
        Fragment(data={"reference": "A9-0000/2023"}),
    ]

    actual = fill_missing_by_reference(fragments, "title")
    expected = [
        Fragment(data={"reference": "A9-1234/2023", "title": "Title 1234"}),
        Fragment(data={"reference": "A9-1234/2023", "title": "Title 1234"}),
        Fragment(data={"reference": "A9-5678/2023", "title": "Title 5678"}),
        Fragment(data={"reference": "A9-5678/2023", "title": "Title 5678"}),
        Fragment(data={"reference": "A9-0000/2023"}),
    ]

    assert [f.data for f in actual] == [f.data for f in expected]


def test_parse_amendment_authors():
    # Single group author
    assert parse_amendment_authors("S&D") == [
        AmendmentAuthorGroup(group=Group["SD"]),
    ]
    assert parse_amendment_authors("The Left") == [
        AmendmentAuthorGroup(group=Group["GUE_NGL"]),
    ]

    # Mutliple group authors, comma as delimiter
    assert parse_amendment_authors("S&D, The Left") == [
        AmendmentAuthorGroup(group=Group["SD"]),
        AmendmentAuthorGroup(group=Group["GUE_NGL"]),
    ]

    # Multiple group authors, newline as delimiter
    assert parse_amendment_authors("The Left\nS&D") == [
        AmendmentAuthorGroup(group=Group["GUE_NGL"]),
        AmendmentAuthorGroup(group=Group["SD"]),
    ]

    # Multiple group authors, space as delimiter
    assert parse_amendment_authors("The Left S&D") == [
        AmendmentAuthorGroup(group=Group["GUE_NGL"]),
        AmendmentAuthorGroup(group=Group["SD"]),
    ]
    assert parse_amendment_authors("S&D The Left") == [
        AmendmentAuthorGroup(group=Group["SD"]),
        AmendmentAuthorGroup(group=Group["GUE_NGL"]),
    ]

    # Multiple group authors, mixed delimiters
    assert parse_amendment_authors("The Left\nS&D Verts/ALE") == [
        AmendmentAuthorGroup(group=Group["GUE_NGL"]),
        AmendmentAuthorGroup(group=Group["SD"]),
        AmendmentAuthorGroup(group=Group["GREEN_EFA"]),
    ]

    # Remove group suffix
    assert parse_amendment_authors("The Left Group S&D") == [
        AmendmentAuthorGroup(group=Group["GUE_NGL"]),
        AmendmentAuthorGroup(group=Group["SD"]),
    ]

    # Remove colon suffix
    assert parse_amendment_authors("Verts/ALE:") == [
        AmendmentAuthorGroup(group=Group["GREEN_EFA"]),
    ]

    # Remove compromise amendment suffix
    assert parse_amendment_authors("PPE (CA)") == [
        AmendmentAuthorGroup(group=Group["EPP"]),
    ]

    # Single committee author
    assert parse_amendment_authors("committee") == [
        AmendmentAuthorCommittee(committee=None),
    ]
    assert parse_amendment_authors("LIBE") == [
        AmendmentAuthorCommittee(committee=Committee["LIBE"]),
    ]

    # Members
    assert parse_amendment_authors("members") == [AmendmentAuthorMembers()]
    assert parse_amendment_authors("MEPs") == [AmendmentAuthorMembers()]

    # Original text
    assert parse_amendment_authors("original text") == [AmendmentAuthorOriginalText()]

    # Amended orally
    assert parse_amendment_authors("amended orally") == [AmendmentAuthorOrally()]

    # Rapporteur
    assert parse_amendment_authors("rapporteur") == [AmendmentAuthorRapporteur()]

    # Invalid author
    with pytest.raises(ScrapingError, match="Could not parse amendment authors: foo bar"):
        assert parse_amendment_authors("EPP FOO BAR")
