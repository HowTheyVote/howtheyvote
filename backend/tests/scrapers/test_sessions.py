import datetime

from howtheyvote.models import PlenarySessionLocation
from howtheyvote.scrapers import ODPSessionScraper

from ..helpers import load_fixture


def test_odp_session_scraper(responses):
    responses.get(
        "https://data.europarl.europa.eu/api/v1/meetings/MTG-PL-2024-07-16",
        body=load_fixture("scrapers/data/sessions/odp_mtg-pl-2024-07-16.xml"),
    )

    scraper = ODPSessionScraper(start_date=datetime.date(2024, 7, 16))
    fragment = scraper.run()

    assert fragment.data["location"] == PlenarySessionLocation.SXB
