from bs4 import BeautifulSoup, Tag
import requests
from datetime import date, datetime
from typing import Set, Dict, Any, List, Optional
from abc import abstractmethod
from itertools import chain
from .types import (
    Member,
    Country,
    Group,
    GroupMembership,
    Position,
    Voting,
    Vote,
    DocReference,
)

ResourceKey = Any
ResourceUrls = Dict[ResourceKey, str]
LoadedResources = Dict[ResourceKey, str]
ParsedResources = Dict[ResourceKey, Any]


class Scraper:
    _resources: ParsedResources = {}

    def run(self) -> Any:
        self._load_resources()
        return self._extract_information()

    @abstractmethod
    def _extract_information(self) -> Any:
        pass

    @abstractmethod
    def _resource_urls(self) -> ResourceUrls:
        pass

    def _load_resources(self) -> None:
        urls = self._resource_urls()
        self._resources = {k: self._load_resource(v) for k, v in urls.items()}

    def _load_resource(self, resource_url: str) -> str:
        raw = requests.get(resource_url).text
        return self._parse_resource(raw)

    @abstractmethod
    def _parse_resource(self, resource: str) -> Any:
        pass


class MembersScraper(Scraper):
    TERMS: List[int] = [8, 9]
    DIRECTORY_BASE_URL: str = "https://europarl.europa.eu/meps/en/directory/xml"

    def _extract_information(self) -> List[Member]:
        self._members: Dict[int, Member] = {}

        for term in self.TERMS:
            for member in self._get_members(term):
                self._add_member(member)

        return list(self._members.values())

    def _add_member(self, member: Member) -> None:
        web_id = member.europarl_website_id

        if web_id not in self._members:
            self._members[web_id] = member
            return

        terms = self._members[web_id].terms | member.terms
        self._members[web_id].terms = terms

    def _get_members(self, term: int) -> List[Member]:
        tags = self._resources[term].find_all("mep")
        return [self._get_member(tag, term) for tag in tags]

    def _get_member(self, tag: Tag, term: int) -> Member:
        europarl_website_id = int(tag.find("id").text)
        return Member(europarl_website_id=europarl_website_id, terms={term})

    def _parse_resource(self, resource: str) -> BeautifulSoup:
        return BeautifulSoup(resource, "lxml-xml")

    def _resource_urls(self) -> ResourceUrls:
        base = self.DIRECTORY_BASE_URL
        return {term: f"{base}/?leg={term}" for term in self.TERMS}


class MemberInfoScraper(Scraper):
    PROFILE_BASE_URL = "https://europarl.europa.eu/meps/en"

    def __init__(self, europarl_website_id: int, terms: Set[int]):
        self.europarl_website_id = europarl_website_id
        self.terms = terms

    def _extract_information(self) -> Member:
        first_name, last_name = Member.parse_full_name(self._full_name())

        return Member(
            europarl_website_id=self.europarl_website_id,
            terms=set(self.terms),
            first_name=first_name,
            last_name=last_name,
            date_of_birth=self._date_of_birth(),
            country=self._country(),
        )

    def _parse_resource(self, resource: str) -> BeautifulSoup:
        return BeautifulSoup(resource, "lxml")

    def _resource_urls(self) -> ResourceUrls:
        web_id = self.europarl_website_id
        base = self.PROFILE_BASE_URL

        return {term: f"{base}/{web_id}/NAME/history/{term}" for term in self.terms}

    def _latest_term(self) -> BeautifulSoup:
        return self._resources[max(self.terms)]

    def _full_name(self) -> str:
        html = self._latest_term()
        return html.select("#presentationmep div.erpl_title-h1")[0].text.strip()

    def _date_of_birth(self) -> Optional[date]:
        raw = self._latest_term().select("#birthDate")

        if not raw:
            return None

        raw = raw[0].text.strip()
        return datetime.strptime(raw, "%d-%m-%Y").date()

    def _country(self) -> Country:
        html = self._latest_term()
        raw = html.select("#presentationmep div.erpl_title-h3")[0].text
        country = raw.split("-")[0].strip()

        return Country.from_str(country)

    def _group_memberships(self) -> List[GroupMembership]:
        memberships = []

        for term, html in self._resources.items():
            items = html.select("#status .erpl_meps-status:first-child ul li")
            memberships.extend([self._group_membership(item, term) for item in items])

        return memberships

    def _group_membership(self, tag: BeautifulSoup, term: int) -> GroupMembership:
        date_range = tag.find("strong").text
        group = tag.find(text=True, recursive=False).split(" : ")[1]
        group = Group.from_str(group)

        membership = GroupMembership(group=group, term=term)

        if "..." in date_range:
            start = date_range.split(" ...")[0]
            start = datetime.strptime(start, "%d-%m-%Y").date()

            membership.start_date = start
            return membership

        date_range = date_range.split(" / ")
        start, end = [datetime.strptime(d, "%d-%m-%Y").date() for d in date_range]

        membership.start_date = start
        membership.end_date = end

        return membership

    def _parse_group(self, tag: BeautifulSoup) -> Group:
        group = tag.find_all(text=True)[-1].split(" : ")[1]
        group = group.split(" - Member")[0]

        return Group.from_str(group)


class VoteResultsScraper(Scraper):
    BASE_URL = "https://europarl.europa.eu/doceo/document"

    def __init__(self, date: date, term: int):
        self.date = date
        self.term = term

    def _resource_urls(self) -> ResourceUrls:
        date = self.date.strftime("%Y-%m-%d")
        file = f"PV-{self.term}-{date}-RCV_FR.xml"

        return {self.date: f"{self.BASE_URL}/{file}"}

    def _parse_resource(self, resource: str) -> BeautifulSoup:
        return BeautifulSoup(resource, "lxml-xml")

    def _extract_information(self) -> List[Vote]:
        doc = next(iter(self._resources.values()))
        tags = doc.find_all("RollCallVote.Result")

        return [self._result(tag) for tag in tags]

    def _result(self, tag: Tag) -> Vote:
        desc_tag = tag.find("RollCallVote.Description.Text")

        return Vote(
            doceo_vote_id=int(tag["Identifier"]),
            date=datetime.fromisoformat(tag.get("Date")),
            description=self._description(desc_tag),
            reference=self._reference(desc_tag),
            votings=self._votings(tag),
        )

    def _description(self, tag: Tag) -> str:
        texts = tag.find_all(text=True, recursive=False)
        texts = [text.strip() for text in texts if text.strip()]
        text = "".join(texts)

        if text.startswith("- "):
            return text[len("- ") :]

        return text

    def _reference(self, tag: Tag) -> Optional[DocReference]:
        ref_tag = tag.find("a")

        if ref_tag is None:
            return None

        return DocReference.from_str(ref_tag.text)

    def _votings(self, tag: Tag) -> List[Voting]:
        results = {
            Position.FOR: tag.find("Result.For"),
            Position.AGAINST: tag.find("Result.Against"),
            Position.ABSTENTION: tag.find("Result.Abstention"),
        }

        votings = [self._votings_by_position(v, k) for k, v in results.items()]
        return list(chain.from_iterable(votings))

    def _votings_by_position(self, tag: Tag, position: Position) -> List[Voting]:
        member_tags = tag.find_all("PoliticalGroup.Member.Name")
        return [self._voting(tag, position) for tag in member_tags]

    def _voting(self, tag: BeautifulSoup, position: Position) -> Voting:
        doceo_id = int(tag.get("MepId"))
        return Voting(doceo_member_id=doceo_id, name=tag.text, position=position)
