import click
from functools import wraps
from ep_votes.helpers import to_json
from ep_votes.scrapers import (
    MembersScraper,
    MemberInfoScraper,
    MemberGroupsScraper,
    VoteResultsScraper,
    DocumentScraper,
)

date_type = click.DateTime(formats=["%Y-%m-%d"])


def json(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        res = handler(*args, **kwargs)
        click.echo(to_json(res))

    return wrapper


@click.group()
def cli():
    pass


@click.command()
@click.option("--term", type=int, required=True, help="Parliamentary term")
@json
def members(term: int):
    return MembersScraper(term=term).run()


@click.command()
@click.option("--web-id", type=int, required=True, help="Member’s ID on the EP website")
@json
def member_info(web_id: int):
    return MemberInfoScraper(web_id=web_id).run()


@click.command()
@click.option("--web-id", type=int, required=True, help="Member’s ID on the EP website")
@click.option("--term", type=int, required=True, help="Parliamentary term")
@json
def member_groups(web_id: int, term: int):
    return MemberGroupsScraper(web_id=web_id, term=term).run()


@click.command()
@click.option("--term", type=int, required=True, help="Parliamentary term")
@click.option(
    "--date", type=date_type, required=True, help="Date of parliamentary sessions"
)
@json
def vote_results(term: int, date: click.DateTime):
    return VoteResultsScraper(date=date, term=term).run()


@click.command()
@click.option("--reference", type=str, required=True, help="Reference of the document")
@json
def document(reference: str):
    return DocumentScraper(reference=reference).run()


cli.add_command(members)
cli.add_command(member_info)
cli.add_command(member_groups)
cli.add_command(vote_results)
cli.add_command(document)


if __name__ == "__main__":
    cli()
