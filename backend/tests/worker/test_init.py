import datetime

import time_machine
from sqlalchemy import select

from howtheyvote.models import PipelineRun, PipelineStatus, PlenarySession
from howtheyvote.pipelines import (
    PipelineResult,
    PressPipeline,
    RCVListPipeline,
    VOTListPipeline,
)
from howtheyvote.worker import get_worker


def test_rcv_list_pipeline(db_session, mocker):
    plenary_session = PlenarySession(
        id="2025-07-07",
        start_date=datetime.date(2025, 7, 7),
        end_date=datetime.date(2025, 7, 10),
    )
    db_session.add(plenary_session)
    db_session.commit()

    rcv_mock = mocker.patch.object(RCVListPipeline, "run")

    # TODO: For some reason tests will take a very long time if we do not mock the
    # press pipeline. Probably that's because it’s being executed many times due to
    # time travel, and each time it’s retrying requests over and over again. But
    # should double-check that.
    press_mock = mocker.patch.object(PressPipeline, "run")
    press_mock.return_value = PipelineResult(
        status=PipelineStatus.SUCCESS,
        checksum=None,
    )

    query = (
        select(PipelineRun)
        .where(PipelineRun.pipeline == RCVListPipeline.__name__)
        .order_by(PipelineRun.started_at)
    )

    # Tuesday, July 8th, at midnight
    with time_machine.travel("2025-07-08T00:00:00+02:00"):
        # Create worker and schedule pipelines
        worker = get_worker()

    # Tuesday, July 8th, at 12:00 pm
    with time_machine.travel("2025-07-08T12:00:00+02:00"):
        rcv_mock.return_value = PipelineResult(
            status=PipelineStatus.DATA_UNAVAILABLE,
            checksum=None,
        )

        worker.run_pending()

        # The pipeline has been run once, but the data wasn’t available yet
        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 1
        assert runs[0].status == PipelineStatus.DATA_UNAVAILABLE

    # Tuesday, July 8th, at 12:10 pm
    with time_machine.travel("2025-07-08T12:10:00+02:00"):
        rcv_mock.return_value = PipelineResult(
            status=PipelineStatus.SUCCESS,
            checksum="123abc",
        )

        worker.run_pending()

        # The pipeline has been run a second time and has successfully fetched the data
        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 2
        assert runs[1].status == PipelineStatus.SUCCESS
        assert runs[1].checksum == "123abc"

    # Tuesday, July 8th, at 12:20 pm
    with time_machine.travel("2025-07-08T12:20:00+02:00"):
        worker.run_pending()

        # The pipeline hasn’t been run again as it was successfully run before
        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 2

    # Tuesday, July 8th, at 5:00 pm
    with time_machine.travel("2025-07-08T17:00:00+02:00"):
        rcv_mock.return_value = PipelineResult(
            status=PipelineStatus.DATA_UNCHANGED,
            checksum=None,
        )

        worker.run_pending()

        # The pipeline has been run again to check for another voting session in
        # the evening, but the data hasn’t changed
        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 3
        assert runs[2].status == PipelineStatus.DATA_UNCHANGED

    # Tuesday, July 8th, at 5:10 pm
    with time_machine.travel("2025-07-08T17:10:00+02:00"):
        rcv_mock.return_value = PipelineResult(
            status=PipelineStatus.SUCCESS,
            checksum=None,
        )

        worker.run_pending()

        # The pipeline has been run again and has successfully fetched the data
        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 4
        assert runs[3].status == PipelineStatus.SUCCESS

    # Tuesday, July 8th, at 08:00 pm
    with time_machine.travel("2025-07-08T20:00:00+02:00"):
        worker.run_pending()

        # The pipeline hasn’t been run again as it has already succeeded twice that day
        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 4

    # Wednesday, July 9th, at 12:00 pm
    with time_machine.travel("2025-07-09T12:00:00+02:00"):
        rcv_mock.return_value = PipelineResult(
            status=PipelineStatus.SUCCESS,
            checksum=None,
        )

        worker.run_pending()

        # The pipeline has been executed again, as it’s the next day
        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 5
        assert runs[4].status == PipelineStatus.SUCCESS


