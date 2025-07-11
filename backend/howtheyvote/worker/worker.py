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
from sqlalchemy import func, select
from structlog import get_logger

from .. import config
from ..db import Session
from ..models import PipelineRun, PipelineStatus
from ..pipelines import PipelineResult
from ..pushover import send_notification

log = get_logger(__name__)

prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

PIPELINE_RUN_DURATION = Histogram(
    "htv_worker_pipeline_run_duration_seconds",
    "Duration of pipeline runs executed by the worker",
    ["pipeline", "status"],
)

PIPELINE_RUNS = Counter(
    "htv_worker_pipeline_runs_total",
    "Total number of pipeline runs executed by the worker",
    ["pipeline", "status"],
)

PIPELINE_NEXT_RUN = Gauge(
    "htv_worker_pipeline_next_run_timestamp_seconds",
    "Timestamp of the next scheduled run of the pipeline",
    ["pipeline"],
)

PIPELINE_LAST_RUN = Gauge(
    "htv_worker_pipeline_last_run_timestamp_seconds",
    "Timestamp of the last run of the pipeline",
    ["pipeline", "status"],
)


class SkipPipeline(Exception):  # noqa: N818
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


def pipeline_ran_successfully(
    pipeline: type[object],
    date: datetime.date,
    count: int = 1,
) -> bool:
    """Check if a given pipeline has been run successfully on a given day."""
    query = (
        select(func.count())
        .select_from(PipelineRun)
        .where(PipelineRun.pipeline == pipeline.__name__)
        .where(func.date(PipelineRun.started_at) == func.date(date))
        .where(PipelineRun.status == PipelineStatus.SUCCESS)
    )
    result = Session.execute(query).scalar() or 0

    return result >= count


def last_pipeline_run_checksum(pipeline: type[object], date: datetime.date) -> str | None:
    """Returns the checksum of the most recent pipeline run on a given day."""
    query = (
        select(PipelineRun.checksum)
        .where(PipelineRun.pipeline == pipeline.__name__)
        .where(func.date(PipelineRun.started_at) == func.date(date))
        .where(PipelineRun.status == PipelineStatus.SUCCESS)
        .order_by(PipelineRun.finished_at.desc())
    )
    return Session.execute(query).scalar()


class Worker:
    """Running a worker starts a long-running process that executes data pipelines in regular
    intervals and stores the status of the pipeline runs in the database."""

    def __init__(self) -> None:
        self._scheduler = Scheduler()
        self._stopped = False
        self._scheduled_pipelines: set[str] = set()

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
        weekdays: Iterable[Weekday] = set(Weekday),
        hours: Iterable[int] = {0},
        minutes: Iterable[int] = {0},
        tz: str | None = None,
    ) -> None:
        """Schedule a job to be executed at the given weekdays, hours, minutes. Optionally
        passing a timezone string via the `tz` parameter indicates that the job should be
        executed at the given time in the respective timezone. The following example
        executes the handler at 6am Berlin time:

        ```
        schedule(my_handler, hours={6}, tz="Europe/Berlin")
        ```
        """

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
                    job = job.do(handler)

    def schedule_pipeline(
        self,
        handler: Callable[..., PipelineResult],
        name: str,
        weekdays: Iterable[Weekday] = set(Weekday),
        hours: Iterable[int] = {0},
        minutes: Iterable[int] = {0},
        tz: str | None = None,
        idempotency_key: Callable[..., str] | None = None,
    ) -> None:
        """Same as `schedule`, but handles exceptions and logs pipeline runs."""

        def wrapped_handler() -> None:
            start_time = time.time()
            started_at = datetime.datetime.now(datetime.UTC)

            idempotency_key_value = None

            # Check if an idempotency key function is given, and skip this run if there was a
            # previous successful run of the pipeline with the same key.
            if idempotency_key:
                idempotency_key_value = idempotency_key()
                count = (
                    select(func.count())
                    .select_from(PipelineRun)
                    .where(PipelineRun.idempotency_key == idempotency_key_value)
                    .where(PipelineRun.pipeline == name)
                    .where(PipelineRun.status == PipelineStatus.SUCCESS)
                )

                if Session.execute(count).scalar_one() > 0:
                    return

            try:
                result = handler()
                status = result.status
                checksum = result.checksum
            except SkipPipeline:
                # Do not log skipped pipeline runs
                return
            except Exception as exc:
                status = PipelineStatus.FAILURE
                checksum = None
                log.exception("Unhandled exception during pipeline run", pipeline=name)
                send_notification(
                    title=f"Pipeline failure: {name}",
                    message=f"Check logs for details. Error message: {exc}",
                )

            duration = time.time() - start_time
            finished_at = datetime.datetime.now(datetime.UTC)

            labels = {"pipeline": name, "status": status.value}
            PIPELINE_RUNS.labels(**labels).inc()
            PIPELINE_LAST_RUN.labels(**labels).set(finished_at.timestamp())
            PIPELINE_RUN_DURATION.labels(**labels).observe(duration)

            run = PipelineRun(
                pipeline=name,
                started_at=started_at,
                finished_at=finished_at,
                status=status,
                checksum=checksum,
                idempotency_key=idempotency_key_value,
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
                status=status.value,
            )

            Session.remove()

        self._scheduled_pipelines.add(name)

        self.schedule(
            handler=wrapped_handler,
            weekdays=weekdays,
            hours=hours,
            minutes=minutes,
            tz=tz,
        )

    def _update_next_run_metrics(self) -> None:
        for name in self._scheduled_pipelines:
            next_run = self._scheduler.get_next_run(name)
            next_run_ts = next_run.timestamp() if next_run else -1
            PIPELINE_NEXT_RUN.labels(pipeline=name).set(next_run_ts)
