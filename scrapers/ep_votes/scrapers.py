from bs4 import BeautifulSoup, Tag
import requests
import re
from datetime import date, datetime
import random
from typing import Any, List, Optional, Tuple, Dict
from abc import ABC, abstractmethod
from .helpers import removeprefix, removesuffix, normalize_table, Rows, Row
from .models import (
    Member,
    MemberInfo,
    Country,
    Group,
    GroupMembership,
    Position,
    Voting,
    VotingList,
    VoteType,
    Vote,
    VoteResult,
    VoteCollection,
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",  # noqa: E501
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15",  # noqa: E501
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",  # noqa: E501
]


def extract_reference(tag: Tag) -> Optional[str]:
    ref_tag = tag.find("a")

    if ref_tag is None:
        return None

    redmap_uri = ref_tag["redmap-uri"]
    allowed = ["/reds:iPlRe", "/reds:iPlRp"]

    if not any(redmap_uri.startswith(prefix) for prefix in allowed):
        return None

    return ref_tag.text


class Scraper(ABC):
    BS_PARSER = "lxml"

    @abstractmethod
    def __init__(self, *args: Any, **kwds: Any):
        raise NotImplementedError

    def run(self) -> Any:
        self._load()
        return self._extract_data()

    @abstractmethod
    def _extract_data(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def _url(self) -> str:
        raise NotImplementedError

    def _load(self) -> None:
        url = self._url()
        raw = requests.get(url, headers=self._headers()).text
        self._resource = BeautifulSoup(raw, self.BS_PARSER)

    def _headers(self) -> Dict[str, str]:
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "en-us",
            "user-agent": random.choice(USER_AGENTS),
        }


class MembersScraper(Scraper):
    BASE_URL = "https://www.europarl.europa.eu/meps/en/directory/xml"
    BS_PARSER = "lxml-xml"

    def __init__(self, term: int):
        self.term = term

    def _url(self) -> str:
        return f"{self.BASE_URL}/?leg={self.term}"

    def _extract_data(self) -> List[Member]:
        tags = self._resource.find_all("mep")
        return [self._member(tag) for tag in tags]

    def _member(self, tag: Tag) -> Member:
        web_id = int(tag.find("id").text)
        return Member(web_id=web_id, terms=[self.term])


class MemberInfoScraper(Scraper):
    BASE_URL = "https://www.europarl.europa.eu/meps/en"

    def __init__(self, web_id: int):
        self.web_id = web_id

    def _url(self) -> str:
        return f"{self.BASE_URL}/{self.web_id}/NAME/home"

    def _extract_data(self) -> MemberInfo:
        first, last = self._name()

        return MemberInfo(
            first_name=first,
            last_name=last,
            date_of_birth=self._date_of_birth(),
            country=self._country(),
        )

    def _name(self) -> Tuple[Optional[str], Optional[str]]:
        tag = self._resource.select_one("#presentationmep div.erpl_title-h1")
        full = tag.text.strip()
        return MemberInfo.parse_full_name(full)

    def _date_of_birth(self) -> Optional[date]:
        tag = self._resource.select_one("#birthDate")

        if not tag:
            return None

        raw = tag.text.strip()
        return datetime.strptime(raw, "%d-%m-%Y").date()

    def _country(self) -> Country:
        tag = self._resource.select_one("#presentationmep div.erpl_title-h3")
        name = tag.text.split("-")[0].strip()
        return Country.from_str(name)


class MemberGroupsScraper(Scraper):
    BASE_URL = "https://www.europarl.europa.eu/meps/en"

    def __init__(self, web_id: int, term: int):
        self.web_id = web_id
        self.term = term

    def _url(self) -> str:
        return f"{self.BASE_URL}/{self.web_id}/NAME/history/{self.term}"

    def _extract_data(self) -> List[GroupMembership]:
        tags = self._resource.select("#status .erpl_meps-status:first-child ul li")
        return [self._group_membership(tag) for tag in tags]

    def _group_membership(self, tag: Tag) -> GroupMembership:
        start, end = self._date_range(tag)

        return GroupMembership(
            group=self._group(tag), term=self.term, start_date=start, end_date=end
        )

    def _group(self, tag: Tag) -> Group:
        text = "".join(tag.find_all(text=True, recursive=False))
        text = removeprefix(text, " : ")

        positions = [
            "President",
            "Co-President",
            "Chair",
            "Co-Chair",
            "Vice-Chair",
            "First Vice-Chair",
            "Member of the Bureau",
            "Treasurer",
            "Co-treasurer",
            "Member",
        ]

        for pos in positions:
            text = removesuffix(text, f" - {pos}")

        return Group.from_str(text)

    def _date_range(self, tag: Tag) -> Tuple[date, Optional[date]]:
        text = tag.find("strong").text

        if "..." in text:
            start_date = text.split(" ...")[0]
            start_date = datetime.strptime(start_date, "%d-%m-%Y").date()

            return start_date, None

        parts = text.split(" / ")
        start, end = [datetime.strptime(part, "%d-%m-%Y") for part in parts]

        return start.date(), end.date()


