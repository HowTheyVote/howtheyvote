import re
from enum import Enum, auto
from dataclasses import dataclass
from unidecode import unidecode
from typing import Optional, Tuple, List
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
    "The Left group in the European Parliament - GUE/NGL": "GUE",
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


class VoteType(Enum):
    FINAL = auto()
    SPLIT = auto()
    AMENDMENT = auto()
    AGENDA = auto()


@dataclass
class Vote:
    doceo_vote_id: int
    date: date
    votings: List[Voting]
    type: Optional[VoteType] = None
    subvote_description: Optional[str] = None
    description: Optional[str] = None
    reference: Optional[DocReference] = None


class ProcedureType(Enum):
    COD = auto()
    CNS = auto()
    APP = auto()
    BUD = auto()
    DEC = auto()
    BUI = auto()
    NLE = auto()
    AVC = auto()
    SYN = auto()
    INL = auto()
    INI = auto()
    RSP = auto()
    DCE = auto()
    COS = auto()
    REG = auto()
    IMM = auto()
    RSO = auto()
    INS = auto()
    ACI = auto()
    DEA = auto()
    RPS = auto()


@dataclass
class ProcedureReference:
    type: ProcedureType
    number: int
    year: int

    @classmethod
    def from_str(cls, ref: str) -> "ProcedureReference":
        regex = r"^(\d{4})\/(\d{4})\(([A-Z]{3})\)"
        match = re.search(regex, ref)

        if not match:
            raise ValueError("Unrecognized procedure reference format")

        return cls(
            year=int(match.group(1)),
            number=int(match.group(2)),
            type=ProcedureType[match.group(3)],
        )


@dataclass
class Procedure:
    title: str
    reference: ProcedureReference


@dataclass
# TODO: Rename to Vote once the current scraper
# implementation has been removed.
class VoteItem:
    subject: str


@dataclass
class VoteCollection:
    title: str
    votes: List[VoteItem]
