from datetime import date, datetime
from typing import Any, cast

from bs4 import BeautifulSoup, Tag
from structlog import get_logger

from ..models import Country, Fragment, Group, Member
from ..pushover import send_notification
from .common import BeautifulSoupScraper, JSONScraper, RequestCache, ScrapingError
from .helpers import parse_full_name

log = get_logger(__name__)


class MembersScraper(BeautifulSoupScraper):
    """Scrapes member IDs from the XML version of the official MEP directory. The
    directory includes outgoing and ingoing members."""

    BASE_URL = "https://www.europarl.europa.eu/meps/en/directory/xml"
    BS_PARSER = "lxml-xml"

    def __init__(self, term: int, request_cache: RequestCache | None = None):
        super().__init__(term=term, request_cache=request_cache)
        self.term = term

    def _url(self) -> str:
        return f"{self.BASE_URL}/?leg={self.term}"

    def _extract_data(self, doc: BeautifulSoup) -> list[Fragment]:
        tags = doc.find_all("mep")
        fragments = [self._member(tag) for tag in tags]
        self._log.info("Extracted members", count=len(fragments))
        return fragments

    def _member(self, tag: Tag) -> Fragment:
        identifier = self._identifier(tag)

        return self._fragment(
            model=Member,
            source_id=f"{identifier}:{self.term}",
            group_key=identifier,
            data={"term": self.term},
        )

    def _identifier(self, tag: Tag) -> int:
        element = tag.select_one("id")

        if not element:
            raise ScrapingError("Could not find `id` element.")

        return int(element.text)


class MemberInfoScraper(BeautifulSoupScraper):
    """Scrapes basic biographical information for a given member (for example
    first and last names, nationality, social media profiles)."""

    BASE_URL = "https://www.europarl.europa.eu/meps/en"

    def __init__(self, web_id: int, request_cache: RequestCache | None = None):
        super().__init__(web_id=web_id, request_cache=request_cache)
        self.web_id = web_id

    def _url(self) -> str:
        return f"{self.BASE_URL}/{self.web_id}/NAME/home"

    def _extract_data(self, doc: BeautifulSoup) -> Fragment:
        first, last = self._name(doc)

        return self._fragment(
            model=Member,
            source_id=self.web_id,
            group_key=self.web_id,
            data={
                "first_name": first,
                "last_name": last,
                "date_of_birth": self._date_of_birth(doc),
                "facebook": self._facebook(doc),
                "twitter": self._twitter(doc),
                "email": self._email(doc),
                "country": self._country(doc),
            },
        )

    def _facebook(self, doc: BeautifulSoup) -> str | None:
        tag = doc.select_one("#presentationmep a.link_fb")
        if tag is None:
            return None

        # https://github.com/python/typeshed/issues/8755
        return cast(str, tag["href"])

    def _twitter(self, doc: BeautifulSoup) -> str | None:
        tag = doc.select_one("#presentationmep a.link_twitt")
        if tag is None:
            return None

        # https://github.com/python/typeshed/issues/8755
        return cast(str, tag["href"])

    def _email(self, doc: BeautifulSoup) -> str | None:
        # The e-mail addresses are reversed in the page-source for spam detection
        # reasons. The reversal is undone using JavaScript on page-load.
        tag = doc.select_one(".link_email[href*='aporue.lraporue']")
        if tag is None:
            return None

        # https://github.com/python/typeshed/issues/8755
        href = cast(str, tag["href"])

        address = href.replace("mailto:", "").replace("[dot]", ".").replace("[at]", "@")
        address = address[::-1]

        return address

    def _name(self, doc: BeautifulSoup) -> tuple[str | None, str | None]:
        tag = doc.select_one("#presentationmep div.es_title-h1")

        if not tag:
            raise ScrapingError("Could not find element containing member name.")

        full = tag.text.strip()
        return parse_full_name(full)

    def _date_of_birth(self, doc: BeautifulSoup) -> date | None:
        tag = doc.select_one(".sln-birth-date")

        if not tag:
            return None

        raw = tag.text.strip()
        return datetime.strptime(raw, "%d-%m-%Y").date()

    def _country(self, doc: BeautifulSoup) -> str:
        tag = doc.select_one("#presentationmep div.es_title-h3")

        if not tag:
            raise ScrapingError("Could not find element containing member country.")

        label = tag.text.split("-")[0].strip()
        country = Country.from_label(label)

        if not country:
            raise ScrapingError(f"Could not find country {label}")

        return country.code


