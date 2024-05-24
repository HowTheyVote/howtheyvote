import datetime

from sqlalchemy import select

from howtheyvote.models import (
    Fragment,
    Group,
    GroupMembership,
    Member,
    PlenarySession,
    PressRelease,
    Vote,
)
from howtheyvote.query import (
    fragments_for_records,
    member_active_at,
    member_has_term,
    press_release_references_vote,
    session_is_current_at,
)


def test_member_has_term(db_session):
    member_1 = Member(id=1, terms=[7])
    member_2 = Member(id=2, terms=[8, 9])
    member_3 = Member(id=3, terms=[9])
    member_4 = Member(id=4, terms=[])

    db_session.add_all([member_1, member_2, member_3, member_4])
    db_session.commit()

    query = select(Member.id).where(member_has_term(9))
    ids = set(db_session.execute(query).scalars())

    assert ids == {2, 3}


def test_member_active_at_ongoing(db_session):
    member = Member(
        id=1,
        group_memberships=[
            GroupMembership(
                term=9,
                start_date=datetime.date(2023, 1, 1),
                end_date=None,
                group=Group["GUE_NGL"],
            ),
        ],
    )

    db_session.add(member)
    db_session.commit()

    query = select(Member.id).where(member_active_at(datetime.date(2022, 12, 31)))
    ids = set(db_session.execute(query).scalars())
    assert ids == set()

    query = select(Member.id).where(member_active_at(datetime.date(2023, 1, 1)))
    ids = set(db_session.execute(query).scalars())
    assert ids == {1}

    query = select(Member.id).where(member_active_at(datetime.date(2999, 1, 1)))
    ids = set(db_session.execute(query).scalars())
    assert ids == {1}


def test_member_active_at(db_session):
    member = Member(
        id=1,
        group_memberships=[
            GroupMembership(
                term=9,
                start_date=datetime.date(2023, 1, 1),
                end_date=datetime.date(2023, 1, 31),
                group=Group["GUE_NGL"],
            ),
        ],
    )

    db_session.add(member)
    db_session.commit()

    query = select(Member.id).where(member_active_at(datetime.date(2022, 12, 31)))
    ids = set(db_session.execute(query).scalars())
    assert ids == set()

    query = select(Member.id).where(member_active_at(datetime.date(2023, 1, 1)))
    ids = set(db_session.execute(query).scalars())
    assert ids == {1}

    query = select(Member.id).where(member_active_at(datetime.date(2023, 1, 31)))
    ids = set(db_session.execute(query).scalars())
    assert ids == {1}

    query = select(Member.id).where(member_active_at(datetime.date(2023, 2, 1)))
    ids = set(db_session.execute(query).scalars())
    assert ids == set()


def test_session_is_current_at(db_session):
    plenary_session = PlenarySession(
        id="2023-01-01",
        start_date=datetime.date(2023, 1, 1),
        end_date=datetime.date(2023, 1, 4),
    )

    db_session.add(plenary_session)
    db_session.commit()

    query = select(PlenarySession.id).where(session_is_current_at(datetime.date(2022, 12, 31)))
    ids = set(db_session.execute(query).scalars())
    assert ids == set()

    query = select(PlenarySession.id).where(session_is_current_at(datetime.date(2023, 1, 1)))
    ids = set(db_session.execute(query).scalars())
    assert ids == {"2023-01-01"}

    query = select(PlenarySession.id).where(session_is_current_at(datetime.date(2023, 1, 4)))
    ids = set(db_session.execute(query).scalars())
    assert ids == {"2023-01-01"}

    query = select(PlenarySession.id).where(session_is_current_at(datetime.date(2023, 1, 5)))
    ids = set(db_session.execute(query).scalars())
    assert ids == set()


def test_press_release_references_vote(db_session):
    timestamp = datetime.datetime(2023, 1, 1, 0, 0, 0)

    vote = Vote(
        id=12345,
        reference="A9-1234/2023",
        timestamp=timestamp,
    )

    press_release_1 = PressRelease(
        id="1",
        references=["A9-5678/2023"],
        published_at=timestamp,
    )

    press_release_2 = PressRelease(
        id="2",
        references=["A9-1234/2023"],
        published_at=timestamp,
    )

    press_release_3 = PressRelease(
        id="3",
        references=["A9-1234/2023", "A9-5678/2023"],
        published_at=timestamp,
    )

    press_release_4 = PressRelease(
        id="4",
        references=["A9-1234/2023"],
        published_at=timestamp + datetime.timedelta(days=1),
    )

    db_session.add(vote)
    db_session.add_all([press_release_1, press_release_2, press_release_3, press_release_4])
    db_session.commit()

    query = select(PressRelease.id).where(press_release_references_vote(vote))
    ids = set(db_session.execute(query).scalars())
    assert ids == {"2", "3"}


def test_press_release_references_vote_procedure(db_session):
    timestamp = datetime.datetime(2023, 1, 1, 0, 0, 0)

    vote = Vote(
        id=12345,
        procedure_reference="2023/1234(COD)",
        timestamp=timestamp,
    )

    press_release_1 = PressRelease(
        id="1",
        procedure_references=["2023/5678(COD)"],
        published_at=timestamp,
    )

    press_release_2 = PressRelease(
        id="2",
        procedure_references=["2023/1234(COD)"],
        published_at=timestamp,
    )

    press_release_3 = PressRelease(
        id="3",
        procedure_references=["2023/1234(COD)", "2023/5678(COD)"],
        published_at=timestamp,
    )

    press_release_4 = PressRelease(
        id="4",
        procedure_references=["2023/1234(COD)"],
        published_at=timestamp + datetime.timedelta(days=1),
    )

    db_session.add(vote)
    db_session.add_all([press_release_1, press_release_2, press_release_3, press_release_4])
    db_session.commit()

    query = select(PressRelease.id).where(press_release_references_vote(vote))
    ids = set(db_session.execute(query).scalars())
    assert ids == {"2", "3"}


def test_fragments_for_record(db_session):
    vote = Vote(id=1)

    vote_fragment = Fragment(
        model="Vote",
        group_key="1",
        source_name="TestScraper",
        source_id="1",
        data={},
    )

    member_fragment = Fragment(
        model="Member",
        group_key="1",
        source_name="TestScraper",
        source_id="1",
        data={},
    )

    db_session.add_all([vote, vote_fragment, member_fragment])
    db_session.commit()

    query = select(Fragment).where(fragments_for_records([vote, None]))
    fragments = list(db_session.execute(query).scalars())

    assert len(fragments) == 1
    assert fragments[0].model == "Vote"
