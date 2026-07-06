import ssl
from typing import Any, cast

import requests
import sentry_sdk
from structlog import get_logger

from . import config
from .cdp import Client

log = get_logger(__name__)

# Firefox 147 cipher suite
# See: https://github.com/lexiforest/curl-impersonate/blob/main/patches/curl.patch
FIREFOX_CIPHERS = ":".join(
    [
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
    ]
)

# Firefox 147 default request headers
# See: https://github.com/lexiforest/curl-impersonate/blob/main/patches/curl.patch
FIREFOX_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:147.0) Gecko/20100101 Firefox/147.0",  # noqa: E501
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
    "Te": "trailers",
}


class WAFTokenError(Exception):
    pass


class BrowserTLSAdapter(requests.adapters.HTTPAdapter):
    """A custom requests HTTP adapter automatically injects a custom TLS context to be
    used for all connections."""

    def __init__(self, ssl_context: ssl.SSLContext, **kwargs: Any) -> None:
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args: Any, **kwargs: Any) -> None:
        kwargs["ssl_context"] = self.ssl_context
        super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, proxy: str, **proxy_kwargs: Any) -> Any:
        proxy_kwargs["ssl_context"] = self.ssl_context
        return super().proxy_manager_for(proxy, **proxy_kwargs)


def get_session(aws_waf_token: str | None = None) -> requests.Session:
    """Returns a requests session object that mimics the TLS configuration of recent
    Firefox versions to prevent detection using TLS fingerprinting techniques such as
    JA3/JA4. If `aws_waf_token` is provided, all requests made using the session object
    include the token as a cookie."""
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3
    ctx.set_ciphers(FIREFOX_CIPHERS)
    ctx.set_alpn_protocols(["h2", "http/1.1"])

    # Firefox does not send a session ticket by default in private mode
    ctx.options |= ssl.OP_NO_TICKET

    session = requests.Session()
    session.mount("https://", BrowserTLSAdapter(ctx))

    session.headers.update(FIREFOX_HEADERS)

    if aws_waf_token:
        session.cookies.set("aws-waf-token", aws_waf_token)

    return session


def solve_ep_aws_waf_challenge() -> str:
    # Requests to /doceo/* seem to always trigger the JS challenge (in contrast to
    # other pages such as the homepage).
    return solve_aws_waf_challenge(
        "https://www.europarl.europa.eu/doceo/document/A-10-2026-0011_EN.html"
    )


def solve_eurlex_aws_waf_challenge() -> str:
    return solve_aws_waf_challenge("https://eur-lex.europa.eu/homepage.html?locale=en")


def solve_aws_waf_challenge(url: str) -> str:
    """Requests the given URL using headless Chromium, waits until the automatic JS challenge
    is completed, and returns the AWS WAF token."""
    client = Client(
        host=config.CHROMIUM_HOST,
        port=config.CHROMIUM_PORT,
        timeout=10,
    )

    with client.connect() as session:
        session.send(
            "Emulation.setDeviceMetricsOverride",
            {
                # MacBook Air 13 screen resolution
                "width": 1560,
                "height": 1644,
                "deviceScaleFactor": 2,
                "mobile": False,
            },
        )

        session.send("Page.enable")

        # Navigate to the URL that triggers the JS challenge. This emits a first navigation
        # challenge. Once the JS challenge has been solved, a redirect happens and the token
        # cookie gets set. This emits a second navigation event.
        with (
            session.expect_event("Page.frameNavigated") as wait_1,
            session.expect_event("Page.frameNavigated") as wait_2,
        ):
            session.send("Page.navigate", {"url": url})
            wait_1()
            wait_2()

        response = session.send("Network.getCookies")

    for cookie in response["cookies"]:
        if cookie["name"] == "aws-waf-token":
            log.info(
                "Obtained AWS WAF token",
                aws_waf_token=cookie["value"],
                domain=cookie["domain"],
            )
            sentry_sdk.metrics.count(
                "waf_challenges",
                1,
                attributes={
                    "status": "success",
                    "url": url,
                },
            )
            return cast(str, cookie["value"])

    sentry_sdk.metrics.count(
        "waf_challenges",
        1,
        attributes={
            "status": "failure",
            "url": url,
        },
    )
    raise WAFTokenError("Failed to obtain an AWS WAF token.")
