import datetime
import time

from prometheus_client import Gauge
from sqlalchemy import exists, func, select
from structlog import get_logger

from .. import config
from ..db import Session
from ..export import Export
from ..files import file_path
from ..models import PipelineRun, PipelineRunResult, PlenarySession
from ..pipelines import MembersPipeline, PressPipeline, RCVListPipeline, SessionsPipeline
from ..query import session_is_current_at
from .worker import SkipPipelineError, Weekday, Worker

log = get_logger(__name__)


def op_rcv() -> None:
    """Checks if there is a current plenary session and, if yes, fetches the latest roll-call
    vote results."""
    today = datetime.date.today()

    if not _is_session_day(today):
        raise SkipPipelineError()

    if _ran_successfully(RCVListPipeline, today):
        raise SkipPipelineError()

    pipeline = RCVListPipeline(term=config.CURRENT_TERM, date=today)
    pipeline.run()


def op_press() -> None:
    """Checks if there is a current plenary session and, if yes, fetches the latest press
    releases from the Parliament’s news hub."""
    today = datetime.date.today()

    if not _is_session_day(today):
        raise SkipPipelineError()

    pipeline = PressPipeline(date=today, with_rss=True)
    pipeline.run()


def op_sessions() -> None:
    """Fetches plenary session dates."""
    pipeline = SessionsPipeline(term=config.CURRENT_TERM)
    pipeline.run()


def op_members() -> None:
    """Fetches information about all members of the current term."""
    pipeline = MembersPipeline(term=config.CURRENT_TERM)
    pipeline.run()


EXPORT_LAST_RUN = Gauge(
    "htv_export_last_run_timestamp_seconds",
    "Timestamp when the CSV export was generated the last time",
)


def op_generate_export() -> None:
    export = Export(outdir=file_path("export"))
    export.run()
    EXPORT_LAST_RUN.set(time.time())


def _is_session_day(date: datetime.date) -> bool:
    """Check if there is a session on the given day."""
    query = select(PlenarySession.id).where(session_is_current_at(date))
    session = Session.execute(query).scalar()
    return session is not None


def _ran_successfully(pipeline: type[object], date: datetime.date) -> bool:
    """Check if a given pipeline has been run successfully on a given day."""
    query = (
        exists()
        .where(PipelineRun.pipeline == pipeline.__name__)
        .where(func.date(PipelineRun.started_at) == func.date(date))
        .where(PipelineRun.result == PipelineRunResult.SUCCESS)
        .select()
    )

    return bool(Session.execute(query).scalar())


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

# Mon-Thu between 12:00 and 15:00, every 10 mins
worker.schedule_pipeline(
    op_rcv,
    name=RCVListPipeline.__name__,
    weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
    hours=range(12, 15),
    minutes=range(0, 60, 10),
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
    # While the schedules for other pipelines follow real-life events in Brussels/Strasbourg
    # time, this isn’t the case for the export so we can just use UTC for simplicity.
    tz="UTC",
)
