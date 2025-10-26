import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from requests import Response
from structlog import get_logger

from ..models import PipelineStatus
from ..scrapers import ScrapingError

log = get_logger(__name__)


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
