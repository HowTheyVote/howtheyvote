import re
from enum import Enum, auto
from dataclasses import dataclass
from unidecode import unidecode
from typing import Set, Optional, Tuple, List
from datetime import date

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
    "Group of the European People's Party (Christian Democrats)": "EPP",
    "Non-attached Members": "NI",
    "Identity and Democracy Group": "ID",
    "Group of the Progressive Alliance of Socialists and Democrats in the European Parliament": "SD",  # noqa: E501
    "European Conservatives and Reformists Group": "ECR",
    "Group of the Greens/European Free Alliance": "GREENS",
    "Renew Europe Group": "RENEW",
    "Group of the European United Left - Nordic Green Left": "GUE",
    "Europe of Freedom and Direct Democracy Group": "EFDD",
}


class Group(Enum):
    EPP = auto()
    SD = auto()
    GREENS = auto()
    RENEW = auto()
    GUE = auto()
    ECR = auto()
    ID = auto()
    NI = auto()
    EFDD = auto()

    @classmethod
    def from_str(cls, name: str) -> "Group":
        if name in cls.__members__:
            return cls[name]

        return cls[GROUP_NAMES[name]]


class DocType(Enum):
    A = auto()  # report
    B = auto()  # motion for resolution
    RC = auto()  # joint motion for resolution


@dataclass
class DocReference:
    type: DocType
    term: int
    number: int
    year: int

    @classmethod
    def from_str(cls, ref: str) -> "DocReference":
        regex = r"^(A|B|RC)(?:-B)?(\d{1,2})-(\d{4})\/(\d{4})$"
        match = re.search(regex, ref)

        if not match:
            raise ValueError("Unrecognized document reference format")

        return cls(
            type=DocType[match.group(1)],
            term=int(match.group(2)),
            number=int(match.group(3)),
            year=int(match.group(4)),
        )


@dataclass
class Doc:
    title: str
    reference: DocReference


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
class Member:
    web_id: int
    terms: Optional[Set[int]] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[Country] = None
    group: Optional[Group] = None
    date_of_birth: Optional[date] = None

    @staticmethod
    def parse_full_name(name: str) -> Tuple[Optional[str], Optional[str]]:
        first = r"(?P<first>[A-Za-z\-\'\s\.]+?)"
        affix = r"(?:\s|" + "|".join(NAME_AFFIXES) + r")*"
        aristocratic_title = r"(?:\(.*\)\s)?"
        last = r"(?P<last>" + aristocratic_title + affix + r"[A-Z\-\'\s]+)"

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
class Vote:
    doceo_vote_id: int
    date: date
    votings: List[Voting]
    description: Optional[str] = None
    reference: Optional[DocReference] = None
