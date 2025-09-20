import datetime

import click
from sqlalchemy import delete, func, select

from ..db import Session
from ..models import Fragment, Vote


@click.group()
def flush() -> None:
    """Flush fragments."""
    pass


@flush.command()
@click.option("--id", "vote_ids", type=int, multiple=True)
@click.option("--date", "dates", type=click.DateTime(formats=["%Y-%m-%d"]), multiple=True)
@click.option("--source-name", "source_names", multiple=True)
def votes(
    vote_ids: list[str],
    dates: list[datetime.datetime] | None,
    source_names: list[str],
) -> None:
    """Flush votes fragments."""
    if not vote_ids and not dates and not source_names:
        raise click.UsageError("Provide at least one option to filter fragments.")

    votes_query = select(Vote.id)

    if vote_ids:
        votes_query = votes_query.where(Vote.id.in_(vote_ids))

    if dates:
        votes_query = votes_query.where(
            func.date(Vote.timestamp).in_(date.date() for date in dates)
        )

    where = [
        Fragment.model == Vote.__name__,
        Fragment.group_key.in_(votes_query),
    ]

    if source_names:
        where.append(Fragment.source_name.in_(source_names))

    count = Session.execute(select(func.count()).select_from(Fragment).where(*where)).scalar()

    click.confirm(f"This will delete {count} fragments. Continue?", abort=True)

    result = Session.execute(delete(Fragment).where(*where))
    Session.commit()

    click.echo(f"Deleted {result.rowcount} fragments.")
