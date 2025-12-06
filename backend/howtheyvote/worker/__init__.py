import datetime
import time
from collections.abc import Callable

from prometheus_client import Gauge
from sqlalchemy import func, or_, select
from structlog import get_logger

from .. import config
from ..db import Session
from ..export import generate_export
from ..files import file_path
from ..models import PipelineRun, PipelineStatus, PlenarySession
from ..pipelines import (
    MembersPipeline,
    OEILSummaryPipeline,
    PipelineResult,
    PressPipeline,
    RCVListPipeline,
    SessionsPipeline,
    VOTListPipeline,
)
from ..pushover import send_notification
from ..query import session_is_current_at
from .worker import (
    SkipPipeline,
    Weekday,
    Worker,
    last_pipeline_run_checksum,
)

log = get_logger(__name__)


def rcv_list_handler() -> PipelineResult:
    """Checks if there is a current plenary session and, if yes, fetches the latest roll-call
    vote results."""
    today = datetime.date.today()

    if not _is_session_day(today):
        raise SkipPipeline()

    last_run_checksum = last_pipeline_run_checksum(
        pipeline=RCVListPipeline,
        date=today,
    )
    pipeline = RCVListPipeline(
        term=config.CURRENT_TERM,
        date=today,
        last_run_checksum=last_run_checksum,
    )

    pipeline = RCVListPipeline(term=config.CURRENT_TERM, date=today)
    return pipeline.run()


def rcv_list_notification_handler() -> None:
    """Checks whether the RCV list pipeline has been executed successfuly, and sends a
    Pushover notification if not."""
    today = datetime.date.today()

    # Do not check for last run on days without Plenary
    if not _is_session_day(today):
        return None

    query = (
        select(PipelineRun)
        .where(PipelineRun.pipeline == RCVListPipeline.__name__)
        .where(func.date(PipelineRun.started_at) == func.date(today))
        .where(
            or_(
                PipelineRun.status == PipelineStatus.SUCCESS,
                PipelineRun.status == PipelineStatus.FAILURE,
            )
        )
    )
    run = Session.execute(query).scalar()

    if run:
        # RCV pipeline ran successfully or failed, do nothing.
        # Failed pipeline runs always send notifications separately.
        return None

    send_notification(
        title="No RCV list found at end of day",
        message=(
            "The last scheduled run of the day did not find an RCV list."
            "Either there were no roll-call votes today or source data is not yet available."
        ),
    )


def make_vot_list_handler(days_ago: int) -> Callable[[], PipelineResult]:
    """Returns a worker handler to scrape the VOT list for a previous session day.
    In contrast to RCV lists, VOT lists are usually published with at least one day
    of delay. That means trying to scrape the VOT list the same day would fail in
    most cases."""

    def vot_list_handler() -> PipelineResult:
        date = datetime.date.today() - datetime.timedelta(days=days_ago)

        if not _is_session_day(date):
            raise SkipPipeline()

        pipeline = VOTListPipeline(term=config.CURRENT_TERM, date=date)
        return pipeline.run()

    return vot_list_handler


def press_handler() -> PipelineResult:
    """Checks if there is a current plenary session and, if yes, fetches the latest press
    releases from the Parliament’s news hub."""
    today = datetime.date.today()

    if not _is_session_day(today):
        raise SkipPipeline()

    pipeline = PressPipeline(date=today, with_rss=True)
    return pipeline.run()


def sessions_handler() -> PipelineResult:
    """Fetches plenary session dates."""
    pipeline = SessionsPipeline(term=config.CURRENT_TERM)
    return pipeline.run()


def members_handler() -> PipelineResult:
    """Fetches information about all members of the current term."""
    pipeline = MembersPipeline(term=config.CURRENT_TERM)
    return pipeline.run()


def summaries_handler() -> PipelineResult:
    """Fetches all potentially available OEIL Summaries of the last four weeks."""
    pipeline = OEILSummaryPipeline()
    return pipeline.run()


EXPORT_LAST_RUN = Gauge(
    "htv_export_last_run_timestamp_seconds",
    "Timestamp when the CSV export was generated the last time",
)


def export_handler() -> None:
    """Generate the CSV export."""
    archive_path = file_path("export/export")
    generate_export(archive_path)
    EXPORT_LAST_RUN.set(time.time())


def _is_session_day(date: datetime.date) -> bool:
    """Check if there is a session on the given day."""
    query = select(PlenarySession.id).where(session_is_current_at(date))
    session = Session.execute(query).scalar()
    return session is not None


def get_worker() -> Worker:
    worker = Worker()

    # Mon at 04:00
    worker.schedule_pipeline(
        sessions_handler,
        name=SessionsPipeline.__name__,
        weekdays={Weekday.MON},
        hours={4},
        tz=config.TIMEZONE,
    )

    # Mon at 05:00
    worker.schedule_pipeline(
        members_handler,
        name=MembersPipeline.__name__,
        weekdays={Weekday.MON},
        hours={5},
        tz=config.TIMEZONE,
    )

    # Mon at 07:00
    worker.schedule_pipeline(
        summaries_handler,
        name=OEILSummaryPipeline.__name__,
        weekdays={Weekday.MON},
        hours={7},
        tz=config.TIMEZONE,
    )

    # Mon-Thu between 12:00 and 15:00, every 10 mins until it succeeds
    worker.schedule_pipeline(
        rcv_list_handler,
        name=RCVListPipeline.__name__,
        weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
        hours=range(12, 15),
        minutes=range(0, 60, 10),
        tz=config.TIMEZONE,
        idempotency_key_func=lambda: f"{datetime.date.today().isoformat()}-midday",
    )

    # Mon-Thu between 17:00 and 20:00, every 10 mins until it succeeds
    worker.schedule_pipeline(
        rcv_list_handler,
        name=RCVListPipeline.__name__,
        weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
        hours=range(17, 20),
        minutes=range(0, 60, 10),
        tz=config.TIMEZONE,
        idempotency_key_func=lambda: f"{datetime.date.today().isoformat()}-evening",
    )

    # Mon-Thu at 20:00
    worker.schedule(
        rcv_list_notification_handler,
        weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
        hours={20},
        tz=config.TIMEZONE,
    )

    # Mon-Sun at 21:00
    # Schedule separate jobs running the VOT list pipeline for 1d ago, 2d ago, ..., 7d ago
    for i in range(1, 8):
        worker.schedule_pipeline(
            make_vot_list_handler(i),
            name=VOTListPipeline.__name__,
            hours={21},
            tz=config.TIMEZONE,
            idempotency_key_func=(
                lambda i=i: (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
            ),
        )

    # Mon-Thu, between 13:00 and 20:00, every 30 mins
    worker.schedule_pipeline(
        press_handler,
        name=PressPipeline.__name__,
        weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
        hours=range(13, 20),
        minutes={0, 30},
        tz=config.TIMEZONE,
    )

    # Sun at 04:00
    worker.schedule(
        export_handler,
        weekdays={Weekday.SUN},
        hours={4},
        # While the schedules for other pipelines follow real-life events in Brussels/
        # Strasbourg time, this isn’t the case for the export so we can just use UTC
        # for simplicity.
        tz="UTC",
    )

    return worker


worker = get_worker()
