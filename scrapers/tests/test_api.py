import pytest
from flask import Flask
from ep_votes.api import params, json_response, to_json
from ep_votes.models import Country, Voting, Position
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


def test_to_json_date():
    data = {"date": date(2021, 1, 1)}
    assert to_json(data) == '{"date": "2021-01-01"}'


def test_to_json_set():
    data = {"set": set([1, 2, 3])}
    assert to_json(data) == '{"set": [1, 2, 3]}'


def test_to_json_enum():
    data = {"enum": Country.DE}
    assert to_json(data) == '{"enum": "DE"}'


def test_to_json_voting():
    data = {"voting": Voting(doceo_member_id=1, name="Name", position=Position.FOR)}
    assert to_json(data) == '{"voting": ["Name", "FOR"]}'
