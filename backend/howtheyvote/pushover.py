import requests
from structlog import get_logger

from . import config

API_URL = "https://api.pushover.net/1/messages.json"
log = get_logger(__name__)


def send_notification(message: str, title: str | None = None, url: str | None = None) -> None:
    if not config.PUSHOVER_API_TOKEN or not config.PUSHOVER_USER_KEY:
        log.warn(
            "Pushover API token or user key not configured. No push notification will be sent."
        )
        return

    # Pushover limits the size of titles and messages, but apparently automatically truncates
    # strings longer than that, so we don’t need to handle that on our side:
    # https://jcs.org/2023/07/12/api

    try:
        response = requests.post(
            API_URL,
            data={
                "token": config.PUSHOVER_API_TOKEN,
                "user": config.PUSHOVER_USER_KEY,
                "title": title,
                "message": message,
                "url": url,
            },
        )
        response.raise_for_status()
    except requests.RequestException:
        # Sending push notifications isn't critical, so we don't want request exceptions
        # to bubble up, logging them is enough.
        log.exception(
            "Failed to send push notification",
            message=message,
            title=title,
            url=url,
        )
