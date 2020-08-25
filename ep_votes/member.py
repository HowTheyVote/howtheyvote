import re
from dataclasses import dataclass
from unidecode import unidecode
from .country import Country
from .group import Group


@dataclass
class Member:
    first_name: str
    last_name: str
    country: Country
    group: Group
    term: int
    europarl_website_id: int


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


def parse_name(name):
    first = r"(?P<first>[A-Za-z\-\'\s\.]+?)"
    affix = r"(?:\s|" + "|".join(NAME_AFFIXES) + r")*"
    last = r"(?P<last>" + affix + r"[A-Z\-\'\s]+)"

    regex = r"^" + first + r"\s" + last + r"$"
    match = re.search(regex, unidecode(name))

    return match.group("first"), match.group("last")
