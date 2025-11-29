import html
import random
import time
from abc import ABC, abstractmethod
from typing import Any

import requests
from bs4 import BeautifulSoup
from cachetools import Cache
from requests import RequestException, Response
from structlog import get_logger

from .. import config
from ..models import BaseWithId, Fragment

log = get_logger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",  # noqa: E501
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15",  # noqa: E501
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",  # noqa: E501
]


class ScrapingError(Exception):
    pass


class NoWorkingUrlError(ScrapingError):
    pass


RequestCache = Cache[str, Response | None]


def get_url(
    url: str,
    headers: dict[str, str],
    request_cache: RequestCache | None = None,
    max_retries: int = 0,
    timeout: int = config.REQUEST_TIMEOUT,
) -> requests.Response | None:
    if isinstance(request_cache, Cache):
        if url in request_cache:
            log.info("Request cache hit", url=url)
            return request_cache[url]
        else:
            log.info("Request cache miss", url=url)

    response = None

    for retry in range(0, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)

            # Very basic request throttling with exponential backoff for retries
            time.sleep(config.REQUEST_SLEEP * (2**retry))

            if response.ok:
                log.info(
                    "URL request succeeded",
                    url=url,
                    retry=retry,
                    max_retries=max_retries,
                    status=response.status_code,
                    took=response.elapsed.total_seconds(),
                )
                break

            log.warning(
                "URL request failed",
                url=url,
                retry=retry,
                max_retries=max_retries,
                status=response.status_code,
                took=response.elapsed.total_seconds(),
            )
        except RequestException:
            log.warning(
                "URL request failed",
                url=url,
                retry=retry,
                max_retries=max_retries,
            )

    if isinstance(request_cache, Cache):
        log.info("Caching response", url=url)
        request_cache[url] = response

    return response


class BaseScraper[T](ABC):
    REQUEST_MAX_RETRIES: int = 0
    REQUEST_TIMEOUT: int = config.REQUEST_TIMEOUT

    def __init__(self, request_cache: RequestCache | None = None, **kwargs: Any) -> None:
        self._request_cache = request_cache
        self._log = log.bind(scraper=type(self).__name__, **kwargs)

    def run(self) -> Any:
        self._log.info("Running scraper")
        self.response = self._fetch()
        doc = self._parse(self.response)
        return self._extract_data(doc)

    @abstractmethod
    def _extract_data(self, doc: T) -> Any:
        raise NotImplementedError

    @abstractmethod
    def _url(self) -> str | list[str]:
        raise NotImplementedError

    @abstractmethod
    def _parse(self, response: Response) -> T:
        raise NotImplementedError

    def _fragment(
        self,
        model: type[BaseWithId],
        source_id: str | int,
        group_key: str | int,
        data: Any,
    ) -> Fragment:
        return Fragment(
            model=model.__name__,
            source_id=source_id,
            source_name=type(self).__name__,
            source_url=self.response.request.url,
            group_key=group_key,
            data=data,
        )

    def _fetch(self) -> Response:
        urls = self._url()
        headers = self._headers()

        if isinstance(urls, str):
            urls = [urls]

        for url in urls:
            self._log.info("Loading source", url=url, user_agent=headers["user-agent"])
            response = get_url(
                url=url,
                headers=headers,
                request_cache=self._request_cache,
                max_retries=self.REQUEST_MAX_RETRIES,
                timeout=self.REQUEST_TIMEOUT,
            )

            if not response or not response.ok:
                continue

            return response

        self._log.error("No working URL found.", urls=urls)
        raise NoWorkingUrlError("No working URL found.")

    def _headers(self) -> dict[str, str]:
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "en-us",
            "user-agent": random.choice(USER_AGENTS),
        }


class BeautifulSoupScraper(BaseScraper[BeautifulSoup]):
    BS_PARSER: str = "lxml"
    RESPONSE_ENCODING: str | None = None

    def _parse(self, response: Response) -> BeautifulSoup:
        # Some sources do not return the correct character encoding in the
        # HTTP headers which confuses request when trying to decode the
        # response. In those cases, we need to force the correct encoding.
        if self.RESPONSE_ENCODING:
            raw = response.content.decode(self.RESPONSE_ENCODING)
        else:
            raw = response.text

        # Handle HTML-encoded special-characters, as BeautifulSoup
        # seems to decode them to incorrect Unicode characters
        if self.BS_PARSER != "lxml-xml":
            raw = html.unescape(raw)

        return BeautifulSoup(raw, self.BS_PARSER)


class JSONScraper(BaseScraper[Any]):
    def _parse(self, response: Response) -> Any:
        return response.json()
