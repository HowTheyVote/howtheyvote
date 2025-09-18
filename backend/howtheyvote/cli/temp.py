import datetime

import click
from cachetools import LRUCache
from sqlalchemy import func, or_, select
from structlog import get_logger

from ..analysis import PressReleaseAnalyzer, VotePositionCountsAnalyzer
from ..db import Session
from ..files import vote_sharepic_path
from ..models import Fragment, Member, PlenarySession, PressRelease, Vote
from ..query import member_active_at
from ..scrapers import (
    DocumentScraper,
    EurlexDocumentScraper,
    EurlexProcedureScraper,
    NoWorkingUrlError,
    PressReleaseScraper,
    ProcedureScraper,
    RCVListScraper,
    RequestCache,
    ScrapingError,
    VOTListScraper,
)
from ..sharepics import generate_vote_sharepic
from ..store import Aggregator, BulkWriter, index_records, map_press_release

log = get_logger(__name__)


@click.group()
def temp() -> None:
    """A namespace for temporary commands required as workarounds or for data migrations."""
    pass


@temp.command()
def sharepics() -> None:
    """Generate share pictures for all votes."""
    query = select(Vote).where(Vote.is_main == True)  # noqa: E712
    votes = Session.execute(query, execution_options={"yield_per": 500}).scalars()

    for vote in votes:
        try:
            image = generate_vote_sharepic(vote.id)
        except Exception:
            log.info("Failed generating sharepic", vote_id=vote.id)
            continue

        path = vote_sharepic_path(vote.id)
        path.write_bytes(image)


@temp.command()
def eurovoc() -> None:
    """Scrape EuroVoc concepts for all votes."""
    query = select(Vote)
    query = query.where(
        or_(
            Vote.procedure_reference != None,  # noqa: E711
            Vote.reference != None,  # noqa: E711
        )
    )
    query = query.order_by(
        Vote.procedure_reference,
        Vote.reference,
    )
    votes = Session.execute(query, execution_options={"yield_per": 500}).scalars()
    cache: RequestCache = LRUCache(maxsize=50)
    writer = BulkWriter()

    for partition in votes.partitions():
        for vote in partition:
            if not vote.procedure_reference:
                continue

            try:
                proc_scraper = EurlexProcedureScraper(
                    vote_id=vote.id,
                    procedure_reference=vote.procedure_reference,
                    request_cache=cache,
                )
                writer.add(proc_scraper.run())
            except ScrapingError:
                pass

        for vote in partition:
            if not vote.reference:
                continue

            try:
                doc_scraper = EurlexDocumentScraper(
                    vote_id=vote.id,
                    reference=vote.reference,
                    request_cache=cache,
                )
                writer.add(doc_scraper.run())
            except ScrapingError:
                pass

        writer.flush()


@temp.command()
def procedures() -> None:
    """Scrape all procedure files."""
    query = select(Vote)
    query = query.where(Vote.procedure_reference != None)  # noqa: E711
    query = query.order_by(Vote.procedure_reference)
    votes = Session.execute(query, execution_options={"yield_per": 500}).scalars()
    cache: RequestCache = LRUCache(maxsize=50)
    writer = BulkWriter()

    for partition in votes.partitions():
        for vote in partition:
            if not vote.procedure_reference:
                continue

            try:
                proc_scraper = ProcedureScraper(
                    vote_id=vote.id,
                    procedure_reference=vote.procedure_reference,
                    reference=vote.reference,
                    request_cache=cache,
                )
                writer.add(proc_scraper.run())
            except ScrapingError:
                pass

        writer.flush()


