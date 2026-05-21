import html
import ssl
import time
from abc import ABC, abstractmethod
from typing import Any

import requests
from bs4 import BeautifulSoup
from cachetools import Cache
from requests import RequestException, Response
from requests.adapters import HTTPAdapter
from structlog import get_logger

from .. import config
from ..models import BaseWithId, Fragment

log = get_logger(__name__)


class ScrapingError(Exception):
    pass


class NoWorkingUrlError(ScrapingError):
    pass


RequestCache = Cache[str, Response | None]


class BrowserTLSAdapter(HTTPAdapter):
    def __init__(self, ssl_context, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        proxy_kwargs["ssl_context"] = self.ssl_context
        return super().proxy_manager_for(proxy, **proxy_kwargs)


# Firefox 147 cipher suite
# See: https://github.com/lexiforest/curl-impersonate/blob/main/patches/curl.patch
FIREFOX_CIPHERS = ":".join([
    "TLS_AES_128_GCM_SHA256",
    "TLS_CHACHA20_POLY1305_SHA256",
    "TLS_AES_256_GCM_SHA384",
    "ECDHE-ECDSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-CHACHA20-POLY1305",
    "ECDHE-RSA-CHACHA20-POLY1305",
    "ECDHE-ECDSA-AES256-GCM-SHA384",
    "ECDHE-RSA-AES256-GCM-SHA384",
    "ECDHE-ECDSA-AES256-SHA",
    "ECDHE-RSA-AES256-SHA",
    "ECDHE-ECDSA-AES128-SHA",
    "ECDHE-RSA-AES128-SHA",
    "AES128-GCM-SHA256",
    "AES256-GCM-SHA384",
    "AES256-SHA",
    "AES128-SHA",
])

# Firefox 147 default request headers
# See: https://github.com/lexiforest/curl-impersonate/blob/main/patches/curl.patch
FIREFOX_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:147.0) Gecko/20100101 Firefox/147.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
    "Te": "trailers"
}


def get_url(
    url: str,
    headers: dict[str, str],
    request_cache: RequestCache | None = None,
    aws_waf_token: str | None = None,
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
            ctx = ssl.create_default_context()
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            ctx.maximum_version = ssl.TLSVersion.TLSv1_3
            ctx.set_ciphers(FIREFOX_CIPHERS)

            # Firefox does not send a session ticket by default in private mode
            ctx.options |= ssl.OP_NO_TICKET
            
            ctx.set_alpn_protocols(["h2", "http/1.1"])

            session = requests.Session()
            session.mount("https://", BrowserTLSAdapter(ctx))

            cookies = {"aws-waf-token": aws_waf_token} if aws_waf_token else None
            response = session.get(
                url,
                headers={
                    **FIREFOX_HEADERS,
                    **headers,
                },
                timeout=timeout,
                cookies=cookies,
            )

            # Very basic request throttling with exponential backoff for retries
            time.sleep(config.REQUEST_SLEEP * (2**retry))

            if not response.ok:
                log.warning(
                    "URL request failed",
                    url=url,
                    retry=retry,
                    max_retries=max_retries,
                    status=response.status_code,
                    took=response.elapsed.total_seconds(),
                )
                # Retry in case it's just a temporary issue
                continue

            if response.headers.get("x-amzn-waf-action") == "challenge":
                log.error(
                    "Encountered AWS WAF JavaScript challenge",
                    url=url,
                    retry=retry,
                    max_retries=max_retries,
                    status=response.status_code,
                    took=response.elapsed.total_seconds(),
                    aws_waf_token=aws_waf_token,
                )
                # Do not retry, we would just get the same challenge again
                return None

            log.info(
                "URL request succeeded",
                url=url,
                retry=retry,
                max_retries=max_retries,
                status=response.status_code,
                took=response.elapsed.total_seconds(),
            )
            break
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

    def __init__(
        self,
        request_cache: RequestCache | None = None,
        aws_waf_token: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._request_cache = request_cache
        self._aws_waf_token = aws_waf_token
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
            self._log.info("Loading source", url=url)
            response = get_url(
                url=url,
                headers=headers,
                request_cache=self._request_cache,
                aws_waf_token=self._aws_waf_token,
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
