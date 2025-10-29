import logging
import sys
from collections.abc import MutableMapping
from typing import Any

import sentry_sdk
import structlog
from sentry_sdk import logger as sentry_logger

from . import config

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)


# The Sentry Python SDK currently doesn’t support structlog yet.
# This is a custom structlog processor that forwards log messages to Sentry based on
# https://www.structlog.org/en/stable/processors.html#examples.
def sentry_processor(
    logger: Any,
    log_method: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    # I don’t think there currently is a way to do this without relying on private
    # methods from the Sentry SDK, but hopefully structlog will be supported soon:
    # https://github.com/getsentry/sentry-python/issues/4417
    _event_dict = structlog.stdlib.add_log_level_number(
        logger,
        log_method,
        dict(event_dict),  # Copy dict to ensure original isn’t mutated
    )
    level = _event_dict.pop("level_number")
    event = _event_dict.pop("event")

    severity_number, severity_text = sentry_logger._log_level_to_otel(
        level,
        sentry_sdk.integrations.logging.SEVERITY_TO_OTEL_SEVERITY,
    )

    sentry_logger._capture_log(severity_text, severity_number, event, attributes=_event_dict)

    # Return original event dict for the next processor
    return event_dict


structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        # The Sentry processor needs to be inserted in the chain before the final
        # renderer processor (otherwise the structured log arguments are lost).
        sentry_processor,
        structlog.dev.ConsoleRenderer()
        if config.ENV == "test" or config.ENV == "local"
        else structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)
