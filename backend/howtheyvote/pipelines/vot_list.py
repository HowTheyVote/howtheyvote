import datetime
from collections.abc import Iterator

import sentry_sdk
from cachetools import LRUCache
from sqlalchemy import select
from structlog import get_logger

from ..analysis import VoteGroupsAnalyzer
from ..db import Session
from ..models import PlenarySession, Vote
from ..query import session_is_current_at
from ..scrapers import (
    NoWorkingUrlError,
    ODPDocumentScraper,
    RequestCache,
    ScrapingError,
    VOTListScraper,
)
from ..store import Aggregator, BulkWriter, index_records, map_vote
from ..waf import solve_ep_aws_waf_challenge
from .common import BasePipeline, DataUnavailable, generate_vote_sharepics

log = get_logger(__name__)


class VOTListPipeline(BasePipeline):
    def __init__(self, term: int, date: datetime.date):
        super().__init__(term=term, date=date)
        self.term = term
        self.date = date
        self._vote_ids: set[str] = set()
        self._request_cache: RequestCache = LRUCache(maxsize=25)

    def _run(self) -> None:
        self._aws_waf_token = solve_ep_aws_waf_challenge()

        self._scrape_vot_list()

        # The `ODPDocumentScraper` retrieves amendment URLs for votes. We need to know
        # the amendment numbers to retrieve amendment URLs, and we only have the
        # amendment numbers once we’ve scraped the VOT list. So we need to re-scrape
        # the ODP documents after we’ve scraped the VOT list.
        self._scrape_odp_documents()

        self._analyze_vote_groups()
        self._index_votes()

        generate_vote_sharepics(self._votes())

    def _scrape_vot_list(self) -> None:
        self._log.info("Scraping VOT list")
        scraper = VOTListScraper(
            term=self.term,
            date=self.date,
            aws_waf_token=self._aws_waf_token,
        )

        try:
            fragments = list(scraper.run())
        except NoWorkingUrlError as exc:
            raise DataUnavailable("Pipeline data source is not available") from exc

        writer = BulkWriter()
        writer.add(fragments)
        writer.flush()

        self._vote_ids = writer.get_touched()

    def _scrape_odp_documents(self) -> None:
        log.info("Scraping ODP documents", date=self.date, term=self.term)
        writer = BulkWriter()

        for vote in self._votes():
            if not vote.reference:
                log.info(
                    "Skipping ODP document scraper as vote has no reference",
                    vote_id=vote.id,
                )
                continue

            if vote.reference.startswith("C"):
                log.info(
                    "Skipping ODP document scraper as reference is commission doc reference",
                    vote_id=vote.id,
                )
                continue

            scraper = ODPDocumentScraper(
                vote_id=vote.id,
                reference=vote.reference,
                amendment_number=vote.amendment_number,
                request_cache=self._request_cache,
            )

            try:
                writer.add(scraper.run())
            except NoWorkingUrlError:
                pass
            except ScrapingError as err:
                log.exception(
                    "Failed scraping document",
                    vote_id=vote.id,
                    reference=vote.reference,
                )
                sentry_sdk.capture_exception(err)

        writer.flush()

    def _analyze_vote_groups(self) -> None:
        self._log.info("Running vote groups analysis")
        writer = BulkWriter()
        session = Session.execute(
            select(PlenarySession).where(session_is_current_at(self.date))
        ).scalar_one()
        analyzer = VoteGroupsAnalyzer(
            session_start_date=session.start_date,
            votes=self._votes(),
        )
        writer.add(analyzer.run())
        writer.flush()

    def _index_votes(self) -> None:
        self._log.info("Indexing votes")
        index_records(Vote, self._votes())

    def _votes(self) -> Iterator[Vote]:
        aggregator = Aggregator(Vote)
        return aggregator.mapped_records(map_func=map_vote, group_keys=self._vote_ids)
