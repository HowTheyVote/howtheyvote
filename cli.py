import click
import json
from dataclasses import is_dataclass, asdict
from typing import Any
from datetime import date
from enum import Enum
from ep_votes.scrapers import (
    MembersScraper,
    MemberInfoScraper,
    MemberGroupsScraper,
    VoteResultsScraper,
)

date_type = click.DateTime(formats=["%Y-%m-%d"])


class EPVotesEncoder(json.JSONEncoder):
    DATE_FORMAT = "%Y-%m-%d"

    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime(self.DATE_FORMAT)

        if isinstance(obj, set):
            return list(obj)

        if isinstance(obj, Enum):
            return obj.name

        if is_dataclass(obj):
            return asdict(obj)

        return super(EPVotesEncoder, self).default(obj)


def to_json(data: Any, indent=None):
    return json.dumps(data, cls=EPVotesEncoder, indent=2)


@click.group()
def cli():
    pass


@click.command()
@click.option("--term", type=int, required=True, help="Parliamentary term")
def members(term: int) -> None:
    scraper = MembersScraper(term=term)
    members = scraper.run()

    click.echo(to_json(members))


@click.command()
@click.option("--web-id", type=int, required=True, help="Member’s ID on the EP website")
def member_info(web_id: int) -> None:
    scraper = MemberInfoScraper(web_id=web_id)
    member = scraper.run()

    click.echo(to_json(member))


@click.command()
@click.option("--web-id", type=int, required=True, help="Member’s ID on the EP website")
@click.option("--term", type=int, required=True, help="Parliamentary term")
def member_groups(web_id: int, term: int) -> None:
    scraper = MemberGroupsScraper(web_id=web_id, term=term)
    groups = scraper.run()

    click.echo(to_json(groups))


@click.command()
@click.option("--term", type=int, required=True, help="Parliamentary term")
@click.option(
    "--date", type=date_type, required=True, help="Date of parliamentary sessions"
)
def vote_results(term: int, date: click.DateTime) -> None:
    scraper = VoteResultsScraper(date=date, term=term)
    votes = scraper.run()

    click.echo(to_json(votes))


cli.add_command(members)
cli.add_command(member_info)
cli.add_command(member_groups)
cli.add_command(vote_results)


if __name__ == "__main__":
    cli()
