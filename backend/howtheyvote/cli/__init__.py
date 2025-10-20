import pathlib
import shutil
import tempfile

import click

from ..db import Session
from ..export import generate_export
from ..files import file_path
from ..sharepics import generate_vote_sharepic
from ..worker import worker as worker_
from .aggregate import aggregate
from .dev import dev
from .flush import flush
from .pipeline import pipeline
from .search import search
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
    archive_path = file_path("export/export")
    generate_export(archive_path)


cli.add_command(system)
cli.add_command(aggregate)
cli.add_command(pipeline)
cli.add_command(dev)
cli.add_command(temp)
cli.add_command(flush)
cli.add_command(search)
