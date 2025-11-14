import click

from ..db import migrate as _migrate
from ..db import optimize as _optimize
from ..search import delete_indexes as _delete_indexes


@click.group()
def system() -> None:
    """Initialize or migrate the database and/or search index."""
    pass


@system.command()
def delete_indexes() -> None:
    """Delete search indexes."""
    _delete_indexes()


@system.command()
def migrate() -> None:
    """Run database migrations."""
    _migrate()


@system.command()
def upgrade() -> None:
    """Equivalent of running the `migrate` and `configure-indexes` subcommands."""
    _migrate()


@system.command()
def optimize() -> None:
    """Merge the SQLite WAL and vacuum."""
    _optimize()
