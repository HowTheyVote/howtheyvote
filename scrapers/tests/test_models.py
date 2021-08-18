import pytest
from ep_votes.models import (
    Country,
    Group,
    MemberInfo,
    Vote,
    VoteResult,
    VoteType,
)


def test_country_from_str():
    assert Country.from_str("Austria") == Country.AT


def test_country_from_str_alternates():
    assert Country.from_str("Czech Republic") == Country.CZ
    assert Country.from_str("Czechia") == Country.CZ


def test_group_from_str():
    assert Group.from_str("Group of the Greens/European Free Alliance") == Group.GREENS


def test_group_from_str_short():
    assert Group.from_str("GREENS") == Group.GREENS


def test_member_info_parse_full_name():
    assert MemberInfo.parse_full_name("Katarina BARLEY") == ("Katarina", "BARLEY")


def test_member_info_parse_full_name_multiple_first_names():
    assert MemberInfo.parse_full_name("Marek Paweł BALT") == ("Marek Paweł", "BALT")
    assert MemberInfo.parse_full_name("Anna-Michelle ASIMAKOPOULOU") == (
        "Anna-Michelle",
        "ASIMAKOPOULOU",
    )


def test_member_info_parse_full_name_multiple_last_names():
    assert MemberInfo.parse_full_name("Pablo ARIAS ECHEVERRÍA") == (
        "Pablo",
        "ARIAS ECHEVERRÍA",
    )
    assert MemberInfo.parse_full_name("Attila ARA-KOVÁCS") == ("Attila", "ARA-KOVÁCS")


def test_member_info_parse_full_name_not_all_caps_last_name():
    assert MemberInfo.parse_full_name("Ramon TREMOSA i BALCELLS") == (
        "Ramon",
        "TREMOSA i BALCELLS",
    )


def test_member_info_parse_full_name_middle_initial():
    assert MemberInfo.parse_full_name("Jakop G. DALUNDE") == ("Jakop G.", "DALUNDE")


def test_member_info_parse_full_name_special_affixes():
    assert MemberInfo.parse_full_name("David McALLISTER") == ("David", "McALLISTER")
    assert MemberInfo.parse_full_name("Pilar del CASTILLO VERA") == (
        "Pilar",
        "del CASTILLO VERA",
    )
    assert MemberInfo.parse_full_name("Rosa d'AMATO") == ("Rosa", "d'AMATO")
    assert MemberInfo.parse_full_name("Peter van DALEN") == ("Peter", "van DALEN")
    assert MemberInfo.parse_full_name("Ursula von der LEYEN") == (
        "Ursula",
        "von der LEYEN",
    )
    assert MemberInfo.parse_full_name("Sophie in ’t VELD") == ("Sophie", "in ’t VELD")


def test_member_info_info_parse_full_name_special_chars():
    assert MemberInfo.parse_full_name("Jörg MEUTHEN") == ("Jörg", "MEUTHEN")
    assert MemberInfo.parse_full_name("Leïla CHAIBI") == ("Leïla", "CHAIBI")
    assert MemberInfo.parse_full_name("Stéphane SÉJOURNÉ") == ("Stéphane", "SÉJOURNÉ")


def test_member_info_parse_full_name_aristocratic_title():
    assert MemberInfo.parse_full_name("William (The Earl of) DARTMOUTH") == (
        "William",
        "(The Earl of) DARTMOUTH",
    )


def test_vote_result_from_str():
    assert VoteResult.from_str("+") == VoteResult.ADOPTED
    assert VoteResult.from_str("-") == VoteResult.REJECTED

    with pytest.raises(ValueError):
        VoteResult.from_str("↓")


def _vote_factory(**data):
    default = {
        "subject": "Subject",
        "subheading": "Subheading",
        "author": "original text",
        "type": VoteType.PRIMARY,
        "result": VoteResult.ADOPTED,
        "amendment": None,
        "split_part": None,
        "remarks": None,
    }

    return Vote(**(default | data))


