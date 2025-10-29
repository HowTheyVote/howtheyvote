import datetime
from collections.abc import Iterator

from structlog import get_logger

from ..models import Vote
from ..scrapers import NoWorkingUrlError, VOTListScraper
from ..store import Aggregator, BulkWriter, index_records, map_vote
from .common import BasePipeline, DataUnavailable, generate_vote_sharepics

log = get_logger(__name__)


class VOTListPipeline(BasePipeline):
    def __init__(self, term: int, date: datetime.date):
        super().__init__(term=term, date=date)
        self.term = term
        self.date = date
        self._vote_ids: set[str] = set()

    def _run(self) -> None:
        self._scrape_vot_list()
        self._index_votes()

        generate_vote_sharepics(self._votes())

    def _scrape_vot_list(self) -> None:
        self._log.info("Scraping VOT list")
        scraper = VOTListScraper(term=self.term, date=self.date)

        try:
            fragments = list(scraper.run())
        except NoWorkingUrlError as exc:
            raise DataUnavailable("Pipeline data source is not available") from exc

        writer = BulkWriter()
        writer.add(fragments)
        writer.flush()

        self._vote_ids = writer.get_touched()

    def _index_votes(self) -> None:
        self._log.info("Indexing votes")
        index_records(Vote, self._votes())

    def _votes(self) -> Iterator[Vote]:
        aggregator = Aggregator(Vote)
        return aggregator.mapped_records(map_func=map_vote, group_keys=self._vote_ids)