class VotingListsScraper(Scraper):
    BASE_URL = "https://www.europarl.europa.eu/doceo/document"
    BS_PARSER = "lxml-xml"

    def __init__(self, date: date, term: int):
        self.date = date
        self.term = term

    def _url(self) -> str:
        date = self.date.strftime("%Y-%m-%d")
        return f"{self.BASE_URL}/PV-{self.term}-{date}-RCV_FR.xml"

    def _extract_data(self) -> List[VotingList]:
        tags = self._resource.find_all("RollCallVote.Result")
        return [self._voting_list(tag) for tag in tags]

    def _voting_list(self, tag: Tag) -> VotingList:
        return VotingList(
            description=self._description(tag),
            reference=self._reference(tag),
            doceo_vote_id=int(tag["Identifier"]),
            votings=self._votings(tag),
        )

    def _votings(self, tag: Tag) -> List[Voting]:
        votings = []

        results = {
            Position.FOR: tag.find("Result.For"),
            Position.AGAINST: tag.find("Result.Against"),
            Position.ABSTENTION: tag.find("Result.Abstention"),
        }

        for position, child in results.items():
            if not child:
                continue

            votings.extend(self._votings_by_position(child, position))

        return votings

    def _votings_by_position(self, tag: Tag, position: Position) -> List[Voting]:
        tags = tag.find_all("PoliticalGroup.Member.Name")
        return [self._voting(tag, position) for tag in tags]

    def _voting(self, tag: BeautifulSoup, position: Position) -> Voting:
        doceo_id = int(tag.get("MepId"))
        return Voting(doceo_member_id=doceo_id, name=tag.text, position=position)

    def _reference(self, tag: Tag) -> Optional[str]:
        return extract_reference(tag.find("RollCallVote.Description.Text"))

    def _description(self, tag: Tag) -> str:
        desc_tag = tag.find("RollCallVote.Description.Text")
        return removeprefix(desc_tag.text.strip(), "- ")


class VoteCollectionsScraper(Scraper):
    BS_PARSER = "lxml-xml"
    BASE_URL = "https://europarl.europa.eu/doceo/document/"
    # PV-9-2021-03-09-VOT_EN.xml

    def __init__(self, term: int, date: date):
        self.term = term
        self.date = date

    def _url(self) -> str:
        document = f"PV-{self.term}-{self.date}-VOT_EN.xml"
        return f"{self.BASE_URL}{document}"

    def _extract_data(self) -> List[VoteCollection]:
        tags = self._resource.find_all("Vote.Result")
        collections = [self._collection(tag) for tag in tags]
        return [collection for collection in collections if len(collection.votes) > 0]

    def _collection(self, tag: Tag) -> VoteCollection:
        return VoteCollection(
            title=self._title(tag),
            reference=self._reference(tag),
            votes=self._votes(tag),
        )

    def _reference(self, tag: Tag) -> Optional[str]:
        return extract_reference(tag.find("Vote.Result.Description.Text"))

    def _votes(self, tag: Tag) -> List[Vote]:
        votes_table = tag.select_one("Vote\\.Result\\.Table\\.Results > TABLE")
        votes_table = normalize_table(votes_table)
        votes_table = self._add_referenced_text(votes_table)
        votes_table = [row for row in votes_table if self._include_row(row)]

        return [self._vote(row) for row in votes_table]

    def _add_referenced_text(self, votes_table: Rows) -> Rows:
        current_reference = None
        for row in votes_table:
            keys = row.keys()
            if len(keys) == 1 and "Subject" in keys:
                current_reference = row.get("Subject")
            else:
                row["referenced_text"] = current_reference

        return votes_table

    def _include_row(self, row: Row) -> bool:
        # non-RCV votes or full row headings (since c4 does not exist there)
        c4 = row.get("RCV etc.")
        if not c4 or not c4.endswith("RCV"):
            return False

        # lapsed votes
        if row.get("Vote") == "↓":
            return False

        return True

    def _vote(self, row: Row) -> Vote:
        return Vote(
            subject=row.get("Subject"),
            author=row.get("Author"),
            result=VoteResult.from_str(str(row["Vote"])),
            split_part=self._split_part(row.get("RCV etc.")),
            amendment=self._amendment(row.get("Am No")),
            type=self._type(row),
        )

    def _type(self, row: Row) -> VoteType:
        if row.get("Am No") == "§":
            return VoteType.SEPARATE

        if row.get("Am No") is not None:
            return VoteType.AMENDMENT

        return VoteType.PRIMARY

    def _amendment(self, string: Optional[str]) -> Optional[str]:
        return string if string != "§" else None

    def _split_part(self, string: Optional[str]) -> Optional[int]:
        split_part = re.search(r"^(\d*)\/RCV$", string or "")
        split_part = split_part.group(1) if split_part else None  # type: ignore
        split_part = int(split_part) if split_part else None  # type: ignore
        return split_part

    def _title(self, tag: Tag) -> str:
        title_tag = tag.find("Vote.Result.Text.Title")
        return title_tag.text.strip()