def test_vote_formatted_basic_split_vote():
    vote = _vote_factory(
        type=VoteType.SEPARATE,
        subject="§ 1",
        split_part=1,
    )

    assert vote.formatted == "§ 1/1"


def test_vote_formatted_basic_split_vote_with_recital():
    vote = _vote_factory(
        type=VoteType.SEPARATE,
        subject="Recital A",
        split_part=1,
    )

    assert vote.formatted == "Considérant A/1"


def test_vote_formatted_basic_split_vote_with_citation():
    vote = _vote_factory(
        type=VoteType.SEPARATE,
        subject="Citation 1",
        split_part=1,
    )

    assert vote.formatted == "Visa 1/1"


def test_vote_formatted_basic_split_vote_with_part():
    vote = _vote_factory(
        type=VoteType.SEPARATE,
        subject="Part I",
        split_part=1,
    )

    assert vote.formatted == "Partie I/1"


def test_vote_formatted_basic_split_vote_with_annex():
    vote = _vote_factory(
        type=VoteType.SEPARATE,
        subject="Annex, Part I",
        split_part=1,
    )

    assert vote.formatted == "Annexe, Partie I/1"


def test_vote_formatted_basic_split_vote_with_appendix():
    vote = _vote_factory(
        type=VoteType.SEPARATE,
        subject="Appendix 1",
        split_part=1,
    )

    assert vote.formatted == "Appendice 1/1"


def test_vote_formatted_amendment_with_coresponding_part():
    vote = _vote_factory(
        type=VoteType.AMENDMENT,
        amendment="1CP",
    )

    assert vote.formatted == "Am 1PC"


def test_vote_formatted_amendment_with_coresponding_part_and_number():
    vote = _vote_factory(
        type=VoteType.AMENDMENT,
        amendment="1CP1",
    )

    assert vote.formatted == "Am 1PC1"


def test_vote_formatted_amendment_with_compromise_amendment():
    vote = _vote_factory(
        type=VoteType.AMENDMENT,
        amendment="1CA",
    )

    assert vote.formatted == "Am 1AC"


def test_vote_formatted_deleted_amendment():
    vote = _vote_factory(
        type=VoteType.AMENDMENT,
        amendment="1D",
    )

    assert vote.formatted == "Am 1S"


def test_vote_formatted_amendment():
    vote = _vote_factory(
        type=VoteType.AMENDMENT,
        amendment="1",
    )

    assert vote.formatted == "Am 1"


def test_vote_formatted_amendment_range():
    vote = _vote_factory(
        type=VoteType.AMENDMENT,
        amendment="1 - 2",
    )

    assert vote.formatted == "Am 1 - 2"


def test_vote_formatted_resolution():
    vote = _vote_factory(
        type=VoteType.PRIMARY,
        subject="Resolution (as a whole)",
    )

    assert vote.formatted == "Proposition de résolution"


def test_vote_formatted_motion_for_resolution():
    vote = _vote_factory(
        type=VoteType.PRIMARY,
        subject="Motion for resolution (as a whole)",
    )

    assert vote.formatted == "Proposition de résolution"


def test_vote_formatted_motion_for_resolution_with_committee():
    vote = _vote_factory(
        type=VoteType.PRIMARY,
        subject="Motion for a resolution (EMPL committee) (as a whole)",
    )

    assert vote.formatted == "Proposition de résolution"


def test_vote_formatted_commision_proposal():
    vote = _vote_factory(
        type=VoteType.PRIMARY,
        subject="Commission proposal",
    )

    assert vote.formatted == "Proposition de la Commission"


def test_vote_formatted_single_vote():
    vote = _vote_factory(type=VoteType.PRIMARY, subject="Single vote")

    assert vote.formatted == "Vote unique"


def test_vote_reference_in_subject():
    vote = _vote_factory(subject="A9-0123/2021", subheading="B9-4567/2021")

    assert vote.reference == "A9-0123/2021"


def test_vote_reference_in_subheading():
    vote = _vote_factory(subheading="B9-4567/2021")

    assert vote.reference == "B9-4567/2021"


def test_vote_reference_not_present():
    vote = _vote_factory()

    assert vote.reference is None
