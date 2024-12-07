import datetime

import pytest
from sqlalchemy import select

from howtheyvote.models import Group, GroupMembership, Member, Vote
from howtheyvote.pipelines import DataUnavailableError, DataUnchangedError, RCVListPipeline

from ..helpers import load_fixture


@pytest.mark.always_mock_requests
def test_run_source_not_available(responses, db_session):
    with pytest.raises(DataUnavailableError):
        pipe = RCVListPipeline(term=9, date=datetime.date(2024, 4, 10))
        pipe.run()


def test_run_data_unchanged(responses, db_session):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-04-24-RCV_FR.xml",
        body=load_fixture("pipelines/data/rcv-list_pv-9-2024-04-24-rcv-fr-noon.xml"),
    )

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

    # Run the pipeline for the first time
    pipe = RCVListPipeline(
        term=9,
        date=datetime.date(2024, 4, 24),
    )
    pipe.run()
    last_run_checksum = pipe.checksum

    vote_ids = list(db_session.execute(select(Vote.id)).scalars())
    assert vote_ids == [168834]

    # Run the pipeline again and provide the checksum of the first run
    with pytest.raises(DataUnchangedError):
        pipe = RCVListPipeline(
            term=9,
            date=datetime.date(2024, 4, 24),
            last_run_checksum=last_run_checksum,
        )
        pipe.run()

    # Simulate that the source data has been updated in the meantime
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-04-24-RCV_FR.xml",
        body=load_fixture("pipelines/data/rcv-list_pv-9-2024-04-24-rcv-fr-evening.xml"),
    )

    # Run the pipeline again and provide the checksum of the first run
    pipe = RCVListPipeline(
        term=9,
        date=datetime.date(2024, 4, 24),
        last_run_checksum=last_run_checksum,
    )
    pipe.run()

    vote_ids = list(db_session.execute(select(Vote.id)).scalars())
    assert vote_ids == [168834, 168864]
