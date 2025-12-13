import datetime as dt
from collections.abc import Iterator

import sentry_sdk
from sqlalchemy import and_, func, select

from ..db import Session
from ..models import OEILSummary, Vote
from ..scrapers import OEILSummaryIDScraper, OEILSummaryScraper, ScrapingError
from ..store import Aggregator, BulkWriter, index_records, map_summary, map_vote
from .common import BasePipeline


class OEILSummariesPipeline(BasePipeline):
    def __init__(
        self,
        start_date: dt.date,
        end_date: dt.date,
        force: bool = False,
    ):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.force = force

    def _run(self) -> None:
        self._scrape_summary_ids()
        self._index_votes()
        self._scrape_summaries()
        self._index_summaries()

    def _scrape_summary_ids(self) -> None:
        query = select(Vote).where(
            and_(
                Vote.is_main == True,  #  noqa: E712
                func.date(Vote.timestamp) >= self.start_date,
                func.date(Vote.timestamp) <= self.end_date,
            ),
        )

        if not self.force:
            query = query.where(Vote.oeil_summary_id.is_(None))

        votes = Session.execute(query).scalars().all()

        self._log.info("Scrapping OEIL summary IDs", vote_count=len(votes))
        writer = BulkWriter()

        for vote in votes:
            if not vote.reference and not vote.procedure_reference:
                continue
            try:
                scraper = OEILSummaryIDScraper(
                    vote_id=vote.id,
                    reference=vote.reference,
                    procedure_reference=vote.procedure_reference,
                    day_of_vote=vote.date,
                )
                writer.add(scraper.run())
            except ScrapingError as err:
                self._log.exception(
                    "Failed scraping OEIL summary ID",
                    vote_id=vote.id,
                    reference=vote.reference,
                    procedure_reference=vote.procedure_reference,
                    day_of_vote=vote.date,
                )
                sentry_sdk.capture_exception(err)

        writer.flush()
        self._vote_ids = writer.get_touched()

    def _scrape_summaries(self) -> None:
        self._log.info("Scraping OEIL summaries")
        writer = BulkWriter()

        for vote in self._votes():
            if not vote.oeil_summary_id:
                continue
            try:
                scraper = OEILSummaryScraper(summary_id=vote.oeil_summary_id)
                writer.add(scraper.run())
            except ScrapingError as err:
                self._log.exception(
                    "Failed scraping OEIL summary",
                    oeil_summary_id=vote.oeil_summary_id,
                )
                sentry_sdk.capture_exception(err)

        writer.flush()
        self._summary_ids = writer.get_touched()

    def _summaries(self) -> Iterator[OEILSummary]:
        aggregator = Aggregator(OEILSummary)
        return aggregator.mapped_records(map_func=map_summary, group_keys=self._summary_ids)

    def _votes(self) -> Iterator[Vote]:
        aggregator = Aggregator(Vote)
        return aggregator.mapped_records(map_func=map_vote, group_keys=self._vote_ids)

    def _index_votes(self) -> None:
        self._log.info("Indexing votes")
        index_records(Vote, self._votes())

    def _index_summaries(self) -> None:
        self._log.info("Indexing summaries")
        index_records(OEILSummary, self._summaries())
