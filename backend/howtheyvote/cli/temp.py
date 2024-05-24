import datetime

import click
from cachetools import LRUCache
from sqlalchemy import or_, select
from structlog import get_logger

from ..db import Session
from ..files import vote_sharepic_path
from ..models import Member, PlenarySession, Vote
from ..query import member_active_at
from ..scrapers import (
    EurlexDocumentScraper,
    EurlexProcedureScraper,
    NoWorkingUrlError,
    ProcedureScraper,
    RCVListScraper,
    RequestCache,
    ScrapingError,
)
from ..sharepics import generate_vote_sharepic
from ..store import BulkWriter

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
def procedure_titles() -> None:
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
                    request_cache=cache,
                )
                writer.add(proc_scraper.run())
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
