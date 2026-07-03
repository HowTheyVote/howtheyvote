import json
import socket
import threading
from collections import defaultdict
from collections.abc import Callable, Generator
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FutureTimeoutError
from contextlib import AbstractContextManager, contextmanager
from typing import Any, TypedDict, cast

import requests
from typing_extensions import TypeIs
from websocket import WebSocket, WebSocketTimeoutException


class BrowserError(Exception):
    def __init__(self, message: str, error: dict[Any, Any] | None = None):
        super().__init__(message)
        self.error = error


class TimeoutError(Exception):
    pass


class SuccessResultMessage(TypedDict):
    id: int
    result: dict[str, Any]


class ErrorResultMessage(TypedDict):
    id: int
    error: dict[str, Any]


class EventMessage(TypedDict):
    method: str
    params: dict[str, Any]


ResultMessage = SuccessResultMessage | ErrorResultMessage
Message = ResultMessage | EventMessage


# Needed for type narrowing
def is_result_message(message: Message) -> TypeIs[ResultMessage]:
    return "id" in message


def is_error_result(message: ResultMessage) -> TypeIs[ErrorResultMessage]:
    return "error" in message


type WaitFunc[T: Message] = Callable[[], T]


class Session:
    def __init__(self, ws_url: str, timeout: int):
        self._ws_url = ws_url
        self._ws = WebSocket()
        self._ws.settimeout(timeout)
        self._timeout = timeout
        self._message_counter = 0

        self._waiting_for_result: dict[int, list[Future[ResultMessage]]] = defaultdict(list)
        self._waiting_for_event: dict[str, list[Future[EventMessage]]] = defaultdict(list)
        self._waiting_lock = threading.Lock()

        # A background thread receiving incoming messages
        self._receive_thread: threading.Thread

        self._stop_event = threading.Event()

    @contextmanager
    def connect(self) -> Generator["Session", None, None]:
        self._ws.connect(self._ws_url, timeout=self._timeout)  # type: ignore
        self._receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._receive_thread.start()

        try:
            yield self
        finally:
            self._stop_event.set()
            self._receive_thread.join()
            self._ws.close()

    def _receive_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                message = cast(Message, json.loads(self._ws.recv()))
            except WebSocketTimeoutException:
                # We don’t need to do anything here, as the method waiting for the future
                # to be resolved in the main thread will timeout.
                continue

            if is_result_message(message):
                self._handle_result_message(message)
            else:
                self._handle_event_message(message)

    def _handle_result_message(self, message: ResultMessage) -> None:
        with self._waiting_lock:
            for future in self._waiting_for_result[message["id"]]:
                future.set_result(message)

    def _handle_event_message(self, message: EventMessage) -> None:
        with self._waiting_lock:
            for future in self._waiting_for_event[message["method"]]:
                if not future.done():
                    future.set_result(message)
                    # Only resolve the first registered future for the event. Events do
                    # not have unique IDs, and we need to be able to register multiple
                    # futures for multiple subsequent events of the same type (e.g.,
                    # subsequent navigation events due to redirects).
                    break

    @contextmanager
    def _wait_for[K: str | int, M: Message](
        self,
        key: K,
        waiting: dict[K, list[Future[M]]],
    ) -> Generator[WaitFunc[M], None, None]:
        # When waiting for a command result or an event, we store a future in `waiting`.
        # Whenever it receives a message, the background thread checks `waiting` for a future
        # matching the message ID or event name and resolves the future.
        future: Future[M] = Future()

        with self._waiting_lock:
            waiting[key].append(future)

        # Rather than blocking directly, we return a wait function that blocks when called.
        # This gives the caller more flexibility. For example, the caller can register the
        # future, then send a command that triggers the event, and only then start waiting.
        def wait() -> M:
            try:
                return future.result(self._timeout)
            except FutureTimeoutError as exc:
                raise TimeoutError() from exc

        try:
            yield wait
        finally:
            with self._waiting_lock:
                waiting[key].remove(future)

    def _wait_for_result(
        self,
        message_id: int,
    ) -> AbstractContextManager[WaitFunc[ResultMessage]]:
        return self._wait_for(message_id, self._waiting_for_result)

    def _wait_for_event(
        self,
        event: str,
    ) -> AbstractContextManager[WaitFunc[EventMessage]]:
        return self._wait_for(event, self._waiting_for_event)

    def send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a CDP command and wait for the result. The method blocks until the result
        has been received."""
        message_id = self.generate_message_id()

        with self._wait_for_result(message_id) as wait:
            payload = {
                "id": message_id,
                "method": method,
                "params": params,
            }
            self._ws.send(json.dumps(payload))
            message = wait()

        if is_error_result(message):
            raise BrowserError("Received error response", message["error"])

        return message["result"]

    def expect_event(self, event: str) -> AbstractContextManager[WaitFunc[EventMessage]]:
        """Wait for an event. Returns a context manager that yields a wait function. Calling
        the wait function blocks until the event has been received. It is important to enter
        the context manager before sending the command that triggers the event. Otherwise the
        event could be received (and discarded) before waiting for it."""
        return self._wait_for_event(event)

    def generate_message_id(self) -> int:
        message_id = self._message_counter
        self._message_counter += 1
        return message_id


class Client:
    # This is a pretty naive, synchroneous implementation of the Chrome DevTools Protocol
    # (CDP), but it might be good enough for our limited use case and avoids pulling in a
    # big dependency such as Playwright. This class is only used to open a new tab and
    # establish a Websockets connection for the CDP protocol. The `Session` class is
    # responsible for sending/receiving CDP messages via the Websockets connection."""

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
        """Open a new browser tab and enstablish a CDP Websockets connection."""
        tab_id = self._open_tab()

        try:
            with Session(
                ws_url=self._ws_url(tab_id),
                timeout=self._timeout,
            ).connect() as session:
                yield session
        finally:
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
