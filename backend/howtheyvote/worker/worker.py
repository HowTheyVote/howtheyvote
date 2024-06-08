import datetime
import enum
import signal
import time
from collections.abc import Callable, Iterable
from typing import Any

import prometheus_client
from prometheus_client import Counter, Gauge, Histogram
from prometheus_client import start_http_server as start_metrics_server
from schedule import Scheduler
from structlog import get_logger

from .. import config
from ..db import Session
from ..models import PipelineRun, PipelineRunResult
from ..pipelines import DataUnavailableError

log = get_logger(__name__)

prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

PIPELINE_RUN_DURATION = Histogram(
    "htv_worker_pipeline_run_duration_seconds",
    "Duration of pipeline runs executed by the worker",
    ["pipeline", "result"],
)

PIPELINE_RUNS = Counter(
    "htv_worker_pipeline_runs_total",
    "Total number of pipeline runs executed by the worker",
    ["pipeline", "result"],
)

PIPELINE_NEXT_RUN = Gauge(
    "htv_worker_pipeline_next_run_timestamp_seconds",
    "Timestamp of the next scheduled run of the pipeline",
    ["pipeline"],
)


class SkipPipelineError(Exception):
    pass


class Weekday(enum.Enum):
    SUN = "sunday"
    MON = "monday"
    TUE = "tuesday"
    WED = "wednesday"
    THU = "thursday"
    FRI = "friday"
    SAT = "saturday"


Handler = Callable[..., Any]


class Worker:
    """Running a worker starts a long-running process that executes data pipelines in regular
    intervals and stores the result of the pipeline runs in the database."""

    def __init__(self) -> None:
        self._scheduler = Scheduler()
        self._stopped = False
        self._scheduled: set[str] = set()

    def run(self) -> None:
        """Start an endless loop executing scheduled pipelines."""
        log.info("Starting worker")
        self._stopped = False

        # Expose Prometheus metrics
        start_metrics_server(config.WORKER_PROMETHEUS_PORT)
        log.info("Started Prometheus metrics server")

        signal.signal(signal.SIGTERM, self.stop)

        while not self._stopped:
            self.run_pending()
            time.sleep(1)
            self._update_next_run_metrics()

        self._stopped = False

    def stop(self, *_: Any) -> None:
        """Gracefully stop the worker. If a pipeline is currently being executes this will
        complete the pipeline run before stopping the worker."""
        log.info("Shutting down worker")

    def run_pending(self) -> None:
        """Run pending tasks but do not start an endless loop. This is useful in unit tests."""
        self._scheduler.run_pending()

    def schedule(
        self,
        handler: Handler,
        name: str,
        weekdays: Iterable[Weekday] = set(Weekday),
        hours: Iterable[int] = {0},
        minutes: Iterable[int] = {0},
        tz: str | None = None,
    ) -> None:
        """Schedule a pipeline to be executed at the given weekdays, hours, minutes.
        Optionally passing a timezone string via the `tz` parameter indicates that the
        pipeline should be executed at the given time in the respective timezone. For
        example, `schedule(my_handler, hours={6}, tz="Europe/Berlin")` executes the
        handler at 6am Berlin time."""

        self._scheduled.add(name)
        wrapped_handler = self._wrap_handler(name, handler)

        # `schedule` doesn’t support some use cases, for example:
        # "Run job every 10 minutes on Monday between 3 and pm".
        # This is a very naive wrapper around `schedule` that schedules every combination
        # of weekdays, hours, and minutes as a separate job. This is good enough for us.
        for weekday in weekdays:
            for hour in hours:
                for minute in minutes:
                    formatted_hour = str(hour).rjust(2, "0")
                    formatted_minute = str(minute).rjust(2, "0")
                    formatted_time = f"{formatted_hour}:{formatted_minute}"

                    # This is equivalent to something like `every().monday.at("12:30")`
                    job = self._scheduler.every()
                    job = getattr(job, weekday.value)
                    job = job.at(formatted_time, tz)
                    job = job.tag(name)
                    job = job.do(wrapped_handler)

    def _wrap_handler(self, name: str, handler: Handler) -> Handler:
        # Wraps the actual handler function to add exception handling and result logging.

        def wrapped() -> None:
            start_time = time.time()
            started_at = datetime.datetime.now(datetime.UTC)

            try:
                handler()
                result = PipelineRunResult.SUCCESS
            except SkipPipelineError:
                # Do not log skipped pipeline runs
                return
            except DataUnavailableError:
                result = PipelineRunResult.DATA_UNAVAILABLE
            except Exception:
                result = PipelineRunResult.FAILURE

            duration = time.time() - start_time
            finished_at = datetime.datetime.now(datetime.UTC)

            labels = {"pipeline": name, "result": result.value}
            PIPELINE_RUNS.labels(**labels).inc()
            PIPELINE_RUN_DURATION.labels(**labels).observe(duration)

            run = PipelineRun(
                pipeline=name,
                started_at=started_at,
                finished_at=finished_at,
                result=result.value,
            )

            Session.add(run)
            Session.commit()

            log.info(
                "Pipeline run completed",
                name=name,
                run_id=run.id,
                started_at=started_at.isoformat(),
                finished_at=finished_at.isoformat(),
                duration=duration,
                result=result.value,
            )

            Session.remove()

        return wrapped

    def _update_next_run_metrics(self) -> None:
        for name in self._scheduled:
            next_run = self._scheduler.get_next_run(name)
            next_run_ts = next_run.timestamp() if next_run else -1
            PIPELINE_NEXT_RUN.labels(pipeline=name).set(next_run_ts)
