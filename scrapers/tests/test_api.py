import pytest
from flask import Flask
from ep_votes.api import params, json_response
from datetime import date


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def handler():
    def handler(date: date):
        return date

    return handler


def test_params(app, handler):
    with app.test_request_context(query_string="date=2021-01-01"):
        decorated_handler = params(date=date.fromisoformat)(handler)

        assert decorated_handler() == date(2021, 1, 1)


def test_params_missing(app, handler):
    with app.test_request_context():
        decorated_handler = params(date=date.fromisoformat)(handler)
        expected = {"message": "Missing required parameters: date"}, 400

        assert decorated_handler() == expected


def test_json_response():
    handler = lambda: {"message": "ok"}  # noqa: E731
    decorated_handler = json_response(handler)
    response = decorated_handler()

    assert response.status_code == 200
    assert response.data == b'{"message": "ok"}'


def test_json_response_status():
    handler = lambda: ({"message": "error"}, 500)  # noqa: E731
    decorated_handler = json_response(handler)
    response = decorated_handler()

    assert response.status_code == 500
    assert response.data == b'{"message": "error"}'
