import re

from ..models import VotePositionCounts

NUMBER_REGEX = r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)"

INTEGER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}


def parse_int(text: str) -> int:
    """Converts a string representation of a number (either a string of digits or
    the English language word for integers up to 12) to a Python integer. Raises a
    ValueError if the input cannot be parsed."""
    if text.lower() in INTEGER_WORDS:
        return INTEGER_WORDS[text.lower()]

    return int(text)


VOTE_RESULT_REGEX_1 = re.compile(
    NUMBER_REGEX
    + r"\s(?:votes?|MEPs? voted)\s(?:in\sfavou?r|for),\s"
    + NUMBER_REGEX
    + r"\sagainst,?\s(?:and|with)\s"
    + NUMBER_REGEX
    + r"\s(?:abstentions?|abstained)",
    flags=re.I,
)

VOTE_RESULT_REGEX_2 = re.compile(
    r"(?:with|by)\s"
    + NUMBER_REGEX
    + r"(?:\svotes)?\sto\s"
    + NUMBER_REGEX
    + r"(?:\sagainst)?,?\s(?:and\s|with\s)?"
    + NUMBER_REGEX
    + r"\sabstentions?"
)


def extract_vote_results(text: str) -> list[VotePositionCounts]:
    matches = VOTE_RESULT_REGEX_1.finditer(text)
    results: list[VotePositionCounts] = []

    for match in matches:
        try:
            results.append(
                {
                    "FOR": parse_int(match.group(1)),
                    "AGAINST": parse_int(match.group(2)),
                    "ABSTENTION": parse_int(match.group(3)),
                    "DID_NOT_VOTE": 0,
                }
            )
        except ValueError:
            continue

    matches = VOTE_RESULT_REGEX_2.finditer(text)
    for match in matches:
        try:
            results.append(
                {
                    "FOR": parse_int(match.group(1)),
                    "AGAINST": parse_int(match.group(2)),
                    "ABSTENTION": parse_int(match.group(3)),
                    "DID_NOT_VOTE": 0,
                }
            )
        except ValueError:
            continue

    return results
