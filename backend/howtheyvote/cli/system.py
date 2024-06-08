import click

from ..db import migrate as _migrate
from ..meili import configure_indexes as _configure_indexes
from ..meili import delete_indexes as _delete_indexes


@click.group()
def system() -> None:
    """Initialize or migrate the database and/or search index."""
    pass


@system.command()
def configure_indexes() -> None:
    """Configure Meilisearch indexes."""
    _configure_indexes()


@system.command()
def delete_indexes() -> None:
    """Delete Meilisearch indexes."""
    _delete_indexes()


@system.command()
def migrate() -> None:
    """Run database migrations."""
    _migrate()


@system.command()
def upgrade() -> None:
    """Equivalent of running the `migrate` and `configure-indexes` subcommands."""
    _configure_indexes()
    _migrate()
