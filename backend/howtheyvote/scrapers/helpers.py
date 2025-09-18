import re

from structlog import get_logger
from unidecode import unidecode

from ..helpers import REFERENCE_REGEX
from ..models import (
    AmendmentAuthor,
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
from .common import ScrapingError

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


# See explanation as listed for example in session agendas:
# https://www.europarl.europa.eu/doceo/document/OJQ-10-2025-02-13_EN.pdf#page=2
PROCEDURE_STAGE_MAPPING = {
    r"\*\*\*\s?I": ProcedureStage.OLP_FIRST_READING,
    r"\*\*\*\s?II": ProcedureStage.OLP_SECOND_READING,
    r"\*\*\*\s?III": ProcedureStage.OLP_THIRD_READING,
    # These also occur in titles. However, we only strip the symbol from the title
    # and do not store the stage because these procedures don’t have multiple stages
    # in Parliament.
    r"\*\*\*": None,
    r"\*": None,
}


def parse_dlv_title(title: str) -> tuple[str, ProcedureStage | None]:
    title = title.strip()

    for stage_pattern, stage in PROCEDURE_STAGE_MAPPING.items():
        pattern = r"(?P<title>.*)\s+" + stage_pattern
        match = re.fullmatch(pattern, title)

        if match:
            return (match.group("title"), stage)

    return (title, None)


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


def parse_amendment_authors(raw_authors: str) -> list[AmendmentAuthor]:
    # The delimiters used in case of multiple authors aren't consistent and include spaces,
    # newlines, and commata. In case spaces it’s not trivial to detect if they are used as
    # a delimiter or as part of an author’s label, e.g. in "Renew The Left Members".
    raw_authors = raw_authors.lower()

    authors: list[AmendmentAuthor] = []

    if "\n" in raw_authors:
        delimiter = "\n"
    elif "," in raw_authors:
        delimiter = ","
    else:
        delimiter = None

    # If a newline or a comma is used as the delimiter, we can simply split the text
    if delimiter:
        for raw_author in raw_authors.split(delimiter):
            authors.extend(parse_amendment_authors(raw_author))

        return authors

    # If a space is used as the delimiter, we need to differentiate between spaces used as a
    # delimiter and spaces that a part of an author label. We start by splitting the text into
    # tokens. We then try to parse just the first token. If that fails, we try parsing the
    # frist two tokens as an author, etc.
    #
    # For example, in case of the raw authors string "Renew The Left Members":
    #
    # 1. Try to parse just "Renew" as an author.
    #    This succeeds, so we continue with the next token.
    # 2. Try to parse just "The" as an author.
    #    This fails, so we try including the next token.
    # 3. Try to parse "The Left" as an author.
    #    This succeeds, so we continue with the next token.
    # 4. Try to parse "Members" an an author.
    #    This succeeds. No tokens remain.
    tokens = raw_authors.strip().split(" ")

    # "CA" is short for "Compromise Amendment". We don’t have a use case for this, so for now
    # we simply ignore it
    tokens = [token for token in tokens if token != "(ca)"]

    while len(tokens) > 0:
        author = None

        for end in range(1, len(tokens) + 1):
            try:
                author = parse_amendment_author(" ".join(tokens[0:end]))
                tokens = tokens[end:]

                # Sometimes the source data contains a "Group" suffix after the group label,
                # e.g. "The Left Group" instead of just "The Left" which we have to also pop
                # from the tokens list
                if (
                    isinstance(author, AmendmentAuthorGroup)
                    and len(tokens) > 0
                    and tokens[0] == "group"
                ):
                    tokens = tokens[1:]

                break
            except ValueError:
                pass

        if author:
            authors.append(author)
        else:
            raise ScrapingError(f"Could not parse amendment authors: {' '.join(tokens)}")

    return authors


def parse_amendment_author(raw_author: str) -> AmendmentAuthor:
    raw_author = raw_author.strip().removesuffix(":")

    if raw_author == "original text":
        return AmendmentAuthorOriginalText()

    if raw_author == "members" or raw_author == "meps":
        return AmendmentAuthorMembers()

    if raw_author == "committee":
        return AmendmentAuthorCommittee(committee=None)

    if raw_author == "amended orally":
        return AmendmentAuthorOrally()

    if raw_author == "rapporteur":
        return AmendmentAuthorRapporteur()

    committee = Committee.get(raw_author.upper())

    if committee:
        return AmendmentAuthorCommittee(committee=committee)

    group = Group.from_label(raw_author)

    if group:
        return AmendmentAuthorGroup(group=group)

    raise ValueError(f"Invalid amendment author: {raw_author}")
