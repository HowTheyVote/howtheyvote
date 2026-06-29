import json
import socket
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, cast

import requests
from websocket import WebSocket, WebSocketTimeoutException


class BrowserError(Exception):
    def __init__(self, message: str, error: dict[Any, Any] | None = None):
        super().__init__(message)
        self.error = error


class TimeoutError(Exception):
    pass


class Timeout:
    def __init__(self, seconds: int | None):
        self.seconds = seconds
        self.start_time = time.time()

    def tick(self) -> None:
        """Check if the timeout has been reached and, if yes, raise an exception."""
        if self.seconds is None:
            return

        if time.time() >= self.start_time + self.seconds:
            raise TimeoutError()


class Session:
    def __init__(self, ws_url: str, timeout: int):
        self._ws_url = ws_url
        self._ws = WebSocket()
        self._ws.settimeout(timeout)
        self._timeout = timeout
        self._message_counter = 0

    def open(self) -> None:
        self._ws.connect(self._ws_url)  # type: ignore

    def close(self) -> None:
        self._ws.close()

    def send(self, method: str, params: dict[Any, Any] | None = None) -> dict[Any, Any]:
        message_id = self.generate_message_id()

        payload = {
            "id": message_id,
            "method": method,
            "params": params,
        }

        self._ws.send(json.dumps(payload))

        # Timeouts between messages (i.e. we didn’t receive a message for n seconds)
        # are handled by `websocket-client`, but we also need to handle cases were
        # we do receive a message at least every n seconds, but none of the messages
        # is the response to our outbound message.
        timeout = Timeout(self._timeout)

        while True:
            timeout.tick()
            data = self.receive()

            if data.get("id") != message_id:
                continue

            if "error" in data:
                raise BrowserError("Received error response", data["error"])

            result = cast(dict[Any, Any], data["result"])
            return result

    def wait_event(self, event: str) -> dict[Any, Any]:
        # Timeouts between messages (i.e. we didn’t receive a message for n seconds)
        # are handled by `websocket-client`, but we also need to handle cases were
        # we do receive a message at least every n seconds, but none of the messages
        # matches the given event.
        timeout = Timeout(self._timeout)

        while True:
            timeout.tick()
            data = self.receive()

            if data.get("method") == event:
                params = cast(dict[Any, Any], data["params"])
                return params

    def receive(self) -> dict[Any, Any]:
        """Wait for any new incoming message."""
        try:
            message = json.loads(self._ws.recv())
            return cast(dict[Any, Any], message)
        except WebSocketTimeoutException:
            raise TimeoutError() from None

    def generate_message_id(self) -> int:
        message_id = self._message_counter
        self._message_counter += 1
        return message_id


class Client:
    # This is a pretty naive, synchroneous implementation of the Chrome DevTools Protocol
    # (CDP), but it might be good enough for our limited use case and avoids pulling in a
    # big dependency such as Playwright."""

    DEFAULT_TIMEOUT = 30

    def __init__(self, host: str, port: int, timeout: int | None = None):
        # Chrome requires that the `Host` header is an IP address or `localhost`. However, in
        # most cases we want to connect using a Docker hostname, so we need to resolve the
        # hostname to the Docker IP address first.
        self._host = socket.gethostbyname(host)
        self._port = port
        self._timeout = timeout or self.DEFAULT_TIMEOUT

    @contextmanager
    def connect(self) -> Generator[Session, None, None]:
        tab_id = self._open_tab()
        session = Session(ws_url=self._ws_url(tab_id), timeout=self._timeout)
        session.open()

        try:
            yield session
        finally:
            session.close()
            self._close_tab(tab_id)

    def _open_tab(self) -> str:
        url = self._json_url("new")
        res = requests.put(url)
        data = res.json()

        if not res.ok:
            raise BrowserError("Couldn't open new tab")

        return cast(str, data["id"])

    def _close_tab(self, tab_id: str) -> None:
        url = self._json_url(f"close/{tab_id}")
        res = requests.get(url)

        if not res.ok:
            raise BrowserError("Couldn’t close tab")

    def _json_url(self, path: str) -> str:
        return f"http://{self._host}:{self._port}/json/{path}"

    def _ws_url(self, tab_id: str) -> str:
        return f"ws://{self._host}:{self._port}/devtools/page/{tab_id}"