class MemberGroupsScraper(BeautifulSoupScraper):
    """Scrapes group memberships for a given member and term. This includes current and past
    group memberships with start and end dates."""

    BASE_URL = "https://www.europarl.europa.eu/meps/en"

    def __init__(self, web_id: int, term: int, request_cache: RequestCache | None = None):
        super().__init__(web_id=web_id, term=term, request_cache=request_cache)
        self.web_id = web_id
        self.term = term

    def _url(self) -> str:
        return f"{self.BASE_URL}/{self.web_id}/NAME/history/{self.term}"

    def _extract_data(self, doc: BeautifulSoup) -> Fragment:
        tags = doc.select("#status .erpl_meps-status:first-child ul li")
        group_memberships = [self._group_membership(tag) for tag in tags]
        self._log.info("Extracted group memberships", count=len(group_memberships))

        return self._fragment(
            model=Member,
            source_id=f"{self.web_id}:{self.term}",
            group_key=self.web_id,
            data={"group_memberships": group_memberships},
        )

    def _group_membership(self, tag: Tag) -> dict[str, Any]:
        start, end = self._date_range(tag)
        group = self._group(tag, date=start)

        return {
            "group": group,
            "term": self.term,
            "start_date": start,
            "end_date": end,
        }

    def _group(self, tag: Tag, date: date) -> str:
        text = "".join(tag.find_all(string=True, recursive=False))
        text = text.removeprefix(" : ")

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
            "First Vice-Chair/Member of the Bureau",
            "Treasurer/Vice-Chair/Member of the Bureau",
        ]

        for pos in positions:
            text = text.removesuffix(f" - {pos}")

        group = Group.from_label(text, date=date)

        if not group:
            raise ScrapingError(f"Could not find group named {text}")

        return group.code

    def _date_range(self, tag: Tag) -> tuple[date, date | None]:
        strong = cast(Tag | None, tag.find("strong"))

        if not strong:
            raise ScrapingError("Could not find element containing date range.")

        text = strong.text

        if "..." in text:
            iso_str = text.split(" ...")[0]
            start_date = datetime.strptime(iso_str, "%d-%m-%Y").date()

            return start_date, None

        parts = text.split(" / ")
        start, end = (datetime.strptime(part, "%d-%m-%Y") for part in parts)

        return start.date(), end.date()


class ODPMemberScraper(JSONScraper):
    BASE_URL = "https://data.europarl.europa.eu/api/v2/meps"

    def __init__(self, web_id: int, request_cache: RequestCache | None = None):
        super().__init__(web_id=web_id, request_cache=request_cache)
        self.web_id = web_id
        self.REQUEST_TIMEOUT = 60

    def _url(self) -> str:
        return f"{self.BASE_URL}/{self.web_id}?format=application/ld+json"

    def _extract_data(self, doc: Any) -> Fragment:
        memberships = doc["data"][0]["hasMembership"]
        national_parties = [
            ms
            for ms in memberships
            if ms.get("membershipClassification") == "def/ep-entities/NATIONAL_POLITICAL_GROUP"
        ]

        party_memberships = [
            party_membership
            for np in national_parties
            if (party_membership := self._party_membership(np)) is not None
        ]

        return self._fragment(
            model=Member,
            source_id=f"{self.web_id}",
            group_key=self.web_id,
            data={"national_party_memberships": party_memberships},
        )

    def _party_membership(self, membership: dict[str, Any]) -> dict[str, Any] | None:
        time_period = membership.get("memberDuring")
        if time_period is None:
            raise ScrapingError("Invalid National Party Date from ODP.")
        start_date = datetime.strptime(time_period["startDate"], "%Y-%m-%d").date()
        end_date = (
            datetime.strptime(time_period["endDate"], "%Y-%m-%d").date()
            if time_period.get("endDate")
            else None
        )

        # In some cases we have active memberships for which the organization is not known.
        # We do not store them, but inform us to possibly inquire about them.
        if membership.get("organization") is None:
            send_notification(
                title="Party-membership without organization key found.",
                message=f"For MEP ID {self.web_id}",
                url=self._url(),
            )
            return None

        party_id = membership["organization"].split("/", 1)[1]

        return {
            "party": party_id,
            "start_date": start_date,
            "end_date": end_date,
        }
