import pathlib
import shutil
import tempfile

import click
from click_aliases import ClickAliasedGroup

from ..db import Session
from ..export import generate_export
from ..files import file_path
from ..sharepics import generate_vote_sharepic
from ..worker import worker as worker_
from .aggregate import aggregate
from .dev import dev
from .flush import flush
from .pipeline import pipeline
from .system import system
from .temp import temp


@click.group(cls=ClickAliasedGroup)
def cli() -> None:
    pass


@cli.command()
def worker() -> None:
    """Start a worker process to execute scheduled pipeline runs."""
    worker_.run()


@cli.command()
def export() -> None:
    """Generate a CSV data export."""
    archive_path = file_path("export/export")
    generate_export(archive_path)


cli.add_command(system, aliases=["sys"])
cli.add_command(aggregate, aliases=["agg"])
cli.add_command(pipeline, aliases=["pipe"])
cli.add_command(dev)
cli.add_command(temp)
cli.add_command(flush)
