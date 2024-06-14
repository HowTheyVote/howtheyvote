import click

from ..db import Session
from ..export import Export
from ..files import file_path
from ..sharepics import generate_vote_sharepic
from ..worker import worker as worker_
from .aggregate import aggregate
from .dev import dev
from .pipeline import pipeline
from .system import system
from .temp import temp


@click.group()
def cli() -> None:
    pass


@cli.command()
def worker() -> None:
    """Start a worker process to execute scheduled pipeline runs."""
    worker_.run()


@cli.command()
def export() -> None:
    """Generate a CSV data export."""
    export = Export(outdir=file_path("export"))
    export.run()


cli.add_command(system)
cli.add_command(aggregate)
cli.add_command(pipeline)
cli.add_command(dev)
cli.add_command(temp)
