import datetime
import time

from prometheus_client import Gauge
from sqlalchemy import func, select
from structlog import get_logger

from .. import config
from ..db import Session
from ..export import generate_export
from ..files import file_path
from ..models import PipelineRun, PipelineStatus, PlenarySession
from ..pipelines import (
    MembersPipeline,
    PipelineResult,
    PressPipeline,
    RCVListPipeline,
    SessionsPipeline,
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


def op_rcv() -> PipelineResult:
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


def op_press() -> PipelineResult:
    """Checks if there is a current plenary session and, if yes, fetches the latest press
    releases from the Parliament’s news hub."""
    today = datetime.date.today()

    if not _is_session_day(today):
        raise SkipPipeline()

    pipeline = PressPipeline(date=today, with_rss=True)
    return pipeline.run()


def op_sessions() -> PipelineResult:
    """Fetches plenary session dates."""
    pipeline = SessionsPipeline(term=config.CURRENT_TERM)
    return pipeline.run()


def op_members() -> PipelineResult:
    """Fetches information about all members of the current term."""
    pipeline = MembersPipeline(term=config.CURRENT_TERM)
    return pipeline.run()


EXPORT_LAST_RUN = Gauge(
    "htv_export_last_run_timestamp_seconds",
    "Timestamp when the CSV export was generated the last time",
)


def op_generate_export() -> None:
    archive_path = file_path("export/export")
    generate_export(archive_path)
    EXPORT_LAST_RUN.set(time.time())


def op_notify_last_run_unsuccessful() -> None:
    today = datetime.date.today()

    # Do not check for last run on days without Plenary
    if not _is_session_day(today):
        return None

    query = (
        select(PipelineRun)
        .where(PipelineRun.pipeline == RCVListPipeline.__name__)
        .where(func.date(PipelineRun.started_at) == func.date(today))
        .where(PipelineRun.status == PipelineStatus.SUCCESS)
    )
    run = Session.execute(query).scalar()

    if run:
        # RCV pipeline ran successfully, do nothing
        return None

    send_notification(
        title="No RCV List found at end of day",
        message=(
            "The last scheduled run of the day did not find an RCV list."
            "Either there were not roll-call votes today, or there was an issue."
        ),
    )


def _is_session_day(date: datetime.date) -> bool:
    """Check if there is a session on the given day."""
    query = select(PlenarySession.id).where(session_is_current_at(date))
    session = Session.execute(query).scalar()
    return session is not None


def get_worker() -> Worker:
    worker = Worker()

    # Mon at 04:00
    worker.schedule_pipeline(
        op_sessions,
        name=SessionsPipeline.__name__,
        weekdays={Weekday.MON},
        hours={4},
        tz=config.TIMEZONE,
    )

    # Mon at 05:00
    worker.schedule_pipeline(
        op_members,
        name=MembersPipeline.__name__,
        weekdays={Weekday.MON},
        hours={5},
        tz=config.TIMEZONE,
    )

    # Mon-Thu between 12:00 and 15:00, every 10 mins until it succeeds
    worker.schedule_pipeline(
        op_rcv,
        name=RCVListPipeline.__name__,
        weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
        hours=range(12, 15),
        minutes=range(0, 60, 10),
        tz=config.TIMEZONE,
        idempotency_key=lambda: f"{datetime.date.today().isoformat()}-midday",
    )

    # Mon-Thu between 17:00 and 20:00, every 10 mins until it succeeds
    worker.schedule_pipeline(
        op_rcv,
        name=RCVListPipeline.__name__,
        weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
        hours=range(17, 20),
        minutes=range(0, 60, 10),
        tz=config.TIMEZONE,
        idempotency_key=lambda: f"{datetime.date.today().isoformat()}-evening",
    )

    # Mon-Thu at 20:00
    worker.schedule(
        op_notify_last_run_unsuccessful,
        weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
        hours={20},
        tz=config.TIMEZONE,
    )

    # Mon-Thu, between 13:00 and 20:00, every 30 mins
    worker.schedule_pipeline(
        op_press,
        name=PressPipeline.__name__,
        weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
        hours=range(13, 20),
        minutes={0, 30},
        tz=config.TIMEZONE,
    )

    # Sun at 04:00
    worker.schedule(
        op_generate_export,
        weekdays={Weekday.SUN},
        hours={4},
        # While the schedules for other pipelines follow real-life events in Brussels/
        # Strasbourg time, this isn’t the case for the export so we can just use UTC
        # for simplicity.
        tz="UTC",
    )

    return worker


worker = get_worker()
