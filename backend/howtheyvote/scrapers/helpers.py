import re

from structlog import get_logger
from unidecode import unidecode

from ..helpers import REFERENCE_REGEX
from ..models import Fragment

log = get_logger(__name__)

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


def parse_full_name(name: str) -> tuple[str | None, str | None]:
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
    last = r"(?P<last>" + aristocratic_title + affix + r"[A-Za-z\-\'\s]+)"

    regex = r"^" + first + r"\s" + last + r"$"
    match = re.search(regex, unidecode(name))

    if match is None:
        return (None, None)

    # In order to keep special characters, use the
    # start/end indices of match groups with the
    # original name
    return name[: match.end("first")], name[match.start("last") :]


def normalize_whitespace(string: str) -> str:
    return re.sub(r"\s+", " ", string).strip()


def normalize_name(name: str) -> str:
    return unidecode(name.lower()).replace("-", " ")


def parse_rcv_text(
    text: str, extract_english: bool = False
) -> tuple[str | None, str | None, str | None, str | None]:
    delimiter = " - "

    # Replace different types of dashes with standard dashes
    text = re.sub(r"\s[-–—]\s", " - ", text)

    parts = [part.strip() for part in text.split(delimiter)]
    before_reference = []
    after_reference = []

    reference = None
    description = None
    rapporteur = None
    title = None

    while parts:
        part = parts.pop(0)
        match = re.fullmatch(REFERENCE_REGEX, part)

        if match:
            reference = match.group(0)
            break
        else:
            before_reference.append(part)

    after_reference = parts

    # In many cases, the RCV description contains the actual title
    # in 3 languages (French, English, and German). If the number of
    # parts (seperated by dashes) is a multiple of 3, this is likely
    # the case. If not, we don’t know for sure.
    if extract_english:
        if before_reference and len(before_reference) % 3 == 0:
            # Extract the English translation of the title
            multiplier = len(before_reference) // 3
            start = 1 * multiplier
            end = 2 * multiplier
            title = delimiter.join(before_reference[start:end])
        elif before_reference and not reference:
            title = delimiter.join(before_reference)
    else:
        if before_reference:
            title = delimiter.join(before_reference)
        else:
            title = None

    # If the vote is related to a report (reference starts with "A"), the
    # part after the reference contains the name of the rapporteur
    if reference and reference.startswith("A"):
        rapporteur = after_reference.pop(0)

    if after_reference:
        description = delimiter.join(after_reference)
    else:
        description = None

    return (title, rapporteur, reference, description)


def fill_missing_by_reference(fragments: list[Fragment], key: str) -> list[Fragment]:
    # If the list contains multiple votes on the same topic, usually the first has
    # a full title, the remaining votes only contain the (same) reference. We loop
    # through and try to populate missing titles based on references.
    by_reference = {}

    for fragment in fragments:
        data = fragment.data
        ref = data.get("reference")
        value = data.get(key)

        if ref and value:
            by_reference[ref] = value

    for fragment in fragments:
        data = fragment.data
        ref = data.get("reference")
        if not data.get(key) and ref:
            value = by_reference.get(ref)
            if value:
                data[key] = value

    return fragments
