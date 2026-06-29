from concurrent.futures import ThreadPoolExecutor
from typing import cast

from structlog import get_logger

from . import config
from .cdp import Client

log = get_logger(__name__)


class WAFTokenError(Exception):
    pass


def solve_ep_aws_waf_challenge() -> str:
    # Requests to /doceo/* seem to always trigger the JS challenge (in contrast to
    # other pages such as the homepage).
    return solve_aws_waf_challenge(
        "https://www.europarl.europa.eu/doceo/document/A-10-2026-0011_EN.html"
    )


def solve_eurlex_aws_waf_challenge() -> str:
    return solve_aws_waf_challenge("https://eur-lex.europa.eu/homepage.html?locale=en")


def solve_aws_waf_challenge(url: str) -> str:
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

        with ThreadPoolExecutor() as executor:
            # After the JS challenge has been solved, a cookie is set and a navigation to
            # the originally requested URL occurs.
            executor.submit(session.wait_event, "Page.frameNavigated")
            # Only navigate after waiting for the navigation event. Otherwise the navigation
            # event might occur before we wait for it.
            executor.submit(session.send, "Page.navigate", {"url": url})

        response = session.send("Network.getCookies")

    for cookie in response["cookies"]:
        if cookie["name"] == "aws-waf-token":
            log.info(
                "Obtained AWS WAF token",
                aws_waf_token=cookie["value"],
                domain=cookie["domain"],
            )
            return cast(str, cookie["value"])

    raise WAFTokenError("Failed to obtain an AWS WAF token.")
