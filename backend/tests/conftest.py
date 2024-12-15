"""The database configuration relies on module globals and as such is a bit fragile, but
it works and hopefully doesn't need to be adjusted too often. We use the pytest-env plugin
to set the `HTV_BACKEND_DATABASE_URI` environment variables to a separate SQLite file when
running tests and use pytest hooks to start a transaction before individual tests are
executed and rollback any changes after execution. In order to test API routes, we make use
of Flask’s built-in test client."""

import os

import pytest
from responses import FirstMatchRegistry, RequestsMock

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


class DummyRegistry(FirstMatchRegistry):
    """A registry that ignores any requests that are added."""

    def add(self, response):
        return response


@pytest.fixture
def responses(request):
    """Allows mocking HTTP requests made with `requests`. Request mocking can be
    disabled globally using the `HTV_TEST_MOCK_REQUESTS=false` env variable to
    run tests against the live sources rather than test fixtures. Individual tests
    can be marked using `always_mock_requests` to mock them even if requests mocks
    are disabled globally. However, it’s preferred to write tests that can be run
    against the live data sources."""

    mock_requests = os.environ.get("HTV_TEST_MOCK_REQUESTS", "true").lower() in ["true", "1"]
    marks = [m.name for m in request.node.iter_markers()]
    always_mock_requests = "always_mock_requests" in marks

    if always_mock_requests or mock_requests:
        with RequestsMock() as r:
            # Yield a "normal" requests mock that fails any request that isn’t explicitly mocked.
            yield r
        return

    # When calling `responses.get("http://...", body="Lorem ipsum")` in a test to register
    # a mock response, the mock is stored in a registry. When the tested then tries to send
    # a matching request, `responses` tries to find a matching mock in the registry. To
    # disable all mocks, we simply pass a dummy registry that never actually registers any
    # mocks and allow all unmatched requests to pass to the original source.
    with RequestsMock(registry=DummyRegistry) as r:
        r.add_passthru("http")
        yield r
