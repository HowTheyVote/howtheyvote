import requests
from responses import matchers

from howtheyvote.pushover import send_notification


def test_send_notification(responses, mocker):
    mocker.patch("howtheyvote.config.PUSHOVER_API_TOKEN", "api-token-123")
    mocker.patch("howtheyvote.config.PUSHOVER_USER_KEY", "user-key-123")

    res = responses.post(
        url="https://api.pushover.net/1/messages.json",
        match=[
            matchers.urlencoded_params_matcher(
                {
                    "token": "api-token-123",
                    "user": "user-key-123",
                    "title": "Title",
                    "message": "Message",
                    "url": "https://howtheyvote.eu",
                }
            )
        ],
        body="1",
    )

    send_notification(
        title="Title",
        message="Message",
        url="https://howtheyvote.eu",
    )

    assert res.call_count == 1


def test_send_notification_connection_error(responses, mocker, logs):
    mocker.patch("howtheyvote.config.PUSHOVER_API_TOKEN", "api-token-123")
    mocker.patch("howtheyvote.config.PUSHOVER_USER_KEY", "user-key-123")

    responses.post(
        url="https://api.pushover.net/1/messages.json",
        body=requests.ConnectionError("Could not connect to api.pushover.net"),
    )

    send_notification(
        title="Title",
        message="Message",
        url="https://howtheyvote.eu",
    )

    assert len(logs) == 1
    assert logs[0]["event"] == "Failed to send push notification"
    assert logs[0]["log_level"] == "error"
    assert logs[0]["title"] == "Title"
    assert logs[0]["message"] == "Message"
    assert logs[0]["url"] == "https://howtheyvote.eu"


def test_send_notification_no_api_creds(logs):
    send_notification(message="Lorem ipsum")
    assert len(logs) == 1
    assert (
        logs[0]["event"]
        == "Pushover API token or user key not configured. No push notification will be sent."
    )
