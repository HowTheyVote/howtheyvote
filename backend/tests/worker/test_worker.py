import datetime

import time_machine
from sqlalchemy import select

from howtheyvote.models import PipelineRun, PipelineStatus
from howtheyvote.pipelines import PipelineResult
from howtheyvote.worker.worker import (
    Weekday,
    Worker,
    last_pipeline_run_checksum,
    pipeline_ran_successfully,
)


def get_handler():
    def handler():
        handler.calls += 1

    handler.calls = 0
    return handler


def test_worker_schedule_weekday(db_session):
    worker = Worker()
    handler = get_handler()

    # Mar 24th 2024 is a Sunday
    now = datetime.datetime(2024, 3, 24, 23, 59)
    with time_machine.travel(now):
        worker.schedule(handler, weekdays={Weekday.MON})
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


def test_worker_schedule_time(db_session):
    worker = Worker()
    handler = get_handler()

    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 29)):
        # Every day at 10:30
        worker.schedule(handler, hours={10}, minutes={30})
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
        worker.schedule(handler, hours={10}, minutes={0})
        worker.run_pending()
        assert handler.calls == 0

    # The next `run_pending` ticket happens only at 10:04, even though the job was
    # scheduled to be run at 10:00.
    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 4)):
        worker.run_pending()
        assert handler.calls == 1


def test_worker_schedule_timezone(db_session):
    worker = Worker()
    handler = get_handler()

    # Mar 30th 2024, 23:00 in Brussels
    with time_machine.travel(datetime.datetime(2024, 3, 30, 22, 0)):
        # Every day at midnight
        worker.schedule(handler, hours={0}, minutes={0}, tz="Europe/Brussels")
        worker.run_pending()
        assert handler.calls == 0

    # Mar 31st 2024, 00:00 in Brussels
    with time_machine.travel(datetime.datetime(2024, 3, 30, 23, 0)):
        worker.run_pending()
        assert handler.calls == 1


def test_worker_schedule_timezone_dst(db_session):
    worker = Worker()
    handler = get_handler()

    # Mar 31st 2024, 23:00 in Brussels (DST)
    with time_machine.travel(datetime.datetime(2024, 3, 31, 21, 0)):
        # Every day at midnight
        worker.schedule(handler, hours={0}, minutes={0}, tz="Europe/Brussels")
        worker.run_pending()
        assert handler.calls == 0

    # Apr 1st 2024, 00:00 in Brussels (DST)
    with time_machine.travel(datetime.datetime(2024, 3, 31, 22, 0)):
        worker.run_pending()
        assert handler.calls == 1


def test_worker_schedule_pipeline_log_runs(db_session):
    worker = Worker()

    def pipeline_handler():
        return PipelineResult(
            status=PipelineStatus.SUCCESS,
            checksum="123abc",
        )

    with time_machine.travel(datetime.datetime(2024, 1, 1, 0, 0)):
        worker.schedule_pipeline(pipeline_handler, name="test", hours={10})
        worker.run_pending()

        runs = list(db_session.execute(select(PipelineRun)).scalars())
        assert len(runs) == 0

    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 0)):
        worker.run_pending()

        runs = list(db_session.execute(select(PipelineRun)).scalars())
        assert len(runs) == 1

        run = runs[0]
        assert run.pipeline == "test"
        assert run.status == PipelineStatus.SUCCESS
        assert run.checksum == "123abc"
        assert run.started_at.date() == datetime.date(2024, 1, 1)
        assert run.finished_at.date() == datetime.date(2024, 1, 1)


def test_worker_schedule_pipeline_log_runs_status(db_session):
    worker = Worker()

    def data_unavailable():
        return PipelineResult(
            status=PipelineStatus.DATA_UNAVAILABLE,
            checksum=None,
        )

    def failure():
        return PipelineResult(
            status=PipelineStatus.FAILURE,
            checksum=None,
        )

    with time_machine.travel(datetime.datetime(2024, 1, 1, 0, 0)):
        worker.schedule_pipeline(
            data_unavailable,
            name="data_unavailable",
            hours={10},
        )
        worker.schedule_pipeline(
            failure,
            name="failure",
            hours={10},
        )

    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 0)):
        worker.run_pending()

        runs = list(db_session.execute(select(PipelineRun)).scalars())
        assert len(runs) == 2

        assert runs[0].pipeline == "data_unavailable"
        assert runs[0].status == PipelineStatus.DATA_UNAVAILABLE

        assert runs[1].pipeline == "failure"
        assert runs[1].status == PipelineStatus.FAILURE


