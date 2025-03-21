import datetime

import click
from sqlalchemy import select
from structlog import get_logger

from ..db import Session
from ..models import PlenarySession
from ..pipelines import (
    MembersPipeline,
    PressPipeline,
    RCVListEnglishPipeline,
    RCVListPipeline,
    SessionsPipeline,
)

log = get_logger(__name__)


@click.group()
def pipeline() -> None:
    """Run a data pipeline."""
    pass


@pipeline.command()
@click.option("--term", type=int, required=True)
@click.option("--skip-members", is_flag=True)
@click.option("--skip-sessions", is_flag=True)
@click.option("--skip-rcv-lists", is_flag=True)
@click.option("--skip-press", is_flag=True)
def all(
    term: int,
    skip_members: bool = False,
    skip_sessions: bool = False,
    skip_rcv_lists: bool = False,
    skip_press: bool = False,
) -> None:
    """Run all data pipelines for a given term. This can be useful to scrape data
    for an entire term from scratch. However, it can take several hours to complete."""
    if not skip_members:
        members_pipe = MembersPipeline(term=term)
        members_pipe.run()

    if not skip_sessions:
        sessions_pipe = SessionsPipeline(term=term)
        sessions_pipe.run()

    if not skip_rcv_lists:
        query = select(PlenarySession).where(PlenarySession.term == term)
        results = Session.execute(query, {"yield_per": 500}).scalars()

        for session in results:
            delta = session.end_date - session.start_date

            for i in range(delta.days + 1):
                date = session.start_date + datetime.timedelta(days=i)
                rcv_pipe = RCVListPipeline(term=term, date=date)
                rcv_pipe.run()

    if not skip_press:
        press_pipe = PressPipeline()
        press_pipe.run()


@pipeline.command()
@click.option("--term", type=int, required=True)
@click.option("--date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
def rcv_list(term: int, date: datetime.datetime) -> None:
    """Run the RCV list pipeline for a given day. This scrapes the list of roll-call votes
    for the given day as well as additional sources for related legislative procedures or
    plenary documents."""
    pipeline = RCVListPipeline(term=term, date=date.date())
    pipeline.run()


@pipeline.command()
@click.option("--term", type=int, required=True)
@click.option("--date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
def rcv_list_en(term: int, date: datetime.datetime) -> None:
    """Run the English RCV lists pipeline for a given day. This scrapes only vote titles,
    but not the actualy vote results or any other data."""
    pipeline = RCVListEnglishPipeline(term, date)
    pipeline.run()


@pipeline.command()
@click.option("--date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.option("--rss", type=bool, is_flag=True)
def press(date: datetime.datetime, rss: bool = False) -> None:
    """Run the press pipeline for a given day. This scrapes official EP press releases and
    tries to match them to votes that took place on the same day."""
    pipeline = PressPipeline(date=date.date(), with_rss=rss)
    pipeline.run()


@pipeline.command()
@click.option("--term", type=int, required=True)
def members(term: int) -> None:
    """Run the members pipeline for a given term. This scrapes a complete lists of all
    current and past members as well as additional information about them."""
    pipeline = MembersPipeline(term=term)
    pipeline.run()


@pipeline.command()
@click.option("--term", type=int, required=True)
def sessions(term: int) -> None:
    """Run the sessions pipeline for a given term. This scrapes plenary session dates
    and locations."""
    pipeline = SessionsPipeline(term=term)
    pipeline.run()
