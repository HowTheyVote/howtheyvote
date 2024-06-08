import datetime

from sqlalchemy import select
from structlog import get_logger

from .. import config
from ..db import Session
from ..models import PipelineRun, PipelineRunResult, PlenarySession
from ..pipelines import MembersPipeline, PressPipeline, RCVListPipeline, SessionsPipeline
from ..query import session_is_current_at
from .worker import SkipPipelineError, Weekday, Worker, pipeline_ran_successfully

log = get_logger(__name__)


def op_rcv_midday() -> None:
    """Checks if there is a current plenary session and, if yes, fetches the latest roll-call
    vote results."""
    today = datetime.date.today()

    if not _is_session_day(today):
        raise SkipPipelineError()

    if pipeline_ran_successfully(RCVListPipeline, today):
        raise SkipPipelineError()

    pipeline = RCVListPipeline(term=config.CURRENT_TERM, date=today)
    pipeline.run()


def op_rcv_evening() -> None:
    """While on most plenary days, there’s only one voting session around midday, on some days
    there is another sesssion in the evening, usually around 17:00. The vote results of the
    evening sessions are appended to the same source document that also contains the results
    of the midday votes. This method fetches the latest roll-call vote results, even if they
    have been fetched successfully earlier on the same day."""
    today = datetime.date.today()

    if not _is_session_day(today):
        raise SkipPipelineError()

    if pipeline_ran_successfully(RCVListPipeline, today, count=2):
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


def _is_session_day(date: datetime.date) -> bool:
    """Check if there is a session on the given day."""
    query = select(PlenarySession.id).where(session_is_current_at(date))
    session = Session.execute(query).scalar()
    return session is not None


worker = Worker()

# Mon at 04:00
worker.schedule(
    op_sessions,
    name=SessionsPipeline.__name__,
    weekdays={Weekday.MON},
    hours={4},
    tz=config.TIMEZONE,
)

# Mon at 05:00
worker.schedule(
    op_members,
    name=MembersPipeline.__name__,
    weekdays={Weekday.MON},
    hours={5},
    tz=config.TIMEZONE,
)

# Mon-Thu between 12:00 and 15:00, every 10 mins
worker.schedule(
    op_rcv_midday,
    name=RCVListPipeline.__name__,
    weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
    hours=range(12, 15),
    minutes=range(0, 60, 10),
    tz=config.TIMEZONE,
)

# Mon-Thu between 17:00 and 20:00, every 10 mins
worker.schedule(
    op_rcv_evening,
    name=RCVListPipeline.__name__,
    weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
    hours=range(17, 20),
    minutes=range(0, 60, 10),
    tz=config.TIMEZONE,
)

# Mon-Thu, between 13:00 and 20:00, every 30 mins
worker.schedule(
    op_press,
    name=PressPipeline.__name__,
    weekdays={Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU},
    hours=range(13, 20),
    minutes={0, 30},
    tz=config.TIMEZONE,
)