def test_worker_schedule_pipeline_unhandled_exceptions(db_session):
    worker = Worker()

    def woops():
        raise Exception()

    with time_machine.travel(datetime.datetime(2024, 1, 1, 0, 0)):
        worker.schedule_pipeline(woops, name="woops", hours={10})

    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 0)):
        worker.run_pending()

        runs = list(db_session.execute(select(PipelineRun)).scalars())
        assert len(runs) == 1
        assert runs[0].pipeline == "woops"
        assert runs[0].status == PipelineStatus.FAILURE


def test_worker_schedule_pipeline_unhandled_exception_notification(db_session, mocker):
    send_notification = mocker.patch("howtheyvote.worker.worker.send_notification")
    worker = Worker()

    def woops():
        raise Exception("Woops, that didn’t work!")

    with time_machine.travel(datetime.datetime(2024, 1, 1, 0, 0)):
        worker.schedule_pipeline(woops, name="woops", hours={10})

    with time_machine.travel(datetime.datetime(2024, 1, 1, 10, 0)):
        worker.run_pending()
        send_notification.assert_called_with(
            title="Pipeline failure: woops",
            message="Check logs for details. Error message: Woops, that didn’t work!",
        )


def test_pipeline_ran_successfully(db_session):
    class TestPipeline:
        pass

    now = datetime.datetime.now()
    today = now.date()

    run = PipelineRun(
        started_at=now,
        finished_at=now,
        pipeline=TestPipeline.__name__,
        status=PipelineStatus.FAILURE,
    )
    db_session.add(run)
    db_session.commit()

    assert pipeline_ran_successfully(TestPipeline, today) is False

    run = PipelineRun(
        started_at=now,
        finished_at=now,
        pipeline=TestPipeline.__name__,
        status=PipelineStatus.SUCCESS,
    )
    db_session.add(run)
    db_session.commit()

    assert pipeline_ran_successfully(TestPipeline, today) is True
    assert pipeline_ran_successfully(TestPipeline, today, count=2) is False

    run = PipelineRun(
        started_at=now,
        finished_at=now,
        pipeline=TestPipeline.__name__,
        status=PipelineStatus.SUCCESS,
    )
    db_session.add(run)
    db_session.commit()

    assert pipeline_ran_successfully(TestPipeline, today, count=2) is True


def test_last_pipeline_run_checksum(db_session):
    class TestPipeline:
        pass

    with time_machine.travel(datetime.datetime(2024, 1, 1, 0, 0)):
        checksum = last_pipeline_run_checksum(
            pipeline=TestPipeline,
            date=datetime.date(2024, 1, 1),
        )
        assert checksum is None

    run = PipelineRun(
        started_at=datetime.datetime(2024, 1, 1, 0, 0, 0),
        finished_at=datetime.datetime(2024, 1, 1, 0, 0, 0),
        pipeline=TestPipeline.__name__,
        status=PipelineStatus.SUCCESS,
        checksum="123abc",
    )
    db_session.add(run)
    db_session.commit()

    with time_machine.travel(datetime.datetime(2024, 1, 1, 1, 0, 0)):
        checksum = last_pipeline_run_checksum(
            pipeline=TestPipeline,
            date=datetime.date(2024, 1, 1),
        )
        assert checksum == "123abc"

        checksum = last_pipeline_run_checksum(
            pipeline=TestPipeline,
            date=datetime.date(2024, 1, 2),
        )
        assert checksum is None

    run = PipelineRun(
        started_at=datetime.datetime(2024, 1, 1, 12, 0, 0),
        finished_at=datetime.datetime(2024, 1, 1, 12, 0, 0),
        pipeline=TestPipeline.__name__,
        status=PipelineStatus.SUCCESS,
        checksum="456def",
    )
    db_session.add(run)
    db_session.commit()

    with time_machine.travel(datetime.datetime(2024, 1, 1, 13, 0, 0)):
        checksum = last_pipeline_run_checksum(
            pipeline=TestPipeline,
            date=datetime.date(2024, 1, 1),
        )
        assert checksum == "456def"
