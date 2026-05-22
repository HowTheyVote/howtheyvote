import datetime
from collections.abc import Iterator

from sqlalchemy import select
from structlog import get_logger

from ..analysis import VoteGroupsAnalyzer
from ..db import Session
from ..models import PlenarySession, Vote
from ..query import session_is_current_at
from ..scrapers import NoWorkingUrlError, VOTListScraper
from ..store import Aggregator, BulkWriter, index_records, map_vote
from ..waf import solve_ep_aws_waf_challenge
from .common import BasePipeline, DataUnavailable, generate_vote_sharepics

log = get_logger(__name__)


class VOTListPipeline(BasePipeline):
    def __init__(self, term: int, date: datetime.date):
        super().__init__(term=term, date=date)
        self.term = term
        self.date = date
        self._aws_waf_token = solve_ep_aws_waf_challenge()
        self._vote_ids: set[str] = set()

    def _run(self) -> None:
        self._scrape_vot_list()
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