@temp.command()
def documents() -> None:
    """Scrape all referenced documents"""
    query = select(Vote)
    query = query.where(Vote.reference != None)  # noqa: E711
    query = query.order_by(Vote.reference)
    votes = Session.execute(query, execution_options={"yield_per": 500}).scalars()
    cache: RequestCache = LRUCache(maxsize=50)
    writer = BulkWriter()

    for partition in votes.partitions():
        for vote in partition:
            if not vote.reference:
                continue

            try:
                doc_scraper = DocumentScraper(
                    vote_id=vote.id,
                    reference=vote.reference,
                    request_cache=cache,
                )
                writer.add(doc_scraper.run())
            except ScrapingError:
                pass

        writer.flush()


@temp.command()
def rcv_lists() -> None:
    """Scrape all RCV lists."""
    writer = BulkWriter()

    query = select(PlenarySession)
    query = query.where(PlenarySession.start_date <= datetime.datetime.now())
    results = Session.execute(query).scalars()

    for session in results:
        delta = session.end_date - session.start_date

        for i in range(delta.days + 1):
            date = session.start_date + datetime.timedelta(days=i)

            members_query = (
                select(Member)
                .where(member_active_at(date))
                .with_only_columns(
                    Member.id,
                    Member.first_name,
                    Member.last_name,
                )
            )
            active_members = [tuple(row) for row in Session.execute(members_query).all()]

            scraper = RCVListScraper(
                term=session.term,
                date=date,
                active_members=active_members,
            )

            try:
                writer.add(scraper.run())
            except NoWorkingUrlError:
                pass

            writer.flush()


@temp.command()
def vot_lists() -> None:
    """Scrape all VOT lists."""
    writer = BulkWriter()

    query = select(PlenarySession)
    query = query.where(
        PlenarySession.start_date <= datetime.datetime.now(),
        PlenarySession.start_date >= datetime.datetime(2024, 1, 1),
    )
    results = Session.execute(query).scalars()

    for session in results:
        delta = session.end_date - session.start_date

        for i in range(delta.days + 1):
            date = session.start_date + datetime.timedelta(days=i)

            scraper = VOTListScraper(term=session.term, date=date)

            try:
                writer.add(scraper.run())
            except NoWorkingUrlError:
                pass

            writer.flush()


@temp.command()
def fill_term_column() -> None:
    """Set term to 9 for all terms without stored term."""
    query = select(Vote)
    query = query.where(Vote.term == None)  # noqa: E711
    votes = Session.execute(query, execution_options={"yield_per": 500}).scalars()
    writer = BulkWriter()

    for partition in votes.partitions():
        for vote in partition:
            fragment = Fragment(
                source_id=vote.id,
                group_key=vote.id,
                source_name="FillTermColumnCommand",
                model="Vote",
                data={"term": 9},
            )
            writer.add(fragment)
        writer.flush()


@temp.command()
def press_releases() -> None:
    dates = Session.execute(
        select(func.distinct(func.date(PressRelease.published_at)))
    ).scalars()

    for date in dates:
        # Scrape press releases
        writer = BulkWriter()
        release_ids = list(
            Session.execute(
                select(PressRelease.id).where(func.date(PressRelease.published_at) == date)
            ).scalars()
        )

        for release_id in release_ids:
            scraper = PressReleaseScraper(release_id)
            writer.add(scraper.run())

        writer.flush()

        # Extract position counts
        writer = BulkWriter()
        aggregator = Aggregator(PressRelease)
        releases = list(
            aggregator.mapped_records(
                map_func=map_press_release,
                group_keys=release_ids,
            )
        )
        for release in releases:
            writer.add(VotePositionCountsAnalyzer(release.id, release.text).run())
        writer.flush()

        # Index press releases
        releases = list(
            aggregator.mapped_records(
                map_func=map_press_release,
                group_keys=release_ids,
            )
        )
        index_records(PressRelease, releases)

        # Match press releases and votes
        writer = BulkWriter()
        votes = list(
            Session.execute(select(Vote).where(func.date(Vote.timestamp) == date)).scalars()
        )
        writer.add(PressReleaseAnalyzer(votes, releases).run())
        writer.flush()
