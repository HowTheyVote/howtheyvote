from collections.abc import Iterator

import sentry_sdk
from structlog import get_logger

from ..models import PlenarySession
from ..scrapers import CalendarSessionsScraper, ODPSessionScraper, ScrapingError
from ..store import Aggregator, BulkWriter, index_records, map_plenary_session
from .common import BasePipeline

log = get_logger(__name__)


class SessionsPipeline(BasePipeline):
    def __init__(self, term: int):
        super().__init__(term=term)
        self.term = term
        self._session_ids: set[str] = set()

    def _run(self) -> None:
        self._scrape_sessions()
        self._scrape_session_locations()
        self._index_sessions()

    def _scrape_sessions(self) -> None:
        log.info("Scrapping plenary sessions", term=self.term)
        writer = BulkWriter()
        scraper = CalendarSessionsScraper(term=self.term)
        writer.add(scraper.run())
        writer.flush()
        self._session_ids = writer.get_touched()

    def _scrape_session_locations(self) -> None:
        log.info("Scraping locations of plenary sessions", term=self.term)
        writer = BulkWriter()

        for plenary_session in self._sessions():
            if plenary_session.location:
                # Do not bother to re-scrape the location of sessions if they are
                # already in the database. Locations are unlikely to change even for
                # upcoming sessions.
                log.info(
                    "Skipping session as location already in database",
                    session_id=plenary_session.id,
                    location=plenary_session.location,
                )
                continue

            try:
                scraper = ODPSessionScraper(start_date=plenary_session.start_date)
                writer.add(scraper.run())
            except ScrapingError as err:
                log.exception(
                    "Failed scraping location of plenary session",
                    session_id=plenary_session.id,
                )
                sentry_sdk.capture_exception(err)

        writer.flush()

    def _index_sessions(self) -> None:
        log.info("Indexing plenary sessions", term=self.term)
        index_records(PlenarySession, self._sessions())

    def _sessions(self) -> Iterator[PlenarySession]:
        aggregator = Aggregator(PlenarySession)
        return aggregator.mapped_records(
            map_func=map_plenary_session, group_keys=self._session_ids
        )
