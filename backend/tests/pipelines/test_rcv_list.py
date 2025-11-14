import datetime

import pytest
from sqlalchemy import select

from howtheyvote.models import (
    Committee,
    Group,
    GroupMembership,
    Member,
    MemberVote,
    OEILSubject,
    PipelineStatus,
    Vote,
    VotePosition,
)
from howtheyvote.pipelines import RCVListPipeline

from ..helpers import load_fixture


@pytest.fixture
def member(db_session):
    member = Member(
        id=197490,
        first_name="Magdalena",
        last_name="ADAMOWICZ",
        group_memberships=[
            GroupMembership(
                term=9,
                start_date=datetime.datetime(2019, 7, 2),
                end_date=datetime.datetime(2024, 7, 15),
                group=Group["EPP"],
            ),
        ],
    )

    db_session.add(member)
    db_session.commit()

    yield member


@pytest.mark.always_mock_requests
def test_run_source_not_available(responses, db_session):
    pipe = RCVListPipeline(term=9, date=datetime.date(2024, 4, 10))
    result = pipe.run()
    assert result.status == PipelineStatus.DATA_UNAVAILABLE


@pytest.mark.always_mock_requests
def test_run(responses, db_session, member, mocker):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-04-24-RCV_FR.xml",
        body=load_fixture("pipelines/data/rcv-list_pv-9-2024-04-24-rcv-fr-noon.xml"),
    )
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/A-9-2024-0163_EN.html",
        body=load_fixture("pipelines/data/document_a-9-2024-0163-en.html"),
    )
    responses.get(
        "https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file?reference=2024/2006(REG)",
        body=load_fixture("pipelines/data/oeil_2024-2006-reg.html"),
    )

    mock = mocker.patch("howtheyvote.pipelines.rcv_list.send_notification")

    # Run the pipeline for the first time
    RCVListPipeline(term=9, date=datetime.date(2024, 4, 24)).run()

    votes = list(db_session.execute(select(Vote)).scalars())
    assert len(votes) == 1

    assert votes[0].id == 168834
    assert votes[0].term == 9
    assert votes[0].title is None
    assert (
        votes[0].procedure_title
        == "EP\xa0Rules of Procedure: training on preventing conflict and harassment in the workplace and on good office management"
    )
    assert votes[0].reference == "A9-0163/2024"
    assert votes[0].procedure_reference == "2024/2006(REG)"
    assert votes[0].responsible_committees == [Committee["AFCO"]]
    assert votes[0].oeil_subjects == [OEILSubject["8.40.01.08"]]
    assert votes[0].member_votes == [MemberVote(web_id=197490, position=VotePosition.FOR)]

    # Push notification is sent after pipeline has completed successfully
    assert mock.call_count == 1
    assert mock.call_args.kwargs["title"] == "Scraped RCV list for Wed, Apr 24"
    assert mock.call_args.kwargs["message"] == "1 votes (0 main votes)"


@pytest.mark.always_mock_requests
def test_run_data_unchanged(responses, db_session, member):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-04-24-RCV_FR.xml",
        body=load_fixture("pipelines/data/rcv-list_pv-9-2024-04-24-rcv-fr-noon.xml"),
    )

    # Run the pipeline for the first time
    pipe = RCVListPipeline(
        term=9,
        date=datetime.date(2024, 4, 24),
    )
    result = pipe.run()
    assert result.status == PipelineStatus.SUCCESS
    assert (
        result.checksum == "c01379e8e00e9d8e60c71eebf90941c3318be9751a911d4f08b24aa9d0be26af"
    )

    vote_ids = list(db_session.execute(select(Vote.id)).scalars())
    assert vote_ids == [168834]

    # Run the pipeline again and provide the checksum of the first run
    pipe = RCVListPipeline(
        term=9,
        date=datetime.date(2024, 4, 24),
        last_run_checksum="c01379e8e00e9d8e60c71eebf90941c3318be9751a911d4f08b24aa9d0be26af",
    )
    result = pipe.run()
    assert result.status == PipelineStatus.DATA_UNCHANGED
    assert result.checksum is None

    # Simulate that the source data has been updated in the meantime
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-04-24-RCV_FR.xml",
        body=load_fixture("pipelines/data/rcv-list_pv-9-2024-04-24-rcv-fr-evening.xml"),
    )

    # Run the pipeline again and provide the checksum of the first run
    pipe = RCVListPipeline(
        term=9,
        date=datetime.date(2024, 4, 24),
        last_run_checksum="c01379e8e00e9d8e60c71eebf90941c3318be9751a911d4f08b24aa9d0be26af",
    )
    result = pipe.run()
    assert result.status == PipelineStatus.SUCCESS
    assert (
        result.checksum == "743bf734045d7c797afea9e8c1127c047a4924bcd5090883ff8a74421376d511"
    )

    vote_ids = list(db_session.execute(select(Vote.id)).scalars())
    assert vote_ids == [168834, 168864]
