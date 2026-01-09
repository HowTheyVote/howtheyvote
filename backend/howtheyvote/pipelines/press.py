import datetime
from collections.abc import Iterator

import sentry_sdk
from sqlalchemy import func, select
from structlog import get_logger

from ..analysis import PressReleaseAnalyzer, PressReleaseVotePositionCountsAnalyzer
from ..db import Session
from ..models import PlenarySession, PressRelease, Vote
from ..query import session_is_current_at
from ..scrapers import (
    PressReleaseScraper,
    PressReleasesIndexScraper,
    PressReleasesRSSScraper,
    ScrapingError,
)
from ..store import Aggregator, BulkWriter, index_records, map_press_release, map_vote
from .common import BasePipeline

log = get_logger(__name__)


class PressPipeline(BasePipeline):
    # At the time we introduced this constant, the value covered roughly one term. However,
    # this obviously depends on the amount of press releases published and might need to be
    # adjusted or made configurable in the future.
    MAX_PAGES = 175

    def __init__(
        self,
        date: datetime.date | None = None,
        with_rss: bool | None = False,
    ):
        super().__init__(date=date, with_rss=with_rss)
        self.date = date
        self.with_rss = with_rss
        self._release_ids: set[str] = set()
        self._vote_ids: set[str] = set()

    def _run(self) -> None:
        if self.with_rss:
            self._scrape_press_releases_rss()

        self._scrape_press_releases_index()
        self._scrape_press_releases()
        self._analyze_vote_position_counts()
        self._match_press_releases()
        self._index_press_releases()
        self._index_votes()

    def _scrape_press_releases_rss(self) -> None:
        log.info("Fetching press releases from RSS", date=self.date)
        writer = BulkWriter()
        scraper = PressReleasesRSSScraper()
        writer.add(scraper.run())
        writer.flush()
        self._release_ids.update(writer.get_touched())

    def _scrape_press_releases_index(self) -> None:
        # There are two ways of running this pipeline, with or without a date. When passing
        # a date, we use the filtering options of the EP Press Room. Without a date, we simply
        # iterate over all press releases (up to a maximum number of pages).

        if self.date:
            # The filtering feature of the EP Press Room often doesn't return all press
            # releases for the given date. Sometimes the index in one language doesn't include
            # all press releases (even if individual releases are translated), so we scrape
            # both languages. However, even this likely misses a few press releases.
            self._scrape_press_releases_index_by_date(language="fr", date=self.date)
            self._scrape_press_releases_index_by_date(language="en", date=self.date)
        else:
            for page in range(self.MAX_PAGES):
                self._scrape_press_releases_index_by_page(language="en", page=page)

    def _scrape_press_releases_index_by_page(self, language: str, page: int) -> None:
        writer = BulkWriter()
        log.info("Scraping press releases by page", page=page)
        scraper = PressReleasesIndexScraper(language=language, page=page)
        writer.add(scraper.run())
        writer.flush()

        self._release_ids.update(writer.get_touched())

    def _scrape_press_releases_index_by_date(self, language: str, date: datetime.date) -> None:
        log.info("Fetching plenary session information", date=date)
        query = select(PlenarySession).where(session_is_current_at(date))
        plenary_session = Session.execute(query).scalar()

        if not plenary_session:
            log.error("No plenary session found for the given day.", date=self.date)
            return

        writer = BulkWriter()

        log.info("Scraping press releases by date", date=self.date)
        scraper = PressReleasesIndexScraper(
            session_start_date=plenary_session.start_date,
            language=language,
        )
        writer.add(scraper.run())
        writer.flush()

        self._release_ids.update(writer.get_touched())

    def _scrape_press_releases(self) -> None:
        writer = BulkWriter(auto_flush=1000)

        for release_id in self._release_ids:
            log.info("Scraping press release contents", release_id=release_id, date=self.date)

            try:
                scraper = PressReleaseScraper(release_id=release_id)
                writer.add(scraper.run())
            except ScrapingError as err:
                log.exception(
                    "Failed scraping press release contents",
                    release_id=release_id,
                    date=self.date,
                )
                sentry_sdk.capture_exception(err)

        writer.flush()

    def _analyze_vote_position_counts(self) -> None:
        writer = BulkWriter()

        for press_release in self._press_releases():
            log.info(
                "Extracting vote position counts",
                release_id=press_release.id,
                date=self.date,
            )
            analyzer = PressReleaseVotePositionCountsAnalyzer(
                release_id=press_release.id,
                text=press_release.text,
            )
            writer.add(analyzer.run())

        writer.flush()

    def _match_press_releases(self) -> None:
        dates = set(pr.published_at.date() for pr in self._press_releases() if pr.published_at)
        log.info("Matching press releases and votes for dates", count=len(dates))

        for date in dates:
            self._match_press_releases_by_date(date)

    def _match_press_releases_by_date(self, date: datetime.date) -> None:
        log.info("Fetching votes", date=date)
        query = select(Vote).where(func.date(Vote.timestamp) == date)
        votes = list(Session.execute(query).scalars())

        if not votes:
            log.error(
                "No votes found for given date, skipping press release matching",
                dates=date,
            )
            return

        log.info("Matching press releases and votes", date=date)
        writer = BulkWriter()
        analyzer = PressReleaseAnalyzer(votes=votes, press_releases=self._press_releases())
        writer.add(analyzer.run())
        writer.flush()

        self._vote_ids.update(writer.get_touched())

    def _index_press_releases(self) -> None:
        log.info("Indexing press releases", date=self.date)
        index_records(PressRelease, self._press_releases())

    def _index_votes(self) -> None:
        log.info("Indexing votes", date=self.date)
        index_records(Vote, self._votes())

    def _press_releases(self) -> Iterator[PressRelease]:
        aggregator = Aggregator(PressRelease)
        return aggregator.mapped_records(
            map_func=map_press_release, group_keys=self._release_ids
        )

    def _votes(self) -> Iterator[Vote]:
        aggregator = Aggregator(Vote)
        return aggregator.mapped_records(map_func=map_vote, group_keys=self._vote_ids)
