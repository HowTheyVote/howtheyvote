from typing import Any

from alembic import command as alembic_command
from alembic.config import Config
from sqlalchemy import create_engine, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import scoped_session, sessionmaker
from structlog import get_logger

from . import __path__, config
from .json import json_dumps, json_loads

log = get_logger(__name__)


engine = create_engine(
    config.DATABASE_URI,
    # We use a custom JSON serializer/deserializer to handle enums,
    # custom serialization of dataclasses (e.g. `Country`) etc.
    json_serializer=json_dumps,
    json_deserializer=json_loads,
)

session_factory = sessionmaker(engine)
Session = scoped_session(session_factory)


@event.listens_for(engine, "connect")
def on_connect(connection: DBAPIConnection, _: Any) -> None:
    cursor = connection.cursor()

    # Set up Write-Ahead Log to ensure that reads do not block writes and
    # writes do not block reads
    cursor.execute("PRAGMA journal_mode=WAL;")

    cursor.close()


def migrate() -> None:
    """Run Alembic database migrations."""
    with engine.connect() as connection:
        alembic_config = Config()
        root = list(__path__)[0]
        alembic_config.set_main_option("script_location", f"{root}/alembic")
        alembic_config.attributes["connection"] = connection
        log.info("Running database migrations.")
        alembic_command.upgrade(alembic_config, "head")
