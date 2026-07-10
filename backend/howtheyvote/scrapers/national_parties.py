from typing import Any
from .common import JSONScraper, RequestCache
from ..models import NationalParty
from structlog import get_logger

log = get_logger(__name__)

class ODPNationalPartyScraper(JSONScraper):
    BASE_URL = "https://data.europarl.europa.eu/api/v2/corporate-bodies"

    def __init__(self, id: int, request_cache: RequestCache | None = None):
        super().__init__(id=id, request_cache=request_cache)
        self.id = id
        self.REQUEST_TIMEOUT = 60

    def _url(self) -> str:
        return f"{self.BASE_URL}/{self.id}?format=application/ld+json"

    def _extract_data(self, doc: Any) -> NationalParty:
        self._log.info(f"Loading data for org/{self.id}")
        content = doc["data"][0]
        
        time_period = content["temporal"]
        start_date = time_period["startDate"]
        end_date = time_period.get("endDate")

        country_code = content["represents"][0].rsplit("/", 1)[-1]

        return NationalParty(
            self.id,
            content["label"],
            content["prefLabel"]["en"],
            start_date,
            end_date,
            country_code
        )
