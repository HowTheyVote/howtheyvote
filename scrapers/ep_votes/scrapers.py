from bs4 import BeautifulSoup, Tag
import requests
from datetime import date, datetime
from typing import Any, List, Optional, Tuple, Union
from abc import ABC, abstractmethod
from .helpers import removeprefix, removesuffix
from .models import (
    Member,
    MemberInfo,
    Country,
    Group,
    GroupMembership,
    Position,
    Voting,
    Vote,
    Doc,
    DocReference,
)


class Scraper(ABC):
    BS_PARSER = "lxml"

    @abstractmethod
    def __init__(self, *args: Any, **kwds: Any):
        pass

    def run(self) -> Any:
        self._load()
        return self._extract_data()

    @abstractmethod
    def _extract_data(self) -> Any:
        pass

    @abstractmethod
    def _url(self) -> str:
        pass

    def _load(self) -> None:
        url = self._url()
        raw = requests.get(url).text
        self._resource = BeautifulSoup(raw, self.BS_PARSER)


class MembersScraper(Scraper):
    BASE_URL = "https://europarl.europa.eu/meps/en/directory/xml"
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
    BASE_URL = "https://europarl.europa.eu/meps/en"

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
    BASE_URL = "https://europarl.europa.eu/meps/en"

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
        text = removesuffix(text, " - Chair")
        text = removesuffix(text, " - Co-Chair")
        text = removesuffix(text, " - Vice-Chair")
        text = removesuffix(text, " - Member")

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


class VoteResultsScraper(Scraper):
    BASE_URL = "https://europarl.europa.eu/doceo/document"
    BS_PARSER = "lxml-xml"

    def __init__(self, date: date, term: int):
        self.date = date
        self.term = term

    def _url(self) -> str:
        date = self.date.strftime("%Y-%m-%d")
        return f"{self.BASE_URL}/PV-{self.term}-{date}-RCV_FR.xml"

    def _extract_data(self) -> List[Vote]:
        tags = self._resource.find_all("RollCallVote.Result")
        return [self._result(tag) for tag in tags]

    def _result(self, tag: Tag) -> Vote:
        return Vote(
            doceo_vote_id=int(tag["Identifier"]),
            date=self._date(tag),
            description=self._description(tag),
            reference=self._reference(tag),
            votings=self._votings(tag),
        )

    def _date(self, tag: Tag) -> date:
        return datetime.fromisoformat(tag.get("Date"))

    def _description(self, tag: Tag) -> str:
        desc_tag = tag.find("RollCallVote.Description.Text")

        texts = desc_tag.find_all(text=True, recursive=False)
        texts = [text.strip() for text in texts if text.strip()]
        text = removeprefix("".join(texts), "- ")

        return text

    def _reference(self, tag: Tag) -> Optional[DocReference]:
        ref_tag = tag.find("RollCallVote.Description.Text").find("a")

        if ref_tag is None:
            return None

        return DocReference.from_str(ref_tag.text)

    def _votings(self, tag: Tag) -> List[Voting]:
        votings = []

        results = {
            Position.FOR: tag.find("Result.For"),
            Position.AGAINST: tag.find("Result.Against"),
            Position.ABSTENTION: tag.find("Result.Abstention"),
        }

        for position, child in results.items():
            votings.extend(self._votings_by_position(child, position))

        return votings

    def _votings_by_position(self, tag: Tag, position: Position) -> List[Voting]:
        tags = tag.find_all("PoliticalGroup.Member.Name")
        return [self._voting(tag, position) for tag in tags]

    def _voting(self, tag: BeautifulSoup, position: Position) -> Voting:
        doceo_id = int(tag.get("MepId"))
        return Voting(doceo_member_id=doceo_id, name=tag.text, position=position)


class DocumentScraper(Scraper):
    BASE_URL = "https://europarl.europa.eu/doceo/document"

    def __init__(self, reference: Union[DocReference, str]):
        if isinstance(reference, str):
            reference = DocReference.from_str(reference)

        self.reference = reference

    def _url(self) -> str:
        ref = self.reference
        file = f"{ref.type.name}-{ref.term}-{ref.year:04}-{ref.number:04}_EN.html"
        return f"{self.BASE_URL}/{file}"

    def _extract_data(self) -> Doc:
        return Doc(title=self._title())

    def _title(self) -> str:
        tag = self._resource.find("title")
        return tag.text.strip()
