import requests

from typing import Any

from ..data import DATA_DIR, DataclassContainer
from ..models import NationalParty
from ..scrapers import ODPNationalPartyScraper
from .common import BasePipeline


class ODPNationalPartiesPipeline(BasePipeline):
    def _run(self) -> None:
        self.known_parties = self._load_known_parties()
        self.all_parties = self._load_all_odp_parties()

        # We need to retrieve info for parties that we do not yet have locally.
        # As we do not know for sure how renamings are handled by the ODP,
        # also rescrape info for active parties.
        party_identifier_to_scrape = [
            party["identifier"]
            for party in self.all_parties
            if (known := self.known_parties.get(party["identifier"])) is None
            or known.end_date is None
        ]
        self._log.info(  # noqa: T201
            f"Scraping data for {len(party_identifier_to_scrape)} "
            "parties which are new or still active."
        )
        for identifier in party_identifier_to_scrape:
            try:
                party_info = ODPNationalPartyScraper(id=identifier).run()
                self.known_parties.add(party_info)
            finally:
                self.known_parties.save()

    def _load_known_parties(self) -> DataclassContainer[NationalParty]:
        known_parties = DataclassContainer(
            dataclass=NationalParty,
            file_path=DATA_DIR.joinpath("national_parties.json"),
            key=lambda national_party: national_party.id,
        )
        known_parties.load()
        return known_parties

    def _load_all_odp_parties(self) -> Any:
        all_parties_response = requests.get(
            "https://data.europarl.europa.eu/api/v2/corporate-bodies?body-classification=NATIONAL_POLITICAL_GROUP&format=application/ld+json&offset=0",
            timeout=60,
        ).json()
        all_parties = all_parties_response["data"]
        self._log.info(f"Got data for {len(all_parties)} national parties from ODP.")  # noqa: T201
        return all_parties
