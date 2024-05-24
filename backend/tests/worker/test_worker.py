import datetime

import time_machine
from sqlalchemy import select

from howtheyvote.models import PipelineRun, PipelineRunResult
from howtheyvote.pipelines import DataUnavailableError, PipelineError
from howtheyvote.worker.worker import Weekday, Worker


def get_handler():
    def handler():
        handler.calls += 1

    handler.calls = 0
    return handler


def test_worker_weekday(db_session):
    worker = Worker()
    handler = get_handler()

    # Mar 24th 2024 is a Sunday
    now = datetime.datetime(2024, 3, 24, 23, 59)
    with time_machine.travel(now):
        worker.schedule(handler, name="test", weekdays={Weekday.MON})
        worker.run_pending()
        assert handler.calls == 0

    # Mar 25th 2024 is a Monday
    now = datetime.datetime(2024, 3, 25, 0, 0)
    with time_machine.travel(now):
        worker.run_pending()
        assert handler.calls == 1

    # Mar 26th 2024 is a Tuesday
    now = datetime.datetime(2024, 3, 26, 0, 0)
    with time_machine.travel(now):
        worker.run_pending()
        assert handler.calls == 1


def test_worker_time(db_session):
    worker = Worker()
    handler = get_handler()

    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 29)):
        # Every day at 10:30
        worker.schedule(handler, name="test", hours={10}, minutes={30})
        worker.run_pending()
        assert handler.calls == 0

    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 30)):
        worker.run_pending()
        assert handler.calls == 1

    with time_machine.travel(datetime.datetime(2024, 1, 2, 10, 30)):
        worker.run_pending()
        assert handler.calls == 2


def test_worker_delayed(db_session):
    # The worker runs jobs sequentially on the main thread. If a job take too long
    # subsequent tasks might get delayed, but they will still be executed.

    worker = Worker()
    handler = get_handler()

    with time_machine.travel(datetime.datetime(2024, 1, 1, 9, 59)):
        worker.schedule(handler, name="test", hours={10}, minutes={0})
        worker.run_pending()
        assert handler.calls == 0

    # The next `run_pending` ticket happens only at 10:04, even though the job was
    # scheduled to be run at 10:00.
    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 4)):
        worker.run_pending()
        assert handler.calls == 1


def test_worker_timezone(db_session):
    worker = Worker()
    handler = get_handler()

    # Mar 30th 2024, 23:00 in Brussels
    with time_machine.travel(datetime.datetime(2024, 3, 30, 22, 0)):
        # Every day at midnight
        worker.schedule(
            handler,
            name="test",
            hours={0},
            minutes={0},
            tz="Europe/Brussels",
        )
        worker.run_pending()
        assert handler.calls == 0

    # Mar 31st 2024, 00:00 in Brussels
    with time_machine.travel(datetime.datetime(2024, 3, 30, 23, 0)):
        worker.run_pending()
        assert handler.calls == 1


def test_worker_timezone_dst(db_session):
    worker = Worker()
    handler = get_handler()

    # Mar 31st 2024, 23:00 in Brussels (DST)
    with time_machine.travel(datetime.datetime(2024, 3, 31, 21, 0)):
        # Every day at midnight
        worker.schedule(
            handler,
            name="test",
            hours={0},
            minutes={0},
            tz="Europe/Brussels",
        )
        worker.run_pending()
        assert handler.calls == 0

    # Apr 1st 2024, 00:00 in Brussels (DST)
    with time_machine.travel(datetime.datetime(2024, 3, 31, 22, 0)):
        worker.run_pending()
        assert handler.calls == 1


def test_log_runs(db_session):
    worker = Worker()
    handler = get_handler()

    with time_machine.travel(datetime.datetime(2024, 1, 1, 0, 0)):
        worker.schedule(handler, name="test", hours={10})
        worker.run_pending()
        assert handler.calls == 0

        runs = list(db_session.execute(select(PipelineRun)).scalars())
        assert len(runs) == 0

    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 0)):
        worker.run_pending()
        assert handler.calls == 1

        runs = list(db_session.execute(select(PipelineRun)).scalars())
        assert len(runs) == 1

        run = runs[0]
        assert run.pipeline == "test"
        assert run.result == PipelineRunResult.SUCCESS
        assert run.started_at.date() == datetime.date(2024, 1, 1)
        assert run.finished_at.date() == datetime.date(2024, 1, 1)


def test_log_runs_exceptions(db_session):
    worker = Worker()

    def data_unavailable_error():
        raise DataUnavailableError()

    def pipeline_error():
        raise PipelineError()

    with time_machine.travel(datetime.datetime(2024, 1, 1, 0, 0)):
        worker.schedule(data_unavailable_error, name="data_unavailable_error", hours={10})
        worker.schedule(pipeline_error, name="pipeline_error", hours={10})

    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 0)):
        worker.run_pending()

        runs = list(db_session.execute(select(PipelineRun)).scalars())
        assert len(runs) == 2

        assert runs[0].pipeline == "data_unavailable_error"
        assert runs[0].result == PipelineRunResult.DATA_UNAVAILABLE

        assert runs[1].pipeline == "pipeline_error"
        assert runs[1].result == PipelineRunResult.FAILURE
