"""The database configuration relies on module globals and as such is a bit fragile, but
it works and hopefully doesn't need to be adjusted too often. We use the pytest-env plugin
to set the `HTV_BACKEND_DATABASE_URI` environment variables to a separate SQLite file when
running tests and use pytest hooks to start a transaction before individual tests are
executed and rollback any changes after execution. In order to test API routes, we make use
of Flask’s built-in test client."""

import pytest
import responses as responses_lib

from howtheyvote.db import Session, engine, migrate, session_factory
from howtheyvote.meili import configure_indexes, delete_indexes
from howtheyvote.wsgi import app as flask_app


@pytest.fixture(scope="session")
def migrations():
    """Runs database migrations once before all tests."""
    migrate()
    yield None


@pytest.fixture()
def db_session(migrations):
    """Starts a transaction before individual tests are executed and rolls back all changes
    after execution."""
    connection = engine.connect()
    transaction = connection.begin()

    session_factory.configure(bind=connection)
    yield Session
    Session.remove()

    transaction.rollback()
    connection.close()


@pytest.fixture()
def search_index():
    """Deletes and recreates search indexes before the test runs."""
    delete_indexes()
    configure_indexes()
    yield


@pytest.fixture()
def app(db_session):
    """Providdes an instance of the Flask app."""
    yield flask_app


@pytest.fixture()
def api(app):
    """Provides a Flask test client that allows simulating HTTP requests."""
    yield app.test_client()


@pytest.fixture
def responses():
    """Allows mocking HTTP requests made with requests."""
    with responses_lib.RequestsMock() as r:
        yield r
