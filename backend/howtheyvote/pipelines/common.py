import hashlib
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import sentry_sdk
from prometheus_client import Counter
from requests import Response
from structlog import get_logger

from ..files import ensure_parent, vote_sharepic_path
from ..models import PipelineStatus, Vote
from ..pushover import send_notification
from ..scrapers import ScrapingError
from ..sharepics import generate_vote_sharepic

log = get_logger(__name__)

SHAREPICS_GENERATED = Counter(
    "htv_sharepics_generated_total",
    "Total number of generated sharepics",
    ["status"],
)


@dataclass
class PipelineResult:
    status: PipelineStatus
    checksum: str | None
    exception: Exception | None = None


class DataUnavailable(Exception):  # noqa: N818
    pass


class DataUnchanged(Exception):  # noqa: N818
    pass


class BasePipeline(ABC):
    last_run_checksum: str | None
    checksum: str | None

    def __init__(self, last_run_checksum: str | None = None, **kwargs: Any) -> None:
        self.last_run_checksum = last_run_checksum
        self.checksum = None
        self._log = log.bind(pipeline=type(self).__name__, **kwargs)

    def run(self) -> PipelineResult:
        self._log.info("Running pipeline")
        exception = None

        try:
            self._run()
            status = PipelineStatus.SUCCESS
        except DataUnavailable:
            status = PipelineStatus.DATA_UNAVAILABLE
        except DataUnchanged:
            status = PipelineStatus.DATA_UNCHANGED
        except ScrapingError as exc:
            exception = exc
            status = PipelineStatus.FAILURE
            self._log.exception("Failed running pipeline")

        return PipelineResult(
            status=status,
            checksum=self.checksum,
            exception=exception,
        )

    @abstractmethod
    def _run(self) -> None:
        raise NotImplementedError


def compute_response_checksum(response: Response) -> str:
    """Compute the SHA256 hash of the response contents."""
    return hashlib.sha256(response.content).hexdigest()


def generate_vote_sharepics(votes: Iterable[Vote]) -> None:
    failure_count = 0
    success_count = 0

    for vote in votes:
        log.info("Generating vote sharepic.", vote_id=vote.id)

        try:
            image = generate_vote_sharepic(vote.id)
            path = vote_sharepic_path(vote.id)
            ensure_parent(path)
            path.write_bytes(image)
            SHAREPICS_GENERATED.labels(status="success").inc()
            success_count += 1
        except Exception as err:
            log.exception("Failed generating vote sharepic.", vote_id=vote.id)
            sentry_sdk.capture_exception(err)
            SHAREPICS_GENERATED.labels(status="error").inc()
            failure_count += 1

    if failure_count > 0:
        send_notification(
            title="Failed generating sharepics",
            message=f"{failure_count} failures (out of {success_count + failure_count})",
        )
