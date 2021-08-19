from bs4 import BeautifulSoup, Tag
import html
import requests
import re
from datetime import date, datetime
import random
from typing import Any, List, Optional, Tuple, Dict, Union
from abc import ABC, abstractmethod
from .helpers import (
    removeprefix,
    removesuffix,
    normalize_table,
    Rows,
    Row,
    normalize_whitespace,
    extract_reference,
)
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
    Session,
    Location,
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",  # noqa: E501
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15",  # noqa: E501
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",  # noqa: E501
]


class ScrapingException(Exception):
    pass


class Scraper(ABC):
    BS_PARSER: str = "lxml"
    RESPONSE_ENCODING: Optional[str] = None

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
    def _url(self) -> Union[str, List[str]]:
        raise NotImplementedError

    def _load(self) -> None:
        self.url = self._url()

        if isinstance(self.url, str):
            self.url = [self.url]

        for url in self.url:
            res = requests.get(url, headers=self._headers())

            if not res.ok:
                continue

            # Some sources do not return the correct character encoding in the
            # HTTP headers which confuses request when trying to decode the
            # response. In those cases, we need to force the correct encoding.
            if self.RESPONSE_ENCODING:
                raw = res.content.decode(self.RESPONSE_ENCODING)
            else:
                raw = res.text

            # Handle HTML-encoded special-characters, as BeautifulSoup
            # seems to decode them to incorrect Unicode characters
            if self.BS_PARSER != "lxml-xml":
                raw = html.unescape(raw)

            self._resource = BeautifulSoup(raw, self.BS_PARSER)

            return

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
        tag = self._resource.select_one(".sln-birth-date")

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
            "Vice-President",
            "Chair",
            "Co-Chair",
            "Vice-Chair",
            "First Vice-Chair",
            "Chair of the Bureau",
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
    BASE_URL_EP = "https://www.europarl.europa.eu/doceo/document"
    BASE_URL_DR = "https://www.europarl.europa.eu/RegData/seance_pleniere/proces_verbal"
    BS_PARSER = "lxml-xml"
    RESPONSE_ENCODING = "utf-8"

    # Some members are also known by alternate names which are
    # sometimes used in voting lists. We use this dict to replace
    # alternate names with the names listed in the MEP profiles
    # on the official website of the Parliament.
    ALTERNATE_NAMES = {
        "Pagazaurtundúa Ruiz": "Pagazaurtundúa",
        "Lechevalier": "Letard-Lechevalier",
        "Gambús": "Gambus Millet",
        "Kozłowska-Rajewicz": "Kozłowska",
        "Aguilera García": "Aguilera",
        "Rodríguez-Piñero Fernández": "Rodríguez-Piñero",
        "Papadakis Konstantinos": "Papadakis",
        "Miranda": "Miranda Paz",
    }

    def __init__(self, date: date, term: int):
        self.date = date
        self.term = term

    def _url(self) -> List[str]:
        date = self.date.strftime("%Y-%m-%d")
        doceo_url = f"{self.BASE_URL_EP}/PV-{self.term}-{date}-RCV_FR.xml"

        year = self.date.strftime("%Y")
        month = self.date.strftime("%m")
        day = self.date.strftime("%d")
        document_register_url = (
            f"{self.BASE_URL_DR}/{year}/{month}-{day}/liste_presence/"
            f"P{self.term}_PV({year}){month}-{day}(RCV)_XC.xml"
        )

        return [doceo_url, document_register_url]

    def _extract_data(self) -> List[VotingList]:
        tags = self._resource.find_all("RollCallVote.Result")
        return [self._voting_list(tag) for tag in tags]

    def _voting_list(self, tag: Tag) -> VotingList:

        doceo_vote_id = None

        try:
            doceo_vote_id = int(tag["Identifier"])

        except KeyError:
            pass

        return VotingList(
            description=self._description(tag),
            reference=self._reference(tag),
            doceo_vote_id=doceo_vote_id,
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
        tags = tag.find_all("PoliticalGroup.Member.Name") + tag.find_all("Member.Name")
        return [self._voting(tag, position) for tag in tags]

    def _voting(self, tag: BeautifulSoup, position: Position) -> Voting:
        doceo_id = int(tag.get("MepId"))
        name = self.ALTERNATE_NAMES.get(tag.text, tag.text)

        return Voting(doceo_member_id=doceo_id, name=name, position=position)

    def _reference(self, tag: Tag) -> Optional[str]:
        return extract_reference(tag.find("RollCallVote.Description.Text").text)

    def _description(self, tag: Tag) -> str:
        desc_tag = tag.find("RollCallVote.Description.Text")
        return normalize_whitespace(removeprefix(desc_tag.text.strip(), "- "))


class VoteCollectionsScraper(Scraper):
    BS_PARSER = "lxml-xml"
    BASE_URL_EP = "https://www.europarl.europa.eu/doceo/document/"
    BASE_URL_DR = (
        "https://www.europarl.europa.eu/RegData/seance_pleniere/proces_verbal/"
    )
    RESPONSE_ENCODING = "utf-8"
    # PV-9-2021-03-09-VOT_EN.xml

    def __init__(self, term: int, date: date):
        self.term = term
        self.date = date

    def _url(self) -> List[str]:
        date = self.date.strftime("%Y-%m-%d")
        doceo_url = f"{self.BASE_URL_EP}PV-{self.term}-{date}-VOT_EN.xml"
        year = self.date.strftime("%Y")
        month = self.date.strftime("%m")
        day = self.date.strftime("%d")
        document_register_url = (
            f"{self.BASE_URL_DR}{year}/{month}-{day}/liste_presence/P{self.term}"
            f"_PV({year}){month}-{day}(VOT)_EN.xml"
        )

        return [doceo_url, document_register_url]

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
        return extract_reference(tag.find("Vote.Result.Description.Text").text)

    def _votes(self, tag: Tag) -> List[Vote]:
        votes_table = tag.select_one("Vote\\.Result\\.Table\\.Results > TABLE")
        votes_table = normalize_table(votes_table)
        votes_table = self._add_subheading(votes_table)
        votes_table = [row for row in votes_table if self._include_row(row)]

        return [self._vote(row) for row in votes_table]

    def _add_subheading(self, votes_table: Rows) -> Rows:
        current_reference = None
        for row in votes_table:
            keys = row.keys()
            if len(keys) == 1 and "Subject" in keys:
                current_reference = row.get("Subject")
            else:
                row["Subheading"] = current_reference

        return votes_table

    def _include_row(self, row: Row) -> bool:
        # non-RCV votes or full row headings (since c4 does not exist there)
        c4 = row.get("RCV etc.")
        if not c4 or not c4.endswith("RCV"):
            return False

        # lapsed votes
        if row.get("Vote") == "↓" or row.get("RCV/EV – remarks") == "↓":
            return False

        return True

    def _vote(self, row: Row) -> Vote:

        remarks = row.get("RCV/EV – remarks")
        if remarks:
            remarks = remarks.replace(" ", "")

        return Vote(
            subject=row.get("Subject"),
            author=row.get("Author"),
            result=VoteResult.from_str(str(row["Vote"])),
            split_part=self._split_part(row.get("RCV etc.")),
            amendment=self._amendment(row.get("Am No")),
            type=self._type(row),
            remarks=remarks,
            subheading=row.get("Subheading"),
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
        return normalize_whitespace(title_tag.text.strip())


class SummaryIDScraper(Scraper):
    BASE_URL = "https://oeil.secure.europarl.europa.eu/oeil/popups/"

    def __init__(self, week_of_year: int, reference: str):
        self.week_of_year = week_of_year
        self.reference = reference

    def _url(self) -> str:
        popup = f"ficheprocedure.do?reference={self.reference}"
        return f"{self.BASE_URL}{popup}"

    def _extract_data(self) -> Optional[str]:
        rows = self._resource.select("#key_events-data .ep-table-row")
        summary_rows_in_week = [
            row for row in rows if self._is_summary_row_in_week(row) is True
        ]

        if len(summary_rows_in_week) > 1:
            raise ScrapingException("Multiple summaries available for the given week.")

        if len(summary_rows_in_week) <= 0:
            raise ScrapingException("No summary found.")

        summary_row = summary_rows_in_week[0]
        button = summary_row.select_one("button[onclick]")

        if not button:
            raise ScrapingException("No summary found.")

        regex = r"\/oeil\/popups\/summary\.do\?id=(\d*)"
        match = re.search(regex, button["onclick"])

        if not match:
            raise ScrapingException("No summary found.")

        return match.group(1)

    def _is_summary_row_in_week(self, row: Tag) -> bool:
        header_cells = row.select(".ep-table-column-head")

        if len(header_cells) < 2:
            return False

        date = datetime.strptime(header_cells[0].text.strip(), "%d/%m/%Y")
        week_of_year = int(date.strftime("%W"))
        description = header_cells[1].text.strip()

        if not description.startswith("Decision by Parliament"):
            return False

        # When scraping summaries, we don't know the exact date
        # when the vote took place. Instead, we know the week
        # of the vote. We *think* it's safe to assume that there
        # won't be two votes on the same subject in the same week.
        if week_of_year != self.week_of_year:
            return False

        return True


class SummaryScraper(Scraper):
    BASE_URL = "https://oeil.secure.europarl.europa.eu/oeil/popups/"

    def __init__(self, summary_id: str):
        self.summary_id = summary_id

    def _url(self) -> str:
        popup = f"summary.do?id={self.summary_id}&t=e&l=en"
        return f"{self.BASE_URL}{popup}"

    def _extract_data(self) -> str:
        items = self._resource.select(".ep-a_text > .MsoNormal")
        items = [self._format_paragraph(item) for item in items]

        return "\n\n".join(items)

    def _format_paragraph(self, paragraph: Tag) -> str:
        text = paragraph.text.strip().replace("\n", " ")

        style = paragraph.get("style")

        if not style:
            return text

        # Headings aren't marked up using appropriate HTML tags.
        # Instead, they are simply styled using inline CSS.
        # In case we detect those styles, we prepend Markdown
        # syntax for second-level headings.
        if "font-weight" in style and "bold" in style:
            return "## " + text

        return text


class SessionsScraper(Scraper):
    BASE_URL = "https://oeil.secure.europarl.europa.eu/oeil/srvc/calendar.json"

    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month

    def _load(self) -> None:
        self._resource = requests.get(self._url()).json()

    def _url(self) -> str:
        return f"{self.BASE_URL}?y={self.year}&m={self.month}"

    def _extract_data(self) -> List[Session]:
        sessions = self._resource["sessions"]
        return [self._session(session) for session in sessions]

    def _session(self, session: dict) -> Session:
        return Session(
            start_date=self._parse_date(session["start"]),
            end_date=self._parse_date(session["end"]),
            location=self._parse_location(session["location"]),
        )

    def _parse_date(self, date_string: str) -> date:
        return date.fromisoformat(
            date_string[0:4] + "-" + date_string[4:6] + "-" + date_string[6:]
        )

    def _parse_location(self, location_string: str) -> Location:
        if "BRUSSELS" in location_string:
            return Location.BRUSSELS
        else:
            return Location.STRASBOURG
