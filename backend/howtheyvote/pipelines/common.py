from abc import ABC, abstractmethod
from typing import Any

from structlog import get_logger

from ..scrapers import ScrapingError

log = get_logger(__name__)


class PipelineError(Exception):
    pass


class DataUnavailableError(PipelineError):
    pass


class DataUnchangedError(PipelineError):
    pass


class BasePipeline(ABC):
    last_run_checksum: str | None
    checksum: str | None

    def __init__(self, last_run_checksum: str | None = None, **kwargs: Any) -> None:
        self.last_run_checksum = last_run_checksum
        self.checksum = None
        self._log = log.bind(pipeline=type(self).__name__, **kwargs)

    def run(self) -> None:
        self._log.info("Running pipeline")

        try:
            self._run()
        except ScrapingError:
            self._log.exception("Failed running pipeline")

    @abstractmethod
    def _run(self) -> None:
        raise NotImplementedError
