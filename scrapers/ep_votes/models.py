import re
from enum import Enum, auto
from dataclasses import dataclass
from unidecode import unidecode
from typing import Optional, Tuple, List
from datetime import date
from .helpers import extract_reference

COUNTRY_NAMES = {
    "Austria": "AT",
    "Belgium": "BE",
    "Bulgaria": "BG",
    "Cyprus": "CY",
    "Czech Republic": "CZ",
    "Czechia": "CZ",
    "Germany": "DE",
    "Denmark": "DK",
    "Estonia": "EE",
    "Spain": "ES",
    "Finland": "FI",
    "France": "FR",
    "United Kingdom": "GB",
    "Greece": "GR",
    "Croatia": "HR",
    "Hungary": "HU",
    "Ireland": "IE",
    "Italy": "IT",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Latvia": "LV",
    "Malta": "MT",
    "Netherlands": "NL",
    "Poland": "PL",
    "Portugal": "PT",
    "Romania": "RO",
    "Sweden": "SE",
    "Slovenia": "SI",
    "Slovakia": "SK",
}


class Country(Enum):
    AT = auto()
    BE = auto()
    BG = auto()
    CY = auto()
    CZ = auto()
    DE = auto()
    DK = auto()
    EE = auto()
    ES = auto()
    FI = auto()
    FR = auto()
    GB = auto()
    GR = auto()
    HR = auto()
    HU = auto()
    IE = auto()
    IT = auto()
    LT = auto()
    LU = auto()
    LV = auto()
    MT = auto()
    NL = auto()
    PL = auto()
    PT = auto()
    RO = auto()
    SE = auto()
    SI = auto()
    SK = auto()

    @classmethod
    def from_str(cls, name: str) -> "Country":
        return cls[COUNTRY_NAMES[name]]


GROUP_NAMES = {
    # 9th parliamentary term
    "Group of the European People's Party (Christian Democrats)": "EPP",
    "Non-attached Members": "NI",
    "Identity and Democracy Group": "ID",
    "Group of the Progressive Alliance of Socialists and Democrats in the European Parliament": "SD",  # noqa: E501
    "European Conservatives and Reformists Group": "ECR",
    "Group of the Greens/European Free Alliance": "GREENS",
    "Renew Europe Group": "RENEW",
    "The Left group in the European Parliament - GUE/NGL": "LEFT",
    # 8th parliamentary term
    "Europe of Freedom and Direct Democracy Group": "EFDD",
    "Group of the Alliance of Liberals and Democrats for Europe": "ALDE",
    "Confederal Group of the European United Left - Nordic Green Left": "GUE",
    "Group of the European United Left - Nordic Green Left": "GUE",
    "Europe of Nations and Freedom Group": "ENF",
}


class Group(Enum):
    EPP = auto()
    SD = auto()
    GREENS = auto()
    RENEW = auto()
    LEFT = auto()
    ECR = auto()
    ID = auto()
    NI = auto()

    ALDE = auto()
    GUE = auto()
    EFDD = auto()
    ENF = auto()

    @classmethod
    def from_str(cls, name: str) -> "Group":
        if name in cls.__members__:
            return cls[name]

        return cls[GROUP_NAMES[name]]


@dataclass
class Member:
    web_id: int
    terms: List[int]


NAME_AFFIXES = [
    "de",
    "del",
    "della",
    "di",
    "du",
    "d'",
    "M'",
    "Mac",
    "Mc",
    "van",
    "von",
    "der",
    "zu",
    "und",
    "in 't",
]


@dataclass
class MemberInfo:
    first_name: Optional[str]
    last_name: Optional[str]
    country: Country
    date_of_birth: Optional[date]

    @staticmethod
    def parse_full_name(name: str) -> Tuple[Optional[str], Optional[str]]:
        # Last names are indicated on the parliament with upper case letters.
        # If we find two upper case letters following each other we found the
        # end of the first name. There are also parts like "de" that can be
        # part of the first or the last name. If we find two capitalized letters
        # after such a word, it belongs to the last name. Otherwise it belongs to
        # the first name. Affixes of last names can also contain special characters
        # and have multiple parts (see NAME_AFFIXES).
        # Brackets are always an indicator for the end of the first name.
        # e.g. William -- (The Earl of) DARTMOUTH
        first = r"(?P<first>^(?:(?!\s((?:[\(A-Z]){2}|['a-z\s]*(?:[A-Z]){2})).)+)"

        affix = r"(?:\s|" + "|".join(NAME_AFFIXES) + r")*"
        aristocratic_title = r"(?:\(.*\)\s)?"
        last = r"(?P<last>" + aristocratic_title + affix + r"[[A-Za-z\-\'\s]+)"

        regex = r"^" + first + r"\s" + last + r"$"
        match = re.search(regex, unidecode(name))

        if match is None:
            return (None, None)

        # In order to keep special characters, use the
        # start/end indices of match groups with the
        # original name
        return name[: match.end("first")], name[match.start("last") :]


@dataclass
class GroupMembership:
    group: Group
    term: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class Position(Enum):
    FOR = auto()
    AGAINST = auto()
    ABSTENTION = auto()


@dataclass
class Voting:
    doceo_member_id: int
    name: str
    position: Position


@dataclass
class VotingList:
    description: str
    reference: Optional[str]
    doceo_vote_id: Optional[int]
    votings: List[Voting]


class VoteType(Enum):
    PRIMARY = auto()
    AMENDMENT = auto()
    SEPARATE = auto()


class VoteResult(Enum):
    ADOPTED = auto()
    REJECTED = auto()

    @classmethod
    def from_str(cls, string: str) -> "VoteResult":
        if string == "+":
            return cls.ADOPTED

        if string == "-":
            return cls.REJECTED

        raise ValueError("Vote must be either be adopted or rejected.")


@dataclass
class Vote:
    author: Optional[str]
    subject: Optional[str]
    result: VoteResult
    split_part: Optional[int]
    amendment: Optional[str]
    type: VoteType
    remarks: Optional[str]
    subheading: Optional[str]
    final: bool

    @property
    def formatted(self) -> str:
        formatted = ""

        if self.type == VoteType.PRIMARY:
            subject = str(self.subject)

            if subject == "Commission proposal":
                return "Proposition de la Commission"

            if "(as a whole)" in subject:
                return "Proposition de résolution"

            if subject == "Single vote":
                return "Vote unique"

        if self.type == VoteType.SEPARATE:
            formatted = str(self.subject)
            formatted = formatted.replace("Recital", "Considérant")
            formatted = formatted.replace("Citation", "Visa")
            formatted = formatted.replace("Part", "Partie")
            formatted = formatted.replace("Annex", "Annexe")
            formatted = formatted.replace("Appendix", "Appendice")

        if self.type == VoteType.AMENDMENT:
            formatted = "Am " + str(self.amendment)
            formatted = formatted.replace("CP", "PC")
            formatted = formatted.replace("CA", "AC")
            formatted = formatted.replace("D", "S")

        if self.split_part is not None:
            formatted = formatted + "/" + str(self.split_part)

        return formatted

    @property
    def reference(self) -> Optional[str]:
        reference = extract_reference(self.subject)
        if reference:
            return reference
        reference = extract_reference(self.subheading)
        if reference:
            return reference
        return None


@dataclass
class VoteCollection:
    title: str
    reference: Optional[str]
    votes: List[Vote]


class Location(Enum):
    BRUSSELS = auto()
    STRASBOURG = auto()


@dataclass
class Session:
    start_date: date
    end_date: date
    location: Location
