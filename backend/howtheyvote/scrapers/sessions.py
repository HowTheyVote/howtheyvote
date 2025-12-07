from datetime import date, datetime
from typing import Any

from bs4 import BeautifulSoup

from ..models import Fragment, PlenarySession, PlenarySessionLocation
from .common import BeautifulSoupScraper, JSONScraper, RequestCache, ScrapingError


class CalendarSessionsScraper(JSONScraper):
    BASE_URL = (
        "https://www.europarl.europa.eu/plenary/en/ajax/"
        "getSessionCalendar.html?family=PV&termId="
    )

    def __init__(
        self,
        term: int,
        request_cache: RequestCache | None = None,
    ):
        super().__init__(term=term, request_cache=request_cache)
        self.term = term

    def _url(self) -> str:
        return f"{self.BASE_URL}{self.term}"

    def _extract_data(self, doc: dict[Any, Any]) -> list[Fragment]:
        start_date_attr = doc.get("startDate")
        end_date_attr = doc.get("endDate")

        if not isinstance(start_date_attr, str):
            raise ScrapingError("Could not find `startDate` property.")

        if not isinstance(end_date_attr, str):
            raise ScrapingError("Could not find `endDate` property.")

        start_date = datetime.strptime(start_date_attr, "%d/%m/%Y").date()
        end_date = datetime.strptime(end_date_attr, "%d/%m/%Y").date()
        sessions = doc.get("sessionCalendar", [])

        # The data source has a separate item for every day of a plenary session. Using
        # the start date as dict keys automatically de-duplicates the items. The result
        # is one item per plenary session.
        fragments = {}

        for session in sessions:
            fragment = self._session(session)
            if start_date <= fragment.data["start_date"] <= end_date:
                fragments[fragment.data["start_date"]] = fragment

        return list(fragments.values())

    def _session(self, session: dict[Any, Any]) -> Fragment:
        start_date = self._date(
            session["year"],
            session["monthStartDateSession"],
            session["dayStartDateSession"],
        )

        end_date = self._date(
            session["year"],
            session["monthEndDateSession"],
            session["dayEndDateSession"],
        )

        return self._fragment(
            model=PlenarySession,
            source_id=start_date.isoformat(),
            group_key=start_date.isoformat(),
            data={
                "start_date": start_date,
                "end_date": end_date,
                "term": self.term,
            },
        )

    def _date(self, year: str, month: str, day: str) -> date:
        return date(int(year), int(month), int(day))


class ODPSessionScraper(BeautifulSoupScraper):
    BASE_URL = "https://data.europarl.europa.eu/api/v1/meetings"
    BS_PARSER = "lxml-xml"

    def __init__(
        self,
        start_date: date,
        request_cache: RequestCache | None = None,
    ):
        super().__init__(start_date=date, request_cache=request_cache)
        self.start_date = start_date
        self.REQUEST_TIMEOUT = 120

    def _url(self) -> str:
        return f"{self.BASE_URL}/MTG-PL-{self.start_date.isoformat()}"

    def _extract_data(self, doc: BeautifulSoup) -> Fragment | None:
        locality = doc.select_one("rdf|RDF > eli-dl|Activity > vcard|hasLocality")

        if not locality:
            return None

        locality_url = locality["rdf:resource"]
        location = None

        if not locality_url or not isinstance(locality_url, str):
            return None

        if locality_url.endswith("/FRA_SXB"):
            location = PlenarySessionLocation.SXB

        if locality_url.endswith("/BEL_BRU"):
            location = PlenarySessionLocation.BRU

        if not location:
            return None

        return self._fragment(
            model=PlenarySession,
            source_id=self.start_date.isoformat(),
            group_key=self.start_date.isoformat(),
            data={"location": location},
        )
