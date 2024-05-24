import requests
from cachetools import LRUCache

from howtheyvote.scrapers.common import get_url


def test_get_url(responses):
    mock = responses.get("https://example.org", body="Hello World")

    response = get_url("https://example.org", headers={})
    assert response and response.status_code == 200
    assert mock.call_count == 1

    response = get_url("https://example.org", headers={})
    assert response and response.status_code == 200
    assert mock.call_count == 2


def test_get_url_timeout(responses):
    responses.get("https://example.org", body=requests.RequestException())

    response = get_url("https://example.org", headers={})
    assert response is None


def test_get_url_cache(responses):
    mock = responses.get("https://example.org", body="Hello World")
    cache = LRUCache(maxsize=10)

    response = get_url("https://example.org", headers={}, request_cache=cache)
    assert response and response.status_code == 200
    assert mock.call_count == 1

    response = get_url("https://example.org", headers={}, request_cache=cache)
    assert response and response.status_code == 200
    assert mock.call_count == 1


def test_get_url_retries(responses):
    error = responses.get("https://example.org", body="Internal Server Error", status=500)
    success = responses.get("https://example.org", body="Hello World")

    response = get_url("https://example.org", headers={}, max_retries=1)
    assert response and response.status_code == 200
    assert error.call_count == 1
    assert success.call_count == 1
