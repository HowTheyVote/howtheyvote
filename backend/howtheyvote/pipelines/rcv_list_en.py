import datetime
from collections.abc import Iterator

from cachetools import LRUCache

from ..models import Vote
from ..scrapers import RCVListEnglishScraper, RequestCache
from ..store import Aggregator, BulkWriter, index_records, map_vote
from .common import BasePipeline


class RCVListEnglishPipeline(BasePipeline):
    """Scrapes the English RCV vote results for a single day. This is a separate pipeline
    from `RCVListPipeline` (which uses French RCV lists) because the English and French
    version are often published at different times."""

    def __init__(
        self,
        term: int,
        date: datetime.date,
        last_run_checksum: str | None = None,
    ):
        super().__init__(term=term, date=date)
        self.term = term
        self.date = date
        self._vote_ids: set[str] = set()
        self._request_cache: RequestCache = LRUCache(maxsize=25)

    def _run(self) -> None:
        self._scrape_rcv_list()
        self._index_votes()

    def _scrape_rcv_list(self) -> None:
        self._log.info("Scraping RCV lists", date=self.date, term=self.term)

        scraper = RCVListEnglishScraper(term=self.term, date=self.date)
        writer = BulkWriter()
        writer.add(scraper.run())
        writer.flush()

        self._vote_ids = writer.get_touched()

    def _index_votes(self) -> None:
        self._log.info("Indexing votes", date=self.date, term=self.term)
        index_records(Vote, self._votes())

    def _votes(self) -> Iterator[Vote]:
        aggregator = Aggregator(Vote)
        return aggregator.mapped_records(map_func=map_vote, group_keys=self._vote_ids)
