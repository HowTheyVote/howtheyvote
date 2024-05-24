import base64
from urllib.parse import urljoin

from structlog import get_logger

from .. import config
from .cdp import Client

log = get_logger(__name__)


def generate_vote_sharepic(vote_id: int) -> bytes:
    """Generate a share picture for the given vote."""
    url = urljoin(config.FRONTEND_PRIVATE_URL, f"/votes/{vote_id}/sharepic")
    return capture_screenshot(url)


def capture_screenshot(url: str) -> bytes:
    """Uses a headless Chromium browser to take a screenshot of the given `url`
    and writes the resulting PNG file to `path`."""
    log.info("Capturing screenshot", url=url)

    client = Client(host="chromium", port=9222, timeout=5)

    with client.connect() as session:
        session.send(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": 600,
                "height": 315,
                "deviceScaleFactor": 2,
                "mobile": False,
            },
        )
        session.send("Page.enable")
        session.send("Page.navigate", {"url": url, "format": "png"})
        session.wait_event("Page.loadEventFired")
        res = session.send("Page.captureScreenshot")

        return base64.b64decode(res["data"])
