from bs4 import BeautifulSoup, Tag
import requests
import re
from datetime import date, datetime
from typing import Any, List, Optional, Tuple
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
    VoteType,
    Vote,
    Doc,
    DocType,
    DocReference,
    Procedure,
    ProcedureReference,
)


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
        vote_type, subvote_description = self._subvote(tag)

        return Vote(
            doceo_vote_id=int(tag["Identifier"]),
            date=self._date(tag),
            description=self._description(tag),
            reference=self._reference(tag),
            votings=self._votings(tag),
            type=vote_type,
            subvote_description=subvote_description,
        )

    def _date(self, tag: Tag) -> date:
        return datetime.fromisoformat(tag.get("Date"))

    def _description(self, tag: Tag) -> str:
        ref_tag = self._reference_tag(tag)
        desc_tag = tag.find("RollCallVote.Description.Text")

        text = desc_tag.text

        if ref_tag:
            text = text.replace(ref_tag.text, " ")

        return removeprefix(text.strip(), "- ")

    def _subvote(self, tag: Tag) -> Tuple[VoteType, Optional[str]]:
        description = self._description(tag)

        numbering_regex = r"\s*\d+(?:\s*-\s*\d+)?(?:\/\d+)?"

        single_amendment_regex = r"Am" + numbering_regex
        amendments_regex = (
            single_amendment_regex + r"(?:\s+" + single_amendment_regex + r")*$"
        )
        amendments = re.search(amendments_regex, description)

        if amendments:
            return VoteType.AMENDMENT, amendments.group(0)

        single_paragraph_regex = r"§" + numbering_regex
        paragraphs_regex = (
            single_paragraph_regex + r"(?:\s+" + single_paragraph_regex + r")*$"
        )
        paragraphs = re.search(paragraphs_regex, description)

        if paragraphs:
            return VoteType.SPLIT, paragraphs.group(0)

        consideration_regex = r"Consid[eé]rant\s*[A-Z]+(?:\/\d+)?$"
        consideration = re.search(consideration_regex, description)

        if consideration:
            return VoteType.SPLIT, consideration.group(0)

        if description.startswith("Ordre du jour"):
            return VoteType.AGENDA, None

        return VoteType.FINAL, None

    def _reference(self, tag: Tag) -> Optional[DocReference]:
        ref_tag = self._reference_tag(tag)

        if not ref_tag:
            return None

        return DocReference.from_str(ref_tag.text)

    def _reference_tag(self, tag: Tag) -> Optional[BeautifulSoup]:
        ref_tag = tag.find("RollCallVote.Description.Text").find("a")

        if ref_tag is None:
            return None

        redmap_uri = ref_tag["redmap-uri"]
        allowed = ["/reds:iPlRe", "/reds:iPlRp"]

        if not any(redmap_uri.startswith(prefix) for prefix in allowed):
            return None

        return ref_tag

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


class DocumentInfoScraper(Scraper):
    BASE_URL = "https://europarl.europa.eu/doceo/document"

    def __init__(self, type: DocType, term: int, year: int, number: int):
        self.type = type
        self.term = term
        self.year = year
        self.number = number

    def _url(self) -> str:
        file = f"{self.type.name}-{self.term}-{self.year:04}-{self.number:04}_EN.html"
        return f"{self.BASE_URL}/{file}"

    def _extract_data(self) -> Doc:
        return Doc(title=self._title())

    def _title(self) -> str:
        tag = self._resource.find("title")
        return tag.text.strip()


class ProcedureScraper(Scraper):
    BS_PARSER = "lxml-xml"
    BASE_URL = "https://oeil.secure.europarl.europa.eu/oeil/popups/printresultlist.xml?lang=en&limit=1&q=documentEP:D-"  # noqa: E501

    def __init__(self, type: DocType, term: int, year: int, number: int):
        self.type = type
        self.term = term
        self.year = year
        self.number = number

    def _url(self) -> str:
        document = f"{self.type.name}{self.term}-{self.number:04}/{self.year:04}"
        return f"{self.BASE_URL}{document}"

    def _extract_data(self) -> Procedure:
        item_tag = self._resource.find("item")
        title_tag = item_tag.find("title")
        reference_tag = item_tag.find("reference")

        return Procedure(
            title=self._title(title_tag), reference=self._reference(reference_tag)
        )

    def _title(self, tag: Tag) -> str:
        return tag.text.strip().replace("\n", " ")

    def _reference(self, tag: Tag) -> ProcedureReference:
        return ProcedureReference.from_str(tag.text.strip())
