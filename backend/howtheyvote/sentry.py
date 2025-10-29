from typing import Literal

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry(component: Literal["backend", "worker"]) -> None:
    sentry_sdk.init(
        enable_logs=True,
        send_default_pii=False,
        traces_sample_rate=0,
        integrations=[
            # Prevent Sentry’s default logging integration from forwarding any logs, as we
            # configure our own structlog processor that forwards logs to Sentry.
            LoggingIntegration(
                event_level=None,
                level=None,
                sentry_logs_level=None,
            ),
        ],
    )
    sentry_sdk.set_tag("component", component)
