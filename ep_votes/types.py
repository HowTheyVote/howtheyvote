import re
from enum import Enum, auto
from dataclasses import dataclass
from unidecode import unidecode

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

    @staticmethod
    def from_str(name):
        return Country[COUNTRY_NAMES[name]]


GROUP_NAMES = {
    "Group of the European People's Party (Christian Democrats)": "EPP",
    "Non-attached Members": "NI",
    "Identity and Democracy Group": "ID",
    "Group of the Progressive Alliance of Socialists and Democrats in the European Parliament": "SD",  # noqa: E501
    "European Conservatives and Reformists Group": "ECR",
    "Group of the Greens/European Free Alliance": "GREENS",
    "Renew Europe Group": "RENEW",
    "Group of the European United Left - Nordic Green Left": "GUE",
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

    @staticmethod
    def from_str(name):
        return Group[GROUP_NAMES[name]]


class Type(Enum):
    A = auto()  # report
    B = auto()  # motion for resolution
    RC = auto()  # joint motion for resolution


@dataclass
class DocReference:
    type: Type
    term: int
    number: int
    year: int

    @staticmethod
    def from_str(ref):
        regex = r"^(A|B|RC)(?:-B)?(\d{1,2})-(\d{4})\/(\d{4})$"
        match = re.search(regex, ref)

        if not match:
            raise ValueError("Unrecognized document reference format")

        return DocReference(
            type=Type[match.group(1)],
            term=int(match.group(2)),
            number=int(match.group(3)),
            year=int(match.group(4)),
        )

    def url(self):
        BASE = "https://www.europarl.europa.eu/doceo/document"
        path = f"/{self.type.name}-{self.term}-{self.year:04}-{self.number:04}_EN.html"
        return BASE + path


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
    first_name: str
    last_name: str
    country: Country
    group: Group
    europarl_website_id: int

    @staticmethod
    def parse_full_name(name):
        first = r"(?P<first>[A-Za-z\-\'\s\.]+?)"
        affix = r"(?:\s|" + "|".join(NAME_AFFIXES) + r")*"
        last = r"(?P<last>" + affix + r"[A-Z\-\'\s]+)"

        regex = r"^" + first + r"\s" + last + r"$"
        match = re.search(regex, unidecode(name))

        # In order to keep special characters, use the
        # start/end indices of match groups with the
        # original name
        return name[: match.end("first")], name[match.start("last") :]
