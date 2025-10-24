import re
from collections import defaultdict

import click

from ..models import Vote
from ..search import get_index, prefix_to_field


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
