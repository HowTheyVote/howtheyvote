import time
from collections.abc import Iterator

from structlog import get_logger

from .. import config
from ..files import download_file, image_thumb, member_photo_path
from ..models import Member
from ..scrapers import (
    MemberGroupsScraper,
    MemberInfoScraper,
    MembersScraper,
    ScrapingError,
)
from ..store import Aggregator, BulkWriter, index_records, map_member
from .common import BasePipeline

log = get_logger(__name__)


class MembersPipeline(BasePipeline):
    def __init__(self, term: int):
        super().__init__(term=term)
        self.term = term
        self._member_ids: set[str] = set()

    def _run(self) -> None:
        self._scrape_members()
        self._scrape_member_groups()
        self._scrape_member_infos()
        self._index_members()
        self._download_member_photos()

    def _scrape_members(self) -> None:
        log.info("Scraping RCV lists", term=self.term)

        writer = BulkWriter()
        scraper = MembersScraper(term=self.term)
        writer.add(scraper.run())
        writer.flush()

        self._member_ids = writer.get_touched()

    def _scrape_member_groups(self) -> None:
        writer = BulkWriter()

        for member in self._members():
            log.info("Scraping member groups", term=self.term, member_id=member.id)

            try:
                scraper = MemberGroupsScraper(web_id=member.id, term=self.term)
                writer.add(scraper.run())
            except ScrapingError:
                log.exception(
                    "Failed scraping member groups", member_id=member.id, term=self.term
                )

        writer.flush()

    def _scrape_member_infos(self) -> None:
        writer = BulkWriter()

        for member in self._members():
            log.info("Scraping member info", term=self.term, member_id=member.id)

            try:
                scraper = MemberInfoScraper(web_id=member.id)
                writer.add(scraper.run())
            except ScrapingError:
                log.exception(
                    "Failed scraping member info", member_id=member.id, term=self.term
                )

        writer.flush()

    def _download_member_photos(self) -> None:
        for member in self._members():
            url = f"https://www.europarl.europa.eu/mepphoto/{member.id}.jpg"

            log.info("Downloading member photo.", member_id=member.id)

            try:
                path = download_file(url, member_photo_path(member.id))
            except Exception:
                log.exception("Failed download member photo.", member_id=member.id)
                continue

            if not path:
                log.error("Failed downloading member photo.", member_id=member.id)
                continue

            log.info("Creating member photo thumbnail.", web_id=member.id)
            image_thumb(path, member_photo_path(member.id, size=104), format="jpeg", size=104)

            time.sleep(config.REQUEST_SLEEP)

    def _index_members(self) -> None:
        log.info("Indexing members", term=self.term)
        index_records(Member, self._members())

    def _members(self) -> Iterator[Member]:
        aggregator = Aggregator(Member)
        return aggregator.mapped_records(map_func=map_member, group_keys=self._member_ids)