def test_rcv_list_notification(db_session, mocker):
    plenary_session = PlenarySession(
        id="2025-07-07",
        start_date=datetime.date(2025, 7, 7),
        end_date=datetime.date(2025, 7, 10),
    )
    db_session.add(plenary_session)
    db_session.commit()

    rcv_mock = mocker.patch.object(RCVListPipeline, "run")
    press_mock = mocker.patch.object(PressPipeline, "run")

    press_mock.return_value = PipelineResult(
        status=PipelineStatus.SUCCESS,
        checksum=None,
    )

    pushover_mock = mocker.patch("howtheyvote.worker.send_notification")

    query = (
        select(PipelineRun)
        .where(PipelineRun.pipeline == RCVListPipeline.__name__)
        .order_by(PipelineRun.started_at)
    )

    # Tuesday, July 8th, at 07:45 pm
    with time_machine.travel("2025-07-08T19:45:00+02:00"):
        # Create worker and schedule pipelines
        worker = get_worker()

    # Tuesday, July 8th, at 07:50 pm
    with time_machine.travel("2025-07-08T19:50:00+02:00"):
        rcv_mock.return_value = PipelineResult(
            status=PipelineStatus.SUCCESS,
            checksum=None,
        )

        worker.run_pending()

        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 1
        assert runs[0].status == PipelineStatus.SUCCESS

    # Tuesday, July 8th, at 08:00 pm
    with time_machine.travel("2025-07-08T20:00:00+02:00"):
        worker.run_pending()

        # No notification has been sent because the pipeline has been executed successfully
        assert pushover_mock.call_count == 0

    # Wednesday, July 9th, at 07:45 pm
    with time_machine.travel("2025-07-09T19:45:00+02:00"):
        # Create worker and schedule pipelines
        worker = get_worker()

    # Wednesday, July 9th, at 07:50 pm
    with time_machine.travel("2025-07-09T19:50:00+02:00"):
        rcv_mock.return_value = PipelineResult(
            status=PipelineStatus.DATA_UNAVAILABLE,
            checksum=None,
        )

        worker.run_pending()

        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 2
        assert runs[1].status == PipelineStatus.DATA_UNAVAILABLE

    # Wednesday, July 9th, at 08:00 pm
    with time_machine.travel("2025-07-09T20:00:00+02:00"):
        worker.run_pending()

        # A notification has been sent because the pipeline hasn’t been executed successfully
        assert pushover_mock.call_count == 1
        assert pushover_mock.call_args.kwargs["title"] == "No RCV List found at end of day"


def test_vot_list_pipeline(db_session, mocker):
    plenary_session = PlenarySession(
        id="2025-07-07",
        start_date=datetime.date(2025, 7, 7),
        end_date=datetime.date(2025, 7, 10),
    )
    db_session.add(plenary_session)
    db_session.commit()

    vot_mock = mocker.patch.object(
        VOTListPipeline,
        "run",
        autospec=True,
    )

    rcv_mock = mocker.patch.object(RCVListPipeline, "run")
    rcv_mock.return_value = PipelineResult(
        status=PipelineStatus.SUCCESS,
        checksum=None,
    )

    press_mock = mocker.patch.object(PressPipeline, "run")
    press_mock.return_value = PipelineResult(
        status=PipelineStatus.SUCCESS,
        checksum=None,
    )

    query = (
        select(PipelineRun)
        .where(PipelineRun.pipeline == VOTListPipeline.__name__)
        .order_by(PipelineRun.started_at)
    )

    # Tuesday, July 8th, at midnight
    with time_machine.travel("2025-07-08T00:10:00+02:00"):
        # Create worker and schedule pipelines
        worker = get_worker()

    # Tuesday, July 8th, at 21:00 am
    with time_machine.travel("2025-07-08T21:00:00+02:00"):
        vot_mock.return_value = PipelineResult(
            status=PipelineStatus.DATA_UNAVAILABLE,
            checksum=None,
        )

        worker.run_pending()

        # The pipeline has been run once for Monday
        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 1
        assert runs[0].status == PipelineStatus.DATA_UNAVAILABLE
        assert vot_mock.call_args_list[0].args[0].date == datetime.date(2025, 7, 7)

    # Wednesday, July 9th, at 21:00 am
    with time_machine.travel("2025-07-09T21:00:00+02:00"):
        vot_mock.return_value = PipelineResult(
            status=PipelineStatus.SUCCESS,
            checksum=None,
        )

        worker.run_pending()

        # The pipeline has been run one more time for Monday and once for Tuesday
        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 3

        assert runs[1].status == PipelineStatus.SUCCESS
        assert vot_mock.call_args_list[1].args[0].date == datetime.date(2025, 7, 8)

        assert runs[2].status == PipelineStatus.SUCCESS
        assert vot_mock.call_args_list[2].args[0].date == datetime.date(2025, 7, 7)

    # Thursday, July 10th, at 21:00 am
    with time_machine.travel("2025-07-10T21:00:00+02:00"):
        worker.run_pending()

        # The pipeline has been run once for Wednesday
        runs = list(db_session.execute(query).scalars())
        assert len(runs) == 4

        assert runs[3].status == PipelineStatus.SUCCESS
        assert vot_mock.call_args_list[3].args[0].date == datetime.date(2025, 7, 9)
