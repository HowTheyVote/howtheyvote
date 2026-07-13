import re
from collections import defaultdict

import click
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from ..api.query import SearchQuery
from ..db import Session
from ..models import Fragment, Vote
from ..search import field_to_prefix, get_index, prefix_to_field
from ..store import (
    Aggregator,
    index_records,
    make_cli_fragment_source,
    map_vote,
    upsert_fragments,
)


@click.group()
def search() -> None:
    """Search index debugging tools"""
    pass


@search.command()
@click.argument("vote_id", type=int)
def terms(vote_id: int) -> None:
    """Returns a list of terms for a given vote."""

    with get_index(Vote) as index:
        doc = index.get_document(vote_id)
        terms = [item.term.decode("utf-8") for item in doc.termlist()]

        # Group terms by prefix
        groups: dict[str | None, list[str]] = defaultdict(list)

        for full_term in terms:
            match = re.match(r"^([A-Z]+)(.*)$", full_term)

            if match:
                prefix = match.group(1)
                term = match.group(2)
            else:
                prefix = None
                term = full_term

            groups[prefix].append(term)

        for prefix, terms in groups.items():
            if prefix:
                click.echo(prefix_to_field(prefix).upper())
            else:
                click.echo("NO PREFIX")

            for term in terms:
                click.echo(term)

            click.echo()


@search.command()
@click.argument("vote_id", type=int)
@click.argument("field", type=str)
@click.argument("term", type=str)
def positions(vote_id: int, field: str, term: str) -> None:
    """Returns a list of positions for the given vote, field, and term."""
    prefix = field_to_prefix(field)

    with get_index(Vote) as index:
        for position in index.positionlist(vote_id, f"{prefix}{term}"):
            click.echo(position)


@search.command()
def dictionary() -> None:
    """Returns a list of all terms in the dictionary."""

    with get_index(Vote) as index:
        for term in index.spellings():
            click.echo(term.term)


@search.command()
def synonyms() -> None:
    """Returns a list of all synonyms."""

    with get_index(Vote) as index:
        for term in index.synonym_keys():
            for synonym in index.synonyms(term):
                click.echo(f"{term.decode('utf-8')}:{synonym.decode('utf-8')}")


@search.command()
@click.argument("query")
def query(query: str) -> None:
    """Print a text representation of the parsed query."""
    click.echo(SearchQuery(Vote).query(query).debug())


@search.group()
def keywords() -> None:
    """Manage search keywords for individual votes."""
    pass


@keywords.command("add")
@click.argument("vote_id", type=int)
@click.argument("keyword")
def add_keyword(vote_id: int, keyword: str) -> None:
    try:
        vote = Session.execute(select(Vote).where(Vote.id == vote_id)).scalar_one()
    except NoResultFound as exc:
        raise click.UsageError(f"Invalid vote ID {vote_id}") from exc

    keywords = set(vote.keywords or ())
    keywords.add(keyword)

    fragment = Fragment(
        model=Vote.__name__,
        source_id=vote_id,
        source_name=make_cli_fragment_source("keywords"),
        source_url=None,
        group_key=vote_id,
        data={
            "keywords": sorted(keywords),
        },
    )

    upsert_fragments([fragment])

    aggregator = Aggregator(Vote)
    mapped_records = aggregator.mapped_records(map_vote, [str(vote_id)])
    index_records(Vote, mapped_records)


@keywords.command("remove")
@click.argument("vote_id", type=int)
@click.argument("keyword")
def remove_keyword(vote_id: int, keyword: str) -> None:
    try:
        vote = Session.execute(select(Vote).where(Vote.id == vote_id)).scalar_one()
    except NoResultFound as exc:
        raise click.UsageError(f"Invalid vote ID {vote_id}") from exc

    keywords = set(vote.keywords or ())
    keywords.remove(keyword)

    fragment = Fragment(
        model=Vote.__name__,
        source_id=vote_id,
        source_name=make_cli_fragment_source("keywords"),
        source_url=None,
        group_key=vote_id,
        data={
            "keywords": sorted(keywords),
        },
    )

    upsert_fragments([fragment])

    aggregator = Aggregator(Vote)
    mapped_records = aggregator.mapped_records(map_vote, [str(vote_id)])
    index_records(Vote, mapped_records)


@keywords.command("list")
@click.argument("vote_id", type=int)
def list_keywords(vote_id: int) -> None:
    try:
        vote = Session.execute(select(Vote).where(Vote.id == vote_id)).scalar_one()
    except NoResultFound as exc:
        raise click.UsageError(f"Invalid vote ID {vote_id}") from exc

    for keyword in vote.keywords:
        click.echo(keyword)
