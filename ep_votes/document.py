import re
from enum import Enum, auto
from dataclasses import dataclass


class Type(Enum):
    A = auto()  # report
    B = auto()  # motion for resolution
    RC = auto()  # joint motion for resolution


@dataclass
class Reference:
    type: Type
    term: int
    number: int
    year: int


def parse_ref(ref):
    regex = r"^(A|B|RC)(?:-B)?(\d{1,2})-(\d{4})\/(\d{4})$"
    match = re.search(regex, ref)

    if not match:
        raise ValueError("Unrecognized document reference format")

    return Reference(
        type=Type[match.group(1)],
        term=int(match.group(2)),
        number=int(match.group(3)),
        year=int(match.group(4)),
    )


def url(ref):
    BASE = "https://www.europarl.europa.eu/doceo/document"
    filepath = f"/{ref.type.name}-{ref.term}-{ref.year:04}-{ref.number:04}_EN.html"
    return BASE + filepath
