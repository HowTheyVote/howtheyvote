import datetime as dt
from collections.abc import Iterator
from datetime import datetime, timedelta

from sqlalchemy import distinct, func, select
from structlog import get_logger

from ..db import Session
from ..models import OEILSummary, Vote
from ..scrapers import OEILSummaryIDScraper, OEILSummaryScraper, ScrapingError
from ..store import Aggregator, BulkWriter, index_records, map_summary, map_vote
from .common import BasePipeline

log = get_logger(__name__)


class OEILSummaryPipeline(BasePipeline):
    def __init__(self, date: dt.date | None = None, force: bool = False):
        super().__init__()
        self.date = date if date else None
        self.force = force

    def _run(self) -> None:
        self._scrape_summary_ids()
        self._index_votes()
        self._scrape_summaries()
        self._index_summaries()

    def _scrape_summary_ids(self) -> None:
        query = select(Vote).where(Vote.is_main)
        if self.date:
            query = query.where(func.date(Vote.date) == self.date)
        else:
            query = query.where(
                Vote.timestamp.between(datetime.now() - timedelta(weeks=8), datetime.now())
            )

        if not self.force:
            query = query.where(Vote.oeil_summary_id.is_(None))

        votes = Session.execute(query).scalars().all()

        writer = BulkWriter()

        log.info("Scrapping OEIL summaries")

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
            except ScrapingError:
                pass

        writer.flush()
        self._vote_ids = writer.get_touched()

    def _scrape_summaries(self) -> None:
        already_scraped_summaries = select(OEILSummary.id).scalar_subquery()

        query = select(distinct(Vote.oeil_summary_id)).where(Vote.oeil_summary_id.is_not(None))

        if self.date:
            query = query.where(func.date(Vote.timestamp) == self.date)

        if not self.force:
            query = query.where(~Vote.oeil_summary_id.in_(already_scraped_summaries))

        result = Session.execute(query).scalars().all()

        writer = BulkWriter()

        for summary_id in result:
            if summary_id is None:
                continue
            try:
                scraper = OEILSummaryScraper(summary_id=summary_id)
                writer.add(scraper.run())
            except ScrapingError:
                pass

        writer.flush()
        self._summary_ids = writer.get_touched()

    def _summaries(self) -> Iterator[OEILSummary]:
        aggregator = Aggregator(OEILSummary)
        return aggregator.mapped_records(map_func=map_summary, group_keys=self._summary_ids)

    def _votes(self) -> Iterator[Vote]:
        aggregator = Aggregator(Vote)
        return aggregator.mapped_records(map_func=map_vote, group_keys=self._vote_ids)

    def _index_votes(self) -> None:
        log.info("Indexing votes")
        index_records(Vote, self._votes())

    def _index_summaries(self) -> None:
        log.info("Indexing summaries")
        index_records(OEILSummary, self._summaries())
