import datetime
from collections.abc import Iterator

from cachetools import LRUCache
from prometheus_client import Counter
from sqlalchemy import select
from structlog import get_logger

from ..analysis import (
    MainVoteAnalyzer,
    VoteGroupsAnalyzer,
)
from ..db import Session
from ..files import ensure_parent, vote_sharepic_path
from ..helpers import frontend_url
from ..models import Member, Vote, VoteGroup
from ..pushover import send_notification
from ..query import member_active_at
from ..scrapers import (
    DocumentScraper,
    EurlexDocumentScraper,
    EurlexProcedureScraper,
    NoWorkingUrlError,
    ProcedureScraper,
    RCVListScraper,
    RequestCache,
    ScrapingError,
)
from ..sharepics import generate_vote_sharepic
from ..store import Aggregator, BulkWriter, index_records, map_vote, map_vote_group
from .common import (
    BasePipeline,
    DataUnavailable,
    DataUnchanged,
    compute_response_checksum,
)

log = get_logger(__name__)

SHAREPICS_GENERATED = Counter(
    "htv_sharepics_generated_total",
    "Total number of generated sharepics",
    ["status"],
)


class RCVListPipeline(BasePipeline):
    """Scrapes the RCV vote results for a single day, then runs analysis on the
    extracted votes and scrapes additional information such as data about legislative
    procedures."""

    def __init__(
        self,
        term: int,
        date: datetime.date,
        last_run_checksum: str | None = None,
    ):
        super().__init__(term=term, date=date, last_run_checksum=last_run_checksum)
        self.term = term
        self.date = date
        self.last_run_checksum = last_run_checksum
        self.checksum: str | None = None
        self._vote_ids: set[str] = set()
        self._vote_group_ids: set[str] = set()
        self._request_cache: RequestCache = LRUCache(maxsize=25)

    def _run(self) -> None:
        self._scrape_rcv_list()
        self._scrape_documents()
        self._scrape_eurlex_documents()
        self._scrape_procedures()
        self._scrape_eurlex_procedures()
        self._analyze_main_votes()
        self._analyze_vote_groups()
        self._index_votes()

        # Share pictures have to be generated after the votes are indexed. Otherwise,
        # rendering the share pictures fails as data about new votes hasn’t yet been
        # written to the database.
        self._generate_vote_sharepics()

        self._index_vote_groups()

        # Send Pushover notification
        send_notification(
            title=f"Scraped RCV list for {self.date.strftime('%a, %b %-d')}",
            message=f"{len(self._vote_ids)} votes, {len(self._vote_group_ids)} vote groups",
            url=frontend_url("votes"),
        )

    def _scrape_rcv_list(self) -> None:
        log.info("Fetching active members", date=self.date)
        query = (
            select(Member)
            .where(member_active_at(self.date))
            .with_only_columns(
                Member.id,
                Member.first_name,
                Member.last_name,
            )
        )
        active_members = [tuple(row) for row in Session.execute(query).all()]

        log.info("Scraping RCV lists", date=self.date, term=self.term)
        scraper = RCVListScraper(
            term=self.term,
            date=self.date,
            active_members=active_members,
        )

        try:
            fragments = scraper.run()
        except NoWorkingUrlError as exc:
            raise DataUnavailable("Pipeline data source is not available") from exc

        if (
            self.last_run_checksum is not None
            and self.last_run_checksum == compute_response_checksum(scraper.response)
        ):
            raise DataUnchanged("The data source hasn't changed since the last pipeline run.")

        self.checksum = compute_response_checksum(scraper.response)

        writer = BulkWriter()
        writer.add(fragments)
        writer.flush()

        self._vote_ids = writer.get_touched()

    def _scrape_documents(self) -> None:
        log.info("Scraping documents", date=self.date, term=self.term)
        writer = BulkWriter()

        for vote in self._votes():
            if not vote.reference:
                log.info(
                    "Skipping document scraper as vote has no reference",
                    vote_id=vote.id,
                )
                continue

            scraper = DocumentScraper(
                vote_id=vote.id,
                reference=vote.reference,
                request_cache=self._request_cache,
            )

            try:
                writer.add(scraper.run())
            except ScrapingError:
                log.exception(
                    "Failed scraping document",
                    vote_id=vote.id,
                    reference=vote.reference,
                )

        writer.flush()

    def _scrape_eurlex_documents(self) -> None:
        log.info("Scraping EUR-Lex documents", date=self.date, term=self.term)
        writer = BulkWriter()

        for vote in self._votes():
            if not vote.reference:
                log.info(
                    "Skipping EUR-Lex document scraper as vote has no reference",
                    vote_id=vote.id,
                )
                continue

            scraper = EurlexDocumentScraper(
                vote_id=vote.id,
                reference=vote.reference,
                request_cache=self._request_cache,
            )

            try:
                writer.add(scraper.run())
            except ScrapingError:
                log.exception(
                    "Failed scraping EUR-Lex document",
                    vote_id=vote.id,
                    procedure_reference=vote.reference,
                )

        writer.flush()

    def _scrape_procedures(self) -> None:
        log.info("Scraping procedures", date=self.date, term=self.term)
        writer = BulkWriter()

        for vote in self._votes():
            if not vote.procedure_reference:
                log.info(
                    "Skipping procedure scraper as vote has no procedure reference",
                    vote_id=vote.id,
                )
                continue

            scraper = ProcedureScraper(
                vote_id=vote.id,
                procedure_reference=vote.procedure_reference,
                request_cache=self._request_cache,
            )

            try:
                writer.add(scraper.run())
            except ScrapingError:
                log.exception(
                    "Failed scraping procedure",
                    vote_id=vote.id,
                    procedure_reference=vote.procedure_reference,
                )

        writer.flush()

    def _scrape_eurlex_procedures(self) -> None:
        log.info("Scraping EUR-Lex procedures", date=self.date, term=self.term)
        writer = BulkWriter()

        for vote in self._votes():
            if not vote.procedure_reference:
                log.info(
                    "Skipping EUR-Lex procedure scraper as vote has no procedure reference",
                    vote_id=vote.id,
                )
                continue

            scraper = EurlexProcedureScraper(
                vote_id=vote.id,
                procedure_reference=vote.procedure_reference,
                request_cache=self._request_cache,
            )

            try:
                writer.add(scraper.run())
            except ScrapingError:
                log.exception(
                    "Failed scraping EUR-Lex procedure",
                    vote_id=vote.id,
                    procedure_reference=vote.procedure_reference,
                )

        writer.flush()

    def _analyze_main_votes(self) -> None:
        log.info("Running main votes analysis", date=self.date, term=self.term)
        writer = BulkWriter()

        for vote in self._votes():
            analyzer = MainVoteAnalyzer(
                vote_id=vote.id, description=vote.description, title=vote.title
            )
            writer.add(analyzer.run())

        writer.flush()

    def _analyze_vote_groups(self) -> None:
        log.info("Running vote groups analysis", date=self.date, term=self.term)
        writer = BulkWriter()
        analyzer = VoteGroupsAnalyzer(date=self.date, votes=self._votes())
        writer.add(analyzer.run())
        writer.flush()

        self._vote_group_ids = writer.get_touched()

    def _generate_vote_sharepics(self) -> None:
        failure_count = 0
        success_count = 0

        for vote in self._votes():
            if not vote.is_main:
                log.info(
                    "Skipping sharepic generation because vote is not main.", vote_id=vote.id
                )
                continue

            log.info("Generating vote sharepic.", vote_id=vote.id)

            try:
                image = generate_vote_sharepic(vote.id)
                path = vote_sharepic_path(vote.id)
                ensure_parent(path)
                path.write_bytes(image)
                SHAREPICS_GENERATED.labels(status="success").inc()
                success_count += 1
            except Exception:
                log.exception("Failed generating vote sharepic.", vote_id=vote.id)
                SHAREPICS_GENERATED.labels(status="error").inc()
                failure_count += 1

        if failure_count > 0:
            send_notification(
                title="Failed generating sharepics",
                message=f"{failure_count} failures (out of {success_count + failure_count})",
            )

    def _index_votes(self) -> None:
        log.info("Indexing votes", date=self.date, term=self.term)
        index_records(Vote, self._votes())

    def _index_vote_groups(self) -> None:
        log.info("Indexing vote groups", date=self.date, term=self.term)
        index_records(VoteGroup, self._vote_groups())

    def _votes(self) -> Iterator[Vote]:
        aggregator = Aggregator(Vote)
        return aggregator.mapped_records(map_func=map_vote, group_keys=self._vote_ids)

    def _vote_groups(self) -> Iterator[VoteGroup]:
        aggregator = Aggregator(VoteGroup)
        return aggregator.mapped_records(
            map_func=map_vote_group, group_keys=self._vote_group_ids
        )
